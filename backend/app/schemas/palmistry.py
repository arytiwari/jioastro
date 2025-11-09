"""
Pydantic schemas for Palmistry API endpoints.

This module defines all request/response models for the Palmistry Intelligence Module.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, validator


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class DeviceInfo(BaseModel):
    """Device information for image capture metadata."""

    user_agent: Optional[str] = Field(None, description="Browser user agent")
    screen_width: Optional[int] = Field(None, description="Screen width in pixels")
    screen_height: Optional[int] = Field(None, description="Screen height in pixels")
    device_type: Optional[Literal["mobile", "tablet", "desktop"]] = Field(
        None,
        description="Device category"
    )


class ImageUploadRequest(BaseModel):
    """Request model for uploading palm image."""

    hand_type: Literal["left", "right"] = Field(
        ...,
        description="Which hand is being captured"
    )
    view_type: Literal["front", "back", "zoomed", "thumb_edge", "side"] = Field(
        ...,
        description="Type of palm view"
    )
    image: str = Field(
        ...,
        description="Base64 encoded image data"
    )
    capture_method: Literal["camera", "upload"] = Field(
        ...,
        description="How the image was captured"
    )
    profile_id: Optional[str] = Field(
        None,
        description="Birth profile ID for holistic AI analysis (combines astrology, numerology, palmistry)"
    )
    device_info: Optional[DeviceInfo] = Field(
        None,
        description="Device metadata"
    )

    @validator("image")
    def validate_image_format(cls, v):
        """Validate base64 image format."""
        if not v or len(v) < 100:
            raise ValueError("Image data is too short or invalid")
        # Check for data URL prefix
        if v.startswith("data:image"):
            return v
        # Assume raw base64 if no prefix
        return f"data:image/jpeg;base64,{v}"


class AnalysisRequest(BaseModel):
    """Request model for analyzing palm images."""

    photo_ids: List[str] = Field(  # Changed from List[UUID] to List[str]
        ...,
        min_items=1,
        max_items=10,
        description="List of photo IDs to analyze (1-10 photos)"
    )
    reanalysis: bool = Field(
        False,
        description="Force reanalysis even if results exist"
    )
    priority: Literal["high", "normal", "low"] = Field(
        "normal",
        description="Analysis priority for queue"
    )


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback on interpretations."""

    interpretation_id: str = Field(..., description="Interpretation ID")  # Changed from UUID to str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    feedback_type: Literal["accuracy", "completeness", "clarity", "relevance"] = Field(
        ...,
        description="Type of feedback"
    )
    comments: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional comments"
    )


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ImageValidation(BaseModel):
    """Image quality validation results."""

    is_hand_detected: bool = Field(..., description="Whether a hand was detected")
    focus_quality: Literal["poor", "fair", "good", "excellent"] = Field(
        ...,
        description="Image focus quality"
    )
    lighting_quality: Literal["poor", "fair", "good", "excellent"] = Field(
        ...,
        description="Lighting quality"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Improvement suggestions"
    )
    quality_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall quality score (0-100)"
    )


class ImageUploadResponse(BaseModel):
    """Response model for image upload."""

    photo_id: str = Field(..., description="Unique photo ID")  # Changed from UUID to str
    thumbnail_url: str = Field(..., description="Thumbnail URL")
    image_url: str = Field(..., description="Full image URL")
    quality_score: float = Field(..., description="Quality score (0-100)")
    validation: ImageValidation = Field(..., description="Validation results")
    created_at: datetime = Field(..., description="Upload timestamp")


class LineDetection(BaseModel):
    """Individual palm line detection result."""

    line_type: str = Field(..., description="Type of line (e.g., life, heart, head)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    coordinates: List[List[float]] = Field(
        ...,
        description="Line coordinates [[x1,y1], [x2,y2], ...]"
    )
    characteristics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Line characteristics (length, depth, breaks, etc.)"
    )


