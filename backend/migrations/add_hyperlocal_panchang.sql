-- Migration: Add Hyperlocal Panchang feature tables
-- Feature: Location-based daily Panchang with contextual guidance
-- Author: Claude Code
-- Date: 2024-11-09

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

CREATE POLICY "Anyone can view panchang cache"
    ON panchang_cache FOR SELECT
    TO public
    USING (true);

-- Panchang Subscriptions: Users can only access their own subscriptions
ALTER TABLE panchang_subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own panchang subscriptions"
    ON panchang_subscriptions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own panchang subscriptions"
    ON panchang_subscriptions FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Panchang Preferences: Users can only access their own preferences
ALTER TABLE panchang_preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own panchang preferences"
    ON panchang_preferences FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own panchang preferences"
    ON panchang_preferences FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Daily Guidance Log: Users can only access their own guidance
ALTER TABLE daily_guidance_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own daily guidance"
    ON daily_guidance_log FOR SELECT
    USING (auth.uid() = user_id);

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

CREATE TRIGGER trigger_panchang_subscriptions_updated_at
    BEFORE UPDATE ON panchang_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_panchang_tables_updated_at();

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
