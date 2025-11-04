-- Vedic Astro Engine - AI Extension Schema
-- PostgreSQL / Supabase
-- Extends existing schema (profiles, charts, queries, responses, feedback)

-- ============================================================================
-- PART 1: KNOWLEDGE BASE SYSTEM
-- ============================================================================

-- Enable vector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Sources: Books, articles, scriptures
CREATE TABLE kb_sources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255),
  work_type VARCHAR(50) NOT NULL CHECK (work_type IN ('scripture', 'classical', 'modern', 'article', 'research')),
  language VARCHAR(20) DEFAULT 'sanskrit',
  publication_year INTEGER,
  edition VARCHAR(100),
  isbn VARCHAR(20),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Rules: Individual astrological rules extracted from sources
CREATE TABLE kb_rules (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  rule_id VARCHAR(50) UNIQUE NOT NULL, -- e.g., "BPHS-12-3"
  source_id UUID NOT NULL REFERENCES kb_sources(id) ON DELETE CASCADE,

  -- Classification
  domain VARCHAR(50) NOT NULL CHECK (domain IN (
    'career', 'health', 'wealth', 'relationships', 'education',
    'property', 'travel', 'litigation', 'spirituality', 'longevity',
    'palmistry', 'numerology', 'general'
  )),
  chart_context VARCHAR(50) NOT NULL CHECK (chart_context IN (
    'natal', 'dasha', 'transit', 'varga', 'palm', 'name', 'composite'
  )),
  scope VARCHAR(50) NOT NULL CHECK (scope IN (
    'house', 'sign', 'planet', 'aspect', 'yoga', 'line', 'mount', 'number', 'composite'
  )),

  -- Rule content
  condition TEXT NOT NULL, -- IF clause
  effect TEXT NOT NULL, -- THEN clause
  modifiers JSONB DEFAULT '[]', -- ["strength", "combust", "retrograde", etc.]

  -- Metadata
  weight DECIMAL(3,2) DEFAULT 0.5 CHECK (weight >= 0 AND weight <= 1),
  anchor TEXT, -- Shloka/verse/page number
  sanskrit_text TEXT,
  translation TEXT,
  commentary TEXT,

  -- Application context
  applicable_vargas TEXT[], -- ['D1', 'D9', 'D60']
  requires_yoga VARCHAR(100), -- If depends on specific yoga
  cancelers TEXT[], -- Rules that cancel this one

  -- Versioning
  version INTEGER DEFAULT 1,
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('draft', 'active', 'deprecated')),

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vector embeddings for semantic search
CREATE TABLE kb_rule_embeddings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  rule_id UUID NOT NULL REFERENCES kb_rules(id) ON DELETE CASCADE,
  embedding vector(1536), -- OpenAI ada-002 dimension
  model_version VARCHAR(50) DEFAULT 'text-embedding-ada-002',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(rule_id, model_version)
);

