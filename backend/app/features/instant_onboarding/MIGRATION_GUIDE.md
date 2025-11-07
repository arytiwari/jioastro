# Instant Onboarding - Database Migration Guide

## Quick Start

### Option 1: Supabase SQL Editor (Recommended)

1. **Open Supabase Dashboard**
   ```
   https://supabase.com/dashboard/project/YOUR_PROJECT_ID/sql
   ```

2. **Copy the SQL Script**
   - Open: `backend/supabase_migration_instant_onboarding.sql`
   - Copy entire contents

3. **Execute in SQL Editor**
   - Paste into Supabase SQL Editor
   - Click "Run" button
   - Wait for success confirmation

4. **Verify Migration**
   ```sql
   -- Run this verification query:
   SELECT
       'Migration Complete!' AS status,
       (SELECT COUNT(*) FROM information_schema.tables
        WHERE table_name LIKE 'instant_onboarding%') AS tables_created,
       (SELECT COUNT(*) FROM pg_indexes
        WHERE tablename LIKE 'instant_onboarding%') AS indexes_created,
       (SELECT COUNT(*) FROM pg_policies
        WHERE tablename LIKE 'instant_onboarding%') AS policies_created;
   ```

   **Expected Output:**
   ```
   status: "Migration Complete!"
   tables_created: 2
   indexes_created: 13
   policies_created: 9
   ```

### Option 2: Supabase CLI

```bash
# Navigate to backend directory
cd backend

# Run migration via Supabase CLI
supabase db push --file supabase_migration_instant_onboarding.sql

# Or if using local development
supabase db reset
supabase migration new instant_onboarding
# Copy contents of supabase_migration_instant_onboarding.sql to the new migration file
supabase db push
```

### Option 3: Direct PostgreSQL Connection

If you have direct database access:

```bash
psql "postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres" \
  -f supabase_migration_instant_onboarding.sql
```

## What Gets Created

### 📊 Database Objects

#### 1. **Enum Types** (2)
- `session_status`: started, collecting_data, generating_chart, completed, failed
- `onboarding_channel`: whatsapp, web, voice, sms

#### 2. **Tables** (2)

**instant_onboarding_sessions**
- Tracks user onboarding sessions
- Stores collected data incrementally
- Supports multiple channels and languages
- 14 columns total

**instant_onboarding_profiles**
- Links sessions to generated profiles
- Tracks engagement metrics
- Stores conversion data
- 10 columns total

#### 3. **Indexes** (13)
Performance optimizations for:
- Session key lookups
- User ID queries
- Phone number searches
- Status filtering
- Time-based queries
- Channel analytics

#### 4. **Triggers** (1)
- Auto-update `updated_at` timestamp on session changes

#### 5. **RLS Policies** (9)
Security policies for:
- Anonymous session creation
- User-specific data access
- Service role full access
- Session key-based operations

#### 6. **Analytics Views** (2)
- `instant_onboarding_session_stats`: Daily session statistics
- `instant_onboarding_conversion_metrics`: Conversion and engagement rates

#### 7. **Helper Functions** (1)
- `cleanup_expired_onboarding_sessions()`: Cleanup old incomplete sessions

## Post-Migration Steps

### 1. Enable Feature Flag

```bash
# Add to .env file
echo "FEATURE_INSTANT_ONBOARDING=true" >> .env

# Or export in terminal
export FEATURE_INSTANT_ONBOARDING=true
```

### 2. Update Backend Code

The migration script needs to be registered. Add to `main.py`:

```python
from app.features.instant_onboarding import instant_onboarding_feature

# In lifespan function:
try:
    feature_registry.register(instant_onboarding_feature)
    print("✅ Instant Onboarding feature registered")
except Exception as e:
    print(f"⚠️  Failed to register: {e}")

# With routers:
app.include_router(
    instant_onboarding_feature.router,
    prefix="/api/v2",
    tags=["Bonus Features"]
)
```

### 3. Restart Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### 4. Test the Feature

Visit API documentation:
```
http://localhost:8000/docs#/Bonus%20Features/start_session_instant_onboarding_session_start_post
```

**Test Session Creation:**
```bash
curl -X POST "http://localhost:8000/api/v2/instant-onboarding/session/start" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "web",
    "language": "en"
  }'
```

**Expected Response:**
```json
{
  "session_id": "uuid-here",
  "session_key": "random-session-key",
  "status": "collecting_data",
  "next_step": "name",
  "message": "Welcome! Let's create your birth chart in 90 seconds. What's your name?"
}
```

## Testing Data

### Create Test Session

```sql
-- Insert test session
INSERT INTO instant_onboarding_sessions (
    session_key,
    channel,
    language,
    collected_data,
    status
) VALUES (
    'test_' || gen_random_uuid()::text,
    'web',
    'en',
    '{"name": "Test User"}',
    'collecting_data'
) RETURNING *;
```

