"""
Pytest configuration and fixtures for JioAstro backend tests
"""
import pytest
from typing import Dict, Any
from httpx import AsyncClient
from unittest.mock import MagicMock, AsyncMock
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_d1_planets() -> Dict[str, Any]:
    """
    Sample D1 (Rashi) planetary positions for testing
    Based on a typical birth chart with various planetary placements
    """
    return {
        "Sun": {
            "house": 1,
            "sign": "Aries",
            "sign_num": 1,
            "degree": 15.5,
            "abs_degree": 15.5,
            "is_retrograde": False,
            "is_combust": False
        },
        "Moon": {
            "house": 4,
            "sign": "Cancer",
            "sign_num": 4,
            "degree": 22.3,
            "abs_degree": 112.3,
            "is_retrograde": False,
            "is_combust": False
        },
        "Mars": {
            "house": 8,
            "sign": "Scorpio",
            "sign_num": 8,
            "degree": 10.2,
            "abs_degree": 220.2,
            "is_retrograde": False,
            "is_combust": False
        },
        "Mercury": {
            "house": 12,
            "sign": "Pisces",
            "sign_num": 12,
            "degree": 5.8,
            "abs_degree": 335.8,
            "is_retrograde": False,
            "is_combust": False
        },
        "Jupiter": {
            "house": 10,
            "sign": "Capricorn",
            "sign_num": 10,
            "degree": 18.9,
            "abs_degree": 288.9,
            "is_retrograde": False,
            "is_combust": False
        },
        "Venus": {
            "house": 2,
            "sign": "Taurus",
            "sign_num": 2,
            "degree": 28.1,
            "abs_degree": 58.1,
            "is_retrograde": False,
            "is_combust": False
        },
        "Saturn": {
            "house": 7,
            "sign": "Libra",
            "sign_num": 7,
            "degree": 12.4,
            "abs_degree": 192.4,
            "is_retrograde": False,
            "is_combust": False
        },
        "Rahu": {
            "house": 3,
            "sign": "Gemini",
            "sign_num": 3,
            "degree": 8.7,
            "abs_degree": 68.7,
            "is_retrograde": True
        },
        "Ketu": {
            "house": 9,
            "sign": "Sagittarius",
            "sign_num": 9,
            "degree": 8.7,
            "abs_degree": 248.7,
            "is_retrograde": True
        }
    }


@pytest.fixture
def sample_d9_planets() -> Dict[str, Any]:
    """
    Sample D9 (Navamsa) planetary positions for testing
    """
    return {
        "Sun": {
            "house": 5,
            "sign": "Leo",
            "sign_num": 5,
            "is_retrograde": False
        },
        "Moon": {
            "house": 1,
            "sign": "Aries",
            "sign_num": 1,
            "is_retrograde": False
        },
        "Mars": {
            "house": 8,
            "sign": "Scorpio",
            "sign_num": 8,
            "is_retrograde": False
        },
        "Mercury": {
            "house": 6,
            "sign": "Virgo",
            "sign_num": 6,
            "is_retrograde": False
        },
        "Jupiter": {
            "house": 9,
            "sign": "Sagittarius",
            "sign_num": 9,
            "is_retrograde": False
        },
        "Venus": {
            "house": 7,
            "sign": "Libra",
            "sign_num": 7,
            "is_retrograde": False
        },
        "Saturn": {
            "house": 10,
            "sign": "Capricorn",
            "sign_num": 10,
            "is_retrograde": False
        },
        "Rahu": {
            "house": 11,
            "sign": "Aquarius",
            "sign_num": 11,
            "is_retrograde": True
        },
        "Ketu": {
            "house": 5,
            "sign": "Leo",
            "sign_num": 5,
            "is_retrograde": True
        }
    }


