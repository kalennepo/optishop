from typing import List, Optional, Tuple, Dict
from backend.models.store import Store
from backend.models.aisle import Aisle
from backend.models.grocery_item import GroceryItem
from backend.repositories.store import StoreRepository
from backend.repositories.aisle import AisleRepository
from backend.repositories.item import ItemRepository

class StoreEditorService:
    """
    Backend foundation for the Store Layout Editor.
    Handles the creation and manipulation of the store's physical layout.
    """
    def __init__(self, store_repo: StoreRepository, aisle_repo: AisleRepository, item_repo: ItemRepository):
        self.store_repo = store_repo
        self.aisle_repo = aisle_repo
        self.item_repo = item_repo

    # --- Store Management ---
    def create_store(self, name: str, width: float, height: float) -> Store:
        store = Store(name=name, width=width, height=height)
        return self.store_repo.add(store)

    def get_store(self, store_id: int) -> Optional[Store]:
        return self.store_repo.get_by_id(store_id)

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
        return self.aisle_repo.add(aisle)

    def update_aisle(self, aisle_id: int, **kwargs) -> Optional[Aisle]:
        """Update aisle properties like name or dimensions."""
        aisle = self.aisle_repo.get_by_id(aisle_id)
        if not aisle:
            return None

        # Predict new dimensions
        new_x_min = kwargs.get('x_min', aisle.x_min)
        new_y_min = kwargs.get('y_min', aisle.y_min)
        new_x_max = kwargs.get('x_max', aisle.x_max)
        new_y_max = kwargs.get('y_max', aisle.y_max)
        new_name = kwargs.get('name', aisle.name)
        
        store = aisle.store

        # Re-validate after update if dimensions changed
        if new_x_min < 0 or new_x_max > store.width or new_y_min < 0 or new_y_max > store.height:
             raise ValueError("Updated aisle dimensions are outside of store boundaries")
             
        if new_x_min >= new_x_max or new_y_min >= new_y_max:
             raise ValueError("Invalid coordinates: x_min must be less than x_max, etc.")
             
        # Check for overlaps with *other* aisles
        for existing_aisle in store.aisles:
            if existing_aisle.id == aisle_id:
                continue
                
            overlap_x = new_x_min < existing_aisle.x_max and new_x_max > existing_aisle.x_min
            overlap_y = new_y_min < existing_aisle.y_max and new_y_max > existing_aisle.y_min
            
            if overlap_x and overlap_y:
                raise ValueError(f"Aisle '{new_name}' overlaps with existing structure '{existing_aisle.name}'")

        # Apply changes
        for key, value in kwargs.items():
            if hasattr(aisle, key):
                setattr(aisle, key, value)

        return self.aisle_repo.update(aisle)

    def delete_aisle(self, aisle_id: int) -> bool:
        aisle = self.aisle_repo.get_by_id(aisle_id)
        if aisle:
            return self.aisle_repo.delete(aisle)
        return False

    # --- Item Management ---
    def add_item_to_aisle(self, aisle_id: int, name: str, pos_x: float, pos_y: float) -> Optional[GroceryItem]:
        """
        Adds a grocery item to an aisle.
        Validation: Is the item near or inside the aisle?
        """
        aisle = self.aisle_repo.get_by_id(aisle_id)
        if not aisle:
            return None

        item = GroceryItem(aisle_id=aisle_id, name=name, pos_x=pos_x, pos_y=pos_y)
        return self.item_repo.add(item)

    def update_item(self, item_id: int, **kwargs) -> Optional[GroceryItem]:
        """Update an item's position, name, or aisle association."""
        item = self.item_repo.get_by_id(item_id)
        if not item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)

        return self.item_repo.update(item)

    def delete_item(self, item_id: int) -> bool:
        item = self.item_repo.get_by_id(item_id)
        if item:
            return self.item_repo.delete(item)
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
