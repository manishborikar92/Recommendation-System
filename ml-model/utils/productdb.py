import pandas as pd
from pymongo import MongoClient
from typing import Dict, Any
import json, os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

class ProductDatabase:
    def __init__(self, connection_string: str = MONGO_URI):
        """Initialize MongoDB connection and create database/collection."""
        self.client = MongoClient(connection_string)
        self.db = self.client['product_database']
        self.collection = self.db['products']
        
        # Create index on product_id for faster queries
        self.collection.create_index('product_id', unique=True)

    def import_csv(self, file_path: str) -> None:
        """Import data from CSV file into MongoDB."""
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Select only the required columns
            selected_columns = [
                'product_id', 'product_name', 'category',
                'discounted_price', 'actual_price', 'discount_percentage',
                'rating', 'rating_count', 'about_product',
                'img_link', 'product_features'
            ]

            # Convert selected data to dictionary format
            products = df[selected_columns].to_dict('records')
            
            # Insert data into MongoDB
            for product in products:
                # Convert numeric strings to float where appropriate
                for field in ['discounted_price', 'actual_price', 'discount_percentage', 'rating']:
                    if isinstance(product[field], str):
                        try:
                            product[field] = float(product[field].replace(',', ''))
                        except (ValueError, AttributeError):
                            pass
                
                # Convert rating_count to integer
                if isinstance(product['rating_count'], str):
                    try:
                        product['rating_count'] = int(product['rating_count'].replace(',', ''))
                    except (ValueError, AttributeError):
                        pass
                
                # Handle product_features if it's a string representation of a list/dict
                if isinstance(product['product_features'], str):
                    try:
                        product['product_features'] = json.loads(product['product_features'])
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                # Use upsert to avoid duplicates
                self.collection.update_one(
                    {'product_id': product['product_id']},
                    {'$set': product},
                    upsert=True
                )
            
            print(f"Successfully imported {len(products)} products to MongoDB")
            
        except Exception as e:
            print(f"Error importing data: {str(e)}")

    def get_product_by_id(self, product_id: str) -> Dict[str, Any]:
        """Retrieve product information by product_id."""
        try:
            product = self.collection.find_one({'product_id': product_id})
            if product:
                # Remove MongoDB's _id field from the result
                product.pop('_id', None)
                return product
            return None
        except Exception as e:
            print(f"Error retrieving product: {str(e)}")
            return None

    def close_connection(self):
        """Close the MongoDB connection."""
        self.client.close()

def main():
    # Example usage
    # Initialize database connection
    db = ProductDatabase()
    
    # Import data from CSV
    csv_file_path = "data/processed/preprocessed_data.csv"  # Replace with your CSV file path
    # db.import_csv(csv_file_path)
    
    # Example: Retrieve product by ID
    product_id = "B08L12N5H1"  # Replace with actual product ID
    product = db.get_product_by_id(product_id)
    
    if product:
        print("Product found:")
        print(json.dumps(product, indent=2))
    else:
        print("Product not found")
    
    # Close connection
    db.close_connection()

if __name__ == "__main__":
    main()