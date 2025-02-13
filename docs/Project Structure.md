### **CSV File Columns and Rows**
```
id,name,main_category,sub_category,image,link,ratings,no_of_ratings,discount_price,actual_price,discount_ratio
AF321D06AE,SOUNDLINK Soft Silicone Ear Plugs - 2 Pcs/Box Reusable Waterproof Earplugs Prevent Water Reduce Noise for Swimming and Bat...,stores,Amazon Fashion,https://m.media-amazon.com/images/I/51ETdNss3VL._AC_UL320_.jpg,https://www.amazon.in/SOUNDLINK-Soft-Silicone-Ear-Plugs/dp/B075GKQCG2/ref=sr_1_6956?qid=1679212438&s=apparel&sr=1-6956,3.5,115,243.0,1240.0,0.804

```

### **Project Structure**  
```  
project/  
├── data/                    
│   ├── raw/   
│   │   └── Amazon-Products-Raw.csv  
│   └── processed/
│       └── Amazon-Products-Optimized.csv
│
├── database/                   
│   ├── csv_importer.py         # Upload `Amazon-Products-Optimized.csv` data to database
│   └── interactions.py         # Create tablename with `userId` for each new user
│
├── main.py                     # FastAPI app setup    
├── schemas.py                  # Pydantic input/output validation  
├── routers/                    # API endpoints  
│   ├── recommendations.py      # `/home`, `/product`, `/search`  
│   └── interactions.py         # `/interactions`: Upload to database
├── services/                   # Business logic  
│   ├── recommender.py          # Hybrid merging logic  
│   ├── search.py               # Query expansion  
│   └── models.py               # ML model wrappers (TF-IDF, FP-Growth)  
├── ml/                         # Model training scripts  
│   ├── train_content_model.py  # TF-IDF embeddings  
│   └── train_fp_growth.py      # Association rules  
└── config/                      
    └── settings.py             # Environment variables (DB URL, weights)  
``` 

### **Completed Works**
 - **Data Processing**: Cleaned and optimized the raw data.
 - **Database**: Created a PostgreSQL database and uploaded the optimized data.
 - **Database** : Created a table for each user to store their interactions.
 - **API**: Developed a FastAPI application with endpoints for interactions
 - **main. py**: FastAPI app setup
 - **ml/train_content_model.py**: Complited TF-IDF embeddings
 - **services/content_recommender.py**: Complted model loading and prediction
 - **routers/interactions.py**: Created an endpoint to upload interactions to the database
 - **routers/recommendations.py**: Created an endpoint to get recommendations for recommendation similar to the product