"""
Pydantic schemas for Remedy Planner feature
Handles remedy tracking with habit formation and streaks
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime, time
from enum import Enum


# Enums

class RemedyType(str, Enum):
    """Types of remedies"""
    MANTRA = "mantra"
    GEMSTONE = "gemstone"
    CHARITY = "charity"
    FASTING = "fasting"
    PUJA = "puja"
    YANTRA = "yantra"
    COLOR_THERAPY = "color_therapy"
    MEDITATION = "meditation"
    RITUAL = "ritual"
    DONATION = "donation"
    PLANT = "plant"
    RUDRAKSHA = "rudraksha"
    LIFESTYLE = "lifestyle"
    DIETARY = "dietary"
    SPIRITUAL_PRACTICE = "spiritual_practice"


class RemedyFrequency(str, Enum):
    """Frequency of remedy practice"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_SPECIFIC_DAYS = "on_specific_days"
    ONE_TIME = "one_time"


class DifficultyLevel(str, Enum):
    """Difficulty level"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class AssignmentStatus(str, Enum):
    """Status of remedy assignment"""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class AssignedBy(str, Enum):
    """Who assigned the remedy"""
    AI = "ai"
    ASTROLOGER = "astrologer"
    SELF = "self"


class MoodLevel(str, Enum):
    """Mood levels"""
    POOR = "poor"
    OKAY = "okay"
    GOOD = "good"
    EXCELLENT = "excellent"


class TimeOfDay(str, Enum):
    """Time of day for tracking"""
    SUNRISE = "sunrise"
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    SUNSET = "sunset"
    NIGHT = "night"


# Request Schemas

class SearchRemediesRequest(BaseModel):
    """Search remedies catalog"""
    remedy_type: Optional[RemedyType] = None
    planet: Optional[str] = None
    dosha: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    frequency: Optional[RemedyFrequency] = None
    search_query: Optional[str] = None
    cost_estimate: Optional[str] = None  # 'free', 'low', 'medium', 'high'
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class AssignRemedyRequest(BaseModel):
    """Assign a remedy to user"""
    remedy_id: str
    profile_id: Optional[str] = None
    assigned_reason: str = Field(..., min_length=10, max_length=500)
    custom_instructions: Optional[str] = Field(None, max_length=1000)
    target_start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    custom_frequency: Optional[str] = None
    total_days_target: Optional[int] = Field(None, ge=1, le=365)
    reminder_enabled: bool = True
    reminder_time: Optional[time] = None
    reminder_days: Optional[List[str]] = None

    @validator('reminder_days')
    def validate_reminder_days(cls, v):
        if v:
            valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in v:
                if day.lower() not in valid_days:
                    raise ValueError(f"Invalid day: {day}")
        return v


class UpdateAssignmentRequest(BaseModel):
    """Update remedy assignment"""
    status: Optional[AssignmentStatus] = None
    custom_instructions: Optional[str] = None
    reminder_enabled: Optional[bool] = None
    reminder_time: Optional[time] = None
    reminder_days: Optional[List[str]] = None
    user_notes: Optional[str] = None
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5)
    user_feedback: Optional[str] = None


class TrackRemedyRequest(BaseModel):
    """Track daily remedy completion"""
    assignment_id: str
    tracking_date: date
    completed: bool
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    duration_minutes: Optional[int] = Field(None, ge=1, le=300)
    notes: Optional[str] = Field(None, max_length=500)
    mood_before: Optional[MoodLevel] = None
    mood_after: Optional[MoodLevel] = None
    location: Optional[str] = None
    time_of_day: Optional[TimeOfDay] = None

    @validator('tracking_date')
    def validate_tracking_date(cls, v):
        if v > date.today():
            raise ValueError("Cannot track future dates")
        if v < date.today().replace(year=date.today().year - 1):
            raise ValueError("Cannot track dates older than 1 year")
        return v


# Response Schemas

class RemedyCatalogItem(BaseModel):
    """Remedy from catalog"""
    id: str
    remedy_name: str
    remedy_type: RemedyType
    description: str
    detailed_instructions: Optional[str] = None
    planet: Optional[str] = None
    house: Optional[int] = None
    dosha: Optional[str] = None
    affliction_type: List[str] = Field(default_factory=list)
    frequency: RemedyFrequency
    best_time: Optional[str] = None
    duration_days: Optional[int] = None
    difficulty_level: DifficultyLevel
    benefits: List[str] = Field(default_factory=list)
    precautions: List[str] = Field(default_factory=list)
    cost_estimate: Optional[str] = None
    materials_needed: List[str] = Field(default_factory=list)
    scripture_reference: Optional[str] = None
    source_authority: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class RemedyAssignment(BaseModel):
    """Assigned remedy with progress"""
    id: str
    user_id: str
    profile_id: Optional[str] = None
    remedy: RemedyCatalogItem
    assigned_reason: str
    assigned_by: AssignedBy
    assignment_context: Optional[Dict[str, Any]] = None
    custom_instructions: Optional[str] = None
    target_start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    custom_frequency: Optional[str] = None
    status: AssignmentStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    total_days_target: Optional[int] = None
    days_completed: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_completed_date: Optional[date] = None
    user_notes: Optional[str] = None
    effectiveness_rating: Optional[int] = None
    user_feedback: Optional[str] = None
    reminder_enabled: bool = True
    reminder_time: Optional[time] = None
    reminder_days: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RemedyTracking(BaseModel):
    """Daily tracking record"""
    id: str
    assignment_id: str
    user_id: str
    tracking_date: date
    completed: bool
    completed_at: Optional[datetime] = None
    quality_rating: Optional[int] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    mood_before: Optional[MoodLevel] = None
    mood_after: Optional[MoodLevel] = None
    location: Optional[str] = None
    time_of_day: Optional[TimeOfDay] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RemedyAchievement(BaseModel):
    """Achievement/milestone"""
    id: str
    user_id: str
    assignment_id: Optional[str] = None
    achievement_type: str
    achievement_name: str
    achievement_description: Optional[str] = None
    achievement_icon: Optional[str] = None
    unlocked_at: datetime
    streak_count: Optional[int] = None

    class Config:
        from_attributes = True


class RemediesSearchResponse(BaseModel):
    """Search results from catalog"""
    remedies: List[RemedyCatalogItem]
    total_count: int
    page: int = 1
    page_size: int = 20
    has_more: bool


class AssignmentsListResponse(BaseModel):
    """List of user's assignments"""
    assignments: List[RemedyAssignment]
    total_count: int
    active_count: int
    completed_count: int


