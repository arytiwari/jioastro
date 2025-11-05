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

        # Token budget tracking
        self.token_budget = {
            "max_total": 8000,  # Maximum tokens per reading
            "coordinator": 500,
            "retriever": 0,  # No LLM call, uses vector search
            "synthesizer": 3000,
            "verifier": 1500,
            "predictor": 2000
        }
        self.tokens_used = 0

    async def generate_comprehensive_reading(
        self,
        chart_data: Dict[str, Any],
        query: Optional[str] = None,
        domains: Optional[List[str]] = None,
        include_predictions: bool = True,
        include_transits: bool = False,
        prediction_window_months: int = 12
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

        Returns:
            Dictionary with comprehensive reading, predictions, citations, and metadata
        """
        print("🎭 Starting Multi-Role Orchestration...")
        self.tokens_used = 0

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
            predictions=prediction_results
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
        predictions: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesizer role: Combine all information into comprehensive interpretation

        Returns:
            Dictionary with synthesized interpretation and domain analyses
        """
        print("✍️  Synthesizer: Combining all information...")

        # Prepare chart context
        chart_context = self._prepare_chart_context(chart_data)

        # Prepare rules context
        rules_context = self._format_rules_for_synthesis(retrieval['by_domain'])

        # Prepare predictions context
        predictions_context = ""
        if predictions and predictions.get('predictions'):
            predictions_context = "\n\n--- TIME-BASED PREDICTIONS ---\n"
            for pred in predictions['predictions']:
                predictions_context += f"\n{pred['domain'].upper()}: {pred.get('prediction_summary', '')}"
                predictions_context += f"\nConfidence: {pred.get('confidence_score', 0)}%"

        # Create synthesis prompt
        system_prompt = """You are an expert Vedic astrology synthesizer.
Your role is to combine chart data, scriptural rules, and predictions into a comprehensive, personalized interpretation.

Guidelines:
- Synthesize information from multiple sources
- CITE rules using [RULE-ID] format
- Be specific about planetary positions and their effects
- Include time-based predictions if provided
- Maintain warm, empowering tone
- Organize by domain if analyzing multiple areas
- End with practical remedies"""

        user_prompt = f"""
{chart_context}

{rules_context}

{predictions_context}

Query: {query or "Provide a comprehensive life reading"}
Domains to Analyze: {', '.join(coordination['domains_to_analyze'])}

Create a comprehensive interpretation that:
1. Addresses the query directly
2. Analyzes each requested domain
3. Cites scriptural rules using [RULE-ID]
4. Includes predictions with timeframes if available
5. Provides practical guidance
6. Suggests appropriate remedies

Format the response in clear sections for each domain.
Length: 400-600 words total.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=self.token_budget['synthesizer']
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
