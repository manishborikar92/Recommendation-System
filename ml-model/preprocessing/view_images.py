import os
import logging
from logging.handlers import RotatingFileHandler
import pandas as pd
from flask import Flask, render_template
from urllib.parse import urlparse
import time

# Configuration
CSV_PATH = 'data/processed/Amazon-Products-Preprocessed.csv'
LOG_DIR = 'data/logs'
MAX_IMAGE_COUNT = 326804  # Safety limit for maximum images to process
PORT = 5000
HOST = '0.0.0.0'

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure advanced logging
def configure_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %Z'
    )

    # Rotating file handler (10 MB per file, max 5 backups)
    file_handler = RotatingFileHandler(
        filename=f'{LOG_DIR}/view_imagees.log',
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Error file handler
    error_file_handler = RotatingFileHandler(
        filename=f'{LOG_DIR}/errors.log',
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(error_file_handler)

    return logger

logger = configure_logger('ImageGrid')

app = Flask(__name__)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def load_image_urls():
    start_time = time.time()
    logger.info("Starting CSV processing")
    
    if not os.path.exists(CSV_PATH):
        logger.error(f"CSV file not found: {CSV_PATH}")
        raise FileNotFoundError(f"CSV file {CSV_PATH} not found")

    try:
        # Read CSV in optimized way
        df = pd.read_csv(
            CSV_PATH,
            usecols=['image'],  # Only load needed column
            dtype={'image': 'string'},
            engine='c'  # Use C engine for faster parsing
        )
        
        # Clean and validate URLs
        df.dropna(subset=['image'], inplace=True)
        df['image'] = df['image'].str.strip()
        df = df[df['image'].apply(is_valid_url)]
        
        # Limit maximum images for safety
        urls = df['image'].head(MAX_IMAGE_COUNT).tolist()
        
        load_time = time.time() - start_time
        logger.info(f"Processed {len(urls)} valid image URLs in {load_time:.2f} seconds")
        return urls
    
    except KeyError:
        logger.error("CSV file missing required 'image' column")
        raise
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        raise

@app.route('/')
def image_grid():
    start_time = time.time()
    logger.info("Request received for image grid")
    
    try:
        image_urls = load_image_urls()
        if not image_urls:
            logger.warning("No valid image URLs found in CSV")
            
        render_time = time.time() - start_time
        logger.info(f"Rendered page with {len(image_urls)} images in {render_time:.2f} seconds")
        return render_template('grid.html', image_urls=image_urls)
    
    except Exception as e:
        logger.error(f"Error generating image grid: {str(e)}")
        return render_template('error.html'), 500

if __name__ == '__main__':
    logger.info(f"Starting server on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, threaded=True)