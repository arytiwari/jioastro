"""
Life Threads API Endpoints
Timeline visualization with Dasha periods and life events
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.core.security import get_current_user
from app.core.supabase_client import SupabaseClient
from app.db.database import get_supabase_client
from app.services.life_threads_service import LifeThreadsService
from app.schemas.life_threads import (
    CreateLifeEventRequest,
    UpdateLifeEventRequest,
    LifeEvent,
    LifeEventsListResponse,
    TimelineResponse,
    EventStatistics,
    EventType
)

router = APIRouter()


@router.post("/events", response_model=LifeEvent, status_code=201)
async def create_life_event(
    request: CreateLifeEventRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Create a new life event

    - Maps event to active Dasha period automatically
    - Calculates astrological significance
    - Supports 15 event categories
    """
    service = LifeThreadsService(supabase)
    user_id = current_user["user_id"]

    try:
        return await service.create_life_event(user_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")


@router.get("/events/{event_id}", response_model=LifeEvent)
async def get_life_event(
    event_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Get a specific life event by ID"""
    service = LifeThreadsService(supabase)
    user_id = current_user["user_id"]

    event = await service.get_life_event(user_id, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@router.put("/events/{event_id}", response_model=LifeEvent)
async def update_life_event(
    event_id: str,
    request: UpdateLifeEventRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Update an existing life event"""
    service = LifeThreadsService(supabase)
    user_id = current_user["user_id"]

    try:
        return await service.update_life_event(user_id, event_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/events/{event_id}", status_code=204)
async def delete_life_event(
    event_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Delete a life event"""
    service = LifeThreadsService(supabase)
    user_id = current_user["user_id"]

    await service.delete_life_event(user_id, event_id)
    return None


@router.get("/events", response_model=LifeEventsListResponse)
async def list_life_events(
    profile_id: Optional[str] = Query(None, description="Filter by profile"),
    event_types: Optional[List[EventType]] = Query(None, description="Filter by event types"),
    start_date: Optional[date] = Query(None, description="Filter events after this date"),
    end_date: Optional[date] = Query(None, description="Filter events before this date"),
    milestones_only: bool = Query(False, description="Show only milestone events"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    List user's life events with filters

    - Filter by profile, event type, date range
    - Option to show only milestones
    - Paginated results
    """
    service = LifeThreadsService(supabase)
    user_id = current_user["user_id"]

    event_type_values = [et.value for et in event_types] if event_types else None

    events, total = await service.list_life_events(
        user_id=user_id,
        profile_id=profile_id,
        event_types=event_type_values,
        start_date=start_date,
        end_date=end_date,
        milestones_only=milestones_only,
        limit=limit,
        offset=offset
    )

    return LifeEventsListResponse(
        events=events,
        total_count=total,
        page=(offset // limit) + 1,
        page_size=limit,
        has_more=(offset + limit) < total
    )


@router.get("/timeline/{profile_id}", response_model=TimelineResponse)
async def get_dasha_timeline(
    profile_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Get complete Dasha timeline with life events

    - 120-year Vimshottari cycle
    - Events mapped to Mahadasha periods
    - Cached for 30 days
    - Includes event statistics
    """
    service = LifeThreadsService(supabase)
    user_id = current_user["user_id"]

    try:
        timeline = await service.get_dasha_timeline(user_id, profile_id)

        # Get milestones
        milestones = []
        for period in timeline.mahadasha_periods:
            milestones.extend([e for e in period.events if e.is_milestone])

        # Event distribution
        event_type_distribution = {}
        events_by_dasha = {}

        for period in timeline.mahadasha_periods:
            if period.events:
                events_by_dasha[period.planet] = events_by_dasha.get(period.planet, 0) + len(period.events)
                for event in period.events:
                    event_type_distribution[event.event_type.value] = \
                        event_type_distribution.get(event.event_type.value, 0) + 1

        return TimelineResponse(
            timeline=timeline,
            milestones=milestones[:10],  # Top 10 milestones
            event_type_distribution=event_type_distribution,
            events_by_dasha=events_by_dasha
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics", response_model=EventStatistics)
async def get_event_statistics(
    profile_id: Optional[str] = Query(None, description="Filter by profile"),
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Get statistics about user's life events

    - Total events, milestones count
    - Distribution by type, impact, Dasha
    - Most active periods
    - Average events per year
    """
    service = LifeThreadsService(supabase)
    user_id = current_user["user_id"]

    return await service.get_event_statistics(user_id, profile_id)
