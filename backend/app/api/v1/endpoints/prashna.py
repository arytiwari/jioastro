"""
API endpoints for Prashna (Horary Astrology).

Provides:
- Prashna chart calculation and analysis
- Save/retrieve Prashna questions
- Question-based astrological answers

Database: Uses Supabase REST API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.core.security import get_current_user
from app.core.supabase_client import SupabaseClient
from app.schemas import prashna as schemas
from app.services.prashna_service import prashna_service
from app.db.database import get_supabase_client

router = APIRouter()


@router.post("/analyze", response_model=schemas.PrashnaChartResponse, status_code=status.HTTP_200_OK)
async def analyze_prashna(
    request: schemas.PrashnaRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze a horary (Prashna) question with AI-powered detailed answer.

    Calculates chart for the moment the question is asked and provides:
    - Ascendant (Lagna) analysis
    - Moon position (most important in Prashna)
    - Relevant houses for question type
    - Planetary strengths and combinations
    - AI-powered detailed answer with timing, remedies, and confidence level
    """
    try:
        # Use AI-enhanced analysis
        analysis = await prashna_service.analyze_prashna_with_ai(
            question=request.question,
            question_type=request.question_type,
            query_datetime=request.datetime,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone_str=request.timezone
        )
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze Prashna: {str(e)}"
        )


@router.post("/save", response_model=schemas.SavedPrashnaResponse, status_code=status.HTTP_201_CREATED)
async def save_prashna(
    request: schemas.SavePrashnaRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Save a Prashna analysis for future reference.
    """
    try:
        # Create new Prashna record
        prashna_data = {
            "user_id": current_user["user_id"],
            "question": request.question,
            "question_type": request.question_type,
            "query_datetime": request.query_datetime.isoformat(),
            "latitude": request.latitude,
            "longitude": request.longitude,
            "timezone": request.timezone,
            "prashna_chart": request.prashna_chart,
            "analysis": request.analysis,
            "notes": request.notes
        }

        result = await supabase.insert("prashnas", prashna_data)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save Prashna: {str(e)}"
        )


@router.get("/list", response_model=schemas.PrashnaListResponse, status_code=status.HTTP_200_OK)
async def list_prashnas(
    limit: int = 10,
    offset: int = 0,
    question_type: str = None,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    List all saved Prashnas for the current user.

    Optional filters:
    - question_type: Filter by question type (career, relationship, etc.)
    - limit: Number of results (default 10)
    - offset: Pagination offset (default 0)
    """
    import logging
    import traceback
    logger = logging.getLogger(__name__)

    try:
        user_id = current_user["user_id"]
        logger.info(f"Listing prashnas for user: {user_id}")

        # Build filters
        filters = {"user_id": user_id}
        if question_type:
            filters["question_type"] = question_type

        logger.info(f"Filters: {filters}")

        # Get total count
        logger.info("Getting count...")
        try:
            total = await supabase.count("prashnas", filters=filters)
            logger.info(f"Count result: {total}")
        except Exception as count_error:
            logger.error(f"Count error: {type(count_error).__name__}: {count_error}")
            logger.error(traceback.format_exc())
            raise

        # Get paginated results
        logger.info("Getting prashnas list...")
        try:
            prashnas = await supabase.select(
                "prashnas",
                filters=filters,
                order="created_at.desc",
                limit=limit,
                offset=offset
            )
            logger.info(f"Got {len(prashnas) if prashnas else 0} prashnas")
        except Exception as select_error:
            logger.error(f"Select error: {type(select_error).__name__}: {select_error}")
            logger.error(traceback.format_exc())
            raise

        return {
            "prashnas": prashnas or [],
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Failed to list Prashnas: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list Prashnas: {str(e)}"
        )


@router.get("/{prashna_id}", response_model=schemas.SavedPrashnaResponse, status_code=status.HTTP_200_OK)
async def get_prashna(
    prashna_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Get a specific Prashna by ID.
    """
    try:
        user_id = current_user["user_id"]

        prashna = await supabase.select(
            "prashnas",
            filters={"id": str(prashna_id), "user_id": user_id},
            single=True
        )

        if not prashna:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prashna not found"
            )

        return prashna

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Prashna: {str(e)}"
        )


@router.delete("/{prashna_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prashna(
    prashna_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Delete a Prashna by ID.
    """
    try:
        user_id = current_user["user_id"]

        # Check if prashna exists and belongs to user
        prashna = await supabase.select(
            "prashnas",
            filters={"id": str(prashna_id), "user_id": user_id},
            single=True
        )

        if not prashna:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prashna not found"
            )

        # Delete the prashna
        await supabase.delete(
            "prashnas",
            filters={"id": str(prashna_id), "user_id": user_id}
        )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Prashna: {str(e)}"
        )
