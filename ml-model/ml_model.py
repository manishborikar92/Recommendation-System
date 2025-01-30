# ---------- ml_model.py ----------
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_union
from sklearn.compose import ColumnTransformer
import pandas as pd
import joblib

class RecommendationModel:
    def __init__(self):
        self.product_model = None
        self.feature_union = None
        
    def _create_feature_pipeline(self):
        text_pipeline = TfidfVectorizer(
            stop_words='english', 
            max_features=500,
            lowercase=True
        )
        numeric_features = ['ratings', 'discount_ratio', 'no_of_ratings']
        
        return make_union(
            ColumnTransformer(
                [('text', text_pipeline, 'name')],
                remainder='drop'  # Explicitly drop other columns
            ),
            ColumnTransformer(
                [('numeric', StandardScaler(), numeric_features)],
                remainder='drop'
            )
        )
        
    def train(self, products_df):
        # Ensure proper data types
        products_df = products_df.astype({
            'ratings': 'float32',
            'discount_ratio': 'float32',
            'no_of_ratings': 'float32'
        })
        
        # Create feature pipeline
        self.feature_union = self._create_feature_pipeline()
        features = self.feature_union.fit_transform(products_df)
        
        # Train model
        self.product_model = NearestNeighbors(
            n_neighbors=50, 
            metric='cosine', 
            algorithm='brute'
        )
        self.product_model.fit(features)
        
        joblib.dump(self, 'recommendation_model.pkl')

    def get_similar_products(self, product_id, products_df):
        try:
            # Filter to relevant features
            product_data = products_df[products_df['id'] == product_id]
            if product_data.empty:
                return []
                
            features = self.feature_union.transform(
                product_data[['name', 'ratings', 'discount_ratio', 'no_of_ratings']]
            )
            distances, indices = self.product_model.kneighbors(features)
            return products_df.iloc[indices[0]]['id'].tolist()
        except Exception as e:
            print(f"Similarity error: {str(e)}")
            return []