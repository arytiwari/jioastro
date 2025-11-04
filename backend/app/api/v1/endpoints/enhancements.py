"""
API Endpoints for Phase 4 Enhancement Services
Remedies, Rectification, Transits, and Shadbala
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date, time
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.services.remedy_service import remedy_service
from app.services.rectification_service import rectification_service
from app.services.transit_service import transit_service
from app.services.shadbala_service import shadbala_service
from app.services.astrology import astrology_service


router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class RemedyRequest(BaseModel):
    """Request for remedy generation"""
    profile_id: str = Field(..., description="Birth profile ID")
    domain: Optional[str] = Field(None, description="Specific domain (career, relationships, etc.)")
    max_remedies: int = Field(5, ge=1, le=10, description="Maximum number of remedies")
    include_practical: bool = Field(True, description="Include modern alternatives")


class EventAnchor(BaseModel):
    """Life event for rectification"""
    event_type: str = Field(..., description="Type of event (marriage, job_start, etc.)")
    event_date: str = Field(..., description="Event date (ISO format)")
    event_significance: str = Field("medium", description="Significance (very_high, high, medium, low)")
    description: Optional[str] = Field(None, description="Optional description")


class RectificationRequest(BaseModel):
    """Request for birth time rectification"""
    name: str = Field(..., description="Person's name")
    birth_date: str = Field(..., description="Birth date (YYYY-MM-DD)")
    approximate_time: str = Field(..., description="Approximate birth time (HH:MM)")
    time_window_minutes: int = Field(30, ge=5, le=120, description="Uncertainty window in minutes")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone_str: str = Field("UTC", description="Timezone")
    city: str = Field(..., description="Birth city")
    event_anchors: List[EventAnchor] = Field(..., min_items=1, description="Life events for correlation")


class TransitRequest(BaseModel):
    """Request for transit calculation"""
    profile_id: str = Field(..., description="Birth profile ID")
    transit_date: Optional[str] = Field(None, description="Transit date (ISO format, default: now)")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Observer latitude (default: birth location)")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Observer longitude")
    timezone_str: Optional[str] = Field(None, description="Timezone")


class TransitTimelineRequest(BaseModel):
    """Request for transit timeline"""
    profile_id: str = Field(..., description="Birth profile ID")
    start_date: Optional[str] = Field(None, description="Start date (default: now)")
    end_date: Optional[str] = Field(None, description="End date (default: +30 days)")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    timezone_str: Optional[str] = Field(None)


class ShadbalaRequest(BaseModel):
    """Request for Shadbala calculation"""
    profile_id: str = Field(..., description="Birth profile ID")


# ============================================================================
# REMEDY ENDPOINTS
# ============================================================================

@router.post("/remedies/generate", response_model=dict)
async def generate_remedies(
    request: RemedyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate personalized Vedic remedies based on birth chart

    Returns remedies for weak/afflicted planets based on:
    - Current dasha period (highest priority)
    - Specific domain (career, relationships, etc.)
    - Planet strength analysis
    """
    try:
        # Get birth profile and chart
        # Note: In production, fetch from database
        # For now, we'll need chart data passed or profile lookup

        # This is a placeholder - in production, fetch profile from DB
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Profile lookup not yet implemented. Pass chart_data directly for now."
        )

        # Example implementation:
        # profile = await get_profile(request.profile_id, current_user['id'])
        # chart = astrology_service.calculate_birth_chart(...)
        #
        # remedies = remedy_service.generate_remedies(
        #     chart_data=chart,
        #     domain=request.domain,
        #     max_remedies=request.max_remedies,
        #     include_practical=request.include_practical
        # )
        #
        # return {
        #     "success": True,
        #     "remedies": remedies
        # }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/remedies/generate-from-chart", response_model=dict)
