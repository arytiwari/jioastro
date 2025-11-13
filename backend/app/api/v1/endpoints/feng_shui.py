"""
Feng Shui Integration API Endpoints
Provides feng shui analysis with profile integration
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.security import get_current_user
from app.services.feng_shui_service import FengShuiService
from app.schemas.feng_shui import (
    CreateFengShuiAnalysisRequest,
    FengShuiAnalysis,
    FengShuiAnalysisListResponse,
    FengShuiRecommendationListResponse,
    UpdateRecommendationRequest,
    FengShuiRecommendation,
    KuaCalculationResponse,
    DirectionGuidance,
    ColorTherapyResponse,
    ElementBalanceResponse,
    FengShuiStats,
    UpdateSpaceLayoutRequest
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=FengShuiAnalysis)
async def create_feng_shui_analysis(
    request: CreateFengShuiAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create feng shui analysis based on birth profile
    Calculates Kua number and generates personalized recommendations
    """
    try:
        user_id = current_user["user_id"]
        service = FengShuiService()

        result = await service.create_analysis(
            user_id=user_id,
            profile_id=request.profile_id,
            space_type=request.space_type,
            space_orientation=request.space_orientation,
            space_layout=request.space_layout
        )

        return result["analysis"]

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create feng shui analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create analysis: {str(e)}")


