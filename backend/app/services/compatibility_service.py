"""
Vedic Astrology Compatibility Matching Service

Implements traditional Kundali matching techniques:
- Ashtakoot (Guna Milan) - 8-factor compatibility scoring
- Manglik Dosha analysis
- Compatibility recommendations
"""

from typing import Dict, Any, List, Tuple
from datetime import date


class CompatibilityService:
    """Singleton service for Vedic astrology compatibility analysis."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize compatibility calculation data."""
        # Nakshatra mapping for compatibility calculations
        self.NAKSHATRAS = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
            "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
            "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
            "Uttara Bhadrapada", "Revati"
        ]

        # Varna (spiritual compatibility) - 1 point
        self.VARNA_MAP = {
            "Ashwini": "Vaishya", "Bharani": "Vaishya", "Krittika": "Brahmin",
            "Rohini": "Shudra", "Mrigashira": "Shudra", "Ardra": "Shudra",
            "Punarvasu": "Vaishya", "Pushya": "Kshatriya", "Ashlesha": "Shudra",
            "Magha": "Shudra", "Purva Phalguni": "Brahmin", "Uttara Phalguni": "Kshatriya",
            "Hasta": "Vaishya", "Chitra": "Shudra", "Swati": "Shudra",
            "Vishakha": "Shudra", "Anuradha": "Shudra", "Jyeshtha": "Shudra",
            "Mula": "Shudra", "Purva Ashadha": "Brahmin", "Uttara Ashadha": "Kshatriya",
            "Shravana": "Shudra", "Dhanishta": "Shudra", "Shatabhisha": "Shudra",
            "Purva Bhadrapada": "Brahmin", "Uttara Bhadrapada": "Kshatriya", "Revati": "Shudra"
        }

        # Vashya (mutual attraction) - 2 points
        self.VASHYA_MAP = {
            "Ashwini": "Quadruped", "Bharani": "Quadruped", "Krittika": "Quadruped",
            "Rohini": "Quadruped", "Mrigashira": "Quadruped", "Ardra": "Human",
            "Punarvasu": "Human", "Pushya": "Quadruped", "Ashlesha": "Serpent",
            "Magha": "Serpent", "Purva Phalguni": "Quadruped", "Uttara Phalguni": "Human",
            "Hasta": "Quadruped", "Chitra": "Quadruped", "Swati": "Quadruped",
            "Vishakha": "Quadruped", "Anuradha": "Quadruped", "Jyeshtha": "Quadruped",
            "Mula": "Quadruped", "Purva Ashadha": "Human", "Uttara Ashadha": "Quadruped",
            "Shravana": "Quadruped", "Dhanishta": "Serpent", "Shatabhisha": "Quadruped",
            "Purva Bhadrapada": "Human", "Uttara Bhadrapada": "Human", "Revati": "Aquatic"
        }

        # Gana (temperament compatibility) - 6 points
        self.GANA_MAP = {
            "Ashwini": "Deva", "Bharani": "Manushya", "Krittika": "Rakshasa",
            "Rohini": "Manushya", "Mrigashira": "Deva", "Ardra": "Manushya",
            "Punarvasu": "Deva", "Pushya": "Deva", "Ashlesha": "Rakshasa",
            "Magha": "Rakshasa", "Purva Phalguni": "Manushya", "Uttara Phalguni": "Manushya",
            "Hasta": "Deva", "Chitra": "Rakshasa", "Swati": "Deva",
            "Vishakha": "Rakshasa", "Anuradha": "Deva", "Jyeshtha": "Rakshasa",
            "Mula": "Rakshasa", "Purva Ashadha": "Manushya", "Uttara Ashadha": "Manushya",
            "Shravana": "Deva", "Dhanishta": "Rakshasa", "Shatabhisha": "Rakshasa",
            "Purva Bhadrapada": "Manushya", "Uttara Bhadrapada": "Manushya", "Revati": "Deva"
        }

        # Yoni (sexual compatibility) - 4 points
        self.YONI_MAP = {
            "Ashwini": ("Horse", "M"), "Bharani": ("Elephant", "M"), "Krittika": ("Sheep", "F"),
            "Rohini": ("Serpent", "M"), "Mrigashira": ("Serpent", "F"), "Ardra": ("Dog", "F"),
            "Punarvasu": ("Cat", "F"), "Pushya": ("Sheep", "M"), "Ashlesha": ("Cat", "M"),
            "Magha": ("Rat", "M"), "Purva Phalguni": ("Rat", "F"), "Uttara Phalguni": ("Cow", "M"),
            "Hasta": ("Buffalo", "F"), "Chitra": ("Tiger", "F"), "Swati": ("Buffalo", "M"),
            "Vishakha": ("Tiger", "M"), "Anuradha": ("Deer", "F"), "Jyeshtha": ("Deer", "M"),
            "Mula": ("Dog", "M"), "Purva Ashadha": ("Monkey", "M"), "Uttara Ashadha": ("Mongoose", "M"),
            "Shravana": ("Monkey", "F"), "Dhanishta": ("Lion", "F"), "Shatabhisha": ("Horse", "F"),
            "Purva Bhadrapada": ("Lion", "M"), "Uttara Bhadrapada": ("Cow", "F"), "Revati": ("Elephant", "F")
        }

        # Nadi (health/genetic compatibility) - 8 points
        self.NADI_MAP = {
            "Ashwini": "Aadi", "Bharani": "Madhya", "Krittika": "Antya",
            "Rohini": "Madhya", "Mrigashira": "Aadi", "Ardra": "Madhya",
            "Punarvasu": "Aadi", "Pushya": "Madhya", "Ashlesha": "Antya",
            "Magha": "Aadi", "Purva Phalguni": "Madhya", "Uttara Phalguni": "Antya",
            "Hasta": "Madhya", "Chitra": "Aadi", "Swati": "Madhya",
            "Vishakha": "Antya", "Anuradha": "Aadi", "Jyeshtha": "Madhya",
            "Mula": "Antya", "Purva Ashadha": "Madhya", "Uttara Ashadha": "Aadi",
            "Shravana": "Madhya", "Dhanishta": "Antya", "Shatabhisha": "Aadi",
            "Purva Bhadrapada": "Madhya", "Uttara Bhadrapada": "Antya", "Revati": "Madhya"
        }

    # =========================================================================
    # NAKSHATRA CALCULATION
    # =========================================================================

    def get_nakshatra(self, moon_longitude: float) -> Dict[str, Any]:
        """
        Calculate Nakshatra from Moon's longitude.

        Args:
            moon_longitude: Moon's longitude in degrees (0-360)

        Returns:
            Dictionary with nakshatra name, number, and pada
        """
        # Each nakshatra spans 13.333... degrees (360 / 27)
        nakshatra_size = 360.0 / 27.0
        nakshatra_num = int(moon_longitude / nakshatra_size)
        nakshatra_name = self.NAKSHATRAS[nakshatra_num]

        # Calculate pada (1-4) within the nakshatra
        position_in_nakshatra = moon_longitude % nakshatra_size
        pada = int(position_in_nakshatra / (nakshatra_size / 4)) + 1

        return {
            "name": nakshatra_name,
            "number": nakshatra_num + 1,
            "pada": pada,
            "longitude": moon_longitude,
            "position_in_nakshatra": position_in_nakshatra
        }

    # =========================================================================
    # ASHTAKOOT (GUNA MILAN) CALCULATIONS
    # =========================================================================

    def calculate_varna(self, boy_nakshatra: str, girl_nakshatra: str) -> Dict[str, Any]:
        """Calculate Varna (spiritual compatibility) - 1 point max."""
        boy_varna = self.VARNA_MAP.get(boy_nakshatra)
        girl_varna = self.VARNA_MAP.get(girl_nakshatra)

        varna_order = ["Brahmin", "Kshatriya", "Vaishya", "Shudra"]
        boy_rank = varna_order.index(boy_varna) if boy_varna in varna_order else 3
        girl_rank = varna_order.index(girl_varna) if girl_varna in varna_order else 3

        # Boy's varna should be equal or higher (lower index)
        points = 1 if boy_rank <= girl_rank else 0

        return {
            "name": "Varna",
            "max_points": 1,
            "obtained_points": points,
            "boy_value": boy_varna,
            "girl_value": girl_varna,
            "compatible": points > 0,
            "description": "Spiritual compatibility and ego"
        }

    def calculate_vashya(self, boy_nakshatra: str, girl_nakshatra: str) -> Dict[str, Any]:
        """Calculate Vashya (mutual attraction) - 2 points max."""
        boy_vashya = self.VASHYA_MAP.get(boy_nakshatra)
        girl_vashya = self.VASHYA_MAP.get(girl_nakshatra)

        # Full points for same vashya, partial for compatible types
        if boy_vashya == girl_vashya:
            points = 2
        elif (boy_vashya == "Human" and girl_vashya == "Aquatic") or \
             (boy_vashya == "Aquatic" and girl_vashya == "Human"):
            points = 1
        elif (boy_vashya == "Quadruped" and girl_vashya == "Human") or \
             (boy_vashya == "Human" and girl_vashya == "Quadruped"):
            points = 1
        else:
            points = 0

        return {
            "name": "Vashya",
            "max_points": 2,
            "obtained_points": points,
            "boy_value": boy_vashya,
            "girl_value": girl_vashya,
            "compatible": points > 0,
            "description": "Mutual attraction and control"
        }

    def calculate_tara(self, boy_nakshatra_num: int, girl_nakshatra_num: int) -> Dict[str, Any]:
        """Calculate Tara (birth star compatibility) - 3 points max."""
        # Count from girl's nakshatra to boy's
        count_from_girl = ((boy_nakshatra_num - girl_nakshatra_num) % 27) + 1
        # Count from boy's nakshatra to girl's
        count_from_boy = ((girl_nakshatra_num - boy_nakshatra_num) % 27) + 1

        # Determine category (1-9 repeating pattern)
        girl_tara_category = ((count_from_girl - 1) % 9) + 1
        boy_tara_category = ((count_from_boy - 1) % 9) + 1

        # Favorable taras: 1,3,5,7 (Janma, Sampat, Kshema, Sadhaka, Mitra, Ati-Mitra)
        favorable_taras = [1, 3, 5, 7]

        girl_favorable = girl_tara_category in favorable_taras
        boy_favorable = boy_tara_category in favorable_taras

        if girl_favorable and boy_favorable:
            points = 3
        elif girl_favorable or boy_favorable:
            points = 1.5
        else:
            points = 0

        return {
            "name": "Tara",
            "max_points": 3,
            "obtained_points": points,
            "boy_tara": boy_tara_category,
            "girl_tara": girl_tara_category,
            "compatible": points > 1,
            "description": "Birth star compatibility and longevity"
        }

    def calculate_yoni(self, boy_nakshatra: str, girl_nakshatra: str) -> Dict[str, Any]:
        """Calculate Yoni (sexual compatibility) - 4 points max."""
        boy_yoni = self.YONI_MAP.get(boy_nakshatra, ("Unknown", "M"))
        girl_yoni = self.YONI_MAP.get(girl_nakshatra, ("Unknown", "F"))

        boy_animal, boy_gender = boy_yoni
        girl_animal, girl_gender = girl_yoni

        # Enemy pairs
        enemy_pairs = [
            ("Horse", "Buffalo"), ("Elephant", "Lion"), ("Sheep", "Monkey"),
            ("Serpent", "Mongoose"), ("Dog", "Deer"), ("Cat", "Rat"), ("Tiger", "Cow")
        ]

        # Friendly pairs
        friendly_pairs = [
            ("Horse", "Horse"), ("Elephant", "Elephant"), ("Sheep", "Sheep"),
            ("Serpent", "Serpent"), ("Dog", "Dog"), ("Cat", "Cat"),
            ("Tiger", "Tiger"), ("Cow", "Cow"), ("Buffalo", "Buffalo"),
            ("Rat", "Rat"), ("Deer", "Deer"), ("Monkey", "Monkey"),
            ("Lion", "Lion"), ("Mongoose", "Mongoose")
        ]

        is_enemy = any((boy_animal == a and girl_animal == b) or (boy_animal == b and girl_animal == a)
                      for a, b in enemy_pairs)
        is_friendly = any((boy_animal == a and girl_animal == b) or (boy_animal == b and girl_animal == a)
                         for a, b in friendly_pairs)

        if boy_animal == girl_animal and boy_gender != girl_gender:
            points = 4  # Perfect match
        elif is_friendly:
            points = 3
        elif is_enemy:
            points = 0
        else:
            points = 2  # Neutral

        return {
            "name": "Yoni",
            "max_points": 4,
            "obtained_points": points,
            "boy_value": boy_animal,
            "girl_value": girl_animal,
            "compatible": points >= 2,
            "description": "Sexual compatibility and physical attraction"
        }

    def calculate_graha_maitri(self, boy_chart: Dict[str, Any], girl_chart: Dict[str, Any],
                               boy_nakshatra: str, girl_nakshatra: str) -> Dict[str, Any]:
        """Calculate Graha Maitri (planetary friendship) - 5 points max."""
        # Get moon sign lords
        boy_moon_sign = self.get_sign_from_nakshatra(boy_nakshatra)
        girl_moon_sign = self.get_sign_from_nakshatra(girl_nakshatra)

        boy_lord = self.get_sign_lord(boy_moon_sign)
        girl_lord = self.get_sign_lord(girl_moon_sign)

        # Check friendship status
        relationship = self.get_planetary_relationship(boy_lord, girl_lord)

        if relationship == "friend":
            points = 5
        elif relationship == "neutral":
            points = 4
        else:  # enemy
            points = 0.5

        return {
            "name": "Graha Maitri",
            "max_points": 5,
            "obtained_points": points,
            "boy_moon_sign": boy_moon_sign,
            "girl_moon_sign": girl_moon_sign,
            "boy_lord": boy_lord,
            "girl_lord": girl_lord,
            "relationship": relationship,
            "compatible": points >= 3,
            "description": "Mental compatibility and friendship"
        }

    def calculate_gana(self, boy_nakshatra: str, girl_nakshatra: str) -> Dict[str, Any]:
        """Calculate Gana (temperament compatibility) - 6 points max."""
        boy_gana = self.GANA_MAP.get(boy_nakshatra)
        girl_gana = self.GANA_MAP.get(girl_nakshatra)

        if boy_gana == girl_gana:
            points = 6
        elif boy_gana == "Deva" and girl_gana == "Manushya":
            points = 6
        elif boy_gana == "Manushya" and girl_gana == "Deva":
            points = 5
        elif boy_gana == "Deva" and girl_gana == "Rakshasa":
            points = 1
        elif boy_gana == "Manushya" and girl_gana == "Rakshasa":
            points = 0.5
        else:
            points = 0

        return {
            "name": "Gana",
            "max_points": 6,
            "obtained_points": points,
            "boy_value": boy_gana,
            "girl_value": girl_gana,
            "compatible": points >= 3,
            "description": "Temperament and behavior compatibility"
        }

    def calculate_bhakoot(self, boy_nakshatra: str, girl_nakshatra: str) -> Dict[str, Any]:
        """Calculate Bhakoot (sign position compatibility) - 7 points max."""
        boy_sign_num = self.get_sign_number_from_nakshatra(boy_nakshatra)
        girl_sign_num = self.get_sign_number_from_nakshatra(girl_nakshatra)

        # Count signs from girl to boy
        diff = (boy_sign_num - girl_sign_num) % 12

        # Unfavorable positions: 2-12, 6-8, 9-5
        unfavorable_diffs = [2, 5, 6, 8, 9]

        if diff in unfavorable_diffs or (12 - diff) in unfavorable_diffs:
            points = 0
        else:
            points = 7

        return {
            "name": "Bhakoot",
            "max_points": 7,
            "obtained_points": points,
            "boy_sign_number": boy_sign_num,
            "girl_sign_number": girl_sign_num,
            "sign_difference": diff,
            "compatible": points > 0,
            "description": "Financial prosperity and family welfare"
        }

    def calculate_nadi(self, boy_nakshatra: str, girl_nakshatra: str) -> Dict[str, Any]:
        """Calculate Nadi (health compatibility) - 8 points max."""
        boy_nadi = self.NADI_MAP.get(boy_nakshatra)
        girl_nadi = self.NADI_MAP.get(girl_nakshatra)

        # Same nadi is inauspicious (affects progeny health)
        points = 0 if boy_nadi == girl_nadi else 8

        return {
            "name": "Nadi",
            "max_points": 8,
            "obtained_points": points,
            "boy_value": boy_nadi,
            "girl_value": girl_nadi,
            "compatible": points > 0,
            "description": "Health and progeny compatibility"
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def get_sign_from_nakshatra(self, nakshatra: str) -> str:
        """Get zodiac sign from nakshatra."""
        nakshatra_index = self.NAKSHATRAS.index(nakshatra)
        sign_num = (nakshatra_index * 13.333) // 30
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        return signs[int(sign_num)]

    def get_sign_number_from_nakshatra(self, nakshatra: str) -> int:
        """Get sign number (1-12) from nakshatra."""
        nakshatra_index = self.NAKSHATRAS.index(nakshatra)
        return int((nakshatra_index * 13.333) // 30) + 1

    def get_sign_lord(self, sign: str) -> str:
        """Get ruling planet of a sign."""
        lords = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }
        return lords.get(sign, "Unknown")

    def get_planetary_relationship(self, planet1: str, planet2: str) -> str:
        """Get relationship between two planets."""
        friendships = {
            "Sun": {"friend": ["Moon", "Mars", "Jupiter"], "enemy": ["Venus", "Saturn"]},
            "Moon": {"friend": ["Sun", "Mercury"], "enemy": ["None"]},
            "Mars": {"friend": ["Sun", "Moon", "Jupiter"], "enemy": ["Mercury"]},
            "Mercury": {"friend": ["Sun", "Venus"], "enemy": ["Moon"]},
            "Jupiter": {"friend": ["Sun", "Moon", "Mars"], "enemy": ["Mercury", "Venus"]},
            "Venus": {"friend": ["Mercury", "Saturn"], "enemy": ["Sun", "Moon"]},
            "Saturn": {"friend": ["Mercury", "Venus"], "enemy": ["Sun", "Moon", "Mars"]}
        }

        if planet1 == planet2:
            return "friend"

        planet1_friends = friendships.get(planet1, {}).get("friend", [])
        planet1_enemies = friendships.get(planet1, {}).get("enemy", [])

        if planet2 in planet1_friends:
            return "friend"
        elif planet2 in planet1_enemies:
            return "enemy"
        else:
            return "neutral"

    # =========================================================================
    # MANGLIK DOSHA ANALYSIS
    # =========================================================================

    def calculate_manglik_dosha(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Manglik (Kuja) Dosha.

        Manglik dosha occurs when Mars is in houses 1, 4, 7, 8, or 12.
        """
        planets = chart.get("planets", {})
        mars_data = planets.get("Mars", {})
        mars_house = mars_data.get("house")

        manglik_houses = [1, 4, 7, 8, 12]
        is_manglik = mars_house in manglik_houses

        # Calculate severity
        severity = "none"
        if is_manglik:
            if mars_house in [1, 7, 8]:
                severity = "high"
            elif mars_house in [4, 12]:
                severity = "medium"

        # Check cancellations
        cancellations = self.check_manglik_cancellations(chart, mars_house)

        return {
            "is_manglik": is_manglik,
            "mars_house": mars_house,
            "severity": severity,
            "cancellations": cancellations,
            "is_cancelled": len(cancellations) > 0,
            "description": self.get_manglik_description(is_manglik, severity, cancellations)
        }

    def check_manglik_cancellations(self, chart: Dict[str, Any], mars_house: int) -> List[str]:
        """Check for Manglik dosha cancellations."""
        cancellations = []
        planets = chart.get("planets", {})

        # Jupiter aspect on Mars cancels
        jupiter = planets.get("Jupiter", {})
        if self.planets_aspect_each_other(planets.get("Mars", {}), jupiter):
            cancellations.append("Jupiter aspects Mars")

        # Mars in own sign or exaltation
        mars = planets.get("Mars", {})
        mars_sign = mars.get("sign")
        if mars_sign in ["Aries", "Scorpio"]:  # Own signs
            cancellations.append("Mars in own sign")
        elif mars_sign == "Capricorn":  # Exaltation
            cancellations.append("Mars exalted")

        # Both partners Manglik cancels
        # (This will be checked in the main compatibility function)

        return cancellations

    def planets_aspect_each_other(self, planet1: Dict[str, Any], planet2: Dict[str, Any]) -> bool:
        """Check if two planets aspect each other (simple 7th house aspect)."""
        house1 = planet1.get("house", 0)
        house2 = planet2.get("house", 0)

        if house1 == 0 or house2 == 0:
            return False

        # Check 7th house aspect
        return (house2 == (house1 + 6) % 12 + 1) or (house1 == (house2 + 6) % 12 + 1)

    def get_manglik_description(self, is_manglik: bool, severity: str, cancellations: List[str]) -> str:
        """Get description of Manglik status."""
        if not is_manglik:
            return "No Manglik Dosha present"

        if cancellations:
            return f"{severity.title()} Manglik Dosha present but cancelled by: {', '.join(cancellations)}"

        return f"{severity.title()} Manglik Dosha present"

    # =========================================================================
    # MAIN COMPATIBILITY ANALYSIS
    # =========================================================================

    def analyze_compatibility(self, boy_chart: Dict[str, Any], girl_chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete compatibility analysis.

        Args:
            boy_chart: Boy's birth chart data
            girl_chart: Girl's birth chart data

        Returns:
            Complete compatibility report
        """
        # Get Moon positions
        boy_moon = boy_chart.get("planets", {}).get("Moon", {}).get("longitude", 0)
        girl_moon = girl_chart.get("planets", {}).get("Moon", {}).get("longitude", 0)

        # Calculate nakshatras
        boy_nakshatra_data = self.get_nakshatra(boy_moon)
        girl_nakshatra_data = self.get_nakshatra(girl_moon)

        boy_nakshatra = boy_nakshatra_data["name"]
        girl_nakshatra = girl_nakshatra_data["name"]
        boy_nakshatra_num = boy_nakshatra_data["number"]
        girl_nakshatra_num = girl_nakshatra_data["number"]

        # Calculate all Ashtakoot factors
        varna = self.calculate_varna(boy_nakshatra, girl_nakshatra)
        vashya = self.calculate_vashya(boy_nakshatra, girl_nakshatra)
        tara = self.calculate_tara(boy_nakshatra_num, girl_nakshatra_num)
        yoni = self.calculate_yoni(boy_nakshatra, girl_nakshatra)
        graha_maitri = self.calculate_graha_maitri(boy_chart, girl_chart, boy_nakshatra, girl_nakshatra)
        gana = self.calculate_gana(boy_nakshatra, girl_nakshatra)
        bhakoot = self.calculate_bhakoot(boy_nakshatra, girl_nakshatra)
        nadi = self.calculate_nadi(boy_nakshatra, girl_nakshatra)

        # Calculate Manglik Dosha
        boy_manglik = self.calculate_manglik_dosha(boy_chart)
        girl_manglik = self.calculate_manglik_dosha(girl_chart)

        # Check if both Manglik (cancels the dosha)
        manglik_compatibility = {
            "boy_manglik": boy_manglik,
            "girl_manglik": girl_manglik,
            "compatible": (not boy_manglik["is_manglik"] and not girl_manglik["is_manglik"]) or
                         (boy_manglik["is_manglik"] and girl_manglik["is_manglik"]) or
                         boy_manglik["is_cancelled"] or girl_manglik["is_cancelled"],
            "note": "Both partners being Manglik cancels the dosha" if
                   (boy_manglik["is_manglik"] and girl_manglik["is_manglik"]) else ""
        }

        # Calculate total score
        guna_milan_factors = [varna, vashya, tara, yoni, graha_maitri, gana, bhakoot, nadi]
        total_points = sum(f["obtained_points"] for f in guna_milan_factors)
        max_points = 36

        # Determine compatibility level
        compatibility_level, recommendation = self.get_compatibility_rating(total_points, manglik_compatibility["compatible"])

        return {
            "boy_nakshatra": boy_nakshatra_data,
            "girl_nakshatra": girl_nakshatra_data,
            "guna_milan": {
                "total_points": total_points,
                "max_points": max_points,
                "percentage": round((total_points / max_points) * 100, 1),
                "factors": guna_milan_factors,
                "level": compatibility_level
            },
            "manglik_analysis": manglik_compatibility,
            "overall_compatibility": {
                "level": compatibility_level,
                "recommendation": recommendation,
                "summary": self.generate_summary(total_points, manglik_compatibility)
            }
        }

    def get_compatibility_rating(self, points: float, manglik_compatible: bool) -> Tuple[str, str]:
        """Get compatibility level and recommendation based on points."""
        if not manglik_compatible:
            return "poor", "Not recommended due to Manglik incompatibility"

        if points >= 28:
            return "excellent", "Highly compatible match - Excellent for marriage"
        elif points >= 24:
            return "very_good", "Very good compatibility - Recommended for marriage"
        elif points >= 18:
            return "good", "Good compatibility - Can proceed with proper understanding"
        elif points >= 12:
            return "average", "Average compatibility - Requires effort from both partners"
        else:
            return "poor", "Poor compatibility - Not recommended without remedies"

    def generate_summary(self, points: float, manglik_data: Dict[str, Any]) -> str:
        """Generate compatibility summary."""
        summary_parts = []

        # Guna Milan summary
        if points >= 28:
            summary_parts.append(f"Excellent Guna Milan score of {points}/36 indicates very high compatibility.")
        elif points >= 18:
            summary_parts.append(f"Good Guna Milan score of {points}/36 indicates positive compatibility.")
        else:
            summary_parts.append(f"Guna Milan score of {points}/36 indicates challenges that need attention.")

        # Manglik summary
        if manglik_data["boy_manglik"]["is_manglik"] and manglik_data["girl_manglik"]["is_manglik"]:
            summary_parts.append("Both partners have Manglik Dosha which cancels the negative effects.")
        elif manglik_data["compatible"]:
            summary_parts.append("No Manglik Dosha issues present.")
        else:
            summary_parts.append("Manglik Dosha incompatibility needs remedial measures.")

        return " ".join(summary_parts)


# Singleton instance
compatibility_service = CompatibilityService()
