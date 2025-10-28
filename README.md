# Vedic AI Astrology - MVP

AI-powered Vedic astrology service with accurate birth chart generation and personalized interpretations using GPT-4.

## 🌟 Features

### Core Functionality (MVP)
- ✅ User registration and authentication (Supabase Auth)
- ✅ Birth chart generation (Rashi D-1 and Navamsa D-9)
- ✅ AI-powered personalized interpretations (OpenAI GPT-4)
- ✅ Natural language query interface
- ✅ Mobile-responsive, clean UI
- ✅ Feedback system for continuous improvement
- ✅ Vimshottari Dasha calculation
- ✅ Yoga (planetary combination) detection

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
│   │       ├── astrology.py   # Chart calculations
│   │       └── ai_service.py  # AI interpretations
│   ├── main.py             # App entry point
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Docker config
│
├── frontend/               # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   │   ├── ui/           # shadcn/ui components
│   │   └── chart/        # Chart visualizations
│   ├── lib/              # Utilities
│   │   ├── api.ts       # API client
│   │   └── supabase.ts  # Auth client
│   ├── package.json
│   └── tailwind.config.ts
│
└── docs/                  # Documentation
    ├── database-schema.sql
    └── DEPLOYMENT.md
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
- `POST /api/v1/charts/calculate` - Calculate chart
- `GET /api/v1/charts/{profile_id}/{chart_type}` - Get chart

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
- **Chart Types**: D1 (Rashi/Birth chart), D9 (Navamsa)
- **Dasha System**: Vimshottari (120-year cycle)
- **Yogas**: Raj Yoga, Dhana Yoga, Gaja Kesari, Budhaditya, and more

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
