"""
Comprehensive tests for gender field functionality across profiles and instant onboarding.

Tests cover:
- Schema validation (ProfileCreate, ProfileUpdate, QuickChartRequest)
- Profile creation with gender field
- Instant onboarding with gender field
- API integration tests
- Edge cases and validation
"""

import pytest
from datetime import date, time
from pydantic import ValidationError
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.features.instant_onboarding.schemas import QuickChartRequest


# ============================================================================
# Schema Validation Tests
# ============================================================================

class TestProfileSchemaGenderValidation:
    """Test gender field validation in Profile schemas"""

    def test_profile_create_with_valid_gender_male(self):
        """Test creating profile with gender='male'"""
        profile_data = {
            "name": "John Doe",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "birth_city": "New Delhi",
            "birth_timezone": "Asia/Kolkata",
            "gender": "male",
            "is_primary": False
        }

        profile = ProfileCreate(**profile_data)
        assert profile.gender == "male"

    def test_profile_create_with_valid_gender_female(self):
        """Test creating profile with gender='female'"""
        profile_data = {
            "name": "Jane Doe",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": "female"
        }

        profile = ProfileCreate(**profile_data)
        assert profile.gender == "female"

    def test_profile_create_with_valid_gender_other(self):
        """Test creating profile with gender='other'"""
        profile_data = {
            "name": "Alex Doe",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": "other"
        }

        profile = ProfileCreate(**profile_data)
        assert profile.gender == "other"

    def test_profile_create_without_gender(self):
        """Test creating profile without gender field (should be None)"""
        profile_data = {
            "name": "Anonymous User",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
        }

        profile = ProfileCreate(**profile_data)
        assert profile.gender is None

    def test_profile_create_with_none_gender(self):
        """Test creating profile with gender=None"""
        profile_data = {
            "name": "Test User",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": None
        }

        profile = ProfileCreate(**profile_data)
        assert profile.gender is None

    def test_profile_create_with_invalid_gender(self):
        """Test creating profile with invalid gender value should raise error"""
        profile_data = {
            "name": "Test User",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": "invalid"
        }

        with pytest.raises(ValidationError) as exc_info:
            ProfileCreate(**profile_data)

        # Check that error is related to gender field
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('gender',) for error in errors)

    def test_profile_create_gender_case_sensitivity(self):
        """Test that gender values are case-sensitive"""
        profile_data = {
            "name": "Test User",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": "MALE"  # Uppercase should fail
        }

        with pytest.raises(ValidationError):
            ProfileCreate(**profile_data)

    def test_profile_update_with_gender(self):
        """Test updating profile with gender field"""
        update_data = {
            "name": "Updated Name",
            "gender": "female"
        }

        update = ProfileUpdate(**update_data)
        assert update.gender == "female"
        assert update.name == "Updated Name"

    def test_profile_update_only_gender(self):
        """Test updating only gender field"""
        update_data = {
            "gender": "other"
        }

        update = ProfileUpdate(**update_data)
        assert update.gender == "other"
        assert update.name is None  # Other fields should be None

    def test_profile_update_clear_gender(self):
        """Test clearing gender field in update"""
        update_data = {
            "gender": None
        }

        update = ProfileUpdate(**update_data)
        assert update.gender is None


class TestInstantOnboardingSchemaGenderValidation:
    """Test gender field validation in Instant Onboarding schemas"""

    def test_quick_chart_request_with_gender_male(self):
        """Test quick chart request with gender='male'"""
        request_data = {
            "name": "John Doe",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone": "Asia/Kolkata",
            "gender": "male"
        }

        request = QuickChartRequest(**request_data)
        assert request.gender == "male"

    def test_quick_chart_request_with_gender_female(self):
        """Test quick chart request with gender='female'"""
        request_data = {
            "name": "Jane Doe",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "latitude": 28.6139,
            "longitude": 77.2090,
            "gender": "female"
        }

        request = QuickChartRequest(**request_data)
        assert request.gender == "female"

    def test_quick_chart_request_without_gender(self):
        """Test quick chart request without gender (optional)"""
        request_data = {
            "name": "Anonymous User",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "latitude": 28.6139,
            "longitude": 77.2090,
        }

        request = QuickChartRequest(**request_data)
        assert request.gender is None

    def test_quick_chart_request_with_invalid_gender(self):
        """Test quick chart request with invalid gender should raise error"""
        request_data = {
            "name": "Test User",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "latitude": 28.6139,
            "longitude": 77.2090,
            "gender": "unknown"  # Invalid value
        }

        with pytest.raises(ValidationError) as exc_info:
            QuickChartRequest(**request_data)

        errors = exc_info.value.errors()
        assert any(error['loc'] == ('gender',) for error in errors)

    def test_quick_chart_request_with_session_key_and_gender(self):
        """Test using session_key with additional gender field"""
        request_data = {
            "session_key": "test-session-123",
            "gender": "other"  # Can still provide gender with session
        }

        request = QuickChartRequest(**request_data)
        assert request.session_key == "test-session-123"
        assert request.gender == "other"


