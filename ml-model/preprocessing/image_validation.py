import pandas as pd
import requests
import concurrent.futures
import logging
import os
import argparse
from datetime import datetime
import threading

# Configure logging
log_dir = 'data/logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'image_validation.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Thread-local storage for requests sessions
thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session

def validate_url(url):
    """Validate if a URL points to a valid image resource."""
    session = get_session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        # Use GET with stream=True to avoid downloading entire content
        with session.get(url, stream=True, timeout=10, headers=headers, allow_redirects=True) as response:
            content_type = response.headers.get('Content-Type', '')
            
            if response.status_code == 200 and content_type.startswith('image/'):
                logger.debug(f"Valid image URL: {url}")
                return (url, True)
            
            logger.warning(f"Invalid URL ({response.status_code} - {content_type}): {url}")
            return (url, False)
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for {url}: {str(e)}")
        return (url, False)
    except Exception as e:
        logger.error(f"Unexpected error for {url}: {str(e)}")
        return (url, False)

def process_csv(input_path, output_path):
    """Process CSV file to validate and filter image URLs."""
    start_time = datetime.now()
    logger.info(f"Starting CSV processing. Input: {input_path}, Output: {output_path}")

    try:
        # Read input CSV
        logger.info("Reading input file")
        df = pd.read_csv(input_path)
        
        if 'image' not in df.columns:
            raise ValueError("CSV file does not contain 'image' column")
        
        urls = df['image'].tolist()
        logger.info(f"Loaded {len(urls)} URLs for validation")

        # Validate URLs in parallel
        logger.info("Starting URL validation")
        valid_urls = set()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(validate_url, url): url for url in urls}
            
            for future in concurrent.futures.as_completed(futures):
                url, is_valid = future.result()
                if is_valid:
                    valid_urls.add(url)

        # Filter and save valid rows
        logger.info("Filtering valid rows")
        cleaned_df = df[df['image'].isin(valid_urls)]
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        cleaned_df.to_csv(output_path, index=False)
        
        duration = datetime.now() - start_time
        logger.info(f"Processing completed in {duration.total_seconds():.2f} seconds")
        logger.info(f"Original rows: {len(df)}, Cleaned rows: {len(cleaned_df)}, Removed: {len(df) - len(cleaned_df)}")
    
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Validate image URLs in CSV file')
    # parser.add_argument('--input', required=True, help='Input CSV file path')
    # parser.add_argument('--output', required=True, help='Output CSV file path')
    # args = parser.parse_args()
    args = argparse.Namespace(input='data/processed/Amazon-Products-Cleaned.csv', output='data/processed/Amazon-Products-Preprocessed.csv')
    try:
        process_csv(args.input, args.output)
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        exit(1)