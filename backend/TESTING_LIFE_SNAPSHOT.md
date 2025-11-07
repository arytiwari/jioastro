# Testing Life Snapshot Feature (Magical 12 #1)

**Status:** Ready for Testing
**Date:** 2025-11-07

---

## ⚠️ Important: Environment Setup

Before testing, you need to handle environment variables correctly:

###  1. Clear Conflicting Variables

```bash
# Unset the instant_onboarding variable (temporarily disabled)
unset FEATURE_INSTANT_ONBOARDING

# Ensure Life Snapshot is enabled
export FEATURE_LIFE_SNAPSHOT=true
```

### 2. Verify Environment

```bash
# Should show "true"
echo $FEATURE_LIFE_SNAPSHOT

# Should be empty
echo $FEATURE_INSTANT_ONBOARDING
```

---

## 🗄️ Database Migration

Before testing, run the database migration:

### Option 1: Direct PostgreSQL

```bash
psql -d your_database_name -f docs/migrations/life_snapshot_tables.sql
```

### Option 2: Supabase SQL Editor

1. Open Supabase Dashboard → SQL Editor
2. Copy contents of `docs/migrations/life_snapshot_tables.sql`
3. Paste and click "Run"
4. Verify the `life_snapshot_data` table was created

---

## 🚀 Start the Server

```bash
# Make sure you're in the backend directory
cd /Users/arvind.tiwari/Desktop/jioastro/backend

# Activate virtual environment
source venv/bin/activate

# Start server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Expected Output:**
```
🚀 Starting JioAstro API...
✅ Database initialized via direct connection
📦 Registering Magical 12 features...
✅ Life Snapshot feature registered (Magical 12 #1)
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## ✅ Manual Testing Steps

### Test 1: Server Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "supabase_rest_api",
  "api": "operational"
}
```

---

### Test 2: Feature Info (No Auth Required)

```bash
curl http://localhost:8000/api/v2/life-snapshot/
```

**Expected Response:**
```json
{
  "feature": "life_snapshot",
  "version": "1.0.0",
  "description": "60-second personalized life insights powered by AI",
  "magical_twelve_number": 1,
  "read_time_seconds": 60,
  "cache_ttl_seconds": 3600
}
```

**If you get 403 Forbidden:**
- Feature flag is not enabled
- Run: `export FEATURE_LIFE_SNAPSHOT=true`
- Restart the server

---

### Test 3: Auth Protection (Should Fail Without Token)

```bash
curl -X POST http://localhost:8000/api/v2/life-snapshot/generate \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "12345678-1234-1234-1234-123456789012", "force_refresh": false}'
```

**Expected Response:**
```json
{
  "detail": "Not authenticated"
}
```

✅ This is correct! The endpoint is protected.

---

### Test 4: API Documentation

Open in your browser:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

**What to Look For:**
1. Find "Magical 12" tag
2. See "Life Snapshot" endpoints:
   - `GET /api/v2/life-snapshot/`
   - `POST /api/v2/life-snapshot/generate`
   - `GET /api/v2/life-snapshot/{snapshot_id}`
   - `GET /api/v2/life-snapshot/list`

---

## 🔐 Testing with Authentication

To test authenticated endpoints, you need a JWT token:

### Option 1: Get Token from Frontend

1. Login to the frontend application
2. Open DevTools → Application → Local Storage
3. Find the auth token
4. Copy the token value

### Option 2: Use Existing Test User

If you have test credentials:

```bash
# Login to get token (adjust endpoint as needed)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword"}'
```

### Test 5: Generate Snapshot (With Auth)

```bash
# Replace YOUR_JWT_TOKEN and YOUR_PROFILE_ID
export JWT_TOKEN="your-jwt-token-here"
export PROFILE_ID="your-profile-uuid-here"

curl -X POST http://localhost:8000/api/v2/life-snapshot/generate \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"profile_id\": \"$PROFILE_ID\", \"force_refresh\": false}"
```

**Expected Response:**
```json
{
  "snapshot_id": "uuid-here",
  "profile": {
    "id": "profile-uuid",
    "name": "Profile Name"
  },
  "generated_at": "2025-11-07T12:00:00Z",
  "expires_at": "2025-11-07T13:00:00Z",
  "insights": {
    "top_themes": [
      {
        "title": "Career Growth",
        "description": "Strong planetary support for professional advancement",
        "confidence": 0.85,
        "planetary_basis": ["Jupiter in 10th", "Venus MD"]
      }
      // ... 2 more themes
    ],
    "risks": [ /* 3 risks */ ],
    "opportunities": [ /* 3 opportunities */ ],
    "actions": [ /* 3 actions */ ],
    "life_phase": "Growth Period",
    "read_time_seconds": 60
  },
  "transits": {
    "jupiter": {"sign": "Taurus", "house_from_moon": 5},
    "saturn": {"sign": "Aquarius", "house_from_moon": 2}
  }
}
```

---

### Test 6: Get Snapshot by ID

```bash
# Use snapshot_id from previous response
export SNAPSHOT_ID="snapshot-uuid-here"

