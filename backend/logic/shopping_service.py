from typing import List, Tuple, Optional, Dict
from sqlalchemy.orm import Session
from backend.models.store import Store
from backend.models.aisle import Aisle
from backend.models.grocery_item import GroceryItem
from backend.logic.store_map import StoreMap
from backend.logic.routing_engine import RoutingEngine

class ShoppingService:
    """
    The Master Service that coordinates the entire shopping route generation.
    It ties the Database, Map, and RoutingEngine together.
    """
    def __init__(self, db: Session):
        self.db = db

    def generate_route(
        self, 
        store_id: int, 
        item_names: List[str], 
        entrance: Tuple[float, float] = (1.0, 1.0), 
        exit_pos: Tuple[float, float] = (1.0, 1.0)
    ) -> Dict:
        """
        Generates a complete, optimized shopping path.
        """
        # 1. Fetch the store and its layout from DB
        store = self.db.query(Store).filter(Store.id == store_id).first()
        if not store:
            return {"error": "Store not found"}

        # 2. Find the requested items in this store
        found_items = []
        all_store_items = []
        for aisle in store.aisles:
            all_store_items.extend(aisle.items)

        for name in item_names:
            match = next((i for i in all_store_items if i.name.lower() == name.lower()), None)
            if match:
                found_items.append(match)

        if not found_items:
            return {"error": "No items found from the list"}

        # 3. Initialize the StoreMap and RoutingEngine
        store_map = StoreMap()
        store_map.load_from_store(store) # Loads a default grid graph
        
        engine = RoutingEngine(store_map)

        # 4. Step 1: Optimize the ORDER of items (TSP)
        optimized_item_sequence = engine.get_optimal_item_sequence(entrance, exit_pos, found_items)

        # 5. Step 2: Generate the detailed walking PATH between each stop
        full_path_nodes: List[str] = []
        current_node = store_map.get_nearest_node(*entrance)
        
        # Create a list of target nodes (including final exit)
        targets = []
        for item in optimized_item_sequence:
            targets.append(store_map.get_nearest_node(item.pos_x, item.pos_y))
        targets.append(store_map.get_nearest_node(*exit_pos))
        
        total_distance = 0.0
        for target_node in targets:
            segment_nodes, segment_cost = engine.find_shortest_path(current_node, target_node)
            if segment_nodes:
                if full_path_nodes:
                    full_path_nodes.extend(segment_nodes[1:])
                else:
                    full_path_nodes.extend(segment_nodes)
                total_distance += segment_cost
                current_node = target_node
            else:
                print(f"Warning: Could not find path to node {target_node}")

        # Convert node IDs back to (x, y) coordinates
        path_coordinates = [store_map.get_node_coords(node_id) for node_id in full_path_nodes]

        return {
            "store_name": store.name,
            "optimized_order": [item.name for item in optimized_item_sequence],
            "optimized_items": optimized_item_sequence,
            "total_waypoints": len(optimized_item_sequence),
            "path_coordinates": path_coordinates,
            "total_steps": len(path_coordinates),
            "estimated_distance": total_distance
        }
