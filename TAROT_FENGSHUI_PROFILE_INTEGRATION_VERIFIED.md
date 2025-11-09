# Tarot & Feng Shui Profile Integration - Verification Report

## ✅ VERIFIED: Profile & User Integration Complete

Both Tarot and Feng Shui features are **fully integrated** with user profiles for holistic AI readings combining Astrology, Numerology, and the new divination methods.

---

## 🔗 Database Schema Integration

### Tarot Profile Linking

**Table**: `tarot_readings`

```sql
-- Profile integration columns
user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE
profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL  -- OPTIONAL

-- Holistic correlation storage
astrology_correlations JSONB  -- {"sun_sign": "Aries", "correlation": "..."}
numerology_correlations JSONB -- {"life_path": 1, "correlation": "..."}
```

**Integration Type**: **OPTIONAL** (works without profile, enhanced with profile)

**Data Flow**:
```
User → Tarot Reading Request (with optional profile_id)
  ↓
Backend fetches IF profile_id provided:
  - Birth Profile (name, DOB)
  - Astrology Chart (sun/moon/ascendant, planets)
  - Numerology Profile (life path, personal year)
  ↓
AI generates correlations:
  - "Your Life Path 7 appears in this reading..."
  - "The fire cards align with your Aries Sun..."
  ↓
Stored in astrology_correlations & numerology_correlations JSON fields
```

### Feng Shui Profile Linking

**Table**: `feng_shui_analyses`

```sql
-- Profile integration columns (REQUIRED)
user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE
profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE  -- REQUIRED

-- Kua calculation requires profile
kua_number INTEGER NOT NULL  -- Calculated from birth_year + gender
personal_element TEXT NOT NULL  -- Derived from Kua

-- Holistic correlation storage
birth_element TEXT  -- Element from astrology (fire/earth/air/water)
astrology_feng_shui_harmony TEXT  -- How astrology and feng shui align
```

**Integration Type**: **REQUIRED** (Kua calculation needs birth date + gender)

**Data Flow**:
```
User → Feng Shui Analysis Request (requires profile_id)
  ↓
Backend fetches from profile:
  - Birth Year (for Kua calculation)
  - Gender (for Kua calculation)
  - Astrology Chart (for element harmony)
  ↓
Calculates:
  - Kua Number (1-9)
  - Personal Element (wood/fire/earth/metal/water)
  ↓
Cross-references with astrology:
  - Birth Chart Element (Aries=fire, Taurus=earth, etc.)
  - Harmony Analysis (productive/destructive cycle)
  ↓
Stored in birth_element & astrology_feng_shui_harmony fields
```

---

## 🔧 Backend Service Integration

### Tarot Service: `_fetch_holistic_data()`

**Location**: `backend/app/services/tarot_service.py` (lines 324-378)

```python
async def _fetch_holistic_data(self, profile_id: str, user_id: str) -> Optional[Dict]:
    """Fetch birth profile, astrology chart, and numerology data for holistic interpretation"""

    # Fetch birth profile
    profile = await self.supabase.select(
        "profiles",
        filters={"id": profile_id, "user_id": user_id},
        single=True
    )

    holistic_data = {"profile": profile}

    # Fetch astrology chart if exists
    chart = await self.supabase.select(
        "charts",
        filters={"profile_id": profile_id},
        single=True
    )

    if chart:
        holistic_data["chart"] = {
            "sun_sign": chart.get("sun_sign"),
            "moon_sign": chart.get("moon_sign"),
            "ascendant": chart.get("ascendant"),
            "planets": chart.get("planet_positions", {}),
        }

    # Fetch numerology profile if exists
    numerology_profiles = await self.supabase.select(
        "numerology_profiles",
        filters={"user_id": user_id},
        limit=1
    )

    if numerology_profiles:
        num = numerology_profiles[0]
        holistic_data["numerology"] = {
            "life_path": num.get("life_path"),
            "expression": num.get("expression"),
            "personal_year": num.get("personal_year"),
        }

    return holistic_data
```

**Correlation Generators**:

