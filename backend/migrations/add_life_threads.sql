-- Migration: Add Life Threads feature tables
-- Feature: Visual timeline of Dasha periods with major life events
-- Author: Claude Code
-- Date: 2024-11-09

-- Life Events table: User-created events mapped to Dasha periods
CREATE TABLE IF NOT EXISTS life_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Event details
    event_type TEXT NOT NULL CHECK (event_type IN (
        'career', 'education', 'relationship', 'marriage', 'childbirth',
        'health', 'relocation', 'financial', 'spiritual', 'achievement',
        'loss', 'travel', 'property', 'family', 'other'
    )),
    event_name TEXT NOT NULL,
    event_date DATE NOT NULL,
    event_description TEXT,
    event_impact TEXT CHECK (event_impact IN ('positive', 'negative', 'neutral', 'mixed')),

    -- Astrological context (calculated at time of event)
    dasha_period JSONB, -- { "mahadasha": "Venus", "antardasha": "Sun", "pratyantardasha": "Moon" }
    transit_context JSONB, -- Major transits at event time

    -- User annotations
    tags TEXT[], -- Custom tags for filtering
    is_milestone BOOLEAN DEFAULT false, -- Mark important events
    privacy_level TEXT DEFAULT 'private' CHECK (privacy_level IN ('private', 'shared', 'public')),

    -- AI insights (optional)
    astrological_significance TEXT, -- AI-generated correlation with chart

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes for performance
    CONSTRAINT valid_event_date CHECK (event_date >= '1900-01-01' AND event_date <= CURRENT_DATE + INTERVAL '10 years')
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_life_events_user_id ON life_events(user_id);
CREATE INDEX IF NOT EXISTS idx_life_events_profile_id ON life_events(profile_id);
CREATE INDEX IF NOT EXISTS idx_life_events_event_date ON life_events(event_date);
CREATE INDEX IF NOT EXISTS idx_life_events_event_type ON life_events(event_type);
CREATE INDEX IF NOT EXISTS idx_life_events_is_milestone ON life_events(is_milestone) WHERE is_milestone = true;

-- Dasha Timeline Cache (for performance)
CREATE TABLE IF NOT EXISTS dasha_timeline_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

    -- Timeline data
    timeline_data JSONB NOT NULL, -- Full Vimshottari Dasha timeline
    major_periods JSONB NOT NULL, -- Simplified view of Mahadasha periods

    -- Metadata
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '30 days',

    UNIQUE(profile_id)
);

CREATE INDEX IF NOT EXISTS idx_dasha_timeline_cache_profile_id ON dasha_timeline_cache(profile_id);
CREATE INDEX IF NOT EXISTS idx_dasha_timeline_cache_expires_at ON dasha_timeline_cache(expires_at);

-- Row-Level Security Policies

-- Life Events: Users can only access their own events
ALTER TABLE life_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own life events"
    ON life_events FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own life events"
    ON life_events FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own life events"
    ON life_events FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own life events"
    ON life_events FOR DELETE
    USING (auth.uid() = user_id);

-- Dasha Timeline Cache: Users can only access their own cached data
ALTER TABLE dasha_timeline_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own dasha timeline cache"
    ON dasha_timeline_cache FOR SELECT
    USING (
        profile_id IN (
            SELECT id FROM profiles WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage their own dasha timeline cache"
    ON dasha_timeline_cache FOR ALL
    USING (
        profile_id IN (
            SELECT id FROM profiles WHERE user_id = auth.uid()
        )
    )
    WITH CHECK (
        profile_id IN (
            SELECT id FROM profiles WHERE user_id = auth.uid()
        )
    );

-- Function: Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_life_events_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_life_events_updated_at
    BEFORE UPDATE ON life_events
    FOR EACH ROW
    EXECUTE FUNCTION update_life_events_updated_at();

-- Function: Get current Dasha period for a date
CREATE OR REPLACE FUNCTION get_dasha_for_date(
    p_profile_id UUID,
    p_date DATE
) RETURNS JSONB AS $$
DECLARE
    v_timeline JSONB;
    v_period JSONB;
BEGIN
    -- Get cached timeline
    SELECT timeline_data INTO v_timeline
    FROM dasha_timeline_cache
    WHERE profile_id = p_profile_id
    AND expires_at > NOW();

    IF v_timeline IS NULL THEN
        RETURN NULL;
    END IF;

    -- Find matching period (simplified - actual implementation would iterate through periods)
    -- This is a placeholder - actual Dasha calculation happens in backend service
    RETURN jsonb_build_object(
        'mahadasha', 'Venus',
        'antardasha', 'Sun',
        'pratyantardasha', 'Moon'
    );
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON TABLE life_events IS 'User life events mapped to astrological Dasha periods for timeline visualization';
COMMENT ON TABLE dasha_timeline_cache IS 'Cached Vimshottari Dasha timeline calculations for performance';
COMMENT ON COLUMN life_events.dasha_period IS 'Dasha period active at the time of the event (Mahadasha/Antardasha/Pratyantardasha)';
COMMENT ON COLUMN life_events.astrological_significance IS 'AI-generated analysis of how this event correlates with birth chart and transits';
