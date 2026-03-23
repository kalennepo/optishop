import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.store import Store
from backend.models.aisle import Aisle
from backend.models.grocery_item import GroceryItem
from backend.logic.store_map import StoreMap
from backend.logic.navigator import AStarNavigator
from backend.logic.optimizer import RouteOptimizer

def test_route_optimization():
    # 1. Setup Store with 3 items in a line
    # Map is 20m wide. Entrance at 0, items at 5, 15, 10, Exit at 20.
    # Logic: The best route should be Entrance(0) -> 5 -> 10 -> 15 -> Exit(20)
    # If it was Greedy, it might go 0 -> 5 -> 15 -> 10 -> 20 (longer)
    
    test_store = Store(name="Optimization Test Store")
    # No aisles for this simple test to make distances predictable
    test_store.aisles = []
    
    item_a = GroceryItem(name="Item 5m", pos_x=5.0, pos_y=1.0)
    item_b = GroceryItem(name="Item 15m", pos_x=15.0, pos_y=1.0)
    item_c = GroceryItem(name="Item 10m", pos_x=10.0, pos_y=1.0)
    
    items = [item_a, item_b, item_c]
    
    # 2. Setup Logic
    store_map = StoreMap(width=25, height=5, resolution=1.0)
    navigator = AStarNavigator(store_map)
    optimizer = RouteOptimizer(navigator)
    
    # 3. Optimize
    entrance = (1.0, 1.0)
    exit_pos = (23.0, 1.0)
    
    print(f"Optimizing route for: {[i.name for i in items]}")
    optimized_items = optimizer.get_optimal_route(entrance, exit_pos, items)
    
    # 4. Results
    order_names = [i.name for i in optimized_items]
    print(f"Optimal Order: {order_names}")
    
    # Check if the order is logical (5 -> 10 -> 15)
    assert order_names == ["Item 5m", "Item 10m", "Item 15m"]
    print("Test passed successfully!")

if __name__ == "__main__":
    test_route_optimization()
