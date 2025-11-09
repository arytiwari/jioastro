"""Chart API Endpoints - Using Supabase REST API"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.chart import ChartCalculateRequest, ChartResponse
from app.core.security import get_current_user
from app.services.astrology import astrology_service
from app.services.supabase_service import supabase_service
from app.services.divisional_charts_service import divisional_charts_service

router = APIRouter()


@router.post("/calculate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def calculate_chart(
    request: ChartCalculateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate and cache a birth chart (D1, D9, or Moon)
    If chart already exists, return cached version
    """
    try:
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

        # Check if chart already exists
        existing_chart = await supabase_service.get_chart(
            profile_id=request.profile_id,
            chart_type=request.chart_type
        )

        if existing_chart:
            # Recalculate dasha periods based on current date
            # (planetary positions are cached, but dashas need to be current)
            chart_data = existing_chart.get('chart_data', {})

            if 'planets' in chart_data and 'Moon' in chart_data['planets']:
                from datetime import datetime, date, time

                # Parse birth data from profile
                if isinstance(profile['birth_date'], str):
                    birth_date = datetime.fromisoformat(profile['birth_date']).date()
                else:
                    birth_date = profile['birth_date']

                if isinstance(profile['birth_time'], str):
                    birth_time = datetime.fromisoformat(f"2000-01-01T{profile['birth_time']}").time()
                else:
                    birth_time = profile['birth_time']

                birth_datetime = datetime.combine(birth_date, birth_time)

                # Recalculate dasha with current date
                from app.services.vedic_astrology_accurate import accurate_vedic_astrology
                updated_dasha = accurate_vedic_astrology._calculate_vimshottari_dasha(
                    chart_data['planets']['Moon'],
                    birth_datetime
                )

                # Update chart data with fresh dasha calculation
                chart_data['dasha'] = updated_dasha
                existing_chart['chart_data'] = chart_data

            # Return chart with updated dasha
            return existing_chart

        # Calculate new chart
        try:
            # Parse date/time strings from database
            from datetime import date, time, datetime

            # Debug: print what we're getting
            print(f"Profile data - birth_date: {profile['birth_date']} (type: {type(profile['birth_date'])})")
            print(f"Profile data - birth_time: {profile['birth_time']} (type: {type(profile['birth_time'])})")

            # Handle different date/time formats from Supabase
            if isinstance(profile['birth_date'], str):
                birth_date = datetime.fromisoformat(profile['birth_date']).date()
            else:
                birth_date = profile['birth_date']

            if isinstance(profile['birth_time'], str):
                # Parse time string - could be HH:MM:SS or just HH:MM
                birth_time = datetime.fromisoformat(f"2000-01-01T{profile['birth_time']}").time()
            else:
                birth_time = profile['birth_time']

            print(f"Parsed - birth_date: {birth_date} (type: {type(birth_date)})")
            print(f"Parsed - birth_time: {birth_time} (type: {type(birth_time)})")

            # Ensure all parameters are in the correct format
            name = str(profile['name'])  # Ensure name is a string
            latitude = float(str(profile['birth_lat']))  # Convert to string first, then float
            longitude = float(str(profile['birth_lon']))
            timezone_str = str(profile.get('birth_timezone') or 'UTC')  # Ensure it's a string
            city = str(profile.get('birth_city') or 'Unknown')

            print(f"Parameters for Kerykeion:")
            print(f"  name: {name} (type: {type(name)})")
            print(f"  latitude: {latitude} (type: {type(latitude)})")
            print(f"  longitude: {longitude} (type: {type(longitude)})")
            print(f"  timezone_str: {timezone_str} (type: {type(timezone_str)})")
            print(f"  city: {city} (type: {type(city)})")

            if request.chart_type == "D1":
                chart_data = astrology_service.calculate_birth_chart(
                    name=name,
                    birth_date=birth_date,
                    birth_time=birth_time,
                    latitude=latitude,
                    longitude=longitude,
                    timezone_str=timezone_str,
                    city=city
                )
            elif request.chart_type == "D9":
                chart_data = astrology_service.calculate_navamsa_chart(
                    name=name,
                    birth_date=birth_date,
                    birth_time=birth_time,
                    latitude=latitude,
                    longitude=longitude,
                    timezone_str=timezone_str,
                    city=city
                )
            elif request.chart_type == "Moon":
                chart_data = astrology_service.calculate_moon_chart(
                    name=name,
                    birth_date=birth_date,
                    birth_time=birth_time,
                    latitude=latitude,
                    longitude=longitude,
                    timezone_str=timezone_str,
                    city=city
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid chart type. Use 'D1', 'D9', or 'Moon'"
                )
        except Exception as e:
            import traceback
            print(f"Error calculating chart: {str(e)}")
            print("Full traceback:")
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chart calculation failed: {str(e)}"
            )

        # Save chart to database
        new_chart = await supabase_service.create_chart({
            "profile_id": str(request.profile_id),  # Convert UUID to string
            "chart_type": request.chart_type,
            "chart_data": chart_data,
            "chart_svg": None  # Will be generated by frontend for MVP
        })

        if not new_chart:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save chart"
            )

        return new_chart

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in calculate_chart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chart calculation: {str(e)}"
        )