@router.get("/analyses", response_model=FengShuiAnalysisListResponse)
async def get_feng_shui_analyses(
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's feng shui analyses
    """
    try:
        user_id = current_user["user_id"]
        service = FengShuiService()

        result = await service.get_user_analyses(user_id=user_id)

        # Limit results
        analyses = result["analyses"][:limit]

        # Transform to brief format
        analyses_brief = [
            {
                "id": a["id"],
                "profile_id": a["profile_id"],
                "kua_number": a["kua_number"],
                "personal_element": a["personal_element"],
                "space_type": a.get("space_type"),
                "compatibility_score": a.get("compatibility_score", 0.0),
                "created_at": a["created_at"]
            }
            for a in analyses
        ]

        return {
            "analyses": analyses_brief,
            "total_count": len(analyses_brief)
        }

    except Exception as e:
        logger.error(f"Failed to fetch analyses: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analyses")


@router.get("/analyses/{analysis_id}", response_model=FengShuiAnalysis)
async def get_feng_shui_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific feng shui analysis
    """
    try:
        user_id = current_user["user_id"]
        service = FengShuiService()

        analysis = await service.supabase.select(
            "feng_shui_analyses",
            filters={"id": analysis_id, "user_id": user_id},
            single=True
        )

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analysis")


@router.patch("/analyses/{analysis_id}", response_model=FengShuiAnalysis)
async def update_feng_shui_analysis(
    analysis_id: str,
    request: UpdateSpaceLayoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update space layout for an analysis
    """
    try:
        user_id = current_user["user_id"]
        service = FengShuiService()

        # Verify ownership
        analysis = await service.supabase.select(
            "feng_shui_analyses",
            filters={"id": analysis_id, "user_id": user_id},
            single=True
        )

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Update
        from datetime import datetime
        update_data = {"updated_at": datetime.utcnow().isoformat()}

        if request.space_type is not None:
            update_data["space_type"] = request.space_type
        if request.space_orientation is not None:
            update_data["space_orientation"] = request.space_orientation
            # Recalculate compatibility score
            kua_number = analysis["kua_number"]
            favorable_dirs = analysis["favorable_directions"]
            compatibility = service._calculate_space_compatibility(
                kua_number, request.space_orientation, favorable_dirs
            )
            update_data["compatibility_score"] = compatibility
        if request.space_layout is not None:
            update_data["space_layout"] = request.space_layout

        updated = await service.supabase.update(
            "feng_shui_analyses",
            filters={"id": analysis_id, "user_id": user_id},
            data=update_data
        )

        return updated

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update analysis")


@router.get("/analyses/{analysis_id}/recommendations", response_model=FengShuiRecommendationListResponse)
async def get_feng_shui_recommendations(
    analysis_id: str,
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get recommendations for a feng shui analysis
    """
    try:
        user_id = current_user["user_id"]
        service = FengShuiService()

        result = await service.get_recommendations_for_analysis(
            analysis_id=analysis_id,
            user_id=user_id
        )

        # Apply filters
        recommendations = result["recommendations"]
        if category:
            recommendations = [r for r in recommendations if r.get("category") == category]
        if priority:
            recommendations = [r for r in recommendations if r.get("priority") == priority]

        return {
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "by_category": result.get("by_category", {}),
            "by_priority": result.get("by_priority", {}),
            "implemented_count": result.get("implemented_count", 0)
        }

    except Exception as e:
        logger.error(f"Failed to fetch recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch recommendations")


@router.patch("/recommendations/{recommendation_id}", response_model=FengShuiRecommendation)
async def update_feng_shui_recommendation(
    recommendation_id: str,
    request: UpdateRecommendationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update recommendation implementation status
    """
    try:
        user_id = current_user["user_id"]
        service = FengShuiService()

        # Verify ownership
        recommendation = await service.supabase.select(
            "feng_shui_recommendations",
            filters={"id": recommendation_id, "user_id": user_id},
            single=True
        )

        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        # Update
        from datetime import datetime
        update_data = {"updated_at": datetime.utcnow().isoformat()}

        if request.is_implemented is not None:
            update_data["is_implemented"] = request.is_implemented
            if request.is_implemented and not recommendation.get("implemented_at"):
                update_data["implemented_at"] = datetime.utcnow().isoformat()

        if request.user_notes is not None:
            update_data["user_notes"] = request.user_notes

        if request.effectiveness_rating is not None:
            update_data["effectiveness_rating"] = request.effectiveness_rating

        updated = await service.supabase.update(
            "feng_shui_recommendations",
            filters={"id": recommendation_id, "user_id": user_id},
            data=update_data
        )

        return updated

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update recommendation {recommendation_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update recommendation")


@router.post("/calculate-kua", response_model=KuaCalculationResponse)
async def calculate_kua_number(
    profile_id: str = Query(..., description="Profile ID to calculate Kua number for"),
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate Kua number for a profile without creating full analysis
    Quick calculation endpoint
    """
    try:
        user_id = current_user["user_id"]
        service = FengShuiService()

        # Fetch profile
        profile = await service.supabase.select(
            "profiles",
            filters={"id": profile_id, "user_id": user_id},
            single=True
        )

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Extract birth year and gender
        from datetime import datetime
        birth_date = profile.get("birth_date")
        gender = profile.get("gender", "male")

        if not birth_date:
            raise HTTPException(status_code=400, detail="Birth date required")

        birth_year = datetime.fromisoformat(birth_date.replace('Z', '+00:00')).year

        # Calculate
        kua_number = service.calculate_kua_number(birth_year, gender)
        personal_element = service.get_personal_element(kua_number)
        life_gua_group = service.get_life_gua_group(kua_number)

        favorable_dirs = service.FAVORABLE_DIRECTIONS.get(kua_number, {})
        unfavorable_dirs = service.UNFAVORABLE_DIRECTIONS.get(kua_number, {})

        lucky_colors = service.get_lucky_colors(personal_element)
        unlucky_colors = service.get_unlucky_colors(personal_element)

        # Description
        description = f"Your Kua number {kua_number} places you in the {life_gua_group.title()} Life Group with {personal_element.title()} as your personal element. This influences your favorable directions and color choices for optimal energy flow."

        return {
            "kua_number": kua_number,
            "personal_element": personal_element,
            "life_gua_group": life_gua_group,
            "favorable_directions": favorable_dirs,
            "unfavorable_directions": unfavorable_dirs,
            "lucky_colors": lucky_colors,
            "unlucky_colors": unlucky_colors,
            "description": description
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate Kua: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate Kua number")


@router.get("/direction-guidance/{kua_number}", response_model=list[DirectionGuidance])
async def get_direction_guidance(
    kua_number: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed guidance for all 8 directions based on Kua number
    """
    try:
        if kua_number < 1 or kua_number > 9 or kua_number == 5:
            raise HTTPException(status_code=400, detail="Invalid Kua number (must be 1-9, excluding 5)")

        service = FengShuiService()

        favorable_dirs = service.FAVORABLE_DIRECTIONS.get(kua_number, {})
        unfavorable_dirs = service.UNFAVORABLE_DIRECTIONS.get(kua_number, {})

        # Direction names and best uses
        direction_info = {
            "sheng_qi": {"name": "Wealth & Success", "best_for": ["desk", "work area", "entrance"]},
            "tian_yi": {"name": "Health & Well-being", "best_for": ["bed headboard", "dining", "meditation"]},
            "yan_nian": {"name": "Love & Relationships", "best_for": ["bedroom", "living room", "social areas"]},
            "fu_wei": {"name": "Personal Growth", "best_for": ["study", "meditation", "personal space"]},
            "huo_hai": {"name": "Mishaps", "best_for": []},
            "wu_gui": {"name": "Five Ghosts", "best_for": []},
            "liu_sha": {"name": "Six Killings", "best_for": []},
            "jue_ming": {"name": "Total Loss", "best_for": []}
        }

        # Build guidance for all 8 compass directions
        all_directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        guidance_list = []

        for direction in all_directions:
            # Check if favorable
            is_favorable = direction in favorable_dirs.values()
            direction_type = None
            name = None
            best_for = []

            if is_favorable:
                for dtype, dval in favorable_dirs.items():
                    if dval == direction:
                        direction_type = dtype
                        name = direction_info[dtype]["name"]
                        best_for = direction_info[dtype]["best_for"]
                        break
                guidance_text = f"Excellent direction for {name.lower()}. Face this direction or place important areas here."
            else:
                # Check which unfavorable type
                for dtype, dval in unfavorable_dirs.items():
                    if dval == direction:
                        direction_type = dtype
                        name = direction_info[dtype]["name"]
                        break
                guidance_text = f"Unfavorable direction ({name}). Avoid facing this direction for important activities or use feng shui remedies."

            guidance_list.append({
                "direction": direction,
                "is_favorable": is_favorable,
                "direction_type": direction_type,
                "name": name,
                "guidance": guidance_text,
                "best_for": best_for
            })

        return guidance_list

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get direction guidance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get direction guidance")


@router.get("/color-therapy/{kua_number}", response_model=ColorTherapyResponse)
async def get_color_therapy(
    kua_number: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get color therapy recommendations based on Kua number
    """
    try:
        if kua_number < 1 or kua_number > 9 or kua_number == 5:
            raise HTTPException(status_code=400, detail="Invalid Kua number")

        service = FengShuiService()
        personal_element = service.get_personal_element(kua_number)

        lucky_colors_raw = service.get_lucky_colors(personal_element)
        unlucky_colors_raw = service.get_unlucky_colors(personal_element)

        # Map colors to hex codes (simplified)
        color_hex_map = {
            "green": "#00A651", "brown": "#8B4513", "teal": "#008080", "olive": "#808000",
            "red": "#FF0000", "orange": "#FFA500", "pink": "#FFC0CB", "purple": "#800080", "maroon": "#800000",
            "yellow": "#FFFF00", "beige": "#F5F5DC", "tan": "#D2B48C",
            "white": "#FFFFFF", "gold": "#FFD700", "silver": "#C0C0C0", "gray": "#808080", "bronze": "#CD7F32",
            "black": "#000000", "blue": "#0000FF", "navy": "#000080", "dark gray": "#A9A9A9",
            "dark green": "#006400"
        }

        lucky_colors = [{"color": c, "hex": color_hex_map.get(c, "#CCCCCC"), "meaning": f"Enhances {personal_element} energy"} for c in lucky_colors_raw]
        unlucky_colors = [{"color": c, "hex": color_hex_map.get(c, "#CCCCCC"), "meaning": f"Weakens {personal_element} energy"} for c in unlucky_colors_raw]

        # Room suggestions
        room_color_suggestions = {
            "bedroom": lucky_colors_raw[:2],
            "living_room": lucky_colors_raw[:3],
            "office": lucky_colors_raw[1:3] if len(lucky_colors_raw) > 1 else lucky_colors_raw,
            "kitchen": lucky_colors_raw[:2]
        }

        return {
            "lucky_colors": lucky_colors,
            "unlucky_colors": unlucky_colors,
            "room_color_suggestions": room_color_suggestions,
            "clothing_colors": lucky_colors_raw,
            "decor_suggestions": [
                f"Use {lucky_colors_raw[0]} for accent walls or major furniture",
                f"Incorporate {lucky_colors_raw[1] if len(lucky_colors_raw) > 1 else lucky_colors_raw[0]} in textiles and accessories",
                f"Avoid large areas of {unlucky_colors_raw[0]} in main living spaces"
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get color therapy: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get color therapy")


@router.get("/element-balance/{kua_number}", response_model=ElementBalanceResponse)
async def get_element_balance(
    kua_number: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get element balance recommendations
    """
    try:
        if kua_number < 1 or kua_number > 9 or kua_number == 5:
            raise HTTPException(status_code=400, detail="Invalid Kua number")

        service = FengShuiService()
        personal_element = service.get_personal_element(kua_number)

        supporting_elements = service.get_supporting_elements(personal_element)
        weakening_elements = service.get_weakening_elements(personal_element)

        # Productive cycle
        productive_cycle = [
            "Wood feeds Fire",
            "Fire creates Earth",
            "Earth produces Metal",
            "Metal collects Water",
            "Water nourishes Wood"
        ]

        # Destructive cycle
        destructive_cycle = [
            "Wood depletes Earth",
            "Earth dams Water",
            "Water extinguishes Fire",
            "Fire melts Metal",
            "Metal cuts Wood"
        ]

        # Balance recommendations
        balance_recs = [
            f"Your personal element is {personal_element.title()}. Enhance it with {supporting_elements[0].title()} element objects.",
            f"Minimize {weakening_elements[0].title()} element presence as it weakens your {personal_element} energy.",
            f"Use the productive cycle: Add {supporting_elements[0]} to strengthen {personal_element}.",
        ]

        return {
            "personal_element": personal_element,
            "supporting_elements": supporting_elements,
            "weakening_elements": weakening_elements,
            "productive_cycle": productive_cycle,
            "destructive_cycle": destructive_cycle,
            "balance_recommendations": balance_recs
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get element balance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get element balance")


@router.get("/stats", response_model=FengShuiStats)
async def get_feng_shui_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's feng shui statistics
    """
    try:
        user_id = current_user["user_id"]
        service = FengShuiService()

        # Get analyses
        analyses_result = await service.get_user_analyses(user_id=user_id)
        analyses = analyses_result["analyses"]

        # Get all recommendations
        all_recommendations = []
        for analysis in analyses:
            recs_result = await service.get_recommendations_for_analysis(
                analysis_id=str(analysis["id"]),
                user_id=user_id
            )
            all_recommendations.extend(recs_result["recommendations"])

        # Calculate stats
        total_analyses = len(analyses)
        total_recommendations = len(all_recommendations)
        implemented = len([r for r in all_recommendations if r.get("is_implemented", False)])
        implementation_rate = (implemented / total_recommendations * 100) if total_recommendations > 0 else 0.0

        # Average effectiveness
        rated_recs = [r for r in all_recommendations if r.get("effectiveness_rating")]
        avg_effectiveness = sum(r["effectiveness_rating"] for r in rated_recs) / len(rated_recs) if rated_recs else 0.0

        # Most used space type
        space_types = [a.get("space_type") for a in analyses if a.get("space_type")]
        most_used_space = max(set(space_types), key=space_types.count) if space_types else None

        # Kua number (from most recent analysis)
        kua_number = analyses[0].get("kua_number") if analyses else None

        return {
            "total_analyses": total_analyses,
            "total_recommendations": total_recommendations,
            "implemented_recommendations": implemented,
            "implementation_rate": implementation_rate,
            "avg_effectiveness_rating": avg_effectiveness,
            "most_used_space_type": most_used_space,
            "kua_number": kua_number
        }

    except Exception as e:
        logger.error(f"Failed to fetch stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")
