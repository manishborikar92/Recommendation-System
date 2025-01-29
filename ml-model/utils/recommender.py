import os
import json
import pickle
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)

class ProductRecommender:
    def __init__(self):
        """Initialize the recommendation system."""
        self.data = None
        self.product_features_matrix = None
        self.product_ids = None
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.scaler = MinMaxScaler()
        self.required_columns = [
            'product_id', 'product_name', 'category', 'discounted_price',
            'actual_price', 'discount_percentage', 'rating', 'rating_count',
            'about_product', 'img_link', 'product_features'
        ]
    
    def validate_input_data(self, df: pd.DataFrame) -> None:
        """Validate that input DataFrame contains all required columns."""
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"Input DataFrame is missing required columns: {missing_columns}\n"
                f"Required columns are: {self.required_columns}"
            )
    
    def clean_numeric_value(self, value):
        """Clean numeric values by removing commas and converting to float."""
        if isinstance(value, str):
            try:
                return float(value.replace(',', ''))
            except (ValueError, AttributeError):
                return 0.0
        elif pd.isna(value):
            return 0.0
        return float(value)
        
    def preprocess_data(self, df: pd.DataFrame) -> None:
        """Preprocess the data and create feature matrix."""
        self.validate_input_data(df)
        self.data = df.copy()
        
        # Clean numerical features and update self.data
        numerical_features = [
            'discounted_price', 'actual_price',
            'discount_percentage', 'rating', 'rating_count'
        ]
        numerical_data = pd.DataFrame()
        for feature in numerical_features:
            numerical_data[feature] = self.data[feature].apply(self.clean_numeric_value)
        
        # Update self.data with cleaned numerical values
        self.data[numerical_features] = numerical_data
        
        # Process text features
        def process_features(features):
            if isinstance(features, str):
                try:
                    features_dict = json.loads(features)
                    return ' '.join([str(v) for v in features_dict.values()])
                except:
                    return features
            return str(features)
        
        self.data['text_features'] = (
            self.data['product_name'].fillna('') + ' ' +
            self.data['category'].fillna('') + ' ' +
            self.data['about_product'].fillna('') + ' ' +
            self.data['product_features'].apply(process_features)
        )
        
        # TF-IDF and numerical feature processing
        text_matrix = self.tfidf_vectorizer.fit_transform(self.data['text_features'])
        scaled_numerical = self.scaler.fit_transform(numerical_data)
        self.product_features_matrix = np.hstack([text_matrix.toarray(), scaled_numerical])
        self.product_ids = self.data['product_id'].values
    
    def get_enhanced_product_recommendations(
        self, 
        category_limit: int = 10, 
        products_per_category: int = 10, 
        overall_limit: int = 20, 
        similar_products_limit: int = 5
    ) -> Dict[str, any]:
        """
        Enhanced product recommendations with composite scoring and intelligent sampling.
        """
        self._validate_parameters(category_limit, products_per_category, overall_limit, similar_products_limit)
        
        if not isinstance(self.data, pd.DataFrame):
            logger.error("Product data is missing or invalid.")
            raise ValueError("Product data not available")

        required_features = {'rating', 'rating_count', 'discount_percentage', 'discounted_price'}
        missing_features = required_features - set(self.data.columns)
        if missing_features:
            raise ValueError(f"Missing required features in data: {missing_features}")

        try:
            processed_data = self.data.copy()
            processed_data = self._calculate_composite_scores(processed_data)

            return {
                'overall_top_products': self._get_overall_top_products(processed_data, overall_limit),
                'top_products_by_category': self._get_category_top_products(processed_data, category_limit, products_per_category),
                'similar_products': self._get_similar_products(processed_data, category_limit, similar_products_limit)
            }
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            raise

    def _validate_parameters(self, category_limit: int, products_per_category: int, overall_limit: int, similar_products_limit: int) -> None:
        """Ensure input parameters are within valid ranges."""
        limits = [category_limit, products_per_category, overall_limit, similar_products_limit]
        if not all(isinstance(x, int) and x > 0 for x in limits):
            raise ValueError("All limits must be positive integers")
        if category_limit > 50 or products_per_category > 20 or overall_limit > 100:
            raise ValueError("Exceeded maximum allowed limit values")

    def _calculate_composite_scores(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate composite scores with weighted features."""
        feature_weights = {'rating': 0.4, 'rating_count': 0.3, 'discount_percentage': 0.2, 'discounted_price': 0.1}
        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(data[list(feature_weights.keys())])
        scaled_features[:, list(feature_weights.keys()).index('discounted_price')] = 1 - scaled_features[:, list(feature_weights.keys()).index('discounted_price')]
        data['composite_score'] = np.dot(scaled_features, np.array(list(feature_weights.values())))
        return data

    def _get_overall_top_products(self, data: pd.DataFrame, limit: int) -> List[Dict]:
        """Get top products across all categories."""
        return data.sort_values('composite_score', ascending=False).head(limit)[list(self._selected_columns())].to_dict('records')

    def _get_category_top_products(self, data: pd.DataFrame, category_limit: int, products_per_category: int) -> Dict[str, List[Dict]]:
        """Get top products organized by category."""
        top_categories = data.groupby('category')['composite_score'].mean().sort_values(ascending=False).head(category_limit).index.tolist()
        return {category: self._get_category_products(data, category, products_per_category) for category in top_categories}

    def _get_category_products(self, data: pd.DataFrame, category: str, limit: int) -> List[Dict]:
        """Get top products for a specific category."""
        return data[data['category'] == category].sort_values('composite_score', ascending=False).head(limit)[list(self._selected_columns())].to_dict('records')

    def _get_similar_products(self, data: pd.DataFrame, category_limit: int, limit: int) -> Dict[str, List[Dict]]:
        """Get context-aware similar products."""
        similar_products = {}
        top_categories = data['category'].value_counts().head(category_limit).index.tolist()
        for category in top_categories:
            try:
                seed_product = data[data['category'] == category].nlargest(1, 'composite_score').iloc[0]
                recommendations = self.find_similar_products(seed_product['product_id'])
                similar = [p for p in recommendations if p[0] != seed_product['product_id'] and self._get_product_category(p[0]) == category][:limit]
                similar_products[category] = self._get_product_details([p[0] for p in similar])
            except (IndexError, KeyError):
                logger.warning(f"No products found for category: {category}")
                similar_products[category] = []
        return similar_products

    def _selected_columns(self) -> set:
        """Columns to include in output."""
        return {'product_id', 'product_name', 'category', 'discounted_price', 'actual_price', 'discount_percentage', 'rating', 'rating_count', 'about_product', 'img_link'}

    def _get_product_category(self, product_id: str) -> str:
        """Helper to get category for a product ID."""
        result = self.data[self.data['product_id'] == product_id]
        if not result.empty:
            return result.iloc[0]['category']
        raise KeyError(f"Product ID {product_id} not found.")

    def _get_product_details(self, product_ids: List[str]) -> List[Dict]:
        """Retrieve details for a list of product IDs."""
        return self.data[self.data['product_id'].isin(product_ids)][list(self._selected_columns())].to_dict('records')

        
    def find_similar_products(self, product_id: str, n_recommendations: int = 12) -> List[Tuple[str, float]]:
        """Find similar products based on product ID."""
        try:
            # Find the index of the target product
            product_idx = np.where(self.product_ids == product_id)[0][0]
            
            # Calculate similarity scores
            similarity_scores = cosine_similarity(
                self.product_features_matrix[product_idx].reshape(1, -1),
                self.product_features_matrix
            )[0]
            
            # Get indices of top similar products (excluding the input product)
            similar_indices = similarity_scores.argsort()[::-1][1:n_recommendations + 1]
            
            # Return product IDs and similarity scores
            recommendations = [
                (self.product_ids[idx], similarity_scores[idx])
                for idx in similar_indices
            ]
            
            return recommendations
            
        except Exception as e:
            print(f"Error finding similar products: {str(e)}")
            return []
    
    def get_product_details(self, product_ids: List[str]) -> pd.DataFrame:
        """Get detailed information for recommended products."""
        return self.data[self.data['product_id'].isin(product_ids)][
            [   'product_id', 'product_name', 'category', 'discounted_price',
                'actual_price', 'discount_percentage', 'rating', 'rating_count',
                'about_product', 'img_link']
        ]
    
    def save_model(self, filepath: str) -> None:
        """Save the trained model to a file."""
        model_data = {
            'product_features_matrix': self.product_features_matrix,
            'product_ids': self.product_ids,
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'scaler': self.scaler,
            'data': self.data
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str) -> None:
        """Load a trained model from a file."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.product_features_matrix = model_data['product_features_matrix']
        self.product_ids = model_data['product_ids']
        self.tfidf_vectorizer = model_data['tfidf_vectorizer']
        self.scaler = model_data['scaler']
        self.data = model_data['data']

def main():
    try:
        # Load the preprocessed data
        csv_file_path = "data/processed/cleaned_data.csv"  # Replace with your CSV file path
        df = pd.read_csv(csv_file_path)
        
        # Initialize the recommender system
        recommender = ProductRecommender()
        print("Preprocessing data...")
        recommender.preprocess_data(df)
        
        # Create model directory if it doesn't exist
        os.makedirs('model', exist_ok=True)
        
        # Save the trained model
        print("Saving model...")
        recommender.save_model('model/product_recommender_model.pkl')
        
        # # Example: Get recommendations for a product
        # example_product_id = "B095RTJH1M"
        # print(f"\nFinding recommendations for product ID: {example_product_id}")
        # recommendations = recommender.find_similar_products(example_product_id)
        
        # if recommendations:
        #     print(f"\nTop 10 similar products for product ID {example_product_id}:")
        #     recommended_ids = [rec[0] for rec in recommendations]
        #     recommended_products = recommender.get_product_details(recommended_ids)
            
        #     for (prod_id, similarity), (_, row) in zip(recommendations, recommended_products.iterrows()):
        #         print(f"\nProduct ID: {prod_id}")
        #         print(f"Similarity Score: {similarity:.4f}")
        #         print(f"Name: {row['product_name']}")
        #         print(f"Category: {row['category']}")
        #         print(f"Price: ${row['discounted_price']}")
        #         print(f"Rating: {row['rating']} ({row['rating_count']} reviews)")
                
    except FileNotFoundError:
        print(f"Error: Could not find the CSV file at {csv_file_path}")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()