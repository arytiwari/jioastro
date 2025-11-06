"""
Pytest configuration and shared fixtures
Provides test data, mocks, and utilities for all tests
"""

import pytest
import asyncio
from typing import Dict, Any, Generator
from datetime import datetime, date, time
from unittest.mock import Mock, AsyncMock, patch
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Import app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from app.core.security import get_current_user


# ============================================================================
# Event Loop Fixture
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Client Fixtures
# ============================================================================

@pytest.fixture
def client():
    """Synchronous test client"""
    return TestClient(app)


@pytest.fixture
async def async_client(mock_current_user):
    """Asynchronous test client with authentication override"""
    # Override the get_current_user dependency
    async def override_get_current_user():
        return mock_current_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Clean up overrides after test
    app.dependency_overrides.clear()


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for testing"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyLTEyMyIsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSJ9.test"


@pytest.fixture
def auth_headers(mock_jwt_token):
    """Authentication headers with JWT token"""
    return {"Authorization": f"Bearer {mock_jwt_token}"}


@pytest.fixture
def mock_current_user():
    """Mock current user for dependency injection"""
    return {
        "user_id": "test-user-123",
        "email": "test@test.com",
        "aud": "authenticated"
    }


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_birth_data():
    """Sample birth data for testing"""
    return {
        "name": "Test User",
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "birth_city": "New Delhi",
        "birth_lat": 28.6139,
        "birth_lon": 77.2090,
        "birth_timezone": "Asia/Kolkata",
        "is_primary": True
    }


@pytest.fixture
def sample_chart_data():
    """Sample chart data for testing"""
    return {
        "planets": {
            "Sun": {"longitude": 45.5, "sign_num": 2, "sign": "Taurus", "house": 1, "retrograde": False},
            "Moon": {"longitude": 120.3, "sign_num": 4, "sign": "Cancer", "house": 3, "retrograde": False},
            "Mars": {"longitude": 200.7, "sign_num": 7, "sign": "Libra", "house": 6, "retrograde": False},
            "Mercury": {"longitude": 55.2, "sign_num": 2, "sign": "Taurus", "house": 1, "retrograde": False},
            "Jupiter": {"longitude": 95.8, "sign_num": 4, "sign": "Cancer", "house": 3, "retrograde": False},
            "Venus": {"longitude": 30.1, "sign_num": 1, "sign": "Aries", "house": 12, "retrograde": False},
            "Saturn": {"longitude": 280.4, "sign_num": 10, "sign": "Capricorn", "house": 9, "retrograde": False},
            "Rahu": {"longitude": 150.0, "sign_num": 5, "sign": "Leo", "house": 4, "retrograde": True},
            "Ketu": {"longitude": 330.0, "sign_num": 11, "sign": "Aquarius", "house": 10, "retrograde": True}
        },
        "houses": {
            "1": {"sign": "Aries", "sign_num": 1, "degree": 15.5},
            "2": {"sign": "Taurus", "sign_num": 2, "degree": 15.5},
            "3": {"sign": "Gemini", "sign_num": 3, "degree": 15.5},
            "4": {"sign": "Cancer", "sign_num": 4, "degree": 15.5},
            "5": {"sign": "Leo", "sign_num": 5, "degree": 15.5},
            "6": {"sign": "Virgo", "sign_num": 6, "degree": 15.5},
            "7": {"sign": "Libra", "sign_num": 7, "degree": 15.5},
            "8": {"sign": "Scorpio", "sign_num": 8, "degree": 15.5},
            "9": {"sign": "Sagittarius", "sign_num": 9, "degree": 15.5},
            "10": {"sign": "Capricorn", "sign_num": 10, "degree": 15.5},
            "11": {"sign": "Aquarius", "sign_num": 11, "degree": 15.5},
            "12": {"sign": "Pisces", "sign_num": 12, "degree": 15.5}
        },
        "ascendant": {"sign": "Aries", "sign_num": 1, "degree": 15.5}
    }


@pytest.fixture
def sample_profile_response():
    """Sample profile API response"""
    return {
        "id": "test-profile-123",
        "user_id": "test-user-123",
        "name": "Test User",
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "birth_city": "New Delhi",
        "birth_lat": 28.6139,
        "birth_lon": 77.2090,
        "birth_timezone": "Asia/Kolkata",
        "is_primary": True,
        "created_at": "2025-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_numerology_data():
    """Sample numerology calculation data"""
    return {
        "full_name": "John Doe",
        "birth_date": "1990-01-15",
        "system": "both"
    }


# ============================================================================
# Service Mocks
# ============================================================================

@pytest.fixture
def mock_supabase_service():
    """Mock Supabase service"""
    mock = AsyncMock()
    mock.get_profile.return_value = {
        "id": "test-profile-123",
        "user_id": "test-user-123",
        "name": "Test User",
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "birth_city": "New Delhi",
        "birth_lat": 28.6139,
        "birth_lon": 77.2090,
        "birth_timezone": "Asia/Kolkata"
    }
    mock.get_chart.return_value = {
        "chart_data": {"planets": {}, "houses": {}}
    }
    return mock


@pytest.fixture
def mock_openai_service():
    """Mock OpenAI service for AI tests"""
    mock = Mock()
    mock.generate_response.return_value = "This is a test AI response."
    return mock


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = AsyncMock()
    session.execute.return_value = Mock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def performance_threshold():
    """Performance thresholds for different operations"""
    return {
        "fast": 0.1,      # 100ms
        "medium": 0.5,    # 500ms
        "slow": 2.0,      # 2 seconds
        "very_slow": 5.0  # 5 seconds
    }


# ============================================================================
# Utility Functions
# ============================================================================

def assert_valid_uuid(value: str):
    """Assert that a string is a valid UUID"""
    import uuid
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        pytest.fail(f"'{value}' is not a valid UUID")


def assert_valid_datetime(value: str):
    """Assert that a string is a valid ISO datetime"""
    try:
        datetime.fromisoformat(value.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError):
        pytest.fail(f"'{value}' is not a valid ISO datetime")


def assert_response_structure(response: Dict[str, Any], required_fields: list):
    """Assert that response contains all required fields"""
    for field in required_fields:
        assert field in response, f"Missing required field: {field}"


# Make utility functions available to all tests
pytest.assert_valid_uuid = assert_valid_uuid
pytest.assert_valid_datetime = assert_valid_datetime
pytest.assert_response_structure = assert_response_structure
