import sys
import os

# Add the root directory to sys.path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.logic.store_map import StoreMap

def test_store_map_graph():
    # 1. Instantiate StoreMap
    store_map = StoreMap()
    
    # 2. Test add_node
    store_map.add_node("entrance", 0.0, 0.0)
    store_map.add_node("aisle_1", 0.0, 5.0)
    
    assert store_map.has_node("entrance")
    assert store_map.has_node("aisle_1")
    assert store_map.get_node_coords("entrance") == (0.0, 0.0)
    assert store_map.get_node_coords("aisle_1") == (0.0, 5.0)
    
    # 3. Test add_directed_edge
    store_map.add_directed_edge("entrance", "aisle_1", 5.0)
    
    neighbors = store_map.get_neighbors("entrance")
    assert len(neighbors) == 1
    assert neighbors[0] == {"to": "aisle_1", "weight": 5.0}
    
    # 4. Test get_nearest_node
    # Coordinates (0.1, 4.8) should be closest to "aisle_1" (0.0, 5.0)
    nearest = store_map.get_nearest_node(0.1, 4.8)
    assert nearest == "aisle_1", f"Expected 'aisle_1', but got '{nearest}'"
    
    # Coordinates (0.1, 0.1) should be closest to "entrance" (0.0, 0.0)
    nearest = store_map.get_nearest_node(0.1, 0.1)
    assert nearest == "entrance", f"Expected 'entrance', but got '{nearest}'"

    print("StoreMap Graph tests passed successfully!")

if __name__ == "__main__":
    test_store_map_graph()
