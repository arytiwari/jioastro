# Azure OpenAI Embedding Update - Status

**Date**: 2025-11-06
**Status**: ⚠️ DATABASE MIGRATION REQUIRED

---

## ✅ What Was Updated

### Azure OpenAI Configuration Detected

Your Azure OpenAI configuration is now using:
- **Model**: text-embedding-3-large
- **Deployment**: text-embedding-3-large
- **Dimensions**: 3072 (default for this model)
- **API Version**: 2025-01-01-preview

### Code Updates Completed

✅ Updated all embedding generation services to handle Azure OpenAI properly:

1. **rule_extraction_service.py** - Rule extraction embeddings
2. **document_processor.py** - Document chunk embeddings
3. **knowledge_base.py** - Knowledge base embeddings

All services now detect Azure vs OpenAI and handle the API differences correctly.

---

## ⚠️ Critical Issue: Dimension Mismatch

**Problem**: Your Azure deployment outputs **3072 dimensions**, but the database expects **1536 dimensions**.

### Current State

```
Azure OpenAI text-embedding-3-large: 3072 dimensions ✅
Database knowledge_base.embedding:   1536 dimensions ❌
                                     ↑
                                     MISMATCH
```

### Impact

- Embeddings cannot be stored in the database
- Vector similarity search will fail
- Rule extraction will complete but embeddings won't persist

---

## 🔧 Solution: Database Migration Required

### Step 1: Run SQL Migration in Supabase

**File**: `backend/docs/database-migrations/003_update_embedding_dimensions_to_3072.sql`

**Instructions**:
1. Open Supabase Dashboard
2. Go to SQL Editor → New Query
3. Copy the entire contents of `003_update_embedding_dimensions_to_3072.sql`
4. Paste and click "Run"

**What the migration does**:
```sql
1. Drop existing vector index
2. ALTER TABLE knowledge_base
   ALTER COLUMN embedding TYPE vector(3072)
3. Recreate vector index for 3072 dimensions
4. Update match_knowledge() function signature
5. Clear existing embeddings (1536-dim incompatible)
```

**Important Notes**:
- ✅ All 10 existing rules will be preserved
- ❌ Existing embeddings will be cleared (0 currently, so no data loss)
- ⏱️ Migration takes ~5 seconds
- 🔒 No data loss (rules remain, only embeddings cleared)

---

### Step 2: Verify Migration

After running the SQL, verify it worked:

```bash
cd backend
source venv/bin/activate
python scripts/run_embedding_dimension_migration.py verify
```

**Expected Output**:
```
✅ knowledge_base table accessible
✅ Embedding column exists
📊 Detected dimensions: 3072
✅ MIGRATION SUCCESSFUL - Dimensions = 3072
📚 Total rules: 10
```

---

### Step 3: Test Embedding Generation

After migration, test that embeddings are being stored:

```bash
python -c "
import asyncio
from app.services.rule_extraction_service import rule_extraction_service
from app.services.supabase_service import supabase_service

async def test():
    # Test rule
    test_rule = {
        'condition': 'Sun in 1st house',
        'effect': 'Strong personality and leadership',
        'domain': 'general',
        'confidence': 'high'
    }

    # Generate embedding
    embedding = await rule_extraction_service._generate_rule_embedding(test_rule)

    print(f'✅ Generated embedding: {len(embedding)} dimensions')

    # Try to store in database
    try:
        response = supabase_service.client.table('knowledge_base').insert({
            'rule_id': 'TEST-EMBED-001',
            'domain': 'general',
            'condition': test_rule['condition'],
            'effect': test_rule['effect'],
            'weight': 0.9,
            'embedding': embedding
        }).execute()

        print('✅ Successfully stored embedding in database!')

        # Clean up test rule
        supabase_service.client.table('knowledge_base')\
            .delete().eq('rule_id', 'TEST-EMBED-001').execute()
        print('✅ Test cleanup complete')

    except Exception as e:
        print(f'❌ Failed to store embedding: {e}')

asyncio.run(test())
"
```

**Expected Output**:
```
✅ Generated embedding: 3072 dimensions
✅ Successfully stored embedding in database!
✅ Test cleanup complete
```

---

### Step 4: Re-process Documents (Optional)

Once embeddings are working, you can re-process documents:

```bash
# Process all documents
python scripts/reprocess_knowledge_documents.py

# Or process single document
python scripts/reprocess_knowledge_documents.py <document-id>
```

**Note**: Currently uploaded documents are scanned PDFs with no text, so they won't extract rules until you upload text versions.

