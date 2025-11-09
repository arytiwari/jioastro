-- Feng Shui Integration Feature - Database Migration
-- Creates tables for feng shui analyses and recommendations

-- =====================================================
-- 1. FENG SHUI ANALYSES - User's feng shui consultations
-- =====================================================
CREATE TABLE IF NOT EXISTS feng_shui_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,  -- Required for birth-based Kua calculation

    -- Kua Number and Element (calculated from birth date and gender)
    kua_number INTEGER NOT NULL CHECK (kua_number BETWEEN 1 AND 9),
    personal_element TEXT NOT NULL CHECK (personal_element IN ('wood', 'fire', 'earth', 'metal', 'water')),
    life_gua_group TEXT NOT NULL CHECK (life_gua_group IN ('east', 'west')),  -- East or West life group

    -- Favorable Directions (based on Kua number)
    favorable_directions JSONB NOT NULL,  -- {"sheng_qi": "SE", "tian_yi": "E", "yan_nian": "S", "fu_wei": "N"}
    unfavorable_directions JSONB NOT NULL,  -- {"huo_hai": "W", "wu_gui": "NW", "liu_sha": "SW", "jue_ming": "NE"}
    direction_meanings JSONB,  -- Meanings of each direction type

    -- Color and Element Recommendations
    lucky_colors JSONB NOT NULL,  -- ["green", "brown", "blue"]
    unlucky_colors JSONB NOT NULL,  -- ["white", "gold", "gray"]
    supporting_elements JSONB,  -- ["water", "wood"] - elements that support personal element
    weakening_elements JSONB,  -- ["metal"] - elements that weaken personal element

    -- Space Information
    space_type TEXT,  -- home, office, bedroom, living_room, etc.
    space_orientation TEXT,  -- N, NE, E, SE, S, SW, W, NW (facing direction)
    space_layout JSONB,  -- {"rooms": [...], "main_entrance": "N", "bedroom": "E"}

    -- Analysis Results
    analysis_summary TEXT,  -- AI-generated summary
    compatibility_score FLOAT DEFAULT 0.0,  -- How well space aligns with Kua (0-100)

    -- Astrological Correlations (from birth chart)
    birth_element TEXT,  -- Element from astrology chart
    planetary_influences JSONB,  -- Planets affecting directions
    astrology_feng_shui_harmony TEXT,  -- How astrology and feng shui align

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feng_shui_analyses_user ON feng_shui_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_feng_shui_analyses_profile ON feng_shui_analyses(profile_id);
CREATE INDEX IF NOT EXISTS idx_feng_shui_analyses_kua ON feng_shui_analyses(kua_number);
CREATE INDEX IF NOT EXISTS idx_feng_shui_analyses_created ON feng_shui_analyses(created_at DESC);

COMMENT ON TABLE feng_shui_analyses IS 'Feng Shui analyses based on user birth profile and Kua number calculations';
COMMENT ON COLUMN feng_shui_analyses.profile_id IS 'Required - birth profile used to calculate Kua number and correlate with astrology';
COMMENT ON COLUMN feng_shui_analyses.kua_number IS 'Kua number (1-9) calculated from birth year and gender';
COMMENT ON COLUMN feng_shui_analyses.favorable_directions IS 'Four favorable directions: Sheng Qi (wealth), Tian Yi (health), Yan Nian (relationships), Fu Wei (personal growth)';
COMMENT ON COLUMN feng_shui_analyses.unfavorable_directions IS 'Four unfavorable directions to avoid';