@pytest.fixture
def manglik_chart_high_intensity() -> Dict[str, Any]:
    """
    Chart with high Manglik Dosha intensity
    Mars in 8th house (very high intensity position)
    """
    return {
        "Sun": {"house": 5, "sign": "Leo", "sign_num": 5, "abs_degree": 135.0, "is_retrograde": False, "is_combust": False},
        "Moon": {"house": 2, "sign": "Taurus", "sign_num": 2, "abs_degree": 45.0, "is_retrograde": False, "is_combust": False},
        "Mars": {"house": 8, "sign": "Scorpio", "sign_num": 8, "abs_degree": 225.0, "is_retrograde": False, "is_combust": False},
        "Mercury": {"house": 6, "sign": "Virgo", "sign_num": 6, "abs_degree": 165.0, "is_retrograde": False, "is_combust": False},
        "Jupiter": {"house": 3, "sign": "Gemini", "sign_num": 3, "abs_degree": 75.0, "is_retrograde": False, "is_combust": False},
        "Venus": {"house": 11, "sign": "Aquarius", "sign_num": 11, "abs_degree": 315.0, "is_retrograde": False, "is_combust": False},
        "Saturn": {"house": 9, "sign": "Sagittarius", "sign_num": 9, "abs_degree": 255.0, "is_retrograde": False, "is_combust": False},
        "Rahu": {"house": 12, "sign": "Pisces", "sign_num": 12, "abs_degree": 345.0, "is_retrograde": True},
        "Ketu": {"house": 6, "sign": "Virgo", "sign_num": 6, "abs_degree": 165.0, "is_retrograde": True}
    }


@pytest.fixture
def kaal_sarpa_full_chart() -> Dict[str, Any]:
    """
    Chart with Full Kaal Sarpa Yoga (all 7 planets between Rahu-Ketu)
    Rahu in 1st house, Ketu in 7th house
    """
    return {
        "Sun": {"house": 3, "sign": "Gemini", "sign_num": 3, "abs_degree": 75.0, "is_retrograde": False, "is_combust": False},
        "Moon": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": False, "is_combust": False},
        "Mars": {"house": 5, "sign": "Leo", "sign_num": 5, "abs_degree": 135.0, "is_retrograde": False, "is_combust": False},
        "Mercury": {"house": 2, "sign": "Taurus", "sign_num": 2, "abs_degree": 45.0, "is_retrograde": False, "is_combust": False},
        "Jupiter": {"house": 6, "sign": "Virgo", "sign_num": 6, "abs_degree": 165.0, "is_retrograde": False, "is_combust": False},
        "Venus": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 110.0, "is_retrograde": False, "is_combust": False},
        "Saturn": {"house": 3, "sign": "Gemini", "sign_num": 3, "abs_degree": 80.0, "is_retrograde": False, "is_combust": False},
        "Rahu": {"house": 1, "sign": "Aries", "sign_num": 1, "abs_degree": 10.0, "is_retrograde": True},
        "Ketu": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 190.0, "is_retrograde": True}
    }


@pytest.fixture
def pitra_dosha_high_chart() -> Dict[str, Any]:
    """
    Chart with high Pitra Dosha
    Sun-Rahu conjunction in 9th house (primary indicator)
    """
    return {
        "Sun": {"house": 9, "sign": "Sagittarius", "sign_num": 9, "abs_degree": 255.0, "is_retrograde": False, "is_combust": False},
        "Moon": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": False, "is_combust": False},
        "Mars": {"house": 2, "sign": "Taurus", "sign_num": 2, "abs_degree": 45.0, "is_retrograde": False, "is_combust": False},
        "Mercury": {"house": 10, "sign": "Capricorn", "sign_num": 10, "abs_degree": 285.0, "is_retrograde": False, "is_combust": False},
        "Jupiter": {"house": 5, "sign": "Leo", "sign_num": 5, "abs_degree": 135.0, "is_retrograde": False, "is_combust": False},
        "Venus": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 195.0, "is_retrograde": False, "is_combust": False},
        "Saturn": {"house": 9, "sign": "Sagittarius", "sign_num": 9, "abs_degree": 260.0, "is_retrograde": False, "is_combust": False},
        "Rahu": {"house": 9, "sign": "Sagittarius", "sign_num": 9, "abs_degree": 258.0, "is_retrograde": True},
        "Ketu": {"house": 3, "sign": "Gemini", "sign_num": 3, "abs_degree": 78.0, "is_retrograde": True}
    }


