-- ============================================================================
-- Palmistry Intelligence Module - Database Schema
-- Version: 1.0
-- Date: 2025-11-08
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
    hand_type VARCHAR(10) NOT NULL CHECK (hand_type IN ('left', 'right')),
    view_type VARCHAR(20) NOT NULL CHECK (view_type IN ('front', 'back', 'zoomed', 'thumb_edge', 'side')),
    capture_method VARCHAR(20) NOT NULL CHECK (capture_method IN ('camera', 'upload')),

    -- Image Storage
    image_url TEXT NOT NULL,
    thumbnail_url TEXT,

    -- Image Metadata
    image_metadata JSONB DEFAULT '{}'::jsonb,
    -- Example: {"width": 1920, "height": 1080, "format": "jpeg", "size_bytes": 245678}

    -- Quality Metrics
    quality_score FLOAT CHECK (quality_score BETWEEN 0 AND 100),
    focus_score FLOAT CHECK (focus_score BETWEEN 0 AND 100),
    lighting_score FLOAT CHECK (lighting_score BETWEEN 0 AND 100),

    -- Capture Information
    capture_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    device_info JSONB DEFAULT '{}'::jsonb,
    -- Example: {"camera": "iPhone 14", "browser": "Chrome", "os": "iOS 17"}

    -- Processing Status
    is_processed BOOLEAN DEFAULT FALSE,
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for palm_photos
CREATE INDEX idx_palm_photos_user_id ON palm_photos(user_id);
CREATE INDEX idx_palm_photos_hand_type ON palm_photos(hand_type);
CREATE INDEX idx_palm_photos_created_at ON palm_photos(created_at DESC);
CREATE INDEX idx_palm_photos_quality_score ON palm_photos(quality_score) WHERE quality_score IS NOT NULL;
CREATE INDEX idx_palm_photos_is_processed ON palm_photos(is_processed) WHERE is_processed = FALSE;

-- Comments
COMMENT ON TABLE palm_photos IS 'Stores all captured or uploaded palm images with metadata and quality metrics';
COMMENT ON COLUMN palm_photos.quality_score IS 'Overall image quality score (0-100)';
COMMENT ON COLUMN palm_photos.image_metadata IS 'JSON containing image dimensions, format, size, etc.';

-- ============================================================================
-- Table 2: palm_readings
-- Stores AI-generated palm analysis results
-- ============================================================================

CREATE TABLE IF NOT EXISTS palm_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    photo_ids UUID[] NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    hand_type VARCHAR(10) NOT NULL CHECK (hand_type IN ('left', 'right', 'both')),

    -- Detection Results
    lines_detected JSONB DEFAULT '{}'::jsonb,
    -- Example: {
    --   "life_line": {"present": true, "quality": "clear", "length": "long", "depth": "deep",
    --                 "breaks": [], "confidence": 0.92},
    --   "head_line": {...}, "heart_line": {...}, "fate_line": {...}
    -- }

    mounts_detected JSONB DEFAULT '{}'::jsonb,
    -- Example: {
    --   "venus": {"prominence": "high", "area": 125.5, "confidence": 0.88},
    --   "jupiter": {...}, "saturn": {...}
    -- }

    -- Shape & Proportions
    hand_shape VARCHAR(20) CHECK (hand_shape IN ('earth', 'air', 'fire', 'water')),
    finger_lengths JSONB DEFAULT '{}'::jsonb,
    -- Example: {"thumb": 65, "index": 78, "middle": 85, "ring": 80, "pinky": 58}

    -- Analysis Results
    personality_traits JSONB DEFAULT '[]'::jsonb,
    health_indicators JSONB DEFAULT '[]'::jsonb,
    career_insights JSONB DEFAULT '[]'::jsonb,
    relationship_patterns JSONB DEFAULT '[]'::jsonb,
    life_events_timeline JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"event": "career_change", "age": 35, "confidence": 0.85, "description": "..."}]

    -- Confidence Scores
    overall_confidence FLOAT CHECK (overall_confidence BETWEEN 0 AND 1),
    line_confidence JSONB DEFAULT '{}'::jsonb,
    mount_confidence JSONB DEFAULT '{}'::jsonb,

    -- Integration with other systems
    astrology_correlation JSONB DEFAULT '{}'::jsonb,
    numerology_correlation JSONB DEFAULT '{}'::jsonb,

    -- Metadata
    processing_time_ms INTEGER,
    analysis_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_archived BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for palm_readings
