"""
Pydantic schemas for Reality Check Loop
Learning from prediction outcomes
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# =====================================================
# ENUMS
# =====================================================

class PredictionType(str, Enum):
    """Types of predictions"""
    DASHA_PREDICTION = "dasha_prediction"
    TRANSIT_PREDICTION = "transit_prediction"
    COMPATIBILITY = "compatibility"
    CAREER = "career"
    HEALTH = "health"
    RELATIONSHIPS = "relationships"
    FINANCES = "finances"
    SPIRITUAL = "spiritual"
    GENERAL = "general"


class PredictionCategory(str, Enum):
    """Categories for predictions"""
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    HEALTH = "health"
    FINANCES = "finances"
    SPIRITUAL = "spiritual"
    GENERAL = "general"


class SourceType(str, Enum):
    """Source of the prediction"""
    AI_QUERY = "ai_query"
    READING = "reading"
    CHART_ANALYSIS = "chart_analysis"
    DASHA_PERIOD = "dasha_period"
    TRANSIT = "transit"
    YOGA_DETECTION = "yoga_detection"


class ConfidenceLevel(str, Enum):
    """Confidence level for predictions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PredictionStatus(str, Enum):
    """Status of a prediction"""
    ACTIVE = "active"
    PENDING_OUTCOME = "pending_outcome"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TimingAccuracy(str, Enum):
    """How accurate was the timing"""
    EARLY = "early"
    ON_TIME = "on_time"
    LATE = "late"
    SIGNIFICANTLY_LATE = "significantly_late"


class SeverityMatch(str, Enum):
    """How well did severity match"""
    UNDERSTATED = "understated"
    ACCURATE = "accurate"
    OVERSTATED = "overstated"


class InsightType(str, Enum):
    """Type of learning insight"""
    PATTERN = "pattern"
    CORRELATION = "correlation"
    WEAKNESS = "weakness"
    STRENGTH = "strength"
    IMPROVEMENT = "improvement"


class ImpactLevel(str, Enum):
    """Impact level of an insight"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MetricScope(str, Enum):
    """Scope of metrics"""
    USER = "user"
    CATEGORY = "category"
    TYPE = "type"
    GLOBAL = "global"
    ASTROLOGER = "astrologer"


class TrendDirection(str, Enum):
    """Trend direction for metrics"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


class ReminderType(str, Enum):
    """Type of reminder"""
    TIMEFRAME_APPROACHING = "timeframe_approaching"
    TIMEFRAME_REACHED = "timeframe_reached"
    TIMEFRAME_PASSED = "timeframe_passed"
    FOLLOWUP = "followup"


# =====================================================
# REQUEST SCHEMAS
# =====================================================

class CreatePrediction(BaseModel):
    """Create a new prediction"""
    profile_id: Optional[str] = None
    prediction_type: PredictionType
    prediction_category: PredictionCategory
    source_type: SourceType
    source_id: Optional[str] = None
    prediction_text: str = Field(..., min_length=10, max_length=2000)
    prediction_summary: Optional[str] = Field(None, max_length=200)
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    expected_timeframe_start: Optional[str] = Field(None, description="Date (YYYY-MM-DD)")
    expected_timeframe_end: Optional[str] = Field(None, description="Date (YYYY-MM-DD)")
    timeframe_description: Optional[str] = Field(None, max_length=200)
    astrological_context: Optional[Dict[str, Any]] = None
    key_factors: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[str] = None


