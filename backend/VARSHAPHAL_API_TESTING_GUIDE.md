# Varshaphal API Testing Guide

**Backend URL:** http://localhost:8001
**Base Path:** `/api/v1/varshaphal`

---

## 🔐 Authentication Setup

All Varshaphal endpoints require a JWT token from Supabase Auth.

### Get JWT Token from Supabase

```bash
# Login via Supabase
curl -X POST 'https://YOUR_PROJECT.supabase.co/auth/v1/token?grant_type=password' \
  -H 'apikey: YOUR_SUPABASE_ANON_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "...",
  "user": {...}
}
```

**Save the `access_token`** - you'll use it as `YOUR_JWT_TOKEN` below.

---

## 🧪 Testing Methods

### Method 1: HTML Test Page (Easiest) ⭐

**Open in browser:**
```
file:///Users/arvind.tiwari/Desktop/jioastro/backend/test_varshaphal.html
```

**Or serve locally:**
```bash
cd backend
python -m http.server 8080
# Then open: http://localhost:8080/test_varshaphal.html
```

**Features:**
- ✅ Beautiful UI with tabs
- ✅ All 4 endpoints (Generate, Get, List, Delete)
- ✅ Real-time response display
- ✅ Error handling
- ✅ No installation required

---

### Method 2: FastAPI Swagger UI

**Open in browser:**
```
http://localhost:8001/docs
```

**Steps:**
1. Click **🔓 Authorize** (top right)
2. Enter: `Bearer YOUR_JWT_TOKEN`
3. Click "Authorize"
4. Expand any endpoint
5. Click "Try it out"
6. Fill parameters
7. Click "Execute"

---

### Method 3: curl Commands

#### 1. Generate Varshaphal

```bash
curl -X POST http://localhost:8001/api/v1/varshaphal/generate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "550e8400-e29b-41d4-a716-446655440000",
    "target_year": 2025,
    "force_refresh": false
  }'
```

**Response (200 OK):**
```json
{
  "varshaphal_id": "abc123...",
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "target_year": 2025,
  "generated_at": "2025-11-08T12:00:00Z",
  "expires_at": "2025-12-08T12:00:00Z",
  "solar_return_chart": {
    "solar_return_time": "2025-01-15T10:30:00Z",
    "varsha_lagna": {...},
    "muntha": {...},
    "planets": {...},
    "houses": {...},
    "yogas": [...]
  },
  "patyayini_dasha": [...],
  "sahams": {...},
  "annual_interpretation": {
    "overall_quality": "Excellent",
    "year_summary": "...",
    "monthly_predictions": [...],
    "best_periods": [...],
    "worst_periods": [...],
    "opportunities": [...],
    "challenges": [...],
    "remedies": [...]
  },
  "is_cached": false
}
```

#### 2. Get Varshaphal by ID

```bash
curl -X GET http://localhost:8001/api/v1/varshaphal/abc123... \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 3. List All Varshaphals

```bash
curl -X POST http://localhost:8001/api/v1/varshaphal/list \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "550e8400-e29b-41d4-a716-446655440000",
    "limit": 10,
    "offset": 0
  }'
