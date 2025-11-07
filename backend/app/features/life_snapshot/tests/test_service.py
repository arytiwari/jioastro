"""
Unit tests for Life Snapshot service.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.features.life_snapshot.service import LifeSnapshotService
from app.features.life_snapshot import constants


@pytest.fixture
def service():
    """Create service instance."""
    return LifeSnapshotService()


def test_service_initialization(service):
    """Test service initializes correctly."""
    service.initialize()
    assert service._initialized is True


def test_cache_key_generation(service):
    """Test cache key generation."""
    user_id = str(uuid4())
    profile_id = str(uuid4())
    timestamp = datetime.now(timezone.utc)

    key1 = service._generate_cache_key(user_id, profile_id, timestamp)
    key2 = service._generate_cache_key(user_id, profile_id, timestamp)

    assert key1 == key2  # Same inputs should generate same key
    assert len(key1) == 64  # SHA256 produces 64 hex characters


def test_cache_key_different_dates(service):
    """Test cache keys differ across dates."""
    user_id = str(uuid4())
    profile_id = str(uuid4())

    today = datetime.now(timezone.utc)
    tomorrow = today + timedelta(days=1)

    key_today = service._generate_cache_key(user_id, profile_id, today)
    key_tomorrow = service._generate_cache_key(user_id, profile_id, tomorrow)

    assert key_today != key_tomorrow  # Different dates should generate different keys


def test_life_phase_determination(service):
    """Test life phase determination."""
    chart_data = {"yogas": ["Raj Yoga"], "current_dasha": {"mahadasha": "Jupiter"}}
    transits = {"jupiter": {"house_from_moon": 5}}

    phase = service._determine_life_phase(chart_data, transits)

    assert phase in [
        constants.LIFE_PHASE_GROWTH,
        constants.LIFE_PHASE_CONSOLIDATION,
        constants.LIFE_PHASE_TRANSFORMATION,
        constants.LIFE_PHASE_STABILITY,
        constants.LIFE_PHASE_CHALLENGE
    ]


def test_constants_configuration():
    """Test that constants are properly configured."""
    assert constants.FEATURE_NAME == "life_snapshot"
    assert constants.FEATURE_VERSION == "1.0.0"
    assert constants.TOP_THEMES_COUNT == 3
    assert constants.RISKS_COUNT == 3
    assert constants.OPPORTUNITIES_COUNT == 3
    assert constants.ACTIONS_COUNT == 3
    assert constants.ESTIMATED_READ_TIME_SECONDS == 60
    assert constants.SNAPSHOT_CACHE_TTL_SECONDS == 3600


# Integration tests (require database)
# These would normally use pytest-asyncio and mock database

# @pytest.mark.asyncio
# async def test_generate_snapshot(service, mock_db, mock_profile):
#     """Test snapshot generation."""
#     user_id = str(uuid4())
#     profile_id = str(uuid4())
#
#     result = await service.generate_snapshot(
#         db=mock_db,
#         user_id=user_id,
#         profile_id=profile_id,
#         force_refresh=False
#     )
#
#     assert result is not None
#     assert "snapshot_id" in result
#     assert "insights" in result
#     assert len(result["insights"]["top_themes"]) <= constants.TOP_THEMES_COUNT


# @pytest.mark.asyncio
# async def test_cached_snapshot_retrieval(service, mock_db, mock_profile):
#     """Test that cached snapshots are reused."""
#     user_id = str(uuid4())
#     profile_id = str(uuid4())
#
#     # Generate first snapshot
#     result1 = await service.generate_snapshot(
#         db=mock_db,
#         user_id=user_id,
#         profile_id=profile_id,
#         force_refresh=False
#     )
#
#     # Get snapshot again (should use cache)
#     result2 = await service.generate_snapshot(
#         db=mock_db,
#         user_id=user_id,
#         profile_id=profile_id,
#         force_refresh=False
#     )
#
#     assert result1["snapshot_id"] == result2["snapshot_id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
