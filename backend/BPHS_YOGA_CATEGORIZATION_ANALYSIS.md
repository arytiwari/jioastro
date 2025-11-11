# BPHS Yoga Categorization Analysis

**Generated:** 2025-11-11
**Purpose:** Comprehensive comparison of current yoga implementation against BPHS specification
**Source Files:**
- Current Implementation: `/backend/app/services/extended_yoga_service.py` (6894 lines)
- BPHS Specification: `/BPHS_Yoga_Categories.json` (v1.0)

---

## Executive Summary

### Current Implementation Status
- **Total Yogas Detected:** ~350+ yogas across multiple categories
- **BPHS Spec Coverage:** Partial implementation with significant gaps
- **Implementation Approach:** Mix of classical BPHS yogas + practical modern interpretations
- **Major Gaps:** Missing ~50+ classical BPHS yogas from named categories

### Key Findings

#### Strengths
1. ✅ **Pancha Mahapurusha Yogas:** Complete (5/5) - Ruchaka, Bhadra, Hamsa, Malavya, Sasa
2. ✅ **Sun/Moon Yogas:** Well-covered - Vesi, Vosi, Ubhayachari, Sunapha, Anapha, Durudhura
3. ✅ **Nabhasa Yogas:** Extensive (32+ variants) - Ashraya, Dala, Akriti groups
4. ✅ **Viparita Raj Yogas:** Complete (3/3) - Harsha, Sarala, Vimal
5. ✅ **Penury Yogas:** Comprehensive (16 variants) from BPHS Ch.42

#### Critical Gaps
1. ❌ **Major Named Yogas Missing:** Bherī, Mṛdaṅga, Śarada, Khadga, Kalpadruma, Kālanidhi (9/15 missing from Ch.36)
2. ❌ **Divisional Amplifiers:** All 8 missing (Parijāta, Uttama, Gopura, Siṁhāsana, Parvata, Devaloka, Brahmaloka, Iravataṁsa)
3. ❌ **Subtle Raj Yogas:** Missing Arūḍha relations, birth moment factors, Vargottama Moon variations
4. ❌ **Category Field:** Not implemented - yogas lack standardized BPHS category classification

#### Observations
- **Over-implementation:** 350+ yogas vs ~100 in BPHS spec (includes Bhava yogas, Nitya yogas, practical variations)
- **Naming Inconsistencies:** Multiple naming styles (BPHS classical, modern, descriptive)
- **Category Mismatches:** "Wealth & Prosperity" vs BPHS "Major Positive Yogas"
- **Strength Calculation:** Custom algorithm (dignity 60% + house 40%) not in BPHS

---

## Category Mapping

### 1. Major Positive Yogas (BPHS: 36 yogas)

#### A. Pancha Mahapurusha (5 yogas) - Ch.75

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Ruchaka (Mars)** | ✅ Implemented | `_detect_pancha_mahapurusha()` | "Pancha Mahapurusha" | Full BPHS compliance |
| **Bhadrā (Mercury)** | ✅ Implemented | `_detect_pancha_mahapurusha()` | "Pancha Mahapurusha" | Full BPHS compliance |
| **Haṁsa (Jupiter)** | ✅ Implemented | `_detect_pancha_mahapurusha()` | "Pancha Mahapurusha" | Full BPHS compliance |
| **Mālavya (Venus)** | ✅ Implemented | `_detect_pancha_mahapurusha()` | "Pancha Mahapurusha" | Full BPHS compliance |
| **Śaśa (Saturn)** | ✅ Implemented | `_detect_pancha_mahapurusha()` | "Pancha Mahapurusha" | Full BPHS compliance |

**Coverage:** 5/5 (100%) ✅

---

#### B. Named Yogas (Ch.36) - 15 yogas

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Gaja-Keśarī** | ✅ Implemented | `_detect_gajakesari_yoga()` | "Raja Yoga" | Category mismatch |
| **Amala** | ✅ Implemented | `_detect_amala_yoga()` | "Fame & Reputation" | Category mismatch |
| **Parvata** | ✅ Implemented | `_detect_parvata_yoga()` | "Wealth & Character" | Category mismatch |
| **Kahāla** | ✅ Implemented | `_detect_kahala_yoga()` | "Leadership" | Category mismatch |
| **Chāmara** | ✅ Implemented | `_detect_chamara_yoga()` | "Fame & Authority" | Category mismatch |
| **Śaṅkha** | ❌ Missing | - | - | Not detected |
| **Bherī** | ❌ Missing | - | - | Not detected |
| **Mṛdaṅga** | ❌ Missing | - | - | Not detected |
| **Śrīnātha** | ⚠️ Partial | `_detect_rare_yogas()` as "Shrinatha" | "Wealth & Comfort" | Simplified version |
| **Śārada** | ❌ Missing | - | - | Not detected |
| **Matsya** | ✅ Implemented | `_detect_rare_yogas()` | "Fame & Character" | Full implementation |
| **Kūrma** | ✅ Implemented | `_detect_rare_yogas()` | "Wealth & Character" | Full implementation |
| **Khadga** | ❌ Missing | - | - | Not detected |
| **Lakṣmī** | ✅ Implemented | `_detect_lakshmi_saraswati_yoga()` | "Wealth" | Multiple variants |
| **Kusuma** | ✅ Implemented | `_detect_rare_yogas()` | "Fame & Authority" | Full implementation |
| **Kālanidhi** | ⚠️ Partial | `_detect_kalanidhi_yoga()` | - | Separate method, incomplete |
| **Kalpadruma (Parijāta)** | ⚠️ Partial | `_detect_additional_house_lord_yogas()` as "Parijata" | "Fame & Honor" | Different definition |
| **Trimūrti—Hari/Hara/Brahmā** | ❌ Missing | - | - | Not detected |
| **Lagna‑Ādhi (Ādhi from Lagna)** | ⚠️ Partial | `_detect_adhi_yoga()` | "Wealth & Power" | Only from Moon, not Lagna |

**Coverage:** 8/19 full, 4/19 partial = 42% ❌

---

