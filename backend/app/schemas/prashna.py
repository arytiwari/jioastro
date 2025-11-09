"""
Pydantic schemas for Prashna (Horary Astrology) API.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class PrashnaRequest(BaseModel):
    """Request to analyze a horary question"""
    question: str
    question_type: str  # career, relationship, health, finance, education, legal, travel, property, children, spiritual, general
    datetime: datetime
    latitude: float
    longitude: float
    timezone: str


class SavePrashnaRequest(BaseModel):
    """Request to save a prashna analysis"""
    question: str
    question_type: str
    query_datetime: datetime
    latitude: float
    longitude: float
    timezone: str
    prashna_chart: Dict[str, Any]
    analysis: Dict[str, Any]
    notes: Optional[str] = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class PlanetPosition(BaseModel):
    """Planet position in Prashna chart"""
    name: str
    sign: str
    degree: float
    house: int
    is_retrograde: bool
    nakshatra: str
    nakshatra_pada: int


class HouseInfo(BaseModel):
    """House information in Prashna"""
    house_number: int
    sign: str
    lord: str
    lord_position: str
    lord_house: int
    significance: str
    strength: str


class MoonAnalysis(BaseModel):
    """Detailed Moon analysis for Prashna"""
    sign: str
    nakshatra: str
    pada: int
    degree: float
    house: int
    is_waxing: bool
    lunar_phase: str
    strength: str
    aspects_from: List[str]
    aspects_to: List[str]
    interpretation: str


class LagnaAnalysis(BaseModel):
    """Lagna (Ascendant) analysis"""
    sign: str
    degree: float
    lord: str
    lord_position: str
    lord_house: int
    lord_strength: str
    significance: str


class QuestionAnalysis(BaseModel):
    """Analysis specific to question type"""
    relevant_house: int
    house_lord: str
    house_lord_position: str
    house_lord_strength: str
    karaka_planet: str
    karaka_position: str
    karaka_strength: str
    supporting_factors: List[str]
    opposing_factors: List[str]


class PrashnaAnswer(BaseModel):
    """Final answer to the Prashna question"""
    outcome: str  # favorable, unfavorable, mixed, uncertain
    confidence: str  # high, medium, low
    timing: Optional[str]
    summary: str
    detailed_interpretation: str
    recommendations: List[str]
    precautions: List[str]


# ============================================================================
# AI-POWERED ANSWER SCHEMAS
# ============================================================================

class TimingPrediction(BaseModel):
    """AI-powered timing prediction"""
    timeframe: str = Field(..., description="Predicted timeframe (e.g., '2-3 months', '6-12 months')")
    basis: str = Field(..., description="Astrological reasoning for the timing")
    key_dates: str = Field(..., description="Specific periods or transits to watch")


class RemedyItem(BaseModel):
    """Individual Vedic remedy"""
    title: str = Field(..., description="Brief remedy name")
    description: str = Field(..., description="Detailed instructions for performing the remedy")


class AIAnswer(BaseModel):
    """AI-generated detailed answer for Prashna question"""
    answer: str = Field(..., description="Direct answer: Yes, No, Maybe, or Uncertain")
    explanation: str = Field(..., description="Detailed 500-800 word astrological explanation")
    timing: TimingPrediction
    obstacles: List[str] = Field(default_factory=list, description="Challenges to overcome")
    opportunities: List[str] = Field(default_factory=list, description="Favorable factors")
    remedies: List[RemedyItem] = Field(default_factory=list, description="Specific Vedic remedies")
    confidence: int = Field(..., ge=0, le=100, description="Confidence level (0-100)")
    confidence_explanation: str = Field(..., description="Explanation for confidence level")


class PrashnaChartResponse(BaseModel):
    """Complete Prashna chart response with optional AI analysis"""
    question: str
    question_type: str
    query_datetime: str
    location: Dict[str, float]

    # Chart data
    ascendant: LagnaAnalysis
    moon: MoonAnalysis
    planets: List[PlanetPosition]
    houses: List[HouseInfo]

    # Analysis
    question_analysis: QuestionAnalysis
    answer: PrashnaAnswer

    # Additional factors
    yogas_present: List[Dict[str, str]]
    planetary_strengths: Dict[str, str]
    overall_chart_strength: str

    # AI-powered answer (optional)
    ai_answer: Optional[AIAnswer] = None
    has_ai_analysis: bool = False


# ============================================================================
# SAVED PRASHNA SCHEMAS
# ============================================================================

class SavedPrashnaResponse(BaseModel):
    """Saved Prashna response"""
    id: UUID
    user_id: UUID
    question: str
    question_type: str
    query_datetime: datetime
    latitude: float
    longitude: float
    timezone: str
    prashna_chart: Dict[str, Any]
    analysis: Dict[str, Any]
    notes: Optional[str]
    created_at: datetime


class PrashnaListResponse(BaseModel):
    """List of saved Prashnas"""
    prashnas: List[SavedPrashnaResponse]
    total: int
    limit: int
    offset: int
