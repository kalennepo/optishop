from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session
from backend.models.store import Store
from backend.models.aisle import Aisle
from backend.models.grocery_item import GroceryItem

class StoreEditorService:
    """
    Backend foundation for the Store Layout Editor.
    Handles the creation and manipulation of the store's physical layout.
    """
    def __init__(self, db: Session):
        self.db = db

    # --- Store Management ---
    def create_store(self, name: str, width: float, height: float) -> Store:
        store = Store(name=name, width=width, height=height)
        self.db.add(store)
        self.db.commit()
        self.db.refresh(store)
        return store

    def get_store(self, store_id: int) -> Optional[Store]:
        return self.db.query(Store).filter(Store.id == store_id).first()

    # --- Aisle Management ---
    def add_aisle(self, store_id: int, name: str, x_min: float, y_min: float, x_max: float, y_max: float) -> Optional[Aisle]:
        """
        Adds an aisle and validates that it is within the store's boundaries and doesn't overlap.
        """
        store = self.get_store(store_id)
        if not store:
            return None

        # Validation: Is the aisle within the store boundaries?
        if x_min < 0 or x_max > store.width or y_min < 0 or y_max > store.height:
            raise ValueError(f"Aisle '{name}' is outside of the store boundaries ({store.width}x{store.height})")
        
        # Validation: Does x_min < x_max and y_min < y_max?
        if x_min >= x_max or y_min >= y_max:
            raise ValueError("Invalid coordinates: x_min must be less than x_max, etc.")

        # Validation: Check for overlaps with existing aisles
        for existing_aisle in store.aisles:
            # Two rectangles overlap if they intersect on both axes
            overlap_x = x_min < existing_aisle.x_max and x_max > existing_aisle.x_min
            overlap_y = y_min < existing_aisle.y_max and y_max > existing_aisle.y_min
            
            if overlap_x and overlap_y:
                raise ValueError(f"Aisle '{name}' overlaps with existing structure '{existing_aisle.name}'")

        aisle = Aisle(store_id=store_id, name=name, x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max)
        self.db.add(aisle)
        self.db.commit()
        self.db.refresh(aisle)
        return aisle

    def update_aisle(self, aisle_id: int, **kwargs) -> Optional[Aisle]:
        """Update aisle properties like name or dimensions."""
        aisle = self.db.query(Aisle).filter(Aisle.id == aisle_id).first()
        if not aisle:
            return None

        for key, value in kwargs.items():
            if hasattr(aisle, key):
                setattr(aisle, key, value)
        
        # Re-validate after update if dimensions changed
        store = aisle.store
        if aisle.x_min < 0 or aisle.x_max > store.width or aisle.y_min < 0 or aisle.y_max > store.height:
             raise ValueError("Updated aisle dimensions are outside of store boundaries")

        self.db.commit()
        self.db.refresh(aisle)
        return aisle

    def delete_aisle(self, aisle_id: int) -> bool:
        aisle = self.db.query(Aisle).filter(Aisle.id == aisle_id).first()
        if aisle:
            self.db.delete(aisle)
            self.db.commit()
            return True
        return False

    # --- Item Management ---
    def add_item_to_aisle(self, aisle_id: int, name: str, pos_x: float, pos_y: float) -> Optional[GroceryItem]:
        """
        Adds a grocery item to an aisle.
        Validation: Is the item near or inside the aisle?
        """
        aisle = self.db.query(Aisle).filter(Aisle.id == aisle_id).first()
        if not aisle:
            return None

        item = GroceryItem(aisle_id=aisle_id, name=name, pos_x=pos_x, pos_y=pos_y)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def move_item(self, item_id: int, new_x: float, new_y: float, new_aisle_id: Optional[int] = None) -> Optional[GroceryItem]:
        item = self.db.query(GroceryItem).filter(GroceryItem.id == item_id).first()
        if not item:
            return None
        
        item.pos_x = new_x
        item.pos_y = new_y
        if new_aisle_id:
            item.aisle_id = new_aisle_id

        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item_id: int) -> bool:
        item = self.db.query(GroceryItem).filter(GroceryItem.id == item_id).first()
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False

    # --- Layout Overview ---
    def get_full_layout(self, store_id: int) -> Dict:
        """Returns a nested dictionary of the store's entire layout for the frontend editor."""
        store = self.get_store(store_id)
        if not store:
            return {}

        return {
            "id": store.id,
            "name": store.name,
            "width": store.width,
            "height": store.height,
            "aisles": [
                {
                    "id": a.id,
                    "name": a.name,
                    "x_min": a.x_min,
                    "y_min": a.y_min,
                    "x_max": a.x_max,
                    "y_max": a.y_max,
                    "items": [{"id": i.id, "name": i.name, "x": i.pos_x, "y": i.pos_y} for i in a.items]
                } for a in store.aisles
            ]
        }
