# Database Migrations Guide

This directory contains SQL migration files for the JioAstro database.

## How to Run Migrations

### Option 1: Using Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Click **New Query**
4. Copy the contents of the migration file
5. Paste and click **Run**

### Option 2: Using psql Command Line

```bash
# Set your database URL (from Supabase dashboard → Settings → Database)
export DATABASE_URL="postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres"

# Run the migration
psql $DATABASE_URL -f chart_comparisons_table.sql
```

### Option 3: Using Supabase CLI

```bash
# Install Supabase CLI if not already installed
npm install -g supabase

# Link to your project
supabase link --project-ref [YOUR-PROJECT-REF]

# Run migration
supabase db push
```

## Available Migrations

### `chart_comparisons_table.sql`
**Date**: 2025-01-08
**Purpose**: Create table for storing chart comparison results

**What it creates**:
- `chart_comparisons` table with columns:
  - `id` (UUID, primary key)
  - `user_id` (UUID, foreign key to auth.users)
  - `profile_id_1` (UUID, foreign key to profiles)
  - `profile_id_2` (UUID, foreign key to profiles)
  - `comparison_type` (VARCHAR)
  - `comparison_data` (JSONB)
  - `created_at`, `updated_at` (timestamps)

**Features**:
- Row-Level Security (RLS) enabled
- Indexes on user_id, profile_id_1, profile_id_2, created_at, comparison_type
- Automatic `updated_at` trigger
- Constraint: profile_id_1 != profile_id_2

**Required**: Yes, for chart comparison save functionality

## Verifying Migrations

After running a migration, verify it worked:

```sql
-- Check if table exists
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name = 'chart_comparisons';

-- Check RLS policies
SELECT * FROM pg_policies WHERE tablename = 'chart_comparisons';

-- Check indexes
SELECT indexname FROM pg_indexes WHERE tablename = 'chart_comparisons';
```

## Rollback

If you need to rollback the `chart_comparisons` migration:

```sql
-- Remove all policies
DROP POLICY IF EXISTS chart_comparisons_select_policy ON chart_comparisons;
DROP POLICY IF EXISTS chart_comparisons_insert_policy ON chart_comparisons;
DROP POLICY IF EXISTS chart_comparisons_update_policy ON chart_comparisons;
DROP POLICY IF EXISTS chart_comparisons_delete_policy ON chart_comparisons;

-- Drop trigger and function
DROP TRIGGER IF EXISTS chart_comparisons_updated_at_trigger ON chart_comparisons;
DROP FUNCTION IF EXISTS update_chart_comparisons_updated_at();

-- Drop table
DROP TABLE IF EXISTS chart_comparisons;
```

## Migration Status

| Migration File | Status | Date Applied | Notes |
|---------------|--------|--------------|-------|
| `chart_comparisons_table.sql` | ⏳ Pending | - | Run this to enable chart comparison saving |

**Legend**:
- ⏳ Pending - Not yet applied
- ✅ Applied - Successfully applied
- ❌ Failed - Application failed, check logs

## Best Practices

1. **Always backup** before running migrations in production
2. **Test migrations** in development environment first
3. **Run migrations** during low-traffic periods
4. **Monitor** application logs after applying migrations
5. **Document** any manual changes or data migrations

## Support

For issues with migrations:
1. Check Supabase dashboard logs
2. Verify PostgreSQL version compatibility
3. Ensure proper permissions (service_role key for admin operations)
4. Review `TROUBLESHOOTING_SESSION_2025-01-08.md` for common issues
