"""
Pydantic schemas for Varshaphal (Annual Predictions) API.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID


# Request Schemas

class VarshapalGenerateRequest(BaseModel):
    """Request to generate Varshaphal for a profile."""
    profile_id: str = Field(..., description="Profile ID for which to generate Varshaphal")
    target_year: int = Field(..., description="Year for which to calculate (e.g., 2025)")
    force_refresh: bool = Field(default=False, description="Force recalculation even if cached")

    class Config:
        json_schema_extra = {
            "example": {
                "profile_id": "550e8400-e29b-41d4-a716-446655440000",
                "target_year": 2025,
                "force_refresh": False
            }
        }


class VarshapalHistoryRequest(BaseModel):
    """Request to get Varshaphal history."""
    profile_id: Optional[str] = Field(None, description="Filter by profile ID")
    limit: int = Field(default=10, ge=1, le=50, description="Number of results")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


# Response Schemas

class PlanetPosition(BaseModel):
    """Planet position in Varshaphal chart."""
    longitude: float = Field(..., description="Longitude in degrees")
    sign: str = Field(..., description="Zodiac sign name")
    sign_num: int = Field(..., description="Sign number (1-12)")
    degree_in_sign: float = Field(..., description="Degree within the sign")
    nakshatra: str = Field(..., description="Nakshatra (lunar mansion)")
    retrograde: bool = Field(..., description="Whether planet is retrograde")


class VarshaLagna(BaseModel):
    """Annual Ascendant."""
    longitude: float = Field(..., description="Ascendant longitude")
    sign: str = Field(..., description="Ascendant sign")
    sign_num: int = Field(..., description="Sign number (1-12)")
    degree_in_sign: float = Field(..., description="Degree within sign")


class Muntha(BaseModel):
    """Muntha (progressed point)."""
    sign_num: int = Field(..., description="Sign number where Muntha is located")
    sign: str = Field(..., description="Sign name")
    age: int = Field(..., description="Age in completed years")
    description: str = Field(..., description="Muntha description")


class HouseData(BaseModel):
    """House data in Varshaphal chart."""
    sign_num: int = Field(..., description="Sign number occupying this house")
    sign: str = Field(..., description="Sign name")
    start_degree: float = Field(..., description="Start degree of house")
    end_degree: float = Field(..., description="End degree of house")


class VarshapalYoga(BaseModel):
    """Varshaphal Yoga details."""
    name: str = Field(..., description="Yoga name")
    type: str = Field(..., description="Type: Auspicious, Challenging, Mixed")
    strength: str = Field(..., description="Strength: Strong, Moderate, Weak")
    description: str = Field(..., description="Yoga description")
    planets_involved: List[str] = Field(..., description="Planets forming the yoga")
    effects: str = Field(..., description="Expected effects")


class DashaPeriod(BaseModel):
    """Patyayini Dasha period."""
    planet: str = Field(..., description="Ruling planet")
    start_date: datetime = Field(..., description="Period start date")
    end_date: datetime = Field(..., description="Period end date")
    duration_months: float = Field(..., description="Duration in months")
    effects: str = Field(..., description="Expected effects during this period")


class Saham(BaseModel):
    """Saham (sensitive point) details."""
    longitude: float = Field(..., description="Saham longitude in degrees")
    sign: str = Field(..., description="Sign where Saham is located")
    meaning: str = Field(..., description="What this Saham represents")
    importance: str = Field(..., description="Importance level: Very High, High, Medium")


class MonthlyPrediction(BaseModel):
    """Monthly prediction within the year."""
    period: str = Field(..., description="Period (e.g., 'January - February 2025')")
    ruling_planet: str = Field(..., description="Planet ruling this period")
    theme: str = Field(..., description="Main theme of the month")
    focus_areas: List[str] = Field(..., description="Areas to focus on")
    advice: str = Field(..., description="Advice for the month")


class BestPeriod(BaseModel):
    """Best period in the year."""
    period: str = Field(..., description="Period range")
    reason: str = Field(..., description="Why this is favorable")
    utilize_for: str = Field(..., description="What to utilize this period for")


class WorstPeriod(BaseModel):
    """Challenging period in the year."""
    period: str = Field(..., description="Period range")
    reason: str = Field(..., description="Why this is challenging")
    precautions: str = Field(..., description="Precautions to take")


class AnnualRemedy(BaseModel):
    """Remedy recommendation for the year."""
    category: str = Field(..., description="Remedy category")
    remedy: str = Field(..., description="Specific remedy")
    frequency: str = Field(..., description="How often to perform")


class ImportantSaham(BaseModel):
    """Summary of important Saham."""
    name: str = Field(..., description="Saham name")
    position: str = Field(..., description="Position in chart")
    meaning: str = Field(..., description="What it represents")


class AnnualInterpretation(BaseModel):
    """Comprehensive annual interpretation."""
    overall_quality: str = Field(..., description="Overall year quality: Excellent, Mixed, Challenging")
    year_summary: str = Field(..., description="Summary of the year ahead")
    monthly_predictions: List[MonthlyPrediction] = Field(..., description="Month-by-month predictions")
    best_periods: List[BestPeriod] = Field(..., description="Best periods to utilize")
    worst_periods: List[WorstPeriod] = Field(..., description="Periods requiring caution")
    key_opportunities: List[str] = Field(..., description="Key opportunities")
    key_challenges: List[str] = Field(..., description="Key challenges")
    recommended_remedies: List[AnnualRemedy] = Field(..., description="Recommended remedies")
    important_sahams: List[ImportantSaham] = Field(..., description="Important sensitive points")


class SolarReturnChart(BaseModel):
    """Solar Return Chart data."""
    solar_return_time: datetime = Field(..., description="Exact moment of solar return")
    target_year: int = Field(..., description="Year for which calculated")
    varsha_lagna: VarshaLagna = Field(..., description="Annual Ascendant")
    muntha: Muntha = Field(..., description="Muntha (progressed point)")
    planets: Dict[str, PlanetPosition] = Field(..., description="Planetary positions")
    houses: Dict[int, HouseData] = Field(..., description="House cusps (1-12)")
    yogas: List[VarshapalYoga] = Field(..., description="Varshaphal Yogas detected")
    natal_sun_longitude: float = Field(..., description="Natal Sun position")


class VarshapalResponse(BaseModel):
    """Complete Varshaphal response."""
    varshaphal_id: UUID = Field(..., description="Unique ID for this Varshaphal")
    profile_id: UUID = Field(..., description="Profile ID")
    target_year: int = Field(..., description="Year for which calculated")
    generated_at: datetime = Field(..., description="When this was generated")
    expires_at: datetime = Field(..., description="Cache expiration time")

    solar_return_chart: SolarReturnChart = Field(..., description="Solar return chart details")
    patyayini_dasha: List[DashaPeriod] = Field(..., description="Annual dasha periods")
    sahams: Dict[str, Saham] = Field(..., description="Sensitive points (Sahams)")
    annual_interpretation: AnnualInterpretation = Field(..., description="Comprehensive interpretation")

    is_cached: bool = Field(..., description="Whether this was from cache")

    class Config:
        json_schema_extra = {
            "example": {
                "varshaphal_id": "660e8400-e29b-41d4-a716-446655440000",
                "profile_id": "550e8400-e29b-41d4-a716-446655440000",
                "target_year": 2025,
                "generated_at": "2025-01-15T10:30:00Z",
                "expires_at": "2025-01-15T11:30:00Z",
                "solar_return_chart": {
                    "solar_return_time": "2025-03-21T14:23:45Z",
                    "target_year": 2025,
                    "varsha_lagna": {
                        "longitude": 45.5,
                        "sign": "Taurus",
                        "sign_num": 2,
                        "degree_in_sign": 15.5
                    },
                    "muntha": {
                        "sign_num": 3,
                        "sign": "Gemini",
                        "age": 30,
                        "description": "Muntha is in Gemini for age 30"
                    },
                    "planets": {},
                    "houses": {},
                    "yogas": [],
                    "natal_sun_longitude": 0.5
                },
                "patyayini_dasha": [],
                "sahams": {},
                "annual_interpretation": {
                    "overall_quality": "Excellent",
                    "year_summary": "This promises to be an excellent year...",
                    "monthly_predictions": [],
                    "best_periods": [],
                    "worst_periods": [],
                    "key_opportunities": [],
                    "key_challenges": [],
                    "recommended_remedies": [],
                    "important_sahams": []
                },
                "is_cached": False
            }
        }


class VarshapalListItem(BaseModel):
    """Summary item in Varshaphal list."""
    varshaphal_id: UUID = Field(..., description="Varshaphal ID")
    profile_id: UUID = Field(..., description="Profile ID")
    profile_name: str = Field(..., description="Profile name")
    target_year: int = Field(..., description="Year")
    generated_at: datetime = Field(..., description="When generated")
    expires_at: datetime = Field(..., description="Cache expiration")
    is_expired: bool = Field(..., description="Whether cache is expired")
    overall_quality: str = Field(..., description="Year quality")
    yogas_count: int = Field(..., description="Number of yogas detected")


class VarshapalListResponse(BaseModel):
    """List of Varshaphal calculations."""
    varshaphals: List[VarshapalListItem] = Field(..., description="List of Varshaphal summaries")
    total: int = Field(..., description="Total count")
    limit: int = Field(..., description="Limit used")
    offset: int = Field(..., description="Offset used")

    class Config:
        json_schema_extra = {
            "example": {
                "varshaphals": [
                    {
                        "varshaphal_id": "660e8400-e29b-41d4-a716-446655440000",
                        "profile_id": "550e8400-e29b-41d4-a716-446655440000",
                        "profile_name": "John Doe",
                        "target_year": 2025,
                        "generated_at": "2025-01-15T10:30:00Z",
                        "expires_at": "2025-01-15T11:30:00Z",
                        "is_expired": False,
                        "overall_quality": "Excellent",
                        "yogas_count": 5
                    }
                ],
                "total": 1,
                "limit": 10,
                "offset": 0
            }
        }


class VarshapalErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Profile not found",
                "detail": "No profile exists with the given ID"
            }
        }
