# Jaimini System Implementation Design

**Date:** January 7, 2025
**Status:** Implementation in Progress

---

## Overview

The Jaimini System is an alternative Vedic astrology system attributed to Maharishi Jaimini. Unlike Parashari astrology which focuses on planets, Jaimini emphasizes **signs (rashis)** and their relationships. This system is particularly powerful for timing events and understanding karmic patterns.

---

## Core Concepts

### 1. Chara Karakas (Significators)

Planets become significators based on their **longitudinal degrees** (not sign positions). The planet with the highest degree becomes Atmakaraka (soul significator), and others follow in descending order.

**The 7 Chara Karakas:**

| Karaka | Meaning | Signifies |
|--------|---------|-----------|
| **AK** (Atmakaraka) | Soul | Self, soul's journey, primary life purpose |
| **AmK** (Amatyakaraka) | Minister | Career, profession, advisors |
| **BK** (Bhratrukaraka) | Sibling | Siblings, courage, initiatives |
| **MK** (Matrukaraka) | Mother | Mother, emotions, home, vehicles |
| **PK** (Pitrukaraka) | Father | Father, authority, teachers, dharma |
| **GK** (Gnatikaraka) | Cousin | Obstacles, enemies, diseases, competitors |
| **DK** (Darakaraka) | Spouse | Spouse, relationships, partnerships |

