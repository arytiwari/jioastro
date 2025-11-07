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
            sign_num: Rashi sign number (0-11)

        Returns:
            Dict with sign, sign_num, degree, longitude
        """
        degree_in_sign = longitude % 30

        # Calculate which division within the sign
        div_per_sign = division
        div_size = 30 / div_per_sign
        division_num = int(degree_in_sign / div_size)

        # Calculate divisional sign based on formula
        # Formula depends on whether sign is odd/even (movable/fixed/dual)
        is_odd_sign = (sign_num % 2 == 0)  # Aries (0), Gemini (2), Leo (4), etc.

        if division == 2:  # Hora chart (D2)
            if is_odd_sign:
                # Odd signs: First half -> Leo (4), Second half -> Cancer (3)
                div_sign = 4 if division_num == 0 else 3
            else:
                # Even signs: First half -> Cancer (3), Second half -> Leo (4)
                div_sign = 3 if division_num == 0 else 4

        elif division == 3:  # Drekkana chart (D3)
            # Each sign divided into 3 parts (0°-10°, 10°-20°, 20°-30°)
            div_sign = (sign_num + (division_num * 4)) % 12

        elif division == 4:  # Chaturthamsa chart (D4)
            # Each sign divided into 4 parts (7.5° each)
            div_sign = (sign_num + (division_num * 3)) % 12

        elif division == 7:  # Saptamsa chart (D7)
            # Each sign divided into 7 parts
            if is_odd_sign:
                div_sign = (sign_num + division_num) % 12
            else:
                div_sign = (sign_num + 6 + division_num) % 12

        elif division == 9:  # Navamsa chart (D9) - Standard formula
            div_sign = ((sign_num * 9) + division_num) % 12

        elif division == 10:  # Dashamsa chart (D10)
            # Each sign divided into 10 parts (3° each)
            if is_odd_sign:
                div_sign = (sign_num + division_num) % 12
            else:
                div_sign = (sign_num + 8 + division_num) % 12

        elif division == 12:  # Dwadashamsa chart (D12)
            # Each sign divided into 12 parts (2.5° each)
            div_sign = (sign_num + division_num) % 12

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
            div_sign = (sign_num * 9 + int(division_num / 3)) % 12

        elif division == 30:  # Trimshamsa chart (D30)
            # Complex distribution based on odd/even signs
            if is_odd_sign:
                ranges = [(5, 0), (5, 10), (8, 5), (7, 8), (5, 6)]  # (degrees, lord)
            else:
                ranges = [(5, 5), (7, 4), (8, 3), (5, 2), (5, 1)]

            cumulative = 0
            for deg_range, lord_offset in ranges:
                if degree_in_sign < cumulative + deg_range:
                    div_sign = (sign_num + lord_offset) % 12
                    break
                cumulative += deg_range
            else:
                div_sign = sign_num

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
            div_sign = (sign_num * 5 + int(division_num / 12)) % 12

        else:
            # Default formula for other divisions
            div_sign = (sign_num + division_num) % 12

        # Calculate degree within divisional sign
        div_degree = (degree_in_sign % div_size) * (30 / div_size)
        div_longitude = (div_sign * 30) + div_degree

        return {
            "sign": self.SIGNS[div_sign],
            "sign_num": div_sign,
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


# Singleton instance
divisional_charts_service = DivisionalChartsService()
