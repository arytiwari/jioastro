"""Expert Knowledge API Endpoints"""

from fastapi import APIRouter, Query, HTTPException, status, Depends
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.services.supabase_service import SupabaseService
from app.schemas.expert_knowledge import (
    ContributionCreate,
    ContributionUpdate,
    ContributionResponse,
    ContributionListResponse,
    ContributionReview,
    ContributionImplementation,
    ContributionStatus,
    ContributionCategory,
    ContributionType,
    Priority,
    CommentCreate,
    CommentResponse,
    VoteCreate,
    VoteResponse,
    ImpactCreate,
    ImpactResponse,
    ContributionStats,
    ExpertProfile,
    LeaderboardResponse,
    BulkApproveRequest,
    BulkRejectRequest,
    BulkOperationResponse,
)
from app.core.security import get_current_user

router = APIRouter()

# Initialize Supabase service
supabase_service = SupabaseService()


# ============================================================================
# Contribution Endpoints
# ============================================================================

@router.get("/contributions", response_model=ContributionListResponse)
async def get_contributions(
    status: Optional[ContributionStatus] = Query(None, description="Filter by status"),
    category: Optional[ContributionCategory] = Query(None, description="Filter by category"),
    contribution_type: Optional[ContributionType] = Query(None, description="Filter by type"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    expert_id: Optional[str] = Query(None, description="Filter by expert ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
):
    """
    Get list of expert contributions with filtering and pagination.

    Uses the expert_contribution_stats view for enriched data with vote counts.
    """
    try:
        # Build query using expert_contribution_stats view
        query = supabase_service.client.table("expert_contribution_stats").select("*", count="exact")

        # Apply filters
        if status:
            query = query.eq("status", status.value)
        if category:
            query = query.eq("category", category.value)
        if contribution_type:
            query = query.eq("contribution_type", contribution_type.value)
        if expert_id:
            query = query.eq("expert_id", expert_id)

        # Apply sorting
        ascending = sort_order.lower() == "asc"
        query = query.order(sort_by, desc=not ascending)

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)

        # Execute query
        response = query.execute()

        total = response.count if hasattr(response, 'count') else len(response.data)
        total_pages = (total + page_size - 1) // page_size

        return {
            "contributions": response.data or [],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    except Exception as e:
        print(f"Error fetching contributions: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching contributions: {str(e)}")


@router.get("/contributions/{contribution_id}", response_model=ContributionResponse)
async def get_contribution(contribution_id: int):
    """Get a specific contribution by ID with stats."""
    try:
        response = (supabase_service.client.table("expert_contribution_stats")
                   .select("*")
                   .eq("id", contribution_id)
                   .execute())

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Contribution not found")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching contribution: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching contribution: {str(e)}")


@router.post("/contributions", response_model=ContributionResponse, status_code=status.HTTP_201_CREATED)
async def create_contribution(
    contribution: ContributionCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new expert contribution.

    Requires authentication. The expert_id is automatically set to the current user.
    """
    try:
        # Prepare contribution data
        contribution_data = contribution.model_dump()
        contribution_data["expert_id"] = current_user["sub"]  # Set expert to current user
        contribution_data["status"] = "pending"  # Default status
        contribution_data["version"] = 1  # Initial version

        # Convert enums to strings
        contribution_data["contribution_type"] = contribution_data["contribution_type"].value
        contribution_data["category"] = contribution_data["category"].value
        contribution_data["priority"] = contribution_data["priority"].value

        # Insert into database
        response = (supabase_service.client.table("expert_contributions")
                   .insert(contribution_data)
                   .execute())

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create contribution")

        print(f"✅ Created contribution ID {response.data[0]['id']} by expert {current_user['sub']}")

        # Return the created contribution with stats
        return await get_contribution(response.data[0]["id"])
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating contribution: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating contribution: {str(e)}")


@router.put("/contributions/{contribution_id}", response_model=ContributionResponse)
async def update_contribution(
    contribution_id: int,
    contribution: ContributionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a contribution (only allowed for pending contributions by the owner).
    """
    try:
        # Check if contribution exists and belongs to user
        existing = (supabase_service.client.table("expert_contributions")
                   .select("*")
                   .eq("id", contribution_id)
                   .execute())

        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Contribution not found")

        contribution_data = existing.data[0]

        # Verify ownership
        if contribution_data["expert_id"] != current_user["sub"]:
            raise HTTPException(status_code=403, detail="Not authorized to update this contribution")

        # Only allow updates for pending contributions
        if contribution_data["status"] != "pending":
            raise HTTPException(status_code=400, detail="Can only update pending contributions")

        # Build update data
        update_data = contribution.model_dump(exclude_unset=True)

        # Convert enums to strings if present
        if "contribution_type" in update_data:
            update_data["contribution_type"] = update_data["contribution_type"].value
        if "category" in update_data:
            update_data["category"] = update_data["category"].value
        if "priority" in update_data:
            update_data["priority"] = update_data["priority"].value

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Update contribution
        response = (supabase_service.client.table("expert_contributions")
                   .update(update_data)
                   .eq("id", contribution_id)
                   .execute())

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to update contribution")

        print(f"✅ Updated contribution ID {contribution_id}")

        # Return updated contribution with stats
        return await get_contribution(contribution_id)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating contribution: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating contribution: {str(e)}")


@router.delete("/contributions/{contribution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contribution(
    contribution_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a contribution (only allowed for pending contributions by the owner).
    """
    try:
        # Check if contribution exists and belongs to user
        existing = (supabase_service.client.table("expert_contributions")
                   .select("*")
                   .eq("id", contribution_id)
                   .execute())

        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Contribution not found")

        contribution_data = existing.data[0]

        # Verify ownership
        if contribution_data["expert_id"] != current_user["sub"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this contribution")

        # Only allow deletion for pending contributions
        if contribution_data["status"] != "pending":
            raise HTTPException(status_code=400, detail="Can only delete pending contributions")

        # Delete contribution
        supabase_service.client.table("expert_contributions").delete().eq("id", contribution_id).execute()

        print(f"✅ Deleted contribution ID {contribution_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting contribution: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting contribution: {str(e)}")


# ============================================================================
# Review & Approval Endpoints
# ============================================================================

@router.post("/contributions/{contribution_id}/review", response_model=ContributionResponse)
async def review_contribution(
    contribution_id: int,
    review: ContributionReview,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit a review for a contribution (admin/reviewer only).

    This marks the contribution as 'under_review' and adds review notes.
    """
    try:
        # Check if contribution exists
        existing = (supabase_service.client.table("expert_contributions")
                   .select("*")
                   .eq("id", contribution_id)
                   .execute())

        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Contribution not found")

        # Update contribution with review
        update_data = {
            "status": "under_review",
            "review_notes": review.review_notes,
            "reviewed_by": current_user["sub"],
            "reviewed_at": datetime.utcnow().isoformat(),
        }

        response = (supabase_service.client.table("expert_contributions")
                   .update(update_data)
                   .eq("id", contribution_id)
                   .execute())

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to review contribution")

        print(f"✅ Reviewed contribution ID {contribution_id}")

        # Return updated contribution
        return await get_contribution(contribution_id)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error reviewing contribution: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error reviewing contribution: {str(e)}")


@router.post("/contributions/{contribution_id}/approve", response_model=ContributionResponse)
async def approve_contribution(
    contribution_id: int,
    review: ContributionReview,
    current_user: dict = Depends(get_current_user)
):
    """
    Approve a contribution (admin only).
    """
    try:
        # Check if contribution exists
        existing = (supabase_service.client.table("expert_contributions")
                   .select("*")
                   .eq("id", contribution_id)
                   .execute())

        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Contribution not found")

        # Update contribution status to approved
        update_data = {
            "status": "approved",
            "review_notes": review.review_notes,
            "reviewed_by": current_user["sub"],
            "reviewed_at": datetime.utcnow().isoformat(),
        }

        response = (supabase_service.client.table("expert_contributions")
                   .update(update_data)
                   .eq("id", contribution_id)
                   .execute())

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to approve contribution")

        print(f"✅ Approved contribution ID {contribution_id}")

        # Return updated contribution
        return await get_contribution(contribution_id)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error approving contribution: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error approving contribution: {str(e)}")


@router.post("/contributions/{contribution_id}/reject", response_model=ContributionResponse)
async def reject_contribution(
    contribution_id: int,
    review: ContributionReview,
    current_user: dict = Depends(get_current_user)
):
    """
    Reject a contribution (admin only).
    """
    try:
        # Check if contribution exists
        existing = (supabase_service.client.table("expert_contributions")
                   .select("*")
                   .eq("id", contribution_id)
                   .execute())

        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Contribution not found")

        # Update contribution status to rejected
        update_data = {
            "status": "rejected",
            "review_notes": review.review_notes,
            "reviewed_by": current_user["sub"],
            "reviewed_at": datetime.utcnow().isoformat(),
        }

        response = (supabase_service.client.table("expert_contributions")
                   .update(update_data)
                   .eq("id", contribution_id)
                   .execute())

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to reject contribution")

        print(f"✅ Rejected contribution ID {contribution_id}")

        # Return updated contribution
        return await get_contribution(contribution_id)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error rejecting contribution: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error rejecting contribution: {str(e)}")


@router.post("/contributions/{contribution_id}/implement", response_model=ContributionResponse)
async def mark_contribution_implemented(
    contribution_id: int,
    implementation: ContributionImplementation,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a contribution as implemented (admin/developer only).
    """
    try:
        # Check if contribution exists and is approved
        existing = (supabase_service.client.table("expert_contributions")
                   .select("*")
                   .eq("id", contribution_id)
                   .execute())

        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Contribution not found")

        if existing.data[0]["status"] != "approved":
            raise HTTPException(status_code=400, detail="Can only implement approved contributions")

        # Update contribution status to implemented
        update_data = {
            "status": "implemented",
            "implementation_notes": implementation.implementation_notes,
            "git_commit_hash": implementation.git_commit_hash,
            "implemented_by": current_user["sub"],
            "implemented_at": datetime.utcnow().isoformat(),
        }

        response = (supabase_service.client.table("expert_contributions")
                   .update(update_data)
                   .eq("id", contribution_id)
                   .execute())

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to mark contribution as implemented")

        print(f"✅ Marked contribution ID {contribution_id} as implemented")

        # Return updated contribution
        return await get_contribution(contribution_id)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error marking contribution as implemented: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error marking contribution as implemented: {str(e)}")


# ============================================================================
# Comment Endpoints
# ============================================================================

@router.get("/contributions/{contribution_id}/comments", response_model=List[CommentResponse])
async def get_comments(contribution_id: int):
    """Get all comments for a contribution."""
    try:
        response = (supabase_service.client.table("expert_contribution_comments")
                   .select("*")
                   .eq("contribution_id", contribution_id)
                   .order("created_at", desc=True)
                   .execute())

        return response.data or []
    except Exception as e:
        print(f"Error fetching comments: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching comments: {str(e)}")


@router.post("/contributions/{contribution_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    contribution_id: int,
    comment: CommentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a comment to a contribution."""
    try:
        # Check if contribution exists
        existing = (supabase_service.client.table("expert_contributions")
                   .select("id")
                   .eq("id", contribution_id)
                   .execute())

        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Contribution not found")

        # Create comment
        comment_data = comment.model_dump()
        comment_data["contribution_id"] = contribution_id
        comment_data["user_id"] = current_user["sub"]
        comment_data["comment_type"] = comment_data["comment_type"].value

        response = (supabase_service.client.table("expert_contribution_comments")
                   .insert(comment_data)
                   .execute())

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create comment")

        print(f"✅ Created comment on contribution ID {contribution_id}")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating comment: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating comment: {str(e)}")


# ============================================================================
# Vote Endpoints
# ============================================================================

@router.post("/contributions/{contribution_id}/vote", response_model=VoteResponse)
async def vote_on_contribution(
    contribution_id: int,
    vote: VoteCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Vote on a contribution (upvote or downvote).

    Users can only vote once per contribution. Voting again updates the existing vote.
    """
    try:
        # Check if contribution exists
        existing_contribution = (supabase_service.client.table("expert_contributions")
                                .select("id")
                                .eq("id", contribution_id)
                                .execute())

        if not existing_contribution.data or len(existing_contribution.data) == 0:
            raise HTTPException(status_code=404, detail="Contribution not found")

        # Check if user has already voted
        existing_vote = (supabase_service.client.table("expert_contribution_votes")
                        .select("*")
                        .eq("contribution_id", contribution_id)
                        .eq("user_id", current_user["sub"])
                        .execute())

        vote_data = vote.model_dump()
        vote_data["contribution_id"] = contribution_id
        vote_data["user_id"] = current_user["sub"]

        if existing_vote.data and len(existing_vote.data) > 0:
            # Update existing vote
            response = (supabase_service.client.table("expert_contribution_votes")
                       .update(vote_data)
                       .eq("id", existing_vote.data[0]["id"])
                       .execute())

            print(f"✅ Updated vote on contribution ID {contribution_id}")
        else:
            # Create new vote
            response = (supabase_service.client.table("expert_contribution_votes")
                       .insert(vote_data)
                       .execute())

            print(f"✅ Created vote on contribution ID {contribution_id}")

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to vote on contribution")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error voting on contribution: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error voting on contribution: {str(e)}")


# ============================================================================
# Impact Tracking Endpoints
# ============================================================================

@router.post("/contributions/{contribution_id}/impact", response_model=ImpactResponse, status_code=status.HTTP_201_CREATED)
async def track_impact(
    contribution_id: int,
    impact: ImpactCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Record impact data for a contribution.

    Used to track before/after prediction accuracy improvements.
    """
    try:
        # Check if contribution exists
        existing = (supabase_service.client.table("expert_contributions")
                   .select("id")
                   .eq("id", contribution_id)
                   .execute())

        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Contribution not found")

        # Create impact record
        impact_data = impact.model_dump()
        impact_data["contribution_id"] = contribution_id

        response = (supabase_service.client.table("expert_impact_tracking")
                   .insert(impact_data)
                   .execute())

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to track impact")

        print(f"✅ Tracked impact for contribution ID {contribution_id}")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error tracking impact: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error tracking impact: {str(e)}")


@router.get("/contributions/{contribution_id}/impact", response_model=List[ImpactResponse])
async def get_impact_data(contribution_id: int):
    """Get all impact tracking data for a contribution."""
    try:
        response = (supabase_service.client.table("expert_impact_tracking")
                   .select("*")
                   .eq("contribution_id", contribution_id)
                   .order("created_at", desc=True)
                   .execute())

        return response.data or []
    except Exception as e:
        print(f"Error fetching impact data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching impact data: {str(e)}")


# ============================================================================
# Statistics & Leaderboard Endpoints
# ============================================================================

@router.get("/stats", response_model=ContributionStats)
async def get_contribution_stats():
    """Get overall contribution statistics."""
    try:
        # Get counts by status
        all_contributions = (supabase_service.client.table("expert_contributions")
                            .select("status")
                            .execute())

        contributions = all_contributions.data or []

        stats = {
            "total_contributions": len(contributions),
            "pending_contributions": sum(1 for c in contributions if c["status"] == "pending"),
            "under_review_contributions": sum(1 for c in contributions if c["status"] == "under_review"),
            "approved_contributions": sum(1 for c in contributions if c["status"] == "approved"),
            "implemented_contributions": sum(1 for c in contributions if c["status"] == "implemented"),
            "rejected_contributions": sum(1 for c in contributions if c["status"] == "rejected"),
        }

        # Get vote counts
        all_votes = (supabase_service.client.table("expert_contribution_votes")
                    .select("vote")
                    .execute())

        votes = all_votes.data or []
        stats["total_upvotes"] = sum(1 for v in votes if v["vote"] == 1)
        stats["total_downvotes"] = sum(1 for v in votes if v["vote"] == -1)

        # Get impact metrics
        validated_impacts = (supabase_service.client.table("expert_impact_tracking")
                            .select("accuracy_improvement")
                            .eq("validated", True)
                            .execute())

        impacts = validated_impacts.data or []
        stats["total_validated_impacts"] = len(impacts)
        stats["avg_accuracy_improvement"] = (
            sum(i["accuracy_improvement"] for i in impacts) / len(impacts)
            if impacts else 0.0
        )

        return stats
    except Exception as e:
        print(f"Error fetching stats: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
):
    """
    Get expert leaderboard with rankings.

    Uses the expert_leaderboard view for pre-computed statistics.
    """
    try:
        # Query expert_leaderboard view
        offset = (page - 1) * page_size

        response = (supabase_service.client.table("expert_leaderboard")
                   .select("*", count="exact")
                   .range(offset, offset + page_size - 1)
                   .execute())

        total = response.count if hasattr(response, 'count') else len(response.data)

        return {
            "experts": response.data or [],
            "page": page,
            "page_size": page_size,
            "total": total,
        }
    except Exception as e:
        print(f"Error fetching leaderboard: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching leaderboard: {str(e)}")


# ============================================================================
# Bulk Operations
# ============================================================================

@router.post("/contributions/bulk-approve", response_model=BulkOperationResponse)
async def bulk_approve_contributions(
    request: BulkApproveRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Approve multiple contributions at once (admin only).
    """
    success = []
    failed = []

    for contribution_id in request.contribution_ids:
        try:
            review = ContributionReview(
                review_notes=request.review_notes,
                approved=True
            )
            await approve_contribution(contribution_id, review, current_user)
            success.append(contribution_id)
        except Exception as e:
            failed.append({
                "contribution_id": contribution_id,
                "error": str(e)
            })

    print(f"✅ Bulk approved {len(success)} contributions, {len(failed)} failed")

    return {
        "success": success,
        "failed": failed,
        "total_processed": len(request.contribution_ids)
    }


@router.post("/contributions/bulk-reject", response_model=BulkOperationResponse)
async def bulk_reject_contributions(
    request: BulkRejectRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Reject multiple contributions at once (admin only).
    """
    success = []
    failed = []

    for contribution_id in request.contribution_ids:
        try:
            review = ContributionReview(
                review_notes=request.review_notes,
                approved=False
            )
            await reject_contribution(contribution_id, review, current_user)
            success.append(contribution_id)
        except Exception as e:
            failed.append({
                "contribution_id": contribution_id,
                "error": str(e)
            })

    print(f"✅ Bulk rejected {len(success)} contributions, {len(failed)} failed")

    return {
        "success": success,
        "failed": failed,
        "total_processed": len(request.contribution_ids)
    }
