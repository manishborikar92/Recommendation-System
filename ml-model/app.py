from flask import Flask, request, jsonify
from pymongo import MongoClient
import pandas as pd
from utils.recommender import ProductRecommender

app = Flask(__name__)

# Load the model at startup
recommender = ProductRecommender()
recommender.load_model('model/product_recommender_model.pkl')

def get_product_recommendations(product_id: str, recommender: ProductRecommender) -> list:
    """Get formatted recommendations for a product."""
    recommendations = recommender.find_similar_products(product_id)
    if not recommendations:
        return []
    
    recommended_ids = [rec[0] for rec in recommendations]
    details = recommender.get_product_details(recommended_ids)
    
    formatted_recommendations = []
    for (_, similarity), (_, product) in zip(recommendations, details.iterrows()):

        formatted_recommendations.append({
            'product_id': product['product_id'],
            'product_name': product['product_name'],
            'category': product['category'],
            'discounted_price': product['discounted_price'],
            'actual_price': product['actual_price'],
            'discount_percentage': product['discount_percentage'],
            'rating': product['rating'],
            'rating_count': product['rating_count'],
            'about_product': product['about_product'],
            'img_link': product['img_link'],
            'similarity_score': round(similarity, 4),
        })
    
    return formatted_recommendations

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    username = data["username"]
    product_id = data["product_id"]
    print(f"Received recommendation request for user {username} and product ID {product_id}")

    recommendations = get_product_recommendations(product_id, recommender)
    # recommendations = recommender.find_similar_products(product_id)

    return jsonify({"recommended_products": recommendations})

if __name__ == "__main__":
    app.run(port=5001, debug=True)
