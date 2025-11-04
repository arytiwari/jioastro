# Phase 2: Knowledge Base Development

**Goal**: Implement scripture-grounded rule system with RAG retrieval
**Duration**: 2 weeks (Week 3-4)
**Status**: 🚧 In Progress

---

## Overview

Phase 2 builds the knowledge base that grounds all AI predictions in classical Vedic astrology scriptures. Every prediction must cite a specific rule, making the system transparent and verifiable.

### Core Components

1. **Rule Schema** - Structured format for astrological rules
2. **Ingestion System** - Parse and store rules from scriptures
3. **Embedding Generation** - OpenAI embeddings for semantic search
4. **Symbolic Keys** - Fast lookup by planetary placements
5. **RAG Retrieval** - Hybrid search (symbolic + semantic)
6. **Conflict Resolution** - Handle contradicting rules

---

## Rule Format

### Canonical Structure

```python
{
  "rule_id": "BPHS-15-3",           # Source-Chapter-Verse
  "source_id": "uuid-of-bphs",      # FK to kb_sources

  # Classification
  "domain": "career",                # career, health, wealth, etc.
  "chart_context": "natal",          # natal, dasha, transit, varga
  "scope": "house",                  # house, sign, planet, aspect, yoga

  # Rule Content
  "condition": "IF Sun in 10th house",  # Condition clause
  "effect": "THEN success in government, authority, leadership", # Effect clause
  "modifiers": ["strength", "combustion"],  # Modifying factors

  # Metadata
  "weight": 0.8,                     # Importance (0.0-1.0)
  "anchor": "Chapter 15, Verse 3",   # Original location
  "sanskrit_text": "सूर्यः दशमे...",  # Original Sanskrit
  "translation": "When Sun occupies...",
  "commentary": "Explains the reasoning...",

  # Application
  "applicable_vargas": ["D1"],       # Which charts this applies to
  "requires_yoga": null,             # Prerequisite yoga
  "cancelers": ["BPHS-15-7"],       # Rules that cancel this

  # Symbolic Keys (auto-generated)
  "symbolic_keys": [
    "Sun_10",                        # Planet_House
    "Sun_Capricorn_10",              # Planet_Sign_House
    "government_career"              # Domain tags
  ]
}
```

### Rule Examples

**Example 1: House Lord Placement**
```json
{
  "rule_id": "BPHS-24-12",
  "domain": "career",
  "condition": "IF 10th lord in 4th house",
  "effect": "THEN gains through property, real estate, vehicles",
  "weight": 0.7,
  "anchor": "Chapter 24, Verse 12"
}
```

**Example 2: Planetary Conjunction**
```json
{
  "rule_id": "BPHS-18-5",
  "domain": "wealth",
  "condition": "IF Jupiter conjunct Venus in 2nd house",
  "effect": "THEN wealth through teaching, counseling, or creative arts",
  "weight": 0.85,
  "modifiers": ["strength", "dignity"]
}
```

**Example 3: Dasha Period**
```json
{
  "rule_id": "BPHS-46-8",
  "chart_context": "dasha",
  "condition": "IF Saturn Mahadasha AND Saturn in 8th house",
  "effect": "THEN obstacles, delays, but ultimate transformation",
  "weight": 0.75
}
```

---

## Implementation Steps

### Step 1: Rule Ingestion Service

**File**: `backend/app/services/knowledge_base.py`

```python
class KnowledgeBaseService:
    async def ingest_rule(self, rule_data: dict) -> UUID:
        """
        Ingest a single rule into the knowledge base

        1. Validate rule schema
        2. Store in kb_rules table
        3. Extract symbolic keys
        4. Generate embeddings
        5. Store in kb_rule_embeddings
        6. Store in kb_symbolic_keys
        """

    async def ingest_bulk(self, rules: list[dict]) -> list[UUID]:
        """Batch ingest multiple rules"""

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate OpenAI embedding for rule text"""

    async def extract_symbolic_keys(self, rule: dict) -> list[str]:
        """Extract symbolic keys from rule"""
```

### Step 2: Sample Rules Dataset

**File**: `backend/data/bphs_rules_sample.json`

Start with 50 foundational rules covering:
- House lord placements (12 houses × main combinations) = ~20 rules
- Major yogas (Raj Yoga, Dhana Yoga, etc.) = ~15 rules
- Planetary strengths (exaltation, debilitation) = ~10 rules
- Dasha interpretations (basic Mahadasha effects) = ~5 rules

### Step 3: Ingestion Script

