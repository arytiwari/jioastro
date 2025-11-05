#!/usr/bin/env python3
"""Test admin users API"""

import requests
import json

# Login
login_response = requests.post(
    "http://localhost:8000/api/v1/admin/login",
    json={"username": "admin", "password": "admin@123"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"✅ Logged in, token: {token[:20]}...")
    
    # Get users
    users_response = requests.get(
        "http://localhost:8000/api/v1/admin/users?limit=100",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"\n📊 Status Code: {users_response.status_code}")
    print(f"Response: {json.dumps(users_response.json(), indent=2)}")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
