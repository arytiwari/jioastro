"""
Unit tests for Evidence Mode service.

Tests cover:
- Source CRUD operations
- Citation management
- Validation workflow
- Confidence scoring
- Search and filtering
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime

from app.features.evidence_mode.service import EvidenceModeService
from app.features.evidence_mode.models import (
    EvidenceModeSource,
    EvidenceModeCitation,
    EvidenceModeValidation,
    SourceType,
    ConfidenceLevel,
    ValidationStatus
)
from app.features.evidence_mode import schemas


@pytest.fixture
def service():
    """Create service instance."""
    service = EvidenceModeService()
    service.initialize()
    return service


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return AsyncMock()


@pytest.fixture
def sample_source():
    """Create sample source."""
    return EvidenceModeSource(
        id=uuid4(),
        title="Brihat Parashara Hora Shastra",
        author="Maharishi Parashara",
        source_type=SourceType.CLASSICAL_TEXT,
        description="Foundational text of Vedic astrology",
        excerpt="Chapter 3, Verse 12",
        credibility_score=0.95,
        citation_count=10,
        is_verified=True,
        is_public=True,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_citation(sample_source):
    """Create sample citation."""
    return EvidenceModeCitation(
        id=uuid4(),
        source_id=sample_source.id,
        insight_type="planet_position",
        insight_text="Mars in 10th house indicates strong career drive",
        confidence_level=ConfidenceLevel.HIGH,
        confidence_score=0.85,
        relevance_score=0.9,
        is_active=True,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_validation(sample_citation):
    """Create sample validation."""
    return EvidenceModeValidation(
        id=uuid4(),
        citation_id=sample_citation.id,
        validator_id=uuid4(),
        validator_name="Expert Astrologer",
        status=ValidationStatus.VALIDATED,
        confidence_adjustment=0.05,
        accuracy_score=0.9,
        relevance_score=0.95,
        created_at=datetime.utcnow()
    )


# ============================================================================
# Service Initialization Tests
# ============================================================================

def test_service_initialization(service):
    """Test service initializes correctly."""
    assert service._initialized is True


def test_service_singleton_initialization():
    """Test service can be initialized multiple times safely."""
    service = EvidenceModeService()
    service.initialize()
    service.initialize()  # Should not raise error
    assert service._initialized is True


# ============================================================================
# Source Management Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_source(service, mock_db):
    """Test creating a new source."""
    source_data = schemas.SourceCreate(
        title="Test Source",
        author="Test Author",
        source_type=SourceType.CLASSICAL_TEXT,
        description="Test description",
        tags=["test", "vedic"]
    )

    user_id = uuid4()

    # Mock database operations
    mock_db.add = Mock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    source = await service.create_source(mock_db, source_data, user_id)

    # Verify source was created with correct data
    assert source.title == "Test Source"
    assert source.author == "Test Author"
    assert source.source_type == SourceType.CLASSICAL_TEXT
    assert source.created_by == user_id

    # Verify database operations
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_get_source(service, mock_db, sample_source):
    """Test retrieving a source by ID."""
    source_id = sample_source.id

    # Mock database query
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = sample_source
    mock_db.execute = AsyncMock(return_value=mock_result)

    source = await service.get_source(mock_db, source_id)

    assert source is not None
    assert source.id == source_id
    assert source.title == "Brihat Parashara Hora Shastra"
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_source_not_found(service, mock_db):
    """Test retrieving non-existent source."""
    source_id = uuid4()

    # Mock database query returning None
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    source = await service.get_source(mock_db, source_id)

    assert source is None


@pytest.mark.asyncio
async def test_update_source(service, mock_db, sample_source):
    """Test updating a source."""
    source_id = sample_source.id

    # Mock get_source
    with patch.object(service, 'get_source', return_value=sample_source):
        update_data = schemas.SourceUpdate(
            title="Updated Title",
            credibility_score=0.98
        )

        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        updated_source = await service.update_source(mock_db, source_id, update_data)

        assert updated_source.title == "Updated Title"
        assert updated_source.credibility_score == 0.98
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_source(service, mock_db, sample_source):
    """Test soft deleting a source."""
    source_id = sample_source.id

    # Mock get_source
    with patch.object(service, 'get_source', return_value=sample_source):
        mock_db.commit = AsyncMock()

        result = await service.delete_source(mock_db, source_id)

        assert result is True
        assert sample_source.is_public is False
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_search_sources(service, mock_db, sample_source):
    """Test searching sources with filters."""
    search_params = schemas.SourceSearchRequest(
        query="Parashara",
        source_type=SourceType.CLASSICAL_TEXT,
        is_verified=True,
        page=1,
        page_size=20
    )

    # Mock database queries
    mock_count_result = Mock()
    mock_count_result.scalar.return_value = 1

    mock_query_result = Mock()
    mock_query_result.scalars.return_value.all.return_value = [sample_source]

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_query_result])

    sources, total = await service.search_sources(mock_db, search_params)

    assert total == 1
    assert len(sources) == 1
    assert sources[0].title == "Brihat Parashara Hora Shastra"
    assert mock_db.execute.call_count == 2


# ============================================================================
# Citation Management Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_citation(service, mock_db, sample_source):
    """Test creating a citation."""
    citation_data = schemas.CitationCreate(
        source_id=sample_source.id,
        insight_type="yoga",
        insight_text="Raj Yoga formed by 9th and 10th lord conjunction",
        confidence_level=ConfidenceLevel.HIGH,
        confidence_score=0.88
    )

    user_id = uuid4()

    # Mock get_source
    with patch.object(service, 'get_source', return_value=sample_source):
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        citation = await service.create_citation(mock_db, citation_data, user_id)

        assert citation.source_id == sample_source.id
        assert citation.insight_type == "yoga"
        assert citation.confidence_level == ConfidenceLevel.HIGH
        assert sample_source.citation_count == 11  # Incremented from 10

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_citation_source_not_found(service, mock_db):
    """Test creating citation with non-existent source."""
    citation_data = schemas.CitationCreate(
        source_id=uuid4(),
        insight_type="yoga",
        insight_text="Test insight",
        confidence_level=ConfidenceLevel.MEDIUM,
        confidence_score=0.5
    )

    # Mock get_source returning None
    with patch.object(service, 'get_source', return_value=None):
        with pytest.raises(ValueError, match="Source .* not found"):
            await service.create_citation(mock_db, citation_data)


@pytest.mark.asyncio
async def test_get_citation(service, mock_db, sample_citation):
    """Test retrieving a citation."""
    citation_id = sample_citation.id

    # Mock database query
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = sample_citation
    mock_db.execute = AsyncMock(return_value=mock_result)

    citation = await service.get_citation(mock_db, citation_id)

    assert citation is not None
    assert citation.id == citation_id
    assert citation.insight_type == "planet_position"


@pytest.mark.asyncio
async def test_update_citation_feedback(service, mock_db, sample_citation):
    """Test updating citation feedback."""
    citation_id = sample_citation.id

    # Mock get_citation
    with patch.object(service, 'get_citation', return_value=sample_citation):
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Test helpful feedback
        citation = await service.update_citation_feedback(mock_db, citation_id, is_helpful=True)

        assert citation.helpful_count == 1
        assert citation.view_count == 1

        # Test not helpful feedback
        citation = await service.update_citation_feedback(mock_db, citation_id, is_helpful=False)

        assert citation.not_helpful_count == 1
        assert citation.view_count == 2


# ============================================================================
# Validation Management Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_validation(service, mock_db, sample_citation):
    """Test creating a validation."""
    validation_data = schemas.ValidationCreate(
        citation_id=sample_citation.id,
        status=ValidationStatus.VALIDATED,
        confidence_adjustment=0.05,
        accuracy_score=0.92,
        comments="Well-cited from classical text"
    )

    validator_id = uuid4()

    # Mock get_citation
    with patch.object(service, 'get_citation', return_value=sample_citation):
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        validation = await service.create_validation(
            mock_db,
            validation_data,
            validator_id,
            validator_name="Expert"
        )

        assert validation.citation_id == sample_citation.id
        assert validation.status == ValidationStatus.VALIDATED
        assert validation.validator_id == validator_id
        assert sample_citation.confidence_score == 0.9  # 0.85 + 0.05

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_validation_citation_not_found(service, mock_db):
    """Test creating validation with non-existent citation."""
    validation_data = schemas.ValidationCreate(
        citation_id=uuid4(),
        status=ValidationStatus.PENDING
    )

    # Mock get_citation returning None
    with patch.object(service, 'get_citation', return_value=None):
        with pytest.raises(ValueError, match="Citation .* not found"):
            await service.create_validation(mock_db, validation_data, uuid4())


# ============================================================================
# Confidence Scoring Tests
# ============================================================================

@pytest.mark.asyncio
async def test_calculate_confidence_score_no_citations(service, mock_db):
    """Test confidence calculation with no citations."""
    insight_type = "nonexistent_yoga"

    # Mock empty citations
    with patch.object(service, 'get_citations_for_insight', return_value=[]):
        result = await service.calculate_confidence_score(mock_db, insight_type)

        assert result.insight_type == insight_type
        assert result.citation_count == 0
        assert result.final_confidence == 0.0
        assert result.confidence_level == ConfidenceLevel.VERY_LOW


@pytest.mark.asyncio
async def test_calculate_confidence_score_with_data(service, mock_db, sample_citation, sample_source, sample_validation):
    """Test confidence calculation with citations and validations."""
    insight_type = "planet_position"

    # Link objects
    sample_citation.source = sample_source
    sample_citation.validations = [sample_validation]

    # Mock citations
    with patch.object(service, 'get_citations_for_insight', return_value=[sample_citation]):
        result = await service.calculate_confidence_score(mock_db, insight_type)

        assert result.insight_type == insight_type
        assert result.citation_count == 1
        assert result.average_source_credibility == 0.95
        assert result.validation_count == 1
        assert result.final_confidence > 0.0


@pytest.mark.asyncio
async def test_verify_insight(service, mock_db, sample_citation, sample_source):
    """Test insight verification."""
    verification_request = schemas.InsightVerificationRequest(
        insight_type="yoga",
        insight_text="Raj Yoga",
        include_sources=True
    )

    # Link source to citation
    sample_citation.source = sample_source
    sample_citation.validations = []

    # Mock get_citations_for_insight
    with patch.object(service, 'get_citations_for_insight', return_value=[sample_citation]):
        result = await service.verify_insight(mock_db, verification_request)

        assert result.insight_type == "yoga"
        assert result.has_citations is True
        assert result.citation_count == 1
        assert len(result.citations) == 1


@pytest.mark.asyncio
async def test_confidence_score_bounds(service, mock_db, sample_citation):
    """Test that confidence scores stay within 0.0-1.0 bounds."""
    # Test upper bound
    validation_data = schemas.ValidationCreate(
        citation_id=sample_citation.id,
        status=ValidationStatus.VALIDATED,
        confidence_adjustment=0.5  # Large positive adjustment
    )

    sample_citation.confidence_score = 0.9

    with patch.object(service, 'get_citation', return_value=sample_citation):
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        await service.create_validation(mock_db, validation_data, uuid4())

        # Should be capped at 1.0
        assert sample_citation.confidence_score == 1.0


@pytest.mark.asyncio
async def test_confidence_score_lower_bound(service, mock_db, sample_citation):
    """Test confidence score lower bound."""
    validation_data = schemas.ValidationCreate(
        citation_id=sample_citation.id,
        status=ValidationStatus.VALIDATED,
        confidence_adjustment=-0.95  # Large negative adjustment
    )

    sample_citation.confidence_score = 0.5

    with patch.object(service, 'get_citation', return_value=sample_citation):
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        await service.create_validation(mock_db, validation_data, uuid4())

        # Should be capped at 0.0
        assert sample_citation.confidence_score == 0.0
