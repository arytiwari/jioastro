# Azure Embedding Dimension Configuration Options

## Problem

Your Azure OpenAI `text-embedding-3-large` deployment outputs **3072 dimensions**, but pgvector's **ivfflat index has a 2000 dimension limit**.

**Error**: `column cannot have more than 2000 dimensions for ivfflat index`

---

## Option 1: Use HNSW Index (Recommended) ⭐

**Keep 3072 dimensions, use better index type**

### Advantages
- ✅ Full 3072-dimensional embeddings (better quality)
- ✅ HNSW is faster than ivfflat for most queries
- ✅ Better recall and precision
- ✅ Only requires SQL migration (no Azure config changes)

### Disadvantages
- ⚠️ Uses 2x storage space vs 1536 dimensions
- ⚠️ Slightly longer indexing time during document processing

### Implementation

**Run this SQL in Supabase Dashboard**:

File: `backend/docs/database-migrations/003_update_embedding_dimensions_to_3072_HNSW.sql`

```sql
-- Drop old ivfflat index
DROP INDEX IF EXISTS idx_knowledge_base_embedding;

-- Update column to 3072 dimensions
ALTER TABLE public.knowledge_base
ALTER COLUMN embedding TYPE vector(3072);

-- Create HNSW index (no dimension limit!)
CREATE INDEX idx_knowledge_base_embedding
ON public.knowledge_base
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Update match_knowledge function
DROP FUNCTION IF EXISTS match_knowledge(vector, float, int, text);
CREATE OR REPLACE FUNCTION match_knowledge(
    query_embedding vector(3072),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5,
    filter_domain text DEFAULT NULL
)
RETURNS TABLE (...)
-- [full function in migration file]

-- Clear old embeddings
UPDATE public.knowledge_base SET embedding = NULL WHERE embedding IS NOT NULL;
```

**Verification**:
```bash
python scripts/run_embedding_dimension_migration.py verify
```

---

## Option 2: Reduce to 1536 Dimensions (Simpler)

**Keep database at 1536 dimensions, reconfigure Azure deployment**

### Advantages
- ✅ No database migration needed (already configured for 1536)
- ✅ 50% less storage space
- ✅ Faster indexing and queries
- ✅ Compatible with existing ivfflat index

### Disadvantages
- ⚠️ Slightly lower embedding quality (still excellent)
- ⚠️ Requires reconfiguring Azure deployment

### Implementation

**Step 1**: Update Azure OpenAI Deployment

Unfortunately, Azure OpenAI **doesn't currently support runtime dimension configuration** via API. The dimensions are **set at deployment level**.

You have two sub-options:

#### Option 2A: Create New Deployment with 1536 Dimensions

1. Go to Azure OpenAI Studio
2. Navigate to Deployments
3. Create a **new deployment**:
   - Model: `text-embedding-3-large`
   - Deployment name: `text-embedding-3-large-1536`
   - **Dimensions**: 1536 (if available in Azure UI)

4. Update your `.env`:
   ```bash
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large-1536
   ```

**Note**: As of now, Azure may not expose dimension configuration in the UI. In that case, use Option 2B.

#### Option 2B: Use text-embedding-ada-002 Instead

The classic ada-002 model outputs 1536 dimensions by default:

1. Go to Azure OpenAI Studio
2. Create deployment:
   - Model: `text-embedding-ada-002`
   - Deployment name: `text-embedding-ada-002`

3. Update your `.env`:
   ```bash
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
   ```

**Trade-offs**:
- ✅ Works immediately with existing database
- ✅ Proven, stable model
- ⚠️ Slightly lower quality than text-embedding-3-large
- ⚠️ Older model (but still excellent for most use cases)

**Verification**:
```bash
python -c "
import asyncio
from app.services.rule_extraction_service import rule_extraction_service

async def test():
    test_rule = {
        'condition': 'Mars in 10th house',
        'effect': 'Career success',
        'domain': 'career',
        'confidence': 'high'
    }
    embedding = await rule_extraction_service._generate_rule_embedding(test_rule)
    print(f'Dimensions: {len(embedding)}')
    if len(embedding) == 1536:
        print('✅ Perfect! 1536 dimensions - compatible with database')
    else:
        print(f'⚠️  Got {len(embedding)} dimensions')

asyncio.run(test())
"
```

---

## Comparison Table

| Aspect | Option 1: HNSW (3072-dim) | Option 2: Reduce (1536-dim) |
|--------|---------------------------|------------------------------|
| **Migration Required** | Yes (SQL only) | No |
| **Azure Config Change** | No | Yes |
| **Embedding Quality** | ⭐⭐⭐⭐⭐ Highest | ⭐⭐⭐⭐ Excellent |
| **Storage Space** | 3072 floats per rule | 1536 floats per rule |
| **Query Speed** | Fast (HNSW) | Fast (ivfflat) |
| **Implementation Time** | 5 minutes | 10-15 minutes |
| **Complexity** | Low (just SQL) | Medium (Azure reconfig) |

