# Numerology Frontend Implementation Plan

## Overview
This document outlines the frontend implementation for the Numerology feature (Phase 1 of multi-modal expansion).

## Status
- **Backend**: ✅ COMPLETE
- **API Client**: ✅ COMPLETE
- **Frontend UI**: ⏳ PENDING

## Task 6: Frontend Components (Remaining Work)

### Pages to Create

#### 1. Main Numerology Page (`/dashboard/numerology/page.tsx`)
**Location**: `frontend/app/dashboard/numerology/page.tsx`

**Features**:
- Profile selector (link to existing birth profiles)
- Input form for name + birth date
- System selector (Western, Vedic/Chaldean, Both)
- Quick calculation button
- Results display (tabs for Western + Vedic)

**Components**:
```typescript
// Main page with:
- NumerologyCalculator (form component)
- NumerologyResults (display component)
- SavedProfiles (list component)
```

#### 2. Numerology Profile Detail Page
**Location**: `frontend/app/dashboard/numerology/[id]/page.tsx`

**Features**:
- Full profile display
- Core numbers (Life Path, Expression, Soul Urge, etc.)
- Current cycles (Personal Year, Month, Day)
- Life periods (Pinnacles, Challenges)
- Name trials management
- Vedic numbers (Psychic, Destiny, Planet associations)

#### 3. Name Comparison Tool
**Location**: `frontend/app/dashboard/numerology/compare/page.tsx`

**Features**:
- Compare multiple name spellings
- Side-by-side number comparison
- Recommendations for best name energy
- Save preferred name as trial

### Reusable Components

#### `components/numerology/NumerologyCard.tsx`
Displays a single numerology number with:
- Number value
- Master number indicator
- Karmic debt indicator
- Description/meaning
- Favorable attributes

#### `components/numerology/CyclesTimeline.tsx`
Visual timeline showing:
- Current Personal Year/Month/Day
- Pinnacles (4 life periods)
- Challenges (4 life challenges)
- Universal Year

#### `components/numerology/PlanetAssociations.tsx`
(Vedic system) Shows:
- Psychic Number → Planet
- Destiny Number → Planet
- Favorable dates, colors, gems

#### `components/numerology/NumberBreakdown.tsx`
Shows calculation breakdown:
- Step-by-step reduction
- Master number preservation
- Karmic debt detection

### API Integration Pattern

```typescript
// Example from profiles page
import { apiClient } from '@/lib/api'

const calculateNumerology = async () => {
  try {
    const result = await apiClient.calculateNumerology({
      full_name: formData.name,
      birth_date: formData.birthDate,
      system: 'both',
    })
    setNumerologyData(result.data)
  } catch (error) {
    toast.error(error.message)
  }
}
```

### Styling Guidelines
- Use shadcn/ui components (Card, Badge, Tabs, etc.)
- Tailwind CSS for styling
- Follow existing dashboard page patterns
- Responsive design (mobile-first)
- Color coding for different number types:
  - Master Numbers: gold/yellow
  - Karmic Debt: red/orange
  - Regular: blue/purple

---

## Task 7: 50 Golden Test Cases

### Test Case Structure
Each test case should include:
1. Input data (name, birth date, system)
2. Expected core numbers
3. Expected special numbers (master, karmic debt)
4. Expected cycles for test date
5. Celebrity validation (if applicable)

### Categories (50 total)

**Western System (20 cases)**:
- Life Path 1-9 (9 cases)
- Master Numbers 11, 22, 33 (3 cases)
- Karmic Debt 13, 14, 16, 19 (4 cases)
- Edge cases (leap years, very old dates, etc.) (4 cases)

**Vedic System (20 cases)**:
- Psychic Number 1-9 (9 cases)
- Destiny Number 1-9 (9 cases)
- Compound numbers (2 cases)

**Celebrity Validation (10 cases)**:
- Oprah Winfrey: Life Path 11
- Albert Einstein: Life Path 7
- Marilyn Monroe: Life Path 7, Karmic Debt 16
- Steve Jobs: Life Path 1
- Mother Teresa: Life Path 6
- Bill Gates: Life Path 4
- Taylor Swift: Life Path 22
- Michael Jordan: Life Path 9
- (2 more to be selected)

### Test File Location
`backend/tests/test_numerology_golden_cases.py`

### Expected Structure
```python
class TestGoldenCases:
    """50 golden test cases for numerology calculations"""

    def test_celebrity_oprah_winfrey(self):
        """Oprah Winfrey: January 29, 1954 - Life Path 11"""
        result = WesternNumerology.calculate_life_path(date(1954, 1, 29))
        assert result['number'] == 11
        assert result['is_master'] == True

    # ... 49 more cases
```

---

## Task 8: Comprehensive Documentation

### Documentation Structure

#### 1. User Guide
**Location**: `backend/docs/numerology/USER_GUIDE.md`

**Contents**:
- Introduction to Numerology
- Western vs Vedic systems
- How to interpret each number
- Life cycles and what they mean
- Name trial functionality
- FAQ

#### 2. API Reference
**Location**: `backend/docs/numerology/API_REFERENCE.md`

**Contents**:
- All 11 endpoints with examples
- Request/response schemas
- Error codes and handling
- Rate limiting
- Authentication requirements

#### 3. Calculation Reference
**Location**: `backend/docs/numerology/CALCULATION_REFERENCE.md`

**Contents**:
- Pythagorean letter-to-number mapping
- Chaldean letter-to-number mapping
- Master number rules
- Karmic debt detection
- Cycle calculations
- Pinnacle/Challenge formulas

