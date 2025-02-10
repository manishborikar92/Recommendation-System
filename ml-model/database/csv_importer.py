import os
import logging
import re
from sqlalchemy import create_engine, Column, String, Text, Float, Integer, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
import pandas as pd

# Ensure the logs directory exists
LOG_DIR = 'data/logs'
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging to file and console with detailed formatting
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'csv_importer.log'))
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# Define the declarative base
Base = declarative_base()

class Product(Base):
    """SQLAlchemy model for the products table."""
    __tablename__ = 'products'
    id = Column(String(10), primary_key=True)
    name = Column(Text, nullable=False)
    main_category = Column(Text, nullable=False)
    sub_category = Column(Text, nullable=False)
    image = Column(Text)
    link = Column(Text)
    ratings = Column(Float)
    no_of_ratings = Column(Integer)
    discount_price = Column(Numeric)
    actual_price = Column(Numeric)
    discount_ratio = Column(Numeric)

def validate_product_id(product_id: str) -> bool:
    """
    Validate product_id format (10 uppercase alphanumeric).
    
    Returns True if valid, else False.
    """
    return re.match(r'^[A-Z0-9]{10}$', product_id) is not None

def import_csv_to_db(csv_path: str, database_url: str, batch_size: int = 10000) -> None:
    """
    Imports CSV data into the PostgreSQL products table using bulk upload.
    
    Rows with invalid product IDs are filtered out, and insertion is performed in batches.
    The "ON CONFLICT DO NOTHING" clause is used so that rows that are already uploaded (duplicate IDs)
    are skipped.
    
    Args:
        csv_path: Path to the CSV file.
        database_url: Database connection URL.
        batch_size: Number of records to insert per batch.
    """
    session = None
    try:
        # Initialize database connection
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create tables if they do not exist
        Base.metadata.create_all(engine)
        
        # Read CSV using pandas
        df = pd.read_csv(csv_path)
        total_rows = len(df)
        logger.info(f"Loaded CSV with {total_rows} rows from '{csv_path}'.")
        
        # Validate product IDs and filter out invalid ones
        valid_mask = df['id'].apply(validate_product_id)
        if not valid_mask.all():
            invalid_indices = df.index[~valid_mask].tolist()
            for idx in invalid_indices:
                logger.warning(f"Row {idx}: Invalid product ID '{df.at[idx, 'id']}'. Skipping row.")
            df = df[valid_mask]
        
        total_valid = len(df)
        logger.info(f"{total_valid} rows have valid product IDs and will be processed.")
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict(orient='records')
        
        # Insert in batches using PostgreSQL bulk insert with ON CONFLICT DO NOTHING
        for start in range(0, total_valid, batch_size):
            end = min(start + batch_size, total_valid)
            batch = records[start:end]
            stmt = insert(Product).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
            session.execute(stmt)
            session.commit()
            logger.info(f"Inserted batch of records from index {start} to {end - 1}.")
        
        logger.info("CSV import completed successfully.")
    
    except Exception as e:
        logger.error(f"Fatal error during CSV import: {str(e)}")
        if session:
            session.rollback()
    
    finally:
        if session:
            session.close()

if __name__ == "__main__":
    # Configuration via environment variables or default values
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/dbname')
    CSV_PATH = os.getenv('CSV_PATH', 'data/processed/Amazon-Products-Preprocessed.csv')
    
    # Run the CSV import with the specified batch size (tune as necessary)
    import_csv_to_db(CSV_PATH, DATABASE_URL, batch_size=10000)
