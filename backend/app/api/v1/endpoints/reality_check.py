"""
Reality Check Loop API Endpoints
Learning from prediction outcomes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.core.security import get_current_user
from app.services.reality_check_service import reality_check_service
from app.schemas.reality_check import (
    # Request schemas
    CreatePrediction,
    UpdatePrediction,
    CreateOutcome,
    UpdateOutcome,
    CreateLearningInsight,
    PredictionFilters,
    OutcomeFilters,
    # Response schemas
    Prediction,
    PredictionWithOutcome,
    PredictionList,
    PredictionOutcome,
    LearningInsight,
    LearningInsightList,
    UserAccuracyStats,
    RealityCheckDashboard,
    # Enums
    PredictionStatus,
    PredictionCategory,
    PredictionType,
    InsightType,
)

router = APIRouter()


# =====================================================
# PREDICTION ENDPOINTS
# =====================================================

@router.post("/predictions", response_model=Prediction, status_code=201)
async def create_prediction(
    prediction_data: CreatePrediction,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new prediction

    Stores a prediction made by the system that can later be verified by the user.
    """
    try:
        result = await reality_check_service.create_prediction(
            user_id=current_user["user_id"],
            prediction_data=prediction_data.model_dump(exclude_unset=True),
        )

        if not result:
            raise HTTPException(status_code=500, detail="Failed to create prediction")

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions", response_model=PredictionList)
async def get_predictions(
    status: Optional[PredictionStatus] = None,
    category: Optional[PredictionCategory] = None,
    prediction_type: Optional[PredictionType] = None,
    profile_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    """
    Get user's predictions with optional filters

    Returns a paginated list of predictions with counts for outcomes.
    """
    try:
        filters = {}
        if status:
            filters["status"] = status
        if category:
            filters["category"] = category
        if prediction_type:
            filters["prediction_type"] = prediction_type
        if profile_id:
            filters["profile_id"] = profile_id

        result = await reality_check_service.get_predictions(
            user_id=current_user["user_id"],
            filters=filters,
            limit=limit,
            offset=offset,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{prediction_id}", response_model=PredictionWithOutcome)
async def get_prediction(
    prediction_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get a specific prediction with its outcome (if any)
    """
    try:
        prediction = await reality_check_service.get_prediction(
            prediction_id=prediction_id,
            user_id=current_user["user_id"],
        )

        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")

        # Get outcome if exists
        outcome = await reality_check_service.get_outcome(
            prediction_id=prediction_id,
            user_id=current_user["user_id"],
        )

        return {**prediction, "outcome": outcome}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/predictions/{prediction_id}", response_model=Prediction)
async def update_prediction(
    prediction_id: str,
    updates: UpdatePrediction,
    current_user: dict = Depends(get_current_user),
):
    """
    Update a prediction
    """
    try:
        result = await reality_check_service.update_prediction(
            prediction_id=prediction_id,
            user_id=current_user["user_id"],
            updates=updates.model_dump(exclude_unset=True),
        )

        if not result:
            raise HTTPException(status_code=404, detail="Prediction not found")

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/predictions/{prediction_id}", status_code=204)
async def delete_prediction(
    prediction_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a prediction
    """
    try:
        await reality_check_service.delete_prediction(
            prediction_id=prediction_id,
            user_id=current_user["user_id"],
        )

        return None

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# OUTCOME ENDPOINTS
# =====================================================

@router.post("/outcomes", response_model=PredictionOutcome, status_code=201)
async def create_outcome(
    outcome_data: CreateOutcome,
    current_user: dict = Depends(get_current_user),
):
    """
    Record an outcome for a prediction

    This endpoint records what actually happened and calculates accuracy.
    """
    try:
        result = await reality_check_service.create_outcome(
            user_id=current_user["user_id"],
            outcome_data=outcome_data.model_dump(exclude_unset=True),
        )

        if not result:
            raise HTTPException(status_code=500, detail="Failed to create outcome")

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outcomes/{prediction_id}", response_model=PredictionOutcome)
async def get_outcome(
    prediction_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get outcome for a specific prediction
    """
    try:
        outcome = await reality_check_service.get_outcome(
            prediction_id=prediction_id,
            user_id=current_user["user_id"],
        )

        if not outcome:
            raise HTTPException(status_code=404, detail="Outcome not found")

        return outcome

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/outcomes/{outcome_id}", response_model=PredictionOutcome)
async def update_outcome(
    outcome_id: str,
    updates: UpdateOutcome,
    current_user: dict = Depends(get_current_user),
):
    """
    Update an outcome
    """
    try:
        result = await reality_check_service.update_outcome(
            outcome_id=outcome_id,
            user_id=current_user["user_id"],
            updates=updates.model_dump(exclude_unset=True),
        )

        if not result:
            raise HTTPException(status_code=404, detail="Outcome not found")

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# LEARNING INSIGHTS ENDPOINTS
# =====================================================

@router.get("/insights", response_model=LearningInsightList)
async def get_insights(
    category: Optional[PredictionCategory] = None,
    insight_type: Optional[InsightType] = None,
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    """
    Get learning insights

    Returns system-generated insights learned from prediction outcomes.
    """
    try:
        result = await reality_check_service.get_insights(
            category=category,
            insight_type=insight_type,
            limit=limit,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ACCURACY METRICS ENDPOINTS
# =====================================================

@router.get("/stats", response_model=UserAccuracyStats)
async def get_user_stats(
    current_user: dict = Depends(get_current_user),
):
    """
    Get user's accuracy statistics

    Returns comprehensive stats about prediction accuracy for the user.
    """
    try:
        stats = await reality_check_service.get_user_accuracy_stats(
            user_id=current_user["user_id"]
        )

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", response_model=RealityCheckDashboard)
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
):
    """
    Get complete dashboard data

    Returns all data needed for the Reality Check Loop dashboard:
    - User statistics
    - Recent predictions
    - Pending outcomes
    - Category accuracy
    - Confidence calibration
    - Monthly trends
    - Top insights
    """
    try:
        dashboard_data = await reality_check_service.get_dashboard_data(
            user_id=current_user["user_id"]
        )

        return dashboard_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ADMIN ENDPOINTS (for creating insights)
# =====================================================

@router.post("/admin/insights", response_model=LearningInsight, status_code=201)
async def create_insight(
    insight_data: CreateLearningInsight,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a learning insight (admin/system only)

    This endpoint is for creating system-generated insights from analysis.
    """
    try:
        # TODO: Add admin role check
        # if not current_user.get("is_admin"):
        #     raise HTTPException(status_code=403, detail="Admin access required")

        result = await reality_check_service.create_insight(
            insight_data=insight_data.model_dump(exclude_unset=True),
        )

        if not result:
            raise HTTPException(status_code=500, detail="Failed to create insight")

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
