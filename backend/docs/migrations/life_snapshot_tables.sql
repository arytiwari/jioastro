-- Migration: Add Life Snapshot tables
-- Feature: Life Snapshot (Magical 12 Feature #1)
-- Date: 2025-11-07

-- Create life_snapshot_data table
CREATE TABLE IF NOT EXISTS life_snapshot_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    profile_id UUID NOT NULL,

    -- Snapshot data
    snapshot_data JSONB NOT NULL,
    transits_data JSONB,
    insights JSONB NOT NULL,

    -- Metadata
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    cache_key VARCHAR(255) UNIQUE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Foreign keys (if users table exists)
    -- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_life_snapshot_user_id ON life_snapshot_data(user_id);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_profile_id ON life_snapshot_data(profile_id);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_cache_key ON life_snapshot_data(cache_key);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_generated_at ON life_snapshot_data(generated_at);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_expires_at ON life_snapshot_data(expires_at);

-- Create composite index for cache lookups
CREATE INDEX IF NOT EXISTS idx_life_snapshot_cache_lookup
ON life_snapshot_data(user_id, profile_id, expires_at);

-- Add comments
COMMENT ON TABLE life_snapshot_data IS 'Life Snapshot data - 60-second personalized life insights';
COMMENT ON COLUMN life_snapshot_data.snapshot_data IS 'Complete snapshot data including themes, risks, opportunities';
COMMENT ON COLUMN life_snapshot_data.insights IS 'Structured insights for API response';
COMMENT ON COLUMN life_snapshot_data.cache_key IS 'SHA256 hash for deduplication';
COMMENT ON COLUMN life_snapshot_data.expires_at IS 'Cache expiration timestamp';

-- Enable row-level security (if using Supabase)
-- ALTER TABLE life_snapshot_data ENABLE ROW LEVEL SECURITY;

-- Create policy for users to access only their own snapshots
-- CREATE POLICY "Users can view their own snapshots"
-- ON life_snapshot_data FOR SELECT
-- USING (auth.uid() = user_id);

-- CREATE POLICY "Users can create their own snapshots"
-- ON life_snapshot_data FOR INSERT
-- WITH CHECK (auth.uid() = user_id);
