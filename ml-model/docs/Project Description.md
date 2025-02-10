### **Precision-Tuned Recommendation System: Project Description**  
#### **Objective**  
Develop a **hybrid recommendation engine** for e-commerce that blends multiple recommendation strategies to deliver **personalized**, **diverse**, and **trend-aware** results. The system prioritizes:  
- **Low Latency**: Responses under 150ms for 95% of requests.  
- **Scalability**: Support over 10,000 requests per minute.  
- **Freshness**: Real-time user interaction tracking and daily model retraining.  

#### **Key Components**  
1. **Recommendation Strategies**:  
   - **Content-Based Filtering**: Analyzes product `name` and `sub_category` using TF-IDF embeddings to find similar items.  
   - **Collaborative Filtering**: Leverages user interaction history (clicks, searches) to personalize recommendations.  
   - **Trending Signals**: Prioritizes items with recent popularity (time-decayed scores updated hourly).  
   - **Association Rules**: Identifies frequently co-clicked products using FP-Growth algorithms.  

2. **Technical Stack**:  
   - **Backend Framework**: FastAPI with Uvicorn for asynchronous request handling.  
   - **Database**: PostgreSQL (TimescaleDB) for time-series interaction data and product metadata.  
   - **ML Libraries**: Scikit-learn (TF-IDF), MLxtend (FP-Growth), SentenceTransformers (semantic search).  

---

### **End-to-End Workflow**  

#### **1. User Interaction Tracking**  
- **Step 1**: Frontend sends interaction events (e.g., `product_click` or `search_query`) to `POST /interactions`.  
- **Step 2**: Server validates input:  
  - `product_id` must be 10 uppercase alphanumeric characters.  
  - `query` must be non-empty after trimming.  
- **Step 3**: Validated data is stored in a PostgreSQL table named after the `user_id` (e.g., `U12345_interactions`), structured as:  
  ```sql
  (event_type TEXT, product_id VARCHAR(10), query TEXT, timestamp TIMESTAMP)
  ```  

#### **2. Recommendation Generation**  
- **Endpoint 1**: `/recommendations/home`  
  - **Process**:  
    1. Fetch the user’s interaction history (last 30 days).  
    2. For new users: Return trending, best-value, and top-category items.  
    3. For existing users: Merge recommendations using weighted logic:  
       ```python
       # 50% clicked items, 40% search terms, 10% diverse picks
       merged = 0.5 * clicked_recs + 0.4 * search_recs + 0.1 * diverse_recs
       ```  
    4. Apply time-decay to trending scores (e.g., `TRENDING_DECAY_RATE = 0.95`).  

- **Endpoint 2**: `/recommendations/product/{product_id}`  
  - **Process**:  
    1. Validate `product_id` format (`^[A-Z0-9]{10}$`).  
    2. Use TF-IDF embeddings to find products with similar `name` and `sub_category`.

- **Endpoint 3**: `/recommendations/search`  
  - **Process**:  
    1. Expand search queries using synonyms (e.g., "earbuds" → "earphones").  
    2. Fallback to trending items if no matches, with `fallback_reason` in the response.  

#### **3. Model Training & Updates**  
- **Hourly Updates**:  
  - Recalculate trending scores using decayed popularity metrics.  
- **Daily Retraining**:  
  1. **TF-IDF Embeddings**: Update product similarity matrices.  
  2. **FP-Growth**: Mine new association rules from recent interactions.  
  3. **User Profiles**: Recompute interaction weights for personalization.  

#### **Response**:  
   - Ranked JSON results returned to frontend.

---

### **Project Structure**  

```  
project/  
│
├── data/                     # Data pipelines  
│   ├── raw/                  # Raw product CSV (e.g., Amazon-Products-Raw.csv)  
│   └── processed/            # Cleaned data (e.g., Amazon-Products-Optimized.csv)  
│
├── database/                 # Database operations  
│   ├── csv_importer.py       # Imports CSV data into PostgreSQL `products` table  
│   └── interactions.py       # Dynamically creates user-specific interaction tables  
│
├── main.py                   # FastAPI app initialization and routing  
├── schemas.py                # Pydantic models for input/output validation  
│
├── routers/                  # API endpoint handlers  
│   ├── recommendations.py    # `/home`, `/product`, `/search` logic  
│   └── interactions.py       # `POST /interactions` event logging  
│
├── services/                 # Business logic modules  
│   ├── recommender.py        # Hybrid merging and ranking algorithms  
│   ├── search.py             # Query expansion and semantic search  
│   └── models.py             # ML model wrappers (TF-IDF, FP-Growth)  
│
├── ml/                       # Machine learning scripts  
│   ├── train_content_model.py  # Generates TF-IDF embeddings  
│   └── train_fp_growth.py    # Computes association rules from interactions  
│
└── config/                   # Configuration  
    └── settings.py           # Environment variables (database URL, decay rates)  
```  

---

### **CSV File Columns and Rows**
```
id,name,main_category,sub_category,image,link,ratings,no_of_ratings,discount_price,actual_price,discount_ratio
AF321D06AE,SOUNDLINK Soft Silicone Ear Plugs - 2 Pcs/Box Reusable Waterproof Earplugs Prevent Water Reduce Noise for Swimming and Bat...,stores,Amazon Fashion,https://m.media-amazon.com/images/I/51ETdNss3VL._AC_UL320_.jpg,https://www.amazon.in/SOUNDLINK-Soft-Silicone-Ear-Plugs/dp/B075GKQCG2/ref=sr_1_6956?qid=1679212438&s=apparel&sr=1-6956,3.5,115,243.0,1240.0,0.804

```

---

#### **Key Files Explained**  
- **`csv_importer.py`**: Maps CSV columns (e.g., `discount_price`, `actual_price`) to the PostgreSQL `products` table.  
- **`recommender.py`**: Implements the `hybrid_merge()` function to combine recommendation signals.  
- **`schemas.py`**: Enforces input validation (e.g., regex checks for `user_id`, `product_id`).  

---

### **Critical Implementation Details**  
1. **Database Schema**:  
   - **Dynamic User Tables**:  Automatically creates `{user_id}_interactions` tables for new users.  
   - **`products`**: Stores product metadata (id, name, main_category, sub_category, image, link, ratings, no_of_ratings, discount_price, actual_price, discount_ratio). 
2. **Async Operations**:  
   - Use **asyncpg** for non-blocking PostgreSQL queries.  
   - FastAPI’s async endpoints to maintain low latency. 
3. **Hybrid Merging Logic**:  
   - Combine signals using configurable weights (e.g., `0.5` for clicked items).  
   - Diversity ensured via random sampling from low-frequency categories.
4. **Edge Case Handling**:  
   - **New Users**: Serve trending items from `products` sorted by `ratings` and `no_of_ratings`. 
   - **Search Fallback**: Use FP-Growth associations if no direct matches.  
5. **Diversity Sampling**:  
   - Randomly selects items from underrepresented categories to avoid over-personalization.  

---

### **Setup & Deployment**  

1. **Dependencies**:  
   ```bash  
   pip install fastapi uvicorn sqlalchemy asyncpg scikit-learn mlxtend sentence-transformers  
   ```  

2. **Environment Variables**:  
   ```python  
   # config/settings.py  
   DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"  
   TRENDING_DECAY_RATE = 0.95  # Time-decayed popularity  
   ```  

3. **Run**:  
   ```bash  
  uvicorn main:app --host 0.0.0.0 --port 8000
   ```  

This structure ensures modularity, scalability, and alignment with the system’s latency and freshness goals.