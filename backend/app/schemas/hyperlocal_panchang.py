"""
Pydantic schemas for Hyperlocal Panchang feature
Handles location-based Panchang calculations and daily guidance
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum


# Enums

class Paksha(str, Enum):
    """Lunar fortnight"""
    SHUKLA = "Shukla"  # Waxing moon
    KRISHNA = "Krishna"  # Waning moon


class MoonPhase(str, Enum):
    """Moon phases"""
    NEW_MOON = "New Moon"
    WAXING_CRESCENT = "Waxing Crescent"
    FIRST_QUARTER = "First Quarter"
    WAXING_GIBBOUS = "Waxing Gibbous"
    FULL_MOON = "Full Moon"
    WANING_GIBBOUS = "Waning Gibbous"
    LAST_QUARTER = "Last Quarter"
    WANING_CRESCENT = "Waning Crescent"


class Ritu(str, Enum):
    """Vedic seasons"""
    VASANTA = "Vasanta"  # Spring (Chaitra-Vaishakha)
    GRISHMA = "Grishma"  # Summer (Jyeshtha-Ashadha)
    VARSHA = "Varsha"    # Monsoon (Shravana-Bhadrapada)
    SHARAD = "Sharad"    # Autumn (Ashwin-Kartik)
    HEMANTA = "Hemanta"  # Pre-winter (Margashirsha-Pausha)
    SHISHIRA = "Shishira" # Winter (Magha-Phalguna)


class DayQuality(str, Enum):
    """Overall day quality"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    CHALLENGING = "challenging"
    DIFFICULT = "difficult"


# Request Schemas

class GetPanchangRequest(BaseModel):
    """Get Panchang for specific date and location"""
    panchang_date: date
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)
    timezone: str = Field(..., description="IANA timezone e.g., 'Asia/Kolkata'")
    location_name: Optional[str] = None


class SubscribeLocationRequest(BaseModel):
    """Subscribe to location for daily Panchang"""
    location_name: str = Field(..., min_length=1, max_length=100)
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)
    timezone: str
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    is_primary: bool = False
    notification_enabled: bool = True
    notification_time: time = Field(default=time(6, 0))


class UpdatePanchangPreferencesRequest(BaseModel):
    """Update user's Panchang preferences"""
    show_tithi: Optional[bool] = None
    show_nakshatra: Optional[bool] = None
    show_yoga: Optional[bool] = None
    show_karana: Optional[bool] = None
    show_rahukaal: Optional[bool] = None
    show_hora: Optional[bool] = None
    show_festivals: Optional[bool] = None
    notify_on_ekadashi: Optional[bool] = None
    notify_on_amavasya: Optional[bool] = None
    notify_on_purnima: Optional[bool] = None
    notify_on_festivals: Optional[bool] = None
    notify_before_rahukaal: Optional[bool] = None
    calendar_sync_enabled: Optional[bool] = None
    calendar_provider: Optional[str] = None


# Response Schemas

class TithiInfo(BaseModel):
    """Tithi (Lunar Day) information"""
    tithi_name: str
    tithi_number: int = Field(..., ge=1, le=30)
    paksha: Paksha
    tithi_start_time: datetime
    tithi_end_time: datetime
    tithi_deity: Optional[str] = None
    tithi_quality: Optional[str] = None
    is_active: bool  # True if current time falls in this Tithi


class NakshatraInfo(BaseModel):
    """Nakshatra (Lunar Mansion) information"""
    nakshatra_name: str
    nakshatra_number: int = Field(..., ge=1, le=27)
    nakshatra_start_time: datetime
    nakshatra_end_time: datetime
    nakshatra_pada: int = Field(..., ge=1, le=4)
    nakshatra_deity: Optional[str] = None
    nakshatra_lord: str  # Ruling planet
    nakshatra_quality: Optional[str] = None
    is_active: bool


class YogaInfo(BaseModel):
    """Yoga information"""
    yoga_name: str
    yoga_number: int = Field(..., ge=1, le=27)
    yoga_start_time: datetime
    yoga_end_time: datetime
    yoga_quality: Optional[str] = None
    is_active: bool


class KaranaInfo(BaseModel):
    """Karana information"""
    karana_name: str
    karana_number: int = Field(..., ge=1, le=11)
    karana_quality: Optional[str] = None


class VaraInfo(BaseModel):
    """Vara (Weekday) information"""
    vara_name: str
    vara_lord: str  # Ruling planet
    vara_number: int = Field(..., ge=0, le=6)  # 0=Sunday


class InauspiciousTime(BaseModel):
    """Inauspicious time period"""
    name: str
    start_time: time
    end_time: time
    description: Optional[str] = None


class AuspiciousTime(BaseModel):
    """Auspicious time period"""
    name: str
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = None


class HoraInfo(BaseModel):
    """Planetary hour (Hora) information"""
    hora_number: int = Field(..., ge=1, le=24)
    planet: str
    start_time: datetime
    end_time: datetime
    is_favorable: bool


class SunMoonData(BaseModel):
    """Sun and Moon timings"""
    sunrise: datetime
    sunset: datetime
    moonrise: Optional[datetime] = None
    moonset: Optional[datetime] = None
    moon_phase: MoonPhase
    moon_illumination: float = Field(..., ge=0, le=100)


