import math
from typing import List, Tuple, Dict, Optional
from backend.models.grocery_item import GroceryItem
from backend.logic.navigator import AStarNavigator

class RouteOptimizer:
    """
    Solves the Traveling Salesperson Problem (TSP) for a grocery list
    using Bitmask Dynamic Programming (Held-Karp Algorithm).
    """
    def __init__(self, navigator: AStarNavigator):
        self.navigator = navigator

    def get_optimal_route(self, entrance: Tuple[float, float], exit_pos: Tuple[float, float], items: List[GroceryItem]) -> List[GroceryItem]:
        """
        Calculates the best order to visit items.
        :param entrance: (x, y) starting point.
        :param exit_pos: (x, y) ending point (e.g., checkout).
        :param items: List of GroceryItem objects to visit.
        :return: Items in the optimal sequence.
        """
        if not items:
            return []

        # 1. Prepare Waypoints
        # Index 0: Entrance
        # Index 1 to N: Grocery Items
        # Index N+1: Exit
        waypoints = [entrance] + [(item.pos_x, item.pos_y) for item in items] + [exit_pos]
        n = len(waypoints)
        
        # 2. Build Distance Matrix using A*
        # dist_matrix[i][j] is the walking distance between waypoint i and j
        dist_matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                path = self.navigator.find_path(waypoints[i], waypoints[j])
                if path:
                    # distance is number of steps * resolution (simplification)
                    # For more accuracy, we could sum the Euclidean distances between steps
                    d = len(path) * self.navigator.store_map.resolution
                    dist_matrix[i][j] = dist_matrix[j][i] = d
                else:
                    dist_matrix[i][j] = dist_matrix[j][i] = float('inf')

        # 3. Bitmask DP (Held-Karp)
        # We need to visit all items (1 to n-2) starting from index 0.
        # We don't include the Exit (n-1) in the mask because it's the mandatory last stop.
        
        num_items = n - 2 # Excluding Entrance and Exit
        # dp[mask][i] = min distance to visit items in 'mask', ending at item 'i'
        # mask is a bitmask where the j-th bit is 1 if item j is visited.
        # i is the index in the original 'items' list (0 to num_items - 1)
        
        dp = {} # (mask, last_item_idx) -> distance

        # Base case: distance from entrance to each item
        for i in range(num_items):
            dp[(1 << i, i)] = dist_matrix[0][i + 1]

        # Fill DP table
        for mask_size in range(2, num_items + 1):
            for mask in range(1 << num_items):
                if bin(mask).count('1') != mask_size:
                    continue
                
                for i in range(num_items):
                    if not (mask & (1 << i)):
                        continue
                    
                    prev_mask = mask ^ (1 << i)
                    res = float('inf')
                    for j in range(num_items):
                        if prev_mask & (1 << j):
                            res = min(res, dp[(prev_mask, j)] + dist_matrix[j + 1][i + 1])
                    dp[(mask, i)] = res

        # 4. Connect to Exit
        full_mask = (1 << num_items) - 1
        min_total_dist = float('inf')
        last_item_idx = -1
        
        for i in range(num_items):
            total = dp[(full_mask, i)] + dist_matrix[i + 1][n - 1]
            if total < min_total_dist:
                min_total_dist = total
                last_item_idx = i

        # 5. Reconstruct Path
        # Work backwards from the full mask
        optimal_item_order = []
        curr_mask = full_mask
        curr_item = last_item_idx
        
        while curr_item != -1:
            optimal_item_order.append(items[curr_item])
            prev_mask = curr_mask ^ (1 << curr_item)
            if prev_mask == 0:
                break
            
            best_prev_item = -1
            min_dist = float('inf')
            for j in range(num_items):
                if prev_mask & (1 << j):
                    # Check if this transition was the one used in DP
                    # Note: floating point comparison can be tricky, using small epsilon
                    d = dp[(prev_mask, j)] + dist_matrix[j + 1][curr_item + 1]
                    if abs(d - dp[(curr_mask, curr_item)]) < 1e-4:
                        best_prev_item = j
                        break
            
            curr_mask = prev_mask
            curr_item = best_prev_item

        optimal_item_order.reverse()
        return optimal_item_order
