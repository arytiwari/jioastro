# Production Deployment Guide - JioAstro

## Overview

This guide covers deploying the complete JioAstro application to production, including all recent features:
- ✅ Indian Cities Database (700+ cities)
- ✅ Session Management with Auto-Refresh
- ✅ Profile Deletion Functionality
- ✅ Admin Portal & Knowledge Management
- ✅ Voice Conversation (OpenAI Integration)

## Recommended Stack

- **Backend:** Railway.app or Google Cloud Run
- **Frontend:** Vercel
- **Database:** Supabase (PostgreSQL)
- **Cache:** Upstash Redis (optional, for rate limiting)
- **CDN:** Vercel Edge Network (automatic)

---

## Pre-Deployment Checklist

### Required Services:
- [ ] Supabase account and project
- [ ] OpenAI API key (for AI and voice features)
- [ ] Railway account OR Google Cloud account
- [ ] Vercel account
- [ ] GitHub repository (already done ✅)

### Required Environment Variables:

**Backend (.env):**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://[user]:[pass]@[host]:5432/[db]
SUPABASE_URL=https://[project].supabase.co
SUPABASE_KEY=[anon-key]
SUPABASE_JWT_SECRET=[jwt-secret]

# OpenAI
OPENAI_API_KEY=sk-[your-key]

# Admin (create secure passwords)
ADMIN_JWT_SECRET=[generate-secure-secret]

# Optional
REDIS_URL=redis://[host]:6379
RATE_LIMIT_QUERIES_PER_DAY=10
ENVIRONMENT=production
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://[project].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[anon-key]
```

---

## Option A: Railway + Vercel (Recommended)

### Step 1: Prepare Supabase Database

#### 1.1 Run Database Migrations

Execute the following migrations in order:

```sql
-- 1. Cities table (700+ Indian cities)
-- Run: backend/migrations/add_indian_cities.sql
-- This creates cities table and populates it with data

-- 2. Admin tables
-- Run: backend/scripts/init_admin_tables.sql
-- This creates admin_users and knowledge_documents tables

-- 3. Phase 3 enhancements (if not already run)
-- Run: backend/docs/add-phase3-columns.sql
-- This adds conversation context and voice features
```

**How to run:**
1. Go to Supabase Dashboard → SQL Editor
2. Copy content from each file
3. Execute in order
4. Verify tables exist:
   - `cities` (should have 700+ rows)
   - `admin_users`
   - `knowledge_documents`

#### 1.2 Create Admin User

Run this script to create your first admin:

```bash
cd backend
python scripts/create_admin_user.py
```

Enter your admin credentials when prompted.

#### 1.3 Configure Supabase Auth

1. Go to Authentication → Settings
2. JWT Settings:
   - JWT Expiry: 28800 (8 hours)
   - Refresh Token Lifetime: 2592000 (30 days)
3. Email Settings:
   - Enable Email auth
   - Configure email templates (optional)

---

### Step 2: Deploy Backend to Railway

#### 2.1 Install Railway CLI

```bash
npm install -g @railway/cli
railway login
```

#### 2.2 Initialize Project

```bash
cd backend
railway init
```

Select "Create new project" and name it (e.g., "jioastro-backend").

#### 2.3 Set Environment Variables

In Railway Dashboard, go to Variables and add:

```bash
# Required
DATABASE_URL=your_supabase_connection_string
SUPABASE_URL=https://[project].supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret
OPENAI_API_KEY=sk-your_openai_key
ADMIN_JWT_SECRET=generate_secure_secret_here

# Optional but recommended
REDIS_URL=redis://default:[password]@[host]:6379
RATE_LIMIT_QUERIES_PER_DAY=10
ENVIRONMENT=production
```

**Generate secrets:**
```bash
# For ADMIN_JWT_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 2.4 Add Redis (Optional)

1. In Railway, click "New" → "Database" → "Add Redis"
2. Copy the Redis URL
3. Add to REDIS_URL environment variable

#### 2.5 Deploy

```bash
railway up
```

Wait for deployment to complete. Get your backend URL from Railway dashboard (e.g., `https://your-app.railway.app`).

#### 2.6 Verify Backend

```bash
curl https://your-backend.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "supabase_rest_api",
  "api": "operational"
}
```

---

### Step 3: Deploy Frontend to Vercel

#### 3.1 Connect GitHub

1. Go to https://vercel.com
2. Click "New Project"
3. Import your GitHub repository (`arytiwari/jioastro`)
4. Set **Root Directory** to `frontend`
5. Framework Preset: Next.js (auto-detected)

