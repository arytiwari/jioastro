"""Profile Schemas"""

from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Optional
from uuid import UUID


class ProfileBase(BaseModel):
    """Base profile schema"""

    name: str = Field(..., min_length=1, max_length=100)
    birth_date: date
    birth_time: time
    birth_lat: float = Field(..., ge=-90, le=90)
    birth_lon: float = Field(..., ge=-180, le=180)
    birth_city: Optional[str] = Field(None, max_length=100)
    birth_timezone: Optional[str] = Field(None, max_length=50)
    is_primary: bool = False


class ProfileCreate(ProfileBase):
    """Schema for creating a new profile"""

    pass


class ProfileUpdate(BaseModel):
    """Schema for updating a profile"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_primary: Optional[bool] = None


class ProfileResponse(ProfileBase):
    """Schema for profile response"""

    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
