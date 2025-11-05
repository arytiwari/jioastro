#!/usr/bin/env python3
"""Test admin API to see document data structure"""

import requests
import json

# Login
login_response = requests.post(
    "http://localhost:8000/api/v1/admin/login",
    json={"username": "admin", "password": "admin@123"}
)

token = login_response.json()["access_token"]
print(f"✅ Logged in, token: {token[:20]}...")

# Get documents
docs_response = requests.get(
    "http://localhost:8000/api/v1/admin/knowledge?limit=100",
    headers={"Authorization": f"Bearer {token}"}
)

data = docs_response.json()
print(f"\n📊 Total documents: {data['total']}")
print("\n📄 Documents:")
print(json.dumps(data['documents'], indent=2))
