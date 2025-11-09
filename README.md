# Vedic AI Astrology - MVP

AI-powered Vedic astrology service with accurate birth chart generation and personalized interpretations using GPT-4.

## 🌟 Features

### Core Functionality (MVP)
- ✅ User registration and authentication (Supabase Auth)
- ✅ Birth chart generation (Rashi D-1 and Navamsa D-9)
- ✅ **Complete Divisional Charts System (Shodashvarga)** - All 16 classical divisions
  - D2-D60 automatic calculation with D1 chart
  - Vimshopaka Bala (composite planetary strength across all vargas)
  - 7-tier strength classification (Parijatamsa to Brahmalokamsa)
  - Divisional yoga detection (Raj, Dhana, Jupiter-Venus)
  - AI-integrated interpretations for each chart
  - 4 dedicated API endpoints for full access
- ✅ AI-powered personalized interpretations (OpenAI GPT-4)
- ✅ Natural language query interface
- ✅ Mobile-responsive, clean UI
- ✅ Feedback system for continuous improvement
- ✅ Vimshottari Dasha calculation (120-year planetary periods)
- ✅ Extended Yoga Detection (40+ classical planetary combinations)
  - Strength calculation & cancellation detection
  - Timing prediction based on dasha periods
  - Historical examples & remedies
  - Interactive timeline visualization
- ✅ **Enhanced Dosha Detection** - Classical afflictions with intensity analysis
  - **Manglik Dosha**: 5-level intensity (Mars from Lagna/Moon/Venus), age-based manifestation, 90% cancellation analysis
  - **Kaal Sarpa Yoga**: 12 variations (Full/Partial classification), type-specific effects & positive outcomes
  - **Pitra Dosha**: 11 indicators (paternal/maternal/progeny/karmic lineage analysis)
  - **Grahan Dosha**: Degree-based intensity (4 eclipse types), benefic protection, mental health support
  - Categorized remedies by severity (base → low/medium → high/very_high)

### Technical Features
- ⚡ FastAPI backend with async/await
- 🎨 Next.js 14 frontend with App Router
- 🔐 Secure authentication with JWT
- 📊 PostgreSQL database (Supabase)
- 🚀 Ready for deployment (Railway + Vercel)
- 📱 PWA-ready for mobile
- 🎯 Rate limiting (10 queries/day for free tier)

## 🏗️ Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Next.js 14    │ ───▶ │   FastAPI       │ ───▶ │   PostgreSQL    │
│   Frontend      │      │   Backend       │      │   (Supabase)    │
│   (Vercel)      │      │   (Railway)     │      └─────────────────┘
└─────────────────┘      └─────────────────┘
                               │
                               ▼
                         ┌─────────────────┐
                         │   OpenAI GPT-4  │
                         │   Interpretation │
                         └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or Supabase account)
- OpenAI API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run database migrations (if using Supabase, run docs/database-schema.sql in SQL editor)

# Start server
uvicorn main:app --reload
```

Backend will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URL and Supabase keys

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📦 Project Structure

```
jioastro/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Config, security
│   │   ├── db/             # Database setup
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   │       ├── ai_orchestrator.py  # Multi-role AI orchestration
│   │       ├── ai_service.py       # AI interpretations
│   │       ├── astrology.py        # Chart calculations
│   │       └── extended_yoga_service.py  # 40+ yoga detection
│   ├── main.py             # App entry point
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Docker config
│
├── frontend/               # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   │   ├── ui/           # shadcn/ui components
│   │   ├── chart/        # Chart visualizations
│   │   └── yoga/         # Yoga components (modal, timeline)
│   ├── lib/              # Utilities
│   │   ├── api.ts       # API client
│   │   └── supabase.ts  # Auth client
│   ├── package.json
│   └── tailwind.config.ts
│
└── docs/                  # Documentation
    ├── database-schema.sql
    ├── DEPLOYMENT.md
    ├── YOGA_ENHANCEMENT.md  # Comprehensive yoga system guide
    └── YOGA_API.md          # Yoga API reference
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-key
SUPABASE_JWT_SECRET=your-secret
OPENAI_API_KEY=sk-your-key
REDIS_URL=redis://localhost:6379
RATE_LIMIT_QUERIES_PER_DAY=10
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## 🎯 API Endpoints

### Authentication
Uses Supabase Auth (handled by frontend)

### Profiles
- `POST /api/v1/profiles` - Create birth profile
- `GET /api/v1/profiles` - List profiles
- `GET /api/v1/profiles/{id}` - Get profile
- `PATCH /api/v1/profiles/{id}` - Update profile
- `DELETE /api/v1/profiles/{id}` - Delete profile

### Charts
- `POST /api/v1/charts/calculate` - Calculate chart (D1, D9, Moon)
- `GET /api/v1/charts/{profile_id}/{chart_type}` - Get chart
- `GET /api/v1/charts/{profile_id}/divisional/all` - Get all divisional charts (D2-D60)
- `GET /api/v1/charts/{profile_id}/divisional/{division}` - Get specific divisional chart
- `GET /api/v1/charts/{profile_id}/vimshopaka-bala` - Get planetary strength across all vargas
- `GET /api/v1/charts/{profile_id}/divisional/{division}/yogas` - Get yogas in divisional chart

### Queries
- `POST /api/v1/queries` - Submit question (get AI interpretation)
- `GET /api/v1/queries` - List query history
- `GET /api/v1/queries/{id}` - Get specific query

