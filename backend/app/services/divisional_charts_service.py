"""
Divisional Charts (Shodashvarga) Calculation Service
Implements D2-D60 divisional charts as per classical Vedic astrology
"""

from typing import Dict, Any, List
from datetime import datetime, date, time


class DivisionalChartsService:
    """Calculate all 16 divisional charts (Shodashvarga)"""

    # Zodiac signs
    SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    # Planet dignities for Vimshopaka Bala calculation (1-indexed: 1=Aries, 12=Pisces)
    PLANET_RULERSHIPS = {
        "Sun": {"own": [5], "exalted": 1, "debilitated": 7, "moolatrikona": 5},  # Leo, Aries, Libra, Leo
        "Moon": {"own": [4], "exalted": 2, "debilitated": 8, "moolatrikona": 4},  # Cancer, Taurus, Scorpio, Cancer
        "Mars": {"own": [1, 8], "exalted": 10, "debilitated": 4, "moolatrikona": 1},  # Aries/Scorpio, Capricorn, Cancer, Aries
        "Mercury": {"own": [3, 6], "exalted": 6, "debilitated": 12, "moolatrikona": 6},  # Gemini/Virgo, Virgo, Pisces, Virgo
        "Jupiter": {"own": [9, 12], "exalted": 4, "debilitated": 10, "moolatrikona": 9},  # Sagittarius/Pisces, Cancer, Capricorn, Sagittarius
        "Venus": {"own": [2, 7], "exalted": 12, "debilitated": 6, "moolatrikona": 7},  # Taurus/Libra, Pisces, Virgo, Libra
        "Saturn": {"own": [10, 11], "exalted": 7, "debilitated": 1, "moolatrikona": 11},  # Capricorn/Aquarius, Libra, Aries, Aquarius
        "Rahu": {"own": [], "exalted": 2, "debilitated": 8, "moolatrikona": -1},  # Taurus, Scorpio
        "Ketu": {"own": [], "exalted": 8, "debilitated": 2, "moolatrikona": -1}  # Scorpio, Taurus
    }

    # Friendship table (planet-based, not sign-based)
    PLANET_FRIENDSHIPS = {
        "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "enemies": ["Venus", "Saturn"], "neutral": ["Mercury"]},
        "Moon": {"friends": ["Sun", "Mercury"], "enemies": [], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"]},
        "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "enemies": ["Mercury"], "neutral": ["Venus", "Saturn"]},
        "Mercury": {"friends": ["Sun", "Venus"], "enemies": ["Moon"], "neutral": ["Mars", "Jupiter", "Saturn"]},
        "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "enemies": ["Mercury", "Venus"], "neutral": ["Saturn"]},
        "Venus": {"friends": ["Mercury", "Saturn"], "enemies": ["Sun", "Moon"], "neutral": ["Mars", "Jupiter"]},
        "Saturn": {"friends": ["Mercury", "Venus"], "enemies": ["Sun", "Moon", "Mars"], "neutral": ["Jupiter"]},
        "Rahu": {"friends": ["Saturn", "Mercury", "Venus"], "enemies": ["Sun", "Moon", "Mars"], "neutral": ["Jupiter"]},
        "Ketu": {"friends": ["Mars", "Venus", "Saturn"], "enemies": ["Sun", "Moon"], "neutral": ["Mercury", "Jupiter"]}
    }

    # Vimshopaka Bala weights (in Shashtiamsa units, total = 20)
    VIMSHOPAKA_WEIGHTS = {
        "D1": 3.5,
        "D2": 1.0,
        "D3": 1.0,
        "D4": 0.5,
        "D7": 0.5,
        "D9": 3.5,
        "D10": 0.5,
        "D12": 0.5,
        "D16": 2.0,
        "D20": 0.5,
        "D24": 0.5,
        "D27": 0.5,
        "D30": 1.0,
        "D40": 0.5,
        "D45": 0.25,
        "D60": 4.0
    }

    # Sign lordships (1-indexed: 1=Aries, 12=Pisces)
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

    def get_planet_dignity(self, planet_name: str, sign_num: int) -> tuple[str, float]:
        """
        Determine planet's dignity in a sign

        Returns:
            (dignity_name, dignity_score_out_of_20)

        Dignity scores:
        - Exalted: 20 points
        - Moolatrikona: 18 points
        - Own sign: 15 points
        - Great friend: 12.5 points
        - Friend: 10 points
        - Neutral: 7.5 points
        - Enemy: 5 points
        - Great enemy: 2.5 points
        - Debilitated: 0 points
        """
        if planet_name not in self.PLANET_RULERSHIPS:
            return ("Neutral", 7.5)

        rulership = self.PLANET_RULERSHIPS[planet_name]

        # Check exaltation
        if rulership["exalted"] == sign_num:
            return ("Exalted", 20.0)

        # Check debilitation
        if rulership["debilitated"] == sign_num:
            return ("Debilitated", 0.0)

        # Check moolatrikona
        if rulership.get("moolatrikona", -1) == sign_num:
            return ("Moolatrikona", 18.0)

        # Check own sign
        if sign_num in rulership["own"]:
            return ("Own Sign", 15.0)

        # Check friendship with sign lord
        sign_lord = self.SIGN_LORDS.get(sign_num)
        if sign_lord and planet_name in self.PLANET_FRIENDSHIPS:
            friendships = self.PLANET_FRIENDSHIPS[planet_name]

            if sign_lord in friendships["friends"]:
                return ("Friend", 10.0)
            elif sign_lord in friendships["enemies"]:
                return ("Enemy", 5.0)
            else:
                return ("Neutral", 7.5)

        return ("Neutral", 7.5)

    def calculate_vimshopaka_bala(
        self,
        d1_planets: Dict[str, Any],
        divisional_charts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate Vimshopaka Bala (composite strength) for all planets

        Vimshopaka Bala = Weighted sum of dignity scores across all 16 vargas
        Total possible: 20 Shashtiamsa units

        Args:
            d1_planets: Planets from D1 chart
            divisional_charts: All divisional charts (D2-D60)

        Returns:
            Dictionary with planet strengths and classifications
        """
        planet_strengths = {}

        # Standard planet list (exclude nodes for some calculations)
        main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        all_planets = main_planets + ["Rahu", "Ketu"]

        for planet_name in all_planets:
            if planet_name not in d1_planets:
                continue

            total_score = 0.0
            varga_scores = {}

            # D1 (Rashi) chart
            d1_sign = d1_planets[planet_name]["sign_num"]
            dignity_name, dignity_score = self.get_planet_dignity(planet_name, d1_sign)
            varga_contribution = (dignity_score / 20.0) * self.VIMSHOPAKA_WEIGHTS["D1"]
            total_score += varga_contribution
            varga_scores["D1"] = {
                "dignity": dignity_name,
                "dignity_score": dignity_score,
                "weight": self.VIMSHOPAKA_WEIGHTS["D1"],
                "contribution": round(varga_contribution, 4)
            }

            # Divisional charts (D2-D60, excluding D9 which might not be in divisional_charts)
            for chart_name, chart_data in divisional_charts.items():
                if chart_name not in self.VIMSHOPAKA_WEIGHTS:
                    continue

                if planet_name not in chart_data.get("planets", {}):
                    continue

                div_sign = chart_data["planets"][planet_name]["sign_num"]
                dignity_name, dignity_score = self.get_planet_dignity(planet_name, div_sign)
                varga_contribution = (dignity_score / 20.0) * self.VIMSHOPAKA_WEIGHTS[chart_name]
                total_score += varga_contribution
                varga_scores[chart_name] = {
                    "dignity": dignity_name,
                    "dignity_score": dignity_score,
                    "weight": self.VIMSHOPAKA_WEIGHTS[chart_name],
                    "contribution": round(varga_contribution, 4)
                }

            # Classify strength (out of 20 Shashtiamsa units)
            if total_score >= 18:
                classification = "Parijatamsa"  # Excellent (18-20)
                quality = "Excellent"
            elif total_score >= 16:
                classification = "Uttamamsa"  # Very Good (16-18)
                quality = "Very Good"
            elif total_score >= 13:
                classification = "Gopuramsa"  # Good (13-16)
                quality = "Good"
            elif total_score >= 10:
                classification = "Simhasanamsa"  # Above Average (10-13)
                quality = "Above Average"
            elif total_score >= 6:
                classification = "Parvatamsa"  # Average (6-10)
                quality = "Average"
            elif total_score >= 3:
                classification = "Devalokamsa"  # Below Average (3-6)
                quality = "Below Average"
            else:
                classification = "Brahmalokamsa"  # Weak (0-3)
                quality = "Weak"

            planet_strengths[planet_name] = {
                "total_score": round(total_score, 4),
                "max_score": 20.0,
                "percentage": round((total_score / 20.0) * 100, 2),
                "classification": classification,
                "quality": quality,
                "varga_scores": varga_scores
            }

        # Summary statistics
        avg_strength = sum(p["total_score"] for p in planet_strengths.values()) / len(planet_strengths)
        strongest_planet = max(planet_strengths.items(), key=lambda x: x[1]["total_score"])
        weakest_planet = min(planet_strengths.items(), key=lambda x: x[1]["total_score"])

        return {
            "planets": planet_strengths,
            "summary": {
                "average_strength": round(avg_strength, 4),
                "strongest_planet": {
                    "name": strongest_planet[0],
                    "score": strongest_planet[1]["total_score"],
                    "quality": strongest_planet[1]["quality"]
                },
                "weakest_planet": {
                    "name": weakest_planet[0],
                    "score": weakest_planet[1]["total_score"],
                    "quality": weakest_planet[1]["quality"]
                },
                "calculation_note": "Vimshopaka Bala calculated using classical Parashara system (20 Shashtiamsa units)"
            }
        }

    def calculate_divisional_position(
        self,
        longitude: float,
        division: int,
        sign_num: int
    ) -> Dict[str, Any]:
        """
        Calculate divisional chart position using standard Vedic formula

        Args:
            longitude: Planet's longitude in D1 (0-360)
            division: Division number (2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60)
            sign_num: Rashi sign number (1-12, where 1=Aries, 12=Pisces)

        Returns:
            Dict with sign, sign_num, degree, longitude
        """
        # Convert to 0-indexed for calculations (1-12 → 0-11)
        sign_num_0 = sign_num - 1

        degree_in_sign = longitude % 30

        # Calculate which division within the sign
        div_per_sign = division
        div_size = 30 / div_per_sign
        division_num = int(degree_in_sign / div_size)

        # Calculate divisional sign based on formula
        # Formula depends on whether sign is odd/even (movable/fixed/dual)
        is_odd_sign = (sign_num_0 % 2 == 0)  # Aries (0), Gemini (2), Leo (4), etc. in 0-indexed

        if division == 2:  # Hora chart (D2)
            if is_odd_sign:
                # Odd signs: First half -> Leo (4), Second half -> Cancer (3)
                div_sign = 4 if division_num == 0 else 3
            else:
                # Even signs: First half -> Cancer (3), Second half -> Leo (4)
                div_sign = 3 if division_num == 0 else 4

        elif division == 3:  # Drekkana chart (D3)
            # Each sign divided into 3 parts (0°-10°, 10°-20°, 20°-30°)
            div_sign = (sign_num_0 + (division_num * 4)) % 12

        elif division == 4:  # Chaturthamsa chart (D4)
            # Each sign divided into 4 parts (7.5° each)
            div_sign = (sign_num_0 + (division_num * 3)) % 12

        elif division == 7:  # Saptamsa chart (D7)
            # Each sign divided into 7 parts
            if is_odd_sign:
                div_sign = (sign_num_0 + division_num) % 12
            else:
                div_sign = (sign_num_0 + 6 + division_num) % 12

        elif division == 9:  # Navamsa chart (D9) - Standard formula
            div_sign = ((sign_num_0 * 9) + division_num) % 12

        elif division == 10:  # Dashamsa chart (D10)
            # Each sign divided into 10 parts (3° each)
            if is_odd_sign:
                div_sign = (sign_num_0 + division_num) % 12
            else:
                div_sign = (sign_num_0 + 8 + division_num) % 12

        elif division == 12:  # Dwadashamsa chart (D12)
            # Each sign divided into 12 parts (2.5° each)
            div_sign = (sign_num_0 + division_num) % 12

        elif division == 16:  # Shodashamsa chart (D16)
            # Each sign divided into 16 parts
            if is_odd_sign:
                div_sign = (0 + division_num) % 12  # Start from Aries
            else:
                div_sign = (6 + division_num) % 12  # Start from Libra

        elif division == 20:  # Vimshamsa chart (D20)
            # Each sign divided into 20 parts (1.5° each)
            if is_odd_sign:
                div_sign = (0 + division_num) % 12  # Start from Aries
            else:
                div_sign = (8 + division_num) % 12  # Start from Sagittarius

        elif division == 24:  # Chaturvimshamsa chart (D24)
            # Each sign divided into 24 parts (1.25° each)
            if is_odd_sign:
                div_sign = (4 + division_num) % 12  # Start from Leo
            else:
                div_sign = (3 + division_num) % 12  # Start from Cancer

        elif division == 27:  # Nakshatramsa/Bhamsa chart (D27)
            # Each sign divided into 27 parts
            div_sign = (sign_num_0 * 9 + int(division_num / 3)) % 12

        elif division == 30:  # Trimshamsa chart (D30)
            # Complex distribution based on odd/even signs
            if is_odd_sign:
                ranges = [(5, 0), (5, 10), (8, 5), (7, 8), (5, 6)]  # (degrees, lord)
            else:
                ranges = [(5, 5), (7, 4), (8, 3), (5, 2), (5, 1)]

            cumulative = 0
            for deg_range, lord_offset in ranges:
                if degree_in_sign < cumulative + deg_range:
                    div_sign = (sign_num_0 + lord_offset) % 12
                    break
                cumulative += deg_range
            else:
                div_sign = sign_num_0

        elif division == 40:  # Khavedamsa chart (D40)
            # Each sign divided into 40 parts (0.75° each)
            if is_odd_sign:
                div_sign = (0 + division_num) % 12  # Start from Aries
            else:
                div_sign = (6 + division_num) % 12  # Start from Libra

        elif division == 45:  # Akshavedamsa chart (D45)
            # Each sign divided into 45 parts
            if is_odd_sign:
                div_sign = (0 + division_num) % 12
            else:
                div_sign = (6 + division_num) % 12

        elif division == 60:  # Shashtiamsa chart (D60)
            # Each sign divided into 60 parts (0.5° each)
            div_sign = (sign_num_0 * 5 + int(division_num / 12)) % 12

        else:
            # Default formula for other divisions
            div_sign = (sign_num_0 + division_num) % 12

        # Calculate degree within divisional sign
        div_degree = (degree_in_sign % div_size) * (30 / div_size)
        div_longitude = (div_sign * 30) + div_degree

        return {
            "sign": self.SIGNS[div_sign],
            "sign_num": div_sign + 1,  # Convert back to 1-indexed (0-11 → 1-12)
            "degree": round(div_degree, 6),
            "longitude": round(div_longitude, 6),
            "division_number": division_num + 1
        }

    def calculate_divisional_chart(
        self,
        d1_planets: Dict[str, Any],
        d1_ascendant: Dict[str, Any],
        division: int,
        chart_name: str,
        purpose: str
    ) -> Dict[str, Any]:
        """
        Calculate a specific divisional chart from D1 positions

        Args:
            d1_planets: Planet positions from D1 (Rashi) chart
            d1_ascendant: Ascendant from D1 chart
            division: Division number (2, 3, 4, etc.)
            chart_name: Name of the chart (e.g., "D2", "D7")
            purpose: Purpose of the chart (e.g., "Wealth", "Children")

        Returns:
            Complete divisional chart data
        """
        # Calculate divisional ascendant
        asc_div_pos = self.calculate_divisional_position(
            d1_ascendant["longitude"],
            division,
            d1_ascendant["sign_num"]
        )

        # Calculate divisional positions for all planets
        div_planets = {}
        for planet_name, planet_data in d1_planets.items():
            div_pos = self.calculate_divisional_position(
                planet_data["longitude"],
                division,
                planet_data["sign_num"]
            )

            # Calculate house in divisional chart
            div_house = ((div_pos["sign_num"] - asc_div_pos["sign_num"]) % 12) + 1

            div_planets[planet_name] = {
                **div_pos,
                "house": div_house,
                "retrograde": planet_data.get("retrograde", False),
                "d1_sign": planet_data["sign"],
                "d1_house": planet_data["house"]
            }

        # Generate houses for divisional chart
        div_houses = []
        for i in range(12):
            house_sign = (asc_div_pos["sign_num"] + i) % 12
            div_houses.append({
                "house_num": i + 1,
                "sign": self.SIGNS[house_sign],
                "sign_num": house_sign,
                "start_degree": 0.0,
                "end_degree": 30.0
            })

        return {
            "chart_type": chart_name,
            "division": division,
            "purpose": purpose,
            "ascendant": {
                **asc_div_pos,
                "house": 1
            },
            "planets": div_planets,
            "houses": div_houses,
            "calculation_method": f"Standard Vedic {chart_name} formula"
        }

    def calculate_all_divisional_charts(
        self,
        d1_planets: Dict[str, Any],
        d1_ascendant: Dict[str, Any],
        priority: str = "high"
    ) -> Dict[str, Any]:
        """
        Calculate all divisional charts based on priority level

        Args:
            d1_planets: Planets from D1 chart
            d1_ascendant: Ascendant from D1 chart
            priority: "high" (6 charts), "medium" (10 charts), "all" (16 charts)

        Returns:
            Dictionary of all calculated divisional charts
        """
        # Define divisions with their purposes
        all_divisions = {
            # High Priority (Shodashvarga - most important)
            "D2": (2, "Hora", "Wealth and prosperity"),
            "D4": (4, "Chaturthamsa", "Property, assets, and fortune"),
            "D7": (7, "Saptamsa", "Children and progeny"),
            "D9": (9, "Navamsa", "Marriage, dharma, and spiritual strength"),
            "D10": (10, "Dashamsa", "Career, profession, and honors"),
            "D24": (24, "Chaturvimshamsa", "Education and learning"),

            # Medium Priority
            "D3": (3, "Drekkana", "Siblings, courage, and initiatives"),
            "D12": (12, "Dwadashamsa", "Parents and ancestry"),
            "D16": (16, "Shodashamsa", "Vehicles, comforts, and happiness"),
            "D20": (20, "Vimshamsa", "Spiritual pursuits and worship"),

            # Lower Priority (Advanced analysis)
            "D27": (27, "Nakshatramsa", "Strengths and weaknesses"),
            "D30": (30, "Trimshamsa", "Evils, misfortunes, and obstacles"),
            "D40": (40, "Khavedamsa", "Auspicious and inauspicious effects"),
            "D45": (45, "Akshavedamsa", "Character and general well-being"),
            "D60": (60, "Shashtiamsa", "Past life karma and overall effects")
        }

        # Select divisions based on priority
        if priority == "high":
            selected = ["D2", "D4", "D7", "D9", "D10", "D24"]
        elif priority == "medium":
            selected = ["D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24"]
        else:  # "all"
            selected = list(all_divisions.keys())

        divisional_charts = {}

        for chart_name in selected:
            if chart_name in all_divisions:
                division, name, purpose = all_divisions[chart_name]

                # Skip D9 as it's calculated separately with more detail
                if chart_name == "D9":
                    continue

                divisional_charts[chart_name] = self.calculate_divisional_chart(
                    d1_planets,
                    d1_ascendant,
                    division,
                    chart_name,
                    purpose
                )

        return divisional_charts

    def detect_divisional_yogas(
        self,
        chart_name: str,
        chart_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect yogas in a specific divisional chart

        Different divisional charts emphasize different life areas:
        - D2 (Hora): Wealth yogas
        - D4 (Chaturthamsa): Property yogas
        - D7 (Saptamsa): Children yogas
        - D9 (Navamsa): Marriage and spiritual yogas
        - D10 (Dashamsa): Career and status yogas
        - D12 (Dwadashamsa): Parents and ancestry yogas

        Args:
            chart_name: Chart name (D2, D3, D4, etc.)
            chart_data: Divisional chart data with planets and ascendant

        Returns:
            List of detected yogas with strength and relevance
        """
        yogas = []
        planets = chart_data.get("planets", {})
        ascendant = chart_data.get("ascendant", {})

        if not planets or not ascendant:
            return yogas

        asc_sign = ascendant.get("sign_num", 0)

        # Detect Kendra (angular) houses (1, 4, 7, 10)
        kendras = [1, 4, 7, 10]
        # Detect Trikona (trinal) houses (1, 5, 9)
        trikonas = [1, 5, 9]

        # Check for Raj Yoga (Kendra-Trikona combinations)
        # Especially important in D1, D9, D10
        if chart_name in ["D1", "D9", "D10"]:
            for planet_name, planet_data in planets.items():
                if planet_name in ["Rahu", "Ketu"]:
                    continue

                planet_house = planet_data.get("house", 0)

                # Check if planet is lord of kendra and in trikona (or vice versa)
                if planet_house in kendras or planet_house in trikonas:
                    # Simple Raj Yoga detection
                    dignity = self._get_planet_dignity_simple(planet_name, planet_data.get("sign_num", 0))

                    if dignity in ["Exalted", "Own Sign", "Friend"]:
                        yoga = {
                            "name": f"Raj Yoga in {chart_name}",
                            "category": "Power & Status",
                            "planet": planet_name,
                            "house": planet_house,
                            "sign": planet_data.get("sign", ""),
                            "dignity": dignity,
                            "description": f"{planet_name} forms Raj Yoga in {chart_name} by occupying house {planet_house}",
                            "strength": "Strong" if dignity == "Exalted" else "Medium",
                            "effects": self._get_raj_yoga_effects(chart_name, planet_name)
                        }
                        yogas.append(yoga)

        # Dhana Yoga (wealth combinations) - especially important in D2, D4
        if chart_name in ["D2", "D4", "D10"]:
            dhana_houses = [2, 5, 9, 11]  # Wealth houses

            for planet_name, planet_data in planets.items():
                if planet_name in ["Rahu", "Ketu"]:
                    continue

                planet_house = planet_data.get("house", 0)

                if planet_house in dhana_houses:
                    dignity = self._get_planet_dignity_simple(planet_name, planet_data.get("sign_num", 0))

                    if dignity in ["Exalted", "Own Sign"]:
                        yoga = {
                            "name": f"Dhana Yoga in {chart_name}",
                            "category": "Wealth",
                            "planet": planet_name,
                            "house": planet_house,
                            "sign": planet_data.get("sign", ""),
                            "dignity": dignity,
                            "description": f"{planet_name} forms Dhana Yoga in {chart_name} in house {planet_house}",
                            "strength": "Strong" if dignity == "Exalted" else "Medium",
                            "effects": self._get_dhana_yoga_effects(chart_name, planet_name)
                        }
                        yogas.append(yoga)

        # Jupiter-Venus combinations (especially in D7 for children, D9 for marriage)
        if chart_name in ["D7", "D9"]:
            jupiter = planets.get("Jupiter", {})
            venus = planets.get("Venus", {})

            if jupiter and venus:
                jup_house = jupiter.get("house", 0)
                ven_house = venus.get("house", 0)

                # Check if they're in mutual kendras or same house
                if abs(jup_house - ven_house) in [0, 3, 6, 9]:
                    yoga = {
                        "name": f"Jupiter-Venus Yoga in {chart_name}",
                        "category": "Benefic Combination",
                        "planets": ["Jupiter", "Venus"],
                        "houses": [jup_house, ven_house],
                        "description": f"Jupiter and Venus form beneficial combination in {chart_name}",
                        "strength": "Medium",
                        "effects": self._get_jupiter_venus_effects(chart_name)
                    }
                    yogas.append(yoga)

        return yogas

    def _get_planet_dignity_simple(self, planet_name: str, sign_num: int) -> str:
        """Simple dignity check for yoga detection"""
        if planet_name not in self.PLANET_RULERSHIPS:
            return "Neutral"

        rulership = self.PLANET_RULERSHIPS[planet_name]

        if rulership["exalted"] == sign_num:
            return "Exalted"
        if rulership["debilitated"] == sign_num:
            return "Debilitated"
        if sign_num in rulership["own"]:
            return "Own Sign"

        sign_lord = self.SIGN_LORDS.get(sign_num)
        if sign_lord and planet_name in self.PLANET_FRIENDSHIPS:
            friendships = self.PLANET_FRIENDSHIPS[planet_name]
            if sign_lord in friendships["friends"]:
                return "Friend"
            elif sign_lord in friendships["enemies"]:
                return "Enemy"

        return "Neutral"

    def _get_raj_yoga_effects(self, chart_name: str, planet: str) -> str:
        """Get effects description for Raj Yoga in specific charts"""
        effects = {
            "D1": f"General power, authority, and recognition in life through {planet}",
            "D9": f"Dharmic strength, spiritual authority, and marital harmony through {planet}",
            "D10": f"Professional success, career advancement, and public recognition through {planet}"
        }
        return effects.get(chart_name, f"Positive effects in {chart_name} matters")

    def _get_dhana_yoga_effects(self, chart_name: str, planet: str) -> str:
        """Get effects description for Dhana Yoga in specific charts"""
        effects = {
            "D2": f"Wealth accumulation and financial prosperity through {planet}",
            "D4": f"Property, assets, and material comforts through {planet}",
            "D10": f"Professional income and career-based wealth through {planet}"
        }
        return effects.get(chart_name, f"Financial benefits in {chart_name} matters")

    def _get_jupiter_venus_effects(self, chart_name: str) -> str:
        """Get effects for Jupiter-Venus combination"""
        effects = {
            "D7": "Beneficial for children, happiness from progeny, and family growth",
            "D9": "Harmonious marriage, spiritual partnership, and domestic happiness"
        }
        return effects.get(chart_name, "General benefic effects")


# Singleton instance
divisional_charts_service = DivisionalChartsService()
