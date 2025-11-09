"""
Pydantic schemas for Guided Rituals API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


# ============================================================================
# RITUAL STEP SCHEMA
# ============================================================================

class RitualStep(BaseModel):
    """Schema for a single ritual step"""
    step_number: int = Field(..., ge=1, description="Step number (1-indexed)")
    title: str = Field(..., min_length=1, max_length=200, description="Step title")
    description: str = Field(..., min_length=1, description="Detailed step description")
    mantra: Optional[str] = Field(None, description="Sanskrit mantra for this step")
    mantra_transliteration: Optional[str] = Field(None, description="Romanized mantra pronunciation")
    mantra_translation: Optional[str] = Field(None, description="English translation of mantra")
    duration_seconds: int = Field(..., ge=1, description="Estimated duration in seconds")
    visual_aid_url: Optional[str] = Field(None, description="URL to image/diagram")
    audio_instruction_url: Optional[str] = Field(None, description="URL to audio instructions")
    required_items: Optional[List[str]] = Field(default_factory=list, description="Items needed for this step")
    tips: Optional[List[str]] = Field(default_factory=list, description="Helpful tips for this step")

    class Config:
        json_schema_extra = {
            "example": {
                "step_number": 1,
                "title": "Purification (Achamana)",
                "description": "Sip water three times while chanting mantras for purification",
                "mantra": "Om Keshavaya Namaha, Om Narayanaya Namaha, Om Madhavaya Namaha",
                "mantra_transliteration": "Om Keshavaaya Namaha, Om Naaraayanaaya Namaha, Om Maadhavaaya Namaha",
                "mantra_translation": "Salutations to Lord Keshava, Narayana, and Madhava",
                "duration_seconds": 60,
                "visual_aid_url": "/images/rituals/achamana.jpg",
                "audio_instruction_url": "/audio/rituals/achamana_en.mp3",
                "required_items": ["water", "spoon"],
                "tips": ["Sit facing East", "Use clean water", "Keep spine straight"]
            }
        }


# ============================================================================
# RITUAL TEMPLATE SCHEMAS
# ============================================================================

class RitualTemplateBase(BaseModel):
    """Base schema for ritual template"""
    name: str = Field(..., min_length=1, max_length=200, description="Ritual name")
    category: str = Field(..., description="Ritual category")
    deity: Optional[str] = Field(None, max_length=100, description="Associated deity")
    duration_minutes: int = Field(..., ge=1, description="Total duration in minutes")
    difficulty: str = Field(..., description="Difficulty level")
    description: Optional[str] = Field(None, description="Ritual description and purpose")
    required_items: Optional[List[str]] = Field(default_factory=list, description="List of required materials")
    steps: List[RitualStep] = Field(..., min_items=1, description="Step-by-step instructions")
    audio_enabled: bool = Field(default=False, description="Whether audio guidance is available")
    benefits: Optional[List[str]] = Field(default_factory=list, description="Benefits of performing this ritual")
    best_time_of_day: Optional[str] = Field(None, description="Recommended time of day")

    @validator('category')
    def validate_category(cls, v):
        allowed = ['daily', 'special', 'remedial', 'festival', 'meditation']
        if v not in allowed:
            raise ValueError(f"Category must be one of: {', '.join(allowed)}")
        return v

    @validator('difficulty')
    def validate_difficulty(cls, v):
        allowed = ['beginner', 'intermediate', 'advanced']
        if v not in allowed:
            raise ValueError(f"Difficulty must be one of: {', '.join(allowed)}")
        return v


class RitualTemplateCreate(RitualTemplateBase):
    """Schema for creating a ritual template"""
    pass


class RitualTemplateUpdate(BaseModel):
    """Schema for updating a ritual template"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = None
    deity: Optional[str] = Field(None, max_length=100)
    duration_minutes: Optional[int] = Field(None, ge=1)
    difficulty: Optional[str] = None
    description: Optional[str] = None
    required_items: Optional[List[str]] = None
    steps: Optional[List[RitualStep]] = None
    audio_enabled: Optional[bool] = None
    benefits: Optional[List[str]] = None
    best_time_of_day: Optional[str] = None


