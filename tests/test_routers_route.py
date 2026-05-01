import pytest

def test_optimize_route_success(client, auth_headers_shopper, auth_headers_owner):
    # Setup: Create a simple store with 2 items
    store_resp = client.post("/api/v1/stores/", json={"name": "Route Store", "width": 100.0, "height": 100.0})
    store_id = store_resp.json()["id"]
    
    aisle_resp = client.post(f"/api/v1/stores/{store_id}/aisles", json={
        "name": "Aisle A", "x_min": 10.0, "y_min": 10.0, "x_max": 15.0, "y_max": 30.0
    })
    aisle_id = aisle_resp.json()["id"]
    
    client.post(
        f"/api/v1/stores/aisles/{aisle_id}/items",
        json={"name": "Milk", "pos_x": 12.0, "pos_y": 15.0},
        headers=auth_headers_owner
    )
    
    client.post(
        f"/api/v1/stores/aisles/{aisle_id}/items",
        json={"name": "Bread", "pos_x": 12.0, "pos_y": 25.0},
        headers=auth_headers_owner
    )
    
    # Request route optimization
    payload = {
        "store_id": store_id,
        "item_names": ["Milk", "Bread"],
        "entrance": [0.0, 0.0],
        "exit_pos": [0.0, 0.0]
    }
    response = client.post("/api/v1/route/optimize", json=payload, headers=auth_headers_shopper)
    
    assert response.status_code == 200
    data = response.json()
    assert data["store_name"] == "Route Store"
    assert len(data["optimized_order"]) == 2
    assert "Milk" in data["optimized_order"]
    assert "Bread" in data["optimized_order"]
    assert len(data["path_coordinates"]) > 0

def test_optimize_route_store_not_found(client, auth_headers_shopper):
    payload = {
        "store_id": 999,
        "item_names": ["Milk"],
        "entrance": [0.0, 0.0],
        "exit_pos": [0.0, 0.0]
    }
    response = client.post("/api/v1/route/optimize", json=payload, headers=auth_headers_shopper)
    
    assert response.status_code == 404
    assert "Store not found" in response.json()["detail"]
