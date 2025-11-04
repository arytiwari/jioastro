-- Memory System Database Schema
-- For Phase 3: LLM Orchestration
-- Supports user preferences, event anchors, and privacy-first memory

-- ============================================================================
-- USER MEMORY TABLE
-- ============================================================================
-- Stores user preferences, feedback, and contextual memory
-- Privacy-first: All user erasable

CREATE TABLE IF NOT EXISTS user_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,

    -- Memory type
    memory_type VARCHAR(50) NOT NULL CHECK (memory_type IN (
        'preference',       -- User preferences (display, language, etc.)
        'feedback',         -- User feedback on interpretations
        'correction',       -- User corrections to predictions
        'context',          -- Contextual information about user
        'event',            -- Past events (not anchors, just memory)
        'goal',             -- User's stated goals/intentions
        'question_history'  -- Past questions for context
    )),

    -- Memory content
    key VARCHAR(255) NOT NULL,           -- Memory key (e.g., 'preferred_language', 'career_focus')
    value TEXT NOT NULL,                 -- Memory value (can be JSON)
    confidence FLOAT DEFAULT 1.0,        -- Confidence in this memory (0-1)

    -- Source tracking
    source VARCHAR(100),                 -- Where this memory came from
    source_id UUID,                      -- Reference to source (query_id, response_id, etc.)

    -- Metadata
    relevance_score FLOAT DEFAULT 1.0,   -- How relevant is this memory (decays over time)
    last_accessed_at TIMESTAMPTZ,        -- When was this memory last used
    access_count INTEGER DEFAULT 0,      -- How many times accessed

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,              -- Optional expiration

    -- Indexing
    UNIQUE(user_id, memory_type, key)
);

-- Indexes for user_memory
CREATE INDEX idx_user_memory_user_id ON user_memory(user_id);
CREATE INDEX idx_user_memory_profile_id ON user_memory(profile_id);
CREATE INDEX idx_user_memory_type ON user_memory(memory_type);
CREATE INDEX idx_user_memory_relevance ON user_memory(relevance_score DESC);
CREATE INDEX idx_user_memory_last_accessed ON user_memory(last_accessed_at DESC);

-- Row Level Security for user_memory
ALTER TABLE user_memory ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own memory" ON user_memory
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own memory" ON user_memory
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own memory" ON user_memory
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own memory" ON user_memory
    FOR DELETE USING (auth.uid() = user_id);


-- ============================================================================
-- EVENT ANCHORS TABLE
-- ============================================================================
-- Stores major life events for birth time rectification
-- Each event helps narrow down birth time accuracy

CREATE TABLE IF NOT EXISTS event_anchors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Event details
    event_type VARCHAR(100) NOT NULL CHECK (event_type IN (
        'marriage',
        'divorce',
        'job_start',
        'job_end',
        'promotion',
        'relocation',
        'childbirth',
        'parent_death',
        'sibling_marriage',
        'major_accident',
        'surgery',
        'property_purchase',
        'business_start',
        'education_start',
        'education_end',
        'spiritual_initiation',
        'foreign_travel',
        'legal_issue',
        'inheritance',
        'other'
    )),

    event_description TEXT,
    event_date DATE NOT NULL,            -- When did this event occur
    event_significance VARCHAR(50) CHECK (event_significance IN ('very_high', 'high', 'medium', 'low')),

    -- Astrological correlation
    expected_dasha VARCHAR(100),         -- Which dasha should this event occur in
    expected_transit TEXT,               -- Expected transit conditions
    correlation_strength FLOAT,          -- How well does this match chart (0-1)

    -- Rectification data
    helps_rectify BOOLEAN DEFAULT TRUE,  -- Is this useful for rectification
    time_sensitivity VARCHAR(50),        -- How time-sensitive is this event

    -- Verification
    verified BOOLEAN DEFAULT FALSE,      -- Has astrologer verified this anchor
    verified_by UUID REFERENCES auth.users(id),
    verified_at TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT                           -- Additional notes
);

-- Indexes for event_anchors
CREATE INDEX idx_event_anchors_user_id ON event_anchors(user_id);
CREATE INDEX idx_event_anchors_profile_id ON event_anchors(profile_id);
CREATE INDEX idx_event_anchors_event_date ON event_anchors(event_date);
CREATE INDEX idx_event_anchors_type ON event_anchors(event_type);
CREATE INDEX idx_event_anchors_verified ON event_anchors(verified);

-- Row Level Security for event_anchors
ALTER TABLE event_anchors ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own event anchors" ON event_anchors
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own event anchors" ON event_anchors
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own event anchors" ON event_anchors
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own event anchors" ON event_anchors
    FOR DELETE USING (auth.uid() = user_id);


