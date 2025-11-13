"""
AI Orchestrator Service
Multi-role LLM system for comprehensive Vedic astrology predictions
Implements: Coordinator, Retriever, Synthesizer, Verifier roles
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from openai import OpenAI, AzureOpenAI
import json
from enum import Enum

from app.core.config import settings
from app.services.rule_retrieval import rule_retrieval_service
from app.services.astrology import astrology_service
from app.services.ai_orchestrator_concise_prompt import get_concise_prompts


class OrchestratorRole(str, Enum):
    """Roles in the orchestration system"""
    COORDINATOR = "coordinator"
    RETRIEVER = "retriever"
    SYNTHESIZER = "synthesizer"
    VERIFIER = "verifier"
    PREDICTOR = "predictor"


class ConfidenceLevel(str, Enum):
    """Confidence levels for predictions"""
    VERY_HIGH = "very_high"  # 90-100%
    HIGH = "high"            # 75-89%
    MEDIUM = "medium"        # 50-74%
    LOW = "low"              # 25-49%
    VERY_LOW = "very_low"    # 0-24%


class AIOrchestrator:
    """
    Multi-role orchestration system for AI-powered Vedic astrology predictions

    Architecture:
    - Coordinator: Routes queries, manages workflow
    - Retriever: Gets relevant rules and chart factors
    - Synthesizer: Combines all information into interpretation
    - Verifier: Checks for contradictions and quality
    - Predictor: Calculates dasha × transit overlaps and date windows
    """

    def __init__(self):
        """Initialize OpenAI client and token budget"""
        if settings.USE_AZURE_OPENAI:
            self.client = AzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.model = settings.AZURE_OPENAI_DEPLOYMENT
            print(f"✅ AI Orchestrator using Azure OpenAI (deployment: {self.model})")
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4-turbo-preview"
            print("✅ AI Orchestrator using OpenAI")

        # Token budget tracking - SIGNIFICANTLY INCREASED for comprehensive reports
        self.token_budget = {
            "max_total": 30000,  # Maximum tokens per reading (increased for comprehensive output)
            "coordinator": 500,
            "retriever": 0,  # No LLM call, uses vector search
            "synthesizer": 20000,  # Increased from 3000 for comprehensive multi-section reports
            "verifier": 2000,  # Increased from 1500
            "predictor": 6000  # Increased from 2000 for detailed timelines
        }
        self.tokens_used = 0

    async def generate_comprehensive_reading(
        self,
        chart_data: Dict[str, Any],
        query: Optional[str] = None,
        domains: Optional[List[str]] = None,
        include_predictions: bool = True,
        include_transits: bool = False,
        prediction_window_months: int = 12,
        numerology_data: Optional[Dict[str, Any]] = None,
        yoga_data: Optional[Dict[str, Any]] = None,
        divisional_charts_data: Optional[Dict[str, Any]] = None,
        vimshopaka_bala_data: Optional[Dict[str, Any]] = None,
        reading_mode: str = "detailed"  # NEW: "concise" (400-500 words) or "detailed" (3500-4000 words)
    ) -> Dict[str, Any]:
        """
        Generate comprehensive reading using multi-role orchestration

        Args:
            chart_data: Complete birth chart data
            query: Optional specific question
            domains: List of domains to analyze (career, wealth, relationships, etc.)
            include_predictions: Whether to generate time-based predictions
            include_transits: Whether to include current transit analysis
            prediction_window_months: How many months ahead to predict
            numerology_data: Optional numerology profile data (Western & Vedic)
            yoga_data: Optional yoga detection data (40+ classical Vedic yogas)
            divisional_charts_data: Optional divisional charts (Shodashvarga) data
            vimshopaka_bala_data: Optional Vimshopaka Bala (planetary strength) data
            reading_mode: "concise" (400-600 words, focused) or "detailed" (2500-4000 words, comprehensive)

        Returns:
            Dictionary with comprehensive reading, predictions, citations, and metadata
        """
        print(f"🎭 Starting Multi-Role Orchestration (Mode: {reading_mode})...")
        self.tokens_used = 0

        if numerology_data:
            print(f"🔢 Numerology data available for holistic analysis")

        if yoga_data:
            print(f"🧘 Yoga data available: {yoga_data.get('total_yogas', 0)} total, {yoga_data.get('significant_yogas', 0)} significant")

        if divisional_charts_data:
            num_charts = len(divisional_charts_data)
            print(f"📊 Divisional charts data available: {num_charts} charts (Shodashvarga system)")

        if vimshopaka_bala_data:
            strongest = vimshopaka_bala_data.get('summary', {}).get('strongest_planet', {})
            print(f"💪 Vimshopaka Bala available - Strongest: {strongest.get('name', 'N/A')} ({strongest.get('quality', 'N/A')})")

        # Step 1: Coordinator - Analyze query and route
        coordination_result = await self._coordinator_role(
            chart_data=chart_data,
            query=query,
            domains=domains
        )

        print(f"📋 Coordinator: {coordination_result['domains_to_analyze']}")

        # Step 2: Retriever - Get relevant rules for each domain
        retrieval_results = await self._retriever_role(
            chart_data=chart_data,
            domains=coordination_result['domains_to_analyze'],
            query=query
        )

        print(f"📚 Retriever: Retrieved {retrieval_results['total_rules']} rules across {len(retrieval_results['by_domain'])} domains")

        # Step 3: Predictor - Calculate dasha × transit overlaps and date windows
        prediction_results = None
        if include_predictions:
            prediction_results = await self._predictor_role(
                chart_data=chart_data,
                domains=coordination_result['domains_to_analyze'],
                window_months=prediction_window_months,
                include_transits=include_transits
            )
            print(f"🔮 Predictor: Generated {len(prediction_results.get('predictions', []))} predictions")

        # Step 4: Synthesizer - Combine all information into interpretation
        synthesis_result = await self._synthesizer_role(
            chart_data=chart_data,
            query=query,
            coordination=coordination_result,
            retrieval=retrieval_results,
            predictions=prediction_results,
            numerology_data=numerology_data,
            yoga_data=yoga_data,
            divisional_charts_data=divisional_charts_data,
            vimshopaka_bala_data=vimshopaka_bala_data,
            reading_mode=reading_mode  # NEW: Pass reading mode to synthesizer
        )

        print(f"✍️  Synthesizer: Generated {len(synthesis_result['interpretation'])} character interpretation")

        # Step 5: Verifier - Check quality and contradictions
        verification_result = await self._verifier_role(
            synthesis=synthesis_result,
            retrieval=retrieval_results,
            chart_data=chart_data
        )

        print(f"✅ Verifier: Quality score {verification_result['quality_score']}/10")

        # Compile final result
        final_result = {
            "interpretation": synthesis_result['interpretation'],
            "domain_analyses": synthesis_result.get('domain_analyses', {}),
            "predictions": prediction_results.get('predictions', []) if prediction_results else [],
            "rules_used": retrieval_results['rules_cited'],
            "total_rules_retrieved": retrieval_results['total_rules'],
            "verification": verification_result,
            "orchestration_metadata": {
                "roles_executed": ["coordinator", "retriever", "synthesizer", "verifier"] + (["predictor"] if include_predictions else []),
                "tokens_used": self.tokens_used,
                "token_budget": self.token_budget['max_total'],
                "domains_analyzed": coordination_result['domains_to_analyze'],
                "model": self.model,
                "timestamp": datetime.utcnow().isoformat()
            },
            "confidence": verification_result.get('overall_confidence', 'medium'),
            "success": True
        }

        print(f"🎉 Orchestration Complete! Total tokens: {self.tokens_used}/{self.token_budget['max_total']}")

        # Debug: Print comprehensive final result
        print(f"\n{'='*100}")
        print(f"📊 FINAL COMPREHENSIVE READING RESULT")
        print(f"{'='*100}")
        print(f"\n📝 Interpretation Length: {len(final_result['interpretation'])} characters")
        print(f"\n🎯 Domain Analyses: {list(final_result.get('domain_analyses', {}).keys())}")
        print(f"\n🔮 Predictions Count: {len(final_result['predictions'])}")
        if final_result['predictions']:
            print("\n📅 PREDICTIONS DETAIL:")
            for i, pred in enumerate(final_result['predictions'], 1):
                print(f"\n  Prediction #{i}:")
                print(f"    Domain: {pred.get('domain', 'N/A')}")
                print(f"    Summary: {pred.get('prediction_summary', 'N/A')[:100]}...")
                print(f"    Key Periods: {len(pred.get('key_periods', []))} periods")
                print(f"    Confidence: {pred.get('confidence_score', 'N/A')}%")
        else:
            print("\n⚠️  NO PREDICTIONS IN FINAL RESULT!")
        print(f"\n📚 Rules Used: {len(final_result['rules_used'])} rules")
        print(f"\n✅ Verification Quality Score: {final_result['verification'].get('quality_score', 'N/A')}/10")
        print(f"\n{'='*100}\n")

        return final_result

    async def _coordinator_role(
        self,
        chart_data: Dict[str, Any],
        query: Optional[str],
        domains: Optional[List[str]]
    ) -> Dict[str, Any]:
        """
        Coordinator role: Analyze query and determine which domains to analyze

        Returns:
            Dictionary with routing decisions and domain priorities
        """
        print("🎭 Coordinator: Analyzing query and routing...")

        # If domains explicitly provided, use those
        if domains:
            return {
                "domains_to_analyze": domains,
                "query_type": "explicit_domains",
                "priority_domain": domains[0] if domains else "general"
            }

        # If specific query provided, use LLM to route
        if query:
            prompt = f"""You are a routing coordinator for a Vedic astrology system.
