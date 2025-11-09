# Magical 12 Phase 1 - Supabase Deployment Guide

## Overview
This guide helps you deploy the **Magical 12 Phase 1** features to Supabase. All backend services use **Supabase REST API** (HTTP/HTTPS connections), not direct PostgreSQL connections.

---

## ✅ Architecture Confirmation

### Backend Connection Pattern
All three new features follow the **Supabase REST API** pattern:

```python
# ✅ CORRECT PATTERN (All services use this)
from app.core.supabase_client import SupabaseClient

class LifeThreadsService:
    def __init__(self):
        self.supabase = SupabaseClient()

    async def get_events(self, user_id):
        # Uses Supabase REST API via HTTP
        result = self.supabase.client.table('life_events') \
            .select('*') \
            .eq('user_id', user_id) \
            .execute()
        return result.data
```

### Services Using Supabase REST API
- ✅ `life_threads_service.py` - Supabase REST API
- ✅ `remedy_planner_service.py` - Supabase REST API
- ✅ `hyperlocal_panchang_service.py` - Supabase REST API
- ✅ `feng_shui_service.py` - Supabase REST API
- ✅ `tarot_service.py` - Supabase REST API
- ✅ All other services - Supabase REST API

**No direct PostgreSQL connections** - Everything goes through Supabase's REST API endpoints over HTTPS.

---

## 🚀 Step-by-Step Deployment

