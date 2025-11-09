# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL: Read This First

**Before starting any development, review:**
- `docs/TROUBLESHOOTING_SESSION_2025-01-08.md` - Common pitfalls and solutions from recent migration

**Key Rules:**
1. ✅ **ALWAYS use Supabase REST API** (`get_supabase_client()`) for database operations
2. ❌ **NEVER use SQLAlchemy** (`get_db()`) - PostgreSQL ports are blocked
3. ✅ **Use `current_user["user_id"]`** NOT `current_user["sub"]`
4. ✅ **Add `timeout=30.0`** to all httpx.AsyncClient instances
5. ✅ **Verify database columns exist** before using in queries

## Project Overview

JioAstro is an AI-powered Vedic astrology and numerology application with accurate birth chart generation, comprehensive numerology analysis, and personalized interpretations using GPT-4.

**Tech Stack:**
- **Backend**: FastAPI (Python 3.11+) with Supabase REST API, astrology calculations (pyswisseph, kerykeion, vedastro), and OpenAI integration
- **Frontend**: Next.js 14 (TypeScript) with Tailwind CSS, shadcn/ui, and Supabase Auth
- **Database**: PostgreSQL via Supabase with Row-Level Security (REST API only)

**Core Features:**
- Birth Charts (D1-D60 divisional charts), Vimshottari Dasha, 40+ Yogas
- Dosha Detection (Manglik, Kaal Sarpa, Pitra, Grahan) - see `docs/DOSHA_SYSTEM.md`
- AI Readings (GPT-4), Numerology (Western & Vedic), Muhurta, Varshaphal
- Prashna (Horary), Chart Comparison, Compatibility, Remedies
- Shadbala, Transits, Evidence Mode, Knowledge Base

**Detailed Documentation:**
- `docs/DOSHA_SYSTEM.md` - Complete dosha detection reference (4 doshas, intensity, cancellations, remedies)
- `docs/YOGA_ENHANCEMENT.md` - Yoga detection system (40+ yogas, strength calculation, timing)
- `docs/DIVISIONAL_CHARTS_ANALYSIS.md` - Divisional charts (D2-D60 Shodashvarga system)
- `backend/docs/numerology/` - Numerology system (Western & Vedic)

## Development Commands

### Quick Start
```bash
# Both backend and frontend
./start.sh

# Backend only (http://localhost:8000, docs at /docs)
cd backend && source venv/bin/activate
uvicorn main:app --reload

# Frontend only (http://localhost:3000)
cd frontend && npm run dev
```

### Testing
```bash
# Backend tests
cd backend && source venv/bin/activate
pytest                                    # All tests
pytest -v                                 # Verbose
pytest tests/test_dosha_detection.py      # Specific file
pytest -m dosha                           # By marker (dosha, yoga, divisional)
pytest --cov=app --cov-report=html        # With coverage

# API testing
curl http://localhost:8000/health
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/v1/profiles
```

### Docker
```bash
docker-compose up              # Start all services
docker-compose up --build      # Build and start
docker-compose down            # Stop
docker-compose logs -f backend # View logs
```

## Architecture

### Database Access Pattern (CRITICAL)

**⚠️ IMPORTANT: ALL database operations MUST use Supabase REST API only. SQLAlchemy is DEPRECATED.**

**REQUIRED pattern:**

```python
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.supabase_client import SupabaseClient
from app.db.database import get_supabase_client

router = APIRouter()

@router.get("/items")
async def list_items(
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    user_id = current_user["sub"]

    # SELECT with filters
    items = await supabase.select(
        "items",
        filters={"user_id": user_id},
        order="created_at.desc",
        limit=10
    )

    # INSERT
    new_item = await supabase.insert("items", {"user_id": user_id, "name": "Item"})

    # UPDATE
    await supabase.update("items", filters={"id": item_id}, data={"name": "Updated"})

    # DELETE
    await supabase.delete("items", filters={"id": item_id})

    # COUNT
    total = await supabase.count("items", filters={"user_id": user_id})

    return {"items": items, "total": total}
```

**Why Supabase REST API?**
- PostgreSQL direct connections (port 5432) are blocked in deployment
- REST API works everywhere without network restrictions
- Row-Level Security properly enforced
- No connection pool management or timeout issues

**DO NOT:**
- ❌ Use SQLAlchemy ORM models (deprecated)
- ❌ Import `AsyncSession` or `get_db()` dependency
- ❌ Use `db.execute()`, `db.add()`, `db.commit()`, etc.

**DO:**
- ✅ Use `SupabaseClient` with `get_supabase_client()` dependency
- ✅ Use async methods: `select()`, `insert()`, `update()`, `delete()`, `count()`
- ✅ Define Pydantic schemas for request/response validation
- ✅ Work with dictionaries for database records