-- =====================================================
-- 2. FENG SHUI RECOMMENDATIONS - Specific actionable recommendations
-- =====================================================
CREATE TABLE IF NOT EXISTS feng_shui_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES feng_shui_analyses(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,

    -- Recommendation Details
    category TEXT NOT NULL CHECK (category IN ('colors', 'directions', 'elements', 'placement', 'remedies', 'enhancements')),
    area TEXT,  -- bedroom, office, entrance, desk, bed, etc.
    title TEXT NOT NULL,  -- "Position Desk in Wealth Direction"
    recommendation TEXT NOT NULL,  -- Detailed recommendation
    reason TEXT,  -- Why this helps based on Kua/chart

    -- Priority and Implementation
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low')),
    impact_score FLOAT DEFAULT 0.0,  -- Expected impact (0-10)
    difficulty TEXT DEFAULT 'easy' CHECK (difficulty IN ('easy', 'moderate', 'difficult')),

    -- Cross-Domain Correlations
    astrology_correlation TEXT,  -- How it relates to birth chart
    numerology_correlation TEXT,  -- How it relates to life path numbers

    -- User Tracking
    is_implemented BOOLEAN DEFAULT false,
    implemented_at TIMESTAMP WITH TIME ZONE,
    user_notes TEXT,
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feng_shui_recommendations_analysis ON feng_shui_recommendations(analysis_id);
CREATE INDEX IF NOT EXISTS idx_feng_shui_recommendations_user ON feng_shui_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_feng_shui_recommendations_category ON feng_shui_recommendations(category);
CREATE INDEX IF NOT EXISTS idx_feng_shui_recommendations_priority ON feng_shui_recommendations(priority);

COMMENT ON TABLE feng_shui_recommendations IS 'Specific feng shui recommendations based on Kua analysis';
COMMENT ON COLUMN feng_shui_recommendations.astrology_correlation IS 'Cross-domain insight correlating feng shui with birth chart planets/houses';
COMMENT ON COLUMN feng_shui_recommendations.numerology_correlation IS 'Cross-domain insight correlating feng shui with life path/destiny numbers';
COMMENT ON COLUMN feng_shui_recommendations.is_implemented IS 'User can track which recommendations they have implemented';

-- =====================================================
-- Row Level Security Policies
-- =====================================================

-- Enable RLS on feng_shui_analyses
ALTER TABLE feng_shui_analyses ENABLE ROW LEVEL SECURITY;

-- Users can view their own analyses
CREATE POLICY feng_shui_analyses_select_own ON feng_shui_analyses
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own analyses
CREATE POLICY feng_shui_analyses_insert_own ON feng_shui_analyses
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own analyses
CREATE POLICY feng_shui_analyses_update_own ON feng_shui_analyses
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own analyses
CREATE POLICY feng_shui_analyses_delete_own ON feng_shui_analyses
    FOR DELETE
    USING (auth.uid() = user_id);

-- Enable RLS on feng_shui_recommendations
ALTER TABLE feng_shui_recommendations ENABLE ROW LEVEL SECURITY;

-- Users can view their own recommendations
CREATE POLICY feng_shui_recommendations_select_own ON feng_shui_recommendations
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own recommendations
CREATE POLICY feng_shui_recommendations_insert_own ON feng_shui_recommendations
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own recommendations
CREATE POLICY feng_shui_recommendations_update_own ON feng_shui_recommendations
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own recommendations
CREATE POLICY feng_shui_recommendations_delete_own ON feng_shui_recommendations
    FOR DELETE
    USING (auth.uid() = user_id);

-- =====================================================
-- Helper Function: Calculate Kua Number
-- =====================================================
-- This function can be called from the application to calculate Kua number
-- based on birth year and gender

CREATE OR REPLACE FUNCTION calculate_kua_number(
    birth_year INTEGER,
    gender TEXT  -- 'male' or 'female'
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    year_digits INTEGER;
    sum_digits INTEGER;
    kua INTEGER;
BEGIN
    -- Use last 2 digits of birth year
    year_digits := birth_year % 100;

    -- Sum the digits
    sum_digits := (year_digits / 10) + (year_digits % 10);

    -- If sum is >= 10, sum again
    IF sum_digits >= 10 THEN
        sum_digits := (sum_digits / 10) + (sum_digits % 10);
    END IF;

    -- Calculate Kua based on gender
    IF gender = 'male' THEN
        kua := 10 - sum_digits;
        -- Kua 5 doesn't exist for males, becomes 2
        IF kua = 5 THEN
            kua := 2;
        END IF;
    ELSE  -- female
        kua := 5 + sum_digits;
        IF kua >= 10 THEN
            kua := kua - 9;
        END IF;
        -- Kua 5 doesn't exist for females, becomes 8
        IF kua = 5 THEN
            kua := 8;
        END IF;
    END IF;

    RETURN kua;
END;
$$;

COMMENT ON FUNCTION calculate_kua_number IS 'Calculates Kua number (1-9) from birth year and gender using traditional feng shui formula';

-- =====================================================
-- Example Usage:
-- =====================================================
-- SELECT calculate_kua_number(1990, 'male');  -- Returns Kua number for male born in 1990
-- SELECT calculate_kua_number(1985, 'female');  -- Returns Kua number for female born in 1985