### 1. Prerequisites
- Supabase account ([signup here](https://supabase.com))
- Your Supabase project credentials:
  - Project URL: `https://[project-id].supabase.co`
  - Anon Key: Public API key
  - JWT Secret: For token validation

### 2. Run Database Migrations

#### Option A: Via Supabase Dashboard (Recommended)

1. **Open Supabase SQL Editor**
   ```
   https://app.supabase.com/project/[YOUR_PROJECT_ID]/sql
   ```

2. **Run Main Migration**
   - Click "New Query"
   - Copy entire contents of `MAGICAL_12_PHASE_1_SUPABASE_MIGRATION.sql`
   - Paste into SQL Editor
   - Click "Run" (or press Ctrl/Cmd + Enter)
   - Wait for completion (should take ~5 seconds)

3. **Run Remedies Catalog Population**
   - Click "New Query" again
   - Copy entire contents of `POPULATE_REMEDIES_CATALOG_SUPABASE.sql`
   - Paste into SQL Editor
   - Click "Run"
   - Wait for completion (should take ~2 seconds)

4. **Verify Tables Created**
   - Go to "Table Editor" in Supabase Dashboard
   - You should see 10 new tables:
     ```
     ✓ life_events
     ✓ dasha_timeline_cache
     ✓ remedies_catalog
     ✓ remedy_assignments
     ✓ remedy_tracking
     ✓ remedy_achievements
     ✓ panchang_cache
     ✓ panchang_subscriptions
     ✓ panchang_preferences
     ✓ daily_guidance_log
     ```

#### Option B: Via Supabase CLI

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link your project
supabase link --project-ref YOUR_PROJECT_ID

# Run migrations
supabase db push

# Or run specific migration
psql -h db.YOUR_PROJECT_ID.supabase.co \
     -U postgres \
     -d postgres \
     -f migrations/MAGICAL_12_PHASE_1_SUPABASE_MIGRATION.sql
```

### 3. Configure Backend Environment

Update your `.env` file with Supabase credentials:

```bash
# Supabase Configuration
SUPABASE_URL=https://[your-project-id].supabase.co
SUPABASE_KEY=[your-anon-key]
SUPABASE_JWT_SECRET=[your-jwt-secret]

# Database (not used - all via REST API, but keep for compatibility)
DATABASE_URL=postgresql+asyncpg://postgres:[password]@db.[project-id].supabase.co:5432/postgres

# OpenAI (for AI features)
OPENAI_API_KEY=sk-[your-key]

# Environment
ENVIRONMENT=production
```

**How to find these values:**
- Go to Supabase Dashboard → Settings → API
- Copy "URL" for `SUPABASE_URL`
- Copy "anon public" key for `SUPABASE_KEY`
- Copy "JWT Secret" for `SUPABASE_JWT_SECRET`

### 4. Deploy Backend

#### Railway.app (Recommended)

1. **Connect Repository**
   ```bash
   # From backend directory
   railway login
   railway init
   railway link
   ```

2. **Set Environment Variables**
   - Go to Railway dashboard
   - Add all variables from `.env`
   - Variables → New Variable → Add each one

3. **Deploy**
   ```bash
   railway up
   ```

#### Alternative: GCP Cloud Run, Heroku, or Vercel

All platforms support FastAPI. Follow their respective deployment guides and ensure environment variables are set.

### 5. Deploy Frontend

#### Vercel (Recommended)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy from frontend directory**
   ```bash
   cd frontend
   vercel
   ```

3. **Set Environment Variables**
   - Go to Vercel dashboard → Settings → Environment Variables
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app/api/v1
     NEXT_PUBLIC_SUPABASE_URL=https://[project-id].supabase.co
     NEXT_PUBLIC_SUPABASE_ANON_KEY=[your-anon-key]
     ```

---

## 🔍 Verification Steps

### 1. Verify Database Tables

Run this query in Supabase SQL Editor:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'life_events', 'dasha_timeline_cache',
    'remedies_catalog', 'remedy_assignments', 'remedy_tracking', 'remedy_achievements',
    'panchang_cache', 'panchang_subscriptions', 'panchang_preferences', 'daily_guidance_log'
);
```

Should return 10 rows.

### 2. Verify Row-Level Security

Run this query:

```sql
SELECT tablename, policyname, permissive, roles, cmd
FROM pg_policies
WHERE schemaname = 'public'
AND tablename IN ('life_events', 'remedy_assignments', 'remedy_tracking')
ORDER BY tablename, policyname;
```

Should return multiple RLS policies.

### 3. Verify Remedies Catalog

```sql
SELECT COUNT(*) as total_remedies,
       COUNT(DISTINCT planet) as planets_covered,
       COUNT(DISTINCT remedy_type) as remedy_types
FROM remedies_catalog;
```

Expected output:
```
total_remedies: 30+
planets_covered: 9 (Sun through Ketu)
remedy_types: 8+ (mantra, charity, fasting, etc.)
```

### 4. Test Backend API

Once backend is deployed, test the endpoints:

```bash
# Health check
curl https://your-backend-url.railway.app/health

# Get remedies catalog (no auth required)
curl https://your-backend-url.railway.app/api/v1/remedy-planner/catalog

# Test with authentication (replace with valid JWT)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://your-backend-url.railway.app/api/v1/life-threads/events
```

### 5. Test Frontend

1. Visit your deployed frontend URL
2. Login/Signup
3. Navigate to new features:
   - `/dashboard/life-threads` - Should load timeline
   - `/dashboard/remedy-planner` - Should show remedy catalog
   - `/dashboard/panchang` - Should display Panchang form

---

## 🛡️ Security Features

All migrations include proper security:

1. **Row-Level Security (RLS)** - Enabled on all tables
   - Users can only access their own data
   - Public data (remedies catalog, panchang cache) accessible to all

2. **Authentication** - Via Supabase Auth
   - JWT validation on all protected endpoints
   - User ID from JWT used for RLS policies

3. **HTTPS Only** - All Supabase connections use HTTPS
   - No direct database connections
   - All traffic encrypted

---

## 📊 Database Schema Summary

### Life Threads (2 tables)
- `life_events` - User life events with Dasha mapping
- `dasha_timeline_cache` - Cached Vimshottari Dasha calculations

### Remedy Planner (4 tables)
- `remedies_catalog` - 30+ Vedic remedies (public read)
- `remedy_assignments` - User remedy assignments
- `remedy_tracking` - Daily completion tracking
- `remedy_achievements` - Gamification badges

### Hyperlocal Panchang (4 tables)
- `panchang_cache` - Location-based Panchang data (public read)
- `panchang_subscriptions` - User location preferences
- `panchang_preferences` - Display preferences
- `daily_guidance_log` - Personalized daily guidance

**Total: 10 tables with full RLS policies**

---

## 🔧 Troubleshooting

### Issue: Migration fails with "relation already exists"
**Solution:** The migration is idempotent. Tables/policies use `IF NOT EXISTS` and `DROP POLICY IF EXISTS`. Safe to re-run.

### Issue: Backend can't connect to Supabase
**Solution:** Verify environment variables:
```bash
echo $SUPABASE_URL
echo $SUPABASE_KEY
# Should print your values, not blank
```

### Issue: RLS blocking requests
**Solution:** Check JWT token is valid:
```python
# In your code
from app.core.security import verify_token
decoded = verify_token(token)
print(decoded)  # Should contain user_id
```

### Issue: Remedies catalog is empty
**Solution:** Run the population script:
```sql
-- In Supabase SQL Editor
\i POPULATE_REMEDIES_CATALOG_SUPABASE.sql
```

---

## 📚 API Documentation

Once backend is deployed, visit:
```
https://your-backend-url.railway.app/docs
```

This opens the **interactive Swagger UI** with all endpoints documented.

### New Endpoints

**Life Threads:**
- `GET /api/v1/life-threads/events` - List user events
- `POST /api/v1/life-threads/events` - Create event
- `GET /api/v1/life-threads/timeline/{profile_id}` - Get Dasha timeline with events

**Remedy Planner:**
- `GET /api/v1/remedy-planner/catalog` - Browse remedies (public)
- `POST /api/v1/remedy-planner/assignments` - Assign remedy
- `POST /api/v1/remedy-planner/tracking` - Track completion
- `GET /api/v1/remedy-planner/dashboard` - Get user dashboard stats

**Panchang:**
- `POST /api/v1/panchang/calculate` - Calculate daily Panchang
- `GET /api/v1/panchang/today` - Get today's Panchang
- `GET /api/v1/panchang/hora` - Get Hora sequence

---

## 🎯 Next Steps

1. **Run Migrations** - Execute both SQL files in Supabase
2. **Deploy Backend** - Push to Railway/GCP/Heroku
3. **Deploy Frontend** - Push to Vercel
4. **Test Features** - Create test account and verify functionality
5. **Monitor** - Check Supabase Dashboard → Logs for errors

---

## 📞 Support

- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs

---

**Deployment Checklist:**

- [ ] Supabase project created
- [ ] Main migration SQL executed
- [ ] Remedies catalog populated
- [ ] 10 tables visible in Supabase dashboard
- [ ] Backend `.env` configured
- [ ] Backend deployed to Railway/GCP
- [ ] Backend health endpoint responding
- [ ] Frontend `.env.local` configured
- [ ] Frontend deployed to Vercel
- [ ] Can login and access new features
- [ ] API calls working (check Network tab)

**You're ready to go! 🚀**
