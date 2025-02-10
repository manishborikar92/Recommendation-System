"""
ml/train_fp_growth.py

This script trains an association rules model using the FP-Growth algorithm.
It scans for all user-specific interaction tables (tables ending with "_interactions"),
loads product click transactions from the past N days (default 30),
executes FP-Growth and association_rules functions from mlxtend, and saves the rules
to a JSON file for later use by the recommendation system.
"""

from dotenv import load_dotenv
load_dotenv()

import os
import logging
import pandas as pd
import numpy as np
import json
from sqlalchemy import create_engine
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_interaction_table_names(engine):
    """
    Retrieve the names of all tables in the public schema that end with '_interactions'.
    """
    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
      AND table_name LIKE '%\\_interactions';
    """
    with engine.connect() as connection:
        # Get the underlying DBAPI connection (which provides .cursor())
        raw_conn = connection.connection
        result = pd.read_sql(query, raw_conn)
    return result['table_name'].tolist()


def load_transactions(engine, days=30):
    """
    Load transactions from each interaction table.

    For each table, the function queries for rows where event_type is 'product_click' 
    and the timestamp is within the past `days` days. Only transactions with at least 2 items 
    are kept.
    """
    logger.info("Loading user transactions from interaction tables...")
    table_names = get_interaction_table_names(engine)
    logger.info(f"Found {len(table_names)} interaction tables.")
    
    transactions = []
    for table in table_names:
        query = f"""
        SELECT product_id FROM {table}
        WHERE event_type = 'product_click'
          AND timestamp >= NOW() - INTERVAL '{days} days';
        """
        try:
            with engine.connect() as connection:
                raw_conn = connection.connection
                df = pd.read_sql(query, raw_conn)
            # Drop nulls and get unique product_ids for the transaction
            products = df['product_id'].dropna().unique().tolist()
            if len(products) > 1:  # Only consider transactions with at least 2 products
                transactions.append(products)
        except Exception as e:
            logger.warning("Failed to load transactions from table %s: %s", table, e)
    logger.info("Collected %d transactions with at least 2 items.", len(transactions))
    return transactions


def train_fp_growth(min_support=0.01, min_confidence=0.5, days=30, output_path='model/fp_rules.json'):
    """
    Train the FP-Growth model and generate association rules.

    Parameters:
      min_support (float): Minimum support threshold for frequent itemsets.
      min_confidence (float): Minimum confidence threshold for association rules.
      days (int): How many days of interaction data to use.
      output_path (str): File path where the rules JSON will be saved.
    """
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    engine = create_engine(DATABASE_URL, future=True)
    
    transactions = load_transactions(engine, days)
    if not transactions:
        logger.error("No transactions available for FP-Growth training.")
        return
    
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df_trans = pd.DataFrame(te_ary, columns=te.columns_)
    
    logger.info("Running FP-Growth algorithm...")
    frequent_itemsets = fpgrowth(df_trans, min_support=min_support, use_colnames=True)
    logger.info("Found %d frequent itemsets.", len(frequent_itemsets))
    
    if frequent_itemsets.empty:
        logger.error("No frequent itemsets found with the provided min_support.")
        return
    
    logger.info("Generating association rules...")
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    logger.info("Generated %d association rules.", len(rules))
    
    # Convert frozensets to lists for JSON serialization
    rules['antecedents'] = rules['antecedents'].apply(lambda x: list(x))
    rules['consequents'] = rules['consequents'].apply(lambda x: list(x))
    
    rules_json = rules.to_dict(orient='records')
    
    # Convert non-finite values (like Infinity) to a valid JSON value
    import math
    for rule in rules_json:
        if 'conviction' in rule and math.isinf(rule['conviction']):
            rule['conviction'] = "Infinity"  # or you can use null: rule['conviction'] = None

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(rules_json, f, indent=2)
    
    logger.info("Association rules saved to %s.", output_path)


if __name__ == "__main__":
    train_fp_growth()
