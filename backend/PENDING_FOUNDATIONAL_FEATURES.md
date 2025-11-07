# Pending Foundational Features - Master List

**Last Updated:** 2025-11-07
**Priority:** These should be completed BEFORE Magical 12 features

---

## 🎯 The Big Picture

The **Magical 12** are user-facing "magic" features that sit on top of a solid computational foundation. Before we can deliver that magic, we need to complete the core astrological calculation engine.

### Architecture Layers

```
┌──────────────────────────────────────────────────────────┐
│   Layer 3: MAGICAL 12 (User Experience)                 │
│   • Life Snapshot, Life Threads, Decision Copilot, etc. │
└──────────────────────────────────────────────────────────┘
                         ↑ depends on
┌──────────────────────────────────────────────────────────┐
│   Layer 2: PRESENTATION & DISPLAY (Frontend)             │
│   • Chart pages, Yoga tabs, Dasha timelines, etc.       │
└──────────────────────────────────────────────────────────┘
                         ↑ depends on
┌──────────────────────────────────────────────────────────┐
│   Layer 1: COMPUTATION ENGINE (Backend) ← WE ARE HERE    │
│   • Calculations, Yogas, Doshas, Dashas, Transits       │
└──────────────────────────────────────────────────────────┘
```

---

## ✅ What's Already Complete (Strong Foundation!)

### 1. Core Infrastructure ✅
- FastAPI backend with async PostgreSQL
- Next.js 14 frontend with TypeScript
- Supabase Auth with JWT
- Azure OpenAI integration (GPT-4)
- Vector-based knowledge base with pgvector

### 2. Basic Charts ✅
- **D1 (Rashi)** - Birth chart
- **D9 (Navamsa)** - Marriage/dharma chart
- Swiss Ephemeris accuracy
- Lahiri ayanamsa (sidereal)
- Nakshatra, pada, dignity, retrograde, combustion

### 3. Numerology (Complete) ✅
- Western (Pythagorean): Life Path, Expression, Soul Urge, etc.
- Vedic (Chaldean): Psychic, Destiny, Name numbers
- Life cycles: Personal Year/Month/Day, Pinnacles, Challenges
- Name trial and comparison tools
- 50 golden test cases, 56% pass rate
- Performance: 0.01-0.27ms

### 4. Yogas (25+ Implemented) ✅
- Pancha Mahapurusha Yogas (5 yogas)
- Wealth Yogas (8 yogas)
- Fame & Authority Yogas (5 yogas)
- Learning & Intelligence Yogas (4 yogas)
- Skills & Leadership Yogas (2 yogas)
- Transformation Yogas (2 yogas)
- Health & Balance Yogas (2 yogas)
- **Total:** 28 yogas with strength classification

### 5. Advanced Systems (Complete) ✅
- **Jaimini System:**
  - Chara Karakas (7 significators)
  - Karakamsha (Atmakaraka in D9)
  - Arudha Padas (12 illusion points)
  - Rashi Drishti (sign aspects)
  - Chara Dasha (sign periods)

- **Lal Kitab System:**
  - 7 types of planetary debts
  - Blind planets (Andhe Graha)
  - Exalted enemies
  - Pakka Ghar (permanent houses)
  - 150+ practical remedies

- **Ashtakavarga System:**
  - Bhinna Ashtakavarga (7 planets × 12 houses)
  - Sarva Ashtakavarga (combined bindus)
  - House strength classification
  - Graha Pinda & Rashi Pinda
  - Transit strength analysis

### 6. Knowledge Base (1,500+ Rules) ✅
- BPHS: 896+ rules
- Surya Siddhanta: 108 rules
- Chaldean: 300 rules
- Pythagoras: 200 rules
- Hybrid RAG retrieval (vector + symbolic)

### 7. AI Readings (Enhanced) ✅
- Comprehensive 2,500-4,000 word reports
- 23 sections (from 500-700 words before)
- Month-by-month timelines (12 months)
- Quarterly forecasts (3 years)
- Yearly predictions (7 years)
- 30,000 token budget

