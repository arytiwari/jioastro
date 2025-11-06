"""Query and AI Interpretation Endpoints - Using Supabase REST API"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta, date, time, timezone

from app.schemas.query import QueryCreate, QueryResponse
from app.schemas.response import ResponseResponse
from app.core.security import get_current_user
from app.core.config import settings
from app.services.astrology import astrology_service
from app.services.ai_service import ai_service
from app.services.supabase_service import supabase_service

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_query(
    query_data: QueryCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit a query and receive AI-powered interpretation
    Includes rate limiting
    """
    try:
        user_id = current_user["user_id"]

        # Rate limiting: Check queries in last 24 hours
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        recent_queries = await supabase_service.get_queries(user_id=user_id, limit=1000)
        recent_count = len([q for q in recent_queries if q.get("created_at") and datetime.fromisoformat(q["created_at"].replace("Z", "+00:00")) >= yesterday])

        if recent_count >= settings.RATE_LIMIT_QUERIES_PER_DAY:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily query limit ({settings.RATE_LIMIT_QUERIES_PER_DAY}) reached. Please try again tomorrow."
            )

        # Verify profile belongs to user
        profile = await supabase_service.get_profile(
            profile_id=query_data.profile_id,
            user_id=user_id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Get or calculate chart
        chart = await supabase_service.get_chart(
            profile_id=query_data.profile_id,
            chart_type="D1"
        )

        if not chart:
            # Calculate chart if it doesn't exist
            try:
                # Handle different date/time formats from Supabase
                if isinstance(profile['birth_date'], str):
                    birth_date = datetime.fromisoformat(profile['birth_date']).date()
                else:
                    birth_date = profile['birth_date']

                if isinstance(profile['birth_time'], str):
                    # Parse time string - could be HH:MM:SS or just HH:MM
                    birth_time = datetime.fromisoformat(f"2000-01-01T{profile['birth_time']}").time()
                else:
                    birth_time = profile['birth_time']

                # Ensure all parameters are in the correct format
                latitude = float(str(profile['birth_lat']))
                longitude = float(str(profile['birth_lon']))
                timezone_str = str(profile.get('birth_timezone') or 'UTC')
                city = str(profile.get('birth_city') or 'Unknown')

                chart_data = astrology_service.calculate_birth_chart(
                    name=profile['name'],
                    birth_date=birth_date,
                    birth_time=birth_time,
                    latitude=latitude,
                    longitude=longitude,
                    timezone_str=timezone_str,
                    city=city
                )

                chart = await supabase_service.create_chart({
                    "profile_id": str(query_data.profile_id),  # Convert UUID to string
                    "chart_type": "D1",
                    "chart_data": chart_data
                })
            except Exception as e:
                print(f"Error calculating chart: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to calculate birth chart: {str(e)}"
                )

        # Fetch numerology data for holistic reading
        numerology_data = None
        try:
            print(f"🔢 Fetching numerology profile for holistic reading...")
            # Get numerology profiles for this user's birth profile
            numerology_profiles = await supabase_service.get_numerology_profiles(
                user_id=user_id,
                profile_id=str(query_data.profile_id)
            )

            if numerology_profiles and len(numerology_profiles) > 0:
                # Use the most recent numerology profile
                latest_profile = numerology_profiles[0]
                numerology_data = {
                    "western": latest_profile.get("western_data"),
                    "vedic": latest_profile.get("vedic_data"),
                    "full_name": latest_profile.get("full_name"),
                    "birth_date": latest_profile.get("birth_date"),
                    "system": latest_profile.get("system")
                }
                print(f"✅ Numerology data found: {numerology_data.get('system')} system")
            else:
                print(f"ℹ️  No numerology profile found for this user/profile")
        except Exception as e:
            print(f"⚠️  Could not fetch numerology data: {str(e)}")
            # Continue without numerology data

        # Generate AI interpretation with all available data
        try:
            print(f"🤖 Generating AI interpretation for question: {query_data.question[:50]}...")
            print(f"📊 Chart data available: {bool(chart.get('chart_data'))}")
            print(f"🔢 Numerology data available: {bool(numerology_data)}")

            ai_result = await ai_service.generate_interpretation(
                chart_data=chart.get("chart_data", {}),
                question=query_data.question,
                category=query_data.category or "general",
                numerology_data=numerology_data
            )

            print(f"✅ AI interpretation generated: {len(ai_result.get('interpretation', ''))} characters")
            print(f"🎯 Model used: {ai_result.get('model')}")
        except Exception as e:
            print(f"❌ Error generating AI interpretation: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate interpretation: {str(e)}"
            )

        # Create query record
        print(f"💾 Creating query record...")
        new_query = await supabase_service.create_query({
            "user_id": user_id,
            "profile_id": str(query_data.profile_id),  # Convert UUID to string
            "question": query_data.question,
            "category": query_data.category
        })
        print(f"✅ Query created with ID: {new_query.get('id')}")

        # Create response record
        print(f"💾 Creating response record...")
        new_response = await supabase_service.create_response({
            "query_id": new_query["id"],
            "interpretation": ai_result["interpretation"],
            "ai_model": ai_result["model"],
            "tokens_used": ai_result.get("tokens_used", 0)
        })
        print(f"✅ Response created with ID: {new_response.get('id')}")

        return {
            "query": new_query,
            "response": new_response
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


@router.get("/", response_model=List[QueryResponse])
async def list_queries(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """List queries for the current user with pagination"""
    try:
        queries = await supabase_service.get_queries(
            user_id=current_user["user_id"],
            limit=limit,
            offset=offset
        )
        return queries
    except Exception as e:
        print(f"Error listing queries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list queries: {str(e)}"
        )


@router.get("/{query_id}", response_model=QueryResponse)
async def get_query(
    query_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific query with its response"""
    try:
        query = await supabase_service.get_query(
            query_id=query_id,
            user_id=current_user["user_id"]
        )

        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found"
            )

        return query
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get query: {str(e)}"
        )
