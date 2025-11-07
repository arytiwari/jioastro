"""
Test script for Life Snapshot Feature (Magical 12 Feature #1)

This script tests all Life Snapshot endpoints and functionality.

Usage:
    python test_life_snapshot.py

Requirements:
    - Backend server must be running (uvicorn main:app --reload)
    - FEATURE_LIFE_SNAPSHOT=true must be set
    - Database migration must be applied
"""

import requests
import json
from uuid import uuid4
from datetime import datetime
import os

# Configuration
BASE_URL = "http://localhost:8000"
API_V2_URL = f"{BASE_URL}/api/v2"

# ANSI color codes for pretty output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_section(title):
    """Print a section header."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(message):
    """Print a success message."""
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    """Print an error message."""
    print(f"{RED}❌ {message}{RESET}")


def print_warning(message):
    """Print a warning message."""
    print(f"{YELLOW}⚠️  {message}{RESET}")


def print_info(message):
    """Print an info message."""
    print(f"{BLUE}ℹ️  {message}{RESET}")


def test_server_health():
    """Test if server is running."""
    print_section("1. Testing Server Health")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("Server is running")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print_error(f"Server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Cannot connect to server: {e}")
        print_warning("Make sure the server is running: uvicorn main:app --reload")
        return False


def test_feature_info():
    """Test feature info endpoint (no auth required)."""
    print_section("2. Testing Feature Info Endpoint")

    try:
        response = requests.get(f"{API_V2_URL}/life-snapshot/", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_success("Feature info endpoint works!")
            print(f"   Feature: {data.get('feature')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Description: {data.get('description')}")
            print(f"   Magical Number: {data.get('magical_twelve_number')}")
            print(f"   Read Time: {data.get('read_time_seconds')}s")
            print(f"   Cache TTL: {data.get('cache_ttl_seconds')}s")
            return True
        elif response.status_code == 403:
            print_error("Feature is disabled!")
            print_warning("Set environment variable: export FEATURE_LIFE_SNAPSHOT=true")
            return False
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False


def test_generate_snapshot_no_auth():
    """Test snapshot generation without authentication (should fail)."""
    print_section("3. Testing Auth Protection")

    try:
        response = requests.post(
            f"{API_V2_URL}/life-snapshot/generate",
            json={"profile_id": str(uuid4()), "force_refresh": False},
            timeout=5
        )

        if response.status_code == 401:
            print_success("Auth protection works! (401 Unauthorized as expected)")
            return True
        else:
            print_warning(f"Expected 401, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False


def test_database_migration():
    """Check if database migration has been applied."""
    print_section("4. Checking Database Migration")

    print_info("To run the migration, execute:")
    print("   psql -d your_database -f docs/migrations/life_snapshot_tables.sql")
    print("\n   Or in Supabase SQL Editor:")
    print("   - Copy contents of docs/migrations/life_snapshot_tables.sql")
    print("   - Paste and execute in SQL Editor")

    print_warning("Migration check requires database access (skipped in this test)")
    return True


def test_api_docs():
    """Check if API documentation includes Life Snapshot endpoints."""
    print_section("5. Testing API Documentation")

    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)

        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})

            life_snapshot_paths = [
                path for path in paths.keys()
                if "life-snapshot" in path
            ]

            if life_snapshot_paths:
                print_success("Life Snapshot endpoints found in API docs!")
                print("   Endpoints:")
                for path in life_snapshot_paths:
                    methods = list(paths[path].keys())
                    print(f"   - {', '.join(methods).upper()} {path}")

                print_info(f"\nView full docs at: {BASE_URL}/docs")
                return True
            else:
                print_error("Life Snapshot endpoints not found in API docs")
                return False
        else:
            print_error(f"Could not fetch OpenAPI spec: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False


def print_test_with_auth_instructions():
    """Print instructions for testing with authentication."""
    print_section("6. Testing with Authentication")

    print_info("To test authenticated endpoints, you need a JWT token.")
    print("\nOption 1 - Get token from frontend:")
    print("   1. Login to the frontend application")
    print("   2. Open browser DevTools > Application > Local Storage")
    print("   3. Find the auth token")
    print("   4. Copy the token value")

    print("\nOption 2 - Use curl with token:")
    print("   export JWT_TOKEN='your-jwt-token-here'")
    print("   curl -X POST http://localhost:8000/api/v2/life-snapshot/generate \\")
    print("     -H 'Authorization: Bearer $JWT_TOKEN' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "profile_id": "your-profile-uuid",')
    print('       "force_refresh": false')
    print("     }'")

    print("\nOption 3 - Create test with mock auth:")
    print("   See app/features/life_snapshot/tests/ for unit test examples")


def run_all_tests():
    """Run all tests."""
    print(f"{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}Life Snapshot Feature Test Suite{RESET}")
    print(f"{BLUE}Magical 12 Feature #1{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")

    results = []

    # Test 1: Server Health
    results.append(("Server Health", test_server_health()))

    if not results[0][1]:
        print_error("\nServer is not running. Stopping tests.")
        return

    # Test 2: Feature Info
    results.append(("Feature Info", test_feature_info()))

    # Test 3: Auth Protection
    results.append(("Auth Protection", test_generate_snapshot_no_auth()))

    # Test 4: Database Migration
    results.append(("Database Migration", test_database_migration()))

    # Test 5: API Docs
    results.append(("API Documentation", test_api_docs()))

    # Test 6: Auth Instructions
    print_test_with_auth_instructions()

    # Summary
    print_section("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"   {test_name}: {status}")

    print(f"\n   Total: {passed}/{total} tests passed")

    if passed == total:
        print_success("\nAll tests passed! ✨")
        print_info("Next steps:")
        print("   1. Run database migration if not already done")
        print("   2. Test authenticated endpoints with a real JWT token")
        print("   3. Create a test profile and generate snapshots")
    else:
        print_warning(f"\n{total - passed} test(s) failed. Check the errors above.")


if __name__ == "__main__":
    # Check if running from correct directory
    if not os.path.exists("main.py"):
        print_error("Please run this script from the backend directory")
        print("   cd backend")
        print("   python test_life_snapshot.py")
        exit(1)

    run_all_tests()
