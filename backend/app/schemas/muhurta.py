"""
Pydantic schemas for Muhurta (Electional Astrology) API.
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from uuid import UUID


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class PanchangRequest(BaseModel):
    """Request to get Panchang for a specific date/time"""
    datetime: datetime
    latitude: float
    longitude: float


class HoraRequest(BaseModel):
    """Request to get Hora for a specific time"""
    datetime: datetime
    latitude: float
    longitude: float


class DailyHoraTableRequest(BaseModel):
    """Request to get complete hora table for a day"""
    date: date
    latitude: float
    longitude: float


class MuhurtaFinderRequest(BaseModel):
    """Request to find auspicious times for an activity"""
    activity_type: str
    start_date: date
    end_date: date
    latitude: float
    longitude: float
    max_results: int = 10


class BestTimeTodayRequest(BaseModel):
    """Request to find best time for activity today"""
    activity_type: str
    latitude: float
    longitude: float


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class TithiResponse(BaseModel):
    """Tithi (Lunar Day) details"""
    tithi_number: int
    tithi_name: str
    paksha: str
    paksha_tithi: int
    progress_percent: float
    ends_at: str
    is_auspicious: bool
    description: str


class NakshatraResponse(BaseModel):
    """Nakshatra (Lunar Mansion) details"""
    nakshatra_number: int
    nakshatra_name: str
    pada: int
    progress_percent: float
    ends_at: str
    ruler: str
    deity: str
    nature: str
    is_auspicious: bool
    favorable_for: List[str]


class YogaResponse(BaseModel):
    """Yoga details"""
    yoga_number: int
    yoga_name: str
    progress_percent: float
    ends_at: str
    quality: str
    is_auspicious: bool
    description: str


class KaranaResponse(BaseModel):
    """Karana (Half Tithi) details"""
    karana_number: int
    karana_name: str
    karana_type: str
    progress_percent: float
    ends_at: str
    is_auspicious: bool
    nature: str


class VaraResponse(BaseModel):
    """Vara (Weekday) details"""
    vara_number: int
    vara_name: str
    ruling_planet: str
    quality: str
    favorable_for: List[str]
    avoid: List[str]


class PanchangResponse(BaseModel):
    """Complete Panchang response"""
    date: str
    time: str
    location: Dict[str, float]
    sunrise: Optional[str]
    sunset: Optional[str]
    tithi: TithiResponse
    nakshatra: NakshatraResponse
    yoga: YogaResponse
    karana: KaranaResponse
    vara: VaraResponse
    overall_quality: str
    auspicious_score: int
    summary: str


class HoraResponse(BaseModel):
    """Hora (Planetary Hour) response"""
    current_time: str
    is_day: bool
    hora_number: int
    ruling_planet: str
    hora_starts: str
    hora_ends: str
    progress_percent: float
    favorable_for: List[str]
    unfavorable_for: List[str]
    strength: str
    next_favorable: Dict[str, Any]


class HoraTableItem(BaseModel):
    """Single hora in daily table"""
    hora_number: int
    period: str
    ruling_planet: str
    starts_at: str
    ends_at: str
    favorable_for: List[str]
    strength: str


class DailyHoraTableResponse(BaseModel):
    """Complete daily hora table"""
    date: str
    horas: List[HoraTableItem]
    total_horas: int


class MuhurtaResult(BaseModel):
    """Single muhurta result"""
    datetime: str
    date: str
    time_range: str
    score: float
    quality: str
    tithi: str
    nakshatra: str
    vara: str
    hora_ruler: str
    yoga: str
    karana: str
    reasons: List[str]
    precautions: List[str]


class MuhurtaFinderResponse(BaseModel):
    """Muhurta finder response"""
    activity_type: str
    search_period: Dict[str, str]
    location: Dict[str, float]
    results: List[MuhurtaResult]
    total_found: int
    message: Optional[str]


class BestTimeTodayResponse(BaseModel):
    """Best time today response"""
    activity_type: str
    best_time: Optional[MuhurtaResult]
    alternatives: List[MuhurtaResult]
    total_found: int
    message: Optional[str]


# ============================================================================
# SAVED MUHURTA SCHEMAS
# ============================================================================

class SaveMuhurtaRequest(BaseModel):
    """Request to save a muhurta"""
    activity_type: str
    selected_datetime: datetime
    muhurta_details: Dict[str, Any]
    notes: Optional[str] = None


class SavedMuhurtaResponse(BaseModel):
    """Saved muhurta response"""
    id: UUID
    user_id: UUID
    activity_type: str
    selected_datetime: datetime
    muhurta_details: Dict[str, Any]
    notes: Optional[str]
    created_at: datetime


class MuhurtaListResponse(BaseModel):
    """List of saved muhurtas"""
    muhurtas: List[SavedMuhurtaResponse]
    total: int
    limit: int
    offset: int


# ============================================================================
# DECISION COPILOT SCHEMAS (AI-POWERED)
# ============================================================================

class DecisionCopilotRequest(BaseModel):
    """Request for AI-powered decision copilot"""
    activity_type: str = Field(..., description="Type of activity: marriage, business, travel, property, surgery")
    start_date: date
    end_date: date
    latitude: float
    longitude: float
    chart_id: Optional[str] = Field(None, description="User's birth chart ID for personalization")
    max_results: int = Field(5, ge=3, le=10, description="Number of options to compare (3-10)")


class MuhurtaOptionAnalysis(BaseModel):
    """AI analysis of a single muhurta option"""
    # Original muhurta data
    datetime: str
    date: str
    time_range: str
    score: float
    quality: str
    tithi: str
    nakshatra: str
    vara: str
    hora_ruler: str
    yoga: str
    karana: str

    # AI-generated analysis
    ai_rating: int = Field(..., ge=1, le=10, description="AI rating 1-10")
    best_time_within_day: str = Field(default="Full day", description="Specific time period within the day")
    pros: List[str] = Field(default_factory=list, description="Positive factors")
    cons: List[str] = Field(default_factory=list, description="Challenges and cautions")
    personalization_note: str = Field(..., description="How this time relates to user's chart")


class BestTimeRecommendation(BaseModel):
    """AI recommendation for best time"""
    option_number: int = Field(..., description="Which option number is recommended (1-indexed)")
    datetime: Optional[str]
    rating: int = Field(..., ge=1, le=10)
    specific_time: str = Field(default="", description="Specific time period within the day")
    reasoning: str = Field(..., description="Why this is the best choice (2-3 sentences)")
    actionable_advice: str = Field(..., description="Specific guidance for this activity")

    # Include all fields from the selected option
    date: Optional[str] = None
    time_range: Optional[str] = None
    score: Optional[float] = None
    quality: Optional[str] = None
    tithi: Optional[str] = None
    nakshatra: Optional[str] = None
    vara: Optional[str] = None
    hora_ruler: Optional[str] = None
    best_time_within_day: Optional[str] = None
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)


class AIGuidance(BaseModel):
    """AI-powered decision guidance"""
    comparison: List[MuhurtaOptionAnalysis] = Field(..., description="All options with AI analysis")
    best_time: BestTimeRecommendation = Field(..., description="Recommended best time")
    total_options: int
    has_personalization: bool = Field(..., description="Whether personal chart was used")


class DecisionCopilotResponse(BaseModel):
    """Complete decision copilot response"""
    activity_type: str
    search_period: Dict[str, str]
    location: Dict[str, float]
    traditional_results: List[MuhurtaResult] = Field(..., description="Traditional Muhurta results")
    ai_guidance: Optional[AIGuidance] = Field(None, description="AI-powered comparison and recommendation")
    has_personalization: bool
    total_options: int
    message: Optional[str] = Field(None, description="Message if no results found")
