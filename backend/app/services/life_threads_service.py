"""
Life Threads Service
Handles Dasha timeline generation and life event management
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, timedelta, timezone, time as datetime_time
from decimal import Decimal
import logging
import hashlib
import json

from app.core.supabase_client import SupabaseClient
from app.schemas.life_threads import (
    CreateLifeEventRequest,
    UpdateLifeEventRequest,
    LifeEvent,
    DashaPeriod,
    MahadashaBlock,
    DashaTimeline,
    TimelineEvent,
    EventStatistics,
    DashaAnalysis
)
from app.services.vedic_astrology_accurate import AccurateVedicAstrology

logger = logging.getLogger(__name__)


class LifeThreadsService:
    """Service for Life Threads - Timeline visualization with Dasha periods"""

    # Vimshottari Dasha periods in years
    VIMSHOTTARI_PERIODS = {
        "Ketu": 7,
        "Venus": 20,
        "Sun": 6,
        "Moon": 10,
        "Mars": 7,
        "Rahu": 18,
        "Jupiter": 16,
        "Saturn": 19,
        "Mercury": 17
    }

    # Total cycle
    TOTAL_CYCLE_YEARS = 120

    # Nakshatra to Dasha Lord mapping (starting from Ashwini)
    NAKSHATRA_DASHA_LORD = [
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
    ]

    def __init__(self, supabase: SupabaseClient):
        self.supabase = supabase

    async def create_life_event(
        self,
        user_id: str,
        request: CreateLifeEventRequest
    ) -> LifeEvent:
        """Create a new life event with astrological context"""

        # Verify profile ownership
        profile = await self.supabase.select(
            "profiles",
            filters={"id": request.profile_id, "user_id": user_id}
        )

        if not profile or len(profile) == 0:
            raise ValueError("Profile not found or access denied")

        profile_data = profile[0]

        # Calculate Dasha period for event date
        dasha_period = await self._get_dasha_for_date(
            request.profile_id,
            request.event_date
        )

        # Prepare event data
        event_data = {
            "user_id": user_id,
            "profile_id": request.profile_id,
            "event_type": request.event_type.value,
            "event_name": request.event_name,
            "event_date": request.event_date.isoformat(),
            "event_description": request.event_description,
            "event_impact": request.event_impact.value if request.event_impact else None,
            "dasha_period": dasha_period,
            "tags": request.tags or [],
            "is_milestone": request.is_milestone,
            "privacy_level": request.privacy_level.value
        }

        # Insert event
        result = await self.supabase.insert("life_events", event_data)

        if not result or len(result) == 0:
            raise RuntimeError("Failed to create life event")

        return LifeEvent(**result[0])

    async def update_life_event(
        self,
        user_id: str,
        event_id: str,
        request: UpdateLifeEventRequest
    ) -> LifeEvent:
        """Update an existing life event"""

        # Build update data
        update_data = {}
        if request.event_type is not None:
            update_data["event_type"] = request.event_type.value
        if request.event_name is not None:
            update_data["event_name"] = request.event_name
        if request.event_date is not None:
            update_data["event_date"] = request.event_date.isoformat()
            # Recalculate Dasha if date changed
            event = await self.supabase.select(
                "life_events",
                filters={"id": event_id, "user_id": user_id}
            )
            if event and len(event) > 0:
                dasha_period = await self._get_dasha_for_date(
                    event[0]["profile_id"],
                    request.event_date
                )
                update_data["dasha_period"] = dasha_period

        if request.event_description is not None:
            update_data["event_description"] = request.event_description
        if request.event_impact is not None:
            update_data["event_impact"] = request.event_impact.value
        if request.tags is not None:
            update_data["tags"] = request.tags
        if request.is_milestone is not None:
            update_data["is_milestone"] = request.is_milestone
        if request.privacy_level is not None:
            update_data["privacy_level"] = request.privacy_level.value

        if not update_data:
            raise ValueError("No fields to update")

        # Update event
        result = await self.supabase.update(
            "life_events",
            filters={"id": event_id, "user_id": user_id},
            data=update_data
        )

        if not result or len(result) == 0:
            raise ValueError("Event not found or access denied")

        return LifeEvent(**result[0])

    async def delete_life_event(self, user_id: str, event_id: str) -> bool:
        """Delete a life event"""
        await self.supabase.delete(
            "life_events",
            filters={"id": event_id, "user_id": user_id}
        )
        return True

    async def get_life_event(self, user_id: str, event_id: str) -> Optional[LifeEvent]:
        """Get a specific life event"""
        result = await self.supabase.select(
            "life_events",
            filters={"id": event_id, "user_id": user_id}
        )

        if not result or len(result) == 0:
            return None

        return LifeEvent(**result[0])

    async def list_life_events(
        self,
        user_id: str,
        profile_id: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        milestones_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[LifeEvent], int]:
        """List user's life events with filters"""

        filters = {"user_id": user_id}
        if profile_id:
            filters["profile_id"] = profile_id
        if milestones_only:
            filters["is_milestone"] = True

        # Note: For date ranges and array filters, we'd need to use raw SQL
        # or handle filtering in Python. For now, basic filters.

        result = await self.supabase.select(
            "life_events",
            filters=filters,
            order="event_date.desc",
            limit=limit,
            offset=offset
        )

        total = await self.supabase.count("life_events", filters=filters)

        events = [LifeEvent(**event) for event in result] if result else []
        return events, total

    async def get_dasha_timeline(
        self,
        user_id: str,
        profile_id: str
    ) -> DashaTimeline:
        """Generate complete Dasha timeline with events"""

        # Get profile
        profile_result = await self.supabase.select(
            "profiles",
            filters={"id": profile_id, "user_id": user_id}
        )

        if not profile_result or len(profile_result) == 0:
            raise ValueError("Profile not found")

        profile = profile_result[0]
        birth_date = datetime.fromisoformat(profile["birth_date"]).date()

        # Check cache
        cached = await self._get_cached_timeline(profile_id)
        if cached:
            # Add events to cached timeline
            return await self._populate_timeline_with_events(cached, user_id, profile_id)

        # Generate timeline
        timeline_data = await self._generate_vimshottari_timeline(
            profile_id,
            birth_date,
            profile.get("birth_time"),
            profile.get("latitude"),
            profile.get("longitude")
        )

        # Cache it
        await self._cache_timeline(profile_id, timeline_data)

        # Add events
        return await self._populate_timeline_with_events(timeline_data, user_id, profile_id)

    async def _generate_vimshottari_timeline(
        self,
        profile_id: str,
        birth_date: date,
        birth_time: Optional[str],
        latitude: Optional[float],
        longitude: Optional[float]
    ) -> Dict[str, Any]:
        """Generate Vimshottari Dasha timeline using accurate birth chart calculation"""

        # Validate required data
        if not birth_time or latitude is None or longitude is None:
            logger.warning(f"Missing birth data for profile {profile_id}, using default timeline")
            return self._generate_default_timeline(profile_id, birth_date)

        try:
            # Create datetime from birth date and time
            time_parts = birth_time.split(':')
            birth_datetime = datetime.combine(
                birth_date,
                datetime_time(int(time_parts[0]), int(time_parts[1]), 0)
            )

            # Calculate accurate birth chart using Swiss Ephemeris
            astro_service = AccurateVedicAstrology()
            chart_data = astro_service.calculate_chart(
                birth_datetime=birth_datetime,
                latitude=latitude,
                longitude=longitude,
                timezone_str="UTC"  # Will be converted internally
            )

            # Get the Vimshottari Dasha data from chart
            dasha_data = chart_data.get("vimshottari_dasha", {})
            mahadashas = dasha_data.get("mahadashas", [])

            if not mahadashas:
                logger.warning(f"No mahadashas calculated for profile {profile_id}, using default")
                return self._generate_default_timeline(profile_id, birth_date)

            # Format mahadasha periods for Life Threads
            mahadasha_periods = []
            for maha in mahadashas:
                mahadasha_periods.append({
                    "planet": maha["planet"],
                    "start_date": maha["start_date"],
                    "end_date": maha["end_date"],
                    "duration_years": maha["years"]
                })

            return {
                "profile_id": profile_id,
                "birth_date": birth_date.isoformat(),
                "vimshottari_start_date": birth_date.isoformat(),
                "mahadasha_periods": mahadasha_periods
            }

        except Exception as e:
            logger.error(f"Error calculating dasha timeline for profile {profile_id}: {e}")
            return self._generate_default_timeline(profile_id, birth_date)

    def _generate_default_timeline(self, profile_id: str, birth_date: date) -> Dict[str, Any]:
        """Generate a default timeline when birth data is incomplete (fallback)"""

        # Use Ketu as default starting dasha (traditional approach)
        dasha_sequence = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        mahadasha_periods = []
        current_date = birth_date

        for planet in dasha_sequence:
            period_years = self.VIMSHOTTARI_PERIODS[planet]
            end_date = current_date + timedelta(days=int(period_years * 365.25))

            mahadasha_periods.append({
                "planet": planet,
                "start_date": current_date.isoformat(),
                "end_date": end_date.isoformat(),
                "duration_years": period_years
            })

            current_date = end_date

        return {
            "profile_id": profile_id,
            "birth_date": birth_date.isoformat(),
            "vimshottari_start_date": birth_date.isoformat(),
            "mahadasha_periods": mahadasha_periods
        }

    async def _cache_timeline(self, profile_id: str, timeline_data: Dict[str, Any]):
        """Cache timeline in database"""
        cache_data = {
            "profile_id": profile_id,
            "timeline_data": timeline_data,
            "major_periods": timeline_data["mahadasha_periods"],
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
        }

        # Upsert
        await self.supabase.upsert(
            "dasha_timeline_cache",
            cache_data,
            on_conflict="profile_id"
        )

    async def _get_cached_timeline(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get cached timeline if not expired"""
        result = await self.supabase.select(
            "dasha_timeline_cache",
            filters={"profile_id": profile_id}
        )

        if not result or len(result) == 0:
            return None

        cache = result[0]
        expires_at = datetime.fromisoformat(cache["expires_at"])

        # Compare timezone-aware datetimes
        now = datetime.now(timezone.utc)
        # Ensure expires_at is timezone-aware
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now:
            return None

        return cache["timeline_data"]

    async def _populate_timeline_with_events(
        self,
        timeline_data: Dict[str, Any],
        user_id: str,
        profile_id: str
    ) -> DashaTimeline:
        """Add events to timeline"""

        # Get all events for this profile
        events_result = await self.supabase.select(
            "life_events",
            filters={"user_id": user_id, "profile_id": profile_id},
            order="event_date.asc"
        )

        events = events_result if events_result else []

        # Map events to Mahadasha periods
        mahadasha_blocks = []
        for period in timeline_data["mahadasha_periods"]:
            period_start = datetime.fromisoformat(period["start_date"]).date()
            period_end = datetime.fromisoformat(period["end_date"]).date()

            # Find events in this period
            period_events = [
                TimelineEvent(
                    id=event["id"],
                    event_name=event["event_name"],
                    event_date=datetime.fromisoformat(event["event_date"]).date(),
                    event_type=event["event_type"],
                    event_impact=event.get("event_impact"),
                    is_milestone=event["is_milestone"],
                    dasha_lord=period["planet"],
                    tags=event.get("tags", [])
                )
                for event in events
                if period_start <= datetime.fromisoformat(event["event_date"]).date() <= period_end
            ]

            mahadasha_blocks.append(
                MahadashaBlock(
                    planet=period["planet"],
                    start_date=period_start,
                    end_date=period_end,
                    duration_years=period["duration_years"],
                    events_count=len(period_events),
                    events=period_events
                )
            )

        # Get profile name
        profile_result = await self.supabase.select(
            "profiles",
            filters={"id": profile_id}
        )
        profile_name = profile_result[0]["name"] if profile_result else "Unknown"

        return DashaTimeline(
            profile_id=profile_id,
            profile_name=profile_name,
            birth_date=datetime.fromisoformat(timeline_data["birth_date"]).date(),
            vimshottari_start_date=datetime.fromisoformat(timeline_data["vimshottari_start_date"]).date(),
            mahadasha_periods=mahadasha_blocks,
            total_events=len(events)
        )

    async def _get_dasha_for_date(
        self,
        profile_id: str,
        event_date: date
    ) -> Dict[str, Any]:
        """Get Dasha period active on a specific date"""

        # Get cached timeline
        timeline = await self._get_cached_timeline(profile_id)

        if not timeline:
            # Generate it
            profile_result = await self.supabase.select(
                "profiles",
                filters={"id": profile_id}
            )
            if not profile_result:
                return {}

            profile = profile_result[0]
            birth_date = datetime.fromisoformat(profile["birth_date"]).date()
            timeline = await self._generate_vimshottari_timeline(
                profile_id,
                birth_date,
                profile.get("birth_time"),
                profile.get("latitude"),
                profile.get("longitude")
            )

        # Find Mahadasha for date
        for period in timeline["mahadasha_periods"]:
            start = datetime.fromisoformat(period["start_date"]).date()
            end = datetime.fromisoformat(period["end_date"]).date()

            if start <= event_date <= end:
                return {
                    "mahadasha": period["planet"],
                    "mahadasha_start": start.isoformat(),
                    "mahadasha_end": end.isoformat()
                }

        return {}

    async def get_event_statistics(
        self,
        user_id: str,
        profile_id: Optional[str] = None
    ) -> EventStatistics:
        """Get statistics about user's life events"""

        filters = {"user_id": user_id}
        if profile_id:
            filters["profile_id"] = profile_id

        events = await self.supabase.select("life_events", filters=filters)

        if not events:
            return EventStatistics(
                total_events=0,
                milestones_count=0,
                events_by_type={},
                events_by_impact={},
                events_by_dasha={},
                average_events_per_year=0.0
            )

        # Calculate stats
        total_events = len(events)
        milestones_count = sum(1 for e in events if e.get("is_milestone"))

        # Events by type
        events_by_type = {}
        for event in events:
            event_type = event["event_type"]
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1

        # Events by impact
        events_by_impact = {}
        for event in events:
            impact = event.get("event_impact")
            if impact:
                events_by_impact[impact] = events_by_impact.get(impact, 0) + 1

        # Events by Dasha
        events_by_dasha = {}
        for event in events:
            dasha_period = event.get("dasha_period", {})
            if dasha_period:
                mahadasha = dasha_period.get("mahadasha")
                if mahadasha:
                    events_by_dasha[mahadasha] = events_by_dasha.get(mahadasha, 0) + 1

        # Most active Dasha
        most_active_dasha = max(events_by_dasha.items(), key=lambda x: x[1])[0] if events_by_dasha else None

        # Average events per year
        if events:
            dates = [datetime.fromisoformat(e["event_date"]).date() for e in events]
            min_year = min(dates).year
            max_year = max(dates).year
            years_span = max(max_year - min_year, 1)
            avg_events_per_year = total_events / years_span
        else:
            avg_events_per_year = 0.0

        return EventStatistics(
            total_events=total_events,
            milestones_count=milestones_count,
            events_by_type=events_by_type,
            events_by_impact=events_by_impact,
            events_by_dasha=events_by_dasha,
            most_active_dasha=most_active_dasha,
            average_events_per_year=avg_events_per_year
        )
