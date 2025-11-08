-- Migration: Add gender field to profiles table
-- Date: 2025-11-08
-- Description: Add optional gender field to support gender-specific astrological interpretations

-- Add gender column to profiles table (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'profiles' AND column_name = 'gender'
    ) THEN
        ALTER TABLE profiles 
        ADD COLUMN gender TEXT CHECK (gender IN ('male', 'female', 'other'));
        
        -- Add comment
        COMMENT ON COLUMN profiles.gender IS 'Optional gender field for astrological interpretations. Values: male, female, other';
    END IF;
END $$;

-- Create index on gender for filtering (optional, useful for analytics)
CREATE INDEX IF NOT EXISTS idx_profiles_gender ON profiles(gender);
