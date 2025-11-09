"""
Guided Rituals API Endpoints

This module provides endpoints for:
- Browsing and searching ritual templates
- Starting and managing ritual sessions
- Tracking user progress and history
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID

from app.core.security import get_current_user
from app.core.supabase_client import SupabaseClient
from app.db.database import get_supabase_client
from app.services.ritual_service import RitualService
from app.schemas.ritual import (
    RitualTemplateResponse,
    RitualTemplateSummary,
    RitualTemplateListResponse,
    RitualSessionStart,
    RitualSessionProgress,
    RitualSessionComplete,
    RitualSessionResponse,
    RitualSessionListResponse,
    RitualUserStats,
    RitualSearchParams,
    SessionFilterParams
)

router = APIRouter()


def get_ritual_service(supabase: SupabaseClient = Depends(get_supabase_client)) -> RitualService:
    """Dependency to get ritual service instance"""
    return RitualService(supabase)


# ============================================================================
# RITUAL TEMPLATE ENDPOINTS
# ============================================================================

@router.get("", response_model=RitualTemplateListResponse)
async def list_rituals(
    category: Optional[str] = Query(None, description="Filter by category"),
    deity: Optional[str] = Query(None, description="Filter by deity"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    List all available ritual templates with optional filters.

    - **category**: Filter by category (daily, special, remedial, festival, meditation)
    - **deity**: Filter by deity (Ganesha, Shiva, Lakshmi, etc.)
    - **difficulty**: Filter by difficulty (beginner, intermediate, advanced)
    - **limit**: Maximum number of results (1-100)
    - **offset**: Number of results to skip for pagination
    """
    try:
        # Apply filters if provided
        if category:
            rituals = await ritual_service.get_rituals_by_category(category, limit=limit)
        elif deity:
            rituals = await ritual_service.get_rituals_by_deity(deity, limit=limit)
        elif difficulty:
            rituals = await ritual_service.get_rituals_by_difficulty(difficulty, limit=limit)
        else:
            rituals = await ritual_service.get_all_rituals(limit=limit, offset=offset)

        # Add step_count to each ritual
        ritual_summaries = []
        for ritual in rituals:
            ritual_dict = dict(ritual)
            ritual_dict['step_count'] = len(ritual.get('steps', []))
            ritual_summaries.append(ritual_dict)

        return {
            "rituals": ritual_summaries,
            "total": len(ritual_summaries),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list rituals: {str(e)}"
        )


