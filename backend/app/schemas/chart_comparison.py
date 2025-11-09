"""
Pydantic schemas for Chart Comparison API.
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class ChartComparisonRequest(BaseModel):
    """Request to compare two birth charts"""
    profile_id_1: str
    profile_id_2: str
    comparison_type: str = "general"  # general, romantic, business, family


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class PlanetAspect(BaseModel):
    """Aspect between two planets"""
    planet_1: str
    planet_2: str
    aspect_type: str  # conjunction, opposition, trine, square, sextile
    aspect_angle: float
    orb: float
    strength: str  # strong, moderate, weak
    interpretation: str
    is_harmonious: bool


class HouseOverlay(BaseModel):
    """One person's planet in another's house"""
    planet: str
    planet_owner: str  # person1 or person2
    falls_in_house: int
    house_owner: str  # person1 or person2
    significance: str
    interpretation: str


class CompatibilityFactor(BaseModel):
    """Individual compatibility factor"""
    factor_name: str
    description: str
    score: float  # 0-100
    is_positive: bool


class ProfileSummary(BaseModel):
    """Brief profile summary for comparison"""
    profile_id: str
    name: str
    ascendant: str
    moon_sign: str
    sun_sign: str


class ComparisonSummary(BaseModel):
    """Overall comparison summary"""
    overall_score: float  # 0-100
    compatibility_level: str  # excellent, good, moderate, challenging, difficult
    strengths: List[str]
    challenges: List[str]
    advice: List[str]


class ChartComparisonResponse(BaseModel):
    """Complete chart comparison response"""
    comparison_type: str
    profile_1: ProfileSummary
    profile_2: ProfileSummary

    # Aspects
    inter_chart_aspects: List[PlanetAspect]
    harmonious_aspects_count: int
    challenging_aspects_count: int

    # House overlays
    house_overlays: List[HouseOverlay]

    # Compatibility factors
    compatibility_factors: List[CompatibilityFactor]

    # Overall summary
    summary: ComparisonSummary

    # Detailed analysis
    detailed_interpretation: str


# ============================================================================
# SYNASTRY SCHEMAS
# ============================================================================

class SynastryRequest(BaseModel):
    """Request for dedicated synastry analysis"""
    profile_id_1: str
    profile_id_2: str
    focus: str = "romantic"  # romantic, business, friendship, family


class DetailedAspectInterpretation(BaseModel):
    """Detailed interpretation of a single aspect"""
    aspect: str
    strength: str
    harmonious: bool
    basic_interpretation: str
    detailed_interpretation: str
    advice: str


class DoubleWhammy(BaseModel):
    """Double whammy aspect (mutual aspect)"""
    planet_pair: str
    aspects: List[PlanetAspect]
    significance: str
    interpretation: str


class SynastryScore(BaseModel):
    """Overall synastry scoring"""
    overall_score: float
    rating: str  # Exceptional, Excellent, Very Good, Good, Moderate, Challenging
    aspects_analyzed: int
    double_whammies_found: int


class FocusAnalysis(BaseModel):
    """Focus-specific analysis"""
    focus_type: str
    relevant_aspects_count: int
    harmonious_count: int
    challenging_count: int
    focus_score: float
    key_aspects: List[PlanetAspect]


class SynastryResponse(BaseModel):
    """Complete synastry analysis response"""
    focus: str
    profile_1: ProfileSummary
    profile_2: ProfileSummary
    aspect_grid: List[List[str]]
    all_aspects: List[PlanetAspect]
    major_aspects: List[PlanetAspect]
    detailed_interpretations: List[DetailedAspectInterpretation]
    double_whammies: List[DoubleWhammy]
    synastry_score: SynastryScore
    focus_analysis: FocusAnalysis
    summary: str


# ============================================================================
# COMPOSITE CHART SCHEMAS
# ============================================================================

class CompositeChartRequest(BaseModel):
    """Request for composite chart generation"""
    profile_id_1: str
    profile_id_2: str


class CompositePlanet(BaseModel):
    """Composite planet position"""
    longitude: float
    sign: str
    sign_num: int
    degree: float
    description: str


class CompositeHouse(BaseModel):
    """Composite house"""
    house_number: int
    sign: str
    cusp: float
    significance: str


class CompositeAnalysis(BaseModel):
    """Composite chart analysis"""
    strengths: List[str]
    challenges: List[str]
    overall_tone: str


class CompositeChartResponse(BaseModel):
    """Complete composite chart response"""
    composite_type: str  # midpoint
    relationship_chart: Dict[str, Any]  # ascendant, planets, houses
    analysis: CompositeAnalysis
    interpretation: str
    strengths: List[str]
    challenges: List[str]
    relationship_themes: List[str]


# ============================================================================
# PROGRESSED CHART SCHEMAS
# ============================================================================

class ProgressedChartRequest(BaseModel):
    """Request for progressed chart calculation"""
    profile_id: str
    current_age: int


class ProgressedPlanet(BaseModel):
    """Progressed planet position"""
    longitude: float
    sign: str
    degree: float
    change_from_natal: Dict[str, Any]


class ProgressedAscendant(BaseModel):
    """Progressed ascendant"""
    longitude: float
    sign: str
    degree: float


class ProgressedChartResponse(BaseModel):
    """Complete progressed chart response"""
    current_age: int
    progressed_date: str
    progressed_ascendant: ProgressedAscendant
    progressed_planets: Dict[str, ProgressedPlanet]
    major_changes: List[str]
    current_themes: List[str]
    interpretation: str
    timing: Dict[str, str]


# ============================================================================
# SAVE COMPARISON SCHEMAS
# ============================================================================

class SaveComparisonRequest(BaseModel):
    """Request to save a comparison"""
    profile_id_1: str
    profile_id_2: str
    comparison_type: str  # general, romantic, business, family
    comparison_data: Dict[str, Any]  # Full comparison result


class SavedComparisonResponse(BaseModel):
    """Saved comparison record"""
    id: str
    user_id: str
    profile_id_1: str
    profile_id_2: str
    comparison_type: str
    comparison_data: Dict[str, Any]
    created_at: str
    updated_at: str


class ComparisonListResponse(BaseModel):
    """List of saved comparisons"""
    comparisons: List[SavedComparisonResponse]
    total: int
    limit: int
    offset: int
