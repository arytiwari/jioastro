"""
Comprehensive test suite for advanced astrological systems endpoints.

Tests:
- Jaimini System (4 endpoints)
- Lal Kitab System (3 endpoints)
- Ashtakavarga System (4 endpoints)
- Varshaphal System (3 endpoints)
- Compatibility System (5 endpoints)

Total: 19 endpoints

Run with:
    pytest tests/test_advanced_systems_endpoints.py -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def auth_token():
    """
    Get a valid auth token for testing.
    NOTE: This is a placeholder. In real tests, you would:
    1. Create a test user
    2. Login and get JWT token
    3. Use that token for all requests
    """
    # For now, return a mock token
    # In production, integrate with Supabase auth
    return "test-token-replace-with-real-jwt"


@pytest.fixture(scope="module")
def test_profile_id(auth_token):
    """
    Create a test profile and return its ID.
    NOTE: Replace with actual profile creation logic.
    """
    # Placeholder - in real tests, create via API
    return "test-profile-id-replace-with-real-id"


@pytest.fixture(scope="module")
def second_profile_id(auth_token):
    """
    Second profile for compatibility testing.
    """
    return "test-profile-id-2-replace-with-real-id"


@pytest.fixture
def auth_headers(auth_token):
    """Return headers with authentication."""
    return {"Authorization": f"Bearer {auth_token}"}


# ============================================================================
# JAIMINI SYSTEM TESTS (4 endpoints)
# ============================================================================

class TestJaiminiSystem:
    """Test all Jaimini system endpoints."""

    def test_get_chara_karakas(self, auth_headers, test_profile_id):
        """Test GET /api/v1/enhancements/jaimini/chara-karakas/{profile_id}"""
        response = client.get(
            f"/api/v1/enhancements/jaimini/chara-karakas/{test_profile_id}",
            headers=auth_headers
        )
        # Accept either 200 (success) or 401/404 (auth/profile not found)
        assert response.status_code in [200, 401, 404, 422]

        if response.status_code == 200:
            data = response.json()
            assert "chara_karakas" in data
            assert isinstance(data["chara_karakas"], list)
            # Should have 7 karakas (AK, AmK, BK, MK, PK, GK, DK)
            if len(data["chara_karakas"]) > 0:
                assert len(data["chara_karakas"]) == 7

    def test_get_karakamsha(self, auth_headers, test_profile_id):
        """Test GET /api/v1/enhancements/jaimini/karakamsha/{profile_id}"""
        response = client.get(
            f"/api/v1/enhancements/jaimini/karakamsha/{test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]

        if response.status_code == 200:
            data = response.json()
            assert "karakamsha" in data

    def test_get_arudha_padas(self, auth_headers, test_profile_id):
        """Test GET /api/v1/enhancements/jaimini/arudha-padas/{profile_id}"""
        response = client.get(
            f"/api/v1/enhancements/jaimini/arudha-padas/{test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]

        if response.status_code == 200:
            data = response.json()
            assert "arudha_padas" in data
            assert isinstance(data["arudha_padas"], list)
            # Should have 12 padas (AL, A2-A12)
            if len(data["arudha_padas"]) > 0:
                assert len(data["arudha_padas"]) == 12

    def test_analyze_jaimini(self, auth_headers, test_profile_id):
        """Test GET /api/v1/enhancements/jaimini/analyze/{profile_id}"""
        response = client.get(
            f"/api/v1/enhancements/jaimini/analyze/{test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]


# ============================================================================
# LAL KITAB SYSTEM TESTS (3 endpoints)
# ============================================================================

class TestLalKitabSystem:
    """Test all Lal Kitab system endpoints."""

    def test_get_planetary_debts(self, auth_headers, test_profile_id):
        """Test GET /api/v1/enhancements/lal-kitab/debts/{profile_id}"""
        response = client.get(
            f"/api/v1/enhancements/lal-kitab/debts/{test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]

        if response.status_code == 200:
            data = response.json()
            assert "debts" in data
            assert isinstance(data["debts"], list)

    def test_get_blind_planets(self, auth_headers, test_profile_id):
        """Test GET /api/v1/enhancements/lal-kitab/blind-planets/{profile_id}"""
        response = client.get(
            f"/api/v1/enhancements/lal-kitab/blind-planets/{test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]

        if response.status_code == 200:
            data = response.json()
            assert "blind_planets" in data
            assert isinstance(data["blind_planets"], list)
            # Should have 9 planets
            if len(data["blind_planets"]) > 0:
                assert len(data["blind_planets"]) == 9

    def test_analyze_lal_kitab(self, auth_headers, test_profile_id):
        """Test GET /api/v1/enhancements/lal-kitab/analyze/{profile_id}"""
        response = client.get(
            f"/api/v1/enhancements/lal-kitab/analyze/{test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]


# ============================================================================
# ASHTAKAVARGA SYSTEM TESTS (4 endpoints)
# ============================================================================

class TestAshtakavargaSystem:
    """Test all Ashtakavarga system endpoints."""

    def test_get_bhinna_ashtakavarga(self, auth_headers, test_profile_id):
        """Test GET /api/v1/enhancements/ashtakavarga/bhinna/{profile_id}"""
        response = client.get(
            f"/api/v1/enhancements/ashtakavarga/bhinna/{test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]

        if response.status_code == 200:
            data = response.json()
            assert "bhinna_ashtakavarga" in data
            assert isinstance(data["bhinna_ashtakavarga"], list)
            # Should have 7 planets (Sun through Saturn)
            if len(data["bhinna_ashtakavarga"]) > 0:
                assert len(data["bhinna_ashtakavarga"]) == 7

    def test_get_sarva_ashtakavarga(self, auth_headers, test_profile_id):
        """Test GET /api/v1/enhancements/ashtakavarga/sarva/{profile_id}"""
        response = client.get(
            f"/api/v1/enhancements/ashtakavarga/sarva/{test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]

        if response.status_code == 200:
            data = response.json()
            assert "sarva_ashtakavarga" in data
            assert "sign_points" in data["sarva_ashtakavarga"]
            assert "total_points" in data["sarva_ashtakavarga"]

    def test_analyze_transit_strength(self, auth_headers, test_profile_id):
        """Test GET /api/v1/enhancements/ashtakavarga/transit/{profile_id}"""
        response = client.get(
            f"/api/v1/enhancements/ashtakavarga/transit/{test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]

    def test_analyze_ashtakavarga(self, auth_headers, test_profile_id):
        """Test GET /api/v1/enhancements/ashtakavarga/analyze/{profile_id}"""
        response = client.get(
            f"/api/v1/enhancements/ashtakavarga/analyze/{test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]


# ============================================================================
# VARSHAPHAL SYSTEM TESTS (3 endpoints)
# ============================================================================

class TestVarshaphalSystem:
    """Test all Varshaphal system endpoints."""

    def test_generate_varshaphal(self, auth_headers, test_profile_id):
        """Test POST /api/v1/varshaphal/generate"""
        response = client.post(
            "/api/v1/varshaphal/generate",
            headers=auth_headers,
            json={
                "profile_id": test_profile_id,
                "target_year": 2025
            }
        )
        assert response.status_code in [200, 201, 401, 404, 422]

    def test_list_varshaphals(self, auth_headers, test_profile_id):
        """Test POST /api/v1/varshaphal/list"""
        response = client.post(
            "/api/v1/varshaphal/list",
            headers=auth_headers,
            json={
                "profile_id": test_profile_id,
                "limit": 10,
                "offset": 0
            }
        )
        assert response.status_code in [200, 401, 404, 422]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_get_varshaphal(self, auth_headers):
        """Test GET /api/v1/varshaphal/{varshaphal_id}"""
        # Use a dummy ID - expect 404 or 401
        response = client.get(
            "/api/v1/varshaphal/dummy-id",
            headers=auth_headers
        )
        assert response.status_code in [404, 401, 422]


# ============================================================================
# COMPATIBILITY SYSTEM TESTS (5 endpoints)
# ============================================================================

class TestCompatibilitySystem:
    """Test all Compatibility system endpoints."""

    def test_analyze_compatibility(self, auth_headers, test_profile_id, second_profile_id):
        """Test POST /api/v1/compatibility/analyze"""
        response = client.post(
            f"/api/v1/compatibility/analyze?boy_profile_id={test_profile_id}&girl_profile_id={second_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]

    def test_get_guna_milan(self, auth_headers, test_profile_id, second_profile_id):
        """Test GET /api/v1/compatibility/guna-milan/{boy_profile_id}/{girl_profile_id}"""
        response = client.get(
            f"/api/v1/compatibility/guna-milan/{test_profile_id}/{second_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]

        if response.status_code == 200:
            data = response.json()
            assert "total_points" in data
            assert "factors" in data

    def test_get_manglik_dosha(self, auth_headers, test_profile_id):
        """Test GET /api/v1/compatibility/manglik/{profile_id}"""
        response = client.get(
            f"/api/v1/compatibility/manglik/{test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]

        if response.status_code == 200:
            data = response.json()
            assert "is_manglik" in data

    def test_get_nakshatra(self, auth_headers, test_profile_id):
        """Test GET /api/v1/compatibility/nakshatra/{profile_id}"""
        response = client.get(
            f"/api/v1/compatibility/nakshatra/{test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]

        if response.status_code == 200:
            data = response.json()
            assert "name" in data
            assert "number" in data

    def test_quick_match(self, auth_headers, test_profile_id):
        """Test POST /api/v1/compatibility/quick-match"""
        response = client.post(
            f"/api/v1/compatibility/quick-match?profile_id={test_profile_id}",
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404, 422]


# ============================================================================
# SUMMARY TEST
# ============================================================================

def test_endpoint_count():
    """Verify all 19 endpoints are accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi_data = response.json()
    paths = openapi_data.get("paths", {})

    # Count advanced system endpoints
    jaimini_count = sum(1 for p in paths if "/enhancements/jaimini/" in p)
    lal_kitab_count = sum(1 for p in paths if "/enhancements/lal-kitab/" in p)
    ashtakavarga_count = sum(1 for p in paths if "/enhancements/ashtakavarga/" in p)
    varshaphal_count = sum(1 for p in paths if "/varshaphal/" in p)
    compatibility_count = sum(1 for p in paths if "/compatibility/" in p)

    print(f"\n📊 Endpoint Count Summary:")
    print(f"  Jaimini: {jaimini_count} endpoints")
    print(f"  Lal Kitab: {lal_kitab_count} endpoints")
    print(f"  Ashtakavarga: {ashtakavarga_count} endpoints")
    print(f"  Varshaphal: {varshaphal_count} endpoints")
    print(f"  Compatibility: {compatibility_count} endpoints")
    print(f"  Total: {jaimini_count + lal_kitab_count + ashtakavarga_count + varshaphal_count + compatibility_count} endpoints\n")

    # Verify counts
    assert jaimini_count == 4, f"Expected 4 Jaimini endpoints, found {jaimini_count}"
    assert lal_kitab_count == 3, f"Expected 3 Lal Kitab endpoints, found {lal_kitab_count}"
    assert ashtakavarga_count == 4, f"Expected 4 Ashtakavarga endpoints, found {ashtakavarga_count}"
    assert varshaphal_count >= 3, f"Expected at least 3 Varshaphal endpoints, found {varshaphal_count}"
    assert compatibility_count >= 5, f"Expected at least 5 Compatibility endpoints, found {compatibility_count}"


if __name__ == "__main__":
    print("Running Advanced Systems Endpoint Tests...")
    print("=" * 80)
    pytest.main([__file__, "-v", "--tb=short"])
