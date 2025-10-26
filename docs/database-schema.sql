-- Vedic AI Astrology Database Schema
-- PostgreSQL / Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Birth Profiles Table
CREATE TABLE profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL, -- References auth.users from Supabase
  name VARCHAR(100) NOT NULL,
  birth_date DATE NOT NULL,
  birth_time TIME NOT NULL,
  birth_lat DECIMAL(9,6) NOT NULL,
  birth_lon DECIMAL(9,6) NOT NULL,
  birth_city VARCHAR(100),
  birth_timezone VARCHAR(50),
  is_primary BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for profiles
CREATE INDEX idx_profiles_user ON profiles(user_id);
CREATE INDEX idx_profiles_primary ON profiles(user_id, is_primary) WHERE is_primary = TRUE;

-- Cached Birth Charts Table
CREATE TABLE charts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  chart_type VARCHAR(10) NOT NULL CHECK (chart_type IN ('D1', 'D9')),
  chart_data JSONB NOT NULL,
  chart_svg TEXT,
  calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(profile_id, chart_type)
);

-- Indexes for charts
CREATE INDEX idx_charts_profile ON charts(profile_id);
CREATE INDEX idx_charts_type ON charts(profile_id, chart_type);

-- User Queries Table
CREATE TABLE queries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  question TEXT NOT NULL,
  category VARCHAR(50),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for queries
CREATE INDEX idx_queries_user ON queries(user_id);
CREATE INDEX idx_queries_profile ON queries(profile_id);
CREATE INDEX idx_queries_created ON queries(created_at DESC);

-- AI Responses Table
CREATE TABLE responses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  query_id UUID NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
  interpretation TEXT NOT NULL,
  ai_model VARCHAR(50),
  tokens_used INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for responses
CREATE INDEX idx_responses_query ON responses(query_id);

-- User Feedback Table
CREATE TABLE feedback (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  response_id UUID NOT NULL REFERENCES responses(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for feedback
CREATE INDEX idx_feedback_response ON feedback(response_id);
CREATE INDEX idx_feedback_user ON feedback(user_id);
CREATE INDEX idx_feedback_rating ON feedback(rating);

-- Row Level Security (RLS) Policies for Supabase

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE charts ENABLE ROW LEVEL SECURITY;
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view their own profiles"
  ON profiles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own profiles"
  ON profiles FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own profiles"
  ON profiles FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own profiles"
  ON profiles FOR DELETE
  USING (auth.uid() = user_id);

-- Charts policies (inherit from profiles)
CREATE POLICY "Users can view charts of their profiles"
  ON charts FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = charts.profile_id
      AND profiles.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create charts for their profiles"
  ON charts FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = charts.profile_id
      AND profiles.user_id = auth.uid()
    )
  );

-- Queries policies
CREATE POLICY "Users can view their own queries"
  ON queries FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own queries"
  ON queries FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Responses policies (inherit from queries)
CREATE POLICY "Users can view responses to their queries"
  ON responses FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM queries
      WHERE queries.id = responses.query_id
      AND queries.user_id = auth.uid()
    )
  );

-- Feedback policies
CREATE POLICY "Users can view their own feedback"
  ON feedback FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own feedback"
  ON feedback FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own feedback"
  ON feedback FOR UPDATE
  USING (auth.uid() = user_id);

-- Comments
COMMENT ON TABLE profiles IS 'Birth profiles for astrological calculations';
COMMENT ON TABLE charts IS 'Cached birth charts (D1, D9, etc.)';
COMMENT ON TABLE queries IS 'User questions for AI interpretation';
COMMENT ON TABLE responses IS 'AI-generated astrological interpretations';
COMMENT ON TABLE feedback IS 'User feedback on AI interpretations';
