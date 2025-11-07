# Ashtakavarga System Implementation Design

**Date:** January 7, 2025
**Status:** Implementation in Progress

---

## Overview

Ashtakavarga is a predictive system in Vedic astrology that uses a **point-based scoring** mechanism to evaluate planetary strength in each house. It's one of the most accurate methods for:
- **Timing events** (transits)
- **Judging planetary strength** in houses
- **Predicting results** of dasha periods
- **Life event forecasting**

The word "Ashtakavarga" means "eight divisions" (Ashta = 8, Varga = division), referring to the 8 reference points: 7 planets + Ascendant.

---

## Core Concepts

### 1. Bhinna Ashtakavarga (Individual Charts)

Each planet has its own Ashtakavarga chart showing **benefic points (bindus)** contributed by other planets and the Ascendant.

**The 7 Planets with Ashtakavarga:**
- Sun
- Moon
- Mars
- Mercury
- Jupiter
- Venus
- Saturn

**Reference Points (Contributors):**
For each planet, bindus are contributed from 8 positions:
1. **Sun**
2. **Moon**
3. **Mars**
4. **Mercury**
5. **Jupiter**
6. **Venus**
7. **Saturn**
8. **Ascendant (Lagna)**

**Calculation Method:**
1. For each reference point, certain houses receive 1 bindu (benefic point)
2. Houses are counted from the reference point's position
3. If a house receives a bindu, mark it as 1; otherwise 0
4. Add up all bindus for each house (max 8 per house)

### 2. Benefic Point Tables

Each planet has a fixed table showing which houses receive bindus from which reference points.

**Example: Sun's Ashtakavarga**

| From | Houses receiving bindus |
|------|------------------------|
| Sun | 1, 2, 4, 7, 8, 9, 10, 11 |
| Moon | 3, 6, 10, 11 |
| Mars | 1, 2, 4, 7, 8, 9, 10, 11 |
| Mercury | 3, 5, 6, 9, 10, 11, 12 |
| Jupiter | 5, 6, 9, 11 |
| Venus | 6, 7, 12 |
| Saturn | 1, 2, 4, 7, 8, 9, 10, 11 |
| Ascendant | 3, 4, 6, 10, 11, 12 |

*(Complete tables for all planets available in classical texts)*

### 3. Sarva Ashtakavarga (Collective Chart)

**Sarva Ashtakavarga** combines all 7 Bhinna Ashtakavarga charts into one unified chart showing total bindus in each house.

**Calculation:**
- Add bindus from all 7 planets for each house
- Each house can have 0-56 bindus (7 planets × 8 reference points)
- Higher bindus = stronger house
- Lower bindus = weaker house

**Standard Interpretation:**
- **30+ bindus**: Very strong house, excellent results
- **25-29 bindus**: Good strength, positive results
- **20-24 bindus**: Average strength, moderate results
- **15-19 bindus**: Below average, challenges likely
- **Below 15**: Weak house, difficulties expected

### 4. Reductions (Shodhya Pinda)

After calculating basic bindus, **reductions** are applied based on:
- **Trikona houses** (1, 5, 9): Reduce if certain planets present
- **Exalted/Debilitated planets**: Adjust bindus
- **Planetary aspects**: Malefic aspects reduce, benefic increase

**Types of Pindas:**
1. **Graha Pinda**: Planetary strength score
2. **Rashi Pinda**: Sign strength score
3. **Yoga Pinda**: Combined strength
4. **Sodhya Pinda**: Net strength after reductions

### 5. Transit Predictions (Gochara)

Ashtakavarga is primarily used for **transit predictions**:

**Method:**
1. Check current transiting planet's position
2. Find bindus in that house in planet's Bhinna chart
3. Find bindus in Sarva Ashtakavarga
4. Higher bindus = favorable transit
5. Lower bindus = challenging transit

**Transit Rules:**
- **4+ bindus**: Favorable transit
- **3 bindus**: Neutral, mixed results
- **0-2 bindus**: Difficult transit, obstacles

**Example:**
If Saturn is transiting 7th house and:
- Saturn's Bhinna chart shows 5 bindus in 7th house → Good
- Sarva Ashtakavarga shows 28 bindus in 7th house → Excellent
- Conclusion: Saturn transit brings positive results despite being malefic

### 6. Kakshya System (Sub-Division)

Each house is divided into **8 kakshyas** (subdivisions), each ruled by one of the 7 planets + Ascendant.

**Kakshya Rulers (in order):**
1. Saturn (3.75°)
2. Jupiter (3.75°)
3. Mars (3.75°)
4. Sun (3.75°)
5. Venus (3.75°)
6. Mercury (3.75°)
7. Moon (3.75°)
8. Ascendant (3.75°)

**Usage:**
- Transiting planet in its own kakshya → Extra strength
- Transiting planet in friendly kakshya → Support
- Transiting planet in enemy kakshya → Challenges

