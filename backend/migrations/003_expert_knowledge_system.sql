-- Expert Knowledge Management System Migration
-- Created: 2025-11-10
-- Description: Creates tables for expert contributions, reviews, and impact tracking

-- ============================================================================
-- 1. Expert Contributions Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS expert_contributions (
    id SERIAL PRIMARY KEY,
    expert_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Contribution Classification
    contribution_type VARCHAR(20) NOT NULL CHECK (contribution_type IN ('additive', 'incremental', 'update')),
    category VARCHAR(50) NOT NULL CHECK (category IN ('yoga', 'dasha', 'transit', 'house', 'planet', 'aspect', 'varga', 'remedy')),
    subcategory VARCHAR(100),

    -- Content
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    rule_definition TEXT,
    example_charts TEXT,
    expected_impact TEXT,

    -- Technical Details
    algorithm_changes TEXT,
    affected_modules TEXT[],
    test_cases JSONB,

    -- References
    classical_reference TEXT,
    modern_reference TEXT,
    research_data JSONB,

    -- Metadata
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'under_review', 'approved', 'implemented', 'rejected')),
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'critical')),
    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 10),

    -- Versioning
    version INTEGER DEFAULT 1,
    replaces_contribution_id INTEGER REFERENCES expert_contributions(id) ON DELETE SET NULL,

    -- Review Process
    reviewed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT,

    -- Implementation
    implemented_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    implemented_at TIMESTAMP WITH TIME ZONE,
    implementation_notes TEXT,
    git_commit_hash VARCHAR(40),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for expert_contributions
CREATE INDEX idx_expert_contributions_expert_id ON expert_contributions(expert_id);
CREATE INDEX idx_expert_contributions_status ON expert_contributions(status);
CREATE INDEX idx_expert_contributions_category ON expert_contributions(category);
CREATE INDEX idx_expert_contributions_type ON expert_contributions(contribution_type);
CREATE INDEX idx_expert_contributions_priority ON expert_contributions(priority);
CREATE INDEX idx_expert_contributions_created_at ON expert_contributions(created_at DESC);

