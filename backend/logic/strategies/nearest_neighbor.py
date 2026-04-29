from typing import Tuple, List, Any
from backend.logic.strategies.base import RouteOptimizationStrategy

class NearestNeighborStrategy(RouteOptimizationStrategy):
    """
    A heuristic approach to solving the routing problem using Nearest Neighbor.
    Very fast, scales well, but does not guarantee the absolute shortest route.
    """
    def optimize(self, engine: Any, entrance_coord: Tuple[float, float], exit_coord: Tuple[float, float], items: List[Any]) -> List[Any]:
        if not items:
            return []

        current_node = engine.store_map.get_nearest_node(*entrance_coord)
        unvisited_items = list(items)
        optimal_item_order = []
        
        while unvisited_items:
            best_item = None
            min_dist = float('inf')
            best_item_node = None
            
            for item in unvisited_items:
                item_node = engine.store_map.get_nearest_node(item.pos_x, item.pos_y)
                _, cost = engine.find_shortest_path(current_node, item_node)
                if cost < min_dist:
                    min_dist = cost
                    best_item = item
                    best_item_node = item_node
            
            optimal_item_order.append(best_item)
            current_node = best_item_node
            unvisited_items.remove(best_item)
            
        return optimal_item_order
