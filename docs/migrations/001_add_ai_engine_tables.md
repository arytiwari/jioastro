# Migration 001: Add AI Engine Tables

**Date**: 2025-11-03
**Purpose**: Add Knowledge Base, Reading Sessions, and User Memory tables for Vedic Astro Engine

## Prerequisites

1. Enable pgvector extension in Supabase:
   - Go to Supabase Dashboard → Database → Extensions
   - Enable `vector` extension

## Apply Migration

### Option 1: Supabase Dashboard (Recommended)

1. Go to Supabase Dashboard → SQL Editor
2. Click "New Query"
3. Copy the entire contents of `../database-schema-ai-engine.sql`
4. Click "Run"
5. Verify all tables created successfully

### Option 2: Command Line

```bash
# Using psql
psql "postgresql://[connection-string]" -f docs/database-schema-ai-engine.sql

# Or using Supabase CLI
supabase db push
```

## Verification

Run this query to verify all tables were created:

```sql
SELECT table_name
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
```

Expected result: 12 tables

## Check Vector Extension

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

Should return one row.

## Sample Queries

### Check initial sources

```sql
SELECT COUNT(*) FROM kb_sources;
-- Should return 5 (BPHS, Phaladeepika, etc.)
```

### Verify RLS policies

```sql
SELECT schemaname, tablename, policyname
FROM pg_policies
WHERE tablename IN ('reading_sessions', 'user_memory', 'event_anchors')
ORDER BY tablename, policyname;
```

## Rollback (if needed)

```sql
-- Drop all AI engine tables (CAUTION: destroys data!)
DROP TABLE IF EXISTS user_rule_confirmations CASCADE;
DROP TABLE IF EXISTS event_anchors CASCADE;
DROP TABLE IF EXISTS user_memory CASCADE;
DROP TABLE IF EXISTS reading_feedback CASCADE;
DROP TABLE IF EXISTS reading_sessions CASCADE;
DROP TABLE IF EXISTS kb_rule_feedback CASCADE;
DROP TABLE IF EXISTS kb_symbolic_keys CASCADE;
DROP TABLE IF EXISTS kb_rule_embeddings CASCADE;
DROP TABLE IF EXISTS kb_rules CASCADE;
DROP TABLE IF EXISTS kb_sources CASCADE;
DROP TABLE IF EXISTS palm_readings CASCADE;
DROP TABLE IF EXISTS numerology_profiles CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS clean_expired_reading_sessions() CASCADE;
```

## Post-Migration Steps

1. **Bootstrap Knowledge Base**: Run the initial rule ingestion script
2. **Generate Embeddings**: Create vector embeddings for existing rules
3. **Test RLS**: Verify row-level security works for a test user
4. **Set up Cleanup**: Schedule `clean_expired_reading_sessions()` to run daily

## Notes

- All tables have RLS enabled for security
- Vector embeddings use OpenAI ada-002 (1536 dimensions)
- Reading sessions expire after 30 days by default
- User memory is version-controlled for safe updates
- Knowledge base rules are weighted and versioned

## Next Steps

After migration:
1. Proceed to Phase 1.2: Build MVP Bridge Layer
2. Start ingesting rules from BPHS into `kb_rules`
3. Generate embeddings for semantic search
