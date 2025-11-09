# Palmistry Database Migration - Deployment Guide

**Date:** 2025-11-08
**Migration Version:** 2.0 (Corrected)

---

## ⚠️ IMPORTANT: Migration Order

There are **3 SQL files** for the Palmistry migration. Execute them in this **exact order**:

### Step 1: Cleanup (If tables already exist)

If you've run any previous Palmistry migration, run the cleanup script first:

**File:** `00_cleanup_palmistry_tables.sql`

```sql
-- This script will:
-- 1. Drop all existing palmistry views
-- 2. Drop all existing palmistry tables
-- 3. Drop all related functions
-- 4. Verify cleanup was successful
```

**How to run:**
1. Go to Supabase Dashboard → SQL Editor
2. Copy entire contents of `00_cleanup_palmistry_tables.sql`
3. Click "Run"
4. Verify output shows 0 tables remaining

**Expected Output:**
```
table_name
----------
(0 rows)
```

---

### Step 2: Create Tables (Main Migration)

**File:** `create_palmistry_tables_v2.sql`

```sql
-- This script will:
-- 1. Create 6 tables (palm_photos, palm_readings, palm_interpretations, ai_models, reanalysis_queue, palm_feedback)
-- 2. Create indexes for performance
-- 3. Enable Row Level Security (RLS)
-- 4. Create RLS policies
-- 5. Create auto-update triggers
-- 6. Create utility views and functions
-- 7. Insert seed data (5 placeholder AI models)
-- 8. Run verification queries
```

**How to run:**
1. Go to Supabase Dashboard → SQL Editor
2. Copy entire contents of `create_palmistry_tables_v2.sql`
3. Click "Run"
4. Verify output shows all tables created

**Expected Output (at end of migration):**
```
table_name              | column_count
-----------------------|-------------
palm_feedback          | 7
palm_interpretations   | 15
palm_photos           | 14
palm_readings         | 16
reanalysis_queue      | 9
ai_models             | 13

(RLS policies shown)

model_name              | model_version           | model_type
-----------------------|------------------------|------------------
MediaPipe Hands        | v1.0.0-placeholder     | hand_detection
Palm Line Detector     | v1.0.0-placeholder     | line_detection
Mount Detector         | v1.0.0-placeholder     | mount_detection
Hand Shape Classifier  | v1.0.0-placeholder     | shape_classification
GPT-4 RAG             | gpt-4-turbo-placeholder| rag_model
```

---

### Step 3: Create Storage Buckets

After tables are created, create the Supabase Storage buckets:

**How to create:**
1. Go to Supabase Dashboard → Storage
2. Click "New bucket"
3. Create bucket: `palm-images`
   - Public: No (private)
   - File size limit: 10 MB
   - Allowed MIME types: `image/jpeg`, `image/png`, `image/webp`
4. Create bucket: `palm-thumbnails`
   - Public: Yes (thumbnails can be public)
   - File size limit: 1 MB
   - Allowed MIME types: `image/jpeg`, `image/png`, `image/webp`

**Set bucket policies:**

For `palm-images` bucket:
```sql
-- Allow authenticated users to upload their own images
CREATE POLICY "Users can upload their own images"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'palm-images' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Allow users to view their own images
CREATE POLICY "Users can view their own images"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'palm-images' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Allow users to delete their own images
CREATE POLICY "Users can delete their own images"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'palm-images' AND auth.uid()::text = (storage.foldername(name))[1]);
```

For `palm-thumbnails` bucket:
```sql
-- Allow authenticated users to upload thumbnails
CREATE POLICY "Users can upload thumbnails"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'palm-thumbnails' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Allow anyone to view thumbnails (public)
CREATE POLICY "Anyone can view thumbnails"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'palm-thumbnails');

-- Allow users to delete their own thumbnails
CREATE POLICY "Users can delete their thumbnails"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'palm-thumbnails' AND auth.uid()::text = (storage.foldername(name))[1]);
```

---

## Verification Steps

### 1. Verify Tables Created

```sql
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name LIKE 'palm_%'
ORDER BY table_name;
```

**Expected:** 6 tables listed

### 2. Verify RLS Policies

```sql
SELECT
    tablename,
    policyname,
    permissive
FROM pg_policies
WHERE tablename LIKE 'palm_%'
ORDER BY tablename, policyname;
```

**Expected:** 4 policies (one per user table)

### 3. Verify Indexes

```sql
SELECT
    tablename,
    indexname
FROM pg_indexes
WHERE tablename LIKE 'palm_%'
ORDER BY tablename, indexname;
```

**Expected:** 15+ indexes

### 4. Verify Seed Data

```sql
SELECT model_name, model_version, model_type, is_active
FROM ai_models
ORDER BY model_type;
```

**Expected:** 5 placeholder AI models

### 5. Verify View

```sql
SELECT * FROM v_recent_readings LIMIT 1;
```

**Expected:** Query executes successfully (may return 0 rows if no data yet)

### 6. Verify Storage Buckets

```sql
SELECT id, name, public
FROM storage.buckets
WHERE name LIKE 'palm-%'
ORDER BY name;
```

