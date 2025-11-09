"""
AstroTwin Circles API Endpoints
Community discovery and pattern analysis based on chart similarity
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from decimal import Decimal

from app.schemas.astrotwin_circles import (
    # Request schemas
    EnableDiscoveryRequest,
    CreateCircleRequest,
    UpdateCircleRequest,
    JoinCircleRequest,
    UpdateMembershipRequest,
    ReportOutcomeRequest,
    FindTwinsRequest,
    CreatePostRequest,
    CreateReplyRequest,
    # Response schemas
    ChartVector,
    AstroTwinMatchListResponse,
    AstroTwinCircle,
    AstroTwinCircleListResponse,
    CircleMembership,
    CircleMembershipListResponse,
    LifeOutcome,
    LifeOutcomeListResponse,
    CirclePost,
    CirclePostListResponse,
    CirclePostReply,
    CirclePostReplyListResponse,
    AstroTwinStats,
    CircleStats,
    OutcomeType,
    CircleType,
)
from app.core.security import get_current_user
from app.services.astrotwin_service import AstroTwinService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# =========================================================================
# DISCOVERY ENDPOINTS
# =========================================================================

@router.post("/enable-discovery", status_code=status.HTTP_200_OK)
async def enable_discovery(
    profile_id: str = Query(..., description="Profile ID to enable discovery for"),
    request: EnableDiscoveryRequest = EnableDiscoveryRequest(),
    current_user: dict = Depends(get_current_user)
):
    """
    Enable AstroTwin discovery for a user's profile
    Generates and stores chart vector for similarity search
    """
    try:
        service = AstroTwinService()
        result = await service.enable_discovery(
            user_id=current_user["user_id"],
            profile_id=profile_id,
            privacy_opt_in=request.privacy_opt_in,
            visible_in_search=request.visible_in_search,
            allow_pattern_learning=request.allow_pattern_learning
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Enable discovery error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable discovery: {str(e)}"
        )


@router.post("/find-twins", response_model=AstroTwinMatchListResponse)
async def find_twins(
    request: FindTwinsRequest = FindTwinsRequest(),
    current_user: dict = Depends(get_current_user)
):
    """
    Find AstroTwins for the current user
    Returns list of similar charts with similarity scores
    """
    try:
        service = AstroTwinService()
        result = await service.find_twins(
            user_id=current_user["user_id"],
            similarity_threshold=float(request.similarity_threshold),
            limit=request.limit,
            filter_by=request.filter_by
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Find twins error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find twins: {str(e)}"
        )


@router.get("/my-twins", response_model=AstroTwinMatchListResponse)
async def get_my_twins(
    similarity_threshold: float = Query(0.3, ge=0.0, le=1.0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user)
):
    """
    Quick endpoint to get user's AstroTwins with default settings
    """
    try:
        service = AstroTwinService()
        result = await service.find_twins(
            user_id=current_user["user_id"],
            similarity_threshold=similarity_threshold,
            limit=limit
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get my twins error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get twins: {str(e)}"
        )


# =========================================================================
# CIRCLE MANAGEMENT ENDPOINTS
# =========================================================================

@router.post("/circles", response_model=AstroTwinCircle, status_code=status.HTTP_201_CREATED)
async def create_circle(
    request: CreateCircleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new AstroTwin circle"""
    try:
        service = AstroTwinService()

        circle_data = {
            "circle_name": request.circle_name,
            "circle_description": request.circle_description,
            "circle_type": request.circle_type.value,
            "is_private": request.is_private,
            "requires_approval": request.requires_approval,
            "max_members": request.max_members,
            "similarity_threshold": request.similarity_threshold,
            "feature_filters": request.feature_filters,
            "tags": request.tags or []
        }

        result = await service.create_circle(
            user_id=current_user["user_id"],
            circle_data=circle_data
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Create circle error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create circle: {str(e)}"
        )


@router.get("/circles", response_model=AstroTwinCircleListResponse)
async def list_circles(
    circle_type: Optional[CircleType] = Query(None),
    is_private: Optional[bool] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    List all circles (public circles + user's circles)
    """
    try:
        service = AstroTwinService()
        result = await service.get_circles(
            user_id=current_user["user_id"],
            circle_type=circle_type.value if circle_type else None,
            is_private=is_private
        )
        return result
    except Exception as e:
        logger.error(f"List circles error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list circles: {str(e)}"
        )


@router.get("/circles/{circle_id}", response_model=AstroTwinCircle)
async def get_circle(
    circle_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get circle details"""
    try:
        service = AstroTwinService()
        circle = await service.get_circle_by_id(
            circle_id=circle_id,
            user_id=current_user["user_id"]
        )

        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found or access denied"
            )

        return circle
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get circle error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get circle: {str(e)}"
        )


