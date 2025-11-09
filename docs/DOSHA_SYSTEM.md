# Dosha Detection System - Complete Reference

JioAstro features enhanced detection of 4 major classical doshas (afflictions) with sophisticated intensity calculations, cancellation analysis, and categorized remedies.

## Overview

**Service Location:** `backend/app/services/dosha_detection_service.py` (~1756 lines)

**Performance:**
- Detection: ~5-15ms per dosha
- Complete analysis (4 doshas): ~20-60ms total
- Negligible overhead on chart calculations

**API Integration:** Doshas automatically detected during chart calculations, included in AI readings

**Frontend:** Dosha analysis pages with detailed breakdowns, intensity visualizations, categorized remedies

**Technical Implementation:**
- **Intensity Scoring**: All doshas calculate base scores with weighted indicators
- **Cancellation System**: Percentage-based reductions from benefic positions, planet strengths
- **Effect Categorization**: Life area-specific effects (family, progeny, finance, health, spiritual)
- **Remedy Stratification**: 3-tier system (base → low/medium → high/very_high)
- **Helper Methods**: Dedicated remedy methods for each dosha type
- **Response Structure**: Includes intensity_label, intensity_score, base_score, reduction_percentage, detailed breakdowns

## 1. Manglik Dosha (Mars Affliction)

### Detection Criteria
- Mars in houses 1, 2, 4, 7, 8, 12 from Lagna, Moon, OR Venus
- House intensity weights:
  - 8th house: 5
  - 1st/12th house: 4
  - 2nd/7th house: 3
  - 4th house: 2
- Sign strength modifiers:
  - Own/Exalted: +20-30%
  - Debilitated: -50%
- Retrograde Mars: +15%
- Combustion: -30%

### Intensity Levels

| Level | Score | Impact | Delays | Remedy Requirement |
|-------|-------|--------|--------|-------------------|
| Very High | 7+ | Severe | 7+ years | Comprehensive remedies essential |
| High | 5-7 | Significant | 5-7 years | Strong remedial measures needed |
| Medium | 3-5 | Moderate | 3-5 years | Remedies recommended |
| Low | 1.5-3 | Mild | 2-3 years | Simple remedies sufficient |
| Very Low | 0-1.5 | Minimal | 1-2 years | Naturally reduces after 28 |

### Cancellations (Bhanga)
- Mars in own/exalted sign: 20% reduction
- Mars well-placed in D9 (house & sign): 25-40% reduction
- Jupiter/Venus in Kendra: 20-35% reduction
- **Total reduction capped at 90%**

### Manifestation Periods
- **Very Low/Low**: 18-30 years (reduces after 28-30)
- **Medium/High**: 22-40 years (partial reduction after 32-35)
- **Very High**: 25-45 years (remedies essential throughout)

### Categorized Remedies by Severity

**Base (all levels):**
- Recite Hanuman Chalisa daily
- Fast on Tuesdays
- Donate red lentils (masoor dal)

**Low/Medium:**
- Wear Red Coral gemstone (after astrological consultation)
- Perform Mangal Shanti Puja
- Lifestyle adjustments for anger management

**High/Very High:**
- Kumbh Vivah (symbolic marriage to Peepal tree)
- Mangal Maha Puja
- Pilgrimage to Ujjain Mangalnath temple
- Install Mangal Yantra
- Comprehensive marriage compatibility analysis essential

---

## 2. Kaal Sarpa Yoga (Serpent Enclosure)

### Detection Criteria
- All 7 planets (excluding Rahu/Ketu) hemmed between Rahu-Ketu axis
- **Full Kaal Sarpa**: 7/7 planets (intensity 10)
- **Strong Partial**: 6/7 planets (intensity 7)
- **Mild Partial**: 5/7 planets (intensity 5)
- Additional intensity modifiers:
  - Benefics hemmed: +30%
  - Luminaries hemmed: +20%

### 12 Classical Variations (by Rahu's house)

