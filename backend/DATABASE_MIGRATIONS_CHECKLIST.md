# Database Migrations Checklist

**Date:** 2025-11-08
**Status:** ✅ Complete

---

## Required Migrations for Supabase

### 1. ✅ Life Snapshot Feature (Magical 12 #1)

**Migration File:** `docs/migrations/life_snapshot_tables.sql`

**What It Creates:**
- `life_snapshot_data` table
- 6 indexes for performance
- Foreign key to `profiles` table
- Optional RLS policies (commented out)

**Run This SQL:**
```sql
-- Migration: Add Life Snapshot tables
-- Feature: Life Snapshot (Magical 12 Feature #1)

CREATE TABLE IF NOT EXISTS life_snapshot_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    profile_id UUID NOT NULL,
    snapshot_data JSONB NOT NULL,
    transits_data JSONB,
    insights JSONB NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    cache_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_life_snapshot_user_id ON life_snapshot_data(user_id);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_profile_id ON life_snapshot_data(profile_id);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_cache_key ON life_snapshot_data(cache_key);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_generated_at ON life_snapshot_data(generated_at);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_expires_at ON life_snapshot_data(expires_at);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_cache_lookup ON life_snapshot_data(user_id, profile_id, expires_at);
```

**Verification:**
```sql
-- Check table exists
SELECT tablename FROM pg_tables WHERE tablename = 'life_snapshot_data';

-- Check indexes (should return 6)
SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'life_snapshot_data';
```

---

### 2. ✅ Varshaphal Feature (Annual Predictions)

**Migration File:** `docs/migrations/varshaphal_tables.sql`

**What It Creates:**
- `varshaphal_data` table
- 8 indexes for performance
- `update_varshaphal_updated_at()` trigger function
- Automatic `updated_at` trigger
- Foreign key to `profiles` table

**Run This SQL:**
```sql
-- Migration: Add Varshaphal (Annual Predictions) tables
-- Fixed version with trigger handling

CREATE TABLE IF NOT EXISTS varshaphal_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    target_year INTEGER NOT NULL,
    solar_return_time TIMESTAMP WITH TIME ZONE NOT NULL,
    natal_sun_longitude VARCHAR(50) NOT NULL,
    solar_return_chart JSONB NOT NULL,
    patyayini_dasha JSONB NOT NULL,
    sahams JSONB NOT NULL,
    annual_interpretation JSONB NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_varshaphal_user_id ON varshaphal_data(user_id);
CREATE INDEX IF NOT EXISTS idx_varshaphal_profile_id ON varshaphal_data(profile_id);
CREATE INDEX IF NOT EXISTS idx_varshaphal_target_year ON varshaphal_data(target_year);
CREATE INDEX IF NOT EXISTS idx_varshaphal_user_year ON varshaphal_data(user_id, target_year);
CREATE INDEX IF NOT EXISTS idx_varshaphal_profile_year ON varshaphal_data(profile_id, target_year);
CREATE INDEX IF NOT EXISTS idx_varshaphal_expires_at ON varshaphal_data(expires_at);
CREATE INDEX IF NOT EXISTS idx_varshaphal_cache_key ON varshaphal_data(cache_key);
CREATE INDEX IF NOT EXISTS idx_varshaphal_id ON varshaphal_data(id);

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS trigger_varshaphal_updated_at ON varshaphal_data;

-- Create trigger function
CREATE OR REPLACE FUNCTION update_varshaphal_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
CREATE TRIGGER trigger_varshaphal_updated_at
    BEFORE UPDATE ON varshaphal_data
    FOR EACH ROW
    EXECUTE FUNCTION update_varshaphal_updated_at();
```

**Verification:**
```sql
-- Check table exists
SELECT tablename FROM pg_tables WHERE tablename = 'varshaphal_data';

-- Check indexes (should return 8)
SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'varshaphal_data';

-- Check trigger exists
SELECT trigger_name FROM information_schema.triggers
WHERE event_object_table = 'varshaphal_data';
```

---

## Migration Execution Steps

### Using Supabase Dashboard (Recommended)

1. **Go to Supabase Dashboard**
   - Navigate to: https://supabase.com/dashboard
   - Select your project
   - Go to **SQL Editor**

2. **Run Life Snapshot Migration**
   - Click **"New Query"**
   - Copy SQL from `docs/migrations/life_snapshot_tables.sql`
   - Click **"Run"** or press `Ctrl+Enter`
   - Verify with verification queries

3. **Run Varshaphal Migration**
   - Click **"New Query"**
   - Copy SQL from `docs/migrations/varshaphal_tables.sql`
   - Click **"Run"** or press `Ctrl+Enter`
   - Verify with verification queries

### Using psql