---

## Implementation Architecture

### Service: `ashtakavarga_service.py`

```python
class AshtakavargaService:
    def __init__(self):
        # Initialize benefic point tables

    # Bhinna Ashtakavarga
    def calculate_bhinna_ashtakavarga(self, planet: str, chart: dict) -> dict
    def get_benefic_points_table(self, planet: str) -> dict
    def calculate_planet_bindus(self, planet: str, reference: str, chart: dict) -> list

    # Sarva Ashtakavarga
    def calculate_sarva_ashtakavarga(self, chart: dict) -> dict
    def combine_bhinna_charts(self, bhinna_charts: dict) -> dict

    # Pinda Calculations
    def calculate_graha_pinda(self, planet: str, chart: dict) -> int
    def calculate_rashi_pinda(self, sign: int, chart: dict) -> int
    def calculate_sodhya_pinda(self, chart: dict) -> dict

    # Transit Analysis
    def analyze_transit(self, planet: str, house: int, chart: dict) -> dict
    def get_transit_strength(self, planet: str, house: int, bhinna: dict, sarva: dict) -> str

    # Kakshya System
    def get_kakshya_lord(self, longitude: float) -> str
    def analyze_kakshya_position(self, planet: str, chart: dict) -> dict

    # Comprehensive Analysis
    def analyze_ashtakavarga(self, chart: dict) -> dict
```

---

## Data Structures

### Bhinna Ashtakavarga Output (Single Planet)
```json
{
  "planet": "Sun",
  "bindus_by_house": {
    "1": 4,
    "2": 5,
    "3": 3,
    "4": 6,
    "5": 5,
    "6": 4,
    "7": 5,
    "8": 4,
    "9": 6,
    "10": 5,
    "11": 7,
    "12": 4
  },
  "total_bindus": 58,
  "strongest_houses": [11, 4, 9],
  "weakest_houses": [3, 6, 8, 12],
  "contributors": {
    "1": ["Sun", "Mars", "Saturn", "Ascendant"],
    "2": ["Sun", "Mars", "Saturn", "Mercury", "Venus"]
  }
}
```

### Sarva Ashtakavarga Output
```json
{
  "bindus_by_house": {
    "1": 28,
    "2": 32,
    "3": 25,
    "4": 35,
    "5": 30,
    "6": 22,
    "7": 27,
    "8": 24,
    "9": 31,
    "10": 29,
    "11": 34,
    "12": 23
  },
  "total_bindus": 340,
  "house_strength": {
    "1": "good",
    "2": "very_strong",
    "3": "average",
    "4": "very_strong",
    "5": "very_strong",
    "6": "average",
    "7": "good",
    "8": "average",
    "9": "very_strong",
    "10": "good",
    "11": "very_strong",
    "12": "average"
  },
  "strongest_houses": [4, 11, 2, 9],
  "weakest_houses": [6, 12, 8]
}
```

### Transit Analysis Output
```json
{
  "transiting_planet": "Saturn",
  "current_house": 7,
  "bhinna_bindus": 5,
  "sarva_bindus": 27,
  "transit_strength": "favorable",
  "effects": [
    "Partnership and marriage matters favored",
    "Business collaborations successful",
    "Legal matters resolved positively"
  ],
  "duration_quality": "good",
  "recommendations": [
    "Good time for new partnerships",
    "Sign contracts during this period",
    "Relationship initiatives well-supported"
  ]
}
```

### Pinda Analysis Output
```json
{
  "graha_pindas": {
    "Sun": 4,
    "Moon": 5,
    "Mars": 3,
    "Mercury": 6,
    "Jupiter": 5,
    "Venus": 4,
    "Saturn": 5
  },
  "rashi_pindas": {
    "Aries": 6,
    "Taurus": 5,
    "Gemini": 4
  },
  "sodhya_pindas": {
    "Sun": 3,
    "Moon": 4
  },
  "strongest_planets": ["Mercury", "Moon", "Jupiter"],
  "weakest_planets": ["Mars"]
}
```

---

## Benefic Point Tables (Complete)

### Sun's Ashtakavarga
| From | Benefic Houses |
|------|----------------|
| Sun | 1, 2, 4, 7, 8, 9, 10, 11 |
| Moon | 3, 6, 10, 11 |
| Mars | 1, 2, 4, 7, 8, 9, 10, 11 |
| Mercury | 3, 5, 6, 9, 10, 11, 12 |
| Jupiter | 5, 6, 9, 11 |
| Venus | 6, 7, 12 |
| Saturn | 1, 2, 4, 7, 8, 9, 10, 11 |
| Ascendant | 3, 4, 6, 10, 11, 12 |

