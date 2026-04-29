from typing import Tuple, List, Any, Dict
from backend.logic.strategies.base import RouteOptimizationStrategy

class TSPExactStrategy(RouteOptimizationStrategy):
    """
    Solves TSP for best item order using DP with Bitmask.
    Guarantees the shortest path but scales poorly with many items.
    """
    def optimize(self, engine: Any, entrance_coord: Tuple[float, float], exit_coord: Tuple[float, float], items: List[Any]) -> List[Any]:
        if not items:
            return []

        start_node = engine.store_map.get_nearest_node(*entrance_coord)
        end_node = engine.store_map.get_nearest_node(*exit_coord)
        
        item_nodes = [engine.store_map.get_nearest_node(item.pos_x, item.pos_y) for item in items]
            
        all_nodes = [start_node] + item_nodes + [end_node]
        n = len(all_nodes)
        
        # Calculate distance matrix using A*
        dist_matrix = [[float('inf')] * n for _ in range(n)]
        for i in range(n):
            dist_matrix[i][i] = 0.0
            for j in range(n):
                if i == j: continue
                _, cost = engine.find_shortest_path(all_nodes[i], all_nodes[j])
                dist_matrix[i][j] = cost

        num_items = len(items)
        dp: Dict[Tuple[int, int], float] = {}

        # Initialize base cases (from entrance to each item)
        for i in range(num_items):
            dp[(1 << i, i)] = dist_matrix[0][i + 1]

        # Fill DP table
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
        
        # Find best last item before heading to exit
        for i in range(num_items):
            total = dp[(full_mask, i)] + dist_matrix[i + 1][n - 1]
            if total < min_total_dist:
                min_total_dist = total
                last_item_idx = i

        # Backtrack to reconstruct the path
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
