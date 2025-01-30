# ---------- data_loader.py ----------
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

def load_data(csv_path, db_url):
    engine = create_engine(db_url)
    
    chunks = pd.read_csv(csv_path, chunksize=1000, 
                        converters={'id': lambda x: str(x)[:10]})
    
    for chunk in chunks:
        chunk = chunk.drop_duplicates(subset=['id'])
        chunk['discount_ratio'] = (chunk['actual_price'] - chunk['discount_price']) / chunk['actual_price']
        chunk['discount_ratio'] = chunk['discount_ratio'].fillna(0).round(2)
        
        chunk.to_sql('products', engine, 
                    if_exists='append', 
                    index=False,
                    method='multi')
        
if __name__ == "__main__":
    load_data("data/processed/Amazon-Products-Optimized.csv", 
             "postgresql://avnadmin:AVNS_OYtoI3VOGPep8jW6PgI@recommendation-system-theodinproject0622-f277.b.aivencloud.com:15032/defaultdb?sslmode=require")