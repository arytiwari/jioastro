"""
Feature registry for managing all feature modules.
"""

from typing import Dict, Optional, List, Type
from .base import BaseFeature
import logging

logger = logging.getLogger(__name__)


class FeatureRegistry:
    """
    Central registry for all feature modules.

    Features are registered at application startup and can be
    accessed by name throughout the application lifecycle.
    """

    _instance: Optional["FeatureRegistry"] = None
    _features: Dict[str, BaseFeature] = {}

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, feature: BaseFeature) -> None:
        """
        Register a feature in the registry.

        Args:
            feature: Feature instance to register

        Raises:
            ValueError: If feature with same name already registered
        """
        instance = cls()

        if feature.name in instance._features:
            raise ValueError(f"Feature '{feature.name}' is already registered")

        # Initialize feature
        feature.initialize()

        # Store in registry
        instance._features[feature.name] = feature

        logger.info(
            f"Registered feature: {feature.display_name} v{feature.version} "
            f"(Magical 12 #{feature.magical_twelve_number})"
        )

    @classmethod
    def get_feature(cls, name: str) -> Optional[BaseFeature]:
        """
        Get a feature by name.

        Args:
            name: Feature name

        Returns:
            Feature instance or None if not found
        """
        instance = cls()
        return instance._features.get(name)

    @classmethod
    def get_all_features(cls) -> List[BaseFeature]:
        """
        Get all registered features.

        Returns:
            List of all feature instances
        """
        instance = cls()
        return list(instance._features.values())

    @classmethod
    def get_feature_names(cls) -> List[str]:
        """
        Get names of all registered features.

        Returns:
            List of feature names
        """
        instance = cls()
        return list(instance._features.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if a feature is registered.

        Args:
            name: Feature name

        Returns:
            True if feature is registered
        """
        instance = cls()
        return name in instance._features

    @classmethod
    def get_features_metadata(cls) -> List[dict]:
        """
        Get metadata for all registered features.

        Returns:
            List of feature metadata dictionaries
        """
        instance = cls()
        return [feature.get_metadata() for feature in instance._features.values()]

    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered features.

        WARNING: This should only be used in testing.
        """
        instance = cls()
        instance._features.clear()
        logger.warning("Feature registry cleared")

    def __repr__(self) -> str:
        return f"<FeatureRegistry: {len(self._features)} features>"


# Global registry instance
feature_registry = FeatureRegistry()