### Feedback
- `POST /api/v1/feedback` - Submit feedback
- `GET /api/v1/feedback/stats` - Get statistics

## 🔬 Astrological Calculations

- **Zodiac System**: Sidereal (Vedic)
- **Ayanamsa**: Lahiri (most common in Vedic astrology)
- **Ephemeris**: Swiss Ephemeris (via pyswisseph)
- **Chart Types**: D1 (Rashi/Birth chart), D9 (Navamsa), Moon Chart
- **Divisional Charts**: Complete Shodashvarga system (16 classical divisions)
  - D2 (Hora): Wealth & prosperity
  - D3 (Drekkana): Siblings, courage
  - D4 (Chaturthamsa): Property, assets
  - D7 (Saptamsa): Children, progeny
  - D10 (Dashamsa): Career, profession
  - D12 (Dwadashamsa): Parents, ancestry
  - D16, D20, D24, D27, D30, D40, D45, D60: Specialized analyses
- **Dasha System**: Vimshottari (120-year cycle)
- **Yogas**: 40+ classical yogas detected with strength calculation and timing prediction
  - Pancha Mahapurusha (Hamsa, Malavya, Sasha, Ruchaka, Bhadra)
  - Raj Yoga, Dhana Yoga, Neecha Bhanga Raj Yoga
  - Kala Sarpa Yoga (12 types)
  - Nabhasa Yogas (Rajju, Musala, Nala, Maala, and more)
  - Gaja Kesari, Budhaditya, and rare yogas

## 🎨 Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Auth**: Supabase Auth with JWT
- **Astrology**: pyswisseph + kerykeion
- **AI**: OpenAI GPT-4 Turbo
- **Cache**: Redis (optional, for rate limiting)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI)
- **State Management**: React Query + Zustand
- **Charts**: Custom SVG with D3.js utilities
- **Forms**: React Hook Form + Zod

## 🚢 Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

### Recommended Stack
- **Backend**: Railway.app (or GCP Cloud Run)
- **Frontend**: Vercel
- **Database**: Supabase
- **Cache**: Upstash Redis

### One-Command Deploy

```bash
# Backend to Railway
cd backend && railway up

# Frontend to Vercel
cd frontend && vercel --prod
```

## 📊 Database Schema

Tables:
- `profiles` - Birth profiles
- `charts` - Cached chart calculations
- `queries` - User questions
- `responses` - AI interpretations
- `feedback` - User ratings

See [database-schema.sql](docs/database-schema.sql) for complete schema.

## 🧪 Testing

### Automated Test Suite

JioAstro includes a comprehensive test suite covering all major features:

**Test Coverage:**
- **Dosha Detection Tests** (26 tests): Manglik, Kaal Sarpa, Pitra, Grahan doshas with intensity, cancellations, and remedies
- **Yoga Detection Tests** (60+ tests): All 40+ classical yogas including Pancha Mahapurusha, Kala Sarpa variations, Nabhasa yogas, and rare yogas
- **Divisional Charts Tests** (50+ tests): D2-D60 calculations, Vimshopaka Bala, planetary dignities, and performance

**Running Tests:**
```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test suite
pytest tests/test_dosha_detection.py
pytest tests/test_extended_yoga.py
pytest tests/test_divisional_charts.py

# Run tests by category
pytest -m dosha        # Dosha detection tests
pytest -m yoga         # Yoga detection tests
pytest -m divisional   # Divisional charts tests
pytest -m unit         # Unit tests only
pytest -m integration  # Integration tests only

# Run with coverage report
pytest --cov=app --cov-report=html
```

**Test Configuration:**
- Located in `backend/pytest.ini`
- Custom markers for categorization
- Performance tests ensure targets (<100ms for dosha detection, <500ms for all yogas)
- Fixtures provide sample charts for testing

### Manual Testing Checklist
- [ ] User registration/login
- [ ] Profile creation with valid birth data
- [ ] D1 chart generation
- [ ] D9 chart generation
- [ ] Query submission (career, relationship, health)
- [ ] Feedback submission
- [ ] Rate limiting (11th query should fail)
- [ ] Mobile responsiveness

## 📈 Roadmap

### Phase 1: MVP (Current) ✅
- Core features (auth, charts, AI)
- Deployment ready
- Mobile responsive

### Phase 2: Enhanced Features (Week 2-3)
- [ ] More divisional charts (D7, D10, D12)
- [ ] Transit predictions
- [ ] PDF report generation
- [ ] South Indian chart style
- [ ] Compatibility analysis (Ashtakoot)

### Phase 3: Learning System (Week 4-5)
- [ ] Automated feedback analysis
- [ ] Prompt optimization
- [ ] A/B testing framework
- [ ] User preference profiling

### Phase 4: Scale (Week 6+)
- [ ] Payment/subscription system
- [ ] Multi-language support
- [ ] Native mobile apps
- [ ] Professional astrologer marketplace

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- **VedAstro** (https://vedastro.org) - Comprehensive Vedic astrology calculations (MIT License)
- Swiss Ephemeris (astrology calculations)
- OpenAI (GPT-4 for interpretations)
- Supabase (database and auth)
- Vercel & Railway (deployment platforms)
- shadcn/ui (beautiful UI components)

### Third-Party Licenses

This project uses VedAstro Python library for advanced Vedic astrology calculations. See [LICENSE-VEDASTRO.txt](LICENSE-VEDASTRO.txt) for full attribution and license details.

---

**Built with 💜 using ancient Vedic wisdom and modern AI technology**