### 8. Admin Dashboard ✅
- User management
- Document upload and processing
- Knowledge base viewer
- Cascade deletion
- Profile management

---

## ⏳ What's PENDING - Must Complete Before Magical 12

### **PHASE 2: Enhanced Chart Calculations** 🔴 CRITICAL
**Duration:** 2-3 weeks
**Priority:** Must complete FIRST

#### 2.1 Divisional Charts (High Priority)
Currently: Only D1 and D9 exist

**Need to Implement:**
- [ ] **D2 (Hora)** - Wealth patterns
- [ ] **D4 (Chaturthamsa)** - Property/fortunes
- [ ] **D6 (Shashthamsa)** - Diseases/enemies
- [ ] **D7 (Saptamsa)** - Children/offspring
- [ ] **D10 (Dasamsa)** - Career trajectory (IMPORTANT!)
- [ ] **D24 (Chaturvimsamsa)** - Education/learning

**Why Important:** Magical 12 features need these for:
- Life Threads Timeline (career, wealth, health threads)
- Decision Copilot (best timing needs D10 for career)
- Life Snapshot (themes need multiple divisional charts)

---

#### 2.2 Doshas (Missing - CRITICAL)
Currently: ZERO doshas implemented

**Need to Implement:**
- [ ] **Manglik Dosha (Kuja Dosha)** - Mars afflictions
  - Presence detection
  - Severity calculation
  - Cancellation rules (10+ factors)
  - Remedies

- [ ] **Kaal Sarpa Dosha** - Rahu-Ketu axis
  - 12 types (Anant, Kulik, Vasuki, Shankhpal, Padma, etc.)
  - Partial vs Complete
  - Effects by type
  - Remedies

- [ ] **Pitra Dosha** - Ancestor karma
  - Detection from 9th house, Sun, Saturn
  - Manifestations
  - Remedies (Tarpan, Shraddha)

- [ ] **Gandanta** - Critical junctions
  - 3 points where fire meets water
  - Birth in Gandanta effects
  - Remedies

- [ ] **Kemadruma Yoga** - Moon isolation
  - Detection (no planets flanking Moon)
  - Severity
  - Cancellation factors

**Why Important:** Magical 12 features need these for:
- Life Snapshot (risks section heavily depends on dosha detection)
- Remedy Planner (prescriptions based on doshas)
- Reality Check (feedback loop on dosha predictions)

---

#### 2.3 Vimshottari Dasha System (Missing - CRITICAL)
Currently: NO dasha calculations

**Need to Implement:**
- [ ] **Dasha Balance at Birth** - Calculate from Moon nakshatra
- [ ] **Mahadasha Periods** - 9 periods × 7-20 years = 120-year cycle
  - Start/end dates for each
  - Lords: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury

- [ ] **Antardasha Periods** - Sub-periods within each Mahadasha
  - 9 sub-periods per Mahadasha
  - Duration calculations

- [ ] **Pratyantardasha** - Sub-sub-periods
  - Third-level granularity

- [ ] **Sookshma Dasha** - Micro-periods (optional)
  - Fourth-level granularity

- [ ] **Current Dasha Pointer** - Where user is NOW
  - Current Mahadasha
  - Current Antardasha
  - Current Pratyantardasha
  - Remaining time in each

- [ ] **Upcoming Dasha Changes** - Next 2 years
  - Major transitions
  - Important period changes

**Why Important:** Magical 12 features HEAVILY depend on this:
- **Life Threads Timeline** - Cannot work without dasha periods!
- **Transit Pulse** - Combines transits with dashas
- **Life Snapshot** - "Next best opportunities" needs dashas
- **Decision Copilot** - Timing depends on dasha + transit combo
- **AI Readings** - Current readings mention dashas but don't calculate them!

---

