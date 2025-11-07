"""
Dosha Detection Service
Detects major doshas (afflictions) in Vedic astrology charts
"""

from typing import Dict, Any, List


class DoshaDetectionService:
    """Detect classical Vedic astrology doshas"""

    def detect_all_doshas(
        self,
        d1_planets: Dict[str, Any],
        d1_ascendant: Dict[str, Any],
        d9_planets: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect all major doshas in the birth chart

        Args:
            d1_planets: Planets from D1 (Rashi) chart
            d1_ascendant: Ascendant from D1 chart
            d9_planets: Planets from D9 (Navamsa) chart (optional for Manglik)

        Returns:
            List of detected doshas with details
        """
        doshas = []

        # 1. Manglik Dosha (Mars affliction)
        manglik = self.detect_manglik_dosha(d1_planets, d9_planets)
        if manglik["present"]:
            doshas.append(manglik)

        # 2. Kaal Sarpa Dosha (All planets between Rahu-Ketu axis)
        kaal_sarpa = self.detect_kaal_sarpa_dosha(d1_planets)
        if kaal_sarpa["present"]:
            doshas.append(kaal_sarpa)

        # 3. Pitra Dosha (Ancestral affliction)
        pitra = self.detect_pitra_dosha(d1_planets)
        if pitra["present"]:
            doshas.append(pitra)

        # 4. Gandanta Dosha (Junction points between signs/nakshatras)
        gandanta = self.detect_gandanta_dosha(d1_planets, d1_ascendant)
        if gandanta["present"]:
            doshas.append(gandanta)

        # 5. Grahan Dosha (Eclipse dosha - Sun/Moon with Rahu/Ketu)
        grahan = self.detect_grahan_dosha(d1_planets)
        if grahan["present"]:
            doshas.append(grahan)

        # 6. Kemdrum Dosha (Moon isolated)
        kemdrum = self.detect_kemdrum_dosha(d1_planets)
        if kemdrum["present"]:
            doshas.append(kemdrum)

        return doshas if doshas else [{
            "name": "No Major Dosha",
            "present": False,
            "severity": "none",
            "description": "No major doshas detected in the chart",
            "effects": "Chart is relatively free from major afflictions",
            "remedies": []
        }]

    def detect_manglik_dosha(
        self,
        d1_planets: Dict[str, Any],
        d9_planets: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Detect Manglik Dosha (Mars in 1st, 2nd, 4th, 7th, 8th, 12th houses)

        Classic Manglik: Mars in houses 1, 4, 7, 8, 12 from Lagna OR Moon
        High Manglik: Mars in 2nd or 8th house
        """
        mars_data = d1_planets.get("Mars", {})
        mars_house_lagna = mars_data.get("house", 0)

        # Get Moon's position to check from Moon
        moon_data = d1_planets.get("Moon", {})
        moon_house = moon_data.get("house", 0)

        # Calculate Mars house from Moon
        mars_sign = mars_data.get("sign_num", 0)
        moon_sign = moon_data.get("sign_num", 0)
        mars_house_from_moon = ((mars_sign - moon_sign) % 12) + 1

        # Manglik houses
        manglik_houses = [1, 2, 4, 7, 8, 12]
        high_intensity_houses = [2, 8]

        # Check from Lagna
        manglik_from_lagna = mars_house_lagna in manglik_houses
        high_from_lagna = mars_house_lagna in high_intensity_houses

        # Check from Moon
        manglik_from_moon = mars_house_from_moon in manglik_houses
        high_from_moon = mars_house_from_moon in high_intensity_houses

        is_manglik = manglik_from_lagna or manglik_from_moon
        is_high_manglik = high_from_lagna or high_from_moon

        # Check for cancellations
        cancellations = []

        # 1. Both partners are Manglik (mentioned in remedies)
        # 2. Mars in own sign (Aries/Scorpio) or exalted (Capricorn)
        mars_sign_name = mars_data.get("sign", "")
        if mars_sign_name in ["Aries", "Scorpio", "Capricorn"]:
            cancellations.append("Mars in own/exalted sign reduces severity")

        # 3. Person born on Tuesday
        # 4. Jupiter/Venus aspecting 7th house
        # 5. Mars in D9 (Navamsa) not afflicting 7th house
        if d9_planets:
            mars_d9 = d9_planets.get("Mars", {})
            if mars_d9.get("house") not in [1, 7, 8]:
                cancellations.append("Mars well-placed in Navamsa")

        # Determine severity
        if not is_manglik:
            severity = "none"
        elif cancellations:
            severity = "low" if len(cancellations) >= 2 else "medium"
        elif is_high_manglik:
            severity = "high"
        else:
            severity = "medium"

        return {
            "name": "Manglik Dosha",
            "present": is_manglik,
            "severity": severity,
            "details": {
                "mars_house_from_lagna": mars_house_lagna,
                "mars_house_from_moon": mars_house_from_moon,
                "manglik_from_lagna": manglik_from_lagna,
                "manglik_from_moon": manglik_from_moon,
                "high_intensity": is_high_manglik,
                "cancellations": cancellations
            },
            "description": (
                f"Mars in {mars_house_lagna}th house from Lagna "
                f"and {mars_house_from_moon}th house from Moon"
            ),
            "effects": (
                "May cause delays or challenges in marriage, conflicts with spouse, "
                "or marital disharmony" if is_manglik else "No Manglik affliction"
            ),
            "remedies": [
                "Marriage with another Manglik person",
                "Kumbh Vivah (symbolic marriage to tree/idol before actual marriage)",
                "Worship Lord Hanuman on Tuesdays",
                "Recite Hanuman Chalisa daily",
                "Donate red lentils on Tuesdays",
                "Wear red coral gemstone after consultation",
                "Fast on Tuesdays"
            ] if is_manglik else []
        }

    def detect_kaal_sarpa_dosha(self, d1_planets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect Kaal Sarpa Dosha (All planets hemmed between Rahu-Ketu axis)
        """
        rahu_data = d1_planets.get("Rahu", {})
        ketu_data = d1_planets.get("Ketu", {})

        rahu_house = rahu_data.get("house", 0)
        ketu_house = ketu_data.get("house", 0)

        # Get all planets except Rahu and Ketu
        planets_to_check = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        # Check if all planets are on one side of Rahu-Ketu axis
        planets_between_rahu_ketu = []
        planets_outside = []

        for planet in planets_to_check:
            planet_house = d1_planets.get(planet, {}).get("house", 0)

            # Check if planet is between Rahu and Ketu
            if rahu_house < ketu_house:
                # Rahu in earlier house, Ketu in later house
                if rahu_house < planet_house < ketu_house:
                    planets_between_rahu_ketu.append(planet)
                else:
                    planets_outside.append(planet)
            else:
                # Rahu in later house, Ketu in earlier house (axis wraps around)
                if planet_house > rahu_house or planet_house < ketu_house:
                    planets_between_rahu_ketu.append(planet)
                else:
                    planets_outside.append(planet)

        # Kaal Sarpa: All planets on one side
        has_kaal_sarpa = (len(planets_between_rahu_ketu) == 7 or len(planets_outside) == 7)

        # Determine type based on Rahu's house
        kaal_sarpa_types = {
            1: "Ananta Kaal Sarpa",
            2: "Kulika Kaal Sarpa",
            3: "Vasuki Kaal Sarpa",
            4: "Shankhapala Kaal Sarpa",
            5: "Padma Kaal Sarpa",
            6: "Mahapadma Kaal Sarpa",
            7: "Takshaka Kaal Sarpa",
            8: "Karkotak Kaal Sarpa",
            9: "Shankhachud Kaal Sarpa",
            10: "Ghatak Kaal Sarpa",
            11: "Vishdhar Kaal Sarpa",
            12: "Sheshnag Kaal Sarpa"
        }

        dosha_type = kaal_sarpa_types.get(rahu_house, "Kaal Sarpa")

        return {
            "name": "Kaal Sarpa Dosha",
            "present": has_kaal_sarpa,
            "severity": "high" if has_kaal_sarpa else "none",
            "details": {
                "type": dosha_type if has_kaal_sarpa else None,
                "rahu_house": rahu_house,
                "ketu_house": ketu_house,
                "planets_between": planets_between_rahu_ketu,
                "planets_outside": planets_outside
            },
            "description": (
                f"{dosha_type} - All seven planets hemmed between Rahu (house {rahu_house}) "
                f"and Ketu (house {ketu_house})" if has_kaal_sarpa
                else "Planets not hemmed between Rahu-Ketu axis"
            ),
            "effects": (
                "May cause sudden obstacles, delays in success, mental anxiety, "
                "and unexpected challenges in life" if has_kaal_sarpa
                else "No Kaal Sarpa affliction"
            ),
            "remedies": [
                "Visit Rahu-Ketu temples and perform abhishekam",
                "Recite Rahu-Ketu mantras daily",
                "Donate to serpent temples",
                "Worship Lord Shiva on Mondays",
                "Keep a Kaal Sarpa Yantra",
                "Perform Kaal Sarpa Dosha Puja on Naga Panchami",
                "Chant Maha Mrityunjaya Mantra 108 times daily"
            ] if has_kaal_sarpa else []
        }

    def detect_pitra_dosha(self, d1_planets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect Pitra Dosha (Ancestral curse/affliction)
        Indicated by: Sun-Rahu conjunction, 9th house affliction, Saturn-Rahu conjunction
        """
        sun_data = d1_planets.get("Sun", {})
        rahu_data = d1_planets.get("Rahu", {})
        saturn_data = d1_planets.get("Saturn", {})

        sun_house = sun_data.get("house", 0)
        rahu_house = rahu_data.get("house", 0)
        saturn_house = saturn_data.get("house", 0)

        # Check for indicators
        indicators = []

        # 1. Sun-Rahu conjunction or mutual aspect
        if sun_house == rahu_house:
            indicators.append("Sun-Rahu conjunction in house " + str(sun_house))

        # 2. Rahu in 9th house (house of father and ancestors)
        if rahu_house == 9:
            indicators.append("Rahu in 9th house (house of father/ancestors)")

        # 3. Saturn-Rahu conjunction
        if saturn_house == rahu_house:
            indicators.append("Saturn-Rahu conjunction in house " + str(saturn_house))

        # 4. Sun in 9th house with malefic
        if sun_house == 9:
            indicators.append("Sun in 9th house")

        has_pitra_dosha = len(indicators) >= 1

        return {
            "name": "Pitra Dosha",
            "present": has_pitra_dosha,
            "severity": "high" if len(indicators) >= 2 else "medium" if has_pitra_dosha else "none",
            "details": {
                "indicators": indicators,
                "sun_house": sun_house,
                "rahu_house": rahu_house,
                "saturn_house": saturn_house
            },
            "description": (
                "Ancestral affliction indicated by: " + "; ".join(indicators)
                if has_pitra_dosha else "No Pitra Dosha indicators found"
            ),
            "effects": (
                "May cause issues with progeny, financial challenges, health issues, "
                "unfulfilled desires, or problems in family lineage" if has_pitra_dosha
                else "No Pitra Dosha affliction"
            ),
            "remedies": [
                "Perform Pitra Tarpan (ancestral offerings) on Amavasya",
                "Perform Shraddha rituals for ancestors",
                "Donate food to Brahmins on Saturdays",
                "Plant Peepal tree and water it regularly",
                "Feed crows and dogs regularly",
                "Recite Pitra Dosha Nivaran Mantra",
                "Visit Gaya for Pind Daan",
                "Donate to the needy in the name of ancestors"
            ] if has_pitra_dosha else []
        }

    def detect_gandanta_dosha(
        self,
        d1_planets: Dict[str, Any],
        d1_ascendant: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect Gandanta Dosha (Junction points between water and fire signs)
        Critical junctions: Pisces-Aries, Cancer-Leo, Scorpio-Sagittarius
        Last 3°20' of water sign to first 3°20' of fire sign
        """
        # Gandanta zones (sign_num, degree_start, degree_end)
        gandanta_zones = [
            (11, 26.666667, 30.0),  # Last 3°20' of Pisces (11)
            (0, 0.0, 3.333333),      # First 3°20' of Aries (0)
            (3, 26.666667, 30.0),    # Last 3°20' of Cancer (3)
            (4, 0.0, 3.333333),      # First 3°20' of Leo (4)
            (7, 26.666667, 30.0),    # Last 3°20' of Scorpio (7)
            (8, 0.0, 3.333333),      # First 3°20' of Sagittarius (8)
        ]

        afflicted_points = []

        # Check Ascendant
        asc_sign = d1_ascendant.get("sign_num", 0)
        asc_degree = d1_ascendant.get("degree", 0)

        for zone_sign, zone_start, zone_end in gandanta_zones:
            if asc_sign == zone_sign and zone_start <= asc_degree <= zone_end:
                afflicted_points.append({
                    "point": "Ascendant",
                    "sign": d1_ascendant.get("sign"),
                    "degree": asc_degree
                })
                break

        # Check Moon (most sensitive to Gandanta)
        moon_data = d1_planets.get("Moon", {})
        moon_sign = moon_data.get("sign_num", 0)
        moon_degree = moon_data.get("degree", 0)

        for zone_sign, zone_start, zone_end in gandanta_zones:
            if moon_sign == zone_sign and zone_start <= moon_degree <= zone_end:
                afflicted_points.append({
                    "point": "Moon",
                    "sign": moon_data.get("sign"),
                    "degree": moon_degree
                })
                break

        has_gandanta = len(afflicted_points) > 0

        # Moon in Gandanta is most critical
        moon_in_gandanta = any(p["point"] == "Moon" for p in afflicted_points)

        return {
            "name": "Gandanta Dosha",
            "present": has_gandanta,
            "severity": "high" if moon_in_gandanta else "medium" if has_gandanta else "none",
            "details": {
                "afflicted_points": afflicted_points,
                "moon_in_gandanta": moon_in_gandanta
            },
            "description": (
                "Critical junction point affliction found in: " +
                ", ".join([f"{p['point']} in {p['sign']} at {p['degree']:.2f}°"
                          for p in afflicted_points])
                if has_gandanta else "No Gandanta affliction"
            ),
            "effects": (
                "May cause initial life struggles, health issues in childhood, "
                "mental anxiety, or transformation through hardship. "
                "Moon in Gandanta can cause emotional turmoil." if has_gandanta
                else "No Gandanta affliction"
            ),
            "remedies": [
                "Perform Gandanta Dosha Shanti Puja",
                "Recite Mahamrityunjaya Mantra 108 times daily",
                "Donate white items on Mondays if Moon is afflicted",
                "Wear Pearl gemstone after consultation",
                "Worship Lord Shiva and Goddess Durga",
                "Perform Rudrabhishek on Mondays",
                "Chant Om Namah Shivaya regularly"
            ] if has_gandanta else []
        }

    def detect_grahan_dosha(self, d1_planets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect Grahan Dosha (Eclipse dosha)
        Sun or Moon conjunct with Rahu or Ketu
        """
        sun_data = d1_planets.get("Sun", {})
        moon_data = d1_planets.get("Moon", {})
        rahu_data = d1_planets.get("Rahu", {})
        ketu_data = d1_planets.get("Ketu", {})

        sun_house = sun_data.get("house", 0)
        moon_house = moon_data.get("house", 0)
        rahu_house = rahu_data.get("house", 0)
        ketu_house = ketu_data.get("house", 0)

        afflictions = []

        # Check Sun with Rahu/Ketu
        if sun_house == rahu_house:
            afflictions.append("Sun-Rahu conjunction (Solar Eclipse yoga)")
        if sun_house == ketu_house:
            afflictions.append("Sun-Ketu conjunction")

        # Check Moon with Rahu/Ketu
        if moon_house == rahu_house:
            afflictions.append("Moon-Rahu conjunction (Lunar Eclipse yoga)")
        if moon_house == ketu_house:
            afflictions.append("Moon-Ketu conjunction")

        has_grahan = len(afflictions) > 0

        return {
            "name": "Grahan Dosha",
            "present": has_grahan,
            "severity": "high" if len(afflictions) >= 2 else "medium" if has_grahan else "none",
            "details": {
                "afflictions": afflictions,
                "sun_house": sun_house,
                "moon_house": moon_house,
                "rahu_house": rahu_house,
                "ketu_house": ketu_house
            },
            "description": (
                "Eclipse affliction found: " + "; ".join(afflictions)
                if has_grahan else "No Grahan Dosha"
            ),
            "effects": (
                "May cause challenges with father (Sun affliction) or mother (Moon affliction), "
                "mental confusion, health issues, or obstacles in life progress" if has_grahan
                else "No Grahan Dosha affliction"
            ),
            "remedies": [
                "Donate during solar/lunar eclipses",
                "Recite Surya mantra (if Sun afflicted) or Chandra mantra (if Moon afflicted)",
                "Worship Lord Vishnu or Lord Shiva",
                "Perform Grahan Dosha Nivaran Puja",
                "Donate black items for Rahu, white items for Moon",
                "Feed Brahmins on eclipse days",
                "Chant Rahu-Ketu mantras regularly"
            ] if has_grahan else []
        }

    def detect_kemdrum_dosha(self, d1_planets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect Kemdrum Dosha (Moon isolated - no planets in 2nd and 12th from Moon)
        """
        moon_data = d1_planets.get("Moon", {})
        moon_house = moon_data.get("house", 0)

        # Calculate 2nd and 12th houses from Moon
        house_before_moon = (moon_house - 2) % 12 + 1
        house_after_moon = (moon_house % 12) + 1

        # Check if any planet (except Rahu/Ketu) in these houses
        planets_to_check = ["Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        planets_before = []
        planets_after = []

        for planet in planets_to_check:
            planet_house = d1_planets.get(planet, {}).get("house", 0)
            if planet_house == house_before_moon:
                planets_before.append(planet)
            if planet_house == house_after_moon:
                planets_after.append(planet)

        has_kemdrum = (len(planets_before) == 0 and len(planets_after) == 0)

        # Check for cancellations
        cancellations = []

        # Jupiter or Venus in Kendra from Lagna cancels
        jupiter_house = d1_planets.get("Jupiter", {}).get("house", 0)
        venus_house = d1_planets.get("Venus", {}).get("house", 0)

        if jupiter_house in [1, 4, 7, 10]:
            cancellations.append("Jupiter in Kendra from Lagna")
        if venus_house in [1, 4, 7, 10]:
            cancellations.append("Venus in Kendra from Lagna")

        effective_kemdrum = has_kemdrum and len(cancellations) == 0

        return {
            "name": "Kemdrum Dosha",
            "present": effective_kemdrum,
            "severity": "medium" if effective_kemdrum else "none",
            "details": {
                "moon_house": moon_house,
                "house_before_moon": house_before_moon,
                "house_after_moon": house_after_moon,
                "planets_before": planets_before,
                "planets_after": planets_after,
                "cancellations": cancellations
            },
            "description": (
                f"Moon isolated in house {moon_house} with no planets in houses "
                f"{house_before_moon} and {house_after_moon}"
                if effective_kemdrum else "Moon not isolated"
            ),
            "effects": (
                "May cause poverty, lack of support, mental depression, or loss of comforts. "
                "However, cancellations can reduce severity." if effective_kemdrum
                else "No Kemdrum affliction"
            ),
            "remedies": [
                "Worship Lord Shiva and fast on Mondays",
                "Wear Pearl gemstone after consultation",
                "Donate white items on Mondays",
                "Recite Chandra (Moon) mantra 108 times daily",
                "Perform Chandra Graha Shanti Puja",
                "Keep fast on Purnima (Full Moon)",
                "Drink water from silver vessel"
            ] if effective_kemdrum else []
        }


# Singleton instance
dosha_detection_service = DoshaDetectionService()
