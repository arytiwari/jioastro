"""
Unit tests for Evidence Mode service.
"""

import pytest
from app.features.evidence_mode.service import EvidenceModeService


@pytest.fixture
def service():
    """Create service instance."""
    return EvidenceModeService()


def test_service_initialization(service):
    """Test service initializes correctly."""
    service.initialize()
    assert service._initialized is True


@pytest.mark.asyncio
async def test_process(service):
    """Test basic processing."""
    service.initialize()

    result = await service.process(
        user_id="test_user",
        profile_id="test_profile",
        data={"test": "data"}
    )

    assert result["status"] == "success"


# Add more tests here
