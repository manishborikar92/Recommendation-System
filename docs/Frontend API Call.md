### Step-by-Step Explanation & API Integration from React-Vite Frontend

To integrate the recommendation system APIs into a React-Vite app, follow these steps for each endpoint. We’ll use Axios for HTTP requests and centralized error handling.

---

### **1. `/recommendations/home` Endpoint**

#### **Frontend API Call**
```javascript
// api.js (Service Module)
import axios from 'axios';

const handleError = (error) => {
  if (error.response) {
    console.error('API Error:', error.response.status, error.response.data);
  } else {
    console.error('Network/Request Error:', error.message);
  }
};

export const getHomeRecommendations = async (userId, responseLimit = 20) => {
  // Validate `user_id` client-side to avoid unnecessary requests
  if (!/^[a-zA-Z0-9]{1,50}$/.test(userId)) {
    throw new Error('Invalid user_id format.');
  }

  const params = {
    user_id: userId,
    response_limit: Math.min(Math.max(responseLimit, 1), 60), // Clamp to 1-60
  };

  try {
    const response = await axios.get('/recommendations/home', { params });
    return response.data;
  } catch (error) {
    handleError(error);
    throw error; // Re-throw for component-level handling
  }
};
```

#### **Example Usage in React Component**
```javascript
import { useEffect, useState } from 'react';
import { getHomeRecommendations } from './api';

const HomePage = ({ userId }) => {
  const [recommendations, setRecommendations] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await getHomeRecommendations(userId);
        setRecommendations(data);
      } catch (error) {
        // Show user-friendly error message
      }
    };
    loadData();
  }, [userId]);

  // Render logic for personalized, trending, etc.
};
```

#### **Request Example**
```
GET /recommendations/home?user_id=U12345&response_limit=20
```

#### **Response Example (200 OK)**
```json
{
  "personalized": [],
  "trending": [
    {
      "id": "B08CF3D7QR",
      "name": "Wireless Headphones",
      "category": "Electronics > Audio",
      "image": "https://example.com/image.jpg",
      "price": 59.99,
      "original_price": 99.99,
      "rating": 4.5,
      "reviews": 1500,
      "discount_ratio": 0.4001
    }
  ],
  "best_value": [/* ... */],
  "top_categories": {
    "Electronics": [/* ... */],
    "Fashion": [/* ... */]
  },
  "diverse_picks": [/* ... */]
}
```

#### **Error Handling**
- **400 Bad Request**: Invalid `user_id` (e.g., special characters).
- **500 Internal Server Error**: Display a generic error message like "Recommendations unavailable."

---

### **2. `/recommendations/product/{product_id}` Endpoint**

#### **Frontend API Call**
```javascript
export const getProductRecommendations = async (productId, responseLimit = 20) => {
  // Validate product_id format before sending
  if (!/^[A-Z0-9]{10}$/.test(productId)) {
    throw new Error('Invalid product_id format.');
  }

  const params = {
    response_limit: Math.min(Math.max(responseLimit, 1), 60),
  };

  try {
    const response = await axios.get(`/recommendations/product/${productId}`, { params });
    return response.data;
  } catch (error) {
    if (error.response?.status === 404) {
      console.error('Product not found.');
    }
    handleError(error);
    throw error;
  }
};
```

#### **Example Usage**
```javascript
// ProductPage.jsx
const ProductPage = ({ productId }) => {
  const [similarProducts, setSimilarProducts] = useState([]);

  useEffect(() => {
    const loadSimilarProducts = async () => {
      try {
        const data = await getProductRecommendations(productId);
        setSimilarProducts(data.similar);
      } catch (error) {
        // Handle error
      }
    };
    loadSimilarProducts();
  }, [productId]);
};
```

#### **Request Example**
```
GET /recommendations/product/B08CF3D7QR?response_limit=10
```