class UpdatePrediction(BaseModel):
    """Update an existing prediction"""
    prediction_text: Optional[str] = Field(None, min_length=10, max_length=2000)
    prediction_summary: Optional[str] = Field(None, max_length=200)
    confidence_level: Optional[ConfidenceLevel] = None
    expected_timeframe_start: Optional[str] = Field(None, description="Date (YYYY-MM-DD)")
    expected_timeframe_end: Optional[str] = Field(None, description="Date (YYYY-MM-DD)")
    timeframe_description: Optional[str] = Field(None, max_length=200)
    status: Optional[PredictionStatus] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class CreateOutcome(BaseModel):
    """Record an outcome for a prediction"""
    prediction_id: str
    outcome_occurred: bool
    actual_date: Optional[str] = Field(None, description="Date when outcome occurred (YYYY-MM-DD)")
    outcome_description: str = Field(..., min_length=10, max_length=2000)
    timing_accuracy: Optional[TimingAccuracy] = None
    severity_match: Optional[SeverityMatch] = None
    what_matched: Optional[str] = Field(None, max_length=1000)
    what_differed: Optional[str] = Field(None, max_length=1000)
    additional_events: Optional[str] = Field(None, max_length=1000)
    helpfulness_rating: int = Field(..., ge=1, le=5)
    would_trust_again: bool

    @validator('timing_accuracy')
    def timing_required_if_occurred(cls, v, values):
        if values.get('outcome_occurred') and not v:
            raise ValueError('timing_accuracy is required when outcome occurred')
        return v

    @validator('severity_match')
    def severity_required_if_occurred(cls, v, values):
        if values.get('outcome_occurred') and not v:
            raise ValueError('severity_match is required when outcome occurred')
        return v


class UpdateOutcome(BaseModel):
    """Update an existing outcome"""
    outcome_occurred: Optional[bool] = None
    actual_date: Optional[str] = Field(None, description="Date (YYYY-MM-DD)")
    outcome_description: Optional[str] = Field(None, min_length=10, max_length=2000)
    timing_accuracy: Optional[TimingAccuracy] = None
    severity_match: Optional[SeverityMatch] = None
    what_matched: Optional[str] = Field(None, max_length=1000)
    what_differed: Optional[str] = Field(None, max_length=1000)
    additional_events: Optional[str] = Field(None, max_length=1000)
    helpfulness_rating: Optional[int] = Field(None, ge=1, le=5)
    would_trust_again: Optional[bool] = None


class CreateLearningInsight(BaseModel):
    """Create a learning insight (admin/system only)"""
    insight_type: InsightType
    category: PredictionCategory
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=20, max_length=2000)
    sample_size: int = Field(..., ge=1)
    accuracy_rate: Optional[float] = Field(None, ge=0, le=100)
    confidence_interval: Optional[float] = Field(None, ge=0, le=100)
    astrological_factors: Optional[Dict[str, Any]] = None
    successful_patterns: Optional[Dict[str, Any]] = None
    failure_patterns: Optional[Dict[str, Any]] = None
    impact_level: ImpactLevel = ImpactLevel.MEDIUM
    actionable_recommendations: Optional[List[str]] = Field(default_factory=list)


# =====================================================
# RESPONSE SCHEMAS
# =====================================================

class Prediction(BaseModel):
    """Prediction response"""
    id: str
    user_id: str
    profile_id: Optional[str]
    prediction_type: str
    prediction_category: str
    source_type: str
    source_id: Optional[str]
    prediction_text: str
    prediction_summary: Optional[str]
    confidence_level: str
    prediction_date: datetime
    expected_timeframe_start: Optional[str]
    expected_timeframe_end: Optional[str]
    timeframe_description: Optional[str]
    astrological_context: Optional[Dict[str, Any]]
    key_factors: Optional[Dict[str, Any]]
    status: str
    reminder_sent: bool
    tags: Optional[List[str]]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PredictionWithOutcome(Prediction):
    """Prediction with its outcome (if any)"""
    outcome: Optional['PredictionOutcome'] = None


class PredictionList(BaseModel):
    """List of predictions with pagination"""
    predictions: List[Prediction]
    total_count: int
    has_outcomes: int
    pending_outcomes: int


class PredictionOutcome(BaseModel):
    """Prediction outcome response"""
    id: str
    prediction_id: str
    user_id: str
    outcome_occurred: bool
    actual_date: Optional[str]
    outcome_description: str
    accuracy_score: Optional[int]
    timing_accuracy: Optional[str]
    severity_match: Optional[str]
    what_matched: Optional[str]
    what_differed: Optional[str]
    additional_events: Optional[str]
    helpfulness_rating: int
    would_trust_again: bool
    verified: bool
    verification_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningInsight(BaseModel):
    """Learning insight response"""
    id: str
    insight_type: str
    category: str
    title: str
    description: str
    sample_size: int
    accuracy_rate: Optional[float]
    confidence_interval: Optional[float]
    astrological_factors: Optional[Dict[str, Any]]
    successful_patterns: Optional[Dict[str, Any]]
    failure_patterns: Optional[Dict[str, Any]]
    impact_level: str
    actionable_recommendations: List[str]
    applied: bool
    applied_at: Optional[datetime]
    effectiveness_score: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningInsightList(BaseModel):
    """List of learning insights"""
    insights: List[LearningInsight]
    total_count: int


