"""
SQLAlchemy ORM models for Palmistry Intelligence Module.

These models map to the tables created in create_palmistry_tables.sql migration.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Float,
    Integer,
    Boolean,
    Text,
    CheckConstraint,
    Index,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class PalmPhoto(Base):
    """
    Stores uploaded palm images with quality metrics.

    This model represents palm images captured via camera or uploaded by users.
    Each photo includes quality scores, metadata, and validation results.
    """

    __tablename__ = "palm_photos"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User Reference
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Image Classification
    hand_type = Column(
        String(10),
        nullable=False,
        comment="Which hand: left or right"
    )
    view_type = Column(
        String(20),
        nullable=False,
        comment="View angle: front, back, zoomed, thumb_edge, side"
    )
    capture_method = Column(
        String(20),
        nullable=False,
        comment="Capture method: camera or upload"
    )

    # Image Storage
    image_url = Column(Text, nullable=False, comment="Full image URL in storage")
    thumbnail_url = Column(Text, comment="Thumbnail URL for previews")

    # Image Metadata
    image_metadata = Column(
        JSONB,
        default={},
        comment="EXIF data, dimensions, file size, etc."
    )

    # Quality Metrics (0-100 scale)
    quality_score = Column(
        Float,
        comment="Overall image quality score"
    )
    focus_score = Column(
        Float,
        comment="Image sharpness/focus quality"
    )
    lighting_score = Column(
        Float,
        comment="Lighting adequacy score"
    )

    # Validation Results
    is_hand_detected = Column(
        Boolean,
        default=False,
        comment="Whether AI detected a hand"
    )
    validation_details = Column(
        JSONB,
        default={},
        comment="Detailed validation results and suggestions"
    )

    # Device Information
    device_info = Column(
        JSONB,
        default={},
        comment="Capture device details"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), comment="Soft delete timestamp")

    # Relationships
    readings = relationship(
        "PalmReading",
        back_populates="photo",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "hand_type IN ('left', 'right')",
            name="palm_photos_hand_type_check"
        ),
        CheckConstraint(
            "view_type IN ('front', 'back', 'zoomed', 'thumb_edge', 'side')",
            name="palm_photos_view_type_check"
        ),
        CheckConstraint(
            "capture_method IN ('camera', 'upload')",
            name="palm_photos_capture_method_check"
        ),
        CheckConstraint(
            "quality_score BETWEEN 0 AND 100",
            name="palm_photos_quality_score_check"
        ),
        CheckConstraint(
            "focus_score BETWEEN 0 AND 100",
            name="palm_photos_focus_score_check"
        ),
        CheckConstraint(
            "lighting_score BETWEEN 0 AND 100",
            name="palm_photos_lighting_score_check"
        ),
        Index("idx_palm_photos_user_created", "user_id", "created_at"),
        Index("idx_palm_photos_hand_type", "hand_type"),
        Index("idx_palm_photos_quality", "quality_score"),
    )

    def __repr__(self):
        return f"<PalmPhoto {self.hand_type} {self.view_type} ({self.id})>"


class PalmReading(Base):
    """
    Stores AI analysis results for palm readings.

    Contains detected lines, mounts, hand shape classification,
    and other analytical results from AI models.
    """

    __tablename__ = "palm_readings"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    photo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("palm_photos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    model_id = Column(
        UUID(as_uuid=True),
        comment="AI model version used for this reading"
    )

    # Hand Classification
    hand_type = Column(
        String(10),
        nullable=False,
        comment="Left or right hand"
    )
    hand_shape = Column(
        String(20),
        comment="Hand shape: earth, air, fire, water"
    )

    # Detection Results (JSONB for flexibility)
    lines_detected = Column(
        JSONB,
        default=[],
        comment="Array of detected palm lines with coordinates and characteristics"
    )
    mounts_detected = Column(
        JSONB,
        default=[],
        comment="Array of detected mounts with prominence levels"
    )
    special_markings = Column(
        JSONB,
        default=[],
        comment="Stars, crosses, triangles, islands, etc."
    )
    finger_analysis = Column(
        JSONB,
        default={},
        comment="Finger length ratios, spacing, flexibility"
    )

    # Predictions
    life_events = Column(
        JSONB,
        default=[],
        comment="Predicted life events with timing"
    )
    personality_traits = Column(
        JSONB,
        default=[],
        comment="Identified personality characteristics"
    )

    # Quality Metrics
    overall_confidence = Column(
        Float,
        nullable=False,
        comment="Overall reading confidence (0.0-1.0)"
    )
    detection_scores = Column(
        JSONB,
        default={},
        comment="Individual detection confidence scores"
    )

    # Processing Metadata
    processing_time_ms = Column(
        Integer,
        comment="Time taken for AI processing in milliseconds"
    )
    model_version = Column(
        String(50),
        comment="Specific model version identifier"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    photo = relationship("PalmPhoto", back_populates="readings")
    interpretations = relationship(
        "PalmInterpretation",
        back_populates="reading",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "hand_type IN ('left', 'right')",
            name="palm_readings_hand_type_check"
        ),
        CheckConstraint(
            "hand_shape IN ('earth', 'air', 'fire', 'water') OR hand_shape IS NULL",
            name="palm_readings_hand_shape_check"
        ),
        CheckConstraint(
            "overall_confidence BETWEEN 0.0 AND 1.0",
            name="palm_readings_confidence_check"
        ),
        Index("idx_palm_readings_user_created", "user_id", "created_at"),
        Index("idx_palm_readings_confidence", "overall_confidence"),
    )

    def __repr__(self):
        return f"<PalmReading {self.hand_type} conf={self.overall_confidence:.2f} ({self.id})>"


class PalmInterpretation(Base):
    """
    Stores RAG-generated natural language interpretations.

    Contains AI-generated explanations, personality insights,
    life event predictions, and cross-domain correlations.
    """

    __tablename__ = "palm_interpretations"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    reading_id = Column(
        UUID(as_uuid=True),
        ForeignKey("palm_readings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Interpretation Content
    summary = Column(
        Text,
        nullable=False,
        comment="Brief 2-3 sentence summary"
    )
    detailed_analysis = Column(
        Text,
        nullable=False,
        comment="Comprehensive interpretation"
    )

    # Structured Insights
    personality_traits = Column(
        JSONB,
        default=[],
        comment="List of key personality traits"
    )
    life_events = Column(
        JSONB,
        default=[],
        comment="Predicted life events with timing and descriptions"
    )
    recommendations = Column(
        JSONB,
        default=[],
        comment="Actionable recommendations and remedies"
    )

    # Cross-Domain Correlations
    astrology_correlations = Column(
        JSONB,
        comment="Correlations with user's birth chart"
    )
    numerology_correlations = Column(
        JSONB,
        comment="Correlations with user's numerology profile"
    )

    # RAG Metadata
    rag_sources = Column(
        JSONB,
        default=[],
        comment="Knowledge base sources used in generation"
    )
    model_version = Column(
        String(50),
        comment="RAG model version"
    )
    generation_parameters = Column(
        JSONB,
        default={},
        comment="Model parameters used (temperature, top_p, etc.)"
    )

    # Quality Metrics
    coherence_score = Column(
        Float,
        comment="Interpretation coherence score"
    )
    relevance_score = Column(
        Float,
        comment="Relevance to reading score"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    reading = relationship("PalmReading", back_populates="interpretations")
    feedback_entries = relationship(
        "PalmFeedback",
        back_populates="interpretation",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        Index("idx_palm_interpretations_user_created", "user_id", "created_at"),
    )

    def __repr__(self):
        return f"<PalmInterpretation reading_id={self.reading_id} ({self.id})>"


class AIModel(Base):
    """
    Tracks AI model versions for reanalysis capability.

    Stores model metadata, accuracy metrics, and deployment information.
    """

    __tablename__ = "ai_models"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Model Identification
    model_name = Column(
        String(100),
        nullable=False,
        comment="Human-readable model name"
    )
    model_version = Column(
        String(50),
        nullable=False,
        unique=True,
        comment="Semantic version (e.g., v1.2.3)"
    )
    model_type = Column(
        String(50),
        nullable=False,
        comment="Type: hand_detection, line_detection, mount_detection, etc."
    )

    # Model Metadata
    model_path = Column(
        Text,
        comment="Storage path for model weights"
    )
    framework = Column(
        String(50),
        comment="PyTorch, TensorFlow, etc."
    )
    architecture = Column(
        String(100),
        comment="Model architecture name (ResNet, U-Net, etc.)"
    )

    # Performance Metrics
    accuracy_metrics = Column(
        JSONB,
        default={},
        comment="Accuracy, precision, recall, F1, etc."
    )
    training_data_size = Column(
        Integer,
        comment="Number of training samples"
    )
    training_date = Column(
        DateTime(timezone=True),
        comment="When model was trained"
    )

    # Deployment Status
    is_active = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this model is currently in production"
    )
    deployment_date = Column(
        DateTime(timezone=True),
        comment="When model was deployed to production"
    )
    deprecated_date = Column(
        DateTime(timezone=True),
        comment="When model was deprecated"
    )

    # Additional Metadata
    description = Column(
        Text,
        comment="Model description and notes"
    )
    changelog = Column(
        Text,
        comment="Changes from previous version"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "model_type IN ('hand_detection', 'line_detection', 'mount_detection', 'shape_classification', 'rag_model')",
            name="ai_models_type_check"
        ),
        Index("idx_ai_models_active", "is_active", "model_type"),
        Index("idx_ai_models_version", "model_version"),
    )

    def __repr__(self):
        return f"<AIModel {self.model_name} {self.model_version}>"


class ReanalysisQueue(Base):
    """
    Queue for reanalyzing photos with updated AI models.

    Tracks photos that need reprocessing when new model versions are deployed.
    """

    __tablename__ = "reanalysis_queue"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    photo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("palm_photos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Model Version Tracking
    old_model_version = Column(
        String(50),
        comment="Previous model version"
    )
    new_model_version = Column(
        String(50),
        nullable=False,
        comment="Target model version for reanalysis"
    )

    # Queue Management
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="Queue status: pending, processing, completed, failed"
    )
    priority = Column(
        Integer,
        default=5,
        comment="Processing priority (1=highest, 10=lowest)"
    )
    retry_count = Column(
        Integer,
        default=0,
        comment="Number of retry attempts"
    )
    error_message = Column(
        Text,
        comment="Error details if status=failed"
    )

    # Timestamps
    scheduled_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When reanalysis was scheduled"
    )
    started_at = Column(
        DateTime(timezone=True),
        comment="When processing started"
    )
    completed_at = Column(
        DateTime(timezone=True),
        comment="When reanalysis completed"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="reanalysis_queue_status_check"
        ),
        CheckConstraint(
            "priority BETWEEN 1 AND 10",
            name="reanalysis_queue_priority_check"
        ),
        Index("idx_reanalysis_queue_status_priority", "status", "priority"),
        Index("idx_reanalysis_queue_scheduled", "scheduled_at"),
    )

    def __repr__(self):
        return f"<ReanalysisQueue photo_id={self.photo_id} status={self.status}>"


class PalmFeedback(Base):
    """
    User feedback on palm interpretations.

    Collects ratings and comments to improve AI models and interpretations.
    """

    __tablename__ = "palm_feedback"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    interpretation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("palm_interpretations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Feedback Content
    rating = Column(
        Integer,
        nullable=False,
        comment="Rating from 1 to 5"
    )
    feedback_type = Column(
        String(50),
        nullable=False,
        comment="Type: accuracy, completeness, clarity, relevance"
    )
    comments = Column(
        Text,
        comment="User comments and suggestions"
    )

    # Sentiment Analysis (optional)
    sentiment_score = Column(
        Float,
        comment="Automated sentiment analysis score (-1.0 to 1.0)"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    interpretation = relationship("PalmInterpretation", back_populates="feedback_entries")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "rating BETWEEN 1 AND 5",
            name="palm_feedback_rating_check"
        ),
        CheckConstraint(
            "feedback_type IN ('accuracy', 'completeness', 'clarity', 'relevance')",
            name="palm_feedback_type_check"
        ),
        Index("idx_palm_feedback_user_created", "user_id", "created_at"),
        Index("idx_palm_feedback_rating", "rating"),
    )

    def __repr__(self):
        return f"<PalmFeedback rating={self.rating} type={self.feedback_type} ({self.id})>"