@pytest.fixture
def grahan_dosha_moon_rahu_chart() -> Dict[str, Any]:
    """
    Chart with Grahan Dosha - Moon-Rahu conjunction (very close)
    """
    return {
        "Sun": {"house": 10, "sign": "Capricorn", "sign_num": 10, "abs_degree": 285.0, "is_retrograde": False, "is_combust": False},
        "Moon": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": False, "is_combust": False},
        "Mars": {"house": 2, "sign": "Taurus", "sign_num": 2, "abs_degree": 45.0, "is_retrograde": False, "is_combust": False},
        "Mercury": {"house": 11, "sign": "Aquarius", "sign_num": 11, "abs_degree": 315.0, "is_retrograde": False, "is_combust": False},
        "Jupiter": {"house": 1, "sign": "Aries", "sign_num": 1, "abs_degree": 15.0, "is_retrograde": False, "is_combust": False},
        "Venus": {"house": 9, "sign": "Sagittarius", "sign_num": 9, "abs_degree": 255.0, "is_retrograde": False, "is_combust": False},
        "Saturn": {"house": 8, "sign": "Scorpio", "sign_num": 8, "abs_degree": 225.0, "is_retrograde": False, "is_combust": False},
        "Rahu": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 107.5, "is_retrograde": True},
        "Ketu": {"house": 10, "sign": "Capricorn", "sign_num": 10, "abs_degree": 287.5, "is_retrograde": True}
    }


@pytest.fixture
def clean_chart() -> Dict[str, Any]:
    """
    Chart with minimal doshas - for testing absence of afflictions
    """
    return {
        "Sun": {"house": 5, "sign": "Leo", "sign_num": 5, "abs_degree": 135.0, "is_retrograde": False, "is_combust": False},
        "Moon": {"house": 4, "sign": "Cancer", "sign_num": 4, "abs_degree": 105.0, "is_retrograde": False, "is_combust": False},
        "Mars": {"house": 10, "sign": "Capricorn", "sign_num": 10, "abs_degree": 285.0, "is_retrograde": False, "is_combust": False},
        "Mercury": {"house": 6, "sign": "Virgo", "sign_num": 6, "abs_degree": 165.0, "is_retrograde": False, "is_combust": False},
        "Jupiter": {"house": 9, "sign": "Sagittarius", "sign_num": 9, "abs_degree": 255.0, "is_retrograde": False, "is_combust": False},
        "Venus": {"house": 7, "sign": "Libra", "sign_num": 7, "abs_degree": 195.0, "is_retrograde": False, "is_combust": False},
        "Saturn": {"house": 11, "sign": "Aquarius", "sign_num": 11, "abs_degree": 315.0, "is_retrograde": False, "is_combust": False},
        "Rahu": {"house": 2, "sign": "Taurus", "sign_num": 2, "abs_degree": 45.0, "is_retrograde": True},
        "Ketu": {"house": 8, "sign": "Scorpio", "sign_num": 8, "abs_degree": 225.0, "is_retrograde": True}
    }


# ============================================================================
# API Testing Fixtures
# ============================================================================

@pytest.fixture
async def async_client():
    """
    Async HTTP client for testing API endpoints
    """
    from main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_supabase_service():
    """
    Mock Supabase service for testing without database
    """
    mock = MagicMock()

    # Mock common methods
    mock.get_profile = AsyncMock(return_value=None)
    mock.get_chart = AsyncMock(return_value=None)
    mock.insert = AsyncMock(return_value={"id": "test-id"})
    mock.update = AsyncMock(return_value={"id": "test-id"})
    mock.delete = AsyncMock(return_value=True)
    mock.select = AsyncMock(return_value=[])

    return mock


@pytest.fixture
def sample_chart_data():
    """
    Sample chart data for testing
    """
    return {
        "planets": {
            "Sun": {"sign": "Aries", "house": 1, "degree": 15.5},
            "Moon": {"sign": "Cancer", "house": 4, "degree": 22.3},
            "Mars": {"sign": "Scorpio", "house": 8, "degree": 10.2},
            "Mercury": {"sign": "Pisces", "house": 12, "degree": 5.8},
            "Jupiter": {"sign": "Capricorn", "house": 10, "degree": 18.9},
            "Venus": {"sign": "Taurus", "house": 2, "degree": 28.1},
            "Saturn": {"sign": "Libra", "house": 7, "degree": 12.4}
        },
        "houses": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "ascendant": {"sign": "Aries", "degree": 5.0}
    }


@pytest.fixture
def performance_threshold():
    """
    Performance thresholds for API tests (in seconds)
    """
    return {
        "fast": 0.1,      # < 100ms
        "medium": 0.5,    # < 500ms
        "slow": 2.0       # < 2s
    }
