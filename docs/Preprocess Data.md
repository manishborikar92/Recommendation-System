
**Processed CSV File Requirements:**

| Column Name       | Data Type | Description                                             |
|-------------------|-----------|---------------------------------------------------------|
| id                | str       | Unique product ID (10 characters)                       |
| name              | str       | Product title/name                                      |
| main_category     | str       | Broad product category                                  |
| sub_category      | str       | Specific product sub-category                           |
| image             | str       | URL to product image                                    |
| link              | str       | Product page URL                                        |
| ratings           | float     | Average rating (0.0-5.0)                                |
| no_of_ratings     | int       | Total number of ratings                                 |
| discount_price    | float     | Current discounted price                                |
| actual_price      | float     | Original price before discount                          |
| discount_ratio    | float     | Calculated (actual_price - discount_price)/actual_price |