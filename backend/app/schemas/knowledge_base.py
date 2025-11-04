"""Knowledge Base Schemas - Rules and Retrieval"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID
from datetime import datetime


class RuleDomain(str, Enum):
    """Rule application domains"""
    CAREER = "career"
    HEALTH = "health"
    WEALTH = "wealth"
    RELATIONSHIPS = "relationships"
    EDUCATION = "education"
    PROPERTY = "property"
    TRAVEL = "travel"
    LITIGATION = "litigation"
    SPIRITUALITY = "spirituality"
    LONGEVITY = "longevity"
    GENERAL = "general"


class ChartContext(str, Enum):
    """Chart types for rule application"""
    NATAL = "natal"
    DASHA = "dasha"
    TRANSIT = "transit"
    VARGA = "varga"
    COMPOSITE = "composite"


class RuleScope(str, Enum):
    """Scope of astrological element"""
    HOUSE = "house"
    SIGN = "sign"
    PLANET = "planet"
    ASPECT = "aspect"
    YOGA = "yoga"
    COMPOSITE = "composite"


class RuleStatus(str, Enum):
    """Rule status for versioning"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class RuleCreate(BaseModel):
    """Schema for creating a new rule"""
    rule_id: str = Field(..., description="Unique rule identifier (e.g., BPHS-15-3)")
    source_id: UUID = Field(..., description="FK to kb_sources table")

    # Classification
    domain: RuleDomain = Field(..., description="Application domain")
    chart_context: ChartContext = Field(..., description="Chart type context")
    scope: RuleScope = Field(..., description="Astrological scope")

    # Rule content
    condition: str = Field(..., min_length=10, description="IF clause describing condition")
    effect: str = Field(..., min_length=10, description="THEN clause describing effect")
    modifiers: List[str] = Field(default_factory=list, description="Modifying factors")

    # Metadata
    weight: float = Field(default=0.5, ge=0.0, le=1.0, description="Rule importance")
    anchor: Optional[str] = Field(None, description="Source location (Chapter X, Verse Y)")
    sanskrit_text: Optional[str] = Field(None, description="Original Sanskrit text")
    translation: Optional[str] = Field(None, description="English translation")
    commentary: Optional[str] = Field(None, description="Explanatory commentary")

    # Application context
    applicable_vargas: List[str] = Field(default_factory=lambda: ["D1"], description="Applicable charts")
    requires_yoga: Optional[str] = Field(None, description="Prerequisite yoga")
    cancelers: List[str] = Field(default_factory=list, description="Rules that cancel this")

    # Versioning
    version: int = Field(default=1, ge=1, description="Rule version")
    status: RuleStatus = Field(default=RuleStatus.ACTIVE, description="Rule status")

    @validator('rule_id')
    def validate_rule_id(cls, v):
        """Validate rule_id format (SOURCE-CHAPTER-VERSE)"""
        parts = v.split('-')
        if len(parts) < 2:
            raise ValueError("rule_id must be in format SOURCE-CHAPTER-VERSE (e.g., BPHS-15-3)")
        return v

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "rule_id": "BPHS-24-12",
                "source_id": "uuid-here",
                "domain": "career",
                "chart_context": "natal",
                "scope": "house",
                "condition": "IF 10th lord in 4th house",
                "effect": "THEN gains through property, real estate, vehicles",
                "modifiers": ["strength", "dignity"],
                "weight": 0.7,
                "anchor": "Chapter 24, Verse 12",
                "applicable_vargas": ["D1"]
            }
        }


class RuleResponse(RuleCreate):
    """Response schema including database fields"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RuleWithEmbedding(RuleResponse):
    """Rule with embedding for internal use"""
    embedding: Optional[List[float]] = None
    symbolic_keys: List[str] = Field(default_factory=list)


class SymbolicKey(BaseModel):
    """Symbolic key for fast lookup"""
    rule_id: UUID
    key_type: str = Field(..., description="Type: planet_house, planet_sign, aspect, yoga")
    key_value: str = Field(..., description="Value: Sun_10, Mars_Aries, etc.")


class RuleRetrievalRequest(BaseModel):
    """Request for rule retrieval"""
    chart_data: Dict[str, Any] = Field(..., description="Birth chart data")
    query: Optional[str] = Field(None, description="Natural language query")
    domain: Optional[RuleDomain] = Field(None, description="Filter by domain")
    chart_context: Optional[ChartContext] = Field(None, description="Filter by chart context")
    limit: int = Field(default=10, ge=1, le=50, description="Max results")
    min_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum rule weight")

    class Config:
        schema_extra = {
            "example": {
                "chart_data": {
                    "ascendant": {"sign": "Pisces"},
                    "planets": {
                        "Sun": {"sign": "Capricorn", "house": 11},
                        "Moon": {"sign": "Leo", "house": 6}
                    }
                },
                "query": "career prospects and professional success",
                "domain": "career",
                "limit": 10
            }
        }


class RuleRetrievalResponse(BaseModel):
    """Response from rule retrieval"""
    rules: List[RuleResponse]
    retrieval_method: str = Field(..., description="symbolic, semantic, or hybrid")
    total_matches: int
    query_time_ms: float

    class Config:
        schema_extra = {
            "example": {
                "rules": [],
                "retrieval_method": "hybrid",
                "total_matches": 5,
                "query_time_ms": 45.2
            }
        }


class RuleIngestionBatch(BaseModel):
    """Batch ingestion request"""
    rules: List[RuleCreate]
    generate_embeddings: bool = Field(default=True, description="Generate embeddings immediately")
    extract_symbolic_keys: bool = Field(default=True, description="Extract symbolic keys immediately")

    @validator('rules')
    def validate_batch_size(cls, v):
        """Limit batch size"""
        if len(v) > 100:
            raise ValueError("Maximum 100 rules per batch")
        if len(v) == 0:
            raise ValueError("At least one rule required")
        return v


class RuleIngestionResponse(BaseModel):
    """Response from batch ingestion"""
    ingested_count: int
    rule_ids: List[UUID]
    embeddings_generated: int
    symbolic_keys_generated: int
    errors: List[str] = Field(default_factory=list)
    duration_seconds: float

    class Config:
        schema_extra = {
            "example": {
                "ingested_count": 50,
                "rule_ids": ["uuid1", "uuid2"],
                "embeddings_generated": 50,
                "symbolic_keys_generated": 150,
                "errors": [],
                "duration_seconds": 12.5
            }
        }


class RuleFeedback(BaseModel):
    """User feedback on rule application"""
    rule_id: UUID
    reading_session_id: UUID
    feedback: str = Field(..., pattern="^(confirmed|contradicted|partial|unknown)$")
    anchor_event_id: Optional[UUID] = None
    notes: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "rule_id": "uuid-here",
                "reading_session_id": "uuid-here",
                "feedback": "confirmed",
                "notes": "Got promotion exactly as predicted"
            }
        }
