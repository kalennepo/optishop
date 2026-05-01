import pytest
import math
from backend.logic.strategies.nearest_neighbor import NearestNeighborStrategy

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
        _, x1_str, y1_str = node_a.split('_')
        _, x2_str, y2_str = node_b.split('_')
        x1, y1 = float(x1_str), float(y1_str)
        x2, y2 = float(x2_str), float(y2_str)
        dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        return (["path"], dist)

def test_nn_0_items():
    engine = MockRoutingEngine()
    strategy = NearestNeighborStrategy()
    
    entrance = (0, 0)
    exit_pos = (10, 10)
    items = []
    
    result = strategy.optimize(engine, entrance, exit_pos, items)
    assert result == []

def test_nn_1_item():
    engine = MockRoutingEngine()
    strategy = NearestNeighborStrategy()
    
    entrance = (0, 0)
    exit_pos = (10, 10)
    item = MockItem("Milk", 5, 5)
    items = [item]
    
    result = strategy.optimize(engine, entrance, exit_pos, items)
    assert result == [item]

def test_nn_multiple_items():
    engine = MockRoutingEngine()
    strategy = NearestNeighborStrategy()
    
    entrance = (0, 0)
    exit_pos = (10, 10)
    # The Nearest Neighbor will go to the closest item from current position
    # From (0,0), closest is (2,2)
    # From (2,2), closest is (3,3)
    # From (3,3), closest is (8,8)
    item1 = MockItem("Milk", 8, 8) 
    item2 = MockItem("Bread", 2, 2)
    item3 = MockItem("Eggs", 3, 3)
    items = [item1, item2, item3]
    
    result = strategy.optimize(engine, entrance, exit_pos, items)
    assert result == [item2, item3, item1]

def test_nn_identical_coordinates():
    engine = MockRoutingEngine()
    strategy = NearestNeighborStrategy()
    
    entrance = (0, 0)
    exit_pos = (10, 10)
    item1 = MockItem("Milk", 5, 5)
    item2 = MockItem("Bread", 5, 5)
    item3 = MockItem("Eggs", 5, 5)
    items = [item1, item2, item3]
    
    result = strategy.optimize(engine, entrance, exit_pos, items)
    
    # Nearest neighbor should still visit all of them (distance 0 between them)
    assert len(result) == 3
    names = [item.name for item in result]
    assert "Milk" in names
    assert "Bread" in names
    assert "Eggs" in names
