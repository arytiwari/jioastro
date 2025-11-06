-- Migration: Update embedding dimensions from 1536 to 3072 with HNSW index
-- Date: 2025-11-06
-- Description: Update knowledge_base table to use text-embedding-3-large (3072 dimensions)
-- Uses HNSW index instead of IVFFlat (supports >2000 dimensions)

-- Step 1: Drop existing vector index (required before altering column type)
DROP INDEX IF EXISTS idx_knowledge_base_embedding;

-- Step 2: Alter embedding column to use vector(3072)
ALTER TABLE public.knowledge_base
ALTER COLUMN embedding TYPE vector(3072);

-- Step 3: Create HNSW index (supports high dimensions, faster than ivfflat)
-- Note: Requires pgvector >= 0.5.0 (Supabase has this)
CREATE INDEX idx_knowledge_base_embedding
ON public.knowledge_base
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- HNSW Parameters:
-- m = 16: Number of connections per layer (default 16, higher = better recall, more memory)
-- ef_construction = 64: Size of dynamic candidate list (default 64, higher = better index quality, slower build)

-- Step 4: Update match_knowledge function to accept 3072-dimensional vectors
DROP FUNCTION IF EXISTS match_knowledge(vector, float, int, text);

CREATE OR REPLACE FUNCTION match_knowledge(
    query_embedding vector(3072),  -- Updated from 1536 to 3072
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5,
    filter_domain text DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    rule_id varchar,
    domain varchar,
    condition text,
    effect text,
    anchor text,
    commentary text,
    weight decimal,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kb.id,
        kb.rule_id,
        kb.domain,
        kb.condition,
        kb.effect,
        kb.anchor,
        kb.commentary,
        kb.weight,
        1 - (kb.embedding <=> query_embedding) AS similarity
    FROM knowledge_base kb
    WHERE
        (filter_domain IS NULL OR kb.domain = filter_domain)
        AND kb.embedding IS NOT NULL
        AND 1 - (kb.embedding <=> query_embedding) > match_threshold
    ORDER BY kb.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Step 5: Clear existing embeddings (they are 1536-dimensional and incompatible)
-- Note: This will delete existing embeddings but keep the rules
-- Rules will need to be re-processed to generate 3072-dimensional embeddings
UPDATE public.knowledge_base
SET embedding = NULL
WHERE embedding IS NOT NULL;

-- Step 6: Add comment documenting the change
COMMENT ON COLUMN public.knowledge_base.embedding IS 'OpenAI text-embedding-3-large (3072 dimensions) for semantic similarity search using HNSW index';

-- Verification queries
-- Run these after migration to verify:

-- 1. Check column type
-- SELECT column_name, udt_name, character_maximum_length
-- FROM information_schema.columns
-- WHERE table_name = 'knowledge_base' AND column_name = 'embedding';

-- 2. Check index exists and type
-- SELECT indexname, indexdef
-- FROM pg_indexes
-- WHERE tablename = 'knowledge_base' AND indexname = 'idx_knowledge_base_embedding';

-- 3. Check function signature
-- SELECT routine_name, data_type
-- FROM information_schema.routines
-- WHERE routine_name = 'match_knowledge';

-- 4. Count rules (should remain unchanged)
-- SELECT COUNT(*) FROM knowledge_base;

-- 5. Count embeddings (should be 0 after clearing)
-- SELECT COUNT(*) FROM knowledge_base WHERE embedding IS NOT NULL;

COMMENT ON TABLE public.knowledge_base IS 'Stores astrology rules extracted from knowledge documents with vector embeddings (3072-dim) using HNSW index for semantic search';
