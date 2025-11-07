"""
Evidence Mode Supabase Service
Handles all Evidence Mode database operations via Supabase REST API
"""

from typing import List, Dict, Any, Optional, Tuple
from supabase import create_client, Client
from app.core.config import settings
from datetime import datetime
import uuid

from . import schemas
from .models import SourceType, ConfidenceLevel, ValidationStatus


class EvidenceModeSupabaseService:
    """Service for Evidence Mode operations using Supabase REST API"""

    def __init__(self):
        """Initialize Supabase client"""
        supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY

        if not supabase_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY must be set")

        self.client: Client = create_client(
            settings.SUPABASE_URL,
            supabase_key
        )

        self._initialized = False

    def initialize(self):
        """Initialize the service (for testing compatibility)"""
        if not self._initialized:
            self._initialized = True
            print("✅ Evidence Mode Supabase service initialized")

    # ========================================================================
    # Source Operations
    # ========================================================================

    async def create_source(
        self,
        source_data: schemas.SourceCreate,
        user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Create a new evidence source"""
        data = {
            "id": str(uuid.uuid4()),
            "title": source_data.title,
            "author": source_data.author,
            "source_type": source_data.source_type.value,
            "description": source_data.description,
            "excerpt": source_data.excerpt,
            "full_text": source_data.full_text,
            "publication_year": source_data.publication_year,
            "publisher": source_data.publisher,
            "isbn_doi": source_data.isbn_doi,
            "url": source_data.url,
            "page_reference": source_data.page_reference,
            "language": source_data.language,
            "tags": source_data.tags,
            "keywords": source_data.keywords,
            "is_public": source_data.is_public,
            "created_by": str(user_id),
            "created_at": datetime.utcnow().isoformat()
        }

        response = self.client.table("evidence_mode_sources").insert(data).execute()
        return response.data[0] if response.data else None

    async def get_source(self, source_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get a source by ID"""
        response = self.client.table("evidence_mode_sources") \
            .select("*") \
            .eq("id", str(source_id)) \
            .execute()
        return response.data[0] if response.data else None

    async def update_source(
        self,
        source_id: uuid.UUID,
        update_data: schemas.SourceUpdate
    ) -> Optional[Dict[str, Any]]:
        """Update a source"""
        # Get existing source
        source = await self.get_source(source_id)
        if not source:
            return None

        # Build update dict with only provided fields
        data = {}
        if update_data.title is not None:
            data["title"] = update_data.title
        if update_data.author is not None:
            data["author"] = update_data.author
        if update_data.description is not None:
            data["description"] = update_data.description
        if update_data.excerpt is not None:
            data["excerpt"] = update_data.excerpt
        if update_data.full_text is not None:
            data["full_text"] = update_data.full_text
        if update_data.url is not None:
            data["url"] = update_data.url
        if update_data.tags is not None:
            data["tags"] = update_data.tags
        if update_data.keywords is not None:
            data["keywords"] = update_data.keywords
        if update_data.credibility_score is not None:
            data["credibility_score"] = update_data.credibility_score
        if update_data.is_verified is not None:
            data["is_verified"] = update_data.is_verified
        if update_data.is_public is not None:
            data["is_public"] = update_data.is_public

        data["updated_at"] = datetime.utcnow().isoformat()

        response = self.client.table("evidence_mode_sources") \
            .update(data) \
            .eq("id", str(source_id)) \
            .execute()
        return response.data[0] if response.data else None

    async def delete_source(self, source_id: uuid.UUID) -> bool:
        """Soft delete a source (set is_public to False)"""
        source = await self.get_source(source_id)
        if not source:
            return False

        response = self.client.table("evidence_mode_sources") \
            .update({"is_public": False}) \
            .eq("id", str(source_id)) \
            .execute()
        return len(response.data) > 0 if response.data else False

    async def search_sources(
        self,
        search_params: schemas.SourceSearchRequest
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Search sources with filters and pagination"""
        # Build query
        query = self.client.table("evidence_mode_sources").select("*", count="exact")

        # Apply filters
        if search_params.source_type:
            query = query.eq("source_type", search_params.source_type.value)

        if search_params.is_verified is not None:
            query = query.eq("is_verified", search_params.is_verified)

        # Text search (if query provided)
        if search_params.query:
            # Use Supabase's textSearch or ilike
            query = query.or_(
                f"title.ilike.%{search_params.query}%,"
                f"author.ilike.%{search_params.query}%,"
                f"description.ilike.%{search_params.query}%"
            )

        # Tags filter
        if search_params.tags:
            for tag in search_params.tags:
                query = query.contains("tags", [tag])

        # Pagination
        offset = (search_params.page - 1) * search_params.page_size
        query = query.range(offset, offset + search_params.page_size - 1) \
                     .order("created_at", desc=True)

        response = query.execute()
        total = response.count if hasattr(response, 'count') else len(response.data)

        return response.data if response.data else [], total

    # ========================================================================
    # Citation Operations
    # ========================================================================

    async def create_citation(
        self,
        citation_data: schemas.CitationCreate,
        user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Create a new citation"""
        # Verify source exists
        source = await self.get_source(citation_data.source_id)
        if not source:
            raise ValueError(f"Source {citation_data.source_id} not found")

        data = {
            "id": str(uuid.uuid4()),
            "source_id": str(citation_data.source_id),
            "insight_type": citation_data.insight_type,
            "insight_text": citation_data.insight_text,
            "insight_reference": citation_data.insight_reference,
            "relevance_score": citation_data.relevance_score,
            "confidence_level": citation_data.confidence_level.value,
            "confidence_score": citation_data.confidence_score,
            "context": citation_data.context,
            "reasoning": citation_data.reasoning,
            "created_by": str(user_id),
            "created_at": datetime.utcnow().isoformat()
        }

        response = self.client.table("evidence_mode_citations").insert(data).execute()
        citation = response.data[0] if response.data else None

        # Increment citation count on source
        if citation:
            self.client.table("evidence_mode_sources") \
                .update({"citation_count": source["citation_count"] + 1}) \
                .eq("id", str(citation_data.source_id)) \
                .execute()

        return citation

    async def get_citation(self, citation_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get a citation by ID with source details"""
        response = self.client.table("evidence_mode_citations") \
            .select("*, evidence_mode_sources(*)") \
            .eq("id", str(citation_id)) \
            .execute()
        return response.data[0] if response.data else None

    async def update_citation_feedback(
        self,
        citation_id: uuid.UUID,
        is_helpful: bool
    ) -> Optional[Dict[str, Any]]:
        """Update citation feedback counters"""
        citation = await self.get_citation(citation_id)
        if not citation:
            return None

        # Update counters
        if is_helpful:
            helpful_count = citation.get("helpful_count", 0) + 1
            data = {"helpful_count": helpful_count}
        else:
            not_helpful_count = citation.get("not_helpful_count", 0) + 1
            data = {"not_helpful_count": not_helpful_count}

        # Always increment view count
        view_count = citation.get("view_count", 0) + 1
        data["view_count"] = view_count

        response = self.client.table("evidence_mode_citations") \
            .update(data) \
            .eq("id", str(citation_id)) \
            .execute()
        return response.data[0] if response.data else None

    async def search_citations(
        self,
        search_params: schemas.CitationSearchRequest
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Search citations with filters"""
        query = self.client.table("evidence_mode_citations") \
            .select("*, evidence_mode_sources(*)", count="exact")

        # Apply filters
        if search_params.insight_type:
            query = query.eq("insight_type", search_params.insight_type)

        if search_params.source_id:
            query = query.eq("source_id", str(search_params.source_id))

        if search_params.confidence_level:
            query = query.eq("confidence_level", search_params.confidence_level.value)

        if search_params.min_confidence is not None:
            query = query.gte("confidence_score", search_params.min_confidence)

        if search_params.is_active is not None:
            query = query.eq("is_active", search_params.is_active)

        # Pagination
        offset = (search_params.page - 1) * search_params.page_size
        query = query.range(offset, offset + search_params.page_size - 1) \
                     .order("created_at", desc=True)

        response = query.execute()
        total = response.count if hasattr(response, 'count') else len(response.data)

        return response.data if response.data else [], total

    async def get_citations_for_insight(
        self,
        insight_type: str,
        min_confidence: float = 0.0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get citations for a specific insight type"""
        response = self.client.table("evidence_mode_citations") \
            .select("*, evidence_mode_sources(*), evidence_mode_validations(*)") \
            .eq("insight_type", insight_type) \
            .eq("is_active", True) \
            .gte("confidence_score", min_confidence) \
            .limit(limit) \
            .order("confidence_score", desc=True) \
            .execute()
        return response.data if response.data else []

    # ========================================================================
    # Validation Operations
    # ========================================================================

    async def create_validation(
        self,
        validation_data: schemas.ValidationCreate,
        validator_id: uuid.UUID,
        validator_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new validation"""
        # Verify citation exists
        citation = await self.get_citation(validation_data.citation_id)
        if not citation:
            raise ValueError(f"Citation {validation_data.citation_id} not found")

        data = {
            "id": str(uuid.uuid4()),
            "citation_id": str(validation_data.citation_id),
            "validator_id": str(validator_id),
            "validator_name": validator_name,
            "status": validation_data.status.value,
            "confidence_adjustment": validation_data.confidence_adjustment,
            "comments": validation_data.comments,
            "suggestions": validation_data.suggestions,
            "alternative_sources": validation_data.alternative_sources,
            "accuracy_score": validation_data.accuracy_score,
            "relevance_score": validation_data.relevance_score,
            "created_at": datetime.utcnow().isoformat()
        }

        response = self.client.table("evidence_mode_validations").insert(data).execute()
        validation = response.data[0] if response.data else None

        # Update citation confidence if adjustment provided
        if validation and validation_data.confidence_adjustment:
            new_confidence = citation.get("confidence_score", 0.5) + validation_data.confidence_adjustment
            # Clamp to 0.0-1.0 range
            new_confidence = max(0.0, min(1.0, new_confidence))

            self.client.table("evidence_mode_citations") \
                .update({"confidence_score": new_confidence}) \
                .eq("id", str(validation_data.citation_id)) \
                .execute()

        return validation

    async def list_validations(
        self,
        citation_id: Optional[uuid.UUID] = None,
        validator_id: Optional[uuid.UUID] = None,
        status: Optional[ValidationStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List validations with filters"""
        query = self.client.table("evidence_mode_validations") \
            .select("*", count="exact")

        if citation_id:
            query = query.eq("citation_id", str(citation_id))

        if validator_id:
            query = query.eq("validator_id", str(validator_id))

        if status:
            query = query.eq("status", status.value)

        # Pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1) \
                     .order("created_at", desc=True)

        response = query.execute()
        total = response.count if hasattr(response, 'count') else len(response.data)

        return response.data if response.data else [], total

    # ========================================================================
    # Confidence Scoring
    # ========================================================================

    async def calculate_confidence_score(
        self,
        insight_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> schemas.ConfidenceScoreResponse:
        """Calculate confidence score for an insight type"""
        # Get all citations for this insight type
        citations = await self.get_citations_for_insight(insight_type, min_confidence=0.0)

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
        base_confidence = sum(c.get("confidence_score", 0.5) for c in citations) / citation_count

        # Source credibility
        credibility_scores = [
            c.get("evidence_mode_sources", {}).get("credibility_score", 0.5)
            for c in citations if c.get("evidence_mode_sources")
        ]
        average_source_credibility = sum(credibility_scores) / len(credibility_scores) if credibility_scores else 0.5

        # Validation scores
        all_validations = []
        for citation in citations:
            validations = citation.get("evidence_mode_validations", [])
            if isinstance(validations, list):
                all_validations.extend(validations)

        validation_count = len(all_validations)
        validation_scores = [
            v.get("accuracy_score", 0.5)
            for v in all_validations if v.get("accuracy_score") is not None
        ]
        average_validation_score = sum(validation_scores) / len(validation_scores) if validation_scores else 0.0

        # Final confidence: weighted average
        # Base confidence (40%) + Source credibility (30%) + Validation (30%)
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
            base_confidence=round(base_confidence, 3),
            citation_count=citation_count,
            average_source_credibility=round(average_source_credibility, 3),
            validation_count=validation_count,
            average_validation_score=round(average_validation_score, 3),
            final_confidence=round(final_confidence, 3),
            confidence_level=confidence_level
        )

    async def verify_insight(
        self,
        verification_request: schemas.InsightVerificationRequest
    ) -> schemas.InsightVerificationResponse:
        """Verify an astrological insight with evidence"""
        # Get citations
        citations = await self.get_citations_for_insight(
            verification_request.insight_type,
            min_confidence=0.0
        )

        # Calculate statistics
        has_citations = len(citations) > 0
        citation_count = len(citations)

        confidence_scores = [c.get("confidence_score", 0.5) for c in citations]
        average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else None
        highest_confidence = max(confidence_scores) if confidence_scores else None

        # Format citations for response
        formatted_citations = []
        if verification_request.include_sources:
            for citation in citations:
                formatted_citations.append({
                    **citation,
                    "source": citation.get("evidence_mode_sources", {})
                })

        return schemas.InsightVerificationResponse(
            insight_type=verification_request.insight_type,
            insight_text=verification_request.insight_text,
            has_citations=has_citations,
            citation_count=citation_count,
            average_confidence=round(average_confidence, 3) if average_confidence else None,
            highest_confidence=round(highest_confidence, 3) if highest_confidence else None,
            citations=formatted_citations,
            suggested_sources=[]  # TODO: Implement source suggestions
        )


# Singleton instance
evidence_mode_supabase_service = EvidenceModeSupabaseService()
