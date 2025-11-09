"""
Pydantic schemas for Life Threads feature
Handles life event tracking mapped to Dasha periods
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class EventType(str, Enum):
    """Life event categories"""
    CAREER = "career"
    EDUCATION = "education"
    RELATIONSHIP = "relationship"
    MARRIAGE = "marriage"
    CHILDBIRTH = "childbirth"
    HEALTH = "health"
    RELOCATION = "relocation"
    FINANCIAL = "financial"
    SPIRITUAL = "spiritual"
    ACHIEVEMENT = "achievement"
    LOSS = "loss"
    TRAVEL = "travel"
    PROPERTY = "property"
    FAMILY = "family"
    OTHER = "other"


class EventImpact(str, Enum):
    """Impact level of event"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class PrivacyLevel(str, Enum):
    """Privacy levels for events"""
    PRIVATE = "private"
    SHARED = "shared"
    PUBLIC = "public"


# Request Schemas

class CreateLifeEventRequest(BaseModel):
    """Create a new life event"""
    profile_id: str = Field(..., description="Birth profile ID to link event to")
    event_type: EventType
    event_name: str = Field(..., min_length=1, max_length=200)
    event_date: date
    event_description: Optional[str] = Field(None, max_length=2000)
    event_impact: Optional[EventImpact] = None
    tags: Optional[List[str]] = Field(default_factory=list, max_items=10)
    is_milestone: bool = False
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE

    @validator('event_date')
    def validate_event_date(cls, v):
        """Ensure event date is reasonable"""
        if v.year < 1900:
            raise ValueError("Event date must be after 1900")
        if v > date.today():
            # Allow future events up to 10 years
            max_future = date.today().replace(year=date.today().year + 10)
            if v > max_future:
                raise ValueError("Event date cannot be more than 10 years in the future")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "profile_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "career",
                "event_name": "Started new job at Tech Company",
                "event_date": "2023-06-15",
                "event_description": "Joined as Senior Software Engineer",
                "event_impact": "positive",
                "tags": ["career", "technology", "growth"],
                "is_milestone": True,
                "privacy_level": "private"
            }
        }


class UpdateLifeEventRequest(BaseModel):
    """Update an existing life event"""
    event_type: Optional[EventType] = None
    event_name: Optional[str] = Field(None, min_length=1, max_length=200)
    event_date: Optional[date] = None
    event_description: Optional[str] = Field(None, max_length=2000)
    event_impact: Optional[EventImpact] = None
    tags: Optional[List[str]] = Field(None, max_items=10)
    is_milestone: Optional[bool] = None
    privacy_level: Optional[PrivacyLevel] = None


class GetTimelineRequest(BaseModel):
    """Get timeline for a profile"""
    profile_id: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    event_types: Optional[List[EventType]] = None
    include_milestones_only: bool = False


# Response Schemas

class DashaPeriod(BaseModel):
    """Dasha period information"""
    mahadasha: str = Field(..., description="Major period planet")
    mahadasha_start: date
    mahadasha_end: date
    antardasha: Optional[str] = Field(None, description="Sub-period planet")
    antardasha_start: Optional[date] = None
    antardasha_end: Optional[date] = None
    pratyantardasha: Optional[str] = Field(None, description="Sub-sub-period planet")
    pratyantardasha_start: Optional[date] = None
    pratyantardasha_end: Optional[date] = None


class TransitContext(BaseModel):
    """Transit context at event time"""
    major_transits: List[Dict[str, Any]] = Field(default_factory=list)
    jupiter_sign: Optional[str] = None
    saturn_sign: Optional[str] = None
    rahu_sign: Optional[str] = None
    ketu_sign: Optional[str] = None


class LifeEvent(BaseModel):
    """Life event with astrological context"""
    id: str
    user_id: str
    profile_id: str
    event_type: EventType
    event_name: str
    event_date: date
    event_description: Optional[str] = None
    event_impact: Optional[EventImpact] = None
    dasha_period: Optional[DashaPeriod] = None
    transit_context: Optional[TransitContext] = None
    tags: List[str] = Field(default_factory=list)
    is_milestone: bool = False
    privacy_level: PrivacyLevel
    astrological_significance: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimelineEvent(BaseModel):
    """Simplified event for timeline visualization"""
    id: str
    event_name: str
    event_date: date
    event_type: EventType
    event_impact: Optional[EventImpact]
    is_milestone: bool
    dasha_lord: str  # Mahadasha planet
    tags: List[str]


class MahadashaBlock(BaseModel):
    """Mahadasha period block for timeline"""
    planet: str
    start_date: date
    end_date: date
    duration_years: float
    events_count: int = 0
    events: List[TimelineEvent] = Field(default_factory=list)


class DashaTimeline(BaseModel):
    """Complete Dasha timeline with events"""
    profile_id: str
    profile_name: str
    birth_date: date
    vimshottari_start_date: date  # Balance at birth
    mahadasha_periods: List[MahadashaBlock]
    total_events: int
    cached_at: Optional[datetime] = None


class LifeEventsListResponse(BaseModel):
    """List of life events with pagination"""
    events: List[LifeEvent]
    total_count: int
    page: int = 1
    page_size: int = 20
    has_more: bool


class TimelineResponse(BaseModel):
    """Timeline visualization data"""
    timeline: DashaTimeline
    milestones: List[TimelineEvent]
    event_type_distribution: Dict[str, int]
    events_by_dasha: Dict[str, int]


class AstrologicalSignificanceResponse(BaseModel):
    """AI-generated astrological significance"""
    event_id: str
    significance: str
    dasha_correlation: str
    transit_correlation: str
    recommendations: List[str] = Field(default_factory=list)


# Stats and Analytics

class EventStatistics(BaseModel):
    """Statistics about user's life events"""
    total_events: int
    milestones_count: int
    events_by_type: Dict[str, int]
    events_by_impact: Dict[str, int]
    events_by_dasha: Dict[str, int]
    most_active_dasha: Optional[str] = None
    most_active_year: Optional[int] = None
    average_events_per_year: float


class DashaAnalysis(BaseModel):
    """Analysis of events during specific Dasha"""
    dasha_lord: str
    start_date: date
    end_date: date
    events_count: int
    positive_events: int
    negative_events: int
    major_themes: List[str] = Field(default_factory=list)
    life_areas_affected: List[str] = Field(default_factory=list)
    overall_quality: str  # e.g., "Productive", "Challenging", "Transformative"
