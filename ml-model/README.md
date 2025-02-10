# Precision-Tuned Recommendation System

## Overview

This project is a **hybrid recommendation engine** for an e-commerce platform. It combines multiple recommendation strategies—content-based filtering, collaborative filtering, trending signals, and association rules—to deliver personalized, diverse, and trend-aware results. The system is designed with a focus on **low latency**, **scalability**, and **freshness**.

- **Latency**: 95% of requests respond in under 150ms.
- **Scalability**: Handles over 10,000 requests per minute.
- **Freshness**: Real-time tracking of user interactions and daily model retraining.

---

## Architecture & Key Components

### 1. Recommendation Strategies

- **Content-Based Filtering**  
  Uses TF-IDF embeddings on product attributes (e.g., `name` and `sub_category`) to identify similar products.

- **Collaborative Filtering**  
  Leverages user interaction history (clicks, searches) to drive personalized recommendations.

- **Trending Signals**  
  Prioritizes products with recent popularity using time-decayed scores (e.g., decay rate set to `TRENDING_DECAY_RATE = 0.95`).

- **Association Rules**  
  Uses the FP-Growth algorithm to determine frequently co-clicked products and drive additional recommendation signals.

### 2. Technical Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) with Uvicorn for asynchronous request handling.
- **Database**: PostgreSQL with TimescaleDB extension for managing time-series interaction data and product metadata.
- **ML Libraries**:  
  - **Scikit-learn**: For TF-IDF calculations.
  - **MLxtend**: For FP-Growth association rule mining.
  - **SentenceTransformers**: For semantic search capabilities.

### 3. Project Structure

```plaintext
project/
│
├── data/                     # Data pipelines
│   ├── raw/                  # Raw CSV files (e.g., Amazon-Products-Raw.csv)
│   └── processed/            # Optimized/cleaned data (e.g., Amazon-Products-Optimized.csv)
│
├── database/                 # Database operations and schema definitions
│   ├── csv_importer.py       # CSV to PostgreSQL products table importer
│   └── interactions.py       # Handles dynamic creation of user-specific interaction tables
│
├── main.py                   # FastAPI app initialization and routing
├── schemas.py                # Pydantic models for request/response validation
│
├── routers/                  # API endpoint handlers
│   ├── recommendations.py    # Endpoints for `/home`, `/product`, `/search`
│   └── interactions.py       # Endpoint for logging user interactions
│
├── services/                 # Business logic modules
│   ├── recommender.py        # Implements hybrid merging and ranking algorithms
│   ├── search.py             # Provides query expansion and semantic search functionality
│   └── models.py             # ML model wrappers for TF-IDF and FP-Growth computations
│
├── ml/                       # Machine learning scripts and training pipelines
│   ├── train_content_model.py  # Script to generate and update TF-IDF embeddings
│   └── train_fp_growth.py    # Script to compute association rules from interaction data
│
└── config/                   # Configuration files and environment settings
    └── settings.py           # Environment variables (e.g., database URL, decay rates)
```

---

## End-to-End Workflow

### 1. User Interaction Tracking

**Flow:**

1. **Event Submission**:  
   - The frontend sends user events (such as `product_click` or `search_query`) to the endpoint `POST /interactions`.
  
2. **Input Validation**:  
   - **Product Click**:  
     - `product_id` must be exactly 10 uppercase alphanumeric characters.
   - **Search Query**:  
     - `query` must be non-empty after trimming whitespace.

3. **Data Storage**:  
   - Valid events are stored in PostgreSQL.  
   - Each user has a dedicated table (named `{user_id}_interactions`) with the following schema:

   ```sql
    table_name = f"{user_id}_interactions"
    query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        event_type TEXT NOT NULL,
        product_id VARCHAR(10),
        query TEXT,
        timestamp TIMESTAMP NOT NULL DEFAULT NOW()
    );
    """
   ```

### 2. Recommendation Generation

#### **Endpoint 1: `/recommendations/home`**

- **Purpose**: Provide a homepage recommendation mix.
- **Process**:
  1. Retrieve the user's interaction history (last 30 days).
  2. **For New Users**:  
     - Return trending items, best-value picks, and top-category selections.
  3. **For Existing Users**:  
     - Merge recommendations from:
       - Clicked items (50% weight)
       - Search queries (40% weight)
       - Diverse picks (10% weight)  
       - **Example merging logic**:
         ```python
         merged = 0.5 * clicked_recs + 0.4 * search_recs + 0.1 * diverse_recs
         ```
  4. Apply a time-decay factor (e.g., `TRENDING_DECAY_RATE = 0.95`) to trending scores.
