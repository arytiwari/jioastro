"""VedAstro API Endpoints - Enhanced Vedic Astrology Features"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from datetime import date, time, datetime

from app.schemas.chart import ChartCalculateRequest
from app.core.security import get_current_user
from app.services.vedastro_service import vedastro_service
from app.services.supabase_service import supabase_service

router = APIRouter()


@router.get("/status")
async def vedastro_status():
    """Check if VedAstro library is available"""
    return {
        "available": vedastro_service.is_available(),
        "message": "VedAstro library is available" if vedastro_service.is_available() else "VedAstro library not installed"
    }


@router.post("/chart/comprehensive")
async def calculate_comprehensive_chart(
    request: ChartCalculateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate comprehensive birth chart using VedAstro
    Returns detailed planetary, house, yoga, and dasha data
    """
    try:
        if not vedastro_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="VedAstro library not available. Please install: pip install vedastro"
            )

        user_id = current_user["user_id"]

        # Verify profile belongs to user
        profile = await supabase_service.get_profile(
            profile_id=request.profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Parse birth data
        if isinstance(profile['birth_date'], str):
            birth_date = datetime.fromisoformat(profile['birth_date']).date()
        else:
            birth_date = profile['birth_date']

        if isinstance(profile['birth_time'], str):
            birth_time = datetime.fromisoformat(f"2000-01-01T{profile['birth_time']}").time()
        else:
            birth_time = profile['birth_time']

        latitude = float(str(profile['birth_lat']))
        longitude = float(str(profile['birth_lon']))
        location_name = str(profile.get('birth_city') or 'Unknown')

        # Calculate timezone offset from timezone string
        timezone_str = str(profile.get('birth_timezone') or 'UTC')
        timezone_offset = "+00:00"  # Default

        # Common timezone mappings
        timezone_offsets = {
            'Asia/Kolkata': '+05:30',
            'Asia/Calcutta': '+05:30',
            'America/New_York': '-05:00',
            'America/Los_Angeles': '-08:00',
            'Europe/London': '+00:00',
            'UTC': '+00:00'
        }
        timezone_offset = timezone_offsets.get(timezone_str, '+00:00')

        # Calculate comprehensive chart using VedAstro
        vedastro_data = vedastro_service.calculate_comprehensive_chart(
            birth_date=birth_date,
            birth_time=birth_time,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            timezone_offset=timezone_offset
        )

        if "error" in vedastro_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=vedastro_data["error"]
            )

        # Extract simplified data for frontend compatibility
        simplified_data = vedastro_service.extract_simplified_chart_data(vedastro_data)

        return {
            "profile_id": request.profile_id,
            "chart_type": "D1",
            "source": "VedAstro",
            "vedastro_data": simplified_data,
            "raw_vedastro": vedastro_data  # Include raw data for advanced features
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in calculate_comprehensive_chart: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate comprehensive chart: {str(e)}"
        )


@router.get("/knowledge/{topic}")
async def get_vedic_knowledge(topic: str):
    """
    Get Vedic astrology knowledge on specific topics
    Topics: planets, houses, yogas, nakshatras, dashas
    """
    try:
        knowledge = vedastro_service.get_vedic_knowledge(topic)

        if not knowledge or not knowledge.get("title"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge topic '{topic}' not found. Available topics: planets, houses, yogas, nakshatras, dashas"
            )

        return knowledge

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge: {str(e)}"
        )


@router.get("/knowledge")
async def list_knowledge_topics():
    """List all available Vedic knowledge topics"""
    return {
        "topics": [
            {"id": "planets", "name": "Planets (Grahas)", "description": "The nine planets in Vedic astrology"},
            {"id": "houses", "name": "Houses (Bhavas)", "description": "The twelve houses representing life areas"},
            {"id": "yogas", "name": "Yogas", "description": "Planetary combinations and their effects"},
            {"id": "nakshatras", "name": "Nakshatras", "description": "27 lunar mansions"},
            {"id": "dashas", "name": "Dashas", "description": "Vimshottari planetary period system"}
        ]
    }
