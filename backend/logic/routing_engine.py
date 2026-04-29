import heapq
import math
from typing import List, Tuple, Dict, Optional

class RoutingEngine:
    """
    Combines pathfinding (A*) and route optimization (TSP) for the graph-based StoreMap.
    Utilizes composition by holding a reference to a StoreMap instance.
    """
    def __init__(self, store_map):
        self.store_map = store_map

    def _heuristic(self, node_a: str, node_b: str) -> float:
        """Calculates Euclidean distance between two nodes via StoreMap encapsulation."""
        coords_a = self.store_map.get_node_coords(node_a)
        coords_b = self.store_map.get_node_coords(node_b)
        
        if not coords_a or not coords_b:
            return float('inf')
            
        x1, y1 = coords_a
        x2, y2 = coords_b
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def find_shortest_path(self, start_node_id: str, end_node_id: str) -> Tuple[List[str], float]:
        """
        Finds the shortest path between two nodes using A*.
        :return: (list of node_id strings, total distance cost)
        """
        if not self.store_map.has_node(start_node_id) or not self.store_map.has_node(end_node_id):
            return [], float('inf')

        frontier = []
        heapq.heappush(frontier, (0.0, start_node_id))
        
        came_from: Dict[str, Optional[str]] = {start_node_id: None}
        cost_so_far: Dict[str, float] = {start_node_id: 0.0}

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == end_node_id:
                break

            for edge in self.store_map.get_neighbors(current):
                next_node = edge["to"]
                new_cost = cost_so_far[current] + edge["weight"]
                
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self._heuristic(next_node, end_node_id)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current

        if end_node_id not in came_from:
            return [], float('inf')

        path = []
        curr = end_node_id
        while curr is not None:
            path.append(curr)
            curr = came_from[curr]
        path.reverse()
        
        return path, cost_so_far[end_node_id]

    def get_optimal_item_sequence(self, entrance_coord: Tuple[float, float], exit_coord: Tuple[float, float], items: list, strategy: Optional['RouteOptimizationStrategy'] = None) -> list:
        """
        Solves TSP for best item order. Dynamically selects strategy if none is provided.
        """
        if not items:
            return []
            
        if strategy is None:
            if len(items) <= 15:
                from backend.logic.strategies.tsp_exact import TSPExactStrategy
                strategy = TSPExactStrategy()
            else:
                from backend.logic.strategies.nearest_neighbor import NearestNeighborStrategy
                strategy = NearestNeighborStrategy()
                
        return strategy.optimize(self, entrance_coord, exit_coord, items)
