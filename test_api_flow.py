import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def run_tests():
    print("Starting integration tests...")
    
    # 1. Register Store Owner
    owner_data = {"email": "owner@test.com", "password": "password", "role": "store_owner"}
    r = requests.post(f"{BASE_URL}/auth/register", json=owner_data)
    if r.status_code != 200:
        print(f"Failed to register owner: {r.text}")
    
    # 2. Login Store Owner
    login_data = {"email": "owner@test.com", "password": "password"}
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if r.status_code != 200:
        print(f"Failed to login owner: {r.text}")
        return
    owner_token = r.json()["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    
    # 3. Import Store
    store_data = {
        "name": "Test Store",
        "width": 20.0,
        "height": 20.0,
        "aisles": [
            {
                "name": "Aisle 1",
                "x_min": 1.0, "y_min": 1.0, "x_max": 2.0, "y_max": 5.0,
                "items": [
                    {"name": "Apple", "pos_x": 1.5, "pos_y": 2.0}
                ]
            }
        ]
    }
    r = requests.post(f"{BASE_URL}/stores/import", json=store_data, headers=owner_headers)
    if r.status_code != 200:
        print(f"Failed to import store: {r.text}")
        return
    store_id = r.json()["id"]
    item_id = r.json()["aisles"][0]["items"][0]["id"]
    print(f"Store created with ID: {store_id}, Item ID: {item_id}")
    
    # 4. Register Shopper
    shopper_data = {"email": "shopper@test.com", "password": "password", "role": "shopper"}
    r = requests.post(f"{BASE_URL}/auth/register", json=shopper_data)
    
    # 5. Login Shopper
    login_data = {"email": "shopper@test.com", "password": "password"}
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    shopper_token = r.json()["access_token"]
    shopper_headers = {"Authorization": f"Bearer {shopper_token}"}
    
    # 6. Create Cart
    r = requests.post(f"{BASE_URL}/carts/", json={"name": "My Cart", "is_favorite": False}, headers=shopper_headers)
    if r.status_code != 200:
        print(f"Failed to create cart: {r.text}")
        return
    cart_id = r.json()["id"]
    
    # 7. Add Item to Cart
    r = requests.post(f"{BASE_URL}/carts/{cart_id}/items", json={"item_id": item_id}, headers=shopper_headers)
    if r.status_code != 200:
        print(f"Failed to add item to cart: {r.text}")
        return
        
    # 8. Favorite Cart
    r = requests.post(f"{BASE_URL}/carts/{cart_id}/favorite", json={"name": "Fave Cart"}, headers=shopper_headers)
    if r.status_code != 200:
        print(f"Failed to favorite cart: {r.text}")
        return
        
    # 9. Get Favorites
    r = requests.get(f"{BASE_URL}/carts/favorites", headers=shopper_headers)
    if r.status_code != 200 or len(r.json()) == 0:
        print(f"Failed to get favorites: {r.text}")
        return
        
    # 10. Report Out of Stock
    r = requests.post(f"{BASE_URL}/stores/items/{item_id}/report-out-of-stock", headers=shopper_headers)
    if r.status_code != 200:
        print(f"Failed to report out of stock: {r.text}")
        return
        
    # 11. Owner Views Report
    r = requests.get(f"{BASE_URL}/stores/{store_id}/reports/out-of-stock", headers=owner_headers)
    if r.status_code != 200 or len(r.json()) == 0:
        print(f"Failed to get out of stock report: {r.text}")
        return
        
    print("All endpoints hit successfully and returned expected 200 OK responses!")

if __name__ == "__main__":
    run_tests()
