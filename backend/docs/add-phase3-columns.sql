-- Add Phase 3 columns to existing reading_sessions table
-- This migration is safe to run multiple times (idempotent)

-- Add interpretation column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reading_sessions' AND column_name = 'interpretation'
    ) THEN
        ALTER TABLE reading_sessions ADD COLUMN interpretation TEXT;
        RAISE NOTICE 'Added interpretation column';
    ELSE
        RAISE NOTICE 'interpretation column already exists';
    END IF;
END $$;

-- Add domain_analyses column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reading_sessions' AND column_name = 'domain_analyses'
    ) THEN
        ALTER TABLE reading_sessions ADD COLUMN domain_analyses JSONB;
        RAISE NOTICE 'Added domain_analyses column';
    ELSE
        RAISE NOTICE 'domain_analyses column already exists';
    END IF;
END $$;

-- Add predictions column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reading_sessions' AND column_name = 'predictions'
    ) THEN
        ALTER TABLE reading_sessions ADD COLUMN predictions JSONB;
        RAISE NOTICE 'Added predictions column';
    ELSE
        RAISE NOTICE 'predictions column already exists';
    END IF;
END $$;

-- Add rules_used column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reading_sessions' AND column_name = 'rules_used'
    ) THEN
        ALTER TABLE reading_sessions ADD COLUMN rules_used JSONB;
        RAISE NOTICE 'Added rules_used column';
    ELSE
        RAISE NOTICE 'rules_used column already exists';
    END IF;
END $$;

-- Add verification column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reading_sessions' AND column_name = 'verification'
    ) THEN
        ALTER TABLE reading_sessions ADD COLUMN verification JSONB;
        RAISE NOTICE 'Added verification column';
    ELSE
        RAISE NOTICE 'verification column already exists';
    END IF;
END $$;

-- Add orchestration_metadata column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reading_sessions' AND column_name = 'orchestration_metadata'
    ) THEN
        ALTER TABLE reading_sessions ADD COLUMN orchestration_metadata JSONB;
        RAISE NOTICE 'Added orchestration_metadata column';
    ELSE
        RAISE NOTICE 'orchestration_metadata column already exists';
    END IF;
END $$;

-- Add query column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reading_sessions' AND column_name = 'query'
    ) THEN
        ALTER TABLE reading_sessions ADD COLUMN query TEXT;
        RAISE NOTICE 'Added query column';
    ELSE
        RAISE NOTICE 'query column already exists';
    END IF;
END $$;

-- Add domains column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reading_sessions' AND column_name = 'domains'
    ) THEN
        ALTER TABLE reading_sessions ADD COLUMN domains TEXT[];
        RAISE NOTICE 'Added domains column';
    ELSE
        RAISE NOTICE 'domains column already exists';
    END IF;
END $$;

-- Add total_tokens_used column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reading_sessions' AND column_name = 'total_tokens_used'
    ) THEN
        ALTER TABLE reading_sessions ADD COLUMN total_tokens_used INTEGER;
        RAISE NOTICE 'Added total_tokens_used column';
    ELSE
        RAISE NOTICE 'total_tokens_used column already exists';
    END IF;
END $$;

-- Add cache_hit column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reading_sessions' AND column_name = 'cache_hit'
    ) THEN
        ALTER TABLE reading_sessions ADD COLUMN cache_hit BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added cache_hit column';
    ELSE
        RAISE NOTICE 'cache_hit column already exists';
    END IF;
END $$;

-- Drop profile_id NOT NULL constraint if it exists (causes issues)
DO $$
BEGIN
    ALTER TABLE reading_sessions ALTER COLUMN profile_id DROP NOT NULL;
    RAISE NOTICE 'Dropped NOT NULL constraint on profile_id';
EXCEPTION
    WHEN undefined_column THEN
        RAISE NOTICE 'profile_id column does not exist';
    WHEN OTHERS THEN
        RAISE NOTICE 'profile_id NOT NULL constraint already removed or does not exist';
END $$;

-- Drop reading_type check constraint if it exists (causes issues)
DO $$
BEGIN
    ALTER TABLE reading_sessions DROP CONSTRAINT IF EXISTS reading_sessions_reading_type_check;
    RAISE NOTICE 'Dropped reading_type check constraint if it existed';
END $$;

-- Final success message
DO $$
BEGIN
    RAISE NOTICE 'SUCCESS: Migration complete! Phase 3 columns are now available.';
END $$;
