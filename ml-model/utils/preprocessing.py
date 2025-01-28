import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

# Define file paths
RAW_DATA_PATH = "data/raw/amazon_reviews.csv"
PROCESSED_DATA_PATH = "data/processed/preprocessed_data.csv"

def load_data(file_path):
    """Load the raw dataset from the CSV file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at {file_path}")
    return pd.read_csv(file_path)

def clean_price_data(df):
    """Convert price columns to numeric values and extract the discount ratio."""
    df['discounted_price'] = df['discounted_price'].replace({'₹': '', ',': ''}, regex=True).astype(float)
    df['actual_price'] = df['actual_price'].replace({'₹': '', ',': ''}, regex=True).astype(float)
    df['discount_percentage'] = df['discount_percentage'].replace({'%': ''}, regex=True).astype(float)
    df['price_discount_ratio'] = (df['actual_price'] - df['discounted_price']) / df['actual_price']
    return df

def fill_missing_values(df):
    """Fill missing values in important columns."""
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['rating'].fillna(df['rating'].median(), inplace=False)  # Avoid in-place modification
    df['rating_count'].fillna(0, inplace=False)
    df['about_product'].fillna("No description available", inplace=False)

    if 'product_features' not in df.columns:
        print("'product_features' column is missing. Filling with empty strings.")
        df['product_features'] = ""
    else:
        df['product_features'].fillna("No features listed", inplace=False)
    
    return df

def encode_categorical_columns(df):
    """Encode categorical columns like 'category' using Label Encoding."""
    le = LabelEncoder()
    df['category_encoded'] = le.fit_transform(df['category'])
    return df

def handle_multiple_reviews(df):
    """Aggregate reviews, selecting the highest rated review for each user-product pair."""
    df = df.sort_values('rating', ascending=False).drop_duplicates(subset=['user_id', 'product_id'], keep='first')
    return df

def create_interaction_matrix(df):
    """Create a user-item interaction matrix."""
    interaction_matrix = df.pivot_table(
        index='user_id',
        columns='product_id',
        values='rating',
        fill_value=0  # Unrated items get a default value of 0
    )
    return interaction_matrix

def extract_text_features(df):
    """Extract features from product descriptions and features using TF-IDF."""
    tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['about_product'] + " " + df['product_features'])
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names_out())
    return tfidf_df

def prepare_cold_start_data(df):
    """Prepare data for cold-start recommendations (e.g., top-rated products)."""
    popular_products = df.sort_values(
        by=['rating', 'rating_count'], 
        ascending=False
    )[[  # Selecting important columns
        'product_id', 'product_name', 'category', 'discounted_price',
        'actual_price', 'discount_percentage', 'rating', 'rating_count',
        'about_product', 'img_link', 'product_features'
    ]].drop_duplicates()
    return popular_products.head(20)

def preprocess_data():
    """Master function to handle all preprocessing steps."""
    print("Loading data...")
    df = load_data(RAW_DATA_PATH)
    
    print("Cleaning price data...")
    df = clean_price_data(df)
    
    print("Filling missing values...")
    df = fill_missing_values(df)
    
    print("Handling multiple reviews per product...")
    df = handle_multiple_reviews(df)
    
    print("Encoding categorical columns...")
    df = encode_categorical_columns(df)
    
    print("Creating interaction matrix...")
    interaction_matrix = create_interaction_matrix(df)
    
    print("Extracting text features...")
    text_features = extract_text_features(df)
    
    print("Preparing cold-start data...")
    cold_start_data = prepare_cold_start_data(df)
    
    print("Saving preprocessed data...")
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    # Save the interaction matrix as CSV
    interaction_matrix.to_csv('data/processed/interaction_matrix.csv', index=True)
    
    print("Preprocessing completed.")
    return df, interaction_matrix, cold_start_data, text_features

if __name__ == "__main__":
    # Run preprocessing and save the outputs
    df, interaction_matrix, cold_start_data, text_features = preprocess_data()
    print("Processed data shape:", df.shape)
    print("Interaction matrix shape:", interaction_matrix.shape)
    print("Cold-start data sample:")
    print(cold_start_data.head())
    print("Text features shape:", text_features.shape)
