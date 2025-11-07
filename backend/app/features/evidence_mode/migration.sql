-- Evidence Mode Feature Database Migration
-- Magical 12 Feature #8: Citation-backed trust system
-- Generated: 2025-11-07
-- Description: Creates tables for evidence sources, citations, and validations

-- ============================================================================
-- Source Types Enum
-- ============================================================================
CREATE TYPE evidence_source_type AS ENUM (
    'classical_text',
    'research_paper',
    'expert_opinion',
    'statistical',
    'traditional',
    'modern_study'
);

-- ============================================================================
-- Confidence Levels Enum
-- ============================================================================
CREATE TYPE evidence_confidence_level AS ENUM (
    'very_high',
    'high',
    'medium',
    'low',
    'very_low'
);

-- ============================================================================
-- Validation Status Enum
-- ============================================================================
CREATE TYPE evidence_validation_status AS ENUM (
    'pending',
    'validated',
    'disputed',
    'rejected'
);

-- ============================================================================
-- Evidence Mode Sources Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS evidence_mode_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source identification
    title VARCHAR(500) NOT NULL,
    author VARCHAR(255),
    source_type evidence_source_type NOT NULL,

    -- Content
    description TEXT,
    excerpt TEXT,
    full_text TEXT,

    -- Reference details
    publication_year INTEGER,
    publisher VARCHAR(255),
    isbn_doi VARCHAR(100),
    url VARCHAR(500),
    page_reference VARCHAR(100),

    -- Metadata
    language VARCHAR(50) DEFAULT 'english',
    tags JSONB,
    keywords JSONB,

    -- Quality metrics
    credibility_score FLOAT DEFAULT 0.5 CHECK (credibility_score >= 0.0 AND credibility_score <= 1.0),
    citation_count INTEGER DEFAULT 0,

    -- Status
    is_verified BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID
);

-- Indexes for performance
CREATE INDEX idx_sources_type_verified ON evidence_mode_sources(source_type, is_verified);
CREATE INDEX idx_sources_title_search ON evidence_mode_sources(title);
CREATE INDEX idx_sources_credibility ON evidence_mode_sources(credibility_score DESC);
CREATE INDEX idx_sources_tags ON evidence_mode_sources USING GIN(tags);
CREATE INDEX idx_sources_keywords ON evidence_mode_sources USING GIN(keywords);

-- Full-text search index for title, author, description
CREATE INDEX idx_sources_fulltext ON evidence_mode_sources
    USING GIN(to_tsvector('english', coalesce(title,'') || ' ' || coalesce(author,'') || ' ' || coalesce(description,'')));

-- ============================================================================
-- Evidence Mode Citations Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS evidence_mode_citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Link to source
    source_id UUID NOT NULL REFERENCES evidence_mode_sources(id) ON DELETE CASCADE,

    -- What is being cited
    insight_type VARCHAR(100) NOT NULL,
    insight_text TEXT NOT NULL,
    insight_reference VARCHAR(255),

    -- Citation details
    relevance_score FLOAT DEFAULT 0.5 CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),
    confidence_level evidence_confidence_level DEFAULT 'medium',
    confidence_score FLOAT CHECK (confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0)),

    -- Context
    context JSONB,
    reasoning TEXT,

    -- Usage tracking
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID
);

-- Indexes for performance
CREATE INDEX idx_citations_source_active ON evidence_mode_citations(source_id, is_active);
CREATE INDEX idx_citations_insight_type ON evidence_mode_citations(insight_type);
CREATE INDEX idx_citations_confidence ON evidence_mode_citations(confidence_level);
CREATE INDEX idx_citations_confidence_score ON evidence_mode_citations(confidence_score DESC NULLS LAST);
CREATE INDEX idx_citations_insight_text_search ON evidence_mode_citations USING GIN(to_tsvector('english', insight_text));

-- ============================================================================
-- Evidence Mode Validations Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS evidence_mode_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Link to citation
    citation_id UUID NOT NULL REFERENCES evidence_mode_citations(id) ON DELETE CASCADE,

    -- Validator information
    validator_id UUID NOT NULL,
    validator_name VARCHAR(255),
    validator_credentials VARCHAR(500),

    -- Validation details
    status evidence_validation_status NOT NULL DEFAULT 'pending',
    confidence_adjustment FLOAT CHECK (confidence_adjustment IS NULL OR (confidence_adjustment >= -1.0 AND confidence_adjustment <= 1.0)),

    -- Feedback
    comments TEXT,
    suggestions TEXT,
    alternative_sources JSONB,

    -- Validation metrics
    accuracy_score FLOAT CHECK (accuracy_score IS NULL OR (accuracy_score >= 0.0 AND accuracy_score <= 1.0)),
    relevance_score FLOAT CHECK (relevance_score IS NULL OR (relevance_score >= 0.0 AND relevance_score <= 1.0)),

    -- Status flags
    is_public BOOLEAN DEFAULT TRUE,
    requires_review BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_validations_citation_status ON evidence_mode_validations(citation_id, status);
CREATE INDEX idx_validations_validator ON evidence_mode_validations(validator_id);
CREATE INDEX idx_validations_status ON evidence_mode_validations(status);
CREATE INDEX idx_validations_created ON evidence_mode_validations(created_at DESC);