#### **Response Example (200 OK)**
```json
{
  "similar": [
    {
      "id": "B08CF3D7QR",
      "name": "Wireless Headphones",
      "category": "Electronics > Audio",
      "image": "https://example.com/image.jpg",
      "price": 59.99,
      "original_price": 99.99,
      "rating": 4.5,
      "reviews": 1500,
      "discount_ratio": 0.4001
    }
  ]
}
```

#### **Errors**
- **400 Bad Request**: Invalid `product_id` (e.g., lowercase letters).
- **404 Not Found**: Product does not exist.

---

### **3. `/recommendations/search` Endpoint**

#### **Frontend API Call**
```javascript
export const searchRecommendations = async (query, responseLimit = 2000) => {
  const trimmedQuery = query.trim();
  if (trimmedQuery.length === 0) {
    throw new Error('Search query cannot be empty.');
  }

  const params = {
    query: trimmedQuery,
    response_limit: Math.min(Math.max(responseLimit, 1), 6000),
  };

  try {
    const response = await axios.get('/recommendations/search', { params });
    return response.data;
  } catch (error) {
    handleError(error);
    throw error;
  }
};
```

#### **Example Usage**
```javascript
// SearchComponent.jsx
const SearchComponent = () => {
  const [results, setResults] = useState([]);

  const handleSearch = async (searchTerm) => {
    try {
      const data = await searchRecommendations(searchTerm);
      setResults(data.results);
      if (data.fallback_reason) {
        console.log('Showing trending items due to no matches.');
      }
    } catch (error) {
      // Handle error
    }
  };
};
```

#### **Request Example**
```
GET /recommendations/search?query=wireless%20earbuds&response_limit=50
```

#### **Response Example (200 OK)**
```json
{
  "results": [
    {
      "id": "B08CF3D7QR",
      "name": "Wireless Headphones",
      "category": "Electronics > Audio",
      "price": 59.99,
      // ... other fields
    }
  ],
  "fallback_reason": "no_search_matches"
}
```

#### **Errors**
- **400 Bad Request**: Empty query after trimming (handled client-side before the request).
- **404 Not Found**: Depends on API implementation (see problem statement ambiguity).

---

### **4. Interaction Tracking (`POST /interactions`)**

#### **Frontend API Call**
```javascript
export const trackInteraction = async (interactionData) => {
  // Validate event_type and required fields
  if (!['product_click', 'search_query'].includes(interactionData.event_type)) {
    throw new Error('Invalid event_type.');
  }

  try {
    await axios.post('/interactions', interactionData);
  } catch (error) {
    handleError(error);
    throw error;
  }
};
```

#### **Example Usage**
```javascript
// Track product click
const ProductCard = ({ productId, userId }) => {
  const handleClick = async () => {
    try {
      await trackInteraction({
        user_id: userId,
        event_type: 'product_click',
        product_id: productId,
      });
    } catch (error) {
      // Log error silently
    }
  };

  return <div onClick={handleClick}>...</div>;
};

// Track search query
const SearchBar = ({ userId }) => {
  const handleSearch = async (query) => {
    try {
      await trackInteraction({
        user_id: userId,
        event_type: 'search_query',
        query: query,
      });
    } catch (error) {
      // Log error silently
    }
  };
};
```

#### **Request Example**
```json
POST /interactions
Body:
{
  "user_id": "U12345",
  "event_type": "product_click",
  "product_id": "B08CF3D7QR"
}
```

#### **Response Example**
- **200 OK**: Empty body.
- **400 Bad Request**: Missing `product_id` or `query`.
- **422 Unprocessable Entity**: Invalid `event_type`.

---

### **Summary**
- **Validation**: Pre-validate inputs client-side to reduce unnecessary API calls.
- **Error Handling**: Centralize error logging and provide user-friendly messages.
- **State Management**: Use React hooks (`useState`, `useEffect`) to manage API data.
- **Interaction Tracking**: Fire-and-forget approach for non-critical tracking (e.g., no UI feedback).