- **Output**: A JSON response that includes arrays for `personalized`, `trending`, `best_value`, `top_categories`, and `diverse_picks`.

#### **Endpoint 2: `/recommendations/product/{product_id}`**

- **Purpose**: Return products similar to a specified product.
- **Process**:
  1. Validate `product_id` using the regex: `^[A-Z0-9]{10}$`.
  2. Retrieve similar items by comparing TF-IDF embeddings of `name` and `sub_category`.
- **Output**: A JSON response containing an array of similar products.

#### **Endpoint 3: `/recommendations/search`**

- **Purpose**: Process and expand search queries to return matching products.
- **Process**:
  1. Expand queries using synonyms (e.g., "earbuds" → "earphones").
  2. If no direct matches are found, fallback to trending items and include a `fallback_reason` in the response.
- **Output**: A JSON response with the search results and an optional `fallback_reason` if applicable.

### 3. Model Training & Updates

- **Hourly Updates**:  
  - Recalculate trending scores using time-decayed popularity metrics.
- **Daily Retraining**:  
  1. **TF-IDF Embeddings**:  
     - Update product similarity matrices.
  2. **FP-Growth**:  
     - Mine new association rules from recent interaction data.
  3. **User Profiles**:  
     - Recompute interaction weights to maintain personalization quality.

---

## CSV File Specifications

- **CSV Columns**:  
  ```plaintext
  id, name, main_category, sub_category, image, link, ratings, no_of_ratings, discount_price, actual_price, discount_ratio
  ```
- **Example Row**:
  ```plaintext
  AF321D06AE,SOUNDLINK Soft Silicone Ear Plugs - 2 Pcs/Box Reusable Waterproof Earplugs...,stores,Amazon Fashion,https://m.media-amazon.com/images/I/51ETdNss3VL._AC_UL320_.jpg,https://www.amazon.in/SOUNDLINK-Soft-Silicone-Ear-Plugs/dp/B075GKQCG2/ref=sr_1_6956?qid=1679212438&s=apparel&sr=1-6956,3.5,115,243.0,1240.0,0.804
  ```
- **Mapping**:  
  - The `csv_importer.py` file maps CSV columns such as `discount_price` and `actual_price` to the corresponding fields in the PostgreSQL `products` table.

---

## Input/Output Specifications

### 1. `/recommendations/home` Endpoint

- **Input**:
  - `user_id` (String): Alphanumeric, 1–50 characters (regex: `^[a-zA-Z0-9]{1,50}$`).
  - `response_limit` (Integer): Default is 20; clamped between 1 and 60.
  
- **Successful Output (200)**:
  ```json
  {
    "personalized": [],
    "trending": [
      {
        "id": "B08CF3D7QR",
        "name": "Wireless Headphones",
        "category": "Electronics > Audio",
        "image": "URL",
        "price": 59.99,
        "original_price": 99.99,
        "rating": 4.5,
        "reviews": 1500,
        "discount_ratio": 0.4001
      }
      // ... up to `response_limit` items
    ],
    "best_value": [],
    "top_categories": {
      "Electronics": [],
      "Fashion": []
    },
    "diverse_picks": []
  }
  ```
- **Error Conditions**:
  - `400 Bad Request`: For invalid `user_id`.
  - `500 Internal Server Error`: In case of failures (e.g., TF-IDF computation errors).

**Special Note**: For new or stale users (30+ days inactivity), the `personalized` array will be empty and recommendations will rely on trending, best-value, and top-category signals.

### 2. `/recommendations/product/{product_id}` Endpoint

- **Input**:
  - `product_id` (Path Parameter): Exactly 10 uppercase alphanumeric characters (regex: `^[A-Z0-9]{10}$`).
  - `response_limit` (Integer): Default is 20; clamped between 1 and 60.
  
- **Successful Output (200)**:
  ```json
  {
    "similar": [
      {
        "id": "B08CF3D7QR",
        "name": "Wireless Headphones",
        "category": "Electronics > Audio",
        "image": "URL",
        "price": 59.99,
        "original_price": 99.99,
        "rating": 4.5,
        "reviews": 1500,
        "discount_ratio": 0.4001
      }
      // ...
    ]
  }
  ```
