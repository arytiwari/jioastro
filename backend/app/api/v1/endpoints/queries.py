"""Query and AI Interpretation Endpoints - Using Supabase REST API"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta

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
        yesterday = datetime.utcnow() - timedelta(days=1)
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
                # Parse date/time strings from database
                from datetime import date, time
                birth_date = date.fromisoformat(profile['birth_date'])
                birth_time = time.fromisoformat(profile['birth_time'])

                chart_data = astrology_service.calculate_birth_chart(
                    name=profile['name'],
                    birth_date=birth_date,
                    birth_time=birth_time,
                    latitude=float(profile['birth_lat']),
                    longitude=float(profile['birth_lon']),
                    timezone_str=profile.get('birth_timezone', 'UTC'),
                    city=profile.get('birth_city', 'Unknown')
                )

                chart = await supabase_service.create_chart({
                    "profile_id": query_data.profile_id,
                    "chart_type": "D1",
                    "chart_data": chart_data
                })
            except Exception as e:
                print(f"Error calculating chart: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to calculate birth chart: {str(e)}"
                )

        # Generate AI interpretation
        try:
            ai_result = ai_service.generate_interpretation(
                chart_data=chart.get("chart_data", {}),
                question=query_data.question,
                category=query_data.category or "general"
            )
        except Exception as e:
            print(f"Error generating AI interpretation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate interpretation: {str(e)}"
            )

        # Create query record
        new_query = await supabase_service.create_query({
            "user_id": user_id,
            "profile_id": query_data.profile_id,
            "question": query_data.question,
            "category": query_data.category
        })

        # Create response record
        new_response = await supabase_service.create_response({
            "query_id": new_query["id"],
            "interpretation": ai_result["interpretation"],
            "model_used": ai_result["model"],
            "tokens_used": ai_result.get("tokens_used", 0)
        })

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
