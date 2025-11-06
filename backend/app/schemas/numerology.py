"""
Pydantic schemas for numerology API endpoints
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class NumerologyCalculateRequest(BaseModel):
    """Request schema for numerology calculation"""
    full_name: str = Field(..., min_length=1, max_length=255, description="Full birth name")
    birth_date: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    system: str = Field(default="both", description="Numerology system: 'western', 'vedic', or 'both'")
    profile_id: Optional[str] = Field(None, description="Optional profile ID to associate with")

    @field_validator('system')
    @classmethod
    def validate_system(cls, v):
        allowed = ['western', 'vedic', 'chaldean', 'both']
        if v not in allowed:
            raise ValueError(f"system must be one of {allowed}")
        return v


class NameTrialCreate(BaseModel):
    """Request schema for creating a name trial"""
    numerology_profile_id: str = Field(..., description="Numerology profile ID")
    trial_name: str = Field(..., min_length=1, max_length=255, description="Trial name to test")
    system: str = Field(default="both", description="System to use: 'western', 'vedic', or 'both'")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes about this trial")

    @field_validator('system')
    @classmethod
    def validate_system(cls, v):
        allowed = ['western', 'vedic', 'chaldean', 'both']
        if v not in allowed:
            raise ValueError(f"system must be one of {allowed}")
        return v


class PrivacyPreferencesUpdate(BaseModel):
    """Request schema for updating privacy preferences"""
    store_numerology_trials: Optional[bool] = None
    share_numerology_anonymously: Optional[bool] = None
    data_retention_days: Optional[int] = Field(None, ge=0, le=3650)  # 0-10 years


# ============================================================================
# RESPONSE SCHEMAS - Core Numbers
# ============================================================================

class NumberDetail(BaseModel):
    """Detailed information about a calculated number"""
    number: int = Field(..., description="The calculated number")
    is_master: bool = Field(default=False, description="Whether this is a master number (11, 22, 33)")
    karmic_debt: Optional[int] = Field(None, description="Karmic debt number if present")
    karmic_debt_meaning: Optional[Dict[str, Any]] = Field(None, description="Karmic debt interpretation if present")
    meaning: Dict[str, Any] = Field(default_factory=dict, description="Interpretation and meaning of this number")
    breakdown: Dict[str, Any] = Field(default_factory=dict, description="Calculation breakdown")


class LetterValue(BaseModel):
    """Letter to number mapping"""
    letter: str
    value: int


class NameBasedNumber(BaseModel):
    """Number calculated from name"""
    number: int
    is_master: bool = False
    karmic_debt: Optional[int] = None
    karmic_debt_meaning: Optional[Dict[str, Any]] = None
    meaning: Dict[str, Any] = {}
    letter_values: List[LetterValue] = []
    breakdown: Dict[str, Any] = {}


class CycleNumber(BaseModel):
    """Current cycle number (Personal Year/Month/Day)"""
    number: int
    meaning: Dict[str, Any] = {}
    breakdown: Dict[str, Any] = {}


class PinnacleChallenge(BaseModel):
    """Pinnacle or Challenge period"""
    period: int
    number: int
    start_age: int
    end_age: Optional[int]  # None for last period
    description: str


# ============================================================================
# RESPONSE SCHEMAS - Western Numerology
# ============================================================================

class WesternCoreNumbers(BaseModel):
    """Core numbers in Western numerology"""
    life_path: NumberDetail
    expression: NameBasedNumber
    soul_urge: NameBasedNumber
    personality: NameBasedNumber
    maturity: NumberDetail
    birth_day: NumberDetail


class WesternSpecialNumbers(BaseModel):
    """Special numbers in Western numerology"""
    master_numbers: List[int] = []
    karmic_debt: List[Dict[str, Any]] = []


class WesternCurrentCycles(BaseModel):
    """Current cycle numbers"""
    personal_year: CycleNumber
    personal_month: CycleNumber
    personal_day: CycleNumber


class WesternLifePeriods(BaseModel):
    """Life period information"""
    pinnacles: List[PinnacleChallenge]
    challenges: List[PinnacleChallenge]


class WesternNumerologyData(BaseModel):
    """Complete Western numerology data"""
    system: str = "western"
    core_numbers: WesternCoreNumbers
    special_numbers: WesternSpecialNumbers
    current_cycles: WesternCurrentCycles
    life_periods: WesternLifePeriods
    calculation_hash: str
    calculated_at: str


# ============================================================================
# RESPONSE SCHEMAS - Vedic Numerology
# ============================================================================

class VedicNumber(BaseModel):
    """Vedic number with planet association"""
    number: int
    planet: str
    day_of_birth: Optional[int] = None
    meaning: Dict[str, Any] = {}
    breakdown: Dict[str, Any] = {}


class VedicNameNumber(BaseModel):
    """Vedic name-based number"""
    number: int
    planet: str
    meaning: str = ""
    letter_values: List[LetterValue] = []
    breakdown: Dict[str, Any] = {}


class VedicPlanetAssociations(BaseModel):
    """Planet associations"""
    psychic_planet: str
    destiny_planet: str


class VedicFavorableNumbers(BaseModel):
    """Favorable and unfavorable numbers"""
    favorable: List[int]
    unfavorable: List[int]
    psychic_favorable: List[int]
    destiny_favorable: List[int]
    reasoning: Dict[str, str]


class NameCorrection(BaseModel):
    """Name correction suggestion"""
    type: str
    message: str
    impact: str
    current_value: Optional[int] = None
    target_value: Optional[int] = None
    target_planet: Optional[str] = None
    favorable_targets: Optional[List[int]] = None


class VedicNumerologyData(BaseModel):
    """Complete Vedic numerology data"""
    system: str = "vedic"
    psychic_number: VedicNumber
    destiny_number: VedicNameNumber
    name_value: VedicNameNumber
    planet_associations: VedicPlanetAssociations
    favorable_numbers: VedicFavorableNumbers
    favorable_dates: List[int]
    name_corrections: List[NameCorrection]
    calculation_hash: str
    calculated_at: str


# ============================================================================
# RESPONSE SCHEMAS - Combined
# ============================================================================

class NumerologyCalculationResponse(BaseModel):
    """Response for numerology calculation"""
    full_name: str
    birth_date: str
    system: str
    western: Optional[WesternNumerologyData] = None
    vedic: Optional[VedicNumerologyData] = None
    calculation_hash: str
    calculated_at: str


class NumerologyProfile(BaseModel):
    """Saved numerology profile"""
    id: str
    user_id: str
    profile_id: Optional[str] = None
    full_name: str
    common_name: Optional[str] = None
    name_at_birth: Optional[str] = None
    system: str
    western_data: Optional[Dict[str, Any]] = None
    vedic_data: Optional[Dict[str, Any]] = None
    cycles: Optional[Dict[str, Any]] = None
    birth_date: str
    calculation_hash: str
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime


class NumerologyProfileResponse(BaseModel):
    """Response for numerology profile with full data"""
    profile: NumerologyProfile
    calculation: Optional[NumerologyCalculationResponse] = None


class NumerologyProfileList(BaseModel):
    """List of numerology profiles"""
    profiles: List[NumerologyProfile]
    count: int


# ============================================================================
# RESPONSE SCHEMAS - Name Trials
# ============================================================================

class NameTrialResponse(BaseModel):
    """Response for name trial"""
    id: str
    numerology_profile_id: str
    user_id: str
    trial_name: str
    system: str
    calculated_values: Dict[str, Any]
    notes: Optional[str] = None
    is_preferred: bool = False
    created_at: datetime


class NameTrialList(BaseModel):
    """List of name trials"""
    trials: List[NameTrialResponse]
    count: int


# ============================================================================
# RESPONSE SCHEMAS - Privacy
# ============================================================================

class PrivacyPreferencesResponse(BaseModel):
    """Response for privacy preferences"""
    user_id: str
    store_numerology_trials: bool
    share_numerology_anonymously: bool
    store_palm_images: bool
    store_palm_features: bool
    erasable_audit: bool
    data_retention_days: int
    privacy_policy_version: Optional[str] = None
    privacy_policy_accepted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# UTILITY SCHEMAS
# ============================================================================

class NumerologyInsight(BaseModel):
    """Numerology insight or interpretation"""
    category: str  # e.g., "life_path", "expression", "current_cycle"
    title: str
    description: str
    influence: str  # "strong", "moderate", "weak"
    time_frame: Optional[str] = None  # e.g., "lifetime", "current_year"


class NumerologyReading(BaseModel):
    """Complete numerology reading with insights"""
    profile_id: str
    calculation: NumerologyCalculationResponse
    insights: List[NumerologyInsight]
    summary: str
    generated_at: datetime


# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class NumerologyError(BaseModel):
    """Error response for numerology endpoints"""
    error: str
    detail: str
    error_code: Optional[str] = None
