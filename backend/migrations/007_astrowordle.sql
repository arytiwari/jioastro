-- Migration: AstroWordle - Daily Astrology Quiz Game
-- Created: 2025-01-11
-- Description: Question bank, daily challenges, streaks, leaderboards, and viral features

-- ============================================================================
-- QUESTION BANK
-- ============================================================================

-- Question types: PLANET_POSITION, NAKSHATRA, YOGA, DASHA, HOUSE_LORD, TRANSIT, TRIVIA
CREATE TABLE IF NOT EXISTS astrowordle_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Question details
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20) NOT NULL, -- beginner, intermediate, advanced

    -- Answer configuration
    correct_answer TEXT NOT NULL,
    answer_format VARCHAR(50) NOT NULL, -- text, multiple_choice, number, planet, nakshatra
    acceptable_answers TEXT[], -- Alternative spellings/answers

    -- Multiple choice options (if applicable)
    options JSONB, -- [{value: "Mars", label: "Mars"}, ...]

    -- Hints and explanation
    hint TEXT,
    explanation TEXT NOT NULL,

    -- Metadata
    category VARCHAR(50), -- planets, nakshatras, yogas, dashas, houses, transits, general
    tags TEXT[],
    difficulty_score INTEGER DEFAULT 50, -- 1-100, used for adaptive selection

    -- Usage stats
    times_shown INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    average_attempts DECIMAL(3,1) DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_astrowordle_questions_type ON astrowordle_questions(question_type);
