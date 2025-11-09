-- Tarot Reading Feature - Database Migration
-- Creates tables for tarot cards, readings, and spreads

-- =====================================================
-- 1. TAROT CARDS - Master table with all 78 cards
-- =====================================================
CREATE TABLE IF NOT EXISTS tarot_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_number INTEGER NOT NULL UNIQUE,  -- 0-77 (0=Fool, 1-21=Major, 22-77=Minor)
    name TEXT NOT NULL,  -- e.g., "The Fool", "Ace of Cups"
    suit TEXT,  -- major_arcana, cups, pentacles, swords, wands
    arcana_type TEXT NOT NULL CHECK (arcana_type IN ('major', 'minor')),
    upright_meaning TEXT NOT NULL,
    reversed_meaning TEXT NOT NULL,
    upright_keywords JSONB DEFAULT '[]'::jsonb,  -- ["new beginnings", "spontaneity"]
    reversed_keywords JSONB DEFAULT '[]'::jsonb,  -- ["recklessness", "fear"]
    imagery_description TEXT,
    element TEXT,  -- fire, water, air, earth, spirit
    astrological_association TEXT,  -- e.g., "Aries", "Mars"
    numerological_value INTEGER,  -- 0-21 for major, 1-14 for minor
    image_url TEXT,  -- Future: store card images
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tarot_cards_suit ON tarot_cards(suit);
CREATE INDEX IF NOT EXISTS idx_tarot_cards_arcana ON tarot_cards(arcana_type);

COMMENT ON TABLE tarot_cards IS 'Master table containing all 78 tarot cards with their meanings';
COMMENT ON COLUMN tarot_cards.card_number IS 'Unique sequential number 0-77';
COMMENT ON COLUMN tarot_cards.upright_keywords IS 'Array of keywords for upright position';
COMMENT ON COLUMN tarot_cards.reversed_keywords IS 'Array of keywords for reversed position';

