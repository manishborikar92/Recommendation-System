# Steps to run /recommend api

```
python3.10 -m venv .venv

pip install -r requirements.txt

python -m pip freeze > requirements  

python utils/preprocessing.py

python utils/clean_csv.py

python utils/productdb.py

python utils/recommender.py

python app.py
```