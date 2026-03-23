from typing import List, Tuple, Optional, Dict
from sqlalchemy.orm import Session
from backend.models.store import Store
from backend.models.aisle import Aisle
from backend.models.grocery_item import GroceryItem
from backend.logic.store_map import StoreMap
from backend.logic.navigator import AStarNavigator
from backend.logic.optimizer import RouteOptimizer

class ShoppingService:
    """
    The Master Service that coordinates the entire shopping route generation.
    It ties the Database, Map, Navigator, and Optimizer together.
    """
    def __init__(self, db: Session):
        self.db = db

    def generate_route(
        self, 
        store_id: int, 
        item_names: List[str], 
        entrance: Tuple[float, float] = (1.0, 1.0), 
        exit_pos: Tuple[float, float] = (1.0, 1.0),
        map_resolution: float = 0.5
    ) -> Dict:
        """
        Generates a complete, optimized shopping path.
        """
        # 1. Fetch the store and its layout from DB
        store = self.db.query(Store).filter(Store.id == store_id).first()
        if not store:
            return {"error": "Store not found"}

        # 2. Find the requested items in this store
        # We search through all items in all aisles of this store
        found_items = []
        all_store_items = []
        for aisle in store.aisles:
            all_store_items.extend(aisle.items)

        for name in item_names:
            # Simple case-insensitive match
            match = next((i for i in all_store_items if i.name.lower() == name.lower()), None)
            if match:
                found_items.append(match)

        if not found_items:
            return {"error": "No items found from the list"}

        # 3. Initialize the Logic Engines
        # We'll assume a default store size for now or calculate based on aisles
        max_x = max([a.x_max for a in store.aisles] + [entrance[0], exit_pos[0]]) + 2.0
        max_y = max([a.y_max for a in store.aisles] + [entrance[1], exit_pos[1]]) + 2.0
        
        store_map = StoreMap(width=max_x, height=max_y, resolution=map_resolution)
        store_map.load_from_store(store)
        
        navigator = AStarNavigator(store_map)
        optimizer = RouteOptimizer(navigator)

        # 4. Step 1: Optimize the ORDER of items (TSP)
        optimized_item_sequence = optimizer.get_optimal_route(entrance, exit_pos, found_items)

        # 5. Step 2: Generate the detailed walking PATH between each stop
        # Sequence: Entrance -> Item 1 -> Item 2 -> ... -> Item N -> Exit
        full_path: List[Tuple[float, float]] = []
        current_pos = entrance
        
        # Create a list of waypoints (including final exit)
        stops = [(item.pos_x, item.pos_y) for item in optimized_item_sequence] + [exit_pos]
        
        for stop in stops:
            segment = navigator.find_path(current_pos, stop)
            if segment:
                # Add segment to full path (avoid duplicating the junction point)
                if full_path:
                    full_path.extend(segment[1:])
                else:
                    full_path.extend(segment)
                current_pos = stop
            else:
                # If a segment fails, we just skip it (or handle error)
                print(f"Warning: Could not find path to {stop}")

        return {
            "store_name": store.name,
            "optimized_order": [item.name for item in optimized_item_sequence],
            "optimized_items": optimized_item_sequence,
            "total_waypoints": len(optimized_item_sequence),
            "path_coordinates": full_path,
            "total_steps": len(full_path),
            "estimated_distance": len(full_path) * map_resolution
        }
