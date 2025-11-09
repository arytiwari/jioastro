-- =====================================================
-- REALITY CHECK LOOP MIGRATION
-- Magical 12 Feature #10: Learning from prediction outcomes
-- =====================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLE: predictions
-- Store all predictions made by the system
-- =====================================================
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,

    -- Prediction metadata
    prediction_type TEXT NOT NULL,  -- 'dasha_prediction', 'transit_prediction', 'compatibility', 'career', 'health', etc.
    prediction_category TEXT NOT NULL,  -- 'career', 'relationships', 'health', 'finances', 'spiritual', 'general'

    -- Source information
    source_type TEXT NOT NULL,  -- 'ai_query', 'reading', 'chart_analysis', 'dasha_period', 'transit'
    source_id UUID,  -- Reference to query_id, reading_id, etc.

    -- Prediction content
    prediction_text TEXT NOT NULL,  -- The actual prediction made
    prediction_summary TEXT,  -- Short summary for display
    confidence_level TEXT DEFAULT 'medium',  -- 'low', 'medium', 'high', 'very_high'

    -- Timeframe
    prediction_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- When prediction was made
    expected_timeframe_start DATE,  -- When prediction should start manifesting
    expected_timeframe_end DATE,  -- When prediction should complete
    timeframe_description TEXT,  -- e.g., "Within 3 months", "During Jupiter dasha"

    -- Astrological context
    astrological_context JSONB,  -- Planet positions, dasha periods, transits at time of prediction
    key_factors JSONB,  -- Important yogas, aspects, planetary positions

    -- Status tracking
    status TEXT DEFAULT 'active',  -- 'active', 'pending_outcome', 'verified', 'rejected', 'expired'
    reminder_sent BOOLEAN DEFAULT FALSE,

    -- Metadata
    tags TEXT[],  -- User-defined tags for categorization
    notes TEXT,  -- Additional notes

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for predictions
CREATE INDEX idx_predictions_user_id ON predictions(user_id);
CREATE INDEX idx_predictions_profile_id ON predictions(profile_id);
CREATE INDEX idx_predictions_status ON predictions(status);
CREATE INDEX idx_predictions_category ON predictions(prediction_category);
CREATE INDEX idx_predictions_type ON predictions(prediction_type);
CREATE INDEX idx_predictions_timeframe_end ON predictions(expected_timeframe_end);
CREATE INDEX idx_predictions_created_at ON predictions(created_at DESC);

-- =====================================================
-- TABLE: prediction_outcomes
-- Store actual outcomes reported by users
-- =====================================================
CREATE TABLE IF NOT EXISTS prediction_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID NOT NULL REFERENCES predictions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Outcome data
    outcome_occurred BOOLEAN NOT NULL,  -- Did the prediction happen?
    actual_date DATE,  -- When did it actually happen?
    outcome_description TEXT NOT NULL,  -- User's description of what happened

    -- Accuracy assessment
    accuracy_score INTEGER CHECK (accuracy_score >= 0 AND accuracy_score <= 100),  -- 0-100% how accurate
    timing_accuracy TEXT,  -- 'early', 'on_time', 'late', 'significantly_late'
    severity_match TEXT,  -- 'understated', 'accurate', 'overstated'

    -- Details
    what_matched TEXT,  -- What aspects of the prediction were accurate
    what_differed TEXT,  -- What aspects were different
    additional_events TEXT,  -- Any related events not predicted

    -- User feedback
    helpfulness_rating INTEGER CHECK (helpfulness_rating >= 1 AND helpfulness_rating <= 5),
    would_trust_again BOOLEAN,

    -- Metadata
    verified BOOLEAN DEFAULT FALSE,  -- Admin/expert verification
    verification_notes TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(prediction_id)  -- One outcome per prediction
);

-- Indexes for prediction_outcomes
CREATE INDEX idx_outcomes_prediction_id ON prediction_outcomes(prediction_id);
CREATE INDEX idx_outcomes_user_id ON prediction_outcomes(user_id);
CREATE INDEX idx_outcomes_occurred ON prediction_outcomes(outcome_occurred);
CREATE INDEX idx_outcomes_accuracy_score ON prediction_outcomes(accuracy_score DESC);

