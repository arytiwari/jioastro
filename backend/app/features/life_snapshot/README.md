# Life Snapshot Feature

**Magical 12 Feature #1**

## Overview

60-second personalized life insights powered by AI. This feature provides users with a quick snapshot of their current life situation based on their birth chart, current transits, and AI-powered interpretation.

## Author

AI Assistant / Development Team

## Version

1.0.0 (Template)

## Status

🚧 **Under Development** - This is a template feature for demonstration

## Description

The Life Snapshot feature generates a concise, 60-second summary of a user's current astrological situation, including:

- Current major transits affecting the user
- Key planetary positions and their meanings
- Top 3 insights for the current period
- One actionable recommendation
- Overall life phase assessment

## Architecture

###

 Module Structure

```
life_snapshot/
├── __init__.py           # Module exports
├── README.md            # This file
├── feature.py           # Feature registration & router
├── models.py            # Database models
├── schemas.py           # Pydantic schemas
├── service.py           # Business logic
├── api.py               # API endpoints
├── constants.py         # Constants
├── dependencies.py      # Feature dependencies
└── tests/
    ├── test_models.py
    ├── test_service.py
    └── test_api.py
```

### Database Schema

**Table: `life_snapshot_data`**

```sql
CREATE TABLE life_snapshot_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    profile_id UUID NOT NULL REFERENCES profiles(id),
    snapshot_data JSONB NOT NULL,
    transits_data JSONB,
    insights JSONB NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    cache_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_life_snapshot_user_id ON life_snapshot_data(user_id);
CREATE INDEX idx_life_snapshot_profile_id ON life_snapshot_data(profile_id);
CREATE INDEX idx_life_snapshot_cache_key ON life_snapshot_data(cache_key);
CREATE INDEX idx_life_snapshot_generated_at ON life_snapshot_data(generated_at);
```

## API Endpoints

### 1. Generate Snapshot

```
POST /api/v2/life-snapshot/generate
```

Generate a new life snapshot for the current user.

**Request:**
```json
{
  "profile_id": "uuid",
  "force_refresh": false
}
```

**Response:**
```json
{
  "snapshot_id": "uuid",
  "profile": {
    "id": "uuid",
    "name": "John Doe"
  },
  "generated_at": "2025-11-07T10:30:00Z",
  "expires_at": "2025-11-07T11:30:00Z",
  "transits": [...],
  "insights": {
    "top_insights": ["Insight 1", "Insight 2", "Insight 3"],
    "recommendation": "Focus on...",
    "life_phase": "Growth Period"
  },
  "read_time_seconds": 60
}
```

### 2. Get Snapshot

```
GET /api/v2/life-snapshot/{snapshot_id}
```

Retrieve an existing snapshot.

### 3. List Snapshots

```
GET /api/v2/life-snapshot/list?profile_id={uuid}&limit=10
```

List recent snapshots for a profile.

## Feature Flag

```bash
# Enable in environment
FEATURE_LIFE_SNAPSHOT=true

# Check in code
from app.core.feature_flags import check_feature, require_feature

if check_feature("life_snapshot"):
    # Feature is enabled
    pass

# Use as decorator
@require_feature("life_snapshot")
async def generate_snapshot(...):
    pass
```

## Development Workflow

### 1. Set Up Development Environment

```bash
# Enable feature flag
export FEATURE_LIFE_SNAPSHOT=true

# Create database migration
cd backend
alembic revision --autogenerate -m "life_snapshot: add snapshot tables"

# Run migration
alembic upgrade head
```

### 2. Run Tests

```bash
# Unit tests
pytest app/features/life_snapshot/tests/test_service.py -v

# Integration tests
pytest app/features/life_snapshot/tests/test_api.py -v

# Coverage
pytest app/features/life_snapshot/ --cov=app/features/life_snapshot --cov-report=html
```

### 3. Test API

```bash
# Start backend
uvicorn main:app --reload

# Test endpoint
curl -X POST http://localhost:8000/api/v2/life-snapshot/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "uuid"}'
```

## Dependencies

### Internal Dependencies
- `app.core.security` - Authentication
- `app.services.astrology` - Chart calculations
- `app.services.ai_service` - AI insights
- `app.models.profile` - User profiles

### External Dependencies
- OpenAI API - AI-powered insights
- Redis - Caching (optional)

## Configuration

```python
# app/features/life_snapshot/config.py

SNAPSHOT_CACHE_TTL = 3600  # 1 hour
SNAPSHOT_MAX_AGE = 86400  # 24 hours
INSIGHTS_COUNT = 3
READ_TIME_SECONDS = 60
```

## Testing

### Unit Test Example

```python
def test_generate_snapshot():
    """Test snapshot generation."""
    service = LifeSnapshotService()
    snapshot = service.generate_snapshot(
        user_id="test_user",
        profile_id="test_profile"
    )

    assert snapshot is not None
    assert len(snapshot.insights.top_insights) == 3
    assert snapshot.read_time_seconds == 60
```

### Integration Test Example

```python
async def test_generate_snapshot_endpoint(client, auth_headers):
    """Test snapshot generation endpoint."""
    response = await client.post(
        "/api/v2/life-snapshot/generate",
        headers=auth_headers,
        json={"profile_id": "test_profile"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "snapshot_id" in data
    assert "insights" in data
```

## Performance

- Target response time: < 2 seconds
- Cache hit rate: > 80%
- AI API timeout: 5 seconds
- Database query time: < 100ms

## Security

- Requires authentication
- User can only access their own snapshots
- Rate limiting: 10 requests per minute
- Sensitive data encrypted at rest

## Monitoring

```python
# Log snapshot generation
logger.info(f"Generated snapshot for user {user_id}, profile {profile_id}")

# Track metrics
metrics.increment("life_snapshot.generated")
metrics.timing("life_snapshot.generation_time", elapsed_time)
metrics.increment("life_snapshot.cache_hit" if cached else "life_snapshot.cache_miss")
```

## Future Enhancements

- [ ] Voice narration of insights
- [ ] Shareable snapshot cards
- [ ] Personalized notification timing
- [ ] Multi-language support
- [ ] Snapshot comparison over time

## Related Features

- **Life Threads** (#2) - Extended timeline view
- **Transit Pulse** (#4) - Real-time transit alerts
- **Evidence Mode** (#8) - Citations for insights

## Support

For questions or issues:
- Check this README
- Review implementation in `service.py`
- Ask in team channel
- Create GitHub issue

---

**Status:** Template - Ready for implementation
**Last Updated:** 2025-11-07
**Next Review:** When implementation starts
