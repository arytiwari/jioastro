# Quick Start Guide - Vedic AI Astrology MVP

This guide will help you get the Vedic AI Astrology MVP up and running in under 15 minutes.

## Prerequisites Checklist

Before you begin, make sure you have:

- [ ] **Python 3.11+** installed (`python --version`)
- [ ] **Node.js 18+** installed (`node --version`)
- [ ] **Supabase account** created at https://supabase.com
- [ ] **OpenAI API key** from https://platform.openai.com

## Step-by-Step Setup

### 1. Set Up Supabase (5 minutes)

1. **Create Project**
   - Go to https://supabase.com
   - Click "New Project"
   - Choose a name, password, and region
   - Wait for project creation (~2 minutes)

2. **Set Up Database**
   - Go to SQL Editor in Supabase
   - Copy contents of `docs/database-schema.sql`
   - Paste and run the SQL

3. **Enable Authentication**
   - Go to Authentication → Providers
   - Enable "Email" provider
   - Keep defaults

4. **Get Credentials**
   - Go to Settings → API
   - Copy these values:
     - Project URL
     - anon public key
     - JWT Secret
   - Go to Settings → Database
   - Copy connection string (change mode to "Session")

### 2. Set Up Backend (3 minutes)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Edit `backend/.env`** with your credentials:
```bash
DATABASE_URL=postgresql+asyncpg://[YOUR_SUPABASE_CONNECTION_STRING]
SUPABASE_URL=https://[YOUR_PROJECT].supabase.co
SUPABASE_KEY=[YOUR_ANON_KEY]
SUPABASE_JWT_SECRET=[YOUR_JWT_SECRET]
OPENAI_API_KEY=sk-[YOUR_OPENAI_KEY]
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
```

```bash
# Start backend server
uvicorn main:app --reload
```

✅ Backend should be running at `http://localhost:8000`
✅ API docs at `http://localhost:8000/docs`

### 3. Set Up Frontend (2 minutes)

Open a **new terminal window**:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
```

**Edit `frontend/.env.local`**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://[YOUR_PROJECT].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[YOUR_ANON_KEY]
```

```bash
# Start frontend
npm run dev
```

✅ Frontend should be running at `http://localhost:3000`

### 4. Test the Application (5 minutes)

1. **Visit Homepage**
   - Open http://localhost:3000
   - You should see the landing page

2. **Test API Health**
   - Open http://localhost:8000/health
   - Should return `{"status": "healthy", ...}`

3. **Test API Docs**
   - Open http://localhost:8000/docs
   - Interactive Swagger UI should load

## Current Status - What's Built

### ✅ Completed (Backend)
- Complete FastAPI backend with async database
- All database models (profiles, charts, queries, responses, feedback)
- Vedic astrology calculation engine
  - D1 (Rashi) chart generation
  - D9 (Navamsa) chart calculation
  - Vimshottari Dasha calculation
  - Yoga detection (Raj, Dhana, Gaja Kesari, etc.)
- AI interpretation service with OpenAI GPT-4
- RESTful API endpoints for all resources
- Rate limiting (10 queries per day)
- JWT authentication integration
- Docker configuration

### ✅ Completed (Frontend)
- Next.js 14 with TypeScript
- Tailwind CSS + shadcn/ui setup
- React Query for state management
- Landing page with features
- API client with JWT handling
- Supabase auth client
- Chart visualization components:
  - Birth chart (North Indian style SVG)
  - Planetary positions table
  - Yoga list display
  - Dasha information card

### ✅ Completed (DevOps)
- Complete database schema with RLS policies
- Comprehensive documentation (README, DEPLOYMENT)
- Environment variable templates
- .gitignore for both stacks
- Dockerfile for backend

## What's Next - Remaining Tasks

### 🔨 To Build (Authentication Pages)
```
frontend/app/auth/login/page.tsx
frontend/app/auth/signup/page.tsx
```

### 🔨 To Build (Dashboard & Profile Management)
```
frontend/app/(dashboard)/layout.tsx        # Protected layout
frontend/app/(dashboard)/dashboard/page.tsx # Main dashboard
frontend/app/(dashboard)/profiles/new/page.tsx  # Create profile
frontend/app/(dashboard)/profiles/[id]/page.tsx # View chart
```

### 🔨 To Build (Query Interface)
```
frontend/app/(dashboard)/ask/page.tsx      # Ask questions
frontend/app/(dashboard)/history/page.tsx  # Query history
frontend/components/query/QueryForm.tsx
frontend/components/query/InterpretationCard.tsx
frontend/components/query/FeedbackButton.tsx
```

### 🔨 To Build (Additional Components)
```
frontend/components/ui/textarea.tsx
frontend/components/ui/select.tsx
frontend/components/ui/dialog.tsx
frontend/components/profile/ProfileForm.tsx
frontend/components/dashboard/StatsCard.tsx
```

## Quick Test Commands

### Test Backend Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Test profiles (needs auth token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/profiles
```

### Check Logs

**Backend:**
- Logs appear in terminal where you ran `uvicorn`

**Frontend:**
- Logs appear in terminal where you ran `npm run dev`
- Also check browser console (F12)

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'kerykeion'"
**Solution:**
```bash
cd backend
source venv/bin/activate  # Make sure venv is activated
pip install -r requirements.txt
```

### Issue: "Database connection failed"
**Solution:**
- Check DATABASE_URL in `.env`
- Make sure it starts with `postgresql+asyncpg://`
- Verify Supabase project is running

### Issue: "CORS error in frontend"
**Solution:**
- Check ALLOWED_ORIGINS in `backend/app/core/config.py`
- Should include `http://localhost:3000`

### Issue: "OpenAI API error"
**Solution:**
- Verify OPENAI_API_KEY in `.env`
- Check you have credits in OpenAI account
- Test key at https://platform.openai.com/api-keys

## Development Workflow

1. **Start Backend** (Terminal 1)
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload
   ```

2. **Start Frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Make Changes**
   - Backend changes auto-reload (with `--reload`)
   - Frontend changes auto-refresh

4. **Test Changes**
   - Backend: http://localhost:8000/docs
   - Frontend: http://localhost:3000

## Next Steps

After setup is complete:

1. ✅ **Verify** all services are running
2. 📝 **Review** the API documentation
3. 🔨 **Build** authentication pages (see TODO list)
4. 🎨 **Create** dashboard and profile forms
5. 💬 **Implement** query interface
6. 🚀 **Deploy** to Railway + Vercel

## Estimated Timeline

- **Authentication Pages**: 2-3 hours
- **Dashboard & Profiles**: 3-4 hours
- **Query Interface**: 2-3 hours
- **Feedback UI**: 1-2 hours
- **Mobile Polish**: 2-3 hours
- **Testing & Fixes**: 2-3 hours
- **Deployment**: 1-2 hours

**Total: 13-20 hours to complete MVP**

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Review [DEPLOYMENT.md](docs/DEPLOYMENT.md) for deployment guide
- Check API docs at http://localhost:8000/docs
- Review database schema in `docs/database-schema.sql`

---

**Ready to build! 🚀**
