from typing import List, Tuple, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, EmailStr

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: str = "shopper" # Optional, could restrict in production

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_verified: bool
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Grocery Item Schemas ---
class GroceryItemBase(BaseModel):
    name: str
    pos_x: float
    pos_y: float

class GroceryItemCreate(GroceryItemBase):
    pass

class GroceryItemUpdate(BaseModel):
    name: Optional[str] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    aisle_id: Optional[int] = None

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

class AisleUpdate(BaseModel):
    name: Optional[str] = None
    x_min: Optional[float] = None
    y_min: Optional[float] = None
    x_max: Optional[float] = None
    y_max: Optional[float] = None

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

class StoreImportItem(BaseModel):
    name: str
    pos_x: float
    pos_y: float

class StoreImportAisle(BaseModel):
    name: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    items: List[StoreImportItem] = []

class StoreImportRequest(BaseModel):
    name: str
    width: float
    height: float
    aisles: List[StoreImportAisle] = []

# --- Cart Schemas ---
class CartItemCreate(BaseModel):
    item_id: int

class CartItemSchema(BaseModel):
    id: int
    cart_id: int
    item_id: int
    item: GroceryItemSchema
    
    model_config = ConfigDict(from_attributes=True)

class CartCreate(BaseModel):
    name: Optional[str] = None
    is_favorite: bool = False

class CartFavoriteRequest(BaseModel):
    name: Optional[str] = None

class CartSchema(BaseModel):
    id: int
    user_id: int
    name: Optional[str]
    is_favorite: bool
    items: List[CartItemSchema] = []
    
    model_config = ConfigDict(from_attributes=True)

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
