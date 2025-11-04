"""Reading Schemas for AI Engine"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID


class ReadingCalculateRequest(BaseModel):
    """Schema for reading calculation request"""

    # Birth data
    name: str
    dob: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date of birth (YYYY-MM-DD)")
    tob: str = Field(..., pattern=r'^\d{2}:\d{2}$', description="Time of birth (HH:MM)")

    # Location (provide either city_id or lat/lon)
    city_id: Optional[str] = None
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: str = "Asia/Kolkata"
    city: str = "Unknown"

    # Chart types to calculate
    chart_types: List[str] = ["D1", "D9", "Moon"]

    # Reading preferences
    reading_type: str = Field(default="full", pattern="^(full|quick|dasha|transit|specific)$")
    domains: Optional[List[str]] = None  # Specific domains to focus on
    include_remedies: bool = False


class ReadingResponse(BaseModel):
    """Schema for reading response"""

    # Session info
    session_id: UUID
    canonical_hash: str
    cached: bool = False

    # Chart data
    charts: Dict[str, Any]
    dashas: Dict[str, Any]
    transits: Optional[Dict[str, Any]] = None

    # Basics
    basics: Dict[str, Any]

    # Metadata
    meta: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class AIReadingRequest(BaseModel):
    """Schema for AI-powered reading request"""

    # Birth data (same as ReadingCalculateRequest)
    name: str
    dob: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    tob: str = Field(..., pattern=r'^\d{2}:\d{2}$')

    # Location
    city_id: Optional[str] = None
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: str = "Asia/Kolkata"
    city: str = "Unknown"

    # AI preferences
    reading_depth: str = Field(default="medium", pattern="^(brief|medium|detailed)$")
    domains: Optional[List[str]] = None
    include_remedies: bool = False
    language: str = "en"

    # Context (optional)
    question: Optional[str] = None  # Specific question to focus on
    event_anchors: Optional[List[Dict[str, Any]]] = None  # Known life events for better predictions


class AIReadingResponse(BaseModel):
    """Schema for AI-powered reading response"""

    # Session info
    session_id: UUID
    canonical_hash: str

    # Summary
    summary: List[str]  # 2-5 bullet points

    # Core findings
    charts: Dict[str, Any]
    dashas: Dict[str, Any]
    transits: Dict[str, Any]

    # Predictions by domain
    predictions: Dict[str, Dict[str, Any]]  # {domain: {windows, strength, triggers, etc.}}

    # Remedies (if requested)
    remedies: Optional[List[Dict[str, Any]]] = None

    # Quality metrics
    confidence: float
    rule_count: int
    citations: List[str]  # Rule IDs cited

    # Meta
    ai_model: str
    total_tokens: int
    cost_usd: float
    duration_seconds: int

    # Next steps
    next_questions: List[str]  # Suggested follow-up questions
    data_to_remember: Dict[str, Any]  # What to store in memory

    created_at: datetime

    class Config:
        from_attributes = True


class QuestionRequest(BaseModel):
    """Schema for specific question"""

    profile_id: UUID
    question: str
    context: Optional[str] = None  # Additional context


class QuestionResponse(BaseModel):
    """Schema for question response"""

    answer: str
    sources: List[str]  # Rule IDs
    confidence: float
    related_predictions: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class RectificationRequest(BaseModel):
    """Schema for birth time rectification"""

    name: str
    dob: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    tob_range_start: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    tob_range_end: str = Field(..., pattern=r'^\d{2}:\d{2}$')

    # Location
    city_id: Optional[str] = None
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: str = "Asia/Kolkata"
    city: str = "Unknown"

    # Event anchors (3-6 required)
    event_anchors: List[Dict[str, Any]]


class RectificationResponse(BaseModel):
    """Schema for rectification response"""

    suggested_times: List[Dict[str, Any]]  # [{time, confidence, reasoning}]
    confidence_range: str  # e.g., "14:30-14:45 (High confidence)"
    anchors_used: List[str]
    notes: str

    class Config:
        from_attributes = True


class MemoryUpdateRequest(BaseModel):
    """Schema for updating user memory"""

    rectified_birth_time: Optional[str] = None
    preferred_place_id: Optional[str] = None
    language: Optional[str] = None
    remedy_preference: Optional[str] = None
    reading_depth: Optional[str] = None
    domains_of_interest: Optional[List[str]] = None


class EventAnchorRequest(BaseModel):
    """Schema for adding event anchor"""

    profile_id: UUID
    event_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    event_time: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    event_type: str
    description: str
    significance: str = Field(default="medium", pattern="^(low|medium|high)$")
