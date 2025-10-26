# Deployment Guide - Vedic AI Astrology MVP

## Overview

This guide covers deploying the Vedic AI Astrology service to production. We recommend using Railway for the backend and Vercel for the frontend.

## Prerequisites

- [ ] Supabase account and project
- [ ] OpenAI API key
- [ ] Railway account (for backend) OR GCP/Azure account (for Docker)
- [ ] Vercel account (for frontend)
- [ ] Custom domain (optional but recommended)

## Option A: Railway + Vercel (Recommended for MVP)

### Step 1: Set Up Supabase

1. Create a new Supabase project at https://supabase.com
2. Go to Project Settings → Database
3. Copy the connection string
4. Go to SQL Editor and run `/docs/database-schema.sql`
5. Go to Authentication → Settings and enable Email auth
6. Copy your Supabase URL and anon key

### Step 2: Deploy Backend to Railway

1. **Create Railway Project**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login
   railway login

   # Link project
   cd backend
   railway init
   ```

2. **Set Environment Variables** in Railway dashboard:
   ```
   DATABASE_URL=<your-supabase-connection-string>
   SUPABASE_URL=<your-supabase-url>
   SUPABASE_KEY=<your-supabase-anon-key>
   SUPABASE_JWT_SECRET=<your-supabase-jwt-secret>
   OPENAI_API_KEY=<your-openai-api-key>
   REDIS_URL=<railway-redis-url-or-upstash>
   ENVIRONMENT=production
   RATE_LIMIT_QUERIES_PER_DAY=10
   ```

3. **Add Redis** (optional but recommended):
   - In Railway, click "New" → "Database" → "Add Redis"
   - Copy the Redis URL to `REDIS_URL` environment variable

4. **Deploy**:
   ```bash
   railway up
   ```

5. **Get your backend URL** from Railway dashboard (e.g., `https://your-app.railway.app`)

### Step 3: Deploy Frontend to Vercel

1. **Push code to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Import to Vercel**:
   - Go to https://vercel.com
   - Click "New Project"
   - Import your GitHub repository
   - Set root directory to `frontend`

3. **Configure Environment Variables** in Vercel:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
   NEXT_PUBLIC_SUPABASE_URL=<your-supabase-url>
   NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-supabase-anon-key>
   ```

4. **Deploy**:
   - Vercel will automatically deploy
   - Get your frontend URL (e.g., `https://your-app.vercel.app`)

### Step 4: Configure CORS

Update backend CORS settings in `backend/app/core/config.py`:

```python
ALLOWED_ORIGINS: List[str] = [
    "https://your-app.vercel.app",
    "https://your-custom-domain.com"
]
```

Redeploy backend:
```bash
railway up
```

## Option B: Docker on GCP Cloud Run

### Step 1: Build and Push Docker Image

```bash
cd backend

# Build image
docker build -t gcr.io/YOUR-PROJECT-ID/vedic-astrology-api .

# Push to GCP
gcloud auth configure-docker
docker push gcr.io/YOUR-PROJECT-ID/vedic-astrology-api
```

### Step 2: Deploy to Cloud Run

```bash
gcloud run deploy vedic-astrology-api \
  --image gcr.io/YOUR-PROJECT-ID/vedic-astrology-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=$DATABASE_URL,OPENAI_API_KEY=$OPENAI_API_KEY
```

### Step 3: Deploy Frontend

Same as Option A, Step 3.

## Option C: All-in-One Docker (Development/Testing)

### Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

Deploy:
```bash
docker-compose up -d
```

## Post-Deployment Checklist

- [ ] Backend health check passes (`/health` endpoint)
- [ ] Frontend loads without errors
- [ ] User can sign up and log in
- [ ] Profile creation works
- [ ] Chart generation works
- [ ] AI query submission works
- [ ] Feedback submission works
- [ ] Mobile responsive on real device
- [ ] API rate limiting works
- [ ] Error handling works properly

## Monitoring

### Railway
- Built-in metrics in Railway dashboard
- View logs: `railway logs`

### Vercel
- Analytics in Vercel dashboard
- View logs in deployment details

### Custom Monitoring (Optional)
- Sentry for error tracking
- Posthog for analytics
- Uptime monitoring (e.g., UptimeRobot)

## Scaling Considerations

### Immediate (MVP)
- Railway auto-scales within plan limits
- Vercel auto-scales globally
- Supabase handles up to 500 concurrent connections

### Future (Post-MVP)
- Add Redis caching for chart calculations
- Add CDN for static assets
- Consider separating AI service
- Add database read replicas
- Implement proper queue for AI requests

## Troubleshooting

### Common Issues

**Backend not connecting to database:**
- Check DATABASE_URL format: `postgresql+asyncpg://...`
- Verify Supabase allows connections from Railway IP

**CORS errors:**
- Add frontend URL to ALLOWED_ORIGINS
- Check protocol (http vs https)

**AI timeouts:**
- Increase timeout in deployment platform
- Check OpenAI API key and quota

**Rate limiting not working:**
- Verify Redis connection
- Check environment variable RATE_LIMIT_QUERIES_PER_DAY

## Cost Estimate (Free Tiers)

- **Supabase**: Free (up to 500MB database, 2GB bandwidth)
- **Railway**: $5-20/month (hobby plan)
- **Vercel**: Free (hobby plan)
- **OpenAI**: Pay-per-use (~$0.03-0.06 per query)

**Total estimated cost for MVP testing: $10-30/month**

## Security Checklist

- [ ] All API keys in environment variables (not hardcoded)
- [ ] HTTPS enabled on all domains
- [ ] Supabase RLS policies active
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (using ORMs)
- [ ] XSS protection in frontend

## Backup Strategy

1. **Database**: Supabase auto-backups daily (free tier: 7 days)
2. **Code**: GitHub repository
3. **Secrets**: Store separately (password manager)

## Domain Setup (Optional)

1. Purchase domain (e.g., Namecheap, Google Domains)
2. Point domain to Vercel (A/CNAME records)
3. Point api subdomain to Railway
4. Enable SSL (automatic with Vercel/Railway)

Example DNS:
```
@ A 76.76.21.21 (Vercel)
api CNAME your-app.railway.app
```

## Support

- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs
- Supabase docs: https://supabase.com/docs
