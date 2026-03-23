import heapq
from typing import List, Tuple, Dict, Optional
from backend.logic.store_map import StoreMap

class AStarNavigator:
    """
    Implementation of A* pathfinding on the StoreMap grid.
    """
    def __init__(self, store_map: StoreMap):
        self.store_map = store_map

    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Returns walkable neighbors (up, down, left, right)."""
        row, col = pos
        neighbors = []
        # Directions: Up, Down, Left, Right
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if self.store_map.is_in_bounds(nr, nc) and self.store_map.grid[nr][nc]:
                neighbors.append((nr, nc))
        return neighbors

    def find_path(self, start_world: Tuple[float, float], end_world: Tuple[float, float]) -> Optional[List[Tuple[float, float]]]:
        """
        Finds a path from start to end using A*.
        Returns a list of real-world (x, y) coordinates.
        """
        start = self.store_map.world_to_grid(start_world[0], start_world[1])
        end = self.store_map.world_to_grid(end_world[0], end_world[1])

        # If start or end is not walkable, we can't find a path
        if not (self.store_map.is_in_bounds(start[0], start[1]) and self.store_map.grid[start[0]][start[1]]):
            return None
        if not (self.store_map.is_in_bounds(end[0], end[1]) and self.store_map.grid[end[0]][end[1]]):
            return None

        frontier = []
        heapq.heappush(frontier, (0, start))
        
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        cost_so_far: Dict[Tuple[int, int], float] = {start: 0}

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == end:
                break

            for next_pos in self._get_neighbors(current):
                new_cost = cost_so_far[current] + 1  # Assuming uniform cost of 1 per cell
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self._heuristic(end, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        if end not in came_from:
            return None

        # Reconstruct path
        path_grid = []
        curr = end
        while curr is not None:
            path_grid.append(curr)
            curr = came_from[curr]
        path_grid.reverse()

        # Convert back to world coordinates
        return [self.store_map.grid_to_world(r, c) for r, c in path_grid]
