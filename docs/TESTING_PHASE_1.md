# Testing Phase 1: MVP Bridge Layer

## Quick Start

### 1. Restart Backend Server

```bash
cd /Users/arvind.tiwari/Desktop/jioastro/backend
uvicorn main:app --reload
```

Wait for:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Test Public Health Endpoints

These should work WITHOUT authentication:

```bash
# Root health check
curl http://localhost:8000/health

# Should return:
# {
#   "status": "healthy",
#   "database": "supabase_rest_api",
#   "api": "operational",
#   "note": "Using Supabase REST API for database operations"
# }

# Readings health check
curl http://localhost:8000/api/v1/readings/health

# Should return:
# {
#   "status": "healthy",
#   "service": "readings",
#   "mvp_bridge": "active",
#   "ai_engine": "pending_phase_3",
#   "endpoints": {...}
# }
```

✅ **Both should return HTTP 200** *(Fixed: Route ordering issue resolved on 2025-11-03)*

### 3. Test API Documentation

Open in browser:
```
http://localhost:8000/docs
```

You should see:
- All existing endpoints (profiles, charts, queries, feedback)
- **NEW**: "readings" section with:
  - POST /api/v1/readings/calculate
  - GET /api/v1/readings/{session_id}
  - GET /api/v1/readings/
  - GET /api/v1/readings/health

### 4. Run Automated Tests

```bash
cd backend
python test_readings_api.py
```

This will test:
1. ✅ Root health check (public)
2. ✅ Readings health check (public)
3. ✅ Calculate endpoint without auth (should fail with 401/403)
4. ⏸️  Calculate endpoint with auth (requires token)

## Testing with Authentication

### Option A: Get Token from Frontend

1. **Start Frontend** (in a new terminal):
   ```bash
   cd /Users/arvind.tiwari/Desktop/jioastro/frontend
   npm run dev
   ```

2. **Login** at http://localhost:3000/auth/login

3. **Get Token** from browser console:
   ```javascript
   localStorage.getItem('auth_token')
   ```

4. **Use Token** in curl:
   ```bash
   curl -X POST http://localhost:8000/api/v1/readings/calculate \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Arvind Tiwari",
       "dob": "1976-02-29",
       "tob": "03:45",
       "latitude": 28.7041,
       "longitude": 77.1025,
       "timezone": "Asia/Kolkata",
       "city": "Delhi"
     }'
   ```

### Option B: Use Swagger UI

1. Go to http://localhost:8000/docs
2. Click "Authorize" button (top right)
3. Enter token: `Bearer YOUR_TOKEN_HERE`
4. Click "Authorize"
5. Now you can test endpoints directly in Swagger UI

### Option C: Use Supabase Test Token

1. Go to Supabase Dashboard → SQL Editor
2. Run:
   ```sql
   SELECT auth.sign({
     email: 'your@email.com',
     password: 'yourpassword'
   });
   ```
3. Copy the token
4. Use in API calls

## Expected Response Format

### Successful Reading Calculation

```json
{
  "session_id": "uuid-here",
  "created_at": "2025-11-03T...",
  "canonical_hash": "sha256-hash-here",
  "charts": {
    "rasi": {
      "chart_type": "D1",
      "ascendant": {...},
      "planets": {...},
      "houses": [...],
      "dasha": {...},
      "yogas": [...]
    },
    "navamsa": {
      "chart_type": "D9",
      ...
    },
    "moon": {
      "chart_type": "Moon",
      ...
    }
  },
  "dashas": {
    "maha": {...},
    "antar": {...},
    "all_mahadashas": [...]
  },
  "transits": {
    "planets": {...},
    "calculated_at": "..."
  },
  "basics": {
    "ascendant": {...},
    "moon_sign": "...",
    "sun_sign": "...",
    "yogas": [...],
    "strengths": {...}
  },
  "meta": {
    "tz": "Asia/Kolkata",
    "lat": 28.7041,
    "lon": 77.1025,
    "city": "Delhi",
    "engine_version": "1.0.0-mvp",
    "canonical_hash": "...",
    "calculation_method": "Swiss Ephemeris with Lahiri Ayanamsa",
    "calculated_at": "..."
  }
}
```

## Troubleshooting

### Issue: 401 Unauthorized on /calculate endpoint
**Cause**: Missing or invalid auth token
**Fix**: Get a valid token from frontend or Supabase

### Issue: 403 Forbidden on /calculate endpoint
**Cause**: Token is valid but user doesn't have permission
**Fix**: Ensure user exists in database and has proper RLS policies

### Issue: 403 on /health endpoint (RESOLVED)
**Status**: ✅ Fixed on 2025-11-03
**Previous Cause**: FastAPI route matching issue - `/{session_id}` route was matching "/health"
**Fix Applied**: Reordered routes to put `/health` before `/{session_id}` in readings.py
**Current Status**: Health endpoint now returns 200 OK without authentication

### Issue: 500 Internal Server Error
**Cause**: Missing database tables or service error
**Fix**:
1. Check backend logs for stack trace
2. Ensure database migration was applied
3. Verify Supabase connection

### Issue: Connection Refused
**Cause**: Backend not running
**Fix**: Start backend with `uvicorn main:app --reload`

### Issue: "reading_sessions table doesn't exist"
**Cause**: Database migration not applied
**Fix**: Run `docs/database-schema-ai-engine.sql` in Supabase SQL Editor

## Verification Checklist

Before proceeding to Phase 2, verify:

- [ ] Backend starts without errors
- [ ] `/health` endpoint returns 200
- [ ] `/api/v1/readings/health` returns 200
- [ ] Swagger UI shows new "readings" endpoints
- [ ] Calculate endpoint requires authentication (401/403 without token)
- [ ] Calculate endpoint works with valid token
- [ ] Response includes D1, D9, and Moon charts
- [ ] Response includes canonical hash
- [ ] Response includes transits
- [ ] No errors in backend console

## Next Steps

Once all tests pass:

1. **Apply Database Migration** (if not done yet)
   - See `docs/migrations/001_add_ai_engine_tables.md`

2. **Start Phase 2**
   - Ingest BPHS rules
   - Build knowledge base retrieval
   - Test rule application

3. **Optional: Test Caching**
   - Make same request twice
   - Second request should be faster (cached)
   - Check `reading_sessions` table for cached entry

## Support

If tests fail:
1. Check backend logs for detailed errors
2. Verify database connection to Supabase
3. Ensure all environment variables are set
4. Try restarting backend server
5. Check CORS settings in `app/core/config.py`

---

*Testing Guide - Phase 1*
*Updated: 2025-11-03*
