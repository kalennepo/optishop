import pytest
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone

from backend.api.dependencies import get_current_user, require_store_owner
from backend.core.security import create_access_token, SECRET_KEY, ALGORITHM
from backend.models.user import User
from backend.repositories.user import UserRepository

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        role="shopper"
    )
    user_repo = UserRepository(db_session)
    return user_repo.add(user)

@pytest.fixture
def owner_user(db_session):
    user = User(
        email="owner@example.com",
        hashed_password="hashed_password",
        role="store_owner"
    )
    user_repo = UserRepository(db_session)
    return user_repo.add(user)

def test_get_current_user_valid(db_session, test_user):
    token = create_access_token(data={"sub": test_user.email})
    
    user = get_current_user(token=token, db=db_session)
    
    assert user is not None
    assert user.email == test_user.email

def test_get_current_user_invalid_token(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="invalid_token", db=db_session)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail

def test_get_current_user_expired_token(db_session, test_user):
    # Create a token that is already expired
    expires_delta = timedelta(minutes=-10)
    token = create_access_token(data={"sub": test_user.email}, expires_delta=expires_delta)
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)
    
    assert exc_info.value.status_code == 401
    assert "Token expired" in exc_info.value.detail

def test_get_current_user_user_not_found(db_session):
    token = create_access_token(data={"sub": "nonexistent@example.com"})
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail

def test_get_current_user_missing_sub(db_session):
    # Create a token without a "sub" claim
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {"other_claim": "value", "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail

def test_require_store_owner_success(owner_user):
    user = require_store_owner(current_user=owner_user)
    assert user.email == owner_user.email
    assert user.role == "store_owner"

def test_require_store_owner_forbidden(test_user):
    with pytest.raises(HTTPException) as exc_info:
        require_store_owner(current_user=test_user)
    
    assert exc_info.value.status_code == 403
    assert "doesn't have enough privileges" in exc_info.value.detail
