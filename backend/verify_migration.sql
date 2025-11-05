-- ============================================================================
-- MIGRATION VERIFICATION QUERIES
-- Run these in Supabase SQL Editor after applying the migration
-- ============================================================================

-- Query 1: Check all 12 tables were created
SELECT
  table_name,
  CASE
    WHEN table_name IN (
      'kb_sources', 'kb_rules', 'kb_rule_embeddings', 'kb_symbolic_keys', 'kb_rule_feedback',
      'reading_sessions', 'reading_feedback', 'user_memory', 'event_anchors',
      'user_rule_confirmations', 'palm_readings', 'numerology_profiles'
    ) THEN '✅ Expected'
    ELSE '⚠️ Unexpected'
  END as status
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'kb_sources',
  'kb_rules',
  'kb_rule_embeddings',
  'kb_symbolic_keys',
  'kb_rule_feedback',
  'reading_sessions',
  'reading_feedback',
  'user_memory',
  'event_anchors',
  'user_rule_confirmations',
  'palm_readings',
  'numerology_profiles'
)
ORDER BY table_name;

-- Expected: 12 rows


-- Query 2: Verify vector extension enabled
SELECT
  extname as extension_name,
  extversion as version,
  '✅ Vector extension enabled' as status
FROM pg_extension
WHERE extname = 'vector';

-- Expected: 1 row showing 'vector' extension


-- Query 3: Check initial sources seeded
SELECT
  COUNT(*) as source_count,
  CASE
    WHEN COUNT(*) = 5 THEN '✅ All 5 sources seeded'
    WHEN COUNT(*) > 0 THEN '⚠️ Partial seeding'
    ELSE '❌ No sources'
  END as status
FROM kb_sources;

-- Expected: 5 sources (BPHS, Phaladeepika, Jataka Parijata, Brihat Jataka, Saravali)


-- Query 4: List all seeded sources
SELECT
  title,
  author,
  work_type,
  publication_year
FROM kb_sources
ORDER BY title;

-- Expected: 5 classical scripture sources


-- Query 5: Verify RLS (Row Level Security) policies
SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles
FROM pg_policies
WHERE tablename IN ('reading_sessions', 'user_memory', 'event_anchors', 'reading_feedback', 'user_rule_confirmations')
ORDER BY tablename, policyname;

-- Expected: Multiple RLS policies for user-owned tables


-- Query 6: Check table structures
SELECT
  table_name,
  COUNT(*) as column_count
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name IN (
  'kb_sources', 'kb_rules', 'reading_sessions', 'user_memory'
)
GROUP BY table_name
ORDER BY table_name;

-- Expected:
-- kb_sources: ~10 columns
-- kb_rules: ~20 columns
-- reading_sessions: ~15 columns
-- user_memory: ~10 columns


-- Query 7: Test reading_sessions table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'reading_sessions'
ORDER BY ordinal_position;

-- Should show: id, user_id, profile_id, canonical_hash, charts, predictions, etc.


-- ============================================================================
-- QUICK SUMMARY CHECK
-- ============================================================================

SELECT
  '1. Tables' as check_type,
  COUNT(*)::text || ' of 12' as result,
  CASE WHEN COUNT(*) = 12 THEN '✅' ELSE '❌' END as status
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
  'kb_sources', 'kb_rules', 'kb_rule_embeddings', 'kb_symbolic_keys', 'kb_rule_feedback',
  'reading_sessions', 'reading_feedback', 'user_memory', 'event_anchors',
  'user_rule_confirmations', 'palm_readings', 'numerology_profiles'
)

UNION ALL

SELECT
  '2. Vector Extension' as check_type,
  'Enabled' as result,
  CASE WHEN EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN '✅' ELSE '❌' END
FROM pg_extension WHERE extname = 'vector' LIMIT 1

UNION ALL

SELECT
  '3. Initial Sources' as check_type,
  COUNT(*)::text || ' of 5' as result,
  CASE WHEN COUNT(*) = 5 THEN '✅' ELSE '⚠️' END
FROM kb_sources

UNION ALL

SELECT
  '4. RLS Policies' as check_type,
  COUNT(DISTINCT tablename)::text || ' tables' as result,
  CASE WHEN COUNT(DISTINCT tablename) >= 5 THEN '✅' ELSE '⚠️' END
FROM pg_policies
WHERE tablename IN ('reading_sessions', 'user_memory', 'event_anchors', 'reading_feedback', 'user_rule_confirmations');

-- Expected output:
-- ✅ 1. Tables: 12 of 12
-- ✅ 2. Vector Extension: Enabled
-- ✅ 3. Initial Sources: 5 of 5
-- ✅ 4. RLS Policies: 5 tables
