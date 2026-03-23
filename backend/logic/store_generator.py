from sqlalchemy.orm import Session
from backend.models.store import Store
from backend.models.aisle import Aisle
from backend.models.grocery_item import GroceryItem

class StoreGenerator:
    """
    Utility to generate a standardized 'Test Store' layout programmatically.
    """
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_test_store(self, name: str = "OptiShop Test Store"):
        # 1. Create the store
        store = Store(name=name)
        self.db.add(store)
        self.db.commit()
        self.db.refresh(store)
        
        # 2. Add some aisles (Vertical shelves)
        # Assuming a 20m x 15m store
        aisles_to_create = [
            ("Produce Aisle", 2.0, 2.0, 3.0, 10.0),
            ("Dairy Aisle", 6.0, 2.0, 7.0, 10.0),
            ("Bakery Aisle", 10.0, 2.0, 11.0, 10.0),
            ("Frozen Foods", 14.0, 2.0, 15.0, 10.0),
        ]
        
        created_aisles = []
        for a_name, x_min, y_min, x_max, y_max in aisles_to_create:
            aisle = Aisle(
                store_id=store.id,
                name=a_name,
                x_min=x_min,
                y_min=y_min,
                x_max=x_max,
                y_max=y_max
            )
            self.db.add(aisle)
            created_aisles.append(aisle)
        
        self.db.commit()
        
        # 3. Add some grocery items
        # Let's put one item in each aisle at different y-positions
        items_to_create = [
            ("Apples", created_aisles[0].id, 1.5, 3.0),
            ("Milk", created_aisles[1].id, 5.5, 5.0),
            ("Bread", created_aisles[2].id, 9.5, 7.0),
            ("Ice Cream", created_aisles[3].id, 13.5, 4.0),
        ]
        
        # Wait, if an item is at x=1.5 and the aisle is from 2.0 to 3.0,
        # it's "next to" the aisle, which is good for walkability.
        # If an item is *inside* an aisle, it won't be reachable.
        
        for i_name, aisle_id, pos_x, pos_y in items_to_create:
            item = GroceryItem(
                aisle_id=aisle_id,
                name=i_name,
                pos_x=pos_x,
                pos_y=pos_y
            )
            self.db.add(item)
        
        self.db.commit()
        print(f"Generated test store '{name}' with {len(aisles_to_create)} aisles and {len(items_to_create)} items.")
        return store
