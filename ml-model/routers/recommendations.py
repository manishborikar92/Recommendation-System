# routers/recommendations.py
from starlette.concurrency import run_in_threadpool
from fastapi import APIRouter, HTTPException, status, Query, Path, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import asyncpg
import math
import os
import logging
from datetime import datetime, timedelta
from schemas import ProductResponse
from pydantic import BaseModel
import re
import sqlalchemy
from sqlalchemy import text
from database.interactions import DBInteractions
from services.models import ContentModel
from services.recommender import hybrid_merge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# -----------------------------
# Pydantic response model
# -----------------------------
class RecommendationResponse(BaseModel):
    personalized: List[Dict[str, Any]]
    trending: List[Dict[str, Any]]
    best_value: List[Dict[str, Any]]
    top_categories: Dict[str, List[Dict[str, Any]]]
    diverse_picks: List[Dict[str, Any]]

# -----------------------------
# Helper function: product fetcher
# -----------------------------
def fetch_products(sql_query: str, params: dict) -> List[Dict[str, Any]]:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")
    engine = sqlalchemy.create_engine(DATABASE_URL)
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query), params)
            rows = result.fetchall()
            products = []
            for row in rows:
                products.append({
                    "id": row["id"],
                    "name": row["name"],
                    "category": f"{row['main_category']} > {row['sub_category']}",
                    "image": row["image"],
                    "price": float(row["discount_price"]) if row["discount_price"] is not None else None,
                    "original_price": float(row["actual_price"]) if row["actual_price"] is not None else None,
                    "rating": float(row["ratings"]) if row["ratings"] is not None else None,
                    "reviews": row["no_of_ratings"],
                    "discount_ratio": float(row["discount_ratio"]) if row["discount_ratio"] is not None else None,
                })
            return products
    except Exception as e:
        logger.exception("Failed to fetch products: %s", e)
        raise

