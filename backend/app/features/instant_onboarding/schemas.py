"""
Pydantic schemas for Instant Onboarding feature.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime, date, time
from typing import Optional, Dict, Any, List, Literal
from uuid import UUID
from enum import Enum


class OnboardingChannel(str, Enum):
    """Channel through which user is onboarding."""
    WHATSAPP = "whatsapp"
    WEB = "web"
    VOICE = "voice"
    SMS = "sms"


class SessionStatus(str, Enum):
    """Status of onboarding session."""
    STARTED = "started"
    COLLECTING_DATA = "collecting_data"
    GENERATING_CHART = "generating_chart"
    COMPLETED = "completed"
    FAILED = "failed"


# Session Management Schemas

class SessionStartRequest(BaseModel):
    """Request to start a new onboarding session."""
    channel: OnboardingChannel = Field(default=OnboardingChannel.WEB)
    language: str = Field(default="en", description="ISO language code (en, hi, etc.)")
    phone_number: Optional[str] = Field(None, description="Phone number for WhatsApp channel")
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SessionStartResponse(BaseModel):
    """Response when starting a new session."""
    session_id: UUID
    session_key: str
    status: SessionStatus
    next_step: str
    message: str  # User-friendly message in selected language

    class Config:
        from_attributes = True


class CollectDataRequest(BaseModel):
    """Request to update session with collected data."""
    session_key: str
    data: Dict[str, Any]  # Flexible data structure for different collection methods


class CollectDataResponse(BaseModel):
    """Response after collecting data."""
    session_id: UUID
    status: SessionStatus
    current_step: int
    next_step: Optional[str]
    message: str
    is_complete: bool
    missing_fields: List[str] = Field(default_factory=list)


# Quick Chart Generation Schemas

class QuickChartRequest(BaseModel):
    """Request for quick chart generation."""
    # Option 1: Use existing session
    session_key: Optional[str] = None

    # Option 2: Provide all data directly
    name: Optional[str] = None
    birth_date: Optional[date] = None
    birth_time: Optional[time] = None
    birth_place: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    timezone: Optional[str] = None
    gender: Optional[Literal["male", "female", "other"]] = Field(
        None,
        description="Optional gender for astrological interpretations"
    )

    # Options
    language: str = Field(default="en")
    include_numerology: bool = Field(default=False)

    @validator("birth_date")
    def validate_birth_date(cls, v):
        if v and v > datetime.now().date():
            raise ValueError("Birth date cannot be in the future")
        return v

    @validator("gender")
    def validate_gender(cls, v):
        """Validate gender field"""
        if v is not None and v not in ["male", "female", "other"]:
            raise ValueError("Gender must be one of: male, female, other")
        return v


class QuickChartResponse(BaseModel):
    """Response with generated chart."""
    session_id: UUID
    profile_id: UUID
    chart_url: Optional[str] = None  # URL to view full chart
    summary: Dict[str, Any]  # Quick summary of key insights

    # Basic chart data
    sun_sign: str
    moon_sign: str
    ascendant: str

    # Top insights
    top_insights: List[str] = Field(default_factory=list, max_items=3)

    # Shareable
    shareable_link: Optional[str] = None
    qr_code: Optional[str] = None  # Base64 encoded QR code image

    # Profile info
    name: Optional[str] = None
    birth_date: Optional[str] = None  # Birth date for display
    generated_at: Optional[str] = None

    class Config:
        from_attributes = True


# WhatsApp Integration Schemas

class WhatsAppWebhookRequest(BaseModel):
    """Schema for WhatsApp webhook payload."""
    messaging_product: str = "whatsapp"
    metadata: Dict[str, Any]
    contacts: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]


class WhatsAppMessageRequest(BaseModel):
    """Simplified WhatsApp message for processing."""
    from_number: str
    message_id: str
    message_type: str  # text, voice, location
    content: Any  # Text, audio file ID, or location data
    timestamp: datetime


class WhatsAppResponse(BaseModel):
    """Response to send back via WhatsApp."""
    to_number: str
    message_type: str = "text"
    content: str
    buttons: Optional[List[Dict[str, str]]] = None


# Voice Input Schemas

class VoiceInputRequest(BaseModel):
    """Request for voice input processing."""
    session_key: str
    audio_url: Optional[str] = None  # URL to audio file
    audio_data: Optional[str] = None  # Base64 encoded audio
    language: str = Field(default="en")


class VoiceInputResponse(BaseModel):
    """Response after processing voice input."""
    transcription: str
    extracted_data: Dict[str, Any]
    confidence: float = Field(ge=0, le=1)
    next_prompt: str


# Session Response Schemas

class SessionResponse(BaseModel):
    """Full session details."""
    id: UUID
    session_key: str
    channel: OnboardingChannel
    status: SessionStatus
    language: str
    current_step: int
    collected_data: Dict[str, Any]
    profile_id: Optional[UUID] = None
    chart_generated: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OnboardingProfileResponse(BaseModel):
    """Onboarding profile details."""
    id: UUID
    session_id: UUID
    profile_id: UUID
    channel: OnboardingChannel
    language: str
    time_taken_seconds: Optional[int] = None
    viewed_chart: bool
    shared_chart: bool
    created_at: datetime

    class Config:
        from_attributes = True
