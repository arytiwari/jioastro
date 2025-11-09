"""
Palmistry API Endpoints.

Provides REST API for palm reading operations including:
- Image upload and validation
- Palm analysis and interpretation
- Reading history and comparison
- Feedback collection

Uses Supabase REST API client instead of SQLAlchemy.
"""

import logging
import traceback
from datetime import datetime
from typing import List, Optional
# UUID imports removed - now using strings for all IDs

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

from app.core.security import get_current_user
from app.core.supabase_client import SupabaseClient
from app.schemas.palmistry import (
    ImageUploadRequest,
    ImageUploadResponse,
    AnalysisRequest,
    AnalysisResponse,
    FeedbackRequest,
    ReadingListResponse,
    ReadingListItem,
    UserReadingStats,
    ComparisonResponse,
    HealthCheckResponse,
    ModelInfo,
    ErrorResponse,
    PalmReading as PalmReadingSchema,
    PalmInterpretation as PalmInterpretationSchema,
)
from app.services.palmistry_storage_service import PalmistryStorageService
from app.services.palm_analysis_service import PalmAnalysisService


logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# IMAGE UPLOAD ENDPOINTS
# ============================================================================

@router.post(
    "/upload",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload palm image",
    description="Upload a palm image for analysis. Supports both camera capture and file upload."
)
async def upload_palm_image(
    request: ImageUploadRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and validate palm image.

    This endpoint:
    1. Validates image quality (focus, lighting, size)
    2. Uploads image to storage
    3. Generates thumbnail
    4. Creates photo record in database
    5. Returns validation results and URLs

    Args:
        request: Image upload request with base64 image data
        current_user: Authenticated user

    Returns:
        ImageUploadResponse with photo ID, URLs, and validation results

    Raises:
        400: Image validation failed
        500: Upload or processing error
    """
    try:
        user_id = current_user["user_id"]
        storage_service = PalmistryStorageService()
        supabase = SupabaseClient()

        # Upload image and generate thumbnail
        image_url, thumbnail_url, metadata, validation = await storage_service.upload_palm_image(
            image_data=request.image,
            user_id=user_id,  # Pass as string, not UUID
            hand_type=request.hand_type,
            view_type=request.view_type,
            device_info=request.device_info.dict() if request.device_info else None
        )

        # Create photo record in database
        photo_data = {
            "user_id": user_id,
            "hand_type": request.hand_type,
            "view_type": request.view_type,
            "capture_method": request.capture_method,
            "image_url": image_url,
            "thumbnail_url": thumbnail_url,
            "image_metadata": metadata,
            "quality_score": validation.quality_score,
            "focus_score": metadata.get("focus_score"),
            "lighting_score": metadata.get("lighting_score"),
            "is_hand_detected": validation.is_hand_detected,
            "validation_details": validation.dict(),
            "device_info": request.device_info.dict() if request.device_info else {},
            "profile_id": request.profile_id if request.profile_id else None,  # Link to birth profile
            "created_at": datetime.utcnow().isoformat()
        }

        photo = await supabase.insert("palm_photos", photo_data)
        logger.info(f"Palm image uploaded successfully: photo_id={photo['id']}")

        return ImageUploadResponse(
            photo_id=str(photo["id"]),  # Convert UUID to string for JSON serialization
            thumbnail_url=thumbnail_url,
            image_url=image_url,
            quality_score=validation.quality_score,
            validation=validation,
            created_at=photo["created_at"]
        )

    except ValueError as e:
        # Validation errors
        error_msg = str(e) or repr(e)
        logger.error(f"Image validation failed: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except Exception as e:
        error_msg = str(e) or repr(e)
        logger.error(f"Image upload failed: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {error_msg}"
        )


# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze palm image",
    description="Trigger AI analysis of uploaded palm image(s)"
)
async def analyze_palm(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze palm image using AI models.

    This endpoint:
    1. Validates photo ownership
    2. Runs AI models (hand detection, line detection, mount detection)
    3. Generates RAG-based interpretation
    4. Stores results in database
    5. Returns complete reading and interpretation

    Args:
        request: Analysis request with photo IDs
        background_tasks: FastAPI background tasks
        current_user: Authenticated user

    Returns:
        AnalysisResponse with reading and interpretation

    Raises:
        404: Photo not found
        400: Invalid request
        500: Analysis error
    """
    try:
        user_id = current_user["user_id"]
        supabase = SupabaseClient()

        # For now, analyze only the first photo
        photo_id = request.photo_ids[0]

        # Verify photo ownership
        photo = await supabase.select(
            "palm_photos",
            filters={"id": photo_id, "user_id": user_id},
            single=True
        )

        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo not found"
            )

        # Get profile_id from photo if linked
        profile_id = photo.get("profile_id")

        # Run analysis (will fetch holistic data if profile_id is provided)
        analysis_service = PalmAnalysisService()
        analysis_result = await analysis_service.analyze_palm(
            photo_id=photo_id,
            image_url=photo["image_url"],
            hand_type=photo["hand_type"],
            view_type=photo["view_type"],
            profile_id=profile_id,  # Pass profile_id for holistic analysis
            user_id=user_id
        )

        # Store reading in database
        reading_data = {
            "photo_id": str(photo_id),
            "user_id": str(user_id),
            "profile_id": str(profile_id) if profile_id else None,  # Link to birth profile
            "hand_type": photo["hand_type"],
            "hand_shape": analysis_result["hand_shape"],
            "lines_detected": analysis_result["lines"],
            "mounts_detected": analysis_result["mounts"],
            "overall_confidence": analysis_result["confidence"],
            "model_version": analysis_result["model_version"],
            "processing_time_ms": analysis_result["processing_time_ms"],
            "created_at": datetime.utcnow().isoformat()
        }

        reading = await supabase.insert("palm_readings", reading_data)

        # Store interpretation
        interpretation_data = {
            "reading_id": str(reading["id"]),
            "user_id": str(user_id),  # Required by NOT NULL constraint
            "profile_id": str(profile_id) if profile_id else None,  # Link to birth profile
            "summary": analysis_result["interpretation"]["summary"],
            "detailed_analysis": analysis_result["interpretation"]["detailed_analysis"],
            "personality_traits": analysis_result["interpretation"]["personality_traits"],
            "life_events": analysis_result["interpretation"]["life_events"],
            "recommendations": analysis_result["interpretation"]["recommendations"],
            "astrology_correlations": analysis_result["interpretation"].get("astrology_correlations"),
            "numerology_correlations": analysis_result["interpretation"].get("numerology_correlations"),
            "rag_sources": analysis_result["interpretation"].get("rag_sources", []),
            "created_at": datetime.utcnow().isoformat()
        }

        interpretation = await supabase.insert("palm_interpretations", interpretation_data)

        logger.info(f"Palm analysis completed: reading_id={reading['id']}")

        # Map database fields to schema fields
        reading_response = {
            "reading_id": str(reading["id"]),
            "photo_id": str(reading["photo_id"]),
            "hand_type": reading["hand_type"],
            "profile_id": str(reading["profile_id"]) if reading.get("profile_id") else None,
            "hand_shape": reading.get("hand_shape"),
            "lines_detected": reading.get("lines_detected", []),
            "mounts_detected": reading.get("mounts_detected", []),
            "overall_confidence": reading["overall_confidence"],
            "model_version": reading.get("model_version", ""),
            "processing_time_ms": reading.get("processing_time_ms", 0),
            "created_at": reading["created_at"]
        }

        interpretation_response = {
            "interpretation_id": str(interpretation["id"]),
            "reading_id": str(interpretation["reading_id"]),
            "user_id": str(interpretation["user_id"]),
            "profile_id": str(interpretation["profile_id"]) if interpretation.get("profile_id") else None,
            "summary": interpretation["summary"],
            "detailed_analysis": interpretation["detailed_analysis"],
            "personality_traits": interpretation.get("personality_traits", []),
            "life_events": interpretation.get("life_events", []),
            "recommendations": interpretation.get("recommendations", []),
            "astrology_correlations": interpretation.get("astrology_correlations"),
            "numerology_correlations": interpretation.get("numerology_correlations"),
            "created_at": interpretation["created_at"],
            "rag_sources": interpretation.get("rag_sources", [])
        }

        return AnalysisResponse(
            reading=PalmReadingSchema(**reading_response),
            interpretation=PalmInterpretationSchema(**interpretation_response),
            status="completed"
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e) or repr(e)
        logger.error(f"Analysis failed: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {error_msg}"
        )