-- ============================================================================
-- Triggers for updated_at timestamps
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_evidence_mode_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for sources table
CREATE TRIGGER trigger_update_evidence_mode_sources_updated_at
    BEFORE UPDATE ON evidence_mode_sources
    FOR EACH ROW
    EXECUTE FUNCTION update_evidence_mode_updated_at();

-- Trigger for citations table
CREATE TRIGGER trigger_update_evidence_mode_citations_updated_at
    BEFORE UPDATE ON evidence_mode_citations
    FOR EACH ROW
    EXECUTE FUNCTION update_evidence_mode_updated_at();

-- Trigger for validations table
CREATE TRIGGER trigger_update_evidence_mode_validations_updated_at
    BEFORE UPDATE ON evidence_mode_validations
    FOR EACH ROW
    EXECUTE FUNCTION update_evidence_mode_updated_at();

-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE evidence_mode_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_mode_citations ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_mode_validations ENABLE ROW LEVEL SECURITY;

-- Sources: Public sources are readable by all authenticated users
CREATE POLICY "Public sources are viewable by authenticated users"
    ON evidence_mode_sources FOR SELECT
    TO authenticated
    USING (is_public = TRUE);

-- Sources: Users can create sources
CREATE POLICY "Authenticated users can create sources"
    ON evidence_mode_sources FOR INSERT
    TO authenticated
    WITH CHECK (TRUE);

-- Sources: Users can update their own sources
CREATE POLICY "Users can update their own sources"
    ON evidence_mode_sources FOR UPDATE
    TO authenticated
    USING (created_by = auth.uid());

-- Citations: Active citations are readable by all authenticated users
CREATE POLICY "Active citations are viewable by authenticated users"
    ON evidence_mode_citations FOR SELECT
    TO authenticated
    USING (is_active = TRUE);

-- Citations: Users can create citations
CREATE POLICY "Authenticated users can create citations"
    ON evidence_mode_citations FOR INSERT
    TO authenticated
    WITH CHECK (TRUE);

-- Citations: Users can update their own citations
CREATE POLICY "Users can update their own citations"
    ON evidence_mode_citations FOR UPDATE
    TO authenticated
    USING (created_by = auth.uid());

-- Validations: Public validations are readable by all authenticated users
CREATE POLICY "Public validations are viewable by authenticated users"
    ON evidence_mode_validations FOR SELECT
    TO authenticated
    USING (is_public = TRUE);

-- Validations: Users can create validations
CREATE POLICY "Authenticated users can create validations"
    ON evidence_mode_validations FOR INSERT
    TO authenticated
    WITH CHECK (TRUE);

-- Validations: Validators can update their own validations
CREATE POLICY "Validators can update their own validations"
    ON evidence_mode_validations FOR UPDATE
    TO authenticated
    USING (validator_id = auth.uid());

-- ============================================================================
-- Views for Analytics
-- ============================================================================

-- View for citation statistics by insight type
CREATE OR REPLACE VIEW evidence_mode_insight_stats AS
SELECT
    c.insight_type,
    COUNT(DISTINCT c.id) as citation_count,
    COUNT(DISTINCT c.source_id) as unique_sources,
    AVG(c.confidence_score) as avg_confidence,
    MAX(c.confidence_score) as max_confidence,
    AVG(s.credibility_score) as avg_source_credibility,
    COUNT(DISTINCT v.id) as validation_count,
    AVG(v.accuracy_score) as avg_accuracy
FROM evidence_mode_citations c
LEFT JOIN evidence_mode_sources s ON c.source_id = s.id
LEFT JOIN evidence_mode_validations v ON c.id = v.citation_id AND v.status = 'validated'
WHERE c.is_active = TRUE
GROUP BY c.insight_type;

-- View for top sources by citation count
CREATE OR REPLACE VIEW evidence_mode_top_sources AS
SELECT
    s.*,
    COUNT(c.id) as active_citations,
    AVG(c.confidence_score) as avg_citation_confidence,
    COUNT(v.id) as total_validations
FROM evidence_mode_sources s
LEFT JOIN evidence_mode_citations c ON s.id = c.source_id AND c.is_active = TRUE
LEFT JOIN evidence_mode_validations v ON c.id = v.citation_id
WHERE s.is_public = TRUE
GROUP BY s.id
ORDER BY s.credibility_score DESC, active_citations DESC;

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE evidence_mode_sources IS 'Reference sources for astrological insights (classical texts, research papers, expert opinions)';
COMMENT ON TABLE evidence_mode_citations IS 'Links between astrological insights and their supporting evidence sources';
COMMENT ON TABLE evidence_mode_validations IS 'Expert validation and peer review of citations';

COMMENT ON COLUMN evidence_mode_sources.credibility_score IS 'Source credibility rating from 0.0 to 1.0';
COMMENT ON COLUMN evidence_mode_sources.citation_count IS 'Number of times this source has been cited';
COMMENT ON COLUMN evidence_mode_citations.confidence_score IS 'Confidence level for this citation from 0.0 to 1.0';
COMMENT ON COLUMN evidence_mode_validations.confidence_adjustment IS 'Adjustment to citation confidence from validator (-1.0 to 1.0)';

-- ============================================================================
-- End of Migration
-- ============================================================================
