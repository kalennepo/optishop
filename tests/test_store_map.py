import sys
import os

# Add the root directory to sys.path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.logic.store_map import StoreMap

def test_store_map_graph(empty_store_map):
    # 1. Use empty_store_map fixture
    store_map = empty_store_map
    
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

def test_load_from_store_with_aisles(empty_store_map):
    # Mocking Store and Aisle
    class MockAisle:
        def __init__(self, x_min, y_min, x_max, y_max):
            self.x_min = x_min
            self.y_min = y_min
            self.x_max = x_max
            self.y_max = y_max

    class MockStore:
        def __init__(self, aisles):
            self.aisles = aisles

    # Create a store with an aisle from (1,1) to (3,3)
    # Resolution = 1.0
    aisle = MockAisle(1.0, 1.0, 3.0, 3.0)
    store = MockStore([aisle])
    
    store_map = empty_store_map
    store_map.load_from_store(store, resolution=1.0)
    
    # Node (2,2) with coords x=2, y=2 should be inside the aisle (1<=2<=3, 1<=2<=3)
    # So node_2_2 should NOT exist.
    assert not store_map.has_node("node_2_2"), "node_2_2 should be inside the aisle and thus not exist."
    
    # Node (0,0) with coords x=0, y=0 should be outside.
    assert store_map.has_node("node_0_0"), "node_0_0 should be outside the aisle and exist."
    
    # Node (1,1) with coords x=1, y=1 is ON the boundary, so it should be UNWALKABLE
    assert not store_map.has_node("node_1_1"), "node_1_1 is on the aisle boundary and should not exist."

    # Node (4,4) with coords x=4, y=4 should be outside.
    assert store_map.has_node("node_4_4"), "node_4_4 should be outside the aisle and exist."
