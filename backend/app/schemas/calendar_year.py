"""
Pydantic schemas for Calendar Year Predictions API.

Calendar Year Predictions provide transit-based annual forecasts
for calendar years (Jan 1 - Dec 31), separate from Varshaphal.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class CalendarYearRequest(BaseModel):
    """Request schema for generating calendar year predictions."""

    profile_id: str = Field(
        ...,
        description="UUID of the birth profile to generate predictions for"
    )
    target_year: int = Field(
        ...,
        ge=1900,
        le=2100,
        description="Calendar year to generate predictions for (e.g., 2026)"
    )


class MonthlyPrediction(BaseModel):
    """Schema for monthly prediction details."""

    month: str = Field(..., description="Month name (January - December)")
    month_number: int = Field(..., ge=1, le=12, description="Month number (1-12)")
    quality: str = Field(
        ...,
        description="Quality rating: Excellent, Very Good, Moderate, Challenging, Difficult"
    )
    sun_sign: str = Field(..., description="Sun's zodiac sign during this month")
    jupiter_house: int = Field(..., ge=1, le=12, description="Jupiter's house position from Moon")
    saturn_house: int = Field(..., ge=1, le=12, description="Saturn's house position from Moon")
    key_themes: List[str] = Field(..., description="Major themes for the month")
    focus_areas: List[str] = Field(..., description="Areas to focus on")
    advice: str = Field(..., description="Specific advice for the month")
    important_dates: Optional[Dict[str, str]] = Field(
        None,
        description="Important dates (Full Moon, New Moon, etc.)"
    )


class MajorTransit(BaseModel):
    """Schema for major planetary transit events."""

    planet: str = Field(..., description="Planet name (Jupiter, Saturn, Rahu, Ketu)")
    event: str = Field(..., description="Transit event description")
    date: str = Field(..., description="Date of transit (YYYY-MM-DD)")
    from_sign: Optional[str] = Field(None, description="Sign transiting from")
    to_sign: str = Field(..., description="Sign transiting to")
    house: int = Field(..., ge=1, le=12, description="House position from Moon")
    effect: str = Field(..., description="Effect of this transit")
    significance: str = Field(
        ...,
        description="Significance level: High, Medium, Low"
    )


class Eclipse(BaseModel):
    """Schema for eclipse predictions."""

    type: str = Field(..., description="Eclipse type: Solar, Lunar")
    date: str = Field(..., description="Date of eclipse (YYYY-MM-DD)")
    time: str = Field(..., description="Time of eclipse (HH:MM UTC)")
    eclipse_type: str = Field(
        ...,
        description="Specific type: Total, Partial, Annular, Penumbral"
    )
    nakshatra: Optional[str] = Field(None, description="Nakshatra where eclipse occurs")
    house: Optional[int] = Field(None, ge=1, le=12, description="House position from Moon")
    effect: str = Field(..., description="Effect of this eclipse")
    recommendations: List[str] = Field(..., description="Recommendations during eclipse")


class BestWorstPeriod(BaseModel):
    """Schema for best/worst month periods."""

    month: str = Field(..., description="Month name")
    quality: str = Field(..., description="Quality rating")
    reason: str = Field(..., description="Reason for this rating")
    advice: str = Field(..., description="How to utilize or navigate this period")


class YearOverview(BaseModel):
    """Schema for overall year summary."""

    overall_quality: str = Field(
        ...,
        description="Overall year quality: Excellent, Very Good, Moderate, Challenging, Difficult"
    )
    key_opportunities: List[str] = Field(..., description="Main opportunities for the year")
    main_challenges: List[str] = Field(..., description="Primary challenges to address")
    recommended_remedies: List[str] = Field(..., description="General remedies for the year")
    important_themes: List[str] = Field(..., description="Overarching themes")


class CalendarYearResponse(BaseModel):
    """Response schema for calendar year predictions."""

    id: Optional[str] = Field(None, description="Database ID if saved")
    profile_id: str = Field(..., description="Profile UUID")
    target_year: int = Field(..., description="Calendar year for predictions")
    year_start: str = Field(..., description="Year start date (YYYY-MM-DD)")
    year_end: str = Field(..., description="Year end date (YYYY-MM-DD)")

    # Monthly breakdown
    monthly_predictions: List[MonthlyPrediction] = Field(
        ...,
        description="12 monthly predictions (January - December)"
    )

    # Major events
    major_transits: List[MajorTransit] = Field(
        ...,
        description="Significant planetary transits during the year"
    )
    eclipses: List[Eclipse] = Field(..., description="Solar and lunar eclipses")

    # Best/worst periods
    best_months: List[BestWorstPeriod] = Field(
        ...,
        description="Top 3 most favorable months"
    )
    worst_months: List[BestWorstPeriod] = Field(
        ...,
        description="2 most challenging months"
    )

    # Year overview
    year_overview: YearOverview = Field(..., description="Overall year summary")

    # Metadata
    generated_at: Optional[datetime] = Field(
        None,
        description="Timestamp when predictions were generated"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "profile_id": "123e4567-e89b-12d3-a456-426614174000",
                "target_year": 2026,
                "year_start": "2026-01-01",
                "year_end": "2026-12-31",
                "monthly_predictions": [
                    {
                        "month": "January",
                        "month_number": 1,
                        "quality": "Very Good",
                        "sun_sign": "Capricorn",
                        "jupiter_house": 5,
                        "saturn_house": 11,
                        "key_themes": ["New beginnings", "Goal setting"],
                        "focus_areas": ["Career planning", "Health routines"],
                        "advice": "Start the year with clear intentions"
                    }
                ],
                "major_transits": [
                    {
                        "planet": "Jupiter",
                        "event": "Jupiter enters Taurus",
                        "date": "2026-05-15",
                        "from_sign": "Aries",
                        "to_sign": "Taurus",
                        "house": 6,
                        "effect": "Expansion in health and service areas",
                        "significance": "High"
                    }
                ],
                "eclipses": [
                    {
                        "type": "Solar",
                        "date": "2026-02-17",
                        "time": "12:15 UTC",
                        "eclipse_type": "Annular",
                        "nakshatra": "Purva Phalguni",
                        "house": 3,
                        "effect": "Changes in communication and siblings",
                        "recommendations": ["Avoid major decisions", "Donate to charity"]
                    }
                ],
                "best_months": [
                    {
                        "month": "March",
                        "quality": "Excellent",
                        "reason": "Jupiter and Venus well-placed",
                        "advice": "Ideal for major initiatives and investments"
                    }
                ],
                "worst_months": [
                    {
                        "month": "August",
                        "quality": "Challenging",
                        "reason": "Saturn retrograde in difficult house",
                        "advice": "Focus on completing existing tasks, avoid new ventures"
                    }
                ],
                "year_overview": {
                    "overall_quality": "Very Good",
                    "key_opportunities": ["Career advancement", "Spiritual growth"],
                    "main_challenges": ["Health maintenance", "Financial planning"],
                    "recommended_remedies": ["Hanuman Chalisa", "Tuesday fasting"],
                    "important_themes": ["Transformation", "Leadership"]
                }
            }
        }


class CalendarYearListItem(BaseModel):
    """Schema for listing calendar year predictions (summary)."""

    id: str = Field(..., description="Database ID")
    profile_id: str = Field(..., description="Profile UUID")
    profile_name: Optional[str] = Field(None, description="Profile name")
    target_year: int = Field(..., description="Calendar year")
    overall_quality: str = Field(..., description="Overall year quality")
    generated_at: datetime = Field(..., description="Generation timestamp")

    class Config:
        from_attributes = True


class CalendarYearDeleteResponse(BaseModel):
    """Response schema for deleting calendar year predictions."""

    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Status message")
    deleted_id: Optional[str] = Field(None, description="ID of deleted prediction")