def fetch_products_by_ids(product_ids: List[str]) -> List[Dict[str, Any]]:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")
    engine = sqlalchemy.create_engine(DATABASE_URL)
    query = text("""
        SELECT id, name, main_category, sub_category, image,
               discount_price, actual_price, ratings, no_of_ratings, discount_ratio
        FROM products
        WHERE id = ANY(:ids)
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"ids": product_ids})
        rows = result.fetchall()
        products = []
        for row in rows:
            products.append({
                "id": row["id"],
                "name": row["name"],
                "category": f"{row['main_category']} > {row['sub_category']}",
                "image": row["image"],
                "price": float(row["discount_price"]) if row["discount_price"] is not None else None,
                "original_price": float(row["actual_price"]) if row["actual_price"] is not None else None,
                "rating": float(row["ratings"]) if row["ratings"] is not None else None,
                "reviews": row["no_of_ratings"],
                "discount_ratio": float(row["discount_ratio"]) if row["discount_ratio"] is not None else None,
            })
        return products

async def get_db():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    try:
        yield conn
    finally:
        await conn.close()

@router.get("/home", response_model=RecommendationResponse)
async def get_home_recommendations(
    user_id: str = Query(..., regex=r"^[a-zA-Z0-9]{1,50}$"),
    response_limit: int = Query(20, ge=1, le=60)
):
    """
    Retrieve home recommendations.
    For new users, personalized array is empty.
    Returns:
      - personalized: Based on user's interaction history (if exists).
      - trending: Products trending by high ratings and review counts.
      - best_value: Products ordered by discount ratio.
      - top_categories: Top products in selected categories (e.g., Electronics and Fashion).
      - diverse_picks: Randomly selected products.
    """
    recommendations = {
        "personalized": [],
        "trending": [],
        "best_value": [],
        "top_categories": {},
        "diverse_picks": []
    }
    
    # Fetch user interactions (last 30 days) asynchronously.
    try:
        interactions = await DBInteractions.fetch_user_interactions('u'+user_id, days=30)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to fetch user interactions"
        )
    
    # Generate personalized recommendations if interactions exist.
    if interactions:
        try:
            content_model = ContentModel(model_dir="model")
            # For simplicity, use the first clicked product available.
            clicked_products = [
                rec["product_id"]
                for rec in interactions
                if rec["event_type"] == "product_click" and rec.get("product_id")
            ]
            if clicked_products:
                similar = content_model.get_similar_products(clicked_products[0], top_n=response_limit)
                if similar:
                    personalized_ids = [item["id"] for item in similar]
                    # Use run_in_threadpool to fetch complete product details.
                    personalized_details = await run_in_threadpool(fetch_products_by_ids, personalized_ids)
                    recommendations["personalized"] = personalized_details
        except Exception as e:
            logger.error("Error generating personalized recommendations: %s", e)
    
    # Fetch trending products (sorted by ratings and review counts).
    try:
        trending_sql = """
            SELECT id, name, main_category, sub_category, image,
                   discount_price, actual_price, ratings, no_of_ratings, discount_ratio
            FROM products
            ORDER BY ratings DESC, no_of_ratings DESC
            LIMIT :limit
        """
        trending = await run_in_threadpool(fetch_products, trending_sql, {"limit": response_limit})
        recommendations["trending"] = trending
    except Exception as e:
        logger.error("Failed to fetch trending products: %s", e)
    
    # Fetch best value products (sorted by discount_ratio descending).
    try:
        best_value_sql = """
            SELECT id, name, main_category, sub_category, image,
                   discount_price, actual_price, ratings, no_of_ratings, discount_ratio
            FROM products
            ORDER BY discount_ratio DESC
            LIMIT :limit
        """
        best_value = await run_in_threadpool(fetch_products, best_value_sql, {"limit": response_limit})
        recommendations["best_value"] = best_value
    except Exception as e:
        logger.error("Failed to fetch best value products: %s", e)
    
    # Fetch top products for each predefined category (e.g., Home Furnishing and Watches).
    try:
        top_categories = {}
        for category in ["Home Furnishing", "Watches"]:
            top_cat_sql = """
                SELECT id, name, main_category, sub_category, image,
                       discount_price, actual_price, ratings, no_of_ratings, discount_ratio
                FROM products
                WHERE sub_category = :category
                ORDER BY ratings DESC
                LIMIT :limit
            """
            top_cat = await run_in_threadpool(fetch_products, top_cat_sql, {"category": category, "limit": response_limit})
            top_categories[category] = top_cat
        recommendations["top_categories"] = top_categories
    except Exception as e:
        logger.error("Failed to fetch top categories: %s", e)
    
    # Fetch diverse picks (random selection to ensure variety).
    try:
        diverse_sql = """
            SELECT id, name, main_category, sub_category, image,
                   discount_price, actual_price, ratings, no_of_ratings, discount_ratio
            FROM products
            ORDER BY RANDOM()
            LIMIT :limit
        """
        diverse = await run_in_threadpool(fetch_products, diverse_sql, {"limit": response_limit})
        recommendations["diverse_picks"] = diverse
    except Exception as e:
        logger.error("Failed to fetch diverse picks: %s", e)
    
    return recommendations

@router.get("/product/{product_id}", response_model=Dict[str, List[Dict[str, Any]]])
async def get_product_recommendations(
    product_id: str = Path(..., regex=r"^[A-Z0-9]{10}$"),
    response_limit: int = Query(20, ge=1, le=60)
):
    """
    Retrieve products similar to the given product_id using a content-based approach.
    """
    try:
        content_model = ContentModel(model_dir="model")
        similar = content_model.get_similar_products(product_id, top_n=response_limit)
        if not similar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No similar products found"
            )

        # Extract the list of recommended product IDs
        similar_ids = [item["id"] for item in similar]

        # Fetch the complete product details from the database
        from sqlalchemy import create_engine, text
        import os

        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")
        engine = create_engine(DATABASE_URL)

        query = text("""
            SELECT id, name, main_category, sub_category, image,
                   discount_price, actual_price, ratings, no_of_ratings, discount_ratio
            FROM products
            WHERE id = ANY(:ids)
        """)

        with engine.connect() as conn:
            result = conn.execute(query, {"ids": similar_ids})
            rows = result.fetchall()

        product_details = []
        for row in rows:
            product_details.append({
                "id": row["id"],
                "name": row["name"],
                "category": f"{row['main_category']} > {row['sub_category']}",
                "image": row["image"],
                "price": float(row["discount_price"]) if row["discount_price"] is not None else None,
                "original_price": float(row["actual_price"]) if row["actual_price"] is not None else None,
                "rating": float(row["ratings"]) if row["ratings"] is not None else None,
                "reviews": row["no_of_ratings"],
                "discount_ratio": float(row["discount_ratio"]) if row["discount_ratio"] is not None else None,
            })

        return {"similar": product_details}
    except Exception as e:
        logger.error("Error fetching similar products: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch similar products"
        )

@router.get("/search", response_model=Dict[str, Any])
async def search_recommendations(
    query: str = Query(..., min_length=1, max_length=255),
    response_limit: int = Query(200, ge=1, le=6000)
):
    """
    Search for products using a query with query expansion.
    Returns:
      - results: List of matched products.
      - fallback_reason: (Optional) set to 'no_search_matches' if no direct matches are found.
    """
    from services.search import search_products  # Import local search function
    try:
        query_trimmed = query.strip()
        if not query_trimmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Empty search query"
            )
        
        results = search_products(query_trimmed, response_limit)
        if not results:
            # Fallback to trending products.
            trending_sql = """
                SELECT id, name, main_category, sub_category, image,
                       discount_price, actual_price, ratings, no_of_ratings, discount_ratio
                FROM products
                ORDER BY ratings DESC, no_of_ratings DESC
                LIMIT :limit
            """
            results = fetch_products(trending_sql, {"limit": response_limit})
            return {"results": results, "fallback_reason": "no_search_matches"}
        return {"results": results}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("Search endpoint error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Search failed"
        )