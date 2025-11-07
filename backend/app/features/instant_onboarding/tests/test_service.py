"""
Unit tests for Instant Onboarding service.
"""

import pytest
from app.features.instant_onboarding.service import InstantOnboardingService


@pytest.fixture
def service():
    """Create service instance."""
    return InstantOnboardingService()


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
