import pandas as pd
import numpy as np

def test_data_quality():
    # Load processed data
    train_df = pd.read_parquet("data/processed/train.parquet")
    
    # Check for missing values
    assert not train_df.isnull().any().any(), "Missing values found"
    
    # Validate rating range
    assert train_df['rating'].between(1, 5).all(), "Invalid rating values"
    
    # Check interaction counts
    user_counts = train_df['user_id'].value_counts()
    assert (user_counts >= 5).all(), "Users with <5 interactions exist"

def test_embeddings():
    title_emb = np.load("data/processed/title_embeddings.npy")
    category_emb = np.load("data/processed/category_embeddings.npy")
    
    assert title_emb.shape[1] == 768, "Invalid BERT embedding dimension"
    assert category_emb.shape[1] == 300, "Invalid TF-IDF dimension"