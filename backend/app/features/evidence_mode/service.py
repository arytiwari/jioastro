"""
Business logic for Evidence Mode feature.

This service handles:
- Source management (CRUD operations)
- Citation creation and linking
- Validation workflow
- Confidence scoring
- Evidence search and retrieval
"""

from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
import logging
from datetime import datetime

from .models import (
    EvidenceModeSource,
    EvidenceModeCitation,
    EvidenceModeValidation,
    SourceType,
    ConfidenceLevel,
    ValidationStatus
)
from . import schemas

logger = logging.getLogger(__name__)


class EvidenceModeService:
    """
    Service for Evidence Mode feature.

    Provides comprehensive citation management, source tracking,
    and confidence scoring for astrological insights.
    """

    def __init__(self):
        self._initialized = False

    def initialize(self):
        """Initialize the service."""
        if self._initialized:
            return

        logger.info("Initializing Evidence Mode service")
        self._initialized = True

    # ========================================================================
    # Source Management
    # ========================================================================

    async def create_source(
        self,
        db: AsyncSession,
        source_data: schemas.SourceCreate,
        created_by: Optional[UUID] = None
    ) -> EvidenceModeSource:
        """
        Create a new evidence source.

        Args:
            db: Database session
            source_data: Source creation data
            created_by: ID of user creating the source

        Returns:
            Created source
        """
        logger.info(f"Creating new source: {source_data.title}")

        source = EvidenceModeSource(
            title=source_data.title,
            author=source_data.author,
            source_type=source_data.source_type,
            description=source_data.description,
            excerpt=source_data.excerpt,
            full_text=source_data.full_text,
            publication_year=source_data.publication_year,
            publisher=source_data.publisher,
            isbn_doi=source_data.isbn_doi,
            url=source_data.url,
            page_reference=source_data.page_reference,
            language=source_data.language,
            tags=source_data.tags,
            keywords=source_data.keywords,
            is_public=source_data.is_public,
            created_by=created_by
        )

        db.add(source)
        await db.commit()
        await db.refresh(source)

        logger.info(f"Created source {source.id}: {source.title}")
        return source

    async def get_source(
        self,
        db: AsyncSession,
        source_id: UUID,
        include_citations: bool = False
    ) -> Optional[EvidenceModeSource]:
        """Get a source by ID."""
        query = select(EvidenceModeSource).where(EvidenceModeSource.id == source_id)

        if include_citations:
            query = query.options(selectinload(EvidenceModeSource.citations))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def search_sources(
        self,
        db: AsyncSession,
        search_params: schemas.SourceSearchRequest
    ) -> Tuple[List[EvidenceModeSource], int]:
        """
        Search for sources with filters and pagination.

        Args:
            db: Database session
            search_params: Search parameters

        Returns:
            Tuple of (sources, total_count)
        """
        # Build base query
        query = select(EvidenceModeSource).where(EvidenceModeSource.is_public == True)
        count_query = select(func.count()).select_from(EvidenceModeSource).where(
            EvidenceModeSource.is_public == True
        )

        # Apply filters
        if search_params.source_type:
            query = query.where(EvidenceModeSource.source_type == search_params.source_type)
            count_query = count_query.where(EvidenceModeSource.source_type == search_params.source_type)

        if search_params.is_verified is not None:
            query = query.where(EvidenceModeSource.is_verified == search_params.is_verified)
            count_query = count_query.where(EvidenceModeSource.is_verified == search_params.is_verified)

        if search_params.query:
            search_filter = or_(
                EvidenceModeSource.title.ilike(f"%{search_params.query}%"),
                EvidenceModeSource.author.ilike(f"%{search_params.query}%"),
                EvidenceModeSource.description.ilike(f"%{search_params.query}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if search_params.tags:
            # Search for sources with any of the specified tags
            query = query.where(
                EvidenceModeSource.tags.op('?|')(search_params.tags)
            )
            count_query = count_query.where(
                EvidenceModeSource.tags.op('?|')(search_params.tags)
            )

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply ordering and pagination
        query = query.order_by(
            desc(EvidenceModeSource.credibility_score),
            desc(EvidenceModeSource.citation_count)
        )
        offset = (search_params.page - 1) * search_params.page_size
        query = query.offset(offset).limit(search_params.page_size)

        # Execute query
        result = await db.execute(query)
        sources = result.scalars().all()

        return sources, total

    async def update_source(
        self,
        db: AsyncSession,
        source_id: UUID,
        update_data: schemas.SourceUpdate
    ) -> Optional[EvidenceModeSource]:
        """Update a source."""
        source = await self.get_source(db, source_id)
        if not source:
            return None

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(source, field, value)

        await db.commit()
        await db.refresh(source)

        logger.info(f"Updated source {source_id}")
        return source

    async def delete_source(self, db: AsyncSession, source_id: UUID) -> bool:
        """Delete a source (soft delete by setting is_public=False)."""
        source = await self.get_source(db, source_id)
        if not source:
            return False

        source.is_public = False
        await db.commit()

        logger.info(f"Deleted source {source_id}")
        return True

    # ========================================================================
    # Citation Management
    # ========================================================================

    async def create_citation(
        self,
        db: AsyncSession,
        citation_data: schemas.CitationCreate,
        created_by: Optional[UUID] = None
    ) -> EvidenceModeCitation:
        """
        Create a new citation linking an insight to a source.

        Args:
            db: Database session
            citation_data: Citation creation data
            created_by: ID of user creating citation

        Returns:
            Created citation
        """
        logger.info(f"Creating citation for insight type: {citation_data.insight_type}")

        # Verify source exists
        source = await self.get_source(db, citation_data.source_id)
        if not source:
            raise ValueError(f"Source {citation_data.source_id} not found")

        citation = EvidenceModeCitation(
            source_id=citation_data.source_id,
            insight_type=citation_data.insight_type,
            insight_text=citation_data.insight_text,
            insight_reference=citation_data.insight_reference,
            relevance_score=citation_data.relevance_score,
            confidence_level=citation_data.confidence_level,
            confidence_score=citation_data.confidence_score,
            context=citation_data.context,
            reasoning=citation_data.reasoning,
            created_by=created_by
        )

        db.add(citation)

        # Increment source citation count
        source.citation_count += 1

        await db.commit()
        await db.refresh(citation)

        logger.info(f"Created citation {citation.id}")
        return citation

    async def get_citation(
        self,
        db: AsyncSession,
        citation_id: UUID,
        include_source: bool = True,
        include_validations: bool = False
    ) -> Optional[EvidenceModeCitation]:
        """Get a citation by ID."""
        query = select(EvidenceModeCitation).where(EvidenceModeCitation.id == citation_id)

        if include_source:
            query = query.options(selectinload(EvidenceModeCitation.source))
        if include_validations:
            query = query.options(selectinload(EvidenceModeCitation.validations))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def search_citations(
        self,
        db: AsyncSession,
        search_params: schemas.CitationSearchRequest
    ) -> Tuple[List[EvidenceModeCitation], int]:
        """
        Search citations with filters.

        Args:
            db: Database session
            search_params: Search parameters

        Returns:
            Tuple of (citations, total_count)
        """
        # Build query
        query = select(EvidenceModeCitation).options(
            selectinload(EvidenceModeCitation.source)
        )
        count_query = select(func.count()).select_from(EvidenceModeCitation)

        # Apply filters
        filters = []
        if search_params.insight_type:
            filters.append(EvidenceModeCitation.insight_type == search_params.insight_type)
        if search_params.source_id:
            filters.append(EvidenceModeCitation.source_id == search_params.source_id)
        if search_params.confidence_level:
            filters.append(EvidenceModeCitation.confidence_level == search_params.confidence_level)
        if search_params.min_confidence is not None:
            filters.append(EvidenceModeCitation.confidence_score >= search_params.min_confidence)
        if search_params.is_active is not None:
            filters.append(EvidenceModeCitation.is_active == search_params.is_active)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply ordering and pagination
        query = query.order_by(
            desc(EvidenceModeCitation.confidence_score),
            desc(EvidenceModeCitation.relevance_score)
        )
        offset = (search_params.page - 1) * search_params.page_size
        query = query.offset(offset).limit(search_params.page_size)

        # Execute query
        result = await db.execute(query)
        citations = result.scalars().all()

        return citations, total

    async def get_citations_for_insight(
        self,
        db: AsyncSession,
        insight_type: str,
        insight_text: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 10
    ) -> List[EvidenceModeCitation]:
        """
        Get citations for a specific insight.

        Args:
            db: Database session
            insight_type: Type of insight
            insight_text: Optional text to match
            min_confidence: Minimum confidence score
            limit: Maximum number of citations

        Returns:
            List of citations
        """
        query = select(EvidenceModeCitation).options(
            selectinload(EvidenceModeCitation.source),
            selectinload(EvidenceModeCitation.validations)
        ).where(
            and_(
                EvidenceModeCitation.insight_type == insight_type,
                EvidenceModeCitation.is_active == True,
                EvidenceModeCitation.confidence_score >= min_confidence
            )
        )

        if insight_text:
            query = query.where(
                EvidenceModeCitation.insight_text.ilike(f"%{insight_text}%")
            )

        query = query.order_by(
            desc(EvidenceModeCitation.confidence_score)
        ).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def update_citation_feedback(
        self,
        db: AsyncSession,
        citation_id: UUID,
        is_helpful: bool
    ) -> Optional[EvidenceModeCitation]:
        """Update citation feedback counters."""
        citation = await self.get_citation(db, citation_id, include_source=False)
        if not citation:
            return None

        if is_helpful:
            citation.helpful_count += 1
        else:
            citation.not_helpful_count += 1

        citation.view_count += 1

        await db.commit()
        await db.refresh(citation)

        return citation

    # ========================================================================
    # Validation Management
    # ========================================================================

    async def create_validation(
        self,
        db: AsyncSession,
        validation_data: schemas.ValidationCreate,
        validator_id: UUID,
        validator_name: Optional[str] = None,
        validator_credentials: Optional[str] = None
    ) -> EvidenceModeValidation:
        """
        Create a new validation for a citation.

        Args:
            db: Database session
            validation_data: Validation data
            validator_id: ID of validator
            validator_name: Name of validator
            validator_credentials: Validator credentials

        Returns:
            Created validation
        """
        logger.info(f"Creating validation for citation: {validation_data.citation_id}")

        # Verify citation exists
        citation = await self.get_citation(db, validation_data.citation_id, include_source=False)
        if not citation:
            raise ValueError(f"Citation {validation_data.citation_id} not found")

        validation = EvidenceModeValidation(
            citation_id=validation_data.citation_id,
            validator_id=validator_id,
            validator_name=validator_name,
            validator_credentials=validator_credentials,
            status=validation_data.status,
            confidence_adjustment=validation_data.confidence_adjustment,
            comments=validation_data.comments,
            suggestions=validation_data.suggestions,
            alternative_sources=validation_data.alternative_sources,
            accuracy_score=validation_data.accuracy_score,
            relevance_score=validation_data.relevance_score
        )

        db.add(validation)

        # Update citation confidence if validated
        if validation_data.status == ValidationStatus.VALIDATED and validation_data.confidence_adjustment:
            new_confidence = citation.confidence_score + validation_data.confidence_adjustment
            citation.confidence_score = max(0.0, min(1.0, new_confidence))

        await db.commit()
        await db.refresh(validation)

        logger.info(f"Created validation {validation.id}")
        return validation

    async def get_validations_for_citation(
        self,
        db: AsyncSession,
        citation_id: UUID
    ) -> List[EvidenceModeValidation]:
        """Get all validations for a citation."""
        query = select(EvidenceModeValidation).where(
            EvidenceModeValidation.citation_id == citation_id
        ).order_by(desc(EvidenceModeValidation.created_at))

        result = await db.execute(query)
        return result.scalars().all()

    # ========================================================================
    # Confidence Scoring
    # ========================================================================

    async def calculate_confidence_score(
        self,
        db: AsyncSession,
        insight_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> schemas.ConfidenceScoreResponse:
        """
        Calculate confidence score for an insight type.

        Takes into account:
        - Number of citations
        - Source credibility
        - Validation scores
        - Historical accuracy

        Args:
            db: Database session
            insight_type: Type of insight
            context: Additional context

        Returns:
            Confidence score breakdown
        """
        # Get all citations for this insight type
        citations = await self.get_citations_for_insight(
            db,
            insight_type=insight_type,
            min_confidence=0.0,
            limit=100
        )

        if not citations:
            return schemas.ConfidenceScoreResponse(
                insight_type=insight_type,
                base_confidence=0.0,
                citation_count=0,
                average_source_credibility=0.0,
                validation_count=0,
                average_validation_score=0.0,
                final_confidence=0.0,
                confidence_level=ConfidenceLevel.VERY_LOW
            )

        # Calculate metrics
        citation_count = len(citations)
        source_credibilities = [c.source.credibility_score for c in citations if c.source]
        average_source_credibility = sum(source_credibilities) / len(source_credibilities) if source_credibilities else 0.0

        # Get validation scores
        validation_count = 0
        validation_scores = []
        for citation in citations:
            for validation in citation.validations:
                if validation.status == ValidationStatus.VALIDATED:
                    validation_count += 1
                    if validation.accuracy_score:
                        validation_scores.append(validation.accuracy_score)

        average_validation_score = sum(validation_scores) / len(validation_scores) if validation_scores else 0.0

        # Calculate base confidence (weighted average)
        base_confidence = sum(c.confidence_score or 0.5 for c in citations) / citation_count

        # Calculate final confidence
        # Formula: base * 0.4 + source_credibility * 0.3 + validation * 0.3
        final_confidence = (
            base_confidence * 0.4 +
            average_source_credibility * 0.3 +
            average_validation_score * 0.3
        )

        # Determine confidence level
        if final_confidence >= 0.9:
            confidence_level = ConfidenceLevel.VERY_HIGH
        elif final_confidence >= 0.75:
            confidence_level = ConfidenceLevel.HIGH
        elif final_confidence >= 0.5:
            confidence_level = ConfidenceLevel.MEDIUM
        elif final_confidence >= 0.25:
            confidence_level = ConfidenceLevel.LOW
        else:
            confidence_level = ConfidenceLevel.VERY_LOW

        return schemas.ConfidenceScoreResponse(
            insight_type=insight_type,
            base_confidence=base_confidence,
            citation_count=citation_count,
            average_source_credibility=average_source_credibility,
            validation_count=validation_count,
            average_validation_score=average_validation_score,
            final_confidence=final_confidence,
            confidence_level=confidence_level
        )

    async def verify_insight(
        self,
        db: AsyncSession,
        verification_request: schemas.InsightVerificationRequest
    ) -> schemas.InsightVerificationResponse:
        """
        Verify an astrological insight with citations.

        Args:
            db: Database session
            verification_request: Verification request

        Returns:
            Verification response with citations
        """
        # Get citations for this insight
        citations = await self.get_citations_for_insight(
            db,
            insight_type=verification_request.insight_type,
            insight_text=verification_request.insight_text if len(verification_request.insight_text) > 20 else None,
            min_confidence=0.0,
            limit=10
        )

        # Calculate statistics
        has_citations = len(citations) > 0
        citation_count = len(citations)

        confidence_scores = [c.confidence_score for c in citations if c.confidence_score]
        average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else None
        highest_confidence = max(confidence_scores) if confidence_scores else None

        # Prepare citation responses
        citation_responses = []
        for citation in citations:
            response = schemas.CitationWithSourceResponse.model_validate(citation)
            citation_responses.append(response)

        return schemas.InsightVerificationResponse(
            insight_type=verification_request.insight_type,
            insight_text=verification_request.insight_text,
            has_citations=has_citations,
            citation_count=citation_count,
            average_confidence=average_confidence,
            highest_confidence=highest_confidence,
            citations=citation_responses,
            suggested_sources=[]
        )


# Global service instance
evidence_mode_service = EvidenceModeService()
