# Evidence Mode - Implementation Guide

**Magical 12 Feature #8**
**Status:** ✅ Core Implementation Complete
**Date:** November 7, 2025
**Author:** Claude AI

---

## Overview

Evidence Mode provides a comprehensive citation-backed trust system for astrological insights. It allows tracking of sources, citations, validations, and confidence scoring to build user trust through transparent evidence-based interpretations.

### Key Features

- **Source Management**: Classical texts, research papers, expert opinions, statistical data
- **Citation Tracking**: Links insights to supporting evidence sources
- **Validation Workflow**: Expert peer review and validation system
- **Confidence Scoring**: Algorithmic confidence calculation based on multiple factors
- **Insight Verification**: Real-time evidence lookup for astrological interpretations

---

## Architecture

### Database Schema

**Three Core Tables:**

1. **evidence_mode_sources** - Reference materials
   - Classical Vedic texts (BPHS, Jataka Parijata, etc.)
   - Research papers and academic studies
   - Expert opinions and traditional teachings
   - Statistical analysis and modern studies

2. **evidence_mode_citations** - Insight-to-source links
   - Maps astrological insights to supporting sources
   - Tracks confidence levels and relevance scores
   - User feedback (helpful/not helpful)

3. **evidence_mode_validations** - Expert reviews
   - Peer validation of citations
   - Confidence adjustments
   - Alternative source suggestions

### Service Layer

`service.py` implements:
- CRUD operations for sources, citations, validations
- Advanced search and filtering
- Confidence score calculation (weighted algorithm)
- Insight verification with evidence lookup

### API Endpoints

**Base Path:** `/api/v2/evidence-mode`

**Sources:**
- `POST /sources` - Create source
- `GET /sources/{id}` - Get source
- `POST /sources/search` - Search sources
- `PATCH /sources/{id}` - Update source
- `DELETE /sources/{id}` - Delete source

**Citations:**
- `POST /citations` - Create citation
- `GET /citations/{id}` - Get citation
- `POST /citations/search` - Search citations
- `POST /citations/{id}/feedback` - Submit feedback

**Validations:**
- `POST /validations` - Create validation
- `GET /citations/{id}/validations` - Get validations

**Verification:**
- `POST /verify` - Verify insight with evidence
- `GET /confidence/{insight_type}` - Calculate confidence
- `GET /insights/{type}/citations` - Get citations by type

---

## Configuration

### Environment Variables

```bash
# Enable Evidence Mode feature
FEATURE_EVIDENCE_MODE=true
```

### Feature Registration

Evidence Mode is registered in `main.py`:

```python
from app.features.evidence_mode import evidence_mode_feature

# Register feature
feature_registry.register(evidence_mode_feature)

# Include router
app.include_router(evidence_mode_feature.router, prefix="/api/v2")
```

---

## Database Setup

### Running the Migration

```bash
# Connect to your PostgreSQL database
psql $DATABASE_URL

# Run the migration
\i app/features/evidence_mode/migration.sql
```

Or using SQLAlchemy (if Alembic is configured):

```bash
alembic revision --autogenerate -m "Add Evidence Mode tables"
alembic upgrade head
```

### Row-Level Security

The migration includes RLS policies for Supabase:
- Public sources viewable by all authenticated users
- Users can create/update their own sources
- Active citations viewable by all authenticated users
- Public validations viewable by all authenticated users

---

## Usage Examples

### 1. Create an Evidence Source

```bash
curl -X POST http://localhost:8000/api/v2/evidence-mode/sources \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Brihat Parashara Hora Shastra",
    "author": "Maharishi Parashara",
    "source_type": "classical_text",
    "description": "The foundational text of Vedic astrology",
    "excerpt": "Chapter 3, Verse 12: Mars in 10th house gives courage...",
    "publication_year": 500,
    "language": "sanskrit",
    "tags": ["classical", "vedic", "bhava", "graha"],
    "is_verified": true
  }'
```

### 2. Create a Citation

```bash
curl -X POST http://localhost:8000/api/v2/evidence-mode/citations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "uuid-of-source",
    "insight_type": "planet_position",
    "insight_text": "Mars in 10th house indicates strong career drive",
    "confidence_level": "high",
    "confidence_score": 0.85,
    "reasoning": "BPHS Chapter 3 explicitly states this placement",
    "context": {
      "planet": "Mars",
      "house": 10,
      "chart_type": "D1"
    }
  }'
```

### 3. Verify an Insight

```bash
curl -X POST http://localhost:8000/api/v2/evidence-mode/verify \
  -H "Content-Type: application/json" \
  -d '{
    "insight_type": "yoga",
    "insight_text": "Raj Yoga formed by 9th and 10th lord conjunction",
    "include_sources": true
  }'
```

