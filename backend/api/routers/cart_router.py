from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.db.db_connection import db_manager
from backend.api.dependencies import get_current_user
from backend.models.user import User
from backend.models.cart import Cart, CartItem
from backend.models.grocery_item import GroceryItem
from backend.repositories.cart import CartRepository, CartItemRepository
from backend.repositories.item import ItemRepository
from backend.schemas.api_schemas import CartSchema, CartCreate, CartItemSchema, CartItemCreate, CartFavoriteRequest

router = APIRouter(
    prefix="/carts",
    tags=["carts"]
)

@router.post("/", response_model=CartSchema)
def create_cart(cart_in: CartCreate, db: Session = Depends(db_manager.get_db), current_user: User = Depends(get_current_user)):
    cart_repo = CartRepository(db)
    new_cart = Cart(
        user_id=current_user.id,
        name=cart_in.name,
        is_favorite=cart_in.is_favorite
    )
    return cart_repo.add(new_cart)

@router.get("/favorites", response_model=List[CartSchema])
def get_favorite_carts(db: Session = Depends(db_manager.get_db), current_user: User = Depends(get_current_user)):
    cart_repo = CartRepository(db)
    return cart_repo.get_user_favorites(current_user.id)

@router.post("/{cart_id}/favorite", response_model=CartSchema)
def favorite_cart(cart_id: int, request: CartFavoriteRequest, db: Session = Depends(db_manager.get_db), current_user: User = Depends(get_current_user)):
    cart_repo = CartRepository(db)
    cart = cart_repo.get_by_id(cart_id)
    if not cart or cart.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cart not found")
        
    cart.is_favorite = True
    if request.name:
        cart.name = request.name
        
    return cart_repo.update(cart)

@router.delete("/favorites/{cart_id}", status_code=204)
def delete_favorite_cart(cart_id: int, db: Session = Depends(db_manager.get_db), current_user: User = Depends(get_current_user)):
    cart_repo = CartRepository(db)
    cart = cart_repo.get_by_id(cart_id)
    if not cart or cart.user_id != current_user.id or not cart.is_favorite:
        raise HTTPException(status_code=404, detail="Favorite cart not found")
        
    cart_repo.delete(cart)

@router.post("/{cart_id}/items", response_model=CartItemSchema)
def add_item_to_cart(cart_id: int, item_in: CartItemCreate, db: Session = Depends(db_manager.get_db), current_user: User = Depends(get_current_user)):
    cart_repo = CartRepository(db)
    item_repo = ItemRepository(db)
    cart_item_repo = CartItemRepository(db)
    
    cart = cart_repo.get_by_id(cart_id)
    if not cart or cart.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cart not found")
        
    grocery_item = item_repo.get_by_id(item_in.item_id)
    if not grocery_item:
        raise HTTPException(status_code=404, detail="Grocery item not found")
        
    # Check if item already exists in cart
    existing_cart_item = cart_item_repo.get_by_cart_and_item(cart_id, item_in.item_id)
    if existing_cart_item:
        return existing_cart_item
        
    new_cart_item = CartItem(
        cart_id=cart_id,
        item_id=item_in.item_id
    )
    return cart_item_repo.add(new_cart_item)

@router.delete("/{cart_id}/items/{item_id}", status_code=204)
def remove_item_from_cart(cart_id: int, item_id: int, db: Session = Depends(db_manager.get_db), current_user: User = Depends(get_current_user)):
    cart_repo = CartRepository(db)
    cart_item_repo = CartItemRepository(db)
    
    cart = cart_repo.get_by_id(cart_id)
    if not cart or cart.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cart not found")
        
    cart_item = cart_item_repo.get_by_cart_and_item(cart_id, item_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
        
    cart_item_repo.delete(cart_item)
