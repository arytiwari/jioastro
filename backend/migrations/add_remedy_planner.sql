-- Migration: Add Remedy Planner feature tables
-- Feature: Track remedies with habit tracking and streaks
-- Author: Claude Code
-- Date: 2024-11-09

-- Remedies Catalog: Master list of Vedic remedies
CREATE TABLE IF NOT EXISTS remedies_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Remedy details
    remedy_name TEXT NOT NULL UNIQUE,
    remedy_type TEXT NOT NULL CHECK (remedy_type IN (
        'mantra', 'gemstone', 'charity', 'fasting', 'puja', 'yantra',
        'color_therapy', 'meditation', 'ritual', 'donation', 'plant',
        'rudraksha', 'lifestyle', 'dietary', 'spiritual_practice'
    )),
    description TEXT NOT NULL,
    detailed_instructions TEXT,

    -- Astrological associations
    planet TEXT CHECK (planet IN ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu')),
    house INTEGER CHECK (house BETWEEN 1 AND 12),
    dosha TEXT CHECK (dosha IN ('Mangal', 'Kaal Sarp', 'Pitra', 'Shrapit')),
    affliction_type TEXT[], -- e.g., ['debilitated_planet', 'malefic_aspect']

    -- Implementation guidance
    frequency TEXT NOT NULL DEFAULT 'daily' CHECK (frequency IN ('daily', 'weekly', 'monthly', 'on_specific_days', 'one_time')),
    best_time TEXT, -- e.g., 'sunrise', 'during_rahukaal', 'on_thursdays'
    duration_days INTEGER, -- Recommended duration (e.g., 40 days for mantra)
    difficulty_level TEXT DEFAULT 'medium' CHECK (difficulty_level IN ('easy', 'medium', 'hard')),

    -- Additional info
    benefits TEXT[],
    precautions TEXT[],
    cost_estimate TEXT, -- e.g., 'free', 'low', 'medium', 'high'
    materials_needed TEXT[],

    -- References
    scripture_reference TEXT,
    source_authority TEXT,

    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Remedy Assignments: Remedies assigned to users
CREATE TABLE IF NOT EXISTS remedy_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    remedy_id UUID NOT NULL REFERENCES remedies_catalog(id) ON DELETE CASCADE,

    -- Assignment details
    assigned_reason TEXT NOT NULL, -- Why this remedy was suggested
    assigned_by TEXT DEFAULT 'ai' CHECK (assigned_by IN ('ai', 'astrologer', 'self')),
    assignment_context JSONB, -- Chart context, dosha info, etc.

    -- Customization
    custom_instructions TEXT,
    target_start_date DATE,
    target_end_date DATE,
    custom_frequency TEXT,

    -- Status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'paused', 'completed', 'abandoned')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    paused_at TIMESTAMP WITH TIME ZONE,

    -- Progress tracking
    total_days_target INTEGER,
    days_completed INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_completed_date DATE,

    -- User notes and reflections
    user_notes TEXT,
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),
    user_feedback TEXT,

    -- Reminders
    reminder_enabled BOOLEAN DEFAULT true,
    reminder_time TIME,
    reminder_days TEXT[], -- e.g., ['monday', 'wednesday', 'friday']

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(user_id, remedy_id, created_at) -- Allow same remedy multiple times but not exact duplicates
);

-- Remedy Tracking: Daily completion tracking
CREATE TABLE IF NOT EXISTS remedy_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES remedy_assignments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Tracking details
    tracking_date DATE NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT false,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Performance notes
    quality_rating INTEGER CHECK (quality_rating BETWEEN 1 AND 5),
    duration_minutes INTEGER,
    notes TEXT,
    mood_before TEXT CHECK (mood_before IN ('poor', 'okay', 'good', 'excellent')),
    mood_after TEXT CHECK (mood_after IN ('poor', 'okay', 'good', 'excellent')),

    -- Context
    location TEXT,
    time_of_day TEXT CHECK (time_of_day IN ('sunrise', 'morning', 'afternoon', 'evening', 'sunset', 'night')),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(assignment_id, tracking_date) -- One entry per day per assignment
);

-- Remedy Achievements: Gamification and milestones
CREATE TABLE IF NOT EXISTS remedy_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    assignment_id UUID REFERENCES remedy_assignments(id) ON DELETE SET NULL,

    -- Achievement details
    achievement_type TEXT NOT NULL CHECK (achievement_type IN (
        'first_completion', 'week_streak', 'month_streak', 'completion_100_days',
        'early_riser', 'consistent_practitioner', 'multiple_remedies', 'perfect_month'
    )),
    achievement_name TEXT NOT NULL,
    achievement_description TEXT,
    achievement_icon TEXT,

    -- Stats
    unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    streak_count INTEGER,

    UNIQUE(user_id, assignment_id, achievement_type)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_remedies_catalog_type ON remedies_catalog(remedy_type);
