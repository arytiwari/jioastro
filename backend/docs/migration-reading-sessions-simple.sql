-- Simple Reading Sessions Table Migration
-- Run this in Supabase SQL Editor

-- Step 1: Drop existing table (if it exists)
DROP TABLE IF EXISTS reading_sessions CASCADE;

-- Step 2: Create new table with Phase 3 schema
CREATE TABLE reading_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    canonical_hash VARCHAR(64) UNIQUE,

    -- Reading parameters
    query TEXT,
    domains TEXT[],
    include_predictions BOOLEAN DEFAULT TRUE,
    include_transits BOOLEAN DEFAULT FALSE,
    prediction_window_months INTEGER DEFAULT 12,

    -- Results
    interpretation TEXT,
    domain_analyses JSONB,
    predictions JSONB,
    rules_used JSONB,
    verification JSONB,
    orchestration_metadata JSONB,

    -- Metrics
    total_tokens_used INTEGER,
    generation_time_ms INTEGER,
    model_used VARCHAR(100),

    -- Feedback
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    user_feedback TEXT,

    -- Cache
    cache_hit BOOLEAN DEFAULT FALSE,
    times_accessed INTEGER DEFAULT 1,
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Step 3: Create indexes
CREATE INDEX idx_reading_sessions_user_id ON reading_sessions(user_id);
CREATE INDEX idx_reading_sessions_hash ON reading_sessions(canonical_hash);
CREATE INDEX idx_reading_sessions_created ON reading_sessions(created_at DESC);

-- Step 4: Enable RLS
ALTER TABLE reading_sessions ENABLE ROW LEVEL SECURITY;

-- Step 5: Create policies
CREATE POLICY "Users can view own sessions"
    ON reading_sessions FOR SELECT
    USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own sessions"
    ON reading_sessions FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own sessions"
    ON reading_sessions FOR UPDATE
    USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete own sessions"
    ON reading_sessions FOR DELETE
    USING (auth.uid()::text = user_id::text);

-- Done!
-- Test with: SELECT * FROM reading_sessions LIMIT 1;
