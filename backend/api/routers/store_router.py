from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.db.db_connection import db_manager
from backend.logic.store_editor import StoreEditorService
from backend.schemas.api_schemas import (
    StoreCreate, StoreSchema, StoreLayoutResponse, 
    AisleCreate, AisleUpdate, AisleSchema, GroceryItemCreate, GroceryItemUpdate, GroceryItemSchema,
    StoreImportRequest
)
from backend.repositories.store import StoreRepository
from backend.repositories.aisle import AisleRepository
from backend.repositories.item import ItemRepository
from backend.api.dependencies import require_store_owner, get_current_user
from backend.models.user import User

router = APIRouter(
    prefix="/stores",
    tags=["stores"]
)

def get_store_editor_service(db: Session) -> StoreEditorService:
    return StoreEditorService(
        store_repo=StoreRepository(db),
        aisle_repo=AisleRepository(db),
        item_repo=ItemRepository(db)
    )

@router.post("/", response_model=StoreSchema)
def create_store(store_in: StoreCreate, db: Session = Depends(db_manager.get_db)):
    service = get_store_editor_service(db)
    return service.create_store(name=store_in.name, width=store_in.width, height=store_in.height)

@router.get("/{store_id}/layout", response_model=StoreLayoutResponse)
def get_store_layout(store_id: int, db: Session = Depends(db_manager.get_db)):
    service = get_store_editor_service(db)
    layout = service.get_full_layout(store_id)
    if not layout:
        raise HTTPException(status_code=404, detail="Store not found")
    return layout

@router.post("/{store_id}/aisles", response_model=AisleSchema)
def add_aisle(store_id: int, aisle_in: AisleCreate, db: Session = Depends(db_manager.get_db)):
    service = get_store_editor_service(db)
    try:
        aisle = service.add_aisle(
            store_id=store_id,
            name=aisle_in.name,
            x_min=aisle_in.x_min,
            y_min=aisle_in.y_min,
            x_max=aisle_in.x_max,
            y_max=aisle_in.y_max
        )
        if not aisle:
            raise HTTPException(status_code=404, detail="Store not found")
        return aisle
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/aisles/{aisle_id}/items", response_model=GroceryItemSchema)
def add_item_to_aisle(aisle_id: int, item_in: GroceryItemCreate, db: Session = Depends(db_manager.get_db), current_user: User = Depends(require_store_owner)):
    service = get_store_editor_service(db)
    item = service.add_item_to_aisle(
        aisle_id=aisle_id,
        name=item_in.name,
        pos_x=item_in.pos_x,
        pos_y=item_in.pos_y
    )
    if not item:
        raise HTTPException(status_code=404, detail="Aisle not found")
    return item

@router.put("/aisles/{aisle_id}", response_model=AisleSchema)
def update_aisle(aisle_id: int, aisle_in: AisleUpdate, db: Session = Depends(db_manager.get_db), current_user: User = Depends(require_store_owner)):
    service = get_store_editor_service(db)
    try:
        aisle = service.update_aisle(
            aisle_id=aisle_id,
            **aisle_in.model_dump(exclude_unset=True)
        )
        if not aisle:
            raise HTTPException(status_code=404, detail="Aisle not found")
        return aisle
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/aisles/{aisle_id}", status_code=204)
def delete_aisle(aisle_id: int, db: Session = Depends(db_manager.get_db), current_user: User = Depends(require_store_owner)):
    service = get_store_editor_service(db)
    if not service.delete_aisle(aisle_id):
        raise HTTPException(status_code=404, detail="Aisle not found")

@router.put("/items/{item_id}", response_model=GroceryItemSchema)
def update_item(item_id: int, item_in: GroceryItemUpdate, db: Session = Depends(db_manager.get_db), current_user: User = Depends(require_store_owner)):
    service = get_store_editor_service(db)
    item = service.update_item(
        item_id=item_id,
        **item_in.model_dump(exclude_unset=True)
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(db_manager.get_db), current_user: User = Depends(require_store_owner)):
    service = get_store_editor_service(db)
    if not service.delete_item(item_id):
        raise HTTPException(status_code=404, detail="Item not found")

@router.post("/items/{item_id}/report-out-of-stock", response_model=GroceryItemSchema)
def report_item_out_of_stock(item_id: int, db: Session = Depends(db_manager.get_db), current_user: User = Depends(get_current_user)):
    service = get_store_editor_service(db)
    item = service.update_item(item_id, in_stock=False)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.get("/{store_id}/reports/out-of-stock", response_model=List[GroceryItemSchema])
def get_out_of_stock_report(store_id: int, db: Session = Depends(db_manager.get_db), current_user: User = Depends(require_store_owner)):
    service = get_store_editor_service(db)
    store = service.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    out_of_stock_items = []
    for aisle in store.aisles:
        for item in aisle.items:
            if not item.in_stock:
                out_of_stock_items.append(item)
    return out_of_stock_items

@router.get("/{store_id}/export", response_model=StoreLayoutResponse)
def export_store_layout(store_id: int, db: Session = Depends(db_manager.get_db), current_user: User = Depends(require_store_owner)):
    service = get_store_editor_service(db)
    layout = service.get_full_layout(store_id)
    if not layout:
        raise HTTPException(status_code=404, detail="Store not found")
    return layout

@router.post("/import", response_model=StoreSchema)
def import_store_layout(import_data: StoreImportRequest, db: Session = Depends(db_manager.get_db), current_user: User = Depends(require_store_owner)):
    service = get_store_editor_service(db)
    # 1. Create the store
    store = service.create_store(name=import_data.name, width=import_data.width, height=import_data.height)
    
    # 2. Iterate through aisles and create them
    for aisle_data in import_data.aisles:
        aisle = service.add_aisle(
            store_id=store.id,
            name=aisle_data.name,
            x_min=aisle_data.x_min,
            y_min=aisle_data.y_min,
            x_max=aisle_data.x_max,
            y_max=aisle_data.y_max
        )
        if not aisle:
            continue
            
        # 3. Add items to the aisle
        for item_data in aisle_data.items:
            service.add_item_to_aisle(
                aisle_id=aisle.id,
                name=item_data.name,
                pos_x=item_data.pos_x,
                pos_y=item_data.pos_y
            )
            
    # Return newly created store
    db.refresh(store)
    return store