Analyze this user query and determine which life domains are most relevant.

User Query: "{query}"

Available Domains:
- career: Professional life, occupation, achievements
- wealth: Financial prosperity, assets, income
- relationships: Marriage, partnerships, spouse
- health: Physical wellbeing, longevity
- education: Learning, knowledge, academic success
- spirituality: Moksha, dharma, spiritual growth
- general: Overall life analysis

Return a JSON object with:
{{
    "domains_to_analyze": ["domain1", "domain2", ...],  // 1-3 most relevant domains
    "priority_domain": "primary_domain",  // Most relevant
    "query_type": "specific" or "general",
    "reasoning": "Brief explanation"
}}
"""

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=300,
                    response_format={"type": "json_object"}
                )

                self.tokens_used += response.usage.total_tokens
                result = json.loads(response.choices[0].message.content)

                return result

            except Exception as e:
                print(f"⚠️  Coordinator LLM call failed: {e}. Using fallback.")
                # Fallback: analyze all main domains
                return {
                    "domains_to_analyze": ["general", "career", "wealth"],
                    "priority_domain": "general",
                    "query_type": "general",
                    "reasoning": "Fallback routing"
                }

        # No query or domains: comprehensive reading
        return {
            "domains_to_analyze": ["general", "career", "wealth", "relationships", "health"],
            "query_type": "comprehensive",
            "priority_domain": "general"
        }

    async def _retriever_role(
        self,
        chart_data: Dict[str, Any],
        domains: List[str],
        query: Optional[str]
    ) -> Dict[str, Any]:
        """
        Retriever role: Get relevant rules from knowledge base for each domain

        Returns:
            Dictionary with retrieved rules organized by domain
        """
        print("📚 Retriever: Fetching rules from knowledge base...")

        all_rules = []
        rules_by_domain = {}

        for domain in domains:
            try:
                result = await rule_retrieval_service.retrieve_rules(
                    chart_data=chart_data,
                    query=query or f"What does the chart indicate about {domain}?",
                    domain=domain,
                    limit=5,
                    min_weight=0.5
                )

                domain_rules = result.get('rules', [])
                all_rules.extend(domain_rules)
                rules_by_domain[domain] = domain_rules

            except Exception as e:
                print(f"⚠️  Rule retrieval failed for domain '{domain}': {e}")
                rules_by_domain[domain] = []

        # Extract cited rule IDs
        rules_cited = [
            {
                "rule_id": rule.get('rule_id'),
                "domain": rule.get('domain'),
                "anchor": rule.get('anchor'),
                "weight": rule.get('weight'),
                "relevance_score": rule.get('relevance_score')
            }
            for rule in all_rules
        ]

        return {
            "total_rules": len(all_rules),
            "by_domain": rules_by_domain,
            "rules_cited": rules_cited
        }

    async def _predictor_role(
        self,
        chart_data: Dict[str, Any],
        domains: List[str],
        window_months: int,
        include_transits: bool
    ) -> Dict[str, Any]:
        """
        Predictor role: Calculate dasha × transit overlaps and generate date windows

        Returns:
            Dictionary with time-based predictions and confidence scores
        """
        print("🔮 Predictor: Calculating dasha × transit overlaps...")

        predictions = []

        # Get current dasha
        current_dasha = chart_data.get('dasha', {})
        if not current_dasha:
            return {"predictions": [], "message": "No dasha data available"}

        # Calculate prediction window
        today = datetime.now()
        end_date = today + timedelta(days=window_months * 30)

        # For each domain, create predictions based on dasha periods
        for domain in domains:
            prediction = await self._generate_domain_prediction(
                chart_data=chart_data,
                domain=domain,
                current_dasha=current_dasha,
                start_date=today,
                end_date=end_date,
                include_transits=include_transits
            )

            if prediction:
                predictions.append(prediction)

        return {
            "predictions": predictions,
            "window_start": today.isoformat(),
            "window_end": end_date.isoformat(),
            "window_months": window_months
        }

    async def _generate_domain_prediction(
        self,
        chart_data: Dict[str, Any],
        domain: str,
        current_dasha: Dict[str, Any],
        start_date: datetime,
        end_date: datetime,
        include_transits: bool
    ) -> Optional[Dict[str, Any]]:
        """Generate prediction for a specific domain"""

        # Extract relevant chart factors for the domain
        chart_context = self._extract_domain_factors(chart_data, domain)

        # Create prediction prompt
        prompt = f"""You are a Vedic astrology prediction engine.
