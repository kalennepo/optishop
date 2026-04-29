from sqlalchemy.orm import Session
from backend.models.aisle import Aisle
from backend.repositories.base import BaseRepository

class AisleRepository(BaseRepository[Aisle]):
    def __init__(self, db: Session):
        super().__init__(db, Aisle)
