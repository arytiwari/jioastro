"""
Jaimini Astrology System Service

Implements the Jaimini system of Vedic astrology including:
- Chara Karakas (7 significators based on degrees)
- Karakamsha (Navamsa position of Atmakaraka)
- Svamsa (Navamsa position of Lagna)
- Arudha Padas (illusion points for all houses)
- Rashi Drishti (sign-based aspects)
- Argala (interventions)
- Chara Dasha (sign-based period system)

Author: JioAstro Development Team
Date: January 2025
"""

from typing import Dict, List, Tuple, Any, Optional
from datetime import date, datetime, timedelta
import math


class JaiminiService:
    """
    Singleton service for Jaimini astrology calculations
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JaiminiService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True

        # Sign classifications
        self.MOVABLE_SIGNS = [1, 4, 7, 10]  # Aries, Cancer, Libra, Capricorn
        self.FIXED_SIGNS = [2, 5, 8, 11]    # Taurus, Leo, Scorpio, Aquarius
        self.DUAL_SIGNS = [3, 6, 9, 12]     # Gemini, Virgo, Sagittarius, Pisces

        # Sign names
        self.SIGN_NAMES = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]

        # Sign lords
        self.SIGN_LORDS = {
            1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
            7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
        }

        # Karaka names and meanings
        self.KARAKA_NAMES = {
            "AK": ("Atmakaraka", "Soul", "Self-realization, spiritual path, core identity"),
            "AmK": ("Amatyakaraka", "Minister", "Career, profession, advisors, support system"),
            "BK": ("Bhratrukaraka", "Sibling", "Siblings, courage, initiatives, co-workers"),
            "MK": ("Matrukaraka", "Mother", "Mother, emotions, home, vehicles, comforts"),
            "PK": ("Pitrukaraka", "Father", "Father, authority, teachers, dharma, principles"),
            "GK": ("Gnatikaraka", "Cousin", "Obstacles, enemies, diseases, competitors, litigation"),
            "DK": ("Darakaraka", "Spouse", "Spouse, relationships, partnerships, business partners")
        }

    # =========================================================================
    # CHARA KARAKAS CALCULATION
    # =========================================================================

    def calculate_chara_karakas(self, planets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the 7 Chara Karakas based on planetary degrees.

        The planet with the highest longitude becomes Atmakaraka (AK),
        second highest becomes Amatyakaraka (AmK), and so on.

        Special rule: Rahu's degree is calculated from opposite point (30° - actual)

        Args:
            planets: Dictionary with planet data including longitude

        Returns:
            Dictionary with all 7 karakas and their details
        """
        # Extract degrees for ranking
        planet_degrees = []

        for planet_name, planet_data in planets.items():
            if planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]:
                longitude = planet_data.get("longitude", 0)

                # Special handling for Rahu - use opposite degree
                if planet_name == "Rahu":
                    sign_num = int(longitude / 30) + 1
                    degree_in_sign = longitude % 30
                    adjusted_degree = 30 - degree_in_sign
                    adjusted_longitude = (sign_num - 1) * 30 + adjusted_degree
                    longitude = adjusted_longitude

                planet_degrees.append({
                    "planet": planet_name,
                    "longitude": longitude,
                    "original_data": planet_data
                })

        # Sort by degree descending (highest first)
        planet_degrees.sort(key=lambda x: x["longitude"], reverse=True)

        # Assign karakas in order
        karaka_order = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
        karakas = {}

        for i, karaka_code in enumerate(karaka_order):
            if i < len(planet_degrees):
                planet_info = planet_degrees[i]
                full_name, role, signification = self.KARAKA_NAMES[karaka_code]

                karakas[karaka_code] = {
                    "code": karaka_code,
                    "full_name": full_name,
                    "role": role,
                    "signification": signification,
                    "planet": planet_info["planet"],
                    "longitude": planet_info["longitude"],
                    "sign": self.SIGN_NAMES[int(planet_info["longitude"] / 30)],
                    "sign_num": int(planet_info["longitude"] / 30) + 1,
                    "degree_in_sign": planet_info["longitude"] % 30,
                    "house": planet_info["original_data"].get("house", None)
                }

        return karakas

    def get_atmakaraka(self, karakas: Dict[str, Any]) -> Dict[str, Any]:
        """Get the Atmakaraka (soul significator)"""
        return karakas.get("AK", {})

    def get_darakaraka(self, karakas: Dict[str, Any]) -> Dict[str, Any]:
        """Get the Darakaraka (spouse significator)"""
        return karakas.get("DK", {})

    # =========================================================================
    # KARAKAMSHA CALCULATION
    # =========================================================================

    def calculate_karakamsha(self, atmakaraka: Dict[str, Any], d9_chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Karakamsha - the Navamsa (D9) position of Atmakaraka.

        Karakamsha reveals:
        - Spiritual inclinations and path
        - Deep-seated desires
        - Career aptitudes from past lives
        - Karmic patterns

        Args:
            atmakaraka: Atmakaraka planet details
            d9_chart: Navamsa (D9) chart data

        Returns:
            Karakamsha analysis with sign, planets, aspects, and interpretations
        """
        if not atmakaraka or not d9_chart:
            return {}

        ak_planet = atmakaraka.get("planet")
        if not ak_planet:
            return {}

        # Get AK's position in D9
        d9_planets = d9_chart.get("planets", {})
        ak_in_d9 = d9_planets.get(ak_planet, {})

        if not ak_in_d9:
            return {}

        karakamsha_sign_num = ak_in_d9.get("sign_num", 1)
        karakamsha_house = ak_in_d9.get("house", 1)

        # Find planets in Karakamsha
        planets_in_karakamsha = []
        for planet_name, planet_data in d9_planets.items():
            if planet_data.get("sign_num") == karakamsha_sign_num and planet_name != ak_planet:
                planets_in_karakamsha.append(planet_name)

        # Get sign lord
        sign_lord = self.SIGN_LORDS.get(karakamsha_sign_num, "Unknown")

        # Basic significations based on sign
        significations = self._get_karakamsha_significations(karakamsha_sign_num)

        return {
            "sign": self.SIGN_NAMES[karakamsha_sign_num - 1],
            "sign_num": karakamsha_sign_num,
            "house_in_d9": karakamsha_house,
            "lord": sign_lord,
            "atmakaraka_planet": ak_planet,
            "planets_in_karakamsha": planets_in_karakamsha,
            "significations": significations["significations"],
            "career_indications": significations["careers"],
            "spiritual_path": significations["spiritual"],
            "interpretation": self._interpret_karakamsha(karakamsha_sign_num, planets_in_karakamsha)
        }

    def _get_karakamsha_significations(self, sign_num: int) -> Dict[str, List[str]]:
        """Get significations for each Karakamsha sign"""
        sign_meanings = {
            1: {  # Aries
                "significations": ["Leadership", "Initiative", "Courage", "Independence"],
                "careers": ["Military", "Sports", "Engineering", "Surgery", "Entrepreneurship"],
                "spiritual": "Karma Yoga (Action-based spirituality)"
            },
            2: {  # Taurus
                "significations": ["Stability", "Material comfort", "Art", "Beauty"],
                "careers": ["Finance", "Banking", "Arts", "Agriculture", "Luxury goods"],
                "spiritual": "Bhakti Yoga (Devotional path through material world)"
            },
            3: {  # Gemini
                "significations": ["Communication", "Intellect", "Versatility", "Trade"],
                "careers": ["Writing", "Teaching", "Media", "Trade", "Technology"],
                "spiritual": "Jnana Yoga (Path of knowledge and communication)"
            },
            4: {  # Cancer
                "significations": ["Nurturing", "Emotions", "Home", "Care"],
                "careers": ["Nursing", "Counseling", "Food industry", "Real estate", "Social work"],
                "spiritual": "Bhakti Yoga (Emotional devotion)"
            },
            5: {  # Leo
                "significations": ["Authority", "Creativity", "Pride", "Leadership"],
                "careers": ["Government", "Politics", "Entertainment", "Management", "Theater"],
                "spiritual": "Raj Yoga (Royal path, leadership in spirituality)"
            },
            6: {  # Virgo
                "significations": ["Service", "Analysis", "Health", "Perfection"],
                "careers": ["Medicine", "Accounting", "Analysis", "Health services", "Editing"],
                "spiritual": "Karma Yoga (Service-oriented spirituality)"
            },
            7: {  # Libra
                "significations": ["Balance", "Partnerships", "Justice", "Harmony"],
                "careers": ["Law", "Diplomacy", "Design", "Partnership business", "Counseling"],
                "spiritual": "Bhakti Yoga (Devotion through relationships)"
            },
            8: {  # Scorpio
                "significations": ["Transformation", "Research", "Occult", "Depth"],
                "careers": ["Research", "Occult sciences", "Surgery", "Investigation", "Psychology"],
                "spiritual": "Tantra Yoga (Transformation path, occult practices)"
            },
            9: {  # Sagittarius
                "significations": ["Wisdom", "Teaching", "Philosophy", "Higher learning"],
                "careers": ["Teaching", "Law", "Philosophy", "Publishing", "Travel industry"],
                "spiritual": "Jnana Yoga (Path of wisdom and higher knowledge)"
            },
            10: {  # Capricorn
                "significations": ["Discipline", "Structure", "Achievement", "Status"],
                "careers": ["Administration", "Construction", "Large organizations", "Government", "Mining"],
                "spiritual": "Karma Yoga (Disciplined spiritual practice)"
            },
            11: {  # Aquarius
                "significations": ["Innovation", "Humanitarianism", "Group work", "Idealism"],
                "careers": ["Technology", "Social causes", "Networking", "Research", "Astrology"],
                "spiritual": "Jnana Yoga (Path of higher consciousness)"
            },
            12: {  # Pisces
                "significations": ["Spirituality", "Compassion", "Imagination", "Transcendence"],
                "careers": ["Spirituality", "Arts", "Healing", "Charity", "Isolation work"],
                "spiritual": "Bhakti Yoga (Pure devotion and surrender)"
            }
        }

        return sign_meanings.get(sign_num, {
            "significations": ["Varied influences"],
            "careers": ["Multiple paths possible"],
            "spiritual": "Individual path based on karmas"
        })

    def _interpret_karakamsha(self, sign_num: int, planets: List[str]) -> str:
        """Generate interpretation of Karakamsha"""
        sign_name = self.SIGN_NAMES[sign_num - 1]

        base = f"Karakamsha in {sign_name} indicates a soul with strong {sign_name} qualities. "

        if planets:
            planet_str = ", ".join(planets)
            base += f"With {planet_str} present, these influences are further emphasized. "
        else:
            base += "No other planets in Karakamsha suggest a pure expression of sign qualities. "

        return base

    def calculate_svamsa(self, lagna_longitude: float, d9_chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Svamsa (Lagnamsa) - Navamsa position of Ascendant.

        Args:
            lagna_longitude: Ascendant longitude in D1
            d9_chart: Navamsa chart data

        Returns:
            Svamsa details with interpretation
        """
        # Calculate D9 position of Lagna
        d9_sign = self._calculate_navamsa_sign(lagna_longitude)

        return {
            "sign": self.SIGN_NAMES[d9_sign - 1],
            "sign_num": d9_sign,
            "lord": self.SIGN_LORDS.get(d9_sign, "Unknown"),
            "significance": "True self-image and karmic tendencies"
        }

    def _calculate_navamsa_sign(self, longitude: float) -> int:
        """Calculate Navamsa (D9) sign from longitude"""
        sign = int(longitude / 30) + 1
        degree_in_sign = longitude % 30
        navamsa_portion = int(degree_in_sign / 3.333333)  # 30/9 = 3.33° per navamsa

        # Calculate D9 sign
        if sign in [1, 5, 9]:  # Fire signs start from own sign
            d9_sign = ((navamsa_portion) % 12) + 1
        elif sign in [2, 6, 10]:  # Earth signs start from 10th
            d9_sign = ((9 + navamsa_portion) % 12) + 1
        elif sign in [3, 7, 11]:  # Air signs start from 7th
            d9_sign = ((6 + navamsa_portion) % 12) + 1
        else:  # Water signs start from 4th
            d9_sign = ((3 + navamsa_portion) % 12) + 1

        return d9_sign

    # =========================================================================
    # ARUDHA PADAS CALCULATION
    # =========================================================================

    def calculate_arudha_pada(self, house: int, chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Arudha Pada for a given house.

        Method:
        1. Find lord of the house
        2. Count from lord's position to the house
        3. Count same distance from the house
        4. Exception: If pada falls in 1st or 7th from house, count 10 signs ahead

        Args:
            house: House number (1-12)
            chart: Birth chart data

        Returns:
            Arudha Pada sign and interpretation
        """
        # Get house sign
        houses = chart.get("houses", {})
        house_sign = houses.get(str(house), {}).get("sign_num", house)

        # Get lord of house
        lord = self.SIGN_LORDS.get(house_sign, "Sun")

        # Find lord's position
        planets = chart.get("planets", {})
        lord_data = planets.get(lord, {})
        lord_house = lord_data.get("house", 1)

        # Calculate distance from lord to house
        if lord_house <= house:
            distance = house - lord_house
        else:
            distance = 12 - lord_house + house

        # Count same distance from house
        pada_house = (house + distance - 1) % 12 + 1

        # Exception rule: If pada in 1st or 7th from house, count 10 ahead
        diff = abs(pada_house - house)
        if diff == 0 or diff == 6:
            pada_house = (house + 10 - 1) % 12 + 1

        pada_sign = houses.get(str(pada_house), {}).get("sign_num", pada_house)

        return {
            "house": pada_house,
            "sign": self.SIGN_NAMES[pada_sign - 1] if pada_sign <= 12 else "Unknown",
            "sign_num": pada_sign,
            "lord": self.SIGN_LORDS.get(pada_sign, "Unknown")
        }

    def calculate_all_arudha_padas(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate all 12 Arudha Padas"""
        arudha_padas = {}

        house_meanings = {
            1: ("AL", "Arudha Lagna", "Self-image, public persona"),
            2: ("A2", "Dhana Pada", "Wealth perception"),
            3: ("A3", "Vikrama Pada", "Courage, siblings image"),
            4: ("A4", "Matru Pada", "Mother, property image"),
            5: ("A5", "Putra Pada", "Children, creativity image"),
            6: ("A6", "Shatru Pada", "Enemies, health image"),
            7: ("A7", "Dara Pada", "Spouse, partnership image"),
            8: ("A8", "Ayu Pada", "Longevity, transformation image"),
            9: ("A9", "Bhagya Pada", "Fortune, father image"),
            10: ("A10", "Karma Pada", "Career, status image"),
            11: ("A11", "Labha Pada", "Gains, aspirations image"),
            12: ("A12", "Vyaya Pada", "Losses, liberation image, also Upapada (marriage) when calculated from 12th")
        }

        for house_num in range(1, 13):
            pada = self.calculate_arudha_pada(house_num, chart)
            code, name, meaning = house_meanings[house_num]

            pada_info = {
                **pada,
                "code": code,
                "name": name,
                "meaning": meaning
            }

            arudha_padas[code] = pada_info

        return arudha_padas

    def calculate_upapada_lagna(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Upapada Lagna (UL) - Arudha of 12th house.

        UL represents:
        - Marriage circumstances
        - Spouse's nature as perceived
        - Quality of married life
        """
        ul = self.calculate_arudha_pada(12, chart)
        ul["name"] = "Upapada Lagna (UL)"
        ul["code"] = "UL"
        ul["meaning"] = "Marriage image and spouse nature"
        return ul

    # =========================================================================
    # RASHI DRISHTI (SIGN ASPECTS)
    # =========================================================================

    def get_sign_type(self, sign_num: int) -> str:
        """Get sign type: movable, fixed, or dual"""
        if sign_num in self.MOVABLE_SIGNS:
            return "movable"
        elif sign_num in self.FIXED_SIGNS:
            return "fixed"
        else:
            return "dual"

    def calculate_rashi_drishti(self, sign_num: int) -> List[int]:
        """
        Calculate Rashi Drishti (sign aspects).

        Rules:
        - Movable signs aspect all fixed signs (except themselves)
        - Fixed signs aspect all movable signs (except themselves)
        - Dual signs aspect other dual signs (except themselves)

        Args:
            sign_num: Sign number (1-12)

        Returns:
            List of aspected sign numbers
        """
        sign_type = self.get_sign_type(sign_num)

        if sign_type == "movable":
            # Aspect all fixed signs
            aspected = [s for s in self.FIXED_SIGNS if s != sign_num]
        elif sign_type == "fixed":
            # Aspect all movable signs
            aspected = [s for s in self.MOVABLE_SIGNS if s != sign_num]
        else:  # dual
            # Aspect other dual signs
            aspected = [s for s in self.DUAL_SIGNS if s != sign_num]

        return sorted(aspected)

    def get_aspecting_signs(self, sign_num: int) -> List[int]:
        """Get signs that aspect this sign"""
        aspecting = []
        for other_sign in range(1, 13):
            if other_sign != sign_num:
                aspects = self.calculate_rashi_drishti(other_sign)
                if sign_num in aspects:
                    aspecting.append(other_sign)
        return aspecting

    # =========================================================================
    # ARGALA (INTERVENTIONS)
    # =========================================================================

    def calculate_argala(self, reference_house: int, chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Argala (beneficial intervention) for a house.

        Planets in 2nd, 4th, 11th from reference create beneficial argala.
        Planets in 12th, 10th, 3rd create virodha (obstruction) to argala.

        Args:
            reference_house: Reference house number
            chart: Chart data with planets

        Returns:
            Argala analysis
        """
        planets = chart.get("planets", {})

        # Houses creating argala
        argala_houses = [
            (reference_house % 12) + 1,      # 2nd house
            (reference_house + 2) % 12 + 1,  # 4th house
            (reference_house + 9) % 12 + 1   # 11th house
        ]

        # Houses creating virodha (obstruction)
        virodha_houses = [
            (reference_house + 10) % 12 + 1,  # 12th house
            (reference_house + 8) % 12 + 1,   # 10th house
            (reference_house + 1) % 12 + 1    # 3rd house
        ]

        argala_planets = []
        virodha_planets = []

        for planet_name, planet_data in planets.items():
            if planet_name != "Ketu":  # Ketu doesn't create argala
                house = planet_data.get("house", 1)

                if house in argala_houses:
                    argala_planets.append({
                        "planet": planet_name,
                        "house": house,
                        "type": "beneficial"
                    })
                elif house in virodha_houses:
                    virodha_planets.append({
                        "planet": planet_name,
                        "house": house,
                        "type": "obstruction"
                    })

        return {
            "argala_planets": argala_planets,
            "virodha_planets": virodha_planets,
            "net_effect": "beneficial" if len(argala_planets) > len(virodha_planets) else "obstructed" if len(virodha_planets) > len(argala_planets) else "neutral"
        }

    # =========================================================================
    # CHARA DASHA (SIMPLIFIED VERSION)
    # =========================================================================

    def calculate_chara_dasha_years(self, sign_num: int, chart: Dict[str, Any]) -> int:
        """
        Calculate dasha years for a sign (simplified method).

        Count from sign to its lord's position.
        Each count = 1 year.

        Args:
            sign_num: Sign number
            chart: Chart data

        Returns:
            Number of years for this sign's dasha
        """
        lord = self.SIGN_LORDS.get(sign_num, "Sun")
        planets = chart.get("planets", {})
        lord_data = planets.get(lord, {})
        lord_sign = lord_data.get("sign_num", sign_num)

        # Count from sign to lord's sign
        if lord_sign >= sign_num:
            years = lord_sign - sign_num + 1
        else:
            years = 12 - sign_num + lord_sign + 1

        return min(years, 12)  # Max 12 years per dasha

    def calculate_chara_dasha_sequence(self, chart: Dict[str, Any], birth_date: date) -> List[Dict[str, Any]]:
        """
        Calculate Chara Dasha sequence (simplified).

        This is a basic implementation. Full Chara Dasha requires
        complex rules based on paka, kendras, etc.

        Args:
            chart: Chart data
            birth_date: Birth date for calculating periods

        Returns:
            List of dasha periods with dates
        """
        lagna_sign = chart.get("ascendant", {}).get("sign_num", 1)

        # Simple forward sequence from lagna
        dasha_sequence = []
        current_date = birth_date

        for i in range(12):
            sign_num = ((lagna_sign + i - 1) % 12) + 1
            years = self.calculate_chara_dasha_years(sign_num, chart)

            end_date = current_date + timedelta(days=years * 365.25)

            dasha_sequence.append({
                "sign": self.SIGN_NAMES[sign_num - 1],
                "sign_num": sign_num,
                "start_date": current_date.isoformat(),
                "end_date": end_date.isoformat(),
                "duration_years": years,
                "lord": self.SIGN_LORDS.get(sign_num, "Unknown")
            })

            current_date = end_date

        return dasha_sequence

    def get_current_chara_dasha(self, dasha_sequence: List[Dict[str, Any]], current_date: date = None) -> Dict[str, Any]:
        """Get current Chara Dasha period"""
        if current_date is None:
            current_date = date.today()

        current_date_str = current_date.isoformat()

        for dasha in dasha_sequence:
            if dasha["start_date"] <= current_date_str <= dasha["end_date"]:
                return dasha

        return {}

    # =========================================================================
    # COMPREHENSIVE JAIMINI ANALYSIS
    # =========================================================================

    def analyze_jaimini_chart(self, chart: Dict[str, Any], d9_chart: Dict[str, Any], birth_date: date) -> Dict[str, Any]:
        """
        Perform comprehensive Jaimini analysis of a chart.

        Args:
            chart: D1 birth chart
            d9_chart: D9 Navamsa chart
            birth_date: Birth date for dasha calculation

        Returns:
            Complete Jaimini analysis
        """
        planets = chart.get("planets", {})

        # Calculate Chara Karakas
        karakas = self.calculate_chara_karakas(planets)

        # Get Atmakaraka
        atmakaraka = self.get_atmakaraka(karakas)

        # Calculate Karakamsha
        karakamsha = self.calculate_karakamsha(atmakaraka, d9_chart)

        # Calculate Svamsa
        lagna_long = chart.get("ascendant", {}).get("longitude", 0)
        svamsa = self.calculate_svamsa(lagna_long, d9_chart)

        # Calculate Arudha Padas
        arudha_padas = self.calculate_all_arudha_padas(chart)

        # Calculate Chara Dasha
        chara_dasha_sequence = self.calculate_chara_dasha_sequence(chart, birth_date)
        current_chara_dasha = self.get_current_chara_dasha(chara_dasha_sequence)

        return {
            "chara_karakas": karakas,
            "atmakaraka": atmakaraka,
            "karakamsha": karakamsha,
            "svamsa": svamsa,
            "arudha_padas": arudha_padas,
            "chara_dasha": {
                "current": current_chara_dasha,
                "sequence": chara_dasha_sequence
            },
            "calculation_date": datetime.now().isoformat()
        }


# Singleton instance
jaimini_service = JaiminiService()
