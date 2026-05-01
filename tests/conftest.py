import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the root directory to sys.path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main import app
from backend.db.db_connection import Base, db_manager
from backend.logic.store_map import StoreMap

from backend.models.user import User
from backend.models.store import Store
from backend.models.aisle import Aisle
from backend.models.grocery_item import GroceryItem
from backend.models.cart import Cart, CartItem

from sqlalchemy.pool import StaticPool

@pytest.fixture
def db_session():
    """Provides an in-memory SQLite SQLAlchemy session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Provides a TestClient with the database dependency overridden."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[db_manager.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

from backend.models.user import User
from backend.repositories.user import UserRepository
from backend.core.security import get_password_hash, create_access_token

@pytest.fixture
def auth_headers_shopper(db_session, client):
    # Create shopper
    user_repo = UserRepository(db_session)
    if not user_repo.get_by_email("shopper@example.com"):
        user = User(
            email="shopper@example.com",
            hashed_password=get_password_hash("password"),
            role="shopper"
        )
        user_repo.add(user)
    
    token = create_access_token({"sub": "shopper@example.com", "role": "shopper"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_headers_owner(db_session, client):
    # Create owner
    user_repo = UserRepository(db_session)
    if not user_repo.get_by_email("owner@example.com"):
        user = User(
            email="owner@example.com",
            hashed_password=get_password_hash("password"),
            role="store_owner"
        )
        user_repo.add(user)
        
    token = create_access_token({"sub": "owner@example.com", "role": "store_owner"})
    return {"Authorization": f"Bearer {token}"}

from backend.logic.store_map import StoreMap
@pytest.fixture
def empty_store_map():
    """Provides a fresh StoreMap instance."""
    return StoreMap()
