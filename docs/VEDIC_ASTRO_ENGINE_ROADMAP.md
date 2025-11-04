# Vedic Astro Engine - Implementation Roadmap

## Vision
Transform JioAstro into a comprehensive AI-powered Vedic astrology platform that:
- Provides precise, scripture-grounded readings
- Reuses existing MVP chart calculations
- Exposes functionality via Web UI, REST APIs, and MCP
- Maintains privacy-first memory system
- Supports multiple modalities (Vedic, Palmistry, Numerology)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chart Pages  │  │ AI Readings  │  │ Chat Interface│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Existing Services (Preserve)             │  │
│  │  • astrology_service (Swiss Ephemeris)               │  │
│  │  • Charts: D1, D9, Moon                              │  │
│  │  • Vimshottari Dasha                                 │  │
│  │  • Yoga Detection                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           NEW: Vedic Astro Engine Layer              │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │ MVP Bridge  │  │  Knowledge   │  │    LLM     │ │  │
│  │  │   Layer     │  │     Base     │  │Orchestrator│ │  │
│  │  └─────────────┘  └──────────────┘  └────────────┘ │  │
│  │         │                │                  │        │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │  Add-ons    │  │   Memory     │  │   Remedy   │ │  │
│  │  │  (Transits, │  │   System     │  │  Generator │ │  │
│  │  │  Shadbala)  │  └──────────────┘  └────────────┘ │  │
│  │  └─────────────┘                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Layer (Triple Exposure)              │  │
│  │  • REST APIs (/api/v1/readings/*)                   │  │
│  │  • MCP Server (tools for Claude Desktop)            │  │
│  │  • WebSocket (streaming predictions)                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL (Supabase)                       │
│  • Existing: profiles, charts, queries, responses           │
│  • NEW: kb_rules, kb_sources, user_memory, event_anchors   │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Foundation (Week 1-2) ⭐ START HERE
**Goal**: Build the bridge layer and database schema

#### 1.1 Database Schema
- [ ] Create `kb_sources` table (books, articles)
- [ ] Create `kb_rules` table (scripture rules)
- [ ] Create `kb_rule_embeddings` table (vector search)
- [ ] Create `user_memory` table (privacy-first)
- [ ] Create `event_anchors` table (rectification)
- [ ] Create `reading_sessions` table (cache by hash)
- [ ] Add indexes and constraints
- [ ] Create migration script

#### 1.2 MVP Bridge Layer
- [ ] Create `services/mvp_bridge.py`
- [ ] Implement `get_charts()` wrapper
- [ ] Add `canonical_hash` generation
- [ ] Implement caching by (user_id, hash)
- [ ] Add standardized output format
- [ ] Create unit tests

#### 1.3 Basic API Endpoints
- [ ] `POST /api/v1/readings/calculate` (MVP bridge)
- [ ] `GET /api/v1/readings/{session_id}` (cached)
- [ ] Health check endpoints
- [ ] API documentation

**Deliverable**: Working bridge layer that wraps existing astrology services

---

### Phase 2: Knowledge Base (Week 3-4)
**Goal**: Implement scripture-grounded rule system

#### 2.1 Rule Schema & Ingestion
- [ ] Design Rule JSON schema
- [ ] Create admin ingestion API
- [ ] Build text parser for BPHS/Phaladeepika
- [ ] Extract rules from first chapter
- [ ] Store in `kb_rules` table
- [ ] Generate embeddings (OpenAI)

#### 2.2 Retrieval System
- [ ] Implement symbolic key extraction
- [ ] Build vector search (pgvector)
- [ ] Create semantic reranking
- [ ] Implement conflict resolution
- [ ] Add rule weighting logic
- [ ] Create KB version control

#### 2.3 Bootstrap Initial Rules
- [ ] Ingest 50+ rules from BPHS
- [ ] Add Phaladeepika rules
- [ ] Include Jataka Parijata basics
- [ ] Create golden test cases
- [ ] Validate rule application

**Deliverable**: Working knowledge base with retrieval system

---

### Phase 3: LLM Orchestration (Week 5-6)
**Goal**: Implement AI-powered reading generation

#### 3.1 Core Orchestration
- [ ] Create `services/ai_orchestrator.py`
- [ ] Implement Coordinator role
- [ ] Implement Retriever role
- [ ] Implement Synthesizer role
- [ ] Implement Verifier role
- [ ] Add token budget tracking

#### 3.2 Prediction Engine
- [ ] Build domain predictors (Career, Health, etc.)
- [ ] Implement dasha × transit overlap logic
- [ ] Create date window calculator
- [ ] Add confidence scoring
- [ ] Generate citations

#### 3.3 Memory System
- [ ] Implement memory read/write
- [ ] Add event anchor storage
- [ ] Create preference management
- [ ] Build memory deduplication
- [ ] Add user erasure support

**Deliverable**: AI engine producing grounded predictions

---

### Phase 4: Add-ons & Enhancements (Week 7)
**Goal**: Fill gaps not in MVP

#### 4.1 Astro Add-ons
- [ ] Transit calculations (if needed)
- [ ] Shadbala implementation
- [ ] Extended yoga detection
- [ ] Ashtakavarga basics
- [ ] Argala analysis (optional)

#### 4.2 Rectification Mode
- [ ] Create anchor collection UI
- [ ] Implement time interval search
- [ ] Build confidence calculator
- [ ] Add rectification API

#### 4.3 Remedy Generator
- [ ] Traditional remedy rules
- [ ] Practical suggestions
- [ ] Remedy pairing logic
- [ ] Citation to sources

**Deliverable**: Complete prediction system with remedies

---

### Phase 5: MCP Integration (Week 8)
**Goal**: Expose as tools for Claude Desktop

#### 5.1 MCP Server
- [ ] Create `mcp_server/` directory
- [ ] Implement MCP protocol
- [ ] Define tool schemas
- [ ] Add authentication
- [ ] Create documentation

#### 5.2 MCP Tools
- [ ] `get_birth_chart` tool
- [ ] `generate_reading` tool
- [ ] `ask_vedic_question` tool
- [ ] `find_auspicious_time` tool
- [ ] `rectify_birth_time` tool

#### 5.3 Testing
- [ ] Test with Claude Desktop
- [ ] Create example workflows
- [ ] Write MCP user guide

**Deliverable**: Working MCP server for AI assistants

---

### Phase 6: Frontend AI Interface (Week 9-10)
**Goal**: Beautiful, intuitive AI reading UI

#### 6.1 Reading Pages
- [ ] `/dashboard/readings/new` - Generate reading
- [ ] `/dashboard/readings/[id]` - View reading
- [ ] `/dashboard/readings/history` - Past readings
- [ ] Reading progress indicator
- [ ] Domain tabs (Career, Health, etc.)

#### 6.2 Chat Interface
- [ ] `/dashboard/ask-ai` - Chat with AI
- [ ] Streaming responses
- [ ] Context awareness
- [ ] Citation display
- [ ] Follow-up questions

#### 6.3 Rectification UI
- [ ] Event anchor collection form
- [ ] Time interval display
- [ ] Confidence visualization
- [ ] Accept/reject rectified time

**Deliverable**: Complete AI-powered frontend

---

### Phase 7: Palmistry & Numerology (Week 11-12)
**Goal**: Multi-modal readings

#### 7.1 Palmistry Module
- [ ] Image upload API
- [ ] Vision model integration (GPT-4 Vision)
- [ ] Line/mount extraction
- [ ] Palm rule ingestion
- [ ] Fusion with Vedic chart

#### 7.2 Numerology Module
- [ ] Name/DoB processing
- [ ] Pythagorean calculation
- [ ] Chaldean calculation
- [ ] Life path/destiny numbers
- [ ] Compatibility analysis

#### 7.3 Fusion Logic
- [ ] Combine Vedic + Palm predictions
- [ ] Add numerology layer
- [ ] Weighted scoring
- [ ] Multi-modal UI

**Deliverable**: Complete multi-modal system

---

### Phase 8: Production & Scale (Week 13-14)
**Goal**: Production-ready deployment

#### 8.1 Performance
- [ ] Query optimization
- [ ] Caching strategy
- [ ] Rate limiting
- [ ] Background jobs (Celery)
- [ ] CDN for charts

#### 8.2 Monitoring
- [ ] Error tracking (Sentry)
- [ ] Performance metrics
- [ ] Usage analytics
- [ ] Cost tracking
- [ ] User feedback collection

#### 8.3 Documentation
- [ ] API documentation (OpenAPI)
- [ ] MCP documentation
- [ ] User guides
- [ ] Developer docs
- [ ] Video tutorials

#### 8.4 Testing
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] Golden case regression
- [ ] Load testing
- [ ] Security audit

**Deliverable**: Production-ready system

---

## Technology Stack

### Backend
- **Existing**: FastAPI, SQLAlchemy, Supabase, Swiss Ephemeris
- **New**:
  - OpenAI API (GPT-4 for orchestration)
  - pgvector (vector search)
  - Redis (caching)
  - Celery (background jobs)

### Frontend
- **Existing**: Next.js 14, TypeScript, Tailwind, shadcn/ui
- **New**:
  - Streaming UI components
  - Chart visualization enhancements
  - Real-time prediction display

### Infrastructure
- **Existing**: Supabase PostgreSQL
- **New**:
  - Redis (Upstash)
  - Vector DB (pgvector extension)
  - MCP server deployment

## Key Principles

1. **Preserve Existing Work**: Never break current functionality
2. **Incremental Enhancement**: Add features layer by layer
3. **Test-Driven**: Golden cases before and after
4. **Cost-Aware**: Token budgets, caching, optimization
5. **Privacy-First**: User-erasable memory, minimal storage
6. **Citation-Required**: Every claim traces to a rule
7. **API-First**: Every feature exposed via API and UI

## Success Metrics

- [ ] All existing chart features work unchanged
- [ ] AI readings cite sources correctly
- [ ] Response time < 10s for full reading
- [ ] Cost per reading < $0.50
- [ ] User satisfaction > 4.5/5
- [ ] MCP tools work in Claude Desktop
- [ ] Test coverage > 80%
- [ ] Zero data breaches

## Next Steps

**Immediate**: Start Phase 1.1 - Database Schema
- Design tables for knowledge base
- Create migration scripts
- Set up vector search extension

**This Week**: Complete Phase 1
- Bridge layer implementation
- Basic API endpoints
- Unit tests

**This Month**: Complete Phases 1-3
- Full knowledge base
- AI orchestration
- Working predictions

---

*Updated: 2025-11-03*
*Version: 1.0*
