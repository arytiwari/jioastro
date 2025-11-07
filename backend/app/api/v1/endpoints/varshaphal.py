"""
API endpoints for Varshaphal (Annual Predictions).

UPDATED: Uses Supabase REST API instead of direct PostgreSQL connections.
No database session (AsyncSession) dependency required.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import hashlib
import logging

from app.core.security import get_current_user
from app.core.supabase_client import supabase_client
from app.schemas import varshaphal as schemas
from app.services.varshaphal_service import varshaphal_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Cache TTL: 30 days (Varshaphal is valid for the year)
VARSHAPHAL_CACHE_TTL_SECONDS = 30 * 24 * 60 * 60


@router.post("/generate", response_model=schemas.VarshapalResponse, status_code=status.HTTP_200_OK)
async def generate_varshaphal(
    request: schemas.VarshapalGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate Varshaphal (Annual Predictions) for a profile.

    Uses Supabase REST API for all database operations.

    Calculates:
    - Solar Return Chart (exact Sun return moment)
    - Varshaphal Yogas (16 special annual yogas)
    - Patyayini Dasha (annual dasha system)
    - Sahams (50+ sensitive points)
    - Month-by-month predictions
    - Best/worst periods
    - Remedies
    """
    user_id = current_user["user_id"]
    logger.info(f"Generating Varshaphal for user {user_id}, profile {request.profile_id}, year {request.target_year}")

    try:
        # Validate profile ownership
        profile = await _get_profile(request.profile_id, user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found or not accessible"
            )

        # Check for cached Varshaphal
        if not request.force_refresh:
            cached = await _get_cached_varshaphal(user_id, request.profile_id, request.target_year)
            if cached:
                logger.info(f"Returning cached Varshaphal {cached['varshaphal_id']}")
                return cached

        # Calculate natal Sun position (needed for solar return)
        natal_sun_longitude = await _get_natal_sun_longitude(profile)

        # Calculate Solar Return Chart
        from datetime import datetime, date, time

        # Parse date and time from REST API response
        birth_date = profile["birth_date"] if isinstance(profile["birth_date"], date) else datetime.fromisoformat(profile["birth_date"]).date()
        birth_time = profile["birth_time"] if isinstance(profile["birth_time"], time) else datetime.fromisoformat(profile["birth_time"]).time()
        birth_datetime = datetime.combine(birth_date, birth_time)

        solar_return_chart = varshaphal_service.calculate_solar_return_chart(
            natal_sun_longitude=natal_sun_longitude,
            birth_date=birth_datetime,
            target_year=request.target_year,
            latitude=float(profile["birth_lat"]),
            longitude=float(profile["birth_lon"]),
            timezone_offset=0  # Using UTC
        )

        # Calculate Patyayini Dasha
        patyayini_dasha = varshaphal_service.calculate_patyayini_dasha(
            solar_return_chart=solar_return_chart,
            target_year=request.target_year
        )

        # Calculate Sahams
        sahams = varshaphal_service.calculate_sahams(
            solar_return_chart=solar_return_chart
        )

        # Generate Annual Interpretation
        annual_interpretation = varshaphal_service.generate_annual_interpretation(
            solar_return_chart=solar_return_chart,
            patyayini_dasha=patyayini_dasha,
            sahams=sahams,
            natal_chart_data=None  # Can be enhanced with full natal chart
        )

        # Store in database
        varshaphal_record = await _store_varshaphal(
            user_id=user_id,
            profile_id=request.profile_id,
            target_year=request.target_year,
            natal_sun_longitude=natal_sun_longitude,
            solar_return_chart=solar_return_chart,
            patyayini_dasha=patyayini_dasha,
            sahams=sahams,
            annual_interpretation=annual_interpretation
        )

        # Format response
        return await _format_varshaphal_response(varshaphal_record, is_cached=False)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating Varshaphal: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Varshaphal: {str(e)}"
        )


