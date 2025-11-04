"""
Extended Yoga Detection Service
Detects 25+ classical Vedic yogas beyond the basic set
"""

from typing import Dict, List, Any


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

    def detect_extended_yogas(self, planets: Dict[str, Any], houses: Any = None) -> List[Dict[str, str]]:
        """
        Detect 25+ extended Vedic yogas

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
                    strength = "Very Strong" if is_exalted else "Strong"
                    yogas.append({
                        "name": yoga_names[planet],
                        "description": f"{planet} in Kendra in {['exalted', 'own'][is_own_sign]} sign - {yoga_effects[planet]}",
                        "strength": strength,
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


# Global instance
extended_yoga_service = ExtendedYogaService()
