-- ============================================================================
-- Evidence Mode - Rollback/Cleanup Script
-- ============================================================================
-- Run this script first if you need to reset Evidence Mode tables
-- This will remove all Evidence Mode objects so you can run migration fresh
-- ============================================================================

-- WARNING: This will delete all Evidence Mode data!
-- Make sure you have backups if needed

-- ============================================================================
-- Step 1: Drop Views
-- ============================================================================

DROP VIEW IF EXISTS evidence_mode_summary CASCADE;

-- ============================================================================
-- Step 2: Drop Triggers
-- ============================================================================

DROP TRIGGER IF EXISTS update_sources_updated_at ON evidence_mode_sources;
DROP TRIGGER IF EXISTS update_citations_updated_at ON evidence_mode_citations;
DROP TRIGGER IF EXISTS update_validations_updated_at ON evidence_mode_validations;

-- ============================================================================
-- Step 3: Drop Functions
-- ============================================================================

DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- ============================================================================
-- Step 4: Drop Tables (in reverse dependency order)
-- ============================================================================

DROP TABLE IF EXISTS evidence_mode_validations CASCADE;
DROP TABLE IF EXISTS evidence_mode_citations CASCADE;
DROP TABLE IF EXISTS evidence_mode_sources CASCADE;

-- ============================================================================
-- Step 5: Drop Enums
-- ============================================================================

DROP TYPE IF EXISTS evidence_validation_status CASCADE;
DROP TYPE IF EXISTS evidence_confidence_level CASCADE;
DROP TYPE IF EXISTS evidence_source_type CASCADE;

-- ============================================================================
-- Verification
-- ============================================================================

-- Check that all objects are dropped
DO $$
DECLARE
    table_count INTEGER;
    type_count INTEGER;
BEGIN
    -- Check for remaining tables
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_name LIKE 'evidence_mode%';

    -- Check for remaining types
    SELECT COUNT(*) INTO type_count
    FROM pg_type
    WHERE typname LIKE 'evidence%';

    RAISE NOTICE '========================================';
    RAISE NOTICE 'Evidence Mode Rollback Complete';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Remaining tables: %', table_count;
    RAISE NOTICE 'Remaining types: %', type_count;

    IF table_count = 0 AND type_count = 0 THEN
        RAISE NOTICE 'Status: ✓ All objects removed';
        RAISE NOTICE 'You can now run supabase_migration.sql';
    ELSE
        RAISE WARNING 'Status: ✗ Some objects remain';
        RAISE NOTICE 'Tables: %', (SELECT array_agg(table_name) FROM information_schema.tables WHERE table_name LIKE 'evidence_mode%');
        RAISE NOTICE 'Types: %', (SELECT array_agg(typname) FROM pg_type WHERE typname LIKE 'evidence%');
    END IF;

    RAISE NOTICE '========================================';
END $$;
