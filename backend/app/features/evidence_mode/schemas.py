"""
Pydantic schemas for Evidence Mode feature.

Request and response schemas for Evidence Mode API endpoints.
"""

from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum


# Enums (matching database enums)
class SourceType(str, Enum):
    """Types of evidence sources."""
    CLASSICAL_TEXT = "classical_text"
    RESEARCH_PAPER = "research_paper"
    EXPERT_OPINION = "expert_opinion"
    STATISTICAL = "statistical"
    TRADITIONAL = "traditional"
    MODERN_STUDY = "modern_study"


class ConfidenceLevel(str, Enum):
    """Confidence levels."""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class ValidationStatus(str, Enum):
    """Validation status."""
    PENDING = "pending"
    VALIDATED = "validated"
    DISPUTED = "disputed"
    REJECTED = "rejected"


# ============================================================================
# Source Schemas
# ============================================================================

class SourceBase(BaseModel):
    """Base schema for evidence source."""
    title: str = Field(..., min_length=1, max_length=500, description="Source title")
    author: Optional[str] = Field(None, max_length=255, description="Author name")
    source_type: SourceType = Field(..., description="Type of source")
    description: Optional[str] = Field(None, description="Source description")
    excerpt: Optional[str] = Field(None, description="Relevant excerpt or quote")


class SourceCreate(SourceBase):
    """Schema for creating a new evidence source."""
    full_text: Optional[str] = Field(None, description="Full text content")
    publication_year: Optional[int] = Field(None, ge=-3000, le=2100, description="Publication year (negative for BCE)")
    publisher: Optional[str] = Field(None, max_length=255)
    isbn_doi: Optional[str] = Field(None, max_length=100, description="ISBN or DOI")
    url: Optional[str] = Field(None, max_length=500, description="Online reference URL")
    page_reference: Optional[str] = Field(None, max_length=100, description="Page or chapter reference")
    language: str = Field("english", max_length=50)
    tags: Optional[List[str]] = Field(None, description="Topic tags")
    keywords: Optional[List[str]] = Field(None, description="Searchable keywords")
    is_public: bool = Field(True, description="Whether source is publicly visible")


