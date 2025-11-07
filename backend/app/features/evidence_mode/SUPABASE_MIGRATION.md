# Evidence Mode - Supabase Migration Guide

## Quick Start

### Option 1: Supabase SQL Editor (Recommended)

1. **Open Supabase Dashboard**
   - Go to https://app.supabase.com
   - Select your JioAstro project

2. **Navigate to SQL Editor**
   - Click "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Copy and Run Migration**
   - Open `supabase_migration.sql` in this directory
   - Copy the entire contents
   - Paste into the SQL Editor
   - Click "Run" or press `Cmd/Ctrl + Enter`

4. **Verify Success**
   - You should see success messages in the Results panel
   - Check the final summary output showing:
     ```
     Sources created: 5
     Citations created: 2
     Validations created: 0
     ```

5. **Enable Feature Flag**
   - Add to your `.env` file:
     ```bash
     FEATURE_EVIDENCE_MODE=true
     ```
   - Restart your backend server

### Option 2: Supabase CLI

If you have the Supabase CLI installed:

```bash
# From the backend directory
supabase db reset --db-url "$DATABASE_URL"
psql "$DATABASE_URL" -f app/features/evidence_mode/supabase_migration.sql
```

### Option 3: Direct psql Connection

If you prefer command line:

```bash
# Get your connection string from Supabase Dashboard
# Settings → Database → Connection String (use "Direct connection")

# Run migration
psql "postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres" \
  -f app/features/evidence_mode/supabase_migration.sql
```

## What This Migration Does

### 1. Creates Database Objects

**Enums (3):**
- `evidence_source_type` - Types of sources (classical_text, research_paper, etc.)
- `evidence_confidence_level` - Confidence ratings (very_high to very_low)
- `evidence_validation_status` - Validation states (pending, validated, disputed, rejected)

**Tables (3):**
- `evidence_mode_sources` - Reference sources (classical texts, papers, etc.)
- `evidence_mode_citations` - Links insights to sources
- `evidence_mode_validations` - Expert peer review records

**Indexes (15):**
- Performance indexes on commonly queried fields
- Full-text search index on sources

### 2. Sets Up Security

**Row Level Security (RLS):**
- Public sources/citations visible to all
- Users can manage their own records
- Validators control their validations
- Automatic user ID tracking via `auth.uid()`

### 3. Loads Initial Data

**Classical Texts (5):**
- Brihat Parashara Hora Shastra (BPHS) - Credibility: 0.98
- Brihat Jataka - Credibility: 0.97
- Saravali - Credibility: 0.96
- Jataka Parijata - Credibility: 0.95
- Phaladeepika - Credibility: 0.94

**Sample Citations (2):**
- Raj Yoga definition
- Gaja Kesari Yoga definition

### 4. Creates Helper Objects

**Triggers:**
- Auto-update `updated_at` timestamps

**Views:**
- `evidence_mode_summary` - Quick stats overview

## Verification

After running the migration, verify it worked:

### Check Tables Exist

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_name LIKE 'evidence_mode%';
```

Expected output:
- evidence_mode_sources
- evidence_mode_citations
- evidence_mode_validations

### Check Data Loaded

```sql
SELECT * FROM evidence_mode_summary;
```

Expected output:
| entity_type | total_count | verified_count | public_count |
|-------------|-------------|----------------|--------------|
| sources     | 5           | 5              | 5            |
| citations   | 2           | 2              | 2            |
| validations | 0           | 0              | 0            |

### Check Sample Source

```sql
SELECT title, author, credibility_score
FROM evidence_mode_sources
WHERE title LIKE '%BPHS%';
```

## Testing the API

Once migration is complete and backend restarted:

1. **Check API Documentation**
   - Visit: http://localhost:8000/docs
   - Look for "Magical 12" tag
   - You should see 16 Evidence Mode endpoints

2. **Test Source Retrieval**
   ```bash
   curl http://localhost:8000/api/v2/evidence-mode/sources/search \
     -H "Content-Type: application/json" \
     -d '{"query": "BPHS", "page": 1, "page_size": 20}'
   ```

3. **Test Citation Search**
   ```bash
   curl http://localhost:8000/api/v2/evidence-mode/citations/search \
     -H "Content-Type: application/json" \
     -d '{"insight_type": "yoga", "page": 1}'
   ```

## Troubleshooting

### Error: "type already exists"

The migration has already been run. To re-run:

1. Drop existing objects first:
   ```sql
   DROP VIEW IF EXISTS evidence_mode_summary;
   DROP TABLE IF EXISTS evidence_mode_validations CASCADE;
   DROP TABLE IF EXISTS evidence_mode_citations CASCADE;
   DROP TABLE IF EXISTS evidence_mode_sources CASCADE;
   DROP TYPE IF EXISTS evidence_validation_status;
   DROP TYPE IF EXISTS evidence_confidence_level;
   DROP TYPE IF EXISTS evidence_source_type;
   DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
   ```

2. Then run the full migration again

### Error: "permission denied"

Ensure you're using the correct database credentials with sufficient permissions. The Supabase dashboard SQL Editor runs with admin privileges.

### No Data Showing in API

1. Check feature flag is enabled: `FEATURE_EVIDENCE_MODE=true`
2. Restart backend server
3. Check RLS policies allow access
4. Verify data exists: `SELECT COUNT(*) FROM evidence_mode_sources;`

## Next Steps

1. ✅ Run migration
2. ✅ Enable feature flag
3. ✅ Restart backend
4. 🔄 Test API endpoints
5. 🔄 Run unit tests: `pytest app/features/evidence_mode/tests/`
6. 🔄 Integrate with AI service (see IMPLEMENTATION.md)
7. 🔄 Build frontend UI components

## Support

For detailed implementation docs, see:
- `IMPLEMENTATION.md` - Complete feature documentation
- `test_service.py` - Unit test examples
- `feature.py` - API endpoint reference

---

**Questions?** Check the IMPLEMENTATION.md file or API documentation at `/docs`
