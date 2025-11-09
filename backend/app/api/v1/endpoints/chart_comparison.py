"""
API endpoints for Chart Comparison and Synastry.

Provides:
- Compare two birth charts
- Synastry analysis
- Compatibility scoring

Database: Uses Supabase REST API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.core.security import get_current_user
from app.core.supabase_client import SupabaseClient
from app.schemas import chart_comparison as schemas
from app.services.chart_comparison_service import chart_comparison_service
from app.db.database import get_supabase_client

router = APIRouter()


@router.post("/compare", response_model=schemas.ChartComparisonResponse, status_code=status.HTTP_200_OK)
async def compare_charts(
    request: schemas.ChartComparisonRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Compare two birth charts for synastry/compatibility analysis.

    Analyzes:
    - Inter-chart aspects (planet to planet)
    - House overlays (one person's planets in another's houses)
    - Compatibility factors (emotional, romantic, communication, etc.)
    - Overall compatibility score and interpretation
    """
    try:
        user_id = current_user["user_id"]

        # Get both profiles
        profile_1 = await supabase.select(
            "profiles",
            filters={"id": request.profile_id_1},
            single=True
        )
        profile_2 = await supabase.select(
            "profiles",
            filters={"id": request.profile_id_2},
            single=True
        )

        if not profile_1 or not profile_2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both profiles not found"
            )

        # Verify user has access to at least one profile
        if profile_1["user_id"] != user_id and profile_2["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to both profiles"
            )

        # Get charts for both profiles
        charts_1 = await supabase.select(
            "charts",
            filters={"profile_id": request.profile_id_1, "chart_type": "D1"},
            limit=1
        )
        charts_2 = await supabase.select(
            "charts",
            filters={"profile_id": request.profile_id_2, "chart_type": "D1"},
            limit=1
        )

        chart_1 = charts_1[0] if charts_1 else None
        chart_2 = charts_2[0] if charts_2 else None

        if not chart_1 or not chart_2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Charts not found for one or both profiles. Please generate charts first."
            )

        # Prepare chart data for comparison
        chart_1_data = chart_1["chart_data"].copy() if chart_1.get("chart_data") else {}
        chart_2_data = chart_2["chart_data"].copy() if chart_2.get("chart_data") else {}

        # Add profile info to chart data
        chart_1_data["id"] = profile_1["id"]
        chart_1_data["name"] = profile_1["name"]
        chart_2_data["id"] = profile_2["id"]
        chart_2_data["name"] = profile_2["name"]

        # Perform comparison
        comparison_result = chart_comparison_service.compare_charts(
            chart_1=chart_1_data,
            chart_2=chart_2_data,
            comparison_type=request.comparison_type
        )

        return comparison_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare charts: {str(e)}"
        )


@router.post("/synastry", response_model=schemas.SynastryResponse, status_code=status.HTTP_200_OK)
async def analyze_synastry(
    request: schemas.SynastryRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Dedicated synastry analysis with detailed aspect interpretations.

    Provides:
    - Aspect grid visualization
    - Double whammy detection
    - Focus-specific analysis (romantic, business, friendship, family)
    - Detailed interpretations for major aspects
    - Overall synastry scoring
    """
    try:
        user_id = current_user["user_id"]

        # Get both profiles
        profile_1 = await supabase.select(
            "profiles",
            filters={"id": request.profile_id_1},
            single=True
        )
        profile_2 = await supabase.select(
            "profiles",
            filters={"id": request.profile_id_2},
            single=True
        )

        if not profile_1 or not profile_2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both profiles not found"
            )

        # Verify user has access to at least one profile
        if profile_1["user_id"] != user_id and profile_2["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to both profiles"
            )

        # Get charts for both profiles
        charts_1 = await supabase.select(
            "charts",
            filters={"profile_id": request.profile_id_1, "chart_type": "D1"},
            limit=1
        )
        charts_2 = await supabase.select(
            "charts",
            filters={"profile_id": request.profile_id_2, "chart_type": "D1"},
            limit=1
        )

        chart_1 = charts_1[0] if charts_1 else None
        chart_2 = charts_2[0] if charts_2 else None

        if not chart_1 or not chart_2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Charts not found for one or both profiles. Please generate charts first."
            )

        # Prepare chart data
        chart_1_data = chart_1["chart_data"].copy() if chart_1.get("chart_data") else {}
        chart_2_data = chart_2["chart_data"].copy() if chart_2.get("chart_data") else {}

        # Add profile info
        chart_1_data["id"] = profile_1["id"]
        chart_1_data["name"] = profile_1["name"]
        chart_2_data["id"] = profile_2["id"]
        chart_2_data["name"] = profile_2["name"]

        # Perform synastry analysis
        synastry_result = chart_comparison_service.analyze_synastry(
            chart_1=chart_1_data,
            chart_2=chart_2_data,
            focus=request.focus
        )

        return synastry_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze synastry: {str(e)}"
        )


@router.post("/composite", response_model=schemas.CompositeChartResponse, status_code=status.HTTP_200_OK)
async def generate_composite_chart(
    request: schemas.CompositeChartRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Generate composite chart using midpoint method.

    Composite chart represents the relationship itself as a separate entity.
    Calculated by finding midpoints between corresponding planets in both charts.

    Provides:
    - Composite planet positions
    - Composite houses
    - Relationship strengths and challenges
    - Relationship themes
    """
    try:
        user_id = current_user["user_id"]

        # Get both profiles
        profile_1 = await supabase.select(
            "profiles",
            filters={"id": request.profile_id_1},
            single=True
        )
        profile_2 = await supabase.select(
            "profiles",
            filters={"id": request.profile_id_2},
            single=True
        )

        if not profile_1 or not profile_2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both profiles not found"
            )

        # Verify user has access to at least one profile
        if profile_1["user_id"] != user_id and profile_2["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to both profiles"
            )

        # Get charts
        charts_1 = await supabase.select(
            "charts",
            filters={"profile_id": request.profile_id_1, "chart_type": "D1"},
            limit=1
        )
        charts_2 = await supabase.select(
            "charts",
            filters={"profile_id": request.profile_id_2, "chart_type": "D1"},
            limit=1
        )

        chart_1 = charts_1[0] if charts_1 else None
        chart_2 = charts_2[0] if charts_2 else None

        if not chart_1 or not chart_2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Charts not found for one or both profiles. Please generate charts first."
            )

        # Prepare chart data
        chart_1_data = chart_1["chart_data"].copy() if chart_1.get("chart_data") else {}
        chart_2_data = chart_2["chart_data"].copy() if chart_2.get("chart_data") else {}

        # Generate composite chart
        composite_result = chart_comparison_service.generate_composite_chart(
            chart_1=chart_1_data,
            chart_2=chart_2_data
        )

        return composite_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate composite chart: {str(e)}"
        )


