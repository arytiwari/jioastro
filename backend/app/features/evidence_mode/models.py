"""
Database models for Evidence Mode feature.

This module provides three main models:
1. EvidenceModeSource - Reference sources (texts, papers, experts)
2. EvidenceModeCitation - Links between insights and sources
3. EvidenceModeValidation - Expert validation and confidence tracking
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.database import Base


class SourceType(str, enum.Enum):
    """Types of evidence sources."""
    CLASSICAL_TEXT = "classical_text"  # BPHS, Jataka Parijata, etc.
    RESEARCH_PAPER = "research_paper"  # Academic research
    EXPERT_OPINION = "expert_opinion"  # Validated astrologer opinions
    STATISTICAL = "statistical"  # Statistical analysis
    TRADITIONAL = "traditional"  # Traditional teachings
    MODERN_STUDY = "modern_study"  # Modern astrological studies


class ConfidenceLevel(str, enum.Enum):
    """Confidence levels for citations and validations."""
    VERY_HIGH = "very_high"  # 90-100%
    HIGH = "high"  # 75-89%
    MEDIUM = "medium"  # 50-74%
    LOW = "low"  # 25-49%
    VERY_LOW = "very_low"  # 0-24%


class ValidationStatus(str, enum.Enum):
    """Status of validation process."""
    PENDING = "pending"
    VALIDATED = "validated"
    DISPUTED = "disputed"
    REJECTED = "rejected"


class EvidenceModeSource(Base):
    """
    Reference sources for astrological insights.

    Stores classical texts, research papers, expert opinions, and other
    evidence sources that back astrological interpretations.

    Table: evidence_mode_sources
    """

    __tablename__ = "evidence_mode_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Source identification
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(255), nullable=True)
    source_type = Column(Enum(SourceType), nullable=False, index=True)

    # Content
    description = Column(Text, nullable=True)
    excerpt = Column(Text, nullable=True)  # Relevant excerpt/quote
    full_text = Column(Text, nullable=True)  # Full text if available

    # Reference details
    publication_year = Column(Integer, nullable=True)
    publisher = Column(String(255), nullable=True)
    isbn_doi = Column(String(100), nullable=True)  # ISBN or DOI
    url = Column(String(500), nullable=True)  # Online reference
    page_reference = Column(String(100), nullable=True)  # Page/chapter reference

    # Metadata
    language = Column(String(50), default="english")
    tags = Column(JSONB, nullable=True)  # Array of topic tags
    keywords = Column(JSONB, nullable=True)  # Searchable keywords

    # Quality metrics
    credibility_score = Column(Float, default=0.5)  # 0.0 to 1.0
    citation_count = Column(Integer, default=0)  # How many times cited

    # Status
    is_verified = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)  # Admin/expert who added

    # Relationships
    citations = relationship("EvidenceModeCitation", back_populates="source", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_source_type_verified', 'source_type', 'is_verified'),
        Index('idx_source_title_search', 'title'),
    )

    def __repr__(self):
        return f"<EvidenceModeSource(title='{self.title}', type={self.source_type})>"


class EvidenceModeCitation(Base):
    """
    Links astrological insights to evidence sources.

    Creates citations that connect specific astrological interpretations,
    yogas, or predictions to their supporting evidence sources.

    Table: evidence_mode_citations
    """

    __tablename__ = "evidence_mode_citations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Link to source
    source_id = Column(UUID(as_uuid=True), ForeignKey("evidence_mode_sources.id"), nullable=False, index=True)

    # What is being cited
    insight_type = Column(String(100), nullable=False)  # "yoga", "planet_position", "dasha", etc.
    insight_text = Column(Text, nullable=False)  # The actual insight/interpretation
    insight_reference = Column(String(255), nullable=True)  # Reference ID (chart_id, query_id, etc.)

    # Citation details
    relevance_score = Column(Float, default=0.5)  # How relevant is this source (0.0 to 1.0)
    confidence_level = Column(Enum(ConfidenceLevel), default=ConfidenceLevel.MEDIUM)
    confidence_score = Column(Float, nullable=True)  # Numeric confidence (0.0 to 1.0)

    # Context
    context = Column(JSONB, nullable=True)  # Additional context (planet positions, house, etc.)
    reasoning = Column(Text, nullable=True)  # Why this citation is relevant

    # Usage tracking
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    source = relationship("EvidenceModeSource", back_populates="citations")
    validations = relationship("EvidenceModeValidation", back_populates="citation", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_citation_insight_type', 'insight_type'),
        Index('idx_citation_source_active', 'source_id', 'is_active'),
        Index('idx_citation_confidence', 'confidence_level'),
    )

    def __repr__(self):
        return f"<EvidenceModeCitation(insight_type='{self.insight_type}', confidence={self.confidence_level})>"


class EvidenceModeValidation(Base):
    """
    Expert validation and peer review of citations.

    Tracks expert validations of citations, including approval, disputes,
    and confidence adjustments.

    Table: evidence_mode_validations
    """

    __tablename__ = "evidence_mode_validations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Link to citation
    citation_id = Column(UUID(as_uuid=True), ForeignKey("evidence_mode_citations.id"), nullable=False, index=True)

    # Validator information
    validator_id = Column(UUID(as_uuid=True), nullable=False)  # Expert/admin user ID
    validator_name = Column(String(255), nullable=True)
    validator_credentials = Column(String(500), nullable=True)

    # Validation details
    status = Column(Enum(ValidationStatus), nullable=False, default=ValidationStatus.PENDING)
    confidence_adjustment = Column(Float, nullable=True)  # Adjustment to citation confidence

    # Feedback
    comments = Column(Text, nullable=True)
    suggestions = Column(Text, nullable=True)
    alternative_sources = Column(JSONB, nullable=True)  # Suggested alternative source IDs

    # Validation metrics
    accuracy_score = Column(Float, nullable=True)  # Expert's accuracy rating (0.0 to 1.0)
    relevance_score = Column(Float, nullable=True)  # Expert's relevance rating (0.0 to 1.0)

    # Status flags
    is_public = Column(Boolean, default=True)
    requires_review = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    citation = relationship("EvidenceModeCitation", back_populates="validations")

    # Indexes
    __table_args__ = (
        Index('idx_validation_citation_status', 'citation_id', 'status'),
        Index('idx_validation_validator', 'validator_id'),
    )

    def __repr__(self):
        return f"<EvidenceModeValidation(citation_id={self.citation_id}, status={self.status})>"
