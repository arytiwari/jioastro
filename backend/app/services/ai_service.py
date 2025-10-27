"""
AI Interpretation Service
Generates personalized Vedic astrology interpretations using OpenAI GPT-4
"""

from typing import Dict, Any
from openai import OpenAI, AzureOpenAI
import os

from app.core.config import settings


class AIInterpretationService:
    """Service for generating AI-powered astrological interpretations"""

    def __init__(self):
        """Initialize OpenAI or Azure OpenAI client"""
        if settings.USE_AZURE_OPENAI:
            # Use Azure OpenAI
            self.client = AzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.model = settings.AZURE_OPENAI_DEPLOYMENT  # Azure uses deployment name
            print(f"✅ Using Azure OpenAI (deployment: {self.model})")
        else:
            # Use standard OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4-turbo-preview"
            print("✅ Using OpenAI")

    def generate_interpretation(
        self,
        chart_data: Dict[str, Any],
        question: str,
        category: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate AI interpretation based on birth chart and user question

        Args:
            chart_data: Complete birth chart data (from astrology service)
            question: User's specific question
            category: Query category (career, relationship, health, etc.)

        Returns:
            Dictionary containing interpretation and metadata
        """

        # Prepare context from chart data
        context = self._prepare_chart_context(chart_data)

        # Create system prompt
        system_prompt = self._create_system_prompt()

        # Create user message
        user_message = f"""
{context}

Query Category: {category.upper()}

User's Question: {question}

Please provide a personalized Vedic astrology interpretation that:
1. Directly answers their question using chart insights
2. References specific planetary positions, houses, and yogas
3. Offers practical, actionable guidance
4. Includes traditional Vedic wisdom
5. Is warm, empowering, and hopeful (never fatalistic)
6. Is approximately 250-300 words
7. Ends with one simple remedy (mantra, gemstone, charity, or practice)
"""

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=800
            )

            interpretation = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            return {
                "interpretation": interpretation,
                "model": self.model,
                "tokens_used": tokens_used,
                "success": True
            }

        except Exception as e:
            # Fallback response if API fails
            return {
                "interpretation": self._generate_fallback_response(question),
                "model": "fallback",
                "tokens_used": 0,
                "success": False,
                "error": str(e)
            }

    def _prepare_chart_context(self, chart_data: Dict[str, Any]) -> str:
        """Prepare chart context for AI prompt"""

        context_parts = []

        # Basic info
        if "basic_info" in chart_data:
            basic = chart_data["basic_info"]
            context_parts.append(f"Birth Details: {basic.get('birth_datetime', 'N/A')}")
            if "location" in basic:
                context_parts.append(f"Location: {basic['location'].get('city', 'Unknown')}")

        # Ascendant
        if "ascendant" in chart_data:
            asc = chart_data["ascendant"]
            context_parts.append(
                f"\nAscendant (Lagna): {asc.get('sign')} at {asc.get('position', 0):.2f}°"
            )

        # Planets
        if "planets" in chart_data:
            context_parts.append("\nPlanetary Positions:")
            for planet, data in chart_data["planets"].items():
                retrograde = " (R)" if data.get("retrograde") else ""
                context_parts.append(
                    f"  - {planet}: {data.get('sign')} in {data.get('house')}th house "
                    f"at {data.get('position', 0):.2f}°{retrograde}"
                )

        # Current Dasha
        if "dasha" in chart_data:
            dasha = chart_data["dasha"]
            context_parts.append(
                f"\nCurrent Dasha: {dasha.get('current_dasha')} "
                f"(period: {dasha.get('period_years')} years)"
            )

        # Yogas
        if "yogas" in chart_data and chart_data["yogas"]:
            context_parts.append("\nDetected Yogas (Astrological Combinations):")
            for yoga in chart_data["yogas"]:
                context_parts.append(
                    f"  - {yoga.get('name')}: {yoga.get('description')} "
                    f"[Strength: {yoga.get('strength', 'Medium')}]"
                )

        return "\n".join(context_parts)

    def _create_system_prompt(self) -> str:
        """Create system prompt for AI"""

        return """You are an expert Vedic astrologer with 20+ years of experience in Jyotish (Vedic astrology). You combine deep traditional knowledge with compassionate, practical guidance.

Your interpretation style:
- Warm, personalized, and empowering
- Grounded in classical Vedic astrology principles
- Practical and actionable
- Hopeful and solution-oriented (never fatalistic or fear-based)
- Clear references to specific chart factors

Format your response with these sections:

**Key Insight:** (2-3 sentences directly answering the question)

**Astrological Analysis:** (Explain what you see in the chart - planetary positions, houses, yogas, dasha period that relate to the question)

**Guidance:** (Practical advice and recommendations based on the analysis)

**Remedy:** (One simple, accessible Vedic remedy - such as a mantra, gemstone recommendation, charitable act, or spiritual practice)

Remember:
- Always reference specific chart elements (planets, signs, houses, yogas)
- Be specific about WHY you're saying what you're saying based on the chart
- Maintain a balance between traditional wisdom and modern applicability
- Keep the tone encouraging and empowering
- Avoid making absolute predictions; instead, discuss tendencies and potentials
"""

    def _generate_fallback_response(self, question: str) -> str:
        """Generate fallback response if API fails"""

        return f"""Thank you for your question: "{question}"

I apologize, but I'm currently unable to generate a detailed interpretation due to technical issues.

**General Guidance:**

Your birth chart is a unique map of your karmic potential and life path. Every chart contains both challenges and opportunities, and Vedic astrology helps us understand how to navigate them wisely.

For the specific area you're asking about, I recommend:
- Reflect on your question during meditation or quiet contemplation
- Consider consulting with a qualified Vedic astrologer for personalized guidance
- Practice patience and self-compassion as you navigate this area of life

**Universal Remedy:**

Chant the Gayatri Mantra daily for clarity and divine guidance:
"Om Bhur Bhuvah Svah, Tat Savitur Varenyam, Bhargo Devasya Dhimahi, Dhiyo Yo Nah Prachodayat"

Please try your query again shortly, and I'll provide a detailed analysis based on your specific chart.
"""


# Singleton instance
ai_service = AIInterpretationService()
