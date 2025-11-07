"""
Evidence Mode Feature Implementation

This module provides REST API endpoints for the Evidence Mode feature,
including source management, citation tracking, validation workflow,
and insight verification.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.features.base import BaseFeature
from app.core.feature_flags import require_feature
from app.core.security import get_current_user
from . import schemas
from .supabase_service import evidence_mode_supabase_service


class EvidenceModeFeature(BaseFeature):
    """
    Evidence Mode feature implementation.

    Provides citation-backed trust system for astrological insights,
    with source management, validation, and confidence scoring.
    """

    @property
    def name(self) -> str:
        return "evidence_mode"

    @property
    def display_name(self) -> str:
        return "Evidence Mode"

    @property
    def description(self) -> str:
        return "Citation-backed trust system"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def author(self) -> str:
        return "Claude AI"

    @property
    def magical_twelve_number(self) -> int:
        return 8

    def _create_router(self) -> APIRouter:
        """Create API router for this feature."""
        router = APIRouter(
            prefix="/evidence-mode",
            tags=["Evidence Mode"]
        )

        # ====================================================================
        # Feature Info
        # ====================================================================

        @router.get("/", response_model=dict)
        @require_feature("evidence_mode")
        async def get_feature_info():
            """Get Evidence Mode feature information."""
            return {
                "feature": self.name,
                "version": self.version,
                "description": self.description,
                "magical_twelve_number": self.magical_twelve_number,
                "status": "active"
            }

        # ====================================================================
        # Source Endpoints
        # ====================================================================

        @router.post("/sources", response_model=schemas.SourceResponse, status_code=status.HTTP_201_CREATED)
        @require_feature("evidence_mode")
        async def create_source(
            source_data: schemas.SourceCreate,
            current_user: dict = Depends(get_current_user)
        ):
            """
            Create a new evidence source.

            Creates a reference source (classical text, research paper, etc.)
            that can be cited to back astrological insights.
            """
            try:
                source = await evidence_mode_supabase_service.create_source(
                    source_data=source_data,
                    user_id=UUID(current_user["user_id"])
                )
                return source
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create source: {str(e)}"
                )

        @router.get("/sources/{source_id}", response_model=schemas.SourceResponse)
        @require_feature("evidence_mode")
        async def get_source(
            source_id: UUID,
            include_citations: bool = Query(False, description="Include citations for this source")
        ):
            """
            Get a source by ID.

            Retrieves detailed information about an evidence source,
            optionally including all citations that reference it.
            """
            source = await evidence_mode_supabase_service.get_source(source_id=source_id)

            if not source:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Source {source_id} not found"
                )

            return source

        @router.post("/sources/search", response_model=schemas.SourceListResponse)
        @require_feature("evidence_mode")
        async def search_sources(
            search_params: schemas.SourceSearchRequest,
        ):
            """
            Search for evidence sources.

            Search and filter sources by type, verification status, tags,
            and text query. Supports pagination.
            """
            try:
                sources, total = await evidence_mode_supabase_service.search_sources(
                    search_params=search_params
                )

                has_more = (search_params.page * search_params.page_size) < total

                return schemas.SourceListResponse(
                    sources=sources,
                    total=total,
                    page=search_params.page,
                    page_size=search_params.page_size,
                    has_more=has_more
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Search failed: {str(e)}"
                )

        @router.patch("/sources/{source_id}", response_model=schemas.SourceResponse)
        @require_feature("evidence_mode")
        async def update_source(
            source_id: UUID,
            update_data: schemas.SourceUpdate,
            current_user: dict = Depends(get_current_user)
        ):
            """
            Update an evidence source.

            Updates source metadata, credibility score, or verification status.
            """
            source = await evidence_mode_supabase_service.update_source(
                source_id=source_id,
                update_data=update_data
            )

            if not source:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Source {source_id} not found"
                )

            return source

        @router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
        @require_feature("evidence_mode")
        async def delete_source(
            source_id: UUID,
            current_user: dict = Depends(get_current_user)
        ):
            """
            Delete an evidence source (soft delete).

            Marks the source as not public rather than permanently deleting it.
            """
            success = await evidence_mode_supabase_service.delete_source(source_id=source_id)

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Source {source_id} not found"
                )

        # ====================================================================
        # Citation Endpoints
        # ====================================================================

        @router.post("/citations", response_model=schemas.CitationResponse, status_code=status.HTTP_201_CREATED)
        @require_feature("evidence_mode")
        async def create_citation(
            citation_data: schemas.CitationCreate,
            current_user: dict = Depends(get_current_user)
        ):
            """
            Create a new citation.

            Links an astrological insight to an evidence source,
            establishing the citation relationship.
            """
            try:
                citation = await evidence_mode_supabase_service.create_citation(
                    citation_data=citation_data,
                    user_id=UUID(current_user["user_id"])
                )
                return citation
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create citation: {str(e)}"
                )

        @router.get("/citations/{citation_id}", response_model=schemas.CitationResponse)
        @require_feature("evidence_mode")
        async def get_citation(
            citation_id: UUID,
            include_validations: bool = Query(False, description="Include validation data"),
        ):
            """
            Get a citation by ID.

            Retrieves citation details including source information
            and optionally validation records.
            """
            citation = await evidence_mode_supabase_service.get_citation(citation_id=citation_id)

            if not citation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Citation {citation_id} not found"
                )

            return citation

        @router.post("/citations/search", response_model=schemas.CitationListResponse)
        @require_feature("evidence_mode")
        async def search_citations(
            search_params: schemas.CitationSearchRequest,
        ):
            """
            Search for citations.

            Filter citations by insight type, source, confidence level,
            and other criteria. Supports pagination.
            """
            try:
                citations, total = await evidence_mode_supabase_service.search_citations(
                    search_params=search_params
                )

                has_more = (search_params.page * search_params.page_size) < total

                return schemas.CitationListResponse(
                    citations=citations,
                    total=total,
                    page=search_params.page,
                    page_size=search_params.page_size,
                    has_more=has_more
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Search failed: {str(e)}"
                )

        @router.post("/citations/{citation_id}/feedback", response_model=schemas.CitationResponse)
        @require_feature("evidence_mode")
        async def submit_citation_feedback(
            citation_id: UUID,
            feedback: schemas.CitationFeedback,
            current_user: dict = Depends(get_current_user)
        ):
            """
            Submit feedback on a citation.

            Records whether a user found a citation helpful or not,
            updating the citation's feedback counters.
            """
            citation = await evidence_mode_supabase_service.update_citation_feedback(
                citation_id=citation_id,
                is_helpful=feedback.is_helpful
            )

            if not citation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Citation {citation_id} not found"
                )

            return citation

        # ====================================================================
        # Validation Endpoints
        # ====================================================================

        @router.post("/validations", response_model=schemas.ValidationResponse, status_code=status.HTTP_201_CREATED)
        @require_feature("evidence_mode")
        async def create_validation(
            validation_data: schemas.ValidationCreate,
            validator_name: str = Query(None, description="Validator name"),
            validator_credentials: str = Query(None, description="Validator credentials"),
            current_user: dict = Depends(get_current_user)
        ):
            """
            Create a validation for a citation.

            Expert or peer validation of a citation, including
            confidence adjustments and feedback.
            """
            try:
                validation = await evidence_mode_supabase_service.create_validation(
                    validation_data=validation_data,
                    validator_id=UUID(current_user["user_id"]),
                    validator_name=validator_name,
                    validator_credentials=validator_credentials
                )
                return validation
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create validation: {str(e)}"
                )

        @router.get("/citations/{citation_id}/validations", response_model=List[schemas.ValidationResponse])
        @require_feature("evidence_mode")
        async def get_validations_for_citation(
            citation_id: UUID,
        ):
            """
            Get all validations for a citation.

            Retrieves validation records showing expert reviews
            and peer assessments of the citation.
            """
            validations, _ = await evidence_mode_supabase_service.list_validations(
                citation_id=citation_id,
                page=1,
                page_size=100
            )
            return validations

        # ====================================================================
        # Verification & Analysis Endpoints
        # ====================================================================

        @router.post("/verify", response_model=schemas.InsightVerificationResponse)
        @require_feature("evidence_mode")
        async def verify_insight(
            verification_request: schemas.InsightVerificationRequest,
        ):
            """
            Verify an astrological insight.

            Searches for citations and sources that support the given insight,
            returning evidence-backed verification with confidence scores.
            """
            try:
                verification = await evidence_mode_supabase_service.verify_insight(
                    verification_request=verification_request
                )
                return verification
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Verification failed: {str(e)}"
                )

        @router.get("/confidence/{insight_type}", response_model=schemas.ConfidenceScoreResponse)
        @require_feature("evidence_mode")
        async def calculate_confidence(
            insight_type: str,
        ):
            """
            Calculate confidence score for an insight type.

            Computes comprehensive confidence metrics based on:
            - Number and quality of citations
            - Source credibility scores
            - Validation assessments
            - Historical accuracy
            """
            try:
                confidence = await evidence_mode_supabase_service.calculate_confidence_score(
                    insight_type=insight_type
                )
                return confidence
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Confidence calculation failed: {str(e)}"
                )

        @router.get("/insights/{insight_type}/citations", response_model=List[schemas.CitationWithSourceResponse])
        @require_feature("evidence_mode")
        async def get_citations_for_insight_type(
            insight_type: str,
            min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence score"),
            limit: int = Query(10, ge=1, le=50, description="Maximum results"),
        ):
            """
            Get citations for a specific insight type.

            Retrieves all citations matching the insight type,
            filtered by minimum confidence threshold.
            """
            citations = await evidence_mode_supabase_service.get_citations_for_insight(
                insight_type=insight_type,
                min_confidence=min_confidence,
                limit=limit
            )

            # Convert to response schema with sources
            citation_responses = []
            for citation in citations:
                response = schemas.CitationWithSourceResponse.model_validate(citation)
                citation_responses.append(response)

            return citation_responses

        # ====================================================================
        # Statistics & Analytics
        # ====================================================================

        @router.get("/stats", response_model=dict)
        @require_feature("evidence_mode")
        async def get_evidence_mode_stats(
        ):
            """
            Get Evidence Mode statistics.

            Returns overall statistics about sources, citations,
            validations, and confidence scores.
            """
            # This would require additional queries - placeholder for now
            return {
                "feature": self.name,
                "version": self.version,
                "status": "Statistics endpoint - to be implemented"
            }

        return router


# Create feature instance
evidence_mode_feature = EvidenceModeFeature()
