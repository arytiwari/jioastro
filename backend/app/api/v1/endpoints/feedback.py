"""Feedback API Endpoints - Using Supabase REST API"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.core.security import get_current_user
from app.services.supabase_service import supabase_service

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: FeedbackCreate,
    current_user: dict = Depends(get_current_user)
):
    """Submit feedback for an AI interpretation"""
    try:
        user_id = current_user["user_id"]

        # Get the response to verify it exists and belongs to the user
        # We need to check if the response's query belongs to this user
        # First, let's get all user queries to find the one with this response
        queries = await supabase_service.get_queries(user_id=user_id, limit=1000)

        # Find the query that has this response_id
        response_belongs_to_user = False
        for query in queries:
            if query.get("responses"):
                for response in query["responses"]:
                    if response.get("id") == str(feedback_data.response_id):
                        response_belongs_to_user = True
                        break
            if response_belongs_to_user:
                break

        if not response_belongs_to_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found or doesn't belong to you"
            )

        # Check if feedback already exists for this response
        existing_feedback = await supabase_service.get_feedback_for_response(
            response_id=str(feedback_data.response_id)
        )

        if existing_feedback:
            # Update existing feedback via Supabase client
            updated_feedback = supabase_service.client.table("feedback").update({
                "rating": feedback_data.rating,
                "comment": feedback_data.comment
            }).eq("id", existing_feedback["id"]).execute()

            return updated_feedback.data[0] if updated_feedback.data else existing_feedback

        # Create new feedback
        new_feedback = await supabase_service.create_feedback({
            "response_id": str(feedback_data.response_id),
            "user_id": user_id,
            "rating": feedback_data.rating,
            "comment": feedback_data.comment
        })

        if not new_feedback:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create feedback"
            )

        return new_feedback

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process feedback: {str(e)}"
        )


@router.get("/response/{response_id}", response_model=dict)
async def get_feedback_for_response(
    response_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get feedback for a specific response"""
    try:
        user_id = current_user["user_id"]

        # Verify response belongs to user
        queries = await supabase_service.get_queries(user_id=user_id, limit=1000)

        response_belongs_to_user = False
        for query in queries:
            if query.get("responses"):
                for response in query["responses"]:
                    if response.get("id") == response_id:
                        response_belongs_to_user = True
                        break
            if response_belongs_to_user:
                break

        if not response_belongs_to_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Response not found or doesn't belong to you"
            )

        # Get feedback
        feedback = await supabase_service.get_feedback_for_response(response_id=response_id)

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )

        return feedback

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_feedback_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get feedback statistics (global stats for MVP)"""
    try:
        # For MVP, return global feedback stats
        stats = await supabase_service.get_feedback_stats()
        return stats

    except Exception as e:
        print(f"Error getting feedback stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback statistics: {str(e)}"
        )
