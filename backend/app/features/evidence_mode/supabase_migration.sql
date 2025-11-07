-- ============================================================================
-- Evidence Mode - Supabase Migration Script
-- ============================================================================
-- Run this script in Supabase SQL Editor (Database → SQL Editor → New Query)
-- This combines both schema creation and seed data
-- ============================================================================

-- ============================================================================
-- Step 1: Create Enums
-- ============================================================================

CREATE TYPE evidence_source_type AS ENUM (
    'classical_text',
    'research_paper',
    'expert_opinion',
    'statistical',
    'traditional',
    'modern_study'
);

CREATE TYPE evidence_confidence_level AS ENUM (
    'very_high',
    'high',
    'medium',
    'low',
    'very_low'
);

CREATE TYPE evidence_validation_status AS ENUM (
    'pending',
    'validated',
    'disputed',
    'rejected'
);

-- ============================================================================
-- Step 2: Create Tables
-- ============================================================================

-- Evidence Sources Table
CREATE TABLE evidence_mode_sources (
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
    publication_year INTEGER CHECK (publication_year >= -3000 AND publication_year <= 2100),
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
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by UUID REFERENCES auth.users(id)
);

-- Evidence Citations Table
CREATE TABLE evidence_mode_citations (
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
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),

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
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by UUID REFERENCES auth.users(id)
);

-- Evidence Validations Table
CREATE TABLE evidence_mode_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Link to citation
    citation_id UUID NOT NULL REFERENCES evidence_mode_citations(id) ON DELETE CASCADE,

    -- Validator information
    validator_id UUID NOT NULL REFERENCES auth.users(id),
    validator_name VARCHAR(255),
    validator_credentials VARCHAR(500),

    -- Validation details
    status evidence_validation_status NOT NULL DEFAULT 'pending',
    confidence_adjustment FLOAT CHECK (confidence_adjustment >= -1.0 AND confidence_adjustment <= 1.0),

    -- Feedback
    comments TEXT,
    suggestions TEXT,
    alternative_sources JSONB,

    -- Validation metrics
    accuracy_score FLOAT CHECK (accuracy_score >= 0.0 AND accuracy_score <= 1.0),
    relevance_score FLOAT CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),

    -- Status flags
    is_public BOOLEAN DEFAULT TRUE,
    requires_review BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    reviewed_at TIMESTAMPTZ
);

-- ============================================================================
-- Step 3: Create Indexes
-- ============================================================================

-- Sources indexes
CREATE INDEX idx_sources_type ON evidence_mode_sources(source_type);
CREATE INDEX idx_sources_verified ON evidence_mode_sources(is_verified);
CREATE INDEX idx_sources_public ON evidence_mode_sources(is_public);
CREATE INDEX idx_sources_type_verified ON evidence_mode_sources(source_type, is_verified);
CREATE INDEX idx_sources_created_by ON evidence_mode_sources(created_by);
CREATE INDEX idx_sources_fulltext ON evidence_mode_sources
    USING GIN(to_tsvector('english', coalesce(title,'') || ' ' || coalesce(author,'') || ' ' || coalesce(description,'')));

-- Citations indexes
CREATE INDEX idx_citations_source ON evidence_mode_citations(source_id);
CREATE INDEX idx_citations_insight_type ON evidence_mode_citations(insight_type);
CREATE INDEX idx_citations_confidence ON evidence_mode_citations(confidence_level);
CREATE INDEX idx_citations_active ON evidence_mode_citations(is_active);
CREATE INDEX idx_citations_source_active ON evidence_mode_citations(source_id, is_active);
CREATE INDEX idx_citations_created_by ON evidence_mode_citations(created_by);

-- Validations indexes
CREATE INDEX idx_validations_citation ON evidence_mode_validations(citation_id);
CREATE INDEX idx_validations_validator ON evidence_mode_validations(validator_id);
CREATE INDEX idx_validations_status ON evidence_mode_validations(status);
CREATE INDEX idx_validations_citation_status ON evidence_mode_validations(citation_id, status);

-- ============================================================================
-- Step 4: Enable Row Level Security (RLS)
-- ============================================================================

ALTER TABLE evidence_mode_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_mode_citations ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_mode_validations ENABLE ROW LEVEL SECURITY;

-- RLS Policies for Sources
CREATE POLICY "Public sources are viewable by everyone"
    ON evidence_mode_sources FOR SELECT
    USING (is_public = true);