-- ============================================================================
-- 2. Expert Contribution Comments Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS expert_contribution_comments (
    id SERIAL PRIMARY KEY,
    contribution_id INTEGER NOT NULL REFERENCES expert_contributions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    comment TEXT NOT NULL,
    comment_type VARCHAR(20) DEFAULT 'general' CHECK (comment_type IN ('general', 'question', 'suggestion', 'concern', 'support')),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for comments
CREATE INDEX idx_expert_comments_contribution ON expert_contribution_comments(contribution_id);
CREATE INDEX idx_expert_comments_user ON expert_contribution_comments(user_id);
CREATE INDEX idx_expert_comments_created_at ON expert_contribution_comments(created_at DESC);

-- ============================================================================
-- 3. Expert Contribution Votes Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS expert_contribution_votes (
    id SERIAL PRIMARY KEY,
    contribution_id INTEGER NOT NULL REFERENCES expert_contributions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    vote INTEGER NOT NULL CHECK (vote IN (-1, 1)), -- -1 downvote, 1 upvote
    rationale TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Prevent duplicate votes from same user
    UNIQUE(contribution_id, user_id)
);

-- Indexes for votes
CREATE INDEX idx_expert_votes_contribution ON expert_contribution_votes(contribution_id);
CREATE INDEX idx_expert_votes_user ON expert_contribution_votes(user_id);

-- ============================================================================
-- 4. Expert Impact Tracking Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS expert_impact_tracking (
    id SERIAL PRIMARY KEY,
    contribution_id INTEGER NOT NULL REFERENCES expert_contributions(id) ON DELETE CASCADE,
    chart_id UUID, -- Optional reference to specific chart

    -- Metrics
    prediction_before JSONB,
    prediction_after JSONB,
    accuracy_improvement FLOAT,

    -- Validation
    user_feedback TEXT,
    validated BOOLEAN DEFAULT FALSE,
    validated_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for impact tracking
CREATE INDEX idx_expert_impact_contribution ON expert_impact_tracking(contribution_id);
CREATE INDEX idx_expert_impact_chart ON expert_impact_tracking(chart_id);
CREATE INDEX idx_expert_impact_validated ON expert_impact_tracking(validated);

-- ============================================================================
-- 5. Expert Statistics View
-- ============================================================================
CREATE OR REPLACE VIEW expert_contribution_stats AS
SELECT
    ec.id,
    ec.expert_id,
    ec.title,
    ec.status,
    ec.category,
    ec.contribution_type,
    ec.created_at,

    -- Vote counts
    COALESCE(SUM(CASE WHEN v.vote = 1 THEN 1 ELSE 0 END), 0) as upvotes,
    COALESCE(SUM(CASE WHEN v.vote = -1 THEN 1 ELSE 0 END), 0) as downvotes,
    COALESCE(SUM(v.vote), 0) as net_votes,

    -- Comment count
    (SELECT COUNT(*) FROM expert_contribution_comments WHERE contribution_id = ec.id) as comment_count,

    -- Impact metrics
    (SELECT AVG(accuracy_improvement) FROM expert_impact_tracking WHERE contribution_id = ec.id AND validated = TRUE) as avg_accuracy_improvement,
    (SELECT COUNT(*) FROM expert_impact_tracking WHERE contribution_id = ec.id AND validated = TRUE) as validated_impact_count

FROM expert_contributions ec
LEFT JOIN expert_contribution_votes v ON ec.id = v.contribution_id
GROUP BY ec.id;

-- ============================================================================
-- 6. Expert Leaderboard View
-- ============================================================================
CREATE OR REPLACE VIEW expert_leaderboard AS
SELECT
    u.id as expert_id,
    u.email,

    -- Contribution counts
    COUNT(ec.id) as total_contributions,
    COUNT(CASE WHEN ec.status = 'approved' THEN 1 END) as approved_contributions,
    COUNT(CASE WHEN ec.status = 'implemented' THEN 1 END) as implemented_contributions,
    COUNT(CASE WHEN ec.status = 'rejected' THEN 1 END) as rejected_contributions,

    -- Vote summary
    COALESCE(SUM(v.vote), 0) as total_votes,

    -- Impact summary
    COALESCE(AVG(it.accuracy_improvement), 0) as avg_impact,

    -- Approval rate
    CASE
        WHEN COUNT(ec.id) > 0
        THEN ROUND(COUNT(CASE WHEN ec.status IN ('approved', 'implemented') THEN 1 END)::numeric / COUNT(ec.id)::numeric * 100, 2)
        ELSE 0
    END as approval_rate_percentage

FROM auth.users u
LEFT JOIN expert_contributions ec ON u.id = ec.expert_id
LEFT JOIN expert_contribution_votes v ON ec.id = v.contribution_id
LEFT JOIN expert_impact_tracking it ON ec.id = it.contribution_id AND it.validated = TRUE
GROUP BY u.id, u.email
HAVING COUNT(ec.id) > 0
ORDER BY approved_contributions DESC, total_votes DESC;

-- ============================================================================
-- 7. Updated Timestamp Trigger
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to expert_contributions
CREATE TRIGGER update_expert_contributions_updated_at
    BEFORE UPDATE ON expert_contributions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to expert_contribution_comments
CREATE TRIGGER update_expert_comments_updated_at
    BEFORE UPDATE ON expert_contribution_comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 8. Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE expert_contributions ENABLE ROW LEVEL SECURITY;
ALTER TABLE expert_contribution_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE expert_contribution_votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE expert_impact_tracking ENABLE ROW LEVEL SECURITY;

-- Contributions: Anyone can view, only authenticated users can create/update their own
CREATE POLICY "Anyone can view contributions" ON expert_contributions
    FOR SELECT USING (true);

CREATE POLICY "Users can create their own contributions" ON expert_contributions
    FOR INSERT WITH CHECK (auth.uid() = expert_id);

CREATE POLICY "Users can update their own pending contributions" ON expert_contributions
    FOR UPDATE USING (auth.uid() = expert_id AND status = 'pending');

-- Comments: Anyone can view, authenticated users can create
CREATE POLICY "Anyone can view comments" ON expert_contribution_comments
    FOR SELECT USING (true);

CREATE POLICY "Authenticated users can create comments" ON expert_contribution_comments
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own comments" ON expert_contribution_comments
    FOR UPDATE USING (auth.uid() = user_id);

-- Votes: Anyone can view, authenticated users can vote once per contribution
CREATE POLICY "Anyone can view votes" ON expert_contribution_votes
    FOR SELECT USING (true);

CREATE POLICY "Authenticated users can vote" ON expert_contribution_votes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own votes" ON expert_contribution_votes
    FOR UPDATE USING (auth.uid() = user_id);

-- Impact: Anyone can view, only system/admins can create
CREATE POLICY "Anyone can view impact tracking" ON expert_impact_tracking
    FOR SELECT USING (true);

-- ============================================================================
-- 9. Sample Data (Optional - for testing)
-- ============================================================================

-- Uncomment below to insert sample data for testing
/*
-- Insert a sample contribution
INSERT INTO expert_contributions (
    expert_id,
    contribution_type,
    category,
    subcategory,
    title,
    description,
    rule_definition,
    expected_impact,
    priority,
    confidence_level,
    classical_reference
) VALUES (
    (SELECT id FROM auth.users LIMIT 1), -- Replace with actual user ID
    'additive',
    'yoga',
    'raj_yoga',
    'Enhanced Budha-Aditya Yoga',
    'When Mercury and Sun are within 3 degrees in Kendra houses (1,4,7,10), and aspected by Jupiter, the native gains exceptional intelligence and administrative abilities.',
    'Sun-Mercury conjunction (< 3°) in Kendra houses (1,4,7,10) + Jupiter aspect → Enhanced Budha-Aditya Yoga',
    'Increase intelligence and career success predictions by 20-30%',
    'high',
    8,
    'Brihat Parashara Hora Shastra, Chapter 41, Verse 15-17'
);
*/

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- Run this script on your Supabase database via SQL Editor
-- Tables created: 4 main tables + 2 views
-- Indexes: 15 indexes for optimal query performance
-- RLS Policies: Security enabled with appropriate access controls
