"""
Feng Shui Integration Pydantic Schemas
Request and response models for feng shui analysis
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== Direction and Element Schemas ====================

class FavorableDirections(BaseModel):
    """Four favorable directions based on Kua number"""
    sheng_qi: str = Field(..., description="Wealth & Success direction (N/NE/E/SE/S/SW/W/NW)")
    tian_yi: str = Field(..., description="Health & Well-being direction")
    yan_nian: str = Field(..., description="Love & Relationships direction")
    fu_wei: str = Field(..., description="Personal Growth & Stability direction")


class UnfavorableDirections(BaseModel):
    """Four unfavorable directions to avoid"""
    huo_hai: str = Field(..., description="Mishaps & Bad Luck direction")
    wu_gui: str = Field(..., description="Five Ghosts direction")
    liu_sha: str = Field(..., description="Six Killings direction")
    jue_ming: str = Field(..., description="Total Loss direction")


class DirectionMeaning(BaseModel):
    """Meaning and application of each direction type"""
    direction_type: str = Field(..., description="e.g., sheng_qi, tian_yi")
    compass_direction: str = Field(..., description="N, NE, E, SE, S, SW, W, NW")
    name: str = Field(..., description="English name (e.g., Wealth & Success)")
    description: str = Field(..., description="Detailed meaning")
    best_use: str = Field(..., description="Best placement (desk, bed, entrance, etc.)")
    benefits: List[str] = Field(default_factory=list, description="Expected benefits")


# ==================== Request Schemas ====================

class CreateFengShuiAnalysisRequest(BaseModel):
    """Request to create feng shui analysis"""
    profile_id: str = Field(..., description="Birth profile ID (required for Kua calculation)")
    space_type: Optional[str] = Field(None, description="home, office, bedroom, living_room, etc.")
    space_orientation: Optional[str] = Field(None, description="Main entrance facing direction (N/NE/E/SE/S/SW/W/NW)")
    space_layout: Optional[Dict[str, Any]] = Field(None, description="Room layout and details")

    class Config:
        json_schema_extra = {
            "example": {
                "profile_id": "profile-uuid-here",
                "space_type": "home",
                "space_orientation": "SE",
                "space_layout": {
                    "main_entrance": "SE",
                    "bedroom": "N",
                    "office": "E",
                    "living_room": "S"
                }
            }
        }


class UpdateSpaceLayoutRequest(BaseModel):
    """Update space layout for existing analysis"""
    space_type: Optional[str] = None
    space_orientation: Optional[str] = None
    space_layout: Optional[Dict[str, Any]] = None


# ==================== Analysis Response Schemas ====================

class FengShuiAnalysis(BaseModel):
    """Complete feng shui analysis"""
    id: str
    user_id: str
    profile_id: str = Field(..., description="Birth profile used for Kua calculation")

    # Kua Number and Element
    kua_number: int = Field(..., ge=1, le=9, description="Personal Kua number (1-9)")
    personal_element: str = Field(..., description="wood, fire, earth, metal, water")
    life_gua_group: str = Field(..., description="east or west life group")

    # Directions
    favorable_directions: FavorableDirections
    unfavorable_directions: UnfavorableDirections
    direction_meanings: Optional[List[DirectionMeaning]] = None

    # Colors and Elements
    lucky_colors: List[str] = Field(..., description="Favorable colors")
    unlucky_colors: List[str] = Field(..., description="Colors to avoid")
    supporting_elements: Optional[List[str]] = Field(None, description="Elements that support personal element")
    weakening_elements: Optional[List[str]] = Field(None, description="Elements that weaken personal element")

    # Space Information
    space_type: Optional[str]
    space_orientation: Optional[str]
    space_layout: Optional[Dict[str, Any]]

    # Analysis Results
    analysis_summary: Optional[str] = Field(None, description="AI-generated summary")
    compatibility_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Space compatibility (0-100)")

    # Astrological Correlations
    birth_element: Optional[str] = Field(None, description="Element from astrology chart")
    planetary_influences: Optional[Dict[str, Any]] = None
    astrology_feng_shui_harmony: Optional[str] = Field(None, description="How astrology and feng shui align")

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FengShuiAnalysisBrief(BaseModel):
    """Brief feng shui analysis (for lists)"""
    id: str
    profile_id: str
    kua_number: int
    personal_element: str
    space_type: Optional[str]
    compatibility_score: float
    created_at: datetime


# ==================== Recommendation Schemas ====================

class CreateRecommendationRequest(BaseModel):
    """Request to create a custom recommendation"""
    analysis_id: str
    category: str = Field(..., description="colors, directions, elements, placement, remedies, enhancements")
    area: Optional[str] = Field(None, description="bedroom, office, entrance, etc.")
    title: str
    recommendation: str
    reason: Optional[str] = None
    priority: str = Field(default="medium", description="high, medium, low")


class UpdateRecommendationRequest(BaseModel):
    """Update recommendation implementation status"""
    is_implemented: Optional[bool] = None
    user_notes: Optional[str] = None
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5, description="1-5 star rating")


class FengShuiRecommendation(BaseModel):
    """Individual feng shui recommendation"""
    id: str
    analysis_id: str
    user_id: str
    profile_id: Optional[str]

    # Recommendation Details
    category: str = Field(..., description="colors, directions, elements, placement, remedies, enhancements")
    area: Optional[str] = Field(None, description="bedroom, office, entrance, etc.")
    title: str
    recommendation: str
    reason: Optional[str]

    # Priority and Implementation
    priority: str = Field(default="medium", description="high, medium, low")
    impact_score: float = Field(default=0.0, ge=0.0, le=10.0)
    difficulty: str = Field(default="easy", description="easy, moderate, difficult")

    # Cross-Domain Correlations
    astrology_correlation: Optional[str] = Field(None, description="Relation to birth chart")
    numerology_correlation: Optional[str] = Field(None, description="Relation to life path")

    # User Tracking
    is_implemented: bool = Field(default=False)
    implemented_at: Optional[datetime] = None
    user_notes: Optional[str] = None
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5)

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FengShuiRecommendationBrief(BaseModel):
    """Brief recommendation info (for lists)"""
    id: str
    category: str
    title: str
    priority: str
    is_implemented: bool
    impact_score: float


# ==================== Response Schemas ====================

class FengShuiAnalysisListResponse(BaseModel):
    """Response with list of analyses"""
    analyses: List[FengShuiAnalysisBrief]
    total_count: int


class FengShuiRecommendationListResponse(BaseModel):
    """Response with list of recommendations"""
    recommendations: List[FengShuiRecommendation]
    total_count: int
    by_category: Dict[str, int] = Field(default_factory=dict, description="Count by category")
    by_priority: Dict[str, int] = Field(default_factory=dict, description="Count by priority")
    implemented_count: int = 0


class KuaCalculationResponse(BaseModel):
    """Response for Kua number calculation"""
    kua_number: int = Field(..., ge=1, le=9)
    personal_element: str
    life_gua_group: str
    favorable_directions: FavorableDirections
    unfavorable_directions: UnfavorableDirections
    lucky_colors: List[str]
    unlucky_colors: List[str]
    description: str = Field(..., description="Explanation of Kua number meaning")


class DirectionGuidance(BaseModel):
    """Guidance for a specific direction"""
    direction: str = Field(..., description="N, NE, E, SE, S, SW, W, NW")
    is_favorable: bool
    direction_type: Optional[str] = Field(None, description="sheng_qi, tian_yi, etc.")
    name: Optional[str] = Field(None, description="Wealth, Health, etc.")
    guidance: str = Field(..., description="What to do with this direction")
    best_for: List[str] = Field(default_factory=list, description="Best uses (desk, bed, entrance, etc.)")


class ColorTherapyResponse(BaseModel):
    """Color therapy recommendations"""
    lucky_colors: List[Dict[str, str]] = Field(..., description="[{color: green, hex: #00FF00, meaning: growth}]")
    unlucky_colors: List[Dict[str, str]]
    room_color_suggestions: Dict[str, List[str]] = Field(default_factory=dict, description="Colors for each room")
    clothing_colors: List[str] = Field(default_factory=list)
    decor_suggestions: List[str] = Field(default_factory=list)


class ElementBalanceResponse(BaseModel):
    """Element balance and recommendations"""
    personal_element: str
    supporting_elements: List[str]
    weakening_elements: List[str]
    productive_cycle: List[str] = Field(..., description="Element generation cycle")
    destructive_cycle: List[str] = Field(..., description="Element control cycle")
    balance_recommendations: List[str] = Field(default_factory=list)


# ==================== Statistics ====================

class FengShuiStats(BaseModel):
    """User's feng shui statistics"""
    total_analyses: int = 0
    total_recommendations: int = 0
    implemented_recommendations: int = 0
    implementation_rate: float = Field(default=0.0, description="Percentage of implemented recommendations")
    avg_effectiveness_rating: float = Field(default=0.0)
    most_used_space_type: Optional[str] = None
    kua_number: Optional[int] = None
