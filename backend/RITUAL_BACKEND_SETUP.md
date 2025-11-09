# Guided Rituals Backend Setup

## Step 1: Run Database Migration

The ritual tables migration needs to be run via Supabase SQL Editor:

1. Go to your Supabase Dashboard
2. Navigate to SQL Editor
3. Copy the contents of `migrations/create_ritual_tables.sql`
4. Execute the SQL script

This will create:
- `ritual_templates` table
- `user_ritual_sessions` table
- Indexes for performance
- Row Level Security policies
- Triggers for updated_at fields

## Step 2: Seed Ritual Templates

After the migration is complete, seed the database with 10 ritual templates:

```bash
cd backend
source venv/bin/activate
python scripts/seed_ritual_templates.py
```

This will insert:
- 3 Daily rituals (Morning Prayers, Ganesh Puja, Evening Aarti)
- 2 Meditation rituals (Gayatri Japa, Om Meditation)
- 2 Special rituals (Satyanarayan Puja, Griha Pravesh)
- 2 Remedial rituals (Navagraha Puja, Mangal Shanti)
- 1 Festival ritual (Diwali Lakshmi Puja)

## Step 3: Verify Backend

The backend API is already configured and running. Verify the endpoints:

```bash
# Health check
curl http://localhost:8000/health

# List rituals (requires auth token)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/rituals

# API documentation
open http://localhost:8000/docs
```

## Available Endpoints

### Ritual Templates
- `GET /api/v1/rituals` - List all rituals with filters
- `GET /api/v1/rituals/{id}` - Get specific ritual details
- `GET /api/v1/rituals/search?q=query` - Search rituals

### Ritual Sessions
- `POST /api/v1/rituals/{id}/start` - Start a new ritual session
- `PUT /api/v1/rituals/sessions/{id}/progress` - Update progress
- `POST /api/v1/rituals/sessions/{id}/pause` - Pause session
- `POST /api/v1/rituals/sessions/{id}/resume` - Resume session
- `POST /api/v1/rituals/sessions/{id}/complete` - Complete session
- `POST /api/v1/rituals/sessions/{id}/abandon` - Abandon session
- `GET /api/v1/rituals/sessions/history` - Get user history
- `GET /api/v1/rituals/sessions/stats` - Get user statistics
- `GET /api/v1/rituals/sessions/{id}` - Get session details
- `DELETE /api/v1/rituals/sessions/{id}` - Delete session

## Files Created

### Core Backend Files
1. `app/services/ritual_service.py` - Core business logic
2. `app/schemas/ritual.py` - Pydantic schemas
3. `app/api/v1/endpoints/rituals.py` - API endpoints
4. `migrations/create_ritual_tables.sql` - Database schema
5. `scripts/seed_ritual_templates.py` - Seed data

### Configuration
- Router registered in `app/api/v1/router.py`
- Service uses Supabase REST API (no SQLAlchemy)
- Row Level Security enabled for user sessions

## Next Steps

Proceed to frontend implementation:
1. Ritual library page (`frontend/app/dashboard/rituals/page.tsx`)
2. Ritual player component
3. Voice synthesis integration
