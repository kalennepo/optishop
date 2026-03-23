import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db.db_connection import Base
from backend.logic.store_editor import StoreEditorService

def test_editor_foundation():
    # 1. Setup in-memory SQLite
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        editor = StoreEditorService(db)

        # 2. Test Store Creation
        print("Testing Store Creation...")
        store = editor.create_store("My Editor Store", width=10.0, height=10.0)
        assert store.name == "My Editor Store"
        assert store.width == 10.0

        # 3. Test Aisle Addition
        print("Testing Aisle Addition...")
        aisle = editor.add_aisle(store.id, "Aisle 1", 2.0, 2.0, 3.0, 8.0)
        assert aisle.name == "Aisle 1"

        # 4. Test Boundary Validation (Failure expected)
        print("Testing Boundary Validation...")
        try:
            editor.add_aisle(store.id, "Invalid Aisle", 8.0, 8.0, 12.0, 12.0)
            assert False, "Should have raised a ValueError"
        except ValueError as e:
            print(f"Correctly caught error: {e}")

        # 5. Test Item Management
        print("Testing Item Addition...")
        item = editor.add_item_to_aisle(aisle.id, "Tomato", 1.5, 5.0)
        assert item.name == "Tomato"

        # 6. Test Layout Fetching
        print("Testing Full Layout Fetch...")
        layout = editor.get_full_layout(store.id)
        assert layout["name"] == "My Editor Store"
        assert len(layout["aisles"]) == 1
        assert layout["aisles"][0]["items"][0]["name"] == "Tomato"

        print("\nSUCCESS: Store Editor Foundation is solid!")

    finally:
        db.close()

if __name__ == "__main__":
    test_editor_foundation()
