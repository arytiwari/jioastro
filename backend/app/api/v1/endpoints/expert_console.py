"""
Expert Console API Endpoints
Professional astrologer tools: settings, rectification, bulk analysis, presets
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.core.security import get_current_user
from app.services.expert_console_service import expert_console_service
from app.schemas.expert_console import (
    # Request schemas
    ExpertSettingsUpdate,
    CreateRectificationSession,
    CreateBulkAnalysisJob,
    CreateCalculationPreset,
    # Response schemas
    ExpertSettings,
    ExpertConsoleStats,
    RectificationSession,
    RectificationSessionList,
    BulkAnalysisJob,
    BulkAnalysisJobList,
    CalculationPreset,
    CalculationPresetList
)

router = APIRouter()


# =============================================================================
# EXPERT SETTINGS
# =============================================================================

@router.get("/settings", response_model=ExpertSettings)
async def get_expert_settings(
    current_user: dict = Depends(get_current_user)
):
    """Get or create expert settings for current user"""
    try:
        settings = await expert_console_service.get_or_create_settings(
            user_id=current_user["user_id"]
        )
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/settings", response_model=ExpertSettings)
async def update_expert_settings(
    settings_update: ExpertSettingsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update expert settings"""
    try:
        # Convert to dict and remove None values
        update_data = {
            k: v for k, v in settings_update.dict().items() if v is not None
        }

        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        updated_settings = await expert_console_service.update_settings(
            user_id=current_user["user_id"],
            settings_update=update_data
        )

        if not updated_settings:
            raise HTTPException(status_code=404, detail="Settings not found")

        return updated_settings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=ExpertConsoleStats)
async def get_expert_console_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get usage statistics for expert console"""
    try:
        stats = await expert_console_service.get_settings_stats(
            user_id=current_user["user_id"]
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# BIRTH TIME RECTIFICATION
# =============================================================================

@router.post("/rectification", response_model=RectificationSession)
async def create_rectification_session(
    session_data: CreateRectificationSession,
    current_user: dict = Depends(get_current_user)
):
    """Create a birth time rectification session"""
    try:
        session = await expert_console_service.create_rectification_session(
            user_id=current_user["user_id"],
            session_data=session_data.dict()
        )

        if not session:
            raise HTTPException(status_code=500, detail="Failed to create rectification session")

        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rectification", response_model=RectificationSessionList)
async def get_rectification_sessions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get user's rectification sessions"""
    try:
        result = await expert_console_service.get_rectification_sessions(
            user_id=current_user["user_id"],
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rectification/{session_id}", response_model=RectificationSession)
async def get_rectification_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific rectification session"""
    try:
        session = await expert_console_service.get_rectification_session(
            session_id=session_id,
            user_id=current_user["user_id"]
        )

        if not session:
            raise HTTPException(status_code=404, detail="Rectification session not found")

        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rectification/{session_id}/process")
async def process_rectification_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Process a rectification session
    WARNING: This can take several minutes for large time windows
    """
    try:
        result = await expert_console_service.process_rectification(
            session_id=session_id,
            user_id=current_user["user_id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rectification/{session_id}")
async def delete_rectification_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a rectification session"""
    try:
        deleted = await expert_console_service.delete_rectification_session(
            session_id=session_id,
            user_id=current_user["user_id"]
        )

        if not deleted:
            raise HTTPException(status_code=404, detail="Rectification session not found")

        return {"message": "Rectification session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# BULK ANALYSIS JOBS
# =============================================================================

@router.post("/bulk-jobs", response_model=BulkAnalysisJob)
async def create_bulk_analysis_job(
    job_data: CreateBulkAnalysisJob,
    current_user: dict = Depends(get_current_user)
):
    """Create a bulk analysis job"""
    try:
        job = await expert_console_service.create_bulk_job(
            user_id=current_user["user_id"],
            job_data=job_data.dict()
        )

        if not job:
            raise HTTPException(status_code=500, detail="Failed to create bulk job")

        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bulk-jobs", response_model=BulkAnalysisJobList)
async def get_bulk_analysis_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get user's bulk analysis jobs"""
    try:
        result = await expert_console_service.get_bulk_jobs(
            user_id=current_user["user_id"],
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bulk-jobs/{job_id}", response_model=BulkAnalysisJob)
async def get_bulk_analysis_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific bulk analysis job"""
    try:
        job = await expert_console_service.get_bulk_job(
            job_id=job_id,
            user_id=current_user["user_id"]
        )

        if not job:
            raise HTTPException(status_code=404, detail="Bulk job not found")

        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-jobs/{job_id}/process")
async def process_bulk_analysis_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Process a bulk analysis job
    WARNING: This can take several minutes for large datasets
    In production, this should be handled by a background worker (Celery/RQ)
    """
    try:
        result = await expert_console_service.process_bulk_job(
            job_id=job_id,
            user_id=current_user["user_id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/bulk-jobs/{job_id}")
async def delete_bulk_analysis_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a bulk analysis job"""
    try:
        deleted = await expert_console_service.delete_bulk_job(
            job_id=job_id,
            user_id=current_user["user_id"]
        )

        if not deleted:
            raise HTTPException(status_code=404, detail="Bulk job not found")

        return {"message": "Bulk job deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# CALCULATION PRESETS
# =============================================================================

@router.post("/presets", response_model=CalculationPreset)
async def create_calculation_preset(
    preset_data: CreateCalculationPreset,
    current_user: dict = Depends(get_current_user)
):
    """Create a calculation preset"""
    try:
        preset = await expert_console_service.create_preset(
            user_id=current_user["user_id"],
            preset_data=preset_data.dict()
        )

        if not preset:
            raise HTTPException(status_code=500, detail="Failed to create preset")

        return preset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets", response_model=CalculationPresetList)
async def get_calculation_presets(
    include_public: bool = Query(True),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get user's calculation presets and optionally public presets"""
    try:
        result = await expert_console_service.get_presets(
            user_id=current_user["user_id"],
            include_public=include_public,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets/{preset_id}", response_model=CalculationPreset)
async def get_calculation_preset(
    preset_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific calculation preset"""
    try:
        preset = await expert_console_service.get_preset(
            preset_id=preset_id,
            user_id=current_user["user_id"]
        )

        if not preset:
            raise HTTPException(
                status_code=404,
                detail="Preset not found or access denied"
            )

        return preset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/presets/{preset_id}", response_model=CalculationPreset)
async def update_calculation_preset(
    preset_id: str,
    preset_update: CreateCalculationPreset,
    current_user: dict = Depends(get_current_user)
):
    """Update a calculation preset (only owner can update)"""
    try:
        # Convert to dict and remove None values
        update_data = {
            k: v for k, v in preset_update.dict().items() if v is not None
        }

        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        updated_preset = await expert_console_service.update_preset(
            preset_id=preset_id,
            user_id=current_user["user_id"],
            update_data=update_data
        )

        if not updated_preset:
            raise HTTPException(
                status_code=404,
                detail="Preset not found or access denied"
            )

        return updated_preset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presets/{preset_id}/use")
async def use_calculation_preset(
    preset_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Increment usage count for a preset
    Call this when applying a preset to a chart calculation
    """
    try:
        await expert_console_service.increment_preset_usage(preset_id=preset_id)
        return {"message": "Preset usage recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/presets/{preset_id}")
async def delete_calculation_preset(
    preset_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a calculation preset (only owner can delete)"""
    try:
        deleted = await expert_console_service.delete_preset(
            preset_id=preset_id,
            user_id=current_user["user_id"]
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Preset not found or access denied"
            )

        return {"message": "Preset deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
