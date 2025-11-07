-- Life Snapshot Feature Migration
-- Creates the life_snapshot_data table for storing snapshot cache

-- Create life_snapshot_data table
CREATE TABLE IF NOT EXISTS life_snapshot_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Snapshot data (themes, risks, opportunities, actions)
    snapshot_data JSONB NOT NULL,

    -- Transit data used for calculation
    transits_data JSONB,

    -- AI-generated insights
    insights JSONB NOT NULL,

    -- Metadata
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    cache_key VARCHAR(255) UNIQUE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_life_snapshot_user_id ON life_snapshot_data(user_id);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_profile_id ON life_snapshot_data(profile_id);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_cache_key ON life_snapshot_data(cache_key);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_generated_at ON life_snapshot_data(generated_at);
CREATE INDEX IF NOT EXISTS idx_life_snapshot_expires_at ON life_snapshot_data(expires_at);

-- Enable Row Level Security
ALTER TABLE life_snapshot_data ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only access their own snapshots
CREATE POLICY "Users can view their own life snapshots"
    ON life_snapshot_data
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own life snapshots"
    ON life_snapshot_data
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own life snapshots"
    ON life_snapshot_data
    FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own life snapshots"
    ON life_snapshot_data
    FOR DELETE
    USING (auth.uid() = user_id);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_life_snapshot_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_life_snapshot_data_updated_at
    BEFORE UPDATE ON life_snapshot_data
    FOR EACH ROW
    EXECUTE FUNCTION update_life_snapshot_updated_at();
