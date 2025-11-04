"""
Remedy Service
Traditional Vedic astrology remedies with modern practical suggestions
Rule-based remedy selection based on chart analysis and specific issues
"""

from typing import Dict, Any, List, Optional
from enum import Enum


class RemedyType(str, Enum):
    """Types of remedies"""
    MANTRA = "mantra"
    GEMSTONE = "gemstone"
    CHARITY = "charity"
    FASTING = "fasting"
    RITUAL = "ritual"
    LIFESTYLE = "lifestyle"
    YANTRA = "yantra"
    COLOR = "color"
    DIRECTION = "direction"


class PlanetRemedyStrength(str, Enum):
    """How urgently a remedy is needed"""
    CRITICAL = "critical"      # Very weak/afflicted planet
    HIGH = "high"             # Moderately afflicted
    MEDIUM = "medium"         # Slight weakness
    MAINTENANCE = "maintenance"  # For already good planets


class RemedyService:
    """
    Service for generating traditional Vedic remedies based on chart analysis

    Features:
    - Planet-specific remedies
    - House-based remedies
    - Dasha period remedies
    - Domain-specific remedies (career, health, etc.)
    - Practical modern alternatives
    """

    def __init__(self):
        """Initialize remedy database"""
        self.planet_remedies = self._initialize_planet_remedies()
        self.house_remedies = self._initialize_house_remedies()
        self.yoga_remedies = self._initialize_yoga_remedies()

    def generate_remedies(
        self,
        chart_data: Dict[str, Any],
        domain: Optional[str] = None,
        specific_issue: Optional[str] = None,
        max_remedies: int = 5,
        include_practical: bool = True
    ) -> Dict[str, Any]:
        """
        Generate personalized remedies based on chart analysis

        Args:
            chart_data: Complete birth chart data
            domain: Specific life domain (career, health, wealth, etc.)
            specific_issue: Specific problem to address
            max_remedies: Maximum number of remedies to return
            include_practical: Include modern practical alternatives

        Returns:
            Dictionary with categorized remedies and explanations
        """
        print(f"🔮 Generating remedies for domain: {domain or 'general'}")

        # Analyze chart to identify weak/afflicted planets
        weak_planets = self._identify_weak_planets(chart_data)

        # Get current dasha
        current_dasha = chart_data.get('dasha', {}).get('current_dasha')

        # Generate remedies based on analysis
        remedies = []

        # 1. Dasha-based remedies (most important)
        if current_dasha:
            dasha_remedies = self._get_dasha_remedies(current_dasha, chart_data)
            remedies.extend(dasha_remedies[:2])  # Top 2 dasha remedies

        # 2. Domain-specific remedies
        if domain:
            domain_remedies = self._get_domain_remedies(domain, chart_data)
            remedies.extend(domain_remedies[:2])

        # 3. Weak planet remedies
        for planet_info in weak_planets[:2]:  # Top 2 weak planets
            planet_remedies = self._get_planet_remedies(
                planet_info['planet'],
                planet_info['strength'],
                chart_data
            )
            remedies.extend(planet_remedies[:1])

        # 4. General strengthening remedies
        general_remedies = self._get_general_remedies(chart_data)
        remedies.extend(general_remedies[:1])

        # Limit to max_remedies
        remedies = remedies[:max_remedies]

        # Add practical alternatives if requested
        if include_practical:
            for remedy in remedies:
                remedy['practical_alternative'] = self._get_practical_alternative(remedy)

        return {
            "remedies": remedies,
            "weak_planets": weak_planets,
            "current_dasha": current_dasha,
            "priority": "high" if len(weak_planets) > 2 else "medium",
            "total_count": len(remedies)
        }

    def _identify_weak_planets(self, chart_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify weak or afflicted planets in the chart"""
        weak_planets = []

        planets = chart_data.get('planets', {})

        for planet, data in planets.items():
            strength = self._calculate_planet_strength(planet, data, chart_data)

            if strength in [PlanetRemedyStrength.CRITICAL, PlanetRemedyStrength.HIGH]:
                weak_planets.append({
                    'planet': planet,
                    'strength': strength,
                    'house': data.get('house'),
                    'sign': data.get('sign'),
                    'retrograde': data.get('retrograde', False)
                })

        # Sort by severity (critical first)
        weak_planets.sort(
            key=lambda x: 0 if x['strength'] == PlanetRemedyStrength.CRITICAL else 1
        )

        return weak_planets

    def _calculate_planet_strength(
        self,
        planet: str,
        planet_data: Dict[str, Any],
        chart_data: Dict[str, Any]
    ) -> str:
        """
        Calculate relative strength of a planet
        Simplified version (full Shadbala would be more complex)
        """
        score = 0

        # Exaltation/Debilitation
        sign = planet_data.get('sign', '')
        exalted_signs = {
            'Sun': 'Aries',
            'Moon': 'Taurus',
            'Mars': 'Capricorn',
            'Mercury': 'Virgo',
            'Jupiter': 'Cancer',
            'Venus': 'Pisces',
            'Saturn': 'Libra'
        }

        debilitated_signs = {
            'Sun': 'Libra',
            'Moon': 'Scorpio',
            'Mars': 'Cancer',
            'Mercury': 'Pisces',
            'Jupiter': 'Capricorn',
            'Venus': 'Virgo',
            'Saturn': 'Aries'
        }

        if sign == exalted_signs.get(planet):
            score += 3  # Very strong
        elif sign == debilitated_signs.get(planet):
            score -= 3  # Very weak

        # House position
        house = planet_data.get('house', 0)
        if house in [1, 4, 7, 10]:  # Angular houses (Kendra)
            score += 2
        elif house in [5, 9]:  # Trines (Trikona)
            score += 1
        elif house in [6, 8, 12]:  # Dusthana (difficult houses)
            score -= 2

        # Retrograde
        if planet_data.get('retrograde', False):
            score -= 1

        # Determine strength level
        if score <= -3:
            return PlanetRemedyStrength.CRITICAL
        elif score <= -1:
            return PlanetRemedyStrength.HIGH
        elif score <= 1:
            return PlanetRemedyStrength.MEDIUM
        else:
            return PlanetRemedyStrength.MAINTENANCE

    def _get_dasha_remedies(
        self,
        dasha_lord: str,
        chart_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get remedies for current dasha period"""
        if dasha_lord not in self.planet_remedies:
            return []

        remedies = self.planet_remedies[dasha_lord]

        return [
            {
                "type": RemedyType.MANTRA,
                "planet": dasha_lord,
                "title": f"{dasha_lord} Dasha Mantra",
                "description": remedies['mantra']['description'],
                "mantra": remedies['mantra']['text'],
                "repetitions": remedies['mantra']['count'],
                "timing": remedies['mantra']['timing'],
                "purpose": f"Strengthen {dasha_lord} during current dasha period",
                "difficulty": "easy",
                "cost": "free"
            },
            {
                "type": RemedyType.CHARITY,
                "planet": dasha_lord,
                "title": f"{dasha_lord} Charity",
                "description": remedies['charity']['description'],
                "items": remedies['charity']['items'],
                "day": remedies['charity']['day'],
                "purpose": f"Appease {dasha_lord} through charitable acts",
                "difficulty": "easy",
                "cost": "low"
            }
        ]

    def _get_domain_remedies(
        self,
        domain: str,
        chart_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get remedies for specific life domain"""
        domain_planet_map = {
            'career': ['Sun', 'Saturn', 'Jupiter'],
            'wealth': ['Jupiter', 'Venus', 'Mercury'],
            'relationships': ['Venus', 'Moon'],
            'health': ['Sun', 'Mars', 'Moon'],
            'education': ['Mercury', 'Jupiter'],
            'spirituality': ['Jupiter', 'Moon']
        }

        relevant_planets = domain_planet_map.get(domain, ['Jupiter'])
        remedies = []

        for planet in relevant_planets[:1]:  # Primary planet for domain
            if planet in self.planet_remedies:
                planet_remedy = self.planet_remedies[planet]
                remedies.append({
                    "type": RemedyType.GEMSTONE,
                    "planet": planet,
                    "title": f"{planet} Gemstone for {domain.title()}",
                    "description": planet_remedy['gemstone']['description'],
                    "gemstone": planet_remedy['gemstone']['primary'],
                    "alternative": planet_remedy['gemstone']['alternative'],
                    "metal": planet_remedy['gemstone']['metal'],
                    "finger": planet_remedy['gemstone']['finger'],
                    "day": planet_remedy['gemstone']['day'],
                    "purpose": f"Strengthen {planet} for {domain} success",
                    "difficulty": "medium",
                    "cost": "medium-high"
                })

        return remedies

    def _get_planet_remedies(
        self,
        planet: str,
        strength: str,
        chart_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get remedies for specific weak planet"""
        if planet not in self.planet_remedies:
            return []

        remedy_data = self.planet_remedies[planet]

        # For critical/high weakness, recommend fasting
        if strength in [PlanetRemedyStrength.CRITICAL, PlanetRemedyStrength.HIGH]:
            return [{
                "type": RemedyType.FASTING,
                "planet": planet,
                "title": f"{planet} Fast",
                "description": remedy_data['fasting']['description'],
                "day": remedy_data['fasting']['day'],
                "foods_to_avoid": remedy_data['fasting']['avoid'],
                "recommended_foods": remedy_data['fasting']['eat'],
                "purpose": f"Purify and strengthen {planet}",
                "difficulty": "medium",
                "cost": "free"
            }]

        return []

    def _get_general_remedies(self, chart_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get general strengthening remedies"""
        return [{
            "type": RemedyType.RITUAL,
            "planet": "General",
            "title": "Daily Surya Namaskar (Sun Salutation)",
            "description": "12 rounds of Surya Namaskar at sunrise strengthens overall vitality and planetary energies",
            "steps": [
                "Face east at sunrise",
                "Perform 12 rounds of Surya Namaskar",
                "Chant Surya mantras with each round",
                "Meditate for 5 minutes after"
            ],
            "timing": "Sunrise (5:30-7:00 AM)",
            "duration": "20-30 minutes",
            "purpose": "Overall health, vitality, and planetary harmony",
            "difficulty": "medium",
            "cost": "free"
        }]

    def _get_practical_alternative(self, remedy: Dict[str, Any]) -> Dict[str, Any]:
        """Get modern practical alternative to traditional remedy"""
        remedy_type = remedy['type']

        practical_alternatives = {
            RemedyType.MANTRA: {
                "title": "Meditation & Affirmation",
                "description": "Modern mindfulness meditation with positive affirmations",
                "action": f"Meditate 10 minutes daily while focusing on the qualities of {remedy.get('planet', 'balance')}"
            },
            RemedyType.GEMSTONE: {
                "title": "Color Therapy",
                "description": f"Wear colors associated with {remedy.get('planet', 'the planet')}",
                "action": f"Incorporate {remedy.get('planet', 'planetary')} colors in your wardrobe and home decor"
            },
            RemedyType.CHARITY: {
                "title": "Volunteering",
                "description": "Modern charitable giving through verified organizations",
                "action": f"Donate or volunteer on {remedy.get('day', 'any day')} to relevant causes"
            },
            RemedyType.FASTING: {
                "title": "Mindful Eating",
                "description": "Conscious dietary choices for planetary balance",
                "action": f"Practice mindful eating and avoid heavy foods on {remedy.get('day', 'specific days')}"
            },
            RemedyType.RITUAL: {
                "title": "Daily Practice",
                "description": "Modern adaptation of traditional practices",
                "action": "Create a consistent daily wellness routine with exercise, meditation, and reflection"
            }
        }

        return practical_alternatives.get(
            remedy_type,
            {
                "title": "General Wellness",
                "description": "Maintain healthy lifestyle practices",
                "action": "Focus on balanced diet, exercise, and stress management"
            }
        )

    def _initialize_planet_remedies(self) -> Dict[str, Dict]:
        """Initialize comprehensive planet remedy database"""
        return {
            "Sun": {
                "mantra": {
                    "text": "Om Hraam Hreem Hraum Sah Suryaya Namah",
                    "count": 108,
                    "timing": "Sunrise, facing east",
                    "description": "Solar mantra for vitality, authority, and father relationships"
                },
                "gemstone": {
                    "primary": "Ruby",
                    "alternative": "Red Garnet",
                    "metal": "Gold or Copper",
                    "finger": "Ring finger (right hand)",
                    "day": "Sunday during sunrise",
                    "description": "Strengthens leadership, confidence, and life force energy"
                },
                "charity": {
                    "items": ["Wheat", "Jaggery", "Copper items", "Red cloth"],
                    "day": "Sunday",
                    "description": "Donate to father figures, government workers, or temples"
                },
                "fasting": {
                    "day": "Sunday",
                    "avoid": ["Salt", "Sour foods"],
                    "eat": ["Wheat products", "Jaggery", "Red fruits"],
                    "description": "Fast from sunrise to sunset or avoid heavy meals"
                },
                "color": "Red, Orange, Golden",
                "direction": "East"
            },
            "Moon": {
                "mantra": {
                    "text": "Om Shraam Shreem Shraum Sah Chandraya Namah",
                    "count": 108,
                    "timing": "Evening, facing northwest",
                    "description": "Lunar mantra for emotions, mind, and mother relationships"
                },
                "gemstone": {
                    "primary": "Pearl",
                    "alternative": "Moonstone",
                    "metal": "Silver",
                    "finger": "Little finger (right hand)",
                    "day": "Monday during evening",
                    "description": "Enhances emotional balance, intuition, and mental peace"
                },
                "charity": {
                    "items": ["White rice", "Milk", "White cloth", "Silver"],
                    "day": "Monday",
                    "description": "Donate to mothers, elderly women, or mental health causes"
                },
                "fasting": {
                    "day": "Monday",
                    "avoid": ["Non-vegetarian food"],
                    "eat": ["White foods", "Milk products", "Rice"],
                    "description": "Light fasting or consume only white-colored sattvic foods"
                },
                "color": "White, Cream, Light Blue",
                "direction": "Northwest"
            },
            "Mars": {
                "mantra": {
                    "text": "Om Kraam Kreem Kraum Sah Bhaumaya Namah",
                    "count": 108,
                    "timing": "Tuesday morning",
                    "description": "Mars mantra for courage, energy, and siblings"
                },
                "gemstone": {
                    "primary": "Red Coral",
                    "alternative": "Carnelian",
                    "metal": "Copper or Gold",
                    "finger": "Ring finger (right hand)",
                    "day": "Tuesday morning",
                    "description": "Boosts courage, energy, property, and brother relationships"
                },
                "charity": {
                    "items": ["Red lentils", "Wheat", "Copper", "Red cloth"],
                    "day": "Tuesday",
                    "description": "Donate to soldiers, athletes, surgeons, or Hanuman temples"
                },
                "fasting": {
                    "day": "Tuesday",
                    "avoid": ["Bitter foods", "Non-veg"],
                    "eat": ["Sweet red foods", "Pomegranate"],
                    "description": "Fast during daytime, break with sweet foods"
                },
                "color": "Red, Maroon, Orange-Red",
                "direction": "South"
            },
            "Mercury": {
                "mantra": {
                    "text": "Om Braam Breem Braum Sah Budhaya Namah",
                    "count": 108,
                    "timing": "Wednesday morning",
                    "description": "Mercury mantra for intellect, communication, business"
                },
                "gemstone": {
                    "primary": "Emerald",
                    "alternative": "Green Tourmaline, Peridot",
                    "metal": "Gold",
                    "finger": "Little finger (right hand)",
                    "day": "Wednesday morning",
                    "description": "Enhances intelligence, speech, business acumen"
                },
                "charity": {
                    "items": ["Green vegetables", "Books", "Green cloth"],
                    "day": "Wednesday",
                    "description": "Donate to students, teachers, or educational institutions"
                },
                "fasting": {
                    "day": "Wednesday",
                    "avoid": ["Heavy meats"],
                    "eat": ["Green vegetables", "Moong dal"],
                    "description": "Light fasting with green foods"
                },
                "color": "Green, Emerald Green",
                "direction": "North"
            },
            "Jupiter": {
                "mantra": {
                    "text": "Om Graam Greem Graum Sah Gurave Namah",
                    "count": 108,
                    "timing": "Thursday morning",
                    "description": "Jupiter mantra for wisdom, wealth, and guru blessings"
                },
                "gemstone": {
                    "primary": "Yellow Sapphire",
                    "alternative": "Topaz, Citrine",
                    "metal": "Gold",
                    "finger": "Index finger (right hand)",
                    "day": "Thursday morning",
                    "description": "Brings wisdom, prosperity, spiritual growth, children"
                },
                "charity": {
                    "items": ["Yellow gram", "Turmeric", "Gold", "Yellow cloth"],
                    "day": "Thursday",
                    "description": "Donate to temples, priests, teachers, or spiritual causes"
                },
                "fasting": {
                    "day": "Thursday",
                    "avoid": ["Banana", "Gram"],
                    "eat": ["Yellow foods", "Turmeric milk"],
                    "description": "Fast during day, eat yellow sattvic foods"
                },
                "color": "Yellow, Gold, Saffron",
                "direction": "Northeast"
            },
            "Venus": {
                "mantra": {
                    "text": "Om Draam Dreem Draum Sah Shukraya Namah",
                    "count": 108,
                    "timing": "Friday morning",
                    "description": "Venus mantra for love, beauty, luxury, and relationships"
                },
                "gemstone": {
                    "primary": "Diamond",
                    "alternative": "White Sapphire, Zircon",
                    "metal": "Silver or Platinum",
                    "finger": "Middle finger or Little finger (right hand)",
                    "day": "Friday morning",
                    "description": "Enhances love, marriage, beauty, arts, luxury"
                },
                "charity": {
                    "items": ["White rice", "Sugar", "White cloth", "Perfume"],
                    "day": "Friday",
                    "description": "Donate to women, artists, or marriage-related causes"
                },
                "fasting": {
                    "day": "Friday",
                    "avoid": ["Curd", "Sour foods"],
                    "eat": ["White sweet foods", "Fragrant rice"],
                    "description": "Light fasting with sweet, pleasant foods"
                },
                "color": "White, Light Pink, Cream",
                "direction": "Southeast"
            },
            "Saturn": {
                "mantra": {
                    "text": "Om Praam Preem Praum Sah Shanaischaraya Namah",
                    "count": 108,
                    "timing": "Saturday evening",
                    "description": "Saturn mantra for discipline, longevity, and karmic balance"
                },
                "gemstone": {
                    "primary": "Blue Sapphire",
                    "alternative": "Amethyst, Lapis Lazuli",
                    "metal": "Iron or Silver",
                    "finger": "Middle finger (right hand)",
                    "day": "Saturday evening",
                    "description": "Reduces obstacles, brings discipline, favors hard work"
                },
                "charity": {
                    "items": ["Black gram", "Iron", "Black cloth", "Mustard oil"],
                    "day": "Saturday",
                    "description": "Donate to elderly, disabled, laborers, or Shani temples"
                },
                "fasting": {
                    "day": "Saturday",
                    "avoid": ["Oil", "Alcohol"],
                    "eat": ["Black gram", "Sesame seeds"],
                    "description": "Avoid oil, consume simple black-colored foods"
                },
                "color": "Black, Dark Blue, Navy",
                "direction": "West"
            }
        }

    def _initialize_house_remedies(self) -> Dict[int, Dict]:
        """Initialize house-specific remedies"""
        return {
            1: {
                "focus": "Self, health, personality",
                "remedy": "Morning meditation, Sun salutations"
            },
            2: {
                "focus": "Wealth, family, speech",
                "remedy": "Lakshmi puja, white flowers on Fridays"
            },
            3: {
                "focus": "Courage, siblings, communication",
                "remedy": "Mars mantra, red coral"
            },
            4: {
                "focus": "Mother, home, peace",
                "remedy": "Moon mantra, white items charity"
            },
            5: {
                "focus": "Children, creativity, intelligence",
                "remedy": "Jupiter mantra, yellow sapphire"
            },
            6: {
                "focus": "Enemies, debts, health issues",
                "remedy": "Durga mantra, service to sick/needy"
            },
            7: {
                "focus": "Marriage, partnerships",
                "remedy": "Venus mantra, Friday fasts"
            },
            8: {
                "focus": "Longevity, transformation, occult",
                "remedy": "Shiva mantra, Saturday fasts"
            },
            9: {
                "focus": "Fortune, spirituality, father",
                "remedy": "Guru mantra, yellow items on Thursdays"
            },
            10: {
                "focus": "Career, reputation, status",
                "remedy": "Sun mantra, Sunday Surya puja"
            },
            11: {
                "focus": "Gains, friends, aspirations",
                "remedy": "Jupiter/Saturn mantras, charity"
            },
            12: {
                "focus": "Losses, liberation, foreign",
                "remedy": "Moksha mantra, spiritual practices"
            }
        }

    def _initialize_yoga_remedies(self) -> Dict[str, Dict]:
        """Initialize yoga-specific remedies"""
        return {
            "Gaja Kesari Yoga": {
                "remedy": "Jupiter and Moon strengthening",
                "mantra": "Om Graam Greem Graum Sah Gurave Namah"
            },
            "Neecha Bhanga Raja Yoga": {
                "remedy": "Strengthen debilitated planet and cancellation factor",
                "action": "Wear gemstone of the canceling planet"
            }
        }


# Singleton instance
remedy_service = RemedyService()
