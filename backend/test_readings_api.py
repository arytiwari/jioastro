"""Test script for Readings API endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test public health endpoint (no auth required)"""
    print("\n1. Testing /health endpoint (public)...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Root health check passed")

def test_readings_health():
    """Test readings health endpoint (should be public)"""
    print("\n2. Testing /api/v1/readings/health endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/readings/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Readings health check passed")

def test_calculate_without_auth():
    """Test calculate endpoint without auth (should fail)"""
    print("\n3. Testing /api/v1/readings/calculate WITHOUT auth (should fail)...")
    data = {
        "name": "Test User",
        "dob": "1990-01-15",
        "tob": "10:30",
        "latitude": 28.7041,
        "longitude": 77.1025,
        "timezone": "Asia/Kolkata",
        "city": "Delhi"
    }
    response = requests.post(f"{BASE_URL}/api/v1/readings/calculate", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 401 or response.status_code == 403
    print("✅ Correctly requires authentication")

def test_with_auth(token: str):
    """Test calculate endpoint with auth"""
    print("\n4. Testing /api/v1/readings/calculate WITH auth...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Test User",
        "dob": "1990-01-15",
        "tob": "10:30",
        "latitude": 28.7041,
        "longitude": 77.1025,
        "timezone": "Asia/Kolkata",
        "city": "Delhi"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/readings/calculate",
        json=data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Reading calculated successfully!")
        print(f"Session ID: {result.get('session_id')}")
        print(f"Canonical Hash: {result.get('meta', {}).get('canonical_hash')}")
        print(f"Charts available: {list(result.get('charts', {}).keys())}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("=" * 60)
    print("Vedic Astro Engine - Readings API Test Suite")
    print("=" * 60)

    try:
        # Test 1: Root health
        test_health()

        # Test 2: Readings health
        test_readings_health()

        # Test 3: Calculate without auth
        test_calculate_without_auth()

        # Test 4: Calculate with auth (provide token if available)
        print("\n" + "=" * 60)
        print("For authenticated tests, provide a valid Supabase JWT token:")
        print("You can get this from:")
        print("1. Login to the frontend")
        print("2. Check browser localStorage for 'auth_token'")
        print("3. Or use Supabase Dashboard to generate a test token")
        print("=" * 60)

        token = input("\nEnter JWT token (or press Enter to skip): ").strip()
        if token:
            test_with_auth(token)
        else:
            print("\n⏭️  Skipping authenticated tests")

        print("\n" + "=" * 60)
        print("✅ All basic tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to {BASE_URL}")
        print("Make sure the backend is running:")
        print("  cd backend")
        print("  uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
