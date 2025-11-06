-- Migration: REPAIR Numerology Schema (Fix Incomplete Tables)
-- Date: 2025-11-05
-- Description: Adds missing columns to partially-created tables
--
-- This script is designed to fix incomplete migrations where tables exist
-- but are missing columns. It only adds missing columns without recreating tables.

-- ============================================================================
-- 1. REPAIR NUMEROLOGY_PROFILES TABLE
-- ============================================================================

-- Add missing columns one by one (will skip if column already exists)
DO $$
BEGIN
  -- Add user_id if missing (core column)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'user_id'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE;
    RAISE NOTICE 'Added column: user_id';
  END IF;

  -- Add profile_id if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'profile_id'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL;
    RAISE NOTICE 'Added column: profile_id';
  END IF;

  -- Add full_name if missing (core column)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'full_name'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN full_name VARCHAR(255) NOT NULL;
    RAISE NOTICE 'Added column: full_name';
  END IF;

  -- Add common_name if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'common_name'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN common_name VARCHAR(255);
    RAISE NOTICE 'Added column: common_name';
  END IF;

  -- Add name_at_birth if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'name_at_birth'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN name_at_birth VARCHAR(255);
    RAISE NOTICE 'Added column: name_at_birth';
  END IF;

  -- Add system if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'system'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN system VARCHAR(50) NOT NULL DEFAULT 'both';
    RAISE NOTICE 'Added column: system';
  END IF;

  -- Add western_data if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'western_data'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN western_data JSONB;
    RAISE NOTICE 'Added column: western_data';
  END IF;

  -- Add vedic_data if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'vedic_data'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN vedic_data JSONB;
    RAISE NOTICE 'Added column: vedic_data';
  END IF;

  -- Add cycles if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'cycles'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN cycles JSONB;
    RAISE NOTICE 'Added column: cycles';
  END IF;

  -- Add birth_date if missing (CORE REQUIRED COLUMN)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'birth_date'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN birth_date DATE NOT NULL DEFAULT '2000-01-01';
    RAISE NOTICE 'Added column: birth_date';
  END IF;

  -- Add calculation_hash if missing (THIS IS THE KEY MISSING COLUMN)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'calculation_hash'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN calculation_hash VARCHAR(64);
    RAISE NOTICE 'Added column: calculation_hash';
  END IF;

  -- Add calculated_at if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'calculated_at'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN calculated_at TIMESTAMP DEFAULT NOW();
    RAISE NOTICE 'Added column: calculated_at';
  END IF;

  -- Add created_at if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'created_at'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
    RAISE NOTICE 'Added column: created_at';
  END IF;

  -- Add updated_at if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'numerology_profiles' AND column_name = 'updated_at'
  ) THEN
    ALTER TABLE numerology_profiles ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
    RAISE NOTICE 'Added column: updated_at';
  END IF;
END $$;

-- ============================================================================
-- 1B. ADD CONSTRAINTS (After all columns exist)
-- ============================================================================

-- Add constraint if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'unique_numerology_profile'
  ) THEN
    ALTER TABLE numerology_profiles
    ADD CONSTRAINT unique_numerology_profile
    UNIQUE (user_id, profile_id, full_name, birth_date);
    RAISE NOTICE 'Added constraint: unique_numerology_profile';
  END IF;
END $$;

-- Add indexes if missing
CREATE INDEX IF NOT EXISTS idx_numerology_user ON numerology_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_numerology_profile ON numerology_profiles(profile_id);
CREATE INDEX IF NOT EXISTS idx_numerology_hash ON numerology_profiles(calculation_hash);
CREATE INDEX IF NOT EXISTS idx_numerology_system ON numerology_profiles(system);
CREATE INDEX IF NOT EXISTS idx_numerology_created ON numerology_profiles(created_at DESC);

-- Enable Row Level Security if not already enabled
ALTER TABLE numerology_profiles ENABLE ROW LEVEL SECURITY;

