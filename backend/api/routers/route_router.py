from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.db_connection import db_manager
from backend.logic.shopping_service import ShoppingService
from backend.schemas.api_schemas import RouteRequest, RouteResponse

router = APIRouter(
    prefix="/route",
    tags=["route"]
)

@router.post("/optimize", response_model=RouteResponse)
def optimize_route(request: RouteRequest, db: Session = Depends(db_manager.get_db)):
    """
    Handles the Indoor GPS algorithm by coordinating with ShoppingService.
    """
    service = ShoppingService(db)
    result = service.generate_route(
        store_id=request.store_id,
        item_names=request.item_names,
        entrance=request.entrance,
        exit_pos=request.exit_pos
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result