# ============================================================================
# READING RETRIEVAL ENDPOINTS
# ============================================================================

@router.get(
    "/readings",
    response_model=ReadingListResponse,
    summary="List user's palm readings",
    description="Get all palm readings for the authenticated user"
)
async def list_readings(
    limit: int = 20,
    offset: int = 0,
    hand_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    List all palm readings for the user.

    Args:
        limit: Number of readings to return (default 20, max 100)
        offset: Pagination offset
        hand_type: Filter by hand type ("left" or "right")
        current_user: Authenticated user

    Returns:
        ReadingListResponse with readings and statistics
    """
    try:
        user_id = current_user["user_id"]
        limit = min(limit, 100)  # Cap at 100
        supabase = SupabaseClient()

        # Build filters
        filters = {"user_id": user_id}
        if hand_type:
            filters["hand_type"] = hand_type

        # Get readings
        readings = await supabase.select(
            "palm_readings",
            filters=filters,
            order="created_at.desc",
            limit=limit,
            offset=offset
        )

        if not readings:
            return ReadingListResponse(
                readings=[],
                total_count=0,
                stats=UserReadingStats(
                    total_readings=0,
                    avg_confidence=0.0,
                    latest_reading_date=None,
                    hands_analyzed={}
                )
            )

        # Get total count
        total_count = await supabase.count("palm_readings", filters=filters)

        # Get photos for thumbnails
        photo_ids = [r["photo_id"] for r in readings]
        photos_data = []
        for photo_id in photo_ids:
            photo = await supabase.select(
                "palm_photos",
                filters={"id": photo_id},
                single=True
            )
            if photo:
                photos_data.append(photo)

        photos = {p["id"]: p for p in photos_data}

        # Check for interpretations
        reading_ids = [r["id"] for r in readings]
        interpretations_data = []
        for reading_id in reading_ids:
            interp = await supabase.select(
                "palm_interpretations",
                filters={"reading_id": reading_id},
                select="reading_id",
                single=True
            )
            if interp:
                interpretations_data.append(interp["reading_id"])

        has_interp = set(interpretations_data)

        # Build response items
        items = [
            ReadingListItem(
                reading_id=str(r["id"]),  # Convert UUID to string
                photo_id=str(r["photo_id"]),  # Convert UUID to string
                hand_type=r["hand_type"],
                created_at=r["created_at"],
                overall_confidence=r["overall_confidence"],
                has_interpretation=r["id"] in has_interp,
                thumbnail_url=photos[r["photo_id"]]["thumbnail_url"] if r["photo_id"] in photos else ""
            )
            for r in readings
        ]

        # Calculate stats
        avg_conf = sum(r["overall_confidence"] for r in readings) / len(readings)
        latest_date = max(r["created_at"] for r in readings)

        # Count by hand type
        hands_analyzed = {}
        for r in readings:
            hands_analyzed[r["hand_type"]] = hands_analyzed.get(r["hand_type"], 0) + 1

        stats = UserReadingStats(
            total_readings=total_count,
            avg_confidence=round(avg_conf, 2),
            latest_reading_date=latest_date,
            hands_analyzed=hands_analyzed
        )

        return ReadingListResponse(
            readings=items,
            total_count=total_count,
            stats=stats
        )

    except Exception as e:
        error_msg = str(e) or repr(e)
        logger.error(f"Failed to list readings: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list readings: {error_msg}"
        )


@router.get(
    "/readings/{reading_id}",
    response_model=AnalysisResponse,
    summary="Get specific palm reading",
    description="Retrieve a specific palm reading with interpretation"
)
async def get_reading(
    reading_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific palm reading.

    Args:
        reading_id: Reading UUID
        current_user: Authenticated user

    Returns:
        AnalysisResponse with reading and interpretation

    Raises:
        404: Reading not found
    """
    try:
        user_id = current_user["user_id"]
        supabase = SupabaseClient()

        # Get reading
        reading = await supabase.select(
            "palm_readings",
            filters={"id": reading_id, "user_id": user_id},
            single=True
        )

        if not reading:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reading not found"
            )

        # Get interpretation
        interpretation = await supabase.select(
            "palm_interpretations",
            filters={"reading_id": reading_id},
            single=True
        )

        # Map database fields to schema fields
        reading_response = {
            "reading_id": str(reading["id"]),
            "photo_id": str(reading["photo_id"]),
            "hand_type": reading["hand_type"],
            "profile_id": str(reading["profile_id"]) if reading.get("profile_id") else None,
            "hand_shape": reading.get("hand_shape"),
            "lines_detected": reading.get("lines_detected", []),
            "mounts_detected": reading.get("mounts_detected", []),
            "overall_confidence": reading["overall_confidence"],
            "model_version": reading.get("model_version", ""),
            "processing_time_ms": reading.get("processing_time_ms", 0),
            "created_at": reading["created_at"]
        }

        interpretation_response = None
        if interpretation:
            interpretation_response = {
                "interpretation_id": str(interpretation["id"]),
                "reading_id": str(interpretation["reading_id"]),
                "user_id": str(interpretation["user_id"]),
                "profile_id": str(interpretation["profile_id"]) if interpretation.get("profile_id") else None,
                "summary": interpretation["summary"],
                "detailed_analysis": interpretation["detailed_analysis"],
                "personality_traits": interpretation.get("personality_traits", []),
                "life_events": interpretation.get("life_events", []),
                "recommendations": interpretation.get("recommendations", []),
                "astrology_correlations": interpretation.get("astrology_correlations"),
                "numerology_correlations": interpretation.get("numerology_correlations"),
                "created_at": interpretation["created_at"],
                "rag_sources": interpretation.get("rag_sources", [])
            }

        return AnalysisResponse(
            reading=PalmReadingSchema(**reading_response),
            interpretation=PalmInterpretationSchema(**interpretation_response) if interpretation_response else None,
            status="completed"
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e) or repr(e)
        logger.error(f"Failed to get reading: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reading: {error_msg}"
        )