**Response:**
```json
{
  "insight_type": "yoga",
  "insight_text": "Raj Yoga formed by 9th and 10th lord conjunction",
  "has_citations": true,
  "citation_count": 5,
  "average_confidence": 0.88,
  "highest_confidence": 0.95,
  "citations": [
    {
      "id": "...",
      "source": {
        "title": "Brihat Parashara Hora Shastra",
        "author": "Maharishi Parashara",
        "source_type": "classical_text",
        "credibility_score": 0.95
      },
      "confidence_level": "very_high",
      "reasoning": "Classic definition of Raj Yoga"
    }
  ]
}
```

### 4. Calculate Confidence Score

```bash
curl http://localhost:8000/api/v2/evidence-mode/confidence/raj_yoga
```

**Response:**
```json
{
  "insight_type": "raj_yoga",
  "base_confidence": 0.82,
  "citation_count": 12,
  "average_source_credibility": 0.89,
  "validation_count": 8,
  "average_validation_score": 0.91,
  "final_confidence": 0.87,
  "confidence_level": "very_high"
}
```

---

## Confidence Scoring Algorithm

The confidence score is calculated using a weighted formula:

```python
final_confidence = (
    base_confidence * 0.4 +      # Average citation confidence
    source_credibility * 0.3 +   # Average source credibility
    validation_score * 0.3       # Average validation scores
)
```

**Confidence Levels:**
- **Very High**: 0.90 - 1.00 (90-100%)
- **High**: 0.75 - 0.89 (75-89%)
- **Medium**: 0.50 - 0.74 (50-74%)
- **Low**: 0.25 - 0.49 (25-49%)
- **Very Low**: 0.00 - 0.24 (0-24%)

---

## Integration with AI Service

Evidence Mode can be integrated with the AI interpretation service:

```python
from app.features.evidence_mode.service import evidence_mode_service

async def generate_interpretation_with_evidence(
    db: AsyncSession,
    insight: str,
    insight_type: str
):
    # Generate AI interpretation
    ai_response = await ai_service.generate_interpretation(insight)

    # Get supporting evidence
    verification = await evidence_mode_service.verify_insight(
        db=db,
        verification_request=InsightVerificationRequest(
            insight_type=insight_type,
            insight_text=insight
        )
    )

    # Combine AI + Evidence
    return {
        "interpretation": ai_response,
        "evidence": verification,
        "confidence": verification.average_confidence
    }
```

---

## Testing

### Unit Tests

```bash
# Run Evidence Mode tests
pytest app/features/evidence_mode/tests/ -v

# With coverage
pytest --cov=app/features/evidence_mode app/features/evidence_mode/tests/
```

### Integration Tests

Test all API endpoints:

```bash
pytest app/features/evidence_mode/tests/test_api.py -v
```

---

## Performance Considerations

### Database Indexes

The migration includes optimized indexes:
- Source title and type search
- Citation lookup by insight type
- Confidence score ordering
- Full-text search on titles and descriptions
- JSONB indexes for tags and keywords

### Caching Strategy (Future Enhancement)

Consider caching:
- Popular source lookups (TTL: 1 hour)
- Confidence scores by insight type (TTL: 30 minutes)
- Top sources list (TTL: 1 hour)

---

## Security

### Row-Level Security (RLS)

All tables use Supabase RLS policies:
- Authenticated users can view public sources/citations
- Users can only update their own content
- Validators can only update their own validations

### Input Validation

All inputs are validated using Pydantic schemas:
- String length limits
- Score range validation (0.0 to 1.0)
- UUID format validation
- Enum type checking

---

## Future Enhancements

### Phase 2 Roadmap

1. **AI-Powered Citation Suggestions**
   - Automatically suggest relevant sources for insights
   - Use embeddings to match insights with classical texts

2. **Expert Dashboard**
   - Dedicated interface for validators
   - Validation leaderboard
   - Citation quality metrics

3. **Source Import Tools**
   - Bulk import from classical texts
   - PDF parsing for research papers
   - Integration with academic databases

4. **Citation Analytics**
   - Insight coverage reports
   - Source utilization statistics
   - Validation trends

5. **Public Evidence Explorer**
   - Frontend UI for browsing sources
   - Citation graph visualization
   - Confidence score explanations

---

## Troubleshooting

### Common Issues

**1. Feature Not Enabled**
```
Error: Feature 'evidence_mode' is not enabled
```
**Solution:** Set `FEATURE_EVIDENCE_MODE=true` in `.env`

**2. Migration Fails**
```
Error: type "evidence_source_type" already exists
```
**Solution:** Drop existing types or use `DROP TYPE IF EXISTS CASCADE`

**3. RLS Blocking Queries**
```
Error: new row violates row-level security policy
```
**Solution:** Ensure proper authentication token and user permissions

---

## API Documentation

Full API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Filter by tag: "Evidence Mode" to see all endpoints.

---

## Contact & Support

- **Feature Owner:** Claude AI
- **Magical Number:** #8
- **Version:** 1.0.0
- **Status:** Core Implementation Complete

For questions or issues, please refer to the main project README or create an issue in the project repository.