-- =====================================================
-- TABLE: learning_insights
-- Store insights learned from prediction outcomes
-- =====================================================
CREATE TABLE IF NOT EXISTS learning_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Insight metadata
    insight_type TEXT NOT NULL,  -- 'pattern', 'correlation', 'weakness', 'strength', 'improvement'
    category TEXT NOT NULL,  -- Same categories as predictions

    -- Insight content
    title TEXT NOT NULL,
    description TEXT NOT NULL,

    -- Statistical backing
    sample_size INTEGER NOT NULL,  -- How many predictions analyzed
    accuracy_rate NUMERIC(5, 2),  -- Overall accuracy percentage
    confidence_interval NUMERIC(5, 2),  -- Statistical confidence

    -- Related factors
    astrological_factors JSONB,  -- Common astrological patterns
    successful_patterns JSONB,  -- What works well
    failure_patterns JSONB,  -- What doesn't work

    -- Impact
    impact_level TEXT DEFAULT 'medium',  -- 'low', 'medium', 'high'
    actionable_recommendations TEXT[],  -- What to improve

    -- Tracking
    applied BOOLEAN DEFAULT FALSE,
    applied_at TIMESTAMPTZ,
    effectiveness_score INTEGER CHECK (effectiveness_score >= 0 AND effectiveness_score <= 100),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for learning_insights
CREATE INDEX idx_insights_type ON learning_insights(insight_type);
CREATE INDEX idx_insights_category ON learning_insights(category);
CREATE INDEX idx_insights_accuracy_rate ON learning_insights(accuracy_rate DESC);
CREATE INDEX idx_insights_applied ON learning_insights(applied);

-- =====================================================
-- TABLE: accuracy_metrics
-- Aggregated accuracy statistics per user/category
-- =====================================================
CREATE TABLE IF NOT EXISTS accuracy_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,  -- NULL for global metrics

    -- Scope
    metric_scope TEXT NOT NULL,  -- 'user', 'category', 'type', 'global', 'astrologer'
    scope_value TEXT,  -- User ID, category name, type name, etc.

    -- Time period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Prediction statistics
    total_predictions INTEGER DEFAULT 0,
    verified_predictions INTEGER DEFAULT 0,  -- Have outcomes
    accurate_predictions INTEGER DEFAULT 0,  -- Outcome occurred as predicted

    -- Accuracy rates
    overall_accuracy_rate NUMERIC(5, 2),  -- Percentage of accurate predictions
    timing_accuracy_rate NUMERIC(5, 2),  -- How often timing was correct
    severity_accuracy_rate NUMERIC(5, 2),  -- How often severity matched

    -- Confidence calibration
    low_confidence_accuracy NUMERIC(5, 2),
    medium_confidence_accuracy NUMERIC(5, 2),
    high_confidence_accuracy NUMERIC(5, 2),
    very_high_confidence_accuracy NUMERIC(5, 2),

    -- User satisfaction
    avg_helpfulness_rating NUMERIC(3, 2),
    trust_rate NUMERIC(5, 2),  -- Percentage who would trust again

    -- Category breakdown
    category_breakdown JSONB,  -- Accuracy by category
    type_breakdown JSONB,  -- Accuracy by prediction type

    -- Trends
    trend_direction TEXT,  -- 'improving', 'stable', 'declining'
    trend_percentage NUMERIC(5, 2),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, metric_scope, scope_value, period_start, period_end)
);

-- Indexes for accuracy_metrics
CREATE INDEX idx_metrics_user_id ON accuracy_metrics(user_id);
CREATE INDEX idx_metrics_scope ON accuracy_metrics(metric_scope, scope_value);
CREATE INDEX idx_metrics_period ON accuracy_metrics(period_start, period_end);
CREATE INDEX idx_metrics_accuracy ON accuracy_metrics(overall_accuracy_rate DESC);

-- =====================================================
-- TABLE: prediction_reminders
-- Track reminders sent to users about predictions
-- =====================================================
CREATE TABLE IF NOT EXISTS prediction_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID NOT NULL REFERENCES predictions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Reminder details
    reminder_type TEXT NOT NULL,  -- 'timeframe_approaching', 'timeframe_reached', 'timeframe_passed', 'followup'
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- User interaction
    opened BOOLEAN DEFAULT FALSE,
    opened_at TIMESTAMPTZ,
    responded BOOLEAN DEFAULT FALSE,
    responded_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for prediction_reminders
CREATE INDEX idx_reminders_prediction_id ON prediction_reminders(prediction_id);
CREATE INDEX idx_reminders_user_id ON prediction_reminders(user_id);
CREATE INDEX idx_reminders_sent_at ON prediction_reminders(sent_at DESC);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE prediction_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE accuracy_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE prediction_reminders ENABLE ROW LEVEL SECURITY;

-- Predictions policies
CREATE POLICY "Users can view own predictions"
ON predictions FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own predictions"
ON predictions FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own predictions"
ON predictions FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own predictions"
ON predictions FOR DELETE
USING (auth.uid() = user_id);

