-- Migration: Add Numerology Schema (SAFE VERSION)
-- Date: 2025-11-05
-- Description: Add missing numerology tables and columns (safe for partial migrations)

-- This version uses IF NOT EXISTS and handles existing tables gracefully

-- ============================================================================
-- 1. NUMEROLOGY PROFILES (Skip if exists)
-- ============================================================================

CREATE TABLE IF NOT EXISTS numerology_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,

  -- Name data
  full_name VARCHAR(255) NOT NULL,
  common_name VARCHAR(255),
  name_at_birth VARCHAR(255),

  -- System preference
  system VARCHAR(50) NOT NULL DEFAULT 'both',

  -- Western/Pythagorean calculations
  western_data JSONB,

  -- Vedic/Chaldean calculations
  vedic_data JSONB,

  -- Cycle windows
  cycles JSONB,

  -- Metadata
  birth_date DATE NOT NULL,
  calculation_hash VARCHAR(64),
  calculated_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT unique_numerology_profile UNIQUE (user_id, profile_id, full_name, birth_date)
);

-- Indexes (will skip if exists)
CREATE INDEX IF NOT EXISTS idx_numerology_user ON numerology_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_numerology_profile ON numerology_profiles(profile_id);
CREATE INDEX IF NOT EXISTS idx_numerology_hash ON numerology_profiles(calculation_hash);
CREATE INDEX IF NOT EXISTS idx_numerology_system ON numerology_profiles(system);
CREATE INDEX IF NOT EXISTS idx_numerology_created ON numerology_profiles(created_at DESC);

-- Row Level Security
ALTER TABLE numerology_profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Users can view own numerology profiles" ON numerology_profiles;
DROP POLICY IF EXISTS "Users can create own numerology profiles" ON numerology_profiles;
DROP POLICY IF EXISTS "Users can update own numerology profiles" ON numerology_profiles;
DROP POLICY IF EXISTS "Users can delete own numerology profiles" ON numerology_profiles;

-- Create policies
CREATE POLICY "Users can view own numerology profiles"
  ON numerology_profiles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own numerology profiles"
  ON numerology_profiles FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own numerology profiles"
  ON numerology_profiles FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own numerology profiles"
  ON numerology_profiles FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================================
-- 2. NUMEROLOGY NAME TRIALS (Skip if exists)
-- ============================================================================

