"""
data_pipeline.py - Ingests and preprocesses Amazon Reviews data for recommendation systems
"""
import os
import json
import argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoTokenizer, AutoModel
import torch
import dvc.api

# Configuration
CONFIG = {
    "data_path": "data/raw/Electronics.json",
    "output_dir": "data/processed",
    "min_interactions": 5,
    "test_size": 0.2,
    "batch_size": 32,
    "seed": 42,
    "bert_model": "distilbert-base-uncased",
    "tfidf_features": 300,
    "embedding_dim": 768
}

def load_data(file_path: str) -> pd.DataFrame:
    """Load JSON data from Amazon dataset"""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return pd.DataFrame(data)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Data cleaning pipeline"""
    # Keep essential columns
    df = df[['reviewerID', 'asin', 'overall', 'summary', 'category', 'unixReviewTime']]
    df = df.rename(columns={
        'reviewerID': 'user_id',
        'asin': 'item_id',
        'overall': 'rating',
        'summary': 'title',
        'unixReviewTime': 'timestamp'
    })

    # Handle missing values
    df = df.dropna(subset=['user_id', 'item_id', 'rating'])
    df['title'] = df['title'].fillna('')
    df['category'] = df['category'].fillna('')

    # Deduplicate interactions
    df = df.sort_values('timestamp').drop_duplicates(
        subset=['user_id', 'item_id'], 
        keep='last'
    )

    # Filter inactive users/items
    user_counts = df['user_id'].value_counts()
    item_counts = df['item_id'].value_counts()
    
    df = df[
        df['user_id'].isin(user_counts[user_counts >= CONFIG['min_interactions']].index) &
        df['item_id'].isin(item_counts[item_counts >= CONFIG['min_interactions']].index)
    ]
    
    return df

def split_data(df: pd.DataFrame) -> tuple:
    """Temporal train/validation/test split"""
    df = df.sort_values('timestamp')
    
    # First split: 80% train, 20% temp
    train_df, temp_df = train_test_split(
        df, 
        test_size=CONFIG['test_size'], 
        stratify=df['user_id'],
        random_state=CONFIG['seed']
    )
    
    # Second split: 10% validation, 10% test
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,
        stratify=temp_df['user_id'],
        random_state=CONFIG['seed']
    )
    
    return train_df, val_df, test_df

def generate_features(train_df: pd.DataFrame) -> dict:
    """Generate feature embeddings and matrices"""
    # Initialize BERT model
    tokenizer = AutoTokenizer.from_pretrained(CONFIG['bert_model'])
    model = AutoModel.from_pretrained(CONFIG['bert_model'])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    
    # Generate BERT embeddings in batches
    title_embeddings = []
    for i in range(0, len(train_df), CONFIG['batch_size']):
        batch_texts = train_df['title'].iloc[i:i+CONFIG['batch_size']].tolist()
        inputs = tokenizer(
            batch_texts,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=128
        ).to(device)
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        batch_embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        title_embeddings.append(batch_embeddings)
    
    title_embeddings = np.concatenate(title_embeddings)
    
    # Generate TF-IDF features
    tfidf = TfidfVectorizer(max_features=CONFIG['tfidf_features'])
    category_embeddings = tfidf.fit_transform(train_df['category']).toarray()
    
    # Create user-item matrix
    user_to_idx = {user: idx for idx, user in enumerate(train_df['user_id'].unique())}
    item_to_idx = {item: idx for idx, item in enumerate(train_df['item_id'].unique())}
    
    return {
        'title_embeddings': title_embeddings,
        'category_embeddings': category_embeddings,
        'user_map': user_to_idx,
        'item_map': item_to_idx,
        'tfidf_vectorizer': tfidf
    }

def save_artifacts(train_df, val_df, test_df, features):
    """Save processed data and features"""
    # Create output directory
    os.makedirs(CONFIG['output_dir'], exist_ok=True)
    
    # Save datasets
    train_df.to_parquet(os.path.join(CONFIG['output_dir'], 'train.parquet'))
    val_df.to_parquet(os.path.join(CONFIG['output_dir'], 'val.parquet'))
    test_df.to_parquet(os.path.join(CONFIG['output_dir'], 'test.parquet'))
    
    # Save features
    np.save(os.path.join(CONFIG['output_dir'], 'title_embeddings.npy'), 
            features['title_embeddings'])
    np.save(os.path.join(CONFIG['output_dir'], 'category_embeddings.npy'), 
            features['category_embeddings'])
    
    # Save mappings
    pd.Series(features['user_map']).to_pickle(
        os.path.join(CONFIG['output_dir'], 'user_map.pkl')
    )
    pd.Series(features['item_map']).to_pickle(
        os.path.join(CONFIG['output_dir'], 'item_map.pkl')
    )

def main():
    # Load and process data
    print("Loading raw data...")
    raw_df = load_data(CONFIG['data_path'])
    
    print("Cleaning data...")
    clean_df = clean_data(raw_df)
    
    print("Splitting data...")
    train_df, val_df, test_df = split_data(clean_df)
    
    print("Generating features...")
    features = generate_features(train_df)
    
    print("Saving artifacts...")
    save_artifacts(train_df, val_df, test_df, features)
    
    print("Data pipeline completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Data ingestion pipeline')
    parser.add_argument('--data-path', type=str, default=CONFIG['data_path'])
    parser.add_argument('--output-dir', type=str, default=CONFIG['output_dir'])
    args = parser.parse_args()
    
    CONFIG.update(vars(args))
    main()

# python data_pipeline.py --data-path ai-ml/data/raw/Electronics.json --output-dir ai-ml/data/processed