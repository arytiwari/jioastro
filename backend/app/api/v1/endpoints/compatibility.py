"""
API Endpoints for Vedic Astrology Compatibility Matching
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.services.compatibility_service import compatibility_service
from app.services.supabase_service import supabase_service

router = APIRouter()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_chart_data_helper(profile_id: str, user_id: str) -> Dict[str, Any]:
    """Fetch chart data for a profile (D1 chart)."""
    # Get profile
    profile_response = supabase_service.client.table("profiles")\
        .select("*")\
        .eq("id", profile_id)\
        .eq("user_id", user_id)\
        .execute()

    if not profile_response.data or len(profile_response.data) == 0:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = profile_response.data[0]

    # Get D1 chart
    d1_response = supabase_service.client.table("charts")\
        .select("*")\
        .eq("profile_id", profile_id)\
        .eq("chart_type", "D1")\
        .execute()

    if not d1_response.data or len(d1_response.data) == 0:
        raise HTTPException(status_code=404, detail="D1 chart not found. Please generate chart first.")

    d1_chart = d1_response.data[0]

    return {
        "profile": profile,
        "d1_chart": d1_chart.get("chart_data", d1_chart)
    }


# ============================================================================
# COMPATIBILITY ENDPOINTS
# ============================================================================

@router.post("/analyze")
async def analyze_compatibility(
    boy_profile_id: str,
    girl_profile_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Perform complete compatibility analysis between two profiles.

    Includes:
    - Ashtakoot (Guna Milan) - 8-factor compatibility
    - Manglik Dosha analysis
    - Overall compatibility rating
    """
    try:
        # Get both charts
        boy_data = await get_chart_data_helper(boy_profile_id, user["user_id"])
        girl_data = await get_chart_data_helper(girl_profile_id, user["user_id"])

        boy_chart = boy_data["d1_chart"]
        girl_chart = girl_data["d1_chart"]

        # Perform compatibility analysis
        analysis = compatibility_service.analyze_compatibility(boy_chart, girl_chart)

        return {
            "boy_profile": {
                "id": boy_profile_id,
                "name": boy_data["profile"].get("name")
            },
            "girl_profile": {
                "id": girl_profile_id,
                "name": girl_data["profile"].get("name")
            },
            "compatibility_analysis": analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze compatibility: {str(e)}"
        )


@router.get("/guna-milan/{boy_profile_id}/{girl_profile_id}")
async def get_guna_milan(
    boy_profile_id: str,
    girl_profile_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get Guna Milan (Ashtakoot) compatibility score.

    Returns the 8-factor compatibility analysis with total score out of 36.
    """
    try:
        # Get both charts
        boy_data = await get_chart_data_helper(boy_profile_id, user["user_id"])
        girl_data = await get_chart_data_helper(girl_profile_id, user["user_id"])

        boy_chart = boy_data["d1_chart"]
        girl_chart = girl_data["d1_chart"]

        # Perform compatibility analysis
        analysis = compatibility_service.analyze_compatibility(boy_chart, girl_chart)

        return {
            "boy_profile_id": boy_profile_id,
            "girl_profile_id": girl_profile_id,
            "guna_milan": analysis["guna_milan"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate Guna Milan: {str(e)}"
        )


@router.get("/manglik/{profile_id}")
async def check_manglik_dosha(
    profile_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Check Manglik (Kuja) Dosha for a single profile.

    Manglik dosha occurs when Mars is placed in houses 1, 4, 7, 8, or 12.
    """
    try:
        # Get chart
        chart_data = await get_chart_data_helper(profile_id, user["user_id"])
        chart = chart_data["d1_chart"]

        # Calculate Manglik Dosha
        manglik_analysis = compatibility_service.calculate_manglik_dosha(chart)

        return {
            "profile_id": profile_id,
            "profile_name": chart_data["profile"].get("name"),
            "manglik_analysis": manglik_analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check Manglik Dosha: {str(e)}"
        )


@router.get("/nakshatra/{profile_id}")
async def get_nakshatra(
    profile_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get Nakshatra (birth star) details for a profile.

    Returns the Moon's nakshatra along with pada and related information.
    """
    try:
        # Get chart
        chart_data = await get_chart_data_helper(profile_id, user["user_id"])
        chart = chart_data["d1_chart"]

        # Get Moon position
        moon_longitude = chart.get("planets", {}).get("Moon", {}).get("longitude", 0)

        # Calculate nakshatra
        nakshatra_data = compatibility_service.get_nakshatra(moon_longitude)

        return {
            "profile_id": profile_id,
            "profile_name": chart_data["profile"].get("name"),
            "nakshatra": nakshatra_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate Nakshatra: {str(e)}"
        )


@router.post("/quick-match")
async def quick_compatibility_match(
    profile_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get quick compatibility matches for a profile against all other profiles.

    Returns a list of profiles sorted by compatibility score.
    """
    try:
        # Get the main profile
        main_profile_data = await get_chart_data_helper(profile_id, user["user_id"])
        main_chart = main_profile_data["d1_chart"]

        # Get all other profiles for this user
        all_profiles_response = supabase_service.client.table("profiles")\
            .select("*")\
            .eq("user_id", user["user_id"])\
            .neq("id", profile_id)\
            .execute()

        if not all_profiles_response.data:
            return {
                "profile_id": profile_id,
                "matches": []
            }

        matches = []

        for other_profile in all_profiles_response.data:
            try:
                # Get the other profile's chart
                other_chart_data = await get_chart_data_helper(other_profile["id"], user["user_id"])
                other_chart = other_chart_data["d1_chart"]

                # Perform compatibility analysis
                # Determine gender-based roles (simplified approach)
                analysis = compatibility_service.analyze_compatibility(main_chart, other_chart)

                matches.append({
                    "profile_id": other_profile["id"],
                    "name": other_profile.get("name"),
                    "date_of_birth": other_profile.get("date_of_birth"),
                    "compatibility_score": analysis["guna_milan"]["total_points"],
                    "compatibility_percentage": analysis["guna_milan"]["percentage"],
                    "compatibility_level": analysis["overall_compatibility"]["level"],
                    "manglik_compatible": analysis["manglik_analysis"]["compatible"]
                })

            except Exception as e:
                # Skip profiles without charts
                continue

        # Sort by compatibility score (descending)
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)

        return {
            "profile_id": profile_id,
            "profile_name": main_profile_data["profile"].get("name"),
            "matches": matches
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find compatibility matches: {str(e)}"
        )
