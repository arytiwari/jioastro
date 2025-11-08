"""
Extended Yoga Detection Service
Detects 25+ classical Vedic yogas beyond the basic set
"""

from typing import Dict, List, Any, Optional


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

    def _calculate_planet_dignity(self, planet_name: str, planets: Dict) -> int:
        """
        Calculate planet dignity score (0-100)
        - Exalted: 100
        - Own sign: 80
        - Friend's sign: 60
        - Neutral sign: 40
        - Enemy's sign: 20
        - Debilitated: 0
        """
        planet_data = planets.get(planet_name, {})
        sign_num = planet_data.get("sign_num", 0)

        if not sign_num:
            return 40  # Default neutral

        # Check exaltation
        if self.EXALTATION_SIGNS.get(planet_name) == sign_num:
            return 100

        # Check debilitation
        if self.DEBILITATION_SIGNS.get(planet_name) == sign_num:
            return 0

        # Check own sign
        if sign_num in self.OWN_SIGNS.get(planet_name, []):
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
        """Check if planet is combusted (too close to Sun)"""
        if planet_name in ["Sun", "Rahu", "Ketu"]:
            return False

        planet_house = planets.get(planet_name, {}).get("house", 0)
        sun_house = planets.get("Sun", {}).get("house", 0)

        # Simple combustion check: same house as Sun
        # (More accurate would use degrees)
        return planet_house == sun_house and planet_house != 0

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

            # Check debilitation
            if self.DEBILITATION_SIGNS.get(planet_name) == sign_num:
                is_cancelled = True
                reasons.append(f"{planet_name} is debilitated in {self.SIGNS[sign_num-1]}")

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
        Detect 40+ extended Vedic yogas including:
        - Pancha Mahapurusha (5), Adhi, Chamara, Lakshmi, Saraswati, Amala, Parvata, Kahala
        - Chandra-Mangala, Guru-Mangala, Viparita Raj (3), Neecha Bhanga
        - Vesi, Vosi, Ubhayachari, Sunapha, Anapha, Durudhura, Kemadruma
        - Budhaditya, Nipuna
        - Kala Sarpa (12 types)
        - Nabhasa Ashraya (4), Dala (2), Akriti (4)
        - Rare yogas (5): Shakata, Shrinatha, Kusuma, Matsya, Kurma

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

        # 33-36: Nabhasa Akriti Yogas (select patterns)
        yogas.extend(self._detect_nabhasa_akriti_yogas(planets))

        # 37-41: Rare Yogas (Shakata, Shrinatha, Kusuma, Matsya, Kurma)
        yogas.extend(self._detect_rare_yogas(planets))

        # NEW YOGAS - Phase 1: Critical
        # 42: Gajakesari Yoga
        yogas.extend(self._detect_gajakesari_yoga(planets))

        # 43: Raj Yoga (Kendra-Trikona - simplified)
        yogas.extend(self._detect_raj_yoga_kendra_trikona(planets))

        # 44: Grahan Yoga
        yogas.extend(self._detect_grahan_yoga(planets))

        # NEW YOGAS - Phase 2: High Priority
        # 45: Dharma-Karmadhipati Yoga (simplified)
        yogas.extend(self._detect_dharma_karmadhipati_yoga(planets))

        # 46: Dhana Yoga (simplified)
        yogas.extend(self._detect_dhana_yoga(planets))

        # 47: Chandal Yoga
        yogas.extend(self._detect_chandal_yoga(planets))

        # 48: Kubera Yoga
        yogas.extend(self._detect_kubera_yoga(planets))

        # 49: Daridra Yoga
        yogas.extend(self._detect_daridra_yoga(planets))

        # NEW YOGAS - Phase 3: Medium Priority
        # 50: Balarishta Yoga
        yogas.extend(self._detect_balarishta_yoga(planets))

        # 51: Kroora Yoga
        yogas.extend(self._detect_kroora_yoga(planets))

        return yogas

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
        Saraswati Yoga: Mercury, Jupiter, Venus in Kendra/Trikona - learning and wisdom
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

        # Saraswati Yoga
        kendra_trikona = [1, 4, 5, 7, 9, 10]
        benefics_strong = []
        for planet in ["Mercury", "Jupiter", "Venus"]:
            p_data = planets.get(planet, {})
            if p_data.get("house") in kendra_trikona:
                benefics_strong.append(planet)

        if len(benefics_strong) == 3:
            yogas.append({
                "name": "Saraswati Yoga",
                "description": "All three benefics in Kendra/Trikona - exceptional learning, wisdom, eloquence",
                "strength": "Strong",
                "category": "Learning & Wisdom"
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
        Viparita Raj Yoga: Lords of 6th, 8th, 12th in mutual houses
        Simplified: Malefics (Mars, Saturn) in 6th, 8th, or 12th
        Success through overcoming adversity
        """
        yogas = []
        dusthana_houses = [6, 8, 12]

        malefics_in_dusthana = [p for p in ["Mars", "Saturn"]
                               if planets.get(p, {}).get("house") in dusthana_houses]

        if len(malefics_in_dusthana) >= 2:
            yogas.append({
                "name": "Viparita Raj Yoga",
                "description": "Malefics in dusthanas - success through overcoming adversity, turning difficulties into opportunities",
                "strength": "Medium",
                "category": "Overcoming Obstacles"
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
                    "description": f"{planet} in 2nd from Sun - wealth, good speech, balanced personality",
                    "strength": "Weak",
                    "category": "Wealth & Character"
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
                    "description": f"{planet} in 12th from Sun - technical skills, authority, independent nature",
                    "strength": "Weak",
                    "category": "Skills & Authority"
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
                "description": "Planets on both sides of Sun - wealth, fame, eloquence, balanced nature",
                "strength": "Medium",
                "category": "Fame & Wealth"
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
                    "description": f"{planet} in 2nd from Moon - wealth, fame, intelligence, self-made success",
                    "strength": "Weak",
                    "category": "Wealth & Intelligence"
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
                    "description": f"{planet} in 12th from Moon - happiness, fame, well-formed body, good health",
                    "strength": "Weak",
                    "category": "Health & Fame"
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
                "description": "Planets on both sides of Moon - wealth, vehicles, comforts, balanced mind",
                "strength": "Medium",
                "category": "Wealth & Comfort"
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
        Nabhasa Akriti Yogas - Based on planetary patterns/shapes
        Implementing select important ones
        """
        yogas = []

        main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        occupied_houses = sorted(list(set([planets.get(p, {}).get("house", 0) for p in main_planets if planets.get(p, {}).get("house", 0) > 0])))

        if len(occupied_houses) < 2:
            return yogas

        # Yuga Yoga - All planets in 1-4 houses
        if occupied_houses[-1] <= 4:
            yogas.append({
                "name": "Yuga Yoga",
                "description": "All planets in first quadrant (H1-4) - Religious, charitable, respected, ascetic tendencies",
                "strength": "Strong",
                "category": "Nabhasa - Akriti"
            })

        # Shola Yoga - All planets in 5-8 houses
        elif occupied_houses[0] >= 5 and occupied_houses[-1] <= 8:
            yogas.append({
                "name": "Shola Yoga",
                "description": "All planets in second quadrant (H5-8) - Argumentative, courageous, wealthy through effort, leadership",
                "strength": "Strong",
                "category": "Nabhasa - Akriti"
            })

        # Gola Yoga - All planets in one sign
        if len(occupied_houses) == 1:
            yogas.append({
                "name": "Gola Yoga",
                "description": "All planets in one sign - Focused personality, poor in early life, gains later, specialized skills",
                "strength": "Medium",
                "category": "Nabhasa - Akriti"
            })

        # Dama Yoga - Planets in consecutive houses
        if len(occupied_houses) >= 3:
            consecutive = all(occupied_houses[i+1] - occupied_houses[i] == 1 for i in range(len(occupied_houses)-1))
            if consecutive:
                yogas.append({
                    "name": "Dama Yoga",
                    "description": "Planets in consecutive houses - Charitable, helpful nature, gains through service, moderate wealth",
                    "strength": "Medium",
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

    def _detect_daridra_yoga(self, planets: Dict) -> List[Dict]:
        """
        Daridra Yoga (Poverty Yoga): Simplified version
        Indicators: Malefics in wealth houses (2, 5, 11) or benefics severely afflicted
        """
        yogas = []
        wealth_houses = [2, 5, 11]
        malefics = ["Mars", "Saturn", "Rahu", "Ketu"]

        malefics_in_wealth = []
        for planet in malefics:
            house = planets.get(planet, {}).get("house", 0)
            if house in wealth_houses:
                malefics_in_wealth.append((planet, house))

        # Check if benefics are debilitated
        debilitated_benefics = []
        for planet in ["Jupiter", "Venus", "Mercury"]:
            sign_num = planets.get(planet, {}).get("sign_num", 0)
            if sign_num == self.DEBILITATION_SIGNS.get(planet):
                debilitated_benefics.append(planet)

        # Daridra Yoga forms when multiple malefics in wealth houses or benefics debilitated
        if len(malefics_in_wealth) >= 2 or len(debilitated_benefics) >= 2:
            desc_parts = []

            if malefics_in_wealth:
                planet_houses = [f"{p[0]} in {p[1]}th" for p in malefics_in_wealth]
                desc_parts.append(f"Malefics in wealth houses ({', '.join(planet_houses)})")

            if debilitated_benefics:
                desc_parts.append(f"Benefics debilitated ({', '.join(debilitated_benefics)})")

            yogas.append({
                "name": "Daridra Yoga",
                "description": f"{' and '.join(desc_parts)} - financial struggles, obstacles to wealth accumulation, need for careful financial planning, wealth comes through hard work",
                "strength": "Medium",
                "category": "Challenge Yoga"
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


# Global instance
extended_yoga_service = ExtendedYogaService()
