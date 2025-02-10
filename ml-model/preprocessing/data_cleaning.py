import pandas as pd
import requests
import uuid
import logging
from logging.handlers import RotatingFileHandler
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException
from dataclasses import dataclass
from datetime import datetime

"""
Invalid Prices: Drop entire column
Invalid Ratings: Replace with 0
"""

RAW_DATA_PATH = "data/raw/Amazon-Products.csv"
PROCESSED_DATA_PATH = "data/processed/Amazon-Products-Cleaned.csv"
LOG_PATH = "data/logs/data_cleaning.log"
TEMP_DIR = "data/temp"

@dataclass
class ProcessingMetrics:
    """Store processing metrics for monitoring and reporting"""
    total_rows: int
    invalid_prices: int
    invalid_ratings: int
    final_rows: int
    processing_time: float

class DataPreprocessor:
    def __init__(
        self, 
        timeout: int = 10, 
        max_workers: int = 10, 
        chunk_size: int = 100,
        retry_count: int = 3
    ):
        self.timeout = timeout
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self.retry_count = retry_count
        self.required_columns = [
            'id', 'name', 'main_category', 'sub_category', 'image', 'link',
            'ratings', 'no_of_ratings', 'discount_price', 'actual_price'
        ]
        self.final_columns = self.required_columns + ['discount_ratio']
        self.temp_dir = Path(TEMP_DIR)
        self.metrics = None
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging with rotation and proper directory creation"""
        log_path = Path(LOG_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            file_handler = RotatingFileHandler(
                LOG_PATH,
                maxBytes=10*1024*1024,
                backupCount=5
            )
            file_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.INFO)

    def _clean_ratings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate ratings column"""
        self.logger.info("Cleaning ratings column...")
        original_count = len(df)
        
        try:
            # Convert ratings to numeric, coerce errors to NaN
            df['ratings'] = pd.to_numeric(
                df['ratings'].astype(str).str.replace('[^0-9.]', '', regex=True),
                errors='coerce'
            )
            
            # Filter valid ratings (typically 0-5 range)
            valid_ratings_mask = (df['ratings'].between(0, 5, inclusive='both')) | (df['ratings'].isna())
            filtered_df = df[valid_ratings_mask].copy()
            
            # Handle NaN values (either fill with 0 or drop)
            filtered_df['ratings'] = filtered_df['ratings'].fillna(0)
            
            removed_count = original_count - len(filtered_df)
            if removed_count > 0:
                self.logger.warning(
                    f"Removed {removed_count} rows ({removed_count/original_count:.1%}) "
                    "with invalid rating values"
                )
                if self.metrics:
                    self.metrics.invalid_ratings = removed_count
                    
            return filtered_df.reset_index(drop=True)
            
        except Exception as e:
            self.logger.error(f"Ratings cleaning failed: {str(e)}")
            raise

    def _clean_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate price columns with improved error handling"""
        self.logger.info("Cleaning price columns...")
        original_count = len(df)

        try:
            for col in ['discount_price', 'actual_price']:
                df[f'{col}_clean'] = (
                    df[col]
                    .astype(str)
                    .str.replace('[₹,]', '', regex=True)
                    .replace('', pd.NA)
                    .astype(float)
                )
            
            valid_prices_mask = (
                (df['actual_price_clean'] > 0) &
                (df['discount_price_clean'] <= df['actual_price_clean']) &
                df['actual_price_clean'].notna() &
                df['discount_price_clean'].notna()
            )
            
            df.loc[valid_prices_mask, 'actual_price'] = df.loc[valid_prices_mask, 'actual_price_clean']
            df.loc[valid_prices_mask, 'discount_price'] = df.loc[valid_prices_mask, 'discount_price_clean']
            
            df.loc[valid_prices_mask, 'discount_ratio'] = (
                (df.loc[valid_prices_mask, 'actual_price_clean'] - 
                 df.loc[valid_prices_mask, 'discount_price_clean']) / 
                df.loc[valid_prices_mask, 'actual_price_clean']
            ).round(4)
            
            df = df.drop(columns=['actual_price_clean', 'discount_price_clean'])
            filtered_df = df[valid_prices_mask].reset_index(drop=True)
            
            removed_count = original_count - len(filtered_df)
            if removed_count > 0:
                self.logger.warning(
                    f"Removed {removed_count} rows ({removed_count/original_count:.1%}) "
                    "with invalid price values"
                )
                if self.metrics:
                    self.metrics.invalid_prices = removed_count

        except Exception as e:
            self.logger.error(f"Price cleaning failed: {str(e)}")
            raise

        return filtered_df

    def _process_chunk(self, chunk: pd.DataFrame, chunk_idx: int) -> Optional[pd.DataFrame]:
        """Process chunk with improved error handling and recovery"""
        if not isinstance(chunk, pd.DataFrame):
            self.logger.error(f"Invalid chunk type for chunk {chunk_idx}")
            return None

        if chunk.empty:
            self.logger.warning(f"Empty chunk received for chunk {chunk_idx}")
            return None

        chunk_file = self.temp_dir / f'chunk_{chunk_idx:04d}.csv'
        tmp_file = self.temp_dir / f'chunk_{chunk_idx:04d}.tmp'

        if chunk_file.exists():
            try:
                processed_chunk = pd.read_csv(chunk_file)
                if len(processed_chunk) > 0:
                    return processed_chunk
                chunk_file.unlink()
            except Exception as e:
                self.logger.error(f"Failed to read existing chunk {chunk_idx}: {str(e)}")
                chunk_file.unlink(missing_ok=True)

        self.logger.info(f"Processing chunk {chunk_idx} with {len(chunk)} rows")
        
        try:
            valid_chunk = chunk.copy()
            valid_chunk = valid_chunk.reset_index(drop=True)
            
            if len(valid_chunk) > 0:
                valid_chunk.to_csv(tmp_file, index=False)
                tmp_file.rename(chunk_file)
                
                self.logger.info(
                    f"Saved chunk {chunk_idx}: {len(valid_chunk)}/{len(chunk)} "
                    f"({len(valid_chunk)/len(chunk):.1%}) rows valid"
                )
                return valid_chunk
            else:
                self.logger.warning(f"No valid rows in processed chunk {chunk_idx}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating valid chunk {chunk_idx}: {str(e)}")
            return None

    def process(self, input_path: str, output_path: str) -> ProcessingMetrics:
        """Enhanced processing pipeline with metrics and cleanup"""
        start_time = datetime.now()
        self.logger.info(f"Starting data processing pipeline for {input_path}")
        
        self.metrics = ProcessingMetrics(
            total_rows=0,
            invalid_prices=0,
            invalid_ratings=0,
            final_rows=0,
            processing_time=0
        )

        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            self.temp_dir.mkdir(parents=True, exist_ok=True)

            df = pd.read_csv(input_path)
            self.metrics.total_rows = len(df)
            self.logger.info(f"Loaded {len(df)} rows")

            missing_columns = set(self.required_columns) - set(df.columns)
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # Clean data in sequence
            df = self._clean_prices(df)
            df = self._clean_ratings(df)
            
            if len(df) == 0:
                raise ValueError("No valid data after cleaning steps")

            chunks = [df[i:i+self.chunk_size] for i in range(0, len(df), self.chunk_size)]
            processed_chunks = []
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_chunk = {
                    executor.submit(self._process_chunk, chunk, idx): idx 
                    for idx, chunk in enumerate(chunks)
                }
                
                for future in as_completed(future_to_chunk):
                    chunk_idx = future_to_chunk[future]
                    try:
                        result = future.result()
                        if isinstance(result, pd.DataFrame) and len(result) > 0:
                            processed_chunks.append(result)
                    except Exception as e:
                        self.logger.error(f"Failed to process chunk {chunk_idx}: {str(e)}")

            if not processed_chunks:
                raise ValueError("No valid chunks processed")

            df_final = pd.concat(processed_chunks, ignore_index=True)
            
            if len(df_final) == 0:
                raise ValueError("No valid rows after processing all chunks")

            # Final transformations with error handling
            df_final = df_final.assign(
                id=lambda x: [uuid.uuid4().hex[:10].upper() for _ in range(len(x))],
                no_of_ratings=lambda x: pd.to_numeric(
                    x.no_of_ratings.astype(str).str.replace(',', ''),
                    errors='coerce'
                ).fillna(0).astype(int),
                ratings=lambda x: x.ratings.astype(float)
            )[self.final_columns]

            df_final = df_final.dropna()

            df_final.to_csv(output_path, index=False)
            self.metrics.final_rows = len(df_final)

        except Exception as e:
            self.logger.critical(f"Processing failed: {str(e)}", exc_info=True)
            raise

        finally:
            try:
                if self.temp_dir.exists():
                    shutil.rmtree(self.temp_dir)
            except Exception as e:
                self.logger.error(f"Failed to cleanup temporary files: {str(e)}")

            self.metrics.processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(
                f"Processing completed in {self.metrics.processing_time:.1f}s\n"
                f"Total rows: {self.metrics.total_rows}\n"
                f"Invalid prices: {self.metrics.invalid_prices}\n"
                f"Invalid ratings: {self.metrics.invalid_ratings}\n"
                f"Final rows: {self.metrics.final_rows}"
            )

        return self.metrics

if __name__ == "__main__":
    try:
        processor = DataPreprocessor(
            timeout=15,
            max_workers=20,
            chunk_size=100,
            retry_count=3
        )
        metrics = processor.process(RAW_DATA_PATH, PROCESSED_DATA_PATH)
        
    except Exception as e:
        logging.critical(f"Critical error in main execution: {str(e)}", exc_info=True)
        raise SystemExit(1) from e