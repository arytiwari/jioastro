"""
Pydantic schemas for Phase 4 Enhancement APIs:
- Remedy Generation
- Birth Time Rectification
- Transit Calculations
- Shadbala (Planetary Strength) Calculations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from enum import Enum


# ==================== REMEDY SCHEMAS ====================

class RemedyDomain(str, Enum):
    """Life domains for targeted remedies"""
    CAREER = "career"
    WEALTH = "wealth"
    HEALTH = "health"
    RELATIONSHIPS = "relationships"
    EDUCATION = "education"
    SPIRITUALITY = "spirituality"
    GENERAL = "general"


class RemedyGenerateRequest(BaseModel):
    """Request to generate remedies"""
    profile_id: str = Field(..., description="Profile ID to get chart data")
    domain: Optional[RemedyDomain] = Field(None, description="Specific life domain to focus on")
    specific_issue: Optional[str] = Field(None, description="Specific problem to address", max_length=500)
    max_remedies: int = Field(5, ge=1, le=10, description="Maximum number of remedies to return")
    include_practical: bool = Field(True, description="Include modern practical alternatives")

    class Config:
        json_schema_extra = {
            "example": {
                "profile_id": "123e4567-e89b-12d3-a456-426614174000",
                "domain": "career",
                "specific_issue": "Struggling with job stability",
                "max_remedies": 5,
                "include_practical": True
            }
        }


class RemedyItem(BaseModel):
    """Individual remedy recommendation"""
    type: str = Field(..., description="Type of remedy (mantra, gemstone, charity, etc.)")
    title: str = Field(..., description="Remedy title")
    description: str = Field(..., description="Detailed description")
    instructions: str = Field(..., description="How to perform the remedy")
    frequency: str = Field(..., description="How often to perform")
    duration: str = Field(..., description="How long to continue")
    difficulty: str = Field(..., description="Difficulty level (easy, medium, hard)")
    cost: str = Field(..., description="Cost estimate (free, low, medium, high)")
    planet: str = Field(..., description="Planet being strengthened")
    practical_alternative: Optional[str] = Field(None, description="Modern practical alternative")
    benefits: List[str] = Field(default_factory=list, description="Expected benefits")


class RemedyGenerateResponse(BaseModel):
    """Response with generated remedies"""
    remedies: List[RemedyItem] = Field(..., description="List of recommended remedies")
    analysis: Dict[str, Any] = Field(..., description="Chart analysis summary")
    priority_planets: List[str] = Field(..., description="Planets requiring attention")
    current_dasha: Optional[str] = Field(None, description="Current dasha period")
    notes: str = Field(..., description="General notes and guidance")


# ==================== RECTIFICATION SCHEMAS ====================

class EventType(str, Enum):
    """Types of life events for rectification"""
    MARRIAGE = "marriage"
    DIVORCE = "divorce"
    JOB_START = "job_start"
    JOB_END = "job_end"
    PROMOTION = "promotion"
    RELOCATION = "relocation"
    CHILDBIRTH = "childbirth"
    PARENT_DEATH = "parent_death"
    PROPERTY_PURCHASE = "property_purchase"
    BUSINESS_START = "business_start"
    EDUCATION_START = "education_start"
    MAJOR_ACCIDENT = "major_accident"
    SURGERY = "surgery"


class EventAnchor(BaseModel):
    """Life event for rectification"""
    event_type: EventType = Field(..., description="Type of event")
    event_date: date = Field(..., description="Date when event occurred")
    description: Optional[str] = Field(None, description="Additional event details", max_length=500)
    significance: int = Field(5, ge=1, le=10, description="How significant was this event (1-10)")

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "marriage",
                "event_date": "2015-06-15",
                "description": "Got married in a grand ceremony",
                "significance": 9
            }
        }


class RectificationRequest(BaseModel):
    """Request for birth time rectification"""
    name: str = Field(..., description="Person's name", min_length=1, max_length=100)
    birth_date: date = Field(..., description="Known birth date")
    approximate_time: time = Field(..., description="Approximate birth time")
    time_window_minutes: int = Field(..., ge=5, le=120, description="Uncertainty window in minutes (e.g., ±30)")
    birth_city: str = Field(..., description="Birth city", max_length=100)
    birth_lat: float = Field(..., ge=-90, le=90, description="Birth latitude")
    birth_lon: float = Field(..., ge=-180, le=180, description="Birth longitude")
    birth_timezone: str = Field(..., description="Birth timezone (e.g., 'Asia/Kolkata')")
    event_anchors: List[EventAnchor] = Field(..., min_length=1, description="Major life events")

    @validator('event_anchors')
    def validate_event_anchors(cls, v):
        if len(v) < 1:
            raise ValueError("At least 1 event anchor is required for rectification")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "birth_date": "1990-05-15",
                "approximate_time": "14:30:00",
                "time_window_minutes": 30,
                "birth_city": "New York",
                "birth_lat": 40.7128,
                "birth_lon": -74.0060,
                "birth_timezone": "America/New_York",
                "event_anchors": [
                    {
                        "event_type": "marriage",
                        "event_date": "2015-06-15",
                        "significance": 9
                    }
                ]
            }
        }


class RectificationCandidate(BaseModel):
    """A candidate birth time with score"""
    birth_time: str = Field(..., description="Candidate birth time (HH:MM:SS)")
    confidence_score: float = Field(..., ge=0, le=100, description="Confidence percentage (0-100)")
    ascendant: str = Field(..., description="Ascendant sign for this time")
    moon_sign: str = Field(..., description="Moon sign for this time")
    event_matches: List[Dict[str, Any]] = Field(default_factory=list, description="How well events matched")
    reasoning: str = Field(..., description="Why this time is suggested")


class RectificationResponse(BaseModel):
    """Response with rectified birth times"""
    top_candidates: List[RectificationCandidate] = Field(..., description="Top 3 candidate times")
    analysis_summary: str = Field(..., description="Summary of rectification analysis")
    events_analyzed: int = Field(..., description="Number of events used")
    candidates_tested: int = Field(..., description="Total candidate times tested")
    recommendation: str = Field(..., description="Overall recommendation")


# ==================== TRANSIT SCHEMAS ====================

class TransitCalculateRequest(BaseModel):
    """Request for transit calculations"""
    profile_id: str = Field(..., description="Profile ID to get birth chart")
    transit_date: Optional[datetime] = Field(None, description="Date/time for transits (default: now)")
    include_timeline: bool = Field(False, description="Include 30-day timeline")
    focus_planets: Optional[List[str]] = Field(None, description="Focus on specific planets")

    class Config:
        json_schema_extra = {
            "example": {
                "profile_id": "123e4567-e89b-12d3-a456-426614174000",
                "transit_date": None,
                "include_timeline": True,
                "focus_planets": ["Jupiter", "Saturn"]
            }
        }


class TransitPlanet(BaseModel):
    """Transit planetary position"""
    planet: str = Field(..., description="Planet name")
    sign: str = Field(..., description="Current zodiac sign")
    degree: float = Field(..., description="Degree within sign")
    house: int = Field(..., description="House in natal chart")
    retrograde: bool = Field(..., description="Is retrograde")
    interpretation: str = Field(..., description="What this transit means")


class TransitAspect(BaseModel):
    """Transit aspect to natal planet"""
    transiting_planet: str = Field(..., description="Transiting planet")
    natal_planet: str = Field(..., description="Natal planet being aspected")
    aspect_type: str = Field(..., description="Type of aspect (conjunction, square, etc.)")
    orb: float = Field(..., description="Orb in degrees")
    strength: str = Field(..., description="Aspect strength (very_strong, strong, moderate, weak)")
    interpretation: str = Field(..., description="What this aspect means")
    is_applying: bool = Field(..., description="Is the aspect getting stronger")


class SignChange(BaseModel):
    """Upcoming planetary sign change"""
    planet: str = Field(..., description="Planet name")
    current_sign: str = Field(..., description="Current sign")
    next_sign: str = Field(..., description="Next sign")
    change_date: datetime = Field(..., description="When the change occurs")
    days_until: float = Field(..., description="Days until change")


class TransitResponse(BaseModel):
    """Response with transit data"""
    transit_date: datetime = Field(..., description="Date/time of transits")
    current_positions: List[TransitPlanet] = Field(..., description="Current planetary positions")
    significant_aspects: List[TransitAspect] = Field(..., description="Important aspects")
    upcoming_sign_changes: List[SignChange] = Field(default_factory=list, description="Sign changes in next 30 days")
    timeline_events: Optional[List[Dict[str, Any]]] = Field(None, description="30-day timeline (if requested)")
    summary: str = Field(..., description="Overall transit summary")
    focus_areas: List[str] = Field(default_factory=list, description="Key life areas to focus on")


# ==================== SHADBALA SCHEMAS ====================

class ShadbalaCalculateRequest(BaseModel):
    """Request for Shadbala calculations"""
    profile_id: str = Field(..., description="Profile ID to calculate strength")
    include_breakdown: bool = Field(True, description="Include detailed component breakdown")
    comparison: bool = Field(True, description="Compare with required minimums")

    class Config:
        json_schema_extra = {
            "example": {
                "profile_id": "123e4567-e89b-12d3-a456-426614174000",
                "include_breakdown": True,
                "comparison": True
            }
        }


class BalaComponent(BaseModel):
    """Individual bala (strength) component"""
    name: str = Field(..., description="Component name (sthana_bala, dig_bala, etc.)")
    value: float = Field(..., description="Strength value in shashtiamsas")
    percentage: float = Field(..., description="Percentage of maximum")
    description: str = Field(..., description="What this component measures")


class PlanetaryStrength(BaseModel):
    """Shadbala strength for one planet"""
    planet: str = Field(..., description="Planet name")
    total_strength: float = Field(..., description="Total strength in shashtiamsas")
    required_minimum: float = Field(..., description="Required minimum strength")
    percentage_of_required: float = Field(..., description="Percentage of required strength")
    rating: str = Field(..., description="Strength rating (exceptional, very_strong, strong, etc.)")
    components: Optional[List[BalaComponent]] = Field(None, description="Detailed breakdown")
    is_above_minimum: bool = Field(..., description="Is above required minimum")
    interpretation: str = Field(..., description="What this strength level means")


class ShadbalaResponse(BaseModel):
    """Response with Shadbala calculations"""
    planetary_strengths: List[PlanetaryStrength] = Field(..., description="Strength for each planet")
    strongest_planet: str = Field(..., description="Strongest planet")
    weakest_planet: str = Field(..., description="Weakest planet")
    average_strength: float = Field(..., description="Average strength percentage")
    planets_above_minimum: int = Field(..., description="How many planets meet minimum")
    overall_chart_strength: str = Field(..., description="Overall chart strength rating")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations based on strengths")
    calculation_date: datetime = Field(..., description="When strength was calculated")


# ==================== YOGA DETECTION SCHEMAS ====================

class YogaCalculateRequest(BaseModel):
    """Request for yoga detection"""
    profile_id: str = Field(..., description="Profile ID to analyze yogas")
    include_all: bool = Field(True, description="Include all detected yogas or only strong ones")

    class Config:
        json_schema_extra = {
            "example": {
                "profile_id": "123e4567-e89b-12d3-a456-426614174000",
                "include_all": True
            }
        }


class YogaItem(BaseModel):
    """Individual yoga detected"""
    name: str = Field(..., description="Yoga name")
    description: str = Field(..., description="What this yoga indicates")
    strength: str = Field(..., description="Strength rating (Very Strong, Strong, Medium, Weak)")
    category: str = Field(..., description="Category (Wealth, Fame, Power, Learning, etc.)")


class YogaResponse(BaseModel):
    """Response with detected yogas"""
    yogas: List[YogaItem] = Field(..., description="All detected yogas")
    total_yogas: int = Field(..., description="Total number of yogas detected")
    categories: Dict[str, int] = Field(default_factory=dict, description="Count by category")
    strongest_yogas: List[str] = Field(default_factory=list, description="Names of very strong yogas")
    summary: str = Field(..., description="Overall yoga summary")
    chart_quality: str = Field(..., description="Overall chart quality based on yogas")