- **Error Conditions**:
  - `400 Bad Request`: If `product_id` is invalid.
  - `404 Not Found`: If no product exists for the provided `product_id`.

### 3. `/recommendations/search` Endpoint

- **Input**:
  - `query` (String): 1–255 characters (after trimming).
  - `response_limit` (Integer): Default is 2000; clamped between 1 and 6000.
  
- **Successful Output (200)**:
  ```json
  {
    "results": [
      // Products matching the expanded query
    ],
    "fallback_reason": "no_search_matches"  // Optional; provided when fallback occurs
  }
  ```
- **Error Conditions**:
  - `400 Bad Request`: If the query is empty after trimming.
  - `404 Not Found`: When no products match the query, triggering a fallback to trending items.

### 4. Interaction Tracking Endpoints

#### **Log an Interaction**

- **Endpoint**: `POST /api/v1/interactions/interactions`
- **Request Body Options**:
  ```json
  // For a product click event:
  {
    "user_id": "user123",
    "event_type": "product_click",
    "product_id": "ABCD1234XY"
  }
  ```
  ```json
  // For a search query event:
  {
    "user_id": "user123",
    "event_type": "search_query",
    "query": "red shoes"
  }
  ```
- **Output**:
  - Success: Returns a 200 status with an empty body.
  - Errors:
    - `400 Bad Request`: If required fields (`product_id` for clicks or `query` for search) are missing.
    - `422 Unprocessable Entity`: For invalid `event_type` or schema violations.

#### **Retrieve User Interactions**

- **Endpoint**: `GET /api/v1/interactions/interactions/{user_id}?days=30`
- **Parameters**:
  - `user_id`: Identifier of the user.
  - `days`: Optional; defaults to 30 days if not provided.

---

## Input Validation Summary

| Parameter        | Validation Rules                                  |
|------------------|---------------------------------------------------|
| `user_id`        | Alphanumeric, 1–50 characters (regex: `^[a-zA-Z0-9]{1,50}$`) |
| `product_id`     | Exactly 10 uppercase alphanumeric characters (regex: `^[A-Z0-9]{10}$`) |
| `query`          | Non-empty string (after trimming); max 255 characters |
| `response_limit` | Integer; clamped to endpoint-specific ranges (e.g., 1–60 for `/home`, 1–6000 for `/search`) |
| `event_type`     | Must be either `product_click` or `search_query`  |

---

## Critical Implementation Details

1. **Database Schema**
   - **Dynamic User Tables**: Automatically creates a table named `{user_id}_interactions` for each new user.
   - **Products Table**: Stores product metadata including `id`, `name`, `main_category`, `sub_category`, `image`, `link`, `ratings`, `no_of_ratings`, `discount_price`, `actual_price`, and `discount_ratio`.

2. **Async Operations**
   - Use **asyncpg** for non-blocking PostgreSQL operations.
   - All FastAPI endpoints are asynchronous to maintain low latency.

3. **Hybrid Merging Logic**
   - Recommendation signals are merged using configurable weights (e.g., 0.5 for clicked items, 0.4 for search queries, and 0.1 for diverse picks).
   - Diversity is ensured by randomly sampling items from underrepresented categories.

4. **Edge Case Handling**
   - **New Users / Zero Interactions**: The `personalized` recommendations array is empty. The system defaults to trending, best-value, and top-category recommendations.
   - **Stale Profiles**: After 30 days of inactivity, the personalized recommendations revert to trending signals.
   - **Search Fallback**: If no direct search matches are found, the endpoint falls back to trending items and includes a `fallback_reason` in the response.

---

## Setup & Deployment

### Dependencies

Install required Python packages:
```bash
pip install fastapi uvicorn sqlalchemy asyncpg scikit-learn mlxtend sentence-transformers
```

### Environment Configuration

Configure environment variables in `config/settings.py`:
```python
# config/settings.py
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
TRENDING_DECAY_RATE = 0.95  # Time-decay factor for trending scores
```

### Running the Application

Start the FastAPI application using Uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Conclusion

This documentation outlines the complete flow—from user interaction tracking to recommendation generation and model retraining. The architecture is modular and designed for performance and scalability, ensuring that the system meets the latency and personalization requirements. Developers should follow this guide to implement and extend the recommendation engine in a production environment.

For further questions or issues, please refer to the inline comments in the code or consult the development team.

---