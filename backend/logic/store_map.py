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