@router.patch("/circles/{circle_id}", response_model=AstroTwinCircle)
async def update_circle(
    circle_id: str,
    request: UpdateCircleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update circle settings (admin/creator only)"""
    try:
        service = AstroTwinService()

        # First check if user is admin/creator
        circle = await service.get_circle_by_id(circle_id, current_user["user_id"])
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found"
            )

        # Check permissions
        if circle.get("user_role") not in ["admin", "creator"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can update circle settings"
            )

        # Build update data (only non-None fields)
        update_data = {k: v for k, v in request.model_dump().items() if v is not None}

        if not update_data:
            return circle  # Nothing to update

        # Update via Supabase
        result = await service.supabase.update(
            "astrotwin_circles",
            data=update_data,
            filters={"id": circle_id}
        )

        if result:
            return result[0]

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update circle"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update circle error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update circle: {str(e)}"
        )


@router.delete("/circles/{circle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_circle(
    circle_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a circle (creator only)"""
    try:
        service = AstroTwinService()

        # Check if user is creator
        circle = await service.get_circle_by_id(circle_id, current_user["user_id"])
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found"
            )

        if circle.get("creator_user_id") != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the creator can delete this circle"
            )

        # Delete
        await service.supabase.delete(
            "astrotwin_circles",
            filters={"id": circle_id}
        )

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete circle error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete circle: {str(e)}"
        )


# =========================================================================
# MEMBERSHIP ENDPOINTS
# =========================================================================

