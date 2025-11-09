-- ============================================================================
-- Palmistry Intelligence Module - Database Schema (Corrected v2)
-- Version: 2.0
-- Date: 2025-11-08
-- Matches ORM models in app/models/palmistry.py
-- ============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table 1: palm_photos
-- Stores all captured/uploaded palm images
-- ============================================================================

CREATE TABLE IF NOT EXISTS palm_photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,

    -- Image Classification
    hand_type VARCHAR(10) NOT NULL CHECK (hand_type IN ('left', 'right')),
    view_type VARCHAR(20) NOT NULL CHECK (view_type IN ('front', 'back', 'zoomed', 'thumb_edge', 'side')),
    capture_method VARCHAR(20) NOT NULL CHECK (capture_method IN ('camera', 'upload')),

    -- Image Storage
    image_url TEXT NOT NULL,
    thumbnail_url TEXT,

    -- Image Metadata
    image_metadata JSONB DEFAULT '{}'::jsonb,

    -- Quality Metrics (0-100 scale)
    quality_score FLOAT CHECK (quality_score BETWEEN 0 AND 100),
    focus_score FLOAT CHECK (focus_score BETWEEN 0 AND 100),
    lighting_score FLOAT CHECK (lighting_score BETWEEN 0 AND 100),

    -- Validation Results
    is_hand_detected BOOLEAN DEFAULT FALSE,
    validation_details JSONB DEFAULT '{}'::jsonb,

    -- Device Information
    device_info JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Soft Delete
    deleted_at TIMESTAMPTZ
);

-- Indexes for palm_photos
CREATE INDEX idx_palm_photos_user_created ON palm_photos(user_id, created_at);
CREATE INDEX idx_palm_photos_hand_type ON palm_photos(hand_type);
CREATE INDEX idx_palm_photos_quality ON palm_photos(quality_score);

-- Comments
COMMENT ON TABLE palm_photos IS 'Stores all captured or uploaded palm images with metadata and quality metrics';
COMMENT ON COLUMN palm_photos.quality_score IS 'Overall image quality score (0-100)';
COMMENT ON COLUMN palm_photos.image_metadata IS 'JSON containing image dimensions, format, size, EXIF data, etc.';
COMMENT ON COLUMN palm_photos.validation_details IS 'Validation results and improvement suggestions';

-- ============================================================================
-- Table 2: palm_readings
-- Stores AI-generated palm analysis results
-- ============================================================================

