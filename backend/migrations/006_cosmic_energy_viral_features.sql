-- Migration: Cosmic Energy Score™ Viral Features
-- Created: 2025-01-11
-- Description: Friend connections, score caching, push notifications, and widget support

-- ============================================================================
-- FRIEND CONNECTIONS
-- ============================================================================

-- Friend connections table (bidirectional friendship)
CREATE TABLE IF NOT EXISTS friend_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    friend_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, accepted, rejected, blocked
    invited_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,

    -- Privacy settings
    share_cosmic_score BOOLEAN DEFAULT true,
    share_streak BOOLEAN DEFAULT true,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT different_users CHECK (user_id != friend_user_id),
    CONSTRAINT unique_connection UNIQUE (user_id, friend_user_id)
);

-- Indexes for friend lookups
CREATE INDEX IF NOT EXISTS idx_friend_connections_user_id ON friend_connections(user_id);
CREATE INDEX IF NOT EXISTS idx_friend_connections_friend_id ON friend_connections(friend_user_id);
CREATE INDEX IF NOT EXISTS idx_friend_connections_status ON friend_connections(status);

-- RLS Policies
ALTER TABLE friend_connections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own connections"
    ON friend_connections FOR SELECT
    USING (auth.uid() = user_id OR auth.uid() = friend_user_id);

CREATE POLICY "Users can create friend invitations"
    ON friend_connections FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their received invitations"
    ON friend_connections FOR UPDATE
    USING (auth.uid() = friend_user_id);

CREATE POLICY "Users can delete their own connections"
    ON friend_connections FOR DELETE
    USING (auth.uid() = user_id OR auth.uid() = friend_user_id);


-- ============================================================================
-- COSMIC SCORE CACHE
-- ============================================================================

-- Cache daily cosmic scores for performance
CREATE TABLE IF NOT EXISTS cosmic_score_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    score_date DATE NOT NULL,

    -- Score data
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    level VARCHAR(20) NOT NULL, -- HIGH_ENERGY, MODERATE_ENERGY, LOW_ENERGY
    color VARCHAR(20) NOT NULL, -- green, yellow, red
    emoji VARCHAR(10) NOT NULL, -- 🟢, 🟡, 🔴

    -- Activities
    best_for TEXT[] NOT NULL,
    avoid TEXT[] NOT NULL,

    -- Breakdown
    breakdown JSONB NOT NULL,

    -- Metadata
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_profile_date UNIQUE (profile_id, score_date)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_cosmic_score_cache_profile ON cosmic_score_cache(profile_id);
CREATE INDEX IF NOT EXISTS idx_cosmic_score_cache_date ON cosmic_score_cache(score_date);
CREATE INDEX IF NOT EXISTS idx_cosmic_score_cache_profile_date ON cosmic_score_cache(profile_id, score_date);

