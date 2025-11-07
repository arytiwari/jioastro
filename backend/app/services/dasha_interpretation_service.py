"""
Dasha Interpretation Service
Provides interpretations for Vimshottari Dasha periods based on classical Vedic astrology
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from openai import OpenAI


class DashaInterpretationService:
    """Generate interpretations for Mahadasha, Antardasha, and Pratyantardasha periods"""

    def __init__(self):
        """Initialize with OpenAI client for AI personalization"""
        api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=api_key) if api_key else None

    # Planetary relationship types for combination effects
    PLANETARY_RELATIONSHIPS = {
        "friends": {
            "Sun": ["Moon", "Mars", "Jupiter"],
            "Moon": ["Sun", "Mercury"],
            "Mars": ["Sun", "Moon", "Jupiter"],
            "Mercury": ["Sun", "Venus"],
            "Jupiter": ["Sun", "Moon", "Mars"],
            "Venus": ["Mercury", "Saturn"],
            "Saturn": ["Mercury", "Venus"],
            "Rahu": ["Mercury", "Venus", "Saturn"],
            "Ketu": ["Mars", "Jupiter"]
        },
        "enemies": {
            "Sun": ["Venus", "Saturn"],
            "Moon": ["None"],
            "Mars": ["Mercury"],
            "Mercury": ["Moon"],
            "Jupiter": ["Mercury", "Venus"],
            "Venus": ["Sun", "Moon"],
            "Saturn": ["Sun", "Moon", "Mars"],
            "Rahu": ["Sun", "Moon", "Mars"],
            "Ketu": ["Sun", "Moon"]
        }
    }

    # Mahadasha planet interpretations
    MAHADASHA_INTERPRETATIONS = {
        "Sun": {
            "general": "Period of authority, leadership, and self-expression. Focus on career advancement and recognition.",
            "positive": [
                "Increased confidence and vitality",
                "Recognition from authorities and government",
                "Career growth and professional success",
                "Enhanced leadership abilities",
                "Favorable for father's well-being"
            ],
            "challenges": [
                "Ego conflicts and authority issues",
                "Strained relationships with superiors",
                "Health issues related to bones and eyesight",
                "Potential for arrogance"
            ],
            "remedies": [
                "Offer water to Sun at sunrise",
                "Wear ruby gemstone (consult astrologer)",
                "Chant Surya mantra or Gayatri mantra",
                "Practice humility and service"
            ]
        },
        "Moon": {
            "general": "Period of emotional growth, nurturing, and mental peace. Focus on home, family, and inner well-being.",
            "positive": [
                "Enhanced emotional intelligence",
                "Strong connection with mother and family",
                "Intuitive and creative abilities flourish",
                "Favorable for travel and changes",
                "Gains through public dealings"
            ],
            "challenges": [
                "Emotional instability and mood swings",
                "Mental stress and anxiety",
                "Health issues related to chest and stomach",
                "Dependency on others"
            ],
            "remedies": [
                "Wear pearl gemstone (consult astrologer)",
                "Chant Chandra mantra",
                "Offer milk to Shiva on Mondays",
                "Practice meditation for mental peace"
            ]
        },
        "Mars": {
            "general": "Period of courage, action, and determination. Focus on overcoming obstacles and achieving goals.",
            "positive": [
                "Increased energy and courage",
                "Success through hard work and determination",
                "Gains through property and land",
                "Enhanced physical strength",
                "Victory over enemies and competitors"
            ],
            "challenges": [
                "Impulsiveness and aggression",
                "Accidents and injuries",
                "Legal disputes and conflicts",
                "Health issues related to blood and muscles",
                "Strained sibling relationships"
            ],
            "remedies": [
                "Wear red coral gemstone (consult astrologer)",
                "Chant Mangal mantra",
                "Donate on Tuesdays (red items, lentils)",
                "Practice anger management and patience"
            ]
        },
        "Mercury": {
            "general": "Period of intellect, communication, and business. Focus on education, commerce, and networking.",
            "positive": [
                "Enhanced intellectual abilities",
                "Success in education and learning",
                "Business and commercial gains",
                "Improved communication skills",
                "Favorable for writing and speech"
            ],
            "challenges": [
                "Nervous tension and overthinking",
                "Scattered energy and lack of focus",
                "Speech-related problems",
                "Health issues related to nerves and skin"
            ],
            "remedies": [
                "Wear emerald gemstone (consult astrologer)",
                "Chant Budha mantra",
                "Donate on Wednesdays (green items, books)",
                "Practice mindfulness and focus exercises"
            ]
        },
        "Jupiter": {
            "general": "Period of wisdom, growth, and prosperity. Focus on spirituality, education, and family expansion.",
            "positive": [
                "Spiritual growth and wisdom",
                "Success in education and teaching",
                "Financial prosperity and wealth",
                "Marriage and child birth",
                "Guidance from mentors and teachers"
            ],
            "challenges": [
                "Overconfidence and over-optimism",
                "Weight gain and health issues",
                "Financial over-expansion",
                "Religious conflicts"
            ],
            "remedies": [
                "Wear yellow sapphire gemstone (consult astrologer)",
                "Chant Guru mantra",
                "Donate on Thursdays (yellow items, turmeric)",
                "Study scriptures and practice dharma"
            ]
        },
        "Venus": {
            "general": "Period of love, luxury, and artistic expression. Focus on relationships, beauty, and pleasures.",
            "positive": [
                "Enhanced creativity and artistic talents",
                "Success in relationships and marriage",
                "Material comforts and luxuries",
                "Gains through women and partnerships",
                "Favorable for arts and entertainment"
            ],
            "challenges": [
                "Over-indulgence in pleasures",
                "Relationship complications",
                "Health issues related to reproductive system",
                "Financial extravagance"
            ],
            "remedies": [
                "Wear diamond or white sapphire (consult astrologer)",
                "Chant Shukra mantra",
                "Donate on Fridays (white items, rice)",
                "Practice moderation and balance"
            ]
        },
        "Saturn": {
            "general": "Period of discipline, karma, and hard work. Focus on patience, perseverance, and long-term goals.",
            "positive": [
                "Spiritual maturity and wisdom",
                "Success through discipline and hard work",
                "Long-lasting achievements",
                "Gains through service and labor",
                "Development of patience and endurance"
            ],
            "challenges": [
                "Delays and obstacles",
                "Health issues, especially joints and chronic ailments",
                "Depression and pessimism",
                "Separation and losses",
                "Karmic lessons and hardships"
            ],
            "remedies": [
                "Wear blue sapphire (only after careful consultation)",
                "Chant Shani mantra",
                "Donate on Saturdays (black items, oil, iron)",
                "Serve the elderly and disabled"
            ]
        },
        "Rahu": {
            "general": "Period of ambition, innovation, and unconventional paths. Focus on breaking boundaries and exploring new territories.",
            "positive": [
                "Sudden gains and unexpected opportunities",
                "Success through foreign connections",
                "Innovation and technological advancement",
                "Political and social influence",
                "Breaking free from limitations"
            ],
            "challenges": [
                "Confusion and illusions",
                "Addictions and obsessions",
                "Scandals and controversies",
                "Health issues related to allergies and poisoning",
                "Karmic complications"
            ],
            "remedies": [
                "Wear hessonite garnet (consult astrologer)",
                "Chant Rahu mantra",
                "Donate on Saturdays (blue/black items)",
                "Practice grounding and mindfulness"
            ]
        },
        "Ketu": {
            "general": "Period of spirituality, detachment, and inner transformation. Focus on letting go and spiritual growth.",
            "positive": [
                "Spiritual awakening and enlightenment",
                "Psychic and intuitive abilities",
                "Freedom from material attachments",
                "Research and occult knowledge",
                "Karmic resolution"
            ],
            "challenges": [
                "Confusion and directionless",
                "Isolation and loneliness",
                "Health issues, especially mysterious ailments",
                "Loss of material possessions",
                "Mental instability"
            ],
            "remedies": [
                "Wear cat's eye gemstone (consult astrologer)",
                "Chant Ketu mantra",
                "Donate on Thursdays (multi-colored items)",
                "Practice meditation and yoga"
            ]
        }
    }

    # Current life phase interpretations based on dasha
    LIFE_PHASE_KEYWORDS = {
        "Sun": ["leadership", "authority", "recognition", "career advancement", "government"],
        "Moon": ["emotions", "family", "nurturing", "travel", "public relations"],
        "Mars": ["action", "courage", "property", "competition", "physical activity"],
        "Mercury": ["intellect", "business", "communication", "education", "networking"],
        "Jupiter": ["wisdom", "prosperity", "expansion", "spirituality", "teaching"],
        "Venus": ["love", "luxury", "creativity", "relationships", "arts"],
        "Saturn": ["discipline", "karma", "hard work", "patience", "service"],
        "Rahu": ["ambition", "innovation", "foreign connections", "unconventional", "technology"],
        "Ketu": ["spirituality", "detachment", "research", "occult", "transformation"]
    }

    def get_mahadasha_interpretation(self, planet: str) -> Dict[str, Any]:
        """Get detailed interpretation for a Mahadasha period"""
        return self.MAHADASHA_INTERPRETATIONS.get(planet, {
            "general": f"{planet} Mahadasha period. Consult with an experienced astrologer for detailed analysis.",
            "positive": ["Favorable planetary influences based on chart placement"],
            "challenges": ["Challenges based on planetary position and aspects"],
            "remedies": [f"Consult astrologer for {planet}-specific remedies"]
        })

    def get_current_dasha_summary(self, current_mahadasha: Dict[str, Any]) -> str:
        """Generate a summary of current Mahadasha influence"""
        planet = current_mahadasha.get("planet", "Unknown")
        keywords = self.LIFE_PHASE_KEYWORDS.get(planet, ["general life experiences"])

        summary = f"Currently in {planet} Mahadasha, a period emphasizing "
        summary += ", ".join(keywords[:3]) + ". "

        interpretation = self.get_mahadasha_interpretation(planet)
        summary += interpretation.get("general", "")

        return summary

    def get_planetary_relationship(self, planet1: str, planet2: str) -> str:
        """Determine relationship between two planets"""
        if planet2 in self.PLANETARY_RELATIONSHIPS["friends"].get(planet1, []):
            return "friendly"
        elif planet2 in self.PLANETARY_RELATIONSHIPS["enemies"].get(planet1, []):
            return "inimical"
        else:
            return "neutral"

    def get_antardasha_interpretation(self, maha_lord: str, antar_lord: str) -> Dict[str, Any]:
        """
        Get interpretation for Antardasha based on planetary combination

        Args:
            maha_lord: Main period lord
            antar_lord: Sub-period lord

        Returns:
            Interpretation of the combined effect
        """
        relationship = self.get_planetary_relationship(maha_lord, antar_lord)

        # Get individual planet themes
        maha_themes = self.LIFE_PHASE_KEYWORDS.get(maha_lord, [])
        antar_themes = self.LIFE_PHASE_KEYWORDS.get(antar_lord, [])

        # Base interpretation
        if maha_lord == antar_lord:
            # Same planet - intensified effects
            summary = f"Intensified {maha_lord} period. The qualities of {maha_lord} are at their peak."
            effect = "very_favorable"
            advice = f"This is the most powerful sub-period within {maha_lord} Mahadasha. Make the most of {maha_lord}'s energies."
        elif relationship == "friendly":
            summary = f"{antar_lord} supports {maha_lord}'s goals. Harmonious period bringing combined benefits."
            effect = "favorable"
            advice = f"Leverage the synergy between {maha_lord} and {antar_lord}. Good time for initiatives related to both planets."
        elif relationship == "inimical":
            summary = f"{antar_lord} creates friction with {maha_lord} objectives. Mixed results possible."
            effect = "challenging"
            advice = f"Balance the conflicting energies of {maha_lord} and {antar_lord}. Practice patience and flexibility."
        else:
            summary = f"{antar_lord} brings neutral influence to {maha_lord} period. Moderate effects."
            effect = "neutral"
            advice = f"Standard period with {antar_lord} coloring the {maha_lord} experience. Stay balanced."

        # Combined themes
        combined_themes = list(set(maha_themes[:2] + antar_themes[:2]))

        return {
            "summary": summary,
            "effect": effect,
            "relationship": relationship,
            "advice": advice,
            "focus_areas": combined_themes,
            "maha_influence": f"{maha_lord} sets the overall tone",
            "antar_influence": f"{antar_lord} colors the experience"
        }

    def enhance_antardashas_with_interpretations(self, antardashas: List[Dict], maha_lord: str) -> List[Dict]:
        """
        Add interpretations to all Antardashas within a Mahadasha

        Args:
            antardashas: List of Antardasha periods
            maha_lord: The Mahadasha lord

        Returns:
            Enhanced Antardashas with interpretations
        """
        for antar in antardashas:
            antar_lord = antar.get("planet")
            if antar_lord:
                antar["interpretation"] = self.get_antardasha_interpretation(maha_lord, antar_lord)

        return antardashas

    def personalize_dasha_with_ai(
        self,
        dasha_data: Dict[str, Any],
        chart_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use AI to personalize Dasha interpretations based on actual chart placements

        Args:
            dasha_data: Enhanced dasha data
            chart_data: Complete birth chart data for context

        Returns:
            Dasha data with AI-personalized interpretations
        """
        if not self.openai_client or not chart_data:
            return dasha_data

        try:
            current_maha = dasha_data.get("current_mahadasha", {})
            current_planet = current_maha.get("planet")

            if not current_planet:
                return dasha_data

            # Get planet's position in the chart
            planets = chart_data.get("planets", {})
            planet_info = planets.get(current_planet, {})

            # Create context for AI
            context = f"""
You are an expert Vedic astrologer. Provide a personalized interpretation for the current {current_planet} Mahadasha.

Chart Context:
- {current_planet} is in {planet_info.get('sign', 'Unknown')} sign
- {current_planet} is in house {planet_info.get('house', 'Unknown')}
- {current_planet} is {'retrograde' if planet_info.get('retrograde') else 'direct'}
- Nakshatra: {planet_info.get('nakshatra', {}).get('name', 'Unknown')}

Current Mahadasha:
- Planet: {current_planet}
- Duration: {current_maha.get('start_date')} to {current_maha.get('end_date')}

Based on this specific chart placement, provide:
1. A personalized summary (2-3 sentences) that considers the sign, house, and nakshatra
2. Three specific areas of focus based on the house placement
3. One key opportunity unique to this placement

Format your response as JSON with keys: personalized_summary, focus_areas (array), key_opportunity
"""

            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert Vedic astrologer providing personalized chart interpretations."},
                    {"role": "user", "content": context}
                ],
                max_tokens=500,
                temperature=0.7
            )

            # Parse AI response
            import json
            ai_content = response.choices[0].message.content
            ai_interpretation = json.loads(ai_content)

            # Add AI personalization to current mahadasha
            current_maha["ai_personalized"] = True
            current_maha["personalized_summary"] = ai_interpretation.get("personalized_summary")
            current_maha["personalized_focus_areas"] = ai_interpretation.get("focus_areas", [])
            current_maha["key_opportunity"] = ai_interpretation.get("key_opportunity")

            dasha_data["current_mahadasha"] = current_maha
            dasha_data["ai_enhanced"] = True

        except Exception as e:
            print(f"AI personalization failed: {e}")
            # Continue with standard interpretations if AI fails

        return dasha_data

    def enhance_dasha_with_interpretations(
        self,
        dasha_data: Dict[str, Any],
        chart_data: Optional[Dict[str, Any]] = None,
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Enhance Dasha data with interpretations and guidance

        Args:
            dasha_data: Raw dasha data from calculation service
            chart_data: Complete birth chart data for AI personalization
            use_ai: Whether to use AI for personalization

        Returns:
            Enhanced dasha data with interpretations
        """
        if not dasha_data or "mahadashas" not in dasha_data:
            return dasha_data

        # Get current mahadasha
        current_maha = dasha_data.get("current_mahadasha", {})
        current_planet = current_maha.get("planet")

        # Add interpretations to current mahadasha
        if current_planet:
            current_maha["interpretation"] = self.get_mahadasha_interpretation(current_planet)
            current_maha["summary"] = self.get_current_dasha_summary(current_maha)
            current_maha["life_themes"] = self.LIFE_PHASE_KEYWORDS.get(current_planet, [])

        # Add brief interpretations to all mahadashas
        for maha in dasha_data.get("mahadashas", []):
            planet = maha.get("planet")
            if planet:
                interpretation = self.get_mahadasha_interpretation(planet)
                maha["brief_interpretation"] = interpretation.get("general", "")
                maha["key_themes"] = self.LIFE_PHASE_KEYWORDS.get(planet, [])[:3]

        # Enhance Antardashas with interpretations
        antardashas = dasha_data.get("antardashas", [])
        if antardashas and current_planet:
            dasha_data["antardashas"] = self.enhance_antardashas_with_interpretations(
                antardashas, current_planet
            )

        # Enhance current Antardasha
        current_antar = dasha_data.get("current_antardasha")
        if current_antar and current_planet:
            antar_lord = current_antar.get("planet")
            if antar_lord:
                current_antar["interpretation"] = self.get_antardasha_interpretation(
                    current_planet, antar_lord
                )
                current_antar["summary"] = current_antar["interpretation"]["summary"]
                dasha_data["current_antardasha"] = current_antar

        # Update the dasha data
        dasha_data["current_mahadasha"] = current_maha
        dasha_data["interpretations_included"] = True

        # Add AI personalization if enabled and chart data available
        if use_ai and chart_data:
            dasha_data = self.personalize_dasha_with_ai(dasha_data, chart_data)

        return dasha_data


# Singleton instance
dasha_interpretation_service = DashaInterpretationService()
