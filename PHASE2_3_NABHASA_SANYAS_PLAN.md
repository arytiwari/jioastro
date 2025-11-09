# Phase 2 & 3: Nabhasa and Sanyas Yogas Implementation Plan

**Date**: November 9, 2025
**Current**: 78 yogas (51 original + 27 Nitya)
**Target**: 107 yogas (+22 Nabhasa + 7 Sanyas)

---

## Phase 2: Complete 32 Nabhasa Yogas

### Current State (10/32 implemented)

✅ **Ashraya Group (4/4)** - Based on sign types
1. Rajju Yoga - All in movable signs (Aries, Cancer, Libra, Capricorn)
2. Musala Yoga - All in fixed signs (Taurus, Leo, Scorpio, Aquarius)
3. Nala Yoga - All in dual signs (Gemini, Virgo, Sagittarius, Pisces)
4. Maala Yoga - Mixed across all three types

✅ **Dala Group (2/2)** - Based on benefic/malefic distribution
1. Mala Yoga - Benefics in kendras
2. Sarpa Yoga - Malefics in kendras

⚠️ **Akriti Group (4/20)** - Planetary patterns
Currently implemented:
1. Yuga Yoga - All in houses 1-4
2. Shola Yoga - All in houses 5-8
3. Gola Yoga - All in one sign
4. Dama Yoga - Planets in consecutive houses

**MISSING (16 Akriti yogas)**:
5. **Shakat Yoga** - All in 1st and 7th houses
6. **Hal Yoga** - All in other than kendra houses (not 1,4,7,10)
7. **Vajra Yoga** - All in 1st and 7th OR all benefics in kendras
8. **Yava Yoga** - All in 1st and 4th OR 1st and 10th
9. **Kamala/Padma Yoga** - All planets in kendras (1,4,7,10)
10. **Vaapi Yoga** - All planets in trikona (1,5,9) OR upachayas (3,6,10,11)
11. **Yupa Yoga** - All from Lagna to 4th house
12. **Ishwara Yoga** - All from Lagna to 7th house
13. **Shakti Yoga** - All in 7 consecutive signs
14. **Dand Yoga** - All in 6 consecutive signs (different from Dama)
15. **Naukaa Yoga** - All in 7 consecutive signs from kendra
16. **Koot Yoga** - All in 4th, 8th, and 12th houses (dusthanas)
17. **Chatra/Chhatra Yoga** - All planets from 10th house
18. **Chaap/Dhanu Yoga** - All in trikona houses (1,5,9)
19. **Ardha Chandra Yoga** - All in 7 houses from lagna
20. **Chakra Yoga** - All planets in kendra and trikona

❌ **Sankhya Group (0/3)** - Numerical patterns
1. **Vallaki Yoga** - Specific benefic/malefic patterns
2. **Daam Yoga** - Planets in 6th and 12th
3. **Paash Yoga** - Planets in upachayas

❌ **Other Variations (0/3)**
1. **Samudra Yoga** - All planets in 6 consecutive signs
2. **Veena Yoga** - Mixed pattern with benefics
3. **Shringataka Yoga** - Specific kendra pattern

---

## Phase 3: Sanyas Yogas (7 classical yogas)

Sanyas Yogas indicate renunciation, spiritual path, and detachment from material life.

### The 7 Classical Sanyas Yogas

1. **Maha Sanyas Yoga**
   - **Formation**: 4 or more planets in one sign/house
   - **Saturn involved**: Especially if Saturn is one of the planets
   - **Effects**: Strong renunciation, spiritual pursuits, monastic life

2. **Parivraja Yoga (Main)**
   - **Formation**: Ascendant lord with Saturn, aspected/conjunct by Jupiter
   - **Alternative**: Jupiter in kendra from Moon with Saturn
   - **Effects**: Wandering monk, pilgrimages, spiritual teacher

3. **Kev

ala Sanyas Yoga**
   - **Formation**: Moon in navamsa of Saturn, aspected by Saturn
   - **Alternative**: Exalted Saturn with Moon
   - **Effects**: Complete renunciation, hermit lifestyle

4. **Markandeya Sanyas Yoga**
   - **Formation**: Jupiter and Saturn in kendras, Moon in 9th/10th
   - **Effects**: Scholarly renunciation, teacher of scriptures

5. **Akhanda Sanyas Yoga**
   - **Formation**: Jupiter in 9th, Saturn in 8th, Rahu/Ketu in 4th
   - **Effects**: Continuous spiritual practice, mysticism

