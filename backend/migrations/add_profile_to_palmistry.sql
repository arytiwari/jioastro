-- Migration: Add profile_id to palmistry tables for holistic AI readings
-- This connects palmistry readings to birth profiles for combined astrology/numerology/palmistry analysis

-- Add profile_id to palm_readings (nullable for backward compatibility)
ALTER TABLE palm_readings
ADD COLUMN IF NOT EXISTS profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL;

-- Create index for faster profile lookups
CREATE INDEX IF NOT EXISTS idx_palm_readings_profile ON palm_readings(profile_id);

-- Add profile_id to palm_interpretations (nullable for backward compatibility)
ALTER TABLE palm_interpretations
ADD COLUMN IF NOT EXISTS profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL;

-- Create index for faster profile lookups
CREATE INDEX IF NOT EXISTS idx_palm_interpretations_profile ON palm_interpretations(profile_id);

-- Add comment explaining the purpose
COMMENT ON COLUMN palm_readings.profile_id IS 'Links palmistry reading to birth profile for holistic AI analysis combining astrology, numerology, and palmistry';
COMMENT ON COLUMN palm_interpretations.profile_id IS 'Links palmistry interpretation to birth profile for cross-domain correlations';