CREATE INDEX idx_palm_readings_user_id ON palm_readings(user_id);
CREATE INDEX idx_palm_readings_model_version ON palm_readings(model_version);
CREATE INDEX idx_palm_readings_analysis_date ON palm_readings(analysis_date DESC);
CREATE INDEX idx_palm_readings_hand_type ON palm_readings(hand_type);
CREATE INDEX idx_palm_readings_is_archived ON palm_readings(is_archived) WHERE is_archived = FALSE;

-- Comments
COMMENT ON TABLE palm_readings IS 'Stores AI-generated palm analysis results including lines, mounts, and predictions';
COMMENT ON COLUMN palm_readings.lines_detected IS 'JSON containing detected palm lines with characteristics';
COMMENT ON COLUMN palm_readings.mounts_detected IS 'JSON containing detected palm mounts with prominence scores';

-- ============================================================================
-- Table 3: palm_interpretations
-- Stores RAG-generated natural language interpretations
-- ============================================================================

CREATE TABLE IF NOT EXISTS palm_interpretations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reading_id UUID NOT NULL,
    user_id UUID NOT NULL,

    -- Interpretations
    summary TEXT NOT NULL,
    detailed_analysis TEXT NOT NULL,
    life_line_interpretation TEXT,
    head_line_interpretation TEXT,
    heart_line_interpretation TEXT,
    fate_line_interpretation TEXT,
    mount_analysis TEXT,
    hand_shape_analysis TEXT,

    -- Predictions
    life_events JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"event": "career_breakthrough", "timing": "age_32", "confidence": 0.85, "description": "..."}]
    health_predictions JSONB DEFAULT '[]'::jsonb,
    relationship_predictions JSONB DEFAULT '[]'::jsonb,

    -- RAG Metadata
    rag_model_version VARCHAR(50),
    sources_used TEXT[] DEFAULT ARRAY[]::TEXT[],
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),

    -- Feedback
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    user_feedback TEXT,
    accuracy_verification JSONB DEFAULT '{}'::jsonb,
    -- Example: {"prediction_123": {"verified": true, "occurred_at": "2025-06-15"}}

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for palm_interpretations
CREATE INDEX idx_palm_interpretations_reading_id ON palm_interpretations(reading_id);
CREATE INDEX idx_palm_interpretations_user_id ON palm_interpretations(user_id);
CREATE INDEX idx_palm_interpretations_user_rating ON palm_interpretations(user_rating) WHERE user_rating IS NOT NULL;
CREATE INDEX idx_palm_interpretations_created_at ON palm_interpretations(created_at DESC);

-- Comments
COMMENT ON TABLE palm_interpretations IS 'Stores RAG-generated natural language interpretations of palm readings';
COMMENT ON COLUMN palm_interpretations.sources_used IS 'Array of knowledge base sources used in interpretation';

-- ============================================================================
-- Table 4: ai_models
-- Tracks AI model versions for reanalysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    -- Types: hand_detection, line_classification, mount_detection, shape_classification, ensemble
    architecture VARCHAR(100),
    -- Examples: resnet50, efficientnet_b4, vit_base, mediapipe_hands

    -- Performance Metrics
    accuracy FLOAT CHECK (accuracy BETWEEN 0 AND 1),
    precision_score FLOAT CHECK (precision_score BETWEEN 0 AND 1),
    recall_score FLOAT CHECK (recall_score BETWEEN 0 AND 1),
    f1_score FLOAT CHECK (f1_score BETWEEN 0 AND 1),
    inference_time_ms INTEGER,

    -- Deployment
    model_url TEXT,
    model_config JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT FALSE,
    deployment_date TIMESTAMPTZ,
    deprecated_date TIMESTAMPTZ,

    -- Training Metadata
    training_dataset_size INTEGER,
    training_date TIMESTAMPTZ,
    changelog TEXT,
    performance_notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(model_name, version)
);

