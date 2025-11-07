"""
Feature modules for JioAstro Magical 12.

This package contains modular feature implementations that can be developed
independently and enabled/disabled via feature flags.
"""

from .base import BaseFeature
from .registry import FeatureRegistry

__all__ = ["BaseFeature", "FeatureRegistry"]
