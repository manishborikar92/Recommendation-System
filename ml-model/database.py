# ---------- database.py ----------
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, ForeignKey, DateTime, Index
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy.schema import CreateTable, DropTable
import os

DATABASE_URL = os.getenv("DB_URL", "postgresql://avnadmin:AVNS_OYtoI3VOGPep8jW6PgI@recommendation-system-theodinproject0622-f277.b.aivencloud.com:15032/defaultdb?sslmode=require")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String(10), primary_key=True)
    name = Column(String(500))
    main_category = Column(String(100))
    sub_category = Column(String(100))
    image = Column(String(500))
    link = Column(String(500))
    ratings = Column(Float)
    no_of_ratings = Column(Integer)
    discount_price = Column(Float)
    actual_price = Column(Float)
    discount_ratio = Column(Float)
    embeddings = Column(JSON)
    
    interactions = relationship("UserHistory", back_populates="product")

class UserHistory(Base):
    __tablename__ = "user_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), index=True)
    product_id = Column(String(10), ForeignKey('products.id', ondelete='CASCADE'))
    interaction_type = Column(String(20))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship("Product", back_populates="interactions")

    __table_args__ = (
        Index('ix_user_product', 'user_id', 'product_id'),
        Index('ix_interaction_time', 'timestamp'),
    )

def create_tables():
    # Explicit table creation order
    with engine.begin() as connection:
        connection.execute(DropTable(UserHistory.__table__, if_exists=True))
        connection.execute(DropTable(Product.__table__, if_exists=True))
        connection.execute(CreateTable(Product.__table__))
        connection.execute(CreateTable(UserHistory.__table__))

if __name__ == "__main__":
    create_tables()