**Migration Status:**
- ✅ Prashna, Chart Comparison - fully migrated
- ⚠️ Legacy endpoints (profiles, charts, queries) - use SQLAlchemy (to be migrated)

### Backend Structure

```
app/
├── api/v1/endpoints/    # Route handlers (charts, profiles, readings, muhurta, etc.)
├── core/                # Config, security, supabase_client
├── db/                  # Database dependencies
├── models/              # SQLAlchemy ORM (DEPRECATED - do not use)
├── schemas/             # Pydantic validation schemas
└── services/            # Business logic
    ├── ai_orchestrator.py             # Multi-role AI reading orchestration
    ├── astrology.py                   # Chart calculations
    ├── divisional_charts_service.py   # D2-D60 divisional charts
    ├── dosha_detection_service.py     # 4 dosha detection
    ├── extended_yoga_service.py       # 40+ yoga detection
    ├── muhurta_service.py             # Panchang, Hora, Muhurta
    ├── numerology_service.py          # Western & Vedic numerology
    └── vedastro_service.py            # VedAstro integration
```

**Key Patterns:**
- All database operations use async/await
- Authentication via Supabase JWT (validated in `core/security.py`)
- Rate limiting for AI queries (10/day free tier)
- CORS configured in `core/config.py`

### Frontend Structure

```
app/
├── auth/               # Login, signup
├── dashboard/          # Protected routes
│   ├── chart/         # Birth charts
│   ├── yogas/         # Yoga analysis
│   ├── numerology/    # Numerology calculator
│   ├── muhurta/       # Panchang, Hora, auspicious times
│   ├── prashna/       # Horary astrology
│   ├── chart-comparison/ # Synastry
│   └── [others]/      # Varshaphal, compatibility, remedies, etc.
└── page.tsx           # Landing

components/
├── ui/                # shadcn/ui components
├── chart/             # DivisionalChartsDisplay, SouthIndianChart, etc.
├── numerology/        # NumerologyCard, CyclesTimeline, etc.
├── yoga/              # YogaDetailsModal, YogaActivationTimeline
└── [feature]/         # Feature-specific components

lib/
├── api.ts             # API client with JWT
└── supabase.ts        # Supabase auth client
```

**Key Patterns:**
- App Router (Next.js 14) with TypeScript
- Authentication via Supabase client
- API calls use axios with automatic JWT injection
- Form validation with react-hook-form + zod

## Important Technical Details

### Astrology Calculations
- **Zodiac**: Sidereal (Vedic), **Ayanamsa**: Lahiri
- **Libraries**: pyswisseph, kerykeion, vedastro
- **Charts**: D1 (Rashi), D9 (Navamsa), plus D2-D60 divisional charts
- **Dasha**: Vimshottari (120-year cycle)
- **Yogas**: 40+ classical yogas (see `docs/YOGA_ENHANCEMENT.md`)
- **Doshas**: 4 major doshas with intensity and cancellations (see `docs/DOSHA_SYSTEM.md`)

### Numerology System
Comprehensive Western (Pythagorean) and Vedic (Chaldean) numerology:
- **Western**: Life Path, Expression, Soul Urge, Personality, Maturity, Birth Day, Master Numbers, Karmic Debt, Personal Year/Month/Day, 4 Pinnacles, 4 Challenges
- **Vedic**: Psychic Number, Destiny Number, Name Number, planetary associations, favorable elements
- **Performance**: Single calculation < 0.01ms, Full profile < 0.12ms
- **Service**: `backend/app/services/numerology_service.py`
- **Docs**: `backend/docs/numerology/`

### Yoga Detection System
Detects 40+ classical Vedic yogas with strength calculation and timing:
- **Categories**: Pancha Mahapurusha (5), Raj, Dhana, Neecha Bhanga (4), Kala Sarpa (12), Nabhasa (10), Rare yogas
- **Strength**: Weighted score (planet dignity 60%, house strength 40%)
- **Timing**: Dasha activation prediction with age ranges
- **Performance**: Detection ~50-100ms for 40+ yogas
- **Service**: `backend/app/services/extended_yoga_service.py`
- **Docs**: `docs/YOGA_ENHANCEMENT.md`

### Dosha Detection System
Enhanced detection of 4 major doshas with intensity, cancellations, remedies:
- **Types**: Manglik (Mars), Kaal Sarpa (Rahu-Ketu axis), Pitra (ancestral), Grahan (eclipse)
- **Intensity**: 5-level scoring with manifestation periods
- **Cancellations**: Benefic protections reduce intensity
- **Remedies**: 3-tier stratification (base → low/medium → high/very_high)
- **Performance**: Complete analysis ~20-60ms
- **Service**: `backend/app/services/dosha_detection_service.py`
- **Docs**: `docs/DOSHA_SYSTEM.md` (complete reference)