CREATE TABLE IF NOT EXISTS numerology_name_trials (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  numerology_profile_id UUID NOT NULL REFERENCES numerology_profiles(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  trial_name VARCHAR(255) NOT NULL,
  system VARCHAR(50) NOT NULL,

  -- Calculated values for this trial name
  calculated_values JSONB NOT NULL,

  -- User notes
  notes TEXT,
  is_preferred BOOLEAN DEFAULT false,

  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_name_trials_profile ON numerology_name_trials(numerology_profile_id);
CREATE INDEX IF NOT EXISTS idx_name_trials_user ON numerology_name_trials(user_id);
CREATE INDEX IF NOT EXISTS idx_name_trials_preferred ON numerology_name_trials(is_preferred) WHERE is_preferred = true;

-- Row Level Security
ALTER TABLE numerology_name_trials ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can manage own name trials" ON numerology_name_trials;

CREATE POLICY "Users can manage own name trials"
  ON numerology_name_trials FOR ALL
  USING (auth.uid() = user_id);

-- ============================================================================
-- 3. PRIVACY PREFERENCES (Skip if exists)
-- ============================================================================

CREATE TABLE IF NOT EXISTS privacy_preferences (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Numerology preferences
  store_numerology_trials BOOLEAN DEFAULT true,
  share_numerology_anonymously BOOLEAN DEFAULT false,

  -- Palmistry preferences (future)
  store_palm_images BOOLEAN DEFAULT false,
  store_palm_features BOOLEAN DEFAULT true,

  -- General preferences
  erasable_audit BOOLEAN DEFAULT true,
  data_retention_days INTEGER DEFAULT 365,

  -- Consent tracking
  privacy_policy_version VARCHAR(20),
  privacy_policy_accepted_at TIMESTAMP,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Row Level Security
ALTER TABLE privacy_preferences ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can manage own privacy preferences" ON privacy_preferences;

CREATE POLICY "Users can manage own privacy preferences"
  ON privacy_preferences FOR ALL
  USING (auth.uid() = user_id);

-- ============================================================================
-- 4. EXTEND KB_RULES for Numerology (Safe column additions)
-- ============================================================================

-- Add new columns only if they don't exist
DO $$
BEGIN
  -- Add system column if it doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'system'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN system VARCHAR(50);
  END IF;

  -- Add modifiers column if it doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'modifiers'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN modifiers JSONB;
  END IF;

  -- Add context column if it doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'context'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN context JSONB;
  END IF;
END $$;

-- Add indexes for new columns (skip if exists)
CREATE INDEX IF NOT EXISTS idx_kb_rules_system ON kb_rules(system);
CREATE INDEX IF NOT EXISTS idx_kb_rules_context ON kb_rules USING GIN(context);
CREATE INDEX IF NOT EXISTS idx_kb_rules_modifiers ON kb_rules USING GIN(modifiers);

-- Update existing astrology rules to have system='vedic' (only if system is NULL)
UPDATE kb_rules
SET system = 'vedic'
WHERE system IS NULL
  AND domain IN ('career', 'wealth', 'relationships', 'health', 'education', 'spirituality');

-- ============================================================================
-- 5. NUMEROLOGY RULE EXAMPLES (Insert only if not exists)
-- ============================================================================

-- Sample rule for Western Life Path 1
INSERT INTO kb_rules (rule_id, domain, system, condition, effect, anchor, weight, tags, context, modifiers)
SELECT
  'NUM-W-LP-01-leadership',
  'numerology',
  'western',
  'IF Life Path = 1',
  'THEN natural leadership qualities, independence, innovation, pioneering spirit',
  'Life Path 1 - The Leader',
  0.95,
  ARRAY['life_path', 'western', 'leadership', 'independence'],
  '{"scope": "life_path", "number": 1, "system": "western"}'::jsonb,
  '{"strength": "strong", "age_range": "all", "career_boost": true}'::jsonb
WHERE NOT EXISTS (
  SELECT 1 FROM kb_rules WHERE rule_id = 'NUM-W-LP-01-leadership'
);

-- Sample rule for Vedic Psychic Number 1 (Sun)
INSERT INTO kb_rules (rule_id, domain, system, condition, effect, anchor, weight, tags, context, modifiers)
SELECT
  'NUM-V-PSY-01-sun',
  'numerology',
  'vedic',
  'IF Psychic Number = 1 (ruled by Sun)',
  'THEN strong personality, leadership, authority, health-conscious, father figure influence',
  'Psychic Number 1 - Sun Influence',
  0.90,
  ARRAY['psychic_number', 'vedic', 'sun', 'leadership'],
  '{"scope": "psychic_number", "number": 1, "planet": "Sun", "system": "vedic"}'::jsonb,
  '{"strength": "strong", "favorable_dates": [1,10,19,28], "favorable_colors": ["gold", "orange"]}'::jsonb
WHERE NOT EXISTS (
  SELECT 1 FROM kb_rules WHERE rule_id = 'NUM-V-PSY-01-sun'
);

-- Sample rule for Master Number 11
INSERT INTO kb_rules (rule_id, domain, system, condition, effect, anchor, weight, tags, context, modifiers)
SELECT
  'NUM-W-MASTER-11-intuition',
  'numerology',
  'western',
  'IF Life Path = 11 (Master Number)',
  'THEN heightened intuition, spiritual insight, idealism, sensitivity, potential for great achievement or struggle',
  'Master Number 11 - Spiritual Messenger',
  0.98,
  ARRAY['master_number', 'life_path', 'western', 'spirituality', 'intuition'],
  '{"scope": "life_path", "number": 11, "is_master": true, "system": "western"}'::jsonb,
  '{"strength": "very_strong", "challenges": ["oversensitivity", "anxiety"], "gifts": ["intuition", "inspiration"]}'::jsonb
WHERE NOT EXISTS (
  SELECT 1 FROM kb_rules WHERE rule_id = 'NUM-W-MASTER-11-intuition'
);

-- Sample rule for Karmic Debt 16
INSERT INTO kb_rules (rule_id, domain, system, condition, effect, anchor, weight, tags, context, modifiers)
SELECT
  'NUM-W-KARMIC-16-ego',
  'numerology',
  'western',
  'IF Karmic Debt = 16 (Life Path or Birth Day)',
  'THEN karmic lessons around ego, pride, relationships; need for humility and spiritual growth',
  'Karmic Debt 16 - Karmic Relationships',
  0.92,
  ARRAY['karmic_debt', 'western', 'relationships', 'ego', 'lessons'],
  '{"scope": "karmic_debt", "number": 16, "system": "western"}'::jsonb,
  '{"strength": "challenging", "lessons": ["humility", "service"], "relationship_impact": true}'::jsonb
WHERE NOT EXISTS (
  SELECT 1 FROM kb_rules WHERE rule_id = 'NUM-W-KARMIC-16-ego'
);

-- Sample rule for Personal Year 1
INSERT INTO kb_rules (rule_id, domain, system, condition, effect, anchor, weight, tags, context, modifiers)
SELECT
  'NUM-W-PY-01-new-beginnings',
  'numerology',
  'western',
  'IF Personal Year = 1',
  'THEN new beginnings, fresh starts, planting seeds, taking initiative, starting new ventures',
  'Personal Year 1 - New Cycle',
  0.88,
  ARRAY['personal_year', 'western', 'cycles', 'new_beginnings'],
  '{"scope": "personal_year", "number": 1, "system": "western", "duration": "1 year"}'::jsonb,
  '{"strength": "strong", "best_for": ["new_projects", "career_change", "relocation"], "avoid": ["finishing_old_projects"]}'::jsonb
WHERE NOT EXISTS (
  SELECT 1 FROM kb_rules WHERE rule_id = 'NUM-W-PY-01-new-beginnings'
);

-- ============================================================================
-- 6. HELPER FUNCTIONS (Replace if exists)
-- ============================================================================

-- Function to calculate Life Path from birth date (basic example)
CREATE OR REPLACE FUNCTION calculate_life_path(birth_date DATE)
RETURNS INTEGER AS $$
DECLARE
  year_sum INTEGER;
  month_sum INTEGER;
  day_sum INTEGER;
  total_sum INTEGER;
BEGIN
  year_sum := EXTRACT(YEAR FROM birth_date);
  month_sum := EXTRACT(MONTH FROM birth_date);
  day_sum := EXTRACT(DAY FROM birth_date);

  total_sum := year_sum + month_sum + day_sum;

  -- Reduce to single digit or master number
  WHILE total_sum > 9 AND total_sum NOT IN (11, 22, 33) LOOP
    total_sum := (total_sum / 10) + (total_sum % 10);
  END LOOP;

  RETURN total_sum;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers (drop and recreate to avoid conflicts)
DROP TRIGGER IF EXISTS update_numerology_profiles_updated_at ON numerology_profiles;
CREATE TRIGGER update_numerology_profiles_updated_at
  BEFORE UPDATE ON numerology_profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_privacy_preferences_updated_at ON privacy_preferences;
CREATE TRIGGER update_privacy_preferences_updated_at
  BEFORE UPDATE ON privacy_preferences
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 7. VIEWS for easy querying (Replace if exists)
-- ============================================================================

-- Combined view of user profiles with numerology
CREATE OR REPLACE VIEW user_numerology_summary AS
SELECT
  p.id as profile_id,
  p.user_id,
  p.name,
  p.birth_date,
  np.id as numerology_id,
  np.full_name,
  np.system,
  np.western_data->>'life_path' as life_path,
  np.western_data->>'expression' as expression,
  np.vedic_data->>'psychic_number' as psychic_number,
  np.vedic_data->>'destiny_number' as destiny_number,
  np.cycles->>'personal_year' as current_personal_year,
  np.calculated_at
FROM profiles p
LEFT JOIN numerology_profiles np ON p.id = np.profile_id
WHERE p.user_id = auth.uid();

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Add migration tracking (only if schema_migrations table exists)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'schema_migrations') THEN
    INSERT INTO schema_migrations (version, description, applied_at)
    VALUES ('001', 'Add numerology schema with profiles, trials, and privacy preferences', NOW())
    ON CONFLICT (version) DO NOTHING;
  END IF;
END $$;
