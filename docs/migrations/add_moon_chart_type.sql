-- Migration: Add 'Moon' to chart_type constraint
-- Date: 2025-11-03
-- Description: Updates the charts table to allow 'Moon' as a valid chart_type

-- Drop the existing constraint
ALTER TABLE charts DROP CONSTRAINT IF EXISTS charts_chart_type_check;

-- Add the new constraint with Moon included
ALTER TABLE charts ADD CONSTRAINT charts_chart_type_check
  CHECK (chart_type IN ('D1', 'D9', 'Moon'));

-- Update the comment
COMMENT ON TABLE charts IS 'Cached birth charts (D1, D9, Moon, etc.)';

-- Verify the constraint was updated
SELECT constraint_name, check_clause
FROM information_schema.check_constraints
WHERE constraint_name = 'charts_chart_type_check';