#### 3.2 Configure Environment Variables

In Vercel project settings, add:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://[project].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

#### 3.3 Deploy

Click "Deploy". Vercel will automatically:
- Install dependencies
- Build Next.js app
- Deploy to global CDN

Get your frontend URL (e.g., `https://your-app.vercel.app`)

---

### Step 4: Configure CORS

Update backend CORS settings to allow your frontend domain.

**Method 1: Update in Railway Dashboard**

Add environment variable:
```bash
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
```

**Method 2: Update code and redeploy**

Edit `backend/app/core/config.py`:
```python
ALLOWED_ORIGINS: List[str] = [
    "https://your-app.vercel.app",
    "https://your-custom-domain.com"
]
```

Then redeploy:
```bash
git add .
git commit -m "Update CORS for production"
git push origin main
railway up
```

---

### Step 5: Post-Deployment Testing

#### 5.1 Test User Flow

1. **Visit Frontend:** https://your-app.vercel.app
2. **Sign Up:** Create a new user account
3. **Create Profile:** Add birth details with city search
4. **Generate Chart:** View birth chart calculation
5. **Delete Profile:** Test delete button works
6. **Logout/Login:** Test session management

#### 5.2 Test Admin Flow

1. **Admin Login:** https://your-app.vercel.app/admin/login
2. **Use credentials** from Step 1.2
3. **Upload Document:** Test knowledge document upload
4. **View Users:** Check user management interface
5. **Delete Profile:** Test admin delete functionality

#### 5.3 Test Cities Search

1. Go to "New Profile" page
2. Type "Mumbai" in city search
3. Verify cities dropdown appears
4. Select a city
5. Verify lat/long auto-fills

#### 5.4 Test Session Management

1. Login to app
2. Stay active (click around)
3. Verify you don't get logged out
4. Leave idle for 31 minutes
5. Verify automatic logout occurs

#### 5.5 Check API Endpoints

```bash
# Health check
curl https://your-backend.railway.app/health

# Cities API
curl https://your-backend.railway.app/api/v1/cities?search=Delhi&limit=3

# Documentation
open https://your-backend.railway.app/docs
```

---

## Option B: Docker Deployment (Alternative)

If you prefer Docker deployment on GCP, AWS, or Azure:

### Step 1: Build Images

```bash
# Backend
cd backend
docker build -t jioastro-backend .

# Frontend
cd ../frontend
docker build -t jioastro-frontend .
```

### Step 2: Deploy to Cloud Provider

**Google Cloud Run:**
```bash
# Tag and push
docker tag jioastro-backend gcr.io/YOUR-PROJECT/jioastro-backend
docker push gcr.io/YOUR-PROJECT/jioastro-backend

# Deploy
gcloud run deploy jioastro-backend \
  --image gcr.io/YOUR-PROJECT/jioastro-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=$DATABASE_URL,OPENAI_API_KEY=$OPENAI_API_KEY
```

**AWS ECS, Azure Container Apps:** Similar process with respective CLIs.

---

## Production Checklist

### Security ✅

- [ ] All API keys in environment variables (not in code)
- [ ] HTTPS enabled (automatic with Vercel/Railway)
- [ ] CORS properly configured
- [ ] Supabase RLS policies active
- [ ] Admin JWT secret generated securely
- [ ] Rate limiting enabled (if Redis configured)
- [ ] SQL injection protection (using ORMs/Supabase)
- [ ] XSS protection (React auto-escapes)

### Database ✅

- [ ] Cities table populated (700+ cities)
- [ ] Admin tables created
- [ ] Phase 3 columns added
- [ ] Admin user created
- [ ] Supabase backups enabled (auto on free tier)

### Features ✅

- [ ] User authentication works
- [ ] Profile creation with city search
- [ ] Chart generation works
- [ ] Profile deletion works (user & admin)
- [ ] Session management active
- [ ] Admin portal accessible
- [ ] Knowledge document upload works
- [ ] Voice conversation (if using OpenAI voice)

### Performance ✅

- [ ] Backend responds < 2s
- [ ] Frontend loads < 3s
- [ ] Images optimized
- [ ] Caching headers set
- [ ] CDN enabled (automatic with Vercel)

### Monitoring ✅

- [ ] Railway logs accessible
- [ ] Vercel analytics enabled
- [ ] Error tracking (optional: Sentry)
- [ ] Uptime monitoring (optional: UptimeRobot)

---

## Cost Estimate

