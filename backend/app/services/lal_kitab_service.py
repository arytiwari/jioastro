"""
Lal Kitab Astrology Service

Implements Lal Kitab system analysis including:
- Planetary debts (Rins) detection
- Blind planets identification
- Exalted enemy positions
- Pakka Ghar (permanent house) analysis
- Practical remedies (Totke)

Author: JioAstro Team
Date: January 2025
"""

from typing import Dict, List, Any, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)


class LalKitabService:
    """
    Singleton service for Lal Kitab astrology calculations.

    Lal Kitab is a unique system that focuses on karmic debts,
    blind planets, and simple practical remedies.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LalKitabService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True

        # Pakka Ghar (Permanent Houses) for each planet
        self.PAKKA_GHAR = {
            "Sun": 1,
            "Moon": 4,
            "Mars": 3,
            "Mercury": 7,
            "Jupiter": 5,
            "Venus": 7,
            "Saturn": 10,
            "Rahu": 12,
            "Ketu": 8
        }

        # Planet exaltation signs
        self.EXALTATION_SIGNS = {
            "Sun": 1,      # Aries
            "Moon": 2,     # Taurus
            "Mars": 10,    # Capricorn
            "Mercury": 6,  # Virgo
            "Jupiter": 4,  # Cancer
            "Venus": 12,   # Pisces
            "Saturn": 7,   # Libra
            "Rahu": 3,     # Gemini (per some traditions)
            "Ketu": 9      # Sagittarius
        }

        # Planet debilitation signs
        self.DEBILITATION_SIGNS = {
            "Sun": 7,      # Libra
            "Moon": 8,     # Scorpio
            "Mars": 4,     # Cancer
            "Mercury": 12, # Pisces
            "Jupiter": 10, # Capricorn
            "Venus": 6,    # Virgo
            "Saturn": 1,   # Aries
            "Rahu": 9,     # Sagittarius
            "Ketu": 3      # Gemini
        }

        # Sign lordships
        self.SIGN_LORDS = {
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

        # Planet friendships
        self.PLANET_FRIENDS = {
            "Sun": ["Moon", "Mars", "Jupiter"],
            "Moon": ["Sun", "Mercury"],
            "Mars": ["Sun", "Moon", "Jupiter"],
            "Mercury": ["Sun", "Venus"],
            "Jupiter": ["Sun", "Moon", "Mars"],
            "Venus": ["Mercury", "Saturn"],
            "Saturn": ["Mercury", "Venus"],
            "Rahu": ["Venus", "Saturn"],
            "Ketu": ["Mars", "Jupiter"]
        }

        self.PLANET_ENEMIES = {
            "Sun": ["Venus", "Saturn"],
            "Moon": ["Rahu", "Ketu"],
            "Mars": ["Mercury"],
            "Mercury": ["Moon"],
            "Jupiter": ["Mercury", "Venus"],
            "Venus": ["Sun", "Moon"],
            "Saturn": ["Sun", "Moon", "Mars"],
            "Rahu": ["Sun", "Moon", "Mars"],
            "Ketu": ["Sun", "Moon"]
        }

        logger.info("LalKitabService initialized")

    # ==================== Planetary Debts Detection ====================

    def detect_planetary_debts(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect all planetary debts (Rins) in the chart.

        Args:
            chart: Birth chart data with planet positions

        Returns:
            Dictionary containing all detected debts with details
        """
        debts = []
        planets = chart.get("planets", {})

        # Check each planet for debt conditions
        for planet_name, planet_data in planets.items():
            if planet_name in ["Ascendant", "MC"]:
                continue

            debt_info = self._check_planet_debt(planet_name, planet_data, chart)
            if debt_info:
                debts.append(debt_info)

        # Calculate overall severity
        severity_counts = {"low": 0, "medium": 0, "high": 0}
        for debt in debts:
            severity_counts[debt["severity"]] += 1

        if severity_counts["high"] > 0:
            overall_severity = "high"
        elif severity_counts["medium"] > 1:
            overall_severity = "high"
        elif severity_counts["medium"] > 0:
            overall_severity = "medium"
        else:
            overall_severity = "low"

        return {
            "debts": debts,
            "total_debts": len(debts),
            "overall_severity": overall_severity,
            "severity_breakdown": severity_counts
        }

    def _check_planet_debt(self, planet: str, planet_data: Dict[str, Any],
                          chart: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if a specific planet indicates a karmic debt."""
        house = planet_data.get("house", 0)
        sign = planet_data.get("sign_num", 0)

        debt_info = None

        # Sun - Father's Debt
        if planet == "Sun":
            if house in [5, 9] or self._is_with_rahu(planet, chart):
                debt_info = {
                    "type": "Father's Debt (Pitra Rin)",
                    "planet": "Sun",
                    "house": house,
                    "reason": self._get_debt_reason(planet, house, chart),
                    "manifestation": "Issues with father, authority figures, government, ego problems",
                    "remedies": self.get_remedies_for_debt("father")
                }

        # Moon - Mother's Debt
        elif planet == "Moon":
            if house in [4, 8] or sign == self.DEBILITATION_SIGNS.get("Moon") or \
               self._is_with_rahu(planet, chart):
                debt_info = {
                    "type": "Mother's Debt (Matri Rin)",
                    "planet": "Moon",
                    "house": house,
                    "reason": self._get_debt_reason(planet, house, chart),
                    "manifestation": "Emotional instability, mother issues, home conflicts, mental stress",
                    "remedies": self.get_remedies_for_debt("mother")
                }

        # Mars - Brother's Debt
        elif planet == "Mars":
            if house in [3, 6] or self._is_with_rahu(planet, chart):
                debt_info = {
                    "type": "Brother's Debt (Bhratri Rin)",
                    "planet": "Mars",
                    "house": house,
                    "reason": self._get_debt_reason(planet, house, chart),
                    "manifestation": "Sibling conflicts, lack of courage, aggression, property disputes",
                    "remedies": self.get_remedies_for_debt("brother")
                }

        # Mercury - Sister's Debt / Communication Debt
        elif planet == "Mercury":
            if house in [3, 7] or self._is_with_rahu(planet, chart) or \
               self._is_combust(planet, chart):
                debt_info = {
                    "type": "Sister's Debt / Communication Debt",
                    "planet": "Mercury",
                    "house": house,
                    "reason": self._get_debt_reason(planet, house, chart),
                    "manifestation": "Communication problems, business failures, sibling issues, education blocks",
                    "remedies": self.get_remedies_for_debt("sister")
                }

        # Jupiter - Guru's Debt / Knowledge Debt
        elif planet == "Jupiter":
            if house in [5, 9] or sign == self.DEBILITATION_SIGNS.get("Jupiter") or \
               self._is_with_rahu(planet, chart):
                debt_info = {
                    "type": "Guru's Debt / Knowledge Debt (Guru Rin)",
                    "planet": "Jupiter",
                    "house": house,
                    "reason": self._get_debt_reason(planet, house, chart),
                    "manifestation": "Teacher problems, blocked wisdom, financial issues, childlessness",
                    "remedies": self.get_remedies_for_debt("guru")
                }

        # Venus - Wife's Debt / Relationship Debt
        elif planet == "Venus":
            if house in [7, 12] or self._is_with_rahu(planet, chart):
                debt_info = {
                    "type": "Wife's Debt / Relationship Debt (Stri Rin)",
                    "planet": "Venus",
                    "house": house,
                    "reason": self._get_debt_reason(planet, house, chart),
                    "manifestation": "Relationship problems, lack of luxury, artistic blocks, spouse issues",
                    "remedies": self.get_remedies_for_debt("wife")
                }

        # Saturn - Ancestor's Debt / Service Debt
        elif planet == "Saturn":
            if house in [8, 10] or self._is_with_rahu(planet, chart):
                debt_info = {
                    "type": "Ancestor's Debt / Service Debt (Pitra Dosha)",
                    "planet": "Saturn",
                    "house": house,
                    "reason": self._get_debt_reason(planet, house, chart),
                    "manifestation": "Karmic burdens, delays, obstacles, chronic health issues, poverty",
                    "remedies": self.get_remedies_for_debt("ancestor")
                }

        # Calculate severity if debt found
        if debt_info:
            debt_info["severity"] = self.calculate_debt_severity(debt_info, planet_data, chart)

        return debt_info

    def _get_debt_reason(self, planet: str, house: int, chart: Dict[str, Any]) -> str:
        """Get the specific reason for the debt."""
        reasons = []

        planets = chart.get("planets", {})
        planet_data = planets.get(planet, {})
        sign = planet_data.get("sign_num", 0)

        # Check various debt-causing conditions
        if self._is_with_rahu(planet, chart):
            reasons.append(f"{planet} conjunct with Rahu")

        if sign == self.DEBILITATION_SIGNS.get(planet):
            reasons.append(f"{planet} debilitated in {planet_data.get('sign', '')}")

        if planet_data.get("is_retrograde", False):
            reasons.append(f"{planet} retrograde (past life carryover)")

        # Specific house-based reasons
        debt_houses = {
            "Sun": [5, 9],
            "Moon": [4, 8],
            "Mars": [3, 6],
            "Mercury": [3, 7],
            "Jupiter": [5, 9],
            "Venus": [7, 12],
            "Saturn": [8, 10]
        }

        if house in debt_houses.get(planet, []):
            reasons.append(f"{planet} in {house}th house (debt house)")

        if self._is_combust(planet, chart):
            reasons.append(f"{planet} combust by Sun")

        return " | ".join(reasons) if reasons else f"{planet} in {house}th house"

    def calculate_debt_severity(self, debt_info: Dict[str, Any],
                                planet_data: Dict[str, Any],
                                chart: Dict[str, Any]) -> str:
        """
        Calculate debt severity: low, medium, or high.

        Factors:
        - Multiple debt indicators = higher severity
        - Retrograde = +1
        - Debilitated = +1
        - With Rahu = +1
        - Combust = +1
        """
        severity_score = 0

        # Count reasons
        reasons = debt_info.get("reason", "")
        severity_score += len(reasons.split("|"))

        # Additional factors
        if planet_data.get("is_retrograde", False):
            severity_score += 1

        if self._is_with_rahu(debt_info["planet"], chart):
            severity_score += 1

        # Determine severity level
        if severity_score >= 4:
            return "high"
        elif severity_score >= 2:
            return "medium"
        else:
            return "low"

    def _is_with_rahu(self, planet: str, chart: Dict[str, Any]) -> bool:
        """Check if planet is in same house as Rahu."""
        planets = chart.get("planets", {})
        planet_house = planets.get(planet, {}).get("house", 0)
        rahu_house = planets.get("Rahu", {}).get("house", 0)
        return planet_house == rahu_house and planet_house != 0

    def _is_combust(self, planet: str, chart: Dict[str, Any]) -> bool:
        """Check if planet is combust (too close to Sun)."""
        if planet == "Sun":
            return False

        planets = chart.get("planets", {})
        planet_data = planets.get(planet, {})
        sun_data = planets.get("Sun", {})

        planet_long = planet_data.get("longitude", 0)
        sun_long = sun_data.get("longitude", 0)

        # Calculate angular distance
        diff = abs(planet_long - sun_long)
        if diff > 180:
            diff = 360 - diff

        # Combustion degrees
        combustion_orbs = {
            "Moon": 12,
            "Mars": 17,
            "Mercury": 14,
            "Jupiter": 11,
            "Venus": 10,
            "Saturn": 15
        }

        return diff < combustion_orbs.get(planet, 0)

    # ==================== Blind Planets Detection ====================

    def detect_blind_planets(self, chart: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect all blind planets (Andhe Graha) in the chart.

        A planet becomes blind when it loses ability to give results.
        """
        blind_planets = []
        planets = chart.get("planets", {})

        for planet_name, planet_data in planets.items():
            if planet_name in ["Ascendant", "MC"]:
                continue

            if self.is_planet_blind(planet_name, chart):
                blind_info = {
                    "planet": planet_name,
                    "house": planet_data.get("house", 0),
                    "reason": self.get_blindness_reason(planet_name, chart),
                    "effects": self._get_blindness_effects(planet_name),
                    "remedies": self.get_remedies_for_blind_planet(planet_name)
                }
                blind_planets.append(blind_info)

        return blind_planets

    def is_planet_blind(self, planet: str, chart: Dict[str, Any]) -> bool:
        """Check if a specific planet is blind."""
        planets = chart.get("planets", {})
        planet_data = planets.get(planet, {})
        house = planet_data.get("house", 0)
        sign = planet_data.get("sign_num", 0)

        # 8th house makes most planets blind
        if house == 8:
            return True

        # Planet-specific blindness conditions
        if planet == "Sun":
            # Sun blind if with Saturn or in 8th
            return self._is_with_planet(planet, "Saturn", chart)

        elif planet == "Moon":
            # Moon blind if in 8th, dark fortnight, or with Rahu/Ketu
            return (self._is_with_rahu(planet, chart) or
                   self._is_with_planet(planet, "Ketu", chart))

        elif planet == "Mars":
            # Mars blind in 8th or 12th or with Saturn
            return house == 12 or self._is_with_planet(planet, "Saturn", chart)

        elif planet == "Mercury":
            # Mercury blind if combust (within 14° of Sun)
            return self._is_combust(planet, chart)

        elif planet == "Jupiter":
            # Jupiter blind in 8th, with Rahu, or debilitated
            return (self._is_with_rahu(planet, chart) or
                   sign == self.DEBILITATION_SIGNS.get("Jupiter"))

        elif planet == "Venus":
            # Venus blind in 8th, 6th, or with malefics
            return house == 6

        elif planet == "Saturn":
            # Saturn blind in 8th or debilitated
            return sign == self.DEBILITATION_SIGNS.get("Saturn")

        elif planet == "Rahu":
            # Rahu blind in 8th or with Moon (Grahan Yoga)
            return self._is_with_planet(planet, "Moon", chart)

        elif planet == "Ketu":
            # Ketu blind in 8th or with Sun
            return self._is_with_planet(planet, "Sun", chart)

        return False

    def get_blindness_reason(self, planet: str, chart: Dict[str, Any]) -> str:
        """Get specific reason why planet is blind."""
        planets = chart.get("planets", {})
        planet_data = planets.get(planet, {})
        house = planet_data.get("house", 0)
        sign = planet_data.get("sign_num", 0)

        reasons = []

        if house == 8:
            reasons.append(f"{planet} in 8th house")

        if house == 12 and planet == "Mars":
            reasons.append(f"{planet} in 12th house")

        if house == 6 and planet == "Venus":
            reasons.append(f"{planet} in 6th house")

        if self._is_combust(planet, chart):
            reasons.append(f"{planet} combust by Sun")

        if self._is_with_rahu(planet, chart):
            reasons.append(f"{planet} with Rahu")

        if self._is_with_planet(planet, "Ketu", chart):
            reasons.append(f"{planet} with Ketu")

        if self._is_with_planet(planet, "Saturn", chart) and planet != "Saturn":
            reasons.append(f"{planet} with Saturn")

        if sign == self.DEBILITATION_SIGNS.get(planet):
            reasons.append(f"{planet} debilitated")

        return " | ".join(reasons) if reasons else "Unknown blindness condition"

    def _get_blindness_effects(self, planet: str) -> List[str]:
        """Get effects of blind planet."""
        effects_map = {
            "Sun": [
                "Weak self-confidence and vitality",
                "Problems with father and authority",
                "Leadership difficulties",
                "Government-related obstacles"
            ],
            "Moon": [
                "Emotional instability and mental stress",
                "Mother's health issues",
                "Home and property problems",
                "Blocked intuition"
            ],
            "Mars": [
                "Lack of courage and energy",
                "Property and sibling disputes",
                "Anger management issues",
                "Surgical complications"
            ],
            "Mercury": [
                "Communication and speech problems",
                "Business and trade failures",
                "Education obstacles",
                "Nervous system issues"
            ],
            "Jupiter": [
                "Blocked wisdom and knowledge",
                "Teacher and mentor problems",
                "Financial instability",
                "Issues with children"
            ],
            "Venus": [
                "Relationship and marriage problems",
                "Loss of luxury and comforts",
                "Artistic blocks",
                "Vehicle troubles"
            ],
            "Saturn": [
                "Extreme delays and obstacles",
                "Chronic health problems",
                "Service and job difficulties",
                "Loneliness and depression"
            ],
            "Rahu": [
                "Confusion and illusions",
                "Uncontrolled desires",
                "Foreign travel problems",
                "Addiction tendencies"
            ],
            "Ketu": [
                "Spiritual confusion",
                "Detachment issues",
                "Occult knowledge blocks",
                "Past life karma manifestations"
            ]
        }

        return effects_map.get(planet, ["General life obstacles"])

    def _is_with_planet(self, planet1: str, planet2: str, chart: Dict[str, Any]) -> bool:
        """Check if two planets are in same house."""
        planets = chart.get("planets", {})
        house1 = planets.get(planet1, {}).get("house", 0)
        house2 = planets.get(planet2, {}).get("house", 0)
        return house1 == house2 and house1 != 0

    # ==================== Exalted Enemies ====================

    def detect_exalted_enemies(self, chart: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect exalted planets in enemy houses.

        When exalted planet sits in enemy's house, creates conflict.
        """
        exalted_enemies = []
        planets = chart.get("planets", {})

        for planet_name, planet_data in planets.items():
            if planet_name in ["Ascendant", "MC", "Rahu", "Ketu"]:
                continue

            sign = planet_data.get("sign_num", 0)
            house = planet_data.get("house", 0)

            # Check if planet is exalted
            if sign == self.EXALTATION_SIGNS.get(planet_name):
                # Get house lord
                house_sign = self._get_house_sign(house, chart)
                house_lord = self.SIGN_LORDS.get(house_sign)

                # Check if house lord is enemy
                if house_lord in self.PLANET_ENEMIES.get(planet_name, []):
                    exalted_enemies.append({
                        "planet": planet_name,
                        "exalted_sign": planet_data.get("sign", ""),
                        "house": house,
                        "house_lord": house_lord,
                        "relationship": "enemy",
                        "effect": self._get_exalted_enemy_effect(planet_name, house_lord)
                    })

        return exalted_enemies

    def _get_house_sign(self, house: int, chart: Dict[str, Any]) -> int:
        """Get sign number of a specific house."""
        # Get ascendant sign
        planets = chart.get("planets", {})
        asc_sign = planets.get("Ascendant", {}).get("sign_num", 1)

        # Calculate house sign (houses progress sequentially from ascendant)
        house_sign = ((asc_sign - 1 + house - 1) % 12) + 1
        return house_sign

    def _get_exalted_enemy_effect(self, planet: str, enemy_lord: str) -> str:
        """Get effect description for exalted planet in enemy house."""
        effects = {
            ("Sun", "Venus"): "Leadership abilities undermined by relationship issues",
            ("Sun", "Saturn"): "Authority conflicts with delays and obstacles",
            ("Moon", "Mars"): "Emotional nature clashes with aggressive environment",
            ("Mars", "Saturn"): "Energy and action blocked by restrictions",
            ("Jupiter", "Mercury"): "Wisdom conflicts with commercial mentality",
            ("Venus", "Sun"): "Luxury and relationships affected by ego",
            ("Venus", "Moon"): "Artistic nature disturbed by emotional instability"
        }

        return effects.get((planet, enemy_lord),
                          f"{planet}'s positive qualities diminished by {enemy_lord}")

    # ==================== Pakka Ghar Analysis ====================

    def check_pakka_ghar_placement(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check which planets are in their Pakka Ghar (permanent house).

        Planets in Pakka Ghar give excellent results.
        """
        placements = {}
        planets = chart.get("planets", {})

        for planet_name, pakka_house in self.PAKKA_GHAR.items():
            planet_data = planets.get(planet_name, {})
            actual_house = planet_data.get("house", 0)

            in_pakka_ghar = (actual_house == pakka_house)

            if in_pakka_ghar:
                result = "excellent"
                description = f"{planet_name} in its permanent house - gives best results"
            else:
                result = "needs remedy"
                description = f"{planet_name} not in permanent house - may need support"

            placements[planet_name] = {
                "pakka_ghar": pakka_house,
                "actual_house": actual_house,
                "in_pakka_ghar": in_pakka_ghar,
                "result": result,
                "description": description
            }

        return placements

    # ==================== Remedies ====================

    def get_remedies_for_debt(self, debt_type: str) -> List[str]:
        """Get specific remedies for each debt type."""
        remedies = {
            "father": [
                "Offer water to Sun at sunrise with red flowers",
                "Respect father and elders, touch their feet",
                "Donate wheat, jaggery, copper on Sundays",
                "Avoid non-vegetarian food on Sundays",
                "Recite Aditya Hridayam or Gayatri Mantra"
            ],
            "mother": [
                "Keep silver items at home (coins, vessel)",
                "Serve mother with devotion, seek her blessings",
                "Donate white items (milk, rice, silver) on Mondays",
                "Avoid milk at night if Moon afflicted",
                "Float coconut in flowing water on Mondays"
            ],
            "brother": [
                "Feed monkeys or donate at Hanuman temple",
                "Help siblings, avoid conflicts",
                "Donate red lentils (masoor dal) on Tuesdays",
                "Recite Hanuman Chalisa daily",
                "Keep red coral or copper at home"
            ],
            "sister": [
                "Feed green grass to cows",
                "Respect maternal aunts and uncles",
                "Donate green items on Wednesdays",
                "Keep parrot or birds at home",
                "Float green items in river on Wednesdays"
            ],
            "guru": [
                "Visit temples regularly, especially on Thursdays",
                "Respect teachers, gurus, and learned people",
                "Donate yellow items (turmeric, chana dal, bananas)",
                "Plant and serve peepal tree",
                "Keep saffron or yellow items at home"
            ],
            "wife": [
                "Respect wife, serve women in family",
                "Donate white items (sugar, rice, milk) on Fridays",
                "Keep cow at home or feed cows regularly",
                "Avoid alcohol and immoral behavior",
                "Wear diamond or white sapphire (if suitable)"
            ],
            "ancestor": [
                "Feed crows daily (especially on Saturdays)",
                "Serve old people and laborers",
                "Donate black items (iron, sesame, black cloth) on Saturdays",
                "Light oil lamp under peepal tree on Saturdays",
                "Perform Shradh ceremony on appropriate dates",
                "Help poor and needy without expectation"
            ]
        }

        return remedies.get(debt_type, ["Consult qualified astrologer for specific remedies"])

    def get_remedies_for_blind_planet(self, planet: str) -> List[str]:
        """Get remedies to 'open the eyes' of blind planet."""
        remedies = {
            "Sun": [
                "Offer water to Sun at sunrise",
                "Donate wheat and jaggery on Sundays",
                "Wear ruby gemstone (after consultation)",
                "Respect father and government authorities"
            ],
            "Moon": [
                "Keep silver items at home",
                "Donate white items on Mondays",
                "Wear pearl (after consultation)",
                "Serve mother and elderly women"
            ],
            "Mars": [
                "Recite Hanuman Chalisa",
                "Donate red lentils on Tuesdays",
                "Wear red coral (after consultation)",
                "Feed monkeys or dogs"
            ],
            "Mercury": [
                "Feed green grass to cows",
                "Donate green items on Wednesdays",
                "Wear emerald (after consultation)",
                "Keep parrot or birds"
            ],
            "Jupiter": [
                "Visit temples on Thursdays",
                "Donate yellow items (bananas, turmeric)",
                "Wear yellow sapphire (after consultation)",
                "Respect teachers and gurus"
            ],
            "Venus": [
                "Feed cows and donate sugar",
                "Donate white items on Fridays",
                "Wear diamond or white sapphire (after consultation)",
                "Respect women and wife"
            ],
            "Saturn": [
                "Feed crows and serve old people",
                "Donate black items on Saturdays",
                "Wear blue sapphire (after consultation)",
                "Light oil lamp under peepal tree"
            ],
            "Rahu": [
                "Feed dogs daily",
                "Donate blue/black items on Saturdays",
                "Keep silver elephant at home",
                "Avoid gambling and speculation"
            ],
            "Ketu": [
                "Feed multicolored dogs",
                "Donate at religious places",
                "Keep a dog as pet",
                "Practice meditation and spirituality"
            ]
        }

        return remedies.get(planet, ["Consult qualified astrologer"])

    def get_remedies_for_planet(self, planet: str, issue: str = "general") -> List[str]:
        """Get general remedies for a planet."""
        # Use blind planet remedies as general remedies
        return self.get_remedies_for_blind_planet(planet)

    def get_general_remedies(self, chart: Dict[str, Any]) -> List[str]:
        """
        Get general Lal Kitab remedies for overall well-being.

        These are universal remedies that benefit everyone.
        """
        return [
            "Feed crows daily (for Saturn - removes obstacles)",
            "Offer water to Sun at sunrise (for vitality and success)",
            "Respect parents and elders (general debt removal)",
            "Donate to needy without expectation (karma cleansing)",
            "Keep home clean, especially kitchen (attracts positive energy)",
            "Light oil lamp in evening (removes darkness/negativity)",
            "Feed animals (cows, dogs, birds) regularly (compassion)",
            "Plant trees, especially peepal and neem (environmental karma)",
            "Visit temples/religious places regularly (spiritual growth)",
            "Help laborers and poor people (Saturn's blessings)"
        ]

    # ==================== Comprehensive Analysis ====================

    def analyze_lal_kitab_chart(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive Lal Kitab analysis.

        Combines all Lal Kitab techniques into one analysis.
        """
        logger.info("Starting comprehensive Lal Kitab chart analysis")

        # Detect all components
        debts = self.detect_planetary_debts(chart)
        blind_planets = self.detect_blind_planets(chart)
        exalted_enemies = self.detect_exalted_enemies(chart)
        pakka_ghar = self.check_pakka_ghar_placement(chart)

        # Collect priority remedies
        priority_remedies = []

        # Add remedies for high severity debts
        for debt in debts["debts"]:
            if debt["severity"] == "high":
                priority_remedies.extend(debt["remedies"][:2])  # Top 2 remedies

        # Add remedies for blind planets
        for blind in blind_planets:
            priority_remedies.extend(blind["remedies"][:2])  # Top 2 remedies

        # Remove duplicates while preserving order
        seen = set()
        priority_remedies = [x for x in priority_remedies if not (x in seen or seen.add(x))]

        # Overall assessment
        assessment_parts = []

        if debts["total_debts"] > 0:
            assessment_parts.append(f"{debts['total_debts']} karmic debt(s) detected")

        if len(blind_planets) > 0:
            assessment_parts.append(f"{len(blind_planets)} blind planet(s) found")

        if len(exalted_enemies) > 0:
            assessment_parts.append(f"{len(exalted_enemies)} exalted planet(s) in enemy houses")

        # Count planets in Pakka Ghar
        in_pakka = sum(1 for p in pakka_ghar.values() if p["in_pakka_ghar"])
        assessment_parts.append(f"{in_pakka} planet(s) in permanent houses")

        overall_assessment = " | ".join(assessment_parts) if assessment_parts else "Chart shows balanced Lal Kitab indicators"

        # Add severity-based guidance
        if debts["overall_severity"] == "high":
            overall_assessment += " - Immediate remedial action recommended"
        elif debts["overall_severity"] == "medium":
            overall_assessment += " - Regular remedies advised"
        else:
            overall_assessment += " - Preventive remedies beneficial"

        return {
            "debts": debts,
            "blind_planets": blind_planets,
            "exalted_enemies": exalted_enemies,
            "pakka_ghar_status": pakka_ghar,
            "priority_remedies": priority_remedies[:10],  # Top 10
            "general_remedies": self.get_general_remedies(chart),
            "overall_assessment": overall_assessment,
            "analysis_summary": {
                "total_debts": debts["total_debts"],
                "debt_severity": debts["overall_severity"],
                "blind_planets_count": len(blind_planets),
                "exalted_enemies_count": len(exalted_enemies),
                "planets_in_pakka_ghar": in_pakka
            }
        }


# Singleton instance
lal_kitab_service = LalKitabService()