@router.delete(
    "/readings/{reading_id}",
    summary="Delete palm reading",
    description="Delete a palm reading and associated data (user must own the reading)"
)
async def delete_reading(
    reading_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a palm reading, interpretation, and associated image.

    Args:
        reading_id: Reading UUID to delete
        current_user: Authenticated user

    Returns:
        Success message

    Raises:
        404: Reading not found or user doesn't own it
        500: Deletion failed
    """
    try:
        user_id = current_user["user_id"]
        supabase = SupabaseClient()
        storage_service = PalmistryStorageService()

        logger.info(f"Deleting reading: reading_id={reading_id}, user_id={user_id}")

        # Get reading and verify ownership
        reading = await supabase.select(
            "palm_readings",
            filters={"id": reading_id, "user_id": user_id},
            single=True
        )

        if not reading:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reading not found or you don't have permission to delete it"
            )

        photo_id = reading["photo_id"]

        # Get photo details for storage deletion
        photo = await supabase.select(
            "palm_photos",
            filters={"id": photo_id},
            single=True
        )

        # Delete from storage (images)
        if photo:
            try:
                await storage_service.delete_palm_image(
                    photo["image_url"],
                    photo.get("thumbnail_url")
                )
                logger.info(f"Deleted images from storage for photo_id={photo_id}")
            except Exception as e:
                logger.warning(f"Failed to delete images from storage: {e}")
                # Continue anyway - DB cleanup is more important

        # Delete interpretation (if exists)
        try:
            await supabase.delete("palm_interpretations", {"reading_id": reading_id})
            logger.info(f"Deleted interpretation for reading_id={reading_id}")
        except Exception as e:
            logger.warning(f"Failed to delete interpretation: {e}")

        # Delete reading
        await supabase.delete("palm_readings", {"id": reading_id})
        logger.info(f"Deleted reading: reading_id={reading_id}")

        # Delete photo
        if photo:
            await supabase.delete("palm_photos", {"id": photo_id})
            logger.info(f"Deleted photo: photo_id={photo_id}")

        return {
            "success": True,
            "message": "Palm reading deleted successfully",
            "reading_id": reading_id
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e) or repr(e)
        logger.error(f"Failed to delete reading: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete reading: {error_msg}"
        )


# ============================================================================
# COMPARISON ENDPOINTS
# ============================================================================

@router.get(
    "/compare",
    response_model=ComparisonResponse,
    summary="Compare left and right hand readings",
    description="Compare the most recent left and right hand readings"
)
async def compare_hands(
    current_user: dict = Depends(get_current_user)
):
    """
    Compare left and right hand readings.

    Returns:
        ComparisonResponse with comparison analysis
    """
    try:
        user_id = current_user["user_id"]
        supabase = SupabaseClient()

        # Get latest left hand reading
        left_reading = await supabase.select(
            "palm_readings",
            filters={"user_id": user_id, "hand_type": "left"},
            order="created_at.desc",
            limit=1,
            single=True
        )

        # Get latest right hand reading
        right_reading = await supabase.select(
            "palm_readings",
            filters={"user_id": user_id, "hand_type": "right"},
            order="created_at.desc",
            limit=1,
            single=True
        )

        if not left_reading or not right_reading:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Both left and right hand readings required for comparison"
            )

        # Get interpretations
        left_interp = await supabase.select(
            "palm_interpretations",
            filters={"reading_id": left_reading["id"]},
            single=True
        )

        right_interp = await supabase.select(
            "palm_interpretations",
            filters={"reading_id": right_reading["id"]},
            single=True
        )

        # TODO: Implement actual comparison logic
        # For now, return placeholder
        return ComparisonResponse(
            left_reading=PalmReadingSchema(**left_reading),
            right_reading=PalmReadingSchema(**right_reading),
            comparison_summary="Comparison analysis coming soon",
            key_differences=[],
            synthesis=""
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e) or repr(e)
        logger.error(f"Failed to compare hands: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare hands: {error_msg}"
        )


# ============================================================================
# FEEDBACK ENDPOINTS
# ============================================================================

@router.post(
    "/feedback",
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback for a reading",
    description="Submit user feedback and rating for a palm reading"
)
async def submit_feedback(
    request: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit feedback for a reading.

    Args:
        request: Feedback request with rating and comments
        current_user: Authenticated user

    Returns:
        Success message
    """
    try:
        user_id = current_user["user_id"]
        supabase = SupabaseClient()

        # Verify reading ownership
        reading = await supabase.select(
            "palm_readings",
            filters={"id": request.reading_id, "user_id": user_id},
            single=True
        )

        if not reading:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reading not found"
            )

        # Create feedback
        feedback_data = {
            "reading_id": request.reading_id,
            "user_id": user_id,
            "rating": request.rating,
            "feedback_text": request.feedback_text,
            "created_at": datetime.utcnow().isoformat()
        }

        await supabase.insert("palm_feedback", feedback_data)

        return {"message": "Feedback submitted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e) or repr(e)
        logger.error(f"Failed to submit feedback: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {error_msg}"
        )


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Check palmistry service health"
)
async def health_check():
    """
    Health check endpoint.

    Returns:
        HealthCheckResponse with service status
    """
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        models=[
            ModelInfo(
                name="Placeholder Hand Detector",
                version="0.1.0",
                status="active"
            )
        ]
    )