#### 2.4 Current Transits (Gochar) (Missing - CRITICAL)
Currently: Only basic transit service exists

**Need to Implement:**
- [ ] **Saturn Transit** - Current position
  - Sign
  - House from Lagna
  - House from Moon
  - Effects and timing
  - Retrograde periods

- [ ] **Jupiter Transit** - Current position
  - Sign
  - House from Lagna
  - House from Moon
  - Effects and timing
  - Retrograde periods

- [ ] **Rahu-Ketu Axis** - Current nodes
  - Rahu sign and house
  - Ketu sign and house (opposite)
  - Effects

- [ ] **Upcoming Major Transits** - Next 12 months
  - Saturn sign changes
  - Jupiter sign changes
  - Rahu-Ketu axis changes
  - Eclipse windows

- [ ] **Double Transit** - Jupiter + Saturn
  - When both aspect same house
  - Major breakthrough windows

**Why Important:** Magical 12 features need this:
- **Transit Pulse Cards** - THE CORE FEATURE!
- **Life Snapshot** - Opportunities based on transits
- **Decision Copilot** - Best timing = transit + dasha combo
- **Life Threads** - Color-coded by transit influences

---

#### 2.5 Sade Sati Analysis (Missing - HIGH PRIORITY)
Currently: Not implemented

**Need to Implement:**
- [ ] **Current Sade Sati Status** - Is user in it?
- [ ] **Phase Identification** - Which of 3 phases
  - 1st Phase: Saturn in 12th from Moon (2.5 years)
  - 2nd Phase: Saturn conjunct Moon (2.5 years) - HARDEST
  - 3rd Phase: Saturn in 2nd from Moon (2.5 years)

- [ ] **Start and End Dates** - For each phase
- [ ] **Next Sade Sati Window** - If not currently in it
- [ ] **Ashtama Shani** - Saturn in 8th from Moon
  - Duration
  - Effects
  - Remedies

**Why Important:**
- **Life Snapshot** - Major life phase indicator
- **Transit Pulse** - High-priority alert
- **Remedy Planner** - Saturn remedies during Sade Sati

---

#### 2.6 More Yogas (Expand to 50+)
Currently: 28 yogas implemented

**Need to Add:**
- [ ] **Parivartana Yogas** - Mutual exchange
  - Maha Parivartana (1st/5th/9th lords)
  - Khala Parivartana (6th/8th/12th lords)
  - Dainya Parivartana (dusthana lords)

- [ ] **Nabhassa Yogas** - Rare patterns
  - Gola Yoga
  - Yuga Yoga
  - Shula Yoga
  - etc. (20+ yogas)

- [ ] **Chandra Yogas** - Moon patterns
  - Already have: Sunapha, Anapha, Durudhura
  - Need: Adhama, Kemadruma cancellations

- [ ] **Surya Yogas** - Sun patterns
  - Already have: Budhaditya, Vesi, Ubhayachari
  - Need: More sun-specific yogas

---

### **PHASE 3: Database Schema Updates** 🔴 CRITICAL
**Duration:** 3-5 days
**Priority:** After Phase 2 calculations ready

**Need to Implement:**
- [ ] Add JSONB columns to `charts` table:
  ```sql
  divisional_charts JSONB
  yogas JSONB  -- Already exists, but needs expansion
  doshas JSONB  -- NEW
  dasha_periods JSONB  -- NEW
  current_dasha JSONB  -- NEW
  transits JSONB  -- NEW
  sade_sati JSONB  -- NEW
  computed_at TIMESTAMPTZ
  computation_version TEXT
  ```

- [ ] Create migration script
- [ ] Update chart creation endpoint
- [ ] Ensure backward compatibility
- [ ] Create indexes for performance

**Why Important:**
- Magical 12 features read from database
- No database = no features work!

---

### **PHASE 4: Frontend Chart Display** 🔴 HIGH PRIORITY
**Duration:** 1-2 weeks
**Priority:** After Phase 3 schema ready

