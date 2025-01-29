# Steps to run /recommend api

```
python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

python -m pip freeze > requirements.txt 

python utils/preprocessing.py

python utils/clean_csv.py

python utils/productdb.py

python utils/recommender.py

python app.py
```