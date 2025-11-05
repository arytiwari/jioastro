# Phase 1: Numerology Integration - Implementation Plan

**Status**: 🚧 In Progress
**Start Date**: 2025-11-05
**Target Completion**: 2025-11-26 (3 weeks)
**Owner**: Development Team

---

## Table of Contents

1. [Overview](#overview)
2. [Scope](#scope)
3. [Architecture](#architecture)
4. [Implementation Tasks](#implementation-tasks)
5. [Test Strategy](#test-strategy)
6. [Documentation Requirements](#documentation-requirements)
7. [Quality Metrics](#quality-metrics)
8. [Timeline](#timeline)
9. [Dependencies](#dependencies)
10. [Risks & Mitigation](#risks--mitigation)

---

## Overview

Phase 1 adds **Numerology** as the second pillar of JioAstro's multi-modal insights platform, complementing the existing Vedic Astrology MVP. This phase implements both **Western/Pythagorean** and **Vedic/Chaldean** numerology systems with full calculation engines, API endpoints, frontend UI, and knowledge base integration.

### Goals

1. ✅ **Complete Numerology Engine**: Both Western and Vedic systems with all calculations
2. ✅ **API Integration**: RESTful endpoints following existing patterns
3. ✅ **Frontend UI**: Dashboard integration with dedicated numerology tab
4. ✅ **Knowledge Base**: 100+ numerology rules integrated with existing KB
5. ✅ **Testing**: 50 golden test cases with 100% pass rate
6. ✅ **Documentation**: Complete technical and user-facing documentation
7. ✅ **Performance**: Sub-500ms calculation time, efficient caching

---

## Scope

### In Scope

**Backend:**
- `numerology_service.py`: Core calculation engine (500 lines)
- `numerology_bridge.py`: MVP bridge pattern for caching (150 lines)
- API endpoints: `/api/v1/numerology/*` (200 lines)
- Pydantic schemas for request/response validation (100 lines)
- Database models (SQLAlchemy ORM) (100 lines)
- 50 golden test cases with pytest (300 lines)

**Frontend:**
- Numerology dashboard tab
- Profile component (Western + Vedic numbers)
- Cycles component (Personal Year, Pinnacles, Challenges)
- Name calculator tool
- Integration with existing auth/API client

**Knowledge Base:**
- 100+ numerology rules (Western + Vedic)
- Rule schema extensions
- Symbolic key generation for numerology
- Integration with existing RAG system

**Documentation:**
- Technical documentation (this file)
- API documentation (OpenAPI/Swagger)
- User guide for numerology features
- Update architecture documentation

### Out of Scope (Future Phases)

- Palmistry integration (Phase 2-3)
- Multi-modal fusion orchestrator enhancements (Phase 5)
- Voice/audio numerology reading (Phase 6)
- Name correction recommendations with ML (Phase 7)
- Compatibility analysis between profiles (Phase 8)

---

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  Frontend (Next.js)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Dashboard   │  │  Numerology  │  │     Name     │ │
│  │     Tab      │  │   Profile    │  │  Calculator  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │ HTTPS/REST
                             ▼
┌─────────────────────────────────────────────────────────┐
│               API Layer (FastAPI)                       │
│  /api/v1/numerology/calculate                           │
│  /api/v1/numerology/profiles                            │
│  /api/v1/numerology/cycles                              │
│  /api/v1/numerology/name-trials                         │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌────────────┐ ┌──────────────┐
│ Numerology   │ │ Numerology │ │   Database   │
│  Service     │ │   Bridge   │ │   (Supabase) │
│              │ │  (Cache)   │ │              │
│ • Western    │ │            │ │ • profiles   │
│ • Vedic      │ │ • Redis    │ │ • name_trials│
│ • Cycles     │ │ • Hash     │ │ • privacy    │
└──────────────┘ └────────────┘ └──────────────┘
```

### Data Flow

```
User Request (Name + DOB)
         ↓
API Endpoint (/numerology/calculate)
         ↓
Validation (Pydantic Schema)
         ↓
Numerology Bridge (check cache by hash)
         ↓ (cache miss)
Numerology Service
  ├─→ Western Engine
  │    ├─ Life Path
  │    ├─ Expression
  │    ├─ Soul Urge
  │    ├─ Personality
  │    ├─ Maturity
  │    ├─ Birth Day
  │    ├─ Master Numbers (11/22/33)
  │    ├─ Karmic Debt (13/14/16/19)
  │    └─ Cycles (Personal Year, Pinnacles, Challenges)
  │
  └─→ Vedic/Chaldean Engine
       ├─ Psychic Number (DOB day)
       ├─ Destiny Number (name value)
       ├─ Name Value
       ├─ Planet Mapping
       ├─ Favorable/Unfavorable Numbers
       └─ Name Corrections
         ↓
Combined Result (Western + Vedic)
         ↓
Save to Database (numerology_profiles)
         ↓
Cache Result (Redis)
         ↓
Response to Frontend
```

---

## Implementation Tasks

### Task 1: Database Schema ✅ COMPLETE

**File**: `docs/database-migrations/001_add_numerology_schema.sql`

**Deliverables**:
- [x] `numerology_profiles` table
- [x] `numerology_name_trials` table
- [x] `privacy_preferences` table
- [x] Extended `kb_rules` with `system`, `modifiers`, `context`
- [x] Sample numerology rules (5 examples)
- [x] Helper functions (calculate_life_path, update_updated_at)
- [x] RLS policies for all new tables
- [x] Indexes for performance
- [x] View for easy querying (user_numerology_summary)

**Testing**:
- [ ] Run migration on dev database
- [ ] Verify all tables created
- [ ] Test RLS policies
- [ ] Verify sample data inserted

---

### Task 2: Numerology Service - Western System

**File**: `backend/app/services/numerology_service.py` (500 lines total, this task: ~300 lines)

**Components**:

#### 2.1 Western Number Calculations

```python
class WesternNumerology:
    """Western/Pythagorean numerology calculations"""

    @staticmethod
    def calculate_life_path(birth_date: date) -> Dict[str, Any]:
        """
        Calculate Life Path number from birth date
        - Reduce month, day, year separately
        - Preserve master numbers (11, 22, 33)
        - Return: {number, is_master, breakdown}
        """
        pass

    @staticmethod
    def calculate_expression(full_name: str) -> Dict[str, Any]:
        """
        Calculate Expression/Destiny number from full name
        - Convert letters to numbers (A=1, B=2, ..., I=9, J=1, ...)
        - Sum and reduce (preserve master numbers)
        - Return: {number, is_master, letter_values, breakdown}
        """
        pass

    @staticmethod
    def calculate_soul_urge(full_name: str) -> Dict[str, Any]:
        """
        Calculate Soul Urge/Heart's Desire from vowels only
        """
        pass

    @staticmethod
    def calculate_personality(full_name: str) -> Dict[str, Any]:
        """
        Calculate Personality number from consonants only
        """
        pass

    @staticmethod
    def calculate_maturity(life_path: int, expression: int) -> int:
        """
        Maturity Number = Life Path + Expression (reduced)
        """
        pass

    @staticmethod
    def calculate_birth_day(birth_date: date) -> int:
        """
        Birth Day Number = day of month (reduced if > 31)
        """
        pass

    @staticmethod
    def detect_karmic_debt(life_path: int, birth_day: int, expression: int) -> List[int]:
        """
        Detect Karmic Debt numbers: 13, 14, 16, 19
        Check if any calculation had these before reduction
        """
        pass

    @staticmethod
    def detect_master_numbers(calculations: Dict) -> List[int]:
        """
        Detect Master Numbers: 11, 22, 33
        Check all calculations for these
        """
        pass
```

#### 2.2 Western Cycle Calculations

```python
    @staticmethod
    def calculate_personal_year(birth_date: date, current_date: date = None) -> int:
        """
        Personal Year = (birth month + birth day + current year) reduced
        """
        pass

    @staticmethod
    def calculate_personal_month(personal_year: int, current_month: int) -> int:
        """
        Personal Month = Personal Year + Current Month (reduced)
        """
        pass

    @staticmethod
    def calculate_personal_day(personal_month: int, current_day: int) -> int:
        """
        Personal Day = Personal Month + Current Day (reduced)
        """
        pass

    @staticmethod
    def calculate_pinnacles(birth_date: date) -> List[Dict[str, Any]]:
        """
        Calculate 4 Pinnacle periods with numbers and age ranges
        Pinnacle 1: birth month + birth day
        Pinnacle 2: birth day + birth year
        Pinnacle 3: Pinnacle 1 + Pinnacle 2
        Pinnacle 4: birth month + birth year
        Age ranges based on Life Path
        """
        pass

    @staticmethod
    def calculate_challenges(birth_date: date) -> List[Dict[str, Any]]:
        """
        Calculate 4 Challenge periods (subtractive)
        Challenge 1: |month - day|
        Challenge 2: |day - year|
        Challenge 3: |Challenge 1 - Challenge 2|
        Challenge 4: |month - year|
        """
        pass
```

**Testing**:
- [ ] Unit tests for each calculation method
- [ ] Test master number preservation
- [ ] Test karmic debt detection
- [ ] Test cycle calculations
- [ ] Golden test cases (20 cases)

---

### Task 3: Numerology Service - Vedic/Chaldean System

**File**: `backend/app/services/numerology_service.py` (continuation, ~200 lines)

**Components**:

```python
class VedicNumerology:
    """Vedic/Chaldean numerology calculations"""

    # Chaldean number mapping (different from Pythagorean)
    CHALDEAN_MAP = {
        'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
        'B': 2, 'K': 2, 'R': 2,
        'C': 3, 'G': 3, 'L': 3, 'S': 3,
        'D': 4, 'M': 4, 'T': 4,
        'E': 5, 'H': 5, 'N': 5, 'X': 5,
        'U': 6, 'V': 6, 'W': 6,
        'O': 7, 'Z': 7,
        'F': 8, 'P': 8
        # Note: No 9 in Chaldean system
    }

    # Planet associations
    PLANET_MAP = {
        1: "Sun", 2: "Moon", 3: "Jupiter",
        4: "Rahu", 5: "Mercury", 6: "Venus",
        7: "Ketu", 8: "Saturn", 9: "Mars"
    }

    @staticmethod
    def calculate_psychic_number(birth_date: date) -> Dict[str, Any]:
        """
        Psychic Number = day of birth (reduced if > 31)
        Represents inner self, personality
        Return: {number, planet, meaning}
        """
        pass

    @staticmethod
    def calculate_destiny_number(full_name: str) -> Dict[str, Any]:
        """
        Destiny Number = full name value (Chaldean system)
        Represents life path, karmic direction
        """
        pass

    @staticmethod
    def calculate_name_value(name: str) -> int:
        """
        Calculate numeric value of name using Chaldean system
        """
        pass

    @staticmethod
    def get_favorable_numbers(psychic: int, destiny: int) -> List[int]:
        """
        Determine favorable numbers based on psychic + destiny
        Consider planet friendships
        """
        pass

    @staticmethod
    def get_unfavorable_numbers(psychic: int, destiny: int) -> List[int]:
        """
        Determine unfavorable numbers based on planet enmities
        """
        pass

    @staticmethod
    def suggest_name_corrections(current_name: str, birth_date: date) -> List[Dict]:
        """
        Suggest name spelling changes for better numerology
        Check if current destiny number harmonizes with psychic
        Return list of suggestions with impact scores
        """
        pass
```

**Testing**:
- [ ] Unit tests for Vedic calculations
- [ ] Test Chaldean number mapping
- [ ] Test planet associations
- [ ] Test name correction suggestions
- [ ] Golden test cases (15 cases)

---

### Task 4: Numerology Bridge (Caching Layer)

**File**: `backend/app/services/numerology_bridge.py` (~150 lines)

```python
"""
Numerology Bridge - Caching & Hash Management
Follows the same pattern as mvp_bridge.py for astrology
"""

from typing import Dict, Any, Optional
from datetime import date
import hashlib
import json
from app.services.numerology_service import NumerologyService
from app.core.config import settings
import redis

class NumerologyBridge:
    """Bridge for numerology calculations with caching"""

    def __init__(self):
        self.service = NumerologyService()
        if settings.REDIS_URL:
            self.redis_client = redis.from_url(settings.REDIS_URL)
        else:
            self.redis_client = None

    def calculate_hash(self, full_name: str, birth_date: date, system: str) -> str:
        """
        Generate unique hash for this calculation
        Hash = SHA256(full_name + birth_date + system)
        """
        data = f"{full_name.lower()}{birth_date.isoformat()}{system}"
        return hashlib.sha256(data.encode()).hexdigest()

    async def get_profile(
        self,
        full_name: str,
        birth_date: date,
        common_name: Optional[str] = None,
        system: str = "both"
    ) -> Dict[str, Any]:
        """
        Get numerology profile with caching
        1. Check Redis cache
        2. Check database cache
        3. Calculate if not cached
        4. Save to cache and database
        """
        # Calculate hash
        calc_hash = self.calculate_hash(full_name, birth_date, system)

        # Try Redis cache first
        if self.redis_client:
            cached = self.redis_client.get(f"numerology:{calc_hash}")
            if cached:
                return json.loads(cached)

        # Try database cache
        # (check numerology_profiles table)

        # Calculate fresh
        result = await self.service.calculate_full_profile(
            full_name=full_name,
            birth_date=birth_date,
            common_name=common_name,
            system=system
        )

        # Cache in Redis (24 hour TTL)
        if self.redis_client:
            self.redis_client.setex(
                f"numerology:{calc_hash}",
                86400,  # 24 hours
                json.dumps(result)
            )

        # Save to database
        # (save to numerology_profiles table)

        return result

# Singleton instance
numerology_bridge = NumerologyBridge()
```

**Testing**:
- [ ] Test hash generation consistency
- [ ] Test Redis caching (hit/miss)
- [ ] Test database caching
- [ ] Test cache invalidation
- [ ] Performance benchmarks

---

### Task 5: API Endpoints

**File**: `backend/app/api/v1/endpoints/numerology.py` (~200 lines)

```python
"""
Numerology API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import date

from app.api.v1.dependencies import get_current_user
from app.schemas.numerology import (
    NumerologyCalculateRequest,
    NumerologyCalculateResponse,
    NumerologyProfileResponse,
    NameTrialRequest,
    NameTrialResponse
)
from app.services.numerology_bridge import numerology_bridge

router = APIRouter(prefix="/numerology", tags=["numerology"])

@router.post("/calculate", response_model=NumerologyCalculateResponse)
async def calculate_numerology(
    request: NumerologyCalculateRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate numerology profile for given name and birth date
    Supports both Western and Vedic systems
    """
    try:
        result = await numerology_bridge.get_profile(
            full_name=request.full_name,
            birth_date=request.birth_date,
            common_name=request.common_name,
            system=request.system
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profiles", response_model=List[NumerologyProfileResponse])
async def list_numerology_profiles(
    current_user = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """
    List all numerology profiles for current user
    """
    pass

@router.get("/profiles/{profile_id}", response_model=NumerologyProfileResponse)
async def get_numerology_profile(
    profile_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get specific numerology profile by ID
    """
    pass

@router.post("/name-trials", response_model=NameTrialResponse)
async def create_name_trial(
    request: NameTrialRequest,
    current_user = Depends(get_current_user)
):
    """
    Try different name spellings and see numerology impact
    """
    pass

@router.get("/cycles/current")
async def get_current_cycles(
    profile_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get current Personal Year, Month, Day for a profile
    """
    pass
```

**Testing**:
- [ ] Integration tests for all endpoints
- [ ] Test authentication
- [ ] Test rate limiting
- [ ] Test error handling
- [ ] OpenAPI schema validation

---

### Task 6: Pydantic Schemas

**File**: `backend/app/schemas/numerology.py` (~100 lines)

```python
"""
Pydantic schemas for numerology API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date

class NumerologyCalculateRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    birth_date: date
    common_name: Optional[str] = Field(None, max_length=255)
    system: str = Field("both", pattern="^(western|vedic|chaldean|both)$")

    @validator('full_name', 'common_name')
    def validate_name(cls, v):
        if v and not v.replace(' ', '').isalpha():
            raise ValueError('Name must contain only letters and spaces')
        return v

class WesternNumerologyData(BaseModel):
    life_path: int
    expression: int
    soul_urge: int
    personality: int
    maturity: int
    birth_day: int
    karmic_debt: List[int]
    master_numbers: List[int]
    personal_year: int
    personal_month: int
    personal_day: int
    pinnacles: List[Dict[str, Any]]
    challenges: List[Dict[str, Any]]
    calculation_breakdown: Dict[str, Any]

class VedicNumerologyData(BaseModel):
    psychic_number: int
    destiny_number: int
    name_value: int
    planet_map: Dict[str, str]
    favorable_numbers: List[int]
    unfavorable_numbers: List[int]
    corrections: List[Dict[str, Any]]
    calculation_breakdown: Dict[str, Any]

class NumerologyCalculateResponse(BaseModel):
    full_name: str
    birth_date: date
    system: str
    western_data: Optional[WesternNumerologyData]
    vedic_data: Optional[VedicNumerologyData]
    calculation_hash: str
    calculated_at: str
```

**Testing**:
- [ ] Schema validation tests
- [ ] Test field constraints
- [ ] Test validators
- [ ] Test serialization/deserialization

---

### Task 7: Database Models (SQLAlchemy)

**File**: `backend/app/models/numerology.py` (~100 lines)

```python
"""
SQLAlchemy ORM models for numerology
"""

from sqlalchemy import Column, String, Date, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from datetime import datetime

class NumerologyProfile(Base):
    __tablename__ = "numerology_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True)

    full_name = Column(String(255), nullable=False)
    common_name = Column(String(255))
    name_at_birth = Column(String(255))

    system = Column(String(50), nullable=False, default="both")

    western_data = Column(JSONB)
    vedic_data = Column(JSONB)
    cycles = Column(JSONB)

    birth_date = Column(Date, nullable=False)
    calculation_hash = Column(String(64))
    calculated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # profile = relationship("Profile", back_populates="numerology_profiles")

class NumerologyNameTrial(Base):
    __tablename__ = "numerology_name_trials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numerology_profile_id = Column(UUID(as_uuid=True), ForeignKey("numerology_profiles.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)

    trial_name = Column(String(255), nullable=False)
    system = Column(String(50), nullable=False)
    calculated_values = Column(JSONB, nullable=False)

    notes = Column(Text)
    is_preferred = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

class PrivacyPreference(Base):
    __tablename__ = "privacy_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), primary_key=True)

    store_numerology_trials = Column(Boolean, default=True)
    share_numerology_anonymously = Column(Boolean, default=False)
    store_palm_images = Column(Boolean, default=False)
    store_palm_features = Column(Boolean, default=True)
    erasable_audit = Column(Boolean, default=True)
    data_retention_days = Column(Integer, default=365)

    privacy_policy_version = Column(String(20))
    privacy_policy_accepted_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

### Task 8: Frontend Components

**Directory**: `frontend/components/numerology/`

#### 8.1 NumerologyProfile.tsx

Display Western and Vedic numbers in a clean, organized format:
- Life Path, Expression, Soul Urge (Western)
- Psychic, Destiny numbers (Vedic)
- Master Numbers badge
- Karmic Debt warnings
- Planet associations

#### 8.2 PersonalCycles.tsx

Show current cycles and upcoming periods:
- Personal Year/Month/Day
- Pinnacles timeline
- Challenges timeline
- Favorable dates this month

#### 8.3 NameCalculator.tsx

Interactive tool for name experiments:
- Input field for name variations
- Real-time calculation
- Comparison with current name
- Save trial feature

#### 8.4 Dashboard Integration

Add numerology tab to existing dashboard:
```typescript
// app/dashboard/numerology/page.tsx
export default function NumerologyPage() {
  // Fetch numerology profile
  // Display profile component
  // Show cycles
  // Name calculator tool
}
```

---

## Test Strategy

### Unit Tests (Backend)

**File**: `backend/tests/test_numerology_service.py`

```python
def test_life_path_calculation():
    """Test Life Path number calculation"""
    # Test case 1: Regular number
    assert calculate_life_path(date(1990, 5, 15)) == 3

    # Test case 2: Master number 11
    assert calculate_life_path(date(1983, 11, 29)) == 11

    # Test case 3: Master number 22
    assert calculate_life_path(date(1984, 7, 22)) == 22

def test_expression_number():
    """Test Expression number from name"""
    assert calculate_expression("John Smith") == 1
    assert calculate_expression("Mary Johnson") == 22  # Master number

def test_karmic_debt_detection():
    """Test Karmic Debt numbers"""
    # Birth date with 16 karmic debt
    assert 16 in detect_karmic_debt(date(1990, 7, 16))
```

**Coverage Target**: 90%+ for numerology_service.py

### Golden Test Cases

**File**: `backend/tests/golden_cases_numerology.json`

50 hand-verified test cases:
- 20 Western calculations (Life Path, Expression, Cycles)
- 15 Vedic calculations (Psychic, Destiny)
- 10 Combined (both systems)
- 5 Edge cases (Master numbers, Karmic debt)

Example golden case:
```json
{
  "name": "Albert Einstein",
  "birth_date": "1879-03-14",
  "expected": {
    "life_path": 8,
    "expression": 33,
    "soul_urge": 5,
    "psychic_number": 5,
    "destiny_number": 6
  }
}
```

### Integration Tests

Test full API flow:
- POST /numerology/calculate → verify response
- GET /numerology/profiles → verify list
- Caching behavior (hit/miss)

### Performance Tests

Benchmark calculations:
- Single calculation: <100ms target
- Batch 100 calculations: <5s target
- Cache retrieval: <10ms target

---

## Documentation Requirements

### 1. Technical Documentation

**File**: `backend/docs/NUMEROLOGY_TECHNICAL_SPEC.md`

Contents:
- Algorithm descriptions
- Number mappings (Pythagorean vs Chaldean)
- Calculation formulas
- Edge cases and special rules
- API reference
- Database schema details

### 2. API Documentation

Auto-generated via FastAPI/OpenAPI:
- Endpoint descriptions
- Request/response schemas
- Example requests
- Error codes

### 3. User Guide

**File**: `docs/USER_GUIDE_NUMEROLOGY.md`

Contents:
- What is numerology?
- How to read your numbers
- Understanding cycles
- Name correction guide
- FAQ

### 4. Architecture Update

Update `JIOASTRO_ARCHITECTURE_DOCUMENTATION.md`:
- Add numerology section
- Update feature list
- Update database schema
- Update API endpoints

---

## Quality Metrics

### Code Quality

- **Test Coverage**: ≥90% for numerology_service.py
- **Linting**: Pass Pylint/Flake8 with score >9.0
- **Type Hints**: 100% coverage (checked with mypy)
- **Documentation**: All public functions have docstrings

### Functional Quality

- **Golden Test Pass Rate**: 100% (50/50 cases)
- **API Success Rate**: >99.9% (excluding user errors)
- **Calculation Accuracy**: Verified against 3 authoritative sources

### Performance

- **Calculation Time**: <100ms (p95)
- **API Response Time**: <500ms (p95)
- **Cache Hit Rate**: >80% after warmup
- **Database Query Time**: <50ms (p95)

### Security

- **RLS Policies**: 100% coverage on new tables
- **Input Validation**: All inputs validated via Pydantic
- **SQL Injection**: Protected (using SQLAlchemy ORM)
- **Privacy**: DPDP compliance (erasable audit, consent)

---

## Timeline

### Week 1 (Nov 5-11)
- [x] Day 1: Database schema setup ✅
- [ ] Day 2-3: Western numerology engine
- [ ] Day 4-5: Vedic numerology engine
- [ ] Day 6-7: Unit tests for calculations

### Week 2 (Nov 12-18)
- [ ] Day 1-2: Numerology bridge & caching
- [ ] Day 3-4: API endpoints & schemas
- [ ] Day 5: Database models
- [ ] Day 6-7: Integration tests

### Week 3 (Nov 19-26)
- [ ] Day 1-3: Frontend components
- [ ] Day 4: Golden test cases
- [ ] Day 5: Documentation
- [ ] Day 6: Performance optimization
- [ ] Day 7: Final testing & QA

---

## Dependencies

### Technical Dependencies

**Python Packages** (add to requirements.txt):
```
# Numerology - no new packages needed (uses standard library)
```

**Frontend Packages**:
```json
// No new packages needed - uses existing UI components
```

### External Dependencies

- Supabase database (existing)
- Redis cache (existing)
- OpenAI API (for future KB integration)

### Team Dependencies

- Database admin: Run migration on production
- Frontend team: Integrate new components
- QA team: Validate golden test cases

---

## Risks & Mitigation

### Risk 1: Calculation Accuracy

**Risk**: Numerology calculations might not match authoritative sources

**Mitigation**:
- Cross-reference with 3+ numerology books
- Create comprehensive golden test suite
- Manual verification by numerology expert

### Risk 2: Performance

**Risk**: Calculating both systems might be slow

**Mitigation**:
- Implement aggressive caching (Redis + DB)
- Optimize calculation algorithms
- Use async/await for parallelization

### Risk 3: Database Migration

**Risk**: Migration might fail on production

**Mitigation**:
- Test migration on staging first
- Create rollback script
- Backup database before migration

### Risk 4: Frontend Integration

**Risk**: New UI might not match existing design system

**Mitigation**:
- Reuse existing shadcn/ui components
- Follow established patterns from astrology UI
- Design review before implementation

---

## Success Criteria

Phase 1 is considered complete when:

- [x] ✅ Database schema deployed to production
- [ ] ✅ All 50 golden test cases pass
- [ ] ✅ API endpoints functional and documented
- [ ] ✅ Frontend UI integrated and responsive
- [ ] ✅ Performance targets met (<500ms API response)
- [ ] ✅ Security review passed (RLS, validation)
- [ ] ✅ Documentation complete (technical + user guide)
- [ ] ✅ Code review approved
- [ ] ✅ QA sign-off

---

## Next Steps After Phase 1

1. **User Acceptance Testing** (1 week)
   - Beta release to 10-20 users
   - Collect feedback
   - Fix bugs

2. **Knowledge Base Integration** (overlaps with Phase 4)
   - Ingest numerology books
   - Extract 100+ rules
   - Integrate with RAG system

3. **Production Deployment** (1 day)
   - Deploy to production
   - Monitor metrics
   - Announce new feature

4. **Phase 2 Planning** (Palmistry)
   - Kickoff meeting
   - Architecture review
   - Timeline finalization

---

**Document Status**: Living Document
**Last Updated**: 2025-11-05
**Next Review**: 2025-11-12 (end of Week 1)

---

*Phase 1: Numerology Integration - Building the Foundation for Multi-Modal Insights*
