"""
Feature flags system for JioAstro Magical 12 features.

This module provides a centralized feature flag management system
that allows features to be enabled/disabled independently.
"""

from enum import Enum
from functools import wraps
from typing import Optional, Dict
from fastapi import HTTPException, status
import os
import logging

logger = logging.getLogger(__name__)


class Feature(str, Enum):
    """Available features in the system."""

    # Magical 12 Features
    LIFE_SNAPSHOT = "life_snapshot"
    LIFE_THREADS = "life_threads"
    DECISION_COPILOT = "decision_copilot"
    TRANSIT_PULSE = "transit_pulse"
    REMEDY_PLANNER = "remedy_planner"
    ASTROTWIN_GRAPH = "astrotwin_graph"
    GUIDED_RITUALS = "guided_rituals"
    EVIDENCE_MODE = "evidence_mode"
    EXPERT_CONSOLE = "expert_console"
    REALITY_CHECK = "reality_check"
    HYPERLOCAL_PANCHANG = "hyperlocal_panchang"
    STORY_REELS = "story_reels"

    # Bonus Features
    INSTANT_ONBOARDING = "instant_onboarding"
    GOAL_BINDING = "goal_binding"
    SANKALP_CONTRACTS = "sankalp_contracts"
    MULTI_MODAL = "multi_modal"

    # Existing Features (from Phase 1-5)
    COMPATIBILITY = "compatibility"
    NUMEROLOGY = "numerology"
    ADVANCED_SYSTEMS = "advanced_systems"
    AI_INSIGHTS = "ai_insights"


class FeatureFlags:
    """
    Feature flag management system.

    Features can be enabled/disabled via:
    1. Environment variables (e.g., FEATURE_LIFE_SNAPSHOT=true)
    2. Runtime API calls (for testing/admin)
    3. Configuration files (future enhancement)
    """

    _instance: Optional["FeatureFlags"] = None
    _flags: Dict[Feature, bool] = {}

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize feature flags from environment."""
        if not self._flags:  # Only load once
            self._load_flags()

    def _load_flags(self) -> None:
        """Load feature flags from environment variables."""
        for feature in Feature:
            env_var = f"FEATURE_{feature.value.upper()}"
            env_value = os.getenv(env_var, "false").lower()

            # Parse boolean value
            is_enabled = env_value in ("true", "1", "yes", "on")

            self._flags[feature] = is_enabled

            status_str = "ENABLED" if is_enabled else "DISABLED"
            logger.info(f"Feature '{feature.value}': {status_str}")

    def is_enabled(self, feature: Feature) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature: Feature to check

        Returns:
            True if feature is enabled
        """
        return self._flags.get(feature, False)

    def enable(self, feature: Feature) -> None:
        """
        Enable a feature at runtime.

        Args:
            feature: Feature to enable
        """
        self._flags[feature] = True
        logger.info(f"Feature '{feature.value}' enabled at runtime")

    def disable(self, feature: Feature) -> None:
        """
        Disable a feature at runtime.

        Args:
            feature: Feature to disable
        """
        self._flags[feature] = False
        logger.info(f"Feature '{feature.value}' disabled at runtime")

    def get_all_flags(self) -> Dict[str, bool]:
        """
        Get all feature flags and their status.

        Returns:
            Dictionary of feature names to enabled status
        """
        return {feature.value: enabled for feature, enabled in self._flags.items()}

    def get_enabled_features(self) -> list[str]:
        """
        Get list of enabled features.

        Returns:
            List of enabled feature names
        """
        return [
            feature.value for feature, enabled in self._flags.items() if enabled
        ]

    def get_disabled_features(self) -> list[str]:
        """
        Get list of disabled features.

        Returns:
            List of disabled feature names
        """
        return [
            feature.value for feature, enabled in self._flags.items() if not enabled
        ]

    def reload(self) -> None:
        """Reload feature flags from environment."""
        self._flags.clear()
        self._load_flags()
        logger.info("Feature flags reloaded from environment")


# Global feature flags instance
feature_flags = FeatureFlags()


def require_feature(feature_name: str):
    """
    Decorator to require a feature flag for an endpoint.

    Usage:
        @router.get("/endpoint")
        @require_feature("life_snapshot")
        async def my_endpoint():
            ...

    Args:
        feature_name: Name of the required feature

    Raises:
        HTTPException: If feature is not enabled
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                feature = Feature(feature_name)
            except ValueError:
                logger.error(f"Invalid feature name: {feature_name}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Invalid feature configuration: {feature_name}",
                )

            if not feature_flags.is_enabled(feature):
                logger.warning(
                    f"Access denied to disabled feature: {feature_name}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Feature '{feature_name}' is not enabled",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def check_feature(feature_name: str) -> bool:
    """
    Check if a feature is enabled (non-raising version).

    Args:
        feature_name: Name of the feature

    Returns:
        True if feature is enabled, False otherwise
    """
    try:
        feature = Feature(feature_name)
        return feature_flags.is_enabled(feature)
    except ValueError:
        logger.error(f"Invalid feature name: {feature_name}")
        return False


def get_feature_status() -> Dict[str, Dict[str, any]]:
    """
    Get detailed status of all features.

    Returns:
        Dictionary with feature information and status
    """
    from app.features.registry import feature_registry

    status = {}

    for feature in Feature:
        feature_name = feature.value
        is_enabled = feature_flags.is_enabled(feature)
        is_registered = feature_registry.is_registered(feature_name)

        registered_feature = feature_registry.get_feature(feature_name)
        metadata = registered_feature.get_metadata() if registered_feature else None

        status[feature_name] = {
            "enabled": is_enabled,
            "registered": is_registered,
            "metadata": metadata,
        }

    return status