6. **Vyatipata Sanyas Yoga**
   - **Formation**: Saturn and Jupiter in mutual kendra with malefics
   - **Effects**: Late-life renunciation after worldly experiences

7. **Kalanala Sanyas Yoga**
   - **Formation**: 4+ planets in 10th house
   - **Ketu prominent**: Ketu in 10th with multiple planets
   - **Effects**: Fame through spirituality, religious leadership

### Modern Interpretation
In modern times, these yogas don't always mean literal monk status. They can indicate:
- Strong spiritual inclinations
- Careers in spirituality, yoga, meditation teaching
- Detachment while living in society
- Philosophical mindset
- Humanitarian work
- Teaching and guiding roles

---

## Implementation Strategy

### Part 1: Missing Akriti Nabhasa Yogas (16 yogas)

**Approach**: Extend `_detect_nabhasa_akriti_yogas()` method

**Pattern Recognition**:
- Consecutive houses: Dama (current), Shakti, Dand, Naukaa, Samudra
- Specific houses: Shakat (1&7), Yava (1&4 or 1&10), Koot (4,8,12)
- Kendra-based: Kamala (all kendras), Vajra (1&7 or all kendras)
- Trikona-based: Vaapi, Chaap
- Quadrant-based: Yuga (1-4), Shola (5-8), Yupa (1-4), Ishwara (1-7), Chatra (from 10th)
- Spread patterns: Ardha Chandra (7 houses), Chakra (kendra + trikona)

**Implementation**:
```python
def _detect_nabhasa_akriti_yogas(self, planets: Dict) -> List[Dict]:
    yogas = []
    main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    occupied_houses = sorted(list(set([...])))

    # Existing 4 yogas...

    # NEW: Shakat Yoga - all in 1st and 7th
    if set(occupied_houses) == {1, 7}:
        yogas.append({...})

    # NEW: Kamala Yoga - all in kendras
    if all(h in [1,4,7,10] for h in occupied_houses):
        yogas.append({...})

    # ... (continue for all 16)

    return yogas
```

### Part 2: Sankhya Nabhasa Yogas (3 yogas)

**Approach**: Create new method `_detect_nabhasa_sankhya_yogas()`

**Pattern**: Specific numerical distributions of benefics/malefics

### Part 3: Other Nabhasa Variations (3 yogas)

**Approach**: Add to existing Akriti or create separate method

### Part 4: Sanyas Yogas (7 yogas)

**Approach**: Create new method `_detect_sanyas_yogas()`

**Key Checks**:
- 4+ planet conjunctions
- Saturn-Jupiter combinations
- Ketu prominence
- Moon-Saturn aspects
- Specific house placements (9th, 10th, 4th, 8th)

---

## Testing Strategy

### Nabhasa Testing
Create synthetic charts with specific planetary distributions:
- All in kendra → Kamala Yoga
- All in 1 & 7 → Shakat Yoga
- 6 consecutive → Dand Yoga
- 7 consecutive → Shakti Yoga

### Sanyas Testing
Test cases:
- 4 planets in one house → Maha Sanyas
- Jupiter kendra from Moon + Saturn → Parivraja
- 4+ planets in 10th → Kalanala

---

## Expected Output

### After Phase 2
- **Total Nabhasa**: 32 (complete)
- **Total Yogas**: 100 (+22)

### After Phase 3
- **Total Sanyas**: 7
- **Total Yogas**: 107 (+7)

---

## Next Steps

1. ✅ Document all 22 Nabhasa yogas (this file)
2. ⏳ Implement 16 Akriti yogas
3. ⏳ Implement 3 Sankhya yogas
4. ⏳ Implement 3 other Nabhasa variations
5. ⏳ Test all 22 Nabhasa yogas
6. ⏳ Implement 7 Sanyas yogas
7. ⏳ Test all 7 Sanyas yogas
8. ⏳ Update documentation

**Estimated Time**: 6-8 hours total
**Target Date**: November 9-10, 2025

---

## Classical References

### Nabhasa Yogas
- **BPHS**: Chapter on Nabhasa Yogas
- **Phaladeepika**: Effects of each Nabhasa yoga
- **Jataka Parijata**: Classification and manifestations

### Sanyas Yogas
- **BPHS**: Chapter on Sanyas Yogas
- **Phaladeepika**: Conditions for renunciation
- **Brihat Jataka**: Planetary combinations for spiritual life
- **Uttara Kalamrita**: Modern interpretations

---

**Status**: Research complete, ready for implementation
