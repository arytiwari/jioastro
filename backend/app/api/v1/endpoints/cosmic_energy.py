"""
Cosmic Energy Score™ API Endpoints
"""

from typing import Optional, List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.services.cosmic_energy_service import cosmic_energy_service
from app.services.supabase_service import supabase_service


router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class CosmicScoreResponse(BaseModel):
    """Response for cosmic energy score"""
    score: int = Field(..., ge=0, le=100, description="Cosmic energy score (0-100)")
    level: str = Field(..., description="Energy level: HIGH ENERGY, MODERATE ENERGY, LOW ENERGY")
    color: str = Field(..., description="Color indicator: green, yellow, red")
    emoji: str = Field(..., description="Emoji indicator: 🟢, 🟡, 🔴")
    best_for: List[str] = Field(..., description="Activities best suited for this energy level")
    avoid: List[str] = Field(..., description="Activities to avoid")
    breakdown: dict = Field(..., description="Score breakdown by component")
    calculated_at: str = Field(..., description="ISO datetime of calculation")
    valid_for_date: str = Field(..., description="Date this score is valid for")


class FriendScoreResponse(BaseModel):
    """Friend's cosmic score (limited visibility)"""
    user_id: str
    name: str
    score: int
    level: str
    emoji: str
    valid_for_date: str


class DailyScoreTrend(BaseModel):
    """Daily score data point"""
    date: str
    score: int
    level: str
    emoji: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/my-score", response_model=CosmicScoreResponse)
async def get_my_cosmic_score(
    profile_id: str,
    target_date: Optional[str] = None,  # ISO date string (YYYY-MM-DD)
    current_user: dict = Depends(get_current_user)
):
    """
    Get my cosmic energy score for today or a specific date

    Returns detailed breakdown of the score calculation
    """
    try:
        user_id = current_user["user_id"]

        # Get profile
        profile = await supabase_service.get_profile(
            profile_id=profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Get birth chart
        chart = await supabase_service.get_chart(
            profile_id=profile_id,
            chart_type="D1"
        )

        if not chart or 'chart_data' not in chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found. Please calculate chart first."
            )

        chart_data = chart['chart_data']

        # Parse target date
        if target_date:
            try:
                parsed_date = date.fromisoformat(target_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        else:
            parsed_date = date.today()

        # Calculate cosmic score
        score_data = cosmic_energy_service.calculate_cosmic_score(
            birth_chart=chart_data,
            target_date=parsed_date,
            target_time=datetime.now()
        )

        return CosmicScoreResponse(**score_data)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error calculating cosmic score: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate cosmic score: {str(e)}"
        )


@router.get("/30-day-trend", response_model=List[DailyScoreTrend])
async def get_30_day_trend(
    profile_id: str,
    start_date: Optional[str] = None,  # ISO date string
    current_user: dict = Depends(get_current_user)
):
    """
    Get 30-day cosmic energy trend

    Used for displaying charts and planning ahead
    """
    try:
        user_id = current_user["user_id"]

        # Get profile
        profile = await supabase_service.get_profile(
            profile_id=profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Get birth chart
        chart = await supabase_service.get_chart(
            profile_id=profile_id,
            chart_type="D1"
        )

        if not chart or 'chart_data' not in chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found. Please calculate chart first."
            )

        chart_data = chart['chart_data']

        # Parse start date
        if start_date:
            try:
                parsed_start = date.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        else:
            parsed_start = date.today()

        # Calculate 30-day scores
        scores = cosmic_energy_service.calculate_30_day_scores(
            birth_chart=chart_data,
            start_date=parsed_start
        )

        return [DailyScoreTrend(**score) for score in scores]

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error calculating 30-day trend: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate trend: {str(e)}"
        )


@router.get("/friends-scores", response_model=List[FriendScoreResponse])
async def get_friends_scores(
    profile_id: str,
    target_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get cosmic scores for all friends (for comparison)

    Only returns friends who have:
    1. Accepted friend connection
    2. Enabled score visibility in privacy settings
    """
    try:
        user_id = current_user["user_id"]

        # TODO: Implement friend connections table
        # For now, return empty list (Phase 2)

        # In Phase 2, this will:
        # 1. Query friend_connections table
        # 2. Get each friend's profile and chart
        # 3. Calculate their scores
        # 4. Return list sorted by score (highest first)

        return []

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting friends' scores: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get friends' scores: {str(e)}"
        )


@router.post("/share-template")
async def generate_share_template(
    profile_id: str,
    target_date: Optional[str] = None,
    template_type: str = "instagram_story",  # instagram_story, whatsapp_status, twitter
    current_user: dict = Depends(get_current_user)
):
    """
    Generate shareable image/template for social media

    Returns URL to generated image or template data
    """
    try:
        user_id = current_user["user_id"]

        # Get profile
        profile = await supabase_service.get_profile(
            profile_id=profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Get birth chart
        chart = await supabase_service.get_chart(
            profile_id=profile_id,
            chart_type="D1"
        )

        if not chart or 'chart_data' not in chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found"
            )

        chart_data = chart['chart_data']

        # Parse target date
        if target_date:
            parsed_date = date.fromisoformat(target_date)
        else:
            parsed_date = date.today()

        # Calculate cosmic score
        score_data = cosmic_energy_service.calculate_cosmic_score(
            birth_chart=chart_data,
            target_date=parsed_date,
            target_time=datetime.now()
        )

        # Generate template data (Phase 2: Actually generate images)
        template_data = {
            "template_type": template_type,
            "score": score_data["score"],
            "emoji": score_data["emoji"],
            "level": score_data["level"],
            "best_for": score_data["best_for"][:2],  # Top 2
            "text": f"⚡ {score_data['score']}%\nMY COSMIC ENERGY TODAY\n\nBest for: {', '.join(score_data['best_for'][:2])}\n\nFind your cosmic score ↗",
            "background_color": score_data["color"],
            "cta": "Get yours at JioAstro.com"
        }

        return {
            "success": True,
            "template_data": template_data,
            "share_text": f"My cosmic energy today: {score_data['emoji']} {score_data['score']}%! Find yours on JioAstro 🌟"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating share template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate template: {str(e)}"
        )