@router.post("/circles/{circle_id}/join")
async def join_circle(
    circle_id: str,
    request: JoinCircleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Request to join or auto-join a circle"""
    try:
        service = AstroTwinService()
        result = await service.join_circle(
            circle_id=circle_id,
            user_id=current_user["user_id"],
            share_outcomes=request.share_outcomes
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Join circle error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join circle: {str(e)}"
        )


@router.post("/circles/{circle_id}/leave")
async def leave_circle(
    circle_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Leave a circle"""
    try:
        service = AstroTwinService()
        result = await service.leave_circle(
            circle_id=circle_id,
            user_id=current_user["user_id"]
        )
        return result
    except Exception as e:
        logger.error(f"Leave circle error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to leave circle: {str(e)}"
        )


@router.get("/circles/{circle_id}/members", response_model=CircleMembershipListResponse)
async def get_circle_members(
    circle_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get list of circle members"""
    try:
        service = AstroTwinService()

        # Check access (must be a member or circle must be public)
        circle = await service.get_circle_by_id(circle_id, current_user["user_id"])
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found or access denied"
            )

        # Get memberships
        memberships = await service.supabase.select(
            "circle_memberships",
            filters={"circle_id": circle_id, "join_status": "active"}
        )

        return {
            "memberships": memberships or [],
            "total_count": len(memberships or [])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get members error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get members: {str(e)}"
        )


@router.patch("/circles/{circle_id}/members/{user_id}")
async def update_membership(
    circle_id: str,
    user_id: str,
    request: UpdateMembershipRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update membership (admin only - approve/reject, change role)"""
    try:
        service = AstroTwinService()

        # Check if current user is admin
        circle = await service.get_circle_by_id(circle_id, current_user["user_id"])
        if not circle or circle.get("user_role") not in ["admin", "moderator"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        # Build update data
        update_data = {k: v for k, v in request.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Update membership
        result = await service.supabase.update(
            "circle_memberships",
            data=update_data,
            filters={"circle_id": circle_id, "user_id": user_id}
        )

        if result:
            return {"success": True, "message": "Membership updated"}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update membership error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update membership: {str(e)}"
        )


# =========================================================================
# LIFE OUTCOMES ENDPOINTS
# =========================================================================

@router.post("/outcomes", response_model=LifeOutcome, status_code=status.HTTP_201_CREATED)
async def report_outcome(
    request: ReportOutcomeRequest,
    profile_id: Optional[str] = Query(None, description="Profile ID for context"),
    current_user: dict = Depends(get_current_user)
):
    """Report a life outcome for pattern analysis"""
    try:
        service = AstroTwinService()

        outcome_data = {
            "profile_id": profile_id,
            "outcome_type": request.outcome_type.value,
            "outcome_title": request.outcome_title,
            "outcome_date": request.outcome_date.isoformat(),
            "outcome_result": request.outcome_result.value,
            "user_rating": request.user_rating,
            "user_notes": request.user_notes,
            "share_anonymously": request.share_anonymously,
            "dasha_context": request.dasha_context,
            "transit_context": request.transit_context,
            "chart_factors": request.chart_factors
        }

        result = await service.report_outcome(
            user_id=current_user["user_id"],
            outcome_data=outcome_data
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Report outcome error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to report outcome: {str(e)}"
        )


@router.get("/outcomes", response_model=LifeOutcomeListResponse)
async def list_outcomes(
    outcome_type: Optional[OutcomeType] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Get user's reported outcomes"""
    try:
        service = AstroTwinService()
        result = await service.get_user_outcomes(
            user_id=current_user["user_id"],
            outcome_type=outcome_type.value if outcome_type else None,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"List outcomes error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list outcomes: {str(e)}"
        )


# =========================================================================
# CIRCLE POSTS ENDPOINTS (Community features)
# =========================================================================

@router.post("/posts", response_model=CirclePost, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: CreatePostRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a post in a circle"""
    try:
        service = AstroTwinService()

        # Check if user is a member
        circle = await service.get_circle_by_id(request.circle_id, current_user["user_id"])
        if not circle or circle.get("user_join_status") != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be an active member to post"
            )

        post_data = {
            "circle_id": request.circle_id,
            "user_id": current_user["user_id"],
            "post_type": request.post_type.value,
            "post_title": request.post_title,
            "post_content": request.post_content
        }

        result = await service.supabase.insert("circle_posts", post_data)

        if result:
            return result[0]

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create post"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create post error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {str(e)}"
        )


@router.get("/circles/{circle_id}/posts", response_model=CirclePostListResponse)
async def get_circle_posts(
    circle_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Get posts from a circle"""
    try:
        service = AstroTwinService()

        # Check access
        circle = await service.get_circle_by_id(circle_id, current_user["user_id"])
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found or access denied"
            )

        posts = await service.supabase.select(
            "circle_posts",
            filters={"circle_id": circle_id, "is_hidden": False},
            order="created_at.desc",
            limit=limit
        )

        return {
            "posts": posts or [],
            "total_count": len(posts or [])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get posts error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get posts: {str(e)}"
        )


@router.post("/posts/{post_id}/replies", response_model=CirclePostReply, status_code=status.HTTP_201_CREATED)
async def create_reply(
    post_id: str,
    request: CreateReplyRequest,
    current_user: dict = Depends(get_current_user)
):
    """Reply to a circle post"""
    try:
        service = AstroTwinService()

        # Get post to verify circle membership
        post = await service.supabase.select(
            "circle_posts",
            filters={"id": post_id}
        )

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        circle_id = post[0]["circle_id"]

        # Check membership
        circle = await service.get_circle_by_id(circle_id, current_user["user_id"])
        if not circle or circle.get("user_join_status") != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be an active member to reply"
            )

        reply_data = {
            "post_id": post_id,
            "user_id": current_user["user_id"],
            "reply_content": request.reply_content
        }

        result = await service.supabase.insert("circle_post_replies", reply_data)

        if result:
            return result[0]

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create reply"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create reply error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reply: {str(e)}"
        )


@router.get("/posts/{post_id}/replies", response_model=CirclePostReplyListResponse)
async def get_post_replies(
    post_id: str,
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user)
):
    """Get replies to a post"""
    try:
        service = AstroTwinService()

        replies = await service.supabase.select(
            "circle_post_replies",
            filters={"post_id": post_id},
            order="created_at.asc",
            limit=limit
        )

        return {
            "replies": replies or [],
            "total_count": len(replies or [])
        }

    except Exception as e:
        logger.error(f"Get replies error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get replies: {str(e)}"
        )


# =========================================================================
# STATS ENDPOINTS
# =========================================================================

@router.get("/stats", response_model=AstroTwinStats)
async def get_user_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get user's AstroTwin statistics"""
    try:
        service = AstroTwinService()
        result = await service.get_user_stats(current_user["user_id"])
        return result
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/circles/{circle_id}/stats", response_model=CircleStats)
async def get_circle_stats(
    circle_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get circle statistics"""
    try:
        service = AstroTwinService()

        # Check access
        circle = await service.get_circle_by_id(circle_id, current_user["user_id"])
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found or access denied"
            )

        # Get member count
        memberships = await service.supabase.select(
            "circle_memberships",
            filters={"circle_id": circle_id, "join_status": "active"}
        )
        member_count = len(memberships or [])

        # Get post count
        posts = await service.supabase.select(
            "circle_posts",
            filters={"circle_id": circle_id}
        )
        total_posts = len(posts or [])

        # Get insights count
        insights = await service.supabase.select(
            "circle_insights",
            filters={"circle_id": circle_id}
        )
        total_insights = len(insights or [])

        return {
            "circle_id": circle_id,
            "member_count": member_count,
            "active_members_last_30_days": 0,  # TODO: Implement
            "total_posts": total_posts,
            "total_insights": total_insights,
            "average_similarity_score": None,  # TODO: Calculate from vectors
            "top_shared_features": []  # TODO: Calculate
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get circle stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get circle stats: {str(e)}"
        )