```

**Response:**
```json
{
  "varshaphals": [
    {
      "varshaphal_id": "abc123...",
      "profile_id": "550e8400...",
      "profile_name": "John Doe",
      "target_year": 2025,
      "generated_at": "2025-11-08T12:00:00Z",
      "expires_at": "2025-12-08T12:00:00Z",
      "is_expired": false,
      "overall_quality": "Excellent",
      "yogas_count": 8
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### 4. Delete Varshaphal

```bash
curl -X DELETE http://localhost:8001/api/v1/varshaphal/abc123... \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:** 204 No Content

---

## 📋 Test Scenarios

### Scenario 1: First Time User (No Cache)

1. **Generate Varshaphal** with `force_refresh: false`
   - Should calculate fresh data
   - Response: `is_cached: false`
   - Time: ~2-5 seconds

2. **Generate Again** (same profile, same year)
   - Should return cached data
   - Response: `is_cached: true`
   - Time: <100ms

3. **Force Refresh** with `force_refresh: true`
   - Should recalculate
   - Response: `is_cached: false`

### Scenario 2: Multiple Years

1. Generate for 2024
2. Generate for 2025
3. Generate for 2026
4. List all → should show 3 records

### Scenario 3: Error Handling

**Test Invalid Profile ID:**
```bash
curl -X POST http://localhost:8001/api/v1/varshaphal/generate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "invalid-uuid",
    "target_year": 2025,
    "force_refresh": false
  }'
```

**Expected:** 404 Not Found

**Test Without Token:**
```bash
curl -X POST http://localhost:8001/api/v1/varshaphal/generate \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "550e8400-e29b-41d4-a716-446655440000",
    "target_year": 2025,
    "force_refresh": false
  }'
```

**Expected:** 401 Unauthorized

---

## 🧩 Understanding the Response

### Solar Return Chart
```json
{
  "solar_return_time": "2025-01-15T10:30:00Z",  // Exact moment Sun returns
  "varsha_lagna": {                             // Annual Ascendant
    "sign": "Aries",
    "degree": 15.5,
    "lord": "Mars"
  },
  "muntha": {                                   // Progressed point
    "sign": "Leo",
    "house": 5,
    "degree": 12.3
  },
  "planets": {                                  // Planetary positions at solar return
    "Sun": {...},
    "Moon": {...},
    // ... all planets
  },
  "houses": [...],                              // House cusps
  "yogas": [                                    // 16 Varshaphal Yogas
    {
      "name": "Ikkavala Yoga",
      "present": true,
      "strength": 0.85,
      "description": "...",
      "effects": "..."
    }
  ]
}
```

### Patyayini Dasha
```json
[
  {
    "planet": "Venus",
    "strength": 0.82,
    "start_date": "2025-01-15T10:30:00Z",
    "end_date": "2025-03-20T08:45:00Z",
    "duration_days": 64,
    "effects": "...",
    "recommendations": "..."
  }
]
```

### Sahams (Sensitive Points)
```json
{
  "punya_saham": {                              // Fortune point
    "longitude": 125.5,
    "sign": "Leo",
    "house": 5,
    "meaning": "Fortune and prosperity"
  },
  "vidya_saham": {                              // Education point
    "longitude": 78.3,
    "sign": "Gemini",
    "house": 3,
    "meaning": "Learning and knowledge"
  }
  // ... 50+ more sahams
}
```

### Annual Interpretation
```json
{
  "overall_quality": "Excellent",               // Excellent/Good/Average/Challenging
  "year_summary": "This year brings...",
  "monthly_predictions": [
    {
      "month": "January",
      "quality": "Good",
      "highlights": [...],
      "warnings": [...]
    }
  ],
  "best_periods": [
    {
      "start_date": "2025-03-10",
      "end_date": "2025-03-25",
      "reason": "Jupiter transit favorable",
      "activities": ["Business deals", "New ventures"]
    }
  ],
  "worst_periods": [...],
  "opportunities": [...],
  "challenges": [...],
  "remedies": [
    "Wear yellow sapphire on Thursday",
    "Donate to educational institutions"
  ]
}
```

---

## 🔍 Debugging Tips

### Check Backend Logs

```bash
# Backend is running on port 8001
# Check logs for errors
tail -f backend_logs.txt  # if logging to file

# Or check terminal where backend is running
```

### Common Issues

**1. 401 Unauthorized**
- Check JWT token is valid
- Verify `Authorization: Bearer TOKEN` format
- Token may be expired (Supabase tokens expire in 1 hour)

**2. 404 Profile Not Found**
- Verify profile exists in database
- Check profile belongs to authenticated user
- Verify UUID format is correct

**3. 500 Internal Server Error**
- Check backend logs
- Verify all required services are running
- Check Swiss Ephemeris files are present

**4. CORS Errors (if testing from different domain)**
- Backend should allow CORS
- Check `app/core/config.py` ALLOWED_ORIGINS

---

## 🎯 Performance Expectations

| Operation | First Time | Cached |
|-----------|-----------|--------|
| Generate Varshaphal | 2-5 seconds | <100ms |
| Get by ID | <50ms | <50ms |
| List All | <100ms | <100ms |
| Delete | <50ms | <50ms |

**Cache Duration:** 30 days (configurable)

---

## 📊 Testing Checklist

- [ ] Backend running on port 8001
- [ ] Database migrations executed
- [ ] JWT token obtained
- [ ] HTML test page opened
- [ ] Generate Varshaphal - Success
- [ ] Get Varshaphal by ID - Success
- [ ] List all Varshaphals - Success
- [ ] Delete Varshaphal - Success
- [ ] Cache working (2nd generate returns cached)
- [ ] Force refresh working
- [ ] Error handling working (invalid IDs)
- [ ] Authentication working (401 without token)

---

## 🚀 Quick Start Example

```bash
# 1. Get your JWT token (save it)
TOKEN="eyJhbGc..."

# 2. Generate Varshaphal
curl -X POST http://localhost:8001/api/v1/varshaphal/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "YOUR_PROFILE_ID",
    "target_year": 2025,
    "force_refresh": false
  }' | jq .

# 3. Save the varshaphal_id from response
VARSHAPHAL_ID="abc123..."

# 4. Get it back
curl -X GET http://localhost:8001/api/v1/varshaphal/$VARSHAPHAL_ID \
  -H "Authorization: Bearer $TOKEN" | jq .

# 5. List all
curl -X POST http://localhost:8001/api/v1/varshaphal/list \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "offset": 0}' | jq .
```

---

## 📝 Notes

- **Cache Key:** Based on `user_id:profile_id:target_year` (SHA256 hash)
- **Expiry:** 30 days from generation
- **Solar Return Time:** Calculated using binary search (1-second accuracy)
- **Yogas Detected:** Up to 16 Varshaphal-specific yogas
- **Sahams:** 50+ sensitive points calculated
- **Dasha System:** Patyayini (annual, not Vimshottari)

---

**Ready to Test!** 🎉

Start with the **HTML test page** for the easiest experience, or use **Swagger UI** for interactive testing.