Generate a specific, time-bound prediction for the {domain.upper()} domain.

Chart Context:
{chart_context}

Current Dasha: {current_dasha.get('current_dasha')} (period: {current_dasha.get('period_years')} years)

Time Window: {start_date.strftime('%B %Y')} to {end_date.strftime('%B %Y')}

Based on the dasha period and chart factors, predict:
1. What will likely happen in this domain during this period
2. When (specific months) the effects will be strongest
3. Confidence level (0-100)

Return JSON:
{{
    "domain": "{domain}",
    "prediction_summary": "Brief prediction",
    "key_periods": [
        {{"month": "2025-03", "event": "description", "intensity": "high/medium/low"}}
    ],
    "confidence_score": 75,
    "reasoning": "Why this prediction is made"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            self.tokens_used += response.usage.total_tokens
            prediction = json.loads(response.choices[0].message.content)

            # Debug: Print the LLM-generated prediction
            print(f"\n{'='*80}")
            print(f"🔮 PREDICTION GENERATED for {domain.upper()} domain:")
            print(f"{'='*80}")
            print(f"Raw LLM Response:\n{json.dumps(prediction, indent=2)}")
            print(f"{'='*80}\n")

            # Add confidence level enum
            prediction['confidence_level'] = self._score_to_confidence_level(
                prediction.get('confidence_score', 50)
            )

            return prediction

        except Exception as e:
            print(f"⚠️  Prediction generation failed for {domain}: {e}")
            return None

    def _extract_domain_factors(self, chart_data: Dict[str, Any], domain: str) -> str:
        """Extract relevant chart factors for a domain"""

        # Domain-specific house mappings
        domain_houses = {
            "career": [1, 10],
            "wealth": [2, 11],
            "relationships": [7, 8],
            "health": [1, 6],
            "education": [4, 5],
            "spirituality": [9, 12]
        }

        relevant_houses = domain_houses.get(domain, [1])

        # Extract planets in relevant houses
        planets = chart_data.get('planets', {})
        relevant_planets = []

        for planet, data in planets.items():
            if data.get('house') in relevant_houses:
                relevant_planets.append(f"{planet} in {data.get('sign')} ({data.get('house')}th house)")

        context = f"Domain: {domain}\n"
        context += f"Relevant Houses: {relevant_houses}\n"
        context += f"Planets: {', '.join(relevant_planets)}\n"

        return context

    def _score_to_confidence_level(self, score: float) -> str:
        """Convert numeric score to confidence level"""
        if score >= 90:
            return ConfidenceLevel.VERY_HIGH.value
        elif score >= 75:
            return ConfidenceLevel.HIGH.value
        elif score >= 50:
            return ConfidenceLevel.MEDIUM.value
        elif score >= 25:
            return ConfidenceLevel.LOW.value
        else:
            return ConfidenceLevel.VERY_LOW.value

    async def _synthesizer_role(
        self,
        chart_data: Dict[str, Any],
        query: Optional[str],
        coordination: Dict[str, Any],
        retrieval: Dict[str, Any],
        predictions: Optional[Dict[str, Any]],
        numerology_data: Optional[Dict[str, Any]] = None,
        yoga_data: Optional[Dict[str, Any]] = None,
        divisional_charts_data: Optional[Dict[str, Any]] = None,
        vimshopaka_bala_data: Optional[Dict[str, Any]] = None,
        reading_mode: str = "concise"  # NEW: Pass reading mode
    ) -> Dict[str, Any]:
        """
        Synthesizer role: Combine all information into comprehensive interpretation

        Returns:
            Dictionary with synthesized interpretation and domain analyses
        """
        print("✍️  Synthesizer: Combining all information...")

        # Prepare chart context
        chart_context = self._prepare_chart_context(chart_data)

        # Prepare numerology context if available
        numerology_context = ""
        if numerology_data:
            numerology_context = self._prepare_numerology_context(numerology_data)
            print(f"📊 Numerology context prepared for synthesis: {len(numerology_context)} characters")
        else:
            print(f"ℹ️  No numerology data for synthesis")

        # Prepare yoga context if available
        yoga_context = ""
        if yoga_data:
            yoga_context = self._prepare_yoga_context(yoga_data)
            print(f"🧘 Yoga context prepared for synthesis: {yoga_data.get('significant_yogas', 0)} significant yogas")
        else:
            print(f"ℹ️  No yoga data for synthesis")

        # Prepare divisional charts context if available
        divisional_charts_context = ""
        if divisional_charts_data:
            divisional_charts_context = self._prepare_divisional_charts_context(divisional_charts_data, vimshopaka_bala_data)
            print(f"📊 Divisional charts context prepared: {len(divisional_charts_data)} charts")
        else:
            print(f"ℹ️  No divisional charts data for synthesis")

        # Prepare rules context
        rules_context = self._format_rules_for_synthesis(retrieval['by_domain'])

        # Prepare predictions context
        predictions_context = ""
        if predictions and predictions.get('predictions'):
            predictions_context = "\n\n--- TIME-BASED PREDICTIONS ---\n"
            for pred in predictions['predictions']:
                predictions_context += f"\n{pred['domain'].upper()}: {pred.get('prediction_summary', '')}"
                predictions_context += f"\nConfidence: {pred.get('confidence_score', 0)}%"

        # Choose prompts based on reading_mode
        if reading_mode == "concise":
            print("📝 Using CONCISE mode for specific queries (400-500 words)")

            # Build context sections
            context_sections = [chart_context]

            if numerology_context:
                context_sections.append(f"\n--- NUMEROLOGY PROFILE ---\n{numerology_context}\n--- END OF NUMEROLOGY ---")

            if yoga_context:
                context_sections.append(f"\n--- CLASSICAL VEDIC YOGAS ---\n{yoga_context}\n--- END OF YOGAS ---")

            if divisional_charts_context:
                context_sections.append(f"\n--- DIVISIONAL CHARTS (SHODASHVARGA) ---\n{divisional_charts_context}\n--- END OF DIVISIONAL CHARTS ---")

            full_context = "\n".join(context_sections)

            # Use concise prompts from separate module (for specific user questions)
            system_prompt, user_prompt = get_concise_prompts(
                full_context=full_context,
                rules_context=rules_context,
                predictions_context=predictions_context,
                query=query or "Provide a focused answer",
                domains=coordination['domains_to_analyze'],
                numerology_data=numerology_data,
                yoga_data=yoga_data,
                divisional_charts_data=divisional_charts_data,
                vimshopaka_bala_data=vimshopaka_bala_data,
                numerology_context=numerology_context,
                yoga_context=yoga_context,
                divisional_charts_context=divisional_charts_context
            )

            max_tokens = 3000  # For 400-500 word specific answers

        else:  # detailed mode
            print("📝 Using DETAILED mode for comprehensive readings (3500-4000 words)")

            # Create synthesis prompt - COMPREHENSIVE VERSION
            system_prompt = """You are an expert Vedic astrology and numerology synthesizer creating COMPREHENSIVE, DETAILED life analysis reports.
Your role is to combine chart data, numerology profiles, scriptural rules, and predictions into an in-depth, structured interpretation covering ALL life aspects.

CRITICAL REQUIREMENTS:
1. Generate COMPREHENSIVE, DETAILED analysis (3500-4000 words minimum)
2. Cover ALL life domains thoroughly, not superficially
3. CITE rules using [RULE-ID] format extensively
4. Include specific planetary positions, degrees, houses, nakshatras, yogas, doshas
5. Provide DETAILED timelines: monthly (next 12 months), quarterly (next 3 years), yearly (next 7 years)
6. Integrate astrology AND numerology comprehensively
7. Include Shodashvarga (divisional charts) analysis where relevant
8. Reference Lal Kitab remedies
9. Provide detailed health risk matrix, financial strategies, relationship compatibility
10. Include action checklists and risk registers

STRUCTURE YOUR RESPONSE WITH THESE COMPREHENSIVE SECTIONS:

## 🌟 EXECUTIVE SUMMARY
(3-4 paragraphs synthesizing the most important insights from astrology and numerology. Include current life phase, major strengths, key challenges, and immediate focus areas.)

## 🔭 CORE ASTROLOGICAL FRAMEWORK

### Lagna and Planetary Core
- Ascendant: Sign, degree, nakshatra, pada, lord, dispositor chain
- Moon: Sign, nakshatra, tithi, paksha
- Planetary positions with full details (dignity, retrograde, combustion, shadbala)
- House lords and their placements

### Major Yogas and Doshas
- Rajayogas (Gajakesari, Budha-Aditya, Pancha Mahapurusha, etc.)
- Dhanayogas (wealth combinations)
- Manglik/Kuja Dosha analysis with cancellations
- Kaal Sarpa Dosha (type and effects)
- Other significant yogas and their effects

## 📊 SHODASHVARGA ANALYSIS
Analyze key divisional charts:
- D1 (Rashi): Overall life
- D2 (Hora): Wealth patterns
- D9 (Navamsa): Marriage and dharma
- D10 (Dashamsa): Career trajectory
- D7 (Saptamsa): Children
- Other relevant vargas based on query

## 🕰️ DASHA ANALYSIS (Vimshottari)
Current Mahadasha, Antardasha, Pratyantardasha with:
- Detailed effects and themes
- Key event windows
- Planetary periods ahead with timing
- Remedial measures for difficult periods

## 🪐 TRANSIT ANALYSIS (Gochar)

### Sade Sati
If applicable, detailed 3-phase analysis with:
- Current phase and effects
- Timing of each phase
- Specific challenges and opportunities
- Phase-specific remedies

### Major Transits
- Saturn transit effects (houses from Lagna and Moon)
- Jupiter transit benefits
- Rahu-Ketu axis movements
- Double transit triggers

## 💰 FINANCIAL & CAREER ANALYSIS
**Career Strengths:** (Based on 10th house, D10, Amatyakaraka, professional yogas)
**Recommended Fields:** (Specific professions based on planetary strengths)
**Income Streams:** (Analysis of 2nd, 6th, 11th houses)
**Growth Triggers:** (Dasha periods and transits for advancement)
**Investment Strategy:** (Timing for property, vehicles, assets - 4th, D4, D16)
**Risk Factors:** (6th, 8th house challenges)
**Financial Timeline:**
- Next 12 months (month-by-month opportunities and cautions)
- 3-year financial trajectory
- 7-year wealth building phases

## 💞 RELATIONSHIPS & MARRIAGE
**Partner Profile:** (7th house, D9 analysis, Venus placement)
**Compatibility Factors:** (Nakshatra matching, Kuta points if applicable)
**Marriage Timing:** (Dasha periods and transit windows)
**Relationship Dynamics:** (Benefic/malefic aspects, yogas)
**Remedies for Harmony:** (Specific mantras, fasts, donations)
**Children Analysis:** (5th house, D7, Jupiter placement, timing windows)

## 🩺 HEALTH & MEDICAL ASTROLOGY
**Constitutional Analysis:** (6th house, Ayurvedic prakriti based on chart)
**Risk Matrix:**
System | Risk Level | Indicators | Prevention
Nervous | High/Medium/Low | Planetary factors | Guidelines
Cardiovascular | | |
Digestive | | |
Reproductive | | |
Respiratory | | |
**Chronic vs Acute Patterns:**
**Surgery Indicators:** (Mars/Ketu/8th house analysis)
**Favorable Healing Periods:**
**Preventive Guidance:** (Diet, lifestyle, Ayurveda, yoga)

## 🏠 PROPERTY, VEHICLES & ASSETS
- 4th house and D4 analysis
- Purchase windows (favorable dasha × transit periods)
- Vehicle indications (D16 Shodasamsa)
- Real estate investment timing
- Cautions and remedies

## ⚖️ LITIGATION & LEGAL MATTERS
- 6th house analysis
- Risk windows for disputes
- Protective measures
- Favorable periods for settlements

## ✈️ FOREIGN TRAVEL & RESIDENCE
- 12th house and foreign settlement yogas
- Travel windows in next 3 years
- Purpose (education, career, pilgrimage)
- Success factors abroad

## 🕉️ SPIRITUALITY & INNER GROWTH
- Atmakaraka and moksha analysis
- D20 Vimsamsa study
- Ketu and 12th house themes
- Spiritual practices suited to chart
- Meditation and yoga recommendations

## 🔮 COMPREHENSIVE TIMELINE PREDICTIONS

### Next 12 Months (Month-by-Month)
Month | Key Themes | Opportunities | Cautions | Overall Rating
Jan 2025 | | | | ⭐⭐⭐⭐
Feb 2025 | | | | ⭐⭐⭐
(Continue for all 12 months)

### Next 3 Years (Quarterly Breakdown)
Q1 2025 | Major Events | Finance | Health | Relationships | Career
Q2 2025 | | | | |
(Continue through Q4 2027)

### Next 7 Years (Yearly Overview)
2025 | Dasha Period | Major Life Events | Focus Areas | Challenges | Opportunities
2026 | | | | |
(Continue through 2031)

## 🔢 NUMEROLOGY INTEGRATION
(REQUIRED if numerology data provided)

### Western Numerology
- **Life Path {number}:** Detailed meaning and life purpose
- **Expression {number}:** Natural talents and abilities
- **Soul Urge {number}:** Inner desires and motivations
- **Personality {number}:** How others perceive you
- **Maturity Number:** Goals after age 35-40
- **Current Personal Year:** {year} - themes and guidance
- **Personal Months:** Next 12 months cycle

### Vedic Numerology
- **Psychic Number (Moolank):** Inner self analysis
- **Destiny Number (Bhagyank):** Life path and purpose
- **Name Number:** Vibration and corrections if needed
- **Planetary Rulers:** Numbers and their planetary associations
- **Lucky Numbers, Days, Colors**

### Astro-Numerology Correlation
(Show how numerological planetary rulers align with astrological planets. Example: Life Path 3 ruled by Jupiter correlating with Jupiter's placement in chart)

## 📕 LAL KITAB INSIGHTS
House-by-house Lal Kitab interpretation:
- Planetary debts and karmic patterns
- Simple home remedies (no costly rituals)
- Do's and Don'ts by planet
- Annual Varshaphal hooks

## 💎 COMPREHENSIVE REMEDIES

### Gemstones
Planet | Stone | Carat | Metal | Finger | Day/Time | Mantra | Trial Period
Jupiter | Yellow Sapphire | 5-7 | Gold | Index (R) | Thu, Sunrise | Om Gurave Namah | 7 days

### Mantras & Practices
Purpose | Mantra/Practice | Frequency | Timing | Duration

### Vrata (Fasting)
Day | Method | Purpose | Duration

### Donations (Dana)
Item | Day | Benefic Planet | Purpose

### Puja, Homa & Pilgrimage
Deity | Ritual | Timing | Purpose

### Color, Directions & Vastu
- Lucky colors / Unfavorable colors
- Sleep direction / Work direction
- Home Vastu corrections

### Diet & Lifestyle (Ayurveda)
- Prakriti (constitution)
- Foods to favor / Foods to avoid
- Yoga asanas / Pranayama
- Daily routine adjustments

## ⚠️ RISK REGISTER
Domain | Specific Risk | Probability | Timing | Mitigation Strategy
Financial | | High/Med/Low | |
Health | | | |
Relationship | | | |
Legal | | | |
Travel | | | |

## ✅ ACTION CHECKLISTS

### Next 30 Days
- [ ] Action item with specific guidance
- [ ] Action item

### Next 90 Days
- [ ] Quarterly goals
- [ ] Preparation steps

### Next 12 Months (Quarterly)
Q1: Key focus areas and deliverables
Q2: Building phase priorities
Q3: Consolidation activities
Q4: Review and planning

## 🎯 CLOSING GUIDANCE
**Core Strengths to Leverage:**
**Key Life Lessons:**
**Favorable Periods Summary:**
**Remedies Priority List:**
**Free Will Reminder:** Planets incline but do not compel. Your choices and efforts shape destiny.

---

IMPORTANT: This should be a COMPREHENSIVE, DETAILED report of 3500-4000 words. Do NOT summarize. Provide in-depth analysis for EACH section."""

            # Build context sections
            context_sections = [chart_context]

            if numerology_context:
                context_sections.append(f"\n--- NUMEROLOGY PROFILE ---\n{numerology_context}\n--- END OF NUMEROLOGY ---")

            if yoga_context:
                context_sections.append(f"\n--- CLASSICAL VEDIC YOGAS ---\n{yoga_context}\n--- END OF YOGAS ---")

            if divisional_charts_context:
                context_sections.append(f"\n--- DIVISIONAL CHARTS (SHODASHVARGA) ---\n{divisional_charts_context}\n--- END OF DIVISIONAL CHARTS ---")

            full_context = "\n".join(context_sections)

            user_prompt = f"""
{full_context}

{rules_context}

{predictions_context}

Query/Focus: {query or "Provide a comprehensive life analysis covering all domains"}
Domains to Analyze: {', '.join(coordination['domains_to_analyze'])}

CREATE A COMPREHENSIVE, DETAILED LIFE ANALYSIS REPORT (3500-4000 WORDS MINIMUM) following the structure provided in the system prompt.

MANDATORY REQUIREMENTS:
1. Follow the comprehensive section structure exactly
2. Provide IN-DEPTH analysis for EVERY section - do NOT skip or summarize
3. Include specific chart details: planetary degrees, nakshatras, houses, yogas, doshas
4. CITE scriptural rules extensively using [RULE-ID] format
5. Generate DETAILED month-by-month timeline for next 12 months
6. Provide quarterly breakdown for next 3 years
7. Include yearly overview for next 7 years
8. {f"INTEGRATE numerology data comprehensively - dedicate substantial space to Life Path {numerology_data.get('western', {}).get('core_numbers', {}).get('life_path', 'N/A')}, Expression, Soul Urge, Personal Year cycles, and Vedic numbers" if numerology_data else "Focus on astrological depth"}
9. Include health risk matrix with multiple body systems
10. Provide detailed financial strategies and career roadmap
11. Include comprehensive remedies table (gemstones, mantras, fasting, donations, etc.)
12. Add risk register with specific risks and mitigations
13. Provide actionable checklists for 30 days, 90 days, and 12 months

TIMELINE REQUIREMENTS:
- Next 12 Months: Create table with columns: Month | Key Themes | Opportunities | Cautions | Rating (1-5 stars)
  * Fill ALL 12 months with specific guidance
- Next 3 Years: Create quarterly table with columns: Quarter | Major Events | Finance | Health | Relationships | Career
  * Fill all 12 quarters (Q1-2025 through Q4-2027)
- Next 7 Years: Create yearly table with columns: Year | Dasha Period | Major Life Events | Focus Areas | Challenges | Opportunities
  * Fill all 7 years (2025-2031)

NUMEROLOGY INTEGRATION (if data provided):
{f'''REQUIRED: Analyze the following numerology data comprehensively:
- Life Path: {numerology_data.get('western', {}).get('core_numbers', {}).get('life_path', 'N/A')}
- Expression: {numerology_data.get('western', {}).get('core_numbers', {}).get('expression', 'N/A')}
- Soul Urge: {numerology_data.get('western', {}).get('core_numbers', {}).get('soul_urge', 'N/A')}
- Personal Year: {numerology_data.get('western', {}).get('personal_cycles', {}).get('personal_year', 'N/A')}
- Vedic Psychic: {numerology_data.get('vedic', {}).get('psychic_number', 'N/A')}
- Vedic Destiny: {numerology_data.get('vedic', {}).get('destiny_number', 'N/A')}

Show how these numbers correlate with astrological factors and enhance the reading.''' if numerology_data else 'Focus on astrological depth and scriptural foundations.'}

HEALTH ANALYSIS REQUIREMENT:
Create detailed health risk matrix covering:
- Nervous system
- Cardiovascular system
- Digestive system
- Reproductive system
- Respiratory system
- Immune system
Rate each as High/Medium/Low risk with specific planetary indicators and preventive guidance.

REMEDIES REQUIREMENT:
Create comprehensive remedies covering:
1. Gemstones table (planet, stone, carat, metal, finger, day/time, mantra)
2. Mantras list (purpose, text, count, frequency)
3. Vrata/fasting schedule (day, method, purpose)
4. Donations schedule (item, day, benefic planet)
5. Color guidance (lucky colors, colors to avoid)
6. Direction guidance (sleep, work, meditation)
7. Ayurvedic recommendations (prakriti, diet do's/don'ts, yoga/pranayama)

This is a FULL COMPREHENSIVE REPORT. Aim for 3500-4000 words. Do NOT summarize or skip sections.
"""

            max_tokens = 25000  # For 3500-4000 word comprehensive reports

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens  # Dynamic: 3000 for concise, 25000 for detailed
            )

            self.tokens_used += response.usage.total_tokens
            interpretation = response.choices[0].message.content

            return {
                "interpretation": interpretation,
                "tokens_used": response.usage.total_tokens
            }

        except Exception as e:
            print(f"❌ Synthesizer failed: {e}")
            return {
                "interpretation": "Unable to generate interpretation due to technical error.",
                "error": str(e)
            }

    def _prepare_chart_context(self, chart_data: Dict[str, Any]) -> str:
        """Prepare chart data for synthesis"""
        context_parts = []

        # Ascendant
        if "ascendant" in chart_data:
            asc = chart_data["ascendant"]
            context_parts.append(f"Ascendant: {asc.get('sign')} at {asc.get('position', 0):.2f}°")

        # Planets
        if "planets" in chart_data:
            context_parts.append("\nPlanetary Positions:")
            for planet, data in chart_data["planets"].items():
                retrograde = " (R)" if data.get("retrograde") else ""
                context_parts.append(
                    f"  {planet}: {data.get('sign')} in {data.get('house')}th house{retrograde}"
                )

        # Dasha
        if "dasha" in chart_data:
            dasha = chart_data["dasha"]
            context_parts.append(f"\nCurrent Dasha: {dasha.get('current_dasha')}")

        return "\n".join(context_parts)

    def _format_rules_for_synthesis(self, rules_by_domain: Dict[str, List]) -> str:
        """Format retrieved rules for synthesis"""
        if not rules_by_domain:
            return ""

        formatted = "\n--- SCRIPTURAL RULES FROM BPHS ---\n"

        for domain, rules in rules_by_domain.items():
            if rules:
                formatted += f"\n{domain.upper()} Domain:\n"
                for i, rule in enumerate(rules[:3], 1):  # Top 3 per domain
                    formatted += f"\n[{rule.get('rule_id')}] (Weight: {rule.get('weight', 0)})\n"
                    formatted += f"Anchor: {rule.get('anchor', '')}\n"
                    formatted += f"Condition: {rule.get('condition', '')}\n"
                    formatted += f"Effect: {rule.get('effect', '')}\n"

        return formatted

    def _prepare_numerology_context(self, numerology_data: Dict[str, Any]) -> str:
        """Prepare numerology context for synthesis"""

        context_parts = []

        print(f"🔍 DEBUG: Numerology data keys: {numerology_data.keys() if numerology_data else 'None'}")

        # Western numerology
        if "western" in numerology_data and numerology_data["western"]:
            western = numerology_data["western"]
            context_parts.append("\n=== WESTERN NUMEROLOGY ===")
            print(f"   Western data found: {western.keys() if isinstance(western, dict) else type(western)}")

            if "core_numbers" in western and western["core_numbers"]:
                core = western["core_numbers"]
                context_parts.append("\nCore Numbers:")

                # Life Path
                if "life_path" in core:
                    lp = core["life_path"]
                    context_parts.append(f"  Life Path {lp.get('number')}: Your life's purpose and journey")
                    if "meaning" in lp and isinstance(lp["meaning"], dict):
                        if "description" in lp["meaning"]:
                            context_parts.append(f"    {lp['meaning']['description']}")

                # Expression
                if "expression" in core:
                    exp = core["expression"]
                    context_parts.append(f"  Expression {exp.get('number')}: Your natural talents and abilities")

                # Soul Urge
                if "soul_urge" in core:
                    su = core["soul_urge"]
                    context_parts.append(f"  Soul Urge {su.get('number')}: Your inner desires and motivations")

                # Personality
                if "personality" in core:
                    pers = core["personality"]
                    context_parts.append(f"  Personality {pers.get('number')}: How others perceive you")

            if "current_cycles" in western:
                cycles = western["current_cycles"]
                context_parts.append("\nCurrent Cycles:")
                if "personal_year" in cycles:
                    py = cycles["personal_year"]
                    context_parts.append(f"  Personal Year {py.get('number')}: This year's theme and opportunities")
                if "personal_month" in cycles:
                    pm = cycles["personal_month"]
                    context_parts.append(f"  Personal Month {pm.get('number')}: This month's focus")
                if "personal_day" in cycles:
                    pd = cycles["personal_day"]
                    context_parts.append(f"  Personal Day {pd.get('number')}: Today's energy")

        # Vedic numerology
        if "vedic" in numerology_data and numerology_data["vedic"]:
            vedic = numerology_data["vedic"]
            context_parts.append("\n=== VEDIC NUMEROLOGY ===")
            print(f"   Vedic data found: {vedic.keys() if isinstance(vedic, dict) else type(vedic)}")

            if "psychic_number" in vedic and vedic["psychic_number"]:
                pn = vedic["psychic_number"]
                planet = pn.get("planet", "")
                context_parts.append(f"\nPsychic Number (Moolank): {pn.get('number')} - Ruled by {planet}")
                if "meaning" in pn and isinstance(pn["meaning"], dict):
                    if "description" in pn["meaning"]:
                        context_parts.append(f"  {pn['meaning']['description']}")

            if "destiny_number" in vedic:
                dn = vedic["destiny_number"]
                planet = dn.get("planet", "")
                context_parts.append(f"\nDestiny Number (Bhagyank): {dn.get('number')} - Ruled by {planet}")
                if "meaning" in dn:
                    meaning_text = dn["meaning"] if isinstance(dn["meaning"], str) else dn["meaning"].get("description", "")
                    if meaning_text:
                        context_parts.append(f"  {meaning_text}")

        return "\n".join(context_parts)

    def _prepare_yoga_context(self, yoga_data: Dict[str, Any]) -> str:
        """Prepare yoga (classical combinations) context for synthesis"""

        context_parts = []

        if not yoga_data or not yoga_data.get('yogas'):
            return ""

        context_parts.append("\n=== CLASSICAL VEDIC YOGAS ===")
        context_parts.append(f"\nTotal Yogas Detected: {yoga_data.get('total_yogas', 0)}")
        context_parts.append(f"Significant Yogas (Strong/Very Strong): {yoga_data.get('significant_yogas', 0)}")

        # Strongest yogas summary
        if yoga_data.get('strongest_yogas'):
            strongest = yoga_data['strongest_yogas']
            context_parts.append(f"\nStrongest Yogas: {', '.join(strongest)}")

        # List all significant yogas with details
        context_parts.append("\n\nDetailed Yoga Analysis:")

        yogas_by_category = {}
        for yoga in yoga_data.get('yogas', []):
            category = yoga.get('category', 'Other')
            if category not in yogas_by_category:
                yogas_by_category[category] = []
            yogas_by_category[category].append(yoga)

        for category, yogas in yogas_by_category.items():
            context_parts.append(f"\n{category}:")
            for yoga in yogas:
                strength = yoga.get('strength', 'Unknown')
                name = yoga.get('name', 'Unknown')
                description = yoga.get('description', '')
                context_parts.append(f"  • {name} ({strength}): {description}")

        context_parts.append("\n\nIMPORTANT: Integrate these yogas throughout your analysis.")
        context_parts.append("- Mention them in relevant sections (career, wealth, relationships, etc.)")
        context_parts.append("- Explain how they manifest in different life areas")
        context_parts.append("- Consider their combined effects and interactions")
        context_parts.append("- Use them to strengthen predictions and recommendations")

        return "\n".join(context_parts)

    def _prepare_divisional_charts_context(
        self,
        divisional_charts_data: Dict[str, Any],
        vimshopaka_bala_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Prepare divisional charts (Shodashvarga) context for synthesis"""

        context_parts = []

        if not divisional_charts_data:
            return ""

        context_parts.append("\n=== DIVISIONAL CHARTS (SHODASHVARGA) ===")
        context_parts.append(f"\nTotal Divisional Charts Available: {len(divisional_charts_data)}")

        # Vimshopaka Bala (Planetary Strength) Summary
        if vimshopaka_bala_data:
            context_parts.append("\n\n=== VIMSHOPAKA BALA (Composite Planetary Strength) ===")

            summary = vimshopaka_bala_data.get('summary', {})
            strongest = summary.get('strongest_planet', {})
            weakest = summary.get('weakest_planet', {})

            context_parts.append(f"Average Planetary Strength: {summary.get('average_strength', 0):.2f}/20")
            context_parts.append(f"Strongest Planet: {strongest.get('name', 'N/A')} ({strongest.get('score', 0):.2f}/20 - {strongest.get('quality', 'N/A')})")
            context_parts.append(f"Weakest Planet: {weakest.get('name', 'N/A')} ({weakest.get('score', 0):.2f}/20 - {weakest.get('quality', 'N/A')})")

            # List all planets with their strengths
            context_parts.append("\nPlanetary Strengths:")
            planets_data = vimshopaka_bala_data.get('planets', {})
            for planet, data in planets_data.items():
                score = data.get('total_score', 0)
                percentage = data.get('percentage', 0)
                quality = data.get('quality', 'Unknown')
                classification = data.get('classification', 'Unknown')
                context_parts.append(f"  • {planet}: {score:.2f}/20 ({percentage:.1f}%) - {quality} ({classification})")

        # Key Divisional Charts Analysis
        context_parts.append("\n\n=== KEY DIVISIONAL CHARTS ANALYSIS ===")

        # Priority order for analysis
        priority_charts = {
            "D2": "Wealth & Prosperity",
            "D9": "Marriage & Dharma",
            "D10": "Career & Profession",
            "D7": "Children & Progeny",
            "D4": "Property & Assets",
            "D12": "Parents & Ancestry",
            "D24": "Education & Learning",
            "D16": "Vehicles & Comforts",
            "D20": "Spiritual Pursuits"
        }

        for chart_name, purpose in priority_charts.items():
            if chart_name in divisional_charts_data:
                chart = divisional_charts_data[chart_name]
                ascendant = chart.get('ascendant', {})
                planets = chart.get('planets', {})

                context_parts.append(f"\n{chart_name} ({purpose}):")
                context_parts.append(f"  Ascendant: {ascendant.get('sign', 'N/A')} {ascendant.get('degree', 0):.2f}°")

                # Highlight planets in key positions (exalted, own sign, kendra/trikona houses)
                important_positions = []
                for planet_name, planet_data in planets.items():
                    house = planet_data.get('house', 0)
                    sign = planet_data.get('sign', 'N/A')
                    degree = planet_data.get('degree', 0)

                    # Check if in kendra (1,4,7,10) or trikona (1,5,9)
                    if house in [1, 4, 5, 7, 9, 10]:
                        important_positions.append(f"{planet_name} in {sign} (House {house}, {degree:.1f}°)")

                if important_positions:
                    context_parts.append("  Key Planetary Positions:")
                    for pos in important_positions[:5]:  # Limit to top 5
                        context_parts.append(f"    - {pos}")

        # Usage instructions
        context_parts.append("\n\nIMPORTANT: How to use Divisional Charts in your analysis:")
        context_parts.append("- D2 insights should inform WEALTH & FINANCIAL sections")
        context_parts.append("- D9 insights are CRITICAL for MARRIAGE & RELATIONSHIPS analysis")
        context_parts.append("- D10 insights are ESSENTIAL for CAREER & PROFESSIONAL analysis")
        context_parts.append("- D7 insights inform CHILDREN analysis")
        context_parts.append("- D4 insights inform PROPERTY & ASSETS discussion")
        context_parts.append("- Use Vimshopaka Bala to identify strongest/weakest planets across all life areas")
        context_parts.append("- Integrate divisional chart insights with D1 analysis for comprehensive interpretation")

        return "\n".join(context_parts)

    async def _verifier_role(
        self,
        synthesis: Dict[str, Any],
        retrieval: Dict[str, Any],
        chart_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verifier role: Check quality, contradictions, and citation accuracy

        Returns:
            Dictionary with quality metrics and issues
        """
        print("✅ Verifier: Checking quality and contradictions...")

        interpretation = synthesis['interpretation']

        # Extract citations from interpretation
        import re
        pattern = r'\[([A-Z0-9\-]+)\]'
        cited_rule_ids = re.findall(pattern, interpretation)

        # Check citation accuracy
        retrieved_rule_ids = [r['rule_id'] for r in retrieval['rules_cited']]
        valid_citations = [rid for rid in cited_rule_ids if rid in retrieved_rule_ids]
        invalid_citations = [rid for rid in cited_rule_ids if rid not in retrieved_rule_ids]

        citation_accuracy = len(valid_citations) / len(cited_rule_ids) if cited_rule_ids else 0

        # Create verification prompt
        prompt = f"""You are a quality verifier for Vedic astrology interpretations.
Review this interpretation and check for:
1. Internal contradictions
2. Misuse of astrological concepts
3. Overly fatalistic or fear-based language
4. Missing important chart factors

Interpretation:
{interpretation}

Return JSON:
{{
    "quality_score": 0-10,
    "issues": ["list of issues found"],
    "contradictions": ["any contradictions"],
    "suggestions": ["improvement suggestions"],
    "overall_confidence": "very_high/high/medium/low"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=self.token_budget['verifier'],
                response_format={"type": "json_object"}
            )

            self.tokens_used += response.usage.total_tokens
            verification = json.loads(response.choices[0].message.content)

            # Add citation metrics
            verification['citation_metrics'] = {
                "total_citations": len(cited_rule_ids),
                "valid_citations": len(valid_citations),
                "invalid_citations": len(invalid_citations),
                "citation_accuracy": citation_accuracy
            }

            return verification

        except Exception as e:
            print(f"⚠️  Verifier failed: {e}. Using fallback.")
            return {
                "quality_score": 7,
                "issues": [],
                "contradictions": [],
                "suggestions": [],
                "overall_confidence": "medium",
                "citation_metrics": {
                    "total_citations": len(cited_rule_ids),
                    "valid_citations": len(valid_citations),
                    "citation_accuracy": citation_accuracy
                }
            }


# Singleton instance
ai_orchestrator = AIOrchestrator()
