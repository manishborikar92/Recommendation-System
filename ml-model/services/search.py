"""
services/search.py

This module provides search functionality with query expansion for the recommendation system.
It performs a robust case-insensitive search on the products catalog using expanded query tokens.
If no products match the query, the caller may fall back to other recommendation strategies.
"""

import os
import logging
import re
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

# Predefined synonyms for query expansion.
SYNONYMS = {
    "earbuds": "earphones",
    "tv": "television",
    "laptop": "notebook",
    "cellphone": "mobile",
    "smartphone": "mobile",
    # Add additional synonyms as needed.
}

def expand_query(query: str) -> str:
    """
    Expand the input query using predefined synonyms.
    
    Each word is checked against the synonyms dictionary;
    if a synonym exists, it is substituted.
    
    Args:
        query (str): The original search query.
        
    Returns:
        str: The expanded search query.
    """
    words = query.split()
    expanded_words = []
    for word in words:
        lower_word = word.lower()
        if lower_word in SYNONYMS:
            expanded_words.append(SYNONYMS[lower_word])
        else:
            expanded_words.append(word)
    return " ".join(expanded_words)

def search_products(query: str, response_limit: int = 20) -> list:
    """
    Search for products in the catalog based on the provided query.
    
    This function performs the search on the 'name' field of products by:
      1. Expanding the query using synonyms.
      2. Tokenizing the expanded query.
      3. Building a compound WHERE clause with ILIKE for each token (joined by AND),
         ensuring that all words must appear in the product name.
    
    Each returned product dictionary includes:
        - id
        - name
        - category (formatted as "main_category > sub_category")
        - image
        - price (discount_price)
        - original_price (actual_price)
        - rating (ratings)
        - reviews (no_of_ratings)
        - discount_ratio

    Args:
        query (str): The search query.
        response_limit (int): Maximum number of products to return.
        
    Returns:
        list: A list of product dictionaries that match the query.
    """
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")
    try:
        engine = create_engine(DATABASE_URL)
        expanded_query = expand_query(query)
        # Tokenize the expanded query
        tokens = re.split(r"\s+", expanded_query.strip().lower())
        if not tokens:
            return []
        
        # Build conditions for each token using ILIKE.
        conditions = []
        params = {}
        for i, token in enumerate(tokens):
            conditions.append("name ILIKE :token{}".format(i))
            params["token{}".format(i)] = f"%{token}%"
        params["limit"] = response_limit
        
        where_clause = " AND ".join(conditions)
        sql_statement = text(f"""
            SELECT id, name, main_category, sub_category, image,
                   discount_price, actual_price, ratings, no_of_ratings, discount_ratio
            FROM products
            WHERE {where_clause}
            LIMIT :limit
        """)
        
        with engine.connect() as conn:
            result = conn.execute(sql_statement, params)
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
        logger.exception("Search query failed: %s", e)
        raise