class AccuracyMetrics(BaseModel):
    """Accuracy metrics response"""
    id: str
    user_id: Optional[str]
    metric_scope: str
    scope_value: Optional[str]
    period_start: str
    period_end: str
    total_predictions: int
    verified_predictions: int
    accurate_predictions: int
    overall_accuracy_rate: Optional[float]
    timing_accuracy_rate: Optional[float]
    severity_accuracy_rate: Optional[float]
    low_confidence_accuracy: Optional[float]
    medium_confidence_accuracy: Optional[float]
    high_confidence_accuracy: Optional[float]
    very_high_confidence_accuracy: Optional[float]
    avg_helpfulness_rating: Optional[float]
    trust_rate: Optional[float]
    category_breakdown: Optional[Dict[str, Any]]
    type_breakdown: Optional[Dict[str, Any]]
    trend_direction: Optional[str]
    trend_percentage: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserAccuracyStats(BaseModel):
    """User's accuracy statistics"""
    total_predictions: int
    verified_predictions: int
    pending_predictions: int
    overall_accuracy_rate: Optional[float]
    avg_helpfulness_rating: Optional[float]
    trust_rate: Optional[float]
    best_category: Optional[str]
    best_category_accuracy: Optional[float]
    worst_category: Optional[str]
    worst_category_accuracy: Optional[float]
    recent_trend: Optional[str]
    category_breakdown: Dict[str, Dict[str, Any]]


class PredictionReminder(BaseModel):
    """Prediction reminder response"""
    id: str
    prediction_id: str
    user_id: str
    reminder_type: str
    sent_at: datetime
    opened: bool
    opened_at: Optional[datetime]
    responded: bool
    responded_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# FILTER SCHEMAS
# =====================================================

class PredictionFilters(BaseModel):
    """Filters for querying predictions"""
    status: Optional[PredictionStatus] = None
    category: Optional[PredictionCategory] = None
    prediction_type: Optional[PredictionType] = None
    confidence_level: Optional[ConfidenceLevel] = None
    profile_id: Optional[str] = None
    has_outcome: Optional[bool] = None
    timeframe_active: Optional[bool] = None  # Currently within timeframe
    timeframe_passed: Optional[bool] = None  # Timeframe has passed
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class OutcomeFilters(BaseModel):
    """Filters for querying outcomes"""
    outcome_occurred: Optional[bool] = None
    min_accuracy_score: Optional[int] = Field(None, ge=0, le=100)
    verified_only: Optional[bool] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


# =====================================================
# STATISTICS SCHEMAS
# =====================================================

class CategoryAccuracy(BaseModel):
    """Accuracy for a specific category"""
    category: str
    total_predictions: int
    verified_predictions: int
    accuracy_rate: Optional[float]
    avg_helpfulness: Optional[float]


class ConfidenceCalibration(BaseModel):
    """Confidence calibration stats"""
    confidence_level: str
    total_predictions: int
    verified_predictions: int
    accuracy_rate: Optional[float]
    expected_accuracy: float  # What the confidence level implies
    calibration_gap: Optional[float]  # Difference between expected and actual


class MonthlyTrend(BaseModel):
    """Monthly prediction trends"""
    month: str
    total_predictions: int
    verified_predictions: int
    accuracy_rate: Optional[float]


class RealityCheckDashboard(BaseModel):
    """Complete dashboard data"""
    user_stats: UserAccuracyStats
    recent_predictions: List[Prediction]
    pending_outcomes: List[Prediction]
    category_accuracy: List[CategoryAccuracy]
    confidence_calibration: List[ConfidenceCalibration]
    monthly_trends: List[MonthlyTrend]
    top_insights: List[LearningInsight]


# Update forward references
PredictionWithOutcome.model_rebuild()
