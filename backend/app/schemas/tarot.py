"""
Tarot Reading Pydantic Schemas
Request and response models for tarot card readings
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== Tarot Card Schemas ====================

class TarotCard(BaseModel):
    """Single tarot card with all metadata"""
    id: str = Field(..., description="Unique card ID")
    card_number: int = Field(..., ge=0, le=77, description="Card number 0-77")
    name: str = Field(..., description="Card name (e.g., The Fool, Ace of Cups)")
    suit: Optional[str] = Field(None, description="major_arcana, cups, pentacles, swords, wands")
    arcana_type: str = Field(..., description="major or minor")
    upright_meaning: str = Field(..., description="Meaning when card is upright")
    reversed_meaning: str = Field(..., description="Meaning when card is reversed")
    upright_keywords: List[str] = Field(default_factory=list, description="Keywords for upright position")
    reversed_keywords: List[str] = Field(default_factory=list, description="Keywords for reversed position")
    imagery_description: Optional[str] = Field(None, description="Description of card imagery")
    element: Optional[str] = Field(None, description="Associated element (fire, water, air, earth, spirit)")
    astrological_association: Optional[str] = Field(None, description="Associated zodiac sign or planet")
    numerological_value: Optional[int] = Field(None, description="Numerological value")
    image_url: Optional[str] = Field(None, description="URL to card image")

    class Config:
        from_attributes = True


class TarotCardBrief(BaseModel):
    """Brief tarot card info (for lists)"""
    id: str
    card_number: int
    name: str
    suit: Optional[str]
    arcana_type: str
    element: Optional[str]


# ==================== Tarot Spread Schemas ====================

class SpreadPosition(BaseModel):
    """Position definition in a tarot spread"""
    position: int = Field(..., description="Position number (1-10)")
    name: str = Field(..., description="Position name (e.g., Past, Present, Future)")
    meaning: str = Field(..., description="What this position represents")


class TarotSpread(BaseModel):
    """Tarot spread template"""
    id: str
    name: str = Field(..., description="Spread name (e.g., Celtic Cross)")
    description: str = Field(..., description="Description of the spread")
    num_cards: int = Field(..., ge=1, le=10, description="Number of cards in spread")
    positions: List[SpreadPosition] = Field(..., description="Position definitions")
    difficulty_level: str = Field(default="beginner", description="beginner, intermediate, advanced")
    category: str = Field(default="general", description="love, career, spiritual, general, decision")
    is_active: bool = Field(default=True)

    class Config:
        from_attributes = True


class TarotSpreadBrief(BaseModel):
    """Brief spread info (for lists)"""
    id: str
    name: str
    description: str
    num_cards: int
    difficulty_level: str
    category: str


# ==================== Reading Request/Response Schemas ====================

class DrawnCard(BaseModel):
    """A card drawn in a reading"""
    card_id: str = Field(..., description="ID of the drawn card")
    card_name: str = Field(..., description="Name of the card")
    card_number: int = Field(..., description="Card number")
    position: int = Field(..., description="Position in spread (1-10)")
    position_name: str = Field(..., description="Name of position (e.g., Past)")
    position_meaning: str = Field(..., description="What this position represents")
    is_reversed: bool = Field(default=False, description="Whether card is reversed")
    suit: Optional[str] = None
    element: Optional[str] = None


class CreateReadingRequest(BaseModel):
    """Request to create a new tarot reading"""
    spread_id: Optional[str] = Field(None, description="ID of spread template to use")
    spread_name: str = Field(..., description="Name of spread (required even if custom)")
    reading_type: str = Field(..., description="daily_card, three_card, celtic_cross, custom")
    question: Optional[str] = Field(None, description="User's question or intention")
    profile_id: Optional[str] = Field(None, description="Birth profile for holistic analysis")
    num_cards: Optional[int] = Field(None, ge=1, le=10, description="Number of cards (for custom spreads)")

    class Config:
        json_schema_extra = {
            "example": {
                "spread_id": "uuid-here",
                "spread_name": "Three Card Spread",
                "reading_type": "three_card",
                "question": "What should I focus on in my career this month?",
                "profile_id": "profile-uuid"
            }
        }


class AstrologyCorrelation(BaseModel):
    """Astrological correlations in tarot reading"""
    sun_sign: Optional[str] = None
    moon_sign: Optional[str] = None
    ascendant: Optional[str] = None
    correlation_notes: Optional[str] = Field(None, description="How cards relate to birth chart")
    planetary_influences: Optional[Dict[str, Any]] = Field(None, description="Planets affecting the reading")


class NumerologyCorrelation(BaseModel):
    """Numerological correlations in tarot reading"""
    life_path: Optional[int] = None
    destiny_number: Optional[int] = None
    personal_year: Optional[int] = None
    correlation_notes: Optional[str] = Field(None, description="How cards relate to numerology")
    card_number_patterns: Optional[List[str]] = Field(None, description="Patterns in card numbers")


class TarotReading(BaseModel):
    """Complete tarot reading with interpretation"""
    id: str
    user_id: str
    profile_id: Optional[str] = Field(None, description="Linked birth profile for holistic analysis")
    reading_type: str
    spread_id: Optional[str]
    spread_name: str
    question: Optional[str]
    cards_drawn: List[DrawnCard] = Field(..., description="Cards drawn in the reading")
    interpretation: Optional[str] = Field(None, description="AI-generated interpretation")
    summary: Optional[str] = Field(None, description="Brief summary of reading")
    astrology_correlations: Optional[AstrologyCorrelation] = Field(None, description="Astrological insights")
    numerology_correlations: Optional[NumerologyCorrelation] = Field(None, description="Numerological insights")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    is_favorite: bool = Field(default=False)
    notes: Optional[str] = Field(None, description="User's personal notes")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TarotReadingBrief(BaseModel):
    """Brief reading info (for lists)"""
    id: str
    reading_type: str
    spread_name: str
    question: Optional[str]
    num_cards: int
    is_favorite: bool
    created_at: datetime


class UpdateReadingRequest(BaseModel):
    """Request to update a reading"""
    is_favorite: Optional[bool] = None
    notes: Optional[str] = None


# ==================== Response Schemas ====================

class TarotCardListResponse(BaseModel):
    """Response with list of tarot cards"""
    cards: List[TarotCardBrief]
    total_count: int


class TarotSpreadListResponse(BaseModel):
    """Response with list of spreads"""
    spreads: List[TarotSpreadBrief]
    total_count: int


class TarotReadingListResponse(BaseModel):
    """Response with list of readings"""
    readings: List[TarotReadingBrief]
    total_count: int


class DailyCardResponse(BaseModel):
    """Response for daily card draw"""
    card: TarotCard
    is_reversed: bool
    interpretation: str
    keywords: List[str]
    guidance: str
    date: datetime


# ==================== Statistics ====================

class TarotStats(BaseModel):
    """User's tarot reading statistics"""
    total_readings: int = 0
    daily_cards_drawn: int = 0
    favorite_readings: int = 0
    most_drawn_card: Optional[Dict[str, Any]] = None
    readings_by_type: Dict[str, int] = Field(default_factory=dict)
    recent_reading_date: Optional[datetime] = None
