# Expert Knowledge Management System

**Status:** 📋 Planning Phase
**Purpose:** Enable domain experts to contribute knowledge for fine-tuning JioAstro's calculations and predictions

---

## System Overview

This system allows astrology experts to submit knowledge entries that:
1. Add new rules and insights (Additive)
2. Refine existing calculations (Incremental)
3. Correct or improve predictions (Updates)

All contributions are reviewed, versioned, and integrated into the core algorithm.

---

## Architecture

### Database Schema

#### 1. `expert_contributions` Table
```sql
CREATE TABLE expert_contributions (
    id SERIAL PRIMARY KEY,
    expert_id UUID REFERENCES users(id),
    contribution_type VARCHAR(20) NOT NULL, -- 'additive', 'incremental', 'update'
    category VARCHAR(50) NOT NULL, -- 'yoga', 'dasha', 'transit', 'house', 'planet', 'aspect'
    subcategory VARCHAR(100), -- Specific topic (e.g., 'raj_yoga', 'vimshottari_dasha')

    -- Content
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    rule_definition TEXT, -- Formal rule description
    example_charts TEXT, -- Birth chart examples demonstrating the rule
    expected_impact TEXT, -- How this should affect predictions

    -- Code/Algorithm
    algorithm_changes TEXT, -- Pseudo-code or actual code changes
    affected_modules TEXT[], -- Which Python modules this impacts
    test_cases JSONB, -- Test cases to validate the change

    -- Metadata
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'under_review', 'approved', 'implemented', 'rejected'
    priority VARCHAR(20) DEFAULT 'normal', -- 'low', 'normal', 'high', 'critical'
    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 10),

    -- References
    classical_reference TEXT, -- Reference to classical texts (BPHS, etc.)
    modern_reference TEXT, -- Reference to modern works
    research_data JSONB, -- Statistical data supporting the rule

    -- Versioning
    version INTEGER DEFAULT 1,
    replaces_contribution_id INTEGER REFERENCES expert_contributions(id),

    -- Review
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP,
    review_notes TEXT,

    -- Implementation
    implemented_by UUID REFERENCES users(id),
    implemented_at TIMESTAMP,
    implementation_notes TEXT,
    git_commit_hash VARCHAR(40),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_expert_contributions_status ON expert_contributions(status);
CREATE INDEX idx_expert_contributions_category ON expert_contributions(category);
CREATE INDEX idx_expert_contributions_expert ON expert_contributions(expert_id);
```