@router.get("/{varshaphal_id}", response_model=schemas.VarshapalResponse, status_code=status.HTTP_200_OK)
async def get_varshaphal(
    varshaphal_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific Varshaphal by ID.

    Uses Supabase REST API for database operations.
    """
    user_id = current_user["user_id"]
    try:
        varshaphal = await supabase_client.select(
            table="varshaphal_data",
            filters={"id": varshaphal_id, "user_id": user_id},
            single=True
        )

        if not varshaphal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Varshaphal not found"
            )

        return await _format_varshaphal_response(varshaphal, is_cached=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Varshaphal: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Varshaphal: {str(e)}"
        )


@router.post("/list", response_model=schemas.VarshapalListResponse, status_code=status.HTTP_200_OK)
async def list_varshaphals(
    request: schemas.VarshapalHistoryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    List all Varshaphal calculations for the current user.

    Uses Supabase REST API for database operations.
    Can filter by profile_id.
    """
    user_id = current_user["user_id"]
    try:
        # Build filters
        filters = {"user_id": user_id}
        if request.profile_id:
            filters["profile_id"] = request.profile_id

        # Get varshaphals with pagination
        varshaphals = await supabase_client.select(
            table="varshaphal_data",
            filters=filters,
            order="target_year.desc",
            limit=request.limit,
            offset=request.offset
        )

        if not varshaphals:
            varshaphals = []

        # Get unique profile IDs
        profile_ids = list(set(str(v["profile_id"]) for v in varshaphals))

        # Get profiles
        profiles_dict = {}
        for pid in profile_ids:
            profile = await supabase_client.select(
                table="profiles",
                filters={"id": pid},
                single=True
            )
            if profile:
                profiles_dict[pid] = profile

        # Format results
        items = []
        for varshaphal in varshaphals:
            profile = profiles_dict.get(str(varshaphal["profile_id"]))

            # Check if expired
            now = datetime.now(timezone.utc)
            expires_at = datetime.fromisoformat(varshaphal["expires_at"].replace('Z', '+00:00'))
            is_expired = now > expires_at

            items.append(schemas.VarshapalListItem(
                varshaphal_id=varshaphal["id"],
                profile_id=varshaphal["profile_id"],
                profile_name=profile["name"] if profile else "Unknown",
                target_year=varshaphal["target_year"],
                generated_at=varshaphal["generated_at"],
                expires_at=varshaphal["expires_at"],
                is_expired=is_expired,
                overall_quality=varshaphal["annual_interpretation"].get("overall_quality", "Unknown"),
                yogas_count=len(varshaphal["solar_return_chart"].get("yogas", []))
            ))

        # Count total
        all_varshaphals = await supabase_client.select(
            table="varshaphal_data",
            filters=filters
        )
        total = len(all_varshaphals) if all_varshaphals else 0

        return schemas.VarshapalListResponse(
            varshaphals=items,
            total=total,
            limit=request.limit,
            offset=request.offset
        )

    except Exception as e:
        logger.error(f"Error listing Varshaphals: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list Varshaphals: {str(e)}"
        )


@router.delete("/{varshaphal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_varshaphal(
    varshaphal_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a specific Varshaphal.

    Uses Supabase REST API for database operations.
    """
    user_id = current_user["user_id"]
    try:
        # Check if Varshaphal exists and belongs to user
        varshaphal = await supabase_client.select(
            table="varshaphal_data",
            filters={"id": varshaphal_id, "user_id": user_id},
            single=True
        )

        if not varshaphal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Varshaphal not found"
            )

        # Delete using REST API
        await supabase_client.delete(
            table="varshaphal_data",
            filters={"id": varshaphal_id, "user_id": user_id}
        )

        logger.info(f"Deleted Varshaphal {varshaphal_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Varshaphal: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Varshaphal: {str(e)}"
        )


# Helper functions

async def _get_profile(profile_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get profile and verify ownership using Supabase REST API."""
    profile = await supabase_client.select(
        table="profiles",
        filters={"id": profile_id, "user_id": user_id},
        single=True
    )
    return profile


async def _get_cached_varshaphal(
    user_id: str,
    profile_id: str,
    target_year: int
) -> Optional[dict]:
    """Check for valid cached Varshaphal using Supabase REST API."""
    now = datetime.now(timezone.utc).isoformat()

    # Get recent varshaphals for this profile and year
    varshaphals = await supabase_client.select(
        table="varshaphal_data",
        filters={
            "user_id": user_id,
            "profile_id": profile_id,
            "target_year": target_year
        },
        order="generated_at.desc",
        limit=5
    )

    if not varshaphals:
        return None

    # Filter for non-expired in Python (Supabase REST API doesn't support > comparison directly)
    for varshaphal in varshaphals:
        if varshaphal["expires_at"] > now:
            return await _format_varshaphal_response(varshaphal, is_cached=True)

    return None


async def _get_natal_sun_longitude(profile: Dict[str, Any]) -> float:
    """
    Get natal Sun longitude from profile's chart using Supabase REST API.

    If chart doesn't exist, calculate it.
    """
    from app.services.vedic_astrology_accurate import AccurateVedicAstrology

    # Try to get from existing chart
    chart = await supabase_client.select(
        table="charts",
        filters={"profile_id": profile["id"]},
        single=True
    )

    if chart and chart.get("chart_data") and 'planets' in chart["chart_data"]:
        sun_data = chart["chart_data"]['planets'].get('Sun', {})
        if 'longitude' in sun_data:
            return sun_data['longitude']

    # Calculate on-the-fly
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

    return chart_data['planets']['Sun']['longitude']


async def _store_varshaphal(
    user_id: str,
    profile_id: str,
    target_year: int,
    natal_sun_longitude: float,
    solar_return_chart: dict,
    patyayini_dasha: List[dict],
    sahams: dict,
    annual_interpretation: dict
) -> Dict[str, Any]:
    """Store Varshaphal in database using Supabase REST API."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=VARSHAPHAL_CACHE_TTL_SECONDS)

    # Generate cache key
    cache_key = _generate_cache_key(user_id, profile_id, target_year)

    # Convert datetime objects to ISO strings for JSON storage
    patyayini_dasha_serialized = []
    for period in patyayini_dasha:
        period_copy = period.copy()
        period_copy['start_date'] = period['start_date'].isoformat()
        period_copy['end_date'] = period['end_date'].isoformat()
        patyayini_dasha_serialized.append(period_copy)

    solar_return_chart_serialized = solar_return_chart.copy()
    solar_return_chart_serialized['solar_return_time'] = solar_return_chart['solar_return_time'].isoformat()

    # Prepare data for insertion
    data = {
        "user_id": user_id,
        "profile_id": profile_id,
        "target_year": target_year,
        "solar_return_time": solar_return_chart['solar_return_time'].isoformat(),
        "natal_sun_longitude": str(natal_sun_longitude),
        "solar_return_chart": solar_return_chart_serialized,
        "patyayini_dasha": patyayini_dasha_serialized,
        "sahams": sahams,
        "annual_interpretation": annual_interpretation,
        "generated_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "cache_key": cache_key
    }

    # Insert using Supabase REST API
    varshaphal = await supabase_client.insert(
        table="varshaphal_data",
        data=data
    )

    logger.info(f"Stored Varshaphal {varshaphal['id']} for profile {profile_id}, year {target_year}")
    return varshaphal


def _generate_cache_key(user_id: str, profile_id: str, target_year: int) -> str:
    """Generate cache key for deduplication."""
    key_str = f"{user_id}:{profile_id}:{target_year}"
    return hashlib.sha256(key_str.encode()).hexdigest()


async def _format_varshaphal_response(varshaphal: Dict[str, Any], is_cached: bool) -> dict:
    """Format Varshaphal for API response (works with dictionary from REST API)."""
    # Parse datetime strings back to datetime objects
    patyayini_dasha = []
    for period in varshaphal["patyayini_dasha"]:
        period_copy = period.copy()
        period_copy['start_date'] = datetime.fromisoformat(period['start_date'])
        period_copy['end_date'] = datetime.fromisoformat(period['end_date'])
        patyayini_dasha.append(period_copy)

    solar_return_chart = varshaphal["solar_return_chart"].copy()
    solar_return_chart['solar_return_time'] = datetime.fromisoformat(solar_return_chart['solar_return_time'])

    response = schemas.VarshapalResponse(
        varshaphal_id=varshaphal["id"],
        profile_id=varshaphal["profile_id"],
        target_year=varshaphal["target_year"],
        generated_at=varshaphal["generated_at"],
        expires_at=varshaphal["expires_at"],
        solar_return_chart=schemas.SolarReturnChart(**solar_return_chart),
        patyayini_dasha=[schemas.DashaPeriod(**p) for p in patyayini_dasha],
        sahams={k: schemas.Saham(**v) for k, v in varshaphal["sahams"].items()},
        annual_interpretation=schemas.AnnualInterpretation(**varshaphal["annual_interpretation"]),
        is_cached=is_cached
    )

    return response.model_dump()
