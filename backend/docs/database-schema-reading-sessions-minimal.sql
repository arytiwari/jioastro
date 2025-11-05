-- Minimal Reading Sessions Table for Phase 3 AI Orchestrator
-- This is a standalone version that doesn't require profiles table

-- Drop existing table if it exists (WARNING: This will delete data!)
DROP TABLE IF EXISTS reading_sessions CASCADE;

-- Create reading_sessions table with minimal dependencies
CREATE TABLE IF NOT EXISTS reading_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Session identification
    canonical_hash VARCHAR(64) UNIQUE,

    -- Reading parameters (basic fields only)
    query TEXT,
    domains TEXT[],
    include_predictions BOOLEAN DEFAULT TRUE,
    include_transits BOOLEAN DEFAULT FALSE,
    prediction_window_months INTEGER DEFAULT 12,

    -- Results stored as JSONB
    interpretation TEXT,
    domain_analyses JSONB,
    predictions JSONB,
    rules_used JSONB,
    verification JSONB,
    orchestration_metadata JSONB,

    -- Performance metrics
    total_tokens_used INTEGER,
    generation_time_ms INTEGER,
    model_used VARCHAR(100),

    -- User feedback
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    user_feedback TEXT,

    -- Cache control
    cache_hit BOOLEAN DEFAULT FALSE,
    times_accessed INTEGER DEFAULT 1,
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_reading_sessions_user_id ON reading_sessions(user_id);
CREATE INDEX idx_reading_sessions_hash ON reading_sessions(canonical_hash);
CREATE INDEX idx_reading_sessions_created ON reading_sessions(created_at DESC);
CREATE INDEX idx_reading_sessions_rating ON reading_sessions(user_rating);

-- Row Level Security
ALTER TABLE reading_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own reading sessions" ON reading_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own reading sessions" ON reading_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own reading sessions" ON reading_sessions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own reading sessions" ON reading_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_reading_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_reading_sessions_timestamp ON reading_sessions;
CREATE TRIGGER update_reading_sessions_timestamp
    BEFORE UPDATE ON reading_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_reading_sessions_updated_at();

-- Grant permissions (if using service role)
-- GRANT ALL ON reading_sessions TO authenticated;
-- GRANT ALL ON reading_sessions TO service_role;

COMMENT ON TABLE reading_sessions IS 'AI reading sessions with orchestration metadata (Phase 3)';