**Need to Implement:**
Enhanced chart page with 7 tabs:

- [ ] **Tab 1: Birth Chart (D1)** - EXISTS, needs minor enhancements
- [ ] **Tab 2: Divisional Charts** - NEW
  - Dropdown selector (D2, D4, D6, D7, D9, D10, D24)
  - Visual chart display
  - Planetary positions
  - Interpretation guide

- [ ] **Tab 3: Yogas** - NEW
  - Beneficial yogas with checkmarks
  - Strength percentages
  - Challenging yogas with warnings
  - Remedies

- [ ] **Tab 4: Doshas** - NEW
  - Manglik Dosha details
  - Kaal Sarpa Dosha type
  - Pitra Dosha
  - Gandanta
  - Remedies for each

- [ ] **Tab 5: Dasha Periods** - NEW (CRITICAL!)
  - Current dasha display (Maha/Antar/Pratyantar)
  - Timeline visualization (all Mahadashas)
  - Color-coded by benefic/malefic
  - Click to expand Antardashas
  - Upcoming changes (next 2 years)

- [ ] **Tab 6: Transits & Sade Sati** - NEW (CRITICAL!)
  - Current transits (Saturn, Jupiter, Rahu-Ketu)
  - Sade Sati status and phase
  - Timeline with start/end dates
  - Ashtama Shani status
  - Upcoming major transits (12 months)

- [ ] **Tab 7: Strengths (Shadbala)** - NEW (Lower priority)
  - Bar chart of planetary strengths
  - Ashtakavarga scores
  - Weakest/strongest planets

**Why Important:**
- Users need to SEE their chart data before Magical 12 can reference it
- Dasha timeline visualization = foundation for Life Threads Timeline
- Transit tab = foundation for Transit Pulse Cards

---

### **PHASE 5: AI Reading Refactor** 🟡 MEDIUM PRIORITY
**Duration:** 3-5 days
**Priority:** After Phase 2-4 complete

**Need to Implement:**
- [ ] Remove ALL computation from `ai_orchestrator.py`
- [ ] Fetch pre-computed data from database
- [ ] Update AI prompts to reference pre-computed data
- [ ] Remove redundant context preparation
- [ ] Verify reading quality maintained

**Why Important:**
- Currently AI readings try to compute some data (inefficient!)
- Should read from database instead
- Will make readings 3-4x faster
- Reduce token usage 20-30%

---

### **PHASE 6: Advanced Calculations** 🟢 LOWER PRIORITY
**Duration:** 2-3 weeks
**Priority:** Future / As Needed

**Optional Features:**
- [ ] Remaining divisional charts (D3, D5, D8, D11, D12, D16, D20, D27, D30, D40, D45, D60)
- [ ] Shadbala (six-fold strength):
  - Sthana Bala, Dig Bala, Kala Bala, Chesta Bala, Naisargika Bala, Drik Bala
- [ ] Extended Ashtakavarga (already mostly done)
- [ ] Vimsopaka Bala
- [ ] Avasthas (planetary states)

---

### **PHASE 7: Compatibility Module** 🟢 LOWER PRIORITY
**Duration:** 1-2 weeks
**Priority:** Future

**Need to Implement:**
- [ ] Koot matching (8 factors, 36 points)
- [ ] Manglik matching
- [ ] Dashas compatibility
- [ ] Divorce/separation indicators
- [ ] Overall compatibility score

---

## 📊 Implementation Priority Matrix

### Must Complete BEFORE Magical 12 (Phases 2-4)

