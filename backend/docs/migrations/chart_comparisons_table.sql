-- Migration: Create chart_comparisons table
-- Date: 2025-01-08
-- Description: Table to store chart comparison results for future reference

CREATE TABLE IF NOT EXISTS chart_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Profile references
    profile_id_1 UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    profile_id_2 UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Comparison type
    comparison_type VARCHAR(50) NOT NULL DEFAULT 'general', -- general, romantic, business, family

    -- Comparison results (stored as JSONB for flexibility)
    comparison_data JSONB NOT NULL,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT different_profiles CHECK (profile_id_1 != profile_id_2)
);

-- Indexes for performance
CREATE INDEX idx_chart_comparisons_user_id ON chart_comparisons(user_id);
CREATE INDEX idx_chart_comparisons_profile_1 ON chart_comparisons(profile_id_1);
CREATE INDEX idx_chart_comparisons_profile_2 ON chart_comparisons(profile_id_2);
CREATE INDEX idx_chart_comparisons_created_at ON chart_comparisons(created_at DESC);
CREATE INDEX idx_chart_comparisons_type ON chart_comparisons(comparison_type);

-- Composite index for finding specific comparisons
CREATE INDEX idx_chart_comparisons_profiles ON chart_comparisons(profile_id_1, profile_id_2);

-- Row Level Security (RLS)
ALTER TABLE chart_comparisons ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view their own comparisons
CREATE POLICY chart_comparisons_select_policy ON chart_comparisons
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can only insert their own comparisons
CREATE POLICY chart_comparisons_insert_policy ON chart_comparisons
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can only update their own comparisons
CREATE POLICY chart_comparisons_update_policy ON chart_comparisons
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Policy: Users can only delete their own comparisons
CREATE POLICY chart_comparisons_delete_policy ON chart_comparisons
    FOR DELETE
    USING (auth.uid() = user_id);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_chart_comparisons_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER chart_comparisons_updated_at_trigger
    BEFORE UPDATE ON chart_comparisons
    FOR EACH ROW
    EXECUTE FUNCTION update_chart_comparisons_updated_at();

-- Comments
COMMENT ON TABLE chart_comparisons IS 'Stores chart comparison results for synastry, composite, and progressed chart analysis';
COMMENT ON COLUMN chart_comparisons.comparison_type IS 'Type of comparison: general, romantic, business, family';
COMMENT ON COLUMN chart_comparisons.comparison_data IS 'Full comparison results including aspects, overlays, compatibility factors, etc.';