async def generate_remedies_from_chart(
    chart_data: dict,
    domain: Optional[str] = None,
    max_remedies: int = 5,
    include_practical: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate remedies directly from chart data (for testing/demo)
    """
    try:
        remedies = remedy_service.generate_remedies(
            chart_data=chart_data,
            domain=domain,
            max_remedies=max_remedies,
            include_practical=include_practical
        )

        return {
            "success": True,
            "remedies": remedies
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# RECTIFICATION ENDPOINTS
# ============================================================================

@router.post("/rectification/calculate", response_model=dict)
async def rectify_birth_time(
    request: RectificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Rectify birth time using event anchors and dasha correlation

    Requires:
    - Approximate birth time
    - Time window of uncertainty
    - At least 1 major life event with exact date

    Returns:
    - Top 3 candidate birth times
    - Confidence score (0-100%)
    - Event-dasha correlations
    """
    try:
        # Parse dates
        birth_date = datetime.fromisoformat(request.birth_date).date()
        approx_time = datetime.strptime(request.approximate_time, "%H:%M").time()

        # Convert event anchors to dict format
        event_anchors_list = [
            {
                "event_type": anchor.event_type,
                "event_date": anchor.event_date,
                "event_significance": anchor.event_significance,
                "description": anchor.description
            }
            for anchor in request.event_anchors
        ]

        # Run rectification
        result = rectification_service.rectify_birth_time(
            name=request.name,
            birth_date=birth_date,
            approximate_time=approx_time,
            time_window_minutes=request.time_window_minutes,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone_str=request.timezone_str,
            city=request.city,
            event_anchors=event_anchors_list
        )

        return {
            "success": True,
            "rectification": result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date/time format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# TRANSIT ENDPOINTS
# ============================================================================

@router.post("/transits/current", response_model=dict)
async def get_current_transits(
    request: TransitRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate current planetary transits and their effects on birth chart

    Returns:
    - Current planetary positions
    - Significant aspects (conjunction, square, trine, etc.)
    - House transits
    - Upcoming sign changes
    - Strength analysis
    """
    try:
        # Get birth chart
        # Note: In production, fetch from database using profile_id
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Profile lookup not yet implemented. Use /transits/current-from-chart for now."
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/transits/current-from-chart", response_model=dict)
async def get_current_transits_from_chart(
    chart_data: dict,
    transit_date: Optional[str] = None,
    latitude: float = 0.0,
    longitude: float = 0.0,
    timezone_str: str = "UTC",
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate transits directly from chart data (for testing/demo)
    """
    try:
        # Parse transit date
        if transit_date:
            transit_dt = datetime.fromisoformat(transit_date)
        else:
            transit_dt = datetime.now()

        # Calculate transits
        transits = transit_service.calculate_current_transits(
            birth_chart=chart_data,
            transit_date=transit_dt,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone_str
        )

        return {
            "success": True,
            "transits": transits
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/transits/timeline", response_model=dict)
async def get_transit_timeline(
    request: TransitTimelineRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate transit timeline for a date range

    Returns significant events (aspects, sign changes) over time
    """
    try:
        # Get birth chart
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Profile lookup not yet implemented. Use /transits/timeline-from-chart for now."
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/transits/timeline-from-chart", response_model=dict)
async def get_transit_timeline_from_chart(
    chart_data: dict,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    latitude: float = 0.0,
    longitude: float = 0.0,
    timezone_str: str = "UTC",
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate transit timeline directly from chart data (for testing/demo)
    """
    try:
        # Parse dates
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        else:
            start_dt = datetime.now()

        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        else:
            from datetime import timedelta
            end_dt = start_dt + timedelta(days=30)

        # Calculate timeline
        timeline = transit_service.calculate_transit_timeline(
            birth_chart=chart_data,
            start_date=start_dt,
            end_date=end_dt,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone_str
        )

        return {
            "success": True,
            "timeline": timeline
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# SHADBALA ENDPOINTS
# ============================================================================

@router.post("/shadbala/calculate", response_model=dict)
async def calculate_shadbala(
    request: ShadbalaRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate Shadbala (six-fold planetary strength)

    Returns:
    - Total Shadbala for each planet
    - 6 component strengths (Sthana, Dig, Kala, Chesta, Naisargika, Drik)
    - Strength rating (Exceptional to Very Weak)
    - Comparison against required minimums
    """
    try:
        # Get birth profile
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Profile lookup not yet implemented. Use /shadbala/calculate-from-chart for now."
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/shadbala/calculate-from-chart", response_model=dict)
async def calculate_shadbala_from_chart(
    chart_data: dict,
    birth_datetime: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate Shadbala directly from chart data (for testing/demo)
    """
    try:
        # Parse birth datetime if provided
        birth_dt = None
        if birth_datetime:
            birth_dt = datetime.fromisoformat(birth_datetime)

        # Calculate Shadbala
        shadbala = shadbala_service.calculate_shadbala(
            chart_data=chart_data,
            birth_datetime=birth_dt
        )

        return {
            "success": True,
            "shadbala": shadbala
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# COMBINED ENDPOINT (All Enhancements)
# ============================================================================

@router.post("/enhancements/all-from-chart", response_model=dict)
async def get_all_enhancements_from_chart(
    chart_data: dict,
    birth_datetime: Optional[str] = None,
    include_remedies: bool = True,
    include_transits: bool = True,
    include_shadbala: bool = True,
    remedy_domain: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all enhancements in one call (for comprehensive analysis)

    Returns:
    - Remedies (if enabled)
    - Current transits (if enabled)
    - Shadbala strengths (if enabled)
    """
    try:
        result = {}

        # Parse birth datetime
        birth_dt = None
        if birth_datetime:
            birth_dt = datetime.fromisoformat(birth_datetime)

        # Generate remedies
        if include_remedies:
            remedies = remedy_service.generate_remedies(
                chart_data=chart_data,
                domain=remedy_domain,
                max_remedies=5,
                include_practical=True
            )
            result['remedies'] = remedies

        # Calculate transits
        if include_transits:
            transits = transit_service.calculate_current_transits(
                birth_chart=chart_data,
                transit_date=datetime.now()
            )
            result['transits'] = transits

        # Calculate Shadbala
        if include_shadbala:
            shadbala = shadbala_service.calculate_shadbala(
                chart_data=chart_data,
                birth_datetime=birth_dt
            )
            result['shadbala'] = shadbala

        return {
            "success": True,
            "enhancements": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
