"""Rule Retrieval Service - RAG with Hybrid Search

This service retrieves astrological rules using a hybrid approach:
1. Symbolic key exact matches (fast lookup for clear patterns)
2. Semantic similarity search (for nuanced natural language queries)
3. Reranking by relevance and weight
4. Conflict resolution
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from app.services.supabase_service import supabase_service
from app.services.knowledge_base import knowledge_base_service


class RuleRetrievalService:
    """Service for retrieving astrological rules using hybrid RAG"""

    def __init__(self):
        self.db = supabase_service
        self.kb = knowledge_base_service

    # =========================================================================
    # MAIN RETRIEVAL
    # =========================================================================

    async def retrieve_rules(
        self,
        chart_data: Dict[str, Any],
        query: Optional[str] = None,
        domain: Optional[str] = None,
        limit: int = 10,
        min_weight: float = 0.3
    ) -> Dict[str, Any]:
        """
        Hybrid rule retrieval combining symbolic and semantic search

        Args:
            chart_data: Birth chart data with planetary positions
            query: Optional natural language query
            domain: Optional domain filter (career, wealth, etc.)
            limit: Maximum rules to return
            min_weight: Minimum rule weight threshold

        Returns:
            Dictionary with rules, method used, and metadata
        """
        start_time = time.time()

        # Extract symbolic keys from chart data
        symbolic_keys = self._extract_chart_symbolic_keys(chart_data)

        # Retrieve rules using hybrid approach
        if query and self.kb.openai_client:
            # Hybrid: symbolic + semantic
            rules = await self._hybrid_search(
                symbolic_keys=symbolic_keys,
                query=query,
                domain=domain,
                limit=limit * 2  # Get more for reranking
            )
            method = "hybrid"
        elif symbolic_keys:
            # Symbolic only
            rules = await self._symbolic_search(
                symbolic_keys=symbolic_keys,
                domain=domain,
                limit=limit
            )
            method = "symbolic"
        else:
            # Fallback to domain-based
            rules = await self._domain_search(domain or "general", limit=limit)
            method = "domain"

        # Filter by weight
        rules = [r for r in rules if r.get('weight', 0) >= min_weight]

        # Resolve conflicts
        rules = await self._resolve_conflicts(rules)

        # Limit results
        rules = rules[:limit]

        query_time = (time.time() - start_time) * 1000  # Convert to ms

        return {
            "rules": rules,
            "retrieval_method": method,
            "total_matches": len(rules),
            "query_time_ms": round(query_time, 2),
            "symbolic_keys_used": symbolic_keys[:10]  # Show first 10 keys
        }

    # =========================================================================
    # SYMBOLIC KEY EXTRACTION FROM CHART
    # =========================================================================

    def _extract_chart_symbolic_keys(self, chart_data: Dict[str, Any]) -> List[str]:
        """
        Extract symbolic keys from birth chart data

        Keys extracted:
        - planet_house: "Sun_10", "Moon_4"
        - planet_sign: "Mars_Aries", "Venus_Taurus"
        - house_lord: "10_lord_in_4" (requires house lords calculation)
        """
        keys = []

        planets = chart_data.get('planets', {})

        # Extract planet-house and planet-sign keys
        for planet_name, planet_data in planets.items():
            house = planet_data.get('house')
            sign = planet_data.get('sign')

            if house:
                keys.append(f"{planet_name}_{house}")

            if sign:
                keys.append(f"{planet_name}_{sign}")

        # TODO: Extract house lord keys (requires house lord calculation)
        # This would need the ascendant and house cusp data

        # Add general domain keys
        keys.extend(["career", "wealth", "relationships", "health", "general"])

        return keys

    # =========================================================================
    # SYMBOLIC SEARCH
    # =========================================================================

    async def _symbolic_search(
        self,
        symbolic_keys: List[str],
        domain: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Fast exact match search using symbolic keys

        Uses PostgreSQL to find rules with matching symbolic keys
        """
        try:
            # Build query
            query = self.db.client.from_("kb_symbolic_keys")\
                .select("rule_id")\
                .in_("key_value", symbolic_keys)

            response = query.execute()

            if not response.data:
                return []

            # Get unique rule IDs
            rule_ids = list(set([item['rule_id'] for item in response.data]))

            # Fetch full rules
            rules_query = self.db.client.from_("kb_rules")\
                .select("*")\
                .in_("id", rule_ids)\
                .eq("status", "active")

            if domain:
                rules_query = rules_query.eq("domain", domain)

            rules_query = rules_query.order("weight", desc=True).limit(limit)

            rules_response = rules_query.execute()

            return rules_response.data if rules_response.data else []

        except Exception as e:
            print(f"❌ Symbolic search error: {str(e)}")
            return []

    # =========================================================================
    # SEMANTIC SEARCH
    # =========================================================================

    async def _semantic_search(
        self,
        query: str,
        domain: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Vector similarity search using embeddings

        Uses pgvector to find semantically similar rules
        """
        try:
            # Generate query embedding
            query_embedding = await self.kb._generate_embedding(query)

            # Use Supabase RPC function for vector similarity
            # Note: This requires a PostgreSQL function to be created
            # For now, we'll fetch all embeddings and calculate similarity in Python

            # Fetch all rule embeddings
            embeddings_response = self.db.client.from_("kb_rule_embeddings")\
                .select("rule_id, embedding")\
                .execute()

            if not embeddings_response.data:
                return []

            # Calculate cosine similarity
            similarities = []
            for emb_data in embeddings_response.data:
                rule_embedding = emb_data['embedding']

                # Ensure embedding is a list of floats
                if isinstance(rule_embedding, str):
                    import json
                    rule_embedding = json.loads(rule_embedding)
                elif not isinstance(rule_embedding, list):
                    rule_embedding = list(rule_embedding)

                similarity = self._cosine_similarity(query_embedding, rule_embedding)
                similarities.append({
                    'rule_id': emb_data['rule_id'],
                    'similarity': similarity
                })

            # Sort by similarity
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            top_rule_ids = [s['rule_id'] for s in similarities[:limit]]

            # Fetch full rules
            rules_query = self.db.client.from_("kb_rules")\
                .select("*")\
                .in_("id", top_rule_ids)\
                .eq("status", "active")

            if domain:
                rules_query = rules_query.eq("domain", domain)

            rules_response = rules_query.execute()

            # Add similarity scores to rules
            rules = rules_response.data if rules_response.data else []
            similarity_map = {s['rule_id']: s['similarity'] for s in similarities}

            for rule in rules:
                rule['semantic_score'] = similarity_map.get(rule['id'], 0.0)

            # Sort by semantic score
            rules.sort(key=lambda x: x.get('semantic_score', 0), reverse=True)

            return rules

        except Exception as e:
            print(f"❌ Semantic search error: {str(e)}")
            return []

    # =========================================================================
    # HYBRID SEARCH
    # =========================================================================

    async def _hybrid_search(
        self,
        symbolic_keys: List[str],
        query: str,
        domain: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining symbolic and semantic results

        Strategy:
        1. Get symbolic matches (fast, high precision)
        2. Get semantic matches (broader coverage)
        3. Merge and rerank by combined score
        """
        # Get both result sets
        symbolic_rules = await self._symbolic_search(symbolic_keys, domain, limit=limit)
        semantic_rules = await self._semantic_search(query, domain, limit=limit)

        # Create combined set with deduplication
        rule_map = {}

        # Add symbolic rules with symbolic score
        for rule in symbolic_rules:
            rule_id = rule['id']
            rule['symbolic_match'] = True
            rule['semantic_score'] = 0.0
            rule_map[rule_id] = rule

        # Add/merge semantic rules
        for rule in semantic_rules:
            rule_id = rule['id']
            semantic_score = rule.get('semantic_score', 0.0)

            if rule_id in rule_map:
                # Rule found in both - update scores
                rule_map[rule_id]['semantic_score'] = semantic_score
            else:
                # New rule from semantic search
                rule['symbolic_match'] = False
                rule_map[rule_id] = rule

        # Calculate combined relevance score
        rules = list(rule_map.values())
        for rule in rules:
            symbolic_boost = 0.3 if rule['symbolic_match'] else 0.0
            semantic_score = rule.get('semantic_score', 0.0)
            weight = rule.get('weight', 0.5)

            # Combined score: symbolic boost + semantic score + rule weight
            rule['relevance_score'] = (symbolic_boost * 0.4) + (semantic_score * 0.4) + (weight * 0.2)

        # Sort by relevance score
        rules.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return rules[:limit]

    # =========================================================================
    # DOMAIN SEARCH (FALLBACK)
    # =========================================================================

    async def _domain_search(self, domain: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fallback: retrieve top rules for a domain"""
        return await self.kb.get_rules_by_domain(domain, limit=limit)

    # =========================================================================
    # CONFLICT RESOLUTION
    # =========================================================================

    async def _resolve_conflicts(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Resolve contradicting rules

        Strategy:
        1. Check for rules with cancelers
        2. Remove cancelled rules
        3. Prioritize by weight
        """
        # Build map of rule_id to rule
        rule_map = {rule['rule_id']: rule for rule in rules}

        # Find rules that cancel others
        cancelled_ids = set()
        for rule in rules:
            cancelers = rule.get('cancelers', [])
            if cancelers:
                for cancelled_id in cancelers:
                    if cancelled_id in rule_map:
                        cancelled_ids.add(cancelled_id)

        # Filter out cancelled rules
        rules = [r for r in rules if r['rule_id'] not in cancelled_ids]

        return rules

    # =========================================================================
    # UTILITY FUNCTIONS
    # =========================================================================

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


# Global instance
rule_retrieval_service = RuleRetrievalService()
