# OptiShop: The Indoor GPS for Grocery Stores

OptiShop is a high-performance "Indoor GPS" backend designed for high-density grocery stores. It digitizes physical store layouts into a 2D navigation grid, allowing users to input their grocery lists and receive the most efficient walking path through the store. By combining spatial modeling with advanced pathfinding and optimization algorithms, OptiShop reduces shopper frustration and maximizes efficiency in complex retail environments.

## Project Overview

OptiShop transforms a physical retail space into a navigable digital map. It calculates optimal routes by considering the exact (x, y) coordinates of every item on a shopper's list, ensuring they never double-back or miss an aisle.

## Tech Stack

*   **Language:** Python 3.12+ (Object-Oriented Architecture)
*   **Database:** Oracle 19c (Primary Data Store)
*   **ORM:** SQLAlchemy 2.0 (Relational Mapping & Repository Pattern)
*   **API Framework:** FastAPI (Asynchronous Service Layer)
*   **Security:** JSON Web Tokens (JWT), passlib (bcrypt) for password hashing
*   **Testing:** Pytest (Full Suite with In-Memory SQLite Fixtures)

---

## Core Architecture

The system is built on a modular, layered architecture emphasizing separation of concerns, the Open/Closed Principle (OCP), and strong encapsulation to ensure scalability and maintainability.

### 1. Data & Repository Layer
The physical store is modeled using a hierarchical relational structure:
*   **User:** Represents system users with Role-Based Access Control (RBAC), differentiating between standard "shoppers" and "store_owners".
*   **Store:** The root entity defining the physical dimensions (width/height) of the retail space.
*   **Aisle:** Represents physical shelving units using **Bounding Boxes** (`x_min`, `y_min`, `x_max`, `y_max`). 
*   **GroceryItem:** Individual products mapped to specific coordinates within their assigned aisles.
*   **Repositories:** Dedicated classes (`StoreRepository`, `UserRepository`, `AisleRepository`, `ItemRepository`) abstract all direct SQLAlchemy operations, keeping the business logic purely focused on domain rules.

### 2. Map Generation (`StoreMap` & `StoreMapBuilder`)
The physical layout is dynamically translated into a pure mathematical graph.
*   **StoreMap:** A decoupled data structure managing raw graph nodes and directed edges, completely ignorant of database models.
*   **StoreMapBuilder:** A builder factory that ingests physical store dimensions and obstacle bounding boxes to construct the `StoreMap`, mapping walkable spaces and carving out unwalkable shelving zones.

### 3. Routing Engine (`RoutingEngine` & Strategies)
OptiShop utilizes the **Strategy Pattern** for dynamic algorithm selection based on the shopping list complexity:
*   **A* Pathfinding:** Resolves precise point-to-point navigation between items, utilizing a Euclidean distance heuristic.
*   **TSPExactStrategy:** Uses Dynamic Programming (Bitmasking) to solve the Traveling Salesperson Problem optimally for lists ≤ 15 items ($O(2^n \cdot n^2)$).
*   **NearestNeighborStrategy:** A fast heuristic fallback for lists > 15 items to ensure instant response times for extensive shopping trips.

### 4. Service Layer (Facades)
*   **ShoppingService:** Orchestrates map construction and algorithm execution behind a clean facade. API consumers interact only with this service to receive optimized routes, remaining completely abstracted from internal graph calculations.
*   **StoreEditorService:** Manages complete CRUD operations for the store layout, executing complex geometrical validation to actively prevent overlapping aisles and ensure items fit within store bounds.

### 5. RESTful API & Security (FastAPI)
OptiShop exposes its logic through a secure, high-performance RESTful API:
*   **Auth Router (`/api/v1/auth`):** Handles user registration and JWT-based authentication.
*   **Store Router (`/api/v1/stores`):** Provides complete CRUD endpoints for stores, aisles, and items. State-modifying endpoints are strictly guarded by **Role-Based Access Control**, requiring specific `store_owner` privileges. Includes bulk Map Import/Export functionality and Inventory reporting (`out-of-stock` flagging).
*   **Route Router (`/api/v1/route`):** Authenticated endpoint for pathfinding. Accepts a list of grocery items and returns a seamlessly optimized, sequenced walking path.
*   **Cart Router (`/api/v1/carts`):** Allows shoppers to compile active shopping carts and permanently save their favorite cart permutations.

---

## The GEMINI.md (AST Repo Map)

This repository includes a specialized `GEMINI.md` file, which serves as an **Abstract Syntax Tree (AST) Repo Map**. 

### What is an AST Repo Map?
Unlike a standard file tree, the AST Repo Map provides a structural "skeleton" of the entire project's logic. It uses the abstract syntax of the Python files to present:
*   **Class Hierarchies:** Clear visibility into how models and services interact.
*   **Method Signatures:** Function names, parameters, and return types (e.g., `find_shortest_path(...) -> Tuple[List[str], float]`).
*   **Docstring Summaries:** High-level explanations of every component's responsibility.

### Why it exists:
This map is designed for **Architectural Grounding**. It allows developers and AI agents to maintain a perfect "mental model" of the system's dependencies and spatial logic without the overhead of reading thousands of lines of implementation code.

---

## Setup & Installation

### 1. Prerequisites
Ensure you have a Python 3.12+ environment and access to an Oracle 19c instance (or modify the `DatabaseManager` to use SQLite/PostgreSQL locally).

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-repo/optishop.git
cd optishop

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the project root to securely handle your Oracle credentials and JWT secret:
```env
DB_USERNAME=your_oracle_username
DB_PASSWORD=your_oracle_password
SECRET_KEY=your_secure_jwt_secret_key
```

### 4. Running the API Server
Start the development server using **Uvicorn**:
```bash
# Run the FastAPI server
python -m backend.main
```
The API will be accessible at `http://localhost:8000`. You can access the interactive Swagger documentation at `http://localhost:8000/docs`.

---

## Testing Suite

OptiShop maintains a rigorous testing standard using **Pytest**, featuring a comprehensive suite of 44 tests covering all core backend logic without modifying the domain models. To ensure speed and isolation, the testing suite utilizes a `conftest.py` configuration with a shared `StaticPool` and reusable fixtures.

### Comprehensive Coverage Areas:
*   **Security & Dependencies:** Exhaustive validation of JWT token generation, expiration handling, password hashing (`bcrypt`), and RBAC dependency injection (`require_store_owner`).
*   **Algorithm Basis Paths:** Isolated, mocked unit testing for the `TSPExactStrategy` and `NearestNeighborStrategy` ensuring every logical branch, including edge cases (0 items, 1 item, identical coordinates), executes flawlessly.
*   **Integration Routers:** End-to-end API testing using FastAPI's `TestClient`. Verifies complete HTTP request/response cycles, domain validation rules (e.g., overlapping aisles), and proper 400/401/403/404 error handling for Auth, Store, Cart, and Route endpoints.

### Key Testing Features:
*   **In-Memory SQLite:** Every test run uses a fast, ephemeral SQLite database in RAM (`check_same_thread=False` with a `StaticPool`) ensuring isolated but state-persistent execution during client requests.
*   **Fixture Injection:** Reusable `db_session`, `client`, and authentication header fixtures streamline test setup and teardown.
*   **Dependency Override:** FastAPI's `dependency_overrides` feature is used to seamlessly inject the test database session into the API endpoints.

### Running Tests:
```bash
# Run the full suite
pytest tests/

# Run tests with verbose output
pytest -v tests/
```
