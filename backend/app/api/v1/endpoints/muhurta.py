"""
API endpoints for Muhurta (Electional Astrology).

Provides:
- Panchang calculations
- Hora calculations
- Auspicious time finder for various activities
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
import os

from app.core.security import get_current_user
from app.schemas import muhurta as schemas
from app.services.muhurta_service import muhurta_service

router = APIRouter()


@router.post("/panchang", response_model=schemas.PanchangResponse, status_code=status.HTTP_200_OK)
async def get_panchang(
    request: schemas.PanchangRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get Panchang (5 elements) for a specific date/time.

    Calculates:
    - Tithi (Lunar Day)
    - Nakshatra (Lunar Mansion)
    - Yoga (Sun-Moon combination)
    - Karana (Half Tithi)
    - Vara (Weekday)
    """
    try:
        panchang = muhurta_service.calculate_panchang(
            dt=request.datetime,
            latitude=request.latitude,
            longitude=request.longitude
        )
        return panchang
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate Panchang: {str(e)}"
        )


@router.post("/hora", response_model=schemas.HoraResponse, status_code=status.HTTP_200_OK)
async def get_hora(
    request: schemas.HoraRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get current Hora (Planetary Hour) for a specific time.

    Each day/night divided into 12 horas, each ruled by a planet.
    """
    try:
        hora = muhurta_service.calculate_hora(
            dt=request.datetime,
            latitude=request.latitude,
            longitude=request.longitude
        )

        if "error" in hora:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=hora["error"]
            )

        return hora
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate Hora: {str(e)}"
        )


@router.post("/hora/daily-table", response_model=schemas.DailyHoraTableResponse, status_code=status.HTTP_200_OK)
async def get_daily_hora_table(
    request: schemas.DailyHoraTableRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get complete Hora table for a day (all 24 horas).

    Shows planetary hours from sunrise to next sunrise.
    """
    try:
        # Convert date to datetime
        dt = datetime.combine(request.date, datetime.min.time())

        horas = muhurta_service.get_daily_hora_table(
            date=dt,
            latitude=request.latitude,
            longitude=request.longitude
        )

        return {
            "date": request.date.isoformat(),
            "horas": horas,
            "total_horas": len(horas)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hora table: {str(e)}"
        )


@router.post("/find-muhurta", response_model=schemas.MuhurtaFinderResponse, status_code=status.HTTP_200_OK)
async def find_muhurta(
    request: schemas.MuhurtaFinderRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Find auspicious times for a specific activity.

    Activity types:
    - marriage: Wedding ceremonies
    - business: Starting a business or venture
    - travel: Journey or travel
    - property: Buying/selling property
    - surgery: Medical procedures

    Returns top muhurtas within date range.
    """
    try:
        # Convert dates to datetime
        start_dt = datetime.combine(request.start_date, datetime.min.time())
        end_dt = datetime.combine(request.end_date, datetime.max.time())

        # Validate date range
        if start_dt > end_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )

        # Limit search to 90 days
        if (end_dt - start_dt).days > 90:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search range cannot exceed 90 days"
            )

        # Find muhurtas based on activity type
        if request.activity_type == "marriage":
            results = muhurta_service.find_marriage_muhurta(
                start_dt, end_dt, request.latitude, request.longitude, request.max_results
            )
        elif request.activity_type == "business":
            results = muhurta_service.find_business_start_muhurta(
                start_dt, end_dt, request.latitude, request.longitude, request.max_results
            )
        elif request.activity_type == "travel":
            results = muhurta_service.find_travel_muhurta(
                start_dt, end_dt, request.latitude, request.longitude, request.max_results
            )
        elif request.activity_type == "property":
            results = muhurta_service.find_property_purchase_muhurta(
                start_dt, end_dt, request.latitude, request.longitude, request.max_results
            )
        elif request.activity_type == "surgery":
            results = muhurta_service.find_surgery_muhurta(
                start_dt, end_dt, request.latitude, request.longitude, request.max_results
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid activity type: {request.activity_type}. Must be one of: marriage, business, travel, property, surgery"
            )

        return {
            "activity_type": request.activity_type,
            "search_period": {
                "start": request.start_date.isoformat(),
                "end": request.end_date.isoformat()
            },
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            "results": results,
            "total_found": len(results),
            "message": None if results else "No auspicious times found in the specified period. Try expanding the date range."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find muhurta: {str(e)}"
        )


@router.post("/best-time-today", response_model=schemas.BestTimeTodayResponse, status_code=status.HTTP_200_OK)
async def get_best_time_today(
    request: schemas.BestTimeTodayRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Find best time for activity TODAY.

    Quick lookup for immediate planning.
    Returns top 3 times if available.
    """
    try:
        result = muhurta_service.find_best_time_today(
            activity_type=request.activity_type,
            latitude=request.latitude,
            longitude=request.longitude
        )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find best time: {str(e)}"
        )


# ============================================================================
# AI-POWERED DECISION COPILOT
# ============================================================================

@router.post("/decision-copilot", response_model=schemas.DecisionCopilotResponse, status_code=status.HTTP_200_OK)
async def get_decision_copilot_guidance(
    request: schemas.DecisionCopilotRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    AI-powered Decision Copilot for choosing the best auspicious time.

    Combines:
    - Traditional Muhurta calculations (Panchang, Hora)
    - User's birth chart analysis (optional - provide chart_id)
    - Current dashas and transits
    - GPT-4 powered comparison and recommendation

    Returns:
    - Multiple time options with AI analysis (pros, cons, ratings)
    - Best time recommendation with reasoning
    - Personalized guidance based on birth chart (if provided)

    Activity types:
    - marriage: Wedding ceremonies
    - business: Starting a business or venture
    - travel: Journey or travel
    - property: Buying/selling property
    - surgery: Medical procedures
    """
    try:
        # Convert dates to datetime
        start_dt = datetime.combine(request.start_date, datetime.min.time())
        end_dt = datetime.combine(request.end_date, datetime.max.time())

        # Validate date range
        if start_dt > end_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )

        # Limit search to 90 days
        if (end_dt - start_dt).days > 90:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search range cannot exceed 90 days"
            )

        # Fetch user's birth chart if chart_id provided
        user_chart_data = None
        user_dasha = None

        if request.chart_id:
            try:
                # Import here to avoid circular imports
                from app.core.supabase_client import SupabaseClient
                from app.db.database import get_supabase_client

                # Get Supabase client
                supabase = SupabaseClient(
                    url=os.getenv("SUPABASE_URL"),
                    key=os.getenv("SUPABASE_KEY")
                )

                # Fetch chart data
                chart = await supabase.select(
                    "charts",
                    filters={"id": request.chart_id, "user_id": current_user["user_id"]},
                    single=True
                )

                if chart:
                    user_chart_data = chart.get("chart_data")
                    # TODO: Fetch current dasha from chart data or calculate
                    # user_dasha = chart.get("dasha_data")

            except Exception as chart_error:
                # Log error but continue without personalization
                import logging
                logging.warning(f"Failed to fetch chart for personalization: {str(chart_error)}")

        # Get AI-powered decision guidance
        result = await muhurta_service.find_muhurta_with_ai_guidance(
            activity_type=request.activity_type,
            start_date=start_dt,
            end_date=end_dt,
            latitude=request.latitude,
            longitude=request.longitude,
            user_chart_data=user_chart_data,
            user_dasha=user_dasha,
            max_results=request.max_results
        )

        # Check if error occurred
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate decision copilot guidance: {str(e)}"
        )


# ============================================================================
# PUBLIC ENDPOINTS (NO AUTH REQUIRED)
# ============================================================================

@router.post("/public/panchang", response_model=schemas.PanchangResponse, status_code=status.HTTP_200_OK)
async def get_panchang_public(request: schemas.PanchangRequest):
    """
    Get Panchang without authentication (public endpoint).

    Limited to current date only for anonymous users.
    """
    try:
        # Limit to current date for public access
        today = datetime.now().date()
        if request.datetime.date() != today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Public access limited to current date only. Please sign in for full access."
            )

        panchang = muhurta_service.calculate_panchang(
            dt=request.datetime,
            latitude=request.latitude,
            longitude=request.longitude
        )
        return panchang
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate Panchang: {str(e)}"
        )


@router.post("/public/hora", response_model=schemas.HoraResponse, status_code=status.HTTP_200_OK)
async def get_hora_public(request: schemas.HoraRequest):
    """
    Get current Hora without authentication (public endpoint).

    Limited to current date only for anonymous users.
    """
    try:
        # Limit to current date for public access
        today = datetime.now().date()
        if request.datetime.date() != today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Public access limited to current date only. Please sign in for full access."
            )

        hora = muhurta_service.calculate_hora(
            dt=request.datetime,
            latitude=request.latitude,
            longitude=request.longitude
        )

        if "error" in hora:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=hora["error"]
            )

        return hora
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate Hora: {str(e)}"
        )
