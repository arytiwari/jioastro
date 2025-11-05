-- Simple test migration to verify syntax
-- Just adds the interpretation column if it doesn't exist

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