class RitualTemplateResponse(RitualTemplateBase):
    """Schema for ritual template response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RitualTemplateSummary(BaseModel):
    """Schema for ritual template summary (list view)"""
    id: UUID
    name: str
    category: str
    deity: Optional[str]
    duration_minutes: int
    difficulty: str
    description: Optional[str]
    required_items: Optional[List[str]]
    audio_enabled: bool
    benefits: Optional[List[str]]
    best_time_of_day: Optional[str]
    step_count: int = Field(..., description="Number of steps in the ritual")

    class Config:
        from_attributes = True


# ============================================================================
# RITUAL SESSION SCHEMAS
# ============================================================================

class RitualSessionStart(BaseModel):
    """Schema for starting a ritual session"""
    ritual_template_id: UUID = Field(..., description="ID of the ritual template to start")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes")


class RitualSessionProgress(BaseModel):
    """Schema for updating ritual progress"""
    current_step: int = Field(..., ge=1, description="Current step number")


class RitualSessionComplete(BaseModel):
    """Schema for completing a ritual session"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="User rating (1-5 stars)")
    notes: Optional[str] = Field(None, max_length=1000, description="Completion notes")


class RitualSessionResponse(BaseModel):
    """Schema for ritual session response"""
    id: UUID
    user_id: UUID
    ritual_template_id: UUID
    started_at: datetime
    completed_at: Optional[datetime]
    current_step: int
    total_steps: int
    status: str = Field(..., description="Session status")
    notes: Optional[str]
    rating: Optional[int]
    created_at: datetime
    updated_at: datetime

    @validator('status')
    def validate_status(cls, v):
        allowed = ['in_progress', 'completed', 'paused', 'abandoned']
        if v not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v

    class Config:
        from_attributes = True


class RitualSessionWithTemplate(RitualSessionResponse):
    """Schema for ritual session with embedded template info"""
    ritual_template: RitualTemplateSummary


class RitualUserStats(BaseModel):
    """Schema for user ritual statistics"""
    total_sessions: int = Field(..., description="Total number of sessions")
    completed: int = Field(..., description="Number of completed sessions")
    in_progress: int = Field(..., description="Number of in-progress sessions")
    paused: int = Field(..., description="Number of paused sessions")
    abandoned: int = Field(..., description="Number of abandoned sessions")
    completion_rate: float = Field(..., description="Completion rate percentage")
    average_rating: Optional[float] = Field(None, description="Average rating for completed rituals")


# ============================================================================
# FILTER AND SEARCH SCHEMAS
# ============================================================================

class RitualFilterParams(BaseModel):
    """Schema for filtering rituals"""
    category: Optional[str] = Field(None, description="Filter by category")
    deity: Optional[str] = Field(None, description="Filter by deity")
    difficulty: Optional[str] = Field(None, description="Filter by difficulty level")
    min_duration: Optional[int] = Field(None, ge=0, description="Minimum duration in minutes")
    max_duration: Optional[int] = Field(None, ge=0, description="Maximum duration in minutes")
    audio_enabled: Optional[bool] = Field(None, description="Filter by audio availability")
    limit: int = Field(50, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class RitualSearchParams(BaseModel):
    """Schema for searching rituals"""
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")


class SessionFilterParams(BaseModel):
    """Schema for filtering user sessions"""
    status: Optional[str] = Field(None, description="Filter by status")
    limit: int = Field(50, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed = ['in_progress', 'completed', 'paused', 'abandoned']
            if v not in allowed:
                raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v


# ============================================================================
# RESPONSE WRAPPERS
# ============================================================================

class RitualTemplateListResponse(BaseModel):
    """Schema for ritual template list response"""
    rituals: List[RitualTemplateSummary]
    total: int
    limit: int
    offset: int


class RitualSessionListResponse(BaseModel):
    """Schema for ritual session list response"""
    sessions: List[RitualSessionResponse]
    total: int
    limit: int
    offset: int
