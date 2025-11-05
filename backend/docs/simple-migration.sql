-- Simple Phase 3 Migration (No DO blocks - works better with Supabase SQL Editor)
-- Run each statement separately if needed

-- Add interpretation column
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS interpretation TEXT;

-- Add domain_analyses column
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS domain_analyses JSONB;

-- Add predictions column
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS predictions JSONB;

-- Add rules_used column
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS rules_used JSONB;

-- Add verification column
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS verification JSONB;

-- Add orchestration_metadata column
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS orchestration_metadata JSONB;

-- Add query column
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS query TEXT;

-- Add domains column
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS domains TEXT[];

-- Add total_tokens_used column
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS total_tokens_used INTEGER;

-- Add cache_hit column
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS cache_hit BOOLEAN DEFAULT FALSE;

-- Add profile_id column (UUID reference to profiles, nullable)
ALTER TABLE reading_sessions ADD COLUMN IF NOT EXISTS profile_id UUID;

-- Drop reading_type check constraint (if it exists)
ALTER TABLE reading_sessions DROP CONSTRAINT IF EXISTS reading_sessions_reading_type_check;
