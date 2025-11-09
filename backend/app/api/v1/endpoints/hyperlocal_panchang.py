"""
Hyperlocal Panchang API Endpoints
Location-based daily Panchang with personalized guidance
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import date
from decimal import Decimal

from app.core.security import get_current_user
from app.core.supabase_client import SupabaseClient
from app.db.database import get_supabase_client
from app.services.hyperlocal_panchang_service import HyperlocalPanchangService
from app.schemas.hyperlocal_panchang import (
    GetPanchangRequest,
    SubscribeLocationRequest,
    UpdatePanchangPreferencesRequest,
    Panchang,
    PanchangSubscription,
    PanchangPreferences
)

router = APIRouter()


@router.post("/calculate", response_model=Panchang)
async def calculate_panchang(
    request: GetPanchangRequest,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Calculate complete Panchang for date and location

    - Tithi, Nakshatra, Yoga, Karana, Vara
    - Sun/Moon rise/set times
    - Rahukaal, Hora sequence (24 planetary hours)
    - Auspicious/Inauspicious times
    - Special day detection (Ekadashi, Amavasya, Purnima)
    - Cached for performance

    Public endpoint - no authentication required
    """
    service = HyperlocalPanchangService(supabase)

    try:
        return await service.get_panchang(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Panchang calculation failed: {str(e)}")


@router.get("/today", response_model=Panchang)
async def get_today_panchang(
    latitude: Decimal = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: Decimal = Query(..., ge=-180, le=180, description="Longitude"),
    timezone: str = Query(..., description="IANA timezone e.g., 'Asia/Kolkata'"),
    location_name: Optional[str] = Query(None, description="Location name"),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Get today's Panchang for location

    Quick endpoint for current date
    """
    service = HyperlocalPanchangService(supabase)

    request = GetPanchangRequest(
        panchang_date=date.today(),
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        location_name=location_name
    )

    try:
        return await service.get_panchang(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Panchang calculation failed: {str(e)}")


# Location Subscriptions

@router.post("/subscriptions", response_model=PanchangSubscription, status_code=201)
async def subscribe_location(
    request: SubscribeLocationRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Subscribe to a location for daily Panchang notifications

    - Save frequently used locations
    - Set primary location
    - Configure notification time
    - Receive daily Panchang alerts
    """
    service = HyperlocalPanchangService(supabase)
    user_id = current_user["sub"]

    try:
        return await service.subscribe_location(user_id, request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions")
async def list_subscriptions(
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """List user's location subscriptions"""
    service = HyperlocalPanchangService(supabase)
    user_id = current_user["sub"]

    subscriptions = await service.list_subscriptions(user_id)
    return {"subscriptions": subscriptions}


@router.delete("/subscriptions/{subscription_id}", status_code=204)
async def delete_subscription(
    subscription_id: str,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Delete a location subscription"""
    user_id = current_user["sub"]

    await supabase.delete(
        "panchang_subscriptions",
        filters={"id": subscription_id, "user_id": user_id}
    )
    return None


# Preferences

@router.get("/preferences", response_model=PanchangPreferences)
async def get_preferences(
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Get user's Panchang display preferences"""
    user_id = current_user["sub"]

    result = await supabase.select(
        "panchang_preferences",
        filters={"user_id": user_id}
    )

    if not result or len(result) == 0:
        # Create default preferences
        default_prefs = {
            "user_id": user_id,
            "show_tithi": True,
            "show_nakshatra": True,
            "show_yoga": True,
            "show_karana": True,
            "show_rahukaal": True,
            "show_hora": True,
            "show_festivals": True,
            "notify_on_ekadashi": False,
            "notify_on_amavasya": False,
            "notify_on_purnima": False,
            "notify_on_festivals": True,
            "notify_before_rahukaal": False,
            "calendar_sync_enabled": False
        }
        result = await supabase.insert("panchang_preferences", default_prefs)

    return PanchangPreferences(**result[0])


@router.put("/preferences", response_model=PanchangPreferences)
async def update_preferences(
    request: UpdatePanchangPreferencesRequest,
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Update Panchang display preferences"""
    user_id = current_user["sub"]

    # Build update data
    update_data = {}
    if request.show_tithi is not None:
        update_data["show_tithi"] = request.show_tithi
    if request.show_nakshatra is not None:
        update_data["show_nakshatra"] = request.show_nakshatra
    if request.show_yoga is not None:
        update_data["show_yoga"] = request.show_yoga
    if request.show_karana is not None:
        update_data["show_karana"] = request.show_karana
    if request.show_rahukaal is not None:
        update_data["show_rahukaal"] = request.show_rahukaal
    if request.show_hora is not None:
        update_data["show_hora"] = request.show_hora
    if request.show_festivals is not None:
        update_data["show_festivals"] = request.show_festivals
    if request.notify_on_ekadashi is not None:
        update_data["notify_on_ekadashi"] = request.notify_on_ekadashi
    if request.notify_on_amavasya is not None:
        update_data["notify_on_amavasya"] = request.notify_on_amavasya
    if request.notify_on_purnima is not None:
        update_data["notify_on_purnima"] = request.notify_on_purnima
    if request.notify_on_festivals is not None:
        update_data["notify_on_festivals"] = request.notify_on_festivals
    if request.notify_before_rahukaal is not None:
        update_data["notify_before_rahukaal"] = request.notify_before_rahukaal
    if request.calendar_sync_enabled is not None:
        update_data["calendar_sync_enabled"] = request.calendar_sync_enabled
    if request.calendar_provider is not None:
        update_data["calendar_provider"] = request.calendar_provider

    result = await supabase.update(
        "panchang_preferences",
        filters={"user_id": user_id},
        data=update_data
    )

    if not result or len(result) == 0:
        raise HTTPException(status_code=404, detail="Preferences not found")

    return PanchangPreferences(**result[0])
