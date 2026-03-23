import sys
import os

# Add the root directory to sys.path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.store import Store
from backend.models.aisle import Aisle
from backend.models.grocery_item import GroceryItem
from backend.logic.store_map import StoreMap

def test_map_generation():
    # 1. Create a mock store (using the classes, no DB session needed for instantiation)
    test_store = Store(name="Test Grocery Store")
    
    # 2. Add some mock aisles
    # Aisle 1: x from 2.0 to 3.0, y from 1.0 to 4.0 (A vertical shelf)
    aisle1 = Aisle(name="Aisle 1", x_min=2.0, y_min=1.0, x_max=3.0, y_max=4.0)
    # Aisle 2: x from 6.0 to 7.0, y from 1.0 to 4.0
    aisle2 = Aisle(name="Aisle 2", x_min=6.0, y_min=1.0, x_max=7.0, y_max=4.0)
    
    test_store.aisles = [aisle1, aisle2]
    
    # 3. Create a map (10m x 6m) with 1m resolution for easy visualization
    store_map = StoreMap(width=10, height=6, resolution=1.0)
    store_map.load_from_store(test_store)
    
    # 4. Visualize the grid (ASCII)
    print(f"Store: {test_store.name}")
    print(f"Grid Dimensions: {store_map.rows} rows x {store_map.cols} cols")
    print("Legend: . = Walkable, # = Aisle (Blocked)")
    
    for r in range(store_map.rows):
        row_str = ""
        for c in range(store_map.cols):
            if store_map.grid[r][c]:
                row_str += ". "
            else:
                row_str += "# "
        print(row_str)
    
    # 5. Basic Assertions
    # Aisle 1 (x=2 to 3, y=1 to 4) should be blocked.
    # world_to_grid(2.5, 2.5) should be blocked.
    assert store_map.is_walkable(2.5, 2.5) == False, "Aisle 1 should be blocked"
    assert store_map.is_walkable(0.5, 0.5) == True, "Entrance area should be walkable"
    
    print("\nTest passed successfully!")

if __name__ == "__main__":
    test_map_generation()
