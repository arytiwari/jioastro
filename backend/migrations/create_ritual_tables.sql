-- ============================================================================
-- Guided Rituals Feature - Database Migration
-- Created: 2025-01-09
-- ============================================================================

-- Drop existing tables if they exist (for clean migration)
DROP TABLE IF EXISTS user_ritual_sessions CASCADE;
DROP TABLE IF EXISTS ritual_templates CASCADE;

-- ============================================================================
-- RITUAL TEMPLATES TABLE
-- Stores pre-defined ritual templates with steps and instructions
-- ============================================================================

CREATE TABLE ritual_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('daily', 'special', 'remedial', 'festival', 'meditation')),
    deity TEXT,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    difficulty TEXT NOT NULL CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    description TEXT,
    required_items JSONB DEFAULT '[]'::jsonb,
    steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    audio_enabled BOOLEAN DEFAULT false,
    benefits TEXT[],
    best_time_of_day TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER RITUAL SESSIONS TABLE
-- Tracks user's ritual practice sessions and progress
-- ============================================================================

CREATE TABLE user_ritual_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    ritual_template_id UUID NOT NULL REFERENCES ritual_templates(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    current_step INTEGER DEFAULT 1 CHECK (current_step > 0),
    total_steps INTEGER NOT NULL CHECK (total_steps > 0),
    status TEXT DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed', 'paused', 'abandoned')),
    notes TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Foreign key to auth.users for user profile linkage
    CONSTRAINT user_ritual_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Ritual templates indexes
CREATE INDEX idx_ritual_templates_category ON ritual_templates(category);
CREATE INDEX idx_ritual_templates_deity ON ritual_templates(deity);
CREATE INDEX idx_ritual_templates_difficulty ON ritual_templates(difficulty);

-- User ritual sessions indexes
CREATE INDEX idx_user_ritual_sessions_user_id ON user_ritual_sessions(user_id);
CREATE INDEX idx_user_ritual_sessions_ritual_id ON user_ritual_sessions(ritual_template_id);
CREATE INDEX idx_user_ritual_sessions_status ON user_ritual_sessions(status);
CREATE INDEX idx_user_ritual_sessions_completed_at ON user_ritual_sessions(completed_at);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on user_ritual_sessions
ALTER TABLE user_ritual_sessions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view only their own ritual sessions
CREATE POLICY "Users can view own ritual sessions"
    ON user_ritual_sessions FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can create their own ritual sessions
CREATE POLICY "Users can create own ritual sessions"
    ON user_ritual_sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update only their own ritual sessions
CREATE POLICY "Users can update own ritual sessions"
    ON user_ritual_sessions FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete only their own ritual sessions
CREATE POLICY "Users can delete own ritual sessions"
    ON user_ritual_sessions FOR DELETE
    USING (auth.uid() = user_id);

-- Enable RLS on ritual_templates (public read-only)
ALTER TABLE ritual_templates ENABLE ROW LEVEL SECURITY;

-- Policy: All authenticated users can view ritual templates
CREATE POLICY "Anyone can view ritual templates"
    ON ritual_templates FOR SELECT
    TO authenticated
    USING (true);

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant permissions on user_ritual_sessions
GRANT ALL ON user_ritual_sessions TO authenticated;
GRANT ALL ON user_ritual_sessions TO service_role;

-- Grant permissions on ritual_templates (read-only for users)
GRANT SELECT ON ritual_templates TO authenticated;
GRANT ALL ON ritual_templates TO service_role;

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for ritual_templates
CREATE TRIGGER update_ritual_templates_updated_at
    BEFORE UPDATE ON ritual_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for user_ritual_sessions
CREATE TRIGGER update_user_ritual_sessions_updated_at
    BEFORE UPDATE ON user_ritual_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE ritual_templates IS 'Pre-defined Vedic ritual templates with step-by-step instructions';
COMMENT ON TABLE user_ritual_sessions IS 'User ritual practice sessions with progress tracking (linked to auth.users)';

COMMENT ON COLUMN ritual_templates.steps IS 'Array of step objects with title, description, mantra, duration, visual_aid_url, etc.';
COMMENT ON COLUMN ritual_templates.required_items IS 'Array of required materials for the ritual';
COMMENT ON COLUMN user_ritual_sessions.user_id IS 'Foreign key to auth.users - ensures sessions are tied to user profile';
COMMENT ON COLUMN user_ritual_sessions.current_step IS 'Current step number user is on (1-indexed)';
COMMENT ON COLUMN user_ritual_sessions.rating IS 'User rating after completing ritual (1-5 stars)';

-- ============================================================================
-- SAMPLE STEP OBJECT STRUCTURE (for reference)
-- ============================================================================
/*
{
  "step_number": 1,
  "title": "Purification (Achamana)",
  "description": "Sip water three times while chanting mantras for purification",
  "mantra": "Om Keshavaya Namaha, Om Narayanaya Namaha, Om Madhavaya Namaha",
  "mantra_transliteration": "Om Keshavaaya Namaha, Om Naaraayanaaya Namaha, Om Maadhavaaya Namaha",
  "mantra_translation": "Salutations to Lord Keshava, Narayana, and Madhava",
  "duration_seconds": 60,
  "visual_aid_url": "/images/rituals/achamana.jpg",
  "audio_instruction_url": "/audio/rituals/achamana_en.mp3",
  "required_items": ["water", "spoon"],
  "tips": ["Sit facing East", "Use clean water", "Keep spine straight"]
}
*/

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
