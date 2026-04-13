from typing import List, Tuple, Dict, Optional, Iterable
import math

class StoreMap:
    """
    Represents the physical store layout as a Directed Graph.
    Encapsulates node and edge data.
    """
    def __init__(self):
        """
        Initializes an empty directed graph.
        """
        self._nodes: Dict[str, Tuple[float, float]] = {}
        self._edges: Dict[str, List[Dict[str, any]]] = {}

    def add_node(self, node_id: str, x: float, y: float):
        """
        Adds a node to the graph with its real-world (x, y) coordinates.
        """
        self._nodes[node_id] = (x, y)
        if node_id not in self._edges:
            self._edges[node_id] = []

    def add_directed_edge(self, from_node: str, to_node: str, weight: float):
        """
        Adds a directed edge between two existing nodes.
        """
        if from_node in self._nodes and to_node in self._nodes:
            self._edges[from_node].append({"to": to_node, "weight": weight})

    def get_node_coords(self, node_id: str) -> Optional[Tuple[float, float]]:
        """Returns the (x, y) coordinates for a given node ID."""
        return self._nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> List[Dict[str, any]]:
        """Returns the list of edges originating from the given node."""
        return self._edges.get(node_id, [])

    def has_node(self, node_id: str) -> bool:
        """Checks if a node exists in the map."""
        return node_id in self._nodes

    def get_all_node_ids(self) -> Iterable[str]:
        """Returns an iterator over all node IDs."""
        return self._nodes.keys()

    def load_from_store(self, store, resolution: float = 2.0):
        """
        Populates the graph by creating a grid of nodes based on the store dimensions.
        Avoids nodes that fall inside an aisle's bounding box.
        Connects adjacent nodes with edges.
        """
        # 1. Determine boundaries
        max_x = 0.0
        max_y = 0.0
        for aisle in store.aisles:
            max_x = max(max_x, aisle.x_max)
            max_y = max(max_y, aisle.y_max)
        
        # Add a bit of padding
        max_x += 2.0
        max_y += 2.0
        
        # 2. Generate nodes in a grid
        rows = int(max_y / resolution) + 1
        cols = int(max_x / resolution) + 1
        
        grid_nodes = {} # (r, c) -> node_id
        
        for r in range(rows):
            for c in range(cols):
                node_id = f"node_{r}_{c}"
                x, y = c * resolution, r * resolution
                
                # Check if (x, y) is inside any aisle
                is_unwalkable = False
                for aisle in store.aisles:
                    if aisle.x_min <= x <= aisle.x_max and aisle.y_min <= y <= aisle.y_max:
                        is_unwalkable = True
                        break
                
                if not is_unwalkable:
                    self.add_node(node_id, x, y)
                    grid_nodes[(r, c)] = node_id
                
        # 3. Connect nodes (bidirectional edges for simplicity)
        for (r, c), u in grid_nodes.items():
            # Connect to Right, Down, Left, Up
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if (nr, nc) in grid_nodes:
                    v = grid_nodes[(nr, nc)]
                    self.add_directed_edge(u, v, resolution)

    def get_nearest_node(self, x: float, y: float) -> Optional[str]:
        """
        Finds the closest node to the given real-world (x, y) coordinate.
        """
        nearest_node_id = None
        min_distance = float('inf')
        
        for node_id, (node_x, node_y) in self._nodes.items():
            distance = math.sqrt((x - node_x)**2 + (y - node_y)**2)
            if distance < min_distance:
                min_distance = distance
                nearest_node_id = node_id
        
        return nearest_node_id

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return sum(len(e) for e in self._edges.values())

    def __repr__(self):
        return f"<StoreMap(nodes={self.node_count}, edges={self.edge_count})>"
