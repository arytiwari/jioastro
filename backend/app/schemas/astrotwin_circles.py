"""
Pydantic schemas for AstroTwin Circles feature
Community discovery and pattern analysis based on chart similarity
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# Enums

class CircleType(str, Enum):
    """Type of AstroTwin circle"""
    FAMILY = "family"
    LIFE_STAGE = "life_stage"
    GOAL = "goal"
    BUSINESS = "business"
    LOCATION = "location"
    CUSTOM = "custom"


class MemberRole(str, Enum):
    """Role within a circle"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"


class JoinStatus(str, Enum):
    """Membership status"""
    PENDING = "pending"
    ACTIVE = "active"
    LEFT = "left"
    REMOVED = "removed"


class OutcomeType(str, Enum):
    """Type of life outcome"""
    JOB_CHANGE = "job_change"
    PROMOTION = "promotion"
    BUSINESS_LAUNCH = "business_launch"
    MARRIAGE = "marriage"
    CHILDBIRTH = "childbirth"
    PROPERTY_PURCHASE = "property_purchase"
    MAJOR_INVESTMENT = "major_investment"
    EDUCATION_MILESTONE = "education_milestone"
    HEALTH_RECOVERY = "health_recovery"
    RELATIONSHIP_BREAKUP = "relationship_breakup"
    FINANCIAL_LOSS = "financial_loss"
    OTHER = "other"


