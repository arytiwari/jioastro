# Switch to text-embedding-ada-002 Guide

## Problem

Both pgvector index types have dimension limits:
- **IVFFlat**: Max 2000 dimensions
- **HNSW**: Max 2000 dimensions

Your current `text-embedding-3-large` outputs **3072 dimensions**, which exceeds both limits.

## Solution: Use text-embedding-ada-002

Switch to `text-embedding-ada-002` which outputs **1536 dimensions** (well under the 2000 limit).

### Performance Comparison

| Model | Dimensions | Quality | Speed | Compatibility |
|-------|-----------|---------|-------|---------------|
| text-embedding-3-large | 3072 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ Too large |
| **text-embedding-ada-002** | **1536** | **⭐⭐⭐⭐** | **⭐⭐⭐⭐⭐** | **✅ Perfect** |

**Note**: ada-002 is still excellent quality - it's the industry standard used by most production applications.

---

## Step-by-Step Implementation

### Step 1: Create New Azure Deployment

1. Go to **Azure OpenAI Studio**
2. Navigate to **Deployments**
3. Click **Create new deployment**
4. Configure:
   - **Model**: `text-embedding-ada-002`
   - **Deployment name**: `text-embedding-ada-002`
   - **Version**: Latest available
5. Click **Create**

### Step 2: Update Backend Configuration

Update your `.env` file:

```bash
# Change this line:
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# To this:
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

### Step 3: Restart Backend

```bash
# Kill any running backend processes
pkill -f "uvicorn main:app"

# Restart
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Step 4: Verify Configuration

```bash
cd backend
source venv/bin/activate
python -c "
from app.core.config import settings
print('Azure OpenAI Configuration:')
print(f'USE_AZURE_OPENAI: {settings.USE_AZURE_OPENAI}')
print(f'EMBEDDING_DEPLOYMENT: {settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}')
"
```

**Expected Output**:
```
Azure OpenAI Configuration:
USE_AZURE_OPENAI: True
EMBEDDING_DEPLOYMENT: text-embedding-ada-002
```

### Step 5: Test Embedding Dimensions

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

    if embedding:
        print(f'✅ Embedding dimensions: {len(embedding)}')
        if len(embedding) == 1536:
            print('✅ PERFECT! Compatible with database (1536 dimensions)')
        else:
            print(f'⚠️  Unexpected: {len(embedding)} dimensions')
    else:
        print('❌ Failed to generate embedding')

asyncio.run(test())
"
```

**Expected Output**:
```
✅ Embedding dimensions: 1536
✅ PERFECT! Compatible with database (1536 dimensions)
```

### Step 6: Test Database Storage

```bash
python -c "
import asyncio
from app.services.rule_extraction_service import rule_extraction_service
from app.services.supabase_service import supabase_service

async def test():
    print('🧪 Testing 1536-dim Embedding Storage')
    print('=' * 60)

    test_rule = {
        'condition': 'Sun in 1st house',
        'effect': 'Strong personality',
        'domain': 'general',
        'confidence': 'high'
    }

    embedding = await rule_extraction_service._generate_rule_embedding(test_rule)
    print(f'✅ Generated: {len(embedding)} dimensions')

    response = supabase_service.client.table('knowledge_base').insert({
        'rule_id': 'TEST-ADA002-001',
        'domain': 'general',
        'condition': test_rule['condition'],
        'effect': test_rule['effect'],
        'weight': 0.9,
        'embedding': embedding
    }).execute()

    if response.data:
        print('✅ Successfully stored embedding in database!')
        print('🎉 System is fully operational!')

        # Cleanup
        supabase_service.client.table('knowledge_base')\
            .delete().eq('rule_id', 'TEST-ADA002-001').execute()
        print('✅ Test cleanup complete')
    else:
        print('❌ Failed to store embedding')

asyncio.run(test())
"
```

**Expected Output**:
```
🧪 Testing 1536-dim Embedding Storage
============================================================
✅ Generated: 1536 dimensions
✅ Successfully stored embedding in database!
🎉 System is fully operational!
✅ Test cleanup complete
```

---

## Verification Checklist

After completing all steps:

- [ ] Azure deployment created for text-embedding-ada-002
- [ ] `.env` updated with new deployment name
- [ ] Backend restarted
- [ ] Configuration verified
- [ ] Embedding dimensions = 1536
- [ ] Test embedding stored successfully

Once all checkmarks are complete, your system is ready to:
- Extract rules from documents automatically
- Generate 1536-dim embeddings
- Store embeddings with vector similarity search
- Retrieve relevant rules for AI responses

---

## Database Status

**Good news**: The database is already configured correctly for 1536 dimensions!

- Current schema: `vector(1536)` ✅
- Index: ivfflat (supports up to 2000 dims) ✅
- Function: `match_knowledge(vector(1536), ...)` ✅

**No database migration needed** - just update Azure configuration.

---

## Next Steps After Configuration

1. **Upload text versions of your PDF documents**
   - Convert PDFs to .txt using OCR
   - Upload via admin portal

2. **System automatically processes documents**:
   - Extracts text
   - Uses GPT-4 to extract rules
   - Generates 1536-dim embeddings
   - Stores in knowledge_base table

3. **Verify in admin interface**:
   - Navigate to `/admin/dashboard/knowledge`
   - Check "Rules" tab for extracted rules
   - Check "Overview" for stats

4. **Test AI integration**:
   - Go to `/dashboard/ask`
   - Ask astrology question
   - Verify response includes rule citations like `[BPHS-XX-XXX]`

---

## Troubleshooting

### Error: "Deployment not found"

**Cause**: Azure deployment name incorrect or not created

**Fix**: Verify deployment exists in Azure OpenAI Studio → Deployments

### Still getting 3072 dimensions

**Cause**: Backend still using old configuration

**Fix**:
1. Check `.env` has correct deployment name
2. Restart backend: `pkill -f uvicorn && uvicorn main:app --reload`
3. Clear any cached environment variables

### Error: "dimensionality mismatch"

**Cause**: Database expecting different dimensions

**Fix**: Run verification to check database schema:
```bash
python scripts/run_embedding_dimension_migration.py verify
```

---

## Why text-embedding-ada-002 is Perfect

**Proven Track Record**:
- Used by thousands of production applications
- Highly optimized and stable
- Excellent semantic understanding

**Performance**:
- Fast inference (< 50ms per embedding)
- Efficient storage (1536 floats vs 3072)
- High recall and precision

**Compatibility**:
- Works with all pgvector indexes
- Industry standard dimension size
- Maximum interoperability

**Cost**:
- Lower cost per embedding than 3-large
- 50% less storage space
- Faster queries

---

**Created**: 2025-11-06
**Status**: Ready to implement
**Time Required**: 10-15 minutes
**Complexity**: Low (just config change)