### View Session Stats

```sql
-- Check session statistics
SELECT * FROM instant_onboarding_session_stats
ORDER BY date DESC
LIMIT 10;
```

### View Conversion Metrics

```sql
-- Check conversion metrics
SELECT * FROM instant_onboarding_conversion_metrics
ORDER BY date DESC
LIMIT 10;
```

## Rollback (If Needed)

To remove all instant onboarding tables:

```sql
-- Drop tables (cascade removes dependent objects)
DROP TABLE IF EXISTS instant_onboarding_profiles CASCADE;
DROP TABLE IF EXISTS instant_onboarding_sessions CASCADE;

-- Drop views
DROP VIEW IF EXISTS instant_onboarding_session_stats;
DROP VIEW IF EXISTS instant_onboarding_conversion_metrics;

-- Drop function
DROP FUNCTION IF EXISTS cleanup_expired_onboarding_sessions;

-- Drop types
DROP TYPE IF EXISTS session_status CASCADE;
DROP TYPE IF EXISTS onboarding_channel CASCADE;
```

## Maintenance

### Clean Up Old Sessions

Run periodically to remove expired sessions:

```sql
-- Clean up sessions older than 7 days
SELECT cleanup_expired_onboarding_sessions();
```

### Monitor Performance

```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'instant_onboarding%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE tablename LIKE 'instant_onboarding%'
ORDER BY idx_scan DESC;
```

## Troubleshooting

### Issue: "relation already exists"
**Solution:** Tables already created, skip creation or drop first

### Issue: "permission denied"
**Solution:** Ensure you're using service_role key or have admin access

### Issue: "enum type already exists"
**Solution:** The `DO $$ BEGIN ... EXCEPTION` block handles this, safe to ignore

### Issue: RLS blocks queries
**Solution:** Check policies or use service_role key for backend operations

## Security Notes

- ✅ RLS enabled on all tables
- ✅ Anonymous users can create sessions (required for instant onboarding)
- ✅ Users can only access their own sessions
- ✅ Service role has full access for backend operations
- ✅ Session keys are used for tracking (not user IDs)
- ⚠️ Session keys should be treated as temporary tokens

## Analytics Queries

### Daily Completion Rate

```sql
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS total_sessions,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'completed') / COUNT(*), 2) AS completion_rate
FROM instant_onboarding_sessions
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### Average Time to Complete

```sql
SELECT
    channel,
    COUNT(*) AS completed_sessions,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) AS avg_seconds,
    MIN(EXTRACT(EPOCH FROM (completed_at - created_at))) AS min_seconds,
    MAX(EXTRACT(EPOCH FROM (completed_at - created_at))) AS max_seconds
FROM instant_onboarding_sessions
WHERE status = 'completed'
  AND completed_at IS NOT NULL
GROUP BY channel;
```

### Conversion Funnel

```sql
SELECT
    'Total Sessions' AS stage,
    COUNT(*) AS count,
    100.0 AS percentage
FROM instant_onboarding_sessions

UNION ALL

SELECT
    'Charts Generated',
    COUNT(*) FILTER (WHERE chart_generated),
    ROUND(100.0 * COUNT(*) FILTER (WHERE chart_generated) / COUNT(*), 2)
FROM instant_onboarding_sessions

UNION ALL

SELECT
    'Charts Viewed',
    COUNT(*) FILTER (WHERE viewed_chart),
    ROUND(100.0 * COUNT(*) FILTER (WHERE viewed_chart) / (SELECT COUNT(*) FROM instant_onboarding_sessions), 2)
FROM instant_onboarding_profiles

UNION ALL

SELECT
    'Charts Shared',
    COUNT(*) FILTER (WHERE shared_chart),
    ROUND(100.0 * COUNT(*) FILTER (WHERE shared_chart) / (SELECT COUNT(*) FROM instant_onboarding_sessions), 2)
FROM instant_onboarding_profiles

UNION ALL

SELECT
    'Converted to Users',
    COUNT(*) FILTER (WHERE converted_to_full_user),
    ROUND(100.0 * COUNT(*) FILTER (WHERE converted_to_full_user) / (SELECT COUNT(*) FROM instant_onboarding_sessions), 2)
FROM instant_onboarding_profiles;
```

## Support

For issues or questions:
1. Check Supabase logs in Dashboard > Logs
2. Review RLS policies if getting permission errors
3. Verify feature flag is enabled: `FEATURE_INSTANT_ONBOARDING=true`
4. Check backend logs for detailed error messages

---

**Migration Version:** 1.0.0
**Created:** 2025-11-07
**Feature:** Instant Onboarding (Bonus #13)
**Status:** Production Ready ✅