-- Indexes for ai_models
CREATE INDEX idx_ai_models_is_active ON ai_models(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_ai_models_model_type ON ai_models(model_type);
CREATE INDEX idx_ai_models_deployment_date ON ai_models(deployment_date DESC);

-- Comments
COMMENT ON TABLE ai_models IS 'Tracks AI model versions, performance metrics, and deployment status';
COMMENT ON COLUMN ai_models.is_active IS 'Indicates if this model version is currently in production use';

-- ============================================================================
-- Table 5: reanalysis_queue
-- Manages re-analysis when models are updated
-- ============================================================================

CREATE TABLE IF NOT EXISTS reanalysis_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    photo_id UUID NOT NULL,
    old_model_version VARCHAR(50) NOT NULL,
    new_model_version VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,

    -- Timing
    scheduled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for reanalysis_queue
CREATE INDEX idx_reanalysis_queue_status ON reanalysis_queue(status) WHERE status IN ('pending', 'processing');
CREATE INDEX idx_reanalysis_queue_priority ON reanalysis_queue(priority DESC, scheduled_at ASC);
CREATE INDEX idx_reanalysis_queue_photo_id ON reanalysis_queue(photo_id);

-- Comments
COMMENT ON TABLE reanalysis_queue IS 'Queue for re-analyzing palm photos when new AI models are deployed';
COMMENT ON COLUMN reanalysis_queue.priority IS 'Priority level (1=highest, 10=lowest) for processing order';

-- ============================================================================
-- Table 6: palm_feedback
-- User feedback for continuous improvement
-- ============================================================================

CREATE TABLE IF NOT EXISTS palm_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    reading_id UUID NOT NULL,
    interpretation_id UUID,

    -- Ratings
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    accuracy_rating INTEGER CHECK (accuracy_rating BETWEEN 1 AND 5),
    clarity_rating INTEGER CHECK (clarity_rating BETWEEN 1 AND 5),
    usefulness_rating INTEGER CHECK (usefulness_rating BETWEEN 1 AND 5),

    -- Detailed Feedback
    what_was_accurate TEXT[] DEFAULT ARRAY[]::TEXT[],
    what_was_inaccurate TEXT[] DEFAULT ARRAY[]::TEXT[],
    missing_insights TEXT,
    additional_comments TEXT,

    -- Verification
    verified_predictions JSONB DEFAULT '{}'::jsonb,
    -- Example: {"prediction_id_1": true, "prediction_id_2": false}

    -- Metadata
    feedback_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_verified BOOLEAN DEFAULT FALSE,
    verification_date TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for palm_feedback
CREATE INDEX idx_palm_feedback_reading_id ON palm_feedback(reading_id);
CREATE INDEX idx_palm_feedback_user_id ON palm_feedback(user_id);
CREATE INDEX idx_palm_feedback_rating ON palm_feedback(rating);
CREATE INDEX idx_palm_feedback_feedback_date ON palm_feedback(feedback_date DESC);

-- Comments
COMMENT ON TABLE palm_feedback IS 'Stores user feedback on reading accuracy for continuous model improvement';
COMMENT ON COLUMN palm_feedback.verified_predictions IS 'JSON tracking which predictions were accurate over time';

-- ============================================================================
-- Foreign Key Constraints (if references exist)
-- Note: Uncomment after profiles table exists
-- ============================================================================

-- ALTER TABLE palm_photos
--     ADD CONSTRAINT fk_palm_photos_user
--     FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE;

-- ALTER TABLE palm_readings
--     ADD CONSTRAINT fk_palm_readings_user
--     FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE;

-- ALTER TABLE palm_interpretations
--     ADD CONSTRAINT fk_palm_interpretations_user
--     FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE;

-- ALTER TABLE palm_interpretations
--     ADD CONSTRAINT fk_palm_interpretations_reading
--     FOREIGN KEY (reading_id) REFERENCES palm_readings(id) ON DELETE CASCADE;

-- ALTER TABLE palm_feedback
--     ADD CONSTRAINT fk_palm_feedback_user
--     FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE;

-- ALTER TABLE palm_feedback
--     ADD CONSTRAINT fk_palm_feedback_reading
--     FOREIGN KEY (reading_id) REFERENCES palm_readings(id) ON DELETE CASCADE;

-- ALTER TABLE reanalysis_queue
--     ADD CONSTRAINT fk_reanalysis_queue_photo
--     FOREIGN KEY (photo_id) REFERENCES palm_photos(id) ON DELETE CASCADE;

-- ============================================================================
-- Trigger Functions for updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to all tables
CREATE TRIGGER update_palm_photos_updated_at BEFORE UPDATE ON palm_photos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_palm_readings_updated_at BEFORE UPDATE ON palm_readings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_palm_interpretations_updated_at BEFORE UPDATE ON palm_interpretations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_models_updated_at BEFORE UPDATE ON ai_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reanalysis_queue_updated_at BEFORE UPDATE ON reanalysis_queue
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Initial Data: Seed AI Models
-- ============================================================================

INSERT INTO ai_models (model_name, version, model_type, architecture, is_active, deployment_date)
VALUES
    ('mediapipe_hands', 'v0.8.10', 'hand_detection', 'mediapipe', TRUE, NOW()),
    ('palm_line_detector', 'v1.0.0', 'line_classification', 'unet_resnet50', TRUE, NOW()),
    ('palm_mount_detector', 'v1.0.0', 'mount_detection', 'efficientnet_b4', TRUE, NOW()),
    ('hand_shape_classifier', 'v1.0.0', 'shape_classification', 'resnet34', TRUE, NOW()),
    ('palm_ensemble', 'v1.0.0', 'ensemble', 'transformer_based', TRUE, NOW())
ON CONFLICT (model_name, version) DO NOTHING;

-- ============================================================================
-- Views for Easy Querying
-- ============================================================================

CREATE OR REPLACE VIEW v_recent_readings AS
SELECT
    pr.id,
    pr.user_id,
    pr.hand_type,
    pr.model_version,
    pr.overall_confidence,
    pr.analysis_date,
    pi.summary,
    pi.user_rating,
    ARRAY_AGG(pp.image_url) as image_urls
FROM palm_readings pr
LEFT JOIN palm_interpretations pi ON pr.id = pi.reading_id
LEFT JOIN LATERAL unnest(pr.photo_ids) AS photo_id ON TRUE
LEFT JOIN palm_photos pp ON pp.id = photo_id
WHERE pr.is_archived = FALSE
GROUP BY pr.id, pr.user_id, pr.hand_type, pr.model_version, pr.overall_confidence,
         pr.analysis_date, pi.summary, pi.user_rating
ORDER BY pr.analysis_date DESC;

COMMENT ON VIEW v_recent_readings IS 'Recent palm readings with summary and images';

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
        MAX(analysis_date) as latest_reading_date,
        jsonb_build_object(
            'left', COUNT(*) FILTER (WHERE hand_type = 'left'),
            'right', COUNT(*) FILTER (WHERE hand_type = 'right'),
            'both', COUNT(*) FILTER (WHERE hand_type = 'both')
        ) as hands_analyzed
    FROM palm_readings
    WHERE user_id = p_user_id AND is_archived = FALSE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Grants (if using RLS)
-- ============================================================================

-- Enable RLS on tables
ALTER TABLE palm_photos ENABLE ROW LEVEL SECURITY;
ALTER TABLE palm_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE palm_interpretations ENABLE ROW LEVEL SECURITY;
ALTER TABLE palm_feedback ENABLE ROW LEVEL SECURITY;

-- RLS Policies (users can only see their own data)
CREATE POLICY palm_photos_user_policy ON palm_photos
    FOR ALL USING (user_id = auth.uid());

CREATE POLICY palm_readings_user_policy ON palm_readings
    FOR ALL USING (user_id = auth.uid());

CREATE POLICY palm_interpretations_user_policy ON palm_interpretations
    FOR ALL USING (user_id = auth.uid());

CREATE POLICY palm_feedback_user_policy ON palm_feedback
    FOR ALL USING (user_id = auth.uid());

-- ============================================================================
-- Migration Complete
-- ============================================================================

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE 'Palmistry tables created successfully!';
    RAISE NOTICE 'Tables: palm_photos, palm_readings, palm_interpretations, ai_models, reanalysis_queue, palm_feedback';
    RAISE NOTICE 'Indexes, triggers, and RLS policies applied.';
END $$;
