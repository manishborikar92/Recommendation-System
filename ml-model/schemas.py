# schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class ProductResponse(BaseModel):
    id: str
    name: str
    main_category: str
    sub_category: str
    image: Optional[str]
    link: Optional[str]
    rating: Optional[float]
    review_count: Optional[int]
    price: Decimal
    original_price: Optional[Decimal]
    discount_ratio: Optional[float]
    
    @classmethod
    def from_db_row(cls, row):
        return cls(
            id=row['id'],
            name=row['name'],
            main_category=row['main_category'],
            sub_category=row['sub_category'],
            image=row['image'],
            link=row['link'],
            rating=row['ratings'],
            review_count=row['no_of_ratings'],
            price=row['discount_price'],
            original_price=row['actual_price'],
            discount_ratio=float(row['discount_ratio']) if row['discount_ratio'] else None
        )
