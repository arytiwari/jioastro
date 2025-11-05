# AI Reading Caching - Setup Guide

## What Was Fixed

### 1. Memory Service (Backend)
**File**: `backend/app/services/memory_service.py`

- ✅ **Updated** `store_reading_session()` to store ALL Phase 3 fields:
  - `interpretation` - Full reading text
  - `domain_analyses` - Domain-specific analyses
  - `predictions` - Time-based predictions
  - `rules_used` - Citations/rules applied
  - `verification` - Quality scores and confidence levels
  - `orchestration_metadata` - Token usage, costs, etc.
  - `profile_id` - Link to birth profile

### 2. Readings Endpoint (Backend)
**File**: `backend/app/api/v1/endpoints/readings.py`

- ✅ **Enabled** cache checking before generating new readings
- ✅ **Fixed** cache hit response to return full data structure matching frontend expectations
- ✅ **GET endpoint** already returns all columns via `SELECT *`

### 3. Frontend Display (Already Working)
**File**: `frontend/app/dashboard/readings/[id]/page.tsx`

- ✅ **sessionStorage** solution working for new readings
- ✅ **Debug logging** added to track data flow
- ✅ **Field mapping** for compatibility (rules_used → rule_citations, etc.)

## What You Need to Do

### Run Database Migration

The database table needs Phase 3 columns added. You have two options:

#### Option 1: Via Supabase Dashboard (Recommended)

1. Go to your **Supabase Dashboard**
2. Navigate to **SQL Editor**
3. Open the file: `backend/docs/add-phase3-columns.sql`
4. Copy and paste the entire SQL into the editor
5. Click **Run** to execute

#### Option 2: Via psql Command Line

```bash
# Replace with your actual database URL
psql YOUR_DATABASE_URL < backend/docs/add-phase3-columns.sql
```

### What the Migration Does

The migration will:
- ✅ Add Phase 3 columns (interpretation, predictions, verification, etc.)
- ✅ Remove problematic constraints (profile_id NOT NULL, reading_type check)
- ✅ Safe to run multiple times (idempotent)

## Testing the Cache

### Test 1: Generate New Reading

1. Go to http://localhost:3001/dashboard/readings
2. Select a birth profile
3. Click "Generate AI Reading"
4. Observe console logs showing data storage
5. Verify all predictions, quality scores, and metadata display correctly

### Test 2: View Cached Reading (Same Parameters)

1. Generate a reading for a specific profile
2. Generate ANOTHER reading with the EXACT SAME profile and parameters
3. Backend should log: **"✨ Cache hit! Returning cached reading"**
4. Reading should load instantly without calling LLM
5. All data should display correctly (not zeros)

### Test 3: View Old Reading from List

1. Go to readings list
2. Click on a previously generated reading
3. Should display full data from database
4. If it shows zeros, check backend logs for storage errors

## How Caching Works Now

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ User Generates AI Reading                                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ Backend: Calculate canonical_hash from parameters            │
│ (profile + query + domains + prediction_window)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
           ┌──────────┴──────────┐
           │  Check Cache         │
           │  (canonical_hash)    │
           └──────────┬───────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼ NOT FOUND               ▼ FOUND (Cache Hit!)
┌────────────────────┐    ┌────────────────────┐
│ Generate with LLM  │    │ Return from DB     │
│ (3000+ tokens)     │    │ (instant!)         │
└────────┬───────────┘    └────────┬───────────┘
         │                         │
         ▼                         │
┌────────────────────┐             │
│ Store in Database  │             │
│ - interpretation   │             │
│ - predictions      │             │
│ - verification     │             │
│ - metadata         │             │
└────────┬───────────┘             │
         │                         │
         └─────────┬───────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │ Return to Frontend  │
         │ (full data)         │
         └─────────┬───────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │ Display Reading     │
         │ ✓ Predictions       │
         │ ✓ Quality Score     │
         │ ✓ Citations         │
         │ ✓ Metadata          │
         └─────────────────────┘
```

### Cache Key (canonical_hash)

The cache is based on a SHA256 hash of:
- Birth data (DOB, time, location)
- Query text
- Domains requested
- Prediction window (months)

**Same parameters = Cache hit = No LLM call needed!**

### Cache Expiration

- Default: **24 hours**
- Configurable in `get_cached_reading(max_age_hours=24)`
- After expiration, new reading is generated

## Backend Logs to Look For

### Successful Cache Hit
```
✨ Cache hit! Returning cached reading: abc123-def456
```

### New Reading Generation
```
🎭 Generating comprehensive reading with orchestrator...
💾 Storing reading session with full data: 4266 chars, 1 predictions, 5 rules
✅ Reading session stored successfully: abc123-def456
```

### Database Storage Success
```
💾 Storing reading session with full data: 4266 chars, 1 predictions, 5 rules
✅ Reading session stored successfully: dd1bc7ed-f2e8-4aaf-a481-c2174b63c8f6
```

### Errors to Watch For

If you see these, the migration hasn't been run yet:
```
❌ column "interpretation" does not exist
❌ null value in column "profile_id" violates not-null constraint
❌ violates check constraint "reading_sessions_reading_type_check"
```

## Cost Savings

### Without Caching
- **Every viewing**: New LLM call
- **Average tokens**: 3000-4000
- **Cost per view**: ~$0.06-0.08
- **10 views/day**: ~$0.70/day

### With Caching
- **First viewing**: LLM call (~$0.07)
- **Subsequent viewings (24hrs)**: FREE (database query only)
- **10 views of same reading**: ~$0.07 total
- **Savings**: ~90% reduction in LLM costs

## Troubleshooting

### Issue: Reading shows zeros/empty data

**Check:**
1. Browser console logs - does it say "Using cached reading data from sessionStorage"?
2. Backend logs - does it say "Storing reading session with full data"?
3. Run migration SQL if you see column errors

### Issue: Cache not working (always regenerating)

**Check:**
1. Backend logs - do you see "Cache hit"?
2. Are you using EXACT same parameters?
3. Has 24 hours passed since last generation?

### Issue: Database errors on insert

**Solution:**
- Run the migration SQL: `backend/docs/add-phase3-columns.sql`
- This adds missing columns and removes problematic constraints

## Files Modified

### Backend
- ✅ `app/services/memory_service.py` - Store full data
- ✅ `app/api/v1/endpoints/readings.py` - Enable caching
- ✅ `docs/add-phase3-columns.sql` - Migration script

### Frontend
- ✅ `app/dashboard/readings/[id]/page.tsx` - Debug logging (already working)

## Next Steps

1. **Run the migration** (see instructions above)
2. **Generate a test reading** and verify it displays correctly
3. **Generate the same reading again** (same profile, no query changes)
4. **Verify cache hit** in backend logs
5. **Confirm instant loading** with full data

Once migration is complete, caching will work automatically for all future readings! 🎉