-- Drop and recreate policies to ensure they're correct
DROP POLICY IF EXISTS "Users can view own numerology profiles" ON numerology_profiles;
DROP POLICY IF EXISTS "Users can create own numerology profiles" ON numerology_profiles;
DROP POLICY IF EXISTS "Users can update own numerology profiles" ON numerology_profiles;
DROP POLICY IF EXISTS "Users can delete own numerology profiles" ON numerology_profiles;

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
-- 2. CREATE MISSING TABLES (If they don't exist)
-- ============================================================================

-- Create numerology_name_trials table if it doesn't exist
CREATE TABLE IF NOT EXISTS numerology_name_trials (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  numerology_profile_id UUID NOT NULL REFERENCES numerology_profiles(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  trial_name VARCHAR(255) NOT NULL,
  system VARCHAR(50) NOT NULL,

  calculated_values JSONB NOT NULL,
  notes TEXT,
  is_preferred BOOLEAN DEFAULT false,

  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_name_trials_profile ON numerology_name_trials(numerology_profile_id);
CREATE INDEX IF NOT EXISTS idx_name_trials_user ON numerology_name_trials(user_id);
CREATE INDEX IF NOT EXISTS idx_name_trials_preferred ON numerology_name_trials(is_preferred) WHERE is_preferred = true;

ALTER TABLE numerology_name_trials ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can manage own name trials" ON numerology_name_trials;
CREATE POLICY "Users can manage own name trials"
  ON numerology_name_trials FOR ALL
  USING (auth.uid() = user_id);

-- Create privacy_preferences table if it doesn't exist
CREATE TABLE IF NOT EXISTS privacy_preferences (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

  store_numerology_trials BOOLEAN DEFAULT true,
  share_numerology_anonymously BOOLEAN DEFAULT false,

  store_palm_images BOOLEAN DEFAULT false,
  store_palm_features BOOLEAN DEFAULT true,

  erasable_audit BOOLEAN DEFAULT true,
  data_retention_days INTEGER DEFAULT 365,

  privacy_policy_version VARCHAR(20),
  privacy_policy_accepted_at TIMESTAMP,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE privacy_preferences ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can manage own privacy preferences" ON privacy_preferences;
CREATE POLICY "Users can manage own privacy preferences"
  ON privacy_preferences FOR ALL
  USING (auth.uid() = user_id);

-- ============================================================================
-- 3. EXTEND KB_RULES TABLE (Add missing columns)
-- ============================================================================

DO $$
BEGIN
  -- Add rule_id if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'rule_id'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN rule_id VARCHAR(100);
    RAISE NOTICE 'Added column: kb_rules.rule_id';
  END IF;

  -- Add domain if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'domain'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN domain VARCHAR(50);
    RAISE NOTICE 'Added column: kb_rules.domain';
  END IF;

  -- Add system column if it doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'system'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN system VARCHAR(50);
    RAISE NOTICE 'Added column: kb_rules.system';
  END IF;

  -- Add condition if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'condition'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN condition TEXT;
    RAISE NOTICE 'Added column: kb_rules.condition';
  END IF;

  -- Add effect if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'effect'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN effect TEXT;
    RAISE NOTICE 'Added column: kb_rules.effect';
  END IF;

  -- Add anchor if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'anchor'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN anchor VARCHAR(255);
    RAISE NOTICE 'Added column: kb_rules.anchor';
  END IF;

  -- Add weight if missing
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'weight'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN weight DECIMAL(3,2);
    RAISE NOTICE 'Added column: kb_rules.weight';
  END IF;

  -- Add tags column if it doesn't exist (THIS IS THE MISSING COLUMN)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'tags'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN tags TEXT[];
    RAISE NOTICE 'Added column: kb_rules.tags';
  END IF;

  -- Add context column if it doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'context'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN context JSONB;
    RAISE NOTICE 'Added column: kb_rules.context';
  END IF;

  -- Add modifiers column if it doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'modifiers'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN modifiers JSONB;
    RAISE NOTICE 'Added column: kb_rules.modifiers';
  END IF;

  -- Add chart_context column if it doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'chart_context'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN chart_context JSONB NOT NULL DEFAULT '{}'::jsonb;
    RAISE NOTICE 'Added column: kb_rules.chart_context';
  END IF;

  -- Add scope column if it doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'kb_rules' AND column_name = 'scope'
  ) THEN
    ALTER TABLE kb_rules ADD COLUMN scope JSONB NOT NULL DEFAULT '{}'::jsonb;
    RAISE NOTICE 'Added column: kb_rules.scope';
  END IF;
END $$;

-- Add indexes for new columns (use B-tree for VARCHAR, GIN for JSONB/arrays)
DO $$
BEGIN
  -- B-tree index for system (VARCHAR)
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_kb_rules_system') THEN
    CREATE INDEX idx_kb_rules_system ON kb_rules(system);
  END IF;

  -- GIN index for context (JSONB)
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_kb_rules_context') THEN
    CREATE INDEX idx_kb_rules_context ON kb_rules USING GIN(context);
  END IF;

  -- GIN index for modifiers (JSONB)
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_kb_rules_modifiers') THEN
    CREATE INDEX idx_kb_rules_modifiers ON kb_rules USING GIN(modifiers);
  END IF;

  -- GIN index for chart_context (JSONB)
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_kb_rules_chart_context') THEN
    CREATE INDEX idx_kb_rules_chart_context ON kb_rules USING GIN(chart_context);
  END IF;

  -- GIN index for tags (TEXT[])
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_kb_rules_tags') THEN
    CREATE INDEX idx_kb_rules_tags ON kb_rules USING GIN(tags);
  END IF;
EXCEPTION WHEN OTHERS THEN
  -- If any index creation fails, log it but continue
  RAISE NOTICE 'Some indexes may already exist or have errors: %', SQLERRM;
END $$;

-- Update existing astrology rules to have system='vedic'
UPDATE kb_rules
SET system = 'vedic'
WHERE system IS NULL
  AND domain IN ('career', 'wealth', 'relationships', 'health', 'education', 'spirituality');

-- ============================================================================
-- 4. SKIP SAMPLE NUMEROLOGY RULES (Due to complex check constraints)
-- ============================================================================

-- Note: Sample numerology rules are skipped due to various check constraints
-- on kb_rules table (chart_context, scope, etc.) that vary by environment.
--
-- You can add numerology rules manually later using your existing kb_sources
-- and following the same structure as your existing kb_rules.
--
-- Example numerology rule structure for future reference:
-- - rule_id: 'NUM-W-LP-01-leadership'
-- - domain: 'numerology'
-- - system: 'western' or 'vedic'
-- - tags: ARRAY['life_path', 'western', 'leadership', 'independence']
-- - context: JSONB with scope, number, system info

DO $$
BEGIN
  RAISE NOTICE '=======================================================';
  RAISE NOTICE 'Sample numerology rules SKIPPED';
  RAISE NOTICE 'You can add them manually via Supabase dashboard or';
  RAISE NOTICE 'using the ingest_comprehensive_rules.py script';
  RAISE NOTICE '=======================================================';
END $$;

-- ============================================================================
-- 5. CREATE HELPER FUNCTIONS (Replace if exists)
-- ============================================================================

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

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
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
-- 6. CREATE VIEWS (Replace if exists)
-- ============================================================================

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
-- REPAIR MIGRATION COMPLETE
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE '=======================================================';
  RAISE NOTICE 'REPAIR MIGRATION COMPLETED SUCCESSFULLY';
  RAISE NOTICE '=======================================================';
  RAISE NOTICE 'Next steps:';
  RAISE NOTICE '1. Run the verification script:';
  RAISE NOTICE '   python backend/scripts/verify_numerology_migration.py';
  RAISE NOTICE '2. Test API endpoints at: http://localhost:8000/docs';
  RAISE NOTICE '3. Look for "numerology" tag in Swagger UI';
  RAISE NOTICE '=======================================================';
END $$;
