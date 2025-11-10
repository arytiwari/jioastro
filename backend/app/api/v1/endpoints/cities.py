"""Cities API Endpoints"""

from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional

from app.services.supabase_service import SupabaseService
from app.schemas.city import CityResponse, CityCreate, CityUpdate
from app.core.security import get_current_user
from fastapi import Depends

router = APIRouter()

# Initialize Supabase service
supabase_service = SupabaseService()


@router.get("/", response_model=List[CityResponse])
async def get_cities(
    search: Optional[str] = Query(None, description="Search by city or state name"),
    state: Optional[str] = Query(None, description="Filter by state"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results")
):
    """
    Get list of Indian cities with coordinates.

    - **search**: Search query for city or state name (case-insensitive partial match)
    - **state**: Filter by specific state
    - **limit**: Maximum number of results (default: 100, max: 500)
    """
    try:
        # Build query using Supabase
        # Start with base query
        if search:
            # Search by name (primary search field)
            response = (supabase_service.client.table("cities")
                       .select("*")
                       .ilike("name", f"%{search}%")
                       .order("name")
                       .limit(limit)
                       .execute())
        elif state:
            # Filter by state only
            response = (supabase_service.client.table("cities")
                       .select("*")
                       .ilike("state", f"%{state}%")
                       .order("name")
                       .limit(limit)
                       .execute())
        else:
            # No filters, return all cities
            response = (supabase_service.client.table("cities")
                       .select("*")
                       .order("name")
                       .limit(limit)
                       .execute())

        if not response.data:
            return []

        return response.data
    except Exception as e:
        print(f"Error in get_cities: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching cities: {str(e)}")


@router.get("/states", response_model=List[str])
async def get_states():
    """
    Get list of all Indian states that have cities in the database.
    """
    # Get distinct states from cities table
    response = supabase_service.client.table("cities").select("state").execute()

    if not response.data:
        return []

    # Extract unique states and sort them
    states = sorted(set(city["state"] for city in response.data if city.get("state")))

    return states


@router.get("/{city_id}", response_model=CityResponse)
async def get_city(city_id: int):
    """
    Get a specific city by ID.
    """
    response = supabase_service.client.table("cities").select("*").eq("id", city_id).execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(status_code=404, detail="City not found")

    return response.data[0]


@router.post("/", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def create_city(city_data: CityCreate):
    """
    Create a new city entry.
    This is automatically called when a user enters a custom city during profile creation.
    """
    try:
        # Auto-generate display_name if not provided
        if not city_data.display_name:
            city_data.display_name = f"{city_data.name}, {city_data.state}"

        # Check if city already exists (avoid duplicates)
        existing_city = supabase_service.client.table("cities").select("*").ilike("name", city_data.name).ilike("state", city_data.state).execute()

        if existing_city.data and len(existing_city.data) > 0:
            # City already exists, return it
            return existing_city.data[0]

        # Create new city
        city_dict = city_data.model_dump()
        response = supabase_service.client.table("cities").insert(city_dict).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create city")

        return response.data[0]
    except Exception as e:
        print(f"Error creating city: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating city: {str(e)}")


@router.post("/find-or-create", response_model=CityResponse)
async def find_or_create_city(city_data: CityCreate):
    """
    Find existing city or create new one.
    Used during profile creation to ensure city exists in database.
    """
    try:
        # Auto-generate display_name if not provided
        if not city_data.display_name:
            city_data.display_name = f"{city_data.name}, {city_data.state}"

        # Try to find existing city by name and coordinates (with small tolerance for coordinates)
        # This allows slight variations in coordinates from geocoding services
        lat_tolerance = 0.1  # ~11km
        lon_tolerance = 0.1

        response = (supabase_service.client.table("cities")
                   .select("*")
                   .ilike("name", city_data.name)
                   .gte("latitude", city_data.latitude - lat_tolerance)
                   .lte("latitude", city_data.latitude + lat_tolerance)
                   .gte("longitude", city_data.longitude - lon_tolerance)
                   .lte("longitude", city_data.longitude + lon_tolerance)
                   .execute())

        if response.data and len(response.data) > 0:
            # Found existing city
            return response.data[0]

        # City doesn't exist, create it
        city_dict = city_data.model_dump()
        create_response = supabase_service.client.table("cities").insert(city_dict).execute()

        if not create_response.data or len(create_response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create city")

        print(f"✅ Created new city: {city_data.display_name} ({city_data.latitude}, {city_data.longitude})")
        return create_response.data[0]
    except Exception as e:
        print(f"Error in find_or_create_city: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error finding/creating city: {str(e)}")


# Admin endpoints (require authentication)
@router.put("/{city_id}", response_model=CityResponse)
async def update_city(
    city_id: int,
    city_data: CityUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing city (Admin only).

    Requires authentication. Only fields provided will be updated.
    """
    try:
        # Check if city exists
        existing_city = supabase_service.client.table("cities").select("*").eq("id", city_id).execute()

        if not existing_city.data or len(existing_city.data) == 0:
            raise HTTPException(status_code=404, detail="City not found")

        # Build update data (only include fields that were provided)
        update_data = city_data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Update city
        response = (supabase_service.client.table("cities")
                   .update(update_data)
                   .eq("id", city_id)
                   .execute())

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to update city")

        print(f"✅ Updated city ID {city_id}: {update_data}")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating city: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating city: {str(e)}")


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_city(
    city_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a city (Admin only).

    Requires authentication.
    """
    try:
        # Check if city exists
        existing_city = supabase_service.client.table("cities").select("*").eq("id", city_id).execute()

        if not existing_city.data or len(existing_city.data) == 0:
            raise HTTPException(status_code=404, detail="City not found")

        # Delete city
        supabase_service.client.table("cities").delete().eq("id", city_id).execute()

        print(f"✅ Deleted city ID {city_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting city: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting city: {str(e)}")
