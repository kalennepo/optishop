from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.db.db_connection import Base 

class Store(Base):
    __tablename__ = "stores"

    # Primary key for the store
    id = Column(Integer, primary_key=True, index=True)
    
    # Name of the store (e.g., "OptiShop Test Store")
    name = Column(String(100), index=True)
    
    # Object-Oriented Relationship: A store can have many aisles.
    # We use the string "Aisle" to refer to the model in aisle.py.
    # 'cascade' ensures that if a store is deleted, its layout is also cleaned up.
    aisles = relationship("Aisle", back_populates="store", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Store(name='{self.name}')>"
