"""
Remedy Planner API Endpoints
Habit tracking with streaks and achievements
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.core.security import get_current_user
from app.core.supabase_client import SupabaseClient
from app.db.database import get_supabase_client
from app.services.remedy_planner_service import RemedyPlannerService
from app.schemas.remedy_planner import (
    SearchRemediesRequest,
    AssignRemedyRequest,
    UpdateAssignmentRequest,
    TrackRemedyRequest,
    RemedyCatalogItem,
    RemedyAssignment,
    RemedyTracking,
    RemediesSearchResponse,
    AssignmentsListResponse,
    TrackingHistoryResponse,
    DashboardStats,
    CalendarView,
    AssignmentStatus
)

router = APIRouter()


# Remedy Catalog Endpoints

@router.post("/remedies/search", response_model=RemediesSearchResponse)
async def search_remedies(
    request: SearchRemediesRequest,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Search remedies catalog

    - 40+ authentic Vedic remedies
    - Filter by planet, dosha, type, difficulty, cost
    - Public endpoint (no auth required)
    """
    service = RemedyPlannerService(supabase)

    remedies, total = await service.search_remedies(request)

    return RemediesSearchResponse(
        remedies=remedies,
        total_count=total,
        page=(request.offset // request.limit) + 1,
        page_size=request.limit,
        has_more=(request.offset + request.limit) < total
    )


@router.get("/remedies/{remedy_id}", response_model=RemedyCatalogItem)
async def get_remedy(
    remedy_id: str,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Get detailed information about a specific remedy"""
    service = RemedyPlannerService(supabase)

    remedy = await service.get_remedy(remedy_id)
    if not remedy:
        raise HTTPException(status_code=404, detail="Remedy not found")

    return remedy


# Assignment Endpoints

@router.post("/assignments", response_model=RemedyAssignment, status_code=201)
async def assign_remedy(
    request: AssignRemedyRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Assign a remedy to yourself

    - Set custom instructions and schedule
    - Configure reminders
    - Starts in pending status
    """
    service = RemedyPlannerService(supabase)
    user_id = current_user["sub"]

    try:
        return await service.assign_remedy(user_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/assignments", response_model=AssignmentsListResponse)
async def list_assignments(
    status: Optional[AssignmentStatus] = Query(None, description="Filter by status"),
    profile_id: Optional[str] = Query(None, description="Filter by profile"),
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    List your remedy assignments

    - Filter by status or profile
    - Includes remedy details
    - Shows progress stats
    """
    service = RemedyPlannerService(supabase)
    user_id = current_user["sub"]

    assignments, total, active, completed = await service.list_assignments(
        user_id, status, profile_id
    )

    return AssignmentsListResponse(
        assignments=assignments,
        total_count=total,
        active_count=active,
        completed_count=completed
    )


@router.get("/assignments/{assignment_id}", response_model=RemedyAssignment)
async def get_assignment(
    assignment_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Get assignment details with remedy information"""
    service = RemedyPlannerService(supabase)
    user_id = current_user["sub"]

    try:
        return await service.get_assignment(user_id, assignment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/assignments/{assignment_id}", response_model=RemedyAssignment)
async def update_assignment(
    assignment_id: str,
    request: UpdateAssignmentRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Update assignment settings

    - Change status (active, paused, completed)
    - Update reminders
    - Add feedback and ratings
    """
    service = RemedyPlannerService(supabase)
    user_id = current_user["sub"]

    try:
        return await service.update_assignment(user_id, assignment_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/assignments/{assignment_id}", status_code=204)
async def delete_assignment(
    assignment_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Delete an assignment"""
    service = RemedyPlannerService(supabase)
    user_id = current_user["sub"]

    await service.delete_assignment(user_id, assignment_id)
    return None


# Tracking Endpoints

@router.post("/tracking", response_model=RemedyTracking, status_code=201)
async def track_remedy(
    request: TrackRemedyRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Track daily remedy completion

    - Mark as completed with quality rating
    - Record mood before/after
    - Automatic streak calculation
    - Achievement unlocking
    """
    service = RemedyPlannerService(supabase)
    user_id = current_user["sub"]

    try:
        return await service.track_remedy(user_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tracking/{assignment_id}/history")
async def get_tracking_history(
    assignment_id: str,
    limit: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Get tracking history for an assignment"""
    service = RemedyPlannerService(supabase)
    user_id = current_user["sub"]

    try:
        tracking = await service.get_tracking_history(user_id, assignment_id, limit)
        return {"tracking_records": tracking}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Dashboard & Analytics

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Get remedy planner dashboard

    - Today's completions
    - Active streaks with at-risk detection
    - Completion rates (week/month)
    - Recent achievements
    - Overall statistics
    """
    service = RemedyPlannerService(supabase)
    user_id = current_user["sub"]

    return await service.get_dashboard_stats(user_id)


@router.get("/calendar/{assignment_id}", response_model=CalendarView)
async def get_calendar_view(
    assignment_id: str,
    year: int = Query(..., ge=2020, le=2030),
    month: int = Query(..., ge=1, le=12),
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Get monthly calendar view

    - Daily completion status
    - Month completion rate
    - Visual calendar data
    """
    service = RemedyPlannerService(supabase)
    user_id = current_user["sub"]

    try:
        return await service.get_calendar_view(user_id, assignment_id, year, month)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