curl http://localhost:8000/api/v2/life-snapshot/$SNAPSHOT_ID \
  -H "Authorization: Bearer $JWT_TOKEN"
```

---

### Test 7: List Snapshots

```bash
curl "http://localhost:8000/api/v2/life-snapshot/list?limit=10&offset=0" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response:**
```json
{
  "snapshots": [
    {
      "id": "uuid",
      "profile_id": "uuid",
      "profile_name": "Name",
      "generated_at": "2025-11-07T12:00:00Z",
      "expires_at": "2025-11-07T13:00:00Z",
      "is_expired": false,
      "themes_count": 3
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

---

### Test 8: Cache Behavior

Test that caching works:

```bash
# Generate snapshot (first time)
curl -X POST http://localhost:8000/api/v2/life-snapshot/generate \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"profile_id\": \"$PROFILE_ID\", \"force_refresh\": false}"

# Note the snapshot_id

# Generate again (should return cached version with same snapshot_id)
curl -X POST http://localhost:8000/api/v2/life-snapshot/generate \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"profile_id\": \"$PROFILE_ID\", \"force_refresh\": false}"

# Force refresh (should generate new snapshot with different snapshot_id)
curl -X POST http://localhost:8000/api/v2/life-snapshot/generate \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"profile_id\": \"$PROFILE_ID\", \"force_refresh\": true}"
```

---

## 🐛 Troubleshooting

### Server Won't Start

**Error:** `Extra inputs are not permitted [FEATURE_INSTANT_ONBOARDING]`

**Solution:**
```bash
unset FEATURE_INSTANT_ONBOARDING
uvicorn main:app --reload
```

---

### Feature Returns 403 Forbidden

**Solution:**
```bash
# Enable the feature
export FEATURE_LIFE_SNAPSHOT=true

# Restart server
# Server must be restarted for env var to take effect
```

---

### Database Connection Failed

**Error:** `Database direct connection failed`

**Solution:**
This is normal! The app will automatically fall back to Supabase REST API. Check that:
- `SUPABASE_URL` is set in `.env`
- `SUPABASE_KEY` is set in `.env`
- `SUPABASE_JWT_SECRET` is set in `.env`

---

### Import Error on Startup

**Error:** `cannot import name 'AstrologyService'`

**Solution:**
The instant_onboarding feature has been temporarily disabled in `main.py` (lines 6, 34-40, 72 are commented out). This is expected for testing Life Snapshot.

---

## 📊 Automated Test Script

Run the automated test script:

```bash
cd /Users/arvind.tiwari/Desktop/jioastro/backend

# Make sure server is running first!
python test_life_snapshot.py
```

This script tests:
- ✅ Server health
- ✅ Feature info endpoint
- ✅ Auth protection
- ✅ API documentation
- ⚠️  Authenticated endpoints (requires manual JWT)

---

## 📝 Test Checklist

- [ ] Environment variables set correctly
- [ ] Database migration applied
- [ ] Server starts without errors
- [ ] Feature shows as registered in logs
- [ ] `/health` endpoint returns 200
- [ ] `/api/v2/life-snapshot/` returns feature info
- [ ] Generate endpoint requires authentication
- [ ] API documentation shows all endpoints
- [ ] Generate snapshot returns valid data (with JWT)
- [ ] Get snapshot by ID works
- [ ] List snapshots works
- [ ] Caching returns same snapshot_id
- [ ] Force refresh generates new snapshot

---

## ✨ Success Criteria

**Feature #1 is working correctly if:**

1. ✅ Server starts with "Life Snapshot feature registered" message
2. ✅ Feature info endpoint returns without auth
3. ✅ Protected endpoints require JWT token
4. ✅ Snapshot generation returns proper JSON structure
5. ✅ Caching works (same snapshot_id without force_refresh)
6. ✅ All 4 endpoints are functional
7. ✅ API documentation is complete

---

## 📧 Next Steps After Testing

Once testing is complete:

1. **Report Issues:** Document any bugs or unexpected behavior
2. **Performance:** Note response times for snapshot generation
3. **Data Quality:** Verify that themes, risks, opportunities make sense
4. **Frontend Integration:** Begin connecting to these endpoints from the frontend
5. **AI Enhancement:** Plan integration with real astrology calculations and AI insights

---

**Testing Guide Created:** 2025-11-07
**Feature:** Life Snapshot (Magical 12 #1)
**Status:** Ready for Manual Testing
