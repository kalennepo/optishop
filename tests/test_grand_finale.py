import sys
import os
import pytest

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.store import Store
from backend.models.aisle import Aisle
from backend.models.grocery_item import GroceryItem
from backend.logic.shopping_service import ShoppingService

def test_full_system_graph(db_session):
    # 1. Use db_session fixture
    db = db_session

    # 2. Directly create a Test Store in the DB
    test_store = Store(name="Graph-based Grocery Store")
    db.add(test_store)
    db.commit()
    
    # Add some aisles (needed for dimensions in load_from_store)
    # Store boundaries: x=0-20, y=0-15
    aisle1 = Aisle(name="Produce", x_min=2.0, y_min=2.0, x_max=4.0, y_max=10.0, store_id=test_store.id)
    aisle2 = Aisle(name="Bakery", x_min=8.0, y_min=2.0, x_max=10.0, y_max=10.0, store_id=test_store.id)
    aisle3 = Aisle(name="Frozen", x_min=14.0, y_min=2.0, x_max=16.0, y_max=10.0, store_id=test_store.id)
    db.add_all([aisle1, aisle2, aisle3])
    db.commit()
    
    # Add some items
    item1 = GroceryItem(name="Apples", pos_x=3.0, pos_y=5.0, aisle_id=aisle1.id)
    item2 = GroceryItem(name="Bread", pos_x=9.0, pos_y=5.0, aisle_id=aisle2.id)
    item3 = GroceryItem(name="Ice Cream", pos_x=15.0, pos_y=5.0, aisle_id=aisle3.id)
    db.add_all([item1, item2, item3])
    db.commit()
    
    # 3. Create a Shopping List (deliberately out of physical order)
    shopping_list = ["Ice Cream", "Apples", "Bread"]

    # 4. Use the Shopping Service
    service = ShoppingService(db)
    entrance = (0.0, 0.0)
    exit_pos = (20.0, 0.0)
    
    result = service.generate_route(
        store_id=test_store.id,
        item_names=shopping_list,
        entrance=entrance,
        exit_pos=exit_pos
    )

    assert "error" not in result

    # 5. Basic Assertions
    # Optimal order from (0,0) to (20,0) with these items should be: Apples -> Bread -> Ice Cream
    assert result['optimized_order'] == ["Apples", "Bread", "Ice Cream"]
    assert len(result['path_coordinates']) > 0
    assert all(isinstance(p, tuple) and len(p) == 2 for p in result['path_coordinates'])
