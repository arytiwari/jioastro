"""
Prashna AI Service - AI-powered answer generation for horary astrology
Uses GPT-4 to generate detailed, nuanced answers to Prashna questions
"""

from typing import Dict, List, Any, Optional
import logging
from openai import OpenAI, AzureOpenAI
import os
from app.core.config import settings

logger = logging.getLogger(__name__)


class PrashnaAIService:
    """AI-powered answer generation for Prashna (horary) astrology"""

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

    async def generate_detailed_answer(
        self,
        question: str,
        question_type: str,
        prashna_chart: Dict[str, Any],
        user_birth_chart: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI-powered answer for Prashna question

        Args:
            question: The question being asked
            question_type: Type of question (career, relationship, etc.)
            prashna_chart: Complete Prashna chart analysis
            user_birth_chart: Optional user's birth chart for personalization

        Returns:
            Dictionary with:
            - answer: Direct answer (Yes/No/Maybe/Uncertain)
            - explanation: Detailed reasoning (500-800 words)
            - timing: When it will manifest
            - obstacles: Challenges to overcome
            - opportunities: Favorable factors
            - remedies: Specific actions to take
            - confidence: 0-100 score with explanation
        """
        try:
            logger.info(f"Generating AI answer for question type: {question_type}")

            # Build comprehensive prompt
            prompt = self._build_prashna_prompt(
                question, question_type, prashna_chart, user_birth_chart
            )

            # Get AI response using OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a master Vedic astrologer specializing in Prashna (horary astrology). Provide detailed, compassionate, and practical answers based on traditional principles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content

            # Parse AI response into structured format
            parsed_answer = self._parse_ai_response(ai_response)

            # Validate remedies are all dictionaries
            if "remedies" in parsed_answer and isinstance(parsed_answer["remedies"], list):
                validated_remedies = []
                for remedy in parsed_answer["remedies"]:
                    if isinstance(remedy, dict) and "title" in remedy and "description" in remedy:
                        validated_remedies.append(remedy)
                    else:
                        logger.warning(f"Filtering out invalid remedy at final validation: {remedy}")
                parsed_answer["remedies"] = validated_remedies

            logger.info(f"AI answer generated successfully with {len(parsed_answer.get('remedies', []))} remedies")
            return parsed_answer

        except Exception as e:
            logger.error(f"Error generating AI answer: {e}", exc_info=True)
            # Return fallback answer
            return self._create_fallback_answer(prashna_chart, question_type)

    def _build_prashna_prompt(
        self,
        question: str,
        question_type: str,
        prashna_chart: Dict[str, Any],
        user_birth_chart: Optional[Dict]
    ) -> str:
        """Build comprehensive prompt for GPT-4"""

        # Extract chart details
        ascendant = prashna_chart.get("ascendant", {})
        moon = prashna_chart.get("moon", {})
        question_analysis = prashna_chart.get("question_analysis", {})
        planets = prashna_chart.get("planets", {})
        yogas = prashna_chart.get("yogas_present", [])

        # Build planet details
        planet_details = self._format_planet_details(planets)

        # Build yogas list
        yogas_text = "\n".join([f"- {yoga['name']}: {yoga.get('significance', yoga.get('description', 'N/A'))}" for yoga in yogas]) if yogas else "None"

        prompt = f"""You are a master Vedic astrologer analyzing a Prashna (horary) chart to answer a specific question.

QUESTION: "{question}"
QUESTION TYPE: {question_type}
QUERY TIME: {prashna_chart.get('query_datetime', 'Not specified')}

PRASHNA CHART DATA:

ASCENDANT (LAGNA) ANALYSIS:
- Sign: {ascendant.get('sign', 'N/A')} at {ascendant.get('degree', 0):.1f}°
- Lord: {ascendant.get('lord', 'N/A')} in {ascendant.get('lord_house', 'N/A')} house
- Lord Position: {ascendant.get('lord_position', 'N/A')}
- Strength: {ascendant.get('lord_strength', 'N/A')}
- Significance: {ascendant.get('significance', 'N/A')}

MOON ANALYSIS (Most Important in Prashna):
- Sign: {moon.get('sign', 'N/A')} at {moon.get('degree', 0):.1f}°
- House: {moon.get('house', 'N/A')}
- Nakshatra: {moon.get('nakshatra', 'N/A')} (Pada {moon.get('pada', 'N/A')})
- Phase: {moon.get('phase', 'N/A')} ({moon.get('illumination', 0):.0f}% illuminated)
- Strength: {moon.get('strength', 'N/A')}
- Assessment: {moon.get('assessment', 'N/A')}

QUESTION-SPECIFIC ANALYSIS:
- Relevant House: {question_analysis.get('relevant_house', 'N/A')}
- House Lord: {question_analysis.get('house_lord', 'N/A')}
- Lord Position: {question_analysis.get('lord_position', 'N/A')}
- Lord Strength: {question_analysis.get('lord_strength', 'N/A')}
- Karaka Planet: {question_analysis.get('karaka_planet', 'N/A')}
- Karaka Position: {question_analysis.get('karaka_position', 'N/A')}
- Karaka Strength: {question_analysis.get('karaka_strength', 'N/A')}
- Assessment: {question_analysis.get('assessment', 'N/A')}

PLANETARY POSITIONS:
{planet_details}

YOGAS PRESENT:
{yogas_text}

OVERALL CHART STRENGTH:
{prashna_chart.get('overall_chart_strength', 'N/A')}

TRADITIONAL ANSWER:
{prashna_chart.get('answer', {}).get('detailed_interpretation', prashna_chart.get('answer', {}).get('summary', 'N/A'))}

---

TASK: Provide a comprehensive astrological answer following this EXACT structure:

1. **DIRECT_ANSWER**: [Must be exactly one of: "Yes" / "No" / "Maybe" / "Uncertain"]

2. **EXPLANATION** (500-800 words):
   Start with a brief summary, then analyze in detail:
   - Ascendant and its lord (represents the querent)
   - Moon position and strength (most crucial in Prashna)
   - Relevant house and its lord for this question type
   - Karaka (significator) planet for this question
   - Supporting or afflicting yogas
   - Synthesis of all factors

3. **TIMING**:
   TIMEFRAME: [Specific prediction like "2-3 months", "6-12 months", "After 2026", etc.]
   BASIS: [Astrological reasoning for the timing]
   KEY_DATES: [Specific periods or transits to watch]

4. **OBSTACLES** (List 3-5 challenges):
   - [Obstacle 1 based on chart]
   - [Obstacle 2]
   - [Obstacle 3]
   ...

5. **OPPORTUNITIES** (List 3-5 favorable factors):
   - [Opportunity 1 based on chart]
   - [Opportunity 2]
   - [Opportunity 3]
   ...

6. **REMEDIES** (3-5 specific Vedic remedies):
   REMEDY_1_TITLE: [Brief title]
   REMEDY_1_DESC: [Specific instructions]

   REMEDY_2_TITLE: [Brief title]
   REMEDY_2_DESC: [Specific instructions]

   [Continue for 3-5 remedies]

7. **CONFIDENCE**: [Number between 0-100]%
   CONFIDENCE_EXPLANATION: [2-3 sentences explaining the confidence level]

IMPORTANT GUIDELINES:
- Use traditional Vedic Prashna principles (Moon is most important)
- Be specific and practical, not vague
- Consider ALL chart factors, not just one or two
- Be compassionate but honest
- If chart shows delays, explain why and when things may improve
- Timing should be based on dasha periods, transits, or traditional Prashna timing rules
- Remedies should be authentic Vedic practices (mantras, charity, fasting, etc.)
- Format your response EXACTLY as specified above for proper parsing

Begin your analysis:
"""

        return prompt

    def _format_planet_details(self, planets: List[Dict]) -> str:
        """Format planetary positions for prompt"""
        if not planets:
            return "Not available"

        details = []
        for planet in planets:
            details.append(
                f"- {planet.get('name', 'Unknown')}: {planet.get('sign', 'N/A')} "
                f"{planet.get('degree', 0):.1f}° in {planet.get('house', 'N/A')} house "
                f"(Nakshatra: {planet.get('nakshatra', 'N/A')}, "
                f"Strength: {planet.get('strength', 'N/A')})"
            )
        return "\n".join(details)

    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """
        Parse AI response into structured format

        Expected format from AI:
        1. **DIRECT_ANSWER**: Yes/No/Maybe/Uncertain
        2. **EXPLANATION** (500-800 words): ...
        3. **TIMING**: ...
        ...
        """
        try:
            # Initialize result
            result = {
                "answer": "Uncertain",
                "explanation": "",
                "timing": {
                    "timeframe": "Uncertain",
                    "basis": "Analysis incomplete",
                    "key_dates": "To be determined"
                },
                "obstacles": [],
                "opportunities": [],
                "remedies": [],
                "confidence": 50,
                "confidence_explanation": "Standard confidence level"
            }

            # Split response into sections
            sections = ai_response.split("**")

            # Parse each section
            current_section = None
            for i, section in enumerate(sections):
                section = section.strip()
                if not section:
                    continue

                # Identify section headers
                if "DIRECT_ANSWER" in section:
                    current_section = "answer"
                    # Next section should have the answer
                    if i + 1 < len(sections):
                        answer_text = sections[i + 1].strip().split("\n")[0].strip(" :")
                        if answer_text in ["Yes", "No", "Maybe", "Uncertain"]:
                            result["answer"] = answer_text

                elif "EXPLANATION" in section:
                    current_section = "explanation"
                    # Collect explanation from subsequent sections until next header
                    explanation_parts = []
                    for j in range(i + 1, len(sections)):
                        if any(header in sections[j] for header in ["TIMING", "OBSTACLES", "OPPORTUNITIES", "REMEDIES", "CONFIDENCE"]):
                            break
                        explanation_parts.append(sections[j].strip())
                    result["explanation"] = "\n\n".join(explanation_parts).strip()

                elif "TIMING" in section:
                    current_section = "timing"
                    # Parse timing details
                    timing_text = ""
                    for j in range(i + 1, len(sections)):
                        if any(header in sections[j] for header in ["OBSTACLES", "OPPORTUNITIES", "REMEDIES", "CONFIDENCE"]):
                            break
                        timing_text += sections[j].strip() + " "

                    # Extract timing components
                    lines = timing_text.split("\n")
                    for line in lines:
                        if "TIMEFRAME:" in line:
                            result["timing"]["timeframe"] = line.split("TIMEFRAME:")[1].strip()
                        elif "BASIS:" in line:
                            result["timing"]["basis"] = line.split("BASIS:")[1].strip()
                        elif "KEY_DATES:" in line:
                            result["timing"]["key_dates"] = line.split("KEY_DATES:")[1].strip()

                elif "OBSTACLES" in section:
                    current_section = "obstacles"
                    # Parse obstacles list
                    obstacles_text = ""
                    for j in range(i + 1, len(sections)):
                        if any(header in sections[j] for header in ["OPPORTUNITIES", "REMEDIES", "CONFIDENCE"]):
                            break
                        obstacles_text += sections[j].strip() + "\n"

                    # Extract list items
                    lines = [l.strip("- ").strip() for l in obstacles_text.split("\n") if l.strip().startswith("-")]
                    result["obstacles"] = lines

                elif "OPPORTUNITIES" in section:
                    current_section = "opportunities"
                    # Parse opportunities list
                    opps_text = ""
                    for j in range(i + 1, len(sections)):
                        if any(header in sections[j] for header in ["REMEDIES", "CONFIDENCE"]):
                            break
                        opps_text += sections[j].strip() + "\n"

                    # Extract list items
                    lines = [l.strip("- ").strip() for l in opps_text.split("\n") if l.strip().startswith("-")]
                    result["opportunities"] = lines

                elif "REMEDIES" in section:
                    current_section = "remedies"
                    # Parse remedies
                    remedies_text = ""
                    for j in range(i + 1, len(sections)):
                        if "CONFIDENCE" in sections[j]:
                            break
                        remedies_text += sections[j].strip() + "\n"

                    # Extract remedy pairs (title and description)
                    remedies = []
                    lines = remedies_text.split("\n")
                    current_remedy = {}
                    for line in lines:
                        if "REMEDY_" in line and "_TITLE:" in line:
                            if current_remedy and "title" in current_remedy and "description" in current_remedy:
                                remedies.append(current_remedy)
                            current_remedy = {"title": line.split(":", 1)[1].strip(), "description": ""}
                        elif "REMEDY_" in line and "_DESC:" in line:
                            if current_remedy:
                                current_remedy["description"] = line.split(":", 1)[1].strip()

                    # Add last remedy if valid
                    if current_remedy and "title" in current_remedy and "description" in current_remedy:
                        remedies.append(current_remedy)

                    # Ensure all remedies are dictionaries with both fields
                    validated_remedies = []
                    for remedy in remedies:
                        if isinstance(remedy, dict) and "title" in remedy and "description" in remedy:
                            validated_remedies.append(remedy)
                        else:
                            logger.warning(f"Skipping invalid remedy: {remedy}")

                    result["remedies"] = validated_remedies

                elif "CONFIDENCE" in section:
                    current_section = "confidence"
                    # Parse confidence score and explanation
                    confidence_text = ""
                    for j in range(i + 1, len(sections)):
                        confidence_text += sections[j].strip() + " "

                    # Extract confidence percentage
                    import re
                    confidence_match = re.search(r'(\d+)%', confidence_text)
                    if confidence_match:
                        result["confidence"] = int(confidence_match.group(1))

                    # Extract explanation
                    if "CONFIDENCE_EXPLANATION:" in confidence_text:
                        result["confidence_explanation"] = confidence_text.split("CONFIDENCE_EXPLANATION:")[1].strip()

            return result

        except Exception as e:
            logger.error(f"Error parsing AI response: {e}", exc_info=True)
            logger.error(f"AI response preview: {ai_response[:500] if ai_response else 'None'}")
            # Return basic structure with AI response as explanation
            return {
                "answer": "Uncertain",
                "explanation": ai_response[:1000] if len(ai_response) > 1000 else ai_response,
                "timing": {
                    "timeframe": "Analysis in progress",
                    "basis": "Please review full explanation",
                    "key_dates": "To be determined"
                },
                "obstacles": ["Detailed analysis in explanation section"],
                "opportunities": ["Please review full explanation"],
                "remedies": [
                    {"title": "General Remedy", "description": "See full analysis for specific guidance"}
                ],
                "confidence": 50,
                "confidence_explanation": "Confidence level varies based on chart clarity"
            }

    def _create_fallback_answer(
        self,
        prashna_chart: Dict[str, Any],
        question_type: str
    ) -> Dict[str, Any]:
        """Create fallback answer if AI generation fails"""
        traditional_answer = prashna_chart.get("answer", {})

        return {
            "answer": traditional_answer.get("answer", "Uncertain"),
            "explanation": traditional_answer.get("interpretation", "Please consult a qualified astrologer for detailed analysis of this question."),
            "timing": {
                "timeframe": traditional_answer.get("timing", {}).get("timeframe", "Uncertain"),
                "basis": "Traditional Prashna rules",
                "key_dates": traditional_answer.get("timing", {}).get("details", "To be determined")
            },
            "obstacles": traditional_answer.get("challenges", ["Chart analysis needed"]),
            "opportunities": traditional_answer.get("favorable_factors", ["Further analysis required"]),
            "remedies": [
                {"title": "General Mantra", "description": "Chant 'Om Namah Shivaya' 108 times daily"},
                {"title": "Charity", "description": "Donate to those in need on the day ruled by the relevant planet"},
                {"title": "Meditation", "description": "Practice daily meditation for mental clarity"}
            ],
            "confidence": traditional_answer.get("confidence", 50),
            "confidence_explanation": "Based on traditional chart analysis only. AI-powered analysis temporarily unavailable."
        }


# Global instance
prashna_ai_service = PrashnaAIService()
