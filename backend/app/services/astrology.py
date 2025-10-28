"""
Vedic Astrology Calculation Service
Using Swiss Ephemeris and Kerykeion for accurate Vedic calculations
"""

from typing import Dict, List, Any
from datetime import datetime, date, time
from kerykeion import AstrologicalSubject
import pytz


class VedicAstrologyService:
    """Service for Vedic astrology calculations"""

    ZODIAC_SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    PLANETS = [
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
        "Rahu", "Ketu"  # Vedic nodes
    ]

    def __init__(self):
        """Initialize astrology service"""
        pass

    def calculate_birth_chart(
        self,
        name: str,
        birth_date: date,
        birth_time: time,
        latitude: float,
        longitude: float,
        timezone_str: str = "UTC",
        city: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Calculate Vedic birth chart (D1 - Rashi chart)

        Args:
            name: Person's name
            birth_date: Date of birth
            birth_time: Time of birth
            latitude: Birth location latitude
            longitude: Birth location longitude
            timezone_str: Timezone string (e.g., 'Asia/Kolkata')
            city: Birth city name

        Returns:
            Complete birth chart data including planets, houses, and yogas
        """

        # Create AstrologicalSubject with Vedic (Sidereal) mode
        # Note: Kerykeion 4.3.0 uses Lahiri ayanamsa by default for Sidereal
        subject = AstrologicalSubject(
            name=name,
            year=birth_date.year,
            month=birth_date.month,
            day=birth_date.day,
            hour=birth_time.hour,
            minute=birth_time.minute,
            lat=latitude,
            lng=longitude,
            tz_str=timezone_str,
            city=city,
            zodiac_type="Sidereal"  # Vedic astrology uses sidereal zodiac (Lahiri by default)
        )

        # Extract chart data
        chart_data = {
            "basic_info": {
                "name": name,
                "birth_datetime": datetime.combine(birth_date, birth_time).isoformat(),
                "location": {
                    "city": city,
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": timezone_str
                }
            },
            "ascendant": {
                "sign": getattr(subject.first_house, 'sign', 'Unknown'),
                "sign_num": getattr(subject.first_house, 'sign_num', 0),
                "position": getattr(subject.first_house, 'position', 0.0),
                "house": 1
            },
            "planets": self._extract_planets(subject),
            "houses": self._extract_houses(subject),
            "yogas": self._detect_yogas(subject),
            "dasha": self._calculate_vimshottari_dasha(subject),
            "chart_type": "D1"
        }

        return chart_data

    def calculate_navamsa_chart(
        self,
        name: str,
        birth_date: date,
        birth_time: time,
        latitude: float,
        longitude: float,
        timezone_str: str = "UTC",
        city: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Calculate Navamsa chart (D9)
        This is a simplified version - full Navamsa requires divisional chart calculations
        """

        # First get the D1 chart
        d1_chart = self.calculate_birth_chart(
            name, birth_date, birth_time, latitude, longitude, timezone_str, city
        )

        # For MVP, we'll calculate Navamsa positions using the standard formula
        # Navamsa = (Planet position in sign * 9) / 30 (rounded down) + sign adjustment
        navamsa_planets = {}

        for planet_name, planet_data in d1_chart["planets"].items():
            navamsa_pos = self._calculate_navamsa_position(
                planet_data["position"],
                planet_data["sign_num"]
            )
            navamsa_planets[planet_name] = navamsa_pos

        return {
            "basic_info": d1_chart["basic_info"],
            "planets": navamsa_planets,
            "chart_type": "D9",
            "note": "Navamsa (D9) - Marriage and spiritual chart"
        }

    def _extract_planets(self, subject: AstrologicalSubject) -> Dict[str, Any]:
        """Extract planetary positions from subject"""

        planets_data = {}

        # Sun
        if hasattr(subject, 'sun'):
            planets_data["Sun"] = {
                "sign": subject.sun.sign,
                "sign_num": subject.sun.sign_num,
                "position": subject.sun.position,
                "house": subject.sun.house,
                "retrograde": subject.sun.retrograde if hasattr(subject.sun, 'retrograde') else False
            }

        # Moon
        if hasattr(subject, 'moon'):
            planets_data["Moon"] = {
                "sign": subject.moon.sign,
                "sign_num": subject.moon.sign_num,
                "position": subject.moon.position,
                "house": subject.moon.house,
                "retrograde": False  # Moon never retrogrades
            }

        # Mars
        if hasattr(subject, 'mars'):
            planets_data["Mars"] = {
                "sign": subject.mars.sign,
                "sign_num": subject.mars.sign_num,
                "position": subject.mars.position,
                "house": subject.mars.house,
                "retrograde": subject.mars.retrograde if hasattr(subject.mars, 'retrograde') else False
            }

        # Mercury
        if hasattr(subject, 'mercury'):
            planets_data["Mercury"] = {
                "sign": subject.mercury.sign,
                "sign_num": subject.mercury.sign_num,
                "position": subject.mercury.position,
                "house": subject.mercury.house,
                "retrograde": subject.mercury.retrograde if hasattr(subject.mercury, 'retrograde') else False
            }

        # Jupiter
        if hasattr(subject, 'jupiter'):
            planets_data["Jupiter"] = {
                "sign": subject.jupiter.sign,
                "sign_num": subject.jupiter.sign_num,
                "position": subject.jupiter.position,
                "house": subject.jupiter.house,
                "retrograde": subject.jupiter.retrograde if hasattr(subject.jupiter, 'retrograde') else False
            }

        # Venus
        if hasattr(subject, 'venus'):
            planets_data["Venus"] = {
                "sign": subject.venus.sign,
                "sign_num": subject.venus.sign_num,
                "position": subject.venus.position,
                "house": subject.venus.house,
                "retrograde": subject.venus.retrograde if hasattr(subject.venus, 'retrograde') else False
            }

        # Saturn
        if hasattr(subject, 'saturn'):
            planets_data["Saturn"] = {
                "sign": subject.saturn.sign,
                "sign_num": subject.saturn.sign_num,
                "position": subject.saturn.position,
                "house": subject.saturn.house,
                "retrograde": subject.saturn.retrograde if hasattr(subject.saturn, 'retrograde') else False
            }

        # Rahu (North Node)
        if hasattr(subject, 'mean_node'):
            planets_data["Rahu"] = {
                "sign": subject.mean_node.sign,
                "sign_num": subject.mean_node.sign_num,
                "position": subject.mean_node.position,
                "house": subject.mean_node.house,
                "retrograde": True  # Rahu always moves retrograde
            }

            # Ketu is always 180 degrees opposite Rahu
            ketu_sign_num = (subject.mean_node.sign_num + 6) % 12
            ketu_position = (subject.mean_node.position + 180) % 360

            planets_data["Ketu"] = {
                "sign": self.ZODIAC_SIGNS[ketu_sign_num],
                "sign_num": ketu_sign_num,
                "position": ketu_position,
                "house": self._get_house_from_position(ketu_position, subject),
                "retrograde": True  # Ketu always moves retrograde
            }

        return planets_data

    def _extract_houses(self, subject: AstrologicalSubject) -> List[Dict[str, Any]]:
        """Extract house cusps"""

        houses = []
        house_attributes = [
            'first_house', 'second_house', 'third_house', 'fourth_house',
            'fifth_house', 'sixth_house', 'seventh_house', 'eighth_house',
            'ninth_house', 'tenth_house', 'eleventh_house', 'twelfth_house'
        ]

        for i, house_attr in enumerate(house_attributes, 1):
            if hasattr(subject, house_attr):
                house_data = getattr(subject, house_attr)
                houses.append({
                    "house_num": i,
                    "sign": getattr(house_data, 'sign', 'Unknown'),
                    "sign_num": getattr(house_data, 'sign_num', 0),
                    "position": getattr(house_data, 'position', 0.0)
                })

        return houses

    def _detect_yogas(self, subject: AstrologicalSubject) -> List[Dict[str, str]]:
        """
        Detect major Vedic yogas (combinations)
        Simplified version for MVP - detecting top 10-15 common yogas
        """

        yogas = []

        # Get planet positions
        planets = self._extract_planets(subject)
        houses = self._extract_houses(subject)

        # 1. Raj Yoga: Lords of 9th and 10th in Kendra (1, 4, 7, 10)
        # Simplified check: if Jupiter (natural 9th lord) and Saturn (natural 10th lord) are strong
        if planets.get("Jupiter") and planets.get("Saturn"):
            jupiter_house = int(planets["Jupiter"]["house"]) if planets["Jupiter"]["house"] else 0
            saturn_house = int(planets["Saturn"]["house"]) if planets["Saturn"]["house"] else 0

            if jupiter_house in [1, 4, 7, 10] and saturn_house in [1, 4, 7, 10]:
                yogas.append({
                    "name": "Raj Yoga",
                    "description": "Combination indicating power, authority, and success. Jupiter and Saturn are well-placed in angles.",
                    "strength": "Strong"
                })

        # 2. Dhana Yoga: Wealth combinations
        if planets.get("Jupiter") and planets.get("Venus"):
            jupiter_house = int(planets["Jupiter"]["house"]) if planets["Jupiter"]["house"] else 0
            venus_house = int(planets["Venus"]["house"]) if planets["Venus"]["house"] else 0
            if jupiter_house == venus_house and jupiter_house > 0:
                yogas.append({
                    "name": "Dhana Yoga",
                    "description": "Jupiter and Venus conjunction indicates wealth and prosperity.",
                    "strength": "Medium"
                })

        # 3. Budhaditya Yoga: Sun-Mercury conjunction
        if planets.get("Sun") and planets.get("Mercury"):
            sun_pos = float(planets["Sun"]["position"]) if planets["Sun"]["position"] else 0
            mercury_pos = float(planets["Mercury"]["position"]) if planets["Mercury"]["position"] else 0

            if abs(sun_pos - mercury_pos) < 10:  # Within 10 degrees
                yogas.append({
                    "name": "Budhaditya Yoga",
                    "description": "Sun-Mercury conjunction enhances intelligence, communication, and learning abilities.",
                    "strength": "Medium"
                })

        # 4. Chandra-Mangala Yoga: Moon-Mars conjunction
        if planets.get("Moon") and planets.get("Mars"):
            moon_house = int(planets["Moon"]["house"]) if planets["Moon"]["house"] else 0
            mars_house = int(planets["Mars"]["house"]) if planets["Mars"]["house"] else 0
            if moon_house == mars_house and moon_house > 0:
                yogas.append({
                    "name": "Chandra-Mangala Yoga",
                    "description": "Moon-Mars combination indicates determination, courage, and material success.",
                    "strength": "Medium"
                })

        # 5. Gaja Kesari Yoga: Jupiter in Kendra from Moon
        if planets.get("Jupiter") and planets.get("Moon"):
            jupiter_house = int(planets["Jupiter"]["house"]) if planets["Jupiter"]["house"] else 0
            moon_house = int(planets["Moon"]["house"]) if planets["Moon"]["house"] else 0

            if jupiter_house > 0 and moon_house > 0:
                # Check if Jupiter is in 1st, 4th, 7th, or 10th from Moon
                house_diff = (jupiter_house - moon_house) % 12
                if house_diff in [0, 3, 6, 9]:  # Kendra relationship
                    yogas.append({
                        "name": "Gaja Kesari Yoga",
                        "description": "Jupiter in angle from Moon - brings wisdom, prosperity, and good fortune.",
                        "strength": "Strong"
                    })

        # 6. Neecha Bhanga Raja Yoga: Cancellation of debilitation
        # Simplified: Check if debilitated planet's lord is in Kendra
        # (Full implementation would be more complex)

        # If no yogas detected, add a default message
        if not yogas:
            yogas.append({
                "name": "General Analysis",
                "description": "Your chart shows unique planetary combinations. Consult detailed analysis for personalized insights.",
                "strength": "Varies"
            })

        return yogas

    def _calculate_vimshottari_dasha(self, subject: AstrologicalSubject) -> Dict[str, Any]:
        """
        Calculate Vimshottari Dasha (planetary periods)
        Simplified version for MVP
        """

        # Vimshottari Dasha is based on Moon's nakshatra position
        # This is a simplified version - full calculation requires nakshatra determination

        moon_position = subject.moon.position if hasattr(subject, 'moon') else 0

        # Nakshatras are 13°20' each (360/27)
        nakshatra_num = int(moon_position / 13.333333)
        nakshatra_lord_sequence = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        nakshatra_lord = nakshatra_lord_sequence[nakshatra_num % 9]

        # Dasha periods (in years)
        dasha_periods = {
            "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10,
            "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
        }

        return {
            "current_dasha": nakshatra_lord,
            "period_years": dasha_periods.get(nakshatra_lord, 0),
            "note": "Simplified Vimshottari Dasha calculation based on Moon's nakshatra"
        }

    def _calculate_navamsa_position(self, planet_position: float, sign_num: int) -> Dict[str, Any]:
        """Calculate Navamsa (D9) position for a planet"""

        # Position within the sign (0-30 degrees)
        pos_in_sign = planet_position % 30

        # Navamsa within the sign (0-8, as there are 9 navamsas per sign)
        navamsa_in_sign = int(pos_in_sign / 3.333333)

        # Calculate the navamsa sign
        # Formula: (sign_num - 1) * 9 + navamsa_in_sign + 1, then mod 12
        navamsa_sign_num = ((sign_num * 9) + navamsa_in_sign) % 12

        return {
            "sign": self.ZODIAC_SIGNS[navamsa_sign_num],
            "sign_num": navamsa_sign_num,
            "navamsa_num": navamsa_in_sign + 1,
            "position": (navamsa_sign_num * 30) + (pos_in_sign % 3.333333) * 9
        }

    def _get_house_from_position(self, position: float, subject: AstrologicalSubject) -> int:
        """Determine which house a given ecliptic position falls into"""

        houses = self._extract_houses(subject)

        # Simple house determination (can be improved)
        for i, house in enumerate(houses):
            next_house = houses[(i + 1) % 12]
            house_start = house["position"]
            house_end = next_house["position"]

            # Handle wrap-around at 360 degrees
            if house_end < house_start:
                if position >= house_start or position < house_end:
                    return house["house_num"]
            else:
                if house_start <= position < house_end:
                    return house["house_num"]

        return 1  # Default to 1st house if not found


# Singleton instance
astrology_service = VedicAstrologyService()
