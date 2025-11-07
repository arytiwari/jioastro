"""
Ashtakavarga Astrology Service

Implements Ashtakavarga system including:
- Bhinna Ashtakavarga (individual planet charts)
- Sarva Ashtakavarga (collective chart)
- Pinda calculations
- Transit strength analysis
- Kakshya system

Author: JioAstro Team
Date: January 2025
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import date
import logging

logger = logging.getLogger(__name__)


class AshtakavargaService:
    """
    Singleton service for Ashtakavarga calculations.

    Ashtakavarga uses a point-based system (bindus) to evaluate
    planetary strength in each house for accurate transit predictions.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AshtakavargaService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True

        # Benefic Point Tables for all 7 planets
        # Format: {planet: {reference_point: [benefic_houses]}}

        self.BENEFIC_POINTS = {
            "Sun": {
                "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
                "Moon": [3, 6, 10, 11],
                "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
                "Mercury": [3, 5, 6, 9, 10, 11, 12],
                "Jupiter": [5, 6, 9, 11],
                "Venus": [6, 7, 12],
                "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
                "Ascendant": [3, 4, 6, 10, 11, 12]
            },
            "Moon": {
                "Sun": [3, 6, 7, 8, 10, 11],
                "Moon": [1, 3, 6, 7, 10, 11],
                "Mars": [2, 3, 5, 6, 9, 10, 11],
                "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
                "Jupiter": [1, 4, 7, 8, 10, 11, 12],
                "Venus": [3, 4, 5, 7, 9, 10, 11],
                "Saturn": [3, 5, 6, 11],
                "Ascendant": [3, 6, 10, 11]
            },
            "Mars": {
                "Sun": [3, 5, 6, 10, 11],
                "Moon": [3, 6, 11],
                "Mars": [1, 2, 4, 7, 8, 10, 11],
                "Mercury": [3, 5, 6, 11],
                "Jupiter": [6, 10, 11, 12],
                "Venus": [6, 8, 11, 12],
                "Saturn": [1, 4, 7, 8, 9, 10, 11],
                "Ascendant": [1, 3, 6, 10, 11]
            },
            "Mercury": {
                "Sun": [5, 6, 9, 11, 12],
                "Moon": [2, 4, 6, 8, 10, 11],
                "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
                "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
                "Jupiter": [6, 8, 11, 12],
                "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
                "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
                "Ascendant": [1, 2, 4, 6, 8, 10, 11]
            },
            "Jupiter": {
                "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
                "Moon": [2, 5, 7, 9, 11],
                "Mars": [1, 2, 4, 7, 8, 10, 11],
                "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
                "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
                "Venus": [2, 5, 6, 9, 10, 11],
                "Saturn": [3, 5, 6, 12],
                "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11]
            },
            "Venus": {
                "Sun": [8, 11, 12],
                "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
                "Mars": [3, 4, 6, 9, 11, 12],
                "Mercury": [3, 5, 6, 9, 11],
                "Jupiter": [5, 8, 9, 10, 11],
                "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
                "Saturn": [3, 4, 5, 8, 9, 10, 11],
                "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11]
            },
            "Saturn": {
                "Sun": [1, 2, 4, 7, 8, 10, 11],
                "Moon": [3, 6, 11],
                "Mars": [3, 5, 6, 10, 11, 12],
                "Mercury": [6, 8, 9, 10, 11, 12],
                "Jupiter": [5, 6, 11, 12],
                "Venus": [6, 11, 12],
                "Saturn": [3, 5, 6, 11],
                "Ascendant": [1, 3, 4, 6, 10, 11]
            }
        }

        # Kakshya lords (8 divisions of 30° = 3.75° each)
        self.KAKSHYA_LORDS = [
            "Saturn",    # 0° - 3.75°
            "Jupiter",   # 3.75° - 7.5°
            "Mars",      # 7.5° - 11.25°
            "Sun",       # 11.25° - 15°
            "Venus",     # 15° - 18.75°
            "Mercury",   # 18.75° - 22.5°
            "Moon",      # 22.5° - 26.25°
            "Ascendant"  # 26.25° - 30°
        ]

        logger.info("AshtakavargaService initialized with benefic point tables")

    # ==================== Bhinna Ashtakavarga ====================

    def calculate_bhinna_ashtakavarga(self, planet: str, chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Bhinna Ashtakavarga for a specific planet.

        Returns bindus (benefic points) for each house.
        """
        if planet not in self.BENEFIC_POINTS:
            logger.warning(f"Bhinna Ashtakavarga not available for {planet}")
            return {}

        planets = chart.get("planets", {})

        # Initialize bindus for all 12 houses
        house_bindus = {str(i): 0 for i in range(1, 13)}
        contributors = {str(i): [] for i in range(1, 13)}

        # Get benefic points table for this planet
        benefic_table = self.BENEFIC_POINTS[planet]

        # Process each reference point
        for reference_point, benefic_houses in benefic_table.items():
            # Get reference point's house position
            if reference_point == "Ascendant":
                reference_house = 1  # Ascendant is always house 1
            else:
                reference_data = planets.get(reference_point, {})
                reference_house = reference_data.get("house", 0)
                if reference_house == 0:
                    continue  # Skip if planet position not available

            # Calculate which houses receive bindus from this reference point
            for benefic_offset in benefic_houses:
                # Count houses from reference position
                target_house = ((reference_house - 1 + benefic_offset - 1) % 12) + 1
                house_bindus[str(target_house)] += 1
                contributors[str(target_house)].append(reference_point)

        # Calculate total bindus
        total_bindus = sum(house_bindus.values())

        # Identify strongest and weakest houses
        sorted_houses = sorted(house_bindus.items(), key=lambda x: x[1], reverse=True)
        strongest_houses = [int(h) for h, b in sorted_houses[:3]]
        weakest_houses = [int(h) for h, b in sorted_houses[-3:]]

        return {
            "planet": planet,
            "bindus_by_house": house_bindus,
            "total_bindus": total_bindus,
            "strongest_houses": strongest_houses,
            "weakest_houses": weakest_houses,
            "contributors": contributors
        }

    def calculate_all_bhinna_ashtakavarga(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Bhinna Ashtakavarga for all 7 planets."""
        bhinna_charts = {}

        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            bhinna_charts[planet] = self.calculate_bhinna_ashtakavarga(planet, chart)

        return bhinna_charts

    # ==================== Sarva Ashtakavarga ====================

    def calculate_sarva_ashtakavarga(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Sarva Ashtakavarga (collective chart).

        Combines all 7 Bhinna Ashtakavarga charts.
        """
        # Get all Bhinna charts
        bhinna_charts = self.calculate_all_bhinna_ashtakavarga(chart)

        # Initialize combined bindus
        combined_bindus = {str(i): 0 for i in range(1, 13)}

        # Sum bindus from all planets for each house
        for planet, bhinna_data in bhinna_charts.items():
            house_bindus = bhinna_data.get("bindus_by_house", {})
            for house, bindus in house_bindus.items():
                combined_bindus[house] += bindus

        # Calculate total bindus
        total_bindus = sum(combined_bindus.values())

        # Evaluate house strength based on bindu count
        house_strength = {}
        for house, bindus in combined_bindus.items():
            if bindus >= 30:
                strength = "very_strong"
            elif bindus >= 25:
                strength = "good"
            elif bindus >= 20:
                strength = "average"
            elif bindus >= 15:
                strength = "below_average"
            else:
                strength = "weak"
            house_strength[house] = strength

        # Identify strongest and weakest houses
        sorted_houses = sorted(combined_bindus.items(), key=lambda x: x[1], reverse=True)
        strongest_houses = [int(h) for h, b in sorted_houses[:4]]
        weakest_houses = [int(h) for h, b in sorted_houses[-3:]]

        return {
            "bindus_by_house": combined_bindus,
            "total_bindus": total_bindus,
            "house_strength": house_strength,
            "strongest_houses": strongest_houses,
            "weakest_houses": weakest_houses,
            "bhinna_charts": bhinna_charts
        }

    # ==================== Pinda Calculations ====================

    def calculate_graha_pinda(self, planet: str, chart: Dict[str, Any]) -> int:
        """
        Calculate Graha Pinda (planetary strength score).

        Graha Pinda = Total bindus in planet's Bhinna chart.
        """
        bhinna = self.calculate_bhinna_ashtakavarga(planet, chart)
        return bhinna.get("total_bindus", 0)

    def calculate_rashi_pinda(self, sign_num: int, chart: Dict[str, Any]) -> int:
        """
        Calculate Rashi Pinda (sign strength score).

        Sum of bindus from all planets for houses occupied by this sign.
        """
        # Get Sarva Ashtakavarga
        sarva = self.calculate_sarva_ashtakavarga(chart)

        # Find houses with this sign
        # This is simplified; in reality, need to map houses to signs
        planets = chart.get("planets", {})
        asc_sign = planets.get("Ascendant", {}).get("sign_num", 1)

        # Calculate which house has this sign
        # (assuming whole sign houses)
        house_with_sign = ((sign_num - asc_sign) % 12) + 1

        return sarva["bindus_by_house"].get(str(house_with_sign), 0)

    def calculate_all_pindas(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate all Pinda values."""
        graha_pindas = {}

        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            graha_pindas[planet] = self.calculate_graha_pinda(planet, chart)

        # Rashi Pindas for all 12 signs
        rashi_pindas = {}
        sign_names = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]

        for i, sign_name in enumerate(sign_names, 1):
            rashi_pindas[sign_name] = self.calculate_rashi_pinda(i, chart)

        # Identify strongest and weakest
        sorted_planets = sorted(graha_pindas.items(), key=lambda x: x[1], reverse=True)
        strongest_planets = [p for p, _ in sorted_planets[:3]]
        weakest_planets = [p for p, _ in sorted_planets[-2:]]

        return {
            "graha_pindas": graha_pindas,
            "rashi_pindas": rashi_pindas,
            "strongest_planets": strongest_planets,
            "weakest_planets": weakest_planets
        }

    # ==================== Transit Analysis ====================

    def analyze_transit(self, planet: str, house: int, chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze transit strength of a planet through a house.

        Args:
            planet: Transiting planet name
            house: House being transited (1-12)
            chart: Natal chart

        Returns:
            Transit analysis with strength and recommendations
        """
        # Get Bhinna Ashtakavarga for this planet
        bhinna = self.calculate_bhinna_ashtakavarga(planet, chart)
        bhinna_bindus = bhinna["bindus_by_house"].get(str(house), 0)

        # Get Sarva Ashtakavarga
        sarva = self.calculate_sarva_ashtakavarga(chart)
        sarva_bindus = sarva["bindus_by_house"].get(str(house), 0)

        # Determine transit strength
        transit_strength = self._evaluate_transit_strength(bhinna_bindus, sarva_bindus)

        # Get effects based on house and planet
        effects = self._get_transit_effects(planet, house, transit_strength)

        # Recommendations
        recommendations = self._get_transit_recommendations(planet, house, transit_strength)

        return {
            "transiting_planet": planet,
            "current_house": house,
            "bhinna_bindus": bhinna_bindus,
            "sarva_bindus": sarva_bindus,
            "transit_strength": transit_strength,
            "effects": effects,
            "recommendations": recommendations,
            "duration_quality": self._get_duration_quality(bhinna_bindus)
        }

    def _evaluate_transit_strength(self, bhinna_bindus: int, sarva_bindus: int) -> str:
        """Evaluate overall transit strength."""
        # Bhinna bindus are primary, Sarva provides context
        if bhinna_bindus >= 4 and sarva_bindus >= 25:
            return "very_favorable"
        elif bhinna_bindus >= 4:
            return "favorable"
        elif bhinna_bindus == 3:
            return "neutral"
        elif bhinna_bindus <= 2 and sarva_bindus >= 25:
            return "mixed"
        else:
            return "difficult"

    def _get_transit_effects(self, planet: str, house: int, strength: str) -> List[str]:
        """Get likely effects of transit based on planet, house, and strength."""

        # House significations
        house_matters = {
            1: "self, personality, health, new beginnings",
            2: "wealth, family, speech, food",
            3: "siblings, courage, short travels, communication",
            4: "home, mother, property, vehicles, peace of mind",
            5: "children, education, speculation, creativity",
            6: "enemies, diseases, debts, service, competition",
            7: "spouse, partnerships, business, relationships",
            8: "longevity, transformation, occult, inheritance",
            9: "fortune, father, guru, dharma, long travels",
            10: "career, reputation, status, authority",
            11: "gains, income, desires, elder siblings, social network",
            12: "expenses, losses, spirituality, foreign lands, liberation"
        }

        # Planet characteristics
        planet_nature = {
            "Sun": "authority, leadership, ego, vitality",
            "Moon": "emotions, mind, mother, public",
            "Mars": "energy, action, courage, conflicts",
            "Mercury": "communication, intellect, business, trade",
            "Jupiter": "wisdom, expansion, fortune, teaching",
            "Venus": "relationships, luxury, arts, pleasures",
            "Saturn": "discipline, delays, responsibilities, karma"
        }

        base_matter = house_matters.get(house, "various life areas")
        planet_quality = planet_nature.get(planet, "planetary")

        effects = []

        if strength in ["very_favorable", "favorable"]:
            effects.append(f"Positive developments in {base_matter}")
            effects.append(f"Enhanced {planet_quality} influence brings benefits")
            effects.append("Good time for initiatives in this area")
        elif strength == "neutral":
            effects.append(f"Mixed results in {base_matter}")
            effects.append("Neither significant gains nor major obstacles")
            effects.append("Proceed with caution and planning")
        else:  # difficult or mixed
            effects.append(f"Challenges likely in {base_matter}")
            effects.append(f"{planet_quality.capitalize()} matters need careful handling")
            effects.append("Patience and remedies recommended")

        return effects

    def _get_transit_recommendations(self, planet: str, house: int, strength: str) -> List[str]:
        """Get recommendations based on transit."""
        recommendations = []

        if strength in ["very_favorable", "favorable"]:
            recommendations.append(f"Excellent time to pursue {house}th house matters")
            recommendations.append("Make important decisions confidently")
            recommendations.append("Initiate new projects in this area")
        elif strength == "neutral":
            recommendations.append("Evaluate opportunities carefully")
            recommendations.append("Avoid major commitments if possible")
            recommendations.append("Focus on preparation and planning")
        else:
            recommendations.append("Avoid new initiatives if possible")
            recommendations.append("Focus on damage control and maintenance")
            recommendations.append(f"Perform remedies for {planet}")
            recommendations.append("Wait for better transit timing")

        return recommendations

    def _get_duration_quality(self, bhinna_bindus: int) -> str:
        """Get quality description for transit duration."""
        if bhinna_bindus >= 5:
            return "excellent"
        elif bhinna_bindus >= 4:
            return "good"
        elif bhinna_bindus == 3:
            return "moderate"
        else:
            return "challenging"

    # ==================== Kakshya System ====================

    def get_kakshya_lord(self, longitude: float) -> str:
        """
        Get Kakshya lord for a specific longitude within a sign.

        Args:
            longitude: Absolute longitude (0-360°)

        Returns:
            Kakshya lord name
        """
        # Get position within sign (0-30°)
        within_sign = longitude % 30

        # Each kakshya is 3.75°
        kakshya_index = int(within_sign / 3.75)

        # Ensure within bounds
        if kakshya_index > 7:
            kakshya_index = 7

        return self.KAKSHYA_LORDS[kakshya_index]

    def analyze_kakshya_position(self, planet: str, chart: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze planet's kakshya position."""
        planets = chart.get("planets", {})
        planet_data = planets.get(planet, {})

        if not planet_data:
            return {}

        longitude = planet_data.get("longitude", 0)
        kakshya_lord = self.get_kakshya_lord(longitude)

        # Check if planet is in its own kakshya
        own_kakshya = (kakshya_lord == planet)

        within_sign = longitude % 30
        kakshya_degree = (within_sign % 3.75)

        return {
            "planet": planet,
            "longitude": longitude,
            "within_sign_degree": within_sign,
            "kakshya_lord": kakshya_lord,
            "own_kakshya": own_kakshya,
            "kakshya_position_degree": kakshya_degree,
            "strength_note": "Extra strength" if own_kakshya else "Normal strength"
        }

    # ==================== Comprehensive Analysis ====================

    def analyze_ashtakavarga(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive Ashtakavarga analysis.

        Returns complete analysis including:
        - All Bhinna Ashtakavarga charts
        - Sarva Ashtakavarga
        - Pinda calculations
        - Kakshya positions
        """
        logger.info("Starting comprehensive Ashtakavarga analysis")

        # Calculate all components
        sarva = self.calculate_sarva_ashtakavarga(chart)
        pindas = self.calculate_all_pindas(chart)

        # Kakshya analysis for all planets
        kakshya_analysis = {}
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            kakshya_analysis[planet] = self.analyze_kakshya_position(planet, chart)

        # Summary statistics
        total_bindus = sarva["total_bindus"]
        avg_bindus_per_house = total_bindus / 12

        # Overall assessment
        strong_house_count = sum(1 for s in sarva["house_strength"].values()
                                if s in ["very_strong", "good"])
        weak_house_count = sum(1 for s in sarva["house_strength"].values()
                              if s in ["weak", "below_average"])

        if strong_house_count >= 6:
            overall_strength = "strong"
        elif weak_house_count >= 6:
            overall_strength = "weak"
        else:
            overall_strength = "balanced"

        return {
            "sarva_ashtakavarga": sarva,
            "bhinna_ashtakavarga": sarva.get("bhinna_charts", {}),
            "pindas": pindas,
            "kakshya_positions": kakshya_analysis,
            "summary": {
                "total_bindus": total_bindus,
                "average_bindus_per_house": round(avg_bindus_per_house, 2),
                "strong_houses": sarva["strongest_houses"],
                "weak_houses": sarva["weakest_houses"],
                "overall_chart_strength": overall_strength,
                "strong_house_count": strong_house_count,
                "weak_house_count": weak_house_count
            },
            "interpretation": self._generate_interpretation(sarva, pindas, overall_strength)
        }

    def _generate_interpretation(self, sarva: Dict[str, Any],
                                 pindas: Dict[str, Any],
                                 overall_strength: str) -> str:
        """Generate overall interpretation."""
        strongest_houses = sarva["strongest_houses"]
        weakest_houses = sarva["weakest_houses"]
        strongest_planets = pindas["strongest_planets"]

        interpretation = f"Chart shows {overall_strength} Ashtakavarga pattern. "
        interpretation += f"Strongest houses ({', '.join(map(str, strongest_houses))}) "
        interpretation += "indicate areas of greatest success and favorable outcomes. "
        interpretation += f"Weakest houses ({', '.join(map(str, weakest_houses))}) "
        interpretation += "may require extra effort and remedies. "
        interpretation += f"Strongest planets ({', '.join(strongest_planets)}) "
        interpretation += "will give best results during their transits and dashas."

        return interpretation


# Singleton instance
ashtakavarga_service = AshtakavargaService()