-- RLS Policies
ALTER TABLE cosmic_score_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own cached scores"
    ON cosmic_score_cache FOR SELECT
    USING (
        profile_id IN (
            SELECT id FROM profiles WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "System can insert cached scores"
    ON cosmic_score_cache FOR INSERT
    WITH CHECK (
        profile_id IN (
            SELECT id FROM profiles WHERE user_id = auth.uid()
        )
    );


-- ============================================================================
-- PUSH NOTIFICATION TOKENS
-- ============================================================================

-- Store push notification tokens for mobile apps
CREATE TABLE IF NOT EXISTS push_notification_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Token details
    token TEXT NOT NULL UNIQUE,
    platform VARCHAR(20) NOT NULL, -- ios, android, web
    device_id TEXT,

    -- Notification preferences
    daily_score_enabled BOOLEAN DEFAULT true,
    weekly_summary_enabled BOOLEAN DEFAULT true,
    friend_activity_enabled BOOLEAN DEFAULT true,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_user_token UNIQUE (user_id, token)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_push_tokens_user_id ON push_notification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_push_tokens_platform ON push_notification_tokens(platform);

-- RLS Policies
ALTER TABLE push_notification_tokens ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own tokens"
    ON push_notification_tokens FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own tokens"
    ON push_notification_tokens FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own tokens"
    ON push_notification_tokens FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own tokens"
    ON push_notification_tokens FOR DELETE
    USING (auth.uid() = user_id);


-- ============================================================================
-- DAILY ENGAGEMENT TRACKING
-- ============================================================================

-- Track daily engagement for streaks and analytics
CREATE TABLE IF NOT EXISTS daily_engagement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    engagement_date DATE NOT NULL,

    -- Engagement metrics
    viewed_cosmic_score BOOLEAN DEFAULT false,
    shared_cosmic_score BOOLEAN DEFAULT false,
    invited_friend BOOLEAN DEFAULT false,
    completed_astrowordle BOOLEAN DEFAULT false,

    -- Streak tracking
    current_streak INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_user_date UNIQUE (user_id, engagement_date)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_daily_engagement_user ON daily_engagement(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_engagement_date ON daily_engagement(engagement_date);

-- RLS Policies
ALTER TABLE daily_engagement ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own engagement"
    ON daily_engagement FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own engagement"
    ON daily_engagement FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own engagement"
    ON daily_engagement FOR UPDATE
    USING (auth.uid() = user_id);


-- ============================================================================
-- SHARE ANALYTICS
-- ============================================================================

-- Track shares for viral analytics
CREATE TABLE IF NOT EXISTS share_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Share details
    share_type VARCHAR(50) NOT NULL, -- cosmic_score, astrowordle_result, cosmic_wrapped
    platform VARCHAR(50) NOT NULL, -- instagram_story, whatsapp_status, twitter, facebook

    -- Referral tracking
    share_code VARCHAR(50) UNIQUE,
    clicks INTEGER DEFAULT 0,
    signups INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_share_analytics_user ON share_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_share_analytics_type ON share_analytics(share_type);
CREATE INDEX IF NOT EXISTS idx_share_analytics_platform ON share_analytics(platform);
CREATE INDEX IF NOT EXISTS idx_share_analytics_code ON share_analytics(share_code);

-- RLS Policies
ALTER TABLE share_analytics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own shares"
    ON share_analytics FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own shares"
    ON share_analytics FOR INSERT
    WITH CHECK (auth.uid() = user_id);


-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get friend count
CREATE OR REPLACE FUNCTION get_friend_count(p_user_id UUID)
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    SELECT COUNT(*)::INTEGER
    FROM friend_connections
    WHERE (user_id = p_user_id OR friend_user_id = p_user_id)
      AND status = 'accepted';
$$;

-- Function to check if users are friends
CREATE OR REPLACE FUNCTION are_friends(p_user_id UUID, p_friend_id UUID)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1 FROM friend_connections
        WHERE ((user_id = p_user_id AND friend_user_id = p_friend_id)
           OR (user_id = p_friend_id AND friend_user_id = p_user_id))
          AND status = 'accepted'
    );
$$;

-- Function to update engagement streak
CREATE OR REPLACE FUNCTION update_engagement_streak(p_user_id UUID, p_date DATE)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_yesterday DATE;
    v_yesterday_engaged BOOLEAN;
    v_current_streak INTEGER;
BEGIN
    v_yesterday := p_date - INTERVAL '1 day';

    -- Check if user was engaged yesterday
    SELECT COUNT(*) > 0 INTO v_yesterday_engaged
    FROM daily_engagement
    WHERE user_id = p_user_id
      AND engagement_date = v_yesterday;

    IF v_yesterday_engaged THEN
        -- Continue streak
        SELECT current_streak + 1 INTO v_current_streak
        FROM daily_engagement
        WHERE user_id = p_user_id
          AND engagement_date = v_yesterday;
    ELSE
        -- Start new streak
        v_current_streak := 1;
    END IF;

    RETURN v_current_streak;
END;
$$;


-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_friend_connections_user_status
    ON friend_connections(user_id, status);

CREATE INDEX IF NOT EXISTS idx_cosmic_cache_recent
    ON cosmic_score_cache(profile_id, score_date DESC);

-- Partial indexes for active connections
CREATE INDEX IF NOT EXISTS idx_friend_connections_accepted
    ON friend_connections(user_id)
    WHERE status = 'accepted';
