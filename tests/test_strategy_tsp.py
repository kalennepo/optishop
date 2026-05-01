import pytest
import math
from backend.logic.strategies.tsp_exact import TSPExactStrategy

class MockItem:
    def __init__(self, name, pos_x, pos_y):
        self.name = name
        self.pos_x = pos_x
        self.pos_y = pos_y

class MockStoreMap:
    def get_nearest_node(self, x, y):
        return f"node_{x}_{y}"

class MockRoutingEngine:
    def __init__(self):
        self.store_map = MockStoreMap()
        
    def find_shortest_path(self, node_a, node_b):
        # Calculate euclidean distance from node names
        _, x1_str, y1_str = node_a.split('_')
        _, x2_str, y2_str = node_b.split('_')
        x1, y1 = float(x1_str), float(y1_str)
        x2, y2 = float(x2_str), float(y2_str)
        dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        return (["path"], dist)

def test_tsp_0_items():
    engine = MockRoutingEngine()
    strategy = TSPExactStrategy()
    
    entrance = (0, 0)
    exit_pos = (10, 10)
    items = []
    
    result = strategy.optimize(engine, entrance, exit_pos, items)
    assert result == []

def test_tsp_1_item():
    engine = MockRoutingEngine()
    strategy = TSPExactStrategy()
    
    entrance = (0, 0)
    exit_pos = (10, 10)
    item = MockItem("Milk", 5, 5)
    items = [item]
    
    result = strategy.optimize(engine, entrance, exit_pos, items)
    assert result == [item]

def test_tsp_2_items():
    engine = MockRoutingEngine()
    strategy = TSPExactStrategy()
    
    entrance = (0, 0)
    exit_pos = (10, 10)
    item1 = MockItem("Milk", 8, 8) # Further from entrance
    item2 = MockItem("Bread", 2, 2) # Closer to entrance
    items = [item1, item2]
    
    result = strategy.optimize(engine, entrance, exit_pos, items)
    # Best path: (0,0) -> Bread(2,2) -> Milk(8,8) -> (10,10)
    assert result == [item2, item1]

def test_tsp_15_items():
    engine = MockRoutingEngine()
    strategy = TSPExactStrategy()
    
    entrance = (0, 0)
    exit_pos = (10, 10)
    
    # Create 15 items in a straight line from entrance to exit
    # This ensures a predictable optimal path
    items = []
    expected_order = []
    for i in range(15):
        # We append them in reverse to ensure the strategy actually sorts them
        pos = (14 - i) * 0.5
        item = MockItem(f"Item_{i}", pos, pos)
        items.append(item)
        expected_order.append(item)
    
    expected_order.reverse() # Optimal is increasing distance
    
    result = strategy.optimize(engine, entrance, exit_pos, items)
    
    # Ensure they are sorted correctly
    assert [item.name for item in result] == [item.name for item in expected_order]
