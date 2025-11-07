-- =====================================================
-- Instant Onboarding Feature - Database Migration
-- Feature #13: WhatsApp-to-chart in 90 seconds
-- =====================================================
--
-- This script creates all necessary tables, indexes, and
-- Row Level Security (RLS) policies for the Instant Onboarding feature.
--
-- Execute this in Supabase SQL Editor:
-- https://supabase.com/dashboard/project/YOUR_PROJECT/sql
--
-- =====================================================

-- Step 1: Create Enum Types
-- =====================================================

-- Session status enum
DO $$ BEGIN
    CREATE TYPE session_status AS ENUM (
        'started',
        'collecting_data',
        'generating_chart',
        'completed',
        'failed'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Onboarding channel enum
DO $$ BEGIN
    CREATE TYPE onboarding_channel AS ENUM (
        'whatsapp',
        'web',
        'voice',
        'sms'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

COMMENT ON TYPE session_status IS 'Status of an onboarding session';
COMMENT ON TYPE onboarding_channel IS 'Channel through which user is onboarding';


-- Step 2: Create instant_onboarding_sessions Table
-- =====================================================

CREATE TABLE IF NOT EXISTS instant_onboarding_sessions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Session Information
    session_key VARCHAR(255) UNIQUE NOT NULL,
    channel onboarding_channel NOT NULL DEFAULT 'web',
    status session_status NOT NULL DEFAULT 'started',
    language VARCHAR(10) NOT NULL DEFAULT 'en',

    -- User Identification (nullable until created)
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    phone_number VARCHAR(20),

    -- Collected Data
    collected_data JSONB NOT NULL DEFAULT '{}',

    -- Progress Tracking
    current_step INTEGER DEFAULT 0,
    steps_completed JSONB NOT NULL DEFAULT '[]',

    -- Result
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    chart_generated BOOLEAN DEFAULT FALSE,

    -- Metadata
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_instant_onboarding_sessions_session_key
    ON instant_onboarding_sessions(session_key);

CREATE INDEX IF NOT EXISTS idx_instant_onboarding_sessions_user_id
    ON instant_onboarding_sessions(user_id)
    WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_instant_onboarding_sessions_phone_number
    ON instant_onboarding_sessions(phone_number)
    WHERE phone_number IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_instant_onboarding_sessions_status
    ON instant_onboarding_sessions(status);

CREATE INDEX IF NOT EXISTS idx_instant_onboarding_sessions_created_at
    ON instant_onboarding_sessions(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_instant_onboarding_sessions_channel_status
    ON instant_onboarding_sessions(channel, status);

-- Composite index for active session lookup
CREATE INDEX IF NOT EXISTS idx_instant_onboarding_sessions_active
    ON instant_onboarding_sessions(phone_number, status, created_at DESC)
    WHERE status IN ('started', 'collecting_data');

-- Add comments
COMMENT ON TABLE instant_onboarding_sessions IS 'Tracks instant onboarding sessions for WhatsApp-to-chart in 90 seconds';
COMMENT ON COLUMN instant_onboarding_sessions.session_key IS 'Unique session identifier for tracking';
COMMENT ON COLUMN instant_onboarding_sessions.collected_data IS 'JSON storage for incrementally collected birth data';
COMMENT ON COLUMN instant_onboarding_sessions.steps_completed IS 'Array of completed step identifiers';


-- Step 3: Create instant_onboarding_profiles Table
-- =====================================================

CREATE TABLE IF NOT EXISTS instant_onboarding_profiles (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Links
    session_id UUID NOT NULL REFERENCES instant_onboarding_sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Onboarding Metadata
    channel onboarding_channel NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    time_taken_seconds INTEGER,

    -- Engagement Metrics
    viewed_chart BOOLEAN DEFAULT FALSE,
    shared_chart BOOLEAN DEFAULT FALSE,
    converted_to_full_user BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_instant_onboarding_profiles_session_id
    ON instant_onboarding_profiles(session_id);

CREATE INDEX IF NOT EXISTS idx_instant_onboarding_profiles_user_id
    ON instant_onboarding_profiles(user_id)
    WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_instant_onboarding_profiles_profile_id
    ON instant_onboarding_profiles(profile_id);

CREATE INDEX IF NOT EXISTS idx_instant_onboarding_profiles_channel
    ON instant_onboarding_profiles(channel);

CREATE INDEX IF NOT EXISTS idx_instant_onboarding_profiles_created_at
    ON instant_onboarding_profiles(created_at DESC);

-- Composite index for analytics
CREATE INDEX IF NOT EXISTS idx_instant_onboarding_profiles_metrics
    ON instant_onboarding_profiles(channel, converted_to_full_user, created_at DESC);

-- Add comments
COMMENT ON TABLE instant_onboarding_profiles IS 'Quick profiles created through instant onboarding';
COMMENT ON COLUMN instant_onboarding_profiles.time_taken_seconds IS 'Time from session start to chart generation';
COMMENT ON COLUMN instant_onboarding_profiles.converted_to_full_user IS 'Whether user created a full account';


-- Step 4: Create Triggers for updated_at
-- =====================================================

-- Trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to instant_onboarding_sessions
DROP TRIGGER IF EXISTS update_instant_onboarding_sessions_updated_at ON instant_onboarding_sessions;
CREATE TRIGGER update_instant_onboarding_sessions_updated_at
    BEFORE UPDATE ON instant_onboarding_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Step 5: Row Level Security (RLS) Policies
-- =====================================================

-- Enable RLS on both tables
ALTER TABLE instant_onboarding_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE instant_onboarding_profiles ENABLE ROW LEVEL SECURITY;

-- Sessions Policies
-- -----------------

-- Allow anonymous users to create sessions (for instant onboarding)
CREATE POLICY "Anyone can create onboarding sessions"
    ON instant_onboarding_sessions
    FOR INSERT
    WITH CHECK (true);

-- Allow anyone to read their own session by session_key (used by API)
CREATE POLICY "Anyone can read session by session_key"
    ON instant_onboarding_sessions
    FOR SELECT
    USING (true);  -- API will filter by session_key

-- Allow users to read their own sessions
CREATE POLICY "Users can read own sessions"
    ON instant_onboarding_sessions
    FOR SELECT
    USING (auth.uid() = user_id);

-- Allow anyone to update session by session_key (used by API during collection)
CREATE POLICY "Anyone can update session by session_key"
    ON instant_onboarding_sessions
    FOR UPDATE
    USING (true);  -- API will filter by session_key

-- Service role has full access (for backend operations)
CREATE POLICY "Service role has full access to sessions"
    ON instant_onboarding_sessions
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Profiles Policies
-- -----------------

-- Allow creation (backend will handle this)
CREATE POLICY "Backend can create onboarding profiles"
    ON instant_onboarding_profiles
    FOR INSERT
    WITH CHECK (true);

-- Users can read their own onboarding profiles
CREATE POLICY "Users can read own onboarding profiles"
    ON instant_onboarding_profiles
    FOR SELECT
    USING (auth.uid() = user_id);

-- Allow reading by profile_id (for analytics)
CREATE POLICY "Anyone can read onboarding profiles by profile_id"
    ON instant_onboarding_profiles
    FOR SELECT
    USING (true);  -- API will filter appropriately

-- Service role has full access
CREATE POLICY "Service role has full access to onboarding profiles"
    ON instant_onboarding_profiles
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');


-- Step 6: Grant Permissions
-- =====================================================

-- Grant usage on types
GRANT USAGE ON TYPE session_status TO anon, authenticated, service_role;
GRANT USAGE ON TYPE onboarding_channel TO anon, authenticated, service_role;

-- Grant table permissions
GRANT ALL ON instant_onboarding_sessions TO service_role;
GRANT SELECT, INSERT, UPDATE ON instant_onboarding_sessions TO authenticated;
GRANT SELECT, INSERT ON instant_onboarding_sessions TO anon;

GRANT ALL ON instant_onboarding_profiles TO service_role;
GRANT SELECT ON instant_onboarding_profiles TO authenticated;
GRANT SELECT ON instant_onboarding_profiles TO anon;


-- Step 7: Helper Views for Analytics
-- =====================================================

-- View for session analytics
CREATE OR REPLACE VIEW instant_onboarding_session_stats AS
SELECT
    channel,
    status,
    language,
    COUNT(*) AS session_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) AS avg_duration_seconds,
    COUNT(*) FILTER (WHERE chart_generated) AS charts_generated,
    DATE_TRUNC('day', created_at) AS date
FROM instant_onboarding_sessions
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY channel, status, language, DATE_TRUNC('day', created_at)
ORDER BY date DESC, channel, status;

COMMENT ON VIEW instant_onboarding_session_stats IS 'Daily statistics for onboarding sessions';

-- View for conversion metrics
CREATE OR REPLACE VIEW instant_onboarding_conversion_metrics AS
SELECT
    channel,
    language,
    COUNT(*) AS total_profiles,
    COUNT(*) FILTER (WHERE viewed_chart) AS viewed_count,
    COUNT(*) FILTER (WHERE shared_chart) AS shared_count,
    COUNT(*) FILTER (WHERE converted_to_full_user) AS converted_count,
    AVG(time_taken_seconds) AS avg_time_seconds,
    ROUND(100.0 * COUNT(*) FILTER (WHERE viewed_chart) / NULLIF(COUNT(*), 0), 2) AS view_rate_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE shared_chart) / NULLIF(COUNT(*), 0), 2) AS share_rate_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE converted_to_full_user) / NULLIF(COUNT(*), 0), 2) AS conversion_rate_pct,
    DATE_TRUNC('day', created_at) AS date