CREATE INDEX IF NOT EXISTS idx_astrowordle_questions_difficulty ON astrowordle_questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_astrowordle_questions_active ON astrowordle_questions(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_astrowordle_questions_category ON astrowordle_questions(category);


-- ============================================================================
-- DAILY CHALLENGES
-- ============================================================================

-- Tracks which question is active each day (deterministic)
CREATE TABLE IF NOT EXISTS astrowordle_daily_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenge_date DATE NOT NULL UNIQUE,
    question_id UUID NOT NULL REFERENCES astrowordle_questions(id),

    -- Stats for this challenge
    total_attempts INTEGER DEFAULT 0,
    total_completions INTEGER DEFAULT 0,
    average_guesses DECIMAL(3,1) DEFAULT 0,

    -- Difficulty adjustment
    actual_difficulty INTEGER, -- Calculated from user performance

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_astrowordle_daily_date ON astrowordle_daily_challenges(challenge_date DESC);


-- ============================================================================
-- USER ATTEMPTS
-- ============================================================================

-- Records each user's attempts at daily challenges
CREATE TABLE IF NOT EXISTS astrowordle_user_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    challenge_id UUID NOT NULL REFERENCES astrowordle_daily_challenges(id),

    -- Attempt details
    guesses JSONB NOT NULL, -- [{guess: "Mars", is_correct: false, timestamp: "..."}, ...]
    num_guesses INTEGER NOT NULL,
    is_completed BOOLEAN DEFAULT false,
    is_correct BOOLEAN DEFAULT false,

    -- Scoring
    score INTEGER NOT NULL, -- 100 for 1 guess, 83 for 2, 66 for 3, 50 for 4, 33 for 5, 16 for 6
    time_taken_seconds INTEGER, -- Time from first to last guess

    -- Share tracking
    has_shared BOOLEAN DEFAULT false,
    share_count INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_user_challenge UNIQUE (user_id, challenge_id),
    CONSTRAINT valid_num_guesses CHECK (num_guesses >= 1 AND num_guesses <= 6)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_astrowordle_attempts_user ON astrowordle_user_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_astrowordle_attempts_challenge ON astrowordle_user_attempts(challenge_id);
CREATE INDEX IF NOT EXISTS idx_astrowordle_attempts_score ON astrowordle_user_attempts(score DESC);
CREATE INDEX IF NOT EXISTS idx_astrowordle_attempts_created ON astrowordle_user_attempts(created_at DESC);

-- RLS Policies
ALTER TABLE astrowordle_user_attempts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own attempts"
    ON astrowordle_user_attempts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own attempts"
    ON astrowordle_user_attempts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own attempts"
    ON astrowordle_user_attempts FOR UPDATE
    USING (auth.uid() = user_id);


-- ============================================================================
-- STREAKS
-- ============================================================================

-- Tracks user streaks
CREATE TABLE IF NOT EXISTS astrowordle_streaks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Current streak
    current_streak INTEGER NOT NULL DEFAULT 0,
    last_played_date DATE,

    -- Best streak
    longest_streak INTEGER NOT NULL DEFAULT 0,
    longest_streak_start_date DATE,
    longest_streak_end_date DATE,

    -- Stats
    total_games_played INTEGER NOT NULL DEFAULT 0,
    total_games_won INTEGER NOT NULL DEFAULT 0,
    total_guesses INTEGER NOT NULL DEFAULT 0,

    -- Distribution of wins by number of guesses
    wins_in_1 INTEGER NOT NULL DEFAULT 0,
    wins_in_2 INTEGER NOT NULL DEFAULT 0,
    wins_in_3 INTEGER NOT NULL DEFAULT 0,
    wins_in_4 INTEGER NOT NULL DEFAULT 0,
    wins_in_5 INTEGER NOT NULL DEFAULT 0,
    wins_in_6 INTEGER NOT NULL DEFAULT 0,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_astrowordle_streaks_user ON astrowordle_streaks(user_id);
CREATE INDEX IF NOT EXISTS idx_astrowordle_streaks_current ON astrowordle_streaks(current_streak DESC);
CREATE INDEX IF NOT EXISTS idx_astrowordle_streaks_longest ON astrowordle_streaks(longest_streak DESC);

-- RLS Policies
ALTER TABLE astrowordle_streaks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own streaks"
    ON astrowordle_streaks FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own streaks"
    ON astrowordle_streaks FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own streaks"
    ON astrowordle_streaks FOR UPDATE
    USING (auth.uid() = user_id);


-- ============================================================================
-- LEADERBOARDS
-- ============================================================================

-- Global and time-based leaderboards
CREATE TABLE IF NOT EXISTS astrowordle_leaderboard_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Leaderboard type
    leaderboard_type VARCHAR(50) NOT NULL, -- daily, weekly, monthly, all_time
    period_start DATE NOT NULL,
    period_end DATE,

    -- Scores
    total_score INTEGER NOT NULL DEFAULT 0,
    games_played INTEGER NOT NULL DEFAULT 0,
    games_won INTEGER NOT NULL DEFAULT 0,
    average_guesses DECIMAL(3,1) DEFAULT 0,
    current_streak INTEGER NOT NULL DEFAULT 0,

    -- Ranking
    rank INTEGER,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_user_period UNIQUE (user_id, leaderboard_type, period_start)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_astrowordle_leaderboard_type ON astrowordle_leaderboard_entries(leaderboard_type);
CREATE INDEX IF NOT EXISTS idx_astrowordle_leaderboard_period ON astrowordle_leaderboard_entries(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_astrowordle_leaderboard_score ON astrowordle_leaderboard_entries(total_score DESC);
CREATE INDEX IF NOT EXISTS idx_astrowordle_leaderboard_rank ON astrowordle_leaderboard_entries(leaderboard_type, rank);

-- RLS Policies
ALTER TABLE astrowordle_leaderboard_entries ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view all leaderboard entries"
    ON astrowordle_leaderboard_entries FOR SELECT
    USING (true);


-- ============================================================================
-- SHARE TEMPLATES
-- ============================================================================

-- Share result templates (emoji grids like Wordle)
CREATE TABLE IF NOT EXISTS astrowordle_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    attempt_id UUID NOT NULL REFERENCES astrowordle_user_attempts(id) ON DELETE CASCADE,

    -- Share details
    share_code VARCHAR(50) UNIQUE,
    emoji_grid TEXT NOT NULL, -- "AstroWordle 123 3/6\n🟢⬜⬜⬜⬜\n🟢🟡⬜⬜⬜\n🟢🟢🟢🟢🟢"
    share_text TEXT NOT NULL,
    template_type VARCHAR(50) NOT NULL, -- whatsapp, instagram_story, twitter

    -- Viral tracking
    clicks INTEGER DEFAULT 0,
    signups INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_astrowordle_shares_user ON astrowordle_shares(user_id);
CREATE INDEX IF NOT EXISTS idx_astrowordle_shares_code ON astrowordle_shares(share_code);
CREATE INDEX IF NOT EXISTS idx_astrowordle_shares_attempt ON astrowordle_shares(attempt_id);

-- RLS Policies
ALTER TABLE astrowordle_shares ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own shares"
    ON astrowordle_shares FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own shares"
    ON astrowordle_shares FOR INSERT
    WITH CHECK (auth.uid() = user_id);


-- ============================================================================
-- FRIEND CHALLENGES
-- ============================================================================

-- Challenge friends to beat your score
CREATE TABLE IF NOT EXISTS astrowordle_friend_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenger_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    challenged_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    challenge_id UUID NOT NULL REFERENCES astrowordle_daily_challenges(id),

    -- Challenge details
    challenger_score INTEGER NOT NULL,
    challenger_guesses INTEGER NOT NULL,

    -- Response
    has_responded BOOLEAN DEFAULT false,
    challenged_score INTEGER,
    challenged_guesses INTEGER,

    -- Result
    winner_user_id UUID REFERENCES auth.users(id),

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    responded_at TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT different_users CHECK (challenger_user_id != challenged_user_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_astrowordle_friend_challenges_challenger ON astrowordle_friend_challenges(challenger_user_id);
CREATE INDEX IF NOT EXISTS idx_astrowordle_friend_challenges_challenged ON astrowordle_friend_challenges(challenged_user_id);
CREATE INDEX IF NOT EXISTS idx_astrowordle_friend_challenges_status ON astrowordle_friend_challenges(has_responded);

-- RLS Policies
ALTER TABLE astrowordle_friend_challenges ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own challenges"
    ON astrowordle_friend_challenges FOR SELECT
    USING (auth.uid() = challenger_user_id OR auth.uid() = challenged_user_id);

CREATE POLICY "Users can create challenges"
    ON astrowordle_friend_challenges FOR INSERT
    WITH CHECK (auth.uid() = challenger_user_id);

CREATE POLICY "Challenged users can update responses"
    ON astrowordle_friend_challenges FOR UPDATE
    USING (auth.uid() = challenged_user_id);


-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get today's challenge
CREATE OR REPLACE FUNCTION get_todays_astrowordle_challenge()
RETURNS UUID
LANGUAGE SQL
STABLE
AS $$
    SELECT id FROM astrowordle_daily_challenges
    WHERE challenge_date = CURRENT_DATE
    LIMIT 1;
$$;

-- Function to calculate score based on number of guesses
CREATE OR REPLACE FUNCTION calculate_astrowordle_score(p_num_guesses INTEGER, p_is_correct BOOLEAN)
RETURNS INTEGER
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT CASE
        WHEN NOT p_is_correct THEN 0
        WHEN p_num_guesses = 1 THEN 100
        WHEN p_num_guesses = 2 THEN 83
        WHEN p_num_guesses = 3 THEN 66
        WHEN p_num_guesses = 4 THEN 50
        WHEN p_num_guesses = 5 THEN 33
        WHEN p_num_guesses = 6 THEN 16
        ELSE 0
    END;
$$;

-- Function to update streak after completing a challenge
CREATE OR REPLACE FUNCTION update_astrowordle_streak(
    p_user_id UUID,
    p_challenge_date DATE,
    p_is_correct BOOLEAN,
    p_num_guesses INTEGER
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_last_played_date DATE;
    v_current_streak INTEGER;
    v_longest_streak INTEGER;
    v_new_streak INTEGER;
BEGIN
    -- Get current streak data
    SELECT last_played_date, current_streak, longest_streak
    INTO v_last_played_date, v_current_streak, v_longest_streak
    FROM astrowordle_streaks
    WHERE user_id = p_user_id;

    -- If no streak record exists, create one
    IF NOT FOUND THEN
        INSERT INTO astrowordle_streaks (user_id, current_streak, last_played_date, longest_streak)
        VALUES (p_user_id,
                CASE WHEN p_is_correct THEN 1 ELSE 0 END,
                p_challenge_date,
                CASE WHEN p_is_correct THEN 1 ELSE 0 END);
        RETURN;
    END IF;

    -- Calculate new streak
    IF p_is_correct THEN
        IF v_last_played_date = p_challenge_date - INTERVAL '1 day' THEN
            -- Continue streak
            v_new_streak := v_current_streak + 1;
        ELSIF v_last_played_date = p_challenge_date THEN
            -- Same day, don't change streak
            v_new_streak := v_current_streak;
        ELSE
            -- Streak broken, start new
            v_new_streak := 1;
        END IF;
    ELSE
        -- Failed challenge, reset streak
        v_new_streak := 0;
    END IF;

    -- Update streak record
    UPDATE astrowordle_streaks
    SET current_streak = v_new_streak,
        last_played_date = p_challenge_date,
        longest_streak = GREATEST(v_longest_streak, v_new_streak),
        total_games_played = total_games_played + 1,
        total_games_won = total_games_won + CASE WHEN p_is_correct THEN 1 ELSE 0 END,
        total_guesses = total_guesses + p_num_guesses,
        -- Update wins distribution
        wins_in_1 = wins_in_1 + CASE WHEN p_is_correct AND p_num_guesses = 1 THEN 1 ELSE 0 END,
        wins_in_2 = wins_in_2 + CASE WHEN p_is_correct AND p_num_guesses = 2 THEN 1 ELSE 0 END,
        wins_in_3 = wins_in_3 + CASE WHEN p_is_correct AND p_num_guesses = 3 THEN 1 ELSE 0 END,
        wins_in_4 = wins_in_4 + CASE WHEN p_is_correct AND p_num_guesses = 4 THEN 1 ELSE 0 END,
        wins_in_5 = wins_in_5 + CASE WHEN p_is_correct AND p_num_guesses = 5 THEN 1 ELSE 0 END,
        wins_in_6 = wins_in_6 + CASE WHEN p_is_correct AND p_num_guesses = 6 THEN 1 ELSE 0 END,
        updated_at = NOW()
    WHERE user_id = p_user_id;
END;
$$;

-- Function to generate daily challenge (deterministic based on date)
CREATE OR REPLACE FUNCTION generate_daily_astrowordle_challenge(p_date DATE)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_question_id UUID;
    v_challenge_id UUID;
    v_seed INTEGER;
BEGIN
    -- Check if challenge already exists
    SELECT id INTO v_challenge_id
    FROM astrowordle_daily_challenges
    WHERE challenge_date = p_date;

    IF FOUND THEN
        RETURN v_challenge_id;
    END IF;

    -- Generate deterministic seed from date
    v_seed := EXTRACT(EPOCH FROM p_date)::INTEGER;

    -- Select question deterministically using seed
    -- This ensures all users get the same question on the same day
    SELECT id INTO v_question_id
    FROM astrowordle_questions
    WHERE is_active = true
    ORDER BY (hashtext(id::text || v_seed::text))
    LIMIT 1;

    -- Create challenge
    INSERT INTO astrowordle_daily_challenges (challenge_date, question_id)
    VALUES (p_date, v_question_id)
    RETURNING id INTO v_challenge_id;

    RETURN v_challenge_id;
END;
$$;


-- ============================================================================
-- SAMPLE QUESTIONS (Initial seed data)
-- ============================================================================

-- Insert sample questions for testing
INSERT INTO astrowordle_questions (question_text, question_type, difficulty, correct_answer, answer_format, acceptable_answers, explanation, category, tags) VALUES

-- Beginner Questions
('Which planet is known as the "Red Planet" in astrology?', 'TRIVIA', 'beginner', 'Mars', 'text', ARRAY['Mars', 'Mangal', 'Kuja'], 'Mars is known as the Red Planet due to its reddish appearance caused by iron oxide on its surface.', 'planets', ARRAY['planets', 'basics']),

('How many nakshatras are there in Vedic astrology?', 'TRIVIA', 'beginner', '27', 'number', ARRAY['27', 'twenty-seven'], 'There are 27 nakshatras (lunar mansions) in Vedic astrology, each spanning 13°20'' of the zodiac.', 'nakshatras', ARRAY['nakshatras', 'basics']),

('Which planet rules the sign Aries?', 'PLANET_POSITION', 'beginner', 'Mars', 'text', ARRAY['Mars', 'Mangal'], 'Mars (Mangal) is the ruling planet of Aries (Mesha), giving Aries its fiery and energetic nature.', 'planets', ARRAY['planets', 'signs', 'rulership']),

('How many houses are there in a birth chart?', 'TRIVIA', 'beginner', '12', 'number', ARRAY['12', 'twelve'], 'A birth chart (kundli) has 12 houses, each representing different areas of life.', 'houses', ARRAY['houses', 'basics']),

('Which nakshatra is known as the "Star of Power"?', 'NAKSHATRA', 'beginner', 'Rohini', 'text', ARRAY['Rohini'], 'Rohini nakshatra is known as the "Star of Power" and is ruled by the Moon. It is considered highly auspicious.', 'nakshatras', ARRAY['nakshatras']),

-- Intermediate Questions
('In Vimshottari Dasha system, how many years is the total cycle?', 'DASHA', 'intermediate', '120', 'number', ARRAY['120', 'one hundred twenty'], 'The Vimshottari Dasha system has a complete cycle of 120 years, distributed among 9 planets.', 'dashas', ARRAY['dasha', 'vimshottari']),

('Which yoga is formed when Jupiter and Moon are in mutual kendras?', 'YOGA', 'intermediate', 'Gaja Kesari', 'text', ARRAY['Gaja Kesari', 'Gajakesari', 'Gajkesari'], 'Gaja Kesari Yoga forms when Jupiter and Moon are in kendras (1st, 4th, 7th, or 10th houses) from each other.', 'yogas', ARRAY['yogas', 'jupiter', 'moon']),

('Which house is known as the "House of Transformation"?', 'HOUSE_LORD', 'intermediate', '8th', 'text', ARRAY['8th', 'eighth', '8'], 'The 8th house represents transformation, death, rebirth, occult knowledge, and sudden events.', 'houses', ARRAY['houses']),

('How many years does Saturn take to complete one orbit around the Sun?', 'TRANSIT', 'intermediate', '29', 'number', ARRAY['29', '29.5', 'twenty-nine'], 'Saturn takes approximately 29.5 years to complete one orbit around the Sun, spending about 2.5 years in each zodiac sign.', 'planets', ARRAY['saturn', 'transits']),

('Which nakshatra is ruled by Ketu?', 'NAKSHATRA', 'intermediate', 'Ashwini', 'text', ARRAY['Ashwini', 'Aswini'], 'Ashwini nakshatra is the first nakshatra and is ruled by Ketu. It represents healing and swift action.', 'nakshatras', ARRAY['nakshatras', 'ketu']),

-- Advanced Questions
('What is the specific degree range of Pushya nakshatra?', 'NAKSHATRA', 'advanced', '93°20'' to 106°40''', 'text', ARRAY['93°20'' to 106°40''', '93-106', 'Cancer 3°20'' to 16°40'''], 'Pushya nakshatra spans from 93°20'' to 106°40'' in the zodiac, falling in the Cancer sign.', 'nakshatras', ARRAY['nakshatras', 'degrees']),

('Which planet has the shortest dasha period in Vimshottari system?', 'DASHA', 'advanced', 'Sun', 'text', ARRAY['Sun', 'Surya'], 'Sun has the shortest dasha period of 6 years in the Vimshottari Dasha system.', 'dashas', ARRAY['dasha', 'sun']),

('What is the Sanskrit name for the yoga formed by all benefics in kendras and all malefics in upachayas?', 'YOGA', 'advanced', 'Shrinatha Yoga', 'text', ARRAY['Shrinatha Yoga', 'Shrinath Yoga', 'Sri Natha Yoga'], 'Shrinatha Yoga is a rare and powerful yoga formed when all benefic planets are in kendras and all malefic planets are in upachaya houses (3, 6, 10, 11).', 'yogas', ARRAY['yogas', 'rare']),

('In which nakshatra pada is Mars most exalted?', 'NAKSHATRA', 'advanced', 'Uttara Bhadrapada 1st pada', 'text', ARRAY['Uttara Bhadrapada 1st pada', 'Uttara Bhadrapada 1', 'UBhadra 1'], 'Mars is exalted at 28° Capricorn, which falls in the 1st pada of Uttara Bhadrapada nakshatra.', 'nakshatras', ARRAY['nakshatras', 'exaltation', 'mars']),

('What is the degree of deep exaltation for Moon?', 'PLANET_POSITION', 'advanced', '3°', 'text', ARRAY['3', '3°', '3 degrees', 'three degrees'], 'Moon is deeply exalted at exactly 3° Taurus, its highest point of strength.', 'planets', ARRAY['moon', 'exaltation'])

ON CONFLICT DO NOTHING;
