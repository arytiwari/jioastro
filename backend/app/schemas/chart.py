"""Chart Schemas"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID


class ChartCalculateRequest(BaseModel):
    """Schema for chart calculation request"""

    profile_id: UUID
    chart_type: str = Field(..., pattern="^(D1|D9)$")


class ChartResponse(BaseModel):
    """Schema for chart response"""

    id: UUID
    profile_id: UUID
    chart_type: str
    chart_data: Dict[str, Any]
    chart_svg: Optional[str] = None
    calculated_at: datetime

    class Config:
        from_attributes = True