-- Symbolic keys for fast lookup (house placements, aspects, etc.)
CREATE TABLE kb_symbolic_keys (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  rule_id UUID NOT NULL REFERENCES kb_rules(id) ON DELETE CASCADE,
  key_type VARCHAR(50) NOT NULL, -- 'planet_house', 'planet_sign', 'aspect', 'yoga', etc.
  key_value TEXT NOT NULL, -- 'Sun_10', 'Mars_Aries', 'Jupiter_aspect_Moon', etc.
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Rule performance tracking
CREATE TABLE kb_rule_feedback (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  rule_id UUID NOT NULL REFERENCES kb_rules(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  reading_session_id UUID NOT NULL,
  feedback VARCHAR(20) NOT NULL CHECK (feedback IN ('confirmed', 'contradicted', 'partial', 'unknown')),
  anchor_event_id UUID, -- Reference to event that confirmed/contradicted
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for knowledge base
CREATE INDEX idx_kb_rules_domain ON kb_rules(domain);
CREATE INDEX idx_kb_rules_rule_id ON kb_rules(rule_id);
CREATE INDEX idx_kb_rules_source ON kb_rules(source_id);
CREATE INDEX idx_kb_rules_status ON kb_rules(status);
CREATE INDEX idx_kb_symbolic_keys_type_value ON kb_symbolic_keys(key_type, key_value);
CREATE INDEX idx_kb_rule_embeddings_vector ON kb_rule_embeddings USING ivfflat (embedding vector_cosine_ops);

-- ============================================================================
-- PART 2: READING SESSIONS & CACHING
-- ============================================================================

-- Reading sessions with canonical hash for caching
CREATE TABLE reading_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  -- Caching
  canonical_hash VARCHAR(64) NOT NULL, -- SHA-256 of input params
  input_params JSONB NOT NULL, -- {dob, tob, city_id, etc.}

  -- Results
  charts JSONB, -- {rasi, navamsa, other_vargas}
  dashas JSONB, -- {maha, antar, etc.}
  transits JSONB,
  predictions JSONB, -- Structured predictions by domain

  -- Metadata
  reading_type VARCHAR(50) DEFAULT 'full' CHECK (reading_type IN ('full', 'quick', 'dasha', 'transit', 'specific')),
  ai_model VARCHAR(50), -- 'gpt-4-turbo', etc.
  total_tokens INTEGER,
  cost_usd DECIMAL(10,4),
  duration_seconds INTEGER,

  -- Quality
  confidence_score DECIMAL(3,2),
  rule_count INTEGER, -- How many rules applied
  citations JSONB, -- Array of rule_ids cited

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '30 days'
);

-- User feedback on readings
CREATE TABLE reading_feedback (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  reading_session_id UUID NOT NULL REFERENCES reading_sessions(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  accuracy_rating INTEGER CHECK (accuracy_rating >= 1 AND accuracy_rating <= 5),
  helpful_predictions TEXT[],
  incorrect_predictions TEXT[],
  comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for sessions
CREATE INDEX idx_reading_sessions_user ON reading_sessions(user_id);
CREATE INDEX idx_reading_sessions_hash ON reading_sessions(user_id, canonical_hash);
CREATE INDEX idx_reading_sessions_created ON reading_sessions(created_at DESC);
CREATE INDEX idx_reading_sessions_expires ON reading_sessions(expires_at) WHERE expires_at IS NOT NULL;

-- ============================================================================
-- PART 3: USER MEMORY SYSTEM (PRIVACY-FIRST)
-- ============================================================================

-- User memory for improving future predictions
CREATE TABLE user_memory (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE,

  -- Immutable profile data
  rectified_birth_time TIME, -- Once agreed upon
  rectification_confidence DECIMAL(3,2),
  preferred_place_id VARCHAR(100), -- From city dropdown

  -- Preferences
  language VARCHAR(10) DEFAULT 'en',
  remedy_preference VARCHAR(50) CHECK (remedy_preference IN ('traditional', 'practical', 'both', 'none')),
  reading_depth VARCHAR(20) DEFAULT 'medium' CHECK (reading_depth IN ('brief', 'medium', 'detailed')),
  domains_of_interest TEXT[], -- ['career', 'health', etc.]

  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  version INTEGER DEFAULT 1
);

-- Event anchors for rectification and validation
CREATE TABLE event_anchors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  event_date DATE NOT NULL,
  event_time TIME,
  event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
    'marriage', 'job_start', 'job_end', 'relocation', 'childbirth',
    'surgery', 'accident', 'major_gain', 'major_loss', 'education_start',
    'education_end', 'property_purchase', 'other'
  )),
  description TEXT NOT NULL,
  significance VARCHAR(20) DEFAULT 'medium' CHECK (significance IN ('low', 'medium', 'high')),

  -- Validation
  used_for_rectification BOOLEAN DEFAULT FALSE,
  validates_rule_ids UUID[], -- Which rules this confirms

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Rule confirmations (no full text, just IDs)
CREATE TABLE user_rule_confirmations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  rule_id UUID NOT NULL REFERENCES kb_rules(id) ON DELETE CASCADE,
  event_anchor_id UUID REFERENCES event_anchors(id) ON DELETE SET NULL,

  confirmation_type VARCHAR(20) NOT NULL CHECK (confirmation_type IN ('confirmed', 'contradicted', 'partial')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  UNIQUE(user_id, rule_id)
);

-- Indexes for memory
CREATE INDEX idx_user_memory_user ON user_memory(user_id);
CREATE INDEX idx_event_anchors_user ON event_anchors(user_id);
CREATE INDEX idx_event_anchors_profile ON event_anchors(profile_id);
CREATE INDEX idx_event_anchors_date ON event_anchors(event_date DESC);
CREATE INDEX idx_user_rule_confirmations_user ON user_rule_confirmations(user_id);

-- ============================================================================
-- PART 4: PALMISTRY & NUMEROLOGY (FUTURE)
-- ============================================================================

-- Palm readings
CREATE TABLE palm_readings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,

  image_url TEXT NOT NULL,
  hand_type VARCHAR(10) CHECK (hand_type IN ('left', 'right', 'both')),

  -- Extracted features
  lines JSONB, -- {life, heart, head, fate, etc.}
  mounts JSONB, -- {jupiter, saturn, sun, etc.}
  fingers JSONB, -- {thumb, index, middle, etc.}
  marks JSONB, -- {crosses, stars, islands, etc.}

  quality_score DECIMAL(3,2),
  ai_model VARCHAR(50),

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Numerology profiles
CREATE TABLE numerology_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,

  full_name VARCHAR(255) NOT NULL,
  common_name VARCHAR(255),

  -- Calculated numbers
  life_path INTEGER,
  destiny INTEGER,
  soul_urge INTEGER,
  personality INTEGER,
  maturity INTEGER,

  -- Cycles
  personal_year INTEGER,
  personal_month INTEGER,
  pinnacle_numbers JSONB,
  challenge_numbers JSONB,

  -- Analysis
  pythagorean JSONB,
  chaldean JSONB,
  compatibility JSONB,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- PART 5: ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all new tables
ALTER TABLE reading_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE event_anchors ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_rule_confirmations ENABLE ROW LEVEL SECURITY;
ALTER TABLE palm_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE numerology_profiles ENABLE ROW LEVEL SECURITY;

-- Reading sessions policies
CREATE POLICY "Users can view their own reading sessions"
  ON reading_sessions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own reading sessions"
  ON reading_sessions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- User memory policies
CREATE POLICY "Users can view their own memory"
  ON user_memory FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own memory"
  ON user_memory FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own memory"
  ON user_memory FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Event anchors policies
CREATE POLICY "Users can view their own event anchors"
  ON event_anchors FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own event anchors"
  ON event_anchors FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own event anchors"
  ON event_anchors FOR UPDATE
  USING (auth.uid() = user_id);

-- Palm readings policies
CREATE POLICY "Users can view their own palm readings"
  ON palm_readings FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own palm readings"
  ON palm_readings FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Numerology policies
CREATE POLICY "Users can view their own numerology profiles"
  ON numerology_profiles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own numerology profiles"
  ON numerology_profiles FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- PART 6: FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_kb_sources_updated_at BEFORE UPDATE ON kb_sources
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_kb_rules_updated_at BEFORE UPDATE ON kb_rules
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_memory_updated_at BEFORE UPDATE ON user_memory
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to clean expired sessions
CREATE OR REPLACE FUNCTION clean_expired_reading_sessions()
RETURNS void AS $$
BEGIN
  DELETE FROM reading_sessions WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PART 7: INITIAL DATA - SAMPLE SOURCES
-- ============================================================================

-- Insert classical sources
INSERT INTO kb_sources (title, author, work_type, language, notes) VALUES
  ('Brihat Parashara Hora Shastra', 'Maharishi Parashara', 'scripture', 'sanskrit', 'Foundation of Vedic astrology'),
  ('Phaladeepika', 'Mantreswara', 'classical', 'sanskrit', 'Predictive techniques'),
  ('Jataka Parijata', 'Vaidyanatha Dikshita', 'classical', 'sanskrit', 'Comprehensive Jyotish text'),
  ('Saravali', 'Kalyana Varma', 'classical', 'sanskrit', 'Detailed planetary effects'),
  ('Uttara Kalamrita', 'Kalidasa', 'classical', 'sanskrit', 'Advanced predictive methods');

-- ============================================================================
-- PART 8: COMMENTS
-- ============================================================================

COMMENT ON TABLE kb_sources IS 'Astrological texts and sources';
COMMENT ON TABLE kb_rules IS 'Individual rules extracted from sources';
COMMENT ON TABLE kb_rule_embeddings IS 'Vector embeddings for semantic search';
COMMENT ON TABLE kb_symbolic_keys IS 'Symbolic keys for fast rule retrieval';
COMMENT ON TABLE reading_sessions IS 'AI-generated reading sessions with caching';
COMMENT ON TABLE user_memory IS 'Privacy-first user memory for personalization';
COMMENT ON TABLE event_anchors IS 'Life events for rectification and validation';
COMMENT ON TABLE palm_readings IS 'Palmistry analysis results';
COMMENT ON TABLE numerology_profiles IS 'Numerology calculations';