| Type | Rahu House | Deity | Negative Effects | Positive Transformation |
|------|-----------|-------|------------------|------------------------|
| **Ananta** | 1st | Ananta Naga | Self-confidence, health, identity issues | Spiritual growth after 42 |
| **Kulika** | 2nd | Kulika Naga | Family conflicts, wealth instability, speech | Communication excellence |
| **Vasuki** | 3rd | Vasuki Naga | Sibling conflicts, courage, communication | Writing/media success |
| **Shankhapala** | 4th | Shankhapala Naga | Property disputes, mother's health, emotions | Real estate success after 35 |
| **Padma** | 5th | Padma Naga | Children issues, intelligence blocks, speculation | Research/innovation abilities |
| **Mahapadma** | 6th | Mahapadma Naga | Health, enemies, debts, litigation | Healing professions, problem-solving |
| **Takshaka** | 7th | Takshaka Naga | Marriage delays, partnership problems | Relationship mastery, public relations |
| **Karkotak** | 8th | Karkotak Naga | Accidents, longevity, inheritance | Occult sciences, transformation |
| **Shankhachud** | 9th | Shankhachud Naga | Father issues, spiritual obstacles, education | Philosophical wisdom, teaching |
| **Ghatak** | 10th | Ghatak Naga | Career instability, authority conflicts | Major success after 42, leadership |
| **Vishdhar** | 11th | Vishdhar Naga | Income fluctuations, unfulfilled desires | Multiple income sources |
| **Sheshnag** | 12th | Sheshnag Naga | Excessive expenses, foreign issues, sleep | Spiritual liberation, moksha |

### Type-Specific Details
Each variation includes:
- Deity association (Naga king)
- Negative effects with life areas affected
- **Positive effects** (transformation abilities, eventual success)
- Manifestation periods with specific age ranges

### Cancellations
- Jupiter in Kendra: 30% reduction
- Venus in Kendra: 20% reduction
- Moon in own/exalted: 25% reduction
- Rahu in favorable signs: 15% reduction
- **Total capped at 85%**

### Categorized Remedies

**Base:**
- Kaal Sarpa Puja on Naga Panchami
- Rahu-Ketu mantras daily
- Serpent donations (silver/gold snake images)

**Low/Medium:**
- Install Kaal Sarpa Yantra
- Serpent worship at temples
- Lifestyle: Non-violence to reptiles

**High/Very High:**
- Specific type-based puja
- Pilgrimage to Trimbakeshwar, Kukke Subramanya, or Kalahasti
- Nagabali Puja
- Advanced mantras (125,000 Maha Mrityunjaya)
- Wear Gomedh (Hessonite) or Cat's Eye gemstones

---

## 3. Pitra Dosha (Ancestral Affliction)

### Detection Criteria - 11 Indicators with 3-tier weighting

**Primary Indicators (weight 3-4):**
- Sun-Rahu conjunction (4): Paternal lineage karma
- Moon-Ketu conjunction (4): Maternal lineage karma
- Rahu in 9th house (3): Ancestral blessing obstacles
- Ketu in 5th house (3): Progeny issues, past merit depletion

**Secondary Indicators (weight 2):**
- Saturn-Rahu conjunction (Shrapit Dosha): Ancestral curse
- Sun debilitated (Libra): Weak father figure
- Moon debilitated (Scorpio): Maternal affliction
- Jupiter debilitated (Capricorn): Reduced ancestral blessings

**Tertiary Indicators (weight 1):**
- Sun in 9th house
- Sun-Ketu conjunction
- Moon-Rahu conjunction
- Multiple planets with Rahu in 9th or Ketu in 5th

### Intensity Levels

| Level | Score | Significance | Remedy Requirement |
|-------|-------|--------------|-------------------|
| Very High | 8+ | Severe ancestral karma | Pind Daan at Gaya essential |
| High | 5-7 | Major ancestral debts | Comprehensive rituals required |
| Medium | 3-4 | Moderate affliction | Annual Shraddha necessary |
| Low | 1-2 | Mild indicators | Simple remedies sufficient |

### Categorized Effects

**Family Lineage:**
- Paternal/maternal relationship strains
- Family discord and conflicts

**Progeny:**
- Delays or difficulties with children
- Childlessness in severe cases

**Financial:**
- Sudden losses despite efforts
- Persistent debts and financial instability

**Health:**
- Mental peace disturbances
- Anxiety and restlessness

**Spiritual:**
- Obstacles in dharma (righteous path)
- Spiritual stagnation

### Manifestation Areas
- **Paternal lineage**: Sun/9th house indicators
- **Maternal lineage**: Moon indicators
- **Progeny issues**: 5th house/Jupiter indicators
- **Karmic debts**: Saturn/Shrapit indicators

### Categorized Remedies

**Base:**
- Feed crows daily (especially during Shraddha)
- Offer water to Peepal tree
- Perform Tarpan on Amavasya (new moon)
- Charity to Brahmins and needy

**Low/Medium:**
- Perform Shraddha during Pitru Paksha (annual fortnight)
- Spiritual practices (meditation, temple visits)
- Lifestyle: Respect elders and ancestors

