-- Migration: Create knowledge_base table for storing astrology rules
-- Date: 2025-11-06
-- Description: Stores extracted rules from knowledge documents with vector embeddings

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create knowledge_base table
CREATE TABLE IF NOT EXISTS public.knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Rule identification
    rule_id VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(50) NOT NULL DEFAULT 'general',

    -- Rule content
    condition TEXT NOT NULL,
    effect TEXT NOT NULL,
    anchor TEXT,  -- Source reference (book, chapter, verse)
    commentary TEXT,

    -- Metadata
    weight DECIMAL(3, 2) DEFAULT 1.0,
    tags TEXT[],

    -- Document linkage
    document_id UUID REFERENCES public.knowledge_documents(id) ON DELETE CASCADE,

    -- Vector embedding for semantic search (OpenAI embedding dimension: 1536)
    embedding vector(1536),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Search optimization
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(condition, '') || ' ' || coalesce(effect, '') || ' ' || coalesce(commentary, ''))
    ) STORED
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_knowledge_base_domain ON public.knowledge_base(domain);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_rule_id ON public.knowledge_base(rule_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_document_id ON public.knowledge_base(document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_search ON public.knowledge_base USING GIN(search_vector);

-- Create index for vector similarity search (IVFFlat for approximate nearest neighbor)
CREATE INDEX IF NOT EXISTS idx_knowledge_base_embedding
ON public.knowledge_base
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create function for vector similarity search
CREATE OR REPLACE FUNCTION match_knowledge(
    query_embedding vector(1536),
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
        AND 1 - (kb.embedding <=> query_embedding) > match_threshold
    ORDER BY kb.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Insert sample rules to test the system
INSERT INTO public.knowledge_base (rule_id, domain, condition, effect, anchor, weight)
VALUES
    ('BPHS-SAMPLE-01', 'general', 'Sun in 1st house', 'Strong personality, leadership qualities, good health', 'Brihat Parashara Hora Shastra, Chapter 1', 0.9),
    ('BPHS-SAMPLE-02', 'career', 'Jupiter in 10th house', 'Success in career, recognition, authority position', 'Brihat Parashara Hora Shastra, Chapter 10', 0.95),
    ('BPHS-SAMPLE-03', 'wealth', 'Venus in 2nd house', 'Wealth accumulation, luxury, artistic talents, sweet speech', 'Brihat Parashara Hora Shastra, Chapter 2', 0.9),
    ('BPHS-SAMPLE-04', 'relationships', 'Moon in 7th house', 'Emotional partner, caring spouse, fluctuating relationships', 'Brihat Parashara Hora Shastra, Chapter 7', 0.85),
    ('BPHS-SAMPLE-05', 'health', 'Mars in 6th house', 'Energy to overcome enemies and diseases, competitive nature', 'Brihat Parashara Hora Shastra, Chapter 6', 0.9),
    ('BPHS-SAMPLE-06', 'education', 'Mercury in 4th house', 'Good education, intelligent mind, communication skills', 'Brihat Parashara Hora Shastra, Chapter 4', 0.9),
    ('BPHS-SAMPLE-07', 'spirituality', 'Jupiter in 9th house', 'Religious inclination, dharmic life, spiritual wisdom', 'Brihat Parashara Hora Shastra, Chapter 9', 0.95),
    ('BPHS-SAMPLE-08', 'career', 'Saturn in 10th house', 'Slow but steady career growth, discipline, hard work pays off', 'Brihat Parashara Hora Shastra, Chapter 10', 0.9),
    ('BPHS-SAMPLE-09', 'wealth', 'Jupiter in 11th house', 'Gains from multiple sources, fulfilled desires, prosperous', 'Brihat Parashara Hora Shastra, Chapter 11', 0.95),
    ('BPHS-SAMPLE-10', 'relationships', 'Venus in 7th house', 'Loving spouse, harmonious marriage, artistic partner', 'Brihat Parashara Hora Shastra, Chapter 7', 0.95)
ON CONFLICT (rule_id) DO NOTHING;

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_knowledge_base_updated_at
    BEFORE UPDATE ON public.knowledge_base
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust based on your RLS policies)
ALTER TABLE public.knowledge_base ENABLE ROW LEVEL SECURITY;

-- Allow service role full access (backend operations)
CREATE POLICY "Service role has full access to knowledge_base"
ON public.knowledge_base
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Allow authenticated users to read knowledge base
CREATE POLICY "Authenticated users can read knowledge_base"
ON public.knowledge_base
FOR SELECT
TO authenticated
USING (true);

-- Allow anon role to read knowledge base (for public queries)
CREATE POLICY "Anon users can read knowledge_base"
ON public.knowledge_base
FOR SELECT
TO anon
USING (true);

COMMENT ON TABLE public.knowledge_base IS 'Stores astrology rules extracted from knowledge documents with vector embeddings for semantic search';
COMMENT ON COLUMN public.knowledge_base.embedding IS 'OpenAI ada-002 embedding (1536 dimensions) for semantic similarity search';
COMMENT ON COLUMN public.knowledge_base.weight IS 'Rule importance weight (0.0 to 1.0), higher means more authoritative';
COMMENT ON FUNCTION match_knowledge IS 'Performs vector similarity search to find relevant rules for a query embedding';
