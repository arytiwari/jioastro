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


class ShadbalaFromChartRequest(BaseModel):
    """Request for Shadbala calculation from chart data"""
    chart_data: dict = Field(..., description="Chart data with planets and houses")
    birth_datetime: Optional[str] = Field(None, description="Birth datetime (ISO format)")


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
        # Extract nested chart_data if present (FastAPI may pass entire body as chart_data)
        if "chart_data" in chart_data and isinstance(chart_data.get("chart_data"), dict):
            print(f"🔧 Remedies: Extracting nested chart_data")
            actual_chart_data = chart_data["chart_data"]
        else:
            actual_chart_data = chart_data

        print(f"🔍 Remedies: Chart data keys: {actual_chart_data.keys() if isinstance(actual_chart_data, dict) else 'NOT A DICT'}")

        remedies = remedy_service.generate_remedies(
            chart_data=actual_chart_data,
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
        # Extract nested chart_data if present (FastAPI may pass entire body as chart_data)
        print(f"🔍 Transits: chart_data type: {type(chart_data)}")
        print(f"🔍 Transits: chart_data keys: {list(chart_data.keys()) if isinstance(chart_data, dict) else 'NOT A DICT'}")
        if isinstance(chart_data, dict) and "chart_data" in chart_data:
            nested_data = chart_data.get("chart_data")
            if isinstance(nested_data, dict):
                print(f"🔧 Transits: Extracting nested chart_data")
                actual_chart_data = nested_data
            else:
                actual_chart_data = chart_data
        else:
            actual_chart_data = chart_data

        print(f"🔍 Transits: Chart data keys after extraction: {actual_chart_data.keys() if isinstance(actual_chart_data, dict) else 'NOT A DICT'}")

        # Parse transit date
        if transit_date:
            transit_dt = datetime.fromisoformat(transit_date)
        else:
            transit_dt = datetime.now()

        # Calculate transits
        transits = transit_service.calculate_current_transits(
            birth_chart=actual_chart_data,
            transit_date=transit_dt,
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone_str
        )

        print(f"🔍 Transits: Result keys: {transits.keys() if isinstance(transits, dict) else 'NOT A DICT'}")

        # Return transits data directly (not nested under "transits" key)
        # Frontend expects: response.data.transit_planets, response.data.significant_aspects, etc.
        return {
            "success": True,
            **transits  # Spread the transits dict into the response
        }

    except Exception as e:
        print(f"❌ Transits error: {str(e)}")
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

        # Extract nested chart_data if present (FastAPI may pass entire body as chart_data)
        print(f"🔍 DEBUG: chart_data type: {type(chart_data)}")
        print(f"🔍 DEBUG: chart_data keys: {list(chart_data.keys()) if isinstance(chart_data, dict) else 'NOT A DICT'}")
        print(f"🔍 DEBUG: Has 'chart_data' key: {'chart_data' in chart_data if isinstance(chart_data, dict) else False}")
        if isinstance(chart_data, dict) and "chart_data" in chart_data:
            nested_data = chart_data.get("chart_data")
            print(f"🔍 DEBUG: Nested chart_data type: {type(nested_data)}")
            print(f"🔍 DEBUG: Nested chart_data is dict: {isinstance(nested_data, dict)}")
            if isinstance(nested_data, dict):
                print(f"🔧 Extracting nested chart_data")
                actual_chart_data = nested_data
            else:
                actual_chart_data = chart_data
        else:
            actual_chart_data = chart_data

        print(f"🔍 Chart data keys after extraction: {actual_chart_data.keys() if isinstance(actual_chart_data, dict) else 'NOT A DICT'}")

        # Calculate Shadbala
        shadbala_result = shadbala_service.calculate_shadbala(
            chart_data=actual_chart_data,
            birth_datetime=birth_dt
        )

        print(f"🔍 Shadbala service returned: {shadbala_result}")
        print(f"🔍 Keys in result: {shadbala_result.keys() if isinstance(shadbala_result, dict) else 'Not a dict'}")

        # Transform the response to match frontend expectations
        # Convert shadbala_by_planet dict to planet_strengths array
        planet_strengths = []
        if "shadbala_by_planet" in shadbala_result:
            print(f"🔍 Found shadbala_by_planet with {len(shadbala_result['shadbala_by_planet'])} planets")
            for planet_name, strength_data in shadbala_result["shadbala_by_planet"].items():
                planet_strengths.append({
                    "planet": planet_name,
                    "total_shadbala": strength_data.get("total_shadbala", 0),
                    "required_shadbala": strength_data.get("required_shadbala", 0),
                    "percentage": strength_data.get("percentage", 0),
                    "strength_rating": strength_data.get("strength_rating", "Unknown"),
                    "components": strength_data.get("components", {})
                })
        else:
            print(f"⚠️ No 'shadbala_by_planet' key in result!")

        print(f"🔍 Returning {len(planet_strengths)} planet strengths")
        return {
            "success": True,
            "planet_strengths": planet_strengths
        }

    except Exception as e:
        print(f"Error calculating Shadbala: {str(e)}")
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
