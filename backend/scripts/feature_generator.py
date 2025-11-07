#!/usr/bin/env python3
"""
Feature Generator CLI for JioAstro Magical 12

This script scaffolds a new feature module with all necessary files.

Usage:
    python scripts/feature_generator.py generate <feature_name> \\
        --description "Feature description" \\
        --author "Your Name" \\
        --magical-number 1

Example:
    python scripts/feature_generator.py generate life_snapshot \\
        --description "60-second personalized life insights" \\
        --author "AI Assistant" \\
        --magical-number 1
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime


# Template files content
INIT_TEMPLATE = '''"""
{display_name} Feature - Magical 12 Feature #{magical_number}

{description}
"""

from .feature import {class_name}Feature

__all__ = ["{class_name}Feature"]
'''

README_TEMPLATE = '''# {display_name} Feature

**Magical 12 Feature #{magical_number}**

## Overview

{description}

## Author

{author}

## Version

1.0.0

## Status

🚧 **Under Development** - Template generated on {date}

## Quick Start

```bash
# Enable feature flag
export FEATURE_{feature_name_upper}=true

# Run tests
pytest app/features/{feature_name}/tests/ -v

# Start backend
uvicorn main:app --reload
```

## API Endpoints

```
POST /api/v2/{feature_name}/...
GET /api/v2/{feature_name}/...
```

## Development

See PARALLEL_DEVELOPMENT_FRAMEWORK.md for complete workflow.

## Testing

```bash
pytest app/features/{feature_name}/tests/test_service.py -v
pytest --cov=app/features/{feature_name}
```

---

**Generated:** {date}
**Next Steps:** Implement business logic in `service.py`
'''

FEATURE_TEMPLATE = '''"""
{display_name} Feature Implementation
"""

from fastapi import APIRouter, Depends
from app.features.base import BaseFeature
from app.core.feature_flags import require_feature
from app.core.security import get_current_user
from . import schemas, service


class {class_name}Feature(BaseFeature):
    """
    {display_name} feature implementation.

    {description}
    """

    @property
    def name(self) -> str:
        return "{feature_name}"

    @property
    def display_name(self) -> str:
        return "{display_name}"

    @property
    def description(self) -> str:
        return "{description}"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def author(self) -> str:
        return "{author}"

    @property
    def magical_twelve_number(self) -> int:
        return {magical_number}

    def _create_router(self) -> APIRouter:
        """Create API router for this feature."""
        router = APIRouter(
            prefix="/{feature_name}",
            tags=["{display_name}"]
        )

        @router.get("/")
        @require_feature("{feature_name}")
        async def get_feature_info():
            """Get feature information."""
            return {{
                "feature": self.name,
                "version": self.version,
                "description": self.description,
                "magical_twelve_number": self.magical_twelve_number
            }}

        # Add your endpoints here
        # Example:
        # @router.post("/action")
        # @require_feature("{feature_name}")
        # async def action(user: dict = Depends(get_current_user)):
        #     # Implementation
        #     pass

        return router


# Create feature instance
{feature_name}_feature = {class_name}Feature()
'''

MODELS_TEMPLATE = '''"""
Database models for {display_name} feature.
"""

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.db.database import Base


class {class_name}Data(Base):
    """
    {display_name} data model.

    Table: {feature_name}_data
    """

    __tablename__ = "{feature_name}_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)

    # Feature-specific fields
    data = Column(JSON, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<{class_name}Data(id={{self.id}}, user_id={{self.user_id}})>"
'''

SCHEMAS_TEMPLATE = '''"""
Pydantic schemas for {display_name} feature.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class {class_name}Base(BaseModel):
    """Base schema for {display_name}."""
    pass


class {class_name}Create(BaseModel):
    """Schema for creating {display_name}."""
    profile_id: UUID = Field(..., description="Profile ID")


class {class_name}Response(BaseModel):
    """Schema for {display_name} response."""
    id: UUID
    user_id: UUID
    profile_id: UUID
    data: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
'''

SERVICE_TEMPLATE = '''"""
Business logic for {display_name} feature.
"""

