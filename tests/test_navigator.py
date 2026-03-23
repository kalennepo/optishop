import sys
import os

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.store import Store
from backend.models.aisle import Aisle
from backend.models.grocery_item import GroceryItem
from backend.logic.store_map import StoreMap
from backend.logic.navigator import AStarNavigator

def test_pathfinding():
    # 1. Setup Test Store
    test_store = Store(name="Pathfinding Store")
    
    # A single large aisle blocking the middle
    # Aisle: x from 4.0 to 6.0, y from 1.0 to 5.0
    aisle = Aisle(name="Middle Aisle", x_min=4.0, y_min=1.0, x_max=6.0, y_max=5.0)
    test_store.aisles = [aisle]
    
    # 2. Setup Map (10m x 7m)
    store_map = StoreMap(width=10, height=7, resolution=1.0)
    store_map.load_from_store(test_store)
    
    # 3. Setup Navigator
    navigator = AStarNavigator(store_map)
    
    # 4. Find Path from (1, 3) to (9, 3) - Must go around the aisle
    start = (1.5, 3.5)
    end = (8.5, 3.5)
    
    path = navigator.find_path(start, end)
    
    # 5. Visualize
    print(f"Pathfinding Test: {start} -> {end}")
    print("Legend: . = Walkable, # = Aisle, @ = Path, S = Start, E = End")
    
    path_grid_coords = []
    if path:
        path_grid_coords = [store_map.world_to_grid(x, y) for x, y in path]
        
    start_grid = store_map.world_to_grid(start[0], start[1])
    end_grid = store_map.world_to_grid(end[0], end[1])

    for r in range(store_map.rows):
        row_str = ""
        for c in range(store_map.cols):
            curr_pos = (r, c)
            if curr_pos == start_grid:
                row_str += "S "
            elif curr_pos == end_grid:
                row_str += "E "
            elif curr_pos in path_grid_coords:
                row_str += "@ "
            elif not store_map.grid[r][c]:
                row_str += "# "
            else:
                row_str += ". "
        print(row_str)
        
    assert path is not None, "Path should be found"
    print(f"\nPath found with {len(path)} steps.")
    print("Test passed successfully!")

if __name__ == "__main__":
    test_pathfinding()
