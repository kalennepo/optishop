from sqlalchemy.orm import Session
from backend.models.store import Store
from backend.repositories.base import BaseRepository

class StoreRepository(BaseRepository[Store]):
    def __init__(self, db: Session):
        super().__init__(db, Store)
