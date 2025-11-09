-- Migration: Add Prashna (Horary Astrology) table
-- Description: Stores horary astrology questions and their analyses

-- Create Prashna table
CREATE TABLE IF NOT EXISTS prashnas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,

    -- Question details
    question TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,

    -- Query moment (when question was asked)
    query_datetime TIMESTAMPTZ NOT NULL,

    -- Location where question was asked
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    timezone VARCHAR(50) NOT NULL,

    -- Prashna chart and analysis (stored as JSON)
    prashna_chart JSONB NOT NULL,
    analysis JSONB NOT NULL,

    -- Optional notes
    notes TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,

    -- Indexes
    CONSTRAINT prashnas_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_prashnas_user_id ON prashnas(user_id);
CREATE INDEX IF NOT EXISTS idx_prashnas_question_type ON prashnas(question_type);
CREATE INDEX IF NOT EXISTS idx_prashnas_created_at ON prashnas(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_prashnas_query_datetime ON prashnas(query_datetime);

-- Enable Row Level Security (RLS)
ALTER TABLE prashnas ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only see their own Prashnas
CREATE POLICY "Users can view own prashnas"
    ON prashnas FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own Prashnas
CREATE POLICY "Users can insert own prashnas"
    ON prashnas FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own Prashnas
CREATE POLICY "Users can update own prashnas"
    ON prashnas FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own Prashnas
CREATE POLICY "Users can delete own prashnas"
    ON prashnas FOR DELETE
    USING (auth.uid() = user_id);

-- Grant permissions
GRANT ALL ON prashnas TO authenticated;
GRANT ALL ON prashnas TO service_role;

-- Add comment to table
COMMENT ON TABLE prashnas IS 'Prashna (Horary Astrology) questions and analyses';
COMMENT ON COLUMN prashnas.question_type IS 'Type of question: career, relationship, health, finance, education, legal, travel, property, children, spiritual, general';
COMMENT ON COLUMN prashnas.query_datetime IS 'Exact moment when the question was asked (used for chart calculation)';
COMMENT ON COLUMN prashnas.prashna_chart IS 'Complete Prashna chart data with planetary positions';
COMMENT ON COLUMN prashnas.analysis IS 'Detailed analysis and answer';
