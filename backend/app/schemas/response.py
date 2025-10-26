"""Response Schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ResponseCreate(BaseModel):
    """Schema for creating a response"""

    query_id: UUID
    interpretation: str
    ai_model: str
    tokens_used: int


class ResponseResponse(BaseModel):
    """Schema for response"""

    id: UUID
    query_id: UUID
    interpretation: str
    ai_model: Optional[str]
    tokens_used: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