### Divisional Charts (Varga Kundali)
Complete Shodashvarga system (16 divisional charts D2-D60):
- **Charts**: D2 (wealth), D3 (siblings), D4 (property), D7 (children), D9 (marriage), D10 (career), D12 (parents), D16 (vehicles), D20 (spiritual), D24 (education), D27 (strengths), D30 (obstacles), D40/D45/D60 (karma)
- **Performance**: All 15 charts ~10-15ms
- **Service**: `backend/app/services/divisional_charts_service.py`
- **Component**: `frontend/components/chart/DivisionalChartsDisplay.tsx`
- **Docs**: `docs/DIVISIONAL_CHARTS_ANALYSIS.md`

### AI Service
- **Model**: OpenAI GPT-4 Turbo
- **Service**: `backend/app/services/ai_service.py`
- **Rate Limiting**: 10 queries/day free tier
- **Context**: Chart data + user query

### Authentication Flow
1. Frontend uses Supabase Auth for login/signup
2. Supabase returns JWT token
3. Frontend includes token in Authorization header
4. Backend validates JWT using `SUPABASE_JWT_SECRET`
5. User ID links to database via Row-Level Security

### Database Schema
Key tables (see `docs/database-schema.sql`):
- `profiles`, `charts`, `queries`, `responses`, `feedback`
- `numerology_profiles`, `numerology_name_trials`
- `prashnas`, `chart_comparisons`

## Environment Variables

### Backend (`.env`)
```bash
DATABASE_URL=postgresql+asyncpg://[user]:[pass]@[host]:5432/[db]
SUPABASE_URL=https://[project].supabase.co
SUPABASE_KEY=[anon-key]
SUPABASE_JWT_SECRET=[jwt-secret]
OPENAI_API_KEY=sk-[your-key]
REDIS_URL=redis://localhost:6379  # Optional
RATE_LIMIT_QUERIES_PER_DAY=10
ENVIRONMENT=development
```

### Frontend (`.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://[project].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[anon-key]
```

## Common Development Workflows

### Adding a New API Endpoint
1. Define Pydantic schemas in `backend/app/schemas/`
2. Implement business logic in `backend/app/services/`
3. Create endpoint handler in `backend/app/api/v1/endpoints/`
4. Register route in router
5. Test via http://localhost:8000/docs

### Adding a New Frontend Page
1. Create page in `frontend/app/[route]/page.tsx`
2. Add UI components in `frontend/components/`
3. Use `frontend/lib/api.ts` for backend calls
4. Handle auth for protected routes
5. Test on http://localhost:3000

### Working with Astrology Calculations
- Main service: `backend/app/services/astrology.py`
- VedAstro: `backend/app/services/vedastro_service.py`
- Charts are cached in database
- Always validate birth data

### Working with Numerology
- Service: `backend/app/services/numerology_service.py`
- Classes: `WesternNumerology`, `VedicNumerology`, `NumerologyService`
- Testing: `backend/tests/test_numerology_golden_cases.py`
- Performance: Run `python scripts/benchmark_numerology.py`
- Frontend: `/dashboard/numerology`, `/dashboard/numerology/compare`

### Modifying AI Prompts
- Service: `backend/app/services/ai_service.py`
- Prompts = chart context + user query
- Consider token limits
- Test with different query types

## Common Pitfalls

1. **Database**: Ensure `postgresql+asyncpg://` prefix for async
2. **CORS**: Check `ALLOWED_ORIGINS` in `backend/app/core/config.py`
3. **JWT**: Ensure `SUPABASE_JWT_SECRET` matches Supabase dashboard
4. **Venv**: Always activate backend venv before Python commands
5. **Redis**: Optional; falls back to in-memory if unavailable
6. **OpenAI**: Verify account has credits before testing AI features

## Deployment

- **Backend**: Railway.app or GCP Cloud Run
- **Frontend**: Vercel
- **Database**: Supabase (PostgreSQL)
- **Cache**: Upstash Redis for production

See `docs/DEPLOYMENT.md` for details.

## Project Status

**Production-ready** with comprehensive features across all major Vedic astrology domains.

**Completed (100%):**
- Core Platform: Auth, Profiles, Feedback
- Astrology: Birth Charts, AI Readings, Dasha, Yogas, Shadbala, Transits, Varshaphal, Compatibility, Remedies, Rectification
- Muhurta: Panchang, Hora, Muhurta Finder, Sunrise/Sunset
- Numerology: Western & Vedic systems, Life Cycles, Name Analysis (11 API endpoints)
- UX: Instant Onboarding, Life Snapshot, Evidence Mode, Knowledge Base, History
- Advanced: Prashna (5 endpoints), Chart Comparison, Dosha Detection (4 doshas), Divisional Charts (D2-D60)

**Feature Count:** 40+ yogas, 4 doshas, 16 divisional charts, 11 numerology endpoints, 5 prashna endpoints
