import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_delivery_flow():
    session = requests.Session()
    
    # 1. Login as Admin/Staff (needed for Kitchen view)
    print("1. Logging in...")
    login_payload = {'username': 'admin', 'password': 'password'}
    resp = session.post(f"{BASE_URL}/login", data=login_payload)
    if resp.url == f"{BASE_URL}/login":
        print("Login Failed")
        return False
    print("Login Successful")

    # 2. Place a Delivery Order (Public API)
    print("2. Placing Order...")
    order_data = {
        "name": "Test User",
        "address": "123 Test St",
        "cart": {
            "1": {"name": "Rice Bowl", "qty": 2, "price": 50.0}
        }
    }
    resp = requests.post(f"{BASE_URL}/api/order", json=order_data)
    if resp.status_code != 200 or not resp.json().get('success'):
        print("Order Placement Failed")
        print(resp.text)
        return False
    
    order_id = resp.json()['order_id']
    print(f"Order Placed. ID: {order_id}")

    # 3. Verify Order Appears in Kitchen View
    print("3. Checking Kitchen View...")
    resp = session.get(f"{BASE_URL}/delivery/kitchen")
    if "Test User" not in resp.text:
        print("Order not found in Kitchen View")
        return False
    print("Order found in Kitchen View")

    print(f"Verification Sent! Manual check required to mark order #{order_id} as delivered.")
    return True

if __name__ == "__main__":
    try:
        if test_delivery_flow():
            print("SUCCESS: Delivery Flow Verified")
        else:
            print("FAILURE: Delivery Flow Issues")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("FAILURE: Could not connect to app. Is it running?")
        sys.exit(1)