@router.post("/progressed", response_model=schemas.ProgressedChartResponse, status_code=status.HTTP_200_OK)
async def calculate_progressed_chart(
    request: schemas.ProgressedChartRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Calculate progressed chart using secondary progressions.

    Secondary progressions: 1 day after birth = 1 year of life

    Shows:
    - Current progressed planet positions
    - Major changes from natal chart
    - Current life themes
    - Progressed ascendant
    """
    try:
        user_id = current_user["user_id"]

        # Get profile
        profile = await supabase.select(
            "profiles",
            filters={"id": request.profile_id},
            single=True
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Verify user has access
        if profile["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this profile"
            )

        # Get natal chart
        charts = await supabase.select(
            "charts",
            filters={"profile_id": request.profile_id, "chart_type": "D1"},
            limit=1
        )

        if not charts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Natal chart not found. Please generate chart first."
            )

        chart = charts[0]
        chart_data = chart["chart_data"].copy() if chart.get("chart_data") else {}

        # Add birth datetime from profile
        chart_data["birth_datetime"] = profile["date_of_birth"]
        chart_data["latitude"] = profile.get("latitude", 0)
        chart_data["longitude"] = profile.get("longitude", 0)

        # Calculate progressed chart
        progressed_result = chart_comparison_service.calculate_progressed_chart(
            natal_chart=chart_data,
            current_age=request.current_age
        )

        if "error" in progressed_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=progressed_result["error"]
            )

        return progressed_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate progressed chart: {str(e)}"
        )


@router.post("/save", response_model=schemas.SavedComparisonResponse, status_code=status.HTTP_201_CREATED)
async def save_comparison(
    request: schemas.SaveComparisonRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Save a chart comparison for future reference.

    Stores the full comparison result in the database so users can
    revisit their analysis later.
    """
    try:
        user_id = current_user["user_id"]

        # Verify user has access to at least one of the profiles
        profile_1 = await supabase.select(
            "profiles",
            filters={"id": request.profile_id_1},
            single=True
        )
        profile_2 = await supabase.select(
            "profiles",
            filters={"id": request.profile_id_2},
            single=True
        )

        if not profile_1 or not profile_2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both profiles not found"
            )

        if profile_1["user_id"] != user_id and profile_2["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to both profiles"
            )

        # Save comparison
        comparison_data = {
            "user_id": user_id,
            "profile_id_1": request.profile_id_1,
            "profile_id_2": request.profile_id_2,
            "comparison_type": request.comparison_type,
            "comparison_data": request.comparison_data
        }

        result = await supabase.insert("chart_comparisons", comparison_data)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save comparison: {str(e)}"
        )


@router.get("/list", response_model=schemas.ComparisonListResponse, status_code=status.HTTP_200_OK)
async def list_comparisons(
    limit: int = 10,
    offset: int = 0,
    comparison_type: str = None,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    List all saved chart comparisons for the current user.

    Optional filters:
    - comparison_type: Filter by type (general, romantic, business, family)
    - limit: Number of results (default 10)
    - offset: Pagination offset (default 0)
    """
    try:
        user_id = current_user["user_id"]

        # Build filters
        filters = {"user_id": user_id}
        if comparison_type:
            filters["comparison_type"] = comparison_type

        # Get total count
        total = await supabase.count("chart_comparisons", filters=filters)

        # Get paginated results
        comparisons = await supabase.select(
            "chart_comparisons",
            filters=filters,
            limit=limit,
            offset=offset
        )

        return {
            "comparisons": comparisons or [],
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list comparisons: {str(e)}"
        )


@router.delete("/{comparison_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comparison(
    comparison_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Delete a saved comparison by ID.
    """
    try:
        user_id = current_user["user_id"]

        # Check if comparison exists and belongs to user
        comparison = await supabase.select(
            "chart_comparisons",
            filters={"id": str(comparison_id), "user_id": user_id},
            single=True
        )

        if not comparison:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comparison not found"
            )

        # Delete the comparison
        await supabase.delete(
            "chart_comparisons",
            filters={"id": str(comparison_id), "user_id": user_id}
        )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comparison: {str(e)}"
        )
