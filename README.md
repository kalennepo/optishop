# OptiShop: The Indoor GPS for Grocery Stores

OptiShop is a high-performance "Indoor GPS" backend designed for high-density grocery stores. It digitizes physical store layouts into a 2D navigation grid, allowing users to input their grocery lists and receive the most efficient walking path through the store. By combining spatial modeling with advanced pathfinding and optimization algorithms, OptiShop reduces shopper frustration and maximizes efficiency in complex retail environments.

## Project Overview

OptiShop transforms a physical retail space into a navigable digital map. It calculates optimal routes by considering the exact (x, y) coordinates of every item on a shopper's list, ensuring they never double-back or miss an aisle.

###Scope & Boundaries
To maintain a focused and high-integrity routing engine, OptiShop adheres to the following boundaries:
*   **Indoor Focus:** Designed specifically for interior retail layouts; does not provide outdoor GPS or parking lot directions.
*   **Static Mapping:** Focuses on spatial navigation and layout optimization. It does **not** track real-time inventory levels or stock-outs.
*   **Pure Navigation:** Operates as a routing utility; it does **not** facilitate financial transactions, payments, or digital coupons.

---

## Tech Stack

*   **Language:** Python 3.12+ (Object-Oriented Architecture)
*   **Database:** Oracle 19c (Primary Data Store)
*   **ORM:** SQLAlchemy 2.0 (Relational Mapping & Session Management)
*   **API Framework:** FastAPI (Asynchronous Service Layer)
*   **Testing:** Pytest (Full Suite with In-Memory SQLite Fixtures)

---

##Core Architecture

The system is built on a modular, layered architecture to ensure scalability and maintainability.

### 1. Data Layer (Domain Models)
The physical store is modeled using a hierarchical relational structure:
*   **Store:** The root entity defining the physical dimensions (width/height) of the retail space.
*   **Aisle:** Represents physical shelving units using **Bounding Boxes** (`x_min`, `y_min`, `x_max`, `y_max`). This allows the system to distinguish between walkable floor space and unwalkable obstacles.
*   **GroceryItem:** Individual products mapped to specific coordinates within their assigned aisles.

### 2. Map Generation (`StoreMap`)
The `StoreMap` service dynamically generates a directed graph representing the store's walkable area. 
*   **Collision Detection:** During grid generation, the system performs real-time bounding-box checks against all `Aisle` objects. 
*   **Unwalkable Zones:** Any grid node falling within an aisle's boundary is automatically pruned, preventing the routing engine from calculating paths that "walk through" solid shelves.

### 3. Routing Engine (`RoutingEngine`)
OptiShop utilizes a dual-algorithm approach to solve the complex "Grocery Trip" problem:
*   **A* Pathfinding:** Used for point-to-point navigation between items, utilizing a Euclidean distance heuristic for maximum efficiency.
*   **Traveling Salesperson (TSP) Optimization:** Used to determine the best *order* in which to visit items on a list.
    *   **Lists ≤ 15 Items:** Uses an exact **Dynamic Programming (Bitmasking)** approach ($O(2^n \cdot n^2)$) for mathematically perfect routes.
    *   **Lists > 15 Items:** Automatically falls back to a high-speed **Nearest Neighbor Heuristic** to ensure instant response times for large shopping trips.

### 4. Service Layer
*   **ShoppingService:** The master controller that orchestrates the entire lifecycle from inputting a list to returning a complete, optimized path.
*   **StoreEditorService:** Provides backend validation for store managers, ensuring aisles do not overlap and items are placed within valid boundaries.

### 5. RESTful API Layer (FastAPI)
OptiShop exposes its core logic through a high-performance RESTful API, organized into versioned routers:
*   **Store Router (`/api/v1/stores`):** Manages store creation, layout retrieval, and the addition of aisles and items.
*   **Route Router (`/api/v1/route`):** The primary endpoint for pathfinding. Accepts a list of grocery items and returns an optimized, sequenced walking path.
*   **Interactive Documentation:** The API includes built-in **Swagger UI** (`/docs`) and **ReDoc** (`/redoc`) for real-time endpoint testing and schema exploration.

---

## The GEMINI.md (AST Repo Map)

This repository includes a specialized `GEMINI.md` file, which serves as an **Abstract Syntax Tree (AST) Repo Map**. 

### What is an AST Repo Map?
Unlike a standard file tree, the AST Repo Map provides a structural "skeleton" of the entire project's logic. It uses the abstract syntax of the Python files to present:
*   **Class Hierarchies:** Clear visibility into how `Store`, `Aisle`, and `GroceryItem` relate.
*   **Method Signatures:** Function names, parameters, and return types (e.g., `find_shortest_path(...) -> Tuple[List[str], float]`).
*   **Docstring Summaries:** High-level explanations of every component's responsibility.

### Why it exists:
This map is designed for **Architectural Grounding**. It allows developers and AI agents to maintain a perfect "mental model" of the system's dependencies and spatial logic without the overhead of reading thousands of lines of implementation code. It ensures that every change—from a bug fix to a new feature—is aligned with OptiShop's core design principles.

---

## Setup & Installation

### 1. Prerequisites
Ensure you have a Python 3.12+ environment and access to an Oracle 19c instance.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-repo/optishop.git
cd optishop

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the project root to securely handle your Oracle credentials:
```env
DB_USERNAME=your_oracle_username
DB_PASSWORD=your_oracle_password
```

### 4. Running the API Server
Start the development server using **Uvicorn**:
```bash
# Run the FastAPI server
python -m backend.main
```
The API will be accessible at `http://localhost:8000`. You can access the interactive documentation at `http://localhost:8000/docs`.

---

## Testing Suite

OptiShop maintains a rigorous testing standard using **Pytest**. To ensure speed and isolation, the testing suite utilizes a `conftest.py` configuration with reusable fixtures.

### Key Testing Features:
*   **In-Memory SQLite:** Every test run creates a fresh, ephemeral SQLite database in RAM, ensuring no data leakage between tests.
*   **Fixture Injection:** Reusable `db_session` and `empty_store_map` fixtures streamline test setup and teardown.
*   **Coverage:** Tests cover everything from basic graph connectivity to complex TSP scaling and aisle collision detection.

### Running Tests:
```bash
# Run the full suite
pytest tests/

# Run tests with verbose output
pytest -v tests/
```
