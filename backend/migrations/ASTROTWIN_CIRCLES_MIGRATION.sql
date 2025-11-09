-- ============================================================================
-- MAGICAL 12 FEATURE #6: ASTROTWIN CIRCLES - Community & Pattern Discovery
-- ============================================================================
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

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- CHART VECTORIZATION - For similarity search
-- ============================================================================

-- Chart Vectors: Encoded birth chart features for similarity matching
CREATE TABLE IF NOT EXISTS chart_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Vector representation (384 dimensions - using sentence transformers size)
    -- Encodes: sun/moon/ascendant, dominant planets, yogas, current dasha, life stage
    chart_vector vector(384) NOT NULL,

    -- Metadata for explainability
    feature_metadata JSONB NOT NULL, -- Stores what went into the vector
    /*
    Example:
    {
        "sun_sign": "Aries",
        "moon_sign": "Cancer",
        "ascendant": "Libra",
        "dominant_planets": ["Venus", "Jupiter", "Mercury"],
        "major_yogas": ["GajaKesari", "Hamsa"],
        "current_dasha_md": "Venus",
        "current_dasha_ad": "Sun",
        "saturn_phase": "Sade Sati Phase 2",
        "life_stage": "30-40",
        "gender": "female",
        "location_region": "North India"
    }
    */

    -- Privacy controls
    privacy_opt_in BOOLEAN DEFAULT false, -- User must explicitly opt-in for discovery
    allow_pattern_learning BOOLEAN DEFAULT false, -- Allow anonymized outcome data for ML
    visible_in_search BOOLEAN DEFAULT false, -- Show in AstroTwin search results

    -- Metadata
    vectorization_version TEXT DEFAULT '1.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(profile_id)
);

