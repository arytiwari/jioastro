"""
Life Snapshot Feature Implementation

UPDATED: Uses Supabase REST API instead of direct PostgreSQL connections.
No database session (AsyncSession) dependency required.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.features.base import BaseFeature
from app.core.feature_flags import require_feature
from app.core.security import get_current_user
from . import schemas, service_no_db as service, constants

import logging

logger = logging.getLogger(__name__)


class LifeSnapshotFeature(BaseFeature):
    """
    Life Snapshot feature implementation.

    Provides 60-second personalized life insights including themes, risks,
    opportunities, and actionable recommendations based on Vedic astrology.
    """

    @property
    def name(self) -> str:
        return constants.FEATURE_NAME

    @property
    def display_name(self) -> str:
        return constants.FEATURE_DISPLAY_NAME

    @property
    def description(self) -> str:
        return "60-second personalized life insights powered by AI"

    @property
    def version(self) -> str:
        return constants.FEATURE_VERSION

    @property
    def author(self) -> str:
        return "JioAstro Development Team"

    @property
    def magical_twelve_number(self) -> int:
        return 1  # First of the Magical 12 features

    def _setup(self) -> None:
        """Initialize Life Snapshot service."""
        logger.info("Setting up Life Snapshot feature")
        service.life_snapshot_service.initialize()

    def _create_router(self) -> APIRouter:
        """Create API router for this feature."""
        router = APIRouter(
            prefix="/life-snapshot",
            tags=["Life Snapshot"]
        )

        @router.get("/")
        @require_feature(constants.FEATURE_NAME)
        async def get_feature_info():
            """
            Get Life Snapshot feature information.

            Returns basic metadata about the feature including version,
            description, and status.
            """
            return {
                "feature": self.name,
                "version": self.version,
                "description": self.description,
                "magical_twelve_number": self.magical_twelve_number,
                "read_time_seconds": constants.ESTIMATED_READ_TIME_SECONDS,
                "cache_ttl_seconds": constants.SNAPSHOT_CACHE_TTL_SECONDS
            }

        @router.post("/generate", response_model=schemas.SnapshotResponse)
        @require_feature(constants.FEATURE_NAME)
        async def generate_snapshot(
            request: schemas.SnapshotGenerateRequest,
            current_user: dict = Depends(get_current_user)
        ):
            """
            Generate a new life snapshot.

            Creates a 60-second personalized life insight including:
            - Top 3 life themes
            - 3 risks this month
            - 3 opportunities
            - 3 actionable recommendations

            Results are cached for 1 hour to improve performance.
            Uses Supabase REST API for all database operations.

            Args:
                request: Snapshot generation request with profile_id and force_refresh flag
                current_user: Authenticated user

            Returns:
                SnapshotResponse with complete snapshot data
            """
            try:
                user_id = current_user.get("user_id")
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User ID not found in token"
                    )

                snapshot = await service.life_snapshot_service.generate_snapshot(
                    user_id=user_id,
                    profile_id=str(request.profile_id),
                    force_refresh=request.force_refresh
                )

                logger.info(f"Generated snapshot {snapshot['snapshot_id']} for user {user_id}")
                return snapshot

            except ValueError as e:
                logger.error(f"Validation error generating snapshot: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
            except Exception as e:
                logger.error(f"Error generating snapshot: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate snapshot"
                )

        @router.get("/{snapshot_id}", response_model=schemas.SnapshotResponse)
        @require_feature(constants.FEATURE_NAME)
        async def get_snapshot(
            snapshot_id: str,
            current_user: dict = Depends(get_current_user)
        ):
            """
            Retrieve a specific snapshot by ID.

            Uses Supabase REST API for database operations.

            Args:
                snapshot_id: UUID of the snapshot to retrieve
                current_user: Authenticated user

            Returns:
                SnapshotResponse with snapshot data
            """
            try:
                user_id = current_user.get("user_id")
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User ID not found in token"
                    )

                snapshot = await service.life_snapshot_service.get_snapshot(
                    snapshot_id=snapshot_id,
                    user_id=user_id
                )

                if not snapshot:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Snapshot {snapshot_id} not found"
                    )

                return snapshot

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error retrieving snapshot: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve snapshot"
                )

        @router.get("/list", response_model=schemas.SnapshotListResponse)
        @require_feature(constants.FEATURE_NAME)
        async def list_snapshots(
            profile_id: str = None,
            limit: int = 10,
            offset: int = 0,
            current_user: dict = Depends(get_current_user)
        ):
            """
            List snapshots for the current user.

            Uses Supabase REST API for database operations.

            Args:
                profile_id: Optional profile ID to filter by
                limit: Maximum number of results (default: 10)
                offset: Offset for pagination (default: 0)
                current_user: Authenticated user

            Returns:
                SnapshotListResponse with list of snapshot summaries
            """
            try:
                user_id = current_user.get("user_id")
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User ID not found in token"
                    )

                result = await service.life_snapshot_service.list_snapshots(
                    user_id=user_id,
                    profile_id=profile_id,
                    limit=min(limit, 100),  # Cap at 100
                    offset=offset
                )

                return result

            except Exception as e:
                logger.error(f"Error listing snapshots: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to list snapshots"
                )

        return router


# Create feature instance
life_snapshot_feature = LifeSnapshotFeature()
