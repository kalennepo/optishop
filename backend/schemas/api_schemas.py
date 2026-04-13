from typing import List, Tuple, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

# --- Grocery Item Schemas ---
class GroceryItemBase(BaseModel):
    name: str
    pos_x: float
    pos_y: float

class GroceryItemCreate(GroceryItemBase):
    pass

class GroceryItemSchema(GroceryItemBase):
    id: int
    aisle_id: int

    model_config = ConfigDict(from_attributes=True)

# --- Aisle Schemas ---
class AisleBase(BaseModel):
    name: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float

class AisleCreate(AisleBase):
    pass

class AisleSchema(AisleBase):
    id: int
    store_id: int
    items: List[GroceryItemSchema] = []

    model_config = ConfigDict(from_attributes=True)

# --- Store Schemas ---
class StoreBase(BaseModel):
    name: str
    width: float
    height: float

class StoreCreate(StoreBase):
    pass

class StoreSchema(StoreBase):
    id: int
    aisles: List[AisleSchema] = []

    model_config = ConfigDict(from_attributes=True)

# --- Layout Overview Schemas (matching get_full_layout) ---
class LayoutItemSchema(BaseModel):
    id: int
    name: str
    x: float
    y: float

class LayoutAisleSchema(BaseModel):
    id: int
    name: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    items: List[LayoutItemSchema]

class StoreLayoutResponse(BaseModel):
    id: int
    name: str
    width: float
    height: float
    aisles: List[LayoutAisleSchema]

# --- Routing Schemas ---
class RouteRequest(BaseModel):
    store_id: int
    item_names: List[str]
    entrance: Tuple[float, float] = (1.0, 1.0)
    exit_pos: Tuple[float, float] = (1.0, 1.0)

class RouteResponse(BaseModel):
    store_name: str
    optimized_order: List[str]
    optimized_items: List[GroceryItemSchema]
    total_waypoints: int
    path_coordinates: List[Tuple[float, float]]
    total_steps: int
    estimated_distance: float
    error: Optional[str] = None