class OutcomeResult(str, Enum):
    """Result of life outcome"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    NEUTRAL = "neutral"


class InsightType(str, Enum):
    """Type of circle insight"""
    SUCCESS_PATTERN = "success_pattern"
    TIMING_INSIGHT = "timing_insight"
    COMMON_CHALLENGE = "common_challenge"
    RECOMMENDED_REMEDY = "recommended_remedy"
    SHARED_EXPERIENCE = "shared_experience"


class PostType(str, Enum):
    """Type of circle post"""
    TEXT = "text"
    QUESTION = "question"
    SUCCESS_STORY = "success_story"
    REMEDY_SHARE = "remedy_share"


# Request Schemas

class EnableDiscoveryRequest(BaseModel):
    """Enable AstroTwin discovery for user"""
    privacy_opt_in: bool = True
    visible_in_search: bool = True
    allow_pattern_learning: bool = False


class CreateCircleRequest(BaseModel):
    """Create a new AstroTwin circle"""
    circle_name: str = Field(..., min_length=3, max_length=100)
    circle_description: Optional[str] = Field(None, max_length=500)
    circle_type: CircleType
    is_private: bool = True
    requires_approval: bool = True
    max_members: int = Field(50, ge=2, le=500)
    similarity_threshold: Optional[Decimal] = Field(None, ge=0.0, le=1.0, description="For auto-suggested circles")
    feature_filters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class UpdateCircleRequest(BaseModel):
    """Update circle settings"""
    circle_name: Optional[str] = Field(None, min_length=3, max_length=100)
    circle_description: Optional[str] = Field(None, max_length=500)
    is_private: Optional[bool] = None
    requires_approval: Optional[bool] = None
    max_members: Optional[int] = Field(None, ge=2, le=500)
    tags: Optional[List[str]] = None


class JoinCircleRequest(BaseModel):
    """Request to join a circle"""
    circle_id: str
    share_outcomes: bool = False


class UpdateMembershipRequest(BaseModel):
    """Update membership settings"""
    role: Optional[MemberRole] = None
    join_status: Optional[JoinStatus] = None
    shared_outcomes: Optional[bool] = None


class ReportOutcomeRequest(BaseModel):
    """Report a life outcome"""
    outcome_type: OutcomeType
    outcome_title: str = Field(..., min_length=5, max_length=200)
    outcome_date: date
    outcome_result: OutcomeResult
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_notes: Optional[str] = Field(None, max_length=1000)
    share_anonymously: bool = False

    # Optional context (auto-filled if not provided)
    dasha_context: Optional[Dict[str, Any]] = None
    transit_context: Optional[Dict[str, Any]] = None
    chart_factors: Optional[Dict[str, Any]] = None


class FindTwinsRequest(BaseModel):
    """Search for AstroTwins"""
    similarity_threshold: Decimal = Field(0.3, ge=0.0, le=1.0, description="Max distance (0=identical, 1=different)")
    limit: int = Field(100, ge=1, le=500)
    filter_by: Optional[Dict[str, Any]] = None  # e.g., {"life_stage": "30-40", "saturn_phase": "Sade Sati"}


class CreatePostRequest(BaseModel):
    """Create a circle post"""
    circle_id: str
    post_type: PostType = PostType.TEXT
    post_title: Optional[str] = Field(None, max_length=200)
    post_content: str = Field(..., min_length=10, max_length=5000)


class CreateReplyRequest(BaseModel):
    """Reply to a circle post"""
    post_id: str
    reply_content: str = Field(..., min_length=5, max_length=2000)


# Response Schemas

class ChartVectorMetadata(BaseModel):
    """Feature metadata explaining what went into the vector"""
    sun_sign: Optional[str] = None
    moon_sign: Optional[str] = None
    ascendant: Optional[str] = None
    dominant_planets: List[str] = Field(default_factory=list)
    major_yogas: List[str] = Field(default_factory=list)
    current_dasha_md: Optional[str] = None
    current_dasha_ad: Optional[str] = None
    saturn_phase: Optional[str] = None
    life_stage: Optional[str] = None
    gender: Optional[str] = None
    location_region: Optional[str] = None


class ChartVector(BaseModel):
    """Chart vector representation"""
    id: str
    profile_id: str
    user_id: str
    feature_metadata: ChartVectorMetadata
    privacy_opt_in: bool
    visible_in_search: bool
    allow_pattern_learning: bool
    vectorization_version: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AstroTwinMatch(BaseModel):
    """An AstroTwin match result"""
    profile_id: str
    similarity_score: Decimal = Field(..., description="0.0 to 1.0, higher is more similar")
    feature_metadata: ChartVectorMetadata
    shared_features: List[str] = Field(default_factory=list, description="What makes you twins")

    class Config:
        from_attributes = True


class AstroTwinMatchListResponse(BaseModel):
    """List of AstroTwin matches"""
    matches: List[AstroTwinMatch]
    total_count: int
    your_features: ChartVectorMetadata


class CircleMemberBrief(BaseModel):
    """Brief member info for circle listing"""
    user_id: str
    role: MemberRole
    joined_at: datetime

    class Config:
        from_attributes = True


class AstroTwinCircle(BaseModel):
    """AstroTwin circle details"""
    id: str
    circle_name: str
    circle_description: Optional[str] = None
    circle_type: CircleType
    creator_user_id: str
    is_private: bool
    requires_approval: bool
    max_members: int
    member_count: int
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    # Optional: Include if user is a member
    user_role: Optional[MemberRole] = None
    user_join_status: Optional[JoinStatus] = None

    class Config:
        from_attributes = True


class AstroTwinCircleListResponse(BaseModel):
    """List of circles"""
    circles: List[AstroTwinCircle]
    total_count: int


class CircleMembership(BaseModel):
    """Circle membership details"""
    id: str
    circle_id: str
    user_id: str
    profile_id: Optional[str] = None
    role: MemberRole
    join_status: JoinStatus
    shared_outcomes: bool
    joined_at: datetime
    left_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CircleMembershipListResponse(BaseModel):
    """List of memberships"""
    memberships: List[CircleMembership]
    total_count: int


class LifeOutcome(BaseModel):
    """Life outcome details"""
    id: str
    user_id: str
    profile_id: Optional[str] = None
    outcome_type: OutcomeType
    outcome_title: str
    outcome_date: date
    outcome_result: OutcomeResult
    dasha_context: Optional[Dict[str, Any]] = None
    transit_context: Optional[Dict[str, Any]] = None
    chart_factors: Optional[Dict[str, Any]] = None
    user_rating: Optional[int] = None
    user_notes: Optional[str] = None
    share_anonymously: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LifeOutcomeListResponse(BaseModel):
    """List of life outcomes"""
    outcomes: List[LifeOutcome]
    total_count: int


class PatternDiscovery(BaseModel):
    """Discovered pattern from data"""
    id: str
    pattern_type: str
    pattern_name: str
    pattern_description: str
    chart_conditions: Dict[str, Any]
    sample_size: int
    correlation_score: Decimal
    confidence_level: Decimal
    success_rate: Decimal
    timing_insights: Optional[Dict[str, Any]] = None
    recommendations: List[str] = Field(default_factory=list)
    discovered_at: datetime
    last_updated: datetime
    is_active: bool

    class Config:
        from_attributes = True


class PatternDiscoveryListResponse(BaseModel):
    """List of discovered patterns"""
    patterns: List[PatternDiscovery]
    total_count: int
    matching_user_chart: bool = Field(False, description="Does user's chart match any of these patterns?")


class CircleInsight(BaseModel):
    """Insight shared within a circle"""
    id: str
    circle_id: str
    pattern_id: Optional[str] = None
    insight_type: InsightType
    insight_title: str
    insight_description: str
    member_count_matching: Optional[int] = None
    success_stories: Optional[Dict[str, Any]] = None
    upvotes: int
    created_at: datetime

    class Config:
        from_attributes = True


class CircleInsightListResponse(BaseModel):
    """List of circle insights"""
    insights: List[CircleInsight]
    total_count: int


class CirclePost(BaseModel):
    """Circle post"""
    id: str
    circle_id: str
    user_id: str
    post_type: PostType
    post_title: Optional[str] = None
    post_content: str
    upvotes: int
    reply_count: int
    is_pinned: bool
    is_hidden: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CirclePostListResponse(BaseModel):
    """List of circle posts"""
    posts: List[CirclePost]
    total_count: int


class CirclePostReply(BaseModel):
    """Reply to a circle post"""
    id: str
    post_id: str
    user_id: str
    reply_content: str
    upvotes: int
    created_at: datetime

    class Config:
        from_attributes = True


class CirclePostReplyListResponse(BaseModel):
    """List of post replies"""
    replies: List[CirclePostReply]
    total_count: int


# Analytics

class AstroTwinStats(BaseModel):
    """User's AstroTwin statistics"""
    total_twins_found: int
    circles_joined: int
    outcomes_reported: int
    patterns_matched: int
    discovery_enabled: bool
    most_similar_twin_score: Optional[Decimal] = None


class CircleStats(BaseModel):
    """Circle statistics"""
    circle_id: str
    member_count: int
    active_members_last_30_days: int
    total_posts: int
    total_insights: int
    average_similarity_score: Optional[Decimal] = None
    top_shared_features: List[str] = Field(default_factory=list)