#### 4. Integration Guide
**Location**: `backend/docs/numerology/INTEGRATION_GUIDE.md`

**Contents**:
- How to integrate with birth profiles
- Frontend component usage
- API client examples
- Common patterns
- Best practices

---

## Task 9: Benchmark Performance and Optimize

### Performance Targets
- Single calculation: < 50ms
- Full profile (both systems): < 100ms
- Bulk comparison (5 names): < 200ms
- Database query: < 50ms

### Benchmark Script
**Location**: `backend/scripts/benchmark_numerology.py`

**Metrics to Measure**:
1. Calculation speed per system
2. Database insert/query performance
3. API endpoint response times
4. Memory usage
5. Concurrent request handling

### Optimization Checklist
- [ ] Add caching layer (Redis) for repeated calculations
- [ ] Optimize database indexes (already have 5 indexes)
- [ ] Add calculation result hashing for deduplication
- [ ] Profile memory usage with `memory_profiler`
- [ ] Load test with `locust` (100 concurrent users)
- [ ] Optimize JSONB queries
- [ ] Add database connection pooling

### Expected Script Output
```
========================================
NUMEROLOGY PERFORMANCE BENCHMARK
========================================

Single Calculations:
  Western Life Path:        12.3ms ✅
  Western Full Profile:     45.2ms ✅
  Vedic Calculations:       18.7ms ✅
  Combined (both systems):  63.5ms ✅

Database Operations:
  Insert Profile:           23.1ms ✅
  Query Profile:            15.4ms ✅
  List Profiles (10):       28.9ms ✅

API Endpoints:
  POST /calculate:          78.2ms ✅
  POST /profiles:           89.4ms ✅
  GET /profiles:            34.5ms ✅

Memory Usage:
  Single calculation:       2.3 MB
  100 calculations:         45.1 MB
  Profile in DB:            ~8 KB

Concurrency Test (50 users):
  Avg Response Time:        95.3ms ✅
  95th Percentile:          142.7ms ✅
  Throughput:               524 req/s ✅

========================================
RESULT: ALL TARGETS MET ✅
========================================
```

---

## Task 10: Update Architecture Documentation

### Files to Update

#### 1. Main Architecture Doc
**Location**: `backend/docs/ARCHITECTURE.md`

**Updates needed**:
- Add Numerology to Phase 1 section
- Update service layer diagram
- Add numerology data flow
- Update database schema diagram

#### 2. Database Schema Doc
**Location**: `backend/docs/database-schema.sql`

**Updates needed**:
- Add numerology_profiles table
- Add numerology_name_trials table
- Add privacy_preferences table
- Document extended kb_rules columns

#### 3. API Documentation
**Location**: `backend/docs/API.md`

**Updates needed**:
- Add /numerology endpoints section
- Update endpoint count (was 40+, now 51+)
- Add numerology examples

#### 4. README Updates
**Location**: `backend/README.md` and `frontend/README.md`

**Updates needed**:
- Add numerology to features list
- Update endpoint count
- Add numerology examples
- Update technology stack (no new dependencies)

#### 5. CLAUDE.md Updates
**Location**: `/CLAUDE.md`

**Updates needed**:
- Add numerology to project overview
- Update backend structure (add numerology service)
- Add numerology API examples
- Update development commands

---

## Implementation Priority

### Phase 6A: Critical Path
1. ✅ Backend calculation engine
2. ✅ Backend API endpoints
3. ✅ Backend tests (51 cases)
4. ✅ Database migration
5. ✅ API client methods
6. ⏳ Main numerology page (calculator + results)
7. ⏳ Profile detail page

### Phase 6B: Enhanced Features
8. Name comparison tool
9. Cycles timeline visualization
10. Name trials management
11. Integration with birth profiles

### Phase 6C: Documentation & Optimization
12. 50 golden test cases
13. Comprehensive documentation
14. Performance benchmarking
15. Architecture documentation updates

---

## Estimated Effort

| Task | Estimated Time | Complexity |
|------|---------------|------------|
| Main numerology page | 3-4 hours | Medium |
| Profile detail page | 2-3 hours | Medium |
| Name comparison tool | 2 hours | Low |
| Reusable components | 3-4 hours | Medium |
| 50 golden test cases | 2-3 hours | Low |
| Documentation (4 docs) | 4-5 hours | Low |
| Benchmark script | 2 hours | Low |
| Architecture updates | 1-2 hours | Low |
| **Total** | **19-26 hours** | **Medium** |

---

## Next Steps

To continue with frontend development, create:

1. **Directory**: `frontend/app/dashboard/numerology/`
2. **Main page**: `page.tsx` (calculator + results)
3. **Component directory**: `frontend/components/numerology/`
4. **Reusable components**: Start with `NumerologyCard.tsx`

The backend is production-ready and can be tested now via:
- Swagger UI: http://localhost:8000/docs
- Look for "numerology" tag (11 endpoints)

---

## Success Criteria

Task 6: ✅ Frontend pages load without errors, can calculate and display numerology
Task 7: ✅ All 50 test cases pass, covering edge cases and celebrity validations
Task 8: ✅ Documentation is comprehensive, clear, and includes examples
Task 9: ✅ All performance targets met (< 100ms for full profile)
Task 10: ✅ Architecture docs updated, reflect current state accurately

**Overall MVP Goal**: Users can calculate, save, and view numerology profiles with both Western and Vedic systems, with performance under 100ms per calculation.