class Panchang(BaseModel):
    """Complete Panchang for a day"""
    panchang_date: date
    location_name: Optional[str] = None
    latitude: Decimal
    longitude: Decimal
    timezone: str

    # Panchang Elements
    tithi: TithiInfo
    nakshatra: NakshatraInfo
    yoga: YogaInfo
    karana: KaranaInfo
    vara: VaraInfo
    paksha: Paksha
    ritu: Optional[Ritu] = None
    masa_name: Optional[str] = None

    # Sun and Moon
    sun_moon: SunMoonData

    # Inauspicious times
    rahukaal_start: time
    rahukaal_end: time
    yamaghanta_start: Optional[time] = None
    yamaghanta_end: Optional[time] = None
    gulika_kaal_start: Optional[time] = None
    gulika_kaal_end: Optional[time] = None
    dur_muhurtam: List[InauspiciousTime] = Field(default_factory=list)

    # Auspicious times
    abhijit_muhurta_start: Optional[time] = None
    abhijit_muhurta_end: Optional[time] = None
    brahma_muhurta_start: Optional[time] = None
    brahma_muhurta_end: Optional[time] = None

    # Hora sequence
    hora_sequence: List[HoraInfo] = Field(default_factory=list)

    # Special days
    is_festival: bool = False
    festival_name: Optional[str] = None
    festival_significance: Optional[str] = None
    is_ekadashi: bool = False
    is_amavasya: bool = False
    is_purnima: bool = False
    is_panchaka: bool = False
    special_days: List[str] = Field(default_factory=list)

    # Bhadra
    bhadra_periods: List[InauspiciousTime] = Field(default_factory=list)

    # Guidance
    daily_guidance: Optional[str] = None
    favorable_activities: List[str] = Field(default_factory=list)
    unfavorable_activities: List[str] = Field(default_factory=list)

    # Metadata
    calculated_at: datetime
    calculation_version: str = "1.0"


class PanchangSubscription(BaseModel):
    """User's location subscription"""
    id: str
    user_id: str
    location_name: str
    latitude: Decimal
    longitude: Decimal
    timezone: str
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    is_primary: bool
    notification_enabled: bool
    notification_time: time
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PanchangPreferences(BaseModel):
    """User's Panchang display preferences"""
    user_id: str
    show_tithi: bool = True
    show_nakshatra: bool = True
    show_yoga: bool = True
    show_karana: bool = True
    show_rahukaal: bool = True
    show_hora: bool = True
    show_festivals: bool = True
    notify_on_ekadashi: bool = False
    notify_on_amavasya: bool = False
    notify_on_purnima: bool = False
    notify_on_festivals: bool = True
    notify_before_rahukaal: bool = False
    calendar_sync_enabled: bool = False
    calendar_provider: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DailyGuidance(BaseModel):
    """Personalized daily guidance"""
    id: str
    user_id: str
    profile_id: Optional[str] = None
    guidance_date: date

    overall_day_quality: DayQuality
    overall_guidance: str

    # Best times
    best_time_for_work: Optional[time] = None
    best_time_for_meditation: Optional[time] = None
    best_time_for_important_decisions: Optional[time] = None
    avoid_time_start: Optional[time] = None
    avoid_time_end: Optional[time] = None

    # Area-specific guidance
    career_guidance: Optional[str] = None
    relationship_guidance: Optional[str] = None
    health_guidance: Optional[str] = None
    financial_guidance: Optional[str] = None
    spiritual_guidance: Optional[str] = None

    # Lucky elements
    lucky_color: Optional[str] = None
    lucky_direction: Optional[str] = None
    lucky_number: Optional[int] = None
    lucky_gemstone: Optional[str] = None

    # Daily remedies
    suggested_mantra: Optional[str] = None
    suggested_deity: Optional[str] = None
    suggested_charity: Optional[str] = None

    # User interaction
    was_viewed: bool = False
    viewed_at: Optional[datetime] = None
    user_rating: Optional[int] = None
    user_feedback: Optional[str] = None

    created_at: datetime

    class Config:
        from_attributes = True


class CurrentTimeCheck(BaseModel):
    """Check if current time is auspicious"""
    panchang_date: date
    check_time: datetime
    is_auspicious: bool
    current_hora: Optional[HoraInfo] = None
    is_in_rahukaal: bool
    is_in_dur_muhurtam: bool
    is_in_bhadra: bool
    is_in_abhijit_muhurta: bool
    recommendations: str
    can_start_new_work: bool


class UpcomingSpecialDays(BaseModel):
    """Upcoming special days and festivals"""
    ekadashi_dates: List[date] = Field(default_factory=list)
    amavasya_dates: List[date] = Field(default_factory=list)
    purnima_dates: List[date] = Field(default_factory=list)
    festivals: List[Dict[str, Any]] = Field(default_factory=list)


class MonthlyPanchang(BaseModel):
    """Panchang for entire month"""
    year: int
    month: int
    location_name: str
    panchangs: List[Panchang]
    special_days: UpcomingSpecialDays
    monthly_summary: str


class PanchangComparison(BaseModel):
    """Compare Panchang for multiple locations"""
    panchang_date: date
    locations: List[Panchang]
    time_zone_differences: Dict[str, int]  # location -> hours difference


# Analytics

class PanchangStats(BaseModel):
    """Statistics about Panchang usage"""
    total_views: int
    favorite_location: Optional[str] = None
    most_viewed_day: Optional[str] = None  # Day of week
    guidance_rating_average: Optional[float] = None
    guidance_usefulness_count: int
