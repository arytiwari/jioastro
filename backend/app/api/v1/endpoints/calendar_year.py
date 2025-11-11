"""
API endpoints for Calendar Year Predictions.

Provides transit-based annual predictions for calendar years (Jan 1 - Dec 31),
separate from Varshaphal (birthday to birthday).

Uses Supabase REST API for all database operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time
import logging

from app.core.security import get_current_user
from app.core.supabase_client import supabase_client
from app.schemas import calendar_year as schemas
from app.services.calendar_year_service import calendar_year_service
from app.services.vedic_astrology_accurate import AccurateVedicAstrology

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=schemas.CalendarYearResponse, status_code=status.HTTP_200_OK)
async def generate_calendar_year(
    request: schemas.CalendarYearRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate Calendar Year Predictions for a profile.

    Uses Supabase REST API for all database operations.

    Calculates:
    - Monthly predictions (January - December)
    - Major planetary transits (Jupiter, Saturn, Rahu/Ketu)
    - Eclipse predictions (Solar and Lunar)
    - Best/worst months identification
    - Opportunities and challenges
    - Year overview and remedies

    Args:
        request: CalendarYearRequest with profile_id and target_year
        current_user: Current authenticated user

    Returns:
        CalendarYearResponse with complete year predictions
    """
    user_id = current_user["user_id"]
    logger.info(
        f"Generating Calendar Year predictions for user {user_id}, "
        f"profile {request.profile_id}, year {request.target_year}"
    )

    try:
        # Validate profile ownership
        profile = await _get_profile(request.profile_id, user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found or not accessible"
            )

        # Get natal chart
        natal_chart = await _get_natal_chart(profile)
        if not natal_chart:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate natal chart"
            )

        # Generate calendar year predictions
        predictions = calendar_year_service.generate_calendar_year_predictions(
            natal_chart=natal_chart,
            target_year=request.target_year,
            birth_lat=float(profile["birth_lat"]),
            birth_lon=float(profile["birth_lon"])
        )

        # Format response
        response_data = {
            "profile_id": request.profile_id,
            "target_year": request.target_year,
            "year_start": f"{request.target_year}-01-01",
            "year_end": f"{request.target_year}-12-31",
            "monthly_predictions": predictions["monthly_predictions"],
            "major_transits": predictions["major_transits"],
            "eclipses": predictions["eclipses"],
            "best_months": predictions["best_months"],
            "worst_months": predictions["worst_months"],
            "year_overview": predictions["year_overview"],
            "generated_at": datetime.utcnow()
        }

        logger.info(
            f"Successfully generated Calendar Year predictions for "
            f"profile {request.profile_id}, year {request.target_year}"
        )

        return schemas.CalendarYearResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating Calendar Year predictions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Calendar Year predictions: {str(e)}"
        )


# Helper functions

async def _get_profile(profile_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get profile and verify ownership using Supabase REST API."""
    try:
        profile = await supabase_client.select(
            table="profiles",
            filters={"id": profile_id, "user_id": user_id},
            single=True
        )
        return profile
    except Exception as e:
        logger.error(f"Error fetching profile: {e}", exc_info=True)
        return None


async def _get_natal_chart(profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get or calculate natal chart for the profile.

    Args:
        profile: Profile data from database

    Returns:
        Natal chart data or None on error
    """
    try:
        # Try to get from existing chart
        chart = await supabase_client.select(
            table="charts",
            filters={"profile_id": profile["id"]},
            single=True
        )

        if chart and chart.get("chart_data"):
            return chart["chart_data"]

        # Calculate on-the-fly using AccurateVedicAstrology
        astrology = AccurateVedicAstrology()

        # Parse date and time from profile (they come as strings from REST API)
        birth_date_str = profile["birth_date"] if isinstance(profile["birth_date"], str) else profile["birth_date"].strftime("%Y-%m-%d")
        birth_time_str = profile["birth_time"] if isinstance(profile["birth_time"], str) else profile["birth_time"].strftime("%H:%M:%S")

        chart_data = astrology.generate_birth_chart(
            date=birth_date_str,
            time=birth_time_str,
            lat=float(profile["birth_lat"]),
            lon=float(profile["birth_lon"]),
            tz_str=profile.get("birth_timezone") or "UTC"
        )

        return chart_data

    except Exception as e:
        logger.error(f"Error calculating natal chart: {e}", exc_info=True)
        return None
