"""
Shadbala Calculation Service
Six-fold planetary strength system in Vedic Astrology
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, time
import math


class ShadbalaService:
    """
    Calculates Shadbala (six-fold planetary strength)

    The six strengths (Balas):
    1. Sthana Bala - Positional strength
    2. Dig Bala - Directional strength
    3. Kala Bala - Temporal strength
    4. Chesta Bala - Motional strength
    5. Naisargika Bala - Natural strength
    6. Drik Bala - Aspectual strength

    Total Shadbala = Sum of all 6 balas (measured in Shashtiamsas - 1/60th of a rupa)
    """

    def __init__(self):
        """Initialize Shadbala service"""

        # Natural strengths (Naisargika Bala) in Shashtiamsas
        self.naisargika_bala = {
            "Sun": 60.0,
            "Moon": 51.43,
            "Mars": 17.14,
            "Mercury": 25.70,
            "Jupiter": 34.28,
            "Venus": 42.85,
            "Saturn": 8.57,
        }

        # Exaltation/debilitation points
        self.exaltation_points = {
            "Sun": {"sign": "Aries", "degree": 10},
            "Moon": {"sign": "Taurus", "degree": 3},
            "Mars": {"sign": "Capricorn", "degree": 28},
            "Mercury": {"sign": "Virgo", "degree": 15},
            "Jupiter": {"sign": "Cancer", "degree": 5},
            "Venus": {"sign": "Pisces", "degree": 27},
            "Saturn": {"sign": "Libra", "degree": 20},
        }

        self.debilitation_points = {
            "Sun": {"sign": "Libra", "degree": 10},
            "Moon": {"sign": "Scorpio", "degree": 3},
            "Mars": {"sign": "Cancer", "degree": 28},
            "Mercury": {"sign": "Pisces", "degree": 15},
            "Jupiter": {"sign": "Capricorn", "degree": 5},
            "Venus": {"sign": "Virgo", "degree": 27},
            "Saturn": {"sign": "Aries", "degree": 20},
        }

        # Own signs (Swakshetra)
        self.own_signs = {
            "Sun": ["Leo"],
            "Moon": ["Cancer"],
            "Mars": ["Aries", "Scorpio"],
            "Mercury": ["Gemini", "Virgo"],
            "Jupiter": ["Sagittarius", "Pisces"],
            "Venus": ["Taurus", "Libra"],
            "Saturn": ["Capricorn", "Aquarius"],
        }

        # Friendly signs
        self.friendly_signs = {
            "Sun": ["Aries", "Scorpio", "Sagittarius"],
            "Moon": ["Taurus", "Gemini"],
            "Mars": ["Leo", "Sagittarius", "Pisces"],
            "Mercury": ["Taurus", "Libra"],
            "Jupiter": ["Cancer", "Aries", "Leo"],
            "Venus": ["Gemini", "Virgo", "Capricorn", "Aquarius"],
            "Saturn": ["Taurus", "Libra", "Gemini", "Virgo"],
        }

        # Enemy signs
        self.enemy_signs = {
            "Sun": ["Libra", "Aquarius"],
            "Moon": ["Capricorn"],
            "Mars": ["Gemini", "Virgo"],
            "Mercury": ["Sagittarius", "Pisces"],
            "Jupiter": ["Gemini", "Virgo"],
            "Venus": ["Aries", "Scorpio"],
            "Saturn": ["Aries", "Leo", "Scorpio"],
        }

        # Directional strength (Dig Bala) - Best houses for each planet
        self.dig_bala_houses = {
            "Sun": 10,      # 10th house (South)
            "Moon": 4,      # 4th house (North)
            "Mars": 10,     # 10th house (South)
            "Mercury": 1,   # 1st house (East)
            "Jupiter": 1,   # 1st house (East)
            "Venus": 4,     # 4th house (North)
            "Saturn": 7,    # 7th house (West)
        }

        # Minimum required Shadbala (in Shashtiamsas)
        self.required_shadbala = {
            "Sun": 390,
            "Moon": 360,
            "Mars": 300,
            "Mercury": 420,
            "Jupiter": 390,
            "Venus": 330,
            "Saturn": 300,
        }

    def calculate_shadbala(
        self,
        chart_data: Dict[str, Any],
        birth_datetime: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate complete Shadbala for all planets

        Args:
            chart_data: Birth chart data from astrology service
            birth_datetime: Birth date and time (for Kala Bala)

        Returns:
            Dictionary with Shadbala values for each planet
        """
        print("🔢 Calculating Shadbala (6-fold planetary strength)...")

        planets = chart_data.get("planets", {})
        houses = chart_data.get("houses", [])
        ascendant = chart_data.get("ascendant", {})

        shadbala_results = {}

        # Calculate for each planet
        for planet, planet_data in planets.items():
            if planet in ["Rahu", "Ketu"]:
                # Rahu and Ketu don't have traditional Shadbala
                continue

            # Calculate all 6 balas
            sthana_bala = self._calculate_sthana_bala(planet, planet_data, chart_data)
            dig_bala = self._calculate_dig_bala(planet, planet_data, ascendant)
            kala_bala = self._calculate_kala_bala(planet, planet_data, birth_datetime)
            chesta_bala = self._calculate_chesta_bala(planet, planet_data)
            naisargika = self.naisargika_bala.get(planet, 0)
            drik_bala = self._calculate_drik_bala(planet, planet_data, planets)

            # Total Shadbala
            total_shadbala = (
                sthana_bala +
                dig_bala +
                kala_bala +
                chesta_bala +
                naisargika +
                drik_bala
            )

            # Required strength
            required = self.required_shadbala.get(planet, 300)
            percentage = (total_shadbala / required) * 100

            # Strength rating
            strength_rating = self._get_strength_rating(percentage)

            shadbala_results[planet] = {
                "total_shadbala": round(total_shadbala, 2),
                "required_shadbala": required,
                "percentage": round(percentage, 2),
                "strength_rating": strength_rating,
                "components": {
                    "sthana_bala": round(sthana_bala, 2),
                    "dig_bala": round(dig_bala, 2),
                    "kala_bala": round(kala_bala, 2),
                    "chesta_bala": round(chesta_bala, 2),
                    "naisargika_bala": round(naisargika, 2),
                    "drik_bala": round(drik_bala, 2),
                }
            }

        # Find strongest and weakest planets
        sorted_planets = sorted(
            shadbala_results.items(),
            key=lambda x: x[1]["percentage"],
            reverse=True
        )

        return {
            "shadbala_by_planet": shadbala_results,
            "strongest_planet": {
                "planet": sorted_planets[0][0],
                "strength": sorted_planets[0][1]["percentage"]
            } if sorted_planets else None,
            "weakest_planet": {
                "planet": sorted_planets[-1][0],
                "strength": sorted_planets[-1][1]["percentage"]
            } if sorted_planets else None,
            "average_strength": round(
                sum(p[1]["percentage"] for p in sorted_planets) / len(sorted_planets), 2
            ) if sorted_planets else 0,
            "planets_above_required": [
                p[0] for p in sorted_planets if p[1]["percentage"] >= 100
            ],
            "planets_below_required": [
                p[0] for p in sorted_planets if p[1]["percentage"] < 100
            ]
        }

    def _calculate_sthana_bala(
        self,
        planet: str,
        planet_data: Dict[str, Any],
        chart_data: Dict[str, Any]
    ) -> float:
        """
        Calculate Sthana Bala (Positional Strength)

        Components:
        - Uchcha Bala (Exaltation strength)
        - Saptavargaja Bala (Divisional chart strength)
        - Ojhayugmarasyamsa Bala (Odd/Even sign strength)
        - Kendradi Bala (Angular house strength)
        - Drekkana Bala (Decanate strength)
        """
        sthana_bala = 0.0

        sign = planet_data.get("sign", "")
        degree = planet_data.get("degree", 0)
        house = planet_data.get("house", 1)

        # 1. Uchcha Bala (Exaltation strength) - Max 60
        uchcha_bala = self._calculate_uchcha_bala(planet, sign, degree)
        sthana_bala += uchcha_bala

        # 2. Sign-based strength - Max 30
        if sign in self.own_signs.get(planet, []):
            sthana_bala += 30  # Own sign
        elif sign in self.friendly_signs.get(planet, []):
            sthana_bala += 22.5  # Friend's sign
        elif sign in self.enemy_signs.get(planet, []):
            sthana_bala += 7.5  # Enemy's sign
        else:
            sthana_bala += 15  # Neutral sign

        # 3. Kendradi Bala (Angular house strength) - Max 60
        if house in [1, 4, 7, 10]:  # Angular (Kendra)
            sthana_bala += 60
        elif house in [2, 5, 8, 11]:  # Succedent (Panaphara)
            sthana_bala += 30
        elif house in [3, 6, 9, 12]:  # Cadent (Apoklima)
            sthana_bala += 15

        # 4. Ojhayugmarasyamsa Bala (Odd/Even) - Max 15
        sign_num = planet_data.get("sign_num", 0)
        is_odd_sign = (sign_num % 2 == 0)  # 0-indexed, so 0,2,4... are odd signs

        # Male planets (Sun, Mars, Jupiter) stronger in odd signs
        # Female planets (Moon, Venus) stronger in even signs
        # Mercury is neutral
        if planet in ["Sun", "Mars", "Jupiter"]:
            sthana_bala += 15 if is_odd_sign else 0
        elif planet in ["Moon", "Venus"]:
            sthana_bala += 15 if not is_odd_sign else 0
        else:  # Mercury
            sthana_bala += 7.5

        return sthana_bala

    def _calculate_uchcha_bala(
        self,
        planet: str,
        sign: str,
        degree: float
    ) -> float:
        """Calculate Uchcha Bala (Exaltation/Debilitation strength)"""

        exaltation = self.exaltation_points.get(planet, {})
        debilitation = self.debilitation_points.get(planet, {})

        # Calculate absolute longitude
        sign_num = self._get_sign_number(sign)
        if sign_num is None:
            return 30  # Neutral

        absolute_degree = (sign_num * 30) + degree

        # Exaltation point
        exalt_sign_num = self._get_sign_number(exaltation.get("sign", ""))
        if exalt_sign_num is not None:
            exalt_degree = (exalt_sign_num * 30) + exaltation.get("degree", 0)

            # Calculate distance from exaltation point
            distance = abs(absolute_degree - exalt_degree)
            if distance > 180:
                distance = 360 - distance

            # Uchcha Bala = 60 * (1 - distance/180)
            uchcha_bala = 60 * (1 - (distance / 180))

            return max(0, min(60, uchcha_bala))

        return 30  # Neutral

    def _calculate_dig_bala(
        self,
        planet: str,
        planet_data: Dict[str, Any],
        ascendant: Dict[str, Any]
    ) -> float:
        """
        Calculate Dig Bala (Directional Strength)

        Each planet is strongest in a specific direction:
        - Sun, Mars: 10th house (South)
        - Moon, Venus: 4th house (North)
        - Mercury, Jupiter: 1st house (East)
        - Saturn: 7th house (West)
        """
        house = planet_data.get("house", 1)
        best_house = self.dig_bala_houses.get(planet, 1)

        # Calculate distance from best house
        distance = abs(house - best_house)
        if distance > 6:
            distance = 12 - distance

        # Maximum Dig Bala is 60 at best house, 0 at opposite house
        dig_bala = 60 * (1 - (distance / 6))

        return max(0, dig_bala)

    def _calculate_kala_bala(
        self,
        planet: str,
        planet_data: Dict[str, Any],
        birth_datetime: Optional[datetime]
    ) -> float:
        """
        Calculate Kala Bala (Temporal Strength)

        Components:
        - Nathonnatha Bala (Day/Night strength)
        - Paksha Bala (Lunar fortnight strength)
        - Tribhaga Bala (Day/Night third strength)
        - Varsha-Masa-Dina-Hora Bala (Year/Month/Day/Hour lord strength)
        """
        kala_bala = 0.0

        # 1. Nathonnatha Bala (Day/Night) - Max 60
        # Diurnal planets (Sun, Jupiter, Venus) stronger during day
        # Nocturnal planets (Moon, Mars, Saturn) stronger at night
        if birth_datetime:
            birth_time = birth_datetime.time()
            hour = birth_time.hour
            is_day = 6 <= hour < 18  # Simplified: 6 AM to 6 PM

            if planet in ["Sun", "Jupiter", "Venus"]:
                kala_bala += 60 if is_day else 0
            elif planet in ["Moon", "Mars", "Saturn"]:
                kala_bala += 60 if not is_day else 0
            else:  # Mercury (neutral)
                kala_bala += 30
        else:
            kala_bala += 30  # Neutral if no time data

        # 2. Paksha Bala (Lunar phase) - Max 60
        # Simplified: Assume average
        kala_bala += 30

        # 3. Additional temporal factors - Max 60
        kala_bala += 30

        return kala_bala

    def _calculate_chesta_bala(
        self,
        planet: str,
        planet_data: Dict[str, Any]
    ) -> float:
        """
        Calculate Chesta Bala (Motional Strength)

        Based on planetary speed and retrograde motion
        """
        # Sun and Moon don't have Chesta Bala (use average)
        if planet in ["Sun", "Moon"]:
            return 30

        # Check if retrograde
        retrograde = planet_data.get("retrograde", False)
        speed = planet_data.get("speed", 0)

        # Retrograde planets get maximum Chesta Bala
        if retrograde:
            return 60

        # Fast-moving planets get higher strength
        # This is simplified; actual calculation is complex
        if abs(speed) > 0.5:
            return 45  # Fast
        elif abs(speed) > 0.1:
            return 30  # Average
        else:
            return 15  # Slow

    def _calculate_drik_bala(
        self,
        planet: str,
        planet_data: Dict[str, Any],
        all_planets: Dict[str, Any]
    ) -> float:
        """
        Calculate Drik Bala (Aspectual Strength)

        Based on aspects received from other planets
        Benefics increase strength, malefics decrease it
        """
        drik_bala = 0.0

        planet_longitude = planet_data.get("longitude", 0)

        # Classify planets
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
        malefics = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]

        # Check aspects from other planets
        for other_planet, other_data in all_planets.items():
            if other_planet == planet:
                continue

            other_longitude = other_data.get("longitude", 0)

            # Calculate angular separation
            separation = abs(planet_longitude - other_longitude)
            if separation > 180:
                separation = 360 - separation

            # Check for major aspects (simplified)
            aspect_strength = 0

            # Opposition (180°)
            if 175 <= separation <= 185:
                aspect_strength = 60
            # Trine (120°)
            elif 115 <= separation <= 125:
                aspect_strength = 45
            # Square (90°)
            elif 85 <= separation <= 95:
                aspect_strength = 30
            # Sextile (60°)
            elif 55 <= separation <= 65:
                aspect_strength = 15

            # Apply aspect
            if aspect_strength > 0:
                if other_planet in benefics:
                    drik_bala += aspect_strength / 4
                elif other_planet in malefics:
                    drik_bala -= aspect_strength / 4

        # Normalize to 0-60 range
        drik_bala = max(-30, min(30, drik_bala)) + 30

        return drik_bala

    def _get_strength_rating(self, percentage: float) -> str:
        """Get strength rating based on percentage of required Shadbala"""
        if percentage >= 150:
            return "Exceptional"
        elif percentage >= 125:
            return "Very Strong"
        elif percentage >= 100:
            return "Strong"
        elif percentage >= 75:
            return "Moderate"
        elif percentage >= 50:
            return "Weak"
        else:
            return "Very Weak"

    def _get_sign_number(self, sign: str) -> Optional[int]:
        """Get zodiac sign number (0-11)"""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        try:
            return signs.index(sign)
        except ValueError:
            return None


# Singleton instance
shadbala_service = ShadbalaService()
