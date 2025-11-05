-- Fix 1: Make profile_id nullable in reading_sessions table
-- This allows MVP bridge to work without requiring a profile
-- The MVP bridge accepts raw birth data, not profile references

ALTER TABLE reading_sessions
ALTER COLUMN profile_id DROP NOT NULL;

-- Fix 2: Add meta column as alias for input_params (for backwards compatibility)
-- Or we can just use input_params in the MVP bridge code

-- Verify Fix 1
SELECT
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns
WHERE table_name = 'reading_sessions'
AND column_name = 'profile_id';

-- Expected result: is_nullable = 'YES'

-- Check column names
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'reading_sessions'
ORDER BY ordinal_position;
