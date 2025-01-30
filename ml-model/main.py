# ---------- main.py ----------
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List  # Added import
import pandas as pd
import database
import ml_model
import joblib
import time

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    products = db.query(database.Product).all()
    products_df = pd.DataFrame([{
        'id': p.id,
        'name': p.name,
        'ratings': p.ratings,
        'discount_ratio': p.discount_ratio,
        'no_of_ratings': p.no_of_ratings
    } for p in products])
    
    try:
        app.state.model = joblib.load('recommendation_model.pkl')
    except:
        app.state.model = ml_model.RecommendationModel()
        app.state.model.train(products_df)
    
    app.state.products_df = products_df
    db.close()
    print("Model loaded successfully")

def _get_user_history(db: Session, user_id: str) -> List[str]:  # Now valid
    return [
        h.product_id for h in db.query(database.UserHistory.product_id)
        .filter(database.UserHistory.user_id == user_id)
        .distinct()
    ]

def _log_recommendations(db: Session, user_id: str, product_ids: List[str]):
    try:
        history_entries = [
            database.UserHistory(
                user_id=user_id,
                product_id=pid,
                interaction_type='recommended'
            ) for pid in product_ids
        ]
        db.bulk_save_objects(history_entries)
        db.commit()
    except Exception as e:
        db.rollback()

@app.get("/recommend", response_model=List[dict])
async def recommend(user_id: str, db: Session = Depends(get_db)):
    start_time = time.time()
    model = app.state.model
    products_df = app.state.products_df
    
    try:
        # Get user interaction history
        interacted_products = _get_user_history(db, user_id)
        recommendations = []
        
        if not interacted_products:
            # New user strategy
            products = db.query(database.Product).order_by(
                database.Product.ratings.desc(),
                database.Product.no_of_ratings.desc()
            ).limit(40).all()
            recommendations = [p.id for p in products]
        else:
            # Hybrid recommendation strategy
            seen_products = set(interacted_products)
            similar_products = []
            
            # Get similar products from history
            for pid in interacted_products[-5:]:  # Consider last 5 interactions
                similar_products += model.get_similar_products(pid, products_df)
                
            # Diversity sampling
            unique_similar = list(set(similar_products) - seen_products)
            recommendations = unique_similar[:20] if len(unique_similar) >= 20 else unique_similar
            
            # Fallback to popular items if needed
            if len(recommendations) < 20:
                popular = db.query(database.Product.id).order_by(
                    database.Product.no_of_ratings.desc()
                ).limit(40 - len(recommendations)).all()
                recommendations += [p.id for p in popular if p.id not in seen_products]
            
            recommendations = recommendations[:40]

        # Get full product details
        products = db.query(database.Product).filter(
            database.Product.id.in_(recommendations[:20])
        ).all()
        
        # Log recommendations
        _log_recommendations(db, user_id, [p.id for p in products])
        
        return [{
            "id": p.id,
            "name": p.name,
            "main_category": p.main_category,
            "sub_category": p.sub_category,
            "image": p.image,
            "link": p.link,
            "ratings": p.ratings,
            "no_of_ratings": p.no_of_ratings,
            "discount_price": p.discount_price,
            "actual_price": p.actual_price
        } for p in products]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print(f"Recommendation time: {time.time() - start_time:.2f}s")

@app.get("/similar", response_model=List[dict])
async def similar_products(product_id: str, db: Session = Depends(get_db)):
    model = app.state.model
    products_df = app.state.products_df
    
    try:
        similar_ids = model.get_similar_products(product_id, products_df)[:12]
        products = db.query(database.Product).filter(
            database.Product.id.in_(similar_ids)
        ).all()
        
        return [{
            "id": p.id,
            "name": p.name,
            "main_category": p.main_category,
            "sub_category": p.sub_category,
            "image": p.image,
            "link": p.link,
            "ratings": p.ratings,
            "no_of_ratings": p.no_of_ratings,
            "discount_price": p.discount_price,
            "actual_price": p.actual_price
        } for p in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))