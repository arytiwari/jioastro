"""
Database models for Instant Onboarding feature.
"""

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Enum as SQLEnum, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.db.database import Base


class SessionStatus(str, enum.Enum):
    """Status of onboarding session."""
    STARTED = "started"
    COLLECTING_DATA = "collecting_data"
    GENERATING_CHART = "generating_chart"
    COMPLETED = "completed"
    FAILED = "failed"


class OnboardingChannel(str, enum.Enum):
    """Channel through which user is onboarding."""
    WHATSAPP = "whatsapp"
    WEB = "web"
    VOICE = "voice"
    SMS = "sms"


class InstantOnboardingSession(Base):
    """
    Track instant onboarding sessions.

    Table: instant_onboarding_sessions
    """

    __tablename__ = "instant_onboarding_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Session info
    session_key = Column(String(255), unique=True, nullable=False, index=True)  # For WhatsApp/external tracking
    channel = Column(SQLEnum(OnboardingChannel), nullable=False, default=OnboardingChannel.WEB)
    status = Column(SQLEnum(SessionStatus), nullable=False, default=SessionStatus.STARTED)
    language = Column(String(10), nullable=False, default="en")  # ISO language code

    # User identification (nullable until created)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    phone_number = Column(String(20), nullable=True)  # For WhatsApp

    # Collected data
    collected_data = Column(JSON, nullable=False, default=dict)  # Stores intermediate form data

    # Progress tracking
    current_step = Column(Integer, default=0)  # Which data point we're collecting
    steps_completed = Column(JSON, nullable=False, default=list)  # List of completed steps

    # Result
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True)
    chart_generated = Column(Boolean, default=False)

    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<InstantOnboardingSession(id={self.id}, channel={self.channel}, status={self.status})>"


class InstantOnboardingProfile(Base):
    """
    Quick profiles created through instant onboarding.

    Table: instant_onboarding_profiles
    """

    __tablename__ = "instant_onboarding_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Link to session and user
    session_id = Column(UUID(as_uuid=True), ForeignKey("instant_onboarding_sessions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)

    # Onboarding metadata
    channel = Column(SQLEnum(OnboardingChannel), nullable=False)
    language = Column(String(10), nullable=False, default="en")
    time_taken_seconds = Column(Integer, nullable=True)  # How long did onboarding take

    # Engagement metrics
    viewed_chart = Column(Boolean, default=False)
    shared_chart = Column(Boolean, default=False)
    converted_to_full_user = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<InstantOnboardingProfile(id={self.id}, channel={self.channel})>"
