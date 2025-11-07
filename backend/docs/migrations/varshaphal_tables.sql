-- Migration: Add Varshaphal (Annual Predictions) tables
-- Created: 2025-11-07
-- Description: Creates tables for storing annual solar return charts and predictions

-- Create varshaphal_data table
CREATE TABLE IF NOT EXISTS varshaphal_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,  -- Supabase Auth user ID (no foreign key)
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Varshaphal metadata
    target_year INTEGER NOT NULL,
    solar_return_time TIMESTAMP WITH TIME ZONE NOT NULL,
    natal_sun_longitude VARCHAR(50) NOT NULL,

    -- Solar Return Chart data (JSONB for flexibility)
    solar_return_chart JSONB NOT NULL,
    -- Stores: varsha_lagna, muntha, planets, houses, yogas

    -- Patyayini Dasha periods (JSONB)
    patyayini_dasha JSONB NOT NULL,
    -- Stores: Array of dasha periods with planets, dates, effects

    -- Sahams (Sensitive Points) (JSONB)
    sahams JSONB NOT NULL,
    -- Stores: Dictionary of saham names to positions and meanings

    -- Annual Interpretation (JSONB)
    annual_interpretation JSONB NOT NULL,
    -- Stores: overall_quality, year_summary, monthly_predictions,
    --         best_periods, worst_periods, opportunities, challenges, remedies

    -- Cache management
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    cache_key VARCHAR(255) UNIQUE NOT NULL,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance

-- Index on user_id (most common query: get all Varshaphals for user)
CREATE INDEX IF NOT EXISTS idx_varshaphal_user_id ON varshaphal_data(user_id);

-- Index on profile_id (query: get Varshaphals for specific profile)
CREATE INDEX IF NOT EXISTS idx_varshaphal_profile_id ON varshaphal_data(profile_id);

-- Index on target_year (query: get Varshaphal for specific year)
CREATE INDEX IF NOT EXISTS idx_varshaphal_target_year ON varshaphal_data(target_year);

-- Composite index on user_id + target_year (common query pattern)
CREATE INDEX IF NOT EXISTS idx_varshaphal_user_year ON varshaphal_data(user_id, target_year);

-- Composite index on profile_id + target_year (common query pattern)
CREATE INDEX IF NOT EXISTS idx_varshaphal_profile_year ON varshaphal_data(profile_id, target_year);

-- Index on expires_at (for cache cleanup queries)
CREATE INDEX IF NOT EXISTS idx_varshaphal_expires_at ON varshaphal_data(expires_at);

-- Index on cache_key (for deduplication lookups)
CREATE INDEX IF NOT EXISTS idx_varshaphal_cache_key ON varshaphal_data(cache_key);

-- Index on id (for primary key lookups)
CREATE INDEX IF NOT EXISTS idx_varshaphal_id ON varshaphal_data(id);

-- Add updated_at trigger
-- Drop existing trigger if it exists (PostgreSQL doesn't support CREATE TRIGGER IF NOT EXISTS)
DROP TRIGGER IF EXISTS trigger_varshaphal_updated_at ON varshaphal_data;

-- Create trigger function (CREATE OR REPLACE handles if it exists)
CREATE OR REPLACE FUNCTION update_varshaphal_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger (now safe because we dropped it first)
CREATE TRIGGER trigger_varshaphal_updated_at
    BEFORE UPDATE ON varshaphal_data
    FOR EACH ROW
    EXECUTE FUNCTION update_varshaphal_updated_at();

-- Add comments for documentation
COMMENT ON TABLE varshaphal_data IS 'Stores annual predictions (Varshaphal) calculations including solar return charts, Patyayini Dasha, Sahams, and interpretations';
COMMENT ON COLUMN varshaphal_data.target_year IS 'Year for which Varshaphal is calculated (e.g., 2025)';
COMMENT ON COLUMN varshaphal_data.solar_return_time IS 'Exact moment when Sun returns to natal position';
COMMENT ON COLUMN varshaphal_data.natal_sun_longitude IS 'Natal Sun longitude in degrees';
COMMENT ON COLUMN varshaphal_data.solar_return_chart IS 'Complete solar return chart data including Varsha Lagna, Muntha, planets, houses, and Varshaphal Yogas';
COMMENT ON COLUMN varshaphal_data.patyayini_dasha IS 'Annual Patyayini Dasha periods for the year';
COMMENT ON COLUMN varshaphal_data.sahams IS 'Sensitive points (Sahams) like Punya Saham, Vidya Saham, etc.';
COMMENT ON COLUMN varshaphal_data.annual_interpretation IS 'Comprehensive annual interpretation including monthly predictions, best/worst periods, opportunities, challenges, and remedies';
COMMENT ON COLUMN varshaphal_data.cache_key IS 'SHA256 hash for cache deduplication (user_id:profile_id:target_year)';
COMMENT ON COLUMN varshaphal_data.expires_at IS 'Cache expiration time (typically 30 days)';

-- Grant permissions (adjust based on your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON varshaphal_data TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- Verification queries (uncomment to test)
-- SELECT COUNT(*) FROM varshaphal_data;
-- SELECT * FROM varshaphal_data LIMIT 1;
-- SELECT tablename, indexname FROM pg_indexes WHERE tablename = 'varshaphal_data';
