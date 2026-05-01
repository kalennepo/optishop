import pytest

def helper_create_store(client):
    response = client.post("/api/v1/stores/", json={"name": "Test Store", "width": 100.0, "height": 100.0})
    return response.json()["id"]

def test_create_store(client):
    response = client.post("/api/v1/stores/", json={"name": "Test Store", "width": 100.0, "height": 100.0})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Store"
    assert data["width"] == 100.0

def test_add_aisle(client):
    store_id = helper_create_store(client)
    
    payload = {
        "name": "Aisle 1",
        "x_min": 10.0,
        "y_min": 10.0,
        "x_max": 20.0,
        "y_max": 20.0
    }
    response = client.post(f"/api/v1/stores/{store_id}/aisles", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Aisle 1"
    
    # Test overlap (400)
    overlap_payload = {
        "name": "Aisle 2",
        "x_min": 15.0,
        "y_min": 15.0,
        "x_max": 25.0,
        "y_max": 25.0
    }
    response_overlap = client.post(f"/api/v1/stores/{store_id}/aisles", json=overlap_payload)
    assert response_overlap.status_code == 400
    assert "overlap" in response_overlap.json()["detail"].lower()

def test_add_item_to_aisle_forbidden(client, auth_headers_shopper):
    store_id = helper_create_store(client)
    aisle_response = client.post(f"/api/v1/stores/{store_id}/aisles", json={
        "name": "Aisle 1", "x_min": 1.0, "y_min": 1.0, "x_max": 2.0, "y_max": 2.0
    })
    aisle_id = aisle_response.json()["id"]
    
    response = client.post(
        f"/api/v1/stores/aisles/{aisle_id}/items",
        json={"name": "Milk", "pos_x": 1.5, "pos_y": 1.5},
        headers=auth_headers_shopper
    )
    assert response.status_code == 403

def test_add_item_to_aisle_success(client, auth_headers_owner):
    store_id = helper_create_store(client)
    aisle_response = client.post(f"/api/v1/stores/{store_id}/aisles", json={
        "name": "Aisle 1", "x_min": 1.0, "y_min": 1.0, "x_max": 2.0, "y_max": 2.0
    })
    aisle_id = aisle_response.json()["id"]
    
    response = client.post(
        f"/api/v1/stores/aisles/{aisle_id}/items",
        json={"name": "Milk", "pos_x": 1.5, "pos_y": 1.5},
        headers=auth_headers_owner
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Milk"

def test_update_aisle(client, auth_headers_owner):
    store_id = helper_create_store(client)
    aisle_response = client.post(f"/api/v1/stores/{store_id}/aisles", json={
        "name": "Aisle 1", "x_min": 1.0, "y_min": 1.0, "x_max": 5.0, "y_max": 5.0
    })
    aisle_id = aisle_response.json()["id"]
    
    response = client.put(
        f"/api/v1/stores/aisles/{aisle_id}",
        json={"name": "Updated Aisle", "x_min": 1.0, "y_min": 1.0, "x_max": 6.0, "y_max": 6.0},
        headers=auth_headers_owner
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Aisle"

def test_delete_aisle(client, auth_headers_owner):
    store_id = helper_create_store(client)
    aisle_response = client.post(f"/api/v1/stores/{store_id}/aisles", json={
        "name": "Aisle 1", "x_min": 1.0, "y_min": 1.0, "x_max": 5.0, "y_max": 5.0
    })
    aisle_id = aisle_response.json()["id"]
    
    response = client.delete(
        f"/api/v1/stores/aisles/{aisle_id}",
        headers=auth_headers_owner
    )
    assert response.status_code == 204

def test_get_layout(client):
    store_id = helper_create_store(client)
    client.post(f"/api/v1/stores/{store_id}/aisles", json={
        "name": "Aisle 1", "x_min": 1.0, "y_min": 1.0, "x_max": 5.0, "y_max": 5.0
    })
    
    response = client.get(f"/api/v1/stores/{store_id}/layout")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == store_id
    assert len(data["aisles"]) == 1
