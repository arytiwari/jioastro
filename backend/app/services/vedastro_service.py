"""
VedAstro Service Integration
Using VedAstro Python library for comprehensive Vedic astrology calculations

License: MIT License - VedAstro @ VedAstro.org (2014-2022)
Attribution: Astrological calculations powered by VedAstro (https://vedastro.org)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date, time
import json

try:
    from vedastro import GeoLocation, Time, Calculate, PlanetName, HouseName, ZodiacName
    VEDASTRO_AVAILABLE = True
except ImportError:
    VEDASTRO_AVAILABLE = False
    print("Warning: VedAstro library not available. Install with: pip install vedastro")


class VedAstroService:
    """Service for VedAstro calculations - comprehensive Vedic astrology engine"""

    def __init__(self):
        """Initialize VedAstro service"""
        self.available = VEDASTRO_AVAILABLE

    def is_available(self) -> bool:
        """Check if VedAstro library is installed and available"""
        return self.available

    def calculate_comprehensive_chart(
        self,
        birth_date: date,
        birth_time: time,
        latitude: float,
        longitude: float,
        location_name: str = "Unknown",
        timezone_offset: str = "+00:00"
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive birth chart using VedAstro

        Args:
            birth_date: Date of birth
            birth_time: Time of birth
            latitude: Birth location latitude
            longitude: Birth location longitude
            location_name: Name of birth location
            timezone_offset: Timezone offset (e.g., "+05:30" for IST)

        Returns:
            Comprehensive chart data with planets, houses, yogas, dasas, etc.
        """

        if not self.available:
            return {"error": "VedAstro library not available"}

        try:
            # Format datetime for VedAstro: "HH:MM DD/MM/YYYY +TZ:00"
            birth_datetime_str = f"{birth_time.strftime('%H:%M')} {birth_date.strftime('%d/%m/%Y')} {timezone_offset}"

            # Create GeoLocation
            geo_location = GeoLocation(location_name, longitude, latitude)

            # Create Time object
            birth_time_obj = Time(birth_datetime_str, geo_location)

            # Calculate all planet data
            all_planet_data = {}
            planet_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

            for planet_name in planet_names:
                try:
                    planet_enum = getattr(PlanetName, planet_name)
                    planet_data_list = Calculate.AllPlanetData(planet_enum, birth_time_obj)
                    all_planet_data[planet_name] = planet_data_list
                except Exception as e:
                    print(f"Error calculating {planet_name}: {e}")
                    all_planet_data[planet_name] = []

            # Calculate house data
            try:
                house_data = Calculate.AllHouseData(birth_time_obj)
            except Exception as e:
                print(f"Error calculating houses: {e}")
                house_data = []

            # Calculate zodiac data
            try:
                zodiac_data = Calculate.AllZodiacSignData(birth_time_obj)
            except Exception as e:
                print(f"Error calculating zodiac: {e}")
                zodiac_data = []

            return {
                "source": "VedAstro",
                "birth_datetime": birth_datetime_str,
                "location": {
                    "name": location_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": timezone_offset
                },
                "planets": all_planet_data,
                "houses": house_data,
                "zodiac": zodiac_data,
                "calculation_time": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "error": f"VedAstro calculation failed: {str(e)}",
                "source": "VedAstro"
            }

    def extract_simplified_chart_data(self, vedastro_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and simplify VedAstro data into our standard chart format

        Args:
            vedastro_data: Raw VedAstro calculation output

        Returns:
            Simplified chart data matching our frontend expectations
        """

        if "error" in vedastro_data:
            return vedastro_data

        try:
            # Parse planet data from VedAstro format
            planets = {}
            for planet_name, planet_calculations in vedastro_data.get("planets", {}).items():
                if planet_calculations:
                    # VedAstro returns list of calculations, extract relevant ones
                    planet_info = self._parse_planet_calculations(planet_calculations)
                    if planet_info:
                        planets[planet_name] = planet_info

            # Parse house data
            houses = []
            house_data_list = vedastro_data.get("houses", [])
            if house_data_list:
                houses = self._parse_house_calculations(house_data_list)

            # Extract ascendant from houses (1st house)
            ascendant = houses[0] if houses else {
                "sign": "Unknown",
                "sign_num": 0,
                "house": 1,
                "position": 0.0
            }

            return {
                "source": "VedAstro",
                "basic_info": vedastro_data.get("location", {}),
                "ascendant": ascendant,
                "planets": planets,
                "houses": houses,
                "chart_type": "D1",
                "vedastro_raw": vedastro_data  # Keep raw data for advanced features
            }

        except Exception as e:
            return {
                "error": f"Failed to parse VedAstro data: {str(e)}",
                "source": "VedAstro"
            }

    def _parse_planet_calculations(self, calculations: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse planet calculations from VedAstro format"""

        try:
            # VedAstro returns calculations as list of dicts/objects
            # Look for zodiac sign, house, and position data
            planet_data = {
                "sign": "Unknown",
                "sign_num": 0,
                "position": 0.0,
                "house": 1,
                "retrograde": False
            }

            # Extract data from calculations list
            for calc in calculations:
                if isinstance(calc, dict):
                    # Look for specific calculation types
                    if "ZodiacSign" in calc or "zodiacSign" in calc:
                        sign = calc.get("ZodiacSign") or calc.get("zodiacSign")
                        if sign:
                            planet_data["sign"] = str(sign)
                            planet_data["sign_num"] = self._sign_name_to_num(str(sign))

                    if "House" in calc or "house" in calc:
                        house = calc.get("House") or calc.get("house")
                        if house:
                            planet_data["house"] = int(house) if isinstance(house, (int, float)) else 1

                    if "Longitude" in calc or "longitude" in calc:
                        longitude = calc.get("Longitude") or calc.get("longitude")
                        if longitude:
                            planet_data["position"] = float(longitude) if isinstance(longitude, (int, float)) else 0.0

                    if "Retrograde" in calc or "retrograde" in calc:
                        retrograde = calc.get("Retrograde") or calc.get("retrograde")
                        planet_data["retrograde"] = bool(retrograde)

            return planet_data

        except Exception as e:
            print(f"Error parsing planet calculations: {e}")
            return None

    def _parse_house_calculations(self, house_data: List[Any]) -> List[Dict[str, Any]]:
        """Parse house calculations from VedAstro format"""

        houses = []
        try:
            for i, house_calc in enumerate(house_data[:12], 1):  # Max 12 houses
                house_info = {
                    "house_num": i,
                    "sign": "Unknown",
                    "sign_num": 0,
                    "position": 0.0
                }

                if isinstance(house_calc, dict):
                    if "ZodiacSign" in house_calc:
                        sign = house_calc["ZodiacSign"]
                        house_info["sign"] = str(sign)
                        house_info["sign_num"] = self._sign_name_to_num(str(sign))

                    if "Longitude" in house_calc or "Position" in house_calc:
                        position = house_calc.get("Longitude") or house_calc.get("Position")
                        if position:
                            house_info["position"] = float(position)

                houses.append(house_info)

        except Exception as e:
            print(f"Error parsing house calculations: {e}")

        return houses

    def _sign_name_to_num(self, sign_name: str) -> int:
        """Convert zodiac sign name to number (0-11)"""

        sign_map = {
            "Aries": 0, "Taurus": 1, "Gemini": 2, "Cancer": 3,
            "Leo": 4, "Virgo": 5, "Libra": 6, "Scorpio": 7,
            "Sagittarius": 8, "Capricorn": 9, "Aquarius": 10, "Pisces": 11
        }

        # Normalize sign name (remove extra chars, title case)
        normalized = sign_name.strip().title()
        return sign_map.get(normalized, 0)

    def get_vedic_knowledge(self, topic: str) -> Dict[str, Any]:
        """
        Get Vedic astrology knowledge on specific topics

        Args:
            topic: Topic name (e.g., "planets", "houses", "yogas", "nakshatras")

        Returns:
            Knowledge data for the topic
        """

        knowledge_base = {
            "planets": {
                "title": "Vedic Planets (Grahas)",
                "description": "The nine planets in Vedic astrology",
                "items": [
                    {"name": "Sun (Surya)", "nature": "Soul, authority, father, government", "strength": "Exalted in Aries, debilitated in Libra"},
                    {"name": "Moon (Chandra)", "nature": "Mind, mother, emotions, public", "strength": "Exalted in Taurus, debilitated in Scorpio"},
                    {"name": "Mars (Mangala)", "nature": "Energy, courage, siblings, property", "strength": "Exalted in Capricorn, debilitated in Cancer"},
                    {"name": "Mercury (Budha)", "nature": "Intelligence, communication, business", "strength": "Exalted in Virgo, debilitated in Pisces"},
                    {"name": "Jupiter (Guru)", "nature": "Wisdom, children, wealth, spirituality", "strength": "Exalted in Cancer, debilitated in Capricorn"},
                    {"name": "Venus (Shukra)", "nature": "Love, marriage, luxury, arts", "strength": "Exalted in Pisces, debilitated in Virgo"},
                    {"name": "Saturn (Shani)", "nature": "Discipline, karma, delays, longevity", "strength": "Exalted in Libra, debilitated in Aries"},
                    {"name": "Rahu (North Node)", "nature": "Desires, illusions, foreign, technology", "strength": "Exalted in Taurus/Gemini"},
                    {"name": "Ketu (South Node)", "nature": "Spirituality, detachment, past life", "strength": "Exalted in Scorpio/Sagittarius"}
                ]
            },
            "houses": {
                "title": "Vedic Houses (Bhavas)",
                "description": "The twelve houses representing different life areas",
                "items": [
                    {"house": 1, "name": "Tanu Bhava", "signifies": "Self, personality, physical body, appearance"},
                    {"house": 2, "name": "Dhana Bhava", "signifies": "Wealth, family, speech, food"},
                    {"house": 3, "name": "Sahaja Bhava", "signifies": "Siblings, courage, communication, short journeys"},
                    {"house": 4, "name": "Sukha Bhava", "signifies": "Mother, home, property, happiness, education"},
                    {"house": 5, "name": "Putra Bhava", "signifies": "Children, creativity, intelligence, romance"},
                    {"house": 6, "name": "Ripu Bhava", "signifies": "Enemies, diseases, debts, service"},
                    {"house": 7, "name": "Kalatra Bhava", "signifies": "Spouse, partnerships, marriage"},
                    {"house": 8, "name": "Ayu Bhava", "signifies": "Longevity, transformation, occult, inheritance"},
                    {"house": 9, "name": "Dharma Bhava", "signifies": "Father, fortune, religion, higher education"},
                    {"house": 10, "name": "Karma Bhava", "signifies": "Career, status, reputation, authority"},
                    {"house": 11, "name": "Labha Bhava", "signifies": "Gains, friends, aspirations, income"},
                    {"house": 12, "name": "Vyaya Bhava", "signifies": "Losses, expenses, foreign lands, spirituality"}
                ]
            },
            "yogas": {
                "title": "Major Vedic Yogas",
                "description": "Important planetary combinations",
                "items": [
                    {"name": "Raj Yoga", "description": "Combination of 9th and 10th lords brings power and success"},
                    {"name": "Dhana Yoga", "description": "Wealth combinations from 2nd, 5th, 9th, 11th lords"},
                    {"name": "Gaja Kesari Yoga", "description": "Jupiter in Kendra from Moon - wisdom and prosperity"},
                    {"name": "Budhaditya Yoga", "description": "Sun-Mercury conjunction enhances intelligence"},
                    {"name": "Chandra-Mangala Yoga", "description": "Moon-Mars combination for wealth"},
                    {"name": "Pancha Mahapurusha Yoga", "description": "Five great yogas from Mars, Mercury, Jupiter, Venus, Saturn"},
                    {"name": "Neecha Bhanga Raj Yoga", "description": "Cancellation of debilitation creates powerful yoga"}
                ]
            },
            "nakshatras": {
                "title": "Nakshatras (Lunar Mansions)",
                "description": "27 lunar mansions in Vedic astrology",
                "items": [
                    {"number": 1, "name": "Ashwini", "lord": "Ketu", "symbol": "Horse head"},
                    {"number": 2, "name": "Bharani", "lord": "Venus", "symbol": "Yoni"},
                    {"number": 3, "name": "Krittika", "lord": "Sun", "symbol": "Razor"},
                    {"number": 4, "name": "Rohini", "lord": "Moon", "symbol": "Chariot"},
                    {"number": 5, "name": "Mrigashira", "lord": "Mars", "symbol": "Deer head"},
                    {"number": 6, "name": "Ardra", "lord": "Rahu", "symbol": "Teardrop"},
                    {"number": 7, "name": "Punarvasu", "lord": "Jupiter", "symbol": "Bow and quiver"},
                    {"number": 8, "name": "Pushya", "lord": "Saturn", "symbol": "Cow udder"},
                    {"number": 9, "name": "Ashlesha", "lord": "Mercury", "symbol": "Serpent"},
                    # Add remaining 18 nakshatras...
                    {"note": "Total 27 nakshatras, each spanning 13°20' of the zodiac"}
                ]
            },
            "dashas": {
                "title": "Vimshottari Dasha System",
                "description": "120-year planetary period system",
                "items": [
                    {"planet": "Ketu", "years": 7, "nature": "Spiritual transformation"},
                    {"planet": "Venus", "years": 20, "nature": "Comfort, luxury, relationships"},
                    {"planet": "Sun", "years": 6, "nature": "Authority, recognition"},
                    {"planet": "Moon", "years": 10, "nature": "Emotional growth, public life"},
                    {"planet": "Mars", "years": 7, "nature": "Energy, conflicts, property"},
                    {"planet": "Rahu", "years": 18, "nature": "Desires, foreign connections"},
                    {"planet": "Jupiter", "years": 16, "nature": "Expansion, wisdom, children"},
                    {"planet": "Saturn", "years": 19, "nature": "Discipline, delays, karma"},
                    {"planet": "Mercury", "years": 17, "nature": "Learning, business, communication"}
                ]
            }
        }

        return knowledge_base.get(topic.lower(), {
            "title": "Topic Not Found",
            "description": f"Knowledge base entry for '{topic}' not available",
            "items": []
        })


# Singleton instance
vedastro_service = VedAstroService()
