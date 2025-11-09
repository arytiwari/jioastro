"""
Muhurta AI Service

AI-powered Decision Copilot for electional astrology (Muhurta).
Provides personalized timing recommendations by combining:
- Traditional Muhurta calculations (Panchang, Hora)
- User's birth chart analysis (optional)
- Current dashas and transits
- GPT-4 powered comparison and recommendations
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from openai import OpenAI, AzureOpenAI
from app.core.config import settings


logger = logging.getLogger(__name__)


class MuhurtaAIService:
    """
    AI-powered Decision Copilot for choosing auspicious times.

    Provides comprehensive analysis of multiple time options including:
    - Overall rating (1-10) for each option
    - Detailed pros and cons
    - Personalization based on user's birth chart
    - Best time recommendation with reasoning
    - Comparison table for easy decision making
    """

    def __init__(self):
        """Initialize OpenAI client"""
        if settings.USE_AZURE_OPENAI:
            self.client = AzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.model = settings.AZURE_OPENAI_DEPLOYMENT
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL or "gpt-4"

    async def generate_decision_guidance(
        self,
        activity_type: str,
        muhurta_options: List[Dict[str, Any]],
        user_birth_chart: Optional[Dict[str, Any]] = None,
        user_current_dasha: Optional[Dict[str, Any]] = None,
        user_transits: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered decision guidance for choosing best time.

        Args:
            activity_type: Type of activity (marriage, business, travel, etc.)
            muhurta_options: List of candidate times with Panchang data
            user_birth_chart: Optional user's birth chart for personalization
            user_current_dasha: Optional current dasha period
            user_transits: Optional current planetary transits

        Returns:
            Dict containing:
            - comparison: List of analyzed options with ratings, pros, cons
            - best_time: Recommended time with reasoning
            - has_personalization: Whether birth chart was used
        """
        try:
            logger.info(f"Generating decision guidance for {activity_type} with {len(muhurta_options)} options")

            # Build comprehensive prompt
            prompt = self._build_decision_prompt(
                activity_type=activity_type,
                muhurta_options=muhurta_options,
                user_birth_chart=user_birth_chart,
                user_current_dasha=user_current_dasha,
                user_transits=user_transits
            )

            # Get AI response using OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a master Vedic astrologer helping clients choose the best auspicious time for important life events. Provide detailed, practical comparisons with specific reasoning."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content
            print(f"\n{'='*80}")
            print(f"MUHURTA AI RESPONSE (length: {len(ai_response) if ai_response else 0})")
            print(f"{'='*80}")
            print(ai_response if ai_response else 'None')  # Print full response
            print(f"{'='*80}\n")
            logger.info(f"AI response received, length: {len(ai_response) if ai_response else 0}")

            # Parse response into structured format
            parsed_result = self._parse_decision_response(ai_response, muhurta_options)

            logger.info(f"Decision guidance generated with {len(parsed_result.get('comparison', []))} options")
            best_time = parsed_result.get('best_time', {})
            print(f"\n*** FINAL RESULT ***")
            print(f"Best time option_number: {best_time.get('option_number', 'NONE')}")
            print(f"Best time specific_time: '{best_time.get('specific_time', 'NONE')}'")
            print(f"Best time rating: {best_time.get('rating', 'NONE')}")
            print(f"Best time datetime: {best_time.get('datetime', 'NONE')}")
            print(f"Best time reasoning length: {len(best_time.get('reasoning', ''))}")
            print(f"*** END FINAL RESULT ***\n")

            return parsed_result

        except Exception as e:
            logger.error(f"Error generating decision guidance: {str(e)}")
            # Return fallback guidance
            return self._create_fallback_guidance(muhurta_options, activity_type)

    def _build_decision_prompt(
        self,
        activity_type: str,
        muhurta_options: List[Dict[str, Any]],
        user_birth_chart: Optional[Dict[str, Any]],
        user_current_dasha: Optional[Dict[str, Any]],
        user_transits: Optional[Dict[str, Any]]
    ) -> str:
        """Build comprehensive prompt for decision guidance."""

        # Format muhurta options
        options_text = self._format_muhurta_options(muhurta_options)

        # Build base prompt
        prompt = f"""You are a master Vedic astrologer helping someone choose the best time for: **{activity_type.upper()}**

CANDIDATE TIMES TO COMPARE:
{options_text}

"""

        # Add personalization if available
        if user_birth_chart:
            chart_summary = self._format_birth_chart_summary(user_birth_chart)
            prompt += f"""USER'S BIRTH CHART:
{chart_summary}

"""

        if user_current_dasha:
            dasha_text = self._format_dasha_info(user_current_dasha)
            prompt += f"""CURRENT DASHA PERIOD:
{dasha_text}

"""

        if user_transits:
            transit_text = self._format_transit_info(user_transits)
            prompt += f"""CURRENT TRANSITS:
{transit_text}

"""

        # Add task instructions
        prompt += f"""YOUR TASK:

Analyze each time option and provide a comprehensive comparison to help the user make the best decision.

For EACH time option, provide:

1. **RATING**: Overall rating from 1-10 (10 being most auspicious)

2. **PROS**: List 3-5 positive factors including:
   - Favorable Panchang elements (Tithi, Nakshatra, Yoga, Karana, Vara)
   - Beneficial planetary hours (Hora)
   - Traditional Muhurta principles
   {"- Personal chart compatibility (how it aligns with user's chart)" if user_birth_chart else ""}
   {"- Favorable dasha/transit alignments" if user_current_dasha or user_transits else ""}

3. **CONS**: List 2-4 challenges or cautions including:
   - Inauspicious elements to be aware of
   - Potential obstacles
   - Things to avoid during this time
   {"- Personal chart conflicts (if any)" if user_birth_chart else ""}

4. **BEST_TIME_WITHIN_DAY**: Specify the optimal time period within this day's range.
   - Format: "Morning (6am-10am)", "Midday (10am-2pm)", "Afternoon (2pm-6pm)", or "Evening (6pm-10pm)"
   - Explain WHY this specific time period is best based on Hora and Panchang factors

5. **PERSONALIZATION NOTE**: {
    "How this time uniquely benefits the user based on their chart, current dasha period, and transits. Be specific about which planets or houses support this timing."
    if user_birth_chart or user_current_dasha or user_transits
    else "Based on universal Vedic principles - this time shows strong traditional auspiciousness through favorable Panchang combinations."
}

After analyzing all options, provide:

6. **BEST TIME RECOMMENDATION**:
   - Which option is the BEST choice
   - The SPECIFIC time period within that day (e.g., "Morning 8am-11am during Jupiter hora")
   - Clear reasoning (2-3 sentences) explaining WHY
   - Specific actionable advice for maximum benefit

RESPONSE FORMAT (STRICT - use this exact structure):

=== OPTION 1 ANALYSIS ===
RATING: [1-10]
BEST_TIME_WITHIN_DAY: [e.g., "Morning 8am-11am during Jupiter hora"]
PROS:
- [Pro 1]
- [Pro 2]
- [Pro 3]
CONS:
- [Con 1]
- [Con 2]
PERSONALIZATION: [Specific note about how this benefits the user - be detailed, not generic]

=== OPTION 2 ANALYSIS ===
[Same format]

... [Continue for all options]

=== BEST TIME RECOMMENDATION ===
RECOMMENDED OPTION: [Option number]
SPECIFIC_TIME: [Exact time period, e.g., "Morning 9am-12pm during Venus and Jupiter horas"]
REASONING: [2-3 sentences explaining why this is the best choice]
ACTIONABLE ADVICE: [Specific guidance for this activity]

Use traditional Vedic Muhurta principles. Be specific, practical, and compassionate in your guidance.
Consider both the universal auspiciousness (Panchang) and personal factors (if chart provided).
"""

        return prompt

    def _format_muhurta_options(self, options: List[Dict[str, Any]]) -> str:
        """Format muhurta options for prompt."""
        formatted = []

        for i, option in enumerate(options, 1):
            text = f"""
--- OPTION {i} ---
Date & Time: {option.get('datetime', 'N/A')}
Overall Score: {option.get('score', 0)}/100
Quality: {option.get('quality', 'Unknown')}

Panchang Elements:
- Tithi: {option.get('tithi', 'Unknown')} (Lunar Day)
- Nakshatra: {option.get('nakshatra', 'Unknown')} (Lunar Mansion)
- Vara: {option.get('vara', 'Unknown')} (Weekday)
- Yoga: {option.get('yoga', 'Unknown')}
- Karana: {option.get('karana', 'Unknown')}
- Hora Ruler: {option.get('hora_ruler', 'Unknown')} (Planetary Hour)

Favorable Factors:
{self._format_list(option.get('reasons', []))}

Precautions:
{self._format_list(option.get('precautions', []))}
"""
            formatted.append(text)

        return "\n".join(formatted)

    def _format_birth_chart_summary(self, chart: Dict[str, Any]) -> str:
        """Format birth chart summary for prompt."""
        # Extract key chart information
        ascendant = chart.get('ascendant', {})
        planets = chart.get('planets', [])

        summary = f"""Ascendant: {ascendant.get('sign', 'Unknown')} ({ascendant.get('degree', 0):.2f}°)

Key Planetary Positions:"""

        # Add major planets
        for planet in planets:
            if planet.get('name') in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
                summary += f"\n- {planet.get('name')}: {planet.get('sign', 'Unknown')} (House {planet.get('house', '?')})"

        return summary

    def _format_dasha_info(self, dasha: Dict[str, Any]) -> str:
        """Format current dasha information."""
        mahadasha = dasha.get('mahadasha', {})
        antardasha = dasha.get('antardasha', {})

        return f"""Mahadasha: {mahadasha.get('planet', 'Unknown')} ({mahadasha.get('start_date', 'N/A')} to {mahadasha.get('end_date', 'N/A')})
Antardasha: {antardasha.get('planet', 'Unknown')} ({antardasha.get('start_date', 'N/A')} to {antardasha.get('end_date', 'N/A')})"""

    def _format_transit_info(self, transits: Dict[str, Any]) -> str:
        """Format current transit information."""
        transit_list = []
        for planet, info in transits.items():
            if isinstance(info, dict):
                transit_list.append(f"- {planet}: {info.get('sign', 'Unknown')} (House {info.get('house', '?')})")

        return "\n".join(transit_list) if transit_list else "Transit information not available"

    def _format_list(self, items: List[str]) -> str:
        """Format list items with bullets."""
        if not items:
            return "- None specified"
        return "\n".join([f"- {item}" for item in items])

    def _parse_decision_response(
        self,
        ai_response: str,
        muhurta_options: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Parse AI response into structured format.

        Extracts:
        - Individual option analyses (rating, pros, cons, personalization)
        - Best time recommendation with reasoning
        """
        try:
            comparison = []
            best_time_info = {}

            # Split response into sections
            sections = ai_response.split('===')

            # Parse option analyses
            option_sections = [s for s in sections if 'OPTION' in s and 'ANALYSIS' in s]

            for i, section in enumerate(option_sections):
                if i >= len(muhurta_options):
                    break

                # The section variable only contains the header, we need the content from the next element
                section_content = ""
                # Find this section in the full sections array and get the next element
                for j, s in enumerate(sections):
                    if section in s and j + 1 < len(sections):
                        section_content = sections[j + 1]
                        break

                if not section_content:
                    section_content = section  # Fallback

                # Extract rating
                rating = self._extract_field(section_content, 'RATING:', numeric=True, default=5)

                # Extract best time within day
                best_time_within_day = self._extract_field(section_content, 'BEST_TIME_WITHIN_DAY:', default="Full day")

                # Extract pros
                pros = self._extract_list_field(section_content, 'PROS:', 'CONS:')

                # Extract cons
                cons = self._extract_list_field(section_content, 'CONS:', 'PERSONALIZATION:')

                # Extract personalization note
                personalization = self._extract_field(section_content, 'PERSONALIZATION:', default="Based on traditional Vedic principles, this time shows favorable Panchang elements.")

                if i == 0:  # Debug first option only
                    print(f"\n*** OPTION {i+1} PARSING ***")
                    print(f"Rating: {rating}")
                    print(f"Best time within day: {best_time_within_day}")
                    print(f"Pros count: {len(pros)}")
                    print(f"Cons count: {len(cons)}")
                    print(f"Personalization: {personalization[:100]}")
                    print(f"*** END OPTION PARSING ***\n")

                # Combine with original muhurta data
                option_analysis = {
                    **muhurta_options[i],
                    'ai_rating': rating,
                    'best_time_within_day': best_time_within_day.strip(),
                    'pros': pros[:5],  # Limit to 5
                    'cons': cons[:4],   # Limit to 4
                    'personalization_note': personalization.strip()
                }

                comparison.append(option_analysis)

            # Parse best time recommendation
            # Find the BEST TIME RECOMMENDATION section and get its content (next element after split)
            best_section_text = ""
            for i, s in enumerate(sections):
                if 'BEST TIME RECOMMENDATION' in s:
                    # The content is in the next element after the header
                    if i + 1 < len(sections):
                        best_section_text = sections[i + 1]
                    break

            if best_section_text:
                recommended_option = self._extract_field(
                    best_section_text,
                    'RECOMMENDED OPTION:',
                    numeric=True,
                    default=1
                )

                reasoning = self._extract_field(best_section_text, 'REASONING:', default="")
                actionable_advice = self._extract_field(best_section_text, 'ACTIONABLE ADVICE:', default="")
                specific_time = self._extract_field(best_section_text, 'SPECIFIC_TIME:', default="")

                print(f"\n*** BEST TIME PARSING ***")
                print(f"Recommended Option: {recommended_option}")
                print(f"Reasoning: {reasoning[:100] if reasoning else 'EMPTY'}")
                print(f"Actionable Advice: {actionable_advice[:100] if actionable_advice else 'EMPTY'}")
                print(f"Specific Time: '{specific_time}' (length: {len(specific_time)})")
                print(f"Best section preview: {best_section_text[:500]}")
                print(f"*** END PARSING ***\n")

                # Get the recommended option (1-indexed to 0-indexed)
                best_index = max(0, min(recommended_option - 1, len(comparison) - 1))

                # Start with fields from the selected option
                best_time_info = {}
                if comparison:
                    best_time_info.update(comparison[best_index])
                    # Rename ai_rating to rating for schema compliance
                    if 'ai_rating' in best_time_info:
                        best_time_info['rating'] = best_time_info.pop('ai_rating')

                # Override with specific best time fields (these take precedence)
                best_time_info['option_number'] = recommended_option
                best_time_info['specific_time'] = specific_time.strip()
                best_time_info['reasoning'] = reasoning.strip()
                best_time_info['actionable_advice'] = actionable_advice.strip()

                print(f"\n*** AFTER SETTING FIELDS ***")
                print(f"best_time_info keys: {list(best_time_info.keys())}")
                print(f"best_time_info['specific_time']: '{best_time_info.get('specific_time', 'KEY NOT FOUND')}'")
                print(f"*** END AFTER SETTING ***\n")

            return {
                'comparison': comparison,
                'best_time': best_time_info,
                'total_options': len(comparison),
                'has_personalization': any('chart' in opt.get('personalization_note', '').lower() for opt in comparison)
            }

        except Exception as e:
            logger.error(f"Error parsing decision response: {str(e)}")
            # Return structured fallback
            return self._create_fallback_guidance(muhurta_options, "general")

    def _extract_field(self, text: str, marker: str, numeric: bool = False, default: Any = "") -> Any:
        """Extract a field value from text."""
        try:
            if marker not in text:
                return default

            # Find start of field
            start = text.index(marker) + len(marker)

            # Find end (next line or next marker)
            end = text.find('\n', start)
            if end == -1:
                end = len(text)

            value = text[start:end].strip()

            if numeric:
                # Extract first number found
                import re
                numbers = re.findall(r'\d+', value)
                return int(numbers[0]) if numbers else default

            return value if value else default

        except Exception:
            return default

    def _extract_list_field(self, text: str, start_marker: str, end_marker: str) -> List[str]:
        """Extract a bulleted list from text."""
        try:
            if start_marker not in text:
                return []

            # Find section
            start = text.index(start_marker) + len(start_marker)
            end = text.index(end_marker) if end_marker in text[start:] else len(text)

            section = text[start:start + end]

            # Extract bullet points
            lines = section.split('\n')
            items = []

            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    item = line[1:].strip()
                    if item:
                        items.append(item)

            return items

        except Exception:
            return []

    def _create_fallback_guidance(
        self,
        muhurta_options: List[Dict[str, Any]],
        activity_type: str
    ) -> Dict[str, Any]:
        """
        Create fallback guidance if AI fails.

        Uses simple scoring to rank options and provide basic recommendations.
        """
        logger.info("Creating fallback guidance (AI unavailable)")

        comparison = []

        for i, option in enumerate(muhurta_options):
            # Simple rating based on score
            score = option.get('score', 50)
            ai_rating = min(10, max(1, int(score / 10)))

            # Generic pros and cons based on quality
            quality = option.get('quality', 'Moderate')

            pros = option.get('reasons', [])[:5] or [
                f"{quality} overall quality",
                f"Score: {score}/100"
            ]

            cons = option.get('precautions', [])[:4] or [
                "Standard precautions apply",
                "Consult astrologer for personalized guidance"
            ]

            comparison.append({
                **option,
                'ai_rating': ai_rating,
                'pros': pros,
                'cons': cons,
                'personalization_note': "No personalization available (using traditional Muhurta only)"
            })

        # Best is highest score
        best_option = max(comparison, key=lambda x: x.get('score', 0))

        return {
            'comparison': comparison,
            'best_time': {
                'option_number': comparison.index(best_option) + 1,
                'datetime': best_option.get('datetime'),
                'rating': best_option.get('ai_rating', 0),
                'reasoning': f"This time has the highest auspiciousness score ({best_option.get('score', 0)}/100) "
                             f"and {best_option.get('quality', 'good')} quality according to traditional Muhurta principles.",
                'actionable_advice': f"Proceed with {activity_type} during this time while following "
                                   f"traditional rituals and maintaining positive intentions.",
                **best_option
            },
            'total_options': len(comparison),
            'has_personalization': False
        }


# Create singleton instance
muhurta_ai_service = MuhurtaAIService()