# ============================================================================
# Data Serialization Tests
# ============================================================================

class TestGenderFieldSerialization:
    """Test that gender field serializes correctly"""

    def test_profile_dict_serialization_with_gender(self):
        """Test that gender field appears in dict output"""
        profile_data = {
            "name": "John Doe",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": "male"
        }

        profile = ProfileCreate(**profile_data)
        profile_dict = profile.model_dump()

        assert "gender" in profile_dict
        assert profile_dict["gender"] == "male"

    def test_profile_dict_serialization_without_gender(self):
        """Test that gender field appears as None when not provided"""
        profile_data = {
            "name": "John Doe",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
        }

        profile = ProfileCreate(**profile_data)
        profile_dict = profile.model_dump()

        assert "gender" in profile_dict
        assert profile_dict["gender"] is None

    def test_profile_json_serialization_with_gender(self):
        """Test JSON serialization includes gender"""
        profile_data = {
            "name": "Jane Doe",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": "female"
        }

        profile = ProfileCreate(**profile_data)
        json_str = profile.model_dump_json()

        assert '"gender":"female"' in json_str or '"gender": "female"' in json_str


# ============================================================================
# Edge Cases and Boundary Tests
# ============================================================================

class TestGenderFieldEdgeCases:
    """Test edge cases for gender field"""

    def test_gender_with_whitespace(self):
        """Test that gender with whitespace is rejected"""
        profile_data = {
            "name": "Test User",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": " male "  # With whitespace
        }

        with pytest.raises(ValidationError):
            ProfileCreate(**profile_data)

    def test_gender_empty_string(self):
        """Test that empty string for gender is rejected"""
        profile_data = {
            "name": "Test User",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": ""  # Empty string
        }

        with pytest.raises(ValidationError):
            ProfileCreate(**profile_data)

    def test_gender_numeric_value(self):
        """Test that numeric values are rejected"""
        profile_data = {
            "name": "Test User",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "gender": 1  # Numeric
        }

        with pytest.raises(ValidationError):
            ProfileCreate(**profile_data)

    def test_all_valid_gender_combinations(self):
        """Test all valid gender values work correctly"""
        valid_genders = ["male", "female", "other", None]

        for gender_value in valid_genders:
            profile_data = {
                "name": f"Test User {gender_value}",
                "birth_date": date(1990, 1, 15),
                "birth_time": time(14, 30),
                "birth_lat": 28.6139,
                "birth_lon": 77.2090,
                "gender": gender_value
            }

            profile = ProfileCreate(**profile_data)
            assert profile.gender == gender_value


# ============================================================================
# Compatibility Tests
# ============================================================================

class TestBackwardCompatibility:
    """Test that existing code without gender still works"""

    def test_profile_creation_without_gender_field_in_data(self):
        """Test that profiles can be created without gender key in data dict"""
        profile_data = {
            "name": "Legacy User",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
            "birth_city": "Mumbai",
            "birth_timezone": "Asia/Kolkata",
            "is_primary": True
        }
        # Note: no 'gender' key at all

        profile = ProfileCreate(**profile_data)
        assert profile.name == "Legacy User"
        assert profile.gender is None  # Should default to None
        assert profile.is_primary is True

    def test_minimal_profile_creation(self):
        """Test minimal profile with only required fields"""
        profile_data = {
            "name": "Minimal User",
            "birth_date": date(1990, 1, 15),
            "birth_time": time(14, 30),
            "birth_lat": 28.6139,
            "birth_lon": 77.2090,
        }

        profile = ProfileCreate(**profile_data)
        assert profile.name == "Minimal User"
        assert profile.gender is None
        assert profile.birth_city is None
        assert profile.birth_timezone is None

    def test_profile_update_without_gender(self):
        """Test profile update works without gender field"""
        update_data = {
            "name": "Updated Name Only"
        }

        update = ProfileUpdate(**update_data)
        assert update.name == "Updated Name Only"
        assert update.gender is None
        assert update.is_primary is None


# ============================================================================
# Documentation Tests
# ============================================================================

class TestSchemaDocumentation:
    """Test that schema documentation is correct"""

    def test_profile_create_has_gender_field_description(self):
        """Test that ProfileCreate schema has gender field with description"""
        schema = ProfileCreate.model_json_schema()

        # Check that gender field exists in schema
        assert "gender" in schema.get("properties", {})

        # Check that it has a description
        gender_field = schema["properties"]["gender"]
        assert "description" in gender_field

    def test_gender_field_is_optional(self):
        """Test that gender is not in required fields"""
        schema = ProfileCreate.model_json_schema()

        # Gender should not be in required fields
        required_fields = schema.get("required", [])
        assert "gender" not in required_fields

    def test_gender_field_has_enum_values(self):
        """Test that gender field shows valid values in schema"""
        schema = ProfileCreate.model_json_schema()

        # Check that gender has enum or anyOf with valid values
        gender_field = schema["properties"]["gender"]

        # Should have enum values or anyOf structure
        assert "anyOf" in gender_field or "enum" in gender_field


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