CREATE TABLE IF NOT EXISTS palm_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Keys
    photo_id UUID NOT NULL REFERENCES palm_photos(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    model_id UUID,  -- References ai_models table (soft reference)

    -- Hand Classification
    hand_type VARCHAR(10) NOT NULL CHECK (hand_type IN ('left', 'right')),
    hand_shape VARCHAR(20) CHECK (hand_shape IN ('earth', 'air', 'fire', 'water')),

    -- Detection Results (JSONB for flexibility)
    lines_detected JSONB DEFAULT '[]'::jsonb,
    mounts_detected JSONB DEFAULT '[]'::jsonb,
    special_markings JSONB DEFAULT '[]'::jsonb,
    finger_analysis JSONB DEFAULT '{}'::jsonb,

    -- Predictions
    life_events JSONB DEFAULT '[]'::jsonb,
    personality_traits JSONB DEFAULT '[]'::jsonb,

    -- Quality Metrics
    overall_confidence FLOAT NOT NULL CHECK (overall_confidence BETWEEN 0.0 AND 1.0),
    detection_scores JSONB DEFAULT '{}'::jsonb,

    -- Processing Metadata
    processing_time_ms INTEGER,
    model_version VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for palm_readings
CREATE INDEX idx_palm_readings_photo_id ON palm_readings(photo_id);
CREATE INDEX idx_palm_readings_user_created ON palm_readings(user_id, created_at);
CREATE INDEX idx_palm_readings_confidence ON palm_readings(overall_confidence);

-- Comments
COMMENT ON TABLE palm_readings IS 'AI analysis results for palm readings';
COMMENT ON COLUMN palm_readings.lines_detected IS 'Array of detected palm lines with coordinates and characteristics';
COMMENT ON COLUMN palm_readings.mounts_detected IS 'Array of detected mounts with prominence levels';
COMMENT ON COLUMN palm_readings.overall_confidence IS 'Overall reading confidence (0.0-1.0)';

-- ============================================================================
-- Table 3: palm_interpretations
-- Stores RAG-generated natural language interpretations
-- ============================================================================

CREATE TABLE IF NOT EXISTS palm_interpretations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Keys
    reading_id UUID NOT NULL REFERENCES palm_readings(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,

    -- Interpretation Content
    summary TEXT NOT NULL,
    detailed_analysis TEXT NOT NULL,

    -- Structured Insights
    personality_traits JSONB DEFAULT '[]'::jsonb,
    life_events JSONB DEFAULT '[]'::jsonb,
    recommendations JSONB DEFAULT '[]'::jsonb,

    -- Cross-Domain Correlations
    astrology_correlations JSONB,
    numerology_correlations JSONB,

    -- RAG Metadata
    rag_sources JSONB DEFAULT '[]'::jsonb,
    model_version VARCHAR(50),
    generation_parameters JSONB DEFAULT '{}'::jsonb,

    -- Quality Metrics
    coherence_score FLOAT,
    relevance_score FLOAT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for palm_interpretations
CREATE INDEX idx_palm_interpretations_reading_id ON palm_interpretations(reading_id);
CREATE INDEX idx_palm_interpretations_user_created ON palm_interpretations(user_id, created_at);

-- Comments
COMMENT ON TABLE palm_interpretations IS 'RAG-generated natural language interpretations of palm readings';
COMMENT ON COLUMN palm_interpretations.summary IS 'Brief 2-3 sentence summary';
COMMENT ON COLUMN palm_interpretations.rag_sources IS 'Knowledge base sources used in generation';

-- ============================================================================
-- Table 4: ai_models
-- Tracks AI model versions for reanalysis capability
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Model Identification
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL UNIQUE,
    model_type VARCHAR(50) NOT NULL CHECK (model_type IN (
        'hand_detection',
        'line_detection',
        'mount_detection',
        'shape_classification',
        'rag_model'
    )),

    -- Model Metadata
    model_path TEXT,
    framework VARCHAR(50),
    architecture VARCHAR(100),

    -- Performance Metrics
    accuracy_metrics JSONB DEFAULT '{}'::jsonb,
    training_data_size INTEGER,
    training_date TIMESTAMPTZ,

    -- Deployment Status
    is_active BOOLEAN DEFAULT FALSE NOT NULL,
    deployment_date TIMESTAMPTZ,
    deprecated_date TIMESTAMPTZ,

    -- Additional Metadata
    description TEXT,
    changelog TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for ai_models
CREATE INDEX idx_ai_models_active ON ai_models(is_active, model_type);
CREATE INDEX idx_ai_models_version ON ai_models(model_version);

-- Comments
COMMENT ON TABLE ai_models IS 'Tracks AI model versions for reanalysis and version management';
COMMENT ON COLUMN ai_models.is_active IS 'Whether this model is currently in production';

-- ============================================================================
-- Table 5: reanalysis_queue
-- Queue for reanalyzing photos with updated AI models
-- ============================================================================

CREATE TABLE IF NOT EXISTS reanalysis_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Keys
    photo_id UUID NOT NULL REFERENCES palm_photos(id) ON DELETE CASCADE,

    -- Model Version Tracking
    old_model_version VARCHAR(50),
    new_model_version VARCHAR(50) NOT NULL,

    -- Queue Management
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending',
        'processing',
        'completed',
        'failed'
    )),
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,

    -- Timestamps
    scheduled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Indexes for reanalysis_queue
CREATE INDEX idx_reanalysis_queue_photo_id ON reanalysis_queue(photo_id);
CREATE INDEX idx_reanalysis_queue_status_priority ON reanalysis_queue(status, priority);
CREATE INDEX idx_reanalysis_queue_scheduled ON reanalysis_queue(scheduled_at);

-- Comments
COMMENT ON TABLE reanalysis_queue IS 'Queue for reanalyzing photos when new AI models are deployed';
COMMENT ON COLUMN reanalysis_queue.priority IS 'Processing priority (1=highest, 10=lowest)';

-- ============================================================================
-- Table 6: palm_feedback
-- User feedback on palm interpretations
-- ============================================================================

CREATE TABLE IF NOT EXISTS palm_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Keys
    interpretation_id UUID NOT NULL REFERENCES palm_interpretations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,

    -- Feedback Content
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    feedback_type VARCHAR(50) NOT NULL CHECK (feedback_type IN (
        'accuracy',
        'completeness',
        'clarity',
        'relevance'
    )),
    comments TEXT,

    -- Sentiment Analysis (optional)
    sentiment_score FLOAT CHECK (sentiment_score BETWEEN -1.0 AND 1.0),

    -- Timestamp
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for palm_feedback
CREATE INDEX idx_palm_feedback_interpretation_id ON palm_feedback(interpretation_id);
CREATE INDEX idx_palm_feedback_user_created ON palm_feedback(user_id, created_at);
CREATE INDEX idx_palm_feedback_rating ON palm_feedback(rating);

