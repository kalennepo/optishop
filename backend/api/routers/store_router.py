from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.db.db_connection import db_manager
from backend.logic.store_editor import StoreEditorService
from backend.schemas.api_schemas import (
    StoreCreate, StoreSchema, StoreLayoutResponse, 
    AisleCreate, AisleSchema, GroceryItemCreate, GroceryItemSchema
)

router = APIRouter(
    prefix="/stores",
    tags=["stores"]
)

@router.post("/", response_model=StoreSchema)
def create_store(store_in: StoreCreate, db: Session = Depends(db_manager.get_db)):
    service = StoreEditorService(db)
    return service.create_store(name=store_in.name, width=store_in.width, height=store_in.height)

@router.get("/{store_id}/layout", response_model=StoreLayoutResponse)
def get_store_layout(store_id: int, db: Session = Depends(db_manager.get_db)):
    service = StoreEditorService(db)
    layout = service.get_full_layout(store_id)
    if not layout:
        raise HTTPException(status_code=404, detail="Store not found")
    return layout

@router.post("/{store_id}/aisles", response_model=AisleSchema)
def add_aisle(store_id: int, aisle_in: AisleCreate, db: Session = Depends(db_manager.get_db)):
    service = StoreEditorService(db)
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
def add_item_to_aisle(aisle_id: int, item_in: GroceryItemCreate, db: Session = Depends(db_manager.get_db)):
    service = StoreEditorService(db)
    item = service.add_item_to_aisle(
        aisle_id=aisle_id,
        name=item_in.name,
        pos_x=item_in.pos_x,
        pos_y=item_in.pos_y
    )
    if not item:
        raise HTTPException(status_code=404, detail="Aisle not found")
    return item