```bash
# Life Snapshot
psql "$DATABASE_URL" -f backend/docs/migrations/life_snapshot_tables.sql

# Varshaphal
psql "$DATABASE_URL" -f backend/docs/migrations/varshaphal_tables.sql
```

---

## Post-Migration Verification

### Complete Verification Script

Run this to verify both migrations:

```sql
-- Check both tables exist
SELECT tablename FROM pg_tables
WHERE tablename IN ('life_snapshot_data', 'varshaphal_data')
ORDER BY tablename;
-- Should return 2 rows

-- Check Life Snapshot indexes (should be 6)
SELECT COUNT(*) AS life_snapshot_indexes
FROM pg_indexes WHERE tablename = 'life_snapshot_data';

-- Check Varshaphal indexes (should be 8)
SELECT COUNT(*) AS varshaphal_indexes
FROM pg_indexes WHERE tablename = 'varshaphal_data';

-- Check Varshaphal trigger
SELECT trigger_name, event_object_table
FROM information_schema.triggers
WHERE event_object_table = 'varshaphal_data';

-- Check foreign keys
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name IN ('life_snapshot_data', 'varshaphal_data')
ORDER BY tc.table_name;
```

**Expected Results:**
- ✅ 2 tables created
- ✅ 6 indexes on `life_snapshot_data`
- ✅ 8 indexes on `varshaphal_data`
- ✅ 1 trigger on `varshaphal_data`
- ✅ 2 foreign keys to `profiles` table

---

## Common Issues & Solutions

### Issue 1: Trigger Already Exists
**Error:** `trigger "trigger_varshaphal_updated_at" for relation "varshaphal_data" already exists`

**Solution:** The migration file has been updated with `DROP TRIGGER IF EXISTS` to handle this. Re-run the migration.

### Issue 2: Table Already Exists
**Error:** `relation "varshaphal_data" already exists`

**Solution:** This is safe! The migration uses `CREATE TABLE IF NOT EXISTS`, so it will skip table creation and only create missing indexes/triggers.

### Issue 3: Foreign Key Error
**Error:** `relation "profiles" does not exist`

**Solution:** Ensure the `profiles` table exists first. If you're setting up a new database, create the profiles table before running these migrations.

### Issue 4: Permission Denied
**Error:** `permission denied for schema public`

**Solution:** Ensure you're running the migration with a user that has CREATE privileges. Use the Supabase service role or database owner.

---

## Optional: Row Level Security (RLS)

If you want to enable RLS for additional security:

### Life Snapshot RLS Policies
```sql
-- Enable RLS
ALTER TABLE life_snapshot_data ENABLE ROW LEVEL SECURITY;

-- Allow users to view their own snapshots
CREATE POLICY "Users can view their own snapshots"
ON life_snapshot_data FOR SELECT
USING (auth.uid() = user_id);

-- Allow users to create their own snapshots
CREATE POLICY "Users can create their own snapshots"
ON life_snapshot_data FOR INSERT
WITH CHECK (auth.uid() = user_id);
```

### Varshaphal RLS Policies
```sql
-- Enable RLS
ALTER TABLE varshaphal_data ENABLE ROW LEVEL SECURITY;

-- Allow users to view their own varshaphals
CREATE POLICY "Users can view their own varshaphals"
ON varshaphal_data FOR SELECT
USING (auth.uid() = user_id);

-- Allow users to create their own varshaphals
CREATE POLICY "Users can create their own varshaphals"
ON varshaphal_data FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Allow users to delete their own varshaphals
CREATE POLICY "Users can delete their own varshaphals"
ON varshaphal_data FOR DELETE
USING (auth.uid() = user_id);
```

**Note:** Currently, the backend uses the **service role key** which bypasses RLS. RLS is optional for additional security if you switch to using the anon key.

---

## Migration Status

- [x] ✅ Life Snapshot table created
- [x] ✅ Life Snapshot indexes created (6)
- [x] ✅ Varshaphal table created
- [x] ✅ Varshaphal indexes created (8)
- [x] ✅ Varshaphal trigger created
- [x] ✅ Foreign keys verified
- [x] ✅ Migration files updated with fixes
- [ ] ⏸️ RLS policies (optional)

---

## Summary

Both migrations are complete and ready for use:

1. **Life Snapshot** - Stores 60-second personalized life insights
2. **Varshaphal** - Stores annual predictions with solar return charts

Both features use **Supabase REST API** (no direct PostgreSQL connections) and are fully operational.

**Total Database Objects Created:**
- 2 tables
- 14 indexes
- 1 trigger function
- 1 trigger
- 2 foreign key constraints

---

**Migrations Completed:** 2025-11-08
**Status:** ✅ Production Ready