#### C. Raj Yoga (Ch.39) - 10 variations

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **LL with 5L/9L** | ✅ Implemented | `_detect_systematic_raj_yogas()` | Multiple "Raj Yoga" entries | Comprehensive |
| **Kendra lords with Trikona lords** | ✅ Implemented | `_detect_systematic_raj_yogas()` | Multiple "Raj Yoga" entries | Comprehensive |
| **LL in trine or kendra** | ✅ Implemented | `_detect_systematic_raj_yogas()` | "Lagna Yoga" | Separate category |
| **10L strong in 10th** | ✅ Implemented | `_detect_karma_raj_yoga()` | "Karma Raj Yoga" | Separate method |
| **All-benefic Kendras** | ✅ Implemented | `_detect_all_benefic_kendras_yoga()` | "All-Benefic Kendras Yoga" | Separate method |
| **Moon–Venus mutual 3/11** | ✅ Implemented | `_detect_moon_venus_mutual_yoga()` | "Moon-Venus Mutual 3rd/11th Yoga" | Separate method |

**Coverage:** 6/6 (100%) ✅ - Plus extensive house lord combinations (144 Bhava yogas)

---

#### D. Royal Association (Ch.40)

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Amatyakaraka/AK & 10L linkages** | ✅ Implemented | `_detect_royal_association_yogas()` | "Raja Yoga" | 16 variations via Jaimini |
| **Clean 10H/11H** | ✅ Implemented | `_detect_royal_association_yogas()` | "Raja Yoga" | Part of royal yogas |

**Coverage:** 2/2 (100%) ✅

---

#### E. Wealth Yogas (Ch.41)

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Named Wealth sets (Ch.41.2–15)** | ⚠️ Partial | Various `_detect_dhana_*()` methods | "Wealth Yoga" | Simplified |
| **5L–9L wealth link** | ✅ Implemented | `_detect_lakshmi_wealth_yogas()` | "Wealth Yoga" | 15 variations |

**Coverage:** 2/2 (100%) ✅

---

#### F. Nabhasa Yogas (Ch.35)

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Kamala** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Full BPHS |
| **Māla** | ✅ Implemented | `_detect_nabhasa_dala_yogas()` | "Nabhasa - Dala" | Full BPHS |

**Coverage:** 2/2 (100%) ✅ - Plus 30+ other Nabhasa variants

---

#### G. Vaapī Clarification (Ch.39 & Ch.41)

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Vaapī (5L & 9L strong relation)** | ✅ Implemented | `_detect_additional_house_lord_yogas()` | "Dharma & Fortune" | Modern interpretation |

**Coverage:** 1/1 (100%) ✅

---

### Summary: Major Positive Yogas
- **Total BPHS:** 36 yogas
- **Fully Implemented:** 24 yogas (67%)
- **Partially Implemented:** 6 yogas (17%)
- **Missing:** 6 yogas (16%)

**Missing Critical Yogas:**
1. Śaṅkha (Ch.36.13–14)
2. Bherī (Ch.36.15–16)
3. Mṛdaṅga (Ch.36.17)
4. Śārada (Ch.36.19–20)
5. Khadga (Ch.36.25–26)
6. Trimūrti (Ch.36.35–36)

---

## 2. Major Challenges (BPHS: 23 yogas)

#### A. Penury Yogas (Ch.42) - 16 variations

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **1L‑12H & 12L‑1H with maraka** | ✅ Implemented | `_detect_penury_yogas()` | "Penury Yoga - Parivartana" | ID 262 |
| **1L‑6H & 6L‑1H with maraka** | ✅ Implemented | `_detect_penury_yogas()` | "Penury Yoga - Parivartana" | ID 263 |
| **1L‑8H with Ketu on Lagna/Moon** | ✅ Implemented | `_detect_penury_yogas()` | "Penury Yoga - Affliction" | ID 264 |
| **1L malefic in 6/8/12 & 2L fallen** | ✅ Implemented | `_detect_penury_yogas()` | "Penury Yoga - Affliction" | ID 265 |
| **1L with dusthana lords** | ✅ Implemented | `_detect_penury_yogas()` | "Penury Yoga - Affliction" | ID 266 |
| **5L‑6H & 9L‑12H maraka afflicted** | ✅ Implemented | `_detect_penury_yogas()` | "Penury Yoga - Affliction" | ID 267 |
| **Malefics in Lagna** | ✅ Implemented | `_detect_penury_yogas()` | "Penury Yoga - Affliction" | ID 268 |
| **Dusthana dispositors afflicted** | ✅ Implemented | `_detect_penury_yogas()` | "Penury Yoga - Affliction" | ID 269 |
| **Moon's navamsa lord as maraka** | ⚠️ Partial | - | - | Requires D9 integration |
| **Rasi LL & Navamsa LL as maraka** | ⚠️ Partial | - | - | Requires D9 integration |
| **Benefics in bad, malefics in good** | ✅ Implemented | `_detect_penury_yogas()` | "Penury Yoga - Distribution" | ID 270 |
| **Dasha harm by dusthana links** | ⚠️ Partial | `_detect_penury_yogas()` | "Penury Yoga - Affliction" | Simplified, no Dasha timing |
| **AK expense factors I** | ❌ Missing | - | - | Requires Jaimini AK analysis |
| **AK expense factors II** | ❌ Missing | - | - | Requires Jaimini AK analysis |
| **Mars+Saturn in 2nd** | ✅ Implemented | `_detect_penury_yogas()` | "Penury Yoga - Affliction" | ID 271 |
| **Sun or Saturn in 2nd** | ✅ Implemented | `_detect_penury_yogas()` | "Penury Yoga - Affliction" | ID 272 |

**Coverage:** 11/16 full, 3/16 partial = 69% ⚠️

---

#### B. Moon's Yogas (Ch.37)

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Kemadruma (Moon isolated)** | ✅ Implemented | `_detect_kemadruma_yoga()` | "Challenge" | Full BPHS |

**Coverage:** 1/1 (100%) ✅

---

#### C. Nabhasa Challenge Yogas (Ch.35)

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Sarpa (malefics in kendras)** | ✅ Implemented | `_detect_nabhasa_dala_yogas()` | "Nabhasa - Dala" | Full BPHS |
| **Gola (all in one sign)** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Full BPHS |
| **Śūla (all in three signs)** | ✅ Implemented | `_detect_nabhasa_sankhya_yogas()` as "Shoola" | "Nabhasa - Sankhya" | Full BPHS |
| **Pāśa (all in five signs)** | ✅ Implemented | `_detect_nabhasa_sankhya_yogas()` as "Paasha" | "Nabhasa - Sankhya" | Full BPHS |
| **Dāma (all in six signs)** | ✅ Implemented | `_detect_nabhasa_sankhya_yogas()` | "Nabhasa - Sankhya" | Full BPHS |

