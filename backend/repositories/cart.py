from sqlalchemy.orm import Session
from typing import List, Optional
from backend.models.cart import Cart, CartItem
from backend.repositories.base import BaseRepository

class CartRepository(BaseRepository[Cart]):
    def __init__(self, db: Session):
        super().__init__(db, Cart)
        
    def get_user_favorites(self, user_id: int) -> List[Cart]:
        return self.db.query(Cart).filter(Cart.user_id == user_id, Cart.is_favorite == True).all()
        
class CartItemRepository(BaseRepository[CartItem]):
    def __init__(self, db: Session):
        super().__init__(db, CartItem)
        
    def get_by_cart_and_item(self, cart_id: int, item_id: int) -> Optional[CartItem]:
        return self.db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.item_id == item_id).first()
