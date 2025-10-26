"""Query and AI Interpretation Endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.profile import Profile
from app.models.chart import Chart
from app.models.query import Query
from app.models.response import Response as ResponseModel
from app.schemas.query import QueryCreate, QueryResponse
from app.schemas.response import ResponseResponse
from app.core.security import get_current_user
from app.core.config import settings
from app.services.astrology import astrology_service
from app.services.ai_service import ai_service

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_query(
    query_data: QueryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Submit a query and receive AI-powered interpretation
    Includes rate limiting
    """

    user_id = UUID(current_user["user_id"])

    # Rate limiting: Check queries in last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    count_result = await db.execute(
        select(func.count(Query.id))
        .where(Query.user_id == user_id, Query.created_at >= yesterday)
    )
    query_count = count_result.scalar()

    if query_count >= settings.RATE_LIMIT_QUERIES_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily query limit ({settings.RATE_LIMIT_QUERIES_PER_DAY}) reached. Please try again tomorrow."
        )

    # Verify profile belongs to user
    profile_result = await db.execute(
        select(Profile).where(
            Profile.id == query_data.profile_id,
            Profile.user_id == user_id
        )
    )

    profile = profile_result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Get or calculate D1 chart
    chart_result = await db.execute(
        select(Chart).where(
            Chart.profile_id == query_data.profile_id,
            Chart.chart_type == "D1"
        )
    )

    chart = chart_result.scalar_one_or_none()

    # If chart doesn't exist, calculate it
    if not chart:
        try:
            chart_data = astrology_service.calculate_birth_chart(
                name=profile.name,
                birth_date=profile.birth_date,
                birth_time=profile.birth_time,
                latitude=float(profile.birth_lat),
                longitude=float(profile.birth_lon),
                timezone_str=profile.birth_timezone or "UTC",
                city=profile.birth_city or "Unknown"
            )

            chart = Chart(
                profile_id=query_data.profile_id,
                chart_type="D1",
                chart_data=chart_data
            )

            db.add(chart)
            await db.flush()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chart calculation failed: {str(e)}"
            )
    else:
        chart_data = chart.chart_data

    # Create query record
    new_query = Query(
        user_id=user_id,
        profile_id=query_data.profile_id,
        question=query_data.question,
        category=query_data.category
    )

    db.add(new_query)
    await db.flush()

    # Generate AI interpretation
    try:
        ai_response = ai_service.generate_interpretation(
            chart_data=chart_data,
            question=query_data.question,
            category=query_data.category or "general"
        )

        # Save response
        new_response = ResponseModel(
            query_id=new_query.id,
            interpretation=ai_response["interpretation"],
            ai_model=ai_response["model"],
            tokens_used=ai_response.get("tokens_used", 0)
        )

        db.add(new_response)
        await db.commit()
        await db.refresh(new_query)
        await db.refresh(new_response)

        return {
            "query": QueryResponse.model_validate(new_query),
            "response": ResponseResponse.model_validate(new_response)
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI interpretation failed: {str(e)}"
        )


@router.get("/", response_model=List[dict])
async def list_queries(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List user's query history with responses"""

    user_id = UUID(current_user["user_id"])

    # Get queries
    query_result = await db.execute(
        select(Query)
        .where(Query.user_id == user_id)
        .order_by(Query.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    queries = query_result.scalars().all()

    # Get responses for each query
    result_list = []
    for query in queries:
        response_result = await db.execute(
            select(ResponseModel).where(ResponseModel.query_id == query.id)
        )
        response = response_result.scalar_one_or_none()

        result_list.append({
            "query": QueryResponse.model_validate(query),
            "response": ResponseResponse.model_validate(response) if response else None
        })

    return result_list


@router.get("/{query_id}", response_model=dict)
async def get_query(
    query_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific query and its response"""

    user_id = UUID(current_user["user_id"])

    # Get query
    query_result = await db.execute(
        select(Query).where(
            Query.id == query_id,
            Query.user_id == user_id
        )
    )

    query = query_result.scalar_one_or_none()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )

    # Get response
    response_result = await db.execute(
        select(ResponseModel).where(ResponseModel.query_id == query_id)
    )

    response = response_result.scalar_one_or_none()

    return {
        "query": QueryResponse.model_validate(query),
        "response": ResponseResponse.model_validate(response) if response else None
    }
