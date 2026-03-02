from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.db_connection import Base 

class GroceryItem(Base):
    __tablename__ = "grocery_items"

    id = Column(Integer, primary_key=True, index=True)
    aisle_id = Column(Integer, ForeignKey("aisles.id")) # Links the item to a specific shelf/column
    name = Column(String(100), index=True) # e.g., "Organic Apples"
    
    # Precise coordinate of the item for the routing algorithm
    pos_x = Column(Float)
    pos_y = Column(Float)

    # OOP Relationship back to the Aisle/Column
    aisle = relationship("Aisle", back_populates="items")