| Feature | Phase | Priority | Duration | Blocks Magical 12? |
|---------|-------|----------|----------|-------------------|
| **Divisional Charts (D2, D4, D6, D7, D10, D24)** | 2 | 🔴 CRITICAL | 1 week | Yes - Life Threads |
| **Doshas (Manglik, Kaal Sarpa, Pitra, Gandanta)** | 2 | 🔴 CRITICAL | 1 week | Yes - Life Snapshot risks |
| **Vimshottari Dasha (Full System)** | 2 | 🔴 CRITICAL | 1 week | Yes - ALL features need this! |
| **Current Transits (Saturn, Jupiter, Rahu-Ketu)** | 2 | 🔴 CRITICAL | 3 days | Yes - Transit Pulse |
| **Sade Sati Analysis** | 2 | 🔴 HIGH | 2 days | Yes - Life Snapshot |
| **Database Schema Updates** | 3 | 🔴 CRITICAL | 3-5 days | Yes - Storage layer |
| **Frontend Chart Display (7 tabs)** | 4 | 🔴 HIGH | 1-2 weeks | Somewhat - UX |

**Total Critical Path:** ~4-5 weeks

---

### Can Do AFTER Initial Magical 12 (Phases 5-7)

| Feature | Phase | Priority | Duration |
|---------|-------|----------|----------|
| AI Reading Refactor | 5 | 🟡 MEDIUM | 3-5 days |
| Advanced Calculations | 6 | 🟢 LOW | 2-3 weeks |
| Compatibility Module | 7 | 🟢 LOW | 1-2 weeks |
| More Yogas (50+ total) | 2 | 🟡 MEDIUM | 1 week |

---

## 🎯 Recommended Implementation Order

### **Sprint 1-2: Core Calculations (Weeks 1-2)**
1. ✅ Life Snapshot (DONE - Magical 12 #1)
2. **Vimshottari Dasha System** - Most critical, blocks everything
3. **Current Transits** - Needed for Transit Pulse
4. **Sade Sati** - High user interest

### **Sprint 3: Doshas & Divisional Charts (Week 3)**
4. **Doshas** - Manglik, Kaal Sarpa, Pitra, Gandanta
5. **Divisional Charts** - D2, D4, D6, D7, D10, D24

### **Sprint 4: Database & Frontend (Week 4)**
6. **Database Schema Updates** - Migration script
7. **Frontend Chart Display** - Start with Dasha and Transit tabs

### **Sprint 5-6: Frontend Complete (Weeks 5-6)**
8. **Frontend Chart Display** - Complete all 7 tabs
9. **Testing & Refinement**

### **THEN: Resume Magical 12 Implementation**
After Sprint 6 complete, we can confidently build:
- Life Threads Timeline (needs dashas + transits)
- Transit Pulse Cards (needs transits + dashas)
- Decision Copilot (needs transits + dashas + D10)
- Evidence Mode (needs complete chart data)
- etc.

---

## 💡 Key Insight

**The Magical 12 are like a house:**
- **Foundation:** Phase 2-3 (calculations + storage)
- **Structure:** Phase 4 (frontend display)
- **Interior Design:** Magical 12 features (user experience)

You can't build a beautiful interior without a solid foundation!

---

## ✅ Conclusion

**You were 100% correct!** We should complete Phases 2-4 (the foundational calculation and display layer) BEFORE building more Magical 12 features.

**Current Status:**
- ✅ Phase 1: Admin Foundation - COMPLETE
- ⏳ Phase 2: Enhanced Chart Calculations - NOT STARTED (4-5 weeks)
- ⏳ Phase 3: Database Schema - NOT STARTED (3-5 days)
- ⏳ Phase 4: Frontend Display - NOT STARTED (1-2 weeks)

**Recommendation:**
Let's implement **Phase 2 (Enhanced Chart Calculations)** first, focusing on:
1. Vimshottari Dasha System (CRITICAL!)
2. Current Transits
3. Doshas
4. Key Divisional Charts (D2, D4, D6, D7, D10, D24)

**Estimated Timeline:** 4-5 weeks for complete foundational layer

Then we can build the Magical 12 on top of this solid foundation!

---

**Created:** 2025-11-07
**Priority:** CRITICAL - Complete before Magical 12
**Status:** Pending Implementation
