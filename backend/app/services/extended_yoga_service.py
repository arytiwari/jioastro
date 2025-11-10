"""
Extended Yoga Detection Service
Detects 25+ classical Vedic yogas beyond the basic set
"""

from typing import Dict, List, Any, Optional
from app.services.jaimini_service import JaiminiService


class ExtendedYogaService:
    """Comprehensive yoga detection service with 25+ classical yogas"""

    SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    # Exaltation signs (1-indexed)
    EXALTATION_SIGNS = {
        "Sun": 1,      # Aries
        "Moon": 2,     # Taurus
        "Mars": 10,    # Capricorn
        "Mercury": 6,  # Virgo
        "Jupiter": 4,  # Cancer
        "Venus": 12,   # Pisces
        "Saturn": 7,   # Libra
    }

    # Debilitation signs
    DEBILITATION_SIGNS = {
        "Sun": 7,      # Libra
        "Moon": 8,     # Scorpio
        "Mars": 4,     # Cancer
        "Mercury": 12, # Pisces
        "Jupiter": 10, # Capricorn
        "Venus": 6,    # Virgo
        "Saturn": 1,   # Aries
    }

    # Own signs
    OWN_SIGNS = {
        "Sun": [5],          # Leo
        "Moon": [4],         # Cancer
        "Mars": [1, 8],      # Aries, Scorpio
        "Mercury": [3, 6],   # Gemini, Virgo
        "Jupiter": [9, 12],  # Sagittarius, Pisces
        "Venus": [2, 7],     # Taurus, Libra
        "Saturn": [10, 11],  # Capricorn, Aquarius
    }

    # Planetary friendships (simplified)
    FRIENDSHIPS = {
        "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "neutrals": ["Mercury"], "enemies": ["Venus", "Saturn"]},
        "Moon": {"friends": ["Sun", "Mercury"], "neutrals": ["Mars", "Jupiter", "Venus", "Saturn"], "enemies": []},
        "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "neutrals": ["Venus", "Saturn"], "enemies": ["Mercury"]},
        "Mercury": {"friends": ["Sun", "Venus"], "neutrals": ["Mars", "Jupiter", "Saturn"], "enemies": ["Moon"]},
        "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "neutrals": ["Saturn"], "enemies": ["Mercury", "Venus"]},
        "Venus": {"friends": ["Mercury", "Saturn"], "neutrals": ["Mars", "Jupiter"], "enemies": ["Sun", "Moon"]},
        "Saturn": {"friends": ["Mercury", "Venus"], "neutrals": ["Jupiter"], "enemies": ["Sun", "Moon", "Mars"]},
    }

    def __init__(self):
        """Initialize Extended Yoga Service with Jaimini integration"""
        self.jaimini = JaiminiService()

    def _calculate_planet_dignity(self, planet_name: str, planets: Dict) -> int:
        """
        Calculate planet dignity score (0-100)
        - Exalted: 100
        - Own sign: 80
        - Friend's sign: 60
        - Neutral sign: 40
        - Enemy's sign: 20
        - Debilitated: 0

        Now uses special state fields from planet data for accuracy
        """
        planet_data = planets.get(planet_name, {})

        # Use special state fields if available
        if planet_data.get("exalted", False):
            return 100

        if planet_data.get("debilitated", False):
            return 0

        if planet_data.get("own_sign", False):
            return 80

        # Check friendship (simplified - would need sign lordship for full accuracy)
        # For now, return moderate scores
        return 50

    def _calculate_house_strength(self, house: int) -> int:
        """
        Calculate house strength score (0-100)
        - Kendra (1,4,7,10): 100
        - Trikona (1,5,9): 90
        - Upachaya (3,6,10,11): 70
        - Dusthana (6,8,12): 20
        - Others: 50
        """
        if house in [1, 4, 7, 10]:  # Kendra
            return 100
        elif house in [5, 9]:  # Trikona (excluding 1 which is already kendra)
            return 90
        elif house in [3, 6, 11]:  # Upachaya (excluding 10 which is kendra)
            return 70
        elif house in [8, 12]:  # Dusthana (excluding 6 which is upachaya)
            return 20
        else:
            return 50

    def _is_combusted(self, planet_name: str, planets: Dict) -> bool:
        """
        Check if planet is combusted (too close to Sun)
        Now uses accurate degree-based calculation from planet data
        """
        if planet_name in ["Sun", "Rahu", "Ketu"]:
            return False

        planet_data = planets.get(planet_name, {})
        # Use the combust field if available (accurate degree-based calculation)
        return planet_data.get("combust", False)

    def _is_retrograde(self, planet_name: str, planets: Dict) -> bool:
        """Check if planet is retrograde"""
        if planet_name in ["Sun", "Moon", "Rahu", "Ketu"]:
            return False
        return planets.get(planet_name, {}).get("retrograde", False)

    def _calculate_yoga_strength(self, yoga_forming_planets: List[str], planets: Dict) -> str:
        """
        Calculate overall yoga strength based on:
        - Planet dignity
        - House placement
        - Combustion
        - Retrograde status

        Returns: "Very Strong", "Strong", "Medium", or "Weak"
        """
        if not yoga_forming_planets:
            return "Medium"

        total_score = 0
        planet_count = 0

        for planet_name in yoga_forming_planets:
            if planet_name not in planets:
                continue

            planet_count += 1

            # Dignity score (0-100)
            dignity = self._calculate_planet_dignity(planet_name, planets)

            # House strength (0-100)
            house = planets.get(planet_name, {}).get("house", 0)
            house_strength = self._calculate_house_strength(house) if house else 50

            # Penalties
            combustion_penalty = -30 if self._is_combusted(planet_name, planets) else 0
            retrograde_adjustment = +10 if self._is_retrograde(planet_name, planets) else 0  # Retrograde can be beneficial for some yogas

            planet_score = (dignity * 0.6 + house_strength * 0.4) + combustion_penalty + retrograde_adjustment
            total_score += max(0, planet_score)

        if planet_count == 0:
            return "Medium"

        avg_score = total_score / planet_count

        # Determine strength category
        if avg_score >= 80:
            return "Very Strong"
        elif avg_score >= 60:
            return "Strong"
        elif avg_score >= 40:
            return "Medium"
        else:
            return "Weak"

    def _check_yoga_cancellation(self, yoga_forming_planets: List[str], planets: Dict) -> tuple[bool, List[str]]:
        """
        Check if yoga is cancelled (bhanga) and return cancellation reasons

        Cancellation happens when:
        - Any yoga-forming planet is debilitated
        - Any yoga-forming planet is combusted
        - Majority of yoga planets are in dusthana (6, 8, 12)

        Returns: (is_cancelled, list_of_reasons)
        """
        is_cancelled = False
        reasons = []

        for planet_name in yoga_forming_planets:
            if planet_name not in planets:
                continue

            planet_data = planets.get(planet_name, {})
            sign_num = planet_data.get("sign_num", 0)
            house = planet_data.get("house", 0)

            # Check debilitation (use special state field if available)
            if planet_data.get("debilitated", False):
                is_cancelled = True
                sign_name = self.SIGNS[sign_num-1] if sign_num > 0 else "unknown"
                reasons.append(f"{planet_name} is debilitated in {sign_name}")

            # Check combustion
            if self._is_combusted(planet_name, planets):
                is_cancelled = True
                reasons.append(f"{planet_name} is combusted by Sun")

            # Check dusthana placement
            if house in [6, 8, 12]:
                reasons.append(f"{planet_name} in dusthana house {house}")

        # If majority in dusthana, yoga is weakened/cancelled
        dusthana_count = sum(1 for p in yoga_forming_planets if planets.get(p, {}).get("house", 0) in [6, 8, 12])
        if dusthana_count > len(yoga_forming_planets) / 2:
            is_cancelled = True

        return (is_cancelled, reasons)

    def detect_extended_yogas(self, planets: Dict[str, Any], houses: Any = None) -> List[Dict[str, str]]:
        """
        Detect 100+ comprehensive classical Vedic yogas (BPHS-compliant):

        **TIER 1 - MAJOR LIFE-DEFINING YOGAS:**
        **Pancha Mahapurusha Yogas (5)**: Ruchaka, Bhadra, Hamsa, Malavya, Sasa
        **Sun-Based Yogas (3)** ⭐ MAJOR: Vesi, Vosi, Ubhayachari (planets around Sun - soul & authority)
        **Moon-Based Yogas (4)** ⭐ MAJOR: Sunapha, Anapha, Durudhura, Kemadruma (planets around Moon - mind & prosperity)
        **Learning & Wisdom (2)** ⭐ MAJOR: Saraswati (one of the most auspicious!), Budhaditya
        **Jupiter-Moon (1)** ⭐ MAJOR: Gaja Kesari

        **TIER 2 - IMPORTANT YOGAS:**
        **Wealth & Prosperity (8)**: Adhi, Lakshmi, Amala, Parvata, Kahala, Dhana, Kubera, Daridra
        **Conjunction Yogas (3)**: Chandra-Mangala, Guru-Mangala, Budhaditya
        **Raja Yogas (3)**: Viparita Raj, Raj Yoga (Kendra-Trikona), Dharma-Karmadhipati
        **Neecha Bhanga (4)**: Debilitation cancellation variations
        **Kala Sarpa (12)**: All types based on Rahu position (transformational)

        **Nabhasa Yogas (32 - COMPLETE)**:
        - Ashraya (4): Rajju, Musala, Nala, Maala
        - Dala (2): Mala, Sarpa
        - Akriti (20): Gola, Yuga, Shola, Hal, Vajra, Yava, Kamala, Vaapi, Yupa, Ishwara, Shakti, Danda, Naukaa, Koota, Chatra, Chaapa, Ardha Chandra, Chakra, Samudra, Dama
        - Sankhya (3): Vallaki, Daam, Paasha
        - Other (3): Included in Akriti

        **Nitya Yogas (27)**: Birth yogas based on Sun-Moon angular distance
        **Sanyas Yogas (7)**: Maha Sanyas, Parivraja, Kevala, Markandeya, Akhanda, Vyatipata, Kalanala
        **Eclipse Yogas (4)**: Grahan (Sun-Rahu, Sun-Ketu, Moon-Rahu, Moon-Ketu)
        **Other Classical (10)**: Gajakesari, Chamara, Nipuna, Chandal, Balarishta, Kroora, Rare (5)

        Args:
            planets: Dictionary of planetary positions with sign_num and house
            houses: Houses data (optional, for advanced yogas)

        Returns:
            List of detected yogas with name, description, strength, and category
        """
        yogas = []

        # 1-5: Pancha Mahapurusha Yogas (5 Great Person yogas)
        yogas.extend(self._detect_pancha_mahapurusha(planets))

        # 6: Adhi Yoga
        yogas.extend(self._detect_adhi_yoga(planets))

        # 7: Chamara Yoga
        yogas.extend(self._detect_chamara_yoga(planets))

        # 8-9: Lakshmi Yoga & Saraswati Yoga
        yogas.extend(self._detect_lakshmi_saraswati_yoga(planets))

        # 10: Amala Yoga
        yogas.extend(self._detect_amala_yoga(planets))

        # 11: Parvata Yoga
        yogas.extend(self._detect_parvata_yoga(planets))

        # 12: Kahala Yoga
        yogas.extend(self._detect_kahala_yoga(planets))

        # 13: Chandra-Mangala Yoga
        yogas.extend(self._detect_chandra_mangala_yoga(planets))

        # 14: Guru-Mangala Yoga
        yogas.extend(self._detect_guru_mangala_yoga(planets))

        # 15: Viparita Raj Yoga
        yogas.extend(self._detect_viparita_raj_yoga(planets))

        # 15a: Additional House Lord Yogas (Vaapi Dharma Lords, Lakshmi Classical, Parijata)
        yogas.extend(self._detect_additional_house_lord_yogas(planets))

        # 16: Neecha Bhanga Raj Yoga
        yogas.extend(self._detect_neecha_bhanga(planets))

        # 17: Vesi Yoga
        yogas.extend(self._detect_vesi_yoga(planets))

        # 18: Vosi Yoga
        yogas.extend(self._detect_vosi_yoga(planets))

        # 19: Ubhayachari Yoga
        yogas.extend(self._detect_ubhayachari_yoga(planets))

        # 20: Sunapha Yoga
        yogas.extend(self._detect_sunapha_yoga(planets))

        # 21: Anapha Yoga
        yogas.extend(self._detect_anapha_yoga(planets))

        # 22: Durudhura Yoga
        yogas.extend(self._detect_durudhura_yoga(planets))

        # 23: Kemadruma Yoga (inauspicious)
        yogas.extend(self._detect_kemadruma_yoga(planets))

        # 24: Budhaditya Yoga (already exists but enhanced)
        yogas.extend(self._detect_budhaditya_yoga(planets))

        # 25: Nipuna Yoga
        yogas.extend(self._detect_nipuna_yoga(planets))

        # 26: Kala Sarpa Yoga (12 types based on Rahu position)
        yogas.extend(self._detect_kala_sarpa_yoga(planets))

        # 27-30: Nabhasa Ashraya Yogas (4 types - based on sign types)
        yogas.extend(self._detect_nabhasa_ashraya_yogas(planets))

        # 31-32: Nabhasa Dala Yogas (2 types - based on benefic/malefic)
        yogas.extend(self._detect_nabhasa_dala_yogas(planets))

        # 33-52: Nabhasa Akriti Yogas (complete 20 pattern yogas)
        yogas.extend(self._detect_nabhasa_akriti_yogas(planets))

        # 53-55: Nabhasa Sankhya Yogas (numerical patterns)
        yogas.extend(self._detect_nabhasa_sankhya_yogas(planets))

        # 56-60: Rare Yogas (Shakata, Shrinatha, Kusuma, Matsya, Kurma)
        yogas.extend(self._detect_rare_yogas(planets))

        # NEW YOGAS - Phase 1: Critical
        # 42: Gajakesari Yoga
        yogas.extend(self._detect_gajakesari_yoga(planets))

        # 43: Raj Yoga (Kendra-Trikona - simplified)
        yogas.extend(self._detect_raj_yoga_kendra_trikona(planets))

        # 43a: Systematic Raj Yogas (BPHS-compliant house lord combinations)
        yogas.extend(self._detect_systematic_raj_yogas(planets))

        # 43b: Benefic Support Yogas (Phase 1.3)
        yogas.extend(self._detect_benefic_support_yogas(planets))

        # 43c: Valor Yogas (Phase 1.4)
        yogas.extend(self._detect_valor_yogas(planets))

        # 43d: Exalted Benefic in 2nd (Phase 1.5)
        yogas.extend(self._detect_exalted_benefic_2nd_yogas(planets))

        # 43e: Viparita-like Support (Phase 1.6)
        yogas.extend(self._detect_viparita_like_support_yogas(planets))

        # 43f: Miscellaneous Raj Supports (Phase 1.7)
        yogas.extend(self._detect_karma_raj_yoga(planets))
        yogas.extend(self._detect_all_benefic_kendras_yoga(planets))
        yogas.extend(self._detect_moon_venus_mutual_yoga(planets))

        # 44: Grahan Yoga
        yogas.extend(self._detect_grahan_yoga(planets))

        # NEW YOGAS - Phase 2: High Priority
        # 45: Dharma-Karmadhipati Yoga (simplified)
        yogas.extend(self._detect_dharma_karmadhipati_yoga(planets))

        # 46: Dhana Yoga (simplified)
        yogas.extend(self._detect_dhana_yoga(planets))

        # 46a: Lakshmi Wealth Yogas (5L-9L relationships)
        yogas.extend(self._detect_lakshmi_wealth_yogas(planets))

        # 46b: Ascendant-Specific Wealth Yogas
        yogas.extend(self._detect_ascendant_wealth_yogas(planets))

        # 47: Chandal Yoga
        yogas.extend(self._detect_chandal_yoga(planets))

        # 48: Kubera Yoga
        yogas.extend(self._detect_kubera_yoga(planets))

        # 49: Daridra Yoga
        yogas.extend(self._detect_daridra_yoga(planets))

        # 49a: Comprehensive Penury Yogas (BPHS Ch.42)
        yogas.extend(self._detect_penury_yogas(planets))

        # 49b: Royal Association Yogas (Jaimini - BPHS Ch.40)
        yogas.extend(self._detect_royal_association_yogas(planets))

        # NEW YOGAS - Phase 3: Medium Priority
        # 50: Balarishta Yoga
        yogas.extend(self._detect_balarishta_yoga(planets))

        # 51: Kroora Yoga
        yogas.extend(self._detect_kroora_yoga(planets))

        # NEW: 27 Nitya Yogas (Birth Yogas based on Sun-Moon distance)
        # 61-87: Nitya Yogas
        yogas.extend(self._detect_nitya_yogas(planets))

        # NEW PHASE 3: Sanyas Yogas (Renunciation Yogas)
        # 88-94: Sanyas Yogas (7 classical renunciation yogas)
        yogas.extend(self._detect_sanyas_yogas(planets))

        # NEW PHASE 4: Bhava Yogas (House Lord Placements)
        # 95-238: Bhava Yogas (144 complete house lord placements: all 12 lords × 12 positions)
        yogas.extend(self._detect_bhava_yogas(planets))

        # Enrich all yogas with classification metadata (importance, impact, life_area)
        return self.enrich_yogas(yogas)

    def _detect_pancha_mahapurusha(self, planets: Dict) -> List[Dict]:
        """
        Pancha Mahapurusha Yogas - 5 great yogas from Mars, Mercury, Jupiter, Venus, Saturn
        Formed when these planets are in own sign or exalted in Kendra (1,4,7,10)
        """
        yogas = []
        kendra_houses = [1, 4, 7, 10]

        yoga_names = {
            "Mars": "Ruchaka Yoga",
            "Mercury": "Bhadra Yoga",
            "Jupiter": "Hamsa Yoga",
            "Venus": "Malavya Yoga",
            "Saturn": "Sasa Yoga"
        }

        yoga_effects = {
            "Mars": "Courage, leadership, victory over enemies, commander qualities",
            "Mercury": "Intelligence, eloquence, learning, business acumen",
            "Jupiter": "Wisdom, righteousness, spiritual knowledge, prosperity",
            "Venus": "Beauty, artistic talents, luxury, marital happiness",
            "Saturn": "Authority, discipline, organizational skills, longevity"
        }

        for planet in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            planet_data = planets.get(planet, {})
            house = planet_data.get("house")
            sign_num = planet_data.get("sign_num")

            if house in kendra_houses:
                # Check if exalted or in own sign
                is_exalted = sign_num == self.EXALTATION_SIGNS.get(planet)
                is_own_sign = sign_num in self.OWN_SIGNS.get(planet, [])

                if is_exalted or is_own_sign:
                    # Calculate accurate strength using new helper
                    calculated_strength = self._calculate_yoga_strength([planet], planets)

                    # Check for cancellation
                    is_cancelled, cancel_reasons = self._check_yoga_cancellation([planet], planets)

                    # Build description with cancellation note if applicable
                    base_desc = f"{planet} in Kendra in {'exalted' if is_exalted else 'own'} sign - {yoga_effects[planet]}"
                    if is_cancelled:
                        base_desc += f" [CANCELLED: {'; '.join(cancel_reasons)}]"
                        calculated_strength = "Weak"  # Downgrade strength if cancelled
                    elif cancel_reasons:
                        base_desc += f" [WEAKENED: {'; '.join(cancel_reasons)}]"

                    yogas.append({
                        "name": yoga_names[planet],
                        "description": base_desc,
                        "strength": calculated_strength,
                        "category": "Pancha Mahapurusha"
                    })

        return yogas

    def _detect_adhi_yoga(self, planets: Dict) -> List[Dict]:
        """
        Adhi Yoga: Benefics (Mercury, Venus, Jupiter) in 6th, 7th, 8th from Moon
        Brings wealth, power, good health, long life
        """
        yogas = []
        moon_house = planets.get("Moon", {}).get("house", 0)

        benefics_in_678 = []
        for planet in ["Mercury", "Venus", "Jupiter"]:
            planet_house = planets.get(planet, {}).get("house", 0)
            house_diff = (planet_house - moon_house) % 12
            if house_diff in [5, 6, 7]:  # 6th, 7th, 8th from Moon (0-indexed: 5,6,7)
                benefics_in_678.append(planet)

        if len(benefics_in_678) >= 2:
            yogas.append({
                "name": "Adhi Yoga",
                "description": f"Benefics ({', '.join(benefics_in_678)}) in 6th/7th/8th from Moon - brings wealth, power, health, longevity",
                "strength": "Strong",
                "category": "Wealth & Power"
            })

        return yogas

    def _detect_chamara_yoga(self, planets: Dict) -> List[Dict]:
        """
        Chamara Yoga: Ascendant lord exalted in Kendra, aspected by Jupiter
        Brings fame, learning, authority
        """
        # Simplified: Jupiter in Kendra and exalted
        yogas = []
        jupiter = planets.get("Jupiter", {})
        if jupiter.get("house") in [1, 4, 7, 10] and jupiter.get("sign_num") == 4:  # Cancer
            yogas.append({
                "name": "Chamara Yoga",
                "description": "Jupiter exalted in Kendra - brings fame, learning, authority, royal favor",
                "strength": "Strong",
                "category": "Fame & Authority"
            })
        return yogas

    def _detect_lakshmi_saraswati_yoga(self, planets: Dict) -> List[Dict]:
        """
        Lakshmi Yoga: Venus strong in Kendra - wealth and prosperity
        Saraswati Yoga (Classical BPHS): Mercury, Jupiter, Venus with mutual conjunction/aspect
        """
        yogas = []

        # Lakshmi Yoga
        venus = planets.get("Venus", {})
        if venus.get("house") in [1, 4, 7, 10]:
            if venus.get("sign_num") in self.OWN_SIGNS.get("Venus", []) or venus.get("sign_num") == 12:
                yogas.append({
                    "name": "Lakshmi Yoga",
                    "description": "Strong Venus in Kendra - brings wealth, prosperity, luxury, beauty",
                    "strength": "Medium",
                    "category": "Wealth"
                })

        # Saraswati Yoga (BPHS Classical Definition)
        # Conditions per Brihat Parashara Hora Shastra:
        # 1. Jupiter, Venus, and Mercury ALL in Kendra (1,4,7,10) OR Trikona (1,5,9) OR 2nd house FROM LAGNA
        # 2. Jupiter must be in strong position (own sign, exaltation, or friendly sign)
        # 3. Mercury should not be combust (optional stricter interpretation)

        mercury = planets.get("Mercury", {})
        jupiter = planets.get("Jupiter", {})
        venus_data = planets.get("Venus", {})

        merc_house = mercury.get("house", 0)
        jup_house = jupiter.get("house", 0)
        ven_house = venus_data.get("house", 0)

        # Kendra houses from Lagna: 1, 4, 7, 10
        # Trikona houses from Lagna: 1, 5, 9
        # Combined with 2nd house: 1, 2, 4, 5, 7, 9, 10
        saraswati_houses = [1, 2, 4, 5, 7, 9, 10]

        if merc_house and jup_house and ven_house:
            # Check if ALL three planets are in these houses FROM LAGNA
            if (merc_house in saraswati_houses and
                jup_house in saraswati_houses and
                ven_house in saraswati_houses):

                # Check Jupiter strength
                jup_sign = jupiter.get("sign_num", 0)
                jup_exalted = jupiter.get("exalted", False)
                jup_own_sign = jup_sign in self.OWN_SIGNS.get("Jupiter", [])  # 9, 12 (Sagittarius, Pisces)

                # Friendly signs for Jupiter: Sun (Leo=5), Moon (Cancer=4), Mars (Aries=1, Scorpio=8)
                jup_friendly_signs = [1, 4, 5, 8]
                jup_in_friendly = jup_sign in jup_friendly_signs

                jup_strong = jup_exalted or jup_own_sign or jup_in_friendly

                if jup_strong:
                    # Optional: Check Mercury not combust (for stricter interpretation)
                    merc_combust = mercury.get("combust", False)

                    # Build formation description
                    house_positions = []
                    if merc_house in [1, 4, 7, 10]:
                        house_positions.append(f"Mercury in {merc_house}th (kendra)")
                    elif merc_house in [5, 9]:
                        house_positions.append(f"Mercury in {merc_house}th (trikona)")
                    else:
                        house_positions.append(f"Mercury in 2nd")

                    if jup_house in [1, 4, 7, 10]:
                        house_positions.append(f"Jupiter in {jup_house}th (kendra)")
                    elif jup_house in [5, 9]:
                        house_positions.append(f"Jupiter in {jup_house}th (trikona)")
                    else:
                        house_positions.append(f"Jupiter in 2nd")

                    if ven_house in [1, 4, 7, 10]:
                        house_positions.append(f"Venus in {ven_house}th (kendra)")
                    elif ven_house in [5, 9]:
                        house_positions.append(f"Venus in {ven_house}th (trikona)")
                    else:
                        house_positions.append(f"Venus in 2nd")

                    strength_note = ""
                    if jup_exalted:
                        strength_note = " (Jupiter exalted)"
                    elif jup_own_sign:
                        strength_note = " (Jupiter in own sign)"
                    else:
                        strength_note = " (Jupiter in friendly sign)"

                    formation = ", ".join(house_positions)

                    yogas.append({
                        "name": "Saraswati Yoga",
                        "description": f"Mercury, Jupiter, Venus in favorable houses from Lagna{strength_note} - exceptional learning, wisdom, eloquence, artistic talents, mastery of arts and sciences, blessed by Goddess Saraswati",
                        "strength": "Very Strong" if jup_exalted else "Strong",
                        "category": "Learning & Wisdom",
                        "importance": "major",
                        "impact": "positive",
                        "yoga_forming_planets": ["Mercury", "Jupiter", "Venus"],
                        "formation": formation,
                        "jupiter_strength": "Exalted" if jup_exalted else ("Own Sign" if jup_own_sign else "Friendly Sign")
                    })

        return yogas

    def _detect_amala_yoga(self, planets: Dict) -> List[Dict]:
        """
        Amala Yoga: Benefic in 10th from Moon or Ascendant
        Brings lasting fame, good reputation, prosperity
        """
        yogas = []
        moon_house = planets.get("Moon", {}).get("house", 0)

        for planet in ["Mercury", "Venus", "Jupiter"]:
            planet_house = planets.get(planet, {}).get("house", 0)
            # Check 10th from Moon (9 houses ahead, 0-indexed)
            if (planet_house - moon_house) % 12 == 9:
                yogas.append({
                    "name": "Amala Yoga",
                    "description": f"{planet} in 10th from Moon - lasting fame, good character, prosperity",
                    "strength": "Medium",
                    "category": "Fame & Reputation"
                })
                break

        return yogas

    def _detect_parvata_yoga(self, planets: Dict) -> List[Dict]:
        """
        Parvata Yoga: Benefics in Kendras and no malefics in Kendras
        Brings wealth, learning, fame
        """
        yogas = []
        kendra_houses = [1, 4, 7, 10]

        benefics_in_kendra = [p for p in ["Mercury", "Venus", "Jupiter"]
                             if planets.get(p, {}).get("house") in kendra_houses]
        malefics_in_kendra = [p for p in ["Mars", "Saturn"]
                             if planets.get(p, {}).get("house") in kendra_houses]

        if len(benefics_in_kendra) >= 2 and len(malefics_in_kendra) == 0:
            yogas.append({
                "name": "Parvata Yoga",
                "description": "Benefics in Kendras without malefics - wealth, learning, charitable nature",
                "strength": "Medium",
                "category": "Wealth & Character"
            })

        return yogas

    def _detect_kahala_yoga(self, planets: Dict) -> List[Dict]:
        """
        Kahala Yoga: Jupiter and 4th lord in mutual Kendras
        Simplified: Jupiter in Kendra from 4th house
        """
        yogas = []
        jupiter_house = planets.get("Jupiter", {}).get("house", 0)

        # Simplified check: Jupiter in Kendra (1,4,7,10)
        if jupiter_house in [1, 4, 7, 10]:
            yogas.append({
                "name": "Kahala Yoga",
                "description": "Jupiter well-placed - brings courage, leadership, victory",
                "strength": "Medium",
                "category": "Leadership"
            })

        return yogas

    def _detect_chandra_mangala_yoga(self, planets: Dict) -> List[Dict]:
        """
        Chandra-Mangala Yoga: Moon and Mars together or in mutual aspect
        Brings wealth through property, courage
        """
        yogas = []
        moon_house = planets.get("Moon", {}).get("house", 0)
        mars_house = planets.get("Mars", {}).get("house", 0)

        # Same house (conjunction)
        if moon_house == mars_house:
            yogas.append({
                "name": "Chandra-Mangala Yoga",
                "description": "Moon-Mars conjunction - wealth through property, courage, practical nature",
                "strength": "Medium",
                "category": "Wealth"
            })
        # 7th house aspect
        elif abs(moon_house - mars_house) == 6 or abs(moon_house - mars_house) == 6:
            yogas.append({
                "name": "Chandra-Mangala Yoga (aspect)",
                "description": "Moon-Mars in opposition - wealth, determination, property gains",
                "strength": "Weak",
                "category": "Wealth"
            })

        return yogas

    def _detect_guru_mangala_yoga(self, planets: Dict) -> List[Dict]:
        """
        Guru-Mangala Yoga: Jupiter and Mars together
        Brings technical expertise, engineering skills, leadership
        """
        yogas = []
        jupiter_house = planets.get("Jupiter", {}).get("house", 0)
        mars_house = planets.get("Mars", {}).get("house", 0)

        if jupiter_house == mars_house:
            yogas.append({
                "name": "Guru-Mangala Yoga",
                "description": "Jupiter-Mars conjunction - technical expertise, engineering skills, strategic thinking",
                "strength": "Medium",
                "category": "Skills & Leadership"
            })

        return yogas

    def _detect_viparita_raj_yoga(self, planets: Dict) -> List[Dict]:
        """
        Viparita Raj Yoga: Three classical types (BPHS-compliant)

        1. Harsha Yoga: 6th lord in 6th, 8th, or 12th house
           - Victory over enemies, good health, courage, happiness

        2. Sarala Yoga: 8th lord in 6th, 8th, or 12th house
           - Long life, overcoming dangers, occult knowledge, fearless nature

        3. Vimal Yoga: 12th lord in 6th, 8th, or 12th house
           - Success despite difficulties, spiritual wisdom, independence, charity

        These yogas indicate success through overcoming adversity.
        Principle: When dusthana lords (6,8,12) occupy other dusthanas,
        they neutralize negative effects and create Raja Yoga.
        """
        yogas = []
        dusthana_houses = [6, 8, 12]

        # Get ascendant sign (0-indexed: 0=Aries, 11=Pisces)
        asc_data = planets.get("Ascendant", {})
        asc_sign_num = asc_data.get("sign_num", 0)

        if not asc_sign_num:
            # Fallback to simplified detection if no ascendant data
            malefics_in_dusthana = [p for p in ["Mars", "Saturn"]
                                   if planets.get(p, {}).get("house") in dusthana_houses]
            if len(malefics_in_dusthana) >= 2:
                yogas.append({
                    "name": "Viparita Raj Yoga",
                    "description": "Malefics in dusthanas - success through overcoming adversity, turning difficulties into opportunities",
                    "strength": "Medium",
                    "category": "Overcoming Obstacles",
                    "importance": "moderate",
                    "impact": "positive"
                })
            return yogas

        # Convert to 0-indexed for _get_house_lord
        asc_sign = asc_sign_num - 1

        # 1. HARSHA YOGA: 6th lord in 6th, 8th, or 12th
        lord_6th = self._get_house_lord(6, asc_sign)
        lord_6th_house = planets.get(lord_6th, {}).get("house", 0)

        if lord_6th_house in dusthana_houses:
            yogas.append({
                "name": "Harsha Viparita Raj Yoga",
                "description": f"6th lord ({lord_6th}) in {lord_6th_house}th house - Victory over enemies, good health, courage and fighting spirit, happiness, success in competitive fields",
                "strength": "Strong",
                "category": "Viparita Raj Yoga",
                "importance": "major",
                "impact": "positive",
                "formation": f"6th house lord {lord_6th} placed in dusthana ({lord_6th_house}th house)"
            })

        # 2. SARALA YOGA: 8th lord in 6th, 8th, or 12th
        lord_8th = self._get_house_lord(8, asc_sign)
        lord_8th_house = planets.get(lord_8th, {}).get("house", 0)

        if lord_8th_house in dusthana_houses:
            yogas.append({
                "name": "Sarala Viparita Raj Yoga",
                "description": f"8th lord ({lord_8th}) in {lord_8th_house}th house - Long life despite obstacles, overcoming dangers and accidents, success in occult sciences, fearless nature, inheritance gains",
                "strength": "Strong",
                "category": "Viparita Raj Yoga",
                "importance": "major",
                "impact": "positive",
                "formation": f"8th house lord {lord_8th} placed in dusthana ({lord_8th_house}th house)"
            })

        # 3. VIMAL YOGA: 12th lord in 6th, 8th, or 12th
        lord_12th = self._get_house_lord(12, asc_sign)
        lord_12th_house = planets.get(lord_12th, {}).get("house", 0)

        if lord_12th_house in dusthana_houses:
            yogas.append({
                "name": "Vimal Viparita Raj Yoga",
                "description": f"12th lord ({lord_12th}) in {lord_12th_house}th house - Success despite financial difficulties, spiritual wisdom and inclinations, charity and helping others, independent nature, gains from foreign lands or spirituality",
                "strength": "Strong",
                "category": "Viparita Raj Yoga",
                "importance": "major",
                "impact": "positive",
                "formation": f"12th house lord {lord_12th} placed in dusthana ({lord_12th_house}th house)"
            })

        return yogas

    def _detect_additional_house_lord_yogas(self, planets: Dict) -> List[Dict]:
        """
        Additional house-lord based classical yogas:
        1. Vaapi Yoga (Dharma Lords Type): 5th and 9th lords in mutual relationship
        2. Lakshmi Yoga (Classical): Lagna lord in Kendra/Trikona + strong benefic in 9th/5th
        3. Parijata Yoga: Lagna lord strong in Kendra/Trikona
        """
        yogas = []

        # Get ascendant sign for house lord calculations
        asc_data = planets.get("Ascendant", {})
        asc_sign_num = asc_data.get("sign_num", 0)

        if not asc_sign_num:
            return yogas

        asc_sign = asc_sign_num - 1  # Convert to 0-indexed

        # Get house lords
        lagna_lord = self._get_house_lord(1, asc_sign)
        lord_5th = self._get_house_lord(5, asc_sign)
        lord_9th = self._get_house_lord(9, asc_sign)

        # Get their positions
        lagna_lord_data = planets.get(lagna_lord, {})
        lord_5th_data = planets.get(lord_5th, {})
        lord_9th_data = planets.get(lord_9th, {})

        lagna_lord_house = lagna_lord_data.get("house", 0)
        lord_5th_house = lord_5th_data.get("house", 0)
        lord_9th_house = lord_9th_data.get("house", 0)

        kendra_houses = [1, 4, 7, 10]
        trikona_houses = [1, 5, 9]
        kendra_trikona = list(set(kendra_houses + trikona_houses))

        # Helper: Check if planet is strong
        def is_planet_strong(planet_name: str) -> bool:
            planet_data = planets.get(planet_name, {})
            sign_num = planet_data.get("sign_num", 0)

            # Check exaltation
            if planet_data.get("exalted", False):
                return True

            # Check own sign
            own_signs = self.OWN_SIGNS.get(planet_name, [])
            if sign_num in own_signs:
                return True

            # Check friendly sign (simplified)
            # Jupiter, Venus, Mercury are natural benefics - generally strong
            if planet_name in ["Jupiter", "Venus", "Mercury"]:
                return True

            return False

        # Helper: Check mutual aspect/conjunction
        def are_in_relationship(house1: int, house2: int) -> tuple[bool, str]:
            """Check if two houses have Kendra/Trikona relationship or aspect"""
            if house1 == 0 or house2 == 0:
                return False, ""

            # Same house (conjunction)
            if house1 == house2:
                return True, "conjunction"

            # Kendra relationship (1-4-7-10 cycle)
            diff = abs(house1 - house2)
            if diff in [3, 6, 9]:
                return True, "kendra"

            # Trikona relationship (1-5-9 cycle)
            if diff in [4, 8]:
                return True, "trikona"

            # 7th aspect (opposition)
            if diff == 6:
                return True, "7th aspect"

            # Mars 4th & 8th aspects
            if diff in [3, 7]:
                return True, "Mars aspect"

            # Jupiter 5th & 9th aspects
            if diff in [4, 8]:
                return True, "Jupiter aspect"

            # Saturn 3rd & 10th aspects
            if diff in [2, 9]:
                return True, "Saturn aspect"

            return False, ""

        # 1. VAAPI YOGA (Dharma Lords Type)
        # 5th and 9th lords in mutual Kendra/Trikona or aspect/conjunction and strong
        if lord_5th_house and lord_9th_house:
            in_relationship, rel_type = are_in_relationship(lord_5th_house, lord_9th_house)
            lord_5th_strong = is_planet_strong(lord_5th)
            lord_9th_strong = is_planet_strong(lord_9th)

            if in_relationship:
                # Determine strength
                if lord_5th_strong and lord_9th_strong:
                    strength = "Strong"
                    strength_desc = "both lords strong"
                elif lord_5th_strong or lord_9th_strong:
                    strength = "Medium"
                    strength_desc = "one lord strong"
                else:
                    strength = "Weak"
                    strength_desc = "lords not strong"

                yogas.append({
                    "name": "Vaapi Yoga (Dharma Lords)",
                    "description": f"5th lord ({lord_5th}) and 9th lord ({lord_9th}) in {rel_type}, {strength_desc} - Fortune through education, righteous actions, spiritual merit, ethical wealth, grace of dharma",
                    "strength": strength,
                    "category": "Dharma & Fortune",
                    "importance": "major" if strength in ["Strong", "Medium"] else "moderate",
                    "impact": "positive",
                    "formation": f"5th house lord {lord_5th} in {lord_5th_house}th, 9th house lord {lord_9th} in {lord_9th_house}th ({rel_type})"
                })

        # 2. LAKSHMI YOGA (Classical BPHS)
        # Lagna lord in Kendra/Trikona AND strong benefic in 9th/5th house
        if lagna_lord_house in kendra_trikona:
            # Check for strong benefics in 5th or 9th house
            benefics = ["Jupiter", "Venus", "Mercury"]
            strong_benefics_in_dharma = []

            for benefic in benefics:
                benefic_data = planets.get(benefic, {})
                benefic_house = benefic_data.get("house", 0)

                if benefic_house in [5, 9] and is_planet_strong(benefic):
                    strong_benefics_in_dharma.append((benefic, benefic_house))

            if strong_benefics_in_dharma:
                benefic_names = ", ".join([f"{b[0]} in {b[1]}th" for b in strong_benefics_in_dharma])

                yogas.append({
                    "name": "Lakshmi Yoga",
                    "description": f"Lagna lord ({lagna_lord}) in {lagna_lord_house}th (Kendra/Trikona) with strong benefic(s) {benefic_names} - Goddess Lakshmi's blessings, wealth, prosperity, luxury, beauty, royal comforts, fortunate life",
                    "strength": "Strong",
                    "category": "Wealth & Prosperity",
                    "importance": "major",
                    "impact": "positive",
                    "formation": f"Lagna lord {lagna_lord} in {lagna_lord_house}th house with strong benefic(s) in dharma houses"
                })

        # 3. PARIJATA YOGA
        # Lagna lord strong in Kendra/Trikona
        if lagna_lord_house in kendra_trikona:
            lagna_lord_strong = is_planet_strong(lagna_lord)

            if lagna_lord_strong:
                yogas.append({
                    "name": "Parijata Yoga",
                    "description": f"Strong Lagna lord ({lagna_lord}) in {lagna_lord_house}th house (Kendra/Trikona) - Fame, honor, happiness, righteous conduct, enjoyment of pleasures, celestial tree of desires fulfilled",
                    "strength": "Strong",
                    "category": "Fame & Honor",
                    "importance": "major",
                    "impact": "positive",
                    "formation": f"Lagna lord {lagna_lord} strong in {lagna_lord_house}th house (Kendra/Trikona)"
                })

        return yogas

    def _detect_neecha_bhanga(self, planets: Dict) -> List[Dict]:
        """
        Neecha Bhanga Raj Yoga: Debilitated planet's dispositor is strong
        Cancellation of debilitation creates powerful results
        """
        yogas = []

        for planet, deb_sign in self.DEBILITATION_SIGNS.items():
            planet_data = planets.get(planet, {})
            if planet_data.get("sign_num") == deb_sign:
                # Check if dispositor is exalted or in Kendra
                # Simplified: just note the debilitation cancellation potential
                yogas.append({
                    "name": "Neecha Bhanga Raj Yoga",
                    "description": f"{planet} debilitation cancellation potential - difficulties transform into exceptional results",
                    "strength": "Strong",
                    "category": "Transformation"
                })

        return yogas

    def _detect_vesi_yoga(self, planets: Dict) -> List[Dict]:
        """
        Vesi Yoga: Planet (except Moon) in 2nd from Sun
        Brings wealth, good speech, ethical nature
        """
        yogas = []
        sun_house = planets.get("Sun", {}).get("house", 0)

        for planet in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            if planet == "Moon":
                continue
            planet_house = planets.get(planet, {}).get("house", 0)
            if (planet_house - sun_house) % 12 == 1:  # 2nd house (1 ahead)
                yogas.append({
                    "name": "Vesi Yoga",
                    "description": f"{planet} in 2nd from Sun - wealth, fame, good character, ethical nature, respect",
                    "strength": "Medium",
                    "category": "Sun-Based Yogas",
                    "importance": "major",
                    "impact": "positive"
                })
                break

        return yogas

    def _detect_vosi_yoga(self, planets: Dict) -> List[Dict]:
        """
        Vosi Yoga: Planet (except Moon) in 12th from Sun
        Brings skills, authority, good character
        """
        yogas = []
        sun_house = planets.get("Sun", {}).get("house", 0)

        for planet in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            if planet == "Moon":
                continue
            planet_house = planets.get(planet, {}).get("house", 0)
            if (planet_house - sun_house) % 12 == 11:  # 12th house (11 ahead in 0-indexed)
                yogas.append({
                    "name": "Vosi Yoga",
                    "description": f"{planet} in 12th from Sun - skills, authority, independence, self-confidence, leadership",
                    "strength": "Medium",
                    "category": "Sun-Based Yogas",
                    "importance": "major",
                    "impact": "positive"
                })
                break

        return yogas

    def _detect_ubhayachari_yoga(self, planets: Dict) -> List[Dict]:
        """
        Ubhayachari Yoga: Planets on both sides of Sun (2nd and 12th)
        Brings wealth, fame, learning
        """
        yogas = []
        sun_house = planets.get("Sun", {}).get("house", 0)

        has_planet_before = False
        has_planet_after = False

        for planet in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            if planet == "Moon":
                continue
            planet_house = planets.get(planet, {}).get("house", 0)
            if (planet_house - sun_house) % 12 == 11:
                has_planet_before = True
            if (planet_house - sun_house) % 12 == 1:
                has_planet_after = True

        if has_planet_before and has_planet_after:
            yogas.append({
                "name": "Ubhayachari Yoga",
                "description": "Planets on both sides of Sun - wealth, fame, eloquence, balanced nature, royal honors (combines Vesi and Vosi benefits)",
                "strength": "Strong",
                "category": "Sun-Based Yogas",
                "importance": "major",
                "impact": "positive"
            })

        return yogas

    def _detect_sunapha_yoga(self, planets: Dict) -> List[Dict]:
        """
        Sunapha Yoga: Planet (except Sun) in 2nd from Moon
        Brings wealth, fame, intelligence
        """
        yogas = []
        moon_house = planets.get("Moon", {}).get("house", 0)

        for planet in ["Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            if planet == "Sun":
                continue
            planet_house = planets.get(planet, {}).get("house", 0)
            if (planet_house - moon_house) % 12 == 1:
                yogas.append({
                    "name": "Sunapha Yoga",
                    "description": f"{planet} in 2nd from Moon - self-made wealth, intelligence, prosperity, comfort, policy-making abilities",
                    "strength": "Medium",
                    "category": "Moon-Based Yogas",
                    "importance": "major",
                    "impact": "positive"
                })
                break

        return yogas

    def _detect_anapha_yoga(self, planets: Dict) -> List[Dict]:
        """
        Anapha Yoga: Planet (except Sun) in 12th from Moon
        Brings happiness, fame, good health
        """
        yogas = []
        moon_house = planets.get("Moon", {}).get("house", 0)

        for planet in ["Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            if planet == "Sun":
                continue
            planet_house = planets.get(planet, {}).get("house", 0)
            if (planet_house - moon_house) % 12 == 11:
                yogas.append({
                    "name": "Anapha Yoga",
                    "description": f"{planet} in 12th from Moon - fame, good health, ornaments, comfort, renown, well-formed body",
                    "strength": "Medium",
                    "category": "Moon-Based Yogas",
                    "importance": "major",
                    "impact": "positive"
                })
                break

        return yogas

    def _detect_durudhura_yoga(self, planets: Dict) -> List[Dict]:
        """
        Durudhura Yoga: Planets on both sides of Moon (2nd and 12th)
        Brings wealth, conveyances, comfort
        """
        yogas = []
        moon_house = planets.get("Moon", {}).get("house", 0)

        has_planet_before = False
        has_planet_after = False

        for planet in ["Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            if planet == "Sun":
                continue
            planet_house = planets.get(planet, {}).get("house", 0)
            if (planet_house - moon_house) % 12 == 11:
                has_planet_before = True
            if (planet_house - moon_house) % 12 == 1:
                has_planet_after = True

        if has_planet_before and has_planet_after:
            yogas.append({
                "name": "Durudhura Yoga",
                "description": "Planets on both sides of Moon - royal status, wealth, vehicles, attendants, comforts, balanced mind (combines Sunapha and Anapha benefits)",
                "strength": "Strong",
                "category": "Moon-Based Yogas",
                "importance": "major",
                "impact": "positive"
            })

        return yogas

    def _detect_kemadruma_yoga(self, planets: Dict) -> List[Dict]:
        """
        Kemadruma Yoga (inauspicious): No planets on either side of Moon
        Can indicate struggles, though other factors can cancel it
        """
        yogas = []
        moon_house = planets.get("Moon", {}).get("house", 0)

        planets_around_moon = []
        for planet in ["Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            planet_house = planets.get(planet, {}).get("house", 0)
            house_diff = (planet_house - moon_house) % 12
            if house_diff in [1, 11]:  # 2nd or 12th from Moon
                planets_around_moon.append(planet)

        if len(planets_around_moon) == 0:
            yogas.append({
                "name": "Kemadruma Yoga",
                "description": "Moon isolated (no planets in 2nd/12th) - potential struggles, need for self-reliance (can be canceled by other factors)",
                "strength": "Weak",
                "category": "Challenge"
            })

        return yogas

    def _detect_budhaditya_yoga(self, planets: Dict) -> List[Dict]:
        """
        Budhaditya Yoga: Sun-Mercury conjunction (enhanced version)
        Brings intelligence, communication skills, learning ability
        """
        yogas = []
        sun_house = planets.get("Sun", {}).get("house", 0)
        mercury_house = planets.get("Mercury", {}).get("house", 0)

        if sun_house == mercury_house:
            # Enhanced: check if in good houses
            if sun_house in [1, 2, 4, 5, 7, 9, 10, 11]:
                strength = "Medium" if sun_house in [1, 5, 10] else "Weak"
                yogas.append({
                    "name": "Budhaditya Yoga",
                    "description": "Sun-Mercury conjunction - sharp intelligence, communication skills, business acumen, learning ability",
                    "strength": strength,
                    "category": "Intelligence"
                })

        return yogas

    def _detect_nipuna_yoga(self, planets: Dict) -> List[Dict]:
        """
        Nipuna Yoga: Mercury and Jupiter in Kendra/Trikona from each other
        Brings exceptional skills, expertise, mastery
        """
        yogas = []
        mercury_house = planets.get("Mercury", {}).get("house", 0)
        jupiter_house = planets.get("Jupiter", {}).get("house", 0)

        house_diff = (jupiter_house - mercury_house) % 12
        if house_diff in [0, 3, 4, 6, 8, 9]:  # Kendra (0,3,6,9) or Trikona (0,4,8)
            yogas.append({
                "name": "Nipuna Yoga",
                "description": "Mercury-Jupiter in favorable positions - exceptional skills, expertise, scholarly nature",
                "strength": "Medium",
                "category": "Skills & Learning"
            })

        return yogas

    def _detect_kala_sarpa_yoga(self, planets: Dict) -> List[Dict]:
        """
        Kala Sarpa Yoga (Kaal Sarp Dosha): All 7 planets hemmed between Rahu-Ketu axis
        12 types based on Rahu's house position
        Brings intense karmic lessons, obstacles followed by breakthroughs
        """
        yogas = []

        # Get Rahu and Ketu positions
        rahu_house = planets.get("Rahu", {}).get("house", 0)
        ketu_house = planets.get("Ketu", {}).get("house", 0)

        if not rahu_house or not ketu_house:
            return yogas

        # Ketu should be opposite to Rahu (7 houses apart)
        if (ketu_house - rahu_house) % 12 != 6:
            return yogas

        # Check if all 7 planets are between Rahu and Ketu
        # Planets should be in houses from Rahu to Ketu (clockwise)
        main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        all_between_rahu_ketu = True
        partial_between = 0

        for planet_name in main_planets:
            planet_house = planets.get(planet_name, {}).get("house", 0)
            if not planet_house:
                continue

            # Calculate if planet is between Rahu and Ketu (clockwise from Rahu)
            distance_from_rahu = (planet_house - rahu_house) % 12
            if distance_from_rahu == 0 or distance_from_rahu >= 6:
                # Planet is not strictly between Rahu and Ketu
                all_between_rahu_ketu = False
            else:
                partial_between += 1

        # Kala Sarpa Yoga: All planets between Rahu-Ketu
        # Partial Kala Sarpa: 5-6 planets between
        if not all_between_rahu_ketu and partial_between < 5:
            return yogas

        # Determine the type based on Rahu's house
        types = {
            1: ("Anant Kala Sarpa", "Affects health, longevity - obstacles in self-development", "Medium"),
            2: ("Kulik Kala Sarpa", "Affects wealth, family - financial ups and downs", "Medium"),
            3: ("Vasuki Kala Sarpa", "Affects siblings, courage - relationship challenges with brothers/sisters", "Medium"),
            4: ("Shankhpal Kala Sarpa", "Affects mother, property - emotional challenges, property disputes", "Strong"),
            5: ("Padma Kala Sarpa", "Affects children, creativity - delays in childbirth, speculative losses", "Strong"),
            6: ("Mahapadma Kala Sarpa", "Affects enemies, health - chronic health issues, hidden enemies", "Very Strong"),
            7: ("Takshak Kala Sarpa", "Affects spouse, partnerships - marital discord, business partnership issues", "Very Strong"),
            8: ("Karkotak Kala Sarpa", "Affects longevity, transformation - sudden changes, accidents, inheritance issues", "Very Strong"),
            9: ("Shankhachud Kala Sarpa", "Affects father, dharma - obstacles in spiritual growth, father's health", "Strong"),
            10: ("Ghatak Kala Sarpa", "Affects career, status - professional setbacks, authority conflicts", "Very Strong"),
            11: ("Vishdhar Kala Sarpa", "Affects gains, social circle - financial losses, unreliable friends", "Strong"),
            12: ("Sheshnag Kala Sarpa", "Affects expenses, liberation - excessive spending, foreign troubles, spiritual seeking", "Strong")
        }

        yoga_type, effects, strength = types.get(rahu_house, ("Unknown Type", "Effects vary", "Medium"))

        if all_between_rahu_ketu:
            yogas.append({
                "name": f"Kala Sarpa Yoga - {yoga_type}",
                "description": f"{effects}. All planets hemmed between Rahu (H{rahu_house}) and Ketu (H{ketu_house}). Brings intense karmic lessons, initial struggles followed by significant breakthroughs after age 42. Requires dedication, patience, and spiritual practices",
                "strength": strength,
                "category": "Transformation"
            })
        else:
            # Partial Kala Sarpa Yoga
            yogas.append({
                "name": f"Partial Kala Sarpa Yoga - {yoga_type}",
                "description": f"{effects}. {partial_between}/7 planets between Rahu-Ketu axis. Milder effects than full Kala Sarpa. Some karmic challenges but more manageable",
                "strength": "Weak" if partial_between == 5 else "Medium",
                "category": "Transformation"
            })

        return yogas

    def _detect_nabhasa_ashraya_yogas(self, planets: Dict) -> List[Dict]:
        """
        Nabhasa Ashraya Yogas (4 types) - Based on planetary occupancy in signs
        1. Rajju - All planets in movable signs (Aries, Cancer, Libra, Capricorn)
        2. Musala - All planets in fixed signs (Taurus, Leo, Scorpio, Aquarius)
        3. Nala - All planets in dual signs (Gemini, Virgo, Sagittarius, Pisces)
        4. Maala - All planets scattered in different sign types
        """
        yogas = []

        movable_signs = [1, 4, 7, 10]  # Aries, Cancer, Libra, Capricorn
        fixed_signs = [2, 5, 8, 11]    # Taurus, Leo, Scorpio, Aquarius
        dual_signs = [3, 6, 9, 12]     # Gemini, Virgo, Sagittarius, Pisces

        main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        in_movable = 0
        in_fixed = 0
        in_dual = 0

        for planet in main_planets:
            sign_num = planets.get(planet, {}).get("sign_num", 0)
            if sign_num in movable_signs:
                in_movable += 1
            elif sign_num in fixed_signs:
                in_fixed += 1
            elif sign_num in dual_signs:
                in_dual += 1

        # Rajju Yoga - All in movable
        if in_movable == 7:
            yogas.append({
                "name": "Rajju Yoga",
                "description": "All planets in movable signs - Active, travels frequently, wandering nature, restless but successful through movement",
                "strength": "Strong",
                "category": "Nabhasa - Ashraya"
            })

        # Musala Yoga - All in fixed
        elif in_fixed == 7:
            yogas.append({
                "name": "Musala Yoga",
                "description": "All planets in fixed signs - Stable, determined, wealthy, leadership qualities, patient and persistent",
                "strength": "Strong",
                "category": "Nabhasa - Ashraya"
            })

        # Nala Yoga - All in dual
        elif in_dual == 7:
            yogas.append({
                "name": "Nala Yoga",
                "description": "All planets in dual signs - Versatile, adaptable, skilled in multiple areas, diplomatic but indecisive",
                "strength": "Strong",
                "category": "Nabhasa - Ashraya"
            })

        # Maala Yoga - Mixed placement
        elif in_movable >= 2 and in_fixed >= 2 and in_dual >= 2:
            yogas.append({
                "name": "Maala Yoga",
                "description": "Planets distributed across all sign types - Balanced personality, enjoys comforts, multiple talents, moderate wealth",
                "strength": "Medium",
                "category": "Nabhasa - Ashraya"
            })

        return yogas

    def _detect_nabhasa_dala_yogas(self, planets: Dict) -> List[Dict]:
        """
        Nabhasa Dala Yogas (2 types) - Based on benefic/malefic distribution
        1. Mala - Benefics in kendras
        2. Sarpa - Malefics in kendras
        """
        yogas = []

        benefics = ["Jupiter", "Venus", "Mercury"]  # Mercury is considered benefic when alone
        malefics = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
        kendras = [1, 4, 7, 10]

        benefics_in_kendra = sum(1 for p in benefics if planets.get(p, {}).get("house", 0) in kendras)
        malefics_in_kendra = sum(1 for p in malefics if planets.get(p, {}).get("house", 0) in kendras)

        # Mala Yoga - All benefics in kendras
        if benefics_in_kendra == 3:
            yogas.append({
                "name": "Mala Yoga",
                "description": "All benefics in kendras - Virtuous, wealthy, enjoys luxuries, respected, happy family life",
                "strength": "Strong",
                "category": "Nabhasa - Dala"
            })

        # Sarpa Yoga - All malefics in kendras
        if malefics_in_kendra >= 4:  # At least 4 out of 5 malefics
            yogas.append({
                "name": "Sarpa Yoga",
                "description": "Malefics in kendras - Struggles, obstacles, cunning nature, gains through effort, sudden ups and downs",
                "strength": "Medium",
                "category": "Nabhasa - Dala"
            })

        return yogas

    def _detect_nabhasa_akriti_yogas(self, planets: Dict) -> List[Dict]:
        """
        Complete 20 Nabhasa Akriti Yogas - Based on planetary patterns/shapes
        According to BPHS classification
        """
        yogas = []

        main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        occupied_houses = sorted(list(set([planets.get(p, {}).get("house", 0) for p in main_planets if planets.get(p, {}).get("house", 0) > 0])))

        if len(occupied_houses) == 0:
            return yogas

        # Get benefics and malefics
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
        malefics = ["Sun", "Mars", "Saturn"]
        benefic_houses = [planets.get(p, {}).get("house", 0) for p in benefics if planets.get(p, {}).get("house", 0)]
        malefic_houses = [planets.get(p, {}).get("house", 0) for p in malefics if planets.get(p, {}).get("house", 0)]

        # 1. Gola Yoga - All planets in one house
        if len(occupied_houses) == 1:
            yogas.append({
                "name": "Gola Yoga",
                "description": "All planets in one house - Intense focus, specialized skills, poverty early then prosperity, concentrated energy",
                "strength": "Medium",
                "category": "Nabhasa - Akriti"
            })

        # 2. Yuga Yoga - All planets in houses 1-4
        if len(occupied_houses) >= 2 and occupied_houses[0] >= 1 and occupied_houses[-1] <= 4:
            yogas.append({
                "name": "Yuga Yoga",
                "description": "All planets in first quadrant (H1-4) - Religious nature, charitable deeds, respected in society, spiritual tendencies",
                "strength": "Strong",
                "category": "Nabhasa - Akriti"
            })

        # 3. Shola Yoga - All planets in houses 5-8
        if len(occupied_houses) >= 2 and occupied_houses[0] >= 5 and occupied_houses[-1] <= 8:
            yogas.append({
                "name": "Shola Yoga",
                "description": "All planets in second quadrant (H5-8) - Courageous, argumentative, wealthy through effort, leadership qualities",
                "strength": "Strong",
                "category": "Nabhasa - Akriti"
            })

        # 4. Halaka/Hal Yoga - No planets in kendras (1,4,7,10)
        kendra_houses = [1, 4, 7, 10]
        trikona_houses = [1, 5, 9]  # Trinal houses for Chaapa Yoga
        if not any(h in kendra_houses for h in occupied_houses):
            yogas.append({
                "name": "Hal Yoga",
                "description": "No planets in kendras - Agricultural pursuits, farming, land-related work, hardworking nature",
                "strength": "Medium",
                "category": "Nabhasa - Akriti"
            })

        # 5. Vajra Yoga - All in 1st & 7th OR benefics in all kendras
        if set(occupied_houses) == {1, 7} or (all(h in kendra_houses for h in benefic_houses) and len(benefic_houses) == 4):
            yogas.append({
                "name": "Vajra Yoga (Nabhasa)",
                "description": "Planets in 1st & 7th or benefics in all kendras - Strong personality, success in early and late life, diamond-like strength",
                "strength": "Very Strong",
                "category": "Nabhasa - Akriti"
            })

        # 6. Yava Yoga - All in 1st & 4th OR 1st & 10th
        if set(occupied_houses) == {1, 4} or set(occupied_houses) == {1, 10}:
            yogas.append({
                "name": "Yava Yoga",
                "description": "Planets in angular houses from lagna - Middle life prosperity, charitable, religious observances",
                "strength": "Strong",
                "category": "Nabhasa - Akriti"
            })

        # 7. Kamala/Padma Yoga - All planets in kendras
        if len(occupied_houses) >= 2 and all(h in kendra_houses for h in occupied_houses):
            yogas.append({
                "name": "Kamala Yoga",
                "description": "All planets in kendras (1,4,7,10) - Fame, wealth, long life, royal honors, lotus-like grace",
                "strength": "Very Strong",
                "category": "Nabhasa - Akriti"
            })

        # 8. Vaapi Yoga - All in Panaphar (2,5,8,11) OR Apoklima (3,6,9,12), NO Kendras
        # Classical BPHS: Well of wealth yoga
        panaphar_houses = [2, 5, 8, 11]  # Succedent houses
        apoklima_houses = [3, 6, 9, 12]  # Cadent houses
        # Check that NO planets are in Kendras (1,4,7,10)
        no_kendras = not any(h in kendra_houses for h in occupied_houses)

        if no_kendras and len(occupied_houses) >= 2:
            # All in Panaphar OR all in Apoklima
            if all(h in panaphar_houses for h in occupied_houses) or \
               all(h in apoklima_houses for h in occupied_houses):
                yogas.append({
                    "name": "Vaapi Yoga",
                    "description": "All planets in Panaphar (2,5,8,11) or Apoklima (3,6,9,12), no Kendras - Well of wealth, accumulation, secretive nature, supportive relationships, high position through hard work",
                    "strength": "Strong",
                    "category": "Nabhasa - Akriti",
                    "importance": "major",  # Wealth-giving yoga
                    "impact": "positive"
                })

        # 9. Yupa Yoga - All from lagna to 4th house
        if len(occupied_houses) >= 2 and occupied_houses[0] == 1 and occupied_houses[-1] <= 4:
            yogas.append({
                "name": "Yupa Yoga",
                "description": "Planets from 1st to 4th house - Religious sacrifices, spiritual practices, revered for rituals",
                "strength": "Medium",
                "category": "Nabhasa - Akriti"
            })

        # 10. Ishwara Yoga - All from lagna to 7th house
        if len(occupied_houses) >= 2 and occupied_houses[0] == 1 and occupied_houses[-1] <= 7:
            yogas.append({
                "name": "Ishwara Yoga",
                "description": "Planets from 1st to 7th house - Lordship qualities, authority, ministerial positions, wealth",
                "strength": "Strong",
                "category": "Nabhasa - Akriti"
            })

        # 11. Shakti Yoga - All in 7 consecutive signs/houses
        if len(occupied_houses) >= 7:
            for i in range(len(occupied_houses) - 6):
                if occupied_houses[i+6] - occupied_houses[i] == 6:  # 7 consecutive
                    yogas.append({
                        "name": "Shakti Yoga",
                        "description": "7 planets in consecutive houses - Cowardice in youth, courage in old age, lazy but successful",
                        "strength": "Medium",
                        "category": "Nabhasa - Akriti"
                    })
                    break

        # 12. Danda Yoga - All in 6 consecutive houses
        if len(occupied_houses) >= 6:
            for i in range(len(occupied_houses) - 5):
                if occupied_houses[i+5] - occupied_houses[i] == 5:  # 6 consecutive
                    yogas.append({
                        "name": "Danda Yoga",
                        "description": "6 planets in consecutive houses - Staff/stick pattern, serving others, moderate income",
                        "strength": "Medium",
                        "category": "Nabhasa - Akriti"
                    })
                    break

        # 13. Naukaa Yoga - All in 7 consecutive houses from a kendra
        if len(occupied_houses) >= 7:
            for kendra in kendra_houses:
                houses_from_kendra = [(h - kendra) % 12 for h in occupied_houses]
                if max(houses_from_kendra) - min(houses_from_kendra) <= 6:
                    yogas.append({
                        "name": "Naukaa Yoga",
                        "description": "7 planets in boat pattern from kendra - Water/ship related work, travel, trade voyages",
                        "strength": "Medium",
                        "category": "Nabhasa - Akriti"
                    })
                    break

        # 14. Koota Yoga - All in 4th, 8th, and 12th houses (dusthanas)
        dusthana_houses = [4, 8, 12]  # Note: 4th is also kendra but in some contexts considered dusthana
        if len(occupied_houses) >= 2 and all(h in dusthana_houses for h in occupied_houses):
            yogas.append({
                "name": "Koota Yoga",
                "description": "Planets in dusthana houses (4,8,12) - Deceptive nature, imprisonment, confinement, secrecy",
                "strength": "Weak",
                "category": "Nabhasa - Akriti"
            })

        # 15. Chatra/Chhatra Yoga - All planets from 10th house
        if occupied_houses[0] == 10 and len(occupied_houses) >= 2:
            yogas.append({
                "name": "Chatra Yoga",
                "description": "Planets from 10th house onwards - Royal canopy, rulership, authority, happiness in early life",
                "strength": "Strong",
                "category": "Nabhasa - Akriti"
            })

        # 16. Chaapa/Dhanu Yoga - All in trikona houses (1,5,9)
        if len(occupied_houses) >= 2 and all(h in trikona_houses for h in occupied_houses):
            yogas.append({
                "name": "Chaapa Yoga",
                "description": "All in trikonas (1,5,9) - Bow/archer pattern, wandering, incarceration in middle age, final success",
                "strength": "Medium",
                "category": "Nabhasa - Akriti"
            })

        # 17. Ardha Chandra Yoga - All in 7 houses from lagna
        if len(occupied_houses) >= 4 and occupied_houses[0] == 1 and (occupied_houses[-1] - occupied_houses[0]) == len(occupied_houses) - 1 and len(occupied_houses) == 7:
            yogas.append({
                "name": "Ardha Chandra Yoga",
                "description": "7 planets spread in half-moon pattern from lagna - Handsome, famous, commanding, head of army",
                "strength": "Strong",
                "category": "Nabhasa - Akriti"
            })

        # 18. Chakra Yoga - All planets in kendra and trikona only
        kendra_trikona = [1, 4, 5, 7, 9, 10]
        if len(occupied_houses) >= 4 and all(h in kendra_trikona for h in occupied_houses):
            yogas.append({
                "name": "Chakra Yoga",
                "description": "Planets in kendras and trikonas - Sovereign ruler, powerful leader, tremendous authority, wheel pattern",
                "strength": "Very Strong",
                "category": "Nabhasa - Akriti"
            })

        # 19. Samudra Yoga - All in 6 consecutive signs
        if len(occupied_houses) >= 6:
            for i in range(len(occupied_houses) - 5):
                if occupied_houses[i+5] - occupied_houses[i] == 5:
                    yogas.append({
                        "name": "Samudra Yoga",
                        "description": "6 planets in consecutive houses - Ocean of wealth, treasure accumulation, generous",
                        "strength": "Strong",
                        "category": "Nabhasa - Akriti"
                    })
                    break

        # 20. Dama Yoga - Planets in consecutive houses (general)
        if len(occupied_houses) >= 3:
            consecutive = all(occupied_houses[i+1] - occupied_houses[i] == 1 for i in range(len(occupied_houses)-1))
            if consecutive and len(occupied_houses) < 6:  # Not already covered by Danda or Shakti
                yogas.append({
                    "name": "Dama Yoga",
                    "description": "Planets in consecutive houses - Charitable, helpful nature, gains through service, moderate wealth",
                    "strength": "Medium",
                    "category": "Nabhasa - Akriti"
                })

        # NEW NABHASA AKRITI YOGAS - BPHS IDs 6-31

        # ID 6: Gada Yoga - All planets in two successive kendras
        successive_kendra_pairs = [(1,4), (4,7), (7,10), (10,1)]
        for k1, k2 in successive_kendra_pairs:
            if len(occupied_houses) >= 2 and set(occupied_houses).issubset({k1, k2}):
                yogas.append({
                    "name": "Gada Yoga",
                    "description": f"All planets in two successive kendras ({k1}th & {k2}th) - Club-like strength, success through partnerships, gains through joint efforts",
                    "strength": "Strong",
                    "category": "Nabhasa - Akriti"
                })
                break

        # ID 7: Sakata Yoga (Nabhasa) - All planets only in 1st and 7th
        # Note: Different from rare Shakata yoga (Moon-Jupiter)
        if len(occupied_houses) >= 2 and set(occupied_houses) == {1, 7}:
            # Check if not already added as Vajra
            if not any(y["name"] == "Vajra Yoga (Nabhasa)" for y in yogas):
                yogas.append({
                    "name": "Sakata Yoga (Nabhasa)",
                    "description": "All planets only in 1st and 7th houses - Cart-wheel pattern, ups and downs in life, gains through persistence",
                    "strength": "Medium",
                    "category": "Nabhasa - Akriti"
                })

        # ID 8: Vihaga Yoga - All planets only in 4th and 10th
        if len(occupied_houses) >= 2 and set(occupied_houses) == {4, 10}:
            yogas.append({
                "name": "Vihaga Yoga",
                "description": "All planets only in 4th and 10th houses - Bird-like movement, travel, messenger, diplomatic success",
                "strength": "Strong",
                "category": "Nabhasa - Akriti"
            })

        # ID 9: Śṛṅgāṭaka Yoga - All planets only in trikonas (1, 5, 9)
        if len(occupied_houses) >= 2 and set(occupied_houses).issubset(trikona_houses):
            # Check if not already covered by Chaapa
            if not any(y["name"] == "Chaapa Yoga" for y in yogas):
                yogas.append({
                    "name": "Śṛṅgāṭaka Yoga",
                    "description": "All planets only in trikonas (1,5,9) - Crossroads of fortune, righteous living, religious authority, spiritual leadership",
                    "strength": "Very Strong",
                    "category": "Nabhasa - Akriti"
                })

        # ID 10: Hala Yoga (Corrected BPHS version) - All in Trishadaya sets
        # Trishadaya: (2,6,10) or (3,7,11) or (4,8,12)
        trishadaya_sets = [
            ([2, 6, 10], "2nd-6th-10th"),
            ([3, 7, 11], "3rd-7th-11th"),
            ([4, 8, 12], "4th-8th-12th")
        ]

        for tri_set, tri_desc in trishadaya_sets:
            if len(occupied_houses) >= 2 and set(occupied_houses).issubset(tri_set):
                yogas.append({
                    "name": "Hala Yoga (Corrected)",
                    "description": f"All planets in {tri_desc} (Trishadaya) - Plough pattern, agricultural success, land-related wealth, hardworking nature",
                    "strength": "Medium",
                    "category": "Nabhasa - Akriti"
                })
                break

        # IDs 11-12: Corrected Benefic/Malefic Kendra patterns
        # ID 11: Vajra (Corrected) - All benefics in 1&7 OR all malefics in 4&10
        benefic_in_17 = all(h in [1, 7] for h in benefic_houses) and len(benefic_houses) >= 3
        malefic_in_410 = all(h in [4, 10] for h in malefic_houses) and len(malefic_houses) >= 2

        if benefic_in_17 or malefic_in_410:
            pattern = "benefics in 1&7" if benefic_in_17 else "malefics in 4&10"
            yogas.append({
                "name": "Vajra Yoga (BPHS Corrected)",
                "description": f"All {pattern} - Diamond strength, invincible in conflicts, lasting success",
                "strength": "Very Strong",
                "category": "Nabhasa - Akriti"
            })

        # ID 12: Yava (Corrected) - All benefics in 4&10 OR all malefics in 1&7
        benefic_in_410 = all(h in [4, 10] for h in benefic_houses) and len(benefic_houses) >= 3
        malefic_in_17 = all(h in [1, 7] for h in malefic_houses) and len(malefic_houses) >= 2

        if benefic_in_410 or malefic_in_17:
            pattern = "benefics in 4&10" if benefic_in_410 else "malefics in 1&7"
            yogas.append({
                "name": "Yava Yoga (BPHS Corrected)",
                "description": f"All {pattern} - Barley grain pattern, prosperity in middle life, charitable deeds",
                "strength": "Strong",
                "category": "Nabhasa - Akriti"
            })

        # IDs 15-18: Spread Patterns (BPHS Corrected) - 7 planets spread over quadrants
        if len([p for p in main_planets if planets.get(p, {}).get("house", 0) > 0]) == 7:

            # ID 15: Yupa (Corrected) - 7 planets spread over houses 1-4
            if all(1 <= h <= 4 for h in occupied_houses):
                yogas.append({
                    "name": "Yupa Yoga (BPHS)",
                    "description": "7 planets spread over 1st-4th houses - Sacrificial post, religious authority, ritualistic success",
                    "strength": "Medium",
                    "category": "Nabhasa - Akriti"
                })

            # ID 16: Śara - 7 planets spread over houses 4-7
            elif all(4 <= h <= 7 for h in occupied_houses):
                yogas.append({
                    "name": "Śara Yoga",
                    "description": "7 planets spread over 4th-7th houses - Arrow pattern, goal-oriented, success through partnerships",
                    "strength": "Medium",
                    "category": "Nabhasa - Akriti"
                })

            # ID 17: Śakti (Corrected) - 7 planets spread over houses 7-10
            elif all(7 <= h <= 10 for h in occupied_houses):
                yogas.append({
                    "name": "Śakti Yoga (BPHS)",
                    "description": "7 planets spread over 7th-10th houses - Spear pattern, powerful authority, career success, combative strength",
                    "strength": "Strong",
                    "category": "Nabhasa - Akriti"
                })

            # ID 18: Daṇḍa (Corrected) - 7 planets spread over houses 10-1 (wrapping)
            elif all(h in [10, 11, 12, 1] for h in occupied_houses):
                yogas.append({
                    "name": "Daṇḍa Yoga (BPHS)",
                    "description": "7 planets spread over 10th-1st houses (wrapping) - Staff pattern, authority through discipline, administrative success",
                    "strength": "Medium",
                    "category": "Nabhasa - Akriti"
                })

        # IDs 19-22: Consecutive House Patterns (BPHS Corrected)
        if len([p for p in main_planets if planets.get(p, {}).get("house", 0) > 0]) == 7:

            # ID 19: Nauka (Corrected) - 7 consecutive from house 1
            consecutive_from_1 = list(range(1, 8))
            if all(h in consecutive_from_1 for h in occupied_houses):
                yogas.append({
                    "name": "Nauka Yoga (BPHS)",
                    "description": "7 consecutive houses starting from 1st - Boat pattern, water-related success, trade voyages",
                    "strength": "Medium",
                    "category": "Nabhasa - Akriti"
                })

            # ID 20: Kūṭa (Corrected) - 7 consecutive from house 4
            consecutive_from_4 = list(range(4, 11))
            if all(h in consecutive_from_4 for h in occupied_houses):
                yogas.append({
                    "name": "Kūṭa Yoga (BPHS)",
                    "description": "7 consecutive houses starting from 4th - Heap/pile pattern, accumulation of wealth, property success",
                    "strength": "Medium",
                    "category": "Nabhasa - Akriti"
                })

            # ID 21: Chatra (Corrected) - 7 consecutive from house 7
            consecutive_from_7 = list(range(7, 14))  # Will be modulo 12
            occupied_adjusted = [(h - 7) for h in occupied_houses]
            if all(0 <= adj <= 6 for adj in occupied_adjusted):
                yogas.append({
                    "name": "Chatra Yoga (BPHS)",
                    "description": "7 consecutive houses starting from 7th - Umbrella/canopy pattern, royal protection, success in partnerships",
                    "strength": "Strong",
                    "category": "Nabhasa - Akriti"
                })

            # ID 22: Dhanus/Chāpa (Corrected) - 7 consecutive from house 10
            consecutive_from_10 = [10, 11, 12, 1, 2, 3, 4]
            if all(h in consecutive_from_10 for h in occupied_houses):
                yogas.append({
                    "name": "Dhanus Yoga (BPHS)",
                    "description": "7 consecutive houses starting from 10th - Bow pattern, career authority, leadership, focused ambition",
                    "strength": "Strong",
                    "category": "Nabhasa - Akriti"
                })

        # IDs 23-24: Alternate Sign Patterns (BPHS Corrected)

        # ID 23: Chakra (Corrected) - 6 alternate signs from Lagna
        # Alternate means: Lagna, Lagna+2, Lagna+4, Lagna+6, Lagna+8, Lagna+10
        # In houses: odd houses (1,3,5,7,9,11) OR even houses (2,4,6,8,10,12)
        all_odd = all(h % 2 == 1 for h in occupied_houses)
        all_even = all(h % 2 == 0 for h in occupied_houses)

        if (all_odd or all_even) and len(occupied_houses) >= 6:
            pattern = "odd houses (1,3,5,7,9,11)" if all_odd else "even houses (2,4,6,8,10,12)"
            yogas.append({
                "name": "Chakra Yoga (BPHS)",
                "description": f"6+ planets in alternate signs ({pattern}) - Wheel of fortune, sovereign power, universal authority",
                "strength": "Very Strong",
                "category": "Nabhasa - Akriti"
            })

        # ID 24: Samudra (Corrected) - 6 alternate signs from 2nd house
        # Starting from 2nd: 2,4,6,8,10,12 (even) or shifted pattern
        # Simplified: Check if 6+ planets in specific alternate pattern
        if all_even and len(occupied_houses) >= 6:
            yogas.append({
                "name": "Samudra Yoga (BPHS)",
                "description": "6+ planets in alternate even houses - Ocean pattern, vast wealth, treasure accumulation, generous nature",
                "strength": "Strong",
                "category": "Nabhasa - Akriti"
            })

        return yogas

    def _detect_rare_yogas(self, planets: Dict) -> List[Dict]:
        """
        Rare but important yogas:
        - Shakata Yoga
        - Shrinatha Yoga
        - Kusuma Yoga
        - Matsya Yoga
        - Kurma Yoga
        """
        yogas = []

        # Shakata Yoga - Moon in 6/8/12 from Jupiter
        moon_house = planets.get("Moon", {}).get("house", 0)
        jupiter_house = planets.get("Jupiter", {}).get("house", 0)

        if moon_house and jupiter_house:
            house_diff = (moon_house - jupiter_house) % 12
            if house_diff in [5, 7, 11]:  # 6th, 8th, 12th from Jupiter
                yogas.append({
                    "name": "Shakata Yoga",
                    "description": "Moon in 6/8/12 from Jupiter - Financial ups and downs, cart-wheel life, gains through perseverance",
                    "strength": "Weak",
                    "category": "Challenge"
                })

        # Shrinatha Yoga - Lord of exaltation in kendra
        # Simplified: Venus (exalted lord of Pisces/Jupiter sign) in kendra
        venus_house = planets.get("Venus", {}).get("house", 0)
        if venus_house in [1, 4, 7, 10]:
            yogas.append({
                "name": "Shrinatha Yoga",
                "description": "Venus in kendra - Wealth, comforts, vehicles, luxurious lifestyle, royal treatment",
                "strength": "Strong",
                "category": "Wealth & Comfort"
            })

        # Kusuma Yoga - Jupiter in lagna, Moon/Venus in 7th
        jupiter_house = planets.get("Jupiter", {}).get("house", 0)
        moon_house = planets.get("Moon", {}).get("house", 0)
        venus_house = planets.get("Venus", {}).get("house", 0)

        if jupiter_house == 1 and (moon_house == 7 or venus_house == 7):
            yogas.append({
                "name": "Kusuma Yoga",
                "description": "Jupiter in 1st, Moon/Venus in 7th - Fame, respect, learned, wealthy, authority position",
                "strength": "Very Strong",
                "category": "Fame & Authority"
            })

        # Matsya Yoga - All planets in 1st-7th houses
        main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        all_in_first_half = all(1 <= planets.get(p, {}).get("house", 0) <= 7 for p in main_planets if planets.get(p, {}).get("house", 0) > 0)

        if all_in_first_half and sum(1 for p in main_planets if planets.get(p, {}).get("house", 0) > 0) >= 6:
            yogas.append({
                "name": "Matsya Yoga",
                "description": "Planets concentrated in 1-7 houses - Righteous, charitable, enjoys comforts, fish-like adaptability",
                "strength": "Medium",
                "category": "Fame & Character"
            })

        # Kurma Yoga - All planets in 4th-10th houses
        all_in_middle_half = all(4 <= planets.get(p, {}).get("house", 0) <= 10 for p in main_planets if planets.get(p, {}).get("house", 0) > 0)

        if all_in_middle_half and sum(1 for p in main_planets if planets.get(p, {}).get("house", 0) > 0) >= 6:
            yogas.append({
                "name": "Kurma Yoga",
                "description": "Planets concentrated in 4-10 houses - Patient, determined, steady progress, turtle-like perseverance, long-lasting gains",
                "strength": "Medium",
                "category": "Wealth & Character"
            })

        return yogas

    # ============================================================================
    # NEW YOGA DETECTION METHODS - Phase 1, 2, 3
    # ============================================================================

    def _detect_gajakesari_yoga(self, planets: Dict) -> List[Dict]:
        """
        Gajakesari Yoga: Jupiter in Kendra (1,4,7,10) from Moon
        One of the most auspicious yogas - brings wisdom, wealth, fame, eloquence
        """
        yogas = []
        moon_house = planets.get("Moon", {}).get("house", 0)
        jupiter_house = planets.get("Jupiter", {}).get("house", 0)

        if not moon_house or not jupiter_house:
            return yogas

        # Calculate house difference (kendra = 1,4,7,10 from Moon)
        house_diff = (jupiter_house - moon_house) % 12

        # Check if Jupiter is in kendra from Moon (0, 3, 6, 9 houses away = 1st, 4th, 7th, 10th)
        if house_diff in [0, 3, 6, 9]:
            # Calculate strength based on Jupiter's dignity
            strength = self._calculate_yoga_strength(["Jupiter", "Moon"], planets)

            # Check for cancellation
            is_cancelled, cancel_reasons = self._check_yoga_cancellation(["Jupiter", "Moon"], planets)

            # Build description
            kendra_name = ["same house", "4th", "7th", "10th"][house_diff // 3] if house_diff != 0 else "conjunction"
            base_desc = f"Jupiter in kendra from Moon ({kendra_name}) - wisdom, fame, prosperity, virtuous nature, good speech, learning"

            if is_cancelled:
                base_desc += f" [CANCELLED: {'; '.join(cancel_reasons)}]"
                strength = "Weak"
            elif cancel_reasons:
                base_desc += f" [WEAKENED: {'; '.join(cancel_reasons)}]"

            yogas.append({
                "name": "Gajakesari Yoga",
                "description": base_desc,
                "strength": strength,
                "category": "Raja Yoga"
            })

        return yogas

    def _detect_raj_yoga_kendra_trikona(self, planets: Dict) -> List[Dict]:
        """
        Raj Yoga (Kendra-Trikona): Simplified version
        Classical: Lords of Kendra (1,4,7,10) with lords of Trikona (1,5,9)
        Simplified: Benefics in both Kendra and Trikona houses simultaneously
        """
        yogas = []
        kendra_houses = [1, 4, 7, 10]
        trikona_houses = [1, 5, 9]
        benefics = ["Jupiter", "Venus", "Mercury"]

        # Check for benefics well-placed in both kendra and trikona
        benefics_in_kendra = []
        benefics_in_trikona = []

        for planet in benefics:
            house = planets.get(planet, {}).get("house", 0)
            if house in kendra_houses:
                benefics_in_kendra.append(planet)
            if house in trikona_houses:
                benefics_in_trikona.append(planet)

        # Raj Yoga forms when benefics occupy both kendra and trikona
        if len(benefics_in_kendra) >= 1 and len(benefics_in_trikona) >= 1:
            forming_planets = list(set(benefics_in_kendra + benefics_in_trikona))
            strength = self._calculate_yoga_strength(forming_planets, planets)

            yogas.append({
                "name": "Raj Yoga (Kendra-Trikona)",
                "description": f"Benefics in Kendra ({', '.join(benefics_in_kendra)}) and Trikona ({', '.join(benefics_in_trikona)}) - power, status, authority, leadership, prosperity",
                "strength": strength,
                "category": "Raja Yoga"
            })

        return yogas

    def _detect_grahan_yoga(self, planets: Dict) -> List[Dict]:
        """
        Grahan Yoga (Eclipse Yoga): Sun or Moon conjunct with Rahu or Ketu
        Indicates karmic challenges, psychological issues, spiritual potential
        """
        yogas = []

        sun_house = planets.get("Sun", {}).get("house", 0)
        moon_house = planets.get("Moon", {}).get("house", 0)
        rahu_house = planets.get("Rahu", {}).get("house", 0)
        ketu_house = planets.get("Ketu", {}).get("house", 0)

        # Sun-Rahu conjunction (Solar Eclipse)
        if sun_house and rahu_house and sun_house == rahu_house:
            yogas.append({
                "name": "Grahan Yoga (Solar Eclipse)",
                "description": f"Sun-Rahu conjunction in house {sun_house} - challenges with father/authority, ego struggles, spiritual awakening through identity crisis, potential for occult knowledge",
                "strength": "Strong",
                "category": "Eclipse Yoga"
            })

        # Sun-Ketu conjunction
        if sun_house and ketu_house and sun_house == ketu_house:
            yogas.append({
                "name": "Grahan Yoga (Solar Eclipse - Ketu)",
                "description": f"Sun-Ketu conjunction in house {sun_house} - detachment from ego, spiritual inclination, challenges with father, enlightenment through self-dissolution",
                "strength": "Medium",
                "category": "Eclipse Yoga"
            })

        # Moon-Rahu conjunction (Lunar Eclipse)
        if moon_house and rahu_house and moon_house == rahu_house:
            yogas.append({
                "name": "Grahan Yoga (Lunar Eclipse)",
                "description": f"Moon-Rahu conjunction in house {moon_house} - emotional turbulence, mental restlessness, challenges with mother, obsessive thinking, powerful intuition",
                "strength": "Very Strong",
                "category": "Eclipse Yoga"
            })

        # Moon-Ketu conjunction
        if moon_house and ketu_house and moon_house == ketu_house:
            yogas.append({
                "name": "Grahan Yoga (Lunar Eclipse - Ketu)",
                "description": f"Moon-Ketu conjunction in house {moon_house} - emotional detachment, psychic abilities, past-life memories, spiritual sensitivity, challenges with mother",
                "strength": "Strong",
                "category": "Eclipse Yoga"
            })

        return yogas

    def _detect_dharma_karmadhipati_yoga(self, planets: Dict) -> List[Dict]:
        """
        Dharma-Karmadhipati Yoga: Simplified version
        Classical: 9th and 10th house lords in conjunction or mutual aspect
        Simplified: Benefics in 9th and 10th houses (dharma and karma houses)
        """
        yogas = []
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]

        benefic_in_9th = None
        benefic_in_10th = None

        for planet in benefics:
            house = planets.get(planet, {}).get("house", 0)
            if house == 9:
                benefic_in_9th = planet
            if house == 10:
                benefic_in_10th = planet

        if benefic_in_9th and benefic_in_10th:
            forming_planets = [benefic_in_9th, benefic_in_10th]
            strength = self._calculate_yoga_strength(forming_planets, planets)

            yogas.append({
                "name": "Dharma-Karmadhipati Yoga",
                "description": f"{benefic_in_9th} in 9th (dharma) and {benefic_in_10th} in 10th (karma) - career success, righteous conduct, fame through good deeds, fortune and profession aligned",
                "strength": strength,
                "category": "Raja Yoga"
            })

        return yogas

    def _detect_dhana_yoga(self, planets: Dict) -> List[Dict]:
        """
        Dhana Yoga (Wealth Yoga): Simplified version
        Classical: Lords of 2nd, 5th, 9th, 11th houses in mutual connections
        Simplified: Benefics in wealth houses (2, 5, 9, 11)
        """
        yogas = []
        wealth_houses = [2, 5, 9, 11]
        benefics = ["Jupiter", "Venus", "Mercury"]

        benefics_in_wealth_houses = []
        for planet in benefics:
            house = planets.get(planet, {}).get("house", 0)
            if house in wealth_houses:
                benefics_in_wealth_houses.append((planet, house))

        # Dhana Yoga forms when 2+ benefics are in wealth houses
        if len(benefics_in_wealth_houses) >= 2:
            planet_names = [p[0] for p in benefics_in_wealth_houses]
            house_list = [str(p[1]) for p in benefics_in_wealth_houses]
            strength = self._calculate_yoga_strength(planet_names, planets)

            yogas.append({
                "name": "Dhana Yoga",
                "description": f"Benefics ({', '.join(planet_names)}) in wealth houses ({', '.join(house_list)}) - multiple income sources, financial growth, prosperity through wisdom",
                "strength": strength,
                "category": "Wealth Yoga"
            })

        return yogas

    def _detect_chandal_yoga(self, planets: Dict) -> List[Dict]:
        """
        Chandal Yoga: Jupiter conjunct with Rahu
        Brings unconventional wisdom, challenges to traditional beliefs, spiritual confusion
        Can also indicate genius-level intelligence in unconventional fields
        """
        yogas = []

        jupiter_house = planets.get("Jupiter", {}).get("house", 0)
        rahu_house = planets.get("Rahu", {}).get("house", 0)

        if jupiter_house and rahu_house and jupiter_house == rahu_house:
            jupiter_sign = planets.get("Jupiter", {}).get("sign_num", 0)

            # Check if Jupiter is strong (own sign or exalted) - can mitigate effects
            is_strong = (jupiter_sign in self.OWN_SIGNS.get("Jupiter", []) or
                        jupiter_sign == self.EXALTATION_SIGNS.get("Jupiter"))

            if is_strong:
                desc = f"Jupiter-Rahu conjunction in house {jupiter_house} - unconventional genius, breakthrough thinking, challenges orthodoxy, but Jupiter's strength brings wisdom. Spiritual seeking through unusual paths"
                strength = "Medium"
            else:
                desc = f"Jupiter-Rahu conjunction in house {jupiter_house} - confusion in beliefs, unconventional path, challenges with gurus/teachers, manipulative tendencies, spiritual crisis leading to growth"
                strength = "Strong"

            yogas.append({
                "name": "Chandal Yoga",
                "description": desc,
                "strength": strength,
                "category": "Challenge Yoga"
            })

        return yogas

    def _detect_kubera_yoga(self, planets: Dict) -> List[Dict]:
        """
        Kubera Yoga: Extreme wealth yoga
        Simplified: Jupiter, Venus, and Mercury all strong (in kendra/trikona or exalted)
        """
        yogas = []

        jupiter_house = planets.get("Jupiter", {}).get("house", 0)
        venus_house = planets.get("Venus", {}).get("house", 0)
        mercury_house = planets.get("Mercury", {}).get("house", 0)

        jupiter_sign = planets.get("Jupiter", {}).get("sign_num", 0)
        venus_sign = planets.get("Venus", {}).get("sign_num", 0)
        mercury_sign = planets.get("Mercury", {}).get("sign_num", 0)

        kendra_trikona = [1, 4, 5, 7, 9, 10]

        # Check if all three benefics are strong
        jupiter_strong = (jupiter_house in kendra_trikona or
                         jupiter_sign == self.EXALTATION_SIGNS.get("Jupiter") or
                         jupiter_sign in self.OWN_SIGNS.get("Jupiter", []))

        venus_strong = (venus_house in kendra_trikona or
                       venus_sign == self.EXALTATION_SIGNS.get("Venus") or
                       venus_sign in self.OWN_SIGNS.get("Venus", []))

        mercury_strong = (mercury_house in kendra_trikona or
                         mercury_sign == self.EXALTATION_SIGNS.get("Mercury") or
                         mercury_sign in self.OWN_SIGNS.get("Mercury", []))

        if jupiter_strong and venus_strong and mercury_strong:
            strength = self._calculate_yoga_strength(["Jupiter", "Venus", "Mercury"], planets)

            yogas.append({
                "name": "Kubera Yoga",
                "description": "All three benefics (Jupiter, Venus, Mercury) are strong - exceptional wealth, luxuries, multiple income streams, prosperity like the god of wealth Kubera",
                "strength": strength,
                "category": "Extreme Wealth"
            })

        return yogas

    def _detect_lakshmi_wealth_yogas(self, planets: Dict) -> List[Dict]:
        """
        Lakshmi-Type Wealth Yogas (BPHS IDs 239-253) - 15 variations

        5th and 9th lords (Dharma/Fortune lords) in various strong relationships

        Relationships:
        1. Conjunction
        2. Mutual Aspect
        3. Mutual Kendra
        4. Mutual Trikona
        5. Parivartana (sign exchange)

        Strength conditions:
        - Both strong (own/exalted)
        - One strong, one neutral
        - Both neutral
        """
        yogas = []

        # Get ascendant sign
        asc_sign = self._calculate_ascendant_sign(planets)
        if asc_sign is None:
            return yogas

        # Get 5th and 9th house lords
        lord_5 = self._get_house_lord(5, asc_sign)
        lord_9 = self._get_house_lord(9, asc_sign)

        # Skip if same planet rules both
        if lord_5 == lord_9:
            return yogas

        # Skip if planets don't exist
        if lord_5 not in planets or lord_9 not in planets:
            return yogas

        # Get positions
        lord_5_house = planets[lord_5].get("house", 0)
        lord_9_house = planets[lord_9].get("house", 0)

        if lord_5_house == 0 or lord_9_house == 0:
            return yogas

        # Check strength levels
        lord_5_very_strong = self._check_lord_strength(lord_5, planets, "very_strong")
        lord_5_strong = self._check_lord_strength(lord_5, planets, "strong")
        lord_9_very_strong = self._check_lord_strength(lord_9, planets, "very_strong")
        lord_9_strong = self._check_lord_strength(lord_9, planets, "strong")

        # Determine overall strength category
        if lord_5_very_strong and lord_9_very_strong:
            strength_category = "both exalted"
            base_strength = "Very Strong"
        elif (lord_5_strong or lord_5_very_strong) and (lord_9_strong or lord_9_very_strong):
            strength_category = "both strong"
            base_strength = "Strong"
        elif (lord_5_strong or lord_5_very_strong) or (lord_9_strong or lord_9_very_strong):
            strength_category = "one strong"
            base_strength = "Medium"
        else:
            strength_category = "both neutral"
            base_strength = "Medium"

        # Check each relationship type

        # 1. CONJUNCTION
        if lord_5_house == lord_9_house:
            yogas.append({
                "name": f"Lakshmi Wealth Yoga: 5L-9L Conjunction ({strength_category})",
                "description": f"5th lord ({lord_5}) and 9th lord ({lord_9}) conjoined in {lord_5_house}th house - exceptional fortune and prosperity through combined dharmic energies, multiple wealth streams",
                "strength": base_strength,
                "category": "Wealth Yoga",
                "yoga_forming_planets": [lord_5, lord_9],
                "formation": f"{lord_5} and {lord_9} in {lord_5_house}th house"
            })

        # 2. MUTUAL ASPECT
        if self._check_mutual_aspect(lord_5_house, lord_9_house, planets, lord_5, lord_9):
            yogas.append({
                "name": f"Lakshmi Wealth Yoga: 5L-9L Mutual Aspect ({strength_category})",
                "description": f"5th lord ({lord_5}) in {lord_5_house}th and 9th lord ({lord_9}) in {lord_9_house}th in mutual aspect - wealth through knowledge and fortune, prosperity from righteous actions",
                "strength": base_strength,
                "category": "Wealth Yoga",
                "yoga_forming_planets": [lord_5, lord_9],
                "formation": f"{lord_5} in {lord_5_house}th aspecting {lord_9} in {lord_9_house}th"
            })

        # 3. MUTUAL KENDRA
        house_distance = abs(lord_5_house - lord_9_house)
        if house_distance in [3, 6, 9]:  # 4th, 7th, 10th from each other
            yogas.append({
                "name": f"Lakshmi Wealth Yoga: 5L-9L Mutual Kendra ({strength_category})",
                "description": f"5th lord ({lord_5}) and 9th lord ({lord_9}) in mutual kendra - stable wealth accumulation, fortunate career, prosperity through structured approach",
                "strength": base_strength,
                "category": "Wealth Yoga",
                "yoga_forming_planets": [lord_5, lord_9],
                "formation": f"{lord_5} in {lord_5_house}th, {lord_9} in {lord_9_house}th (mutual kendra)"
            })

        # 4. MUTUAL TRIKONA
        if house_distance in [4, 8]:  # 5th, 9th from each other
            yogas.append({
                "name": f"Lakshmi Wealth Yoga: 5L-9L Mutual Trikona ({strength_category})",
                "description": f"5th lord ({lord_5}) and 9th lord ({lord_9}) in mutual trikona - fortunate wealth, blessings from ancestors, prosperity through dharma",
                "strength": base_strength,
                "category": "Wealth Yoga",
                "yoga_forming_planets": [lord_5, lord_9],
                "formation": f"{lord_5} in {lord_5_house}th, {lord_9} in {lord_9_house}th (mutual trikona)"
            })

        # 5. PARIVARTANA
        if self._check_parivartana(lord_5, lord_9, planets):
            strength_modifier = "Very Strong" if base_strength == "Strong" else "Strong"
            yogas.append({
                "name": f"Lakshmi Wealth Yoga: 5L-9L Parivartana ({strength_category})",
                "description": f"5th lord ({lord_5}) and 9th lord ({lord_9}) in sign exchange - exceptional wealth through fortune, dharmic prosperity, blessings manifest powerfully",
                "strength": strength_modifier,
                "category": "Wealth Yoga",
                "yoga_forming_planets": [lord_5, lord_9],
                "formation": f"{lord_5} and {lord_9} in mutual sign exchange"
            })

        return yogas

    def _detect_ascendant_wealth_yogas(self, planets: Dict) -> List[Dict]:
        """
        Ascendant-Specific Wealth Yogas (BPHS IDs 224-237) - 14 variations

        Specific planetary combinations that create wealth for each ascendant

        Simplified implementation focusing on major patterns
        """
        yogas = []

        # Get ascendant sign
        asc_sign = self._calculate_ascendant_sign(planets)
        if asc_sign is None:
            return yogas

        # Ascendant-specific wealth patterns
        # These are highly specific to each ascendant

        # Aries Ascendant (asc_sign = 0)
        if asc_sign == 0:
            # Mars (Lagna lord) with Sun & Jupiter
            mars_house = planets.get("Mars", {}).get("house", 0)
            sun_house = planets.get("Sun", {}).get("house", 0)
            jupiter_house = planets.get("Jupiter", {}).get("house", 0)

            if mars_house and (mars_house == sun_house or mars_house == jupiter_house):
                yogas.append({
                    "name": "Aries Wealth Yoga",
                    "description": "Mars (Lagna lord) with Sun/Jupiter - wealth through courage, leadership, military/sports, Mars-ruled professions",
                    "strength": "Strong",
                    "category": "Wealth Yoga - Ascendant Specific"
                })

        # Taurus Ascendant (asc_sign = 1)
        elif asc_sign == 1:
            # Venus strong, with Mercury & Saturn
            venus_house = planets.get("Venus", {}).get("house", 0)
            if venus_house and self._check_lord_strength("Venus", planets, "strong"):
                yogas.append({
                    "name": "Taurus Wealth Yoga",
                    "description": "Strong Venus (Lagna lord) - wealth through arts, beauty, luxury goods, Venusian professions, material comforts",
                    "strength": "Strong",
                    "category": "Wealth Yoga - Ascendant Specific"
                })

        # Gemini Ascendant (asc_sign = 2)
        elif asc_sign == 2:
            # Mercury with Venus
            mercury_house = planets.get("Mercury", {}).get("house", 0)
            venus_house = planets.get("Venus", {}).get("house", 0)

            if mercury_house and venus_house and mercury_house == venus_house:
                yogas.append({
                    "name": "Gemini Wealth Yoga",
                    "description": "Mercury (Lagna lord) with Venus - wealth through communication, business, trade, intellectual pursuits",
                    "strength": "Strong",
                    "category": "Wealth Yoga - Ascendant Specific"
                })

        # Cancer Ascendant (asc_sign = 3)
        elif asc_sign == 3:
            # Moon with Jupiter & Mercury
            moon_house = planets.get("Moon", {}).get("house", 0)
            jupiter_house = planets.get("Jupiter", {}).get("house", 0)

            if moon_house and jupiter_house and abs(moon_house - jupiter_house) <= 1:
                yogas.append({
                    "name": "Cancer Wealth Yoga",
                    "description": "Moon (Lagna lord) with Jupiter - wealth through nurturing, care professions, real estate, emotional intelligence",
                    "strength": "Strong",
                    "category": "Wealth Yoga - Ascendant Specific"
                })

        # Leo Ascendant (asc_sign = 4)
        elif asc_sign == 4:
            # Sun with Mars & Jupiter
            sun_house = planets.get("Sun", {}).get("house", 0)
            mars_house = planets.get("Mars", {}).get("house", 0)
            jupiter_house = planets.get("Jupiter", {}).get("house", 0)

            if sun_house and (sun_house == mars_house or sun_house == jupiter_house):
                yogas.append({
                    "name": "Leo Wealth Yoga",
                    "description": "Sun (Lagna lord) with Mars/Jupiter - wealth through authority, government, leadership, royal professions",
                    "strength": "Very Strong",
                    "category": "Wealth Yoga - Ascendant Specific"
                })

        # Virgo Ascendant (asc_sign = 5)
        elif asc_sign == 5:
            # Mercury strong in own sign
            mercury_sign = planets.get("Mercury", {}).get("sign_num", 0)
            if mercury_sign == 6:  # Virgo
                yogas.append({
                    "name": "Virgo Wealth Yoga",
                    "description": "Mercury (Lagna lord) in Virgo - wealth through analysis, service, health professions, detailed work",
                    "strength": "Strong",
                    "category": "Wealth Yoga - Ascendant Specific"
                })

        # Libra Ascendant (asc_sign = 6)
        elif asc_sign == 6:
            # Venus with Saturn & Mercury
            venus_house = planets.get("Venus", {}).get("house", 0)
            saturn_house = planets.get("Saturn", {}).get("house", 0)

            if venus_house and saturn_house and abs(venus_house - saturn_house) <= 1:
                yogas.append({
                    "name": "Libra Wealth Yoga",
                    "description": "Venus (Lagna lord) with Saturn - wealth through law, justice, balanced partnerships, diplomatic work",
                    "strength": "Strong",
                    "category": "Wealth Yoga - Ascendant Specific"
                })

        # Scorpio Ascendant (asc_sign = 7)
        elif asc_sign == 7:
            # Mars with Moon
            mars_house = planets.get("Mars", {}).get("house", 0)
            moon_house = planets.get("Moon", {}).get("house", 0)

            if mars_house and moon_house and mars_house == moon_house:
                yogas.append({
                    "name": "Scorpio Wealth Yoga",
                    "description": "Mars (Lagna lord) with Moon - wealth through transformation, research, occult sciences, investigation",
                    "strength": "Strong",
                    "category": "Wealth Yoga - Ascendant Specific"
                })

        # Sagittarius Ascendant (asc_sign = 8)
        elif asc_sign == 8:
            # Jupiter in own sign or exalted
            jupiter_sign = planets.get("Jupiter", {}).get("sign_num", 0)
            if jupiter_sign in [4, 9, 12]:  # Cancer (exalted), Sagittarius, Pisces
                yogas.append({
                    "name": "Sagittarius Wealth Yoga",
                    "description": "Jupiter (Lagna lord) in own/exalted sign - wealth through wisdom, teaching, philosophy, higher education",
                    "strength": "Very Strong",
                    "category": "Wealth Yoga - Ascendant Specific"
                })

        # Capricorn Ascendant (asc_sign = 9)
        elif asc_sign == 9:
            # Saturn with Venus & Mercury
            saturn_house = planets.get("Saturn", {}).get("house", 0)
            venus_house = planets.get("Venus", {}).get("house", 0)

            if saturn_house and venus_house and abs(saturn_house - venus_house) <= 1:
                yogas.append({
                    "name": "Capricorn Wealth Yoga",
                    "description": "Saturn (Lagna lord) with Venus - wealth through discipline, long-term investments, structured business, persistence",
                    "strength": "Strong",
                    "category": "Wealth Yoga - Ascendant Specific"
                })

        # Aquarius Ascendant (asc_sign = 10)
        elif asc_sign == 10:
            # Saturn with Mercury
            saturn_house = planets.get("Saturn", {}).get("house", 0)
            mercury_house = planets.get("Mercury", {}).get("house", 0)

            if saturn_house and mercury_house and saturn_house == mercury_house:
                yogas.append({
                    "name": "Aquarius Wealth Yoga",
                    "description": "Saturn (Lagna lord) with Mercury - wealth through innovation, technology, networking, humanitarian work",
                    "strength": "Strong",
                    "category": "Wealth Yoga - Ascendant Specific"
                })

        # Pisces Ascendant (asc_sign = 11)
        elif asc_sign == 11:
            # Jupiter with Venus & Moon
            jupiter_house = planets.get("Jupiter", {}).get("house", 0)
            moon_house = planets.get("Moon", {}).get("house", 0)

            if jupiter_house and moon_house and abs(jupiter_house - moon_house) <= 1:
                yogas.append({
                    "name": "Pisces Wealth Yoga",
                    "description": "Jupiter (Lagna lord) with Moon - wealth through spirituality, healing, creative arts, compassionate work",
                    "strength": "Strong",
                    "category": "Wealth Yoga - Ascendant Specific"
                })

        return yogas

    def _detect_penury_yogas(self, planets: Dict) -> List[Dict]:
        """
        Penury/Poverty Yogas (BPHS Ch.42 - IDs 262-277) - 16 variations

        Yogas indicating financial difficulties, poverty, or obstacles
        These balance the chart analysis by showing challenges alongside opportunities

        Categories:
        1. Dusthana-based poverty (parivartana, placements, afflictions)
        2. 2nd house afflictions (wealth house damaged)
        3. Dharma lords afflicted
        4. Malefic distributions

        Note: Some advanced indicators requiring Navamsa/Dasha are deferred
        """
        yogas = []

        # Get ascendant sign
        asc_sign = self._calculate_ascendant_sign(planets)
        if asc_sign is None:
            return yogas

        # Get house lords
        lord_1 = self._get_house_lord(1, asc_sign)
        lord_2 = self._get_house_lord(2, asc_sign)
        lord_6 = self._get_house_lord(6, asc_sign)
        lord_8 = self._get_house_lord(8, asc_sign)
        lord_12 = self._get_house_lord(12, asc_sign)
        lord_5 = self._get_house_lord(5, asc_sign)
        lord_9 = self._get_house_lord(9, asc_sign)
        lord_7 = self._get_house_lord(7, asc_sign)

        # Maraka lords (2nd and 7th lords - death inflictors, also wealth destroyers)
        maraka_lords = [lord_2, lord_7]

        # Dusthana lords (6, 8, 12 - houses of obstacles, losses, expenses)
        dusthana_lords = [lord_6, lord_8, lord_12]

        # Malefic planets
        malefics = ["Mars", "Saturn", "Rahu", "Ketu"]

        # Benefic planets
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]

        # Get planetary data
        lord_1_house = planets.get(lord_1, {}).get("house", 0)
        lord_1_sign = planets.get(lord_1, {}).get("sign_num", 0)
        lord_2_sign = planets.get(lord_2, {}).get("sign_num", 0)
        lord_6_sign = planets.get(lord_6, {}).get("sign_num", 0)
        lord_12_sign = planets.get(lord_12, {}).get("sign_num", 0)
        lord_5_house = planets.get(lord_5, {}).get("house", 0)
        lord_9_house = planets.get(lord_9, {}).get("house", 0)

        # ====== PATTERN 1: Parivartana with Maraka (IDs 262-263) ======

        # ID 262: 1L-12L parivartana with maraka influence
        if lord_1 != lord_12:
            lord_1_in_12th_sign = (lord_1_sign == (asc_sign + 11) % 12)
            lord_12_in_1st_sign = (lord_12_sign == asc_sign)

            if lord_1_in_12th_sign and lord_12_in_1st_sign:
                # Check if either is maraka lord or aspected by maraka
                is_maraka_involved = (lord_1 in maraka_lords or lord_12 in maraka_lords)

                yogas.append({
                    "name": "Daridra Yoga - Lagna-Vyaya Parivartana",
                    "description": f"{lord_1} and {lord_12} exchange signs (1st-12th parivartana) - loss of vitality, expenses exceed income, wealth dissipation" +
                                   (" with maraka influence (severe)" if is_maraka_involved else ""),
                    "strength": "Strong" if is_maraka_involved else "Medium",
                    "category": "Penury Yoga - Parivartana"
                })

        # ID 263: 1L-6L parivartana with maraka influence
        if lord_1 != lord_6:
            lord_1_in_6th_sign = (lord_1_sign == (asc_sign + 5) % 12)
            lord_6_in_1st_sign = (lord_6_sign == asc_sign)

            if lord_1_in_6th_sign and lord_6_in_1st_sign:
                is_maraka_involved = (lord_1 in maraka_lords or lord_6 in maraka_lords)

                yogas.append({
                    "name": "Daridra Yoga - Lagna-Ripu Parivartana",
                    "description": f"{lord_1} and {lord_6} exchange signs (1st-6th parivartana) - chronic debts, enemies, litigation, health expenses" +
                                   (" with maraka influence (severe)" if is_maraka_involved else ""),
                    "strength": "Strong" if is_maraka_involved else "Medium",
                    "category": "Penury Yoga - Parivartana"
                })

        # ====== PATTERN 2: Dusthana Placements of Lagna Lord (IDs 264-266) ======

        # ID 264: 1L with Ketu or in 8th house
        ketu_house = planets.get("Ketu", {}).get("house", 0)

        if lord_1_house == ketu_house and ketu_house > 0:
            yogas.append({
                "name": "Daridra Yoga - Lagna Lord with Ketu",
                "description": f"{lord_1} conjunct Ketu - loss of direction, spiritual detachment from wealth, sudden unexpected losses",
                "strength": "Medium",
                "category": "Penury Yoga - Affliction"
            })

        if lord_1_house == 8:
            yogas.append({
                "name": "Daridra Yoga - Lagna Lord in 8th",
                "description": f"{lord_1} in 8th house - chronic obstacles, sudden transformations, inheritance issues, hidden financial drains",
                "strength": "Medium",
                "category": "Penury Yoga - Affliction"
            })

        # ID 265: 1L with malefic in dusthana (6/8/12) AND 2L debilitated
        if lord_1_house in [6, 8, 12]:
            # Check if 1L is with any malefic
            malefic_in_same_house = False
            for malefic in malefics:
                if malefic != lord_1:  # Don't count if 1L itself is malefic
                    malefic_house = planets.get(malefic, {}).get("house", 0)
                    if malefic_house == lord_1_house:
                        malefic_in_same_house = True
                        break

            # Check if 2L is debilitated
            lord_2_debilitated = planets.get(lord_2, {}).get("debilitated", False)

            if malefic_in_same_house and lord_2_debilitated:
                yogas.append({
                    "name": "Daridra Yoga - Lagna Lord Afflicted, Dhana Lord Fallen",
                    "description": f"{lord_1} with malefic in dusthana ({lord_1_house}th) AND {lord_2} debilitated - severe financial struggles, difficulty earning and retaining wealth",
                    "strength": "Very Strong",
                    "category": "Penury Yoga - Affliction"
                })

        # ID 266: 1L with 6/8/12 lords without benefic aspect
        if lord_1_house > 0:
            # Check if 1L is with dusthana lords
            with_dusthana_lord = False
            for dusthana_lord in dusthana_lords:
                if dusthana_lord != lord_1:
                    dusthana_lord_house = planets.get(dusthana_lord, {}).get("house", 0)
                    if dusthana_lord_house == lord_1_house:
                        with_dusthana_lord = True
                        break

            if with_dusthana_lord:
                # Check for benefic aspect (simplified - check if any benefic in kendra from 1L)
                has_benefic_aspect = False
                for benefic in benefics:
                    benefic_house = planets.get(benefic, {}).get("house", 0)
                    if benefic_house > 0:
                        house_diff = abs(benefic_house - lord_1_house)
                        # Kendra aspect (1st, 4th, 7th, 10th from 1L's position)
                        if house_diff in [0, 3, 6, 9]:
                            has_benefic_aspect = True
                            break

                if not has_benefic_aspect:
                    yogas.append({
                        "name": "Daridra Yoga - Lagna Lord with Dusthana Lords",
                        "description": f"{lord_1} with dusthana lords without benefic protection - obstacles from enemies, debts, hidden matters without relief",
                        "strength": "Strong",
                        "category": "Penury Yoga - Affliction"
                    })

        # ====== PATTERN 3: Dharma Lords Afflicted (ID 267) ======

        # ID 267: 5L in 6th AND 9L in 12th with maraka aspects
        if lord_5_house == 6 and lord_9_house == 12:
            # Check maraka aspects (simplified - check if maraka lords in same house as 5L or 9L)
            maraka_aspect_5L = any(planets.get(maraka, {}).get("house", 0) == 6 for maraka in maraka_lords if maraka != lord_5)
            maraka_aspect_9L = any(planets.get(maraka, {}).get("house", 0) == 12 for maraka in maraka_lords if maraka != lord_9)

            if maraka_aspect_5L or maraka_aspect_9L:
                yogas.append({
                    "name": "Daridra Yoga - Dharma Lords Afflicted",
                    "description": f"{lord_5} in 6th and {lord_9} in 12th with maraka influence - loss of past merit, spiritual obstacles, difficulties with children and fortune",
                    "strength": "Very Strong",
                    "category": "Penury Yoga - Dharma Affliction"
                })

        # ====== PATTERN 4: Malefics in Lagna (ID 268) ======

        # ID 268: Malefics (except 9L/10L) in Lagna with maraka
        lord_9 = self._get_house_lord(9, asc_sign)
        lord_10 = self._get_house_lord(10, asc_sign)
        beneficial_lords = [lord_9, lord_10]

        malefics_in_lagna = []
        for malefic in malefics:
            malefic_house = planets.get(malefic, {}).get("house", 0)
            if malefic_house == 1 and malefic not in beneficial_lords:
                malefics_in_lagna.append(malefic)

        if len(malefics_in_lagna) > 0:
            # Check if maraka lords also in Lagna
            maraka_in_lagna = any(planets.get(maraka, {}).get("house", 0) == 1 for maraka in maraka_lords)

            if maraka_in_lagna:
                yogas.append({
                    "name": "Daridra Yoga - Malefics in Lagna with Maraka",
                    "description": f"Malefics ({', '.join(malefics_in_lagna)}) in Lagna with maraka lord - damaged personality, obstacles to self-expression, chronic health/wealth issues",
                    "strength": "Strong",
                    "category": "Penury Yoga - Lagna Affliction"
                })

        # ====== PATTERN 5: Dispositor Chains (ID 269) ======

        # ID 269: Dispositors of 6/8/12 lords also in 6/8/12
        dusthana_in_dusthana_count = 0

        for dusthana_lord in dusthana_lords:
            dusthana_lord_sign = planets.get(dusthana_lord, {}).get("sign_num", 0)
            if dusthana_lord_sign > 0:
                # Get dispositor (lord of the sign the dusthana lord is in)
                dispositor = self._get_sign_lord(dusthana_lord_sign)
                dispositor_house = planets.get(dispositor, {}).get("house", 0)

                if dispositor_house in [6, 8, 12]:
                    dusthana_in_dusthana_count += 1

        if dusthana_in_dusthana_count >= 2:
            yogas.append({
                "name": "Daridra Yoga - Dusthana Chain",
                "description": f"Dispositors of dusthana lords also in dusthana - deep karmic debt patterns, recurring obstacles, difficulty breaking negative cycles",
                "strength": "Strong",
                "category": "Penury Yoga - Dispositor"
            })

        # ====== PATTERN 6: House Distribution (ID 272) ======

        # ID 272: Benefics in bad houses (6/8/12), malefics in good houses (1/5/9)
        benefics_in_bad = []
        malefics_in_good = []

        for benefic in benefics:
            benefic_house = planets.get(benefic, {}).get("house", 0)
            if benefic_house in [6, 8, 12]:
                benefics_in_bad.append(benefic)

        for malefic in malefics:
            malefic_house = planets.get(malefic, {}).get("house", 0)
            if malefic_house in [1, 5, 9]:
                malefics_in_good.append(malefic)

        if len(benefics_in_bad) >= 2 and len(malefics_in_good) >= 2:
            yogas.append({
                "name": "Daridra Yoga - Inverted House Distribution",
                "description": f"Benefics ({', '.join(benefics_in_bad)}) in dusthana, malefics ({', '.join(malefics_in_good)}) in trikonas - reversed fortune, good intentions bring problems, obstacles appear as opportunities",
                "strength": "Strong",
                "category": "Penury Yoga - Distribution"
            })

        # ====== PATTERN 7: 2nd House Afflictions (IDs 276-277) ======

        # ID 276: Mars + Saturn in 2nd house
        mars_house = planets.get("Mars", {}).get("house", 0)
        saturn_house = planets.get("Saturn", {}).get("house", 0)

        if mars_house == 2 and saturn_house == 2:
            yogas.append({
                "name": "Daridra Yoga - Mars-Saturn in 2nd",
                "description": "Mars and Saturn both in 2nd house - harsh speech, family conflicts, difficulty accumulating wealth, blocked income sources",
                "strength": "Strong",
                "category": "Penury Yoga - 2nd House"
            })

        # ID 277: Sun-Saturn mutual aspects
        sun_house = planets.get("Sun", {}).get("house", 0)
        saturn_house = planets.get("Saturn", {}).get("house", 0)

        if sun_house > 0 and saturn_house > 0:
            house_diff = abs(sun_house - saturn_house)
            # Mutual aspect: 7th house aspect (opposition)
            if house_diff == 6:  # 7th house apart
                yogas.append({
                    "name": "Daridra Yoga - Sun-Saturn Opposition",
                    "description": "Sun and Saturn in mutual 7th house aspect - conflict between authority and limitation, father issues, career obstacles, delayed recognition",
                    "strength": "Medium",
                    "category": "Penury Yoga - Aspect"
                })

        # ====== PATTERN 8: Moon Afflictions (IDs 270-271 - D1 Proxy) ======
        # NOTE: Full BPHS implementation requires Navamsa (D9) chart data
        # These are simplified D1-based proxies until D9 integration is added

        # ID 270: Moon afflicted by maraka lords (D1 proxy for Navamsa indicator)
        moon_house = planets.get("Moon", {}).get("house", 0)
        moon_sign = planets.get("Moon", {}).get("sign_num", 0)

        if moon_house > 0 and moon_sign > 0:
            # Check if Moon is with maraka lords or in maraka houses (2nd/7th)
            moon_with_maraka = False
            for maraka in maraka_lords:
                maraka_house = planets.get(maraka, {}).get("house", 0)
                if maraka_house == moon_house:
                    moon_with_maraka = True
                    break

            moon_in_maraka_house = moon_house in [2, 7]

            if moon_with_maraka or moon_in_maraka_house:
                yogas.append({
                    "name": "Daridra Yoga - Moon Afflicted by Maraka",
                    "description": f"Moon {'with maraka lord' if moon_with_maraka else 'in maraka house'} in D1 - mental anxiety about finances, emotional attachment to wealth causing loss (full analysis requires Navamsa)",
                    "strength": "Medium",
                    "category": "Penury Yoga - Moon Affliction"
                })

        # ID 271: Both Lagna lords afflicted (D1 proxy)
        if lord_1_house > 0:
            # Check if Lagna lord is with or aspected by maraka
            lord_1_with_maraka = any(planets.get(maraka, {}).get("house", 0) == lord_1_house
                                      for maraka in maraka_lords if maraka != lord_1)

            # Check if Lagna lord is in maraka house
            lord_1_in_maraka = lord_1_house in [2, 7]

            if lord_1_with_maraka or lord_1_in_maraka:
                yogas.append({
                    "name": "Daridra Yoga - Lagna Lord under Maraka Influence",
                    "description": f"{lord_1} {'with maraka lord' if lord_1_with_maraka else 'in maraka house'} - vitality and prosperity threatened by death-inflicting influences (full analysis requires both D1 and D9)",
                    "strength": "Strong",
                    "category": "Penury Yoga - Lagna Affliction"
                })

        # ====== PATTERN 9: Dasha-Period Indicators (IDs 273-275 - General Proxies) ======
        # NOTE: Full BPHS implementation requires Vimshottari Dasha calculations
        # These check for general afflictions that create problems during planet dashas

        # ID 273-274: Dusthana lord dashas causing financial harm
        # Proxy: Identify planets that will cause financial problems in their dashas
        problematic_dasha_lords = []

        for dusthana_lord in dusthana_lords:
            dusthana_lord_house = planets.get(dusthana_lord, {}).get("house", 0)
            dusthana_lord_debilitated = planets.get(dusthana_lord, {}).get("debilitated", False)

            # Dusthana lord in dusthana + debilitated = very problematic dasha
            if dusthana_lord_house in [6, 8, 12] and dusthana_lord_debilitated:
                problematic_dasha_lords.append(dusthana_lord)

        if len(problematic_dasha_lords) >= 1:
            yogas.append({
                "name": "Daridra Yoga - Afflicted Dusthana Lord Dashas",
                "description": f"Dusthana lords ({', '.join(problematic_dasha_lords)}) debilitated in dusthana - their Mahadasha/Antardasha periods will bring financial difficulties, health issues, legal problems (timing requires Vimshottari Dasha calculation)",
                "strength": "Strong",
                "category": "Penury Yoga - Dasha Indicator"
            })

        # ID 275: Maraka lord dashas with weak wealth houses
        # Proxy: Check if maraka lords are strong while wealth lords (2,5,9,11) are weak
        weak_wealth_houses = []

        for wealth_house in [2, 5, 9, 11]:
            wealth_lord = self._get_house_lord(wealth_house, asc_sign)
            wealth_lord_debilitated = planets.get(wealth_lord, {}).get("debilitated", False)
            wealth_lord_house = planets.get(wealth_lord, {}).get("house", 0)

            if wealth_lord_debilitated or wealth_lord_house in [6, 8, 12]:
                weak_wealth_houses.append(wealth_house)

        maraka_strong = False
        for maraka in maraka_lords:
            maraka_exalted = planets.get(maraka, {}).get("exalted", False)
            maraka_house = planets.get(maraka, {}).get("house", 0)
            if maraka_exalted or maraka_house in [1, 4, 7, 10]:  # kendra
                maraka_strong = True
                break

        if len(weak_wealth_houses) >= 2 and maraka_strong:
            yogas.append({
                "name": "Daridra Yoga - Weak Wealth Lords, Strong Maraka",
                "description": f"Wealth houses ({', '.join(map(str, weak_wealth_houses))}) have weak lords while maraka lords are strong - their dasha periods will drain accumulated wealth, medical expenses, family obligations (timing analysis requires Vimshottari Dasha)",
                "strength": "Medium",
                "category": "Penury Yoga - Dasha Indicator"
                })

        return yogas

    def _detect_royal_association_yogas(self, planets: Dict) -> List[Dict]:
        """
        Royal Association Yogas (BPHS Ch.40 - IDs 208-223) - 16 variations

        Jaimini-based yogas using Atmakaraka (AK) and Amatyakaraka (AmK)
        These yogas indicate royal favor, high status, and political success

        AK = Atmakaraka (Self-significator)
        AmK = Amatyakaraka (Career/Minister-significator)

        Requires Jaimini karaka calculations
        """
        yogas = []

        # Calculate Charakarakas using Jaimini service
        try:
            karakas = self.jaimini.calculate_charakarakas(planets)
        except Exception as e:
            # If karaka calculation fails, skip these yogas
            return yogas

        if not karakas or "AK" not in karakas or "AmK" not in karakas:
            return yogas

        ak_planet = karakas.get("AK")
        amk_planet = karakas.get("AmK")

        # Get ascendant sign
        asc_sign = self._calculate_ascendant_sign(planets)
        if asc_sign is None:
            return yogas

        # Get 10th and 11th house lords
        lord_10 = self._get_house_lord(10, asc_sign)
        lord_11 = self._get_house_lord(11, asc_sign)

        # Get planet data
        ak_house = planets.get(ak_planet, {}).get("house", 0)
        ak_sign = planets.get(ak_planet, {}).get("sign_num", 0)
        ak_exalted = planets.get(ak_planet, {}).get("exalted", False)
        ak_own = ak_sign in self.OWN_SIGNS.get(ak_planet, []) if ak_sign > 0 else False

        amk_house = planets.get(amk_planet, {}).get("house", 0)
        amk_sign = planets.get(amk_planet, {}).get("sign_num", 0)
        amk_exalted = planets.get(amk_planet, {}).get("exalted", False)
        amk_own = amk_sign in self.OWN_SIGNS.get(amk_planet, []) if amk_sign > 0 else False

        lord_10_house = planets.get(lord_10, {}).get("house", 0)
        lord_11_house = planets.get(lord_11, {}).get("house", 0)

        # ID 208: 10L with AmK - Career lord with Minister karaka
        if lord_10_house == amk_house and lord_10_house > 0:
            yogas.append({
                "name": "Raja Yoga - Career Lord with Amatyakaraka",
                "description": f"10th lord ({lord_10}) conjunct Amatyakaraka ({amk_planet}) - professional success through ministerial/executive abilities, career advancement, administrative positions",
                "strength": "Very Strong",
                "category": "Royal Association - Jaimini"
            })

        # ID 209: Clean 10th & 11th houses (no malefics)
        malefics = ["Mars", "Saturn", "Rahu", "Ketu"]
        malefics_in_10 = [p for p in malefics if planets.get(p, {}).get("house", 0) == 10]
        malefics_in_11 = [p for p in malefics if planets.get(p, {}).get("house", 0) == 11]

        if len(malefics_in_10) == 0 and len(malefics_in_11) == 0:
            yogas.append({
                "name": "Raja Yoga - Clean Career & Gains Houses",
                "description": "10th and 11th houses free from malefics - unobstructed career growth, smooth income flow, respected professional reputation",
                "strength": "Strong",
                "category": "Royal Association - Jaimini"
            })

        # ID 210: AmK with AK's dispositor
        if ak_sign > 0:
            ak_dispositor = self._get_sign_lord(ak_sign - 1)  # Convert to 0-indexed
            ak_dispositor_house = planets.get(ak_dispositor, {}).get("house", 0)

            if amk_house == ak_dispositor_house and amk_house > 0:
                yogas.append({
                    "name": "Raja Yoga - AmK with AK Dispositor",
                    "description": f"Amatyakaraka ({amk_planet}) with {ak_planet}'s dispositor ({ak_dispositor}) - career aligned with soul purpose, work supports self-development",
                    "strength": "Strong",
                    "category": "Royal Association - Jaimini"
                })

        # ID 211: AK with benefic planets
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
        benefics_with_ak = []

        if ak_house > 0:
            for benefic in benefics:
                if benefic != ak_planet:
                    benefic_house = planets.get(benefic, {}).get("house", 0)
                    if benefic_house == ak_house:
                        benefics_with_ak.append(benefic)

        if len(benefics_with_ak) >= 1:
            yogas.append({
                "name": "Raja Yoga - Atmakaraka with Benefics",
                "description": f"Atmakaraka ({ak_planet}) with benefics ({', '.join(benefics_with_ak)}) - blessed soul, spiritual support, divine grace in self-development",
                "strength": "Strong",
                "category": "Royal Association - Jaimini"
            })

        # ID 212: AmK in own/exaltation
        if amk_exalted or amk_own:
            state = "exalted" if amk_exalted else "own sign"
            yogas.append({
                "name": "Raja Yoga - Strong Amatyakaraka",
                "description": f"Amatyakaraka ({amk_planet}) in {state} - powerful career karaka, executive excellence, ministerial abilities, professional mastery",
                "strength": "Very Strong",
                "category": "Royal Association - Jaimini"
            })

        # ID 213: AK in trines (1, 5, 9)
        if ak_house in [1, 5, 9]:
            house_names = {1: "Lagna", 5: "5th (children/purva punya)", 9: "9th (dharma/fortune)"}
            yogas.append({
                "name": "Raja Yoga - Atmakaraka in Trikona",
                "description": f"Atmakaraka ({ak_planet}) in {house_names[ak_house]} - soul in dharma houses, righteous path, spiritual growth leads to material success",
                "strength": "Strong",
                "category": "Royal Association - Jaimini"
            })

        # ID 214: AK in kendras (1, 4, 7, 10)
        if ak_house in [1, 4, 7, 10]:
            house_names = {1: "Lagna", 4: "4th (home)", 7: "7th (partnerships)", 10: "10th (career)"}
            yogas.append({
                "name": "Raja Yoga - Atmakaraka in Kendra",
                "description": f"Atmakaraka ({ak_planet}) in {house_names[ak_house]} - strong self-expression, angular power, ability to manifest soul's purpose in world",
                "strength": "Strong",
                "category": "Royal Association - Jaimini"
            })

        # ID 215: AmK in kendras
        if amk_house in [1, 4, 7, 10]:
            house_names = {1: "Lagna", 4: "4th (home)", 7: "7th (partnerships)", 10: "10th (career)"}
            yogas.append({
                "name": "Raja Yoga - Amatyakaraka in Kendra",
                "description": f"Amatyakaraka ({amk_planet}) in {house_names[amk_house]} - career success through angular strength, professional prominence, leadership positions",
                "strength": "Strong",
                "category": "Royal Association - Jaimini"
            })

        # ID 216: AK and AmK in mutual kendras
        if ak_house > 0 and amk_house > 0:
            house_diff = abs(ak_house - amk_house)
            if house_diff in [3, 6, 9]:  # Kendra relationship (1, 4, 7, 10 apart)
                yogas.append({
                    "name": "Raja Yoga - AK-AmK Mutual Kendra",
                    "description": f"Atmakaraka ({ak_planet}) and Amatyakaraka ({amk_planet}) in mutual kendras - soul and career in perfect alignment, self-realization through profession",
                    "strength": "Very Strong",
                    "category": "Royal Association - Jaimini"
                })

        # ID 217: AK exalted
        if ak_exalted:
            yogas.append({
                "name": "Raja Yoga - Exalted Atmakaraka",
                "description": f"Atmakaraka ({ak_planet}) exalted - supreme self-expression, soul at its highest potential, destined for greatness",
                "strength": "Very Strong",
                "category": "Royal Association - Jaimini"
            })

        # ID 218: AK in own sign
        if ak_own:
            yogas.append({
                "name": "Raja Yoga - Atmakaraka in Own Sign",
                "description": f"Atmakaraka ({ak_planet}) in own sign - self-mastery, comfortable with soul's purpose, natural authority in chosen field",
                "strength": "Strong",
                "category": "Royal Association - Jaimini"
            })

        # ID 219: Both AK and AmK strong (exalted or own)
        if (ak_exalted or ak_own) and (amk_exalted or amk_own):
            yogas.append({
                "name": "Raja Yoga - Both Karakas Strong",
                "description": f"Both Atmakaraka ({ak_planet}) and Amatyakaraka ({amk_planet}) in exaltation/own signs - complete success, self and career both empowered, leadership excellence",
                "strength": "Very Strong",
                "category": "Royal Association - Jaimini"
            })

        # ID 220: AmK aspecting 10th house (Jaimini aspects)
        if amk_sign > 0:
            # Convert to 0-indexed for Jaimini aspect calculation
            amk_sign_0indexed = (amk_sign - 1) % 12
            aspected_signs = self.jaimini.calculate_jaimini_aspects(amk_sign_0indexed)

            # Get 10th house sign
            house_10_sign = (asc_sign + 9) % 12  # 10th house from ascendant

            if house_10_sign in aspected_signs:
                yogas.append({
                    "name": "Raja Yoga - AmK Aspects 10th House",
                    "description": f"Amatyakaraka ({amk_planet}) aspects 10th house with Jaimini aspect - career karaka directly influences profession, ministerial success, administrative power",
                    "strength": "Strong",
                    "category": "Royal Association - Jaimini"
                })

        # ID 221: AK and AmK conjunct
        if ak_house == amk_house and ak_house > 0:
            yogas.append({
                "name": "Raja Yoga - AK-AmK Conjunction",
                "description": f"Atmakaraka ({ak_planet}) conjunct Amatyakaraka ({amk_planet}) - soul and career unified, work IS life purpose, complete dedication brings supreme success",
                "strength": "Very Strong",
                "category": "Royal Association - Jaimini"
            })

        # ID 222: AmK in 10th house
        if amk_house == 10:
            yogas.append({
                "name": "Raja Yoga - AmK in 10th House",
                "description": f"Amatyakaraka ({amk_planet}) in 10th house - career karaka in career house, ministerial positions, executive authority, professional eminence",
                "strength": "Very Strong",
                "category": "Royal Association - Jaimini"
            })

        # ID 223: AK in 10th house
        if ak_house == 10:
            yogas.append({
                "name": "Raja Yoga - AK in 10th House",
                "description": f"Atmakaraka ({ak_planet}) in 10th house - soul's purpose IS career, destined for public recognition, self-realization through profession",
                "strength": "Very Strong",
                "category": "Royal Association - Jaimini"
            })

        return yogas

    def _get_house_lord(self, house_num: int, asc_sign: int) -> str:
        """
        Get the planetary lord of a house based on ascendant sign

        Args:
            house_num: House number (1-12)
            asc_sign: Ascendant sign number (0-indexed: 0=Aries, 11=Pisces)

        Returns:
            Planet name that rules the house
        """
        # Calculate which sign rules the house
        # House 1 = Ascendant sign, House 2 = next sign, etc.
        house_sign = (asc_sign + house_num - 1) % 12

        # Sign lordships (0-indexed: 0=Aries, 11=Pisces)
        sign_lords = {
            0: "Mars",      # Aries
            1: "Venus",     # Taurus
            2: "Mercury",   # Gemini
            3: "Moon",      # Cancer
            4: "Sun",       # Leo
            5: "Mercury",   # Virgo
            6: "Venus",     # Libra
            7: "Mars",      # Scorpio
            8: "Jupiter",   # Sagittarius
            9: "Saturn",    # Capricorn
            10: "Saturn",   # Aquarius
            11: "Jupiter"   # Pisces
        }

        return sign_lords.get(house_sign, "Unknown")

    def _get_sign_lord(self, sign_num: int) -> str:
        """
        Get the planetary lord of a zodiac sign

        Args:
            sign_num: Sign number (0-indexed: 0=Aries, 11=Pisces)

        Returns:
            Planet name that rules the sign
        """
        sign_lords = {
            0: "Mars",      # Aries
            1: "Venus",     # Taurus
            2: "Mercury",   # Gemini
            3: "Moon",      # Cancer
            4: "Sun",       # Leo
            5: "Mercury",   # Virgo
            6: "Venus",     # Libra
            7: "Mars",      # Scorpio
            8: "Jupiter",   # Sagittarius
            9: "Saturn",    # Capricorn
            10: "Saturn",   # Aquarius
            11: "Jupiter"   # Pisces
        }

        return sign_lords.get(sign_num, "Unknown")

    def _calculate_ascendant_sign(self, planets: Dict) -> Optional[int]:
        """
        Calculate ascendant sign from planet data using multiple fallback strategies

        Args:
            planets: Dictionary of planet positions

        Returns:
            Ascendant sign number (0-indexed: 0=Aries, 11=Pisces) or None if cannot determine
        """
        # Strategy 1: Try to find ascendant directly in planet data
        # Some chart calculations include "Ascendant" as a key
        if "Ascendant" in planets:
            asc_data = planets["Ascendant"]
            if "sign_num" in asc_data:
                # sign_num is typically 1-indexed, convert to 0-indexed
                return (asc_data["sign_num"] - 1) % 12

        # Strategy 2: Try to infer ascendant from house 1 placement
        # In Whole Sign system, if planet is in house 1, its sign is the ascendant
        for planet_name, planet_data in planets.items():
            if planet_data.get("house") == 1:
                sign_num = planet_data.get("sign_num", 0)
                if sign_num > 0:
                    return (sign_num - 1) % 12  # Convert to 0-indexed

        # Strategy 3: Calculate from any planet's house-sign relationship
        # If a planet is in house H and sign S, then ascendant sign = (S - H + 1) mod 12
        for planet_name, planet_data in planets.items():
            house = planet_data.get("house", 0)
            sign_num = planet_data.get("sign_num", 0)
            if house > 0 and sign_num > 0:
                # Convert sign_num to 0-indexed for calculation
                asc_sign = (sign_num - house) % 12
                return asc_sign

        # Cannot determine ascendant
        return None

    def _check_parivartana(self, lord1: str, lord2: str, planets: Dict) -> bool:
        """
        Check if two planets are in mutual sign exchange (Parivartana Yoga)

        Parivartana occurs when:
        - Planet A is in the sign ruled by Planet B
        - Planet B is in the sign ruled by Planet A

        Args:
            lord1: First planet name
            lord2: Second planet name
            planets: Dictionary of planet positions

        Returns:
            True if planets are in parivartana, False otherwise
        """
        if lord1 not in planets or lord2 not in planets:
            return False

        # Get the signs both planets are in
        lord1_sign = planets[lord1].get("sign_num", 0)
        lord2_sign = planets[lord2].get("sign_num", 0)

        if lord1_sign == 0 or lord2_sign == 0:
            return False

        # Get the signs each planet rules
        lord1_own_signs = self.OWN_SIGNS.get(lord1, [])
        lord2_own_signs = self.OWN_SIGNS.get(lord2, [])

        # Check if lord1 is in lord2's sign AND lord2 is in lord1's sign
        lord1_in_lord2_sign = lord1_sign in lord2_own_signs
        lord2_in_lord1_sign = lord2_sign in lord1_own_signs

        return lord1_in_lord2_sign and lord2_in_lord1_sign

    def _check_mutual_aspect(self, house1: int, house2: int, planets: Dict,
                            lord1: str, lord2: str) -> bool:
        """
        Check if two house lords mutually aspect each other

        Aspects in Vedic astrology:
        - All planets: 7th house aspect (opposition)
        - Mars: 4th, 7th, 8th aspects
        - Jupiter: 5th, 7th, 9th aspects
        - Saturn: 3rd, 7th, 10th aspects

        Args:
            house1: First house number
            house2: Second house number
            planets: Dictionary of planet positions
            lord1: Lord of first house
            lord2: Lord of second house

        Returns:
            True if lords mutually aspect, False otherwise
        """
        if lord1 not in planets or lord2 not in planets:
            return False

        # Get actual house positions of both lords
        lord1_house = planets[lord1].get("house", 0)
        lord2_house = planets[lord2].get("house", 0)

        if lord1_house == 0 or lord2_house == 0:
            return False

        # Helper function to check if planet aspects a house
        def planet_aspects_house(planet: str, from_house: int, to_house: int) -> bool:
            # Calculate house distance
            distance = (to_house - from_house) % 12
            if distance == 0:
                return False  # Same house, not an aspect

            # All planets aspect 7th house
            if distance == 6:  # 7th house is 6 positions away (1-indexed to 0-indexed)
                return True

            # Mars special aspects: 4th (3 positions), 8th (7 positions)
            if planet == "Mars" and distance in [3, 7]:
                return True

            # Jupiter special aspects: 5th (4 positions), 9th (8 positions)
            if planet == "Jupiter" and distance in [4, 8]:
                return True

            # Saturn special aspects: 3rd (2 positions), 10th (9 positions)
            if planet == "Saturn" and distance in [2, 9]:
                return True

            return False

        # Check if lord1 aspects lord2's house AND lord2 aspects lord1's house
        lord1_aspects_lord2 = planet_aspects_house(lord1, lord1_house, lord2_house)
        lord2_aspects_lord1 = planet_aspects_house(lord2, lord2_house, lord1_house)

        return lord1_aspects_lord2 and lord2_aspects_lord1

    def _check_lord_strength(self, lord: str, planets: Dict,
                            strength_type: str = "neutral") -> bool:
        """
        Enhanced strength validation for house lords

        Three strength levels:
        - "neutral": Not debilitated (minimum requirement)
        - "strong": In own sign or exalted
        - "very_strong": Exalted or vargottama

        Args:
            lord: Planet name
            planets: Dictionary of planet positions
            strength_type: "neutral", "strong", or "very_strong"

        Returns:
            True if lord meets the strength requirement, False otherwise
        """
        if lord not in planets:
            return False

        planet_data = planets[lord]

        # Check debilitation (never passes any strength test)
        if planet_data.get("debilitated", False):
            return False

        # Get planet's sign
        sign_num = planet_data.get("sign_num", 0)
        if sign_num == 0:
            return False

        # Check exaltation
        is_exalted = planet_data.get("exalted", False)

        # Check own sign
        is_own_sign = planet_data.get("own_sign", False)

        # Check vargottama (same sign in D1 and D9)
        # This would require D9 data which might not be available
        # For now, we'll use exalted as proxy for very strong

        if strength_type == "neutral":
            # Just needs to not be debilitated
            return True

        elif strength_type == "strong":
            # Needs to be in own sign or exalted
            return is_exalted or is_own_sign

        elif strength_type == "very_strong":
            # Needs to be exalted (or vargottama, but we'll use exalted)
            return is_exalted

        return False

    def _detect_systematic_raj_yogas(self, planets: Dict) -> List[Dict]:
        """
        Detect all 67 systematic Raj Yogas based on BPHS house lord combinations

        BPHS Section F: Raj Yoga (Combination for Authority/Power/Status)

        Classical Definition:
        Raj Yogas form when Kendra lords (1, 4, 7, 10) connect with Trikona lords (1, 5, 9)

        9 Base House Lord Pairs:
        - 1L with 5L, 9L (Lagna lord with trikona lords)
        - 4L with 5L, 9L (4th lord with trikona lords)
        - 7L with 5L, 9L (7th lord with trikona lords)
        - 10L with 5L, 9L (10th lord with trikona lords)
        - 5L with 9L (two trikona lords together)

        5 Relationship Types for each pair:
        1. Conjunction (same house)
        2. Mutual Aspect (planets aspect each other)
        3. Mutual Kendra (occupy kendra houses from each other)
        4. Mutual Trikona (occupy trikona houses from each other)
        5. Parivartana (mutual sign exchange)

        Total: 9 pairs × 5 types = 45 core Raj Yoga combinations

        Effects:
        - Authority, power, status in society
        - Leadership qualities and recognition
        - Success in career and public life
        - Wealth and prosperity
        - Fulfillment of ambitions

        Strength depends on:
        - Dignity of participating planets (exalted > own sign > neutral)
        - Houses they occupy (kendra > trikona > others)
        - Relationship type (conjunction strongest, then parivartana, then aspects)
        """
        yogas = []

        # Get ascendant sign
        asc_sign = self._calculate_ascendant_sign(planets)
        if asc_sign is None:
            return yogas

        # Define the 9 house-lord pairs for Raj Yoga
        # Format: (house1, house2, description)
        house_pairs = [
            # Lagna lord combinations
            (1, 5, "Lagna Lord with 5th Lord"),
            (1, 9, "Lagna Lord with 9th Lord"),

            # Kendra lords with Trikona lords
            (4, 5, "4th Lord with 5th Lord"),
            (4, 9, "4th Lord with 9th Lord"),
            (7, 5, "7th Lord with 5th Lord"),
            (7, 9, "7th Lord with 9th Lord"),
            (10, 5, "10th Lord with 5th Lord"),
            (10, 9, "10th Lord with 9th Lord"),

            # Two Trikona lords
            (5, 9, "5th Lord with 9th Lord"),
        ]

        # Check each house-lord pair
        for house1, house2, pair_desc in house_pairs:
            # Get the planetary lords of these houses
            lord1 = self._get_house_lord(house1, asc_sign)
            lord2 = self._get_house_lord(house2, asc_sign)

            # Skip if same planet rules both houses (no yoga)
            if lord1 == lord2:
                continue

            # Skip if planets don't exist in data
            if lord1 not in planets or lord2 not in planets:
                continue

            # Get planet positions
            lord1_house = planets[lord1].get("house", 0)
            lord2_house = planets[lord2].get("house", 0)

            if lord1_house == 0 or lord2_house == 0:
                continue

            # Check each relationship type

            # 1. CONJUNCTION (same house) - Strongest
            if lord1_house == lord2_house:
                # Check if at least one lord is strong
                if (self._check_lord_strength(lord1, planets, "neutral") and
                    self._check_lord_strength(lord2, planets, "neutral")):

                    # Calculate strength based on house and dignity
                    strength_score = 0
                    if lord1_house in [1, 4, 7, 10]:  # Kendra
                        strength_score += 30
                    elif lord1_house in [5, 9]:  # Trikona
                        strength_score += 25

                    # Add planet strength
                    if self._check_lord_strength(lord1, planets, "strong"):
                        strength_score += 20
                    if self._check_lord_strength(lord2, planets, "strong"):
                        strength_score += 20

                    strength = "Strong" if strength_score >= 50 else "Medium"

                    yogas.append({
                        "name": f"Raj Yoga: {house1}L-{house2}L Conjunction",
                        "description": f"{pair_desc} conjoined in {lord1_house}th house - exceptional authority, power, and success through combined energies of {lord1} and {lord2}",
                        "strength": strength,
                        "category": "Raj Yoga",
                        "yoga_forming_planets": [lord1, lord2],
                        "formation": f"{lord1} and {lord2} in {lord1_house}th house"
                    })

            # 2. MUTUAL ASPECT - Strong
            if self._check_mutual_aspect(lord1_house, lord2_house, planets, lord1, lord2):
                if (self._check_lord_strength(lord1, planets, "neutral") and
                    self._check_lord_strength(lord2, planets, "neutral")):

                    yogas.append({
                        "name": f"Raj Yoga: {house1}L-{house2}L Mutual Aspect",
                        "description": f"{pair_desc} in mutual aspect - authority and recognition through planetary influences of {lord1} (in {lord1_house}th) and {lord2} (in {lord2_house}th)",
                        "strength": "Medium",
                        "category": "Raj Yoga",
                        "yoga_forming_planets": [lord1, lord2],
                        "formation": f"{lord1} in {lord1_house}th aspecting {lord2} in {lord2_house}th"
                    })

            # 3. MUTUAL KENDRA - Medium
            # Check if the two lords occupy kendra positions from each other
            house_distance = abs(lord1_house - lord2_house)
            if house_distance in [3, 6, 9]:  # 4th, 7th, 10th from each other (kendra relationship)
                if (self._check_lord_strength(lord1, planets, "neutral") and
                    self._check_lord_strength(lord2, planets, "neutral")):

                    yogas.append({
                        "name": f"Raj Yoga: {house1}L-{house2}L Mutual Kendra",
                        "description": f"{pair_desc} in mutual kendra positions - power and stability through angular relationship between {lord1} (in {lord1_house}th) and {lord2} (in {lord2_house}th)",
                        "strength": "Medium",
                        "category": "Raj Yoga",
                        "yoga_forming_planets": [lord1, lord2],
                        "formation": f"{lord1} in {lord1_house}th, {lord2} in {lord2_house}th (mutual kendra)"
                    })

            # 4. MUTUAL TRIKONA - Medium
            # Check if the two lords occupy trikona positions from each other
            if house_distance in [4, 8]:  # 5th, 9th from each other (trikona relationship)
                if (self._check_lord_strength(lord1, planets, "neutral") and
                    self._check_lord_strength(lord2, planets, "neutral")):

                    yogas.append({
                        "name": f"Raj Yoga: {house1}L-{house2}L Mutual Trikona",
                        "description": f"{pair_desc} in mutual trikona positions - fortune and dharmic success through trinal harmony between {lord1} (in {lord1_house}th) and {lord2} (in {lord2_house}th)",
                        "strength": "Medium",
                        "category": "Raj Yoga",
                        "yoga_forming_planets": [lord1, lord2],
                        "formation": f"{lord1} in {lord1_house}th, {lord2} in {lord2_house}th (mutual trikona)"
                    })

            # 5. PARIVARTANA (Sign Exchange) - Very Strong
            if self._check_parivartana(lord1, lord2, planets):
                # Parivartana is considered very powerful
                strength = "Strong"

                # Check if it's Maha Parivartana (both in kendra/trikona)
                if ((lord1_house in [1, 4, 7, 10, 5, 9]) and
                    (lord2_house in [1, 4, 7, 10, 5, 9])):
                    strength = "Very Strong"
                    prefix = "Maha "
                else:
                    prefix = ""

                yogas.append({
                    "name": f"Raj Yoga: {house1}L-{house2}L {prefix}Parivartana",
                    "description": f"{pair_desc} in mutual sign exchange ({prefix}Parivartana) - exceptional power through complete energy exchange between {lord1} (in {lord2}'s sign) and {lord2} (in {lord1}'s sign)",
                    "strength": strength,
                    "category": "Raj Yoga",
                    "yoga_forming_planets": [lord1, lord2],
                    "formation": f"{lord1} and {lord2} in sign exchange"
                })

        return yogas

    def _detect_benefic_support_yogas(self, planets: Dict) -> List[Dict]:
        """
        Phase 1.3: Benefic Support Yogas (24 variations)

        BPHS IDs 112-135: Benefics positioned favorably from anchor points

        Benefic planets (Jupiter, Venus, Mercury, waxing Moon) in 2nd, 4th, or 5th
        from Lagna lord's sign provide support for success and prosperity.

        Anchors:
        - Lagna lord's sign (primary anchor)

        Positions: 2nd, 4th, 5th house from anchor sign
        Benefics: Jupiter, Venus, Mercury, Moon (when waxing)

        Formula: 4 benefics × 3 positions × 2 anchors = 24 combinations
        (For now implementing with Lagna lord's sign as primary anchor)

        Effects:
        - Financial support and stability
        - Educational achievements
        - Family harmony and support
        - Favorable opportunities
        """
        yogas = []

        # Get ascendant sign
        asc_sign = self._calculate_ascendant_sign(planets)
        if asc_sign is None:
            return yogas

        # Get Lagna lord
        lagna_lord = self._get_house_lord(1, asc_sign)
        if lagna_lord not in planets:
            return yogas

        # Get the sign Lagna lord is positioned in
        lagna_lord_sign = planets[lagna_lord].get("sign_num", 0)
        if lagna_lord_sign == 0:
            return yogas

        # Convert to 0-indexed
        lagna_lord_sign_idx = lagna_lord_sign - 1

        # Define benefics
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]

        # Define support positions from Lagna lord's sign (2nd, 4th, 5th)
        support_positions = {
            2: "2nd from Lagna lord's sign",
            4: "4th from Lagna lord's sign",
            5: "5th from Lagna lord's sign"
        }

        # Check each benefic
        for benefic in benefics:
            if benefic not in planets:
                continue

            benefic_sign = planets[benefic].get("sign_num", 0)
            if benefic_sign == 0:
                continue

            # Convert to 0-indexed
            benefic_sign_idx = benefic_sign - 1

            # Calculate distance from Lagna lord's sign
            sign_distance = (benefic_sign_idx - lagna_lord_sign_idx) % 12

            # Check if in support position (2nd, 4th, 5th from Lagna lord's sign)
            if sign_distance in [1, 3, 4]:  # 0-indexed: 1=2nd, 3=4th, 4=5th
                position_num = sign_distance + 1
                position_desc = support_positions.get(position_num, f"{position_num}th")

                # Additional check for Moon - prefer waxing
                if benefic == "Moon":
                    # Check if Moon is waxing (optional - include all Moon for now)
                    benefic_label = "Moon"
                else:
                    benefic_label = benefic

                # Check if benefic is strong
                is_strong = self._check_lord_strength(benefic, planets, "strong")
                strength = "Medium" if is_strong else "Weak"

                yogas.append({
                    "name": f"Benefic Support Yoga: {benefic_label} in {position_num}th from Lagna Lord",
                    "description": f"{benefic_label} positioned in {position_desc} ({self.SIGNS[benefic_sign_idx]}) - provides support through {self._get_benefic_quality(benefic)}, enhances success and prosperity",
                    "strength": strength,
                    "category": "Raj Yoga Support",
                    "yoga_forming_planets": [benefic, lagna_lord],
                    "formation": f"{benefic} in {self.SIGNS[benefic_sign_idx]}, {position_num}th from {lagna_lord}'s position in {self.SIGNS[lagna_lord_sign_idx]}"
                })

        return yogas

    def _get_benefic_quality(self, planet: str) -> str:
        """Get the quality/domain each benefic supports"""
        qualities = {
            "Jupiter": "wisdom, expansion, and fortune",
            "Venus": "comfort, arts, and relationships",
            "Mercury": "intelligence, communication, and skills",
            "Moon": "emotional support and public favor"
        }
        return qualities.get(planet, "positive influences")

    def _detect_valor_yogas(self, planets: Dict) -> List[Dict]:
        """
        Phase 1.4: Valor/Overcoming Yogas (12 variations)

        BPHS IDs 136-147: Malefics in upachaya (growth) positions from anchor

        Sun, Mars, or Saturn in 3rd or 6th from Lagna lord's sign provide:
        - Courage and valor
        - Ability to overcome enemies and obstacles
        - Competitive strength
        - Success through effort

        Formula: 3 malefics × 2 positions × 2 anchors = 12 combinations
        """
        yogas = []

        # Get ascendant sign
        asc_sign = self._calculate_ascendant_sign(planets)
        if asc_sign is None:
            return yogas

        # Get Lagna lord
        lagna_lord = self._get_house_lord(1, asc_sign)
        if lagna_lord not in planets:
            return yogas

        # Get the sign Lagna lord is positioned in
        lagna_lord_sign = planets[lagna_lord].get("sign_num", 0)
        if lagna_lord_sign == 0:
            return yogas

        # Convert to 0-indexed
        lagna_lord_sign_idx = lagna_lord_sign - 1

        # Define malefics
        malefics = ["Sun", "Mars", "Saturn"]

        # Define upachaya positions (3rd, 6th from Lagna lord's sign)
        upachaya_positions = {
            3: "3rd from Lagna lord's sign (courage)",
            6: "6th from Lagna lord's sign (victory over enemies)"
        }

        # Check each malefic
        for malefic in malefics:
            if malefic not in planets:
                continue

            malefic_sign = planets[malefic].get("sign_num", 0)
            if malefic_sign == 0:
                continue

            # Convert to 0-indexed
            malefic_sign_idx = malefic_sign - 1

            # Calculate distance from Lagna lord's sign
            sign_distance = (malefic_sign_idx - lagna_lord_sign_idx) % 12

            # Check if in upachaya position (3rd, 6th from Lagna lord's sign)
            if sign_distance in [2, 5]:  # 0-indexed: 2=3rd, 5=6th
                position_num = sign_distance + 1
                position_desc = upachaya_positions.get(position_num, f"{position_num}th")

                # Check if malefic is strong
                is_strong = self._check_lord_strength(malefic, planets, "strong")
                strength = "Medium" if is_strong else "Weak"

                quality = self._get_malefic_quality(malefic)

                yogas.append({
                    "name": f"Valor Yoga: {malefic} in {position_num}th from Lagna Lord",
                    "description": f"{malefic} positioned {position_desc} ({self.SIGNS[malefic_sign_idx]}) - provides {quality}, ability to overcome obstacles and enemies",
                    "strength": strength,
                    "category": "Raj Yoga Support",
                    "yoga_forming_planets": [malefic, lagna_lord],
                    "formation": f"{malefic} in {self.SIGNS[malefic_sign_idx]}, {position_num}th from {lagna_lord}'s position in {self.SIGNS[lagna_lord_sign_idx]}"
                })

        return yogas

    def _get_malefic_quality(self, planet: str) -> str:
        """Get the quality/domain each malefic provides"""
        qualities = {
            "Sun": "authority and leadership",
            "Mars": "courage and competitive strength",
            "Saturn": "discipline and perseverance"
        }
        return qualities.get(planet, "strength through challenges")

    def _detect_exalted_benefic_2nd_yogas(self, planets: Dict) -> List[Dict]:
        """
        Phase 1.5: Exalted Benefic in 2nd House (4 variations)

        BPHS IDs 148-151: Jupiter/Venus/Mercury/Moon exalted in 2nd house

        Exalted benefic in 2nd house indicates:
        - Exceptional wealth accumulation
        - Eloquent speech and communication
        - Strong family support
        - Financial wisdom

        Exaltation signs:
        - Jupiter in Cancer (4)
        - Venus in Pisces (12)
        - Mercury in Virgo (6)
        - Moon in Taurus (2)
        """
        yogas = []

        benefics = {
            "Jupiter": (4, "Cancer", "wisdom in wealth, expansive financial growth"),
            "Venus": (12, "Pisces", "luxurious lifestyle, artistic income"),
            "Mercury": (6, "Virgo", "intellectual earnings, business acumen"),
            "Moon": (2, "Taurus", "emotional security through wealth, stable finances")
        }

        for benefic, (exalt_sign, exalt_sign_name, quality) in benefics.items():
            if benefic not in planets:
                continue

            planet_data = planets[benefic]
            planet_house = planet_data.get("house", 0)
            planet_sign = planet_data.get("sign_num", 0)
            is_exalted = planet_data.get("exalted", False)

            # Check if in 2nd house AND exalted
            if planet_house == 2 and is_exalted and planet_sign == exalt_sign:
                yogas.append({
                    "name": f"Exalted {benefic} in 2nd House Yoga",
                    "description": f"{benefic} exalted in {exalt_sign_name} in 2nd house - exceptional {quality}, powerful wealth-generating combination",
                    "strength": "Strong",
                    "category": "Raj Yoga Support",
                    "yoga_forming_planets": [benefic],
                    "formation": f"{benefic} exalted in 2nd house ({exalt_sign_name})"
                })

        return yogas

    def _detect_viparita_like_support_yogas(self, planets: Dict) -> List[Dict]:
        """
        Phase 1.6: Viparita-like Raj Support (28 variations)

        BPHS IDs 152-179: Debilitated planets in dusthana (3/6/8/12) with strong Lagna lord

        Classical principle: Debilitation in upachaya/dusthana houses can give positive results
        when the Lagna lord is strong, converting weakness into strength.

        Formula: 7 planets × 4 houses (3rd, 6th, 8th, 12th) = 28 combinations

        Effects:
        - Overcoming adversity through struggle
        - Success after initial obstacles
        - Transformation of weakness into strength
        - Victory through perseverance

        Condition: Lagna lord must be strong (own/exalted) for the yoga to manifest
        """
        yogas = []

        # Get ascendant sign
        asc_sign = self._calculate_ascendant_sign(planets)
        if asc_sign is None:
            return yogas

        # Get Lagna lord and check strength
        lagna_lord = self._get_house_lord(1, asc_sign)
        if lagna_lord not in planets:
            return yogas

        # Lagna lord must be strong for this yoga to work
        if not self._check_lord_strength(lagna_lord, planets, "strong"):
            return yogas  # Skip if Lagna lord is weak

        # Define all 7 classical planets (excluding Rahu/Ketu)
        classical_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        # Dusthana/Upachaya houses where debilitation can be beneficial
        beneficial_dusthana = {
            3: "3rd house (courage through struggle)",
            6: "6th house (victory over enemies)",
            8: "8th house (transformation through crisis)",
            12: "12th house (spiritual liberation)"
        }

        # Check each planet
        for planet in classical_planets:
            if planet not in planets:
                continue

            planet_data = planets[planet]
            planet_house = planet_data.get("house", 0)
            is_debilitated = planet_data.get("debilitated", False)

            # Check if planet is debilitated AND in beneficial dusthana
            if is_debilitated and planet_house in beneficial_dusthana:
                house_desc = beneficial_dusthana[planet_house]

                yogas.append({
                    "name": f"Viparita-like Support: Debilitated {planet} in {planet_house}th",
                    "description": f"{planet} debilitated in {house_desc} with strong Lagna lord ({lagna_lord}) - weakness transforms to strength, success through overcoming obstacles",
                    "strength": "Medium",
                    "category": "Raj Yoga Support",
                    "yoga_forming_planets": [planet, lagna_lord],
                    "formation": f"Debilitated {planet} in {planet_house}th, supported by strong {lagna_lord}"
                })

        return yogas

    def _detect_karma_raj_yoga(self, planets: Dict) -> List[Dict]:
        """
        Phase 1.7.1: Karma Raj Yoga (ID 180)

        10th lord in own sign or exalted in 10th house, aspecting Lagna

        This is a powerful career and authority yoga indicating:
        - Exceptional professional success
        - Leadership in chosen field
        - Recognition and authority
        - Strong career foundation
        """
        yogas = []

        # Get ascendant sign
        asc_sign = self._calculate_ascendant_sign(planets)
        if asc_sign is None:
            return yogas

        # Get 10th lord
        lord_10 = self._get_house_lord(10, asc_sign)
        if lord_10 not in planets:
            return yogas

        planet_data = planets[lord_10]
        planet_house = planet_data.get("house", 0)

        # Check if 10th lord is in 10th house
        if planet_house == 10:
            # Check if strong (own/exalted)
            if self._check_lord_strength(lord_10, planets, "strong"):
                yogas.append({
                    "name": "Karma Raj Yoga",
                    "description": f"10th lord {lord_10} strong in 10th house - exceptional professional success, career authority, recognition in chosen field",
                    "strength": "Strong",
                    "category": "Raj Yoga Support",
                    "yoga_forming_planets": [lord_10],
                    "formation": f"{lord_10} in own/exalted sign in 10th house"
                })

        return yogas

    def _detect_all_benefic_kendras_yoga(self, planets: Dict) -> List[Dict]:
        """
        Phase 1.7.2: All-Benefic Kendras (ID 181)

        All occupied kendra houses (1,4,7,10) contain only benefic planets

        This creates:
        - Harmony in all four pillars of life
        - Balanced success in self, home, relationships, career
        - Protection from adversity
        - Overall auspiciousness
        """
        yogas = []

        # Define benefics
        benefics = {"Jupiter", "Venus", "Mercury", "Moon"}

        # Get planets in kendras
        kendras = [1, 4, 7, 10]
        kendra_planets = {}

        for house in kendras:
            kendra_planets[house] = []

        # Collect planets in kendras
        for planet_name, planet_data in planets.items():
            if planet_name in ["Rahu", "Ketu", "Ascendant"]:
                continue
            house = planet_data.get("house", 0)
            if house in kendras:
                kendra_planets[house].append(planet_name)

        # Check if any kendra is occupied
        occupied_kendras = [h for h in kendras if kendra_planets[h]]
        if not occupied_kendras:
            return yogas

        # Check if ALL occupied kendras contain ONLY benefics
        all_benefic = True
        for house in occupied_kendras:
            for planet in kendra_planets[house]:
                if planet not in benefics:
                    all_benefic = False
                    break
            if not all_benefic:
                break

        if all_benefic:
            benefic_list = []
            for house in occupied_kendras:
                benefic_list.extend(kendra_planets[house])

            yogas.append({
                "name": "All-Benefic Kendras Yoga",
                "description": f"All occupied kendras contain only benefics ({', '.join(set(benefic_list))}) - harmonious life, balanced success in all four pillars (self, home, relationships, career)",
                "strength": "Medium",
                "category": "Raj Yoga Support",
                "yoga_forming_planets": list(set(benefic_list)),
                "formation": f"Benefics in kendras: {', '.join([f'{h}th' for h in occupied_kendras])}"
            })

        return yogas

    def _detect_moon_venus_mutual_yoga(self, planets: Dict) -> List[Dict]:
        """
        Phase 1.7.3: Moon-Venus Mutual 3rd/11th (IDs 182-183)

        Moon and Venus in mutual 3rd and 11th positions

        This creates:
        - Emotional and material prosperity
        - Artistic success and gains
        - Harmony between heart and desires
        - Financial gains through creativity
        """
        yogas = []

        if "Moon" not in planets or "Venus" not in planets:
            return yogas

        moon_house = planets["Moon"].get("house", 0)
        venus_house = planets["Venus"].get("house", 0)

        if moon_house == 0 or venus_house == 0:
            return yogas

        # Check if Moon is in 3rd from Venus AND Venus is in 11th from Moon (or vice versa)
        moon_from_venus = (moon_house - venus_house) % 12
        venus_from_moon = (venus_house - moon_house) % 12

        # Case 1: Moon in 3rd from Venus, Venus in 11th from Moon
        if moon_from_venus == 2 and venus_from_moon == 10:  # 0-indexed: 2=3rd, 10=11th
            yogas.append({
                "name": "Moon-Venus Mutual 3rd/11th Yoga",
                "description": f"Moon in 3rd from Venus, Venus in 11th from Moon - emotional prosperity, artistic gains, harmony between heart and desires",
                "strength": "Medium",
                "category": "Raj Yoga Support",
                "yoga_forming_planets": ["Moon", "Venus"],
                "formation": f"Moon in {moon_house}th, Venus in {venus_house}th (mutual 3-11)"
            })

        # Case 2: Venus in 3rd from Moon, Moon in 11th from Venus
        elif venus_from_moon == 2 and moon_from_venus == 10:
            yogas.append({
                "name": "Moon-Venus Mutual 3rd/11th Yoga",
                "description": f"Venus in 3rd from Moon, Moon in 11th from Venus - material prosperity, creative success, gains through emotional intelligence",
                "strength": "Medium",
                "category": "Raj Yoga Support",
                "yoga_forming_planets": ["Moon", "Venus"],
                "formation": f"Venus in {venus_house}th, Moon in {moon_house}th (mutual 3-11)"
            })

        return yogas

    def _detect_daridra_yoga(self, planets: Dict) -> List[Dict]:
        """
        Daridra Yoga (Poverty Yoga): According to BPHS

        Classical Definition:
        - Lord of 11th house (gains/income) placed in dusthana houses (6th, 8th, or 12th)

        This indicates:
        - Financial struggles and obstacles to wealth accumulation
        - Difficulty retaining gains
        - Losses through debts (6th), sudden events (8th), or expenses (12th)

        Note: Severity depends on the strength of the 11th lord and cancellations
        """
        yogas = []

        # Get ascendant sign using helper method
        asc_sign = self._calculate_ascendant_sign(planets)
        if asc_sign is None:
            return yogas

        # Find lord of 11th house
        lord_of_11th = self._get_house_lord(11, asc_sign)

        # Get the house position of 11th lord
        eleventh_lord_data = planets.get(lord_of_11th, {})
        eleventh_lord_house = eleventh_lord_data.get("house", 0)

        # Dusthana houses (6th, 8th, 12th)
        dusthana_houses = [6, 8, 12]

        # Check if 11th lord is in dusthana
        if eleventh_lord_house in dusthana_houses:
            dusthana_meanings = {
                6: "debts, diseases, and enemies",
                8: "sudden losses, obstacles, and transformations",
                12: "expenses, losses, and foreign matters"
            }

            meaning = dusthana_meanings.get(eleventh_lord_house, "difficulties")

            yogas.append({
                "name": "Daridra Yoga",
                "description": f"Lord of 11th house ({lord_of_11th}) placed in {eleventh_lord_house}th house - financial struggles, obstacles to wealth accumulation, losses through {meaning}, need for careful financial planning and debt management",
                "strength": "Medium",
                "category": "Challenge Yoga",
                "yoga_forming_planets": [lord_of_11th],
                "formation": f"{lord_of_11th} (11th lord) in {eleventh_lord_house}th house"
            })

        return yogas

    def _detect_balarishta_yoga(self, planets: Dict) -> List[Dict]:
        """
        Balarishta Yoga: Indicators of childhood health challenges
        Simplified: Malefics in 1st, 4th, 8th houses with Moon afflicted
        Note: Modern medicine has reduced the severity of this yoga
        """
        yogas = []

        moon_house = planets.get("Moon", {}).get("house", 0)
        moon_sign = planets.get("Moon", {}).get("sign_num", 0)

        # Check if Moon is afflicted (debilitated or with malefics)
        moon_debilitated = (moon_sign == self.DEBILITATION_SIGNS.get("Moon"))

        malefics_with_moon = []
        for planet in ["Mars", "Saturn", "Rahu", "Ketu"]:
            planet_house = planets.get(planet, {}).get("house", 0)
            if planet_house == moon_house:
                malefics_with_moon.append(planet)

        # Check malefics in critical houses for children
        critical_houses = [1, 4, 8]
        malefics_in_critical = []
        for planet in ["Mars", "Saturn"]:
            house = planets.get(planet, {}).get("house", 0)
            if house in critical_houses:
                malefics_in_critical.append(f"{planet} in {house}th")

        if (moon_debilitated and malefics_with_moon) or len(malefics_in_critical) >= 2:
            yogas.append({
                "name": "Balarishta Yoga",
                "description": f"Moon afflicted or malefics in critical houses - indicates need for extra care in childhood, potential health challenges in early years. Note: Modern medicine significantly mitigates these effects",
                "strength": "Weak",
                "category": "Health Indicator"
            })

        return yogas

    def _detect_kroora_yoga(self, planets: Dict) -> List[Dict]:
        """
        Kroora Yoga (Cruel Yoga): Multiple malefics in kendras without benefic aspects
        Indicates harsh personality, aggressive nature, but also strength and courage
        """
        yogas = []
        kendras = [1, 4, 7, 10]
        malefics = ["Mars", "Saturn", "Sun"]

        malefics_in_kendra = []
        for planet in malefics:
            house = planets.get(planet, {}).get("house", 0)
            if house in kendras:
                malefics_in_kendra.append((planet, house))

        # Kroora Yoga forms when 2+ malefics in kendras
        if len(malefics_in_kendra) >= 2:
            planet_houses = [f"{p[0]} in {p[1]}th" for p in malefics_in_kendra]

            # Check if mitigated by Jupiter's aspect or presence
            jupiter_house = planets.get("Jupiter", {}).get("house", 0)
            mitigated = jupiter_house in kendras

            if mitigated:
                desc = f"Malefics in kendras ({', '.join(planet_houses)}) but mitigated by Jupiter - strong personality, determination, leadership through firm approach, courage"
                strength = "Weak"
            else:
                desc = f"Malefics in kendras ({', '.join(planet_houses)}) - harsh demeanor, aggressive approach, difficulties in relationships, but also indicates strength, courage, and ability to overcome obstacles"
                strength = "Medium"

            yogas.append({
                "name": "Kroora Yoga",
                "description": desc,
                "strength": strength,
                "category": "Personality Indicator"
            })

        return yogas

    def _detect_nabhasa_sankhya_yogas(self, planets: Dict) -> List[Dict]:
        """
        Nabhasa Sankhya Yogas (3) - Numerical pattern yogas
        Based on specific count and distribution patterns
        """
        yogas = []

        main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
        malefics = ["Sun", "Mars", "Saturn"]

        benefic_houses = [planets.get(p, {}).get("house", 0) for p in benefics if planets.get(p, {}).get("house", 0)]
        malefic_houses = [planets.get(p, {}).get("house", 0) for p in malefics if planets.get(p, {}).get("house", 0)]

        upachaya_houses = [3, 6, 10, 11]

        # 1. Vallaki Yoga - Benefics in upachayas, malefics elsewhere
        benefics_in_upachaya = sum(1 for h in benefic_houses if h in upachaya_houses)
        malefics_in_upachaya = sum(1 for h in malefic_houses if h in upachaya_houses)

        if benefics_in_upachaya >= 3 and malefics_in_upachaya == 0:
            yogas.append({
                "name": "Vallaki Yoga",
                "description": "Benefics in upachayas (3,6,10,11) with malefics elsewhere - Musical talents, artistic skills, cultured nature",
                "strength": "Medium",
                "category": "Nabhasa - Sankhya"
            })

        # 2. Daam Yoga - Malefics in 6th and 12th houses
        malefics_in_6_12 = [h for h in malefic_houses if h in [6, 12]]
        if len(malefics_in_6_12) >= 2:
            yogas.append({
                "name": "Daam Yoga",
                "description": "Malefics in 6th and 12th houses - Binding pattern, obstacles, enemies, losses, need for perseverance",
                "strength": "Weak",
                "category": "Nabhasa - Sankhya"
            })

        # 3. Paasha Yoga - All malefics in upachayas (3,6,10,11)
        if len(malefic_houses) >= 2 and all(h in upachaya_houses for h in malefic_houses):
            yogas.append({
                "name": "Paasha Yoga",
                "description": "All malefics in upachayas (3,6,10,11) - Noose/bondage pattern, imprisonment risk, restricted freedom",
                "strength": "Weak",
                "category": "Nabhasa - Sankhya"
            })

        # 4. Vīṇā Yoga (ID 31) - All 7 planets spread over exactly 7 signs
        # Count unique signs occupied by the 7 classical planets
        occupied_signs = set()
        for planet in main_planets:
            sign_num = planets.get(planet, {}).get("sign_num", 0)
            if sign_num > 0:
                occupied_signs.add(sign_num)

        # Check if we have all 7 planets and they occupy exactly 7 signs
        planets_with_position = sum(1 for p in main_planets if planets.get(p, {}).get("sign_num", 0) > 0)

        if planets_with_position == 7 and len(occupied_signs) == 7:
            yogas.append({
                "name": "Vīṇā Yoga",
                "description": "All 7 planets spread over exactly 7 signs - Musical instrument pattern, artistic talents, cultured nature, harmonious life, success in fine arts",
                "strength": "Strong",
                "category": "Nabhasa - Sankhya"
            })

        return yogas

    def _detect_sanyas_yogas(self, planets: Dict) -> List[Dict]:
        """
        7 Classical Sanyas Yogas - Renunciation yogas indicating spiritual path

        According to BPHS and classical texts, these indicate:
        - Strong spiritual inclinations
        - Renunciation tendencies
        - Teaching/guiding roles
        - Detachment (not always literal monk status in modern times)
        """
        yogas = []

        # Get houses and signs
        jupiter_house = planets.get("Jupiter", {}).get("house", 0)
        saturn_house = planets.get("Saturn", {}).get("house", 0)
        moon_house = planets.get("Moon", {}).get("house", 0)
        rahu_house = planets.get("Rahu", {}).get("house", 0)
        ketu_house = planets.get("Ketu", {}).get("house", 0)
        sun_house = planets.get("Sun", {}).get("house", 0)

        kendra_houses = [1, 4, 7, 10]

        # Count planets in each house for conjunction detection
        house_planet_count = {}
        main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        for planet in main_planets:
            house = planets.get(planet, {}).get("house", 0)
            if house:
                house_planet_count[house] = house_planet_count.get(house, 0) + 1

        # 1. Maha Sanyas Yoga - 4 or more planets in one house (especially with Saturn)
        for house, count in house_planet_count.items():
            if count >= 4:
                planets_in_house = [p for p in main_planets if planets.get(p, {}).get("house", 0) == house]
                has_saturn = "Saturn" in planets_in_house
                yogas.append({
                    "name": "Maha Sanyas Yoga",
                    "description": f"4+ planets in house {house} {'(including Saturn) ' if has_saturn else ''}- Great renunciation, strong spiritual calling, monastic tendencies, detachment from material world",
                    "strength": "Very Strong" if has_saturn else "Strong",
                    "category": "Sanyas Yoga",
                    "yoga_forming_planets": planets_in_house
                })
                break

        # 2. Parivraja Yoga - Jupiter in kendra from Moon, with Saturn
        if jupiter_house and moon_house:
            jupiter_from_moon = (jupiter_house - moon_house) % 12
            if jupiter_from_moon in [0, 3, 6, 9]:  # Kendra positions
                if saturn_house:
                    # Check if Saturn aspects or conjoins Jupiter
                    saturn_jupiter_distance = abs(saturn_house - jupiter_house)
                    if saturn_house == jupiter_house or saturn_jupiter_distance == 6:  # Conjunction or aspect
                        yogas.append({
                            "name": "Parivraja Yoga",
                            "description": "Jupiter in kendra from Moon with Saturn - Wandering monk, spiritual teacher, pilgrimages, renunciation after worldly experiences",
                            "strength": "Strong",
                            "category": "Sanyas Yoga",
                            "yoga_forming_planets": ["Jupiter", "Saturn", "Moon"]
                        })

        # 3. Kevala Sanyas Yoga - Exalted or strong Saturn with Moon
        saturn_sign = planets.get("Saturn", {}).get("sign_num", 0)
        saturn_exalted = (saturn_sign == 7)  # Libra

        if moon_house and saturn_house:
            if saturn_house == moon_house or abs(saturn_house - moon_house) == 6:  # Conjunction or aspect
                if saturn_exalted or saturn_sign in self.OWN_SIGNS.get("Saturn", []):
                    yogas.append({
                        "name": "Kevala Sanyas Yoga",
                        "description": "Exalted/strong Saturn with Moon - Complete renunciation, hermit lifestyle, absolute detachment, spiritual mastery",
                        "strength": "Very Strong",
                        "category": "Sanyas Yoga",
                        "yoga_forming_planets": ["Saturn", "Moon"]
                    })

        # 4. Markandeya Sanyas Yoga - Jupiter and Saturn in kendras, Moon in 9th or 10th
        if jupiter_house in kendra_houses and saturn_house in kendra_houses:
            if moon_house in [9, 10]:
                yogas.append({
                    "name": "Markandeya Sanyas Yoga",
                    "description": "Jupiter & Saturn in kendras, Moon in 9th/10th - Scholarly renunciation, teacher of scriptures, revered sage",
                    "strength": "Strong",
                    "category": "Sanyas Yoga",
                    "yoga_forming_planets": ["Jupiter", "Saturn", "Moon"]
                })

        # 5. Akhanda Sanyas Yoga - Jupiter in 9th, Saturn in 8th, Rahu/Ketu in 4th
        if jupiter_house == 9 and saturn_house == 8:
            if rahu_house == 4 or ketu_house == 4:
                yogas.append({
                    "name": "Akhanda Sanyas Yoga",
                    "description": "Jupiter-9th, Saturn-8th, Rahu/Ketu-4th - Continuous spiritual practice, mysticism, unbroken meditation",
                    "strength": "Very Strong",
                    "category": "Sanyas Yoga",
                    "yoga_forming_planets": ["Jupiter", "Saturn", "Rahu" if rahu_house == 4 else "Ketu"]
                })

        # 6. Vyatipata Sanyas Yoga - Saturn and Jupiter in mutual kendra with malefics
        if jupiter_house and saturn_house:
            jupiter_saturn_distance = (saturn_house - jupiter_house) % 12
            if jupiter_saturn_distance in [0, 3, 6, 9]:  # Mutual kendra
                # Check if malefics (Sun, Mars) are involved
                malefic_involved = False
                for planet in ["Sun", "Mars"]:
                    p_house = planets.get(planet, {}).get("house", 0)
                    if p_house and (p_house == jupiter_house or p_house == saturn_house):
                        malefic_involved = True
                        break

                if malefic_involved:
                    yogas.append({
                        "name": "Vyatipata Sanyas Yoga",
                        "description": "Saturn-Jupiter in mutual kendra with malefics - Late-life renunciation after worldly experiences, spiritual turning point",
                        "strength": "Medium",
                        "category": "Sanyas Yoga",
                        "yoga_forming_planets": ["Jupiter", "Saturn"]
                    })

        # 7. Kalanala Sanyas Yoga - 4+ planets in 10th house OR Ketu in 10th with multiple planets
        if 10 in house_planet_count and house_planet_count[10] >= 4:
            yogas.append({
                "name": "Kalanala Sanyas Yoga",
                "description": "4+ planets in 10th house - Fame through spirituality, religious leadership, public spiritual teaching",
                "strength": "Strong",
                "category": "Sanyas Yoga",
                "yoga_forming_planets": [p for p in main_planets if planets.get(p, {}).get("house", 0) == 10]
            })
        elif ketu_house == 10 and 10 in house_planet_count and house_planet_count[10] >= 3:
            yogas.append({
                "name": "Kalanala Sanyas Yoga (Ketu variant)",
                "description": "Ketu in 10th with 3+ planets - Spiritual fame, mystical teaching, guide to liberation",
                "strength": "Strong",
                "category": "Sanyas Yoga",
                "yoga_forming_planets": [p for p in main_planets + ["Ketu"] if planets.get(p, {}).get("house", 0) == 10]
            })

        return yogas

    def _detect_nitya_yogas(self, planets: Dict) -> List[Dict]:
        """
        27 Nitya Yogas (Birth Yogas) - Based on Sun-Moon longitudinal distance

        According to BPHS, these are fixed yogas determined by the angular distance
        between Sun and Moon at birth. The 360° circle is divided into 27 equal parts
        of 13°20' each, creating 27 distinct yogas.

        Each Nitya Yoga has specific effects on personality, fortune, and life path.
        """
        yogas = []

        # Get Sun and Moon longitudes
        sun_long = planets.get("Sun", {}).get("longitude")
        moon_long = planets.get("Moon", {}).get("longitude")

        if sun_long is None or moon_long is None:
            return yogas

        # Calculate angular distance from Sun to Moon (0-360°)
        distance = (moon_long - sun_long) % 360

        # Each Nitya Yoga spans 13°20' (13.333...)
        nitya_span = 360 / 27  # 13.333...

        # Determine which of the 27 Nitya Yogas is formed
        nitya_index = int(distance / nitya_span)

        # Define all 27 Nitya Yogas with their effects
        nitya_yogas_data = [
            {
                "name": "Vishkambha Yoga",
                "range": "0° - 13°20'",
                "effects": "Determination, ability to overcome obstacles, research aptitude, can be stubborn",
                "nature": "Mixed",
                "deity": "Yama (God of Death)",
                "strength": "Medium"
            },
            {
                "name": "Priti Yoga",
                "range": "13°20' - 26°40'",
                "effects": "Friendly nature, popularity, good relationships, pleasant personality, social success",
                "nature": "Auspicious",
                "deity": "Vishnu (Preserver)",
                "strength": "Strong"
            },
            {
                "name": "Ayushman Yoga",
                "range": "26°40' - 40°",
                "effects": "Longevity, good health, vitality, blessed with long life and prosperity",
                "nature": "Auspicious",
                "deity": "Chandra (Moon)",
                "strength": "Strong"
            },
            {
                "name": "Saubhagya Yoga",
                "range": "40° - 53°20'",
                "effects": "Fortune, happiness, blessed life, marital bliss, overall well-being",
                "nature": "Auspicious",
                "deity": "Brahma (Creator)",
                "strength": "Strong"
            },
            {
                "name": "Shobhana Yoga",
                "range": "53°20' - 66°40'",
                "effects": "Attractiveness, beauty, charm, artistic talents, refined tastes",
                "nature": "Auspicious",
                "deity": "Brihaspati (Jupiter)",
                "strength": "Strong"
            },
            {
                "name": "Atiganda Yoga",
                "range": "66°40' - 80°",
                "effects": "Obstacles, conflicts, aggressive nature, challenges in relationships",
                "nature": "Inauspicious",
                "deity": "Agni (Fire)",
                "strength": "Medium"
            },
            {
                "name": "Sukarma Yoga",
                "range": "80° - 93°20'",
                "effects": "Good deeds, virtuous nature, ethical conduct, success through right action",
                "nature": "Auspicious",
                "deity": "Indra (King of Gods)",
                "strength": "Strong"
            },
            {
                "name": "Dhriti Yoga",
                "range": "93°20' - 106°40'",
                "effects": "Patience, perseverance, determination, ability to sustain efforts, steady progress",
                "nature": "Auspicious",
                "deity": "Jala (Water)",
                "strength": "Medium"
            },
            {
                "name": "Shoola Yoga",
                "range": "106°40' - 120°",
                "effects": "Sharp mind, critical nature, pain/suffering, can be harsh or piercing in speech",
                "nature": "Inauspicious",
                "deity": "Sarpa (Serpent)",
                "strength": "Medium"
            },
            {
                "name": "Ganda Yoga",
                "range": "120° - 133°20'",
                "effects": "Obstacles, difficulties, prone to accidents, need for caution in undertakings",
                "nature": "Inauspicious",
                "deity": "Agni (Fire)",
                "strength": "Medium"
            },
            {
                "name": "Vriddhi Yoga",
                "range": "133°20' - 146°40'",
                "effects": "Growth, expansion, prosperity, accumulation of wealth, business success",
                "nature": "Auspicious",
                "deity": "Vishnu (Preserver)",
                "strength": "Strong"
            },
            {
                "name": "Dhruva Yoga",
                "range": "146°40' - 160°",
                "effects": "Stability, permanence, fixed determination, long-lasting results, reliability",
                "nature": "Auspicious",
                "deity": "Bhumi (Earth)",
                "strength": "Strong"
            },
            {
                "name": "Vyaghata Yoga",
                "range": "160° - 173°20'",
                "effects": "Violence, conflicts, accidents, sudden events, aggressive tendencies",
                "nature": "Inauspicious",
                "deity": "Vayu (Wind)",
                "strength": "Medium"
            },
            {
                "name": "Harshana Yoga",
                "range": "173°20' - 186°40'",
                "effects": "Joy, cheerfulness, optimism, brings happiness to self and others, uplifting nature",
                "nature": "Auspicious",
                "deity": "Bhaga (Fortune)",
                "strength": "Strong"
            },
            {
                "name": "Vajra Yoga",
                "range": "186°40' - 200°",
                "effects": "Diamond-like strength, invincibility, powerful personality, strong constitution",
                "nature": "Auspicious",
                "deity": "Indra (King of Gods)",
                "strength": "Strong"
            },
            {
                "name": "Siddhi Yoga",
                "range": "200° - 213°20'",
                "effects": "Spiritual attainment, success in endeavors, accomplishment of goals, mastery",
                "nature": "Auspicious",
                "deity": "Ganesha (Remover of Obstacles)",
                "strength": "Very Strong"
            },
            {
                "name": "Vyatipata Yoga",
                "range": "213°20' - 226°40'",
                "effects": "Calamities, misfortunes, sudden reversals, need for careful planning",
                "nature": "Inauspicious",
                "deity": "Rudra (Destroyer)",
                "strength": "Medium"
            },
            {
                "name": "Variyan Yoga",
                "range": "226°40' - 240°",
                "effects": "Nobility, generosity, charitable nature, respected in society, humanitarian",
                "nature": "Auspicious",
                "deity": "Varuna (Water God)",
                "strength": "Strong"
            },
            {
                "name": "Parigha Yoga",
                "range": "240° - 253°20'",
                "effects": "Obstacles, confinement, restrictions, delays in achievements, perseverance needed",
                "nature": "Inauspicious",
                "deity": "Tvashta (Celestial Architect)",
                "strength": "Medium"
            },
            {
                "name": "Shiva Yoga",
                "range": "253°20' - 266°40'",
                "effects": "Auspiciousness, spiritual inclination, blessings of Lord Shiva, transformation",
                "nature": "Auspicious",
                "deity": "Shiva (Transformer)",
                "strength": "Very Strong"
            },
            {
                "name": "Siddha Yoga",
                "range": "266°40' - 280°",
                "effects": "Perfection, accomplishment, spiritual realization, mastery in chosen field",
                "nature": "Auspicious",
                "deity": "Kartikeya (Warrior God)",
                "strength": "Very Strong"
            },
            {
                "name": "Sadhya Yoga",
                "range": "280° - 293°20'",
                "effects": "Achievable goals, practical success, manifestation of desires, diligence",
                "nature": "Auspicious",
                "deity": "Savita (Solar Deity)",
                "strength": "Strong"
            },
            {
                "name": "Shubha Yoga",
                "range": "293°20' - 306°40'",
                "effects": "Auspiciousness, good fortune, pleasant life, beneficial results, positive outlook",
                "nature": "Auspicious",
                "deity": "Lakshmi (Goddess of Wealth)",
                "strength": "Strong"
            },
            {
                "name": "Shukla Yoga",
                "range": "306°40' - 320°",
                "effects": "Purity, righteousness, moral character, clean intentions, virtuous living",
                "nature": "Auspicious",
                "deity": "Parvati (Divine Mother)",
                "strength": "Strong"
            },
            {
                "name": "Brahma Yoga",
                "range": "320° - 333°20'",
                "effects": "Spiritual knowledge, wisdom, scholarly pursuits, connection with divine, vedic learning",
                "nature": "Auspicious",
                "deity": "Brahma (Creator)",
                "strength": "Very Strong"
            },
            {
                "name": "Indra Yoga",
                "range": "333°20' - 346°40'",
                "effects": "Leadership, authority, royal qualities, command over others, administrative skills",
                "nature": "Auspicious",
                "deity": "Indra (King of Gods)",
                "strength": "Very Strong"
            },
            {
                "name": "Vaidhriti Yoga",
                "range": "346°40' - 360°",
                "effects": "Obstacles, opposition, reversals, need for patience, challenges in sustaining efforts",
                "nature": "Inauspicious",
                "deity": "Pitris (Ancestors)",
                "strength": "Medium"
            }
        ]

        # Get the detected Nitya Yoga
        if 0 <= nitya_index < 27:
            nitya_data = nitya_yogas_data[nitya_index]

            # Calculate exact position within the yoga
            yoga_start = nitya_index * nitya_span
            position_in_yoga = distance - yoga_start
            percentage_through = (position_in_yoga / nitya_span) * 100

            # Build description
            desc = f"Sun-Moon distance {distance:.2f}° ({percentage_through:.1f}% through {nitya_data['range']}). "
            desc += f"Effects: {nitya_data['effects']}. "
            desc += f"Ruling Deity: {nitya_data['deity']}. "
            desc += f"Nature: {nitya_data['nature']}"

            yogas.append({
                "name": nitya_data["name"],
                "description": desc,
                "strength": nitya_data["strength"],
                "category": "Nitya Yoga (Birth Yoga)",
                "yoga_forming_planets": ["Sun", "Moon"],
                "formation": f"Sun-Moon angular distance: {distance:.2f}°",
                "sun_moon_distance": distance,
                "nitya_index": nitya_index + 1,  # 1-indexed for display
                "nature": nitya_data["nature"],
                "deity": nitya_data["deity"]
            })

        return yogas

    def calculate_yoga_timing(self, yoga: Dict, chart_data: Dict[str, Any], current_dasha: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Calculate when a yoga will fructify (become active) based on:
        - Dasha periods of yoga-forming planets
        - Transits of yoga-forming planets
        - Age-based activation

        Args:
            yoga: Detected yoga dict with name, planets, etc.
            chart_data: Full chart data including dashas
            current_dasha: Optional current dasha info

        Returns:
            Dictionary with timing information
        """
        timing_info = {
            "yoga_name": yoga.get("name", "Unknown"),
            "activation_status": "Unknown",
            "current_strength": yoga.get("strength", "Medium"),
            "dasha_activation_periods": [],
            "peak_periods": [],
            "general_activation_age": None,
            "recommendations": []
        }

        # Extract yoga-forming planets from description or default logic
        yoga_planets = self._extract_yoga_planets(yoga)

        if not yoga_planets:
            timing_info["activation_status"] = "Always Active"
            timing_info["recommendations"].append("This yoga's effects are constant throughout life")
            return timing_info

        # Get dasha information from chart
        dashas = chart_data.get("dashas", {})
        vimshottari = dashas.get("vimshottari_dasha", [])

        # Calculate dasha activation periods
        for dasha_period in vimshottari[:10]:  # Next 10 periods
            dasha_planet = dasha_period.get("planet", "")

            if dasha_planet in yoga_planets:
                timing_info["dasha_activation_periods"].append({
                    "planet": dasha_planet,
                    "start_date": dasha_period.get("start_date"),
                    "end_date": dasha_period.get("end_date"),
                    "period_type": "Mahadasha",
                    "intensity": "High"
                })

            # Check antardashas
            for antardasha in dasha_period.get("antardashas", [])[:5]:
                antardasha_planet = antardasha.get("planet", "")
                if antardasha_planet in yoga_planets:
                    timing_info["dasha_activation_periods"].append({
                        "planet": antardasha_planet,
                        "start_date": antardasha.get("start_date"),
                        "end_date": antardasha.get("end_date"),
                        "period_type": f"{dasha_planet} Mahadasha - {antardasha_planet} Antardasha",
                        "intensity": "Medium"
                    })

        # Determine general activation age based on yoga type
        yoga_category = yoga.get("category", "")

        if "Pancha Mahapurusha" in yoga_category:
            timing_info["general_activation_age"] = "25-35 years"
            timing_info["peak_periods"].append("During dasha/antardasha of the yoga planet")

        elif "Transformation" in yoga_category:
            timing_info["general_activation_age"] = "After 42 years (especially for Kala Sarpa)"
            timing_info["peak_periods"].append("Saturn maturity period (36+ years)")

        elif "Wealth" in yoga_category:
            timing_info["general_activation_age"] = "28-45 years"
            timing_info["peak_periods"].append("Jupiter and Venus dashas")

        elif "Fame" in yoga_category or "Power" in yoga_category:
            timing_info["general_activation_age"] = "32-50 years"
            timing_info["peak_periods"].append("Sun and Mars dashas, 10th house transits")

        else:
            timing_info["general_activation_age"] = "Throughout life with varying intensity"
            timing_info["peak_periods"].append("During relevant planetary periods")

        # Determine current activation status
        if current_dasha:
            current_planet = current_dasha.get("planet", "")
            if current_planet in yoga_planets:
                timing_info["activation_status"] = "Currently Active"
                timing_info["recommendations"].append(f"Yoga is active now during {current_planet} dasha - excellent time to leverage its benefits")
            else:
                timing_info["activation_status"] = "Dormant"
                next_period = next((p for p in timing_info["dasha_activation_periods"] if p["planet"] in yoga_planets), None)
                if next_period:
                    timing_info["recommendations"].append(f"Yoga will activate during {next_period['planet']} period starting {next_period.get('start_date', 'soon')}")

        return timing_info

    def _extract_yoga_planets(self, yoga: Dict) -> List[str]:
        """
        Extract the planets forming this yoga from its name/description
        """
        planets = []
        description = yoga.get("description", "").lower()
        name = yoga.get("name", "").lower()

        planet_keywords = {
            "Sun": ["sun"],
            "Moon": ["moon", "chandra"],
            "Mars": ["mars", "mangala", "kuja"],
            "Mercury": ["mercury", "budha"],
            "Jupiter": ["jupiter", "guru"],
            "Venus": ["venus", "shukra"],
            "Saturn": ["saturn", "shani"],
            "Rahu": ["rahu"],
            "Ketu": ["ketu"]
        }

        for planet, keywords in planet_keywords.items():
            if any(keyword in name or keyword in description for keyword in keywords):
                planets.append(planet)

        # Special cases
        if "pancha mahapurusha" in yoga.get("category", "").lower():
            if "ruchaka" in name:
                planets = ["Mars"]
            elif "bhadra" in name:
                planets = ["Mercury"]
            elif "hamsa" in name:
                planets = ["Jupiter"]
            elif "malavya" in name:
                planets = ["Venus"]
            elif "sasa" in name:
                planets = ["Saturn"]

        if "adhi" in name:
            planets = ["Mercury", "Venus", "Jupiter"]

        if "gaja kesari" in name or "gajakesari" in name:
            planets = ["Jupiter", "Moon"]

        return planets

    # ========================================================================
    # PHASE 4: BHAVA YOGAS (House Lord Placements)
    # ========================================================================

    # Sign lordships (1-indexed: 1=Aries, 2=Taurus, etc.)
    SIGN_LORDS = {
        1: "Mars",      # Aries
        2: "Venus",     # Taurus
        3: "Mercury",   # Gemini
        4: "Moon",      # Cancer
        5: "Sun",       # Leo
        6: "Mercury",   # Virgo
        7: "Venus",     # Libra
        8: "Mars",      # Scorpio
        9: "Jupiter",   # Sagittarius
        10: "Saturn",   # Capricorn
        11: "Saturn",   # Aquarius
        12: "Jupiter"   # Pisces
    }

    def get_house_lord(self, house_number: int, ascendant_sign: int) -> str:
        """
        Determine which planet rules a specific house.

        In Vedic astrology (whole sign house system), each house corresponds
        to a sign, and each sign has a ruling planet.

        Args:
            house_number: 1-12 (house to find lord for)
            ascendant_sign: 1-12 (Aries=1, Taurus=2, etc.)

        Returns:
            Planet name that rules the house

        Example:
            For Aries ascendant (ascendant_sign=1):
            - 1st house = Aries → ruled by Mars
            - 2nd house = Taurus → ruled by Venus
            - 10th house = Capricorn → ruled by Saturn
        """
        # Calculate the sign of the house
        # house_sign = ((ascendant_sign - 1) + (house_number - 1)) % 12 + 1
        house_sign = ((ascendant_sign - 1 + house_number - 1) % 12) + 1

        return self.SIGN_LORDS[house_sign]

    def get_house_lords_map(self, ascendant_sign: int) -> Dict[int, str]:
        """
        Get all 12 house lords for a chart.

        Args:
            ascendant_sign: 1-12 (Aries=1, Taurus=2, etc.)

        Returns:
            Dictionary mapping house number (1-12) to ruling planet

        Example:
            For Aries ascendant: {1: "Mars", 2: "Venus", 3: "Mercury", ...}
        """
        return {house: self.get_house_lord(house, ascendant_sign) for house in range(1, 13)}

    def _get_ascendant_sign(self, planets: Dict) -> Optional[int]:
        """
        Extract ascendant sign from planets dict.

        The ascendant sign might be stored in:
        - planets["Ascendant"]["sign_num"]
        - planets["Lagna"]["sign_num"]
        - Or passed separately

        Returns:
            Ascendant sign (1-12) or None if not found
        """
        # Try different keys for ascendant
        for key in ["Ascendant", "Lagna", "ASC"]:
            if key in planets:
                sign_num = planets[key].get("sign_num")
                if sign_num is not None:
                    # Ensure it's 1-indexed
                    if sign_num == 0:
                        return 1
                    return sign_num if sign_num <= 12 else sign_num

        return None

    def _detect_bhava_yogas(self, planets: Dict) -> List[Dict]:
        """
        Detect Bhava Yogas based on house lord placements.

        Bhava Yogas are formed when a house lord (ruler of a house) is placed
        in a specific house, creating unique combinations with distinct effects.

        Formula: 12 house lords × 12 possible placements = 144 combinations

        Complete implementation: All 12 house lords (1-12) = 144 yogas

        House Lords by Significance:
        - 1st lord (Lagna/Tanu Karaka) - Self, personality, vitality
        - 2nd lord (Dhana Karaka) - Wealth, family, speech
        - 3rd lord (Sahaja Karaka) - Siblings, courage, communication
        - 4th lord (Sukha Karaka) - Mother, property, education, happiness
        - 5th lord (Putra Karaka) - Intelligence, children, past merit
        - 6th lord (Ripu/Shatru Karaka) - Enemies, service, health
        - 7th lord (Kalatra Karaka) - Spouse, partnerships, business
        - 8th lord (Randhra Karaka) - Longevity, transformation, occult
        - 9th lord (Dharma/Bhagya Karaka) - Fortune, father, spirituality
        - 10th lord (Karma Karaka) - Career, status, profession
        - 11th lord (Labha Karaka) - Gains, income, desires, friends
        - 12th lord (Vyaya Karaka) - Expenses, losses, foreign, moksha

        Args:
            planets: Dictionary of planetary positions with house and sign_num

        Returns:
            List of detected Bhava Yogas
        """
        yogas = []

        # Get ascendant sign
        ascendant_sign = self._get_ascendant_sign(planets)

        if not ascendant_sign:
            # Can't detect Bhava Yogas without ascendant
            return yogas

        # Get all house lords
        house_lords = self.get_house_lords_map(ascendant_sign)

        # Detect all 12 house lords (complete Bhava Yoga system)
        # All lords are important as each governs specific life areas
        all_lords = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        for lord_house in all_lords:
            lord_planet = house_lords[lord_house]
            lord_placement = planets.get(lord_planet, {}).get("house", 0)

            if lord_placement and lord_placement > 0:
                yoga = self._get_bhava_yoga_details(
                    lord_house,
                    lord_placement,
                    lord_planet,
                    ascendant_sign
                )
                if yoga:
                    yogas.append(yoga)

        return yogas

    def _get_bhava_yoga_details(
        self,
        lord_house: int,
        placement: int,
        planet: str,
        ascendant_sign: int
    ) -> Optional[Dict]:
        """
        Get detailed effects for a specific house lord placement (Bhava Yoga).

        Args:
            lord_house: Which house lord (1-12)
            placement: Where the lord is placed (1-12)
            planet: The planet that is the lord
            ascendant_sign: The ascendant sign (1-12)

        Returns:
            Yoga dict with name, description, effects, strength, or None
        """
        # Define house names for readability
        house_names = {
            1: "1st (Lagna)", 2: "2nd (Dhana)", 3: "3rd (Sahaja)",
            4: "4th (Sukha)", 5: "5th (Putra)", 6: "6th (Ripu)",
            7: "7th (Kalatra)", 8: "8th (Randhra)", 9: "9th (Dharma)",
            10: "10th (Karma)", 11: "11th (Labha)", 12: "12th (Vyaya)"
        }

        # Calculate house distance (useful for determining strength)
        distance_from_lagna = placement
        is_kendra = placement in [1, 4, 7, 10]
        is_trikona = placement in [1, 5, 9]
        is_dusthana = placement in [6, 8, 12]
        is_upachaya = placement in [3, 6, 10, 11]

        # Determine strength based on placement type
        if is_kendra and is_trikona:  # 1st house
            base_strength = "Very Strong"
        elif is_kendra or is_trikona:
            base_strength = "Strong"
        elif is_upachaya:
            base_strength = "Medium"
        elif is_dusthana:
            base_strength = "Weak"
        else:
            base_strength = "Medium"

        # Get specific effects based on lord_house and placement
        effects_data = self._get_bhava_yoga_effects(lord_house, placement)

        if not effects_data:
            return None

        return {
            "name": effects_data["name"],
            "description": effects_data["description"],
            "strength": effects_data.get("strength", base_strength),
            "category": "Bhava Yoga (House Lord Placement)",
            "yoga_forming_planets": [planet],
            "formation": f"{lord_house}{self._get_ordinal(lord_house)} lord ({planet}) in {placement}{self._get_ordinal(placement)} house",
            "effects": effects_data["effects"],
            "life_areas": effects_data.get("life_areas", [])
        }

    def _get_ordinal(self, n: int) -> str:
        """Convert number to ordinal string (1 → st, 2 → nd, etc.)"""
        if 11 <= n <= 13:
            return "th"
        last_digit = n % 10
        if last_digit == 1:
            return "st"
        elif last_digit == 2:
            return "nd"
        elif last_digit == 3:
            return "rd"
        else:
            return "th"

    def _get_bhava_yoga_effects(self, lord_house: int, placement: int) -> Optional[Dict]:
        """
        Get classical effects for house lord placements from BPHS.

        This contains the core wisdom of Bhava Yogas - effects when a house lord
        occupies a specific house.

        Complete implementation (144 Bhava Yogas):
        - 1st lord placements (12 yogas) - Lagna/Self yogas
        - 2nd lord placements (12 yogas) - Wealth/Family yogas
        - 3rd lord placements (12 yogas) - Courage/Skills yogas
        - 4th lord placements (12 yogas) - Property/Happiness yogas
        - 5th lord placements (12 yogas) - Intelligence/Children yogas
        - 6th lord placements (12 yogas) - Service/Health yogas
        - 7th lord placements (12 yogas) - Partnership/Marriage yogas
        - 8th lord placements (12 yogas) - Transformation/Occult yogas
        - 9th lord placements (12 yogas) - Fortune/Dharma yogas
        - 10th lord placements (12 yogas) - Career/Karma yogas
        - 11th lord placements (12 yogas) - Gains/Income yogas
        - 12th lord placements (12 yogas) - Moksha/Foreign yogas

        Total: 144 complete Bhava Yogas (all house lord combinations)

        Args:
            lord_house: Which house lord (1-12)
            placement: Where it's placed (1-12)

        Returns:
            Dict with name, description, effects, strength, life_areas
        """
        # All Bhava Yoga effects database
        # Format: bhava_effects[lord_house][placement] = {name, description, effects, strength, life_areas}

        bhava_effects = {}

        # ====================================================================
        # 1ST LORD (LAGNA LORD) PLACEMENTS - Self, Personality, Life Path
        # ====================================================================
        bhava_effects[1] = {
            1: {
                "name": "Lagna Adhi Yoga",
                "description": "1st lord in 1st house - Self-empowered personality",
                "effects": "Strong personality, good health, magnetic presence, self-confidence, leadership qualities, independent nature, long life",
                "strength": "Very Strong",
                "life_areas": ["Personality", "Health", "Self-confidence", "Leadership"]
            },
            2: {
                "name": "Dhana Yoga",
                "description": "1st lord in 2nd house - Self-earned wealth",
                "effects": "Wealth through own efforts, eloquent speech, family support, good financial sense, accumulation of resources",
                "strength": "Strong",
                "life_areas": ["Wealth", "Family", "Speech", "Resources"]
            },
            3: {
                "name": "Sahasa Yoga",
                "description": "1st lord in 3rd house - Courage and skills",
                "effects": "Courageous nature, younger siblings bring joy, skilled in arts/crafts, short journeys profitable, self-made success",
                "strength": "Medium",
                "life_areas": ["Courage", "Siblings", "Skills", "Communication"]
            },
            4: {
                "name": "Sukha Yoga",
                "description": "1st lord in 4th house - Happiness and comfort",
                "effects": "Property ownership, vehicles, mother's blessings, educational success, domestic happiness, comfortable life",
                "strength": "Strong",
                "life_areas": ["Property", "Mother", "Education", "Happiness"]
            },
            5: {
                "name": "Putra Yoga",
                "description": "1st lord in 5th house - Intelligence and progeny",
                "effects": "High intelligence, blessed with children, creative talents, good speculation, spiritual inclinations, past life merit",
                "strength": "Very Strong",
                "life_areas": ["Intelligence", "Children", "Creativity", "Spirituality"]
            },
            6: {
                "name": "Ripu Sthana Yoga",
                "description": "1st lord in 6th house - Victory over obstacles",
                "effects": "Health challenges but eventual victory over enemies, success in service/competition, ability to overcome obstacles, may face debts early in life",
                "strength": "Weak",
                "life_areas": ["Health", "Enemies", "Service", "Competition"]
            },
            7: {
                "name": "Kalatra Yoga",
                "description": "1st lord in 7th house - Partnership focused",
                "effects": "Focus on partnerships, spouse plays important role, business success, public relations skills, may travel for work/partnership",
                "strength": "Strong",
                "life_areas": ["Marriage", "Partnership", "Business", "Travel"]
            },
            8: {
                "name": "Ayu Sthana Yoga",
                "description": "1st lord in 8th house - Transformation and longevity",
                "effects": "Interest in occult/mysticism, transformative life experiences, research abilities, inheritance possible, need to guard health",
                "strength": "Weak",
                "life_areas": ["Longevity", "Occult", "Research", "Transformation"]
            },
            9: {
                "name": "Bhagya Yoga",
                "description": "1st lord in 9th house - Fortune and blessings",
                "effects": "Great fortune, father's support, spiritual wisdom, higher education, long journeys bring success, dharmic life, strong moral character",
                "strength": "Very Strong",
                "life_areas": ["Fortune", "Father", "Spirituality", "Higher Education"]
            },
            10: {
                "name": "Karma Yoga",
                "description": "1st lord in 10th house - Career success",
                "effects": "Outstanding career success, fame, leadership in profession, authority, respect in society, strong work ethic, public recognition",
                "strength": "Very Strong",
                "life_areas": ["Career", "Fame", "Leadership", "Authority"]
            },
            11: {
                "name": "Labha Yoga",
                "description": "1st lord in 11th house - Gains and fulfillment",
                "effects": "Multiple income sources, fulfillment of desires, large friend circle, elder siblings supportive, gains increase with age",
                "strength": "Strong",
                "life_areas": ["Gains", "Friends", "Desires", "Income"]
            },
            12: {
                "name": "Vyaya Sthana Yoga",
                "description": "1st lord in 12th house - Foreign lands and spirituality",
                "effects": "Foreign residence/travel, spiritual pursuits, expenses on self, isolation for meditation, success in foreign lands, charitable nature",
                "strength": "Medium",
                "life_areas": ["Foreign Lands", "Spirituality", "Expenses", "Isolation"]
            }
        }

        # ====================================================================
        # 9TH LORD (DHARMA LORD) PLACEMENTS - Fortune, Father, Spirituality
        # ====================================================================
        bhava_effects[9] = {
            1: {
                "name": "Dharma Lagna Yoga",
                "description": "9th lord in 1st house - Fortune in personality",
                "effects": "Fortunate personality, blessed life, dharmic conduct, wise and philosophical, respected for knowledge, father's blessings strong",
                "strength": "Very Strong",
                "life_areas": ["Fortune", "Wisdom", "Respect", "Dharma"]
            },
            2: {
                "name": "Dhana Dharma Yoga",
                "description": "9th lord in 2nd house - Wealth through fortune",
                "effects": "Wealth from fortune and family, father may help financially, truthful speech brings gains, family traditions important",
                "strength": "Strong",
                "life_areas": ["Wealth", "Family", "Fortune", "Values"]
            },
            3: {
                "name": "Sahasa Dharma Yoga",
                "description": "9th lord in 3rd house - Fortune through courage",
                "effects": "Fortune through self-effort and courage, younger siblings blessed, communication skills lead to success, religious writings possible",
                "strength": "Medium",
                "life_areas": ["Courage", "Communication", "Self-effort", "Writing"]
            },
            4: {
                "name": "Sukha Dharma Yoga",
                "description": "9th lord in 4th house - Fortunate domestic life",
                "effects": "Property through fortune, mother is fortunate, educational opportunities abundant, vehicles and comforts, peaceful home",
                "strength": "Strong",
                "life_areas": ["Property", "Mother", "Education", "Comfort"]
            },
            5: {
                "name": "Putra Dharma Yoga",
                "description": "9th lord in 5th house - Highly fortunate yoga",
                "effects": "Excellent Raj Yoga - blessed children, high intelligence, spiritual wisdom, creative genius, speculation brings gains, mantra siddhi possible",
                "strength": "Very Strong",
                "life_areas": ["Children", "Intelligence", "Spirituality", "Creativity"]
            },
            6: {
                "name": "Ripu Dharma Yoga",
                "description": "9th lord in 6th house - Challenges to fortune",
                "effects": "Father may have health issues, fortune comes through service/competition, obstacles to higher education initially, victory over enemies through dharma",
                "strength": "Weak",
                "life_areas": ["Service", "Obstacles", "Father's Health", "Competition"]
            },
            7: {
                "name": "Kalatra Dharma Yoga",
                "description": "9th lord in 7th house - Fortune through partnerships",
                "effects": "Fortunate marriage, spouse brings luck, business partnerships blessed, travel for spiritual/business purposes successful",
                "strength": "Strong",
                "life_areas": ["Marriage", "Partnership", "Fortune", "Travel"]
            },
            8: {
                "name": "Randhra Dharma Yoga",
                "description": "9th lord in 8th house - Hidden fortune",
                "effects": "Inheritance possible, sudden gains from fortune, interest in occult/spirituality deepens with age, father's longevity good, research into philosophy",
                "strength": "Medium",
                "life_areas": ["Inheritance", "Occult", "Research", "Sudden Gains"]
            },
            9: {
                "name": "Dharma Adhi Yoga",
                "description": "9th lord in 9th house - Maximum fortune",
                "effects": "Extremely fortunate life, father is prosperous and supportive, higher education abroad possible, spiritual teacher potential, pilgrimage to holy places, dharmic wealth",
                "strength": "Very Strong",
                "life_areas": ["Fortune", "Father", "Higher Education", "Spirituality"]
            },
            10: {
                "name": "Karma Dharma Yoga (Dharma-Karmadhipati Yoga)",
                "description": "9th lord in 10th house - Fortune through career",
                "effects": "Raj Yoga - career brings fortune, ethical profession, fame through righteous action, father may influence career, respected leader",
                "strength": "Very Strong",
                "life_areas": ["Career", "Fortune", "Ethics", "Fame"]
            },
            11: {
                "name": "Labha Dharma Yoga",
                "description": "9th lord in 11th house - Fortune brings gains",
                "effects": "Fortunate gains, desires fulfilled easily, elder siblings fortunate, income from multiple sources, fortune increases after marriage",
                "strength": "Strong",
                "life_areas": ["Gains", "Desires", "Fortune", "Income"]
            },
            12: {
                "name": "Vyaya Dharma Yoga",
                "description": "9th lord in 12th house - Foreign fortune and moksha",
                "effects": "Fortune in foreign lands, spiritual expenditures bring merit, pilgrimage expenses, father may reside abroad, moksha yoga - liberation pursuits",
                "strength": "Medium",
                "life_areas": ["Foreign Lands", "Spirituality", "Pilgrimage", "Liberation"]
            }
        }

        # ====================================================================
        # 10TH LORD (KARMA LORD) PLACEMENTS - Career, Status, Profession
        # ====================================================================
        bhava_effects[10] = {
            1: {
                "name": "Karma Lagna Yoga",
                "description": "10th lord in 1st house - Career-focused personality",
                "effects": "Strong career focus, self-made success, professional reputation excellent, leadership in chosen field, work defines identity",
                "strength": "Very Strong",
                "life_areas": ["Career", "Self-made Success", "Leadership", "Identity"]
            },
            2: {
                "name": "Dhana Karma Yoga",
                "description": "10th lord in 2nd house - Wealth through career",
                "effects": "Career brings wealth, family profession possible, eloquent professional speaker, financial success through work, reputation for earning ability",
                "strength": "Strong",
                "life_areas": ["Wealth", "Career", "Family Business", "Speech"]
            },
            3: {
                "name": "Sahasa Karma Yoga",
                "description": "10th lord in 3rd house - Career through skills",
                "effects": "Success through skills and communication, media/writing career possible, younger siblings help career, short business trips, courageous professional decisions",
                "strength": "Medium",
                "life_areas": ["Skills", "Communication", "Media", "Courage"]
            },
            4: {
                "name": "Sukha Karma Yoga",
                "description": "10th lord in 4th house - Career brings comfort",
                "effects": "Real estate career possible, mother influences profession, educational institutions, vehicles for work, professional happiness, work from home success",
                "strength": "Strong",
                "life_areas": ["Real Estate", "Education", "Mother's Influence", "Comfort"]
            },
            5: {
                "name": "Putra Karma Yoga",
                "description": "10th lord in 5th house - Creative career success",
                "effects": "Creative profession, children may continue profession, intelligent career choices, speculation in career pays off, teaching/entertainment career",
                "strength": "Strong",
                "life_areas": ["Creativity", "Children", "Teaching", "Entertainment"]
            },
            6: {
                "name": "Ripu Karma Yoga",
                "description": "10th lord in 6th house - Service-oriented career",
                "effects": "Service profession (medical, legal, military), competitive career, success over professional rivals, litigation expertise, health-related profession",
                "strength": "Medium",
                "life_areas": ["Service", "Competition", "Medicine", "Law"]
            },
            7: {
                "name": "Kalatra Karma Yoga",
                "description": "10th lord in 7th house - Partnership in career",
                "effects": "Business partnerships successful, spouse may be business partner, foreign business, public relations career, consulting profession",
                "strength": "Strong",
                "life_areas": ["Business Partnership", "Foreign Trade", "Consulting", "Public Relations"]
            },
            8: {
                "name": "Randhra Karma Yoga",
                "description": "10th lord in 8th house - Transformative career",
                "effects": "Research career, occult/astrology profession, sudden career changes, insurance/investigation work, inheritance may affect career, crisis management",
                "strength": "Weak",
                "life_areas": ["Research", "Occult", "Investigation", "Transformation"]
            },
            9: {
                "name": "Dharma Karma Yoga",
                "description": "10th lord in 9th house - Fortunate career (Raj Yoga)",
                "effects": "Highly fortunate profession, father helps career, higher education leads to career success, teaching/law/religion career, foreign assignments, ethical profession brings respect",
                "strength": "Very Strong",
                "life_areas": ["Fortune", "Higher Education", "Teaching", "Ethics"]
            },
            10: {
                "name": "Karma Adhi Yoga",
                "description": "10th lord in 10th house - Career powerhouse",
                "effects": "Extraordinary career success, natural leader, peak professional achievement, authority in field, famous in profession, strong work ethic, lasting legacy",
                "strength": "Very Strong",
                "life_areas": ["Career Success", "Fame", "Authority", "Legacy"]
            },
            11: {
                "name": "Labha Karma Yoga",
                "description": "10th lord in 11th house - Career brings massive gains",
                "effects": "High income from career, professional desires fulfilled, network crucial for career, multiple income streams from profession, elder siblings aid career",
                "strength": "Very Strong",
                "life_areas": ["Income", "Gains", "Networking", "Desires"]
            },
            12: {
                "name": "Vyaya Karma Yoga",
                "description": "10th lord in 12th house - Foreign/spiritual career",
                "effects": "Foreign career/postings, hospital/prison/ashram work, spiritual profession, expenses on career, work in isolated places, charitable organizations, behind-scenes work",
                "strength": "Medium",
                "life_areas": ["Foreign Career", "Spirituality", "Isolation", "Charity"]
            }
        }

        # ====================================================================
        # 5TH LORD (PURVA PUNYA) PLACEMENTS - Intelligence, Children, Creativity
        # ====================================================================
        bhava_effects[5] = {
            1: {
                "name": "Putra Lagna Yoga",
                "description": "5th lord in 1st house - Intelligence shines",
                "effects": "Highly intelligent personality, creative self-expression, speculative mind, children bring joy, past life merits visible, romantic nature",
                "strength": "Strong",
                "life_areas": ["Intelligence", "Creativity", "Children", "Romance"]
            },
            2: {
                "name": "Dhana Putra Yoga",
                "description": "5th lord in 2nd house - Wealth through intelligence",
                "effects": "Intelligent financial decisions, speculation brings wealth, children contribute to family wealth, creative speech/voice, artistic talents bring income",
                "strength": "Strong",
                "life_areas": ["Wealth", "Speculation", "Creativity", "Speech"]
            },
            3: {
                "name": "Sahasa Putra Yoga",
                "description": "5th lord in 3rd house - Creative communication",
                "effects": "Creative writing/media skills, younger siblings intelligent, artistic crafts, courageous speculation, short travels with children",
                "strength": "Medium",
                "life_areas": ["Writing", "Communication", "Arts", "Siblings"]
            },
            4: {
                "name": "Sukha Putra Yoga",
                "description": "5th lord in 4th house - Domestic creativity",
                "effects": "Children bring domestic happiness, property through speculation, creative home environment, mother is creative/intelligent, educational institutions at home",
                "strength": "Strong",
                "life_areas": ["Home", "Children", "Education", "Property"]
            },
            5: {
                "name": "Putra Adhi Yoga",
                "description": "5th lord in 5th house - Maximum creativity",
                "effects": "Blessed with intelligent children, exceptional creativity, speculation highly favorable, mantra siddhi, teaching abilities, spiritual practices powerful, romance flourishes",
                "strength": "Very Strong",
                "life_areas": ["Children", "Creativity", "Spirituality", "Speculation"]
            },
            6: {
                "name": "Ripu Putra Yoga",
                "description": "5th lord in 6th house - Challenges to progeny",
                "effects": "Delayed children or health issues to children, speculation may cause debts, creative work in service/medicine, competitive intelligence, victory through intellect",
                "strength": "Weak",
                "life_areas": ["Obstacles", "Service", "Children's Health", "Competition"]
            },
            7: {
                "name": "Kalatra Putra Yoga",
                "description": "5th lord in 7th house - Creative partnerships",
                "effects": "Spouse is creative/intelligent, children after marriage bring joy, creative business partnerships, romantic marriage, speculation in partnership",
                "strength": "Strong",
                "life_areas": ["Marriage", "Partnership", "Romance", "Children"]
            },
            8: {
                "name": "Randhra Putra Yoga",
                "description": "5th lord in 8th house - Hidden creativity",
                "effects": "Interest in occult knowledge, research-oriented intelligence, sudden speculative gains/losses, inheritance from children, transformative creativity, mystical children",
                "strength": "Weak",
                "life_areas": ["Occult", "Research", "Transformation", "Speculation"]
            },
            9: {
                "name": "Dharma Putra Yoga (Raj Yoga)",
                "description": "5th lord in 9th house - Fortunate intelligence",
                "effects": "Excellent Raj Yoga - highly intelligent and fortunate children, past merit brings fortune, creative spiritual wisdom, higher education excellent, speculation blessed by luck",
                "strength": "Very Strong",
                "life_areas": ["Fortune", "Intelligence", "Spirituality", "Children"]
            },
            10: {
                "name": "Karma Putra Yoga",
                "description": "5th lord in 10th house - Creative career",
                "effects": "Creative profession brings success, children follow in career, intelligent career decisions, speculation affects career, teaching/entertainment profession",
                "strength": "Strong",
                "life_areas": ["Career", "Creativity", "Children", "Fame"]
            },
            11: {
                "name": "Labha Putra Yoga",
                "description": "5th lord in 11th house - Creative gains",
                "effects": "Speculation brings gains, children achieve their desires, creative network, multiple income from creative work, fulfillment through children",
                "strength": "Strong",
                "life_areas": ["Gains", "Children", "Speculation", "Desires"]
            },
            12: {
                "name": "Vyaya Putra Yoga",
                "description": "5th lord in 12th house - Foreign creativity",
                "effects": "Children may reside abroad, creative work in isolation, expenses on children's education, speculation causes expenses, spiritual creativity, meditation brings insights",
                "strength": "Medium",
                "life_areas": ["Foreign Lands", "Spirituality", "Expenses", "Isolation"]
            }
        }

        # ====================================================================
        # 2ND LORD (DHANA KARAKA) PLACEMENTS - Wealth, Family, Speech
        # ====================================================================
        bhava_effects[2] = {
            1: {
                "name": "Dhana Lagna Yoga",
                "description": "2nd lord in 1st house - Self-earned wealth",
                "effects": "Self-made wealth, eloquent speaker, strong family values, attractive face, good eating habits, resourceful personality, wealth through personal efforts",
                "strength": "Strong",
                "life_areas": ["Wealth", "Personality", "Speech", "Self-reliance"]
            },
            2: {
                "name": "Dhana Adhi Yoga",
                "description": "2nd lord in 2nd house - Wealth multiplication",
                "effects": "Great wealth accumulation, strong family bonds, sweet speech, excellent financial management, inheritance, multiple income sources, food prosperity",
                "strength": "Very Strong",
                "life_areas": ["Wealth", "Family", "Speech", "Prosperity"]
            },
            3: {
                "name": "Sahasa Dhana Yoga",
                "description": "2nd lord in 3rd house - Wealth through courage",
                "effects": "Wealth through skills/arts, siblings support financially, earnings from communication/writing, self-effort brings money, short journeys profitable",
                "strength": "Medium",
                "life_areas": ["Skills", "Communication", "Siblings", "Courage"]
            },
            4: {
                "name": "Sukha Dhana Yoga",
                "description": "2nd lord in 4th house - Property wealth",
                "effects": "Wealth from property/vehicles, mother's family prosperous, comfortable home life, education brings wealth, real estate success, landed property",
                "strength": "Strong",
                "life_areas": ["Property", "Comfort", "Education", "Mother"]
            },
            5: {
                "name": "Putra Dhana Yoga",
                "description": "2nd lord in 5th house - Intelligent wealth",
                "effects": "Wealth through speculation/investments, children bring prosperity, creative earnings, past life merit brings wealth, lottery/shares favorable, intelligent financial decisions",
                "strength": "Very Strong",
                "life_areas": ["Speculation", "Children", "Intelligence", "Investments"]
            },
            6: {
                "name": "Ripu Dhana Yoga",
                "description": "2nd lord in 6th house - Service wealth",
                "effects": "Earnings through service/medicine, wealth after overcoming obstacles, loans/debts possible but manageable, enemies create financial stress, health expenses",
                "strength": "Weak",
                "life_areas": ["Service", "Debts", "Obstacles", "Health"]
            },
            7: {
                "name": "Kalatra Dhana Yoga",
                "description": "2nd lord in 7th house - Partnership wealth",
                "effects": "Wealth through spouse/partnerships, business brings prosperity, marriage improves finances, foreign trade profitable, eloquent in public speaking",
                "strength": "Strong",
                "life_areas": ["Marriage", "Business", "Partnership", "Trade"]
            },
            8: {
                "name": "Randhra Dhana Yoga",
                "description": "2nd lord in 8th house - Hidden wealth",
                "effects": "Sudden financial ups and downs, inheritance likely, wealth through research/occult, family secrets affect finances, longevity of wealth uncertain, insurance/wills important",
                "strength": "Weak",
                "life_areas": ["Inheritance", "Uncertainty", "Occult", "Transformation"]
            },
            9: {
                "name": "Dharma Dhana Yoga (Raj Yoga)",
                "description": "2nd lord in 9th house - Fortune wealth",
                "effects": "Excellent Raj Yoga - wealth through father/gurus, dharmic earnings, religious donations bring returns, fortunate family, higher education brings wealth, ethical money",
                "strength": "Very Strong",
                "life_areas": ["Fortune", "Ethics", "Father", "Spirituality"]
            },
            10: {
                "name": "Karma Dhana Yoga",
                "description": "2nd lord in 10th house - Career wealth",
                "effects": "Wealth through profession, family business success, career brings financial stability, good reputation increases earnings, government favor possible",
                "strength": "Strong",
                "life_areas": ["Career", "Profession", "Reputation", "Authority"]
            },
            11: {
                "name": "Labha Dhana Yoga",
                "description": "2nd lord in 11th house - Continuous gains",
                "effects": "Excellent wealth yoga - multiple income streams, elder siblings helpful, desires fulfilled through wealth, network brings prosperity, steady gains throughout life",
                "strength": "Very Strong",
                "life_areas": ["Gains", "Income", "Desires", "Network"]
            },
            12: {
                "name": "Vyaya Dhana Yoga",
                "description": "2nd lord in 12th house - Expenses on family",
                "effects": "Family expenses high, wealth goes to charity/spirituality, foreign residence possible, speech may cause losses, expenditure on education, hidden wealth abroad",
                "strength": "Medium",
                "life_areas": ["Expenses", "Foreign", "Charity", "Losses"]
            }
        }

        # ====================================================================
        # 3RD LORD (SAHAJA KARAKA) PLACEMENTS - Siblings, Courage, Communication
        # ====================================================================
        bhava_effects[3] = {
            1: {
                "name": "Sahasa Lagna Yoga",
                "description": "3rd lord in 1st house - Courageous personality",
                "effects": "Very courageous and adventurous, self-reliant nature, younger siblings influence life, skilled in arts/crafts, active communication style, athletic build",
                "strength": "Strong",
                "life_areas": ["Courage", "Skills", "Independence", "Communication"]
            },
            2: {
                "name": "Dhana Sahaja Yoga",
                "description": "3rd lord in 2nd house - Wealth through skills",
                "effects": "Earnings through skills/arts, siblings contribute to wealth, communication skills bring money, family supports courage, writing/media income",
                "strength": "Medium",
                "life_areas": ["Skills", "Wealth", "Communication", "Siblings"]
            },
            3: {
                "name": "Sahaja Adhi Yoga",
                "description": "3rd lord in 3rd house - Maximum courage",
                "effects": "Extremely courageous, excellent relationship with siblings, highly skilled, successful in arts/media, short travels beneficial, strong willpower, initiative brings success",
                "strength": "Very Strong",
                "life_areas": ["Courage", "Siblings", "Skills", "Initiative"]
            },
            4: {
                "name": "Sukha Sahaja Yoga",
                "description": "3rd lord in 4th house - Skillful comfort",
                "effects": "Property through self-effort, mother encourages skills, comfortable life through talents, vehicles for travel, education in arts, home-based creative work",
                "strength": "Medium",
                "life_areas": ["Property", "Skills", "Comfort", "Mother"]
            },
            5: {
                "name": "Putra Sahaja Yoga",
                "description": "3rd lord in 5th house - Creative skills",
                "effects": "Highly creative and artistic, children are talented, speculation through skills, intelligent communication, performing arts, romantic courage",
                "strength": "Strong",
                "life_areas": ["Creativity", "Skills", "Children", "Romance"]
            },
            6: {
                "name": "Ripu Sahaja Yoga",
                "description": "3rd lord in 6th house - Competitive courage",
                "effects": "Victory through courage, siblings may have health issues, competition brings success, service requires skills, courage overcomes enemies, medical/healing skills",
                "strength": "Medium",
                "life_areas": ["Competition", "Service", "Courage", "Victory"]
            },
            7: {
                "name": "Kalatra Sahaja Yoga",
                "description": "3rd lord in 7th house - Partnership skills",
                "effects": "Spouse is artistic/communicative, business partnerships successful, courage in relationships, travels with spouse, diplomatic skills, trade journeys",
                "strength": "Medium",
                "life_areas": ["Partnership", "Communication", "Business", "Travel"]
            },
            8: {
                "name": "Randhra Sahaja Yoga",
                "description": "3rd lord in 8th house - Hidden talents",
                "effects": "Courage in crisis, research/investigative skills, occult communication abilities, transformative efforts, siblings face ups and downs, longevity through courage",
                "strength": "Weak",
                "life_areas": ["Research", "Occult", "Crisis", "Transformation"]
            },
            9: {
                "name": "Dharma Sahaja Yoga",
                "description": "3rd lord in 9th house - Dharmic courage",
                "effects": "Courageous in dharma, long journeys bring skills, siblings are fortunate, religious arts/music, teaching communication, publishing success, pilgrimage journeys",
                "strength": "Strong",
                "life_areas": ["Fortune", "Travel", "Teaching", "Publishing"]
            },
            10: {
                "name": "Karma Sahaja Yoga",
                "description": "3rd lord in 10th house - Skillful career",
                "effects": "Career in communication/media/arts, self-made career success, professional skills recognized, siblings help career, entrepreneurial courage, performance profession",
                "strength": "Strong",
                "life_areas": ["Career", "Skills", "Performance", "Recognition"]
            },
            11: {
                "name": "Labha Sahaja Yoga",
                "description": "3rd lord in 11th house - Gains through skills",
                "effects": "Skills bring income, siblings bring gains, desires fulfilled through effort, communication network profitable, artistic income, wishes achieved through courage",
                "strength": "Strong",
                "life_areas": ["Gains", "Skills", "Desires", "Network"]
            },
            12: {
                "name": "Vyaya Sahaja Yoga",
                "description": "3rd lord in 12th house - Foreign skills",
                "effects": "Skills used abroad, siblings may live far away, expenses on hobbies/arts, isolation develops talents, spiritual communication, meditation requires effort",
                "strength": "Weak",
                "life_areas": ["Foreign", "Isolation", "Spirituality", "Expenses"]
            }
        }

        # ====================================================================
        # 4TH LORD (SUKHA KARAKA) PLACEMENTS - Mother, Property, Education, Happiness
        # ====================================================================
        bhava_effects[4] = {
            1: {
                "name": "Sukha Lagna Yoga",
                "description": "4th lord in 1st house - Comfortable personality",
                "effects": "Mother's influence strong, property ownership, vehicles, educational success, peaceful nature, domestic happiness, emotional security, comfortable life",
                "strength": "Strong",
                "life_areas": ["Comfort", "Mother", "Property", "Education"]
            },
            2: {
                "name": "Dhana Sukha Yoga",
                "description": "4th lord in 2nd house - Property wealth",
                "effects": "Wealth through real estate, family property, mother brings prosperity, comfortable family life, ancestral wealth, vehicles as assets, savings for comfort",
                "strength": "Strong",
                "life_areas": ["Property", "Wealth", "Family", "Assets"]
            },
            3: {
                "name": "Sahaja Sukha Yoga",
                "description": "4th lord in 3rd house - Property through effort",
                "effects": "Property through self-effort, mother encourages skills, siblings share property, short moves for property, courage brings comfort, education in arts",
                "strength": "Medium",
                "life_areas": ["Effort", "Property", "Skills", "Siblings"]
            },
            4: {
                "name": "Sukha Adhi Yoga",
                "description": "4th lord in 4th house - Maximum happiness",
                "effects": "Excellent property holdings, strong mother's support, multiple vehicles, superior education, domestic bliss, emotional fulfillment, landed property, peaceful heart",
                "strength": "Very Strong",
                "life_areas": ["Property", "Mother", "Education", "Happiness"]
            },
            5: {
                "name": "Putra Sukha Yoga",
                "description": "4th lord in 5th house - Educational intelligence",
                "effects": "Excellent education, intelligent children, creative home, mother is wise, property for children, speculation in real estate, comfortable romance, teaching from home",
                "strength": "Very Strong",
                "life_areas": ["Education", "Intelligence", "Children", "Creativity"]
            },
            6: {
                "name": "Ripu Sukha Yoga",
                "description": "4th lord in 6th house - Property challenges",
                "effects": "Property disputes possible, mother's health issues, emotional stress, service from home, medical education, debt for property, victory through persistence, healthcare real estate",
                "strength": "Weak",
                "life_areas": ["Disputes", "Service", "Health", "Obstacles"]
            },
            7: {
                "name": "Kalatra Sukha Yoga",
                "description": "4th lord in 7th house - Partnership property",
                "effects": "Property through spouse, comfortable marriage, business from home, relocation after marriage, spouse is educated, partnership in real estate, vehicles through marriage",
                "strength": "Strong",
                "life_areas": ["Marriage", "Property", "Partnership", "Relocation"]
            },
            8: {
                "name": "Randhra Sukha Yoga",
                "description": "4th lord in 8th house - Inheritance property",
                "effects": "Inherited property, mother's longevity concerns, sudden property gains/losses, hidden assets, research education, transformation through family, occult real estate",
                "strength": "Weak",
                "life_areas": ["Inheritance", "Uncertainty", "Mother", "Transformation"]
            },
            9: {
                "name": "Dharma Sukha Yoga (Raj Yoga)",
                "description": "4th lord in 9th house - Fortunate property",
                "effects": "Excellent Raj Yoga - religious property, fortunate mother, higher education abroad, dharmic comfort, father and mother harmonious, pilgrimage properties, ashram/temple land",
                "strength": "Very Strong",
                "life_areas": ["Fortune", "Education", "Religion", "Mother"]
            },
            10: {
                "name": "Karma Sukha Yoga (Raj Yoga)",
                "description": "4th lord in 10th house - Career property",
                "effects": "Excellent Raj Yoga - property through career, professional education, office/workplace ownership, mother supports career, government property, fame brings comfort, authority",
                "strength": "Very Strong",
                "life_areas": ["Career", "Property", "Fame", "Authority"]
            },
            11: {
                "name": "Labha Sukha Yoga",
                "description": "4th lord in 11th house - Property gains",
                "effects": "Multiple properties, elder siblings share property, desires for comfort fulfilled, income from real estate, vehicles as gains, networking brings property, wishes achieved",
                "strength": "Strong",
                "life_areas": ["Gains", "Property", "Income", "Desires"]
            },
            12: {
                "name": "Vyaya Sukha Yoga",
                "description": "4th lord in 12th house - Foreign property",
                "effects": "Property abroad, mother may live far, expenses on property/vehicles, foreign education, isolated property, spiritual home, meditation room, ashram residence",
                "strength": "Medium",
                "life_areas": ["Foreign", "Spirituality", "Isolation", "Expenses"]
            }
        }

        # ====================================================================
        # 6TH LORD (RIPU/SHATRU KARAKA) PLACEMENTS - Enemies, Service, Health
        # ====================================================================
        bhava_effects[6] = {
            1: {
                "name": "Ripu Lagna Yoga",
                "description": "6th lord in 1st house - Competitive personality",
                "effects": "Competitive nature, health needs attention, service-oriented, ability to fight obstacles, enemies openly visible, medical profession possible, athletic build",
                "strength": "Weak",
                "life_areas": ["Competition", "Health", "Service", "Enemies"]
            },
            2: {
                "name": "Dhana Ripu Yoga",
                "description": "6th lord in 2nd house - Wealth through service",
                "effects": "Earnings through service/medicine, family disputes over money, debts affect wealth, speech creates enemies, hard work for savings, overcoming financial obstacles",
                "strength": "Weak",
                "life_areas": ["Service", "Debts", "Family", "Obstacles"]
            },
            3: {
                "name": "Sahaja Ripu Yoga",
                "description": "6th lord in 3rd house - Victory through courage",
                "effects": "Victory over enemies through courage, siblings may face health issues, competitive skills, service communication, effort overcomes obstacles, brave in competition",
                "strength": "Medium",
                "life_areas": ["Victory", "Courage", "Competition", "Siblings"]
            },
            4: {
                "name": "Sukha Ripu Yoga",
                "description": "6th lord in 4th house - Property disputes",
                "effects": "Property disputes possible, mother's health concerns, stress at home, service from property, medical education, debt for vehicles, emotional challenges",
                "strength": "Weak",
                "life_areas": ["Disputes", "Property", "Mother", "Stress"]
            },
            5: {
                "name": "Putra Ripu Yoga",
                "description": "6th lord in 5th house - Children health issues",
                "effects": "Children's health needs care, delayed progeny, speculation causes debts, creative service, competitive intelligence, educational obstacles, victory through intellect",
                "strength": "Weak",
                "life_areas": ["Children", "Health", "Obstacles", "Speculation"]
            },
            6: {
                "name": "Ripu Adhi Yoga",
                "description": "6th lord in 6th house - Victory over enemies",
                "effects": "Excellent for victory - defeats all enemies, strong health recovery, success in service/legal fields, overcomes debts, litigation expertise, medical profession success",
                "strength": "Strong",
                "life_areas": ["Victory", "Service", "Health", "Competition"]
            },
            7: {
                "name": "Kalatra Ripu Yoga",
                "description": "6th lord in 7th house - Partnership conflicts",
                "effects": "Conflicts in marriage/partnerships, spouse may have health issues, business disputes, marriage after obstacles, partner in service field, legal partnerships",
                "strength": "Weak",
                "life_areas": ["Marriage", "Conflicts", "Partnership", "Legal"]
            },
            8: {
                "name": "Randhra Ripu Yoga (Viparita Raj Yoga)",
                "description": "6th lord in 8th house - Transformation through obstacles",
                "effects": "Viparita Raj Yoga - enemies destroy themselves, chronic health but long life, sudden victory over obstacles, inheritance through service, occult healing, research medicine",
                "strength": "Medium",
                "life_areas": ["Longevity", "Victory", "Occult", "Healing"]
            },
            9: {
                "name": "Dharma Ripu Yoga",
                "description": "6th lord in 9th house - Obstacles to fortune",
                "effects": "Conflicts with father/gurus, dharma through service, health issues during travel, legal battles over beliefs, competitive higher education, service abroad",
                "strength": "Weak",
                "life_areas": ["Conflicts", "Father", "Travel", "Beliefs"]
            },
            10: {
                "name": "Karma Ripu Yoga",
                "description": "6th lord in 10th house - Service career",
                "effects": "Career in service/medicine/legal fields, workplace competition, success through hard work, enemies in profession, health stress from career, government service",
                "strength": "Medium",
                "life_areas": ["Career", "Service", "Competition", "Work"]
            },
            11: {
                "name": "Labha Ripu Yoga",
                "description": "6th lord in 11th house - Gains through service",
                "effects": "Income through service, victory brings gains, debts eventually paid, elder siblings face obstacles, desires fulfilled after struggle, competitive income",
                "strength": "Medium",
                "life_areas": ["Gains", "Service", "Victory", "Income"]
            },
            12: {
                "name": "Vyaya Ripu Yoga (Viparita Raj Yoga)",
                "description": "6th lord in 12th house - Hidden victory",
                "effects": "Viparita Raj Yoga - enemies defeated secretly, expenses destroy debts, service abroad, health expenses but healing, hospitalization for recovery, foreign medical work",
                "strength": "Medium",
                "life_areas": ["Foreign", "Victory", "Healing", "Expenses"]
            }
        }

        # ====================================================================
        # 7TH LORD (KALATRA KARAKA) PLACEMENTS - Spouse, Partnerships, Business
        # ====================================================================
        bhava_effects[7] = {
            1: {
                "name": "Kalatra Lagna Yoga",
                "description": "7th lord in 1st house - Partnership focused",
                "effects": "Spouse plays major role in life, attractive personality, focus on relationships, partner-oriented, business success, public relations skills, early marriage possible",
                "strength": "Strong",
                "life_areas": ["Marriage", "Partnership", "Personality", "Relationships"]
            },
            2: {
                "name": "Dhana Kalatra Yoga",
                "description": "7th lord in 2nd house - Wealth through spouse",
                "effects": "Wealth through marriage/partnerships, spouse brings prosperity, family business partnerships, eloquent partner, in-laws support finances, joint assets grow",
                "strength": "Strong",
                "life_areas": ["Wealth", "Marriage", "Partnership", "Family"]
            },
            3: {
                "name": "Sahaja Kalatra Yoga",
                "description": "7th lord in 3rd house - Active partnerships",
                "effects": "Spouse is courageous/communicative, business partnerships in media/arts, siblings introduce spouse, marriage through effort, partner travels, creative business",
                "strength": "Medium",
                "life_areas": ["Partnership", "Communication", "Courage", "Travel"]
            },
            4: {
                "name": "Sukha Kalatra Yoga",
                "description": "7th lord in 4th house - Comfortable marriage",
                "effects": "Domestic happiness through spouse, property after marriage, spouse like mother figure, partner is educated, comfortable partnership, relocation for marriage, vehicles together",
                "strength": "Strong",
                "life_areas": ["Marriage", "Comfort", "Property", "Happiness"]
            },
            5: {
                "name": "Putra Kalatra Yoga",
                "description": "7th lord in 5th house - Romantic marriage",
                "effects": "Love marriage, spouse is intelligent/creative, children from good marriage, speculation with partner, romantic relationship, creative business, joyful partnership",
                "strength": "Very Strong",
                "life_areas": ["Romance", "Love", "Children", "Creativity"]
            },
            6: {
                "name": "Ripu Kalatra Yoga",
                "description": "7th lord in 6th house - Partnership challenges",
                "effects": "Marital disputes possible, spouse in service/health field, delayed marriage, obstacles in partnerships, partner overcomes enemies, business competition, health issues to spouse",
                "strength": "Weak",
                "life_areas": ["Conflicts", "Delays", "Service", "Obstacles"]
            },
            7: {
                "name": "Kalatra Adhi Yoga",
                "description": "7th lord in 7th house - Perfect partnership",
                "effects": "Excellent marriage, strong spouse, successful partnerships, long-lasting relationships, business prosperity, public recognition, balanced relationships, partner is ideal match",
                "strength": "Very Strong",
                "life_areas": ["Marriage", "Partnership", "Business", "Public"]
            },
            8: {
                "name": "Randhra Kalatra Yoga",
                "description": "7th lord in 8th house - Transformative marriage",
                "effects": "Spouse brings transformation, inheritance through marriage, partner interested in occult, sudden changes in relationship, research partnerships, longevity concerns, deep intimacy",
                "strength": "Weak",
                "life_areas": ["Transformation", "Inheritance", "Intimacy", "Occult"]
            },
            9: {
                "name": "Dharma Kalatra Yoga (Raj Yoga)",
                "description": "7th lord in 9th house - Fortunate marriage",
                "effects": "Excellent Raj Yoga - spouse is fortunate/spiritual, marriage brings dharma, partner from good family, long distance marriage, religious partnership, foreign spouse possible, blessed union",
                "strength": "Very Strong",
                "life_areas": ["Fortune", "Marriage", "Dharma", "Travel"]
            },
            10: {
                "name": "Karma Kalatra Yoga (Raj Yoga)",
                "description": "7th lord in 10th house - Career partnership",
                "effects": "Excellent Raj Yoga - spouse helps career, business partnerships excel, fame through marriage, professional partner, public recognition together, authority in partnerships",
                "strength": "Very Strong",
                "life_areas": ["Career", "Fame", "Partnership", "Authority"]
            },
            11: {
                "name": "Labha Kalatra Yoga",
                "description": "7th lord in 11th house - Profitable partnerships",
                "effects": "Gains through spouse/partnerships, desires fulfilled in marriage, business brings income, profitable collaborations, network through spouse, wishes achieved together",
                "strength": "Strong",
                "life_areas": ["Gains", "Income", "Desires", "Network"]
            },
            12: {
                "name": "Vyaya Kalatra Yoga",
                "description": "7th lord in 12th house - Foreign partnerships",
                "effects": "Spouse from foreign land, marriage causes relocation, expenses on partnerships, spiritual union, isolated together, bed pleasures good, foreign business, partner abroad",
                "strength": "Medium",
                "life_areas": ["Foreign", "Spirituality", "Expenses", "Isolation"]
            }
        }

        # ====================================================================
        # 8TH LORD (RANDHRA KARAKA) PLACEMENTS - Longevity, Transformation, Occult
        # ====================================================================
        bhava_effects[8] = {
            1: {
                "name": "Randhra Lagna Yoga",
                "description": "8th lord in 1st house - Mysterious personality",
                "effects": "Mysterious aura, interest in occult, transformative life experiences, health fluctuations, research-oriented mind, sudden changes, long life if well-placed, secretive nature",
                "strength": "Weak",
                "life_areas": ["Occult", "Transformation", "Health", "Mystery"]
            },
            2: {
                "name": "Dhana Randhra Yoga",
                "description": "8th lord in 2nd house - Uncertain wealth",
                "effects": "Sudden financial ups/downs, inheritance possible, family secrets, wealth through research/occult, speech about mysteries, savings fluctuate, hidden family wealth",
                "strength": "Weak",
                "life_areas": ["Inheritance", "Fluctuation", "Secrets", "Wealth"]
            },
            3: {
                "name": "Sahaja Randhra Yoga",
                "description": "8th lord in 3rd house - Courageous transformation",
                "effects": "Siblings face transformations, courage in crisis, occult communication, research skills, sudden short journeys, transformation through effort, investigative abilities",
                "strength": "Medium",
                "life_areas": ["Courage", "Research", "Siblings", "Crisis"]
            },
            4: {
                "name": "Sukha Randhra Yoga",
                "description": "8th lord in 4th house - Property inheritance",
                "effects": "Inherited property, mother's longevity concerns, sudden property changes, emotional transformations, education in research, hidden real estate, occult from home",
                "strength": "Weak",
                "life_areas": ["Inheritance", "Property", "Mother", "Emotions"]
            },
            5: {
                "name": "Putra Randhra Yoga",
                "description": "5th lord in 8th house - Transformative creativity",
                "effects": "Children face transformations, delayed progeny, occult intelligence, research education, sudden speculative gains/losses, past life karma affects children, mystical insights",
                "strength": "Weak",
                "life_areas": ["Children", "Occult", "Research", "Transformation"]
            },
            6: {
                "name": "Ripu Randhra Yoga (Viparita Raj Yoga)",
                "description": "8th lord in 6th house - Longevity through obstacles",
                "effects": "Viparita Raj Yoga - long life despite health challenges, victory over chronic enemies, transformation destroys obstacles, occult healing powers, service in research/medicine",
                "strength": "Medium",
                "life_areas": ["Longevity", "Victory", "Healing", "Service"]
            },
            7: {
                "name": "Kalatra Randhra Yoga",
                "description": "8th lord in 7th house - Transformative partnerships",
                "effects": "Spouse brings transformation, inheritance through marriage, partner interested in occult, sudden partnership changes, deep intimacy, research partnerships, longevity concerns",
                "strength": "Weak",
                "life_areas": ["Marriage", "Transformation", "Inheritance", "Intimacy"]
            },
            8: {
                "name": "Randhra Adhi Yoga",
                "description": "8th lord in 8th house - Occult mastery",
                "effects": "Long life, occult/mysticism mastery, inheritance likely, research excellence, transformation ability, sudden gains, hidden wealth, regeneration power, tantric knowledge",
                "strength": "Strong",
                "life_areas": ["Longevity", "Occult", "Inheritance", "Transformation"]
            },
            9: {
                "name": "Dharma Randhra Yoga",
                "description": "8th lord in 9th house - Mystical wisdom",
                "effects": "Mystical spirituality, transformation through dharma, research in philosophy, sudden foreign journeys, occult teachings, father's longevity concerns, hidden religious knowledge",
                "strength": "Medium",
                "life_areas": ["Mysticism", "Philosophy", "Transformation", "Father"]
            },
            10: {
                "name": "Karma Randhra Yoga",
                "description": "8th lord in 10th house - Research career",
                "effects": "Career in research/occult/investigation, sudden career changes, inheritance affects profession, transformation through work, detective/psychology/mining career, authority fluctuates",
                "strength": "Medium",
                "life_areas": ["Career", "Research", "Investigation", "Change"]
            },
            11: {
                "name": "Labha Randhra Yoga",
                "description": "8th lord in 11th house - Sudden gains",
                "effects": "Sudden unexpected gains, inheritance from elder siblings, occult income, transformation brings profits, research network, desires fulfilled mysteriously, lottery wins possible",
                "strength": "Medium",
                "life_areas": ["Gains", "Inheritance", "Sudden", "Income"]
            },
            12: {
                "name": "Vyaya Randhra Yoga (Viparita Raj Yoga)",
                "description": "8th lord in 12th house - Spiritual transformation",
                "effects": "Viparita Raj Yoga - spiritual transformation, expenses on research, foreign occult studies, liberation through transformation, moksha yoga, meditation brings insights, hidden powers",
                "strength": "Medium",
                "life_areas": ["Spirituality", "Moksha", "Occult", "Liberation"]
            }
        }

        # ====================================================================
        # 11TH LORD (LABHA KARAKA) PLACEMENTS - Gains, Income, Friends
        # ====================================================================
        bhava_effects[11] = {
            1: {
                "name": "Labha Lagna Yoga",
                "description": "11th lord in 1st house - Gains through self",
                "effects": "Self-made income, desires fulfilled through personality, elder siblings helpful, optimistic nature, gains through appearance, networking abilities, ambitious personality",
                "strength": "Strong",
                "life_areas": ["Gains", "Personality", "Desires", "Self-effort"]
            },
            2: {
                "name": "Dhana Labha Yoga",
                "description": "11th lord in 2nd house - Wealth multiplication",
                "effects": "Excellent wealth yoga - multiple income sources, family brings gains, savings accumulate, desires for wealth fulfilled, elder siblings support finances, continuous prosperity",
                "strength": "Very Strong",
                "life_areas": ["Wealth", "Income", "Savings", "Prosperity"]
            },
            3: {
                "name": "Sahaja Labha Yoga",
                "description": "11th lord in 3rd house - Gains through skills",
                "effects": "Income through skills/communication, siblings bring profits, creative income, networking brings success, short journeys profitable, artistic gains, courageous for desires",
                "strength": "Strong",
                "life_areas": ["Skills", "Communication", "Gains", "Network"]
            },
            4: {
                "name": "Sukha Labha Yoga",
                "description": "11th lord in 4th house - Property gains",
                "effects": "Gains from real estate, mother brings prosperity, comfortable income, multiple properties, vehicles as gains, educational income, networking from home, desires for comfort fulfilled",
                "strength": "Strong",
                "life_areas": ["Property", "Gains", "Comfort", "Mother"]
            },
            5: {
                "name": "Putra Labha Yoga (Raj Yoga)",
                "description": "11th lord in 5th house - Speculative gains",
                "effects": "Excellent Raj Yoga - gains through speculation/investments, children bring prosperity, creative income, past merit brings gains, lottery/shares favorable, desires fulfilled through intelligence",
                "strength": "Very Strong",
                "life_areas": ["Speculation", "Children", "Creativity", "Gains"]
            },
            6: {
                "name": "Ripu Labha Yoga",
                "description": "11th lord in 6th house - Gains through service",
                "effects": "Income through service, victory over financial obstacles, desires after struggle, competitive income, debt eventually repaid, healing professions bring gains, hard work pays",
                "strength": "Medium",
                "life_areas": ["Service", "Competition", "Victory", "Income"]
            },
            7: {
                "name": "Kalatra Labha Yoga",
                "description": "11th lord in 7th house - Partnership gains",
                "effects": "Gains through spouse/partnerships, business brings profits, desires fulfilled through marriage, partner is prosperous, networking through spouse, profitable collaborations",
                "strength": "Strong",
                "life_areas": ["Partnership", "Business", "Marriage", "Gains"]
            },
            8: {
                "name": "Randhra Labha Yoga",
                "description": "11th lord in 8th house - Sudden gains",
                "effects": "Sudden unexpected income, inheritance brings gains, occult/research income, desires fulfilled mysteriously, lottery possible, transformation brings profits, hidden income sources",
                "strength": "Medium",
                "life_areas": ["Sudden", "Inheritance", "Occult", "Gains"]
            },
            9: {
                "name": "Dharma Labha Yoga (Raj Yoga)",
                "description": "11th lord in 9th house - Fortunate gains",
                "effects": "Excellent Raj Yoga - fortune brings gains, dharmic income, father's network helpful, higher education brings income, desires fulfilled through luck, religious gains, blessed prosperity",
                "strength": "Very Strong",
                "life_areas": ["Fortune", "Dharma", "Gains", "Prosperity"]
            },
            10: {
                "name": "Karma Labha Yoga",
                "description": "11th lord in 10th house - Career gains",
                "effects": "Career brings excellent income, professional network strong, desires fulfilled through work, authority increases earnings, reputation brings gains, government favor possible",
                "strength": "Strong",
                "life_areas": ["Career", "Income", "Authority", "Fame"]
            },
            11: {
                "name": "Labha Adhi Yoga",
                "description": "11th lord in 11th house - Maximum gains",
                "effects": "Excellent gains yoga - all desires fulfilled, multiple income streams, elder siblings very helpful, networking brings wealth, wishes achieved easily, continuous prosperity throughout life",
                "strength": "Very Strong",
                "life_areas": ["Gains", "Desires", "Income", "Wishes"]
            },
            12: {
                "name": "Vyaya Labha Yoga",
                "description": "11th lord in 12th house - Foreign gains",
                "effects": "Income from abroad, expenses equal income, desires for spirituality, foreign network, charitable giving, gains through isolation, spiritual desires fulfilled, hidden income",
                "strength": "Medium",
                "life_areas": ["Foreign", "Expenses", "Spirituality", "Charity"]
            }
        }

        # ====================================================================
        # 12TH LORD (VYAYA KARAKA) PLACEMENTS - Expenses, Losses, Foreign, Moksha
        # ====================================================================
        bhava_effects[12] = {
            1: {
                "name": "Vyaya Lagna Yoga",
                "description": "12th lord in 1st house - Spiritual personality",
                "effects": "Spiritual inclinations, expenses on self/health, foreign residence possible, isolated personality, meditation-oriented, charitable nature, moksha desires, pilgrimage interests",
                "strength": "Medium",
                "life_areas": ["Spirituality", "Foreign", "Expenses", "Isolation"]
            },
            2: {
                "name": "Dhana Vyaya Yoga",
                "description": "12th lord in 2nd house - Wealth expenses",
                "effects": "High family expenses, wealth goes to charity, foreign investments, speech about spirituality, savings for foreign travel, generous donations, hidden wealth abroad",
                "strength": "Weak",
                "life_areas": ["Expenses", "Charity", "Foreign", "Wealth"]
            },
            3: {
                "name": "Sahaja Vyaya Yoga",
                "description": "12th lord in 3rd house - Foreign skills",
                "effects": "Skills used abroad, siblings may live far, expenses on hobbies/arts, courage for spirituality, isolation develops talents, communication about meditation, journeys abroad",
                "strength": "Medium",
                "life_areas": ["Foreign", "Skills", "Isolation", "Spirituality"]
            },
            4: {
                "name": "Sukha Vyaya Yoga",
                "description": "12th lord in 4th house - Foreign property",
                "effects": "Property abroad, mother lives far or spiritual, expenses on vehicles/property, foreign education, isolated residence, meditation room important, ashram property, emotional detachment",
                "strength": "Medium",
                "life_areas": ["Foreign", "Property", "Spirituality", "Mother"]
            },
            5: {
                "name": "Putra Vyaya Yoga",
                "description": "12th lord in 5th house - Foreign children",
                "effects": "Children abroad or spiritual, expenses on children's education, creativity in isolation, speculation causes losses, meditation brings insights, spiritual intelligence, foreign study",
                "strength": "Medium",
                "life_areas": ["Children", "Foreign", "Spirituality", "Expenses"]
            },
            6: {
                "name": "Ripu Vyaya Yoga (Viparita Raj Yoga)",
                "description": "12th lord in 6th house - Victory through expenses",
                "effects": "Viparita Raj Yoga - expenses destroy enemies, debts lead to liberation, service abroad, healing expenses beneficial, foreign medical work, obstacles lead to moksha, hospitalization heals",
                "strength": "Medium",
                "life_areas": ["Victory", "Foreign", "Healing", "Liberation"]
            },
            7: {
                "name": "Kalatra Vyaya Yoga",
                "description": "12th lord in 7th house - Foreign spouse",
                "effects": "Spouse from foreign land, marriage abroad, partnership expenses, relocation after marriage, spiritual partnership, bed pleasures good, business abroad, isolated with partner",
                "strength": "Medium",
                "life_areas": ["Foreign", "Marriage", "Relocation", "Expenses"]
            },
            8: {
                "name": "Randhra Vyaya Yoga (Viparita Raj Yoga)",
                "description": "12th lord in 8th house - Spiritual transformation",
                "effects": "Viparita Raj Yoga - moksha yoga, spiritual transformation deep, expenses on occult/research, foreign inheritance, isolation brings insights, meditation on death, liberation focus, tantric practices",
                "strength": "Medium",
                "life_areas": ["Moksha", "Transformation", "Spirituality", "Occult"]
            },
            9: {
                "name": "Dharma Vyaya Yoga",
                "description": "12th lord in 9th house - Foreign dharma",
                "effects": "Spiritual journeys abroad, father lives far, expenses on pilgrimage, foreign gurus, higher education abroad, charitable dharma, ashram life, renunciation tendencies, monastery attraction",
                "strength": "Medium",
                "life_areas": ["Pilgrimage", "Foreign", "Dharma", "Renunciation"]
            },
            10: {
                "name": "Karma Vyaya Yoga",
                "description": "12th lord in 10th house - Foreign career",
                "effects": "Career abroad, expenses on profession, work in isolation/hospitals/ashrams, foreign business, spiritual career, losses through authority, MNC work, export-import, international profession",
                "strength": "Medium",
                "life_areas": ["Foreign", "Career", "Isolation", "Spirituality"]
            },
            11: {
                "name": "Labha Vyaya Yoga",
                "description": "12th lord in 11th house - Foreign gains",
                "effects": "Income from abroad, expenses equal gains, desires for spirituality fulfilled, foreign network, charitable income, gains through isolation, spiritual wishes achieved, hidden profits",
                "strength": "Medium",
                "life_areas": ["Foreign", "Gains", "Spirituality", "Network"]
            },
            12: {
                "name": "Vyaya Adhi Yoga",
                "description": "12th lord in 12th house - Complete moksha",
                "effects": "Strong moksha yoga - complete spiritual liberation, life abroad, isolated residence, meditation mastery, ashram/monastery life, detachment from material, enlightenment focus, final liberation",
                "strength": "Strong",
                "life_areas": ["Moksha", "Liberation", "Spirituality", "Foreign"]
            }
        }

        # Return the specific effect if available
        if lord_house in bhava_effects and placement in bhava_effects[lord_house]:
            return bhava_effects[lord_house][placement]

        return None

    def _classify_yoga_impact(self, name: str, category: str) -> str:
        """Classify yoga impact: positive, negative, mixed, neutral"""
        name_lower = name.lower()
        category_lower = category.lower()

        # Mixed indicators (both challenges and opportunities)
        mixed_keywords = ["kala sarpa", "viparita", "sanyas", "randhra"]
        for keyword in mixed_keywords:
            if keyword in name_lower or keyword in category_lower:
                return "mixed"

        # Negative indicators
        negative_keywords = ["dosha", "kemadruma", "daridra", "shakata", "balarishta", "grahan", "pitra", "manglik", "kroora"]
        for keyword in negative_keywords:
            if keyword in name_lower or keyword in category_lower:
                return "negative"

        # Positive indicators
        positive_keywords = ["raj yoga", "dhana", "mahapurusha", "adhi yoga", "labha", "putra", "gajakesari", "kubera", "lakshmi", "sukha"]
        for keyword in positive_keywords:
            if keyword in name_lower or keyword in category_lower:
                return "positive"

        # Category-based
        if any(c in category_lower for c in ["challenge", "obstacle"]):
            return "negative"
        if any(c in category_lower for c in ["wealth", "power", "fame", "learning"]):
            return "positive"

        return "positive"  # Default

    def _classify_yoga_importance(self, name: str, strength: str, category: str) -> str:
        """Classify yoga importance: major, moderate, minor"""
        name_lower = name.lower()
        category_lower = category.lower()

        # House lord placement yogas (Bhava Yogas) are NOT major by default
        # They should be classified by their strength, not by name keywords
        if "bhava yoga" in category_lower or "house lord placement" in category_lower:
            # House lord yogas: classify by strength only
            if strength == "Very Strong":
                return "moderate"
            elif strength == "Strong":
                return "moderate"
            else:  # Medium or Weak
                return "minor"

        # Major yogas - life-changing combinations
        major_keywords = [
            # Pancha Mahapurusha Yogas (5 great person yogas)
            "hamsa", "malavya", "sasa", "ruchaka", "bhadra",
            # Sun-Based Yogas (BPHS Tier 1)
            "vesi", "vosi", "ubhayachari",
            # Moon-Based Yogas (BPHS Tier 1)
            "sunapha", "anapha", "durudhura",
            # Learning & Wisdom Yogas (BPHS Tier 1)
            "saraswati",
            # Major Raj Yogas
            "raj yoga", "neecha bhanga",
            # Major Dhana Yogas (classical wealth yogas)
            # Note: "dhana yoga" is safe here because house lord yogas are filtered out
            # by the category check above (lines 3906-3913) before reaching this point
            "kubera", "lakshmi", "maha dhana", "dhana yoga",
            # Major benefic yogas
            "gajakesari", "gaja kesari", "adhi yoga", "vasumathi",
            # Major challenging yogas
            "kala sarpa", "kemadruma", "daridra", "shakata",
            # Doshas (major afflictions)
            "manglik", "grahan", "pitra", "kaal sarp"
        ]

        for keyword in major_keywords:
            if keyword in name_lower:
                return "major"

        # Category-based major classification
        if "mahapurusha" in category_lower:
            return "major"

        if "pancha mahapurusha" in category_lower:
            return "major"

        # Raj Yoga category is always major
        if "raj yoga" in category_lower or "raja yoga" in category_lower:
            return "major"

        # Major Dhana Yogas
        if "dhana yoga" in category_lower and strength in ["Very Strong", "Strong"]:
            return "major"

        # Very strong yogas in important categories are major
        if strength == "Very Strong" and any(c in category_lower for c in ["wealth", "power", "fame", "learning", "challenge"]):
            return "major"

        # Moderate yogas - significant but not life-defining
        moderate_keywords = [
            "nabhasa", "sanyas", "yoga", "bhanga", "nitya",
            "budhaditya", "chandra mangal", "guru mangal", "parivartana", "viparita"
        ]

        # Nabhasa yogas are moderate
        if "nabhasa" in category_lower:
            return "moderate"

        # Sanyas yogas are moderate
        if "sanyas" in category_lower or "sanyasa" in category_lower:
            return "moderate"

        # Strong yogas not already classified as major
        if strength in ["Very Strong", "Strong"]:
            return "moderate"

        # Check if any moderate keyword is present
        for keyword in moderate_keywords:
            if keyword in name_lower and strength in ["Strong", "Medium"]:
                return "moderate"

        # Default to minor
        return "minor"

    def _categorize_life_area(self, category: str, name: str = "") -> str:
        """Categorize yoga by primary life area"""
        combined = f"{category.lower()} {name.lower() if name else ''}"

        if any(k in combined for k in ["wealth", "dhana", "kubera", "lakshmi", "labha"]):
            return "Wealth"
        if any(k in combined for k in ["power", "status", "fame", "authority", "karma"]):
            return "Career & Status"
        if any(k in combined for k in ["kalatra", "marriage", "partnership"]):
            return "Relationships"
        if any(k in combined for k in ["learning", "wisdom", "intelligence", "spirituality", "sanyas", "moksha", "dharma"]):
            return "Spirituality & Wisdom"
        if any(k in combined for k in ["putra", "children"]):
            return "Children & Family"
        if any(k in combined for k in ["challenge", "obstacle", "dosha", "ripu"]):
            return "Challenges"
        if any(k in combined for k in ["health", "longevity"]):
            return "Health"

        return "General"

    def _enrich_yoga_with_metadata(self, yoga: Dict) -> Dict:
        """Enrich a yoga with classification metadata"""
        enriched = yoga.copy()
        enriched["impact"] = self._classify_yoga_impact(yoga["name"], yoga["category"])
        enriched["importance"] = self._classify_yoga_importance(yoga["name"], yoga.get("strength", "Medium"), yoga["category"])
        enriched["life_area"] = self._categorize_life_area(yoga["category"], yoga["name"])
        return enriched

    def _deduplicate_yogas(self, yogas: List[Dict]) -> List[Dict]:
        """
        Deduplicate yogas that have the same name (with spelling variations).

        For example, "Gaja Kesari Yoga" and "Gajakesari Yoga" are the same yoga.
        When duplicates are found, keep the one with more detailed information.
        """
        from collections import defaultdict

        def normalize_name(name: str) -> str:
            """Normalize yoga name for comparison (remove spaces, lowercase)"""
            return name.lower().replace(" ", "").replace("-", "")

        # Group yogas by normalized name
        grouped = defaultdict(list)
        for yoga in yogas:
            norm_name = normalize_name(yoga.get("name", ""))
            grouped[norm_name].append(yoga)

        deduplicated = []
        for norm_name, yoga_list in grouped.items():
            if len(yoga_list) == 1:
                # No duplicates, add as is
                deduplicated.append(yoga_list[0])
            else:
                # Multiple yogas with same normalized name - merge them
                # Prefer the one with more details, cancellation notes, or higher strength

                # Sort by priority:
                # 1. Has cancellation/weakening notes (more detailed)
                # 2. Longer description
                # 3. Strength order: Very Strong > Strong > Medium > Weak

                strength_order = {"Very Strong": 4, "Strong": 3, "Medium": 2, "Weak": 1}

                def yoga_priority(y):
                    desc = y.get("description", "")
                    has_notes = "[CANCELLED" in desc or "[WEAKENED" in desc
                    strength_val = strength_order.get(y.get("strength", "Medium"), 2)
                    desc_len = len(desc)
                    return (has_notes, strength_val, desc_len)

                # Sort and take the best one
                yoga_list.sort(key=yoga_priority, reverse=True)
                best_yoga = yoga_list[0]

                # Optionally merge formation details from other versions
                # (if they provide additional info)
                formations = []
                for yoga in yoga_list:
                    formation = yoga.get("formation", "")
                    if formation and formation not in formations:
                        formations.append(formation)

                if len(formations) > 1:
                    best_yoga["formation"] = "; ".join(formations)

                deduplicated.append(best_yoga)

        return deduplicated

    def enrich_yogas(self, yogas: List[Dict]) -> List[Dict]:
        """Deduplicate and enrich all yogas with classification metadata"""
        # NEW: Use comprehensive normalization system for proper deduplication and categorization
        from app.services.yoga_normalization import deduplicate_yogas

        # First deduplicate using comprehensive normalization (handles spelling variations)
        deduplicated = deduplicate_yogas(yogas)

        # Then enrich with metadata
        return [self._enrich_yoga_with_metadata(yoga) for yoga in deduplicated]


# Global instance
extended_yoga_service = ExtendedYogaService()
