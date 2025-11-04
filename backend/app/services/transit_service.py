"""
Transit Calculation Service
Calculates current planetary positions and their effects on birth chart
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
from app.services.astrology import astrology_service
import swisseph as swe


class TransitService:
    """
    Service for calculating planetary transits and their effects

    Transits show current planetary positions and how they interact
    with natal (birth) chart positions
    """

    def __init__(self):
        """Initialize transit service"""
        # Aspect orbs (degrees of allowance for aspects)
        self.aspect_orbs = {
            "conjunction": 8.0,      # 0° - planets together
            "opposition": 8.0,       # 180° - planets opposite
            "trine": 8.0,           # 120° - harmonious
            "square": 7.0,          # 90° - challenging
            "sextile": 6.0,         # 60° - opportunity
        }

        # Aspect interpretations
        self.aspect_meanings = {
            "conjunction": "merging, intensifying, focusing",
            "opposition": "tension, awareness, balance needed",
            "trine": "harmony, ease, natural flow",
            "square": "challenge, friction, growth through effort",
            "sextile": "opportunity, cooperation, potential",
        }

        # House significations
        self.house_meanings = {
            1: "self, personality, physical body",
            2: "wealth, possessions, values",
            3: "communication, siblings, short travels",
            4: "home, mother, emotional foundation",
            5: "creativity, children, romance",
            6: "health, service, daily work",
            7: "partnerships, marriage, business",
            8: "transformation, inheritance, occult",
            9: "higher learning, spirituality, long travels",
            10: "career, reputation, father",
            11: "gains, friends, aspirations",
            12: "losses, isolation, spirituality",
        }

    def calculate_current_transits(
        self,
        birth_chart: Dict[str, Any],
        transit_date: Optional[datetime] = None,
        latitude: float = 0.0,
        longitude: float = 0.0,
        timezone_str: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Calculate current planetary transits and their effects on birth chart

        Args:
            birth_chart: Birth chart data (from astrology_service)
            transit_date: Date/time for transits (default: now)
            latitude: Observer latitude for transit chart
            longitude: Observer longitude for transit chart
            timezone_str: Timezone for transit chart

        Returns:
            Dictionary with transit positions and significant aspects
        """
        if transit_date is None:
            transit_date = datetime.now()

        print(f"🌟 Calculating transits for {transit_date.strftime('%Y-%m-%d %H:%M')}")

        # Calculate transit chart (current planetary positions)
        transit_chart = astrology_service.calculate_birth_chart(
            name="Transit",
            birth_date=transit_date.date(),
            birth_time=transit_date.time(),
            latitude=latitude,
            longitude=longitude,
            timezone_str=timezone_str,
            city="Transit Location"
        )

        # Get natal planets from birth chart
        natal_planets = birth_chart.get("planets", {})
        transit_planets = transit_chart.get("planets", {})

        # Find significant aspects between transits and natal
        transit_aspects = self._find_transit_aspects(
            natal_planets=natal_planets,
            transit_planets=transit_planets
        )

        # Find planets changing signs soon
        sign_changes = self._find_upcoming_sign_changes(
            transit_planets=transit_planets,
            days_ahead=30
        )

        # Identify house transits (which house is each transit planet in?)
        house_transits = self._identify_house_transits(
            birth_chart=birth_chart,
            transit_planets=transit_planets
        )

        # Calculate transit strength
        strength_analysis = self._analyze_transit_strength(
            transit_aspects=transit_aspects,
            house_transits=house_transits
        )

        return {
            "transit_date": transit_date.isoformat(),
            "transit_planets": {
                planet: {
                    "sign": data.get("sign"),
                    "degree": data.get("degree"),  # Degree within sign (0-30)
                    "longitude": data.get("longitude"),  # Absolute position (0-360)
                    "house": data.get("house"),
                    "retrograde": data.get("retrograde", False)
                }
                for planet, data in transit_planets.items()
            },
            "significant_aspects": transit_aspects,
            "upcoming_sign_changes": sign_changes,
            "house_transits": house_transits,
            "strength_analysis": strength_analysis,
            "summary": self._generate_transit_summary(
                transit_aspects=transit_aspects,
                house_transits=house_transits,
                sign_changes=sign_changes
            )
        }

    def calculate_transit_timeline(
        self,
        birth_chart: Dict[str, Any],
        start_date: datetime,
        end_date: datetime,
        latitude: float = 0.0,
        longitude: float = 0.0,
        timezone_str: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Calculate transit timeline for a date range

        Args:
            birth_chart: Birth chart data
            start_date: Start of timeline
            end_date: End of timeline
            latitude: Observer latitude
            longitude: Observer longitude
            timezone_str: Timezone

        Returns:
            Dictionary with significant events in timeline
        """
        print(f"📅 Calculating transit timeline: {start_date.date()} to {end_date.date()}")

        timeline_events = []
        current_date = start_date

        # Sample every 3 days
        while current_date <= end_date:
            transits = self.calculate_current_transits(
                birth_chart=birth_chart,
                transit_date=current_date,
                latitude=latitude,
                longitude=longitude,
                timezone_str=timezone_str
            )

            # Add significant aspects to timeline
            for aspect in transits["significant_aspects"]:
                if aspect["strength"] in ["very_strong", "strong"]:
                    timeline_events.append({
                        "date": current_date.date().isoformat(),
                        "type": "aspect",
                        "description": f"{aspect['transit_planet']} {aspect['aspect']} natal {aspect['natal_planet']}",
                        "strength": aspect["strength"],
                        "effect": aspect["interpretation"]
                    })

            # Add sign changes to timeline
            for change in transits["upcoming_sign_changes"]:
                timeline_events.append({
                    "date": change["date"],
                    "type": "sign_change",
                    "description": f"{change['planet']} enters {change['new_sign']}",
                    "current_sign": change["current_sign"],
                    "new_sign": change["new_sign"]
                })

            current_date += timedelta(days=3)

        # Sort by date
        timeline_events.sort(key=lambda x: x["date"])

        return {
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "total_events": len(timeline_events),
            "events": timeline_events[:50]  # Limit to 50 most significant
        }

    def _find_transit_aspects(
        self,
        natal_planets: Dict[str, Any],
        transit_planets: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find significant aspects between transiting and natal planets"""
        aspects = []

        for transit_planet, transit_data in transit_planets.items():
            transit_position = transit_data.get("longitude", 0)
            if transit_position is None:
                transit_position = 0

            for natal_planet, natal_data in natal_planets.items():
                natal_position = natal_data.get("longitude", 0)
                if natal_position is None:
                    natal_position = 0

                # Calculate angular separation
                separation = abs(transit_position - natal_position)

                # Normalize to 0-180 degrees
                if separation > 180:
                    separation = 360 - separation

                # Check for each aspect type
                for aspect_name, orb in self.aspect_orbs.items():
                    aspect_angle = self._get_aspect_angle(aspect_name)

                    # Calculate difference from exact aspect
                    diff = abs(separation - aspect_angle)

                    if diff <= orb:
                        # Aspect found!
                        strength = self._calculate_aspect_strength(diff, orb)

                        aspects.append({
                            "transit_planet": transit_planet,
                            "natal_planet": natal_planet,
                            "aspect": aspect_name,
                            "orb": round(diff, 2),
                            "strength": strength,
                            "transit_sign": transit_data.get("sign"),
                            "natal_sign": natal_data.get("sign"),
                            "interpretation": self._interpret_transit_aspect(
                                transit_planet=transit_planet,
                                natal_planet=natal_planet,
                                aspect=aspect_name
                            )
                        })

        # Sort by strength (strongest first)
        aspects.sort(key=lambda x: (
            {"very_strong": 4, "strong": 3, "moderate": 2, "weak": 1}.get(x["strength"], 0)
        ), reverse=True)

        return aspects

    def _find_upcoming_sign_changes(
        self,
        transit_planets: Dict[str, Any],
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """Find planets changing signs in next N days"""
        sign_changes = []

        # Note: This is a simplified version
        # A full implementation would use Swiss Ephemeris to calculate exact times

        for planet, data in transit_planets.items():
            current_sign = data.get("sign")
            current_degree = data.get("degree", 0)  # Degree within sign (0-30)
            if current_degree is None:
                current_degree = 0

            # If planet is in last 5 degrees of sign, it's changing soon
            if current_degree >= 25:
                next_sign = self._get_next_sign(current_sign)

                # Estimate days until sign change (rough approximation)
                degrees_to_change = 30 - current_degree
                avg_speed = self._get_average_daily_speed(planet)

                if avg_speed > 0:
                    days_until = degrees_to_change / avg_speed

                    if days_until <= days_ahead:
                        sign_changes.append({
                            "planet": planet,
                            "current_sign": current_sign,
                            "new_sign": next_sign,
                            "days_until": round(days_until, 1),
                            "date": (datetime.now() + timedelta(days=days_until)).date().isoformat()
                        })

        # Sort by soonest first
        sign_changes.sort(key=lambda x: x["days_until"])

        return sign_changes

    def _identify_house_transits(
        self,
        birth_chart: Dict[str, Any],
        transit_planets: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify which natal house each transit planet is in"""
        house_transits = []

        # Get house cusps from birth chart
        houses = birth_chart.get("houses", {})

        for planet, data in transit_planets.items():
            transit_degree = data.get("longitude", 0)
            if transit_degree is None:
                transit_degree = 0

            # Find which house this degree falls in
            house_num = self._find_house_for_degree(transit_degree, houses)

            if house_num:
                house_transits.append({
                    "planet": planet,
                    "sign": data.get("sign"),
                    "house": house_num,
                    "meaning": self.house_meanings.get(house_num, "unknown"),
                    "interpretation": f"{planet} transiting your {self._ordinal(house_num)} house affects: {self.house_meanings.get(house_num, 'unknown')}"
                })

        return house_transits

    def _analyze_transit_strength(
        self,
        transit_aspects: List[Dict[str, Any]],
        house_transits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze overall strength and themes of current transits"""

        # Count aspects by type
        aspect_counts = {}
        for aspect in transit_aspects:
            aspect_type = aspect["aspect"]
            aspect_counts[aspect_type] = aspect_counts.get(aspect_type, 0) + 1

        # Identify strongest aspect
        strongest_aspect = transit_aspects[0] if transit_aspects else None

        # Count house emphasis
        house_counts = {}
        for transit in house_transits:
            house = transit["house"]
            house_counts[house] = house_counts.get(house, 0) + 1

        # Find most emphasized house
        emphasized_house = max(house_counts.items(), key=lambda x: x[1])[0] if house_counts else None

        return {
            "total_aspects": len(transit_aspects),
            "aspect_breakdown": aspect_counts,
            "strongest_aspect": {
                "description": f"{strongest_aspect['transit_planet']} {strongest_aspect['aspect']} {strongest_aspect['natal_planet']}",
                "strength": strongest_aspect["strength"]
            } if strongest_aspect else None,
            "most_emphasized_house": {
                "house": emphasized_house,
                "planet_count": house_counts.get(emphasized_house, 0),
                "meaning": self.house_meanings.get(emphasized_house, "unknown")
            } if emphasized_house else None
        }

    def _generate_transit_summary(
        self,
        transit_aspects: List[Dict[str, Any]],
        house_transits: List[Dict[str, Any]],
        sign_changes: List[Dict[str, Any]]
    ) -> str:
        """Generate human-readable transit summary"""
        summary_parts = []

        # Strongest aspects
        strong_aspects = [a for a in transit_aspects if a["strength"] in ["very_strong", "strong"]]
        if strong_aspects:
            summary_parts.append(f"🌟 {len(strong_aspects)} significant aspects active")

        # Sign changes
        if sign_changes:
            upcoming = sign_changes[0]
            summary_parts.append(
                f"🔄 {upcoming['planet']} enters {upcoming['new_sign']} in {upcoming['days_until']} days"
            )

        # House emphasis
        if house_transits:
            house_summary = f"🏠 Focus on houses: {', '.join([str(t['house']) for t in house_transits[:3]])}"
            summary_parts.append(house_summary)

        return " | ".join(summary_parts) if summary_parts else "No significant transits at this time"

    # Helper methods

    def _get_aspect_angle(self, aspect_name: str) -> float:
        """Get the angle for an aspect type"""
        angles = {
            "conjunction": 0,
            "opposition": 180,
            "trine": 120,
            "square": 90,
            "sextile": 60,
        }
        return angles.get(aspect_name, 0)

    def _calculate_aspect_strength(self, diff: float, orb: float) -> str:
        """Calculate aspect strength based on orb"""
        percentage = (diff / orb) * 100

        if percentage <= 25:
            return "very_strong"
        elif percentage <= 50:
            return "strong"
        elif percentage <= 75:
            return "moderate"
        else:
            return "weak"

    def _interpret_transit_aspect(
        self,
        transit_planet: str,
        natal_planet: str,
        aspect: str
    ) -> str:
        """Generate interpretation for transit aspect"""
        aspect_meaning = self.aspect_meanings.get(aspect, "interaction")

        interpretations = {
            ("Sun", "Sun"): f"Focus on identity and self-expression through {aspect_meaning}",
            ("Moon", "Moon"): f"Emotional cycles and inner reflection through {aspect_meaning}",
            ("Jupiter", "Sun"): f"Growth, optimism, and opportunities through {aspect_meaning}",
            ("Saturn", "Sun"): f"Discipline, responsibility, and structure through {aspect_meaning}",
            ("Jupiter", "Moon"): f"Emotional expansion and good fortune through {aspect_meaning}",
            ("Saturn", "Moon"): f"Emotional maturity and serious reflection through {aspect_meaning}",
            ("Mars", "Mars"): f"Energy, assertion, and drive through {aspect_meaning}",
            ("Venus", "Venus"): f"Love, beauty, and relationships through {aspect_meaning}",
        }

        key = (transit_planet, natal_planet)
        return interpretations.get(key, f"{transit_planet} activating natal {natal_planet} through {aspect_meaning}")

    def _get_next_sign(self, current_sign: str) -> str:
        """Get the next zodiac sign"""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]

        try:
            current_index = signs.index(current_sign)
            return signs[(current_index + 1) % 12]
        except ValueError:
            return "Unknown"

    def _get_average_daily_speed(self, planet: str) -> float:
        """Get average daily motion for a planet (in degrees)"""
        speeds = {
            "Sun": 1.0,
            "Moon": 13.0,
            "Mercury": 1.5,
            "Venus": 1.2,
            "Mars": 0.5,
            "Jupiter": 0.08,
            "Saturn": 0.03,
            "Rahu": -0.05,  # Retrograde motion
            "Ketu": -0.05,
        }
        return speeds.get(planet, 0.5)

    def _find_house_for_degree(
        self,
        degree: float,
        houses: Any
    ) -> Optional[int]:
        """Find which house a degree falls in"""
        # Houses can be a list or dict
        if isinstance(houses, list):
            # For whole sign houses (Vedic), match by sign
            # Calculate which sign the degree is in
            sign_num = int(degree / 30)

            # Find the house with this sign
            for house in houses:
                if isinstance(house, dict) and house.get('sign_num') == sign_num:
                    return house.get('house_num', 1)

            # Fallback: return based on position relative to houses
            return (sign_num % 12) + 1

        elif isinstance(houses, dict):
            # Legacy dict format
            house_positions = []

            for house_num in range(1, 13):
                house_data = houses.get(str(house_num), {})
                if isinstance(house_data, dict):
                    cusp_degree = house_data.get("position", 0)
                    house_positions.append((house_num, cusp_degree))
                elif isinstance(house_data, (int, float)):
                    house_positions.append((house_num, house_data))

            if not house_positions:
                return 1

            # Sort by degree
            house_positions.sort(key=lambda x: x[1])

            # Find which house the degree falls in
            for i in range(len(house_positions)):
                house_num, cusp_degree = house_positions[i]
                next_cusp = house_positions[(i + 1) % 12][1]

                # Handle wraparound at 360/0
                if next_cusp < cusp_degree:
                    if degree >= cusp_degree or degree < next_cusp:
                        return house_num
                else:
                    if cusp_degree <= degree < next_cusp:
                        return house_num

        return 1  # Default to 1st house

    def _ordinal(self, n: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"


# Singleton instance
transit_service = TransitService()