---

## Recommendation

### Use Option 1 (HNSW with 3072 dimensions) if:
- ✅ You want the best possible embedding quality
- ✅ You're okay with 2x storage space
- ✅ You prefer a simple SQL-only migration
- ✅ You want to use the latest model

### Use Option 2 (Reduce to 1536) if:
- ✅ You want to minimize storage space
- ✅ You're comfortable reconfiguring Azure
- ✅ You want to avoid database migration
- ✅ Slightly lower quality is acceptable (still excellent)

**My Recommendation**: **Option 1 (HNSW)** - Easier to implement, better quality, and HNSW is a better index anyway.

---

## Implementation Guide: Option 1 (HNSW)

### Step 1: Check pgvector Version

Verify Supabase has pgvector >= 0.5.0 (needed for HNSW):

```sql
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

Expected: `0.5.0` or higher

If lower version, Supabase support can update it, or use Option 2.

### Step 2: Run Migration

Copy contents of:
```
backend/docs/database-migrations/003_update_embedding_dimensions_to_3072_HNSW.sql
```

Paste in: **Supabase Dashboard → SQL Editor → New Query**

Click **Run**

### Step 3: Verify

```bash
cd backend
source venv/bin/activate
python scripts/run_embedding_dimension_migration.py verify
```

Expected output:
```
✅ knowledge_base table accessible
✅ Embedding column exists
📊 Detected dimensions: 3072
✅ MIGRATION SUCCESSFUL - Dimensions = 3072
```

### Step 4: Test Embedding Storage

```bash
python -c "
import asyncio
from app.services.rule_extraction_service import rule_extraction_service
from app.services.supabase_service import supabase_service

async def test():
    print('Testing 3072-dim embedding storage...')

    test_rule = {
        'condition': 'Sun in 1st house',
        'effect': 'Strong personality',
        'domain': 'general',
        'confidence': 'high'
    }

    embedding = await rule_extraction_service._generate_rule_embedding(test_rule)
    print(f'✅ Generated: {len(embedding)} dimensions')

    response = supabase_service.client.table('knowledge_base').insert({
        'rule_id': 'TEST-3072-001',
        'domain': 'general',
        'condition': test_rule['condition'],
        'effect': test_rule['effect'],
        'weight': 0.9,
        'embedding': embedding
    }).execute()

    print('✅ Successfully stored 3072-dim embedding!')

    # Cleanup
    supabase_service.client.table('knowledge_base')\
        .delete().eq('rule_id', 'TEST-3072-001').execute()
    print('✅ Test complete')

asyncio.run(test())
"
```

### Step 5: Ready to Process Documents

Your system is now ready! When you upload text-based documents:
- Rules will be extracted automatically
- 3072-dimensional embeddings will be generated
- Stored with HNSW index for fast semantic search

---

## Troubleshooting

### Error: "index method 'hnsw' not recognized"

**Cause**: pgvector version < 0.5.0

**Fix**: Contact Supabase support to update pgvector, or use Option 2

### Error: "out of memory"

**Cause**: HNSW indexing large dataset with high dimensions

**Fix**: Reduce HNSW parameters:
```sql
-- Lower memory usage (slightly lower recall)
CREATE INDEX ... USING hnsw (...) WITH (m = 8, ef_construction = 32);
```

### Embeddings still showing 3072 but should be 1536

**Cause**: Azure deployment not changed (if using Option 2)

**Fix**: Verify `.env` has correct deployment name, restart backend

---

## Performance Notes

### HNSW vs IVFFlat

Based on pgvector benchmarks:

| Metric | HNSW | IVFFlat |
|--------|------|---------|
| Query Speed | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Recall | ⭐⭐⭐⭐⭐ (>95%) | ⭐⭐⭐⭐ (85-95%) |
| Index Build Time | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Memory Usage | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Dimension Limit | No limit | 2000 |

**Verdict**: HNSW is better for most use cases, especially high-dimensional embeddings.

---

## Next Steps After Migration

1. ✅ Upload text versions of your PDF documents
2. ✅ System will automatically extract rules
3. ✅ 3072-dim embeddings generated and stored
4. ✅ Vector similarity search enabled
5. ✅ AI responses include relevant rule citations

---

**Created**: 2025-11-06
**Status**: Awaiting your choice of Option 1 or Option 2
**Recommended**: Option 1 (HNSW with 3072 dimensions)