### Moon's Ashtakavarga
| From | Benefic Houses |
|------|----------------|
| Sun | 3, 6, 7, 8, 10, 11 |
| Moon | 1, 3, 6, 7, 10, 11 |
| Mars | 2, 3, 5, 6, 9, 10, 11 |
| Mercury | 1, 3, 4, 5, 7, 8, 10, 11 |
| Jupiter | 1, 4, 7, 8, 10, 11, 12 |
| Venus | 3, 4, 5, 7, 9, 10, 11 |
| Saturn | 3, 5, 6, 11 |
| Ascendant | 3, 6, 10, 11 |

### Mars' Ashtakavarga
| From | Benefic Houses |
|------|----------------|
| Sun | 3, 5, 6, 10, 11 |
| Moon | 3, 6, 11 |
| Mars | 1, 2, 4, 7, 8, 10, 11 |
| Mercury | 3, 5, 6, 11 |
| Jupiter | 6, 10, 11, 12 |
| Venus | 6, 8, 11, 12 |
| Saturn | 1, 4, 7, 8, 9, 10, 11 |
| Ascendant | 1, 3, 6, 10, 11 |

### Mercury's Ashtakavarga
| From | Benefic Houses |
|------|----------------|
| Sun | 5, 6, 9, 11, 12 |
| Moon | 2, 4, 6, 8, 10, 11 |
| Mars | 1, 2, 4, 7, 8, 9, 10, 11 |
| Mercury | 1, 3, 5, 6, 9, 10, 11, 12 |
| Jupiter | 6, 8, 11, 12 |
| Venus | 1, 2, 3, 4, 5, 8, 9, 11 |
| Saturn | 1, 2, 4, 7, 8, 9, 10, 11 |
| Ascendant | 1, 2, 4, 6, 8, 10, 11 |

### Jupiter's Ashtakavarga
| From | Benefic Houses |
|------|----------------|
| Sun | 1, 2, 3, 4, 7, 8, 9, 10, 11 |
| Moon | 2, 5, 7, 9, 11 |
| Mars | 1, 2, 4, 7, 8, 10, 11 |
| Mercury | 1, 2, 4, 5, 6, 9, 10, 11 |
| Jupiter | 1, 2, 3, 4, 7, 8, 10, 11 |
| Venus | 2, 5, 6, 9, 10, 11 |
| Saturn | 3, 5, 6, 12 |
| Ascendant | 1, 2, 4, 5, 6, 7, 9, 10, 11 |

### Venus' Ashtakavarga
| From | Benefic Houses |
|------|----------------|
| Sun | 8, 11, 12 |
| Moon | 1, 2, 3, 4, 5, 8, 9, 11, 12 |
| Mars | 3, 4, 6, 9, 11, 12 |
| Mercury | 3, 5, 6, 9, 11 |
| Jupiter | 5, 8, 9, 10, 11 |
| Venus | 1, 2, 3, 4, 5, 8, 9, 11 |
| Saturn | 3, 4, 5, 8, 9, 10, 11 |
| Ascendant | 1, 2, 3, 4, 5, 8, 9, 11 |

### Saturn's Ashtakavarga
| From | Benefic Houses |
|------|----------------|
| Sun | 1, 2, 4, 7, 8, 10, 11 |
| Moon | 3, 6, 11 |
| Mars | 3, 5, 6, 10, 11, 12 |
| Mercury | 6, 8, 9, 10, 11, 12 |
| Jupiter | 5, 6, 11, 12 |
| Venus | 6, 11, 12 |
| Saturn | 3, 5, 6, 11 |
| Ascendant | 1, 3, 4, 6, 10, 11 |

---

## Integration Points

1. **Chart Calculation:** Ashtakavarga calculated during main chart generation
2. **Storage:** Add `ashtakavarga_data` JSONB column to `charts` table
3. **API Endpoints:**
   - `/api/v1/enhancements/ashtakavarga/bhinna/{planet}`
   - `/api/v1/enhancements/ashtakavarga/sarva`
   - `/api/v1/enhancements/ashtakavarga/transit`
4. **Frontend:** New tab "Ashtakavarga Analysis" with visual bindu charts

---

## Visualization Recommendations

1. **Bhinna Charts**: 12-house circle with bindu counts in each house
2. **Sarva Chart**: Larger circle with colored intensity (darker = more bindus)
3. **Transit View**: Current planet positions overlaid on Sarva chart
4. **Timeline**: Show future transits through high/low bindu houses

---

## References

- **Brihat Parashara Hora Shastra** (Chapters on Ashtakavarga)
- **Uttara Kalamrita** by Kalidasa (Ashtakavarga sections)
- **Ashtakavarga System of Prediction** by B.V. Raman
- **Practical Application of Ashtakavarga** by K.S. Charak

---

## Testing Strategy

1. **Validation:** Compare with Jagannatha Hora, Parashara's Light
2. **Golden Cases:** Use known charts with verified Ashtakavarga
3. **Transit Testing:** Verify transit predictions match classical results
4. **Performance:** Benchmark calculation time (< 200ms for full analysis)
