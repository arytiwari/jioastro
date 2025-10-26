"""Feedback Schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class FeedbackCreate(BaseModel):
    """Schema for creating feedback"""

    response_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""

    id: UUID
    response_id: UUID
    user_id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
