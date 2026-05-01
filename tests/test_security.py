import pytest
import jwt
from datetime import datetime, timedelta, timezone
from backend.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)

def test_password_hashing():
    password = "supersecretpassword123"
    
    # Hash the password
    hashed = get_password_hash(password)
    
    # Ensure it's not the plaintext password
    assert hashed != password
    
    # Verify correct password
    assert verify_password(password, hashed) is True
    
    # Verify incorrect password
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    data = {"sub": "test@example.com"}
    
    # Create token
    token = create_access_token(data=data)
    
    # Decode token to verify contents
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    assert payload.get("sub") == "test@example.com"
    assert "exp" in payload
    
    # Verify expiration is in the future
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert exp_time > datetime.now(timezone.utc)

def test_create_access_token_with_expires_delta():
    data = {"sub": "test2@example.com"}
    expires_delta = timedelta(minutes=30)
    
    token = create_access_token(data=data, expires_delta=expires_delta)
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == "test2@example.com"
    
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    expected_exp_time = datetime.now(timezone.utc) + expires_delta
    
    # Allow for a small delta (1-2 seconds) due to execution time
    assert abs((exp_time - expected_exp_time).total_seconds()) < 5
