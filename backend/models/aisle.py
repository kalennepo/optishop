from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.db_connection import Base 

class Aisle(Base):
    __tablename__ = "aisles"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    name = Column(String(50)) 
    
    # Defining the rectangle (Bounding Box) of the physical shelf
    x_min = Column(Float) 
    y_min = Column(Float)
    x_max = Column(Float)
    y_max = Column(Float)

    store = relationship("Store", back_populates="aisles")
    items = relationship("GroceryItem", back_populates="aisle", cascade="all, delete-orphan")