@router.get("/{profile_id}/{chart_type}", response_model=dict)
async def get_chart(
    profile_id: str,
    chart_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific chart (D1 or D9)"""
    try:
        user_id = current_user["user_id"]

        # Verify profile belongs to user
        profile = await supabase_service.get_profile(
            profile_id=profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Get chart
        chart = await supabase_service.get_chart(
            profile_id=profile_id,
            chart_type=chart_type
        )

        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chart {chart_type} not found. Please calculate it first."
            )

        # Recalculate dasha periods based on current date
        chart_data = chart.get('chart_data', {})

        if 'planets' in chart_data and 'Moon' in chart_data['planets']:
            from datetime import datetime

            # Parse birth data from profile
            if isinstance(profile['birth_date'], str):
                birth_date = datetime.fromisoformat(profile['birth_date']).date()
            else:
                birth_date = profile['birth_date']

            if isinstance(profile['birth_time'], str):
                birth_time = datetime.fromisoformat(f"2000-01-01T{profile['birth_time']}").time()
            else:
                birth_time = profile['birth_time']

            birth_datetime = datetime.combine(birth_date, birth_time)

            # Recalculate dasha with current date
            from app.services.vedic_astrology_accurate import accurate_vedic_astrology
            updated_dasha = accurate_vedic_astrology._calculate_vimshottari_dasha(
                chart_data['planets']['Moon'],
                birth_datetime
            )

            # Update chart data with fresh dasha calculation
            chart_data['dasha'] = updated_dasha
            chart['chart_data'] = chart_data

        return chart

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting chart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chart: {str(e)}"
        )


@router.delete("/{profile_id}/{chart_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chart(
    profile_id: str,
    chart_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a cached chart (will be recalculated on next request)"""
    try:
        user_id = current_user["user_id"]

        # Verify profile belongs to user
        profile = await supabase_service.get_profile(
            profile_id=profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Delete chart
        deleted = await supabase_service.delete_chart(
            profile_id=profile_id,
            chart_type=chart_type
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chart {chart_type} not found"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting chart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chart: {str(e)}"
        )


@router.get("/{profile_id}/divisional/all", response_model=dict)
async def get_all_divisional_charts(
    profile_id: str,
    priority: str = "all",
    current_user: dict = Depends(get_current_user)
):
    """
    Get all divisional charts for a profile

    Priority levels:
    - high: D2, D4, D7, D10, D24 (6 charts - excluding D9)
    - medium: high + D3, D12, D16, D20 (10 charts)
    - all: All 15 divisional charts (D2-D60, excluding D9)
    """
    try:
        user_id = current_user["user_id"]

        # Verify profile belongs to user
        profile = await supabase_service.get_profile(
            profile_id=profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Get D1 chart (divisional charts are embedded in it)
        d1_chart = await supabase_service.get_chart(
            profile_id=profile_id,
            chart_type="D1"
        )

        if not d1_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="D1 chart not found. Please calculate it first."
            )

        chart_data = d1_chart.get('chart_data', {})
        divisional_charts = chart_data.get('divisional_charts', {})

        if not divisional_charts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No divisional charts found. Chart may be old - please regenerate."
            )

        # Filter by priority if needed
        if priority == "high":
            priority_charts = ["D2", "D4", "D7", "D10", "D24"]
            divisional_charts = {
                k: v for k, v in divisional_charts.items()
                if k in priority_charts
            }
        elif priority == "medium":
            priority_charts = ["D2", "D3", "D4", "D7", "D10", "D12", "D16", "D20", "D24"]
            divisional_charts = {
                k: v for k, v in divisional_charts.items()
                if k in priority_charts
            }

        return {
            "profile_id": profile_id,
            "priority": priority,
            "total_charts": len(divisional_charts),
            "divisional_charts": divisional_charts
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting divisional charts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get divisional charts: {str(e)}"
        )


@router.get("/{profile_id}/divisional/{division}", response_model=dict)
async def get_specific_divisional_chart(
    profile_id: str,
    division: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific divisional chart (D2, D3, D4, D7, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60)
    Note: D9 (Navamsa) is available via the standard /charts/{profile_id}/D9 endpoint
    """
    try:
        user_id = current_user["user_id"]

        # Verify profile belongs to user
        profile = await supabase_service.get_profile(
            profile_id=profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Validate division
        valid_divisions = ["D2", "D3", "D4", "D7", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]
        if division not in valid_divisions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid division. Must be one of: {', '.join(valid_divisions)}"
            )

        # Get D1 chart (divisional charts are embedded in it)
        d1_chart = await supabase_service.get_chart(
            profile_id=profile_id,
            chart_type="D1"
        )

        if not d1_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="D1 chart not found. Please calculate it first."
            )

        chart_data = d1_chart.get('chart_data', {})
        divisional_charts = chart_data.get('divisional_charts', {})

        if division not in divisional_charts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{division} chart not found. Chart may be old - please regenerate D1 chart."
            )

        return {
            "profile_id": profile_id,
            "division": division,
            "chart_data": divisional_charts[division]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting divisional chart {division}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get divisional chart: {str(e)}"
        )


@router.get("/{profile_id}/vimshopaka-bala", response_model=dict)
async def get_vimshopaka_bala(
    profile_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get Vimshopaka Bala (composite planetary strength) for a profile

    Vimshopaka Bala is the weighted strength of planets across all 16 divisional charts.
    This classical Vedic technique provides deep insights into planetary power and effects.

    Returns:
    - Strength scores for all planets (out of 20 Shashtiamsa units)
    - Quality classifications (Parijatamsa, Uttamamsa, Gopuramsa, etc.)
    - Detailed varga-wise breakdown showing dignity in each divisional chart
    - Summary statistics (strongest/weakest planets, average strength)
    """
    try:
        user_id = current_user["user_id"]

        # Verify profile belongs to user
        profile = await supabase_service.get_profile(
            profile_id=profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Get D1 chart (Vimshopaka Bala is embedded in it)
        d1_chart = await supabase_service.get_chart(
            profile_id=profile_id,
            chart_type="D1"
        )

        if not d1_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="D1 chart not found. Please calculate it first."
            )

        chart_data = d1_chart.get('chart_data', {})
        vimshopaka_bala = chart_data.get('vimshopaka_bala')

        if not vimshopaka_bala:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vimshopaka Bala not found. Chart may be old - please regenerate D1 chart."
            )

        return {
            "profile_id": profile_id,
            "vimshopaka_bala": vimshopaka_bala,
            "description": "Vimshopaka Bala shows composite planetary strength across all 16 divisional charts using classical Parashara system"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting Vimshopaka Bala: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Vimshopaka Bala: {str(e)}"
        )


@router.get("/{profile_id}/divisional/{division}/yogas", response_model=dict)
async def get_divisional_chart_yogas(
    profile_id: str,
    division: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Detect yogas in a specific divisional chart

    Different divisional charts emphasize different yogas:
    - D2 (Hora): Wealth yogas (Dhana Yoga)
    - D4 (Chaturthamsa): Property yogas
    - D7 (Saptamsa): Children yogas (Jupiter-Venus combinations)
    - D9 (Navamsa): Marriage and spiritual yogas (Raj Yoga)
    - D10 (Dashamsa): Career yogas (Raj Yoga, Dhana Yoga)
    - D12 (Dwadashamsa): Parents and ancestry yogas

    Returns:
    - List of yogas found in the divisional chart
    - Yoga strength, category, and effects
    - Planets and houses involved
    """
    try:
        user_id = current_user["user_id"]

        # Verify profile belongs to user
        profile = await supabase_service.get_profile(
            profile_id=profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Validate division
        valid_divisions = ["D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]
        if division not in valid_divisions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid division. Must be one of: {', '.join(valid_divisions)}"
            )

        # Get D1 chart
        d1_chart = await supabase_service.get_chart(
            profile_id=profile_id,
            chart_type="D1"
        )

        if not d1_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="D1 chart not found. Please calculate it first."
            )

        chart_data = d1_chart.get('chart_data', {})
        divisional_charts = chart_data.get('divisional_charts', {})

        if division not in divisional_charts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{division} chart not found. Chart may be old - please regenerate D1 chart."
            )

        # Detect yogas in the divisional chart
        yogas = divisional_charts_service.detect_divisional_yogas(
            division,
            divisional_charts[division]
        )

        return {
            "profile_id": profile_id,
            "division": division,
            "total_yogas": len(yogas),
            "yogas": yogas,
            "note": f"Yogas detected in {division} chart. Different charts emphasize different life areas."
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error detecting yogas in {division}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect yogas in divisional chart: {str(e)}"
        )
