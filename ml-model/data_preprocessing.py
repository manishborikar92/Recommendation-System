import pandas as pd
import uuid
import requests
import logging
import numpy as np
from typing import List, Optional
from tqdm import tqdm
import concurrent.futures
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure constants
MAX_WORKERS = 5  # For concurrent image validation
REQUEST_TIMEOUT = 10  # seconds
VALID_IMAGE_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/webp'}

class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass

def clean_numeric_string(value: str) -> str:
    """Clean numeric values from currency symbols and commas"""
    if pd.isna(value) or not isinstance(value, str):
        return str(value)
    return re.sub(r'[^\d.]', '', value)

def is_valid_image(url: str) -> bool:
    """Validate image URL with timeout and proper content type checking"""
    if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
        return False

    try:
        response = requests.head(
            url,
            allow_redirects=True,
            timeout=REQUEST_TIMEOUT,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        return (
            response.status_code == 200 and
            response.headers.get('Content-Type', '').split(';')[0] in VALID_IMAGE_CONTENT_TYPES
        )
    except (requests.RequestException, ValueError):
        return False

def validate_image_urls(urls: List[str]) -> pd.Series:
    """Validate multiple image URLs concurrently with progress tracking"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(is_valid_image, url): url for url in urls}
        results = {}
        
        with tqdm(total=len(urls), desc="Validating images", unit="url") as pbar:
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    logger.error(f"Error validating {url}: {str(e)}")
                    results[url] = False
                finally:
                    pbar.update(1)
    
    return pd.Series(results.values(), index=results.keys())

def clean_and_validate_data(
    csv_file: str,
    output_file: str,
    required_columns: Optional[List[str]] = None,
    numeric_columns: List[str] = [
        'ratings', 'no_of_ratings', 'discount_price', 
        'actual_price', 'discount_ratio'
    ]
) -> None:
    """
    Enhanced data cleaning and validation with:
    - Numeric data preprocessing
    - Robust error handling
    - Advanced data quality checks
    """
    try:
        # Initialize data quality metrics
        metrics = {
            'initial_rows': 0,
            'missing_values_removed': 0,
            'invalid_images_removed': 0,
            'invalid_numeric_removed': 0,
            'invalid_ratio_removed': 0,
            'final_rows': 0
        }

        # Read data with optimized memory usage
        dtypes = {col: 'string' for col in numeric_columns}
        df = pd.read_csv(
            csv_file,
            dtype=dtypes,
            true_values=['yes', 'true', 't', 'y'],
            false_values=['no', 'false', 'f', 'n'],
            encoding='utf-8'
        )
        metrics['initial_rows'] = len(df)

        # Handle missing values in required columns
        if required_columns is None:
            required_columns = ['name', 'main_category', 'sub_category', 'image', 'link']
            
        initial_count = len(df)
        df = df.dropna(subset=required_columns)
        metrics['missing_values_removed'] = initial_count - len(df)

        # Generate unique IDs if missing
        if 'id' not in df.columns or df['id'].isna().any():
            df['id'] = [uuid.uuid4().hex[:12].upper() for _ in range(len(df))]
        else:
            df['id'] = df['id'].astype('string').str.strip().str.upper()

        # Enhanced numeric data cleaning
        for col in numeric_columns:
            if col in df.columns:
                # Clean string values before conversion
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(clean_numeric_string)
                
                # Convert to numeric with error tracking
                converted = pd.to_numeric(df[col], errors='coerce')
                invalid_count = converted.isna().sum()
                
                if invalid_count > 0:
                    logger.warning(f"Found {invalid_count} invalid values in {col}")
                    metrics['invalid_numeric_removed'] += invalid_count
                
                df[col] = converted

        # Remove rows with invalid numeric values
        initial_count = len(df)
        df = df.dropna(subset=numeric_columns)
        metrics['invalid_numeric_removed'] += (initial_count - len(df))

        # Validate discount ratio consistency
        if all(col in df.columns for col in ['discount_price', 'actual_price', 'discount_ratio']):
            try:
                # Handle division by zero and invalid values
                with np.errstate(divide='ignore', invalid='ignore'):
                    calculated_ratio = np.where(
                        df['actual_price'] > 0,
                        (df['actual_price'] - df['discount_price']) / df['actual_price'],
                        np.nan
                    )
                
                # Create validation mask
                ratio_mask = (
                    (df['discount_ratio'].notna()) &
                    (np.abs(df['discount_ratio'] - calculated_ratio) < 0.01)
                )
                
                invalid_ratios = len(df) - ratio_mask.sum()
                if invalid_ratios > 0:
                    logger.warning(f"Removing {invalid_ratios} rows with inconsistent discount ratios")
                    metrics['invalid_ratio_removed'] = invalid_ratios
                    df = df[ratio_mask]
            except KeyError as e:
                logger.error(f"Missing required column for ratio validation: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Error during ratio validation: {str(e)}")
                raise

        # Validate image URLs
        if len(df) > 0:
            image_validation_results = validate_image_urls(df['image'].tolist())
            df = df[image_validation_results.values]
            metrics['invalid_images_removed'] = len(image_validation_results) - sum(image_validation_results)
        else:
            logger.warning("No valid rows remaining after numeric processing")
            metrics['invalid_images_removed'] = 0

        # Optimize data types
        for col in numeric_columns:
            if col in df.columns:
                if np.issubdtype(df[col].dtype, np.floating) and (df[col] % 1 == 0).all():
                    df[col] = df[col].astype('Int64')

        # Final data quality metrics
        metrics['final_rows'] = len(df)
        logger.info(f"Data quality metrics: {metrics}")

        if metrics['final_rows'] == 0:
            logger.error("No valid rows remaining after processing")
            raise DataValidationError("No valid data remaining after processing")

        # Save optimized output
        df.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"Successfully processed data. Output saved to {output_file}")

    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise DataValidationError(f"Data processing failed: {str(e)}") from e

if __name__ == "__main__":
    RAW_DATA_PATH = "data/raw/Amazon-Products.csv"
    PROCESSED_DATA_PATH = "data/processed/Amazon-Products-Optimized1.csv"

    try:
        clean_and_validate_data(
            csv_file=RAW_DATA_PATH,
            output_file=PROCESSED_DATA_PATH,
            required_columns=[
                'id', 'name', 'main_category', 
                'sub_category', 'image', 'link'
            ]
        )
    except DataValidationError as e:
        logger.error("Data processing pipeline failed")
        raise SystemExit(1) from e