class MountDetection(BaseModel):
    """Palm mount detection result."""

    mount_name: str = Field(..., description="Mount name (e.g., Venus, Jupiter)")
    prominence: Literal["flat", "moderate", "prominent", "very_prominent"] = Field(
        ...,
        description="Mount prominence level"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    area_coordinates: List[List[float]] = Field(
        ...,
        description="Mount area polygon coordinates"
    )


class PalmReading(BaseModel):
    """Complete palm reading analysis result."""

    reading_id: str = Field(..., description="Unique reading ID")  # Changed from UUID to str
    photo_id: str = Field(..., description="Associated photo ID")  # Changed from UUID to str
    hand_type: Literal["left", "right"] = Field(..., description="Hand type")
    profile_id: Optional[str] = Field(None, description="Linked birth profile ID for holistic analysis")

    # AI Detection Results
    hand_shape: Optional[Literal["earth", "air", "fire", "water"]] = Field(
        None,
        description="Hand shape classification"
    )
    lines_detected: List[LineDetection] = Field(
        default_factory=list,
        description="Detected palm lines"
    )
    mounts_detected: List[MountDetection] = Field(
        default_factory=list,
        description="Detected palm mounts"
    )

    # Metadata
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    model_version: str = Field(..., description="AI model version used")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    created_at: datetime = Field(..., description="Analysis timestamp")


class EventPrediction(BaseModel):
    """Predicted life event from palm reading."""

    event_type: str = Field(..., description="Type of event (career, health, relationship)")
    description: str = Field(..., description="Event description")
    age_range: Optional[str] = Field(None, description="Predicted age range (e.g., '25-30')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    zone: Optional[str] = Field(None, description="Palm zone where event is indicated")


class PalmInterpretation(BaseModel):
    """RAG-generated natural language interpretation."""

    interpretation_id: str = Field(..., description="Unique interpretation ID")  # Changed from UUID to str
    reading_id: str = Field(..., description="Associated reading ID")  # Changed from UUID to str
    user_id: str = Field(..., description="User ID")  # Required by database schema
    profile_id: Optional[str] = Field(None, description="Linked birth profile ID for holistic analysis")

    # Interpretation Content
    summary: str = Field(..., description="Brief summary of reading")
    detailed_analysis: str = Field(..., description="Detailed interpretation")
    personality_traits: List[str] = Field(
        default_factory=list,
        description="Key personality traits"
    )
    life_events: List[EventPrediction] = Field(
        default_factory=list,
        description="Predicted life events"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations and remedies"
    )

    # Cross-Domain Correlations (with Astrology/Numerology)
    astrology_correlations: Optional[Dict[str, Any]] = Field(
        None,
        description="Correlations with user's birth chart"
    )
    numerology_correlations: Optional[Dict[str, Any]] = Field(
        None,
        description="Correlations with user's numerology profile"
    )

    # Metadata
    created_at: datetime = Field(..., description="Generation timestamp")  # Changed from generated_at to match DB
    rag_sources: List[str] = Field(
        default_factory=list,
        description="Knowledge base sources used"
    )


class AnalysisResponse(BaseModel):
    """Response model for palm analysis."""

    reading: PalmReading = Field(..., description="Palm reading results")
    interpretation: PalmInterpretation = Field(..., description="AI interpretation")
    status: Literal["completed", "processing", "failed"] = Field(
        ...,
        description="Analysis status"
    )
    error_message: Optional[str] = Field(None, description="Error message if failed")


class UserReadingStats(BaseModel):
    """User's palm reading statistics."""

    total_readings: int = Field(..., description="Total number of readings")
    avg_confidence: float = Field(..., description="Average reading confidence")
    latest_reading_date: Optional[datetime] = Field(
        None,
        description="Date of latest reading"
    )
    hands_analyzed: Dict[str, int] = Field(
        default_factory=dict,
        description="Count by hand type"
    )


class ReadingListItem(BaseModel):
    """Summary item for reading list."""

    reading_id: str  # Changed from UUID to str
    photo_id: str  # Changed from UUID to str
    hand_type: Literal["left", "right"]
    created_at: datetime
    overall_confidence: float
    has_interpretation: bool
    thumbnail_url: str


class ReadingListResponse(BaseModel):
    """Response model for listing user's readings."""

    readings: List[ReadingListItem] = Field(..., description="List of readings")
    total_count: int = Field(..., description="Total number of readings")
    stats: UserReadingStats = Field(..., description="User statistics")


class ComparisonResponse(BaseModel):
    """Response model for comparing left and right hand readings."""

    left_reading: Optional[PalmReading] = Field(None, description="Left hand reading")
    right_reading: Optional[PalmReading] = Field(None, description="Right hand reading")
    comparison_analysis: str = Field(
        ...,
        description="AI-generated comparison analysis"
    )
    key_differences: List[str] = Field(
        default_factory=list,
        description="Key differences between hands"
    )
    unified_interpretation: str = Field(
        ...,
        description="Combined interpretation of both hands"
    )


class ReanalysisQueueItem(BaseModel):
    """Reanalysis queue item status."""

    queue_id: str  # Changed from UUID to str
    photo_id: str  # Changed from UUID to str
    old_model_version: str
    new_model_version: str
    status: Literal["pending", "processing", "completed", "failed"]
    priority: int
    scheduled_at: datetime
    completed_at: Optional[datetime] = None


class ModelInfo(BaseModel):
    """AI model information."""

    model_id: str  # Changed from UUID to str
    model_name: str
    model_version: str
    model_type: Literal["hand_detection", "line_detection", "mount_detection", "shape_classification"]
    is_active: bool
    accuracy_metrics: Dict[str, float]
    deployment_date: datetime


class HealthCheckResponse(BaseModel):
    """Health check response for Palmistry service."""

    status: Literal["healthy", "degraded", "unhealthy"]
    database_connected: bool
    storage_accessible: bool
    ai_models_loaded: bool
    active_models: List[ModelInfo]
    queue_size: int
    last_check: datetime


# ============================================================================
# ERROR RESPONSE SCHEMAS
# ============================================================================

class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused error")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[List[ErrorDetail]] = Field(
        None,
        description="Detailed error information"
    )
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
