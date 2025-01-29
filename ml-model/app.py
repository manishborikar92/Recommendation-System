from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.recommender import ProductRecommender
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the model at startup
try:
    recommender = ProductRecommender()
    recommender.load_model('model/product_recommender_model.pkl')
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    raise  # Ensures the app doesn't start without the model

def get_product_recommendations(product_id: str, recommender: ProductRecommender) -> list:
    """Get formatted recommendations for a product."""
    recommendations = recommender.find_similar_products(product_id)
    if not recommendations:
        return []
    
    # Extract recommended product IDs and similarities
    recommended_ids = [rec[0] for rec in recommendations]
    details = recommender.get_product_details(recommended_ids)
    
    # Create a lookup dictionary for product details
    product_map = {row['product_id']: row for _, row in details.iterrows()}
    
    formatted_recommendations = []
    for product_id, similarity in recommendations:
        product = product_map.get(product_id)
        if product is None:
            continue  # Skip products without details
            
        formatted_recommendations.append({
            'product_id': product_id,
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
    """Endpoint for product recommendations"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.json
    product_id = data.get("product_id")
    
    if not product_id:
        return jsonify({"error": "Missing product_id parameter"}), 400
    
    logger.info(f"Received recommendation request for product ID {product_id}")
    
    try:
        recommendations = get_product_recommendations(product_id, recommender)
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    
    if not recommendations:
        return jsonify({"error": "No recommendations found"}), 404
        
    return jsonify({"recommended_products": recommendations})

@app.route("/trending", methods=["GET"])
def get_trending_products():
    """Endpoint for trending products"""
    try:
        recommendations = recommender.get_enhanced_product_recommendations()
        
        return jsonify({
            "overall_top": recommendations.get('overall_top_products', []),
            "category_top": recommendations.get('top_products_by_category', []),
            "similar_products": recommendations.get('similar_products', [])
        })
    except Exception as e:
        logger.error(f"Trending products error: {str(e)}")
        return jsonify({"error": "Failed to fetch trending products"}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)