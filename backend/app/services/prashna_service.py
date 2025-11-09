"""
Prashna (Horary Astrology) Service using Swiss Ephemeris
Answers specific questions based on the chart cast for the moment the question is asked
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime
import swisseph as swe
import pytz


class PrashnaService:
    """Service for Prashna (Horary) astrology calculations"""

    # Zodiac signs (Rashi)
    SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    # Sign lords
    SIGN_LORDS = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
        "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
        "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
        "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
    }

    # Nakshatras (27 lunar mansions)
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]

    # Planet constants
    PLANETS = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE,
        "Ketu": swe.MEAN_NODE
    }

    # Question type to house mapping (relevant house for each question type)
    QUESTION_HOUSES = {
        "career": 10,
        "relationship": 7,
        "health": 6,
        "finance": 2,
        "education": 5,
        "legal": 6,
        "travel": 9,
        "property": 4,
        "children": 5,
        "spiritual": 9,
        "general": 1
    }

    # Karaka (significator) planets for each question type
    QUESTION_KARAKAS = {
        "career": "Sun",
        "relationship": "Venus",
        "health": "Sun",
        "finance": "Jupiter",
        "education": "Jupiter",
        "legal": "Jupiter",
        "travel": "Moon",
        "property": "Mars",
        "children": "Jupiter",
        "spiritual": "Jupiter",
        "general": "Moon"
    }

    # Benefic and malefic planets
    BENEFICS = ["Jupiter", "Venus", "Moon", "Mercury"]
    MALEFICS = ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]

    def __init__(self):
        """Initialize Swiss Ephemeris with Lahiri ayanamsa"""
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    def analyze_prashna(
        self,
        question: str,
        question_type: str,
        query_datetime: datetime,
        latitude: float,
        longitude: float,
        timezone_str: str
    ) -> Dict[str, Any]:
        """
        Analyze a horary question using Prashna techniques

        Args:
            question: The question being asked
            question_type: Type of question (career, relationship, etc.)
            query_datetime: Exact moment the question was asked
            latitude: Location latitude
            longitude: Location longitude
            timezone_str: Timezone string

        Returns:
            Complete Prashna analysis with answer
        """

        # Convert to UTC
        if timezone_str != "UTC":
            try:
                local_tz = pytz.timezone(timezone_str)
                local_dt = local_tz.localize(query_datetime)
                query_datetime_utc = local_dt.astimezone(pytz.UTC)
            except:
                query_datetime_utc = query_datetime
        else:
            query_datetime_utc = query_datetime

        # Calculate Julian Day
        jd = swe.julday(
            query_datetime_utc.year,
            query_datetime_utc.month,
            query_datetime_utc.day,
            query_datetime_utc.hour + query_datetime_utc.minute/60.0 + query_datetime_utc.second/3600.0
        )

        # Get ayanamsa
        ayanamsa = swe.get_ayanamsa_ut(jd)

        # Calculate Ascendant
        cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
        asc_longitude = ascmc[0]
        asc_sidereal = (asc_longitude - ayanamsa) % 360
        asc_sign = int(asc_sidereal / 30)
        asc_degree = asc_sidereal % 30

        # Calculate all planets
        planets = self._calculate_planets(jd, ayanamsa, asc_sign)

        # Calculate houses
        houses = self._calculate_houses(asc_sign, planets)

        # Analyze Lagna (Ascendant)
        lagna_analysis = self._analyze_lagna(asc_sign, asc_degree, planets)

        # Analyze Moon (crucial in Prashna)
        moon_analysis = self._analyze_moon(planets["Moon"], jd, planets)

        # Analyze question-specific factors
        question_analysis = self._analyze_question(
            question_type, houses, planets, asc_sign
        )

        # Derive answer
        answer = self._derive_answer(
            question_type, lagna_analysis, moon_analysis,
            question_analysis, planets, houses
        )

        # Detect yogas
        yogas = self._detect_prashna_yogas(planets, asc_sign)

        # Calculate planetary strengths
        strengths = self._calculate_planetary_strengths(planets, asc_sign)

        return {
            "question": question,
            "question_type": question_type,
            "query_datetime": query_datetime.isoformat(),
            "location": {"latitude": latitude, "longitude": longitude},
            "ascendant": lagna_analysis,
            "moon": moon_analysis,
            "planets": self._format_planets_for_response(planets),
            "houses": houses,
            "question_analysis": question_analysis,
            "answer": answer,
            "yogas_present": yogas,
            "planetary_strengths": strengths,
            "overall_chart_strength": self._assess_chart_strength(planets, lagna_analysis, moon_analysis)
        }

    def _calculate_planets(self, jd: float, ayanamsa: float, asc_sign: int) -> Dict[str, Dict[str, Any]]:
        """Calculate positions of all planets"""
        planets = {}

        for planet_name, planet_id in self.PLANETS.items():
            if planet_name == "Ketu":
                # Ketu is 180° from Rahu
                rahu_pos = planets["Rahu"]["longitude"]
                ketu_pos = (rahu_pos + 180) % 360
                planet_data = planets["Rahu"].copy()
                planet_data["longitude"] = ketu_pos
                planet_data["sign"] = self.SIGNS[int(ketu_pos / 30)]
                planet_data["degree"] = ketu_pos % 30
            else:
                # Calculate planet position
                planet_data_raw, ret_flag = swe.calc_ut(jd, planet_id)
                tropical_long = planet_data_raw[0]
                sidereal_long = (tropical_long - ayanamsa) % 360

                planet_data = {
                    "longitude": sidereal_long,
                    "sign": self.SIGNS[int(sidereal_long / 30)],
                    "degree": sidereal_long % 30,
                    "is_retrograde": ret_flag < 0
                }

            # Calculate nakshatra
            nakshatra_num = int(planet_data["longitude"] / 13.333333)
            pada = int((planet_data["longitude"] % 13.333333) / 3.333333) + 1
            planet_data["nakshatra"] = self.NAKSHATRAS[nakshatra_num]
            planet_data["nakshatra_pada"] = pada

            # Calculate house
            planet_sign = int(planet_data["longitude"] / 30)
            house = ((planet_sign - asc_sign) % 12) + 1
            planet_data["house"] = house

            planets[planet_name] = planet_data

        return planets

    def _calculate_houses(self, asc_sign: int, planets: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate house information"""
        houses = []

        for i in range(12):
            house_num = i + 1
            house_sign_num = (asc_sign + i) % 12
            house_sign = self.SIGNS[house_sign_num]
            house_lord = self.SIGN_LORDS[house_sign]

            # Find lord's position
            lord_data = planets[house_lord]
            lord_house = lord_data["house"]
            lord_position = f"{lord_data['sign']} {lord_data['degree']:.1f}°"

            # House significance
            significance = self._get_house_significance(house_num)

            # Assess house strength
            strength = self._assess_house_strength(house_num, house_lord, planets, asc_sign)

            houses.append({
                "house_number": house_num,
                "sign": house_sign,
                "lord": house_lord,
                "lord_position": lord_position,
                "lord_house": lord_house,
                "significance": significance,
                "strength": strength
            })

        return houses

    def _analyze_lagna(self, asc_sign: int, asc_degree: float, planets: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze Lagna (Ascendant) for Prashna"""
        sign_name = self.SIGNS[asc_sign]
        lord = self.SIGN_LORDS[sign_name]
        lord_data = planets[lord]

        # Assess lord strength
        lord_strength = "strong" if lord_data["house"] in [1, 4, 5, 7, 9, 10] else "weak"
        if lord_data["is_retrograde"]:
            lord_strength = "weakened"

        return {
            "sign": sign_name,
            "degree": asc_degree,
            "lord": lord,
            "lord_position": f"{lord_data['sign']} {lord_data['degree']:.1f}°",
            "lord_house": lord_data["house"],
            "lord_strength": lord_strength,
            "significance": "Represents the querent (person asking the question) and their current state"
        }

    def _analyze_moon(self, moon_data: Dict[str, Any], jd: float, planets: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Detailed Moon analysis for Prashna (Moon is crucial in horary)"""
        # Determine lunar phase
        sun_long = planets["Sun"]["longitude"]
        moon_long = moon_data["longitude"]
        phase_diff = (moon_long - sun_long) % 360

        if 0 <= phase_diff < 90:
            lunar_phase = "Waxing Crescent"
            is_waxing = True
        elif 90 <= phase_diff < 180:
            lunar_phase = "Waxing Gibbous"
            is_waxing = True
        elif 180 <= phase_diff < 270:
            lunar_phase = "Waning Gibbous"
            is_waxing = False
        else:
            lunar_phase = "Waning Crescent"
            is_waxing = False

        # Calculate aspects (simple opposition/conjunction check)
        aspects_from = []
        aspects_to = []

        for planet_name, planet_info in planets.items():
            if planet_name == "Moon":
                continue

            diff = abs(moon_long - planet_info["longitude"])
            if diff > 180:
                diff = 360 - diff

            if diff < 10:  # Conjunction
                aspects_from.append(f"{planet_name} (conjunction)")
                aspects_to.append(f"{planet_name} (conjunction)")
            elif 170 < diff < 190:  # Opposition
                aspects_from.append(f"{planet_name} (opposition)")
                aspects_to.append(f"{planet_name} (opposition)")

        # Moon strength assessment
        if moon_data["sign"] in ["Taurus", "Cancer"]:
            strength = "excellent"
        elif is_waxing and phase_diff < 180:
            strength = "good"
        elif not is_waxing:
            strength = "weak"
        else:
            strength = "moderate"

        interpretation = self._interpret_moon_position(
            moon_data, is_waxing, lunar_phase, aspects_from
        )

        return {
            "sign": moon_data["sign"],
            "nakshatra": moon_data["nakshatra"],
            "pada": moon_data["nakshatra_pada"],
            "degree": moon_data["degree"],
            "house": moon_data["house"],
            "is_waxing": is_waxing,
            "lunar_phase": lunar_phase,
            "strength": strength,
            "aspects_from": aspects_from,
            "aspects_to": aspects_to,
            "interpretation": interpretation
        }

    def _analyze_question(
        self,
        question_type: str,
        houses: List[Dict[str, Any]],
        planets: Dict[str, Dict[str, Any]],
        asc_sign: int
    ) -> Dict[str, Any]:
        """Analyze factors specific to the question type"""

        # Get relevant house
        relevant_house = self.QUESTION_HOUSES.get(question_type, 1)
        house_info = houses[relevant_house - 1]

        # Get karaka planet
        karaka = self.QUESTION_KARAKAS.get(question_type, "Moon")
        karaka_data = planets[karaka]

        # Assess strengths
        house_lord_strength = self._assess_planet_strength(house_info["lord"], planets, asc_sign)
        karaka_strength = self._assess_planet_strength(karaka, planets, asc_sign)

        # Find supporting and opposing factors
        supporting = []
        opposing = []

        # Check if benefics aspect the relevant house or karaka
        for benefic in self.BENEFICS:
            if benefic in planets:
                benefic_house = planets[benefic]["house"]
                if benefic_house == relevant_house:
                    supporting.append(f"{benefic} in relevant house {relevant_house}")

        # Check if malefics aspect the relevant house or karaka
        for malefic in self.MALEFICS:
            if malefic in planets:
                malefic_house = planets[malefic]["house"]
                if malefic_house == relevant_house:
                    opposing.append(f"{malefic} in relevant house {relevant_house}")

        return {
            "relevant_house": relevant_house,
            "house_lord": house_info["lord"],
            "house_lord_position": house_info["lord_position"],
            "house_lord_strength": house_lord_strength,
            "karaka_planet": karaka,
            "karaka_position": f"{karaka_data['sign']} {karaka_data['degree']:.1f}°",
            "karaka_strength": karaka_strength,
            "supporting_factors": supporting if supporting else ["No major supporting factors detected"],
            "opposing_factors": opposing if opposing else ["No major opposing factors detected"]
        }

    def _derive_answer(
        self,
        question_type: str,
        lagna: Dict[str, Any],
        moon: Dict[str, Any],
        question_analysis: Dict[str, Any],
        planets: Dict[str, Dict[str, Any]],
        houses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Derive the final answer based on all factors"""

        # Calculate score based on various factors
        score = 0
        max_score = 0
        reasons = []

        # Lagna lord strength (20 points)
        max_score += 20
        if lagna["lord_strength"] == "strong":
            score += 20
            reasons.append("Lagna lord is strong, favorable for success")
        elif lagna["lord_strength"] == "weak":
            score += 10
            reasons.append("Lagna lord is moderately placed")
        else:
            reasons.append("Lagna lord is weakened")

        # Moon strength (30 points - Moon is most important in Prashna)
        max_score += 30
        if moon["strength"] == "excellent":
            score += 30
            reasons.append("Moon is excellently placed, highly auspicious")
        elif moon["strength"] == "good":
            score += 20
            reasons.append("Moon is well-placed and waxing")
        elif moon["strength"] == "moderate":
            score += 15
            reasons.append("Moon has moderate strength")
        else:
            score += 5
            reasons.append("Moon is weak, indicating challenges")

        # Question house lord strength (25 points)
        max_score += 25
        if question_analysis["house_lord_strength"] == "strong":
            score += 25
            reasons.append(f"House lord {question_analysis['house_lord']} is strong")
        elif question_analysis["house_lord_strength"] == "moderate":
            score += 15
        else:
            reasons.append(f"House lord {question_analysis['house_lord']} is weak")

        # Karaka strength (25 points)
        max_score += 25
        if question_analysis["karaka_strength"] == "strong":
            score += 25
            reasons.append(f"Karaka planet {question_analysis['karaka_planet']} is strong")
        elif question_analysis["karaka_strength"] == "moderate":
            score += 15
        else:
            reasons.append(f"Karaka planet {question_analysis['karaka_planet']} is weak")

        # Calculate percentage
        percentage = (score / max_score) * 100

        # Determine outcome
        if percentage >= 75:
            outcome = "favorable"
            confidence = "high"
            summary = "The chart indicates a highly favorable outcome. Proceed with confidence."
        elif percentage >= 55:
            outcome = "favorable"
            confidence = "medium"
            summary = "The chart shows favorable indications, though some caution is advised."
        elif percentage >= 40:
            outcome = "mixed"
            confidence = "medium"
            summary = "The outcome is mixed with both favorable and challenging factors."
        elif percentage >= 25:
            outcome = "unfavorable"
            confidence = "medium"
            summary = "The chart shows challenging factors. Reconsider timing or approach."
        else:
            outcome = "unfavorable"
            confidence = "high"
            summary = "The chart strongly advises against proceeding at this time."

        # Timing estimation
        timing = self._estimate_timing(outcome, moon, question_analysis)

        # Detailed interpretation
        detailed = self._create_detailed_interpretation(
            question_type, outcome, lagna, moon, question_analysis, reasons
        )

        # Recommendations
        recommendations = self._generate_recommendations(outcome, question_type, moon, lagna)

        # Precautions
        precautions = self._generate_precautions(question_analysis, moon)

        return {
            "outcome": outcome,
            "confidence": confidence,
            "timing": timing,
            "summary": summary,
            "detailed_interpretation": detailed,
            "recommendations": recommendations,
            "precautions": precautions
        }

    def _interpret_moon_position(
        self,
        moon_data: Dict[str, Any],
        is_waxing: bool,
        lunar_phase: str,
        aspects: List[str]
    ) -> str:
        """Generate Moon interpretation"""
        interpretation = f"Moon in {moon_data['sign']} in {moon_data['nakshatra']} nakshatra. "

        if is_waxing:
            interpretation += "Waxing Moon indicates growth and expansion. "
        else:
            interpretation += "Waning Moon suggests completion and release. "

        if moon_data["sign"] in ["Taurus", "Cancer"]:
            interpretation += "Moon is in its exaltation/own sign, giving excellent results. "

        if aspects:
            interpretation += f"Influenced by: {', '.join(aspects)}. "

        return interpretation

    def _estimate_timing(
        self,
        outcome: str,
        moon: Dict[str, Any],
        question_analysis: Dict[str, Any]
    ) -> str:
        """Estimate timing for the outcome"""
        if outcome == "unfavorable":
            return "Not recommended at this time"

        # Use Moon's nakshatra for timing
        nakshatra = moon["nakshatra"]
        house = question_analysis["relevant_house"]

        if house in [1, 2, 3]:
            timing = "Within 1-3 months"
        elif house in [4, 5, 6]:
            timing = "Within 3-6 months"
        elif house in [7, 8, 9]:
            timing = "Within 6-9 months"
        else:
            timing = "Within 9-12 months"

        return timing

    def _create_detailed_interpretation(
        self,
        question_type: str,
        outcome: str,
        lagna: Dict[str, Any],
        moon: Dict[str, Any],
        question_analysis: Dict[str, Any],
        reasons: List[str]
    ) -> str:
        """Create detailed interpretation"""
        interpretation = f"Prashna analysis for {question_type} question:\n\n"
        interpretation += f"The querent is represented by {lagna['sign']} Lagna with lord {lagna['lord']} "
        interpretation += f"placed in {lagna['lord_house']} house.\n\n"
        interpretation += f"The Moon, crucial in Prashna, is in {moon['sign']} in the {moon['house']} house, "
        interpretation += f"currently in {moon['lunar_phase']} phase.\n\n"
        interpretation += f"For this {question_type} question, house {question_analysis['relevant_house']} "
        interpretation += f"and planet {question_analysis['karaka_planet']} are most significant.\n\n"
        interpretation += "Key factors:\n"
        for reason in reasons:
            interpretation += f"- {reason}\n"

        return interpretation

    def _generate_recommendations(
        self,
        outcome: str,
        question_type: str,
        moon: Dict[str, Any],
        lagna: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        if outcome == "favorable":
            recommendations.append("Proceed with the matter as planetary influences are supportive")
            if moon["is_waxing"]:
                recommendations.append("Act during waxing Moon for best results")
        else:
            recommendations.append("Wait for a more auspicious time")
            recommendations.append("Strengthen relevant planets through remedies")

        # Question-specific recommendations
        if question_type == "career":
            recommendations.append("Focus on Sun and Saturn strength for career matters")
        elif question_type == "relationship":
            recommendations.append("Venus and 7th house need to be favorable")

        return recommendations

    def _generate_precautions(
        self,
        question_analysis: Dict[str, Any],
        moon: Dict[str, Any]
    ) -> List[str]:
        """Generate precautions"""
        precautions = []

        if question_analysis["opposing_factors"]:
            for factor in question_analysis["opposing_factors"]:
                if "Saturn" in factor:
                    precautions.append("Saturn's influence suggests delays - be patient")
                if "Mars" in factor:
                    precautions.append("Mars indicates conflicts - avoid confrontations")
                if "Rahu" in factor or "Ketu" in factor:
                    precautions.append("Shadow planets suggest hidden factors - investigate thoroughly")

        if moon["strength"] == "weak":
            precautions.append("Weak Moon suggests emotional uncertainty - seek clarity before proceeding")

        if not precautions:
            precautions.append("No major precautions indicated")

        return precautions

    def _detect_prashna_yogas(self, planets: Dict[str, Dict[str, Any]], asc_sign: int) -> List[Dict[str, str]]:
        """Detect important yogas in Prashna chart"""
        yogas = []

        # Check for benefic planets in Kendra (1, 4, 7, 10)
        kendras = [1, 4, 7, 10]
        for benefic in self.BENEFICS:
            if benefic in planets and planets[benefic]["house"] in kendras:
                yogas.append({
                    "name": f"{benefic} in Kendra",
                    "significance": "Favorable - benefic in angular house"
                })

        # Check Moon-Jupiter combination
        moon_house = planets["Moon"]["house"]
        jupiter_house = planets["Jupiter"]["house"]
        if abs(moon_house - jupiter_house) <= 1:
            yogas.append({
                "name": "Moon-Jupiter association",
                "significance": "Highly auspicious - wisdom and emotional clarity"
            })

        return yogas

    def _calculate_planetary_strengths(self, planets: Dict[str, Dict[str, Any]], asc_sign: int) -> Dict[str, str]:
        """Calculate strength of each planet"""
        strengths = {}

        for planet_name, planet_data in planets.items():
            strength = self._assess_planet_strength(planet_name, planets, asc_sign)
            strengths[planet_name] = strength

        return strengths

    def _assess_planet_strength(self, planet_name: str, planets: Dict[str, Dict[str, Any]], asc_sign: int) -> str:
        """Assess individual planet strength"""
        if planet_name not in planets:
            return "unknown"

        planet_data = planets[planet_name]
        house = planet_data["house"]

        # Strong houses: 1, 4, 5, 7, 9, 10
        if house in [1, 4, 5, 7, 9, 10]:
            strength = "strong"
        elif house in [2, 3, 11]:
            strength = "moderate"
        else:
            strength = "weak"

        # Retrograde weakens
        if planet_data.get("is_retrograde", False):
            if strength == "strong":
                strength = "moderate"
            else:
                strength = "weak"

        return strength

    def _assess_chart_strength(
        self,
        planets: Dict[str, Dict[str, Any]],
        lagna: Dict[str, Any],
        moon: Dict[str, Any]
    ) -> str:
        """Assess overall chart strength"""
        score = 0

        # Strong lagna
        if lagna["lord_strength"] == "strong":
            score += 2

        # Strong moon
        if moon["strength"] in ["excellent", "good"]:
            score += 2

        # Benefics in kendras
        for benefic in self.BENEFICS:
            if benefic in planets and planets[benefic]["house"] in [1, 4, 7, 10]:
                score += 1

        if score >= 5:
            return "excellent"
        elif score >= 3:
            return "good"
        elif score >= 1:
            return "moderate"
        else:
            return "weak"

    def _format_planets_for_response(self, planets: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format planets for API response"""
        formatted = []
        for name, data in planets.items():
            formatted.append({
                "name": name,
                "sign": data["sign"],
                "degree": data["degree"],
                "house": data["house"],
                "is_retrograde": data.get("is_retrograde", False),
                "nakshatra": data["nakshatra"],
                "nakshatra_pada": data["nakshatra_pada"]
            })
        return formatted

    def _get_house_significance(self, house_num: int) -> str:
        """Get significance of each house"""
        significances = {
            1: "Self, personality, vitality",
            2: "Wealth, family, speech",
            3: "Courage, siblings, skills",
            4: "Mother, home, property, emotions",
            5: "Children, education, creativity, intelligence",
            6: "Enemies, diseases, debts, obstacles",
            7: "Marriage, partnerships, relationships",
            8: "Longevity, transformation, hidden matters",
            9: "Fortune, dharma, father, spirituality",
            10: "Career, status, profession, authority",
            11: "Gains, income, aspirations, friendships",
            12: "Losses, expenditure, spirituality, foreign lands"
        }
        return significances.get(house_num, "Unknown")

    def _assess_house_strength(
        self,
        house_num: int,
        house_lord: str,
        planets: Dict[str, Dict[str, Any]],
        asc_sign: int
    ) -> str:
        """Assess strength of a house"""
        lord_data = planets[house_lord]
        lord_house = lord_data["house"]

        # Lord in kendra/trikona
        if lord_house in [1, 4, 5, 7, 9, 10]:
            strength = "strong"
        elif lord_house in [2, 3, 11]:
            strength = "moderate"
        else:
            strength = "weak"

        # Check for planets in the house
        planets_in_house = [name for name, data in planets.items() if data["house"] == house_num]
        if any(p in self.BENEFICS for p in planets_in_house):
            strength = "strong"
        elif any(p in self.MALEFICS for p in planets_in_house):
            if strength == "strong":
                strength = "moderate"
            else:
                strength = "weak"

        return strength


# Create singleton instance
prashna_service = PrashnaService()
