# OPTISHOP AST REPO MAP
SYSTEM INSTRUCTIONS:
1. LOGIC OMITTED: Functions are NOT empty. Implementations are abstracted for context efficiency.
2. READ/WRITE PROTOCOL: To modify a function, you MUST ask the user to provide the specific file path first. Do NOT hallucinate modifications without the source file.
3. ARCHITECTURAL GROUNDING: OptiShop acts as an "Indoor GPS" for grocery stores. It uses SQLAlchemy/Oracle 19c for the data layer, and A* Pathfinding + TSP (Traveling Salesperson) for the routing engine.
4. SCOPE BOUNDARIES: OptiShop DOES NOT track real-time inventory, handle financial transactions, or provide outdoor GPS directions.
5. PRECISION: Use exact class, function, and file names from this map.

---

```python

# generate_repo_map.py
def format_function(node, indent): # Helper to format a function signature, return type, and brief docstring.
def parse_file(filepath): # Parses a Python file and returns its AST skeleton.
def generate_map(root_dir): # Walks the directory and builds the repo map.

# backend/api/routers/route_router.py
def optimize_route(request, db): # Handles the Indoor GPS algorithm by coordinating with ShoppingService.

# backend/api/routers/store_router.py
def create_store(store_in, db):
def get_store_layout(store_id, db):
def add_aisle(store_id, aisle_in, db):
def add_item_to_aisle(aisle_id, item_in, db):

# backend/db/db_connection.py
class DatabaseManager: # An Object-Oriented manager for handling the Oracle 19c database connection.
    def __init__(self):
    def _create_engine(self): # Private method to construct the URL and return the engine.
    def get_db(self): # Yields a database session. Used for FastAPI dependency injection.
    def test_connection(self): # Tests the connection to the ISU Oracle database.

# backend/logic/routing_engine.py
class RoutingEngine: # Combines pathfinding (A*) and route optimization (TSP) for the graph-based StoreMap.
    def __init__(self, store_map):
    def _heuristic(self, node_a, node_b) -> float: # Calculates Euclidean distance between two nodes via StoreMap encapsulation.
    def find_shortest_path(self, start_node_id, end_node_id) -> Tuple[List[str], float]: # Finds the shortest path between two nodes using A*.
    def get_optimal_item_sequence(self, entrance_coord, exit_coord, items) -> list: # Solves TSP for best item order. Falls back to Nearest Neighbor for > 15 items.

# backend/logic/shopping_service.py
class ShoppingService: # The Master Service that coordinates the entire shopping route generation.
    def __init__(self, db):
    def generate_route(self, store_id, item_names, entrance, exit_pos) -> Dict: # Generates a complete, optimized shopping path.

# backend/logic/store_editor.py
class StoreEditorService: # Backend foundation for the Store Layout Editor.
    def __init__(self, db):
    def create_store(self, name, width, height) -> Store:
    def get_store(self, store_id) -> Optional[Store]:
    def add_aisle(self, store_id, name, x_min, y_min, x_max, y_max) -> Optional[Aisle]: # Adds an aisle and validates that it is within the store's boundaries and doesn't overlap.
    def update_aisle(self, aisle_id) -> Optional[Aisle]: # Update aisle properties like name or dimensions.
    def delete_aisle(self, aisle_id) -> bool:
    def add_item_to_aisle(self, aisle_id, name, pos_x, pos_y) -> Optional[GroceryItem]: # Adds a grocery item to an aisle.
    def move_item(self, item_id, new_x, new_y, new_aisle_id) -> Optional[GroceryItem]:
    def delete_item(self, item_id) -> bool:
    def get_full_layout(self, store_id) -> Dict: # Returns a nested dictionary of the store's entire layout for the frontend editor.

# backend/logic/store_generator.py
class StoreGenerator: # Utility to generate a standardized 'Test Store' layout programmatically.
    def __init__(self, db_session):
    def create_test_store(self, name):

# backend/logic/store_map.py
class StoreMap: # Represents the physical store layout as a Directed Graph.
    def __init__(self): # Initializes an empty directed graph.
    def add_node(self, node_id, x, y): # Adds a node to the graph with its real-world (x, y) coordinates.
    def add_directed_edge(self, from_node, to_node, weight): # Adds a directed edge between two existing nodes.
    def get_node_coords(self, node_id) -> Optional[Tuple[float, float]]: # Returns the (x, y) coordinates for a given node ID.
    def get_neighbors(self, node_id) -> List[Dict[str, any]]: # Returns the list of edges originating from the given node.
    def has_node(self, node_id) -> bool: # Checks if a node exists in the map.
    def get_all_node_ids(self) -> Iterable[str]: # Returns an iterator over all node IDs.
    def load_from_store(self, store, resolution): # Populates the graph by creating a grid of nodes based on the store dimensions.
    def get_nearest_node(self, x, y) -> Optional[str]: # Finds the closest node to the given real-world (x, y) coordinate.
    def node_count(self) -> int:
    def edge_count(self) -> int:
    def __repr__(self):

# backend/models/aisle.py
class Aisle:

# backend/models/grocery_item.py
class GroceryItem:

# backend/models/store.py
class Store:
    def __repr__(self):

# backend/schemas/api_schemas.py
class GroceryItemBase:
class GroceryItemCreate:
class GroceryItemSchema:
class AisleBase:
class AisleCreate:
class AisleSchema:
class StoreBase:
class StoreCreate:
class StoreSchema:
class LayoutItemSchema:
class LayoutAisleSchema:
class StoreLayoutResponse:
class RouteRequest:
class RouteResponse:

# tests/conftest.py
def db_session(): # Provides an in-memory SQLite SQLAlchemy session.
def empty_store_map(): # Provides a fresh StoreMap instance.

# tests/test_grand_finale.py
def test_full_system_graph(db_session):

# tests/test_routing_engine.py
class MockItem:
    def __init__(self, name, pos_x, pos_y):
def test_routing_engine(empty_store_map):
def test_tsp_scaling(empty_store_map):

# tests/test_store_editor.py
def test_editor_foundation(db_session):

# tests/test_store_map.py
def test_store_map_graph(empty_store_map):
def test_load_from_store_with_aisles(empty_store_map):
```
