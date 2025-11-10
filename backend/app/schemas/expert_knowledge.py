"""Expert Knowledge System Schemas"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


# ============================================================================
# Enums
# ============================================================================

class ContributionType(str, Enum):
    """Types of expert contributions"""
    ADDITIVE = "additive"  # New knowledge/rules
    INCREMENTAL = "incremental"  # Refinements to existing rules
    UPDATE = "update"  # Corrections/bug fixes


class ContributionCategory(str, Enum):
    """Knowledge categories"""
    YOGA = "yoga"  # Planetary combinations
    DASHA = "dasha"  # Planetary periods
    TRANSIT = "transit"  # Gochar effects
    HOUSE = "house"  # Bhava significations
    PLANET = "planet"  # Graha characteristics
    ASPECT = "aspect"  # Drishti
    VARGA = "varga"  # Divisional charts
    REMEDY = "remedy"  # Remedial measures


class ContributionStatus(str, Enum):
    """Contribution workflow states"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"


class Priority(str, Enum):
    """Priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class CommentType(str, Enum):
    """Comment types"""
    GENERAL = "general"
    QUESTION = "question"
    SUGGESTION = "suggestion"
    CONCERN = "concern"
    SUPPORT = "support"


# ============================================================================
# Base Schemas
# ============================================================================

class ContributionBase(BaseModel):
    """Base schema for contributions"""
    contribution_type: ContributionType = Field(..., description="Type of contribution")
    category: ContributionCategory = Field(..., description="Knowledge category")
    subcategory: Optional[str] = Field(None, max_length=100, description="Specific topic")

    title: str = Field(..., min_length=1, max_length=200, description="Contribution title")
    description: str = Field(..., min_length=10, description="Detailed description")

    rule_definition: Optional[str] = Field(None, description="Formal rule description")
    example_charts: Optional[str] = Field(None, description="Birth chart examples")
    expected_impact: Optional[str] = Field(None, description="Expected effect on predictions")

    algorithm_changes: Optional[str] = Field(None, description="Code/algorithm changes")
    affected_modules: Optional[List[str]] = Field(None, description="Python modules affected")
    test_cases: Optional[Dict[str, Any]] = Field(None, description="Test cases")

    classical_reference: Optional[str] = Field(None, description="Classical text reference")
    modern_reference: Optional[str] = Field(None, description="Modern work reference")
    research_data: Optional[Dict[str, Any]] = Field(None, description="Statistical data")

    priority: Priority = Field(default=Priority.NORMAL, description="Priority level")
    confidence_level: Optional[int] = Field(None, ge=1, le=10, description="Confidence (1-10)")

    @validator('confidence_level')
    def validate_confidence(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Confidence level must be between 1 and 10')
        return v


# ============================================================================
# Request Schemas
# ============================================================================

class ContributionCreate(ContributionBase):
    """Schema for creating a new contribution"""
    pass


class ContributionUpdate(BaseModel):
    """Schema for updating a contribution (partial update)"""
    contribution_type: Optional[ContributionType] = None
    category: Optional[ContributionCategory] = None
    subcategory: Optional[str] = None

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10)

    rule_definition: Optional[str] = None
    example_charts: Optional[str] = None
    expected_impact: Optional[str] = None

    algorithm_changes: Optional[str] = None
    affected_modules: Optional[List[str]] = None
    test_cases: Optional[Dict[str, Any]] = None

    classical_reference: Optional[str] = None
    modern_reference: Optional[str] = None
    research_data: Optional[Dict[str, Any]] = None

    priority: Optional[Priority] = None
    confidence_level: Optional[int] = Field(None, ge=1, le=10)


class ContributionReview(BaseModel):
    """Schema for reviewing a contribution"""
    review_notes: str = Field(..., min_length=10, description="Review comments")
    approved: bool = Field(..., description="Approve or reject")


class ContributionImplementation(BaseModel):
    """Schema for marking contribution as implemented"""
    implementation_notes: str = Field(..., min_length=10, description="Implementation details")
    git_commit_hash: Optional[str] = Field(None, max_length=40, description="Git commit SHA")


# ============================================================================
# Response Schemas
# ============================================================================

class ContributionResponse(ContributionBase):
    """Schema for contribution response"""
    id: int
    expert_id: UUID

    status: ContributionStatus
    version: int
    replaces_contribution_id: Optional[int] = None

    # Review info
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None

    # Implementation info
    implemented_by: Optional[UUID] = None
    implemented_at: Optional[datetime] = None
    implementation_notes: Optional[str] = None
    git_commit_hash: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Additional stats (from view)
    upvotes: Optional[int] = 0
    downvotes: Optional[int] = 0
    net_votes: Optional[int] = 0
    comment_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ContributionListResponse(BaseModel):
    """Paginated list of contributions"""
    contributions: List[ContributionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Comment Schemas
# ============================================================================

class CommentCreate(BaseModel):
    """Schema for creating a comment"""
    comment: str = Field(..., min_length=1, description="Comment text")
    comment_type: CommentType = Field(default=CommentType.GENERAL, description="Comment type")


class CommentResponse(BaseModel):
    """Schema for comment response"""
    id: int
    contribution_id: int
    user_id: UUID
    comment: str
    comment_type: CommentType
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Vote Schemas
# ============================================================================

class VoteCreate(BaseModel):
    """Schema for creating a vote"""
    vote: int = Field(..., description="Vote: 1 for upvote, -1 for downvote")
    rationale: Optional[str] = Field(None, description="Reason for vote")

    @validator('vote')
    def validate_vote(cls, v):
        if v not in [-1, 1]:
            raise ValueError('Vote must be either 1 (upvote) or -1 (downvote)')
        return v


class VoteResponse(BaseModel):
    """Schema for vote response"""
    id: int
    contribution_id: int
    user_id: UUID
    vote: int
    rationale: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Impact Tracking Schemas
# ============================================================================

class ImpactCreate(BaseModel):
    """Schema for creating impact record"""
    chart_id: Optional[UUID] = Field(None, description="Chart ID if specific")
    prediction_before: Dict[str, Any] = Field(..., description="Prediction before contribution")
    prediction_after: Dict[str, Any] = Field(..., description="Prediction after contribution")
    accuracy_improvement: float = Field(..., description="Accuracy improvement percentage")
    user_feedback: Optional[str] = Field(None, description="User feedback")


class ImpactResponse(BaseModel):
    """Schema for impact response"""
    id: int
    contribution_id: int
    chart_id: Optional[UUID]
    prediction_before: Dict[str, Any]
    prediction_after: Dict[str, Any]
    accuracy_improvement: float
    user_feedback: Optional[str]
    validated: bool
    validated_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Statistics & Leaderboard Schemas
# ============================================================================

class ContributionStats(BaseModel):
    """Overall contribution statistics"""
    total_contributions: int
    pending_contributions: int
    under_review_contributions: int
    approved_contributions: int
    implemented_contributions: int
    rejected_contributions: int

    total_upvotes: int
    total_downvotes: int

    avg_accuracy_improvement: float
    total_validated_impacts: int


class ExpertProfile(BaseModel):
    """Expert profile with stats"""
    expert_id: UUID
    email: str

    total_contributions: int
    approved_contributions: int
    implemented_contributions: int
    rejected_contributions: int

    total_votes: int
    avg_impact: float
    approval_rate_percentage: float

    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    experts: List[ExpertProfile]
    page: int
    page_size: int
    total: int


# ============================================================================
# Filter/Query Parameters
# ============================================================================

class ContributionFilters(BaseModel):
    """Filters for querying contributions"""
    status: Optional[ContributionStatus] = None
    category: Optional[ContributionCategory] = None
    contribution_type: Optional[ContributionType] = None
    priority: Optional[Priority] = None
    expert_id: Optional[UUID] = None

    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    # Sorting
    sort_by: Optional[str] = Field(default="created_at", description="Field to sort by")
    sort_order: Optional[str] = Field(default="desc", description="asc or desc")


# ============================================================================
# Bulk Operations
# ============================================================================

class BulkApproveRequest(BaseModel):
    """Request to approve multiple contributions"""
    contribution_ids: List[int] = Field(..., min_items=1, description="IDs to approve")
    review_notes: str = Field(..., min_length=10, description="Bulk approval notes")


class BulkRejectRequest(BaseModel):
    """Request to reject multiple contributions"""
    contribution_ids: List[int] = Field(..., min_items=1, description="IDs to reject")
    review_notes: str = Field(..., min_length=10, description="Rejection reason")


class BulkOperationResponse(BaseModel):
    """Response for bulk operations"""
    success: List[int]
    failed: List[Dict[str, Any]]
    total_processed: int
