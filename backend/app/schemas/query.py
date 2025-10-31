"""Query Schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class QueryCreate(BaseModel):
    """Schema for creating a query"""

    profile_id: UUID
    question: str = Field(..., min_length=10, max_length=1000)
    category: Optional[str] = Field(None, max_length=50)


class QueryResponse(BaseModel):
    """Schema for query response"""

    id: UUID
    user_id: UUID
    profile_id: UUID
    question: str
    category: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
