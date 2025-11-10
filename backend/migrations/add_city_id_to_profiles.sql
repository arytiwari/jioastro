-- Migration: Add city_id foreign key to profiles table
-- Date: 2025-11-10
-- Description: Link profiles to cities table for consistent city display

-- Add city_id column to profiles table (nullable for backward compatibility)
ALTER TABLE profiles
ADD COLUMN city_id INTEGER;

-- Add foreign key constraint
ALTER TABLE profiles
ADD CONSTRAINT fk_profiles_city
FOREIGN KEY (city_id) REFERENCES cities(id)
ON DELETE SET NULL;

-- Create index for faster lookups
CREATE INDEX idx_profiles_city_id ON profiles(city_id);

-- Update existing profiles to link with cities based on birth_city text
-- This is optional and can be run manually if needed
-- UPDATE profiles p
-- SET city_id = (
--     SELECT c.id
--     FROM cities c
--     WHERE c.display_name ILIKE p.birth_city
--     LIMIT 1
-- )
-- WHERE p.birth_city IS NOT NULL AND p.city_id IS NULL;

-- Note: birth_city column is kept for backward compatibility
-- New profiles should use city_id, but old profiles can still use birth_city