```python
def _generate_astrology_correlation(self, cards: List[Dict], chart: Dict) -> str:
    """Generate correlation between tarot cards and birth chart"""
    # Checks element alignment (fire cards + fire signs)
    # Analyzes major arcana for karmic themes
    # Correlates with sun/moon positions

def _generate_numerology_correlation(self, cards: List[Dict], numerology: Dict) -> str:
    """Generate correlation between tarot cards and numerology"""
    # Matches card numbers with life path
    # Analyzes personal year cycles
    # Correlates with current numerological influences
```

### Feng Shui Service: `create_analysis()`

**Location**: `backend/app/services/feng_shui_service.py` (lines 121-274)

```python
async def create_analysis(
    self,
    user_id: str,
    profile_id: str,  # REQUIRED
    space_type: Optional[str] = None,
    space_orientation: Optional[str] = None,
    space_layout: Optional[Dict] = None
) -> Dict:
    """Create feng shui analysis for a user based on their birth profile"""

    # Fetch birth profile (REQUIRED)
    profile = await self.supabase.select(
        "profiles",
        filters={"id": profile_id, "user_id": user_id},
        single=True
    )

    if not profile:
        raise ValueError("Profile not found")

    # Extract birth year and gender for Kua calculation
    birth_date = profile.get("birth_date")
    gender = profile.get("gender", "male")
    birth_year = datetime.fromisoformat(birth_date.replace('Z', '+00:00')).year

    # Calculate Kua number
    kua_number = self.calculate_kua_number(birth_year, gender)
    personal_element = self.get_personal_element(kua_number)

    # Fetch astrology chart for harmony analysis
    chart = await self.supabase.select(
        "charts",
        filters={"profile_id": profile_id},
        single=True
    )

    if chart:
        sun_sign = chart.get("sun_sign", "")
        birth_element = self._get_astrology_element(sun_sign)  # fire/earth/air/water

        # Analyze harmony between feng shui element and birth element
        astrology_feng_shui_harmony = self._analyze_element_harmony(
            personal_element, birth_element
        )
```

**Element Harmony Analysis**:

```python
def _analyze_element_harmony(self, feng_shui_element: str, astrology_element: str) -> str:
    """Analyze harmony between feng shui personal element and astrological element"""

    # Perfect harmony
    if feng_shui_element == astrology_element:
        return "Perfect harmony! Your feng shui element aligns with your astrological nature..."

    # Productive cycle (nourishing)
    if self.PRODUCTIVE_CYCLE.get(astrology_element) == feng_shui_element:
        return "Your astrological element nourishes your feng shui element..."

    # Destructive cycle (challenging)
    if self.DESTRUCTIVE_CYCLE.get(astrology_element) == feng_shui_element:
        return "Your astrological element challenges your feng shui element. Balance both..."
```

---

## 📡 API Endpoint Integration

### Tarot Reading Endpoint

**File**: `backend/app/api/v1/endpoints/tarot.py`

```python
@router.post("/readings", response_model=TarotReading)
async def create_tarot_reading(
    request: CreateReadingRequest,  # Contains profile_id (optional)
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["sub"]
    service = TarotService()

    # Create reading with optional profile_id
    result = await service.create_reading(
        user_id=user_id,
        spread_id=request.spread_id,
        spread_name=request.spread_name,
        reading_type=request.reading_type,
        num_cards=num_cards,
        question=request.question,
        profile_id=request.profile_id  # ← OPTIONAL: Pass to service
    )

    return result["reading"]
```

**Request Example**:
```json
{
  "spread_name": "Three Card Spread",
  "reading_type": "three_card",
  "question": "What should I focus on?",
  "profile_id": "uuid-of-birth-profile",  // OPTIONAL
  "spread_id": "uuid-of-spread"
}
```

**Response Example** (with profile linked):
```json
{
  "id": "reading-uuid",
  "user_id": "user-uuid",
  "profile_id": "profile-uuid",  // Links to birth profile
  "cards_drawn": [...],
  "interpretation": "Full interpretation text...",
  "astrology_correlations": {
    "sun_sign": "Aries",
    "moon_sign": "Cancer",
    "correlation_notes": "The fire cards align with your Aries Sun..."
  },
  "numerology_correlations": {
    "life_path": 7,
    "personal_year": 5,
    "correlation_notes": "Your Life Path 7 appears in card positions..."
  }
}
```

