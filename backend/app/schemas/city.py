"""City Schemas"""

from pydantic import BaseModel, Field
from typing import Optional


class CityBase(BaseModel):
    """Base city schema"""

    name: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    display_name: str = Field(..., max_length=200)


class CityResponse(CityBase):
    """Schema for city response"""

    id: int

    class Config:
        from_attributes = True


class CitySearchParams(BaseModel):
    """Search parameters for cities"""

    search: Optional[str] = Field(None, description="Search by city or state name")
    state: Optional[str] = Field(None, description="Filter by state")
    limit: int = Field(100, ge=1, le=500, description="Maximum number of results")