from typing import Optional, Dict, Any
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class {class_name}Service:
    """
    Service for {display_name} feature.

    This class contains all business logic for the feature.
    """

    def __init__(self):
        self._initialized = False

    def initialize(self):
        """Initialize the service."""
        if self._initialized:
            return

        logger.info("Initializing {display_name} service")
        # Add initialization logic here

        self._initialized = True

    async def process(self, user_id: str, profile_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process {display_name} request.

        Args:
            user_id: User ID
            profile_id: Profile ID
            data: Input data

        Returns:
            Processed result
        """
        logger.info(f"Processing {{display_name}} for user {{user_id}}, profile {{profile_id}}")

        # TODO: Implement your business logic here

        result = {{
            "status": "success",
            "message": "{display_name} processed successfully"
        }}

        return result


# Global service instance
{feature_name}_service = {class_name}Service()
'''

TEST_SERVICE_TEMPLATE = '''"""
Unit tests for {display_name} service.
"""

import pytest
from app.features.{feature_name}.service import {class_name}Service


@pytest.fixture
def service():
    """Create service instance."""
    return {class_name}Service()


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
        data={{"test": "data"}}
    )

    assert result["status"] == "success"


# Add more tests here
'''

CONSTANTS_TEMPLATE = '''"""
Constants for {display_name} feature.
"""

# Feature configuration
FEATURE_NAME = "{feature_name}"
FEATURE_VERSION = "1.0.0"

# Add your constants here
CACHE_TTL = 3600  # 1 hour
MAX_REQUESTS_PER_MINUTE = 10
'''


def to_class_name(feature_name: str) -> str:
    """Convert feature_name to ClassName."""
    return ''.join(word.capitalize() for word in feature_name.split('_'))


def to_display_name(feature_name: str) -> str:
    """Convert feature_name to Display Name."""
    return ' '.join(word.capitalize() for word in feature_name.split('_'))


def generate_feature(
    feature_name: str,
    description: str,
    author: str,
    magical_number: int
):
    """Generate a new feature module."""

    # Validate inputs
    if not feature_name.replace('_', '').isalnum():
        print(f"Error: Feature name must contain only letters, numbers, and underscores")
        sys.exit(1)

    if magical_number < 1 or magical_number > 12:
        print(f"Error: Magical number must be between 1 and 12")
        sys.exit(1)

    # Paths
    backend_dir = Path(__file__).parent.parent
    features_dir = backend_dir / "app" / "features"
    feature_dir = features_dir / feature_name
    tests_dir = feature_dir / "tests"

    # Check if feature already exists
    if feature_dir.exists():
        print(f"Error: Feature '{feature_name}' already exists at {feature_dir}")
        sys.exit(1)

    # Create directories
    print(f"Creating feature directory: {feature_dir}")
    feature_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(exist_ok=True)

    # Generate file content
    class_name = to_class_name(feature_name)
    display_name = to_display_name(feature_name)
    feature_name_upper = feature_name.upper()
    date = datetime.now().strftime("%Y-%m-%d")

    context = {
        "feature_name": feature_name,
        "class_name": class_name,
        "display_name": display_name,
        "feature_name_upper": feature_name_upper,
        "description": description,
        "author": author,
        "magical_number": magical_number,
        "date": date
    }

    # Create files
    files = {
        "__init__.py": INIT_TEMPLATE,
        "README.md": README_TEMPLATE,
        "feature.py": FEATURE_TEMPLATE,
        "models.py": MODELS_TEMPLATE,
        "schemas.py": SCHEMAS_TEMPLATE,
        "service.py": SERVICE_TEMPLATE,
        "constants.py": CONSTANTS_TEMPLATE,
    }

    for filename, template in files.items():
        file_path = feature_dir / filename
        content = template.format(**context)
        file_path.write_text(content)
        print(f"  ✓ Created {filename}")

    # Create test file
    test_file = tests_dir / "test_service.py"
    test_content = TEST_SERVICE_TEMPLATE.format(**context)
    test_file.write_text(test_content)
    print(f"  ✓ Created tests/test_service.py")

    # Create empty __init__.py for tests
    (tests_dir / "__init__.py").write_text("")

    print(f"\n✅ Feature '{feature_name}' generated successfully!")
    print(f"\nNext steps:")
    print(f"  1. Enable feature flag: export FEATURE_{feature_name_upper}=true")
    print(f"  2. Create database migration: alembic revision --autogenerate -m '{feature_name}: add tables'")
    print(f"  3. Implement business logic in: {feature_dir}/service.py")
    print(f"  4. Add API endpoints in: {feature_dir}/feature.py")
    print(f"  5. Write tests in: {tests_dir}/")
    print(f"  6. Register feature in main.py")
    print(f"\nRead the feature README: {feature_dir}/README.md")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a new feature module for JioAstro"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a new feature")
    generate_parser.add_argument("feature_name", help="Feature name (e.g., life_snapshot)")
    generate_parser.add_argument("--description", required=True, help="Feature description")
    generate_parser.add_argument("--author", required=True, help="Feature author")
    generate_parser.add_argument(
        "--magical-number",
        type=int,
        required=True,
        help="Magical 12 number (1-12)"
    )

    args = parser.parse_args()

    if args.command == "generate":
        generate_feature(
            args.feature_name,
            args.description,
            args.author,
            args.magical_number
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