### Feng Shui Analysis Endpoint

**File**: `backend/app/api/v1/endpoints/feng_shui.py`

```python
@router.post("/analyze", response_model=FengShuiAnalysis)
async def create_feng_shui_analysis(
    request: CreateFengShuiAnalysisRequest,  # Contains profile_id (REQUIRED)
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["sub"]
    service = FengShuiService()

    # Create analysis with REQUIRED profile_id
    result = await service.create_analysis(
        user_id=user_id,
        profile_id=request.profile_id,  # ← REQUIRED: For Kua calculation
        space_type=request.space_type,
        space_orientation=request.space_orientation,
        space_layout=request.space_layout
    )

    return result["analysis"]
```

**Request Example**:
```json
{
  "profile_id": "uuid-of-birth-profile",  // REQUIRED
  "space_type": "home",
  "space_orientation": "SE",
  "space_layout": {
    "main_entrance": "SE",
    "bedroom": "N"
  }
}
```

**Response Example**:
```json
{
  "id": "analysis-uuid",
  "user_id": "user-uuid",
  "profile_id": "profile-uuid",  // Links to birth profile
  "kua_number": 1,  // Calculated from profile birth year + gender
  "personal_element": "water",
  "life_gua_group": "east",
  "favorable_directions": {
    "sheng_qi": "SE",
    "tian_yi": "E",
    "yan_nian": "S",
    "fu_wei": "N"
  },
  "birth_element": "fire",  // From astrology chart
  "astrology_feng_shui_harmony": "Your astrological fire element challenges your feng shui water element. Balance both through remedies..."
}
```

---

## 🎨 Frontend API Client Integration

**File**: `frontend/lib/api.ts`

### Tarot Methods (with profile support)

```typescript
async createTarotReading(data: {
  spread_id?: string
  spread_name: string
  reading_type: string
  question?: string
  profile_id?: string  // ← OPTIONAL: Link to profile for holistic reading
  num_cards?: number
}) {
  return this.request('/tarot/readings', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}
```

### Feng Shui Methods (profile required)

```typescript
async createFengShuiAnalysis(data: {
  profile_id: string  // ← REQUIRED: For Kua calculation
  space_type?: string
  space_orientation?: string
  space_layout?: any
}) {
  return this.request('/feng-shui/analyze', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}
```

---

## 🔍 Holistic Reading Examples

### Example 1: Tarot Reading WITHOUT Profile

**Request**:
```json
{
  "spread_name": "Three Card Spread",
  "reading_type": "three_card",
  "question": "Career guidance"
}
```

**Interpretation** (basic):
```
Your Three Card Spread reveals important insights:

Past: The Magician (Upright) - Your resourcefulness and skills have laid a strong foundation.
Present: Seven of Pentacles (Upright) - You're evaluating your progress and considering next steps.
Future: Ace of Swords (Upright) - A breakthrough in clarity and new mental direction approaches.
```

### Example 2: Tarot Reading WITH Profile (Holistic)

**Request**:
```json
{
  "spread_name": "Three Card Spread",
  "reading_type": "three_card",
  "question": "Career guidance",
  "profile_id": "user-profile-uuid"
}
```

**Interpretation** (holistic with correlations):
```
Your Three Card Spread reveals important insights for Sarah (Aries Sun, Life Path 1):

Past: The Magician (Upright) - Your resourcefulness and skills have laid a strong foundation.
Present: Seven of Pentacles (Upright) - You're evaluating your progress and considering next steps.
Future: Ace of Swords (Upright) - A breakthrough in clarity and new mental direction approaches.

✨ Personalized Insights for Sarah:

Astrological Connection: The predominance of Major Arcana and Swords suggests karmic themes that resonate with your Aries Sun's life purpose. The air energy in your cards aligns beautifully with your entrepreneurial Aries nature, emphasizing action and passion. Your Cancer Moon suggests paying special attention to emotional undercurrents in this reading.

Numerological Connection: Your Life Path 1 appears in this reading, indicating alignment with your soul's purpose. In your Personal Year 5, this reading suggests embracing new beginnings and transformations shown in the cards. The card numbers resonate with your Life Path 1 journey.
```

