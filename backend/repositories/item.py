from sqlalchemy.orm import Session
from backend.models.grocery_item import GroceryItem
from backend.repositories.base import BaseRepository

class ItemRepository(BaseRepository[GroceryItem]):
    def __init__(self, db: Session):
        super().__init__(db, GroceryItem)