-- Index for vector similarity search (using HNSW for fast approximate nearest neighbor)
CREATE INDEX IF NOT EXISTS idx_chart_vectors_vector ON chart_vectors
USING hnsw (chart_vector vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_chart_vectors_user_id ON chart_vectors(user_id);
CREATE INDEX IF NOT EXISTS idx_chart_vectors_opt_in ON chart_vectors(privacy_opt_in) WHERE privacy_opt_in = true;


-- ============================================================================
-- ASTROTWIN CIRCLES - Community management
-- ============================================================================

-- Circles: User-created or system-suggested groups
CREATE TABLE IF NOT EXISTS astrotwin_circles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Circle details
    circle_name TEXT NOT NULL,
    circle_description TEXT,
    circle_type TEXT NOT NULL CHECK (circle_type IN (
        'family',           -- Friends & family
        'life_stage',       -- e.g., "New parents with Saturn transit"
        'goal',             -- e.g., "Career switchers in tech"
        'business',         -- e.g., "Entrepreneurs with Raj Yoga"
        'location',         -- Regional groups
        'custom'            -- User-defined
    )),

    -- Creator/owner
    creator_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Circle settings
    is_private BOOLEAN DEFAULT true, -- Private (invite-only) vs Public (anyone can join)
    requires_approval BOOLEAN DEFAULT true, -- Admin must approve join requests
    max_members INTEGER DEFAULT 50,

    -- Discovery criteria (for system-suggested circles)
    similarity_threshold DECIMAL(3, 2), -- e.g., 0.3 = charts must be <0.3 distance
    feature_filters JSONB, -- e.g., {"saturn_phase": "Sade Sati", "life_stage": "30-40"}

    -- Tags for discovery
    tags TEXT[],

    -- Stats
    member_count INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_astrotwin_circles_creator ON astrotwin_circles(creator_user_id);
CREATE INDEX IF NOT EXISTS idx_astrotwin_circles_type ON astrotwin_circles(circle_type);
CREATE INDEX IF NOT EXISTS idx_astrotwin_circles_public ON astrotwin_circles(is_private) WHERE is_private = false;


-- Circle Membership: User participation in circles
CREATE TABLE IF NOT EXISTS circle_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circle_id UUID NOT NULL REFERENCES astrotwin_circles(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,

    -- Membership details
    role TEXT DEFAULT 'member' CHECK (role IN ('admin', 'moderator', 'member')),
    join_status TEXT DEFAULT 'pending' CHECK (join_status IN ('pending', 'active', 'left', 'removed')),

    -- User contribution
    shared_outcomes BOOLEAN DEFAULT false, -- User shares their life outcomes with circle

    -- Metadata
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    left_at TIMESTAMP WITH TIME ZONE,

    UNIQUE(circle_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_circle_memberships_circle_id ON circle_memberships(circle_id);
CREATE INDEX IF NOT EXISTS idx_circle_memberships_user_id ON circle_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_circle_memberships_active ON circle_memberships(circle_id, join_status) WHERE join_status = 'active';


-- ============================================================================
-- LIFE OUTCOMES - For pattern analysis
-- ============================================================================

-- Life Outcomes: User-reported life events with success/failure tagging
CREATE TABLE IF NOT EXISTS life_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,

    -- Outcome details
    outcome_type TEXT NOT NULL CHECK (outcome_type IN (
        'job_change',
        'promotion',
        'business_launch',
        'marriage',
        'childbirth',
        'property_purchase',
        'major_investment',
        'education_milestone',
        'health_recovery',
        'relationship_breakup',
        'financial_loss',
        'other'
    )),
    outcome_title TEXT NOT NULL,
    outcome_date DATE NOT NULL,
    outcome_result TEXT NOT NULL CHECK (outcome_result IN ('success', 'partial_success', 'failure', 'neutral')),

    -- Context (what was happening astrologically)
    dasha_context JSONB, -- Dasha period at time of outcome
    transit_context JSONB, -- Major transits at time of outcome
    chart_factors JSONB, -- Relevant chart factors (e.g., 10th house strength for job change)

    -- User assessment
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    user_notes TEXT,

    -- Privacy
    share_anonymously BOOLEAN DEFAULT false, -- Allow pattern analysis without identifying user

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_outcome_date CHECK (outcome_date >= '1950-01-01' AND outcome_date <= CURRENT_DATE + INTERVAL '1 year')
);

CREATE INDEX IF NOT EXISTS idx_life_outcomes_user_id ON life_outcomes(user_id);
CREATE INDEX IF NOT EXISTS idx_life_outcomes_type ON life_outcomes(outcome_type);
CREATE INDEX IF NOT EXISTS idx_life_outcomes_result ON life_outcomes(outcome_result);
CREATE INDEX IF NOT EXISTS idx_life_outcomes_date ON life_outcomes(outcome_date);
CREATE INDEX IF NOT EXISTS idx_life_outcomes_shareable ON life_outcomes(share_anonymously) WHERE share_anonymously = true;


-- ============================================================================
-- PATTERN DISCOVERIES - System-learned patterns
-- ============================================================================

-- Pattern Discoveries: Extracted patterns from AstroTwin data
CREATE TABLE IF NOT EXISTS pattern_discoveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Pattern identification
    pattern_type TEXT NOT NULL, -- e.g., "job_change_success"
    pattern_name TEXT NOT NULL,
    pattern_description TEXT NOT NULL,

    -- Conditions
    chart_conditions JSONB NOT NULL, -- What chart features correlate with this pattern
    /*
    Example:
    {
        "venus_dasha": true,
        "jupiter_transit_10th": true,
        "mercury_shadbala": ">0.7",
        "yogas": ["Budhaditya"]
    }
    */

    -- Statistical strength
    sample_size INTEGER NOT NULL, -- How many data points
    correlation_score DECIMAL(4, 3), -- 0.0 to 1.0
    confidence_level DECIMAL(4, 3), -- Statistical confidence

    -- Insights
    success_rate DECIMAL(4, 3), -- % of people with this pattern who succeeded
    timing_insights JSONB, -- When this pattern tends to manifest
    recommendations TEXT[], -- Actionable advice for people matching this pattern

    -- Metadata
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_pattern_discoveries_type ON pattern_discoveries(pattern_type);
CREATE INDEX IF NOT EXISTS idx_pattern_discoveries_active ON pattern_discoveries(is_active) WHERE is_active = true;


-- ============================================================================
-- CIRCLE INSIGHTS - Shared wisdom within circles
-- ============================================================================

-- Circle Insights: Patterns discovered within specific circles
CREATE TABLE IF NOT EXISTS circle_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circle_id UUID NOT NULL REFERENCES astrotwin_circles(id) ON DELETE CASCADE,
    pattern_id UUID REFERENCES pattern_discoveries(id) ON DELETE SET NULL,

    -- Insight details
    insight_type TEXT NOT NULL CHECK (insight_type IN (
        'success_pattern',
        'timing_insight',
        'common_challenge',
        'recommended_remedy',
        'shared_experience'
    )),
    insight_title TEXT NOT NULL,
    insight_description TEXT NOT NULL,

    -- Stats for this circle
    member_count_matching INTEGER, -- How many circle members match this pattern
    success_stories JSONB, -- Anonymized success stories

    -- Engagement
    upvotes INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_circle_insights_circle_id ON circle_insights(circle_id);
CREATE INDEX IF NOT EXISTS idx_circle_insights_type ON circle_insights(insight_type);


-- ============================================================================
-- CIRCLE POSTS - Community interaction (optional social layer)
-- ============================================================================

-- Circle Posts: User posts within circles
CREATE TABLE IF NOT EXISTS circle_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circle_id UUID NOT NULL REFERENCES astrotwin_circles(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Post content
    post_type TEXT DEFAULT 'text' CHECK (post_type IN ('text', 'question', 'success_story', 'remedy_share')),
    post_title TEXT,
    post_content TEXT NOT NULL,

    -- Engagement
    upvotes INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,

    -- Moderation
    is_pinned BOOLEAN DEFAULT false,
    is_hidden BOOLEAN DEFAULT false,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_circle_posts_circle_id ON circle_posts(circle_id);
CREATE INDEX IF NOT EXISTS idx_circle_posts_user_id ON circle_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_circle_posts_created_at ON circle_posts(created_at DESC);


-- Post Replies: Threaded discussions
CREATE TABLE IF NOT EXISTS circle_post_replies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES circle_posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Reply content
    reply_content TEXT NOT NULL,

    -- Engagement
    upvotes INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_circle_post_replies_post_id ON circle_post_replies(post_id);
CREATE INDEX IF NOT EXISTS idx_circle_post_replies_user_id ON circle_post_replies(user_id);


-- ============================================================================
-- ROW-LEVEL SECURITY POLICIES
-- ============================================================================

-- Chart Vectors: Users can only access their own vectors
ALTER TABLE chart_vectors ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own chart vectors" ON chart_vectors;
CREATE POLICY "Users can view their own chart vectors"
    ON chart_vectors FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage their own chart vectors" ON chart_vectors;
CREATE POLICY "Users can manage their own chart vectors"
    ON chart_vectors FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Public search (only for users who opted in)
DROP POLICY IF EXISTS "Public can search opt-in chart vectors" ON chart_vectors;
CREATE POLICY "Public can search opt-in chart vectors"
    ON chart_vectors FOR SELECT
    USING (privacy_opt_in = true AND visible_in_search = true);


-- AstroTwin Circles: Visibility based on privacy settings
ALTER TABLE astrotwin_circles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view public circles" ON astrotwin_circles;
CREATE POLICY "Users can view public circles"
    ON astrotwin_circles FOR SELECT
    USING (is_private = false OR creator_user_id = auth.uid());

DROP POLICY IF EXISTS "Users can create circles" ON astrotwin_circles;
CREATE POLICY "Users can create circles"
    ON astrotwin_circles FOR INSERT
    WITH CHECK (auth.uid() = creator_user_id);

DROP POLICY IF EXISTS "Creators can update their circles" ON astrotwin_circles;
CREATE POLICY "Creators can update their circles"
    ON astrotwin_circles FOR UPDATE
    USING (auth.uid() = creator_user_id)
    WITH CHECK (auth.uid() = creator_user_id);

DROP POLICY IF EXISTS "Creators can delete their circles" ON astrotwin_circles;
CREATE POLICY "Creators can delete their circles"
    ON astrotwin_circles FOR DELETE
    USING (auth.uid() = creator_user_id);


-- Circle Memberships: Users can view memberships of circles they're in
ALTER TABLE circle_memberships ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view memberships in their circles" ON circle_memberships;
CREATE POLICY "Users can view memberships in their circles"
    ON circle_memberships FOR SELECT
    USING (
        user_id = auth.uid() OR
        circle_id IN (
            SELECT circle_id FROM circle_memberships
            WHERE user_id = auth.uid() AND join_status = 'active'
        )
    );

DROP POLICY IF EXISTS "Users can manage their own memberships" ON circle_memberships;
CREATE POLICY "Users can manage their own memberships"
    ON circle_memberships FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);


-- Life Outcomes: Users can only access their own outcomes
ALTER TABLE life_outcomes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own outcomes" ON life_outcomes;
CREATE POLICY "Users can view their own outcomes"
    ON life_outcomes FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage their own outcomes" ON life_outcomes;
CREATE POLICY "Users can manage their own outcomes"
    ON life_outcomes FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);


-- Pattern Discoveries: Public read for active patterns
ALTER TABLE pattern_discoveries ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Anyone can view active patterns" ON pattern_discoveries;
CREATE POLICY "Anyone can view active patterns"
    ON pattern_discoveries FOR SELECT
    TO public
    USING (is_active = true);


-- Circle Insights: Visible to circle members
ALTER TABLE circle_insights ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Circle members can view insights" ON circle_insights;
CREATE POLICY "Circle members can view insights"
    ON circle_insights FOR SELECT
    USING (
        circle_id IN (
            SELECT circle_id FROM circle_memberships
            WHERE user_id = auth.uid() AND join_status = 'active'
        )
    );


-- Circle Posts: Visible to circle members
ALTER TABLE circle_posts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Circle members can view posts" ON circle_posts;
CREATE POLICY "Circle members can view posts"
    ON circle_posts FOR SELECT
    USING (
        circle_id IN (
            SELECT circle_id FROM circle_memberships
            WHERE user_id = auth.uid() AND join_status = 'active'
        )
    );

DROP POLICY IF EXISTS "Circle members can create posts" ON circle_posts;
CREATE POLICY "Circle members can create posts"
    ON circle_posts FOR INSERT
    WITH CHECK (
        auth.uid() = user_id AND
        circle_id IN (
            SELECT circle_id FROM circle_memberships
            WHERE user_id = auth.uid() AND join_status = 'active'
        )
    );

DROP POLICY IF EXISTS "Post authors can update their posts" ON circle_posts;
CREATE POLICY "Post authors can update their posts"
    ON circle_posts FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Post authors can delete their posts" ON circle_posts;
CREATE POLICY "Post authors can delete their posts"
    ON circle_posts FOR DELETE
    USING (auth.uid() = user_id);


-- Circle Post Replies: Visible to circle members
ALTER TABLE circle_post_replies ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Circle members can view replies" ON circle_post_replies;
CREATE POLICY "Circle members can view replies"
    ON circle_post_replies FOR SELECT
    USING (
        post_id IN (
            SELECT id FROM circle_posts WHERE circle_id IN (
                SELECT circle_id FROM circle_memberships
                WHERE user_id = auth.uid() AND join_status = 'active'
            )
        )
    );

DROP POLICY IF EXISTS "Circle members can create replies" ON circle_post_replies;
CREATE POLICY "Circle members can create replies"
    ON circle_post_replies FOR INSERT
    WITH CHECK (
        auth.uid() = user_id AND
        post_id IN (
            SELECT id FROM circle_posts WHERE circle_id IN (
                SELECT circle_id FROM circle_memberships
                WHERE user_id = auth.uid() AND join_status = 'active'
            )
        )
    );


-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_astrotwin_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_chart_vectors_updated_at ON chart_vectors;
CREATE TRIGGER trigger_chart_vectors_updated_at
    BEFORE UPDATE ON chart_vectors
    FOR EACH ROW
    EXECUTE FUNCTION update_astrotwin_updated_at();

DROP TRIGGER IF EXISTS trigger_astrotwin_circles_updated_at ON astrotwin_circles;
CREATE TRIGGER trigger_astrotwin_circles_updated_at
    BEFORE UPDATE ON astrotwin_circles
    FOR EACH ROW
    EXECUTE FUNCTION update_astrotwin_updated_at();

DROP TRIGGER IF EXISTS trigger_circle_posts_updated_at ON circle_posts;
CREATE TRIGGER trigger_circle_posts_updated_at
    BEFORE UPDATE ON circle_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_astrotwin_updated_at();


-- Update circle member count
CREATE OR REPLACE FUNCTION update_circle_member_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE astrotwin_circles
    SET member_count = (
        SELECT COUNT(*)
        FROM circle_memberships
        WHERE circle_id = COALESCE(NEW.circle_id, OLD.circle_id)
        AND join_status = 'active'
    )
    WHERE id = COALESCE(NEW.circle_id, OLD.circle_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_circle_member_count ON circle_memberships;
CREATE TRIGGER trigger_update_circle_member_count
    AFTER INSERT OR UPDATE OR DELETE ON circle_memberships
    FOR EACH ROW
    EXECUTE FUNCTION update_circle_member_count();


-- Update post reply count
CREATE OR REPLACE FUNCTION update_post_reply_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE circle_posts
    SET reply_count = (
        SELECT COUNT(*)
        FROM circle_post_replies
        WHERE post_id = COALESCE(NEW.post_id, OLD.post_id)
    )
    WHERE id = COALESCE(NEW.post_id, OLD.post_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_post_reply_count ON circle_post_replies;
CREATE TRIGGER trigger_update_post_reply_count
    AFTER INSERT OR DELETE ON circle_post_replies
    FOR EACH ROW
    EXECUTE FUNCTION update_post_reply_count();


-- Find similar charts (AstroTwin search)
CREATE OR REPLACE FUNCTION find_astro_twins(
    p_user_id UUID,
    p_similarity_threshold DECIMAL DEFAULT 0.3,
    p_limit INTEGER DEFAULT 100
) RETURNS TABLE (
    profile_id UUID,
    user_id UUID,
    similarity_score DECIMAL,
    feature_metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cv.profile_id,
        cv.user_id,
        (1 - (cv.chart_vector <=> (
            SELECT chart_vector FROM chart_vectors WHERE user_id = p_user_id
        )))::DECIMAL AS similarity_score,
        cv.feature_metadata
    FROM chart_vectors cv
    WHERE cv.user_id != p_user_id
      AND cv.privacy_opt_in = true
      AND cv.visible_in_search = true
      AND (cv.chart_vector <=> (
          SELECT chart_vector FROM chart_vectors WHERE user_id = p_user_id
      )) < p_similarity_threshold
    ORDER BY cv.chart_vector <=> (
        SELECT chart_vector FROM chart_vectors WHERE user_id = p_user_id
    )
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE chart_vectors IS 'Vector representations of birth charts for similarity search (pgvector)';
COMMENT ON TABLE astrotwin_circles IS 'User-created or system-suggested communities of people with similar charts';
COMMENT ON TABLE circle_memberships IS 'User participation in AstroTwin circles';
COMMENT ON TABLE life_outcomes IS 'User-reported life events with success/failure tagging for pattern analysis';
COMMENT ON TABLE pattern_discoveries IS 'System-learned patterns from aggregated chart and outcome data';
COMMENT ON TABLE circle_insights IS 'Shared wisdom and patterns discovered within specific circles';
COMMENT ON TABLE circle_posts IS 'Community posts within circles';
COMMENT ON TABLE circle_post_replies IS 'Threaded replies to circle posts';

COMMENT ON COLUMN chart_vectors.chart_vector IS '384-dimensional vector encoding sun/moon/ascendant, dominant planets, yogas, dasha, life stage';
COMMENT ON COLUMN chart_vectors.privacy_opt_in IS 'User must explicitly opt-in to be discoverable by others';
COMMENT ON COLUMN astrotwin_circles.similarity_threshold IS 'Maximum distance for chart similarity (0.0 = identical, 1.0 = completely different)';
COMMENT ON COLUMN life_outcomes.share_anonymously IS 'Allow this outcome to be used for pattern analysis without identifying the user';


-- ============================================================================
-- MIGRATION COMPLETE!
-- ============================================================================
--
-- Tables Created: 8 (chart_vectors, astrotwin_circles, circle_memberships,
--                    life_outcomes, pattern_discoveries, circle_insights,
--                    circle_posts, circle_post_replies)
--
-- Indexes Created: 20+ (including pgvector HNSW index for fast similarity search)
--
-- Functions Created: 4 (timestamp updates, member count, reply count, twin search)
--
-- Next Steps:
-- 1. Implement chart vectorization service (encode charts to vectors)
-- 2. Implement similarity search API
-- 3. Implement pattern analysis engine
-- 4. Build frontend UI for circles
--
-- ============================================================================
