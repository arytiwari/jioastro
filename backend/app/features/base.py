"""
Base feature class for all feature modules.
"""

from abc import ABC, abstractmethod
from typing import Optional
from fastapi import APIRouter


class BaseFeature(ABC):
    """
    Base class for all feature modules.

    Each feature must:
    - Define a unique name
    - Provide a description
    - Specify version
    - Register an API router
    - Implement initialization logic
    """

    def __init__(self):
        self._initialized = False
        self._router: Optional[APIRouter] = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique feature name (e.g., 'life_snapshot')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable feature name (e.g., 'Life Snapshot')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Feature description."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Feature version (e.g., '1.0.0')."""
        pass

    @property
    @abstractmethod
    def author(self) -> str:
        """Feature author/owner."""
        pass

    @property
    @abstractmethod
    def magical_twelve_number(self) -> int:
        """Which of the Magical 12 features this is (1-12)."""
        pass

    @property
    def router(self) -> APIRouter:
        """Get the FastAPI router for this feature."""
        if self._router is None:
            self._router = self._create_router()
        return self._router

    @abstractmethod
    def _create_router(self) -> APIRouter:
        """
        Create and return the FastAPI router for this feature.

        Returns:
            APIRouter: Configured router with feature endpoints
        """
        pass

    def initialize(self) -> None:
        """
        Initialize the feature.

        Called once when the feature is registered.
        Override this method to perform feature-specific initialization.
        """
        if self._initialized:
            return

        self._setup()
        self._initialized = True

    def _setup(self) -> None:
        """
        Feature-specific setup logic.

        Override this method to perform initialization tasks like:
        - Database connection setup
        - Cache initialization
        - External service connections
        """
        pass

    @property
    def is_initialized(self) -> bool:
        """Check if feature is initialized."""
        return self._initialized

    def get_metadata(self) -> dict:
        """
        Get feature metadata.

        Returns:
            dict: Feature information
        """
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "magical_twelve_number": self.magical_twelve_number,
            "initialized": self.is_initialized,
        }

    def __repr__(self) -> str:
        return f"<Feature: {self.display_name} v{self.version}>"