**Free Tier (for testing):**
- Supabase: Free (up to 500MB, 2GB bandwidth)
- Vercel: Free (hobby plan, unlimited bandwidth)
- Railway: $5/month (hobby plan with $5 free credit)
- OpenAI: Pay-per-use (~$0.03-0.10 per query)

**Total: ~$5-10/month for MVP testing**

**Paid Tier (for production):**
- Supabase Pro: $25/month
- Vercel Pro: $20/month
- Railway Pro: $20-50/month
- OpenAI: $10-100/month (depending on usage)
- Redis (Upstash): $10/month

**Total: ~$85-205/month for production**

---

## Scaling Strategy

### Phase 1 (MVP - Current):
- Single Railway instance
- Vercel edge network
- Supabase pooler
- No Redis (rate limiting in-memory)

### Phase 2 (Growth - 1K+ users):
- Add Redis for rate limiting
- Add Supabase read replicas
- Enable Vercel ISR for charts
- Add CDN for assets

### Phase 3 (Scale - 10K+ users):
- Horizontal scaling on Railway
- Separate AI service
- Queue system for heavy tasks
- Database sharding by user

---

## Troubleshooting

### Backend Issues

**500 errors on startup:**
- Check Railway logs: `railway logs`
- Verify all environment variables set
- Check DATABASE_URL format: `postgresql+asyncpg://...`

**Database connection timeout:**
- Normal! App uses Supabase REST API as fallback
- Check log for: "Using Supabase REST API instead"

**Cities API returns empty:**
- Verify migration was run
- Check: `SELECT COUNT(*) FROM cities;` in Supabase
- Should return 700+

### Frontend Issues

**API calls failing (CORS):**
- Add frontend URL to backend ALLOWED_ORIGINS
- Verify NEXT_PUBLIC_API_URL is correct
- Check protocol (must be https in production)

**Cities dropdown not appearing:**
- Check browser console for errors
- Verify backend cities API responds
- Check network tab for API calls

**Session expires too quickly:**
- Check Supabase JWT settings (should be 8 hours)
- Verify SessionManager is initialized
- Check browser console for session logs

### Admin Issues

**Cannot login to admin:**
- Verify admin user created (Step 1.2)
- Check ADMIN_JWT_SECRET is set in backend
- Verify correct username/password

**Document upload fails:**
- Check file size (< 50MB)
- Verify backend has write permissions
- Check Railway logs for errors

---

## Domain Setup (Optional)

### Custom Domain

1. **Purchase domain** (Namecheap, Google Domains, etc.)

2. **Configure DNS:**
   ```
   Type    Name    Value
   A       @       76.76.21.21 (Vercel IP)
   CNAME   api     your-app.railway.app
   CNAME   www     cname.vercel-dns.com
   ```

3. **Add to Vercel:**
   - Project Settings → Domains
   - Add your domain
   - Follow verification steps

4. **Add to Railway:**
   - Settings → Domains
   - Add api.yourdomain.com
   - Update ALLOWED_ORIGINS

5. **Update Environment Variables:**
   ```bash
   # Vercel
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1

   # Railway
   ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

---

## Monitoring & Maintenance

### Daily
- Check Railway logs for errors
- Monitor OpenAI usage/costs
- Check Supabase database size

### Weekly
- Review Vercel analytics
- Check API response times
- Review user feedback

### Monthly
- Database backup verification
- Security updates
- Dependency updates
- Cost review

---

## Rollback Strategy

If deployment fails:

```bash
# Railway
railway rollback

# Vercel
# Go to Deployments → Click previous deployment → "Promote to Production"

# Database
# Restore from Supabase backup (Settings → Backups)
```

---

## Support Resources

- **Railway:** https://docs.railway.app
- **Vercel:** https://vercel.com/docs
- **Supabase:** https://supabase.com/docs
- **Next.js:** https://nextjs.org/docs
- **FastAPI:** https://fastapi.tiangolo.com

---

## Next Steps After Deployment

1. **Enable Monitoring:**
   - Set up Sentry for error tracking
   - Configure Posthog for analytics
   - Add UptimeRobot for uptime monitoring

2. **Performance Optimization:**
   - Enable Redis caching
   - Add CDN for static assets
   - Optimize database queries

3. **Security Hardening:**
   - Add rate limiting per IP
   - Enable 2FA for admin
   - Set up backup automation
   - Add DDoS protection

4. **User Features:**
   - Email notifications
   - Payment integration
   - Social login
   - Mobile app

---

**Status:** Ready for Production Deployment ✅

**Last Updated:** 2025-11-05

**Version:** 1.0.0