-- =====================================================
-- 2. TAROT SPREADS - Predefined spread templates
-- =====================================================
CREATE TABLE IF NOT EXISTS tarot_spreads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,  -- "Celtic Cross", "Three Card Spread"
    description TEXT NOT NULL,
    num_cards INTEGER NOT NULL,  -- Number of cards in this spread
    positions JSONB NOT NULL,  -- [{"position": 1, "name": "Past", "meaning": "What led to this situation"}]
    difficulty_level TEXT DEFAULT 'beginner' CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    category TEXT DEFAULT 'general' CHECK (category IN ('love', 'career', 'spiritual', 'general', 'decision')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tarot_spreads_category ON tarot_spreads(category);
CREATE INDEX IF NOT EXISTS idx_tarot_spreads_difficulty ON tarot_spreads(difficulty_level);

COMMENT ON TABLE tarot_spreads IS 'Predefined tarot spread templates (Celtic Cross, 3-card, etc.)';
COMMENT ON COLUMN tarot_spreads.positions IS 'JSON array defining each card position and its meaning';

-- =====================================================
-- 3. TAROT READINGS - User's tarot readings
-- =====================================================
CREATE TABLE IF NOT EXISTS tarot_readings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,  -- Optional link for holistic analysis
    reading_type TEXT NOT NULL,  -- daily_card, three_card, celtic_cross, custom
    spread_id UUID REFERENCES tarot_spreads(id) ON DELETE SET NULL,
    spread_name TEXT NOT NULL,  -- Store name even if spread deleted
    question TEXT,  -- Optional user question/intention
    cards_drawn JSONB NOT NULL,  -- [{"card_id": "uuid", "position": 1, "is_reversed": false, "card_name": "The Fool"}]
    interpretation TEXT,  -- AI-generated interpretation
    summary TEXT,  -- Brief summary of the reading
    astrology_correlations JSONB,  -- If profile linked: {"sun_sign": "Aries", "correlation": "..."}
    numerology_correlations JSONB,  -- If profile linked: {"life_path": 1, "correlation": "..."}
    confidence_score FLOAT DEFAULT 0.0,  -- AI confidence in interpretation
    is_favorite BOOLEAN DEFAULT false,  -- User can mark favorite readings
    notes TEXT,  -- User's personal notes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tarot_readings_user ON tarot_readings(user_id);
CREATE INDEX IF NOT EXISTS idx_tarot_readings_profile ON tarot_readings(profile_id);
CREATE INDEX IF NOT EXISTS idx_tarot_readings_type ON tarot_readings(reading_type);
CREATE INDEX IF NOT EXISTS idx_tarot_readings_created ON tarot_readings(created_at DESC);

COMMENT ON TABLE tarot_readings IS 'User tarot readings with AI interpretations and profile correlations';
COMMENT ON COLUMN tarot_readings.profile_id IS 'Links reading to birth profile for holistic analysis with astrology/numerology';
COMMENT ON COLUMN tarot_readings.cards_drawn IS 'Array of cards drawn with positions and orientations';
COMMENT ON COLUMN tarot_readings.astrology_correlations IS 'Cross-domain insights correlating cards with birth chart';
COMMENT ON COLUMN tarot_readings.numerology_correlations IS 'Cross-domain insights correlating cards with life path numbers';

-- =====================================================
-- Row Level Security Policies
-- =====================================================

-- Enable RLS on tarot_readings
ALTER TABLE tarot_readings ENABLE ROW LEVEL SECURITY;

-- Users can view their own readings
CREATE POLICY tarot_readings_select_own ON tarot_readings
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own readings
CREATE POLICY tarot_readings_insert_own ON tarot_readings
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own readings
CREATE POLICY tarot_readings_update_own ON tarot_readings
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own readings
CREATE POLICY tarot_readings_delete_own ON tarot_readings
    FOR DELETE
    USING (auth.uid() = user_id);

-- Public read access to tarot_cards and tarot_spreads (reference data)
ALTER TABLE tarot_cards ENABLE ROW LEVEL SECURITY;
CREATE POLICY tarot_cards_public_read ON tarot_cards FOR SELECT USING (true);

ALTER TABLE tarot_spreads ENABLE ROW LEVEL SECURITY;
CREATE POLICY tarot_spreads_public_read ON tarot_spreads FOR SELECT USING (true);

-- =====================================================
-- Insert Default Tarot Spreads
-- =====================================================

INSERT INTO tarot_spreads (name, description, num_cards, positions, difficulty_level, category) VALUES
(
    'Daily Card',
    'A single card drawn to provide guidance for the day ahead',
    1,
    '[{"position": 1, "name": "Daily Card", "meaning": "Energy and guidance for today"}]'::jsonb,
    'beginner',
    'general'
),
(
    'Three Card Spread',
    'Classic three-card spread for past, present, and future insights',
    3,
    '[
        {"position": 1, "name": "Past", "meaning": "What has led to the current situation"},
        {"position": 2, "name": "Present", "meaning": "Current energies and influences"},
        {"position": 3, "name": "Future", "meaning": "Potential outcome and direction"}
    ]'::jsonb,
    'beginner',
    'general'
),
(
    'Mind-Body-Spirit',
    'Three-card spread examining mental, physical, and spiritual aspects',
    3,
    '[
        {"position": 1, "name": "Mind", "meaning": "Mental state and thoughts"},
        {"position": 2, "name": "Body", "meaning": "Physical well-being and health"},
        {"position": 3, "name": "Spirit", "meaning": "Spiritual growth and purpose"}
    ]'::jsonb,
    'beginner',
    'spiritual'
),
(
    'Celtic Cross',
    'The most famous tarot spread, providing comprehensive insight into a situation',
    10,
    '[
        {"position": 1, "name": "Present", "meaning": "Your current situation"},
        {"position": 2, "name": "Challenge", "meaning": "Immediate obstacles or influences"},
        {"position": 3, "name": "Past", "meaning": "Foundation and past influences"},
        {"position": 4, "name": "Future", "meaning": "What is approaching"},
        {"position": 5, "name": "Above", "meaning": "Your goal or best outcome"},
        {"position": 6, "name": "Below", "meaning": "Subconscious influences"},
        {"position": 7, "name": "Advice", "meaning": "Your attitude or approach"},
        {"position": 8, "name": "External", "meaning": "External influences and others"},
        {"position": 9, "name": "Hopes/Fears", "meaning": "Your hopes and fears"},
        {"position": 10, "name": "Outcome", "meaning": "Final outcome and resolution"}
    ]'::jsonb,
    'advanced',
    'general'
),
(
    'Career Path',
    'Five-card spread focused on career and professional development',
    5,
    '[
        {"position": 1, "name": "Current Position", "meaning": "Your current career situation"},
        {"position": 2, "name": "Obstacles", "meaning": "Challenges to overcome"},
        {"position": 3, "name": "Strengths", "meaning": "Your skills and advantages"},
        {"position": 4, "name": "Opportunities", "meaning": "Upcoming possibilities"},
        {"position": 5, "name": "Outcome", "meaning": "Potential career direction"}
    ]'::jsonb,
    'intermediate',
    'career'
),
(
    'Relationship Spread',
    'Seven-card spread exploring relationship dynamics',
    7,
    '[
        {"position": 1, "name": "You", "meaning": "Your position in the relationship"},
        {"position": 2, "name": "Partner", "meaning": "Their position in the relationship"},
        {"position": 3, "name": "Connection", "meaning": "What connects you"},
        {"position": 4, "name": "Conflict", "meaning": "What divides you"},
        {"position": 5, "name": "Past", "meaning": "Past influences on relationship"},
        {"position": 6, "name": "Present", "meaning": "Current state of relationship"},
        {"position": 7, "name": "Future", "meaning": "Potential outcome"}
    ]'::jsonb,
    'intermediate',
    'love'
),
(
    'Decision Making',
    'Five-card spread to help make important decisions',
    5,
    '[
        {"position": 1, "name": "Situation", "meaning": "Current circumstances"},
        {"position": 2, "name": "Option A", "meaning": "First path and its outcome"},
        {"position": 3, "name": "Option B", "meaning": "Second path and its outcome"},
        {"position": 4, "name": "What You Need to Know", "meaning": "Hidden factors"},
        {"position": 5, "name": "Guidance", "meaning": "Best course of action"}
    ]'::jsonb,
    'intermediate',
    'decision'
)
ON CONFLICT (name) DO NOTHING;
