# Precision-Tuned Recommendation System: Workflow & Features

## Overview
This document provides a structured explanation of the hybrid recommendation website's workflow and features. The system blends multiple recommendation strategies to deliver personalized, diverse, and trend-aware recommendations while ensuring low latency and scalability.

## 1. System Objectives
- **Personalization**: User-specific recommendations based on interaction history.
- **Diversity**: Ensuring varied suggestions to prevent over-personalization.
- **Trend Awareness**: Leveraging trending signals for fresh recommendations.
- **Performance**: Maintaining response times under 150ms for 95% of requests.
- **Scalability**: Handling over 10,000 requests per minute.

## 2. Recommendation Strategies
The recommendation system employs a hybrid approach consisting of:
- **Content-Based Filtering**: Uses TF-IDF embeddings to find similar products based on `name` and `sub_category`.
- **Collaborative Filtering**: Suggests products based on user interaction history.
- **Trending Signals**: Highlights popular products based on time-decayed scores.
- **Association Rules (FP-Growth)**: Identifies frequently co-clicked products.

## 3. API Endpoints & Workflow
### 3.1 `/recommendations/home`
#### **Input**:
- `user_id`: Alphanumeric (1–50 characters)
- `response_limit`: Integer (Default: 20, clamped to 1–60)

#### **Process**:
1. Fetch user interaction history (last 30 days).
2. New users receive trending, best-value, and top-category items.
3. For existing users, recommendations are merged:
   ```python
   merged = 0.5 * clicked_recs + 0.4 * search_recs + 0.1 * diverse_recs
   ```
4. Apply time-decay to trending scores (`TRENDING_DECAY_RATE = 0.95`).

#### **Output**:
- Personalized recommendations
- Trending items
- Best value products
- Top categories
- Diverse picks

### 3.2 `/recommendations/product/{product_id}`
#### **Input**:
- `product_id`: 10 uppercase alphanumeric characters
- `response_limit`: Integer (Default: 20, clamped to 1–60)

#### **Process**:
1. Validate `product_id` format.
2. Use TF-IDF embeddings to find similar products.

#### **Output**:
- List of similar products

### 3.3 `/recommendations/search`
#### **Input**:
- `query`: String (1–255 characters)
- `response_limit`: Integer (Default: 2000, clamped to 1–6000)

#### **Process**:
1. Expand search queries using synonyms.
2. Fallback to trending items if no matches are found.

#### **Output**:
- Search results
- Trending fallback (if no matches found)

### 3.4 Interaction Tracking
#### **Log an Interaction**
- **Endpoint**: `POST /api/v1/interactions`
- **Event Types**:
  - `product_click`: Requires `product_id`
  - `search_query`: Requires `query`

#### **Retrieve User Interactions**
- **Endpoint**: `GET /api/v1/interactions/{user_id}?days=30`

## 4. Model Training & Updates
- **Hourly Updates**: Recalculate trending scores using time-decayed popularity.
- **Daily Retraining**:
  - Update TF-IDF embeddings.
  - Recompute association rules with FP-Growth.
  - Refresh user interaction weights for personalization.

## 5. Project Structure
```
project/
├── data/                     # Data pipelines
│   ├── raw/                  # Raw product data
│   └── processed/            # Cleaned & optimized data
├── database/                 # Database operations
│   ├── csv_importer.py       # Imports CSV data
│   └── interactions.py       # Handles user interactions
├── main.py                   # FastAPI app initialization
├── routers/                  # API endpoint handlers
│   ├── recommendations.py    # Handles recommendation logic
│   └── interactions.py       # Handles interaction logging
├── services/                 # Business logic modules
│   ├── recommender.py        # Hybrid merging & ranking
│   ├── search.py             # Query expansion & semantic search
│   └── models.py             # ML model wrappers
├── ml/                       # Machine learning scripts
│   ├── train_content_model.py  # Generates TF-IDF embeddings
│   └── train_fp_growth.py    # Computes association rules
└── config/                   # Configuration files
    └── settings.py           # Environment variables
```

## 6. Key Implementation Details
- **Database Schema**:
  - Dynamic tables for user interactions.
  - `products` table storing product metadata.
- **Async Operations**:
  - Use `asyncpg` for non-blocking PostgreSQL queries.
  - FastAPI async endpoints for efficiency.
- **Hybrid Merging Logic**:
  - Weighted signals (`0.5` clicked items, `0.4` search terms, `0.1` diverse picks).
  - Diversity sampling for balanced recommendations.
- **Edge Case Handling**:
  - **New Users**: Served trending items.
  - **Search Fallback**: Uses FP-Growth associations if no direct matches.

## 7. Setup & Deployment
### **Dependencies**
```bash
pip install fastapi uvicorn sqlalchemy asyncpg scikit-learn mlxtend sentence-transformers
```

### **Environment Variables**
```python
# config/settings.py
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
TRENDING_DECAY_RATE = 0.95  # Time-decayed popularity
```

### **Run the Application**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