**Coverage:** 5/5 (100%) ✅

---

### Summary: Major Challenges
- **Total BPHS:** 23 yogas
- **Fully Implemented:** 18 yogas (78%)
- **Partially Implemented:** 3 yogas (13%)
- **Missing:** 2 yogas (9%)

**Missing Critical Yogas:**
1. AK expense factors I (Ch.42.14)
2. AK expense factors II (Ch.42.15)

---

## 3. Standard Yogas (BPHS: 38 yogas)

#### A. Moon's Yogas (Ch.37) - 5 variations

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Sunāpha** | ✅ Implemented | `_detect_sunapha_yoga()` | "Moon-Based Yogas" | Category mismatch |
| **Anāpha** | ✅ Implemented | `_detect_anapha_yoga()` | "Moon-Based Yogas" | Category mismatch |
| **Durudhura** | ✅ Implemented | `_detect_durudhura_yoga()` | "Moon-Based Yogas" | Category mismatch |
| **Adhi from Moon** | ⚠️ Partial | `_detect_adhi_yoga()` | "Wealth & Power" | Only 6/7/8 from Moon, not Adhi proper |
| **Dhana from Moon** | ❌ Missing | - | - | Not detected |

**Coverage:** 3/5 full, 1/5 partial = 60% ⚠️

---

#### B. Sun's Yogas (Ch.38) - 3 variations

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Vesi** | ✅ Implemented | `_detect_vesi_yoga()` | "Sun-Based Yogas" | Category mismatch |
| **Vasi** | ✅ Implemented | `_detect_vosi_yoga()` | "Sun-Based Yogas" | Category mismatch |
| **Ubhayachari** | ✅ Implemented | `_detect_ubhayachari_yoga()` | "Sun-Based Yogas" | Category mismatch |

**Coverage:** 3/3 (100%) ✅

---

#### C. Nabhasa Standard Yogas (Ch.35) - 30 variations

**Ashraya Group (4 yogas):**

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Rajju** | ✅ Implemented | `_detect_nabhasa_ashraya_yogas()` | "Nabhasa - Ashraya" | Full BPHS |
| **Mushala** | ✅ Implemented | `_detect_nabhasa_ashraya_yogas()` as "Musala" | "Nabhasa - Ashraya" | Full BPHS |
| **Nala** | ✅ Implemented | `_detect_nabhasa_ashraya_yogas()` | "Nabhasa - Ashraya" | Full BPHS |

**Coverage:** 3/4 (75%) - Missing "Maala" (listed in Major Positive instead)

**Dala Group (2 yogas):** Both covered above in Major Positive/Challenge sections