-- ============================================================================
-- READING SESSIONS TABLE (Enhanced)
-- ============================================================================
-- Track orchestrated reading sessions with full metadata

CREATE TABLE IF NOT EXISTS reading_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Session identification
    canonical_hash VARCHAR(64) UNIQUE,   -- Hash of (profile_id, chart_version, query_type)

    -- Reading parameters
    query TEXT,
    domains TEXT[],                      -- Array of domains analyzed
    include_predictions BOOLEAN DEFAULT TRUE,
    include_transits BOOLEAN DEFAULT FALSE,
    prediction_window_months INTEGER DEFAULT 12,

    -- Results (stored as JSONB for flexibility)
    interpretation TEXT,
    domain_analyses JSONB,               -- Separate analyses per domain
    predictions JSONB,                   -- Time-based predictions
    rules_used JSONB,                    -- Rules cited
    verification JSONB,                  -- Quality metrics
    orchestration_metadata JSONB,        -- Roles executed, tokens, etc.

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
    expires_at TIMESTAMPTZ                -- Optional cache expiration
);

-- Indexes for reading_sessions
CREATE INDEX idx_reading_sessions_user_id ON reading_sessions(user_id);
CREATE INDEX idx_reading_sessions_profile_id ON reading_sessions(profile_id);
CREATE INDEX idx_reading_sessions_hash ON reading_sessions(canonical_hash);
CREATE INDEX idx_reading_sessions_created ON reading_sessions(created_at DESC);
CREATE INDEX idx_reading_sessions_rating ON reading_sessions(user_rating);

-- Row Level Security for reading_sessions
ALTER TABLE reading_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own reading sessions" ON reading_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own reading sessions" ON reading_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own reading sessions" ON reading_sessions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own reading sessions" ON reading_sessions
    FOR DELETE USING (auth.uid() = user_id);


-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_user_memory_updated_at BEFORE UPDATE ON user_memory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_event_anchors_updated_at BEFORE UPDATE ON event_anchors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reading_sessions_updated_at BEFORE UPDATE ON reading_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- Function to decay memory relevance over time
CREATE OR REPLACE FUNCTION decay_memory_relevance()
RETURNS void AS $$
BEGIN
    UPDATE user_memory
    SET relevance_score = GREATEST(0.1, relevance_score * 0.95)
    WHERE memory_type IN ('context', 'event', 'question_history')
    AND last_accessed_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Optional: Schedule this function to run periodically
-- CREATE EXTENSION IF NOT EXISTS pg_cron;
-- SELECT cron.schedule('decay-memory', '0 0 * * *', 'SELECT decay_memory_relevance()');


-- ============================================================================
-- EXAMPLE QUERIES
-- ============================================================================

-- Get user's most relevant memories
-- SELECT * FROM user_memory
-- WHERE user_id = '...'
-- ORDER BY relevance_score DESC, last_accessed_at DESC
-- LIMIT 10;

-- Get event anchors for rectification
-- SELECT * FROM event_anchors
-- WHERE profile_id = '...'
-- AND helps_rectify = TRUE
-- ORDER BY event_significance DESC, correlation_strength DESC;

-- Check if reading is cached
-- SELECT * FROM reading_sessions
-- WHERE canonical_hash = '...'
-- AND expires_at > NOW()
-- ORDER BY created_at DESC
-- LIMIT 1;

-- Get user's reading history
-- SELECT id, query, domains, user_rating, created_at
-- FROM reading_sessions
-- WHERE user_id = '...'
-- ORDER BY created_at DESC;


-- ============================================================================
-- PRIVACY & GDPR COMPLIANCE
-- ============================================================================

-- Function to erase all user data (GDPR right to erasure)
CREATE OR REPLACE FUNCTION erase_user_data(target_user_id UUID)
RETURNS void AS $$
BEGIN
    -- Delete memory
    DELETE FROM user_memory WHERE user_id = target_user_id;

    -- Delete event anchors
    DELETE FROM event_anchors WHERE user_id = target_user_id;

    -- Delete reading sessions
    DELETE FROM reading_sessions WHERE user_id = target_user_id;

    RAISE NOTICE 'All data for user % has been erased', target_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE user_memory IS 'Privacy-first user memory system for contextual AI readings';
COMMENT ON TABLE event_anchors IS 'Major life events for birth time rectification';
COMMENT ON TABLE reading_sessions IS 'Cached orchestrated reading sessions with full metadata';
COMMENT ON FUNCTION decay_memory_relevance() IS 'Gradually reduces relevance of old memories';
COMMENT ON FUNCTION erase_user_data(UUID) IS 'GDPR-compliant user data erasure';