class SourceUpdate(BaseModel):
    """Schema for updating an evidence source."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    author: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    excerpt: Optional[str] = None
    full_text: Optional[str] = None
    url: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    credibility_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_verified: Optional[bool] = None
    is_public: Optional[bool] = None


class SourceResponse(SourceBase):
    """Schema for evidence source response."""
    id: UUID
    full_text: Optional[str] = None
    publication_year: Optional[int] = None
    publisher: Optional[str] = None
    isbn_doi: Optional[str] = None
    url: Optional[str] = None
    page_reference: Optional[str] = None
    language: str
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    credibility_score: float
    citation_count: int
    is_verified: bool
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True


class SourceListResponse(BaseModel):
    """Schema for paginated source list."""
    sources: List[SourceResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# ============================================================================
# Citation Schemas
# ============================================================================

class CitationBase(BaseModel):
    """Base schema for citation."""
    insight_type: str = Field(..., max_length=100, description="Type of insight (yoga, planet, dasha)")
    insight_text: str = Field(..., min_length=1, description="The astrological insight")
    insight_reference: Optional[str] = Field(None, max_length=255, description="Reference ID")


class CitationCreate(CitationBase):
    """Schema for creating a new citation."""
    source_id: UUID = Field(..., description="ID of the evidence source")
    relevance_score: float = Field(0.5, ge=0.0, le=1.0, description="Relevance score")
    confidence_level: ConfidenceLevel = Field(ConfidenceLevel.MEDIUM)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    reasoning: Optional[str] = Field(None, description="Why this citation is relevant")


class CitationUpdate(BaseModel):
    """Schema for updating a citation."""
    insight_text: Optional[str] = None
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_level: Optional[ConfidenceLevel] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    context: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    is_active: Optional[bool] = None


class CitationResponse(CitationBase):
    """Schema for citation response."""
    id: UUID
    source_id: UUID
    relevance_score: float
    confidence_level: ConfidenceLevel
    confidence_score: Optional[float] = None
    context: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    view_count: int
    helpful_count: int
    not_helpful_count: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None

    # Include source details
    source: Optional[SourceResponse] = None

    # Include validation summary
    validation_count: Optional[int] = 0
    average_accuracy: Optional[float] = None

    class Config:
        from_attributes = True


class CitationWithSourceResponse(CitationResponse):
    """Citation response with full source details."""
    source: SourceResponse


class CitationListResponse(BaseModel):
    """Schema for paginated citation list."""
    citations: List[CitationResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# ============================================================================
# Validation Schemas
# ============================================================================

class ValidationBase(BaseModel):
    """Base schema for validation."""
    status: ValidationStatus = Field(..., description="Validation status")


class ValidationCreate(ValidationBase):
    """Schema for creating a new validation."""
    citation_id: UUID = Field(..., description="ID of the citation being validated")
    confidence_adjustment: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Confidence adjustment")
    comments: Optional[str] = Field(None, description="Validation comments")
    suggestions: Optional[str] = Field(None, description="Suggestions for improvement")
    alternative_sources: Optional[List[UUID]] = Field(None, description="Alternative source IDs")
    accuracy_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Accuracy rating")
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Relevance rating")


class ValidationUpdate(BaseModel):
    """Schema for updating a validation."""
    status: Optional[ValidationStatus] = None
    confidence_adjustment: Optional[float] = Field(None, ge=-1.0, le=1.0)
    comments: Optional[str] = None
    suggestions: Optional[str] = None
    accuracy_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_public: Optional[bool] = None


class ValidationResponse(ValidationBase):
    """Schema for validation response."""
    id: UUID
    citation_id: UUID
    validator_id: UUID
    validator_name: Optional[str] = None
    validator_credentials: Optional[str] = None
    confidence_adjustment: Optional[float] = None
    comments: Optional[str] = None
    suggestions: Optional[str] = None
    alternative_sources: Optional[List[UUID]] = None
    accuracy_score: Optional[float] = None
    relevance_score: Optional[float] = None
    is_public: bool
    requires_review: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ValidationListResponse(BaseModel):
    """Schema for paginated validation list."""
    validations: List[ValidationResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# ============================================================================
# Search and Query Schemas
# ============================================================================

class SourceSearchRequest(BaseModel):
    """Schema for searching sources."""
    query: Optional[str] = Field(None, description="Search query")
    source_type: Optional[SourceType] = None
    is_verified: Optional[bool] = None
    tags: Optional[List[str]] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class CitationSearchRequest(BaseModel):
    """Schema for searching citations."""
    insight_type: Optional[str] = None
    source_id: Optional[UUID] = None
    confidence_level: Optional[ConfidenceLevel] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_active: Optional[bool] = True
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class InsightVerificationRequest(BaseModel):
    """Schema for verifying an astrological insight."""
    insight_type: str = Field(..., max_length=100)
    insight_text: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None
    include_sources: bool = Field(True, description="Include full source details")


class InsightVerificationResponse(BaseModel):
    """Schema for insight verification response."""
    insight_type: str
    insight_text: str
    has_citations: bool
    citation_count: int
    average_confidence: Optional[float] = None
    highest_confidence: Optional[float] = None
    citations: List[CitationWithSourceResponse]
    suggested_sources: List[SourceResponse] = []

    class Config:
        from_attributes = True


# ============================================================================
# Feedback Schemas
# ============================================================================

class CitationFeedback(BaseModel):
    """Schema for citation feedback."""
    citation_id: UUID
    is_helpful: bool = Field(..., description="Whether the citation was helpful")


class ConfidenceScoreResponse(BaseModel):
    """Schema for confidence score calculation response."""
    insight_type: str
    base_confidence: float
    citation_count: int
    average_source_credibility: float
    validation_count: int
    average_validation_score: float
    final_confidence: float
    confidence_level: ConfidenceLevel
