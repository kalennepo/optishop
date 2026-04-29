from typing import List, Tuple
from backend.logic.store_map import StoreMap

class StoreMapBuilder:
    """
    Builder class for constructing a StoreMap graph.
    Responsible for generating nodes and edges based on store dimensions and obstacles,
    keeping the StoreMap pure and decoupled from domain models.
    """
    
    def build(self, width: float, height: float, obstacles: List[Tuple[float, float, float, float]], resolution: float = 2.0) -> StoreMap:
        """
        Builds a StoreMap given dimensions and obstacles.
        
        Args:
            width: Width of the store.
            height: Height of the store.
            obstacles: List of bounding boxes representing un-walkable areas, e.g., aisles.
                       Each obstacle is a tuple: (x_min, y_min, x_max, y_max).
            resolution: The distance between nodes in the grid.
            
        Returns:
            A populated StoreMap graph.
        """
        store_map = StoreMap()
        
        # Add a bit of padding to the dimensions to ensure outer boundaries are reachable
        max_x = width + 2.0
        max_y = height + 2.0
        
        # Generate nodes in a grid
        rows = int(max_y / resolution) + 1
        cols = int(max_x / resolution) + 1
        
        grid_nodes = {} # (r, c) -> node_id
        
        for r in range(rows):
            for c in range(cols):
                node_id = f"node_{r}_{c}"
                x, y = c * resolution, r * resolution
                
                # Check if (x, y) is inside any obstacle
                is_unwalkable = False
                for obs_x_min, obs_y_min, obs_x_max, obs_y_max in obstacles:
                    if obs_x_min <= x <= obs_x_max and obs_y_min <= y <= obs_y_max:
                        is_unwalkable = True
                        break
                
                if not is_unwalkable:
                    store_map.add_node(node_id, x, y)
                    grid_nodes[(r, c)] = node_id
                
        # Connect nodes (bidirectional edges for simplicity)
        for (r, c), u in grid_nodes.items():
            # Connect to Right, Down, Left, Up
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if (nr, nc) in grid_nodes:
                    v = grid_nodes[(nr, nc)]
                    store_map.add_directed_edge(u, v, resolution)
                    
        return store_map