#### 2. `expert_contribution_comments` Table
```sql
CREATE TABLE expert_contribution_comments (
    id SERIAL PRIMARY KEY,
    contribution_id INTEGER REFERENCES expert_contributions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    comment TEXT NOT NULL,
    comment_type VARCHAR(20) DEFAULT 'general', -- 'general', 'question', 'suggestion', 'concern'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. `expert_contribution_votes` Table
```sql
CREATE TABLE expert_contribution_votes (
    id SERIAL PRIMARY KEY,
    contribution_id INTEGER REFERENCES expert_contributions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    vote INTEGER CHECK (vote IN (-1, 1)), -- -1 for downvote, 1 for upvote
    rationale TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(contribution_id, user_id)
);
```

#### 4. `expert_impact_tracking` Table
```sql
CREATE TABLE expert_impact_tracking (
    id SERIAL PRIMARY KEY,
    contribution_id INTEGER REFERENCES expert_contributions(id),
    chart_id UUID REFERENCES charts(id),

    -- Before/After Comparison
    prediction_before JSONB,
    prediction_after JSONB,
    accuracy_improvement FLOAT, -- Percentage improvement

    user_feedback TEXT,
    validated_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Knowledge Categories & Subcategories

### 1. Yogas (Planetary Combinations)
- Raj Yoga (Royal Combinations)
- Dhana Yoga (Wealth)
- Neecha Bhanga Raj Yoga (Cancellation of Debilitation)
- Mahapurusha Yoga (Great Person)
- Custom/Regional Yogas

### 2. Dashas (Planetary Periods)
- Vimshottari Dasha refinements
- Yogini Dasha
- Chara Dasha
- Dasha transition effects

### 3. Transits (Gochar)
- Saturn transit effects
- Jupiter transit effects
- Eclipse impacts
- Transit-natal interactions

### 4. Houses (Bhavas)
- House significations
- House lord relationships
- Bhavat Bhavam (House to House)

### 5. Planets (Grahas)
- Planetary strengths (Shadbala)
- Planetary dignities
- Planetary aspects
- Combustion effects

### 6. Aspects (Drishti)
- Special aspects
- Aspect strength calculations
- Aspect orbs

### 7. Divisional Charts (Vargas)
- D9 (Navamsa) interpretation
- D10 (Dasamsa) career insights
- Varga strength calculations

### 8. Remedies
- Gemstone recommendations
- Mantra prescriptions
- Donation suggestions
- Timing of remedies

---

## API Endpoints

### Expert Contributions
```
POST   /api/v1/admin/expert-knowledge/contributions          - Create new contribution
GET    /api/v1/admin/expert-knowledge/contributions          - List all contributions
GET    /api/v1/admin/expert-knowledge/contributions/{id}     - Get specific contribution
PUT    /api/v1/admin/expert-knowledge/contributions/{id}     - Update contribution
DELETE /api/v1/admin/expert-knowledge/contributions/{id}     - Delete contribution

POST   /api/v1/admin/expert-knowledge/contributions/{id}/review   - Submit review
POST   /api/v1/admin/expert-knowledge/contributions/{id}/approve  - Approve contribution
POST   /api/v1/admin/expert-knowledge/contributions/{id}/reject   - Reject contribution
POST   /api/v1/admin/expert-knowledge/contributions/{id}/implement - Mark as implemented
```

### Comments & Voting
```
POST   /api/v1/admin/expert-knowledge/contributions/{id}/comments     - Add comment
GET    /api/v1/admin/expert-knowledge/contributions/{id}/comments     - Get comments
POST   /api/v1/admin/expert-knowledge/contributions/{id}/vote         - Vote on contribution
```

### Impact Tracking
```
POST   /api/v1/admin/expert-knowledge/contributions/{id}/track-impact  - Record impact
GET    /api/v1/admin/expert-knowledge/contributions/{id}/impact        - View impact data
GET    /api/v1/admin/expert-knowledge/impact-report                   - Overall impact report
```

---

## Frontend Components

### 1. Expert Knowledge Dashboard (`/admin/dashboard/expert-knowledge`)
**Features:**
- Overview statistics (pending, approved, implemented)
- Recent contributions
- Top contributors
- Impact metrics

### 2. Contribution Submission Form
**Sections:**
- Basic Info (title, category, type)
- Description & Rules
- Examples & Test Cases
- References & Research
- Algorithm Changes (optional code)

**Form Fields:**
```typescript
interface ContributionForm {
  // Basic
  contributionType: 'additive' | 'incremental' | 'update'
  category: 'yoga' | 'dasha' | 'transit' | 'house' | 'planet' | 'aspect'
  subcategory: string
  title: string
  description: string

  // Details
  ruleDefinition: string
  exampleCharts: string
  expectedImpact: string

  // Technical
  algorithmChanges?: string
  affectedModules?: string[]
  testCases?: object

  // References
  classicalReference?: string
  modernReference?: string
  researchData?: object

  // Metadata
  priority: 'low' | 'normal' | 'high' | 'critical'
  confidenceLevel: number // 1-10
}
```

### 3. Contribution Review Interface
**Features:**
- Side-by-side comparison (current vs. proposed)
- Comment threads
- Voting mechanism
- Approve/Reject actions
- Implementation checklist

### 4. Knowledge Base Browser
**Features:**
- Search and filter
- Category tree view
- Status filters
- Sort by impact, votes, date
- Version history

---

## Workflow States

```
┌─────────────┐
│   Pending   │ ← Expert submits contribution
└──────┬──────┘
       │
       ↓
┌─────────────┐
│Under Review │ ← Admin/Senior experts review
└──────┬──────┘
       │
       ├───→ Approved ────→ Implemented ────→ Validated
       │
       └───→ Rejected (with feedback)
```

### State Transitions:
1. **Pending** → Expert submits
2. **Under Review** → Admin assigns reviewers
3. **Approved** → Reviewers approve (requires 2+ votes)
4. **Implemented** → Developer integrates into codebase
5. **Validated** → Impact tracking confirms improvement
6. **Rejected** → Reviewers reject (with detailed feedback)

---

## Integration with Core Logic

### 1. Runtime Integration
- Expert rules loaded from database at startup
- Applied as additional filters/weights in calculations
- Cached for performance

### 2. Code Generation
- Approved contributions generate Python code snippets
- Inserted into appropriate service modules
- Versioned with git commits

### 3. A/B Testing
- New rules tested on subset of predictions
- Compared against baseline accuracy
- Gradual rollout based on performance

### 4. Impact Measurement
- Track prediction accuracy before/after
- User feedback correlation
- Statistical significance testing

---

## Example Contributions

### Example 1: Additive (New Yoga)
```json
{
  "contributionType": "additive",
  "category": "yoga",
  "subcategory": "raj_yoga",
  "title": "Budha-Aditya Yoga Enhancement",
  "description": "When Mercury and Sun are within 3 degrees in houses 1, 4, 7, or 10, and aspected by Jupiter, the native gains exceptional intelligence and administrative abilities.",
  "ruleDefinition": "Sun-Mercury conjunction (< 3°) in Kendra houses (1,4,7,10) + Jupiter aspect → Enhanced Budha-Aditya Yoga",
  "algorithmChanges": "Add condition: if (sun_mercury_distance < 3 and house in [1,4,7,10] and jupiter_aspects): yoga_strength *= 1.5",
  "expectedImpact": "Increase intelligence and career success predictions by 20-30%",
  "classicalReference": "Brihat Parashara Hora Shastra, Chapter 41, Verse 15-17",
  "confidenceLevel": 8
}
```

### Example 2: Incremental (Refinement)
```json
{
  "contributionType": "incremental",
  "category": "dasha",
  "subcategory": "vimshottari_dasha",
  "title": "Saturn Dasha Intensity Adjustment",
  "description": "Saturn dasha effects should be weighted by its distance from Moon, not just house position.",
  "ruleDefinition": "Saturn dasha intensity = base_intensity * (1 - (saturn_moon_distance / 180))",
  "algorithmChanges": "Modify saturn_dasha_intensity calculation to include Moon distance factor",
  "expectedImpact": "More accurate Saturn dasha timing predictions, especially for career delays",
  "researchData": {
    "sample_size": 500,
    "accuracy_improvement": "12%"
  },
  "confidenceLevel": 9
}
```

### Example 3: Update (Correction)
```json
{
  "contributionType": "update",
  "category": "planet",
  "subcategory": "combustion",
  "title": "Mercury Combustion Distance Correction",
  "description": "Current system uses 14° for Mercury combustion, but classical texts specify 12° for most zodiac signs and 14° only in Virgo.",
  "ruleDefinition": "Mercury combustion distance: 12° (general), 14° (Virgo only)",
  "algorithmChanges": "Update combustion_distance(Mercury) = 14 if sign == Virgo else 12",
  "expectedImpact": "Fix false positives in Mercury combustion detection",
  "classicalReference": "Brihat Jataka, Chapter 2, Verse 5",
  "confidenceLevel": 10
}
```

---

## Quality Control

### Validation Checklist:
- [ ] Classical text reference provided
- [ ] Example birth charts demonstrate the rule
- [ ] Test cases defined
- [ ] Impact measurement criteria specified
- [ ] No conflicts with existing rules
- [ ] Peer review by 2+ experts
- [ ] Code review if algorithm changes included

### Rejection Criteria:
- Contradicts established classical principles
- Lacks sufficient evidence
- Too speculative (confidence < 5)
- Conflicts with other high-priority rules
- Implementation too complex/risky

---

## Gamification & Incentives

### Expert Reputation System:
- Points for contributions
- Badges for milestones (10 approved, 50 approved, etc.)
- Leaderboard of top contributors
- Special "Expert Astrologer" badge
- Early access to new features

### Contribution Metrics:
- Total submissions
- Approval rate
- Average impact score
- User upvotes
- Implementation rate

---

## Future Enhancements

### Phase 2:
- Machine learning integration
- Automated impact analysis
- Natural language processing for text references
- Visual rule builder (drag-and-drop)
- Integration with external research databases

### Phase 3:
- Collaborative editing
- Real-time validation against test charts
- Automated code generation from rules
- Cross-reference conflict detection
- Multi-language support for international experts

---

## Technical Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL
- SQLAlchemy ORM
- Background workers for processing

**Frontend:**
- Next.js 14
- TypeScript
- React Hook Form
- Monaco Editor (for code editing)
- Diff viewer for comparisons

**Integration:**
- Git integration for versioning
- CI/CD pipeline for testing
- Staging environment for validation

---

## Migration Strategy

### Step 1: Build Infrastructure (Week 1-2)
- Create database tables
- Implement API endpoints
- Build basic admin UI

### Step 2: Expert Onboarding (Week 3)
- Invite select experts
- Gather initial contributions
- Refine submission process

### Step 3: Review Process (Week 4)
- Establish review workflow
- Implement voting system
- Create approval criteria

### Step 4: Integration (Week 5-6)
- Begin implementing approved contributions
- Track impact on predictions
- Iterate based on feedback

### Step 5: Scale (Week 7+)
- Open to more experts
- Automate more of the workflow
- Expand knowledge categories

---

## Success Metrics

### Quantitative:
- Number of contributions (target: 50 in first 3 months)
- Approval rate (target: >60%)
- Implementation rate (target: >40% of approved)
- Prediction accuracy improvement (target: >10%)

### Qualitative:
- Expert satisfaction
- User feedback on predictions
- Code quality of contributions
- Community engagement

---

**Created:** 2025-11-10
**Status:** Ready for Implementation
**Next Action:** Create database schema and API endpoints