@router.get("/{ritual_id}", response_model=RitualTemplateResponse)
async def get_ritual(
    ritual_id: UUID,
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific ritual template.

    Returns complete ritual information including all steps, mantras, and instructions.
    """
    try:
        ritual = await ritual_service.get_ritual_by_id(ritual_id)

        if not ritual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ritual template {ritual_id} not found"
            )

        return ritual

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ritual: {str(e)}"
        )


@router.get("/search", response_model=RitualTemplateListResponse)
async def search_rituals(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Search rituals by name or description.

    - **q**: Search query string
    - **limit**: Maximum number of results (1-100)
    """
    try:
        rituals = await ritual_service.search_rituals(query=q, limit=limit)

        # Add step_count to each ritual
        ritual_summaries = []
        for ritual in rituals:
            ritual_dict = dict(ritual)
            ritual_dict['step_count'] = len(ritual.get('steps', []))
            ritual_summaries.append(ritual_dict)

        return {
            "rituals": ritual_summaries,
            "total": len(ritual_summaries),
            "limit": limit,
            "offset": 0
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search rituals: {str(e)}"
        )


# ============================================================================
# RITUAL SESSION ENDPOINTS
# ============================================================================

@router.post("/{ritual_id}/start", response_model=RitualSessionResponse)
async def start_ritual(
    ritual_id: UUID,
    session_data: RitualSessionStart,
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Start a new ritual session.

    Creates a new session for the specified ritual template and returns the session details.
    """
    try:
        user_id = UUID(current_user["user_id"])

        # Verify ritual template exists
        ritual = await ritual_service.get_ritual_by_id(session_data.ritual_template_id)
        if not ritual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ritual template {session_data.ritual_template_id} not found"
            )

        # Start session
        session = await ritual_service.start_ritual_session(
            user_id=user_id,
            ritual_template_id=session_data.ritual_template_id,
            notes=session_data.notes
        )

        return session

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start ritual session: {str(e)}"
        )


@router.put("/sessions/{session_id}/progress", response_model=RitualSessionResponse)
async def update_progress(
    session_id: UUID,
    progress_data: RitualSessionProgress,
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Update the progress of a ritual session.

    Updates the current step number for the session.
    """
    try:
        user_id = UUID(current_user["user_id"])

        session = await ritual_service.update_progress(
            session_id=session_id,
            user_id=user_id,
            current_step=progress_data.current_step
        )

        return session

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update progress: {str(e)}"
        )


@router.post("/sessions/{session_id}/pause", response_model=RitualSessionResponse)
async def pause_ritual(
    session_id: UUID,
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Pause a ritual session.

    Marks the session as paused so it can be resumed later.
    """
    try:
        user_id = UUID(current_user["user_id"])

        session = await ritual_service.pause_ritual(
            session_id=session_id,
            user_id=user_id
        )

        return session

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause ritual: {str(e)}"
        )


@router.post("/sessions/{session_id}/resume", response_model=RitualSessionResponse)
async def resume_ritual(
    session_id: UUID,
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Resume a paused ritual session.

    Changes session status from paused back to in_progress.
    """
    try:
        user_id = UUID(current_user["user_id"])

        session = await ritual_service.resume_ritual(
            session_id=session_id,
            user_id=user_id
        )

        return session

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume ritual: {str(e)}"
        )


@router.post("/sessions/{session_id}/complete", response_model=RitualSessionResponse)
async def complete_ritual(
    session_id: UUID,
    completion_data: RitualSessionComplete,
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a ritual session as completed.

    Optionally provide a rating (1-5 stars) and completion notes.
    """
    try:
        user_id = UUID(current_user["user_id"])

        session = await ritual_service.complete_ritual(
            session_id=session_id,
            user_id=user_id,
            rating=completion_data.rating,
            notes=completion_data.notes
        )

        return session

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete ritual: {str(e)}"
        )


@router.post("/sessions/{session_id}/abandon", response_model=RitualSessionResponse)
async def abandon_ritual(
    session_id: UUID,
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a ritual session as abandoned.

    Use this when a ritual session is stopped without completion.
    """
    try:
        user_id = UUID(current_user["user_id"])

        session = await ritual_service.abandon_ritual(
            session_id=session_id,
            user_id=user_id
        )

        return session

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to abandon ritual: {str(e)}"
        )


@router.get("/sessions/history", response_model=RitualSessionListResponse)
async def get_session_history(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's ritual session history.

    - **status**: Optional filter by status (in_progress, completed, paused, abandoned)
    - **limit**: Maximum number of results (1-100)
    - **offset**: Number of results to skip for pagination
    """
    try:
        user_id = UUID(current_user["user_id"])

        sessions = await ritual_service.get_user_ritual_history(
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset
        )

        return {
            "sessions": sessions,
            "total": len(sessions),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session history: {str(e)}"
        )


@router.get("/sessions/stats", response_model=RitualUserStats)
async def get_user_stats(
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's ritual practice statistics.

    Returns overall statistics including total sessions, completion rate, average rating, etc.
    """
    try:
        user_id = UUID(current_user["user_id"])

        stats = await ritual_service.get_user_stats(user_id=user_id)

        return stats

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=RitualSessionResponse)
async def get_session(
    session_id: UUID,
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get details of a specific ritual session.

    Returns session information including current progress.
    """
    try:
        user_id = UUID(current_user["user_id"])

        session = await ritual_service.get_session_by_id(
            session_id=session_id,
            user_id=user_id
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        return session

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    ritual_service: RitualService = Depends(get_ritual_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a ritual session.

    Permanently removes the session from the database.
    """
    try:
        user_id = UUID(current_user["user_id"])

        await ritual_service.delete_session(
            session_id=session_id,
            user_id=user_id
        )

        return None

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )
