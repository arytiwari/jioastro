-- Expert Console Database Schema
-- Professional astrologer tools: custom settings, rectification, bulk analysis

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- EXPERT SETTINGS
-- Store user's preferred calculation methods and display options
-- =============================================================================

CREATE TABLE IF NOT EXISTS expert_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Calculation Preferences
    preferred_ayanamsa TEXT DEFAULT 'lahiri' CHECK (preferred_ayanamsa IN (
        'lahiri',           -- Most common (Chitrapaksha)
        'raman',            -- Raman's ayanamsa
        'krishnamurti',     -- KP ayanamsa
        'yukteshwar',       -- Sri Yukteshwar
        'jn_bhasin',        -- JN Bhasin
        'true_citra',       -- True Chitrapaksha
        'true_revati',      -- True Revati
        'true_pushya',      -- True Pushya
        'galactic_center',  -- Modern
        'none'              -- Tropical
    )),

    preferred_house_system TEXT DEFAULT 'placidus' CHECK (preferred_house_system IN (
        'placidus',
        'koch',
        'equal',
        'whole_sign',
        'porphyry',
        'regiomontanus',
        'campanus'
    )),

    -- Display Preferences
    show_seconds BOOLEAN DEFAULT false,
    show_retrograde_symbols BOOLEAN DEFAULT true,
    show_dignity_symbols BOOLEAN DEFAULT true,
    decimal_precision INTEGER DEFAULT 2 CHECK (decimal_precision BETWEEN 0 AND 6),

    -- Advanced Options
    use_true_node BOOLEAN DEFAULT true,  -- True vs Mean Rahu/Ketu
    include_uranus BOOLEAN DEFAULT false, -- Outer planets
    include_neptune BOOLEAN DEFAULT false,
    include_pluto BOOLEAN DEFAULT false,

    -- Divisional Chart Preferences
    default_vargas TEXT[] DEFAULT ARRAY['D1', 'D9']::TEXT[],

    -- Professional Features
    enable_rectification_tools BOOLEAN DEFAULT false,
    enable_bulk_analysis BOOLEAN DEFAULT false,
    enable_custom_exports BOOLEAN DEFAULT false,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(user_id)
);

-- RLS Policies
ALTER TABLE expert_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own expert settings"
ON expert_settings FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own expert settings"
ON expert_settings FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own expert settings"
ON expert_settings FOR UPDATE
USING (auth.uid() = user_id);

-- =============================================================================
-- RECTIFICATION SESSIONS
-- Track birth time rectification attempts and results
-- =============================================================================

CREATE TABLE IF NOT EXISTS rectification_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,

    -- Original Birth Data
    original_name TEXT NOT NULL,
    original_date DATE NOT NULL,
    original_time TIME NOT NULL,
    original_latitude DECIMAL(9, 6) NOT NULL,
    original_longitude DECIMAL(9, 6) NOT NULL,
    original_timezone TEXT NOT NULL,

    -- Rectification Parameters
    time_window_minutes INTEGER DEFAULT 120, -- +/- 2 hours by default
    increment_seconds INTEGER DEFAULT 60, -- Test every minute

    -- Life Events for Verification
    life_events JSONB, -- [{event: "marriage", date: "2015-03-20", expected_dasha: "Venus-Sun"}]

    -- Results
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    tested_times_count INTEGER DEFAULT 0,
    best_match_time TIME,
    best_match_score DECIMAL(5, 2), -- 0-100 confidence score
    results_summary JSONB, -- Detailed results for top matches

    -- Metadata
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE rectification_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own rectification sessions"
ON rectification_sessions FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own rectification sessions"
ON rectification_sessions FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own rectification sessions"
ON rectification_sessions FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own rectification sessions"
ON rectification_sessions FOR DELETE
USING (auth.uid() = user_id);

-- =============================================================================
-- BULK ANALYSIS JOBS
-- Process multiple charts in batches
-- =============================================================================

CREATE TABLE IF NOT EXISTS bulk_analysis_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Job Configuration
    job_name TEXT NOT NULL,
    analysis_type TEXT NOT NULL CHECK (analysis_type IN (
        'chart_generation',
        'dasha_analysis',
        'compatibility_matrix',
        'transit_impact',
        'yoga_detection'
    )),

    -- Input Data
    input_profiles JSONB NOT NULL, -- Array of birth data
    total_profiles INTEGER NOT NULL,

    -- Processing Status
    status TEXT DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    processed_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,

    -- Results
    results_summary JSONB, -- Aggregate statistics
    export_format TEXT DEFAULT 'json' CHECK (export_format IN ('json', 'csv', 'pdf', 'excel')),
    export_url TEXT, -- Cloud storage link if exported

    -- Performance
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_time_seconds INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE bulk_analysis_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own bulk analysis jobs"
ON bulk_analysis_jobs FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own bulk analysis jobs"
ON bulk_analysis_jobs FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own bulk analysis jobs"
ON bulk_analysis_jobs FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own bulk analysis jobs"
ON bulk_analysis_jobs FOR DELETE
USING (auth.uid() = user_id);

-- =============================================================================
-- CUSTOM CALCULATION PRESETS
-- Save and reuse complex calculation configurations
-- =============================================================================

CREATE TABLE IF NOT EXISTS calculation_presets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Preset Details
    preset_name TEXT NOT NULL,
    preset_description TEXT,
    is_public BOOLEAN DEFAULT false, -- Share with other users

    -- Calculation Configuration
    ayanamsa TEXT NOT NULL,
    house_system TEXT NOT NULL,
    calculation_options JSONB NOT NULL, -- {use_true_node, include_outer_planets, etc.}
    varga_selection TEXT[], -- Which divisional charts to include

    -- Usage Tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(user_id, preset_name)
);

-- RLS Policies
ALTER TABLE calculation_presets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own presets and public presets"
ON calculation_presets FOR SELECT
USING (auth.uid() = user_id OR is_public = true);

CREATE POLICY "Users can insert own presets"
ON calculation_presets FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own presets"
ON calculation_presets FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own presets"
ON calculation_presets FOR DELETE
USING (auth.uid() = user_id);

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX idx_expert_settings_user ON expert_settings(user_id);
CREATE INDEX idx_rectification_sessions_user ON rectification_sessions(user_id);
CREATE INDEX idx_rectification_sessions_status ON rectification_sessions(status);
CREATE INDEX idx_bulk_analysis_jobs_user ON bulk_analysis_jobs(user_id);
CREATE INDEX idx_bulk_analysis_jobs_status ON bulk_analysis_jobs(status);
CREATE INDEX idx_calculation_presets_user ON calculation_presets(user_id);
CREATE INDEX idx_calculation_presets_public ON calculation_presets(is_public) WHERE is_public = true;

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_expert_settings_updated_at BEFORE UPDATE ON expert_settings
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rectification_sessions_updated_at BEFORE UPDATE ON rectification_sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bulk_analysis_jobs_updated_at BEFORE UPDATE ON bulk_analysis_jobs
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_calculation_presets_updated_at BEFORE UPDATE ON calculation_presets
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- SAMPLE DATA (Optional - for testing)
-- =============================================================================

-- Insert default expert settings for each user when they first access Expert Console
-- This would typically be done in application code when user enables expert features
