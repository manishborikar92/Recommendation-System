### **Precision-Tuned Recommendation System: Frontend Input/Output Conditions**  

#### **1. `/recommendations/home` Endpoint**  
**Input**:  
- **Required**:  
  - `user_id`: String (Alphanumeric, 1–50 chars; regex: `^[a-zA-Z0-9]{1,50}$`).  
  - `response_limit`: Integer (Default: 20, clamped to 1–60).  

**Output**:  
- **Success (200)**:  
  ```json  
  {  
    "personalized": [],        // Empty for new users; populated for users with interaction history  
    "trending": [  
      {  
        "id": "B08CF3D7QR",    // 10-char alphanumeric  
        "name": "Wireless Headphones",  
        "category": "Electronics > Audio",  
        "image": "URL",  
        "price": 59.99,  
        "original_price": 99.99,  
        "rating": 4.5,  
        "reviews": 1500,
        "discount_ratio": 0.4001  
      },  
      // ... (up to `response_limit` items)  
    ],  
    "best_value": [],          // Same schema as "trending" (price-to-quality ratio)  
    "top_categories": {  
      "Electronics": [],       // Same schema as "trending"  
      "Fashion": []  
    },  
    "diverse_picks": []        // Randomly sampled for diversity  
  }  
  ```  
- **Errors**:  
  - `400 Bad Request`: Invalid `user_id` format.  
  - `500 Internal Server Error`: Model failure (e.g., TF-IDF computation error).  

**Special Conditions**:  
- **New Users**: `personalized` array is empty; recommendations use `trending`, `best_value`, and `top_categories`.  
- **Stale Profiles**: After 30 days of inactivity, recommendations revert to trending.  

---

#### **2. `/recommendations/product/{product_id}` Endpoint**  
**Input**:  
- **Path Parameter**:  
  - `product_id`: String (Exactly 10 uppercase alphanumeric chars; regex: `^[A-Z0-9]{10}$`).  
  - `response_limit`: Integer (Default: 20, clamped to 1–60).  

**Output**:  
- **Success (200)**:  
  ```json  
  {  
    "similar": [  
      {  
        "id": "B08CF3D7QR",    // 10-char alphanumeric  
        "name": "Wireless Headphones",  
        "category": "Electronics > Audio",  
        "image": "URL",  
        "price": 59.99,  
        "original_price": 99.99,  
        "rating": 4.5,  
        "reviews": 1500,
        "discount_ratio": 0.4001  
      },   
      ...
    ]  
  }  
  ```  
- **Errors**:  
  - `400 Bad Request`: Invalid `product_id` (e.g., wrong length or characters).  
  - `404 Not Found`: No product with the given `product_id` exists.  

---

#### **3. `/recommendations/search` Endpoint**  
**Input**:  
- **Required**:  
  - `query`: String (1–255 chars; non-empty after trimming whitespace).  
  - `response_limit`: Integer (Default: 2000, clamped to 1–6000).  

**Output**:  
- **Success (200)**:  
  ```json  
  {  
    "results": [  
      {  
        "id": "B08CF3D7QR",    // 10-char alphanumeric  
        "name": "Wireless Headphones",  
        "category": "Electronics > Audio",  
        "image": "URL",  
        "price": 59.99,  
        "original_price": 99.99,  
        "rating": 4.5,  
        "reviews": 1500,
        "discount_ratio": 0.4001  
      },
      ...
    ],  
    "fallback_reason": "no_search_matches"  // Optional, included if fallback to trending  
  }  
  ```  
- **Errors**:  
  - `400 Bad Request`: Empty query after trimming.  
  - `404 Not Found`: No products match the query (fallback to trending).  

**Special Condition**:  
- **Search Fallback**: If no matches, `results` contains trending items, and `fallback_reason` is added.  

---

#### **4. Interaction Tracking**  
**Endpoints**:
1. **Log an Interaction**
  **Method**:
    POST /api/v1/interactions/interactions

  **Body**:
  ```json  
  {
    "user_id": "user123",
    "event_type": "product_click", 
    "product_id": "ABCD1234XY" 
  }

  OR 

  {
    "user_id": "user123",
    "event_type": "search_query",
    "query": "red shoes"  
  }
  ```

  **Output**:  
  - **Success (200)**: Empty body.  
  - **Errors**:  
    - `400 Bad Request`: Missing `product_id` (for `product_click`) or `query` (for `search_query`).  
    - `422 Unprocessable Entity`: Invalid `event_type` or schema validation failure.  


**Validation Rules:**
- `user_id`: 1-50 alphanumeric characters
- `event_type`: Must be 'product_click' or 'search_query'
- `product_id`: 10 uppercase alphanumeric characters (for product clicks)
- `query`: Non-empty string (for search queries)

2. **Retrieve User Interactions**
  **Method**:
    **GET /api/v1/interactions/interactions/{user_id}?days=30**

    **Parameters:**
    - user_id: Your user identifier
    - days (optional): Number of days to retrieve interactions (default: 30)

---

### **Input Validation Summary**  
| Parameter         | Validation Rules                                  |  
|-------------------|---------------------------------------------------|  
| `user_id`         | Regex: `^[a-zA-Z0-9]{1,50}$`                      |  
| `product_id`      | Regex: `^[A-Z0-9]{10}$` (uppercase)               |  
| `query`           | Trimmed length ≥1, max 255 chars                  |  
| `response_limit`  | Integer clamped to endpoint-specific ranges       |  
| `event_type`      | Must be `product_click` or `search_query`         |  

---

### **Edge Cases & Special Conditions**  
1. **New Users**:  
   - No interaction history → `personalized` array is empty.  
   - Recommendations prioritize `trending`, `best_value`, and `top_categories`.  
2. **Zero Interactions**:  
   - Treated as new user until first `product_click` or `search_query`.  
3. **Stale Profiles**:  
   - After 30 days of inactivity, interaction weights decay; recommendations revert to trending.  
4. **Search Fallback**:  
   - If no search matches, return trending products with `fallback_reason`.  

This ensures robust handling of all frontend input/output scenarios while adhering to latency and personalization goals.