**Expected:**
```
id                  | name             | public
--------------------|------------------|--------
<uuid>             | palm-images      | false
<uuid>             | palm-thumbnails  | true
```

---

## Testing the API

After deployment, test the Palmistry API:

### 1. Health Check

```bash
curl http://localhost:8000/api/v1/palmistry/health
```

**Expected:**
```json
{
  "status": "healthy",
  "database_connected": true,
  "storage_accessible": true,
  "ai_models_loaded": true,
  "active_models": [
    {
      "model_name": "MediaPipe Hands",
      "model_version": "v1.0.0-placeholder",
      "model_type": "hand_detection",
      "is_active": true,
      ...
    },
    ...
  ],
  "queue_size": 0,
  "last_check": "2025-11-08T..."
}
```

### 2. Test via Swagger UI

Open: http://localhost:8000/docs

Look for **"palmistry"** tag and test:
- ✅ POST /palmistry/upload
- ✅ POST /palmistry/analyze
- ✅ GET /palmistry/readings
- ✅ GET /palmistry/readings/{id}
- ✅ GET /palmistry/compare
- ✅ POST /palmistry/feedback
- ✅ GET /palmistry/health

---

## Troubleshooting

### Error: "column does not exist"

**Solution:** Run cleanup script first, then migration again.

```bash
# Run in this order:
1. 00_cleanup_palmistry_tables.sql
2. create_palmistry_tables_v2.sql
```

### Error: "table already exists"

**Solution:** The cleanup script will handle this. Run cleanup first.

### Error: "permission denied for table"

**Solution:** Ensure you're using the Supabase service role key, not anon key.

### Error: "bucket already exists"

**Solution:** Delete existing buckets via Supabase Dashboard → Storage, then recreate.

### Health endpoint shows "unhealthy"

**Possible causes:**
1. Tables not created → Run migration
2. Storage buckets not created → Create buckets
3. RLS policies blocking → Check policies
4. No seed data → Re-run migration

---

## Rollback Instructions

If you need to rollback the migration:

### Option 1: Quick Rollback (Recommended)

```sql
-- Run the cleanup script
-- File: 00_cleanup_palmistry_tables.sql
```

This will remove all palmistry tables and related objects.

### Option 2: Manual Rollback

```sql
-- Drop all palmistry objects
DROP VIEW IF EXISTS v_recent_readings CASCADE;
DROP TABLE IF EXISTS palm_feedback CASCADE;
DROP TABLE IF EXISTS reanalysis_queue CASCADE;
DROP TABLE IF EXISTS palm_interpretations CASCADE;
DROP TABLE IF EXISTS palm_readings CASCADE;
DROP TABLE IF EXISTS ai_models CASCADE;
DROP TABLE IF EXISTS palm_photos CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS get_user_reading_stats(UUID) CASCADE;
```

### Delete Storage Buckets

1. Go to Supabase Dashboard → Storage
2. Delete `palm-images` bucket
3. Delete `palm-thumbnails` bucket

---

## Post-Deployment Checklist

- [ ] All 6 tables created successfully
- [ ] All RLS policies active
- [ ] All indexes created
- [ ] 5 seed AI models inserted
- [ ] View `v_recent_readings` works
- [ ] Storage bucket `palm-images` created (private)
- [ ] Storage bucket `palm-thumbnails` created (public)
- [ ] Health endpoint returns "healthy"
- [ ] Swagger UI shows all 7 endpoints
- [ ] Test endpoints with authentication

---

## Next Steps After Deployment

1. **Frontend Integration**
   - Build camera capture module
   - Create upload interface
   - Implement reading display

2. **AI Model Integration**
   - Deploy real hand detection model
   - Deploy line detection model
   - Deploy mount detection model
   - Integrate RAG pipeline

3. **Monitoring Setup**
   - Set up error tracking
   - Monitor upload success rate
   - Track analysis performance
   - Monitor storage usage

4. **User Testing**
   - Collect feedback
   - Monitor quality scores
   - Analyze reading confidence
   - Iterate based on feedback

---

## File Locations

**Migration Files:**
- Cleanup: `/migrations/00_cleanup_palmistry_tables.sql`
- Main Migration: `/migrations/create_palmistry_tables_v2.sql`
- Old Migration (don't use): `/migrations/create_palmistry_tables.sql`

**Documentation:**
- This Guide: `/migrations/PALMISTRY_DEPLOYMENT_GUIDE.md`
- Architecture: `/docs/PALMISTRY_SYSTEM_ARCHITECTURE.md`
- Implementation Summary: `/docs/PALMISTRY_IMPLEMENTATION_SUMMARY.md`

**Code:**
- ORM Models: `/app/models/palmistry.py`
- Schemas: `/app/schemas/palmistry.py`
- Storage Service: `/app/services/palmistry_storage_service.py`
- Analysis Service: `/app/services/palm_analysis_service.py`
- API Endpoints: `/app/api/v1/endpoints/palmistry.py`

---

**Deployment Guide Version:** 1.0
**Last Updated:** 2025-11-08
**Maintained By:** JioAstro Development Team