-- Comments
COMMENT ON TABLE palm_feedback IS 'User feedback on palm interpretations for continuous improvement';
COMMENT ON COLUMN palm_feedback.rating IS 'Rating from 1 to 5';

-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE palm_photos ENABLE ROW LEVEL SECURITY;
ALTER TABLE palm_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE palm_interpretations ENABLE ROW LEVEL SECURITY;
ALTER TABLE palm_feedback ENABLE ROW LEVEL SECURITY;

-- Policies for palm_photos
CREATE POLICY palm_photos_user_policy ON palm_photos
    FOR ALL USING (user_id = auth.uid());

-- Policies for palm_readings
CREATE POLICY palm_readings_user_policy ON palm_readings
    FOR ALL USING (user_id = auth.uid());

-- Policies for palm_interpretations
CREATE POLICY palm_interpretations_user_policy ON palm_interpretations
    FOR ALL USING (user_id = auth.uid());

-- Policies for palm_feedback
CREATE POLICY palm_feedback_user_policy ON palm_feedback
    FOR ALL USING (user_id = auth.uid());

-- ============================================================================
-- Auto-updating Triggers
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at column
CREATE TRIGGER update_palm_photos_updated_at BEFORE UPDATE ON palm_photos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_palm_readings_updated_at BEFORE UPDATE ON palm_readings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_palm_interpretations_updated_at BEFORE UPDATE ON palm_interpretations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_models_updated_at BEFORE UPDATE ON ai_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Views for Easy Querying
-- ============================================================================

CREATE OR REPLACE VIEW v_recent_readings AS
SELECT
    pr.id as reading_id,
    pr.user_id,
    pr.hand_type,
    pr.hand_shape,
    pr.overall_confidence,
    pr.created_at as reading_date,
    pp.thumbnail_url,
    pp.image_url,
    pi.summary,
    pi.id as interpretation_id,
    (SELECT AVG(rating) FROM palm_feedback WHERE interpretation_id = pi.id) as avg_rating
FROM palm_readings pr
LEFT JOIN palm_photos pp ON pr.photo_id = pp.id
LEFT JOIN palm_interpretations pi ON pr.id = pi.reading_id
WHERE pp.deleted_at IS NULL
ORDER BY pr.created_at DESC;

COMMENT ON VIEW v_recent_readings IS 'Recent palm readings with photos and interpretations';

-- ============================================================================
-- Utility Functions
-- ============================================================================

-- Function to get reading statistics for a user
CREATE OR REPLACE FUNCTION get_user_reading_stats(p_user_id UUID)
RETURNS TABLE (
    total_readings BIGINT,
    avg_confidence FLOAT,
    latest_reading_date TIMESTAMPTZ,
    hands_analyzed JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT as total_readings,
        AVG(overall_confidence)::FLOAT as avg_confidence,
        MAX(created_at) as latest_reading_date,
        jsonb_object_agg(hand_type, count) as hands_analyzed
    FROM (
        SELECT
            hand_type,
            overall_confidence,
            created_at,
            COUNT(*) OVER (PARTITION BY hand_type) as count
        FROM palm_readings
        WHERE user_id = p_user_id
    ) subq
    GROUP BY total_readings;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_user_reading_stats IS 'Get reading statistics for a specific user';

-- ============================================================================
-- Seed Data: Initial AI Models
-- ============================================================================

INSERT INTO ai_models (model_name, model_version, model_type, is_active, description) VALUES
    ('MediaPipe Hands', 'v1.0.0-placeholder', 'hand_detection', true, 'Placeholder for hand detection model'),
    ('Palm Line Detector', 'v1.0.0-placeholder', 'line_detection', true, 'Placeholder for line detection model'),
    ('Mount Detector', 'v1.0.0-placeholder', 'mount_detection', true, 'Placeholder for mount detection model'),
    ('Hand Shape Classifier', 'v1.0.0-placeholder', 'shape_classification', true, 'Placeholder for shape classification model'),
    ('GPT-4 RAG', 'gpt-4-turbo-placeholder', 'rag_model', true, 'Placeholder for RAG interpretation model')
ON CONFLICT (model_version) DO NOTHING;

-- ============================================================================
-- Migration Complete
-- ============================================================================

-- Verify tables created
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name LIKE 'palm_%'
ORDER BY table_name;

-- Verify RLS policies
SELECT
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies
WHERE tablename LIKE 'palm_%'
ORDER BY tablename, policyname;

-- Verify seed data
SELECT model_name, model_version, model_type, is_active FROM ai_models ORDER BY model_type;
