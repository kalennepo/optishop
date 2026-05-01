import pytest

def test_register_user_success(client):
    payload = {
        "email": "testauth@example.com",
        "password": "password123",
        "role": "shopper"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testauth@example.com"
    assert data["role"] == "shopper"
    assert "id" in data
    assert "password" not in data

def test_register_user_duplicate(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "password123",
        "role": "shopper"
    }
    # Register first time
    response1 = client.post("/api/v1/auth/register", json=payload)
    assert response1.status_code == 200
    
    # Register second time
    response2 = client.post("/api/v1/auth/register", json=payload)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]

def test_login_success(client):
    # Register user first
    client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "loginpass",
        "role": "shopper"
    })
    
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "loginpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    client.post("/api/v1/auth/register", json={
        "email": "loginbadpass@example.com",
        "password": "loginpass",
        "role": "shopper"
    })
    
    response = client.post("/api/v1/auth/login", json={
        "email": "loginbadpass@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_invalid_email(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "somepassword"
    })
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]