FROM instant_onboarding_profiles
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY channel, language, DATE_TRUNC('day', created_at)
ORDER BY date DESC, channel;

COMMENT ON VIEW instant_onboarding_conversion_metrics IS 'Conversion and engagement metrics for instant onboarding';

-- Grant view permissions
GRANT SELECT ON instant_onboarding_session_stats TO authenticated, service_role;
GRANT SELECT ON instant_onboarding_conversion_metrics TO authenticated, service_role;


-- Step 8: Cleanup Old Sessions (Function)
-- =====================================================

-- Function to clean up expired sessions (older than 7 days and not completed)
CREATE OR REPLACE FUNCTION cleanup_expired_onboarding_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM instant_onboarding_sessions
        WHERE created_at < NOW() - INTERVAL '7 days'
          AND status NOT IN ('completed', 'failed')
        RETURNING *
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION cleanup_expired_onboarding_sessions IS 'Cleans up incomplete sessions older than 7 days';


-- Step 9: Sample Queries for Testing
-- =====================================================

-- Uncomment to test after running migration

/*
-- Check if tables were created
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_name LIKE 'instant_onboarding%';

-- Check enum types
SELECT typname, enumlabel
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
WHERE typname IN ('session_status', 'onboarding_channel')
ORDER BY typname, e.enumsortorder;

-- Check indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename LIKE 'instant_onboarding%'
ORDER BY tablename, indexname;

-- Check RLS policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename LIKE 'instant_onboarding%'
ORDER BY tablename, policyname;

-- Test session creation
INSERT INTO instant_onboarding_sessions (session_key, channel, language)
VALUES ('test_session_' || gen_random_uuid()::text, 'web', 'en')
RETURNING *;

-- View session stats
SELECT * FROM instant_onboarding_session_stats LIMIT 10;

-- View conversion metrics
SELECT * FROM instant_onboarding_conversion_metrics LIMIT 10;
*/


