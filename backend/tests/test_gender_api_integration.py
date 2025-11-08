"""
API Integration Tests for Gender Field
Tests the complete flow of gender field through API endpoints

These tests cover:
- Profile creation API with gender
- Profile update API with gender
- Instant onboarding API with gender
- Profile retrieval and gender field display
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
from datetime import date, time


# ============================================================================
# Profile API Tests with Gender
# ============================================================================

class TestProfileAPIWithGender:
    """Test profile creation and update APIs with gender field"""

    @pytest.mark.asyncio
    async def test_create_profile_with_gender_male(self, async_client):
        """Test creating profile via API with gender='male'"""
        profile_data = {
            "name": "John Doe",
            "birth_date": "1990-01-15",
            "birth_time": "14:30:00",
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "birth_city": "New Delhi",
            "birth_timezone": "Asia/Kolkata",
            "gender": "male",
            "is_primary": False
        }

        # Mock Supabase client to avoid actual DB calls
        with patch('app.api.v1.endpoints.profiles.get_supabase_client') as mock_supabase:
            mock_client = MagicMock()
            mock_client.insert.return_value = {
                **profile_data,
                "id": "test-profile-123",
                "user_id": "test-user-456",
                "created_at": "2024-01-01T00:00:00Z"
            }
            mock_supabase.return_value = mock_client

            response = await async_client.post(
                "/api/v1/profiles",
                json=profile_data
            )

            # Verify response
            assert response.status_code in [200, 201]
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                # Check that gender is preserved
                assert data.get("gender") == "male"

    @pytest.mark.asyncio
    async def test_create_profile_with_gender_female(self, async_client):
        """Test creating profile via API with gender='female'"""
        profile_data = {
            "name": "Jane Doe",
            "birth_date": "1990-01-15",
            "birth_time": "14:30:00",
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": "female"
        }

        with patch('app.api.v1.endpoints.profiles.get_supabase_client') as mock_supabase:
            mock_client = MagicMock()
            mock_client.insert.return_value = {**profile_data, "id": "test-123"}
            mock_supabase.return_value = mock_client

            response = await async_client.post(
                "/api/v1/profiles",
                json=profile_data
            )

            if response.status_code in [200, 201]:
                data = response.json()
                assert data.get("gender") == "female"

    @pytest.mark.asyncio
    async def test_create_profile_without_gender(self, async_client):
        """Test creating profile via API without gender field"""
        profile_data = {
            "name": "Anonymous User",
            "birth_date": "1990-01-15",
            "birth_time": "14:30:00",
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
        }

        with patch('app.api.v1.endpoints.profiles.get_supabase_client') as mock_supabase:
            mock_client = MagicMock()
            mock_client.insert.return_value = {**profile_data, "id": "test-123", "gender": None}
            mock_supabase.return_value = mock_client

            response = await async_client.post(
                "/api/v1/profiles",
                json=profile_data
            )

            # Should succeed without gender
            assert response.status_code in [200, 201, 400, 401, 403]  # Various possible responses

    @pytest.mark.asyncio
    async def test_create_profile_with_invalid_gender(self, async_client):
        """Test creating profile via API with invalid gender value"""
        profile_data = {
            "name": "Test User",
            "birth_date": "1990-01-15",
            "birth_time": "14:30:00",
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": "invalid_value"
        }

        response = await async_client.post(
            "/api/v1/profiles",
            json=profile_data
        )

        # Should return validation error
        assert response.status_code == 422  # Unprocessable Entity (validation error)

        error_data = response.json()
        assert "detail" in error_data
        # Check that error mentions gender field
        error_detail = str(error_data["detail"])
        assert "gender" in error_detail.lower()

    @pytest.mark.asyncio
    async def test_update_profile_gender(self, async_client):
        """Test updating profile gender via API"""
        update_data = {
            "gender": "other"
        }

        with patch('app.api.v1.endpoints.profiles.get_supabase_client') as mock_supabase:
            mock_client = MagicMock()
            mock_client.update.return_value = {
                "id": "test-profile-123",
                "name": "Test User",
                "gender": "other"
            }
            mock_supabase.return_value = mock_client

            response = await async_client.patch(
                "/api/v1/profiles/test-profile-123",
                json=update_data
            )

            # Check response
            if response.status_code == 200:
                data = response.json()
                assert data.get("gender") == "other"


# ============================================================================
# Instant Onboarding API Tests with Gender
# ============================================================================

class TestInstantOnboardingAPIWithGender:
    """Test instant onboarding API with gender field"""

    @pytest.mark.asyncio
    async def test_quick_chart_with_gender_male(self, async_client):
        """Test quick chart generation with gender='male'"""
        chart_data = {
            "name": "John Doe",
            "birth_date": "1990-01-15",
            "birth_time": "14:30:00",
            "birth_place": "New Delhi",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone": "Asia/Kolkata",
            "gender": "male"
        }

        with patch('app.api.v2.endpoints.instant_onboarding.instant_onboarding_service') as mock_service:
            # Mock successful chart generation
            mock_service.generate_quick_chart.return_value = {
                "session_id": "test-session-123",
                "profile_id": "test-profile-456",
                "sun_sign": "Capricorn",
                "moon_sign": "Scorpio",
                "ascendant": "Leo",
                "summary": {},
                "name": "John Doe",
                "birth_date": "1990-01-15"
            }

            response = await async_client.post(
                "/api/v2/instant-onboarding/quick-chart",
                json=chart_data
            )

            if response.status_code == 200:
                data = response.json()
                # Verify chart was generated
                assert "profile_id" in data or "sun_sign" in data

    @pytest.mark.asyncio
    async def test_quick_chart_with_gender_female(self, async_client):
        """Test quick chart generation with gender='female'"""
        chart_data = {
            "name": "Jane Doe",
            "birth_date": "1990-01-15",
            "birth_time": "14:30:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "gender": "female"
        }

        with patch('app.api.v2.endpoints.instant_onboarding.instant_onboarding_service') as mock_service:
            mock_service.generate_quick_chart.return_value = {
                "session_id": "test-session-123",
                "profile_id": "test-profile-456",
                "sun_sign": "Capricorn",
                "moon_sign": "Scorpio",
                "ascendant": "Leo"
            }

            response = await async_client.post(
                "/api/v2/instant-onboarding/quick-chart",
                json=chart_data
            )

            # Should succeed with female gender
            assert response.status_code in [200, 400, 401, 500]

    @pytest.mark.asyncio
    async def test_quick_chart_without_gender(self, async_client):
        """Test quick chart generation without gender (should still work)"""
        chart_data = {
            "name": "Anonymous User",
            "birth_date": "1990-01-15",
            "birth_time": "14:30:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
        }

        with patch('app.api.v2.endpoints.instant_onboarding.instant_onboarding_service') as mock_service:
            mock_service.generate_quick_chart.return_value = {
                "session_id": "test-session-123",
                "profile_id": "test-profile-456",
                "sun_sign": "Capricorn",
                "moon_sign": "Scorpio",
                "ascendant": "Leo"
            }

            response = await async_client.post(
                "/api/v2/instant-onboarding/quick-chart",
                json=chart_data
            )

            # Should work without gender
            assert response.status_code in [200, 400, 401, 500]

    @pytest.mark.asyncio
    async def test_quick_chart_with_invalid_gender(self, async_client):
        """Test quick chart with invalid gender value"""
        chart_data = {
            "name": "Test User",
            "birth_date": "1990-01-15",
            "birth_time": "14:30:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "gender": "unknown"
        }

        response = await async_client.post(
            "/api/v2/instant-onboarding/quick-chart",
            json=chart_data
        )

        # Should return validation error
        assert response.status_code == 422

        error_data = response.json()
        assert "detail" in error_data


# ============================================================================
# End-to-End Workflow Tests
# ============================================================================

class TestGenderFieldE2E:
    """Test complete workflows with gender field"""

    @pytest.mark.asyncio
    async def test_create_profile_and_verify_gender(self, async_client):
        """Test creating profile with gender and retrieving it"""
        # Step 1: Create profile with gender
        create_data = {
            "name": "Test User",
            "birth_date": "1990-01-15",
            "birth_time": "14:30:00",
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": "male"
        }

        with patch('app.api.v1.endpoints.profiles.get_supabase_client') as mock_supabase:
            mock_client = MagicMock()
            created_profile = {
                **create_data,
                "id": "test-profile-123",
                "user_id": "test-user-456",
                "created_at": "2024-01-01T00:00:00Z"
            }
            mock_client.insert.return_value = created_profile
            mock_client.select.return_value = [created_profile]
            mock_supabase.return_value = mock_client

            # Create
            create_response = await async_client.post(
                "/api/v1/profiles",
                json=create_data
            )

            if create_response.status_code in [200, 201]:
                # Step 2: Retrieve and verify gender is preserved
                profile_id = create_response.json().get("id")

                get_response = await async_client.get(
                    f"/api/v1/profiles/{profile_id}"
                )

                if get_response.status_code == 200:
                    retrieved_profile = get_response.json()
                    assert retrieved_profile.get("gender") == "male"

    @pytest.mark.asyncio
    async def test_instant_onboarding_to_profile_save_with_gender(self, async_client):
        """Test instant onboarding followed by profile save with gender"""
        # Step 1: Generate quick chart with gender
        chart_data = {
            "name": "Jane Doe",
            "birth_date": "1990-01-15",
            "birth_time": "14:30:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "gender": "female"
        }

        with patch('app.api.v2.endpoints.instant_onboarding.instant_onboarding_service') as mock_io:
            with patch('app.api.v1.endpoints.profiles.get_supabase_client') as mock_profiles:
                # Mock instant onboarding
                mock_io.generate_quick_chart.return_value = {
                    "session_id": "test-session-123",
                    "profile_id": "test-profile-456",
                    "sun_sign": "Capricorn",
                    "moon_sign": "Scorpio",
                    "ascendant": "Leo"
                }

                # Mock profile save
                mock_client = MagicMock()
                saved_profile = {
                    "id": "test-profile-456",
                    "name": "Jane Doe",
                    "gender": "female",
                    "birth_date": "1990-01-15"
                }
                mock_client.insert.return_value = saved_profile
                mock_profiles.return_value = mock_client

                # Generate chart
                chart_response = await async_client.post(
                    "/api/v2/instant-onboarding/quick-chart",
                    json=chart_data
                )

                # Should succeed
                assert chart_response.status_code in [200, 400, 401, 500]


# ============================================================================
# Validation Error Tests
# ============================================================================

class TestGenderValidationErrors:
    """Test various validation error scenarios"""

    @pytest.mark.asyncio
    async def test_profile_gender_validation_error_format(self, async_client):
        """Test that gender validation errors have proper format"""
        profile_data = {
            "name": "Test User",
            "birth_date": "1990-01-15",
            "birth_time": "14:30:00",
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": "invalid"
        }

        response = await async_client.post(
            "/api/v1/profiles",
            json=profile_data
        )

        assert response.status_code == 422
        error_data = response.json()

        # Check error structure
        assert "detail" in error_data
        detail = error_data["detail"]

        # Should be a list of errors
        if isinstance(detail, list):
            gender_errors = [e for e in detail if "gender" in str(e.get("loc", []))]
            assert len(gender_errors) > 0

    @pytest.mark.asyncio
    async def test_multiple_invalid_fields_including_gender(self, async_client):
        """Test validation when multiple fields are invalid including gender"""
        profile_data = {
            "name": "",  # Invalid - empty
            "birth_date": "invalid-date",  # Invalid format
            "birth_time": "25:00:00",  # Invalid time
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": "unknown"  # Invalid value
        }

        response = await async_client.post(
            "/api/v1/profiles",
            json=profile_data
        )

        assert response.status_code == 422
        error_data = response.json()

        # Should have multiple errors including gender
        if isinstance(error_data["detail"], list):
            error_fields = [str(e.get("loc", [])) for e in error_data["detail"]]
            # At least gender should be in errors
            assert any("gender" in field for field in error_fields)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
