# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JioAstro is an AI-powered Vedic astrology application with accurate birth chart generation and personalized interpretations using GPT-4. The project consists of:
- **Backend**: FastAPI (Python 3.11+) with async PostgreSQL, astrology calculations (pyswisseph, kerykeion, vedastro), and OpenAI integration
- **Frontend**: Next.js 14 (TypeScript) with Tailwind CSS, shadcn/ui, and Supabase Auth
- **Database**: PostgreSQL via Supabase with Row-Level Security policies

## Development Commands

### Starting Services

```bash
# Quick start (both backend and frontend)
./start.sh

# Backend only
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload
# Runs on http://localhost:8000
# API docs at http://localhost:8000/docs

# Frontend only
cd frontend
npm run dev
# Runs on http://localhost:3000
```

### Backend Development

```bash
# Create virtual environment (first time)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run backend
uvicorn main:app --reload

# Test database connection
python test_db_connection.py

# Run with specific host/port
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Install dependencies (first time)
cd frontend
npm install

# Development
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Docker Commands

```bash
# Start all services with Docker Compose
docker-compose up

# Build and start
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Testing

```bash
# Backend: Test API endpoints
curl http://localhost:8000/health

# Test with authentication
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/profiles
```

## Architecture

### Backend Structure (`backend/`)

```
app/
├── api/v1/endpoints/    # API route handlers
│   ├── charts.py        # Chart generation endpoints
│   ├── feedback.py      # User feedback endpoints
│   ├── profiles.py      # Birth profile CRUD
│   └── queries.py       # AI query endpoints
├── core/                # Core configuration
│   ├── config.py        # Environment config, CORS settings
│   └── security.py      # JWT authentication helpers
├── db/                  # Database setup
│   └── database.py      # SQLAlchemy async session management
├── models/              # SQLAlchemy ORM models
│   ├── chart.py         # Birth chart data
│   ├── feedback.py      # User feedback
│   ├── profile.py       # Birth profiles
│   ├── query.py         # User queries
│   └── response.py      # AI responses
├── schemas/             # Pydantic validation schemas
│   └── [model].py       # Request/response schemas
└── services/            # Business logic
    ├── astrology.py     # Chart calculations (pyswisseph, kerykeion)
    ├── ai_service.py    # OpenAI GPT-4 integration
    └── vedastro_service.py  # VedAstro library integration
```

**Key Backend Patterns:**
- All database operations use async/await with SQLAlchemy
- Authentication via Supabase JWT tokens (validated in `core/security.py`)
- Rate limiting implemented for AI queries (10 per day for free tier)
- CORS configured in `core/config.py` for frontend origin

### Frontend Structure (`frontend/`)

```
app/
├── auth/               # Authentication pages
│   ├── login/         # Login page
│   └── signup/        # Registration page
├── dashboard/         # Protected dashboard routes
│   ├── ask/          # Ask questions to AI
│   ├── chart/        # View birth charts
│   ├── history/      # Query history
│   ├── knowledge/    # Vedic knowledge base
│   └── profiles/     # Birth profile management
└── page.tsx          # Landing page

components/
├── ui/               # shadcn/ui components (button, card, etc.)
├── chart/           # Chart visualization components
└── [feature]/       # Feature-specific components

lib/
├── api.ts           # API client with JWT handling
└── supabase.ts      # Supabase auth client
```

**Key Frontend Patterns:**
- App Router (Next.js 14) with TypeScript
- Authentication state managed via Supabase client
- API calls use axios with automatic JWT token injection
- Form validation with react-hook-form + zod
- State management with Zustand for local state

## Important Technical Details

### Astrology Calculations
- **Zodiac System**: Sidereal (Vedic)
- **Ayanamsa**: Lahiri (standard in Vedic astrology)
- **Libraries**: pyswisseph (Swiss Ephemeris), kerykeion, vedastro
- **Chart Types**: D1 (Rashi/Birth), D9 (Navamsa), with plans for D7, D10, D12
- **Dasha System**: Vimshottari (120-year cycle)
- **Yogas Detected**: Raj Yoga, Dhana Yoga, Gaja Kesari, Budhaditya, etc.

### AI Service Integration
- **Model**: OpenAI GPT-4 Turbo
- **Service**: Located in `backend/app/services/ai_service.py`
- **Rate Limiting**: 10 queries per day for free users (configurable via `RATE_LIMIT_QUERIES_PER_DAY`)
- **Context**: Chart data and user query sent to GPT-4 for personalized interpretations

### Authentication Flow
1. Frontend uses Supabase Auth for login/signup
2. Supabase returns JWT token
3. Frontend stores token and includes in API requests via Authorization header
4. Backend validates JWT using `SUPABASE_JWT_SECRET` in `core/security.py`
5. User ID from JWT links to database records via Row-Level Security

### Database Schema
Key tables (see `docs/database-schema.sql`):
- `profiles`: Birth data (name, DOB, location, timezone)
- `charts`: Cached chart calculations (planet positions, houses)
- `queries`: User questions
- `responses`: AI-generated interpretations
- `feedback`: User ratings for response quality

## Environment Variables

### Backend (`.env`)
```bash
DATABASE_URL=postgresql+asyncpg://[user]:[pass]@[host]:5432/[db]
SUPABASE_URL=https://[project].supabase.co
SUPABASE_KEY=[anon-key]
SUPABASE_JWT_SECRET=[jwt-secret]
OPENAI_API_KEY=sk-[your-key]
REDIS_URL=redis://localhost:6379  # Optional, for rate limiting
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
2. Add database model if needed in `backend/app/models/`
3. Implement business logic in `backend/app/services/`
4. Create endpoint handler in `backend/app/api/v1/endpoints/`
5. Register route in `backend/main.py` or respective router
6. Test via http://localhost:8000/docs (Swagger UI)

### Adding a New Frontend Page
1. Create page component in `frontend/app/[route]/page.tsx`
2. Add necessary UI components in `frontend/components/`
3. Use API client from `frontend/lib/api.ts` for backend calls
4. Handle authentication checks for protected routes
5. Test on http://localhost:3000

### Working with Astrology Calculations
- Main calculation service: `backend/app/services/astrology.py`
- VedAstro integration: `backend/app/services/vedastro_service.py`
- Chart calculations are cached in database to avoid recomputation
- Always validate birth data (valid date, time, location coordinates)

### Modifying AI Prompts
- AI service: `backend/app/services/ai_service.py`
- Prompts are constructed with chart context + user query
- Consider token limits when building prompts
- Test prompt changes with different query types (career, relationships, health)

## Common Pitfalls

1. **Database Connection**: Ensure DATABASE_URL uses `postgresql+asyncpg://` prefix for async support
2. **CORS Issues**: Check `ALLOWED_ORIGINS` in `backend/app/core/config.py` includes frontend URL
3. **JWT Validation**: Ensure SUPABASE_JWT_SECRET matches the value from Supabase dashboard
4. **Virtual Environment**: Always activate backend venv before running Python commands
5. **Rate Limiting**: Redis is optional; rate limiting falls back to in-memory if Redis unavailable
6. **OpenAI Credits**: Verify OpenAI account has available credits before testing AI features

## Deployment

- **Backend**: Recommended on Railway.app or GCP Cloud Run
- **Frontend**: Recommended on Vercel
- **Database**: Uses Supabase (PostgreSQL)
- **Cache**: Upstash Redis for production rate limiting

See `docs/DEPLOYMENT.md` for detailed deployment instructions.

## Project Status

The MVP is functionally complete with authentication, birth chart generation, AI interpretations, and feedback collection. The application is ready for deployment and user testing.
