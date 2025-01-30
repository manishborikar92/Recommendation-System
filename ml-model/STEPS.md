### Steps to run /recommend api

```
python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

python -m pip freeze > requirements.txt 

python data_preprocessing.py

python data_loader.py

uvicorn main:app --host 0.0.0.0 --port 8000
```

### API Endpoints
```
GET /recommend?user_id=<USER_ID> → Returns 20 personalized products
GET /similar?product_id=<PRODUCT_ID> → Returns 12 similar products
```

### Data Flow:
```
Frontend → API → [Authentication] → [Rate Limiting] → [Recommendation Engine]
                   ↑                      |
                   |                      ↓
                   └── [User History] ← PostgreSQL
                        [Product Data] ←─┘
                        [ML Model] ←───┘
```