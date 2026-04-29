from typing import Tuple, List, Any
import abc

class RouteOptimizationStrategy(abc.ABC):
    """
    Interface for route optimization strategies (e.g., TSP Exact, Nearest Neighbor).
    """
    @abc.abstractmethod
    def optimize(self, engine: Any, entrance_coord: Tuple[float, float], exit_coord: Tuple[float, float], items: List[Any]) -> List[Any]:
        """
        Calculates the optimal ordering of items.
        
        Args:
            engine: The RoutingEngine instance (provides access to pathfinding and the map).
            entrance_coord: Start coordinates.
            exit_coord: End coordinates.
            items: List of items to visit.
            
        Returns:
            The ordered list of items.
        """
        pass