CREATE POLICY "Users can view their own sources"
    ON evidence_mode_sources FOR SELECT
    USING (auth.uid() = created_by);

CREATE POLICY "Authenticated users can create sources"
    ON evidence_mode_sources FOR INSERT
    WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users can update their own sources"
    ON evidence_mode_sources FOR UPDATE
    USING (auth.uid() = created_by);

CREATE POLICY "Users can delete their own sources"
    ON evidence_mode_sources FOR DELETE
    USING (auth.uid() = created_by);

-- RLS Policies for Citations
CREATE POLICY "Active citations are viewable by everyone"
    ON evidence_mode_citations FOR SELECT
    USING (is_active = true);

CREATE POLICY "Users can view their own citations"
    ON evidence_mode_citations FOR SELECT
    USING (auth.uid() = created_by);

CREATE POLICY "Authenticated users can create citations"
    ON evidence_mode_citations FOR INSERT
    WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users can update their own citations"
    ON evidence_mode_citations FOR UPDATE
    USING (auth.uid() = created_by);

-- RLS Policies for Validations
CREATE POLICY "Public validations are viewable by everyone"
    ON evidence_mode_validations FOR SELECT
    USING (is_public = true);

CREATE POLICY "Validators can view their own validations"
    ON evidence_mode_validations FOR SELECT
    USING (auth.uid() = validator_id);

CREATE POLICY "Authenticated users can create validations"
    ON evidence_mode_validations FOR INSERT
    WITH CHECK (auth.uid() = validator_id);

CREATE POLICY "Validators can update their own validations"
    ON evidence_mode_validations FOR UPDATE
    USING (auth.uid() = validator_id);

-- ============================================================================
-- Step 5: Create Triggers for Updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_sources_updated_at
    BEFORE UPDATE ON evidence_mode_sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_citations_updated_at
    BEFORE UPDATE ON evidence_mode_citations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_validations_updated_at
    BEFORE UPDATE ON evidence_mode_validations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Step 6: Insert Seed Data - Classical Texts
-- ============================================================================

INSERT INTO evidence_mode_sources (
    title,
    author,
    source_type,
    description,
    excerpt,
    publication_year,
    language,
    tags,
    keywords,
    credibility_score,
    is_verified,
    is_public
) VALUES
(
    'Brihat Parashara Hora Shastra (BPHS)',
    'Maharishi Parashara',
    'classical_text',
    'The foundational text of Vedic astrology, containing the core principles taught by Maharishi Parashara to his disciples. Covers houses, planets, yogas, dashas, and predictive techniques.',
    'The text covers planetary influences, house significations, yogas, dasha systems, and comprehensive predictive methodologies.',
    -500,
    'sanskrit',
    '["classical", "vedic", "foundational", "yogas", "dashas", "houses"]',
    '["parashara", "bphs", "hora", "shastra", "planets", "houses", "yogas"]',
    0.98,
    TRUE,
    TRUE
),
(
    'Jataka Parijata',
    'Vaidyanatha Dikshita',
    'classical_text',
    'A comprehensive treatise on Vedic astrology written in the 15th century CE. Known for its precise rules on chart interpretation, yogas, and predictive techniques.',
    'Detailed analysis of planetary combinations, yogas, and their effects on various life areas.',
    1450,
    'sanskrit',
    '["classical", "vedic", "yogas", "predictions"]',
    '["jataka", "parijata", "vaidyanatha", "combinations", "effects"]',
    0.95,
    TRUE,
    TRUE
),
(
    'Phaladeepika',
    'Mantreswara',
    'classical_text',
    'A classical text focusing on predictive astrology and interpretation of planetary positions. Written in the 14th century CE, it provides clear rules for chart analysis.',
    'Systematic approach to analyzing planetary strength, yogas, and making predictions about life events.',
    1350,
    'sanskrit',
    '["classical", "predictions", "analysis", "strength"]',
    '["phaladeepika", "mantreswara", "planetary", "strength", "predictions"]',
    0.94,
    TRUE,
    TRUE
),
(
    'Saravali',
    'Kalyana Varma',
    'classical_text',
    'An ancient text covering all aspects of Vedic astrology including planetary effects, yogas, dashas, and transits. One of the most comprehensive classical works.',
    'Extensive coverage of planetary combinations, their effects, and timing of events through dasha systems.',
    800,
    'sanskrit',
    '["classical", "comprehensive", "yogas", "dashas", "transits"]',
    '["saravali", "kalyana", "varma", "planetary", "effects", "dashas"]',
    0.96,
    TRUE,
    TRUE
),
(
    'Brihat Jataka',
    'Varahamihira',
    'classical_text',
    'One of the most authoritative classical texts on Vedic astrology by the legendary Varahamihira. Covers natal astrology, planetary combinations, and predictive principles.',
    'Comprehensive treatment of planetary influences, house significations, and yogas with mathematical precision.',
    505,
    'sanskrit',
    '["classical", "authoritative", "varahamihira", "natal", "yogas"]',
    '["brihat", "jataka", "varahamihira", "natal", "combinations"]',
    0.97,
    TRUE,
    TRUE
);

