"""
Simple validation script for advanced system endpoints.
No external dependencies required (uses only requests/http.client).

Run with:
    python3 scripts/validate_advanced_endpoints.py
"""

import http.client
import json
from urllib.parse import urlparse

def test_endpoint_availability(host="localhost", port=8000):
    """Test that all advanced system endpoints are registered."""
    conn = http.client.HTTPConnection(host, port)

    try:
        # Get OpenAPI schema
        conn.request("GET", "/openapi.json")
        response = conn.getresponse()

        if response.status != 200:
            print(f"❌ Failed to get OpenAPI schema: {response.status}")
            return False

        data = json.loads(response.read().decode())
        paths = data.get("paths", {})

        # Count endpoints by system
        jaimini_endpoints = []
        lal_kitab_endpoints = []
        ashtakavarga_endpoints = []
        varshaphal_endpoints = []
        compatibility_endpoints = []

        for path in paths.keys():
            if "/enhancements/jaimini/" in path:
                jaimini_endpoints.append(path)
            elif "/enhancements/lal-kitab/" in path:
                lal_kitab_endpoints.append(path)
            elif "/enhancements/ashtakavarga/" in path:
                ashtakavarga_endpoints.append(path)
            elif "/varshaphal/" in path:
                varshaphal_endpoints.append(path)
            elif "/compatibility/" in path:
                compatibility_endpoints.append(path)

        # Print results
        print("\n" + "=" * 80)
        print("🔍 ADVANCED SYSTEMS ENDPOINT VALIDATION")
        print("=" * 80)

        print("\n📊 Jaimini System (%d endpoints):" % len(jaimini_endpoints))
        for ep in sorted(jaimini_endpoints):
            print(f"  ✓ {ep}")

        print("\n📕 Lal Kitab System (%d endpoints):" % len(lal_kitab_endpoints))
        for ep in sorted(lal_kitab_endpoints):
            print(f"  ✓ {ep}")

        print("\n📐 Ashtakavarga System (%d endpoints):" % len(ashtakavarga_endpoints))
        for ep in sorted(ashtakavarga_endpoints):
            print(f"  ✓ {ep}")

        print("\n📅 Varshaphal System (%d endpoints):" % len(varshaphal_endpoints))
        for ep in sorted(varshaphal_endpoints):
            print(f"  ✓ {ep}")

        print("\n💕 Compatibility System (%d endpoints):" % len(compatibility_endpoints))
        for ep in sorted(compatibility_endpoints):
            print(f"  ✓ {ep}")

        # Summary
        total = len(jaimini_endpoints) + len(lal_kitab_endpoints) + len(ashtakavarga_endpoints) + len(varshaphal_endpoints) + len(compatibility_endpoints)

        print("\n" + "=" * 80)
        print(f"📈 SUMMARY: {total} total advanced system endpoints")
        print("=" * 80)

        # Validation
        errors = []
        if len(jaimini_endpoints) != 4:
            errors.append(f"Expected 4 Jaimini endpoints, found {len(jaimini_endpoints)}")
        if len(lal_kitab_endpoints) != 3:
            errors.append(f"Expected 3 Lal Kitab endpoints, found {len(lal_kitab_endpoints)}")
        if len(ashtakavarga_endpoints) != 4:
            errors.append(f"Expected 4 Ashtakavarga endpoints, found {len(ashtakavarga_endpoints)}")
        if len(varshaphal_endpoints) < 3:
            errors.append(f"Expected at least 3 Varshaphal endpoints, found {len(varshaphal_endpoints)}")
        if len(compatibility_endpoints) < 5:
            errors.append(f"Expected at least 5 Compatibility endpoints, found {len(compatibility_endpoints)}")

        if errors:
            print("\n⚠️  VALIDATION WARNINGS:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print("\n✅ ALL ENDPOINT COUNTS VALIDATED SUCCESSFULLY!")
            print(f"   • Jaimini: {len(jaimini_endpoints)}/4 ✓")
            print(f"   • Lal Kitab: {len(lal_kitab_endpoints)}/3 ✓")
            print(f"   • Ashtakavarga: {len(ashtakavarga_endpoints)}/4 ✓")
            print(f"   • Varshaphal: {len(varshaphal_endpoints)}/3+ ✓")
            print(f"   • Compatibility: {len(compatibility_endpoints)}/5+ ✓")
            return True

    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False
    finally:
        conn.close()


def test_backend_health(host="localhost", port=8000):
    """Test backend health endpoint."""
    conn = http.client.HTTPConnection(host, port)

    try:
        conn.request("GET", "/health")
        response = conn.getresponse()

        if response.status == 200:
            data = json.loads(response.read().decode())
            print("\n💚 Backend Health Check:")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   API: {data.get('api', 'unknown')}")
            return True
        else:
            print(f"\n❌ Backend health check failed: {response.status}")
            return False
    except Exception as e:
        print(f"\n❌ Backend not reachable: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    print("\n🚀 Starting Advanced Systems Validation...")

    # Test backend health
    if not test_backend_health():
        print("\n❌ Backend is not healthy. Please start the backend first.")
        print("   Run: uvicorn main:app --reload")
        exit(1)

    # Test endpoint availability
    if test_endpoint_availability():
        print("\n" + "=" * 80)
        print("🎉 ALL VALIDATIONS PASSED!")
        print("=" * 80)
        exit(0)
    else:
        print("\n" + "=" * 80)
        print("❌ SOME VALIDATIONS FAILED")
        print("=" * 80)
        exit(1)