**High/Very High:**
- **Pind Daan at Gaya (mandatory)**
- Tripindi Shraddha
- Narayan Bali ritual
- Pilgrimage to ancestral temples
- Advanced pujas by qualified priests
- Gemstones for afflicted planets
- Go Daan (cow donation)
- Kanya Daan (daughter's marriage support)
- Establish water facilities (wells, tanks)

---

## 4. Grahan Dosha (Eclipse Affliction)

### Detection Criteria - Degree-based intensity

Sun or Moon conjunct with Rahu or Ketu:
- **Very Close** (≤5°): Weight 4-5 (Moon-Rahu = 5, highest for mental health)
- **Close** (≤10°): Weight 3-4
- **Moderate** (≤15°): Weight 2-3
- **Wide** (>15°): Weight 1.5-2

### 4 Types of Eclipse Yogas

| Type | Conjunction | Primary Effects | Weight |
|------|------------|-----------------|--------|
| **Solar Eclipse** | Sun-Rahu | Father issues, ego/authority conflicts, health | 5 |
| **Sun-Ketu** | Sun-Ketu | Spiritual confusion, identity crisis, mystical inclinations | 4 |
| **Lunar Eclipse** | Moon-Rahu | Mental anxiety, mother issues, emotional instability, phobias | 5 (most serious for mental health) |
| **Moon-Ketu** | Moon-Ketu | Emotional detachment, meditation abilities, psychic sensitivity | 4 |

### Benefic Protection
- Jupiter in Kendra: 25% reduction
- Venus in Kendra: 15% reduction
- Sun in own/exalted (Aries/Leo): 20% reduction
- Moon in own/exalted (Cancer/Taurus): 20% reduction
- **Total capped at 70%**

### Categorized Effects

**Paternal (Sun afflictions):**
- Father relationship issues
- Authority conflicts
- Career obstacles

**Maternal (Moon afflictions):**
- Mother's health concerns
- Emotional dependency

**Mental/Emotional (Moon-Rahu):**
- Anxiety and obsessive thoughts
- Mood swings
- Sleep disturbances
- Phobias

**Spiritual (Ketu afflictions):**
- Spiritual confusion
- Mystical inclinations
- Psychic abilities

**Health:**
- **Sun afflictions**: Heart, bones
- **Moon afflictions**: Digestion, water retention

### Categorized Remedies (Luminary-specific)

**Base:**
- **Eclipse donations** (ESSENTIAL during actual eclipses)
- Avoid eating during eclipses
- Sun mantras: Aditya Hridayam, Gayatri
- Moon mantras: Chandra mantras
- Rahu/Ketu mantras daily

**Low/Medium:**
- Grahan Nivaran Puja
- Charity (luminary-specific):
  - Moon: Rice, ghee, white items
  - Sun: Wheat, jaggery, copper items
- Gemstones:
  - Sun: Ruby
  - Moon: Pearl
  - Rahu: Hessonite (Gomedh)
  - Ketu: Cat's Eye (Lehsunia)
- Meditation and mindfulness

**High/Very High:**
- Grahan Maha Puja
- Surya/Chandra Grahan Shanti rituals
- Pilgrimage:
  - Surya temples (Konark, Modhera)
  - Chandra temples
  - Trimbakeshwar
- Advanced mantras:
  - Aditya Hridayam (daily)
  - 18,000 Rahu/Ketu mantras
- Anna Daan (food donation)
- **Mental health support** (especially for Moon afflictions):
  - Professional meditation training
  - Psychiatric counseling if needed
  - Breathing exercises (Pranayama)
  - Anxiety management techniques

---

## Quick Reference Summary

| Dosha | Detection Time | Main Impact Areas | Essential Remedy |
|-------|---------------|-------------------|------------------|
| **Manglik** | ~5-10ms | Marriage, partnerships | Hanuman Chalisa, Mars remedies |
| **Kaal Sarpa** | ~10-15ms | Overall life obstacles, transformation | Kaal Sarpa Puja, Rahu-Ketu mantras |
| **Pitra** | ~5-10ms | Ancestors, progeny, family harmony | Pind Daan, Shraddha |
| **Grahan** | ~5-10ms | Mental health, parents, authority | Eclipse donations, luminary mantras |

## Code Reference

Service file: `backend/app/services/dosha_detection_service.py:1-1756`

Key methods:
- `detect_manglik_dosha()` - Mars affliction detection
- `detect_kaal_sarpa_yoga()` - Serpent enclosure detection
- `detect_pitra_dosha()` - Ancestral affliction detection
- `detect_grahan_dosha()` - Eclipse affliction detection
- Helper methods for remedies, cancellations, and intensity calculation

## Related Documentation
- `docs/YOGA_ENHANCEMENT.md` - Yoga detection system
- `docs/DIVISIONAL_CHARTS_ANALYSIS.md` - Divisional charts system
- `backend/tests/test_dosha_detection.py` - Test cases and examples
