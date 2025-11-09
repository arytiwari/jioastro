"""
Pydantic schemas for Expert Console
Professional astrologer tools and settings
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class Ayanamsa(str, Enum):
    LAHIRI = "lahiri"
    RAMAN = "raman"
    KRISHNAMURTI = "krishnamurti"
    YUKTESHWAR = "yukteshwar"
    JN_BHASIN = "jn_bhasin"
    TRUE_CITRA = "true_citra"
    TRUE_REVATI = "true_revati"
    TRUE_PUSHYA = "true_pushya"
    GALACTIC_CENTER = "galactic_center"
    NONE = "none"  # Tropical


class HouseSystem(str, Enum):
    PLACIDUS = "placidus"
    KOCH = "koch"
    EQUAL = "equal"
    WHOLE_SIGN = "whole_sign"
    PORPHYRY = "porphyry"
    REGIOMONTANUS = "regiomontanus"
    CAMPANUS = "campanus"


class AnalysisType(str, Enum):
    CHART_GENERATION = "chart_generation"
    DASHA_ANALYSIS = "dasha_analysis"
    COMPATIBILITY_MATRIX = "compatibility_matrix"
    TRANSIT_IMPACT = "transit_impact"
    YOGA_DETECTION = "yoga_detection"


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Request Schemas
class ExpertSettingsUpdate(BaseModel):
    preferred_ayanamsa: Optional[Ayanamsa] = None
    preferred_house_system: Optional[HouseSystem] = None
    show_seconds: Optional[bool] = None
    show_retrograde_symbols: Optional[bool] = None
    show_dignity_symbols: Optional[bool] = None
    decimal_precision: Optional[int] = Field(None, ge=0, le=6)
    use_true_node: Optional[bool] = None
    include_uranus: Optional[bool] = None
    include_neptune: Optional[bool] = None
    include_pluto: Optional[bool] = None
    default_vargas: Optional[List[str]] = None
    enable_rectification_tools: Optional[bool] = None
    enable_bulk_analysis: Optional[bool] = None
    enable_custom_exports: Optional[bool] = None


class LifeEvent(BaseModel):
    event: str = Field(..., description="Event description (e.g., 'marriage', 'job_change')")
    date: str = Field(..., description="Date of the event (YYYY-MM-DD)")
    expected_dasha: Optional[str] = Field(None, description="Expected dasha at event time")


class CreateRectificationSession(BaseModel):
    profile_id: Optional[str] = None
    name: str
    birth_date: str = Field(..., description="Birth date (YYYY-MM-DD)")
    birth_time: str = Field(..., description="Birth time (HH:MM:SS or HH:MM)")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str
    time_window_minutes: int = Field(120, ge=5, le=360, description="+/- time window")
    increment_seconds: int = Field(60, ge=1, le=300, description="Test interval")
    life_events: List[LifeEvent] = Field(default_factory=list)
    notes: Optional[str] = None


class BulkProfileInput(BaseModel):
    name: str
    birth_date: str = Field(..., description="Birth date (YYYY-MM-DD)")
    birth_time: str = Field(..., description="Birth time (HH:MM:SS or HH:MM)")
    latitude: float
    longitude: float
    timezone: str


class CreateBulkAnalysisJob(BaseModel):
    job_name: str = Field(..., min_length=3, max_length=100)
    analysis_type: AnalysisType
    input_profiles: List[BulkProfileInput] = Field(..., min_items=2, max_items=100)
    export_format: str = Field("json", pattern="^(json|csv|pdf|excel)$")


class CreateCalculationPreset(BaseModel):
    preset_name: str = Field(..., min_length=3, max_length=50)
    preset_description: Optional[str] = Field(None, max_length=200)
    is_public: bool = False
    ayanamsa: Ayanamsa
    house_system: HouseSystem
    calculation_options: Dict[str, Any] = Field(default_factory=dict)
    varga_selection: List[str] = Field(default_factory=lambda: ["D1", "D9"])


# Response Schemas
class ExpertSettings(BaseModel):
    id: str
    user_id: str
    preferred_ayanamsa: str
    preferred_house_system: str
    show_seconds: bool
    show_retrograde_symbols: bool
    show_dignity_symbols: bool
    decimal_precision: int
    use_true_node: bool
    include_uranus: bool
    include_neptune: bool
    include_pluto: bool
    default_vargas: List[str]
    enable_rectification_tools: bool
    enable_bulk_analysis: bool
    enable_custom_exports: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RectificationSession(BaseModel):
    id: str
    user_id: str
    profile_id: Optional[str]
    original_name: str
    original_date: str  # Date stored as string (YYYY-MM-DD)
    original_time: str  # Time stored as string (HH:MM:SS)
    original_latitude: float
    original_longitude: float
    original_timezone: str
    time_window_minutes: int
    increment_seconds: int
    life_events: Optional[Dict[str, Any]]
    status: str
    tested_times_count: int
    best_match_time: Optional[str]  # Time stored as string (HH:MM:SS)
    best_match_score: Optional[float]
    results_summary: Optional[Dict[str, Any]]
    started_at: datetime
    completed_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RectificationSessionList(BaseModel):
    sessions: List[RectificationSession]
    total_count: int


class BulkAnalysisJob(BaseModel):
    id: str
    user_id: str
    job_name: str
    analysis_type: str
    input_profiles: Dict[str, Any]
    total_profiles: int
    status: str
    processed_count: int
    failed_count: int
    results_summary: Optional[Dict[str, Any]]
    export_format: str
    export_url: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    processing_time_seconds: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BulkAnalysisJobList(BaseModel):
    jobs: List[BulkAnalysisJob]
    total_count: int


class CalculationPreset(BaseModel):
    id: str
    user_id: str
    preset_name: str
    preset_description: Optional[str]
    is_public: bool
    ayanamsa: str
    house_system: str
    calculation_options: Dict[str, Any]
    varga_selection: List[str]
    usage_count: int
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CalculationPresetList(BaseModel):
    presets: List[CalculationPreset]
    total_count: int


# Stats
class ExpertConsoleStats(BaseModel):
    total_rectification_sessions: int
    total_bulk_jobs: int
    total_presets: int
    rectifications_completed: int
    bulk_jobs_completed: int
    favorite_ayanamsa: Optional[str]
    favorite_house_system: Optional[str]
