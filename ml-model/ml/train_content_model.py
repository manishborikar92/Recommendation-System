# ml/train_content_model.py

import os
import logging
import numpy as np
import pandas as pd
import joblib
from sqlalchemy import create_engine
import faiss
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.decomposition import TruncatedSVD

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ContentRecommender:
    """Trains and saves optimized content-based recommendation model"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.product_ids = None
        self.preprocessor = None
        self.index = None

    def load_data(self) -> pd.DataFrame:
        """Load product data from the database."""
        logger.info("Loading data from database...")
        engine = create_engine(self.database_url, future=True)

        query = """
            SELECT id, name, main_category, sub_category, 
                ratings, no_of_ratings, discount_ratio, actual_price 
            FROM products
        """

        with engine.connect() as connection:
            # Get the underlying DBAPI connection (which provides .cursor())
            raw_conn = connection.connection
            df = pd.read_sql(query, raw_conn)

        return df

    def create_features(self, df: pd.DataFrame) -> None:
        """Feature engineering with optimized pipelines"""
        logger.info("Creating optimized features...")
        
        # Create combined category feature
        df['category'] = df['main_category'] + '_' + df['sub_category']
        
        # Text processing pipeline (memory-efficient)
        text_pipeline = Pipeline([
            ('hasher', HashingVectorizer(n_features=2**18, stop_words='english')),
            ('svd', TruncatedSVD(n_components=100, random_state=42))
        ])
        
        # Numerical pipeline
        num_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        # Categorical pipeline (sparse)
        cat_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('ohe', OneHotEncoder(sparse_output=True, handle_unknown='ignore'))
        ])
        
        # Column transformer
        self.preprocessor = ColumnTransformer([
            ('text', text_pipeline, 'name'),
            ('num', num_pipeline, ['ratings', 'no_of_ratings', 'discount_ratio', 'actual_price']),
            ('cat', cat_pipeline, ['category'])
        ], sparse_threshold=0.8)
        
        # Transform data
        features = self.preprocessor.fit_transform(df)
        
        # Convert to dense float32 for FAISS
        if not isinstance(features, np.ndarray):
            features = features.toarray()
        features = features.astype('float32')
        
        # Normalize for cosine similarity
        faiss.normalize_L2(features)
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(features.shape[1])
        self.index.add(features)
        self.product_ids = df['id'].values

    def save_model(self, output_dir: str = 'model') -> None:
        """Save model components"""
        os.makedirs(output_dir, exist_ok=True)
        faiss.write_index(self.index, os.path.join(output_dir, 'faiss_index.index'))
        np.save(os.path.join(output_dir, 'product_ids.npy'), self.product_ids)
        joblib.dump(self.preprocessor, os.path.join(output_dir, 'preprocessor.joblib'))
        logger.info(f"Model saved to {output_dir} (Size: {self._get_model_size(output_dir)/1024/1024:.2f} MB)")

    def _get_model_size(self, path: str) -> int:
        """Calculate model directory size"""
        return sum(os.path.getsize(os.path.join(path, f)) 
                 for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))

# if __name__ == "__main__":
#     DATABASE_URL = os.getenv('DATABASE_URL')
    
#     trainer = ContentRecommender(DATABASE_URL)
#     df = trainer.load_data()
#     trainer.create_features(df)
#     trainer.save_model()