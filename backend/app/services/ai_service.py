"""
AI Interpretation Service
Generates personalized Vedic astrology interpretations using OpenAI GPT-4
Enhanced with scripture-grounded rules from BPHS knowledge base
"""

from typing import Dict, Any, List, Optional
from openai import OpenAI, AzureOpenAI
import os

from app.core.config import settings
from app.services.rule_retrieval import rule_retrieval_service


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

    async def generate_interpretation(
        self,
        chart_data: Dict[str, Any],
        question: str,
        category: str = "general",
        use_knowledge_base: bool = True
    ) -> Dict[str, Any]:
        """
        Generate AI interpretation based on birth chart and user question
        Enhanced with scripture-grounded rules from BPHS knowledge base

        Args:
            chart_data: Complete birth chart data (from astrology service)
            question: User's specific question
            category: Query category (career, relationship, health, etc.)
            use_knowledge_base: Whether to retrieve and use BPHS rules (default: True)

        Returns:
            Dictionary containing interpretation, metadata, and rule citations
        """

        # Retrieve relevant rules from knowledge base
        retrieved_rules = []
        rules_context = ""

        if use_knowledge_base:
            try:
                rules_result = await self._retrieve_relevant_rules(
                    chart_data,
                    question,
                    category
                )
                retrieved_rules = rules_result.get('rules', [])
                rules_context = self._format_rules_for_prompt(retrieved_rules)
                print(f"✅ Retrieved {len(retrieved_rules)} rules from knowledge base")
            except Exception as e:
                print(f"⚠️  Rule retrieval failed: {e}. Proceeding without KB rules.")
                rules_context = ""

        # Prepare context from chart data
        context = self._prepare_chart_context(chart_data)

        # Create system prompt
        system_prompt = self._create_system_prompt()

        # Create user message with optional rules context
        if rules_context:
            user_message = f"""
{context}

--- SCRIPTURAL RULES FROM BRIHAT PARASHARA HORA SHASTRA ---
{rules_context}
--- END OF SCRIPTURAL RULES ---

Query Category: {category.upper()}

User's Question: {question}

Please provide a personalized Vedic astrology interpretation that:
1. Directly answers their question using chart insights AND the scriptural rules provided above
2. CITE specific rules using their Rule IDs in brackets like [BPHS-18-PAN-03]
3. References specific planetary positions, houses, yogas, and the scriptural basis
4. Offers practical, actionable guidance grounded in classical texts
5. Includes traditional Vedic wisdom from the rules
6. Is warm, empowering, and hopeful (never fatalistic)
7. Is approximately 250-350 words
8. Ends with one simple remedy (mantra, gemstone, charity, or practice)

IMPORTANT: When referencing a rule, include its Rule ID in brackets [RULE-ID] so users can trace back to the source text.
"""
        else:
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

            # Extract rule citations from the interpretation
            cited_rules = self._extract_rule_citations(interpretation, retrieved_rules)

            return {
                "interpretation": interpretation,
                "model": self.model,
                "tokens_used": tokens_used,
                "success": True,
                "rules_used": cited_rules,
                "rules_retrieved": len(retrieved_rules),
                "knowledge_base_used": use_knowledge_base and len(retrieved_rules) > 0
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

        return """You are an expert Vedic astrologer with 20+ years of experience in Jyotish (Vedic astrology). You combine deep traditional knowledge from classical texts like Brihat Parashara Hora Shastra (BPHS) with compassionate, practical guidance.

Your interpretation style:
- Warm, personalized, and empowering
- Grounded in classical Vedic astrology principles from authoritative texts
- Scripture-based analysis using specific rules from BPHS when provided
- Practical and actionable
- Hopeful and solution-oriented (never fatalistic or fear-based)
- Clear references to specific chart factors AND textual sources

When scriptural rules are provided:
- CITE the rules using their Rule IDs in brackets like [BPHS-18-PAN-03]
- Reference the chapter/verse anchors from the texts
- Ground your interpretation in the classical principles stated in the rules
- Explain how the chart activates or fulfills the conditions mentioned in the rules

Format your response with these sections:

**Key Insight:** (2-3 sentences directly answering the question)

**Astrological Analysis:** (Explain what you see in the chart - planetary positions, houses, yogas, dasha period that relate to the question. When rules are provided, reference them with citations.)

**Guidance:** (Practical advice and recommendations based on the analysis)

**Remedy:** (One simple, accessible Vedic remedy - such as a mantra, gemstone recommendation, charitable act, or spiritual practice)

Remember:
- Always reference specific chart elements (planets, signs, houses, yogas)
- When scriptural rules are provided, CITE them using [RULE-ID] format
- Be specific about WHY you're saying what you're saying based on the chart AND classical texts
- Maintain a balance between traditional wisdom and modern applicability
- Keep the tone encouraging and empowering
- Avoid making absolute predictions; instead, discuss tendencies and potentials
"""

    async def _retrieve_relevant_rules(
        self,
        chart_data: Dict[str, Any],
        query: str,
        domain: str
    ) -> Dict[str, Any]:
        """
        Retrieve relevant rules from knowledge base using hybrid RAG

        Args:
            chart_data: Birth chart data
            query: User's question
            domain: Query domain (career, wealth, relationships, etc.)

        Returns:
            Dictionary with retrieved rules and metadata
        """
        # Map category names to knowledge base domains
        domain_mapping = {
            "general": "general",
            "career": "career",
            "relationship": "relationships",
            "relationships": "relationships",
            "health": "health",
            "wealth": "wealth",
            "finance": "wealth",
            "education": "education",
            "spirituality": "spirituality"
        }

        kb_domain = domain_mapping.get(domain.lower(), "general")

        # Retrieve rules
        result = await rule_retrieval_service.retrieve_rules(
            chart_data=chart_data,
            query=query,
            domain=kb_domain,
            limit=5,  # Top 5 most relevant rules
            min_weight=0.5  # Only rules with decent weight
        )

        return result

    def _format_rules_for_prompt(self, rules: List[Dict[str, Any]]) -> str:
        """
        Format retrieved rules for inclusion in GPT-4 prompt

        Args:
            rules: List of rule dictionaries from knowledge base

        Returns:
            Formatted string with rules for prompt context
        """
        if not rules:
            return ""

        formatted_parts = []

        for i, rule in enumerate(rules, 1):
            rule_id = rule.get('rule_id', 'Unknown')
            condition = rule.get('condition', '')
            effect = rule.get('effect', '')
            anchor = rule.get('anchor', '')
            weight = rule.get('weight', 0)
            commentary = rule.get('commentary', '')

            rule_text = f"""
Rule {i}: [{rule_id}] (Weight: {weight})
Anchor: {anchor}
Condition: {condition}
Effect: {effect}"""

            if commentary:
                rule_text += f"\nCommentary: {commentary}"

            formatted_parts.append(rule_text)

        return "\n".join(formatted_parts)

    def _extract_rule_citations(
        self,
        interpretation: str,
        retrieved_rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract rule IDs cited in the interpretation

        Args:
            interpretation: The AI-generated interpretation text
            retrieved_rules: List of rules that were retrieved

        Returns:
            List of cited rules with their metadata
        """
        cited_rules = []

        # Build a map of rule_id to rule data
        rule_map = {rule.get('rule_id'): rule for rule in retrieved_rules}

        # Find all rule citations in the format [RULE-ID]
        import re
        pattern = r'\[([A-Z0-9\-]+)\]'
        citations = re.findall(pattern, interpretation)

        # Deduplicate and get rule details
        seen = set()
        for rule_id in citations:
            if rule_id not in seen and rule_id in rule_map:
                rule = rule_map[rule_id]
                cited_rules.append({
                    "rule_id": rule_id,
                    "anchor": rule.get('anchor', ''),
                    "weight": rule.get('weight', 0),
                    "relevance_score": rule.get('relevance_score', 0)
                })
                seen.add(rule_id)

        return cited_rules

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
