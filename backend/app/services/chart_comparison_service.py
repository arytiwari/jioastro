"""
Chart Comparison Service
Compares two birth charts for synastry, compatibility, and relationship analysis
Includes composite chart generation and progressed chart calculations
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import swisseph as swe


class ChartComparisonService:
    """Service for comparing two birth charts"""

    # Aspect definitions with orbs (in degrees)
    ASPECTS = {
        "conjunction": {"angle": 0, "orb": 8, "harmonious": True},
        "sextile": {"angle": 60, "orb": 6, "harmonious": True},
        "square": {"angle": 90, "orb": 7, "harmonious": False},
        "trine": {"angle": 120, "orb": 8, "harmonious": True},
        "opposition": {"angle": 180, "orb": 8, "harmonious": False},
    }

    # Planet importance weights for compatibility
    PLANET_WEIGHTS = {
        "Sun": 10,
        "Moon": 10,
        "Venus": 9,
        "Mars": 8,
        "Mercury": 7,
        "Jupiter": 8,
        "Saturn": 7,
        "Rahu": 6,
        "Ketu": 6,
        "Ascendant": 9,
    }

    # Romantic compatibility factors
    ROMANTIC_FACTORS = {
        "moon_harmony": "Emotional compatibility and understanding",
        "venus_aspects": "Love, affection, and romantic attraction",
        "mars_compatibility": "Physical attraction and passion",
        "sun_connection": "Core personality alignment",
        "jupiter_support": "Growth, optimism, and shared values",
        "saturn_stability": "Commitment, responsibility, and long-term stability",
    }

    def __init__(self):
        """Initialize chart comparison service"""
        swe.set_ephe_path(None)  # Use default ephemeris path
        swe.set_sid_mode(swe.SIDM_LAHIRI)  # Lahiri ayanamsa for Vedic

    def compare_charts(
        self,
        chart_1: Dict[str, Any],
        chart_2: Dict[str, Any],
        comparison_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Compare two birth charts

        Args:
            chart_1: First person's birth chart
            chart_2: Second person's birth chart
            comparison_type: Type of comparison (general, romantic, business, family)

        Returns:
            Complete chart comparison analysis
        """

        # Extract planet positions
        planets_1 = self._extract_planet_positions(chart_1)
        planets_2 = self._extract_planet_positions(chart_2)

        # Find inter-chart aspects
        aspects = self._find_inter_chart_aspects(planets_1, planets_2)

        # Calculate house overlays
        overlays = self._calculate_house_overlays(chart_1, chart_2)

        # Calculate compatibility factors
        factors = self._calculate_compatibility_factors(
            chart_1, chart_2, aspects, comparison_type
        )

        # Generate summary
        summary = self._generate_summary(aspects, factors, comparison_type)

        # Generate detailed interpretation
        detailed = self._generate_detailed_interpretation(
            chart_1, chart_2, aspects, overlays, factors, comparison_type
        )

        # Count aspects
        harmonious_count = sum(1 for a in aspects if a["is_harmonious"])
        challenging_count = len(aspects) - harmonious_count

        return {
            "comparison_type": comparison_type,
            "profile_1": self._get_profile_summary(chart_1),
            "profile_2": self._get_profile_summary(chart_2),
            "inter_chart_aspects": aspects,
            "harmonious_aspects_count": harmonious_count,
            "challenging_aspects_count": challenging_count,
            "house_overlays": overlays[:10],  # Top 10 most significant
            "compatibility_factors": factors,
            "summary": summary,
            "detailed_interpretation": detailed,
        }

    def _extract_planet_positions(self, chart: Dict[str, Any]) -> Dict[str, float]:
        """Extract planet longitudes from chart"""
        positions = {}

        # Add Ascendant
        if "ascendant" in chart:
            positions["Ascendant"] = chart["ascendant"].get("longitude", 0)

        # Add planets
        if "planets" in chart:
            for planet_name, planet_data in chart["planets"].items():
                if isinstance(planet_data, dict) and "longitude" in planet_data:
                    positions[planet_name] = planet_data["longitude"]

        return positions

    def _find_inter_chart_aspects(
        self,
        planets_1: Dict[str, float],
        planets_2: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Find aspects between planets in two charts"""
        aspects = []

        for planet_1_name, long_1 in planets_1.items():
            for planet_2_name, long_2 in planets_2.items():
                # Calculate angular difference
                diff = abs(long_1 - long_2)
                if diff > 180:
                    diff = 360 - diff

                # Check each aspect type
                for aspect_name, aspect_info in self.ASPECTS.items():
                    target_angle = aspect_info["angle"]
                    orb = aspect_info["orb"]

                    # Calculate orb (difference from exact aspect)
                    actual_orb = abs(diff - target_angle)

                    if actual_orb <= orb:
                        # Determine strength based on orb
                        if actual_orb <= orb / 3:
                            strength = "strong"
                        elif actual_orb <= orb * 2/3:
                            strength = "moderate"
                        else:
                            strength = "weak"

                        # Generate interpretation
                        interpretation = self._interpret_aspect(
                            planet_1_name, planet_2_name, aspect_name, strength
                        )

                        aspects.append({
                            "planet_1": planet_1_name,
                            "planet_2": planet_2_name,
                            "aspect_type": aspect_name,
                            "aspect_angle": diff,
                            "orb": actual_orb,
                            "strength": strength,
                            "interpretation": interpretation,
                            "is_harmonious": aspect_info["harmonious"]
                        })

        # Sort by strength (strong first)
        aspects.sort(key=lambda a: (
            {"strong": 0, "moderate": 1, "weak": 2}[a["strength"]],
            a["orb"]
        ))

        return aspects

    def _calculate_house_overlays(
        self,
        chart_1: Dict[str, Any],
        chart_2: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Calculate house overlays (person 1's planets in person 2's houses and vice versa)"""
        overlays = []

        # Get ascendant signs
        asc_1 = chart_1.get("ascendant", {}).get("sign_num", 0)
        asc_2 = chart_2.get("ascendant", {}).get("sign_num", 0)

        # Person 1's planets in Person 2's houses
        if "planets" in chart_1:
            for planet_name, planet_data in chart_1["planets"].items():
                if isinstance(planet_data, dict) and "sign_num" in planet_data:
                    planet_sign = planet_data["sign_num"]
                    house_in_chart_2 = ((planet_sign - asc_2) % 12) + 1

                    significance = self._get_house_overlay_significance(
                        planet_name, house_in_chart_2, "person1", "person2"
                    )

                    overlays.append({
                        "planet": planet_name,
                        "planet_owner": "person1",
                        "falls_in_house": house_in_chart_2,
                        "house_owner": "person2",
                        "significance": f"Person 1's {planet_name} in Person 2's house {house_in_chart_2}",
                        "interpretation": significance
                    })

        # Person 2's planets in Person 1's houses
        if "planets" in chart_2:
            for planet_name, planet_data in chart_2["planets"].items():
                if isinstance(planet_data, dict) and "sign_num" in planet_data:
                    planet_sign = planet_data["sign_num"]
                    house_in_chart_1 = ((planet_sign - asc_1) % 12) + 1

                    significance = self._get_house_overlay_significance(
                        planet_name, house_in_chart_1, "person2", "person1"
                    )

                    overlays.append({
                        "planet": planet_name,
                        "planet_owner": "person2",
                        "falls_in_house": house_in_chart_1,
                        "house_owner": "person1",
                        "significance": f"Person 2's {planet_name} in Person 1's house {house_in_chart_1}",
                        "interpretation": significance
                    })

        return overlays

    def _calculate_compatibility_factors(
        self,
        chart_1: Dict[str, Any],
        chart_2: Dict[str, Any],
        aspects: List[Dict[str, Any]],
        comparison_type: str
    ) -> List[Dict[str, Any]]:
        """Calculate specific compatibility factors"""
        factors = []

        # Moon harmony (emotional compatibility)
        moon_score = self._calculate_moon_compatibility(chart_1, chart_2, aspects)
        factors.append({
            "factor_name": "Emotional Compatibility",
            "description": "Moon harmony indicates emotional understanding and comfort",
            "score": moon_score,
            "is_positive": moon_score >= 60
        })

        # Venus aspects (love and attraction)
        venus_score = self._calculate_venus_compatibility(aspects)
        factors.append({
            "factor_name": "Love & Attraction",
            "description": "Venus connections show romantic attraction and affection",
            "score": venus_score,
            "is_positive": venus_score >= 60
        })

        # Sun connection (core compatibility)
        sun_score = self._calculate_sun_compatibility(chart_1, chart_2, aspects)
        factors.append({
            "factor_name": "Core Compatibility",
            "description": "Sun aspects indicate overall personality alignment",
            "score": sun_score,
            "is_positive": sun_score >= 60
        })

        # Communication (Mercury)
        mercury_score = self._calculate_mercury_compatibility(aspects)
        factors.append({
            "factor_name": "Communication",
            "description": "Mercury connections show mental compatibility and understanding",
            "score": mercury_score,
            "is_positive": mercury_score >= 60
        })

        # Passion (Mars)
        mars_score = self._calculate_mars_compatibility(aspects)
        factors.append({
            "factor_name": "Passion & Energy",
            "description": "Mars aspects indicate physical attraction and energy dynamics",
            "score": mars_score,
            "is_positive": mars_score >= 55
        })

        # Growth (Jupiter)
        jupiter_score = self._calculate_jupiter_compatibility(aspects)
        factors.append({
            "factor_name": "Growth & Expansion",
            "description": "Jupiter connections show mutual support and shared values",
            "score": jupiter_score,
            "is_positive": jupiter_score >= 60
        })

        # Stability (Saturn)
        saturn_score = self._calculate_saturn_compatibility(aspects)
        factors.append({
            "factor_name": "Commitment & Stability",
            "description": "Saturn aspects indicate long-term potential and responsibility",
            "score": saturn_score,
            "is_positive": saturn_score >= 55
        })

        return factors

    def _generate_summary(
        self,
        aspects: List[Dict[str, Any]],
        factors: List[Dict[str, Any]],
        comparison_type: str
    ) -> Dict[str, Any]:
        """Generate overall comparison summary"""
        # Calculate overall score
        total_score = sum(f["score"] for f in factors) / len(factors) if factors else 50

        # Determine compatibility level
        if total_score >= 80:
            level = "excellent"
        elif total_score >= 70:
            level = "very good"
        elif total_score >= 60:
            level = "good"
        elif total_score >= 50:
            level = "moderate"
        elif total_score >= 40:
            level = "challenging"
        else:
            level = "difficult"

        # Identify strengths
        strengths = []
        for factor in factors:
            if factor["is_positive"] and factor["score"] >= 70:
                strengths.append(factor["factor_name"])

        if not strengths:
            strengths = ["Opportunities for growth and learning together"]

        # Identify challenges
        challenges = []
        for factor in factors:
            if not factor["is_positive"] and factor["score"] < 50:
                challenges.append(f"Work needed in {factor['factor_name'].lower()}")

        if not challenges:
            challenges = ["Maintain open communication"]

        # Generate advice
        advice = []
        if total_score >= 70:
            advice.append("This is a promising connection with natural compatibility")
            advice.append("Continue to nurture the positive aspects of the relationship")
        elif total_score >= 50:
            advice.append("This connection has potential with conscious effort")
            advice.append("Focus on areas of natural harmony while working on challenges")
        else:
            advice.append("This connection requires significant work and understanding")
            advice.append("Clear communication and mutual respect are essential")

        # Add specific advice based on factors
        for factor in factors:
            if not factor["is_positive"]:
                advice.append(f"Pay attention to {factor['factor_name'].lower()}")

        return {
            "overall_score": round(total_score, 1),
            "compatibility_level": level,
            "strengths": strengths[:5],
            "challenges": challenges[:5],
            "advice": advice[:5]
        }

    def _generate_detailed_interpretation(
        self,
        chart_1: Dict[str, Any],
        chart_2: Dict[str, Any],
        aspects: List[Dict[str, Any]],
        overlays: List[Dict[str, Any]],
        factors: List[Dict[str, Any]],
        comparison_type: str
    ) -> str:
        """Generate detailed interpretation text"""
        interpretation = f"Chart Comparison Analysis ({comparison_type})\n\n"

        interpretation += "OVERVIEW:\n"
        interpretation += f"Person 1: {chart_1.get('name', 'Person 1')} - "
        interpretation += f"{chart_1.get('ascendant', {}).get('sign', 'Unknown')} Ascendant\n"
        interpretation += f"Person 2: {chart_2.get('name', 'Person 2')} - "
        interpretation += f"{chart_2.get('ascendant', {}).get('sign', 'Unknown')} Ascendant\n\n"

        interpretation += "KEY ASPECTS:\n"
        for aspect in aspects[:5]:  # Top 5
            interpretation += f"- {aspect['planet_1']} {aspect['aspect_type']} {aspect['planet_2']}: "
            interpretation += f"{aspect['interpretation']}\n"

        interpretation += "\nCOMPATIBILITY FACTORS:\n"
        for factor in factors:
            status = "✓" if factor["is_positive"] else "⚠"
            interpretation += f"{status} {factor['factor_name']}: {factor['score']:.0f}% - {factor['description']}\n"

        interpretation += "\nThis analysis provides insights into the dynamics between these two charts. "
        interpretation += "Remember that astrology is a tool for understanding, not destiny."

        return interpretation

    # Helper methods for calculating individual compatibility factors

    def _calculate_moon_compatibility(
        self, chart_1: Dict, chart_2: Dict, aspects: List[Dict]
    ) -> float:
        """Calculate Moon compatibility score"""
        score = 50  # Base score

        # Check Moon-Moon aspects
        moon_aspects = [a for a in aspects if (
            (a["planet_1"] == "Moon" or a["planet_2"] == "Moon") and
            (a["planet_1"] == "Moon" or a["planet_2"] == "Moon")
        )]

        for aspect in moon_aspects:
            if aspect["is_harmonious"]:
                score += 20 if aspect["strength"] == "strong" else 10
            else:
                score -= 15 if aspect["strength"] == "strong" else 8

        return min(100, max(0, score))

    def _calculate_venus_compatibility(self, aspects: List[Dict]) -> float:
        """Calculate Venus compatibility score"""
        score = 50

        venus_aspects = [a for a in aspects if "Venus" in [a["planet_1"], a["planet_2"]]]

        for aspect in venus_aspects:
            if aspect["is_harmonious"]:
                score += 15 if aspect["strength"] == "strong" else 8
            else:
                score -= 10 if aspect["strength"] == "strong" else 5

        return min(100, max(0, score))

    def _calculate_sun_compatibility(
        self, chart_1: Dict, chart_2: Dict, aspects: List[Dict]
    ) -> float:
        """Calculate Sun compatibility score"""
        score = 50

        sun_aspects = [a for a in aspects if "Sun" in [a["planet_1"], a["planet_2"]]]

        for aspect in sun_aspects:
            if aspect["is_harmonious"]:
                score += 18 if aspect["strength"] == "strong" else 10
            else:
                score -= 12 if aspect["strength"] == "strong" else 6

        return min(100, max(0, score))

    def _calculate_mercury_compatibility(self, aspects: List[Dict]) -> float:
        """Calculate Mercury compatibility score"""
        score = 50

        mercury_aspects = [a for a in aspects if "Mercury" in [a["planet_1"], a["planet_2"]]]

        for aspect in mercury_aspects:
            if aspect["is_harmonious"]:
                score += 15
            else:
                score -= 10

        return min(100, max(0, score))

    def _calculate_mars_compatibility(self, aspects: List[Dict]) -> float:
        """Calculate Mars compatibility score"""
        score = 50

        mars_aspects = [a for a in aspects if "Mars" in [a["planet_1"], a["planet_2"]]]

        for aspect in mars_aspects:
            if aspect["is_harmonious"]:
                score += 12
            else:
                # Mars squares and oppositions can indicate passion, not always negative
                score -= 5

        return min(100, max(0, score))

    def _calculate_jupiter_compatibility(self, aspects: List[Dict]) -> float:
        """Calculate Jupiter compatibility score"""
        score = 50

        jupiter_aspects = [a for a in aspects if "Jupiter" in [a["planet_1"], a["planet_2"]]]

        for aspect in jupiter_aspects:
            if aspect["is_harmonious"]:
                score += 15
            else:
                score -= 8

        return min(100, max(0, score))

    def _calculate_saturn_compatibility(self, aspects: List[Dict]) -> float:
        """Calculate Saturn compatibility score"""
        score = 50

        saturn_aspects = [a for a in aspects if "Saturn" in [a["planet_1"], a["planet_2"]]]

        for aspect in saturn_aspects:
            if aspect["is_harmonious"]:
                score += 15
            else:
                score -= 12  # Saturn hard aspects can be challenging

        return min(100, max(0, score))

    def _interpret_aspect(
        self, planet_1: str, planet_2: str, aspect_type: str, strength: str
    ) -> str:
        """Generate interpretation for an aspect"""
        interpretations = {
            "conjunction": f"{planet_1} and {planet_2} blend energies powerfully",
            "trine": f"{planet_1} and {planet_2} flow harmoniously together",
            "sextile": f"{planet_1} and {planet_2} support each other positively",
            "square": f"{planet_1} and {planet_2} create dynamic tension requiring balance",
            "opposition": f"{planet_1} and {planet_2} pull in different directions, seeking integration"
        }

        base = interpretations.get(aspect_type, f"{planet_1} aspects {planet_2}")
        return f"{base} ({strength})"

    def _get_house_overlay_significance(
        self, planet: str, house: int, planet_owner: str, house_owner: str
    ) -> str:
        """Get significance of house overlay"""
        house_meanings = {
            1: "identity and self-expression",
            2: "values and resources",
            3: "communication and daily activities",
            4: "home and emotional foundation",
            5: "creativity and joy",
            6: "service and daily routines",
            7: "partnership and relationships",
            8: "transformation and shared resources",
            9: "beliefs and expansion",
            10: "career and public life",
            11: "friendship and aspirations",
            12: "spirituality and hidden matters"
        }

        meaning = house_meanings.get(house, "life area")
        return f"Influences {meaning} significantly"

    def _get_profile_summary(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """Get brief profile summary"""
        return {
            "profile_id": chart.get("id", "unknown"),
            "name": chart.get("name", "Unknown"),
            "ascendant": chart.get("ascendant", {}).get("sign", "Unknown"),
            "moon_sign": chart.get("planets", {}).get("Moon", {}).get("sign", "Unknown"),
            "sun_sign": chart.get("planets", {}).get("Sun", {}).get("sign", "Unknown")
        }

    # ============================================================================
    # COMPOSITE CHART GENERATION
    # ============================================================================

    def generate_composite_chart(
        self,
        chart_1: Dict[str, Any],
        chart_2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate composite chart (midpoint method)

        Composite chart represents the relationship itself as a separate entity.
        Calculated by finding midpoints between corresponding planets in both charts.

        Args:
            chart_1: First person's birth chart
            chart_2: Second person's birth chart

        Returns:
            Composite chart with all planetary positions and interpretation
        """
        # Extract planet positions
        planets_1 = self._extract_planet_positions(chart_1)
        planets_2 = self._extract_planet_positions(chart_2)

        # Calculate composite planets (midpoints)
        composite_planets = {}
        for planet_name in planets_1.keys():
            if planet_name in planets_2:
                long_1 = planets_1[planet_name]
                long_2 = planets_2[planet_name]

                # Calculate midpoint (shorter arc)
                diff = abs(long_1 - long_2)
                if diff > 180:
                    # Use longer arc midpoint
                    midpoint = ((long_1 + long_2) / 2 + 180) % 360
                else:
                    # Use shorter arc midpoint
                    midpoint = (long_1 + long_2) / 2

                composite_planets[planet_name] = {
                    "longitude": midpoint,
                    "sign": self._get_sign_from_longitude(midpoint),
                    "sign_num": int(midpoint / 30),
                    "degree": midpoint % 30,
                    "description": self._get_composite_planet_meaning(planet_name, midpoint)
                }

        # Calculate composite houses (based on composite ascendant)
        composite_asc = composite_planets.get("Ascendant", {}).get("longitude", 0)
        composite_houses = self._generate_composite_houses(composite_asc)

        # Analyze composite chart
        composite_analysis = self._analyze_composite_chart(composite_planets, composite_houses)

        return {
            "composite_type": "midpoint",
            "relationship_chart": {
                "ascendant": composite_planets.get("Ascendant", {}),
                "planets": composite_planets,
                "houses": composite_houses
            },
            "analysis": composite_analysis,
            "interpretation": self._interpret_composite_chart(composite_planets, composite_analysis),
            "strengths": composite_analysis.get("strengths", []),
            "challenges": composite_analysis.get("challenges", []),
            "relationship_themes": self._identify_relationship_themes(composite_planets)
        }

    def _get_sign_from_longitude(self, longitude: float) -> str:
        """Get zodiac sign from longitude"""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        return signs[int(longitude / 30)]

    def _get_composite_planet_meaning(self, planet: str, longitude: float) -> str:
        """Get meaning of composite planet position"""
        meanings = {
            "Sun": "The core identity and purpose of the relationship",
            "Moon": "The emotional foundation and comfort level together",
            "Mercury": "How the relationship communicates and thinks",
            "Venus": "How the relationship expresses love and affection",
            "Mars": "How the relationship takes action and asserts itself",
            "Jupiter": "The growth potential and shared beliefs",
            "Saturn": "The responsibilities and long-term structure",
            "Rahu": "The relationship's karmic direction and ambitions",
            "Ketu": "The relationship's spiritual lessons and past patterns",
            "Ascendant": "The relationship's outward expression and approach to life"
        }
        return meanings.get(planet, "Relationship dynamics")

    def _generate_composite_houses(self, composite_asc: float) -> List[Dict[str, Any]]:
        """Generate composite houses based on composite ascendant"""
        houses = []
        asc_sign_num = int(composite_asc / 30)

        for i in range(12):
            house_num = i + 1
            house_sign_num = (asc_sign_num + i) % 12
            house_sign = self._get_sign_from_longitude(house_sign_num * 30)

            houses.append({
                "house_number": house_num,
                "sign": house_sign,
                "cusp": (composite_asc + i * 30) % 360,
                "significance": self._get_house_significance_composite(house_num)
            })

        return houses

    def _get_house_significance_composite(self, house_num: int) -> str:
        """Get significance of composite house"""
        significances = {
            1: "How the relationship presents itself to the world",
            2: "Shared values and resources",
            3: "Communication and daily interactions",
            4: "Emotional foundation and home together",
            5: "Creativity, joy, and children in the relationship",
            6: "Daily routines and service to each other",
            7: "The partnership dynamic itself",
            8: "Shared intimacy and transformation",
            9: "Shared beliefs and adventures",
            10: "Public face and joint achievements",
            11: "Shared goals and social connections",
            12: "Hidden strengths and unconscious patterns"
        }
        return significances.get(house_num, "Relationship area")

    def _analyze_composite_chart(
        self,
        composite_planets: Dict[str, Dict[str, Any]],
        composite_houses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze composite chart for relationship dynamics"""
        strengths = []
        challenges = []

        # Check Sun-Moon relationship (emotional-identity harmony)
        if "Sun" in composite_planets and "Moon" in composite_planets:
            sun_long = composite_planets["Sun"]["longitude"]
            moon_long = composite_planets["Moon"]["longitude"]
            diff = abs(sun_long - moon_long)
            if diff > 180:
                diff = 360 - diff

            if diff < 60:
                strengths.append("Strong emotional-identity alignment in the relationship")
            elif diff > 150:
                challenges.append("Emotional needs and relationship identity may conflict")

        # Check Venus-Mars (romance-passion balance)
        if "Venus" in composite_planets and "Mars" in composite_planets:
            venus_long = composite_planets["Venus"]["longitude"]
            mars_long = composite_planets["Mars"]["longitude"]
            diff = abs(venus_long - mars_long)
            if diff > 180:
                diff = 360 - diff

            if diff < 90:
                strengths.append("Harmonious balance of affection and passion")

        # Check Jupiter for growth potential
        if "Jupiter" in composite_planets:
            jupiter_sign = composite_planets["Jupiter"]["sign"]
            if jupiter_sign in ["Sagittarius", "Pisces", "Cancer"]:
                strengths.append("Strong growth and expansion potential")

        # Check Saturn for commitment
        if "Saturn" in composite_planets:
            saturn_sign = composite_planets["Saturn"]["sign"]
            if saturn_sign in ["Capricorn", "Aquarius", "Libra"]:
                strengths.append("Solid foundation for long-term commitment")
            else:
                challenges.append("Work needed to build lasting structure")

        return {
            "strengths": strengths,
            "challenges": challenges,
            "overall_tone": self._determine_composite_tone(strengths, challenges)
        }

    def _determine_composite_tone(self, strengths: List[str], challenges: List[str]) -> str:
        """Determine overall tone of composite chart"""
        strength_count = len(strengths)
        challenge_count = len(challenges)

        if strength_count > challenge_count * 2:
            return "harmonious"
        elif strength_count > challenge_count:
            return "balanced_positive"
        elif challenge_count > strength_count:
            return "growth_oriented"
        else:
            return "balanced"

    def _interpret_composite_chart(
        self,
        composite_planets: Dict[str, Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> str:
        """Generate interpretation of composite chart"""
        interpretation = "COMPOSITE CHART ANALYSIS\n\n"
        interpretation += "This composite chart represents the relationship itself as a unique entity.\n\n"

        interpretation += "KEY PLACEMENTS:\n"
        for planet_name, planet_data in list(composite_planets.items())[:5]:
            interpretation += f"- Composite {planet_name} in {planet_data['sign']}: "
            interpretation += f"{planet_data.get('description', 'Relationship dynamics')}\n"

        interpretation += f"\nOVERALL TONE: {analysis['overall_tone'].replace('_', ' ').title()}\n"

        return interpretation

    def _identify_relationship_themes(self, composite_planets: Dict[str, Dict[str, Any]]) -> List[str]:
        """Identify main themes in the relationship"""
        themes = []

        # Check for fire sign dominance (passion, action)
        fire_count = sum(1 for p in composite_planets.values()
                        if p.get("sign") in ["Aries", "Leo", "Sagittarius"])
        if fire_count >= 3:
            themes.append("Dynamic and passionate relationship")

        # Check for earth sign dominance (stability, practical)
        earth_count = sum(1 for p in composite_planets.values()
                         if p.get("sign") in ["Taurus", "Virgo", "Capricorn"])
        if earth_count >= 3:
            themes.append("Stable and practical partnership")

        # Check for air sign dominance (mental, communication)
        air_count = sum(1 for p in composite_planets.values()
                       if p.get("sign") in ["Gemini", "Libra", "Aquarius"])
        if air_count >= 3:
            themes.append("Intellectually stimulating connection")

        # Check for water sign dominance (emotional, intuitive)
        water_count = sum(1 for p in composite_planets.values()
                         if p.get("sign") in ["Cancer", "Scorpio", "Pisces"])
        if water_count >= 3:
            themes.append("Deep emotional and intuitive bond")

        if not themes:
            themes.append("Balanced blend of energies")

        return themes

    # ============================================================================
    # PROGRESSED CHART CALCULATIONS (Secondary Progressions)
    # ============================================================================

    def calculate_progressed_chart(
        self,
        natal_chart: Dict[str, Any],
        current_age: int
    ) -> Dict[str, Any]:
        """
        Calculate progressed chart using secondary progressions

        Secondary progressions: 1 day after birth = 1 year of life

        Args:
            natal_chart: Original birth chart
            current_age: Current age of person in years

        Returns:
            Progressed chart with current planetary positions and interpretation
        """
        # Get birth date from chart
        birth_datetime_str = natal_chart.get("birth_datetime")
        if not birth_datetime_str:
            return {"error": "Birth datetime not found in chart"}

        try:
            # Parse birth datetime
            if isinstance(birth_datetime_str, str):
                birth_datetime = datetime.fromisoformat(birth_datetime_str.replace('Z', '+00:00'))
            else:
                birth_datetime = birth_datetime_str

            # Calculate progressed date (1 day per year)
            progressed_date = birth_datetime + timedelta(days=current_age)

            # Get location
            latitude = natal_chart.get("latitude", 0)
            longitude = natal_chart.get("longitude", 0)

            # Calculate Julian day for progressed date
            jd = swe.julday(
                progressed_date.year,
                progressed_date.month,
                progressed_date.day,
                progressed_date.hour + progressed_date.minute/60.0
            )

            # Get ayanamsa
            ayanamsa = swe.get_ayanamsa_ut(jd)

            # Calculate progressed planets
            progressed_planets = {}
            planet_ids = {
                "Sun": swe.SUN,
                "Moon": swe.MOON,
                "Mercury": swe.MERCURY,
                "Venus": swe.VENUS,
                "Mars": swe.MARS,
                "Jupiter": swe.JUPITER,
                "Saturn": swe.SATURN,
            }

            for planet_name, planet_id in planet_ids.items():
                planet_data, _ = swe.calc_ut(jd, planet_id)
                tropical_long = planet_data[0]
                sidereal_long = (tropical_long - ayanamsa) % 360

                progressed_planets[planet_name] = {
                    "longitude": sidereal_long,
                    "sign": self._get_sign_from_longitude(sidereal_long),
                    "degree": sidereal_long % 30,
                    "change_from_natal": self._calculate_progression_change(
                        natal_chart, planet_name, sidereal_long
                    )
                }

            # Calculate progressed ascendant
            cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
            prog_asc_longitude = (ascmc[0] - ayanamsa) % 360

            progressed_ascendant = {
                "longitude": prog_asc_longitude,
                "sign": self._get_sign_from_longitude(prog_asc_longitude),
                "degree": prog_asc_longitude % 30
            }

            # Compare with natal chart
            comparison = self._compare_progressed_to_natal(
                natal_chart, progressed_planets, progressed_ascendant
            )

            # Generate interpretation
            interpretation = self._interpret_progressed_chart(
                current_age, progressed_planets, comparison
            )

            return {
                "current_age": current_age,
                "progressed_date": progressed_date.isoformat(),
                "progressed_ascendant": progressed_ascendant,
                "progressed_planets": progressed_planets,
                "major_changes": comparison["major_changes"],
                "current_themes": comparison["current_themes"],
                "interpretation": interpretation,
                "timing": {
                    "note": "Secondary progressions move slowly",
                    "sun_movement": "Approximately 1 degree per year",
                    "moon_movement": "Approximately 13 degrees per year"
                }
            }

        except Exception as e:
            return {"error": f"Failed to calculate progressed chart: {str(e)}"}

    def _calculate_progression_change(
        self,
        natal_chart: Dict[str, Any],
        planet_name: str,
        progressed_long: float
    ) -> Dict[str, Any]:
        """Calculate how much a planet has progressed from natal position"""
        natal_planets = natal_chart.get("planets", {})
        if planet_name not in natal_planets:
            return {"degrees_moved": 0, "sign_change": False}

        natal_long = natal_planets[planet_name].get("longitude", 0)
        degrees_moved = (progressed_long - natal_long) % 360

        # Handle retrograde cases (take shorter arc)
        if degrees_moved > 180:
            degrees_moved = degrees_moved - 360

        natal_sign = int(natal_long / 30)
        prog_sign = int(progressed_long / 30)
        sign_change = natal_sign != prog_sign

        return {
            "degrees_moved": round(degrees_moved, 2),
            "sign_change": sign_change,
            "new_sign": self._get_sign_from_longitude(progressed_long) if sign_change else None
        }

    def _compare_progressed_to_natal(
        self,
        natal_chart: Dict[str, Any],
        progressed_planets: Dict[str, Dict[str, Any]],
        progressed_asc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare progressed chart to natal chart"""
        major_changes = []
        current_themes = []

        # Check for sign changes
        for planet_name, planet_data in progressed_planets.items():
            change_data = planet_data.get("change_from_natal", {})
            if change_data.get("sign_change"):
                major_changes.append(
                    f"{planet_name} has progressed into {change_data.get('new_sign')}"
                )

        # Check progressed Moon (changes sign every 2-2.5 years)
        if "Moon" in progressed_planets:
            moon_sign = progressed_planets["Moon"]["sign"]
            current_themes.append(f"Current emotional focus: {moon_sign} energy")

        # Check progressed Sun (changes sign every 30 years approximately)
        if "Sun" in progressed_planets:
            sun_sign = progressed_planets["Sun"]["sign"]
            current_themes.append(f"Current life purpose emphasis: {sun_sign} qualities")

        return {
            "major_changes": major_changes if major_changes else ["No major sign changes yet"],
            "current_themes": current_themes
        }

    def _interpret_progressed_chart(
        self,
        age: int,
        progressed_planets: Dict[str, Dict[str, Any]],
        comparison: Dict[str, Any]
    ) -> str:
        """Generate interpretation of progressed chart"""
        interpretation = f"PROGRESSED CHART ANALYSIS (Age {age})\n\n"
        interpretation += "Secondary progressions show your current life stage and developmental focus.\n\n"

        interpretation += "MAJOR DEVELOPMENTS:\n"
        for change in comparison["major_changes"]:
            interpretation += f"- {change}\n"

        interpretation += "\nCURRENT THEMES:\n"
        for theme in comparison["current_themes"]:
            interpretation += f"- {theme}\n"

        interpretation += "\nThis progressed chart reflects your inner growth and evolution since birth."

        return interpretation

    # ============================================================================
    # SYNASTRY-SPECIFIC ANALYSIS
    # ============================================================================

    def analyze_synastry(
        self,
        chart_1: Dict[str, Any],
        chart_2: Dict[str, Any],
        focus: str = "romantic"
    ) -> Dict[str, Any]:
        """
        Dedicated synastry analysis with detailed aspect interpretations

        Args:
            chart_1: First person's chart
            chart_2: Second person's chart
            focus: Focus area (romantic, business, friendship, family)

        Returns:
            Detailed synastry analysis with aspect grid and interpretations
        """
        # Extract planet positions
        planets_1 = self._extract_planet_positions(chart_1)
        planets_2 = self._extract_planet_positions(chart_2)

        # Find all inter-chart aspects
        aspects = self._find_inter_chart_aspects(planets_1, planets_2)

        # Create aspect grid
        aspect_grid = self._create_aspect_grid(planets_1, planets_2, aspects)

        # Analyze double whammies (when planet A aspects planet B AND planet B aspects planet A)
        double_whammies = self._find_double_whammies(aspects)

        # Analyze focus-specific factors
        focus_analysis = self._analyze_synastry_focus(aspects, focus)

        # Calculate synastry score
        synastry_score = self._calculate_synastry_score(aspects, double_whammies, focus)

        # Generate detailed interpretations for each major aspect
        detailed_aspects = self._generate_detailed_aspect_interpretations(
            aspects[:10], focus  # Top 10 aspects
        )

        return {
            "focus": focus,
            "profile_1": self._get_profile_summary(chart_1),
            "profile_2": self._get_profile_summary(chart_2),
            "aspect_grid": aspect_grid,
            "all_aspects": aspects,
            "major_aspects": aspects[:10],
            "detailed_interpretations": detailed_aspects,
            "double_whammies": double_whammies,
            "synastry_score": synastry_score,
            "focus_analysis": focus_analysis,
            "summary": self._generate_synastry_summary(synastry_score, double_whammies, focus)
        }

    def _create_aspect_grid(
        self,
        planets_1: Dict[str, float],
        planets_2: Dict[str, float],
        aspects: List[Dict[str, Any]]
    ) -> List[List[str]]:
        """Create visual aspect grid"""
        # Create header row
        planet_names_2 = list(planets_2.keys())
        grid = [[""] + planet_names_2]

        # Create data rows
        for planet_1 in planets_1.keys():
            row = [planet_1]
            for planet_2 in planet_names_2:
                # Find aspect between planet_1 and planet_2
                aspect = next(
                    (a for a in aspects if
                     (a["planet_1"] == planet_1 and a["planet_2"] == planet_2) or
                     (a["planet_1"] == planet_2 and a["planet_2"] == planet_1)),
                    None
                )
                if aspect:
                    symbol = {
                        "conjunction": "☌",
                        "sextile": "⚹",
                        "square": "□",
                        "trine": "△",
                        "opposition": "☍"
                    }.get(aspect["aspect_type"], "-")
                    row.append(symbol)
                else:
                    row.append("-")
            grid.append(row)

        return grid

    def _find_double_whammies(self, aspects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find double whammy aspects (mutual aspects between same planets)"""
        double_whammies = []

        # Group aspects by planet pair
        aspect_pairs = {}
        for aspect in aspects:
            p1, p2 = aspect["planet_1"], aspect["planet_2"]
            # Create canonical key (alphabetically sorted)
            key = tuple(sorted([p1, p2]))

            if key not in aspect_pairs:
                aspect_pairs[key] = []
            aspect_pairs[key].append(aspect)

        # Find pairs where both directions exist
        for (planet_a, planet_b), pair_aspects in aspect_pairs.items():
            if len(pair_aspects) >= 2:
                double_whammies.append({
                    "planet_pair": f"{planet_a} - {planet_b}",
                    "aspects": pair_aspects,
                    "significance": "Double whammy - especially powerful connection",
                    "interpretation": self._interpret_double_whammy(planet_a, planet_b, pair_aspects)
                })

        return double_whammies

    def _interpret_double_whammy(
        self,
        planet_a: str,
        planet_b: str,
        aspects: List[Dict[str, Any]]
    ) -> str:
        """Interpret double whammy significance"""
        harmonious_count = sum(1 for a in aspects if a["is_harmonious"])
        if harmonious_count >= len(aspects):
            return f"Strong mutual {planet_a}-{planet_b} connection with harmonious energy"
        else:
            return f"Intense {planet_a}-{planet_b} dynamic requiring conscious integration"

    def _analyze_synastry_focus(self, aspects: List[Dict[str, Any]], focus: str) -> Dict[str, Any]:
        """Analyze synastry based on specific focus"""
        focus_planets = {
            "romantic": ["Venus", "Mars", "Moon", "Sun"],
            "business": ["Sun", "Saturn", "Mercury", "Jupiter"],
            "friendship": ["Moon", "Mercury", "Venus", "Jupiter"],
            "family": ["Moon", "Saturn", "Sun", "Jupiter"]
        }

        relevant_planets = focus_planets.get(focus, ["Sun", "Moon", "Venus"])
        focus_aspects = [
            a for a in aspects
            if any(p in relevant_planets for p in [a["planet_1"], a["planet_2"]])
        ]

        harmonious = sum(1 for a in focus_aspects if a["is_harmonious"])
        challenging = len(focus_aspects) - harmonious

        return {
            "focus_type": focus,
            "relevant_aspects_count": len(focus_aspects),
            "harmonious_count": harmonious,
            "challenging_count": challenging,
            "focus_score": (harmonious / len(focus_aspects) * 100) if focus_aspects else 50,
            "key_aspects": focus_aspects[:5]
        }

    def _calculate_synastry_score(
        self,
        aspects: List[Dict[str, Any]],
        double_whammies: List[Dict[str, Any]],
        focus: str
    ) -> Dict[str, Any]:
        """Calculate overall synastry score"""
        base_score = 50

        # Aspect scoring
        for aspect in aspects:
            if aspect["is_harmonious"]:
                if aspect["strength"] == "strong":
                    base_score += 3
                elif aspect["strength"] == "moderate":
                    base_score += 2
                else:
                    base_score += 1
            else:
                if aspect["strength"] == "strong":
                    base_score -= 2
                else:
                    base_score -= 1

        # Double whammy bonus
        base_score += len(double_whammies) * 5

        # Clamp score
        final_score = max(0, min(100, base_score))

        return {
            "overall_score": round(final_score, 1),
            "rating": self._get_synastry_rating(final_score),
            "aspects_analyzed": len(aspects),
            "double_whammies_found": len(double_whammies)
        }

    def _get_synastry_rating(self, score: float) -> str:
        """Get rating from score"""
        if score >= 85:
            return "Exceptional"
        elif score >= 75:
            return "Excellent"
        elif score >= 65:
            return "Very Good"
        elif score >= 55:
            return "Good"
        elif score >= 45:
            return "Moderate"
        else:
            return "Challenging"

    def _generate_detailed_aspect_interpretations(
        self,
        aspects: List[Dict[str, Any]],
        focus: str
    ) -> List[Dict[str, Any]]:
        """Generate detailed interpretations for major aspects"""
        interpretations = []

        for aspect in aspects:
            p1, p2 = aspect["planet_1"], aspect["planet_2"]
            aspect_type = aspect["aspect_type"]

            detailed_interp = self._get_detailed_aspect_meaning(p1, p2, aspect_type, focus)

            interpretations.append({
                "aspect": f"{p1} {aspect_type} {p2}",
                "strength": aspect["strength"],
                "harmonious": aspect["is_harmonious"],
                "basic_interpretation": aspect["interpretation"],
                "detailed_interpretation": detailed_interp,
                "advice": self._get_aspect_advice(p1, p2, aspect_type, focus)
            })

        return interpretations

    def _get_detailed_aspect_meaning(
        self,
        planet1: str,
        planet2: str,
        aspect_type: str,
        focus: str
    ) -> str:
        """Get detailed meaning of specific aspect"""
        # This is a simplified version - could be expanded with comprehensive database
        if planet1 == "Sun" and planet2 == "Moon":
            if aspect_type in ["conjunction", "trine", "sextile"]:
                return "Excellent emotional-identity harmony. You naturally understand each other's needs and purposes."
            else:
                return "Some tension between emotional needs and core identity. Requires understanding and compromise."

        elif "Venus" in [planet1, planet2] and "Mars" in [planet1, planet2]:
            if aspect_type in ["conjunction", "trine", "sextile"]:
                return "Strong romantic and physical attraction. Passion and affection flow naturally."
            else:
                return "Dynamic sexual chemistry with some friction. Can be exciting but may require balance."

        return f"{planet1}-{planet2} {aspect_type} creates specific dynamic in {focus} context"

    def _get_aspect_advice(self, planet1: str, planet2: str, aspect_type: str, focus: str) -> str:
        """Get advice for handling specific aspect"""
        if aspect_type in ["square", "opposition"]:
            return f"Work consciously with this {planet1}-{planet2} dynamic. Awareness transforms challenge into growth."
        else:
            return f"Nurture this positive {planet1}-{planet2} connection as a strength in your {focus}."

    def _generate_synastry_summary(
        self,
        score: Dict[str, Any],
        double_whammies: List[Dict[str, Any]],
        focus: str
    ) -> str:
        """Generate synastry summary"""
        summary = f"SYNASTRY ANALYSIS ({focus.upper()})\n\n"
        summary += f"Overall Compatibility: {score['rating']} ({score['overall_score']}/100)\n\n"

        if double_whammies:
            summary += f"Found {len(double_whammies)} double whammy aspect(s) - particularly powerful connections:\n"
            for dw in double_whammies[:3]:
                summary += f"- {dw['planet_pair']}: {dw['interpretation']}\n"

        summary += f"\nThis synastry analysis examines the interplay between both charts for {focus} compatibility."

        return summary


# Create singleton instance
chart_comparison_service = ChartComparisonService()
