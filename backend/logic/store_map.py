from typing import List, Tuple, Optional, Dict
from backend.models.store import Store
from backend.models.aisle import Aisle
from backend.models.grocery_item import GroceryItem

class StoreMap:
    """
    Represent the physical store layout as a walkable grid.
    Translates real-world coordinates (meters) to grid cells.
    """
    def __init__(self, width: float, height: float, resolution: float = 0.5):
        """
        :param width: Total width of the store in meters.
        :param height: Total height of the store in meters.
        :param resolution: The size of each grid cell in meters (default 0.5m).
        """
        self.width = width
        self.height = height
        self.resolution = resolution
        
        # Calculate number of cells
        self.cols = int(width / resolution)
        self.rows = int(height / resolution)
        
        # Initialize grid: True means walkable, False means blocked
        # Using a 2D list [row][col]
        self.grid = [[True for _ in range(self.cols)] for _ in range(self.rows)]

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Converts real-world (x, y) coordinates to grid indices (row, col)."""
        col = int(x / self.resolution)
        row = int(y / self.resolution)
        return row, col

    def grid_to_world(self, row: int, col: int) -> Tuple[float, float]:
        """Converts grid indices (row, col) to real-world (x, y) coordinates (center of cell)."""
        x = (col + 0.5) * self.resolution
        y = (row + 0.5) * self.resolution
        return x, y

    def is_in_bounds(self, row: int, col: int) -> bool:
        """Checks if a grid cell is within the map boundaries."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def set_walkable(self, x_min: float, y_min: float, x_max: float, y_max: float, walkable: bool):
        """Sets a rectangular area as walkable or blocked."""
        start_row, start_col = self.world_to_grid(x_min, y_min)
        end_row, end_col = self.world_to_grid(x_max, y_max)
        
        for r in range(max(0, start_row), min(self.rows, end_row + 1)):
            for c in range(max(0, start_col), min(self.cols, end_col + 1)):
                if self.is_in_bounds(r, c):
                    self.grid[r][c] = walkable

    def load_from_store(self, store: Store):
        """
        Populates the grid based on the aisles defined in a Store object.
        Everything is walkable by default; aisles mark areas as blocked.
        """
        # Reset grid
        self.grid = [[True for _ in range(self.cols)] for _ in range(self.rows)]
        
        for aisle in store.aisles:
            # We assume aisles are obstacles
            self.set_walkable(aisle.x_min, aisle.y_min, aisle.x_max, aisle.y_max, False)

    def is_walkable(self, x: float, y: float) -> bool:
        """Checks if a real-world coordinate is walkable."""
        row, col = self.world_to_grid(x, y)
        if self.is_in_bounds(row, col):
            return self.grid[row][col]
        return False

    def get_item_grid_pos(self, item: GroceryItem) -> Tuple[int, int]:
        """Returns the grid (row, col) for a grocery item."""
        return self.world_to_grid(item.pos_x, item.pos_y)

    def visualize(self, path: Optional[List[Tuple[float, float]]] = None, items: Optional[List[GroceryItem]] = None):
        """Prints an ASCII representation of the map, optional path, and items."""
        path_grid_coords = set()
        if path:
            path_grid_coords = {self.world_to_grid(x, y) for x, y in path}
            
        item_grid_map = {}
        if items:
            for idx, item in enumerate(items):
                # Use 1-based index as a symbol
                symbol = str(idx + 1)[-1] 
                pos = self.get_item_grid_pos(item)
                item_grid_map[pos] = symbol

        print(f"Map Visualization ({self.rows}x{self.cols})")
        print("Legend: . = Walkable, # = Aisle, @ = Path, 1-N = Items in Order")
        
        for r in range(self.rows):
            row_str = ""
            for c in range(self.cols):
                if (r, c) in item_grid_map:
                    row_str += f"{item_grid_map[(r, c)]} "
                elif (r, c) in path_grid_coords:
                    row_str += "@ "
                elif not self.grid[r][c]:
                    row_str += "# "
                else:
                    row_str += ". "
            print(row_str)

    def __repr__(self):
        return f"<StoreMap(rows={self.rows}, cols={self.cols}, resolution={self.resolution}m)>"