class TrackingHistoryResponse(BaseModel):
    """Tracking history for assignment"""
    assignment: RemedyAssignment
    tracking_records: List[RemedyTracking]
    total_days: int
    completion_rate: float  # Percentage
    average_quality: Optional[float] = None


class StreakInfo(BaseModel):
    """Streak information"""
    assignment_id: str
    remedy_name: str
    current_streak: int
    longest_streak: int
    last_completed_date: Optional[date] = None
    days_until_break: int = 0  # Days until streak breaks if not completed
    is_at_risk: bool = False  # True if streak will break today


class DashboardStats(BaseModel):
    """User's remedy dashboard statistics"""
    total_assignments: int
    active_assignments: int
    completed_assignments: int
    total_remedies_completed_today: int
    total_days_practiced: int
    total_streaks: int
    longest_current_streak: int
    achievements_count: int
    recent_achievements: List[RemedyAchievement] = Field(default_factory=list)
    active_streaks: List[StreakInfo] = Field(default_factory=list)
    completion_rate_this_week: float
    completion_rate_this_month: float


class CalendarView(BaseModel):
    """Calendar view of completions"""
    year: int
    month: int
    assignment_id: str
    remedy_name: str
    daily_completions: Dict[int, bool]  # day -> completed
    total_days_in_month: int
    days_completed: int
    completion_rate: float


class ProgressChart(BaseModel):
    """Progress chart data"""
    assignment_id: str
    remedy_name: str
    data_points: List[Dict[str, Any]]  # Date and completion status
    trend: str  # "improving", "stable", "declining"


class RecommendedRemediesResponse(BaseModel):
    """AI-recommended remedies based on chart"""
    profile_id: str
    profile_name: str
    recommendations: List[Dict[str, Any]]  # Remedy + reasoning
    priority_remedies: List[RemedyCatalogItem]
    dosha_based_remedies: Dict[str, List[RemedyCatalogItem]]