**File**: `backend/scripts/ingest_bphs_rules.py`

```python
async def main():
    # 1. Load sample rules JSON
    # 2. Connect to database
    # 3. Verify kb_sources has BPHS entry
    # 4. For each rule:
    #    - Validate schema
    #    - Ingest into KB
    #    - Generate embeddings
    #    - Store symbolic keys
    # 5. Verify ingestion
    # 6. Generate statistics
```

### Step 4: Retrieval System

**File**: `backend/app/services/rule_retrieval.py`

```python
class RuleRetrievalService:
    async def retrieve_rules(
        self,
        chart_data: dict,
        query: Optional[str] = None,
        domain: Optional[str] = None,
        limit: int = 10
    ) -> list[dict]:
        """
        Hybrid retrieval:
        1. Symbolic key exact matches (fast)
        2. Vector similarity search (semantic)
        3. Rerank by relevance
        4. Filter by domain/context
        5. Resolve conflicts
        """

    async def symbolic_lookup(
        self, keys: list[str]
    ) -> list[dict]:
        """Fast lookup by symbolic keys"""

    async def semantic_search(
        self, query_embedding: list[float], limit: int
    ) -> list[dict]:
        """Vector similarity search"""

    async def resolve_conflicts(
        self, rules: list[dict]
    ) -> list[dict]:
        """Handle contradicting rules"""
```

### Step 5: Testing

**File**: `backend/tests/test_knowledge_base.py`

Test cases:
- Rule ingestion (single, bulk)
- Embedding generation
- Symbolic key extraction
- Rule retrieval (symbolic, semantic, hybrid)
- Conflict resolution

---

## Initial Rules to Ingest

### Priority 1: House Lords (20 rules)

**Template**: "10th lord in Nth house"
- 10th lord in each of 12 houses (career effects)
- 2nd lord in key houses (wealth effects)
- 7th lord in key houses (relationship effects)

### Priority 2: Major Yogas (15 rules)

- Gaja Kesari Yoga
- Raj Yoga (lord of trine + lord of angle)
- Dhana Yoga (wealth combinations)
- Viparita Raj Yoga
- Budhaditya Yoga
- Hamsa/Malavya/Ruchaka/Bhadra/Shasha Yogas

### Priority 3: Planetary Strength (10 rules)

- Exaltation effects (9 planets)
- Debilitation effects (9 planets)
- Retrograde effects
- Combustion effects

### Priority 4: Dasha Effects (5 rules)

- Basic Mahadasha interpretations
- Antardasha combinations
- Transit overlays

---

## Data Sources

### Available

- ✅ BPHS Vol 1 PDF (`Reference Books/Maharishi_Parashara_-_Brihat_Parasara_Hora_Sastra_(Vol._1).pdf`)
- ✅ BPHS Vol 2 PDF (`Reference Books/brihat-parashara-hora-sastra-02.pdf.pdf`)
- ✅ BPHS Full PDF (`Reference Books/brihat-parashara-hora-sastra.pdf`)

### To Extract

From BPHS chapters:
- Chapter 1-5: Foundational concepts
- Chapter 15: Planet and house strengths
- Chapter 18: Planetary combinations
- Chapter 24: House lord effects
- Chapter 46: Dasha interpretations

---

## Success Metrics

- ✅ 50+ rules ingested
- ✅ All rules have embeddings
- ✅ Symbolic keys generated
- ✅ Retrieval returns relevant rules
- ✅ Conflict resolution works
- ✅ Golden test cases pass

---

## Technical Stack

- **Embeddings**: OpenAI `text-embedding-ada-002` (1536 dimensions)
- **Vector DB**: PostgreSQL with pgvector
- **Symbolic Lookup**: PostgreSQL B-tree indexes
- **Conflict Resolution**: Weight-based + rule hierarchy

---

## Timeline

**Week 3** (Nov 4-10):
- Day 1-2: Rule schema + ingestion service
- Day 3-4: Extract 50 rules from BPHS
- Day 5-7: Embedding generation + storage

**Week 4** (Nov 11-17):
- Day 1-3: Retrieval system (symbolic + semantic)
- Day 4-5: Conflict resolution
- Day 6-7: Testing + validation

---

## Next Steps

1. ✅ Review this plan
2. Create `services/knowledge_base.py`
3. Create `data/bphs_rules_sample.json` with first 10 rules
4. Build ingestion script
5. Test with sample rules
6. Scale to 50+ rules

---

*Phase 2 Implementation Plan*
*Created: 2025-11-03*
