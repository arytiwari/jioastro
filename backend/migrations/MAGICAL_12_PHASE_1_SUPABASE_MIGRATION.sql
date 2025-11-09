-- ============================================================================
-- MAGICAL 12 PHASE 1 - COMPREHENSIVE SUPABASE MIGRATION
-- ============================================================================
-- Features: Life Threads (#2), Remedy Planner (#5), Hyperlocal Panchang (#11)
-- Author: Claude Code
-- Date: November 9, 2025
--
-- INSTRUCTIONS:
-- 1. Open Supabase SQL Editor (https://app.supabase.com/project/YOUR_PROJECT/sql)
-- 2. Copy and paste this ENTIRE file
-- 3. Click "Run" to execute all migrations
-- 4. Verify completion by checking the "Tables" section
--
-- This script is idempotent - safe to run multiple times
-- ============================================================================


-- ============================================================================
-- FEATURE #2: LIFE THREADS - Zoomable Life Journey Timeline
-- ============================================================================

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

-- Row-Level Security Policies for Life Events
ALTER TABLE life_events ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own life events" ON life_events;
CREATE POLICY "Users can view their own life events"
    ON life_events FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert their own life events" ON life_events;
CREATE POLICY "Users can insert their own life events"
    ON life_events FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own life events" ON life_events;
CREATE POLICY "Users can update their own life events"
    ON life_events FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own life events" ON life_events;
CREATE POLICY "Users can delete their own life events"
    ON life_events FOR DELETE
    USING (auth.uid() = user_id);

-- Dasha Timeline Cache: Users can only access their own cached data
ALTER TABLE dasha_timeline_cache ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own dasha timeline cache" ON dasha_timeline_cache;
CREATE POLICY "Users can view their own dasha timeline cache"
    ON dasha_timeline_cache FOR SELECT
    USING (
        profile_id IN (
            SELECT id FROM profiles WHERE user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can manage their own dasha timeline cache" ON dasha_timeline_cache;
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

DROP TRIGGER IF EXISTS trigger_life_events_updated_at ON life_events;
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


-- ============================================================================
-- FEATURE #5: REMEDY PLANNER - Actionable Vedic Remedies with Tracking
-- ============================================================================

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

DROP POLICY IF EXISTS "Anyone can view remedies catalog" ON remedies_catalog;
CREATE POLICY "Anyone can view remedies catalog"
    ON remedies_catalog FOR SELECT
    TO public
    USING (is_active = true);

-- Remedy Assignments: Users can only access their own assignments
ALTER TABLE remedy_assignments ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own remedy assignments" ON remedy_assignments;
CREATE POLICY "Users can view their own remedy assignments"
    ON remedy_assignments FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create their own remedy assignments" ON remedy_assignments;
CREATE POLICY "Users can create their own remedy assignments"
    ON remedy_assignments FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own remedy assignments" ON remedy_assignments;
CREATE POLICY "Users can update their own remedy assignments"
    ON remedy_assignments FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own remedy assignments" ON remedy_assignments;
CREATE POLICY "Users can delete their own remedy assignments"
    ON remedy_assignments FOR DELETE
    USING (auth.uid() = user_id);

-- Remedy Tracking: Users can only access their own tracking
ALTER TABLE remedy_tracking ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own remedy tracking" ON remedy_tracking;
CREATE POLICY "Users can view their own remedy tracking"
    ON remedy_tracking FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create their own remedy tracking" ON remedy_tracking;
CREATE POLICY "Users can create their own remedy tracking"
    ON remedy_tracking FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own remedy tracking" ON remedy_tracking;
CREATE POLICY "Users can update their own remedy tracking"
    ON remedy_tracking FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own remedy tracking" ON remedy_tracking;
CREATE POLICY "Users can delete their own remedy tracking"
    ON remedy_tracking FOR DELETE
    USING (auth.uid() = user_id);

-- Remedy Achievements: Users can only access their own achievements
ALTER TABLE remedy_achievements ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own achievements" ON remedy_achievements;
CREATE POLICY "Users can view their own achievements"
    ON remedy_achievements FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage their own achievements" ON remedy_achievements;
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

DROP TRIGGER IF EXISTS trigger_remedies_catalog_updated_at ON remedies_catalog;
CREATE TRIGGER trigger_remedies_catalog_updated_at
    BEFORE UPDATE ON remedies_catalog
    FOR EACH ROW
    EXECUTE FUNCTION update_remedy_tables_updated_at();

DROP TRIGGER IF EXISTS trigger_remedy_assignments_updated_at ON remedy_assignments;
CREATE TRIGGER trigger_remedy_assignments_updated_at
    BEFORE UPDATE ON remedy_assignments
    FOR EACH ROW
    EXECUTE FUNCTION update_remedy_tables_updated_at();

DROP TRIGGER IF EXISTS trigger_remedy_tracking_updated_at ON remedy_tracking;
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

DROP TRIGGER IF EXISTS trigger_update_remedy_streak ON remedy_tracking;
CREATE TRIGGER trigger_update_remedy_streak
    AFTER INSERT OR UPDATE ON remedy_tracking
    FOR EACH ROW
    EXECUTE FUNCTION update_remedy_streak();

-- Comments
COMMENT ON TABLE remedies_catalog IS 'Master catalog of Vedic remedies for various astrological afflictions';
COMMENT ON TABLE remedy_assignments IS 'User-specific remedy assignments with customization and tracking';
COMMENT ON TABLE remedy_tracking IS 'Daily completion tracking for remedies with quality metrics';
COMMENT ON TABLE remedy_achievements IS 'Gamification achievements for remedy completion milestones';


-- ============================================================================
-- FEATURE #11: HYPERLOCAL PANCHANG - Location-Based Daily Vedic Calendar
-- ============================================================================

-- Panchang Cache: Cached daily panchang calculations per location
CREATE TABLE IF NOT EXISTS panchang_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Date and location
    panchang_date DATE NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    timezone TEXT NOT NULL,
    location_name TEXT,

    -- Panchang Elements (Panchangam)

    -- Tithi (Lunar Day) - 30 Tithis in lunar month
    tithi_name TEXT NOT NULL,
    tithi_number INTEGER CHECK (tithi_number BETWEEN 1 AND 30),
    tithi_paksha TEXT CHECK (tithi_paksha IN ('Shukla', 'Krishna')), -- Waxing/Waning
    tithi_start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    tithi_end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    tithi_deity TEXT,
    tithi_quality TEXT, -- Auspicious, Neutral, Inauspicious

    -- Nakshatra (Lunar Mansion) - 27 Nakshatras
    nakshatra_name TEXT NOT NULL,
    nakshatra_number INTEGER CHECK (nakshatra_number BETWEEN 1 AND 27),
    nakshatra_start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    nakshatra_end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    nakshatra_pada INTEGER CHECK (nakshatra_pada BETWEEN 1 AND 4),
    nakshatra_deity TEXT,
    nakshatra_lord TEXT, -- Ruling planet
    nakshatra_quality TEXT,

    -- Yoga - 27 Yogas (combination of Sun and Moon)
    yoga_name TEXT NOT NULL,
    yoga_number INTEGER CHECK (yoga_number BETWEEN 1 AND 27),
    yoga_start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    yoga_end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    yoga_quality TEXT,

    -- Karana - 11 Karanas (half of Tithi)
    karana_name TEXT NOT NULL,
    karana_number INTEGER CHECK (karana_number BETWEEN 1 AND 11),
    karana_quality TEXT,

    -- Vara (Weekday) - Ruled by planets
    vara_name TEXT NOT NULL CHECK (vara_name IN ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')),
    vara_lord TEXT NOT NULL, -- Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn

    -- Paksha (Lunar Fortnight)
    paksha TEXT CHECK (paksha IN ('Shukla', 'Krishna')),

    -- Ritu (Season) - 6 Ritus in Vedic calendar
    ritu TEXT CHECK (ritu IN ('Vasanta', 'Grishma', 'Varsha', 'Sharad', 'Hemanta', 'Shishira')),

    -- Masa (Lunar Month)
    masa_name TEXT,

    -- Sun and Moon data
    sunrise TIMESTAMP WITH TIME ZONE NOT NULL,
    sunset TIMESTAMP WITH TIME ZONE NOT NULL,
    moonrise TIMESTAMP WITH TIME ZONE,
    moonset TIMESTAMP WITH TIME ZONE,

    -- Lunar phase
    moon_phase TEXT CHECK (moon_phase IN ('New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous', 'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent')),
    moon_illumination DECIMAL(5, 2), -- Percentage

    -- Inauspicious times (to avoid)
    rahukaal_start TIME NOT NULL,
    rahukaal_end TIME NOT NULL,
    yamaghanta_start TIME,
    yamaghanta_end TIME,
    gulika_kaal_start TIME,
    gulika_kaal_end TIME,
    dur_muhurtam JSONB, -- Array of inauspicious periods

    -- Auspicious times
    abhijit_muhurta_start TIME,
    abhijit_muhurta_end TIME,
    brahma_muhurta_start TIME,
    brahma_muhurta_end TIME,

    -- Daily Hora (planetary hours)
    hora_sequence JSONB NOT NULL, -- Array of 24 horas with start/end times

    -- Special days and festivals
    is_festival BOOLEAN DEFAULT false,
    festival_name TEXT,
    festival_significance TEXT,
    is_ekadashi BOOLEAN DEFAULT false,
    is_amavasya BOOLEAN DEFAULT false,
    is_purnima BOOLEAN DEFAULT false,

    -- Panchaka (5 inauspicious Nakshatras)
    is_panchaka BOOLEAN DEFAULT false,

    -- Bhadra (inauspicious period)
    bhadra_periods JSONB,

    -- Personalized guidance (AI-generated based on user's chart)
    daily_guidance TEXT,
    favorable_activities TEXT[],
    unfavorable_activities TEXT[],

    -- Metadata
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    calculation_version TEXT DEFAULT '1.0',

    -- Unique constraint: One entry per date per location
    UNIQUE(panchang_date, latitude, longitude)
);

-- User Panchang Subscriptions: Track user locations for daily panchang
CREATE TABLE IF NOT EXISTS panchang_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Location details
    location_name TEXT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    timezone TEXT NOT NULL,
    country TEXT,
    state TEXT,
    city TEXT,

    -- Preferences
    is_primary BOOLEAN DEFAULT false,
    notification_enabled BOOLEAN DEFAULT true,
    notification_time TIME DEFAULT '06:00:00',

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(user_id, location_name)
);

-- Panchang Preferences: User preferences for Panchang display
CREATE TABLE IF NOT EXISTS panchang_preferences (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Display preferences
    show_tithi BOOLEAN DEFAULT true,
    show_nakshatra BOOLEAN DEFAULT true,
    show_yoga BOOLEAN DEFAULT true,
    show_karana BOOLEAN DEFAULT true,
    show_rahukaal BOOLEAN DEFAULT true,
    show_hora BOOLEAN DEFAULT true,
    show_festivals BOOLEAN DEFAULT true,

    -- Notification preferences
    notify_on_ekadashi BOOLEAN DEFAULT false,
    notify_on_amavasya BOOLEAN DEFAULT false,
    notify_on_purnima BOOLEAN DEFAULT false,
    notify_on_festivals BOOLEAN DEFAULT true,
    notify_before_rahukaal BOOLEAN DEFAULT false,

    -- Calendar integration
    calendar_sync_enabled BOOLEAN DEFAULT false,
    calendar_provider TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Daily Guidance Log: Personalized daily guidance based on chart + panchang
CREATE TABLE IF NOT EXISTS daily_guidance_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    panchang_id UUID REFERENCES panchang_cache(id) ON DELETE SET NULL,

    -- Guidance date
    guidance_date DATE NOT NULL,

    -- Personalized guidance (combines chart + panchang + transits)
    overall_day_quality TEXT CHECK (overall_day_quality IN ('excellent', 'good', 'average', 'challenging', 'difficult')),
    overall_guidance TEXT NOT NULL,

    -- Activity recommendations
    best_time_for_work TIME,
    best_time_for_meditation TIME,
    best_time_for_important_decisions TIME,
    avoid_time_start TIME,
    avoid_time_end TIME,

    -- Specific areas
    career_guidance TEXT,
    relationship_guidance TEXT,
    health_guidance TEXT,
    financial_guidance TEXT,
    spiritual_guidance TEXT,

    -- Lucky elements
    lucky_color TEXT,
    lucky_direction TEXT,
    lucky_number INTEGER,
    lucky_gemstone TEXT,

    -- Remedies for the day
    suggested_mantra TEXT,
    suggested_deity TEXT,
    suggested_charity TEXT,

    -- User interaction
    was_viewed BOOLEAN DEFAULT false,
    viewed_at TIMESTAMP WITH TIME ZONE,
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    user_feedback TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(user_id, guidance_date)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_panchang_cache_date ON panchang_cache(panchang_date);
CREATE INDEX IF NOT EXISTS idx_panchang_cache_location ON panchang_cache(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_panchang_cache_date_location ON panchang_cache(panchang_date, latitude, longitude);

CREATE INDEX IF NOT EXISTS idx_panchang_subscriptions_user_id ON panchang_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_panchang_subscriptions_primary ON panchang_subscriptions(user_id, is_primary) WHERE is_primary = true;

CREATE INDEX IF NOT EXISTS idx_daily_guidance_log_user_id ON daily_guidance_log(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_guidance_log_date ON daily_guidance_log(guidance_date);
CREATE INDEX IF NOT EXISTS idx_daily_guidance_log_user_date ON daily_guidance_log(user_id, guidance_date);

-- Row-Level Security Policies

-- Panchang Cache: Public read (location-based data)
ALTER TABLE panchang_cache ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Anyone can view panchang cache" ON panchang_cache;
CREATE POLICY "Anyone can view panchang cache"
    ON panchang_cache FOR SELECT
    TO public
    USING (true);

-- Panchang Subscriptions: Users can only access their own subscriptions
ALTER TABLE panchang_subscriptions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own panchang subscriptions" ON panchang_subscriptions;
CREATE POLICY "Users can view their own panchang subscriptions"
    ON panchang_subscriptions FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage their own panchang subscriptions" ON panchang_subscriptions;
CREATE POLICY "Users can manage their own panchang subscriptions"
    ON panchang_subscriptions FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Panchang Preferences: Users can only access their own preferences
ALTER TABLE panchang_preferences ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own panchang preferences" ON panchang_preferences;
CREATE POLICY "Users can view their own panchang preferences"
    ON panchang_preferences FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage their own panchang preferences" ON panchang_preferences;
CREATE POLICY "Users can manage their own panchang preferences"
    ON panchang_preferences FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Daily Guidance Log: Users can only access their own guidance
ALTER TABLE daily_guidance_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own daily guidance" ON daily_guidance_log;
CREATE POLICY "Users can view their own daily guidance"
    ON daily_guidance_log FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage their own daily guidance" ON daily_guidance_log;
CREATE POLICY "Users can manage their own daily guidance"
    ON daily_guidance_log FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Functions

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_panchang_tables_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_panchang_subscriptions_updated_at ON panchang_subscriptions;
CREATE TRIGGER trigger_panchang_subscriptions_updated_at
    BEFORE UPDATE ON panchang_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_panchang_tables_updated_at();

DROP TRIGGER IF EXISTS trigger_panchang_preferences_updated_at ON panchang_preferences;
CREATE TRIGGER trigger_panchang_preferences_updated_at
    BEFORE UPDATE ON panchang_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_panchang_tables_updated_at();

-- Function: Get Rahukaal timings for a given weekday
CREATE OR REPLACE FUNCTION calculate_rahukaal(
    p_weekday INTEGER, -- 0=Sunday, 1=Monday, etc.
    p_sunrise TIME,
    p_sunset TIME
) RETURNS TABLE(start_time TIME, end_time TIME) AS $$
DECLARE
    v_day_duration INTERVAL;
    v_one_eighth INTERVAL;
    v_rahukaal_start TIME;
    v_rahukaal_end TIME;
    v_rahukaal_period INTEGER;
BEGIN
    -- Calculate day duration and one-eighth
    v_day_duration := p_sunset - p_sunrise;
    v_one_eighth := v_day_duration / 8;

    -- Rahukaal period varies by weekday (1-8, where each period is 1/8 of daylight)
    -- Sunday: 8th period, Monday: 2nd, Tuesday: 7th, Wednesday: 5th
    -- Thursday: 6th, Friday: 4th, Saturday: 3rd
    v_rahukaal_period := CASE p_weekday
        WHEN 0 THEN 8  -- Sunday
        WHEN 1 THEN 2  -- Monday
        WHEN 2 THEN 7  -- Tuesday
        WHEN 3 THEN 5  -- Wednesday
        WHEN 4 THEN 6  -- Thursday
        WHEN 5 THEN 4  -- Friday
        WHEN 6 THEN 3  -- Saturday
    END;

    v_rahukaal_start := p_sunrise + (v_one_eighth * (v_rahukaal_period - 1));
    v_rahukaal_end := p_sunrise + (v_one_eighth * v_rahukaal_period);

    RETURN QUERY SELECT v_rahukaal_start, v_rahukaal_end;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function: Check if current time is auspicious
CREATE OR REPLACE FUNCTION is_time_auspicious(
    p_panchang_id UUID,
    p_check_time TIMESTAMP WITH TIME ZONE
) RETURNS BOOLEAN AS $$
DECLARE
    v_check_time_only TIME;
    v_rahukaal_start TIME;
    v_rahukaal_end TIME;
    v_is_auspicious BOOLEAN := true;
BEGIN
    v_check_time_only := p_check_time::TIME;

    -- Get Rahukaal timings
    SELECT rahukaal_start, rahukaal_end INTO v_rahukaal_start, v_rahukaal_end
    FROM panchang_cache
    WHERE id = p_panchang_id;

    -- Check if time falls in Rahukaal
    IF v_check_time_only >= v_rahukaal_start AND v_check_time_only < v_rahukaal_end THEN
        v_is_auspicious := false;
    END IF;

    -- Additional checks for other inauspicious periods can be added here

    RETURN v_is_auspicious;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON TABLE panchang_cache IS 'Cached daily Panchang calculations for various locations';
COMMENT ON TABLE panchang_subscriptions IS 'User location subscriptions for daily Panchang notifications';
COMMENT ON TABLE panchang_preferences IS 'User preferences for Panchang display and notifications';
COMMENT ON TABLE daily_guidance_log IS 'Personalized daily guidance combining birth chart, Panchang, and transits';

COMMENT ON COLUMN panchang_cache.tithi_name IS 'Lunar day name (e.g., Pratipada, Dwitiya, etc.)';
COMMENT ON COLUMN panchang_cache.nakshatra_name IS 'Lunar mansion name (e.g., Ashwini, Bharani, etc.)';
COMMENT ON COLUMN panchang_cache.yoga_name IS 'Yoga name (combination of Sun-Moon longitude)';
COMMENT ON COLUMN panchang_cache.karana_name IS 'Karana name (half of Tithi)';
COMMENT ON COLUMN panchang_cache.rahukaal_start IS 'Start of Rahukaal (inauspicious period ruled by Rahu)';
COMMENT ON COLUMN panchang_cache.abhijit_muhurta_start IS 'Start of Abhijit Muhurta (most auspicious period of the day)';


-- ============================================================================
-- MIGRATION COMPLETE!
-- ============================================================================
--
-- Tables Created:
--   Life Threads: 2 tables (life_events, dasha_timeline_cache)
--   Remedy Planner: 4 tables (remedies_catalog, remedy_assignments, remedy_tracking, remedy_achievements)
--   Panchang: 4 tables (panchang_cache, panchang_subscriptions, panchang_preferences, daily_guidance_log)
--
-- Total: 10 new tables with full RLS policies
--
-- Functions Created: 6 (auto-update timestamps, Dasha lookup, streak calculation, Rahukaal calculation)
--
-- Next Step: Run the remedies catalog population script to add 40+ Vedic remedies
-- File: populate_remedies_catalog.sql
--
-- ============================================================================