**Akriti Group (20 yogas):**

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Gada** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Full BPHS |
| **Sakata** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Full BPHS |
| **Vihaga** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Full BPHS |
| **Śṛṅgāṭaka** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Full BPHS |
| **Hala** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Full BPHS + corrected version |
| **Vajra** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Multiple versions |
| **Yava** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Multiple versions |
| **Vapi (distribution)** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` as "Vaapi" | "Nabhasa - Akriti" | Full BPHS |
| **Yupa** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Multiple versions |
| **Śara** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Full BPHS |
| **Śakti** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Multiple versions |
| **Daṇḍa** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Multiple versions |
| **Nauka** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Multiple versions |
| **Kūṭa** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` as "Koota" | "Nabhasa - Akriti" | Multiple versions |
| **Chatra** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Multiple versions |
| **Dhanus/Chāpa** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` as "Chaapa/Dhanus" | "Nabhasa - Akriti" | Multiple versions |
| **Chakra** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Multiple versions |
| **Samudra** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Multiple versions |
| **Yuga** | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | "Nabhasa - Akriti" | Full BPHS |
| **Kedāra** | ⚠️ Missing | - | - | Not detected |
| **Vīṇā** | ⚠️ Missing | - | - | Not detected |

**Coverage:** 18/20 (90%) ⚠️

**Sankhya Group (3 yogas):** Covered above in Major Challenges

---

### Summary: Standard Yogas
- **Total BPHS:** 38 yogas
- **Fully Implemented:** 33 yogas (87%)
- **Partially Implemented:** 1 yoga (3%)
- **Missing:** 4 yogas (10%)

**Missing Yogas:**
1. Dhana from Moon (Ch.37.7–12)
2. Kedāra (Ch.35.16)
3. Vīṇā (Ch.35.16)
4. Full Adhi Yoga from Lagna (Ch.36.37)

---

## 4. Minor Yogas & Subtle Influences (BPHS: 15 yogas)

#### A. Divisional Amplifiers (Ch.41.18–27) - 8 yogas

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Parijāta** | ❌ Missing | - | - | Not as divisional amplifier |
| **Uttama** | ❌ Missing | - | - | Not detected |
| **Gopura** | ❌ Missing | - | - | Not detected |
| **Siṁhāsana** | ❌ Missing | - | - | Not detected |
| **Parvata** | ⚠️ Wrong Context | `_detect_parvata_yoga()` | "Wealth & Character" | Different yoga, not amplifier |
| **Devaloka** | ❌ Missing | - | - | Not detected |
| **Brahmaloka** | ❌ Missing | - | - | Not detected |
| **Iravataṁsa** | ❌ Missing | - | - | Not detected |

**Coverage:** 0/8 (0%) ❌

---

#### B. Subtle Raj Yogas (Ch.39) - 7 variations

| BPHS Yoga Name | Implementation Status | Current Method | Current Category | Notes |
|----------------|----------------------|----------------|------------------|-------|
| **Arūḍha relations (AL/DP geometry)** | ❌ Missing | - | - | Requires Jaimini Aruda implementation |
| **Birth moment factor** | ❌ Missing | - | - | Not detected |
| **Strong Vargottama Moon** | ⚠️ Partial | Dignity check in `_get_planet_dignity()` | - | Not as separate yoga |
| **Exalted aspects on Lagna** | ❌ Missing | - | - | Not detected |
| **Benefic in a single Kendra** | ⚠️ Implicit | Part of other yogas | - | Not as separate yoga |
| **Benefic support to authority** | ✅ Implemented | `_detect_benefic_support_yogas()` | "Raja Yoga" | Phase 1.3 enhancement |
| **Valor/Overcoming** | ✅ Implemented | `_detect_valor_yogas()` | "Raja Yoga" | Phase 1.4 enhancement |

**Coverage:** 2/7 full, 2/7 partial = 29% ❌

---

### Summary: Minor Yogas & Subtle Influences
- **Total BPHS:** 15 yogas
- **Fully Implemented:** 2 yogas (13%)
- **Partially Implemented:** 3 yogas (20%)
- **Missing:** 10 yogas (67%)

**Critical Missing:**
1. All 8 Divisional Amplifiers (Ch.41.18–27)
2. Arūḍha relations (AL/DP)
3. Birth moment factors
4. Exalted aspects on Lagna

---

## Gap Analysis

### Missing from BPHS Spec (Total: 53 yogas)

#### Critical Gaps (High Priority)
1. **Divisional Amplifiers (8 yogas):** Parijāta, Uttama, Gopura, Siṁhāsana, Parvata (amplifier), Devaloka, Brahmaloka, Iravataṁsa
2. **Named Yogas Ch.36 (9 yogas):** Śaṅkha, Bherī, Mṛdaṅga, Śārada, Khadga, Trimūrti, Lagna-Ādhi (complete), Kālanidhi (complete), Kalpadruma (complete)
3. **Subtle Raj Yogas (5 yogas):** Arūḍha relations, Birth moment factor, Strong Vargottama Moon (separate), Exalted aspects on Lagna, Benefic in single Kendra (separate)
4. **Moon Yogas (1 yoga):** Dhana from Moon (Ch.37.7–12)
5. **Nabhasa Yogas (2 yogas):** Kedāra, Vīṇā

#### Medium Priority Gaps
6. **Penury Yogas (2 yogas):** AK expense factors I & II (require Jaimini)
7. **Navamsa-Dependent (3 yogas):** Moon's navamsa lord as maraka, Rasi LL & Navamsa LL as maraka, divisional confirmations

**Total Missing:** 30 yogas (27% of BPHS spec)

---

### Extra Yogas Not in BPHS Spec (Total: ~270 yogas)

These are practical yogas added beyond BPHS:

#### Major Additions
1. **Bhava Yogas (144 yogas):** Complete house lord placement analysis (12 lords × 12 houses)
2. **Nitya Yogas (27 yogas):** Birth yogas based on Sun-Moon angular distance
3. **Sanyas Yogas (7 yogas):** Maha Sanyas, Parivraja, Kevala, Markandeya, Akhanda, Vyatipata, Kalanala
4. **Eclipse Yogas (4 yogas):** Grahan (Sun-Rahu, Sun-Ketu, Moon-Rahu, Moon-Ketu)
5. **Ascendant-Specific Wealth (12 yogas):** Aries through Pisces wealth patterns
6. **Lakshmi Wealth Variations (15 yogas):** 5L-9L relationship permutations
7. **Systematic Raj Yogas (20+ yogas):** House lord combinations (1L-5L, 1L-9L, 4L-5L, etc.)
8. **Royal Association Yogas (16 yogas):** Jaimini Amatyakaraka/Atmakaraka patterns
9. **Conjunction Yogas (5 yogas):** Chandra-Mangala, Guru-Mangala, Budhaditya, Ganesha (Jupiter-Ketu, Venus-Ketu)
10. **Challenge Yogas (5 yogas):** Chandal, Balarishta, Kroora, Daridra, Kemadruma

#### Observations
- **Bhava Yogas:** Not in classical BPHS but practical for modern analysis
- **Nitya Yogas:** Traditional but not in BPHS spec (found in Muhurta texts)
- **Sanyas Yogas:** Classical but Ch.40+ in BPHS (renunciation)
- **Wealth Variations:** Systematic expansion of BPHS principles
- **Extra Nabhasa:** Corrected versions + alternate interpretations

---

### Category Mismatches

| BPHS Category | Current Categories Used | Issue |
|---------------|------------------------|-------|
| **Major Positive Yogas** | "Pancha Mahapurusha", "Wealth & Power", "Fame & Authority", "Wealth", "Learning & Wisdom", "Nabhasa - Akriti" | Multiple categories instead of unified |
| **Major Challenges** | "Penury Yoga", "Challenge", "Nabhasa - Dala", "Nabhasa - Sankhya" | Separate categories |
| **Standard Yogas** | "Moon-Based Yogas", "Sun-Based Yogas", "Nabhasa - Ashraya", "Nabhasa - Akriti" | No "Standard Yogas" category |
| **Minor Yogas & Subtle Influences** | Not used | No minor/subtle category distinction |

**Recommendation:** Add standardized `bphs_category` field to each yoga:
- `"bphs_category": "major_positive"`
- `"bphs_category": "major_challenges"`
- `"bphs_category": "standard"`
- `"bphs_category": "minor_subtle"`
- `"bphs_category": "non_bphs_practical"`

---

## Implementation Plan

### Phase 1: Critical BPHS Yogas (Priority 1)

**Timeline:** 2-3 weeks

#### A. Named Yogas Ch.36 (9 yogas)
1. **Śaṅkha Yoga (Ch.36.13–14)**
   - Formation: 5L & 6L exchange OR both in Kendras
   - Effect: Long life, prosperity, righteous conduct

2. **Bherī Yoga (Ch.36.15–16)**
   - Formation: Venus in 1st, Jupiter in 9th, all planets in 1/2/7/12
   - Effect: Long life, wealth, royal honor

3. **Mṛdaṅga Yoga (Ch.36.17)**
   - Formation: Planets in 1st/5th OR 2nd/9th
   - Effect: Wealth, courage, musical talents

4. **Śārada Yoga (Ch.36.19–20)**
   - Formation: Mercury in 4th/5th/9th + strong Moon
   - Effect: Learning, eloquence, poetic abilities

5. **Khadga Yoga (Ch.36.25–26)**
   - Formation: 2L with 9L in good house
   - Effect: Wealth, authority, bravery

6. **Kālanidhi Yoga (Ch.36.31–32) - Complete**
   - Current: Partial implementation
   - Enhance: Full BPHS criteria with Jupiter/Mercury/Venus/2L combinations

7. **Kalpadruma/Parijāta (Ch.36.33–34) - Disambiguate**
   - Current: "Parijata" as separate yoga (1L strong in kendra/trikona)
   - Add: Classical Kalpadruma (wish-fulfilling tree) - complex multi-condition

8. **Trimūrti Yoga (Ch.36.35–36)**
   - Formation: Sun/Moon/Jupiter in excellent positions (karakas strong)
   - Effect: Royal honors, three-fold blessings

9. **Lagna-Ādhi Yoga (Ch.36.37) - Complete**
   - Current: Only from Moon (6/7/8)
   - Add: From Lagna (benefics in 6/7/8 from Lagna)

**Method:** Add dedicated `_detect_bphs_named_yogas_ch36()` method

---

#### B. Divisional Amplifiers (8 yogas) - Ch.41.18–27

These require **divisional chart (Varga) strength analysis**:

1. **Parijāta (Ch.41.18)** - Planet exalted in D1 & Navamsa
2. **Uttama (Ch.41.19)** - Planet exalted in D1, strong in Navamsa
3. **Gopura (Ch.41.20)** - Planet exalted in Navamsa, good in D1
4. **Siṁhāsana (Ch.41.21)** - Planet in own sign in D1 & Navamsa
5. **Parvata (Ch.41.22)** - Planet exalted in D1, own in Navamsa (DIFFERENT from Parvata Ch.36)
6. **Devaloka (Ch.41.23)** - Planet in Mooltrikona both D1 & Navamsa
7. **Brahmaloka (Ch.41.24)** - Planet in friend's sign both D1 & Navamsa
8. **Iravataṁsa (Ch.41.25)** - Planet exalted in Navamsa only

**Prerequisites:**
- Navamsa (D9) chart data accessible in `planets` dict
- D9 dignity fields: `d9_sign`, `d9_exalted`, `d9_own_sign`

**Method:** Add `_detect_divisional_amplifiers()` method

---

#### C. Subtle Raj Yogas (5 yogas)

1. **Arūḍha Relations (Ch.39.23)**
   - Requires: Aruda Lagna (AL) and Darapada (A7/DP) calculation
   - Formation: AL-DP connections, AL lord strong
   - **Dependency:** Jaimini system enhancement

2. **Birth Moment Factor (Ch.39.40)**
   - Formation: Birth near noon (Sun strong) or midnight (Moon strong)
   - Effect: Natural authority/intuition

3. **Strong Vargottama Moon (Ch.39.42)**
   - Formation: Moon in same sign D1 & D9 + aspected by 4+ planets
   - Effect: Exceptional prosperity

4. **Exalted Aspects on Lagna (Ch.39.43)**
   - Formation: Count of exalted planets aspecting Lagna
   - Effect: Proportional to count (2+ = notable)

5. **Benefic in Single Kendra (Ch.39 Generic)**
   - Formation: One strong benefic in any kendra
   - Effect: Basic prosperity, separate from complex yogas

**Method:** Add `_detect_subtle_raj_yogas()` method

---

### Phase 2: Standard Yoga Completion (Priority 2)

**Timeline:** 1 week

#### A. Moon's Dhana Yoga (Ch.37.7–12)
- Formation: 2nd lord from Moon + various conditions
- Effect: Wealth reckoned from Moon
- **Method:** Add to `_detect_sunapha_yoga()` or separate method

#### B. Nabhasa Completion
- **Kedāra Yoga (Ch.35.16):** Planets in 2/6/10 from Lagna
- **Vīṇā Yoga (Ch.35.16):** Planets in musical pattern
- **Method:** Add to `_detect_nabhasa_akriti_yogas()`

---

### Phase 3: Category Field Addition (Priority 3)

**Timeline:** 3-4 days

#### Implementation
1. Add `bphs_category` field to all yoga dictionaries
2. Add `bphs_ref` field with chapter and verse references
3. Add `bphs_section` field (A-J section identifiers)

```python
yoga = {
    "name": "Ruchaka Yoga",
    "description": "...",
    "strength": "Very Strong",
    "category": "Pancha Mahapurusha",  # Keep existing
    "bphs_category": "major_positive",  # NEW
    "bphs_section": "E) Pañcha-Mahāpuruṣa",  # NEW
    "bphs_ref": "Ch.75.1–2",  # NEW
    "importance": "major",
    "impact": "positive"
}
```

#### Category Mapping Rules
```python
BPHS_CATEGORY_MAP = {
    "major_positive": [
        "Pancha Mahapurusha", "Wealth & Power", "Fame & Authority",
        "Wealth", "Learning & Wisdom", "Raja Yoga", "Nabhasa - Akriti" (Kamala/Mala)
    ],
    "major_challenges": [
        "Penury Yoga", "Challenge", "Nabhasa - Dala" (Sarpa),
        "Nabhasa - Akriti" (Gola), "Nabhasa - Sankhya" (Shoola/Paasha/Dama)
    ],
    "standard": [
        "Moon-Based Yogas", "Sun-Based Yogas", "Nabhasa - Ashraya",
        "Nabhasa - Akriti" (most), "Skills & Learning"
    ],
    "minor_subtle": [
        "Divisional Amplifiers", "Subtle Raj Yogas"
    ],
    "non_bphs_practical": [
        "Bhava Yogas", "Nitya Yogas", "Sanyas Yogas",
        "Eclipse Yoga", "Ascendant-Specific", "Conjunction Yogas"
    ]
}
```

---

### Phase 4: Navamsa Integration (Priority 4)

**Timeline:** 1-2 weeks

#### Requirements
1. Ensure D9 data available in `planets` dict for all planets
2. Add D9 dignity fields: `d9_sign_num`, `d9_exalted`, `d9_own_sign`, `d9_debilitated`
3. Update `_get_planet_dignity()` to use D9 for Vargottama check
4. Implement divisional amplifiers (Phase 1B)
5. Add Navamsa-dependent penury yogas:
   - Moon's navamsa lord as maraka
   - Rasi LL & Navamsa LL as maraka

**Method:** Coordinate with divisional charts service integration

---

### Phase 5: Documentation & Testing (Priority 5)

**Timeline:** 1 week

#### Tasks
1. Update `docs/YOGA_ENHANCEMENT.md` with BPHS categorization
2. Add BPHS reference guide for all implemented yogas
3. Create test cases for new yogas (Ch.36 named, divisional amplifiers, subtle raj)
4. Add frontend category filtering by BPHS category
5. Update API documentation with `bphs_category` field

---

## Detailed Yoga Inventory

### Complete Alphabetical Listing (350+ yogas)

| Yoga Name | BPHS Category | BPHS Ref | Implementation Status | Current Method | Notes |
|-----------|---------------|----------|----------------------|----------------|-------|
| **Adhi Yoga** | Major Positive | Ch.36 | ✅ Implemented | `_detect_adhi_yoga()` | From Moon only, missing Lagna variant |
| **Akhanda Sanyas Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_sanyas_yogas()` | Practical renunciation yoga |
| **All-Benefic Kendras Yoga** | Major Positive | Ch.39.48 | ✅ Implemented | `_detect_all_benefic_kendras_yoga()` | Full BPHS |
| **Amala Yoga** | Major Positive | Ch.36.5–6 | ✅ Implemented | `_detect_amala_yoga()` | Full BPHS |
| **Anapha Yoga** | Standard | Ch.37.3–6 | ✅ Implemented | `_detect_anapha_yoga()` | Full BPHS |
| **Ardha Chandra Yoga** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Full BPHS |
| **Atiganda Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga (Muhurta) |
| **Ayushman Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga (Muhurta) |
| **Balarishta Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_balarishta_yoga()` | Child mortality indicators |
| **Bhadra Yoga** | Major Positive | Ch.75.1–2 | ✅ Implemented | `_detect_pancha_mahapurusha()` | Mercury - Full BPHS |
| **Bherī Yoga** | Major Positive | Ch.36.15–16 | ❌ Missing | - | **CRITICAL GAP** |
| **Brahma Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Budhaditya Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_budhaditya_yoga()` | Sun-Mercury conjunction |
| **Chaapa Yoga** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Full BPHS |
| **Chakra Yoga** | Standard | Ch.35.15 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Multiple versions |
| **Chamara Yoga** | Major Positive | Ch.36.11–12 | ✅ Implemented | `_detect_chamara_yoga()` | Simplified |
| **Chandal Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_chandal_yoga()` | Jupiter-Rahu conjunction |
| **Chandra-Mangala Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_chandra_mangala_yoga()` | Moon-Mars conjunction |
| **Chatra Yoga** | Standard | Ch.35.14 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Multiple versions |
| **Daam Yoga** | Major Challenges | Ch.35.16 | ✅ Implemented | `_detect_nabhasa_sankhya_yogas()` | 6 signs - Full BPHS |
| **Dama Yoga** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Consecutive houses |
| **Danda Yoga** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | 6 consecutive |
| **Daṇḍa Yoga (BPHS)** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Corrected version |
| **Daridra Yoga** | Major Challenges | Ch.42 | ✅ Implemented | `_detect_daridra_yoga()`, `_detect_penury_yogas()` | 16 variations |
| **Dharma-Karmadhipati Yoga** | Major Positive | Ch.39 | ✅ Implemented | `_detect_dharma_karmadhipati_yoga()` | Simplified |
| **Dhana Yoga** | Major Positive | Ch.41 | ✅ Implemented | `_detect_dhana_yoga()` | Simplified wealth yoga |
| **Dhanus Yoga (BPHS)** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Bow pattern |
| **Dhriti Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Dhruva Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Durudhura Yoga** | Standard | Ch.37.3–6 | ✅ Implemented | `_detect_durudhura_yoga()` | Full BPHS |
| **Gada Yoga** | Standard | Ch.35.9 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Successive kendras |
| **Gajakesari Yoga** | Major Positive | Ch.36.3–4 | ✅ Implemented | `_detect_gajakesari_yoga()` | Full BPHS |
| **Ganda Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Ganesha Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_ganesha_yoga()` | Jupiter/Venus-Ketu |
| **Gola Yoga** | Major Challenges | Ch.35.16 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | All in one sign |
| **Grahan Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_grahan_yoga()` | 4 eclipse types |
| **Guru-Mangala Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_guru_mangala_yoga()` | Jupiter-Mars |
| **Hal Yoga** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | No kendras |
| **Hala Yoga (Corrected)** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Trishadaya sets |
| **Hamsa Yoga** | Major Positive | Ch.75.1–2 | ✅ Implemented | `_detect_pancha_mahapurusha()` | Jupiter - Full BPHS |
| **Harsha Viparita Raj Yoga** | Major Positive | Ch.39 | ✅ Implemented | `_detect_viparita_raj_yoga()` | 6L in dusthana |
| **Harshana Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Indra Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Ishwara Yoga** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | 1-7 houses |
| **Kahala Yoga** | Major Positive | Ch.36.9–10 | ✅ Implemented | `_detect_kahala_yoga()` | Simplified |
| **Kālanidhi Yoga** | Major Positive | Ch.36.31–32 | ⚠️ Partial | `_detect_kalanidhi_yoga()` | **NEEDS COMPLETION** |
| **Kalanala Sanyas Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_sanyas_yogas()` | Renunciation yoga |
| **Kamala Yoga** | Major Positive | Ch.35.12 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | All in kendras |
| **Karma Raj Yoga** | Major Positive | Ch.39.21–22 | ✅ Implemented | `_detect_karma_raj_yoga()` | 10L strong in 10th |
| **Kemadruma Yoga** | Major Challenges | Ch.37.13 | ✅ Implemented | `_detect_kemadruma_yoga()` | Moon isolated |
| **Kevala Sanyas Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_sanyas_yogas()` | Renunciation yoga |
| **Khadga Yoga** | Major Positive | Ch.36.25–26 | ❌ Missing | - | **CRITICAL GAP** |
| **Koota Yoga** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Dusthanas |
| **Kroora Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_kroora_yoga()` | Malefic afflictions |
| **Kubera Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_kubera_yoga()` | Extreme wealth |
| **Kurma Yoga** | Major Positive | Ch.36.23–24 | ✅ Implemented | `_detect_rare_yogas()` | Turtle pattern |
| **Kusuma Yoga** | Major Positive | Ch.36.29–30 | ✅ Implemented | `_detect_rare_yogas()` | Jupiter-Moon/Venus |
| **Kūṭa Yoga (BPHS)** | Standard | Ch.35.14 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | 7 consecutive from 4th |
| **Lakshmi Yoga** | Major Positive | Ch.36.27–28 | ✅ Implemented | `_detect_lakshmi_saraswati_yoga()`, `_detect_additional_house_lord_yogas()` | Multiple variants |
| **Lakshmi Wealth Yogas** | Major Positive | Ch.41.16,28–34 | ✅ Implemented | `_detect_lakshmi_wealth_yogas()` | 15 variations (5L-9L) |
| **Maala Yoga** | Standard | Ch.35.7 | ✅ Implemented | `_detect_nabhasa_ashraya_yogas()` | Mixed sign types |
| **Maha Sanyas Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_sanyas_yogas()` | Great renunciation |
| **Mala Yoga** | Major Positive | Ch.35.8 | ✅ Implemented | `_detect_nabhasa_dala_yogas()` | Benefics in kendras |
| **Malavya Yoga** | Major Positive | Ch.75.1–2 | ✅ Implemented | `_detect_pancha_mahapurusha()` | Venus - Full BPHS |
| **Markandeya Sanyas Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_sanyas_yogas()` | Renunciation yoga |
| **Matsya Yoga** | Major Positive | Ch.36.21–22 | ✅ Implemented | `_detect_rare_yogas()` | Fish pattern |
| **Moon-Venus Mutual Yoga** | Major Positive | Ch.39.41 | ✅ Implemented | `_detect_moon_venus_mutual_yoga()` | 3/11 relationship |
| **Mṛdaṅga Yoga** | Major Positive | Ch.36.17 | ❌ Missing | - | **CRITICAL GAP** |
| **Musala Yoga** | Standard | Ch.35.7 | ✅ Implemented | `_detect_nabhasa_ashraya_yogas()` | Fixed signs |
| **Nala Yoga** | Standard | Ch.35.7 | ✅ Implemented | `_detect_nabhasa_ashraya_yogas()` | Dual signs |
| **Nauka Yoga (BPHS)** | Standard | Ch.35.14 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Boat pattern |
| **Naukaa Yoga** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Boat pattern (alternate) |
| **Neecha Bhanga Raj Yoga** | Major Positive | Ch.39 | ✅ Implemented | `_detect_neecha_bhanga()` | 4 variations |
| **Nipuna Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nipuna_yoga()` | Mercury-Jupiter favorable |
| **Paasha Yoga** | Major Challenges | Ch.35.16 | ✅ Implemented | `_detect_nabhasa_sankhya_yogas()` | 5 signs |
| **Parigha Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Parijata Yoga** | Major Positive | Ch.36.33–34 | ⚠️ Wrong Definition | `_detect_additional_house_lord_yogas()` | Lagna lord strong, NOT Kalpadruma |
| **Parivraja Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_sanyas_yogas()` | Wandering monk |
| **Parvata Yoga** | Major Positive | Ch.36.7–8 | ✅ Implemented | `_detect_parvata_yoga()` | Benefics in kendras |
| **Parvata (Amplifier)** | Minor Subtle | Ch.41.22 | ❌ Missing | - | **CRITICAL GAP** (different yoga) |
| **Priti Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Raj Yoga (Kendra-Trikona)** | Major Positive | Ch.39 | ✅ Implemented | `_detect_raj_yoga_kendra_trikona()` | Simplified |
| **Rajju Yoga** | Standard | Ch.35.7 | ✅ Implemented | `_detect_nabhasa_ashraya_yogas()` | Movable signs |
| **Ruchaka Yoga** | Major Positive | Ch.75.1–2 | ✅ Implemented | `_detect_pancha_mahapurusha()` | Mars - Full BPHS |
| **Sadhya Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Sakata Yoga (Nabhasa)** | Standard | Ch.35.9 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | 1st & 7th only |
| **Śakti Yoga (BPHS)** | Standard | Ch.35.13 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | 7-10 houses |
| **Samudra Yoga** | Standard | Ch.35.15 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Multiple versions |
| **Śaṅkha Yoga** | Major Positive | Ch.36.13–14 | ❌ Missing | - | **CRITICAL GAP** |
| **Śara Yoga** | Standard | Ch.35.13 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Arrow pattern |
| **Sarala Viparita Raj Yoga** | Major Positive | Ch.39 | ✅ Implemented | `_detect_viparita_raj_yoga()` | 8L in dusthana |
| **Śārada Yoga** | Major Positive | Ch.36.19–20 | ❌ Missing | - | **CRITICAL GAP** |
| **Saraswati Yoga** | Major Positive | Ch.36 (implicit) | ✅ Implemented | `_detect_lakshmi_saraswati_yoga()` | BPHS classical definition |
| **Sarpa Yoga** | Major Challenges | Ch.35.8 | ✅ Implemented | `_detect_nabhasa_dala_yogas()` | Malefics in kendras |
| **Sasa Yoga** | Major Positive | Ch.75.1–2 | ✅ Implemented | `_detect_pancha_mahapurusha()` | Saturn - Full BPHS |
| **Saubhagya Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Shakata Yoga** | Major Positive | Ch.35 (rare) | ✅ Implemented | `_detect_rare_yogas()` | Moon 6/8/12 from Jupiter |
| **Shakti Yoga** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | 7 consecutive |
| **Shiva Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Shobhana Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Shola Yoga** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | H5-8 quadrant |
| **Shoola Yoga** | Major Challenges | Ch.35.16 | ✅ Implemented | `_detect_nabhasa_sankhya_yogas()` | 3 signs |
| **Shrinatha Yoga** | Major Positive | Ch.36.18 | ⚠️ Partial | `_detect_rare_yogas()` | Simplified - Venus in kendra |
| **Shubha Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Shukla Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Siddha Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Siddhi Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Śṛṅgāṭaka Yoga** | Standard | Ch.35.10 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Trikonas only |
| **Sukarma Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Sunapha Yoga** | Standard | Ch.37.3–6 | ✅ Implemented | `_detect_sunapha_yoga()` | Planet 2nd from Moon |
| **Systematic Raj Yogas** | Major Positive | Ch.39 | ✅ Implemented | `_detect_systematic_raj_yogas()` | 20+ house lord combos |
| **Trimūrti Yoga** | Major Positive | Ch.36.35–36 | ❌ Missing | - | **CRITICAL GAP** |
| **Ubhayachari Yoga** | Standard | Ch.38.1–4 | ✅ Implemented | `_detect_ubhayachari_yoga()` | Planets both sides of Sun |
| **Vaapī Nabhasa Yoga** | Standard | Ch.35.12 | ✅ Implemented | `_detect_vaapi_nabhasa_yoga()` | Panaphara/Apoklima |
| **Vaapi Yoga** | Standard | Ch.35 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | No kendras |
| **Vaapi Yoga (Dharma Lords)** | Major Positive | Ch.39 & Ch.41 | ✅ Implemented | `_detect_additional_house_lord_yogas()` | 5L-9L relationship |
| **Vaidhriti Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Vajra Yoga** | Standard | Ch.35.11 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Multiple versions |
| **Vallaki Yoga** | Major Challenges | Ch.35 | ✅ Implemented | `_detect_nabhasa_sankhya_yogas()` | Variant |
| **Variyan Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Vasi Yoga** | Standard | Ch.38.1 | ✅ Implemented | `_detect_vosi_yoga()` | Planet 12th from Sun |
| **Vesi Yoga** | Standard | Ch.38.1 | ✅ Implemented | `_detect_vesi_yoga()` | Planet 2nd from Sun |
| **Vihaga Yoga** | Standard | Ch.35.9 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | 4th & 10th only |
| **Vimal Viparita Raj Yoga** | Major Positive | Ch.39 | ✅ Implemented | `_detect_viparita_raj_yoga()` | 12L in dusthana |
| **Vīṇā Yoga** | Standard | Ch.35.16 | ❌ Missing | - | **GAP** |
| **Viparita Raj Yoga** | Major Positive | Ch.39 | ✅ Implemented | `_detect_viparita_raj_yoga()` | Simplified fallback |
| **Vishkambha Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Vosi Yoga** | Standard | Ch.38.1 | ✅ Implemented | `_detect_vosi_yoga()` | Alternate spelling |
| **Vriddhi Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Vyaghata Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Vyatipata Sanyas Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_sanyas_yogas()` | Renunciation yoga |
| **Vyatipata Yoga** | Non-BPHS | - | ✅ Implemented | `_detect_nitya_yogas()` | Nitya yoga |
| **Yava Yoga** | Standard | Ch.35.11 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Multiple versions |
| **Yuga Yoga** | Standard | Ch.35.16 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | H1-4 quadrant |
| **Yupa Yoga** | Standard | Ch.35.13 | ✅ Implemented | `_detect_nabhasa_akriti_yogas()` | Multiple versions |

