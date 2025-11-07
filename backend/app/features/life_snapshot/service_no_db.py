"""
Business logic for Life Snapshot feature (No-DB version).
This version skips database caching to avoid direct DB connection issues.
"""

from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime, timezone
import logging

from . import schemas, constants
from app.services.supabase_service import SupabaseService
from app.services.transit_service import TransitService
from app.services.vedic_astrology_accurate import AccurateVedicAstrology

logger = logging.getLogger(__name__)


class LifeSnapshotService:
    """
    Service for Life Snapshot feature (No-DB version).

    Generates 60-second life insights including:
    - Top 3 life themes
    - 3 risks this month
    - 3 opportunities
    - 3 actionable recommendations

    NOTE: Database caching is disabled to avoid direct PostgreSQL connection issues.
    """

    def __init__(self):
        self._initialized = False
        self.transit_service = TransitService()
        self.astrology_service = AccurateVedicAstrology()
        self.supabase = SupabaseService()

    def initialize(self):
        """Initialize the service."""
        if self._initialized:
            return

        logger.info("Initializing Life Snapshot service (No-DB mode)")
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
            force_refresh: Ignored in No-DB mode

        Returns:
            Dictionary with snapshot data
        """
        logger.info(f"Generating life snapshot for user {user_id}, profile {profile_id}")

        # Get profile data from Supabase
        profile = await self.supabase.get_profile(profile_id, user_id)
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

        # Create snapshot response (no DB storage)
        snapshot_id = str(uuid4())
        generated_at = datetime.now(timezone.utc)
        expires_at = generated_at  # Valid indefinitely in No-DB mode

        # Convert transits dict to list format for schema compatibility
        transits_list = []
        for planet, data in transits.items():
            transits_list.append({
                "planet": planet,
                **data
            })

        return {
            "snapshot_id": snapshot_id,
            "profile": {
                "id": str(profile_id),
                "name": profile.get("name", "Unknown")
            },
            "generated_at": generated_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "insights": insights_data,
            "transits": transits_list
        }

    async def get_snapshot(
        self,
        snapshot_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific snapshot.

        NOTE: Not supported in No-DB mode. Always returns None.
        """
        logger.warning("get_snapshot called in No-DB mode - not supported")
        return None

    async def list_snapshots(
        self,
        user_id: str,
        profile_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List snapshots for a user.

        NOTE: Not supported in No-DB mode. Always returns empty list.
        """
        logger.warning("list_snapshots called in No-DB mode - not supported")
        return {
            "snapshots": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }

    def _calculate_transits(self, profile: Dict) -> Dict[str, Any]:
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

    async def _get_chart_data(self, profile: Dict) -> Dict[str, Any]:
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
        profile: Dict,
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
        profile: Dict,
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
                title="Communication challenges in partnerships",
                description="Mercury retrograde may cause misunderstandings",
                severity=constants.SEVERITY_LOW,
                date_range="Nov 10-25",
                mitigation="Double-check all agreements and clarify expectations"
            ),
            schemas.LifeRisk(
                title="Energy fluctuations mid-week",
                description="Mars aspect suggests need for rest and recuperation",
                severity=constants.SEVERITY_LOW,
                date_range="Weekly",
                mitigation="Schedule demanding tasks for early week"
            ),
        ]
        return sorted(risks, key=lambda x: (x.severity == constants.SEVERITY_HIGH, x.severity == constants.SEVERITY_MEDIUM), reverse=True)

    async def _generate_opportunities(
        self,
        profile: Dict,
        chart_data: Dict,
        transits: Dict
    ) -> List[schemas.LifeOpportunity]:
        """Generate opportunities."""
        opportunities = [
            schemas.LifeOpportunity(
                title="Network expansion",
                description="Jupiter transit favors meeting influential people",
                window="Next 2 weeks",
                confidence=0.85,
                planetary_support=["Jupiter", "Venus"]
            ),
            schemas.LifeOpportunity(
                title="Creative projects",
                description="Venus period supports artistic expression and innovation",
                window="This month",
                confidence=0.80,
                planetary_support=["Venus", "Mercury"]
            ),
            schemas.LifeOpportunity(
                title="Learning new skills",
                description="Mercury position excellent for education and skill development",
                window="Next 3 weeks",
                confidence=0.75,
                planetary_support=["Mercury", "Jupiter"]
            ),
        ]
        return opportunities

    async def _generate_actions(
        self,
        themes: List[schemas.LifeTheme],
        risks: List[schemas.LifeRisk],
        opportunities: List[schemas.LifeOpportunity]
    ) -> List[schemas.LifeAction]:
        """Generate actionable recommendations."""
        actions = [
            schemas.LifeAction(
                action="Schedule important meetings in the first half of the month",
                reason="Aligns with favorable Jupiter and Venus transits",
                priority="high",
                when="This week"
            ),
            schemas.LifeAction(
                action="Dedicate time daily for creative or spiritual practice",
                reason="Strengthens Venus period energies and personal growth",
                priority="medium",
                when="Daily, 15-30 min"
            ),
            schemas.LifeAction(
                action="Review and update your professional profile",
                reason="Upcoming Jupiter aspect favors career visibility",
                priority="medium",
                when="This weekend"
            ),
        ]
        return actions

    def _determine_life_phase(self, chart_data: Dict, transits: Dict) -> str:
        """Determine current life phase based on chart and transits."""
        # Simplified life phase determination
        # In production, this would use dasha periods and transits
        return "Growth & Expansion"


# Create singleton instance
life_snapshot_service = LifeSnapshotService()