**Calculation Rules:**
- Use absolute longitude (0-360°) ignoring signs
- Rahu counts from **opposite degree** (30° - actual degree in sign)
- If two planets have same degrees, use minutes; if same minutes, use seconds
- Moon is excluded in some traditions (we'll include it)

### 2. Karakamsha

**Karakamsha** is the Navamsa (D9) position of the Atmakaraka (AK). It reveals:
- **Spiritual inclinations**
- **Deep desires and motivations**
- **Career aptitudes**
- **Past life karmas**

Planets in Karakamsha or aspecting it significantly influence the soul's journey.

### 3. Svamsa (Lagnamsa)

**Svamsa** is the Navamsa position of the Lagna (Ascendant). It represents:
- **True self-image**
- **Hidden personality traits**
- **Karmic tendencies**

### 4. Arudha Padas (Illusion Points)

Arudha Padas show **how things appear** rather than how they actually are. They represent the **maya** (illusion) surrounding various life areas.

**Key Arudhas:**

| Arudha | From House | Represents |
|--------|------------|------------|
| **AL** (Arudha Lagna) | 1st | Self-image, public persona, how others see you |
| **UL** (Upapada Lagna) | 12th | Marriage, spouse's nature, marriage circumstances |
| **A2** | 2nd | Wealth perception, family image |
| **A4** | 4th | Property, mother's image |
| **A7** | 7th | Partner's image, business reputation |
| **A10** | 10th | Career reputation, fame |
| **A11** | 11th | Gains perception |

**Calculation Method:**
1. Find the lord of the house
2. Count from the lord to the house
3. Count the same distance from the house
4. That sign is the Arudha Pada
5. **Exception Rules:**
   - If Pada falls in 1st or 7th from the house, count 10 signs ahead instead
   - If lord is in own house, Pada = 4th or 10th from that house

### 5. Rashi Drishti (Sign Aspects)

Unlike Parashari graha drishti (planetary aspects), Jaimini uses **Rashi Drishti** (sign aspects). **All signs aspect other signs**, not individual planets.

**Aspect Rules:**

| Sign Type | Aspects |
|-----------|---------|
| **Movable Signs** (Aries, Cancer, Libra, Capricorn) | Aspect **fixed signs** (excluding own) |
| **Fixed Signs** (Taurus, Leo, Scorpio, Aquarius) | Aspect **movable signs** (excluding own) |
| **Dual Signs** (Gemini, Virgo, Sagittarius, Pisces) | Aspect each other (excluding own) |

**Example:**
- Aries (movable) aspects: Taurus, Leo, Scorpio, Aquarius (all fixed except itself)
- Taurus (fixed) aspects: Aries, Cancer, Libra, Capricorn (all movable except itself)
- Gemini (dual) aspects: Virgo, Sagittarius, Pisces (other duals except itself)

**Argala (Intervention):**
- Planets 2nd, 4th, 11th create **beneficial intervention**
- Planets 3rd, 10th, 5th create **obstructions** to Argala

### 6. Chara Dasha (Movable Periods)

Chara Dasha is a **sign-based dasha system** (not planet-based like Vimshottari). The sequence and length of dashas depend on:
- **Ascendant sign type** (movable/fixed/dual)
- **Paka** (whether certain conditions are met)
- **Direction** (forward or reverse zodiac movement)

**Basic Calculation:**
1. Determine if Lagna is movable, fixed, or dual
2. Check for Paka conditions (Jupiter/Mercury/Moon positions)
3. Determine direction (clockwise or counterclockwise)
4. Calculate dasha years for each sign (0-12 years based on planets)
5. Sequence signs according to rules

**Dasha Length Formula:**
- Count from sign to its lord (or lord's exaltation sign in some methods)
- Each count = 1 year
- Antardashas follow similar logic

---

## Implementation Architecture

### Service: `jaimini_service.py`

```python
class JaiminiService:
    def __init__(self):
        # Initialize with vedic calculations

    # Chara Karakas
    def calculate_chara_karakas(self, planets: dict) -> dict
    def get_atmakaraka(self, karakas: dict) -> dict
    def get_karaka_significations(self, karaka_type: str) -> dict

    # Karakamsha
    def calculate_karakamsha(self, atmakaraka: dict, d9_chart: dict) -> dict
    def analyze_karakamsha(self, karakamsha: dict, d9_chart: dict) -> dict

    # Arudha Padas
    def calculate_arudha_pada(self, house: int, chart: dict) -> dict
    def calculate_all_arudha_padas(self, chart: dict) -> dict
    def calculate_arudha_lagna(self, chart: dict) -> dict
    def calculate_upapada_lagna(self, chart: dict) -> dict

    # Rashi Drishti
    def get_sign_type(self, sign: int) -> str  # movable/fixed/dual
    def calculate_rashi_drishti(self, sign: int) -> list
    def get_aspected_houses(self, house: int, chart: dict) -> list

    # Argala
    def calculate_argala(self, house: int, chart: dict) -> dict
    def calculate_virodha_argala(self, house: int, chart: dict) -> dict

    # Chara Dasha
    def calculate_chara_dasha_direction(self, chart: dict) -> str
    def calculate_chara_dasha_years(self, sign: int, chart: dict) -> int
    def calculate_chara_dasha_sequence(self, chart: dict) -> list
    def calculate_chara_dasha_periods(self, chart: dict, birth_date: date) -> list
```

---

## Data Structures

### Chara Karakas Output
```json
{
  "atmakaraka": {"planet": "Mars", "degree": 298.45, "sign": "Capricorn", "house": 10},
  "amatyakaraka": {"planet": "Venus", "degree": 285.23, "sign": "Capricorn", "house": 10},
  "bhratrukaraka": {"planet": "Mercury", "degree": 275.12, "sign": "Sagittarius", "house": 9},
  "matrukaraka": {"planet": "Sun", "degree": 268.89, "sign": "Sagittarius", "house": 9},
  "pitrukaraka": {"planet": "Saturn", "degree": 245.67, "sign": "Scorpio", "house": 8},
  "gnatikaraka": {"planet": "Moon", "degree": 156.34, "sign": "Virgo", "house": 6},
  "darakaraka": {"planet": "Jupiter", "degree": 125.78, "sign": "Leo", "house": 5}
}
```

### Karakamsha Output
```json
{
  "sign": "Aries",
  "house_in_d9": 1,
  "lord": "Mars",
  "planets_in_karakamsha": ["Sun", "Mercury"],
  "aspecting_planets": ["Jupiter", "Saturn"],
  "significations": ["Leadership", "Initiative", "Courage"],
  "career_indications": ["Military", "Engineering", "Surgery"],
  "spiritual_path": "Karma Yoga (Action-based spirituality)"
}
```

### Arudha Padas Output
```json
{
  "arudha_lagna": {"sign": "Leo", "house": 5, "description": "Charismatic public image"},
  "upapada_lagna": {"sign": "Taurus", "house": 2, "description": "Stable marriage, spouse from wealthy family"},
  "a2_wealth": {"sign": "Virgo", "house": 6},
  "a4_property": {"sign": "Scorpio", "house": 8},
  "a10_career": {"sign": "Pisces", "house": 12}
}
```

### Chara Dasha Output
```json
{
  "current_dasha": {
    "sign": "Scorpio",
    "start_date": "2020-05-15",
    "end_date": "2028-05-15",
    "duration_years": 8,
    "interpretation": "Period of transformation, research, occult interests"
  },
  "all_dashas": [
    {"sign": "Aries", "start": "1990-01-15", "end": "2002-01-15", "years": 12},
    {"sign": "Pisces", "start": "2002-01-15", "end": "2011-01-15", "years": 9}
  ]
}
```

---

## Integration Points

1. **Chart Calculation:** Jaimini data calculated during main chart generation
2. **Storage:** Add `jaimini_data` JSONB column to `charts` table
3. **API Endpoint:** `/api/v1/enhancements/jaimini/analyze`
4. **Frontend:** New tab "Jaimini Analysis" in chart page

---

## References

- **Jaimini Sutras** (Original text)
- **Jaimini Chara Dasha** by Sanjay Rath
- **Karakas: The Jaimini Way** by P.V.R. Narasimha Rao
- **Vedic Astrology: An Integrated Approach** by P.V.R. Narasimha Rao

---

## Testing Strategy

1. **Golden Test Cases:** Use known charts with verified Jaimini calculations
2. **Compare:** Validate against Jagannatha Hora, Parashara's Light
3. **Edge Cases:** Test with Rahu as karaka, same degree planets
4. **Performance:** Benchmark calculation time (< 100ms target)
