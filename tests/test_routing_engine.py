import sys
import os
import pytest
from typing import NamedTuple

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.logic.store_map import StoreMap
from backend.logic.routing_engine import RoutingEngine

# Mocking a GroceryItem for simplicity in tests
class MockItem:
    def __init__(self, name, pos_x, pos_y):
        self.name = name
        self.pos_x = pos_x
        self.pos_y = pos_y

def test_routing_engine(empty_store_map):
    # 1. Setup StoreMap with a linear graph
    sm = empty_store_map
    sm.add_node("entrance", 0.0, 0.0)
    sm.add_node("node_a", 5.0, 0.0)
    sm.add_node("node_b", 10.0, 0.0)
    sm.add_node("exit", 15.0, 0.0)
    
    # Bidirectional connections (weight 5.0 each)
    nodes = ["entrance", "node_a", "node_b", "exit"]
    for i in range(len(nodes) - 1):
        u, v = nodes[i], nodes[i+1]
        sm.add_directed_edge(u, v, 5.0)
        sm.add_directed_edge(v, u, 5.0)
        
    engine = RoutingEngine(sm)
    
    # 2. Test find_shortest_path
    path, cost = engine.find_shortest_path("entrance", "exit")
    assert path == ["entrance", "node_a", "node_b", "exit"]
    assert cost == 15.0
    
    # 3. Test get_optimal_item_sequence
    # Items located near different nodes
    item1 = MockItem("Milk", 9.8, 0.1)     # Near node_b
    item2 = MockItem("Bread", 5.2, -0.1)   # Near node_a
    item3 = MockItem("Apples", 0.1, 0.1)   # Near entrance
    
    items = [item1, item2, item3]
    
    # Shopper starts at entrance (0,0) and ends at exit (15,0)
    optimized_items = engine.get_optimal_item_sequence((0,0), (15,0), items)
    
    assert [i.name for i in optimized_items] == ["Apples", "Bread", "Milk"]

def test_tsp_scaling(empty_store_map):
    # Setup StoreMap
    sm = empty_store_map
    sm.add_node("start", 0.0, 0.0)
    for i in range(1, 21):
        sm.add_node(f"node_{i}", float(i), 0.0)
        sm.add_directed_edge(f"node_{i-1}" if i > 1 else "start", f"node_{i}", 1.0)
        sm.add_directed_edge(f"node_{i}", f"node_{i-1}" if i > 1 else "start", 1.0)
    sm.add_node("exit", 21.0, 0.0)
    sm.add_directed_edge("node_20", "exit", 1.0)
    sm.add_directed_edge("exit", "node_20", 1.0)

    engine = RoutingEngine(sm)

    # Create 20 items
    items = [MockItem(f"Item_{i}", float(i), 0.0) for i in range(1, 21)]

    # This should trigger the Nearest Neighbor fallback and return quickly
    optimized_items = engine.get_optimal_item_sequence((0.0, 0.0), (21.0, 0.0), items)

    assert len(optimized_items) == 20
    # For this linear setup, Nearest Neighbor should return them in order
    assert [i.name for i in optimized_items] == [f"Item_{i}" for i in range(1, 21)]