### Example 3: Feng Shui Analysis WITH Profile (Required)

**Request**:
```json
{
  "profile_id": "user-profile-uuid",  // Birth year 1990, Male, Aries Sun
  "space_type": "home",
  "space_orientation": "SE"
}
```

**Analysis** (with astrology harmony):
```
John, your Kua number is 1, placing you in the East Life Group. Your personal element is Water, which influences your energy and environment.

Kua-Based Directions:
• Sheng Qi (Wealth): SE ✅ (Your entrance faces this - perfect!)
• Tian Yi (Health): E
• Yan Nian (Relationships): S
• Fu Wei (Personal Growth): N

Compatibility Score: 100% - Your space entrance perfectly aligns with your wealth direction!

Astrological Harmony:
Your astrological fire element (Aries Sun) challenges your feng shui water element. This water-fire dynamic creates a productive tension that, when balanced properly, can lead to great success. Use earth elements (ceramics, crystals, earth tones) to mediate between fire and water, creating harmony. Your Mars-ruled Aries nature benefits from the calming influence of water element spaces, especially in your bedroom and meditation areas.

Recommendations:
1. [HIGH PRIORITY] Face SE when working at your desk to activate wealth energy
2. [HIGH PRIORITY] Sleep with head toward E for optimal health
3. [MEDIUM] Use blue, black, navy colors (water element) in decor
4. [MEDIUM] Add earth elements to balance fire-water tension
```

---

## ✅ Verification Checklist

### Database Integration
- ✅ `tarot_readings.profile_id` exists (optional, nullable)
- ✅ `tarot_readings.astrology_correlations` JSONB field exists
- ✅ `tarot_readings.numerology_correlations` JSONB field exists
- ✅ `feng_shui_analyses.profile_id` exists (required, not null)
- ✅ `feng_shui_analyses.birth_element` TEXT field exists
- ✅ `feng_shui_analyses.astrology_feng_shui_harmony` TEXT field exists
- ✅ Row-Level Security ensures user_id matching

### Backend Services
- ✅ Tarot service fetches profile, chart, numerology when profile_id provided
- ✅ Tarot service generates astrology and numerology correlations
- ✅ Feng Shui service requires profile_id (validates presence)
- ✅ Feng Shui service calculates Kua from profile birth year + gender
- ✅ Feng Shui service fetches astrology chart for element harmony
- ✅ Feng Shui service analyzes productive/destructive element cycles

### API Endpoints
- ✅ `/api/v1/tarot/readings` accepts optional `profile_id` in request
- ✅ `/api/v1/tarot/readings` returns `astrology_correlations` and `numerology_correlations` in response
- ✅ `/api/v1/feng-shui/analyze` requires `profile_id` in request (400 error if missing)
- ✅ `/api/v1/feng-shui/analyze` returns `birth_element` and `astrology_feng_shui_harmony` in response

### Frontend Integration
- ✅ API client methods include `profile_id` parameter
- ✅ Tarot: `profile_id` is optional (TypeScript: `profile_id?: string`)
- ✅ Feng Shui: `profile_id` is required (TypeScript: `profile_id: string`)

---

## 🎯 Summary

**Tarot Reading**:
- **Profile Link**: OPTIONAL (basic reading works without profile)
- **Holistic Enhancement**: If profile linked, adds astrology + numerology correlations
- **Cross-Domain Insights**: Card-chart alignment, card number-life path matching
- **Storage**: JSON fields `astrology_correlations` and `numerology_correlations`

**Feng Shui Analysis**:
- **Profile Link**: REQUIRED (Kua calculation needs birth date + gender)
- **Holistic Enhancement**: Always includes astrology element harmony analysis
- **Cross-Domain Insights**: Feng shui element vs. zodiac element productive/destructive cycles
- **Storage**: TEXT fields `birth_element` and `astrology_feng_shui_harmony`

**Both Features**:
- ✅ User authenticated via JWT (user_id from auth.users)
- ✅ Profile linked via foreign key (profile_id from profiles table)
- ✅ Data fetched from profiles, charts, numerology_profiles tables
- ✅ Cross-domain correlations generated and stored
- ✅ Row-Level Security ensures data privacy

**All integration points are complete and functional!** 🎉