-- Prediction outcomes policies
CREATE POLICY "Users can view own outcomes"
ON prediction_outcomes FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own outcomes"
ON prediction_outcomes FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own outcomes"
ON prediction_outcomes FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own outcomes"
ON prediction_outcomes FOR DELETE
USING (auth.uid() = user_id);

-- Learning insights policies (public read for all authenticated users)
CREATE POLICY "Authenticated users can view all insights"
ON learning_insights FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Only admins can insert insights"
ON learning_insights FOR INSERT
TO authenticated
WITH CHECK (false);  -- Will be managed by backend service

-- Accuracy metrics policies
CREATE POLICY "Users can view own metrics"
ON accuracy_metrics FOR SELECT
USING (auth.uid() = user_id OR user_id IS NULL);  -- Own metrics + global metrics

CREATE POLICY "Users can view global metrics"
ON accuracy_metrics FOR SELECT
USING (user_id IS NULL);

-- Prediction reminders policies
CREATE POLICY "Users can view own reminders"
ON prediction_reminders FOR SELECT
USING (auth.uid() = user_id);

-- =====================================================
-- TRIGGERS FOR AUTO-UPDATING updated_at
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers
CREATE TRIGGER update_predictions_updated_at BEFORE UPDATE ON predictions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prediction_outcomes_updated_at BEFORE UPDATE ON prediction_outcomes
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_insights_updated_at BEFORE UPDATE ON learning_insights
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_accuracy_metrics_updated_at BEFORE UPDATE ON accuracy_metrics
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to calculate accuracy score based on outcome
CREATE OR REPLACE FUNCTION calculate_prediction_accuracy(
    p_outcome_occurred BOOLEAN,
    p_timing_accuracy TEXT,
    p_severity_match TEXT
)
RETURNS INTEGER AS $$
DECLARE
    base_score INTEGER := 0;
    timing_bonus INTEGER := 0;
    severity_bonus INTEGER := 0;
BEGIN
    -- Base score: did it happen?
    IF p_outcome_occurred THEN
        base_score := 60;  -- 60% for occurrence

        -- Timing accuracy bonus (up to 20%)
        timing_bonus := CASE p_timing_accuracy
            WHEN 'on_time' THEN 20
            WHEN 'early' THEN 15
            WHEN 'late' THEN 10
            WHEN 'significantly_late' THEN 5
            ELSE 0
        END;

        -- Severity match bonus (up to 20%)
        severity_bonus := CASE p_severity_match
            WHEN 'accurate' THEN 20
            WHEN 'understated' THEN 10
            WHEN 'overstated' THEN 10
            ELSE 0
        END;
    ELSE
        -- Prediction didn't happen
        base_score := 0;
    END IF;

    RETURN base_score + timing_bonus + severity_bonus;
END;
$$ LANGUAGE plpgsql;

-- Function to auto-update prediction status when outcome is added
CREATE OR REPLACE FUNCTION update_prediction_status_on_outcome()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE predictions
    SET
        status = CASE
            WHEN NEW.outcome_occurred THEN 'verified'
            ELSE 'rejected'
        END,
        updated_at = NOW()
    WHERE id = NEW.prediction_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_update_prediction_status
AFTER INSERT OR UPDATE ON prediction_outcomes
FOR EACH ROW EXECUTE FUNCTION update_prediction_status_on_outcome();

-- =====================================================
-- SAMPLE DATA (for testing)
-- =====================================================

-- Note: Sample data would use real user IDs from auth.users
-- This is commented out as it requires actual user data
/*
INSERT INTO predictions (
    user_id, prediction_type, prediction_category, source_type,
    prediction_text, prediction_summary, confidence_level,
    expected_timeframe_start, expected_timeframe_end, timeframe_description
) VALUES (
    'sample-user-id',
    'career',
    'career',
    'ai_query',
    'Based on your Jupiter dasha period starting next month, you will receive a significant career advancement opportunity. This is supported by the Gaja Kesari yoga in your chart and favorable transits.',
    'Career advancement during Jupiter dasha',
    'high',
    CURRENT_DATE + INTERVAL '1 month',
    CURRENT_DATE + INTERVAL '4 months',
    'Within the next 3-4 months during Jupiter dasha period'
);
*/

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

COMMENT ON TABLE predictions IS 'Stores all predictions made by the system for users';
COMMENT ON TABLE prediction_outcomes IS 'Stores actual outcomes reported by users for verification';
COMMENT ON TABLE learning_insights IS 'Stores insights learned from analyzing prediction accuracy';
COMMENT ON TABLE accuracy_metrics IS 'Aggregated accuracy statistics for predictions';
COMMENT ON TABLE prediction_reminders IS 'Tracks reminders sent to users about pending predictions';
