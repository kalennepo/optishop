# OptiShop Backend

OptiShop is a grocery routing and navigation system designed to help retailers digitize their store layouts and provide shoppers with optimized paths to their items. This backend service manages spatial data, product locations, and Oracle 19c database connectivity using SQLAlchemy and FastAPI.

## Tech Stack

* Language: Python
* Database: Oracle 19c
* ORM: SQLAlchemy
* Driver: oracledb
* API Framework: FastAPI (supported via get_db dependency injection)

## Database Architecture: backend/models

The system uses an Object-Oriented approach to map physical grocery stores into a relational database:
* Store (stores): The root entity representing a retail location.
* Aisle (aisles): Defines the physical "Bounding Box" of shelves using x_min, y_min, x_max, and y_max coordinates for spatial mapping.
* GroceryItem (grocery_items): Individual products assigned to aisles with precise pos_x and pos_y coordinates for the routing algorithm.

## Setup and Configuration
* DatabaseManager(): creates connection pool to Oracle 19c server. Singleton so only one engine is created to connect to DB
### 1. Environment Variables
The DatabaseManager expects a .env file in the project root to securely handle Oracle credentials. Ensure the file contains:

```env
DB_USERNAME=your_oracle_username
DB_PASSWORD=your_oracle_password
