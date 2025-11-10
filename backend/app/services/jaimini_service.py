"""
Jaimini Astrology Service

Implements the Jaimini system of Vedic astrology, which differs from Parashara system.
Jaimini uses Chara (movable) karakas, Arudha padas, and unique aspects/yogas.

Key Concepts:
- Charakarakas: 7 temporal significators based on planetary degrees
- Arudha Padas: Projections of houses showing material manifestations
- Argala: Planetary interventions/obstructions
- Jaimini Aspects: Sign-based, not degree-based
- Rashi Drishti: Movable → Fixed, Fixed → Movable, Dual → Dual

References:
- Jaimini Sutras (Maharishi Jaimini)
- Brihat Parashara Hora Shastra (Jaimini chapters)
"""

from typing import Dict, List, Optional, Any, Tuple


class JaiminiService:
    """Service for Jaimini astrology calculations"""

    def __init__(self):
        """Initialize Jaimini service"""
        pass

    def calculate_charakarakas(self, planets: Dict[str, Any]) -> Dict[str, str]:
        """
        Calculate 7 Chara Karakas based on planetary longitude

        Karakas are assigned based on degrees within signs (0-30°).
        The planet with highest degree becomes Atmakaraka, next becomes Amatyakaraka, etc.

        Karakas (Highest to Lowest degree):
        1. Atmakaraka (AK) - Self, Soul
        2. Amatyakaraka (AmK) - Career, Minister
        3. Bhratrikaraka (BK) - Siblings
        4. Matrikaraka (MK) - Mother
        5. Putrakaraka (PK) - Children
        6. Gnatikaraka (GK) - Relatives, Obstacles
        7. Darakaraka (DK) - Spouse

        Note: Rahu is excluded from karaka calculations (some traditions include it)

        Args:
            planets: Dictionary with planet positions including degrees

        Returns:
            Dictionary mapping karaka names to planet names
            Example: {"AK": "Mars", "AmK": "Jupiter", "BK": "Sun", ...}
        """
        # Karaka names in order (highest to lowest)
        karaka_names = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]

        # Planets to consider (exclude Rahu/Ketu in standard Jaimini)
        # Some traditions include Rahu as 8th karaka
        main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        # Extract degrees for each planet
        planet_degrees = {}

        for planet in main_planets:
            if planet in planets:
                planet_data = planets[planet]

                # Get degree within sign (0-30°)
                # Different possible data structures:
                # 1. degree field directly
                # 2. Calculate from longitude
                # 3. degree_in_sign field

                degree = 0.0

                if "degree" in planet_data:
                    # Degree within sign (0-30)
                    degree = float(planet_data["degree"])
                elif "longitude" in planet_data:
                    # Absolute longitude (0-360)
                    # Extract degree within sign
                    longitude = float(planet_data["longitude"])
                    degree = longitude % 30.0
                elif "degree_in_sign" in planet_data:
                    degree = float(planet_data["degree_in_sign"])

                # Store planet with its degree
                if degree >= 0:
                    planet_degrees[planet] = degree

        # Sort planets by degree (descending - highest first)
        sorted_planets = sorted(planet_degrees.items(), key=lambda x: x[1], reverse=True)

        # Assign karakas
        karakas = {}

        for i, (planet, degree) in enumerate(sorted_planets[:7]):
            if i < len(karaka_names):
                karaka_names_full = {
                    "AK": "Atmakaraka",
                    "AmK": "Amatyakaraka",
                    "BK": "Bhratrikaraka",
                    "MK": "Matrikaraka",
                    "PK": "Putrakaraka",
                    "GK": "Gnatikaraka",
                    "DK": "Darakaraka"
                }
                karakas[karaka_names[i]] = planet
                karakas[karaka_names_full[karaka_names[i]]] = planet

        return karakas

    def calculate_arudha_lagna(self, planets: Dict[str, Any], asc_sign: int) -> int:
        """
        Calculate Arudha Lagna (AL) - Material projection of Ascendant

        Formula:
        1. Find Lagna lord's sign position
        2. Count distance from Lagna to Lagna lord
        3. Count same distance from Lagna lord's position
        4. Apply special rules:
           - If AL falls in 1st or 7th from Lagna, count from 4th/10th instead

        Args:
            planets: Planet positions
            asc_sign: Ascendant sign (0-indexed: 0=Aries, 11=Pisces)

        Returns:
            Arudha Lagna house number (1-12)
        """
        # Get Lagna lord
        lagna_lord = self._get_sign_lord(asc_sign)

        # Get Lagna lord's sign position
        if lagna_lord not in planets:
            return 1  # Default to 1st house if data unavailable

        lagna_lord_sign = planets[lagna_lord].get("sign_num", 0)
        if lagna_lord_sign == 0:
            return 1

        # Convert to 0-indexed
        if lagna_lord_sign > 0:
            lagna_lord_sign = lagna_lord_sign - 1

        # Count distance from Lagna to Lagna lord (in signs)
        distance = (lagna_lord_sign - asc_sign) % 12

        # Count same distance from Lagna lord
        arudha_sign = (lagna_lord_sign + distance) % 12

        # Apply special rules
        arudha_distance_from_lagna = (arudha_sign - asc_sign) % 12

        # If AL is in 1st or 7th from Lagna, apply correction
        if arudha_distance_from_lagna == 0:  # Same as Lagna
            # Count 10 houses from Lagna lord instead (4th from 7th position)
            arudha_sign = (lagna_lord_sign + 10) % 12
        elif arudha_distance_from_lagna == 6:  # 7th from Lagna
            # Count 4 houses from Lagna lord instead
            arudha_sign = (lagna_lord_sign + 4) % 12

        # Convert to house number (1-indexed)
        arudha_house = ((arudha_sign - asc_sign) % 12) + 1

        return arudha_house

    def calculate_arudha_padas(self, planets: Dict[str, Any], asc_sign: int) -> Dict[str, int]:
        """
        Calculate all 12 Arudha Padas (A1-A12)

        Each house has an Arudha pada showing its material manifestation.
        A1 = Arudha Lagna (AL) - Most important

        Args:
            planets: Planet positions
            asc_sign: Ascendant sign (0-indexed)

        Returns:
            Dictionary mapping pada names to house numbers
            Example: {"AL": 5, "A2": 7, "A3": 1, ...}
        """
        arudha_padas = {}

        # A1 = Arudha Lagna (special calculation)
        arudha_padas["AL"] = self.calculate_arudha_lagna(planets, asc_sign)
        arudha_padas["A1"] = arudha_padas["AL"]

        # Calculate A2 through A12
        for house_num in range(2, 13):
            arudha_pada = self._calculate_house_arudha(planets, asc_sign, house_num)
            arudha_padas[f"A{house_num}"] = arudha_pada

        return arudha_padas

    def _calculate_house_arudha(self, planets: Dict[str, Any], asc_sign: int, house_num: int) -> int:
        """
        Calculate Arudha Pada for a specific house

        Same formula as Arudha Lagna but for any house

        Args:
            planets: Planet positions
            asc_sign: Ascendant sign (0-indexed)
            house_num: House number (1-12)

        Returns:
            Arudha Pada house number (1-12)
        """
        # Get house sign
        house_sign = (asc_sign + house_num - 1) % 12

        # Get house lord
        house_lord = self._get_sign_lord(house_sign)

        # Get house lord's sign position
        if house_lord not in planets:
            return house_num  # Default to original house

        house_lord_sign = planets[house_lord].get("sign_num", 0)
        if house_lord_sign == 0:
            return house_num

        # Convert to 0-indexed
        if house_lord_sign > 0:
            house_lord_sign = house_lord_sign - 1

        # Count distance from house to house lord
        distance = (house_lord_sign - house_sign) % 12

        # Count same distance from house lord
        arudha_sign = (house_lord_sign + distance) % 12

        # Apply special rules
        arudha_distance_from_house = (arudha_sign - house_sign) % 12

        # If arudha is in 1st or 7th from original house, apply correction
        if arudha_distance_from_house == 0:
            arudha_sign = (house_lord_sign + 10) % 12
        elif arudha_distance_from_house == 6:
            arudha_sign = (house_lord_sign + 4) % 12

        # Convert to house number relative to Lagna
        arudha_house = ((arudha_sign - asc_sign) % 12) + 1

        return arudha_house

    def calculate_argala(self, house: int, planets: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Calculate Argala (interventions) on a house

        Argala represents planetary influences that help or obstruct a house.

        Benefic Argala (Help):
        - 2nd house from reference
        - 4th house from reference
        - 11th house from reference

        Malefic Argala (Obstruction):
        - 3rd house from reference
        - 10th house from reference

        Virodha Argala (Counter-obstruction):
        - 12th house (blocks 2nd house argala)
        - 10th house (blocks 4th house argala)
        - 3rd house (blocks 11th house argala)
        - 9th house (blocks 3rd house argala)
        - 4th house (blocks 10th house argala)

        Args:
            house: Reference house (1-12)
            planets: Planet positions

        Returns:
            Dictionary with argala planets:
            {
                "shubha_argala": ["Jupiter", "Venus"],  # Benefic interventions
                "papa_argala": ["Mars", "Saturn"],      # Malefic interventions
                "virodha_argala": ["Moon"]              # Obstructions
            }
        """
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
        malefics = ["Mars", "Saturn", "Rahu", "Ketu"]

        # Calculate argala houses
        benefic_argala_houses = [
            (house + 1) % 12 or 12,   # 2nd house
            (house + 3) % 12 or 12,   # 4th house
            (house + 10) % 12 or 12   # 11th house
        ]

        malefic_argala_houses = [
            (house + 2) % 12 or 12,   # 3rd house
            (house + 9) % 12 or 12    # 10th house
        ]

        virodha_houses = [
            (house + 11) % 12 or 12,  # 12th house (blocks 2nd)
            (house + 9) % 12 or 12,   # 10th house (blocks 4th)
            (house + 2) % 12 or 12,   # 3rd house (blocks 11th)
            (house + 8) % 12 or 12,   # 9th house (blocks 3rd)
            (house + 3) % 12 or 12    # 4th house (blocks 10th)
        ]

        # Find planets in argala positions
        shubha_argala = []
        papa_argala = []
        virodha_argala = []

        for planet, data in planets.items():
            if planet in ["Ascendant", "MC"]:
                continue

            planet_house = data.get("house", 0)

            # Check benefic argala
            if planet_house in benefic_argala_houses:
                if planet in benefics:
                    shubha_argala.append(planet)

            # Check malefic argala
            if planet_house in malefic_argala_houses:
                if planet in malefics:
                    papa_argala.append(planet)

            # Check virodha argala
            if planet_house in virodha_houses:
                virodha_argala.append(planet)

        return {
            "shubha_argala": shubha_argala,
            "papa_argala": papa_argala,
            "virodha_argala": virodha_argala
        }

    def calculate_jaimini_aspects(self, sign: int) -> List[int]:
        """
        Calculate Jaimini (Rashi) aspects - sign-based, not planetary

        Jaimini aspects are different from Parashara:
        - Movable signs (Aries, Cancer, Libra, Capricorn) aspect fixed signs EXCEPT the one adjacent
        - Fixed signs (Taurus, Leo, Scorpio, Aquarius) aspect movable signs EXCEPT the one adjacent
        - Dual signs (Gemini, Virgo, Sagittarius, Pisces) aspect other dual signs

        Args:
            sign: Sign number (0-indexed: 0=Aries, 11=Pisces)

        Returns:
            List of aspected sign numbers
        """
        # Sign classifications
        movable_signs = [0, 3, 6, 9]      # Aries, Cancer, Libra, Capricorn
        fixed_signs = [1, 4, 7, 10]       # Taurus, Leo, Scorpio, Aquarius
        dual_signs = [2, 5, 8, 11]        # Gemini, Virgo, Sagittarius, Pisces

        aspected_signs = []

        if sign in movable_signs:
            # Aspect all fixed signs except adjacent
            for fixed_sign in fixed_signs:
                distance = (fixed_sign - sign) % 12
                if distance != 1 and distance != 11:  # Not adjacent
                    aspected_signs.append(fixed_sign)

        elif sign in fixed_signs:
            # Aspect all movable signs except adjacent
            for movable_sign in movable_signs:
                distance = (movable_sign - sign) % 12
                if distance != 1 and distance != 11:  # Not adjacent
                    aspected_signs.append(movable_sign)

        elif sign in dual_signs:
            # Aspect other dual signs
            for dual_sign in dual_signs:
                if dual_sign != sign:
                    aspected_signs.append(dual_sign)

        return aspected_signs

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

    def _get_ascendant_sign(self, planets: Dict[str, Any]) -> Optional[int]:
        """
        Extract ascendant sign from planet data

        Args:
            planets: Planet positions dictionary

        Returns:
            Ascendant sign number (0-indexed) or None
        """
        if "Ascendant" in planets:
            asc_data = planets["Ascendant"]
            if "sign_num" in asc_data:
                # Convert to 0-indexed if needed
                sign_num = asc_data["sign_num"]
                return (sign_num - 1) % 12 if sign_num > 0 else 0

        return None


# Create singleton instance
jaimini_service = JaiminiService()
