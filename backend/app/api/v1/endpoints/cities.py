"""Cities API Endpoints"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional

from app.services.supabase_service import SupabaseService
from app.schemas.city import CityResponse

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