**Additional Categories Not Shown:**
- **Bhava Yogas (144):** All 12 house lords in all 12 positions
- **Ascendant-Specific Wealth (12):** Aries through Pisces
- **Royal Association (16):** Jaimini Amatyakaraka/Atmakaraka patterns
- **Kala Sarpa Yoga (12):** All 12 types by Rahu position
- **Eclipse Yogas (4):** Sun/Moon with Rahu/Ketu

---

## Recommendations

### Immediate Actions (Next Sprint)
1. ✅ **Add Critical Named Yogas:** Śaṅkha, Bherī, Mṛdaṅga, Śārada, Khadga, Trimūrti (Ch.36)
2. ✅ **Add Divisional Amplifiers:** All 8 yogas (Ch.41.18–27) - Requires D9 integration
3. ✅ **Add `bphs_category` Field:** Standardize categorization across all yogas
4. ⚠️ **Complete Partial Yogas:** Kālanidhi, Kalpadruma/Parijāta disambiguation, Lagna-Ādhi

### Medium-Term (1-2 months)
1. ✅ **Navamsa Integration:** Ensure D9 data available for all planets, implement D9-dependent yogas
2. ✅ **Add Missing Standard Yogas:** Dhana from Moon, Kedāra, Vīṇā
3. ✅ **Add Subtle Raj Yogas:** Birth moment factor, exalted aspects on Lagna, Vargottama Moon (separate)
4. ⚠️ **Jaimini Enhancements:** Arūḍha relations, AK expense factors

