"""
Transit and Sade Sati Calculation Service
Calculates current planetary transits and Sade Sati periods
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
import swisseph as swe


class TransitService:
    """Calculate planetary transits and Sade Sati"""

    SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    # Transit planets to track
    TRANSIT_PLANETS = {
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE,
        "Ketu": swe.MEAN_NODE  # Ketu is 180° from Rahu
    }

    def __init__(self):
        """Initialize with Lahiri ayanamsa"""
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    def get_current_transits(
        self,
        natal_moon_sign: int,
        natal_ascendant_sign: int,
        reference_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate current planetary transits

        Args:
            natal_moon_sign: Birth Moon sign (0-11)
            natal_ascendant_sign: Birth Ascendant sign (0-11)
            reference_date: Date to calculate transits for (default: today)

        Returns:
            Dictionary with current transit positions and their effects
        """
        if reference_date is None:
            reference_date = date.today()

        # Calculate Julian Day for reference date
        jd = swe.julday(reference_date.year, reference_date.month, reference_date.day, 12.0)

        # Get ayanamsa
        ayanamsa = swe.get_ayanamsa_ut(jd)

        transits = {}

        # Calculate position for each transit planet
        for planet_name, planet_id in self.TRANSIT_PLANETS.items():
            if planet_name == "Ketu":
                continue  # Calculate Ketu from Rahu

            # Calculate tropical position
            result = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)
            tropical_long = result[0][0]

            # Convert to sidereal
            sidereal_long = (tropical_long - ayanamsa) % 360
            sign_num = int(sidereal_long / 30)
            degree = sidereal_long % 30

            # Calculate house from Moon (Chandra Lagna)
            house_from_moon = ((sign_num - natal_moon_sign) % 12) + 1

            # Calculate house from Ascendant (Lagna)
            house_from_lagna = ((sign_num - natal_ascendant_sign) % 12) + 1

            transits[planet_name] = {
                "sign": self.SIGNS[sign_num],
                "sign_num": sign_num,
                "degree": round(degree, 2),
                "longitude": round(sidereal_long, 2),
                "house_from_moon": house_from_moon,
                "house_from_lagna": house_from_lagna,
                "effects": self._get_transit_effects(planet_name, house_from_moon)
            }

        # Calculate Ketu (180° from Rahu)
        if "Rahu" in transits:
            rahu_long = transits["Rahu"]["longitude"]
            ketu_long = (rahu_long + 180) % 360
            ketu_sign = int(ketu_long / 30)
            ketu_degree = ketu_long % 30

            ketu_house_from_moon = ((ketu_sign - natal_moon_sign) % 12) + 1
            ketu_house_from_lagna = ((ketu_sign - natal_ascendant_sign) % 12) + 1

            transits["Ketu"] = {
                "sign": self.SIGNS[ketu_sign],
                "sign_num": ketu_sign,
                "degree": round(ketu_degree, 2),
                "longitude": round(ketu_long, 2),
                "house_from_moon": ketu_house_from_moon,
                "house_from_lagna": ketu_house_from_lagna,
                "effects": self._get_transit_effects("Ketu", ketu_house_from_moon)
            }

        return {
            "reference_date": reference_date.isoformat(),
            "transits": transits,
            "significant_transits": self._identify_significant_transits(transits)
        }

    def _get_transit_effects(self, planet: str, house_from_moon: int) -> str:
        """Get effects of planet transit through house from Moon"""
        effects = {
            "Jupiter": {
                1: "Good health, self-confidence, new beginnings",
                2: "Wealth gains, family harmony",
                3: "Success through efforts, courage",
                4: "Property gains, domestic happiness",
                5: "Children's success, creativity, speculation gains",
                6: "Victory over enemies, health improvement",
                7: "Marriage/partnership benefits, travel",
                8: "Some challenges, but protected from major issues",
                9: "Luck, spiritual growth, father's well-being",
                10: "Career advancement, recognition",
                11: "Income increase, gains from all sources",
                12: "Spiritual growth, foreign gains, but expenses increase"
            },
            "Saturn": {
                1: "Physical challenges, delays, need patience",
                2: "Financial stress, family tensions",
                3: "Hard work required, courage tested",
                4: "Property issues, mother's health concerns",
                5: "Children's challenges, speculation loss",
                6: "Victory over enemies, health issues resolve",
                7: "Partnership delays, marital stress",
                8: "Major challenges, health concerns, transformation",
                9: "Father's challenges, spiritual tests",
                10: "Career obstacles, authority issues",
                11: "Delayed gains, need persistent effort",
                12: "Expenses, losses, spiritual growth through hardship"
            },
            "Rahu": {
                1: "Mental confusion, identity crisis",
                2: "Speech issues, family discord",
                3: "Increased ambition, sibling issues",
                4: "Property complications, emotional turmoil",
                5: "Speculative losses, children's issues",
                6: "Victory over enemies, but stress",
                7: "Relationship complications, foreign influence",
                8: "Sudden changes, health concerns",
                9: "Religious/philosophical challenges",
                10: "Career changes, unconventional success",
                11: "Unexpected gains, unusual friendships",
                12: "Expenses, foreign travel, spiritual confusion"
            },
            "Ketu": {
                1: "Detachment, spiritual seeking",
                2: "Speech issues, family detachment",
                3: "Reduced efforts, introspection",
                4: "Property detachment, emotional distance",
                5: "Children's separation, creative blocks",
                6: "Liberation from enemies, health recovery",
                7: "Partnership detachment, isolation",
                8: "Spiritual transformation, sudden changes",
                9: "Spiritual awakening, pilgrimages",
                10: "Career detachment, spiritual focus",
                11: "Reduced social interaction, losses",
                12: "Spiritual elevation, liberation, expenses"
            }
        }

        return effects.get(planet, {}).get(house_from_moon, "Mixed results")

    def _identify_significant_transits(self, transits: Dict[str, Any]) -> List[str]:
        """Identify particularly significant transits"""
        significant = []

        jupiter = transits.get("Jupiter", {})
        saturn = transits.get("Saturn", {})

        # Jupiter in trine (1, 5, 9) from Moon
        if jupiter.get("house_from_moon") in [1, 5, 9]:
            significant.append(f"Jupiter in favorable {jupiter.get('house_from_moon')}th house from Moon")

        # Saturn in 3, 6, 11 (favorable houses)
        if saturn.get("house_from_moon") in [3, 6, 11]:
            significant.append(f"Saturn in favorable {saturn.get('house_from_moon')}th house from Moon")

        return significant if significant else ["No particularly significant transits at this time"]

    def calculate_sade_sati(
        self,
        natal_moon_sign: int,
        reference_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Calculate Sade Sati (7.5-year Saturn transit period)"""
        if reference_date is None:
            reference_date = date.today()

        # Get current Saturn position
        jd = swe.julday(reference_date.year, reference_date.month, reference_date.day, 12.0)
        ayanamsa = swe.get_ayanamsa_ut(jd)

        result = swe.calc_ut(jd, swe.SATURN, swe.FLG_SWIEPH)
        tropical_long = result[0][0]
        sidereal_long = (tropical_long - ayanamsa) % 360
        saturn_sign = int(sidereal_long / 30)

        # Calculate which house Saturn is transiting from Moon
        house_from_moon = ((saturn_sign - natal_moon_sign) % 12) + 1

        # Determine Sade Sati status
        in_sade_sati = house_from_moon in [12, 1, 2]

        if in_sade_sati:
            if house_from_moon == 12:
                phase = "Rising (1st phase)"
                severity = "Medium"
            elif house_from_moon == 1:
                phase = "Peak (2nd phase)"
                severity = "High"
            else:
                phase = "Setting (3rd phase)"
                severity = "Medium"
        else:
            phase = "Not in Sade Sati"
            severity = "None"

        return {
            "in_sade_sati": in_sade_sati,
            "phase": phase,
            "severity": severity,
            "saturn_current_sign": self.SIGNS[saturn_sign],
            "saturn_house_from_moon": house_from_moon,
            "natal_moon_sign": self.SIGNS[natal_moon_sign],
            "remedies": [
                "Worship Lord Hanuman every Tuesday and Saturday",
                "Recite Hanuman Chalisa daily",
                "Offer mustard oil to Saturn on Saturdays",
                "Donate black items on Saturdays"
            ] if in_sade_sati else []
        }


# Singleton instance
transit_service = TransitService()
