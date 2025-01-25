import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoTokenizer, AutoModel
import torch
import joblib

def preprocess_reviews(raw_path: str = "data/raw/amazon_reviews.csv"):
    # Load data with Windows path compatibility
    df = pd.read_csv(raw_path)
    
    # Clean data
    df = df.dropna(subset=["user_id", "product_id", "rating", "about_product"])
    df = df.drop_duplicates(subset=["user_id", "product_id", "review_id"])
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").clip(1, 5)
    
    # Generate BERT embeddings for content features
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    model = AutoModel.from_pretrained("bert-base-uncased")
    
    def bert_embed(texts):
        inputs = tokenizer(texts.tolist(), return_tensors="pt", padding=True, truncation=True, max_length=128)
        with torch.no_grad():
            outputs = model(**inputs).last_hidden_state.mean(dim=1)
        return outputs.numpy()
    
    # Content features
    df["content_embedding"] = bert_embed(df["about_product"] + " " + df["review_content"]).tolist()
    
    # Categorical features
    tfidf = TfidfVectorizer(max_features=100)
    category_emb = tfidf.fit_transform(df["category"]).toarray()
    df["category_embedding"] = [row for row in category_emb]
    
    # Collaborative features
    user_item_matrix = pd.pivot_table(
        df,
        index="user_id",
        columns="product_id", 
        values="rating",
        fill_value=0
    )
    
    # Split data ensuring no user overlap
    users = df["user_id"].unique()
    train_users, test_users = train_test_split(users, test_size=0.2, random_state=42)
    val_users, test_users = train_test_split(test_users, test_size=0.5, random_state=42)
    
    splits = {}
    for split_name, user_subset in [("train", train_users), ("val", val_users), ("test", test_users)]:
        # Filter users present in both the subset and user_item_matrix
        valid_users = [user for user in user_subset if user in user_item_matrix.index]
        
        split_data = df[df["user_id"].isin(valid_users)]
        splits[split_name] = {
            "data": split_data,
            "user_item_matrix": user_item_matrix.loc[valid_users]
        }
        
        # Create directories and save files
        os.makedirs(f"data/processed/{split_name}", exist_ok=True)
        split_data.to_parquet(f"data/processed/{split_name}/data.parquet")
        np.save(f"data/processed/{split_name}/content_embeddings.npy", np.vstack(split_data["content_embedding"]))
        np.save(f"data/processed/{split_name}/category_embeddings.npy", np.vstack(split_data["category_embedding"]))
    
    # Save TF-IDF model for inference
    joblib.dump(tfidf, "data/processed/tfidf_vectorizer.joblib")
    
    print("Preprocessing completed successfully!")

if __name__ == "__main__":
    preprocess_reviews()