CREATE INDEX IF NOT EXISTS idx_remedies_catalog_planet ON remedies_catalog(planet);
CREATE INDEX IF NOT EXISTS idx_remedies_catalog_dosha ON remedies_catalog(dosha);

CREATE INDEX IF NOT EXISTS idx_remedy_assignments_user_id ON remedy_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_remedy_assignments_remedy_id ON remedy_assignments(remedy_id);
CREATE INDEX IF NOT EXISTS idx_remedy_assignments_status ON remedy_assignments(status);
CREATE INDEX IF NOT EXISTS idx_remedy_assignments_active ON remedy_assignments(user_id, status) WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_remedy_tracking_assignment_id ON remedy_tracking(assignment_id);
CREATE INDEX IF NOT EXISTS idx_remedy_tracking_user_id ON remedy_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_remedy_tracking_date ON remedy_tracking(tracking_date);
CREATE INDEX IF NOT EXISTS idx_remedy_tracking_completed ON remedy_tracking(assignment_id, completed) WHERE completed = true;

CREATE INDEX IF NOT EXISTS idx_remedy_achievements_user_id ON remedy_achievements(user_id);

-- Row-Level Security Policies

-- Remedies Catalog: Public read, admin write
ALTER TABLE remedies_catalog ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view remedies catalog"
    ON remedies_catalog FOR SELECT
    TO public
    USING (is_active = true);

-- Remedy Assignments: Users can only access their own assignments
ALTER TABLE remedy_assignments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own remedy assignments"
    ON remedy_assignments FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own remedy assignments"
    ON remedy_assignments FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own remedy assignments"
    ON remedy_assignments FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own remedy assignments"
    ON remedy_assignments FOR DELETE
    USING (auth.uid() = user_id);

-- Remedy Tracking: Users can only access their own tracking
ALTER TABLE remedy_tracking ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own remedy tracking"
    ON remedy_tracking FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own remedy tracking"
    ON remedy_tracking FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own remedy tracking"
    ON remedy_tracking FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own remedy tracking"
    ON remedy_tracking FOR DELETE
    USING (auth.uid() = user_id);

-- Remedy Achievements: Users can only access their own achievements
ALTER TABLE remedy_achievements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own achievements"
    ON remedy_achievements FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own achievements"
    ON remedy_achievements FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Functions

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_remedy_tables_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_remedies_catalog_updated_at
    BEFORE UPDATE ON remedies_catalog
    FOR EACH ROW
    EXECUTE FUNCTION update_remedy_tables_updated_at();

CREATE TRIGGER trigger_remedy_assignments_updated_at
    BEFORE UPDATE ON remedy_assignments
    FOR EACH ROW
    EXECUTE FUNCTION update_remedy_tables_updated_at();

CREATE TRIGGER trigger_remedy_tracking_updated_at
    BEFORE UPDATE ON remedy_tracking
    FOR EACH ROW
    EXECUTE FUNCTION update_remedy_tables_updated_at();

-- Calculate and update streak on tracking completion
CREATE OR REPLACE FUNCTION update_remedy_streak()
RETURNS TRIGGER AS $$
DECLARE
    v_yesterday DATE;
    v_was_completed BOOLEAN;
    v_current_streak INTEGER;
    v_longest_streak INTEGER;
BEGIN
    -- Only process when marking as completed
    IF NEW.completed = true AND (OLD.completed IS NULL OR OLD.completed = false) THEN
        v_yesterday := NEW.tracking_date - INTERVAL '1 day';

        -- Check if yesterday was completed
        SELECT completed INTO v_was_completed
        FROM remedy_tracking
        WHERE assignment_id = NEW.assignment_id
        AND tracking_date = v_yesterday;

        -- Get current streak from assignment
        SELECT current_streak, longest_streak INTO v_current_streak, v_longest_streak
        FROM remedy_assignments
        WHERE id = NEW.assignment_id;

        -- Update streak
        IF v_was_completed = true THEN
            v_current_streak := v_current_streak + 1;
        ELSE
            v_current_streak := 1;
        END IF;

        -- Update longest streak if needed
        IF v_current_streak > v_longest_streak THEN
            v_longest_streak := v_current_streak;
        END IF;

        -- Update assignment
        UPDATE remedy_assignments
        SET
            current_streak = v_current_streak,
            longest_streak = v_longest_streak,
            days_completed = days_completed + 1,
            last_completed_date = NEW.tracking_date
        WHERE id = NEW.assignment_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_remedy_streak
    AFTER INSERT OR UPDATE ON remedy_tracking
    FOR EACH ROW
    EXECUTE FUNCTION update_remedy_streak();

-- Comments
COMMENT ON TABLE remedies_catalog IS 'Master catalog of Vedic remedies for various astrological afflictions';
COMMENT ON TABLE remedy_assignments IS 'User-specific remedy assignments with customization and tracking';
COMMENT ON TABLE remedy_tracking IS 'Daily completion tracking for remedies with quality metrics';
COMMENT ON TABLE remedy_achievements IS 'Gamification achievements for remedy completion milestones';