-- =====================================================
-- Migration Complete!
-- =====================================================

-- Summary of what was created:
-- - 2 Enum types (session_status, onboarding_channel)
-- - 2 Tables (instant_onboarding_sessions, instant_onboarding_profiles)
-- - 13 Indexes for query performance
-- - 1 Trigger for automatic updated_at timestamps
-- - 9 RLS Policies for security
-- - 2 Analytics views
-- - 1 Cleanup function
--
-- Next steps:
-- 1. Enable the feature flag: export FEATURE_INSTANT_ONBOARDING=true
-- 2. Restart your backend server
-- 3. Test the API at: http://localhost:8000/api/v2/instant-onboarding/
-- 4. Check API docs at: http://localhost:8000/docs#/Bonus%20Features
--
-- =====================================================

-- Verification query - run this to confirm everything is set up
SELECT
    'Migration Complete!' AS status,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_name LIKE 'instant_onboarding%') AS tables_created,
    (SELECT COUNT(*) FROM pg_indexes WHERE tablename LIKE 'instant_onboarding%') AS indexes_created,
    (SELECT COUNT(*) FROM pg_policies WHERE tablename LIKE 'instant_onboarding%') AS policies_created,
    (SELECT COUNT(*) FROM information_schema.views WHERE table_name LIKE 'instant_onboarding%') AS views_created;
