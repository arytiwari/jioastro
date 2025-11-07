"""
Business logic for Life Snapshot feature.

UPDATED: Uses Supabase REST API instead of direct PostgreSQL connections.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
import logging
import hashlib
import json

from . import schemas, constants
from app.services.transit_service import TransitService
from app.services.vedic_astrology_accurate import AccurateVedicAstrology
from app.core.supabase_client import supabase_client

logger = logging.getLogger(__name__)


class LifeSnapshotService:
    """
    Service for Life Snapshot feature.

    Generates 60-second life insights including:
    - Top 3 life themes
    - 3 risks this month
    - 3 opportunities
    - 3 actionable recommendations

    Uses Supabase REST API for all database operations.
    """

    def __init__(self):
        self._initialized = False
        self.transit_service = TransitService()
        self.astrology_service = AccurateVedicAstrology()
        self.supabase = supabase_client

    def initialize(self):
        """Initialize the service."""
        if self._initialized:
            return

        logger.info("Initializing Life Snapshot service (Supabase REST API)")
        self._initialized = True

    async def generate_snapshot(
        self,
        user_id: str,
        profile_id: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a life snapshot for a user profile.

        Args:
            user_id: User ID
            profile_id: Profile ID
            force_refresh: Force regeneration even if cached

        Returns:
            Dictionary with snapshot data
        """
        logger.info(f"Generating life snapshot for user {user_id}, profile {profile_id}")

        # Check for cached snapshot
        if not force_refresh:
            cached = await self._get_cached_snapshot(user_id, profile_id)
            if cached:
                logger.info(f"Returning cached snapshot {cached['snapshot_id']}")
                return cached

        # Get profile data using Supabase REST API
        profile = await self._get_profile(profile_id, user_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found or not accessible")

        # Calculate components
        transits = self._calculate_transits(profile)
        chart_data = await self._get_chart_data(profile)

        # Generate insights
        themes = await self._generate_themes(profile, chart_data, transits)
        risks = await self._generate_risks(profile, chart_data, transits)
        opportunities = await self._generate_opportunities(profile, chart_data, transits)
        actions = await self._generate_actions(themes, risks, opportunities)
        life_phase = self._determine_life_phase(chart_data, transits)

        # Create insights object
        insights_data = {
            "top_themes": [theme.model_dump() for theme in themes[:constants.TOP_THEMES_COUNT]],
            "risks": [risk.model_dump() for risk in risks[:constants.RISKS_COUNT]],
            "opportunities": [opp.model_dump() for opp in opportunities[:constants.OPPORTUNITIES_COUNT]],
            "actions": [action.model_dump() for action in actions[:constants.ACTIONS_COUNT]],
            "life_phase": life_phase,
            "read_time_seconds": constants.ESTIMATED_READ_TIME_SECONDS
        }

        # Create snapshot data
        snapshot_data = {
            "profile_id": str(profile_id),
            "user_id": str(user_id),
            "chart_summary": chart_data,
            "transits_summary": transits
        }

        # Store in database using Supabase REST API
        snapshot_record = await self._store_snapshot(
            user_id=user_id,
            profile_id=profile_id,
            snapshot_data=snapshot_data,
            transits_data=transits,
            insights=insights_data
        )

        # Format response
        return await self._format_snapshot_response(snapshot_record, profile)

    async def get_snapshot(
        self,
        snapshot_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific snapshot using Supabase REST API.

        Args:
            snapshot_id: Snapshot ID
            user_id: User ID (for authorization)

        Returns:
            Snapshot data or None
        """
        snapshot = await self.supabase.select(
            table="life_snapshot_data",
            filters={"id": snapshot_id, "user_id": user_id},
            single=True
        )

        if not snapshot:
            return None

        # Get profile for formatting
        profile = await self.supabase.select(
            table="profiles",
            filters={"id": snapshot["profile_id"]},
            single=True
        )

        return await self._format_snapshot_response(snapshot, profile)

    async def list_snapshots(
        self,
        user_id: str,
        profile_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List snapshots for a user using Supabase REST API.

        Args:
            user_id: User ID
            profile_id: Optional profile ID to filter by
            limit: Max results to return
            offset: Offset for pagination

        Returns:
            List of snapshot summaries
        """
        # Build filters
        filters = {"user_id": user_id}
        if profile_id:
            filters["profile_id"] = profile_id

        # Get snapshots
        snapshots = await self.supabase.select(
            table="life_snapshot_data",
            filters=filters,
            order="generated_at.desc",
            limit=limit,
            offset=offset
        )

        if not snapshots:
            snapshots = []

        # Get unique profile IDs
        profile_ids = list(set(s["profile_id"] for s in snapshots))

        # Get profiles (Note: Supabase REST API doesn't support IN queries directly,
        # so we'll fetch profiles individually or use a stored procedure)
        profiles_dict = {}
        for pid in profile_ids:
            profile = await self.supabase.select(
                table="profiles",
                filters={"id": pid},
                single=True
            )
            if profile:
                profiles_dict[pid] = profile

        # Format results
        items = []
        for snapshot in snapshots:
            profile = profiles_dict.get(snapshot["profile_id"])
            items.append(schemas.SnapshotListItem(
                id=snapshot["id"],
                profile_id=snapshot["profile_id"],
                profile_name=profile["name"] if profile else "Unknown",
                generated_at=snapshot["generated_at"],
                expires_at=snapshot["expires_at"],
                is_expired=self._is_expired(snapshot["expires_at"]),
                themes_count=len(snapshot.get("insights", {}).get("top_themes", []))
            ))

        # Count total (without pagination)
        all_snapshots = await self.supabase.select(
            table="life_snapshot_data",
            filters=filters
        )
        total = len(all_snapshots) if all_snapshots else 0

        return {
            "snapshots": items,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    # Private helper methods

    async def _get_profile(
        self,
        profile_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get profile and verify ownership using Supabase REST API."""
        profile = await self.supabase.select(
            table="profiles",
            filters={"id": profile_id, "user_id": user_id},
            single=True
        )
        return profile

    async def _get_cached_snapshot(
        self,
        user_id: str,
        profile_id: str
    ) -> Optional[Dict[str, Any]]:
        """Check for valid cached snapshot using Supabase REST API."""
        now = datetime.now(timezone.utc).isoformat()

        # Note: Supabase REST API filters are limited
        # We'll fetch recent snapshots and filter in Python
        snapshots = await self.supabase.select(
            table="life_snapshot_data",
            filters={
                "user_id": user_id,
                "profile_id": profile_id
            },
            order="generated_at.desc",
            limit=5
        )

        if not snapshots:
            return None

        # Filter for non-expired snapshots in Python
        for snapshot in snapshots:
            if snapshot["expires_at"] > now:
                profile = await self.supabase.select(
                    table="profiles",
                    filters={"id": snapshot["profile_id"]},
                    single=True
                )
                return await self._format_snapshot_response(snapshot, profile)

        return None

    def _calculate_transits(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate current transits for profile."""
        try:
            # For now, return simplified transit data
            # In production, this would use the full transit service
            return {
                "jupiter": {"sign": "Taurus", "house_from_moon": 5},
                "saturn": {"sign": "Aquarius", "house_from_moon": 2},
                "rahu": {"sign": "Pisces", "house_from_moon": 3}
            }
        except Exception as e:
            logger.error(f"Error calculating transits: {e}")
            return {}

    async def _get_chart_data(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get chart data including yogas and dashas."""
        # For now, return simplified chart data
        # In production, this would integrate with full astrology services
        return {
            "yogas": ["Gaja Kesari", "Budhaditya"],
            "current_dasha": {"mahadasha": "Venus", "antardasha": "Jupiter"},
            "strengths": {"jupiter": 0.8, "venus": 0.7}
        }

    async def _generate_themes(
        self,
        profile: Dict[str, Any],
        chart_data: Dict,
        transits: Dict
    ) -> List[schemas.LifeTheme]:
        """Generate top life themes."""
        themes = [
            schemas.LifeTheme(
                title="Career Growth",
                description="Strong planetary support for professional advancement and recognition",
                confidence=0.85,
                planetary_basis=["Jupiter in 10th", "Venus MD"]
            ),
            schemas.LifeTheme(
                title="Relationship Harmony",
                description="Favorable period for deepening connections and resolving conflicts",
                confidence=0.75,
                planetary_basis=["Venus strong", "Jupiter aspect 7th"]
            ),
            schemas.LifeTheme(
                title="Financial Stability",
                description="Good time for building wealth and managing resources wisely",
                confidence=0.70,
                planetary_basis=["Jupiter aspect 2nd", "No malefic transits"]
            ),
        ]
        return sorted(themes, key=lambda x: x.confidence, reverse=True)

    async def _generate_risks(
        self,
        profile: Dict[str, Any],
        chart_data: Dict,
        transits: Dict
    ) -> List[schemas.LifeRisk]:
        """Generate potential risks."""
        risks = [
            schemas.LifeRisk(
                title="Avoid major purchases after mid-month",
                description="Saturn transit suggests delays in material acquisitions",
                severity=constants.SEVERITY_MEDIUM,
                date_range="Nov 15-30",
                mitigation="Focus on research and planning rather than execution"
            ),
            schemas.LifeRisk(
                title="Health checkup recommended",
                description="6th house influences suggest preventive care is beneficial",
                severity=constants.SEVERITY_LOW,
                date_range="This month",
                mitigation="Schedule routine medical checkup and maintain healthy routines"
            ),
        ]
        return risks

    async def _generate_opportunities(
        self,
        profile: Dict[str, Any],
        chart_data: Dict,
        transits: Dict
    ) -> List[schemas.LifeOpportunity]:
        """Generate opportunities."""
        opportunities = [
            schemas.LifeOpportunity(
                title="Best interview window",
                description="Mercury and Jupiter alignment favors communication and opportunity",
                window="Nov 10-12",
                confidence=0.82,
                planetary_support=["Mercury direct", "Jupiter aspect 10th"]
            ),
            schemas.LifeOpportunity(
                title="Networking peak",
                description="Social connections bring unexpected opportunities",
                window="Full Moon Nov 8",
                confidence=0.75,
                planetary_support=["Moon strong", "11th house activation"]
            ),
        ]
        return sorted(opportunities, key=lambda x: x.confidence, reverse=True)

    async def _generate_actions(
        self,
        themes: List[schemas.LifeTheme],
        risks: List[schemas.LifeRisk],
        opportunities: List[schemas.LifeOpportunity]
    ) -> List[schemas.LifeAction]:
        """Generate actionable recommendations."""
        actions = [
            schemas.LifeAction(
                action="Schedule important meetings or interviews Nov 10-12",
                priority=constants.PRIORITY_HIGH,
                reason="Optimal Mercury-Jupiter alignment for communication",
                when="This week"
            ),
            schemas.LifeAction(
                action="Update resume and LinkedIn profile",
                priority=constants.PRIORITY_HIGH,
                reason="Career growth theme supported by Venus MD",
                when="Before Nov 10"
            ),
            schemas.LifeAction(
                action="Book preventive health checkup",
                priority=constants.PRIORITY_MEDIUM,
                reason="6th house transit suggests preventive care",
                when="This month"
            ),
        ]
        return actions

    def _determine_life_phase(
        self,
        chart_data: Dict,
        transits: Dict
    ) -> str:
        """Determine overall life phase."""
        # Simple logic - can be enhanced with actual dasha analysis
        return constants.LIFE_PHASE_GROWTH

    async def _store_snapshot(
        self,
        user_id: str,
        profile_id: str,
        snapshot_data: Dict,
        transits_data: Dict,
        insights: Dict
    ) -> Dict[str, Any]:
        """Store snapshot in database using Supabase REST API."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=constants.SNAPSHOT_CACHE_TTL_SECONDS)

        # Generate cache key
        cache_key = self._generate_cache_key(user_id, profile_id, now)

        # Prepare data for insertion
        data = {
            "user_id": user_id,
            "profile_id": profile_id,
            "snapshot_data": snapshot_data,
            "transits_data": transits_data,
            "insights": insights,
            "generated_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "cache_key": cache_key
        }

        # Insert using Supabase REST API
        snapshot = await self.supabase.insert(
            table="life_snapshot_data",
            data=data
        )

        logger.info(f"Stored snapshot {snapshot['id']} for profile {profile_id}")
        return snapshot

    async def _format_snapshot_response(
        self,
        snapshot: Dict[str, Any],
        profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Format snapshot for API response."""
        insights = schemas.SnapshotInsights(**snapshot["insights"])

        profile_summary = schemas.ProfileSummary(
            id=snapshot["profile_id"],
            name=profile["name"] if profile else "Unknown"
        )

        response = schemas.SnapshotResponse(
            snapshot_id=snapshot["id"],
            profile=profile_summary,
            generated_at=snapshot["generated_at"],
            expires_at=snapshot["expires_at"],
            insights=insights,
            transits=snapshot.get("transits_data", {})
        )

        return response.model_dump()

    def _generate_cache_key(
        self,
        user_id: str,
        profile_id: str,
        timestamp: datetime
    ) -> str:
        """Generate cache key for deduplication."""
        # Use date (not time) for cache key so same-day requests use same cache
        date_str = timestamp.strftime("%Y-%m-%d")
        key_str = f"{user_id}:{profile_id}:{date_str}"
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _is_expired(self, expires_at: str) -> bool:
        """Check if a snapshot is expired."""
        now = datetime.now(timezone.utc)
        expiry = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        return now > expiry


# Global service instance
life_snapshot_service = LifeSnapshotService()
