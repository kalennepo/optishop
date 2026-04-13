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

    def get_optimal_item_sequence(self, entrance_coord: Tuple[float, float], exit_coord: Tuple[float, float], items: list) -> list:
        """
        Solves TSP for best item order.
        """
        if not items:
            return []

        start_node = self.store_map.get_nearest_node(*entrance_coord)
        end_node = self.store_map.get_nearest_node(*exit_coord)
        
        item_nodes = [self.store_map.get_nearest_node(item.pos_x, item.pos_y) for item in items]
            
        all_nodes = [start_node] + item_nodes + [end_node]
        n = len(all_nodes)
        
        dist_matrix = [[float('inf')] * n for _ in range(n)]
        for i in range(n):
            dist_matrix[i][i] = 0.0
            for j in range(n):
                if i == j: continue
                _, cost = self.find_shortest_path(all_nodes[i], all_nodes[j])
                dist_matrix[i][j] = cost

        num_items = len(items)
        dp: Dict[Tuple[int, int], float] = {}

        for i in range(num_items):
            dp[(1 << i, i)] = dist_matrix[0][i + 1]

        for mask_size in range(2, num_items + 1):
            for mask in range(1 << num_items):
                if bin(mask).count('1') != mask_size: continue
                for i in range(num_items):
                    if not (mask & (1 << i)): continue
                    prev_mask = mask ^ (1 << i)
                    res = min((dp[(prev_mask, j)] + dist_matrix[j + 1][i + 1] 
                               for j in range(num_items) if prev_mask & (1 << j)), default=float('inf'))
                    dp[(mask, i)] = res

        full_mask = (1 << num_items) - 1
        min_total_dist = float('inf')
        last_item_idx = -1
        
        for i in range(num_items):
            total = dp[(full_mask, i)] + dist_matrix[i + 1][n - 1]
            if total < min_total_dist:
                min_total_dist = total
                last_item_idx = i

        optimal_item_order = []
        curr_mask = full_mask
        curr_item = last_item_idx
        
        while curr_item != -1:
            optimal_item_order.append(items[curr_item])
            prev_mask = curr_mask ^ (1 << curr_item)
            if prev_mask == 0: break
            
            best_prev_item = -1
            for j in range(num_items):
                if prev_mask & (1 << j):
                    d = dp[(prev_mask, j)] + dist_matrix[j + 1][curr_item + 1]
                    if abs(d - dp[(curr_mask, curr_item)]) < 1e-4:
                        best_prev_item = j
                        break
            curr_mask = prev_mask
            curr_item = best_prev_item

        optimal_item_order.reverse()
        return optimal_item_order
