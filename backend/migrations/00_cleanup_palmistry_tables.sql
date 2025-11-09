-- ============================================================================
-- Palmistry Tables Cleanup Script
-- Run this FIRST to remove any existing palmistry tables before running the migration
-- ============================================================================

-- Drop all views first (views depend on tables)
DROP VIEW IF EXISTS v_recent_readings CASCADE;

-- Drop all tables in reverse dependency order
DROP TABLE IF EXISTS palm_feedback CASCADE;
DROP TABLE IF EXISTS reanalysis_queue CASCADE;
DROP TABLE IF EXISTS palm_interpretations CASCADE;
DROP TABLE IF EXISTS palm_readings CASCADE;
DROP TABLE IF EXISTS ai_models CASCADE;
DROP TABLE IF EXISTS palm_photos CASCADE;

-- Drop the trigger function if it exists
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS get_user_reading_stats(UUID) CASCADE;

-- Verify cleanup
SELECT
    table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'palm_%';

-- Should return 0 rows if cleanup successful