-- ============================================================================
-- Step 7: Insert Sample Citations
-- ============================================================================

-- Raj Yoga Citation
INSERT INTO evidence_mode_citations (
    source_id,
    insight_type,
    insight_text,
    insight_reference,
    confidence_level,
    confidence_score,
    relevance_score,
    context,
    reasoning,
    is_active
)
SELECT
    id,
    'yoga',
    'Raj Yoga is formed when lords of Kendra (1st, 4th, 7th, 10th) and Trikona (1st, 5th, 9th) houses combine or aspect each other',
    'raj_yoga_definition',
    'very_high',
    0.95,
    0.98,
    '{"yoga_type": "raj_yoga", "houses": ["kendra", "trikona"], "effect": "power_and_authority"}',
    'Classical definition from BPHS Chapter 41, widely accepted across all schools of Vedic astrology',
    TRUE
FROM evidence_mode_sources
WHERE title = 'Brihat Parashara Hora Shastra (BPHS)'
LIMIT 1;

-- Gaja Kesari Yoga Citation
INSERT INTO evidence_mode_citations (
    source_id,
    insight_type,
    insight_text,
    insight_reference,
    confidence_level,
    confidence_score,
    relevance_score,
    context,
    reasoning,
    is_active
)
SELECT
    id,
    'yoga',
    'Gaja Kesari Yoga is formed when Jupiter is in a kendra (angular house) from the Moon, bestowing intelligence, wisdom, and prosperity',
    'gaja_kesari_yoga',
    'very_high',
    0.96,
    0.97,
    '{"yoga_type": "gaja_kesari", "planets": ["jupiter", "moon"], "position": "kendra", "effects": ["intelligence", "wisdom", "prosperity"]}',
    'One of the most celebrated yogas, mentioned in Brihat Jataka and extensively described in classical literature',
    TRUE
FROM evidence_mode_sources
WHERE title = 'Brihat Jataka'
LIMIT 1;

-- ============================================================================
-- Step 8: Create Summary View
-- ============================================================================

CREATE OR REPLACE VIEW evidence_mode_summary AS
SELECT
    'sources' AS entity_type,
    COUNT(*) AS total_count,
    COUNT(*) FILTER (WHERE is_verified = true) AS verified_count,
    COUNT(*) FILTER (WHERE is_public = true) AS public_count
FROM evidence_mode_sources
UNION ALL
SELECT
    'citations' AS entity_type,
    COUNT(*) AS total_count,
    COUNT(*) FILTER (WHERE is_active = true) AS verified_count,
    COUNT(*) FILTER (WHERE confidence_level IN ('very_high', 'high')) AS public_count
FROM evidence_mode_citations
UNION ALL
SELECT
    'validations' AS entity_type,
    COUNT(*) AS total_count,
    COUNT(*) FILTER (WHERE status = 'validated') AS verified_count,
    COUNT(*) FILTER (WHERE is_public = true) AS public_count
FROM evidence_mode_validations;

-- ============================================================================
-- Step 9: Verification Query
-- ============================================================================

-- Display migration summary
DO $$
DECLARE
    source_count INTEGER;
    citation_count INTEGER;
    validation_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO source_count FROM evidence_mode_sources;
    SELECT COUNT(*) INTO citation_count FROM evidence_mode_citations;
    SELECT COUNT(*) INTO validation_count FROM evidence_mode_validations;

    RAISE NOTICE '========================================';
    RAISE NOTICE 'Evidence Mode Migration Complete!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Sources created: %', source_count;
    RAISE NOTICE 'Citations created: %', citation_count;
    RAISE NOTICE 'Validations created: %', validation_count;
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Next: Enable FEATURE_EVIDENCE_MODE=true';
    RAISE NOTICE '========================================';
END $$;

-- Final verification query
SELECT * FROM evidence_mode_summary;