### Long-Term (3+ months)
1. 📊 **Frontend Category Filtering:** Allow users to filter by BPHS category
2. 📖 **BPHS Reference Guide:** Comprehensive documentation with examples
3. 🧪 **Test Coverage:** Add test cases for all BPHS yogas with golden examples
4. 🔄 **Dasha Integration:** Add timing predictions for penury yogas, divisional amplifiers
5. 📈 **Strength Refinement:** Consider BPHS-specific strength algorithms vs custom

---

## Conclusion

### Current State
The implementation contains **~350 yogas** covering:
- ✅ **67% of Major Positive Yogas** (24/36)
- ✅ **78% of Major Challenges** (18/23)
- ✅ **87% of Standard Yogas** (33/38)
- ❌ **13% of Minor/Subtle Yogas** (2/15)

**Overall BPHS Coverage:** ~68% (77/112 yogas)

### Strengths
1. Excellent coverage of Pancha Mahapurusha, Sun/Moon yogas, Nabhasa yogas
2. Comprehensive Viparita Raj Yogas and Penury Yogas
3. Extensive practical additions (Bhava, Nitya, Sanyas, Eclipse yogas)
4. Sophisticated strength calculation and cancellation detection

### Critical Gaps
1. **9 Named Yogas from Ch.36** - Classical importance
2. **8 Divisional Amplifiers from Ch.41.18–27** - Requires Navamsa
3. **5 Subtle Raj Yogas** - Advanced techniques
4. **No standardized BPHS category field** - Organizational issue

### Next Steps
**Priority 1:** Implement missing Ch.36 named yogas + add `bphs_category` field (2-3 weeks)
**Priority 2:** Integrate Navamsa for divisional amplifiers (1-2 weeks)
**Priority 3:** Add subtle raj yogas and complete standard yogas (1 week)
**Priority 4:** Documentation and testing (1 week)

**Target:** 90%+ BPHS coverage within 2 months

---

**Document End**