---

## 📊 Technical Details

### Why 3072 Dimensions?

**text-embedding-3-large** is OpenAI's newest embedding model:
- **Default dimensions**: 3072
- **Advantages**: Better semantic understanding, higher quality embeddings
- **Disadvantages**: 2x storage space vs ada-002 (1536 dimensions)

### Azure OpenAI vs Standard OpenAI

| Feature | Azure OpenAI | Standard OpenAI |
|---------|--------------|-----------------|
| `dimensions` parameter | ❌ Not supported | ✅ Supported |
| Configuration | Set at deployment level | Set per API call |
| Default for text-embedding-3-large | 3072 | 3072 |

**Our Solution**: Code detects Azure and doesn't pass `dimensions` parameter.

### Database Schema Changes

**Before Migration**:
```sql
embedding vector(1536)
-- Index: ivfflat with 1536 dims
-- Function: match_knowledge(query_embedding vector(1536), ...)
```

**After Migration**:
```sql
embedding vector(3072)
-- Index: ivfflat with 3072 dims (recreated)
-- Function: match_knowledge(query_embedding vector(3072), ...)
```

---

## ✅ Current Code Status

All embedding generation code is now **Azure OpenAI compatible**:

### rule_extraction_service.py
```python
if settings.USE_AZURE_OPENAI:
    response = await self.client.embeddings.create(
        model=self.embedding_model,
        input=text_to_embed
        # Azure: dimensions configured at deployment level
    )
else:
    response = await self.client.embeddings.create(
        model=self.embedding_model,
        input=text_to_embed,
        dimensions=1536  # OpenAI: force 1536 dimensions
    )
```

This pattern is implemented in all 3 services that generate embeddings.

---

## 🎯 Success Criteria

The system will be fully operational when:

1. ✅ Azure OpenAI embedding configuration detected
2. ✅ Code updated to handle Azure API differences
3. ✅ Migration SQL file created
4. ⏳ **YOU ACTION: Run SQL migration in Supabase**
5. ⏳ **Verify**: Run verification script
6. ⏳ **Test**: Generate and store test embedding
7. ⏳ **Deploy**: Re-process documents with text versions

**Current Progress**: 3/7 Complete (43%)

**Blocking on**: Step 4 - SQL migration needs to be run manually in Supabase Dashboard

---

## 📝 Quick Reference

### Files Created/Updated

**Migrations**:
- `docs/database-migrations/003_update_embedding_dimensions_to_3072.sql`

**Scripts**:
- `scripts/run_embedding_dimension_migration.py`

**Services Updated**:
- `app/services/rule_extraction_service.py`
- `app/services/document_processor.py`
- `app/services/knowledge_base.py`

### Commands

```bash
# Verify current state
python scripts/run_embedding_dimension_migration.py

# After running SQL migration, verify
python scripts/run_embedding_dimension_migration.py verify

# Test embedding generation
python -c "..." # See Step 3 above

# Re-process documents
python scripts/reprocess_knowledge_documents.py
```

---

## 🚨 Troubleshooting

### Error: "dimensionality of array mismatch"

**Cause**: Migration not run yet, database still expects 1536 dimensions

**Fix**: Run the SQL migration in Supabase Dashboard

### Error: "AsyncEmbeddings.create() got an unexpected keyword argument 'dimensions'"

**Cause**: Azure OpenAI doesn't support the `dimensions` parameter

**Fix**: ✅ Already fixed in code - detects Azure and omits parameter

### Embeddings returning 1536 instead of 3072

**Cause**: Using old ada-002 model or wrong deployment

**Fix**: Verify `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` in `.env` is set to `text-embedding-3-large`

---

## 📞 Support

**Configuration Check**:
```bash
python -c "
from app.core.config import settings
print(f'USE_AZURE_OPENAI: {settings.USE_AZURE_OPENAI}')
print(f'EMBEDDING_DEPLOYMENT: {settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}')
"
```

**Test Embedding Dimensions**:
```bash
python -c "
import asyncio
from openai import AsyncAzureOpenAI
from app.core.config import settings

async def test():
    client = AsyncAzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
    )
    response = await client.embeddings.create(
        model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        input='test'
    )
    print(f'Dimensions: {len(response.data[0].embedding)}')

asyncio.run(test())
"
```

---

**Last Updated**: 2025-11-06
**Status**: ⚠️ WAITING FOR DATABASE MIGRATION
**Next Action**: Run SQL migration in Supabase Dashboard
**Estimated Time**: 5 minutes total (2 min migration + 3 min verification)
