"""
Tarot Reading API Endpoints
Provides tarot card readings with profile integration
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.security import get_current_user
from app.services.tarot_service import TarotService
from app.schemas.tarot import (
    TarotCard,
    TarotCardListResponse,
    TarotSpread,
    TarotSpreadListResponse,
    CreateReadingRequest,
    TarotReading,
    TarotReadingListResponse,
    UpdateReadingRequest,
    DailyCardResponse,
    TarotStats
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/cards", response_model=TarotCardListResponse)
async def get_tarot_cards(
    suit: Optional[str] = Query(None, description="Filter by suit (major_arcana, cups, pentacles, swords, wands)"),
    arcana_type: Optional[str] = Query(None, description="Filter by type (major, minor)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all tarot cards or filtered by suit/type
    """
    try:
        service = TarotService()
        cards = await service.get_all_cards()

        # Apply filters
        if suit:
            cards = [c for c in cards if c.get("suit") == suit]
        if arcana_type:
            cards = [c for c in cards if c.get("arcana_type") == arcana_type]

        return {
            "cards": cards,
            "total_count": len(cards)
        }
    except Exception as e:
        logger.error(f"Failed to fetch tarot cards: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch tarot cards")


@router.get("/cards/{card_id}", response_model=TarotCard)
async def get_tarot_card(
    card_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific tarot card by ID
    """
    try:
        service = TarotService()
        card = await service.get_card_by_id(card_id)

        if not card:
            raise HTTPException(status_code=404, detail="Card not found")

        return card
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch card {card_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch card")


@router.get("/spreads", response_model=TarotSpreadListResponse)
async def get_tarot_spreads(
    category: Optional[str] = Query(None, description="Filter by category (love, career, spiritual, general, decision)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get available tarot spreads
    """
    try:
        service = TarotService()
        spreads = await service.get_spreads(category=category)

        return {
            "spreads": spreads,
            "total_count": len(spreads)
        }
    except Exception as e:
        logger.error(f"Failed to fetch spreads: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch spreads")


@router.get("/spreads/{spread_id}", response_model=TarotSpread)
async def get_tarot_spread(
    spread_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific spread by ID
    """
    try:
        service = TarotService()
        spread = await service.get_spread_by_id(spread_id)

        if not spread:
            raise HTTPException(status_code=404, detail="Spread not found")

        return spread
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch spread {spread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch spread")


@router.post("/daily-card", response_model=DailyCardResponse)
async def draw_daily_card(
    current_user: dict = Depends(get_current_user)
):
    """
    Draw daily card for the user
    Returns existing card if already drawn today
    """
    try:
        user_id = current_user["sub"]
        service = TarotService()

        result = await service.draw_daily_card(user_id)
        card_data = result["card"]

        # Get keywords based on orientation
        keywords = card_data.get("reversed_keywords", []) if result["is_reversed"] else card_data.get("upright_keywords", [])
        meaning = card_data.get("reversed_meaning", "") if result["is_reversed"] else card_data.get("upright_meaning", "")

        # Generate guidance
        orientation = "Reversed" if result["is_reversed"] else "Upright"
        guidance = f"Today's card is {card_data.get('name')} ({orientation}). {meaning[:150]}..."

        from datetime import datetime
        return {
            "card": card_data,
            "is_reversed": result["is_reversed"],
            "interpretation": meaning,
            "keywords": keywords[:5],
            "guidance": guidance,
            "date": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Failed to draw daily card: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to draw daily card")


@router.post("/readings", response_model=TarotReading)
async def create_tarot_reading(
    request: CreateReadingRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new tarot reading
    Optionally link to birth profile for holistic analysis
    """
    try:
        user_id = current_user["sub"]
        service = TarotService()

        # Determine number of cards
        num_cards = request.num_cards

        if not num_cards:
            # Get from spread if specified
            if request.spread_id:
                spread = await service.get_spread_by_id(request.spread_id)
                if spread:
                    num_cards = spread.get("num_cards", 1)
                else:
                    raise HTTPException(status_code=404, detail="Spread not found")
            else:
                # Default based on reading type
                type_defaults = {
                    "daily_card": 1,
                    "three_card": 3,
                    "celtic_cross": 10,
                    "custom": 3
                }
                num_cards = type_defaults.get(request.reading_type, 3)

        if num_cards < 1 or num_cards > 10:
            raise HTTPException(status_code=400, detail="Number of cards must be between 1 and 10")

        # Create reading
        result = await service.create_reading(
            user_id=user_id,
            spread_id=request.spread_id,
            spread_name=request.spread_name,
            reading_type=request.reading_type,
            num_cards=num_cards,
            question=request.question,
            profile_id=request.profile_id
        )

        return result["reading"]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create reading: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create reading: {str(e)}")


@router.get("/readings", response_model=TarotReadingListResponse)
async def get_tarot_readings(
    reading_type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's tarot readings
    """
    try:
        user_id = current_user["sub"]
        service = TarotService()

        result = await service.get_user_readings(
            user_id=user_id,
            limit=limit,
            reading_type=reading_type
        )

        # Transform to brief format
        readings_brief = [
            {
                "id": r["id"],
                "reading_type": r["reading_type"],
                "spread_name": r["spread_name"],
                "question": r.get("question"),
                "num_cards": len(r.get("cards_drawn", [])),
                "is_favorite": r.get("is_favorite", False),
                "created_at": r["created_at"]
            }
            for r in result["readings"]
        ]

        return {
            "readings": readings_brief,
            "total_count": result["total_count"]
        }

    except Exception as e:
        logger.error(f"Failed to fetch readings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch readings")


@router.get("/readings/{reading_id}", response_model=TarotReading)
async def get_tarot_reading(
    reading_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific tarot reading
    """
    try:
        user_id = current_user["sub"]
        service = TarotService()

        reading = await service.get_reading_by_id(reading_id, user_id)

        if not reading:
            raise HTTPException(status_code=404, detail="Reading not found")

        return reading

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch reading {reading_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch reading")


@router.patch("/readings/{reading_id}", response_model=TarotReading)
async def update_tarot_reading(
    reading_id: str,
    request: UpdateReadingRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update tarot reading (favorite status, notes)
    """
    try:
        user_id = current_user["sub"]
        service = TarotService()

        updated = await service.update_reading(
            reading_id=reading_id,
            user_id=user_id,
            is_favorite=request.is_favorite,
            notes=request.notes
        )

        if not updated:
            raise HTTPException(status_code=404, detail="Reading not found")

        return updated

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update reading {reading_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update reading")


@router.delete("/readings/{reading_id}")
async def delete_tarot_reading(
    reading_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a tarot reading
    """
    try:
        user_id = current_user["sub"]
        service = TarotService()

        # Verify ownership
        reading = await service.get_reading_by_id(reading_id, user_id)
        if not reading:
            raise HTTPException(status_code=404, detail="Reading not found")

        # Delete
        await service.supabase.delete(
            "tarot_readings",
            filters={"id": reading_id, "user_id": user_id}
        )

        return {"message": "Reading deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete reading {reading_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete reading")


@router.get("/stats", response_model=TarotStats)
async def get_tarot_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's tarot reading statistics
    """
    try:
        user_id = current_user["sub"]
        service = TarotService()

        result = await service.get_user_readings(user_id=user_id, limit=1000)
        readings = result["readings"]

        # Calculate stats
        total_readings = len(readings)
        daily_cards_drawn = len([r for r in readings if r["reading_type"] == "daily_card"])
        favorite_readings = len([r for r in readings if r.get("is_favorite", False)])

        # Count by type
        readings_by_type = {}
        for r in readings:
            rtype = r["reading_type"]
            readings_by_type[rtype] = readings_by_type.get(rtype, 0) + 1

        # Most recent reading
        recent_reading_date = readings[0]["created_at"] if readings else None

        # Most drawn card (would need to analyze cards_drawn)
        # For now, skip this complex calculation

        return {
            "total_readings": total_readings,
            "daily_cards_drawn": daily_cards_drawn,
            "favorite_readings": favorite_readings,
            "most_drawn_card": None,
            "readings_by_type": readings_by_type,
            "recent_reading_date": recent_reading_date
        }

    except Exception as e:
        logger.error(f"Failed to fetch stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")
