import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db.db_connection import Base
from backend.logic.store_generator import StoreGenerator
from backend.logic.shopping_service import ShoppingService

def test_full_system():
    # 1. Setup in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 2. Generate the Test Store in the DB
        print("--- Step 1: Generating Test Store ---")
        generator = StoreGenerator(db)
        test_store = generator.create_test_store("Grand Finale Store")
        
        # 3. Create a Shopping List (deliberately out of physical order)
        shopping_list = ["Bread", "Apples", "Ice Cream"]
        print(f"--- Step 2: Shopping List: {shopping_list} ---")

        # 4. Use the Master Shopping Service
        service = ShoppingService(db)
        # Assuming Entrance at (0, 0) and Exit at (18, 12)
        entrance = (1.0, 1.0)
        exit_pos = (18.0, 1.0)
        
        print("--- Step 3: Generating Optimized Route ---")
        result = service.generate_route(
            store_id=test_store.id,
            item_names=shopping_list,
            entrance=entrance,
            exit_pos=exit_pos,
            map_resolution=0.5 # 0.5m grid
        )

        if "error" in result:
            print(f"Error: {result['error']}")
            return

        # 5. Output Results
        print("\n--- Route Result ---")
        print(f"Store: {result['store_name']}")
        print(f"Items will be visited in this order: {result['optimized_order']}")
        print(f"Total walking steps: {result['total_steps']}")
        print(f"Estimated walking distance: {result['estimated_distance']} meters")
        
        # 6. Visualize (To see the layout and path)
        print("\n--- Store Map & Route Visualization ---")
        # We need the map object to visualize
        from backend.logic.store_map import StoreMap
        # Use the same parameters as in ShoppingService
        max_x = 20.0
        max_y = 15.0
        store_map = StoreMap(width=max_x, height=max_y, resolution=1.0) # Using 1m resolution for better console view
        store_map.load_from_store(test_store)
        store_map.visualize(path=result['path_coordinates'], items=result['optimized_items'])

        # 7. Basic Validations
        assert result['optimized_order'] == ["Apples", "Bread", "Ice Cream"] # Check if logical (Produce -> Bakery -> Frozen)
        assert len(result['path_coordinates']) > 0
        
        print("\nSUCCESS: The entire system is working from DB to Pathfinding!")

    finally:
        db.close()

if __name__ == "__main__":
    test_full_system()
