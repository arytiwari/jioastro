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

        # Generate unique share code for tracking
        import secrets
        share_code = secrets.token_urlsafe(8)

        # Track share analytics
        await supabase_service.insert_data(
            table="share_analytics",
            data={
                "user_id": user_id,
                "share_type": "cosmic_score",
                "platform": template_type,
                "share_code": share_code
            }
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
            "cta": "Get yours at JioAstro.com",
            "share_url": f"https://jioastro.com/invite/{share_code}"
        }

        return {
            "success": True,
            "template_data": template_data,
            "share_text": f"My cosmic energy today: {score_data['emoji']} {score_data['score']}%! Find yours on JioAstro 🌟\nhttps://jioastro.com/invite/{share_code}",
            "share_code": share_code
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating share template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate template: {str(e)}"
        )


# ============================================================================
# FRIEND CONNECTION ENDPOINTS (Viral Loop)
# ============================================================================

class FriendInviteRequest(BaseModel):
    """Request to invite a friend"""
    friend_email: str = Field(..., description="Friend's email address")


class FriendConnectionResponse(BaseModel):
    """Friend connection details"""
    id: str
    friend_user_id: str
    friend_name: str
    status: str
    invited_at: str
    share_cosmic_score: bool


@router.post("/invite-friend")
async def invite_friend(
    request: FriendInviteRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Invite a friend to connect and share cosmic scores
    """
    try:
        user_id = current_user["user_id"]

        # Check if friend exists
        friend_users = await supabase_service.query_data(
            table="auth.users",
            filters={"email": request.friend_email}
        )

        if not friend_users:
            # Friend doesn't have account - send invitation email
            # TODO: Implement email invitation system
            return {
                "success": True,
                "message": "Invitation email sent",
                "pending_invitation": True
            }

        friend_user_id = friend_users[0]["id"]

        # Check if already connected
        existing = await supabase_service.query_data(
            table="friend_connections",
            filters={
                "user_id": user_id,
                "friend_user_id": friend_user_id
            }
        )

        if existing:
            return {
                "success": False,
                "message": "Friend request already exists"
            }

        # Create friend connection
        connection = await supabase_service.insert_data(
            table="friend_connections",
            data={
                "user_id": user_id,
                "friend_user_id": friend_user_id,
                "status": "pending"
            }
        )

        # Track engagement
        await supabase_service.upsert_data(
            table="daily_engagement",
            data={
                "user_id": user_id,
                "engagement_date": date.today().isoformat(),
                "invited_friend": True
            },
            conflict_columns=["user_id", "engagement_date"]
        )

        return {
            "success": True,
            "message": "Friend request sent",
            "connection_id": connection["id"]
        }

    except Exception as e:
        print(f"Error inviting friend: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invite friend: {str(e)}"
        )


@router.get("/friend-connections", response_model=List[FriendConnectionResponse])
async def get_friend_connections(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all friend connections (pending and accepted)
    """
    try:
        user_id = current_user["user_id"]

        # Get connections where user is requester or receiver
        connections = await supabase_service.raw_query(
            f"""
            SELECT
                fc.id,
                fc.friend_user_id,
                p.name as friend_name,
                fc.status,
                fc.invited_at,
                fc.share_cosmic_score
            FROM friend_connections fc
            LEFT JOIN auth.users u ON fc.friend_user_id = u.id
            LEFT JOIN profiles p ON p.user_id = u.id
            WHERE fc.user_id = '{user_id}'
            ORDER BY fc.created_at DESC
            """
        )

        return [
            FriendConnectionResponse(
                id=conn["id"],
                friend_user_id=conn["friend_user_id"],
                friend_name=conn.get("friend_name", "Unknown"),
                status=conn["status"],
                invited_at=conn["invited_at"],
                share_cosmic_score=conn["share_cosmic_score"]
            )
            for conn in connections
        ]

    except Exception as e:
        print(f"Error getting friend connections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get connections: {str(e)}"
        )


@router.post("/accept-friend/{connection_id}")
async def accept_friend_request(
    connection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Accept a friend request
    """
    try:
        user_id = current_user["user_id"]

        # Verify this is the friend being invited
        connection = await supabase_service.get_by_id(
            table="friend_connections",
            id=connection_id
        )

        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection not found"
            )

        if connection["friend_user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to accept this request"
            )

        # Update connection status
        await supabase_service.update_data(
            table="friend_connections",
            id=connection_id,
            data={
                "status": "accepted",
                "accepted_at": datetime.now().isoformat()
            }
        )

        return {
            "success": True,
            "message": "Friend request accepted"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error accepting friend request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to accept request: {str(e)}"
        )


# ============================================================================
# PUSH NOTIFICATION ENDPOINTS
# ============================================================================

class PushTokenRequest(BaseModel):
    """Push notification token registration"""
    token: str = Field(..., description="FCM/APNS token")
    platform: str = Field(..., description="ios, android, or web")
    device_id: Optional[str] = None


@router.post("/register-push-token")
async def register_push_token(
    request: PushTokenRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Register device for push notifications
    """
    try:
        user_id = current_user["user_id"]

        # Upsert token (update if exists, insert if not)
        await supabase_service.upsert_data(
            table="push_notification_tokens",
            data={
                "user_id": user_id,
                "token": request.token,
                "platform": request.platform,
                "device_id": request.device_id,
                "last_used_at": datetime.now().isoformat()
            },
            conflict_columns=["user_id", "token"]
        )

        return {
            "success": True,
            "message": "Push notifications enabled"
        }

    except Exception as e:
        print(f"Error registering push token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register token: {str(e)}"
        )


@router.put("/notification-preferences")
async def update_notification_preferences(
    daily_score_enabled: bool = True,
    weekly_summary_enabled: bool = True,
    friend_activity_enabled: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Update push notification preferences
    """
    try:
        user_id = current_user["user_id"]

        # Update all user's tokens
        await supabase_service.raw_query(
            f"""
            UPDATE push_notification_tokens
            SET
                daily_score_enabled = {daily_score_enabled},
                weekly_summary_enabled = {weekly_summary_enabled},
                friend_activity_enabled = {friend_activity_enabled},
                updated_at = NOW()
            WHERE user_id = '{user_id}'
            """
        )

        return {
            "success": True,
            "preferences": {
                "daily_score_enabled": daily_score_enabled,
                "weekly_summary_enabled": weekly_summary_enabled,
                "friend_activity_enabled": friend_activity_enabled
            }
        }

    except Exception as e:
        print(f"Error updating preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


# ============================================================================
# WIDGET API ENDPOINTS
# ============================================================================

@router.get("/widget-data")
async def get_widget_data(
    profile_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get compact data for home screen widget

    Optimized for minimal data transfer and fast rendering
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

        # Check cache first
        cached_score = await supabase_service.query_data(
            table="cosmic_score_cache",
            filters={
                "profile_id": profile_id,
                "score_date": date.today().isoformat()
            }
        )

        if cached_score:
            score_data = cached_score[0]
            return {
                "score": score_data["score"],
                "emoji": score_data["emoji"],
                "level": score_data["level"],
                "color": score_data["color"],
                "best_for": score_data["best_for"][:2],  # Top 2 only
                "cached": True
            }

        # Calculate if not cached
        chart = await supabase_service.get_chart(
            profile_id=profile_id,
            chart_type="D1"
        )

        if not chart or 'chart_data' not in chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found"
            )

        score_data = cosmic_energy_service.calculate_cosmic_score(
            birth_chart=chart['chart_data'],
            target_date=date.today(),
            target_time=datetime.now()
        )

        # Cache for future requests
        await supabase_service.insert_data(
            table="cosmic_score_cache",
            data={
                "profile_id": profile_id,
                "score_date": date.today().isoformat(),
                "score": score_data["score"],
                "level": score_data["level"],
                "color": score_data["color"],
                "emoji": score_data["emoji"],
                "best_for": score_data["best_for"],
                "avoid": score_data["avoid"],
                "breakdown": score_data["breakdown"]
            }
        )

        return {
            "score": score_data["score"],
            "emoji": score_data["emoji"],
            "level": score_data["level"],
            "color": score_data["color"],
            "best_for": score_data["best_for"][:2],
            "cached": False
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting widget data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget data: {str(e)}"
        )


@router.post("/track-engagement")
async def track_engagement(
    action: str,  # viewed_cosmic_score, shared_cosmic_score, invited_friend, completed_astrowordle
    current_user: dict = Depends(get_current_user)
):
    """
    Track user engagement for streak and analytics
    """
    try:
        user_id = current_user["user_id"]
        today = date.today().isoformat()

        # Get or create today's engagement record
        engagement = await supabase_service.query_data(
            table="daily_engagement",
            filters={
                "user_id": user_id,
                "engagement_date": today
            }
        )

        if engagement:
            # Update existing record
            update_data = {action: True}
            await supabase_service.update_data(
                table="daily_engagement",
                id=engagement[0]["id"],
                data=update_data
            )
        else:
            # Create new record with streak calculation
            # TODO: Implement streak calculation
            current_streak = 1  # Simplified for now

            await supabase_service.insert_data(
                table="daily_engagement",
                data={
                    "user_id": user_id,
                    "engagement_date": today,
                    action: True,
                    "current_streak": current_streak
                }
            )

        return {
            "success": True,
            "action": action,
            "date": today
        }

    except Exception as e:
        print(f"Error tracking engagement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track engagement: {str(e)}"
        )
