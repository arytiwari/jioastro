"""Profile Schemas"""

from pydantic import BaseModel, Field, validator
from datetime import date, time, datetime
from typing import Optional, Literal, Dict, Any
from uuid import UUID


class ProfileBase(BaseModel):
    """Base profile schema"""

    name: str = Field(..., min_length=1, max_length=100)
    birth_date: date
    birth_time: time
    birth_lat: float = Field(..., ge=-90, le=90)
    birth_lon: float = Field(..., ge=-180, le=180)
    birth_city: Optional[str] = Field(None, max_length=100)
    city_id: Optional[int] = Field(None, description="Foreign key to cities table")
    birth_timezone: Optional[str] = Field(None, max_length=50)
    gender: Optional[Literal["male", "female", "other"]] = Field(
        None,
        description="Optional gender for astrological interpretations. Values: male, female, other"
    )
    is_primary: bool = False

    @validator("gender")
    def validate_gender(cls, v):
        """Validate gender field"""
        if v is not None and v not in ["male", "female", "other"]:
            raise ValueError("Gender must be one of: male, female, other")
        return v


class ProfileCreate(ProfileBase):
    """Schema for creating a new profile"""

    pass


class ProfileUpdate(BaseModel):
    """Schema for updating a profile"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    gender: Optional[Literal["male", "female", "other"]] = None
    is_primary: Optional[bool] = None
    birth_city: Optional[str] = Field(None, max_length=100)
    city_id: Optional[int] = Field(None, description="Foreign key to cities table")


class ProfileResponse(ProfileBase):
    """Schema for profile response"""

    id: UUID
    user_id: UUID
    created_at: datetime
    city: Optional[Dict[str, Any]] = Field(None, description="City information from cities table")

    class Config:
        from_attributes = True
