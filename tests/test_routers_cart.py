import pytest

def helper_create_cart(client, auth_headers):
    response = client.post(
        "/api/v1/carts/",
        json={"name": "Weekly Groceries", "is_favorite": False},
        headers=auth_headers
    )
    return response.json()["id"]

def test_create_cart(client, auth_headers_shopper):
    response = client.post(
        "/api/v1/carts/",
        json={"name": "Weekly Groceries", "is_favorite": False},
        headers=auth_headers_shopper
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Weekly Groceries"
    assert data["is_favorite"] is False

def test_favorite_cart(client, auth_headers_shopper):
    cart_id = helper_create_cart(client, auth_headers_shopper)
    
    response = client.post(
        f"/api/v1/carts/{cart_id}/favorite",
        json={"name": "My Favorite Cart"},
        headers=auth_headers_shopper
    )
    assert response.status_code == 200
    assert response.json()["is_favorite"] is True
    assert response.json()["name"] == "My Favorite Cart"

def test_get_favorite_carts(client, auth_headers_shopper):
    cart_id = helper_create_cart(client, auth_headers_shopper)
    client.post(
        f"/api/v1/carts/{cart_id}/favorite",
        json={"name": "My Favorite Cart"},
        headers=auth_headers_shopper
    )
    
    response = client.get("/api/v1/carts/favorites", headers=auth_headers_shopper)
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["is_favorite"] is True

def test_delete_favorite_cart(client, auth_headers_shopper):
    cart_id = helper_create_cart(client, auth_headers_shopper)
    client.post(
        f"/api/v1/carts/{cart_id}/favorite",
        json={"name": "To Delete"},
        headers=auth_headers_shopper
    )
    
    response = client.delete(
        f"/api/v1/carts/favorites/{cart_id}",
        headers=auth_headers_shopper
    )
    assert response.status_code == 204

def test_cart_item_operations(client, auth_headers_shopper, auth_headers_owner):
    # 1. Create a store and an item (requires owner)
    store_resp = client.post("/api/v1/stores/", json={"name": "Test", "width": 100.0, "height": 100.0})
    store_id = store_resp.json()["id"]
    
    aisle_resp = client.post(f"/api/v1/stores/{store_id}/aisles", json={
        "name": "A1", "x_min": 1.0, "y_min": 1.0, "x_max": 5.0, "y_max": 5.0
    })
    aisle_id = aisle_resp.json()["id"]
    
    item_resp = client.post(
        f"/api/v1/stores/aisles/{aisle_id}/items",
        json={"name": "Apple", "pos_x": 2.0, "pos_y": 2.0},
        headers=auth_headers_owner
    )
    item_id = item_resp.json()["id"]
    
    # 2. Create a cart (requires shopper)
    cart_id = helper_create_cart(client, auth_headers_shopper)
    
    # 3. Add item to cart
    add_resp = client.post(
        f"/api/v1/carts/{cart_id}/items",
        json={"item_id": item_id},
        headers=auth_headers_shopper
    )
    assert add_resp.status_code == 200
    assert add_resp.json()["item_id"] == item_id
    
    # 4. Remove item from cart
    remove_resp = client.delete(
        f"/api/v1/carts/{cart_id}/items/{item_id}",
        headers=auth_headers_shopper
    )
    assert remove_resp.status_code == 204
