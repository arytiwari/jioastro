"""Feedback API Endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.db.database import get_db
from app.models.feedback import Feedback
from app.models.response import Response as ResponseModel
from app.models.query import Query
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Submit feedback for an AI interpretation"""

    user_id = UUID(current_user["user_id"])

    # Verify response exists and belongs to user
    response_result = await db.execute(
        select(ResponseModel)
        .join(Query, Query.id == ResponseModel.query_id)
        .where(
            ResponseModel.id == feedback_data.response_id,
            Query.user_id == user_id
        )
    )

    response = response_result.scalar_one_or_none()

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found or doesn't belong to you"
        )

    # Check if feedback already exists
    existing_feedback_result = await db.execute(
        select(Feedback).where(
            Feedback.response_id == feedback_data.response_id,
            Feedback.user_id == user_id
        )
    )

    existing_feedback = existing_feedback_result.scalar_one_or_none()

    if existing_feedback:
        # Update existing feedback
        existing_feedback.rating = feedback_data.rating
        existing_feedback.comment = feedback_data.comment
        await db.commit()
        await db.refresh(existing_feedback)
        return existing_feedback

    # Create new feedback
    new_feedback = Feedback(
        response_id=feedback_data.response_id,
        user_id=user_id,
        rating=feedback_data.rating,
        comment=feedback_data.comment
    )

    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)

    return new_feedback


@router.get("/response/{response_id}", response_model=FeedbackResponse)
async def get_feedback_for_response(
    response_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get feedback for a specific response"""

    user_id = UUID(current_user["user_id"])

    feedback_result = await db.execute(
        select(Feedback).where(
            Feedback.response_id == response_id,
            Feedback.user_id == user_id
        )
    )

    feedback = feedback_result.scalar_one_or_none()

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )

    return feedback


@router.get("/stats", response_model=dict)
async def get_feedback_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get feedback statistics (admin or user stats)"""

    user_id = UUID(current_user["user_id"])

    # Get user's feedback stats
    result = await db.execute(
        select(
            func.count(Feedback.id).label("total_feedbacks"),
            func.avg(Feedback.rating).label("average_rating")
        )
        .join(ResponseModel, ResponseModel.id == Feedback.response_id)
        .join(Query, Query.id == ResponseModel.query_id)
        .where(Query.user_id == user_id)
    )

    stats = result.one()

    return {
        "total_feedbacks": stats.total_feedbacks or 0,
        "average_rating": round(float(stats.average_rating or 0), 2)
    }
