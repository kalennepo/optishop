import sys
import os
import pytest

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.logic.store_editor import StoreEditorService
from backend.repositories.store import StoreRepository
from backend.repositories.aisle import AisleRepository
from backend.repositories.item import ItemRepository

def test_editor_foundation(db_session):
    # 1. Use db_session fixture
    db = db_session
    editor = StoreEditorService(
        store_repo=StoreRepository(db),
        aisle_repo=AisleRepository(db),
        item_repo=ItemRepository(db)
    )

    # 2. Test Store Creation
    store = editor.create_store("My Editor Store", width=10.0, height=10.0)
    assert store.name == "My Editor Store"
    assert store.width == 10.0

    # 3. Test Aisle Addition
    aisle = editor.add_aisle(store.id, "Aisle 1", 2.0, 2.0, 3.0, 8.0)
    assert aisle.name == "Aisle 1"

    # 4. Test Boundary Validation (Failure expected)
    with pytest.raises(ValueError) as excinfo:
        editor.add_aisle(store.id, "Invalid Aisle", 8.0, 8.0, 12.0, 12.0)
    assert "boundaries" in str(excinfo.value).lower()

    # 4.5. Test Overlap Validation (Failure expected)
    # Aisle 1 is at (2.0, 2.0) to (3.0, 8.0)
    # Attempt to add Aisle 2 that overlaps with Aisle 1
    with pytest.raises(ValueError) as excinfo:
        editor.add_aisle(store.id, "Overlapping Aisle", 2.5, 5.0, 4.0, 9.0)
    assert "overlap" in str(excinfo.value).lower()
    
    # Attempt to add Aisle 3 that does NOT overlap
    aisle3 = editor.add_aisle(store.id, "Aisle 3", 5.0, 2.0, 6.0, 8.0)
    assert aisle3.name == "Aisle 3"

    # 5. Test Item Management
    item = editor.add_item_to_aisle(aisle.id, "Tomato", 1.5, 5.0)
    assert item.name == "Tomato"

    # 6. Test Layout Fetching
    layout = editor.get_full_layout(store.id)
    assert layout["name"] == "My Editor Store"
    assert len(layout["aisles"]) == 2
    assert layout["aisles"][0]["items"][0]["name"] == "Tomato"

    # 7. Test Updating Aisle
    updated_aisle = editor.update_aisle(aisle.id, name="Produce Aisle")
    assert updated_aisle.name == "Produce Aisle"
    
    # 8. Test Invalid Update (overlap)
    with pytest.raises(ValueError) as excinfo:
        editor.update_aisle(aisle3.id, x_min=2.0, y_min=2.0, x_max=3.0, y_max=8.0) # overlaps with aisle 1
    assert "overlap" in str(excinfo.value).lower()
    
    # 9. Test Updating Item
    updated_item = editor.update_item(item.id, name="Cherry Tomato", pos_y=6.0)
    assert updated_item.name == "Cherry Tomato"
    assert updated_item.pos_y == 6.0

    # 10. Test Deletions
    assert editor.delete_item(item.id) is True
    assert editor.delete_aisle(aisle3.id) is True
    layout = editor.get_full_layout(store.id)
    assert len(layout["aisles"]) == 1 # Only one aisle left
    assert len(layout["aisles"][0]["items"]) == 0 # No items left
