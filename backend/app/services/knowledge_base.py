"""Knowledge Base Service - Rule Ingestion and Management"""

import openai
import hashlib
import time
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime

from app.core.config import settings
from app.services.supabase_service import supabase_service
from app.schemas.knowledge_base import (
    RuleCreate,
    RuleResponse,
    RuleIngestionBatch,
    RuleIngestionResponse,
    SymbolicKey
)


class KnowledgeBaseService:
    """Service for managing the knowledge base of astrological rules"""

    def __init__(self):
        self.db = supabase_service

        # Initialize OpenAI client based on configuration
        try:
            if settings.USE_AZURE_OPENAI:
                self.openai_client = openai.AzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    timeout=10.0,  # Add timeout to prevent hanging
                    max_retries=2
                )
                self.embedding_model = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT  # Azure embedding deployment
                print(f"✅ Using Azure OpenAI Embeddings (deployment: {self.embedding_model})")
            else:
                self.openai_client = openai.OpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    timeout=10.0,
                    max_retries=2
                )
                self.embedding_model = "text-embedding-ada-002"
                print("✅ Using OpenAI Embeddings")

            self.embedding_dimensions = 1536
        except Exception as e:
            print(f"⚠️ Error initializing OpenAI client: {str(e)}")
            print("⚠️ Embeddings will not be available")
            self.openai_client = None
            self.embedding_model = None
            self.embedding_dimensions = 1536

    # =========================================================================
    # RULE INGESTION
    # =========================================================================

    async def ingest_rule(
        self,
        rule: RuleCreate,
        generate_embedding: bool = True,
        extract_keys: bool = True
    ) -> UUID:
        """
        Ingest a single rule into the knowledge base

        Args:
            rule: Rule data to ingest
            generate_embedding: Generate OpenAI embedding
            extract_keys: Extract symbolic keys

        Returns:
            UUID of the ingested rule

        Process:
            1. Validate rule data
            2. Store in kb_rules table
            3. Generate and store embedding (if requested)
            4. Extract and store symbolic keys (if requested)
        """
        try:
            # Prepare rule data for insertion
            rule_data = {
                "rule_id": rule.rule_id,
                "source_id": str(rule.source_id),
                "domain": rule.domain,
                "chart_context": rule.chart_context,
                "scope": rule.scope,
                "condition": rule.condition,
                "effect": rule.effect,
                "modifiers": rule.modifiers,
                "weight": rule.weight,
                "anchor": rule.anchor,
                "sanskrit_text": rule.sanskrit_text,
                "translation": rule.translation,
                "commentary": rule.commentary,
                "applicable_vargas": rule.applicable_vargas,
                "requires_yoga": rule.requires_yoga,
                "cancelers": rule.cancelers,
                "version": rule.version,
                "status": rule.status
            }

            # Insert into kb_rules
            response = self.db.client.table("kb_rules").insert(rule_data).execute()

            if not response.data or len(response.data) == 0:
                raise Exception("Failed to insert rule")

            rule_id = UUID(response.data[0]["id"])
            print(f"✅ Rule ingested: {rule.rule_id} (UUID: {rule_id})")

            # Generate embedding if requested
            if generate_embedding:
                await self._generate_and_store_embedding(rule_id, rule)

            # Extract symbolic keys if requested
            if extract_keys:
                await self._extract_and_store_symbolic_keys(rule_id, rule)

            return rule_id

        except Exception as e:
            print(f"❌ Error ingesting rule {rule.rule_id}: {str(e)}")
            raise

    async def ingest_batch(
        self,
        batch: RuleIngestionBatch
    ) -> RuleIngestionResponse:
        """
        Batch ingest multiple rules

        Args:
            batch: Batch of rules to ingest

        Returns:
            Ingestion response with statistics
        """
        start_time = time.time()
        ingested_ids = []
        errors = []
        embeddings_count = 0
        symbolic_keys_count = 0

        for rule in batch.rules:
            try:
                rule_id = await self.ingest_rule(
                    rule,
                    generate_embedding=batch.generate_embeddings,
                    extract_keys=batch.extract_symbolic_keys
                )
                ingested_ids.append(rule_id)

                if batch.generate_embeddings:
                    embeddings_count += 1

                if batch.extract_symbolic_keys:
                    # Count symbolic keys for this rule
                    keys = await self._extract_symbolic_keys_from_rule(rule)
                    symbolic_keys_count += len(keys)

            except Exception as e:
                errors.append(f"{rule.rule_id}: {str(e)}")

        duration = time.time() - start_time

        return RuleIngestionResponse(
            ingested_count=len(ingested_ids),
            rule_ids=ingested_ids,
            embeddings_generated=embeddings_count,
            symbolic_keys_generated=symbolic_keys_count,
            errors=errors,
            duration_seconds=duration
        )

    # =========================================================================
    # EMBEDDING GENERATION
    # =========================================================================

    async def _generate_and_store_embedding(
        self,
        rule_id: UUID,
        rule: RuleCreate
    ) -> None:
        """Generate OpenAI embedding and store it"""
        try:
            # Create embedding text from rule
            embedding_text = self._create_embedding_text(rule)

            # Generate embedding
            embedding = await self._generate_embedding(embedding_text)

            # Store embedding
            embedding_data = {
                "rule_id": str(rule_id),
                "embedding": embedding,
                "model_version": self.embedding_model
            }

            response = self.db.client.table("kb_rule_embeddings").insert(embedding_data).execute()

            if response.data and len(response.data) > 0:
                print(f"  ✅ Embedding generated for {rule.rule_id}")
            else:
                print(f"  ⚠️  Warning: Embedding insert returned no data for {rule.rule_id}")

        except Exception as e:
            print(f"  ❌ Error generating embedding for {rule.rule_id}: {str(e)}")
            raise

    def _create_embedding_text(self, rule: RuleCreate) -> str:
        """
        Create text for embedding generation

        Combines all relevant rule information into a single text
        that captures the semantic meaning for vector search
        """
        parts = [
            f"Domain: {rule.domain}",
            f"Context: {rule.chart_context}",
            f"Condition: {rule.condition}",
            f"Effect: {rule.effect}"
        ]

        if rule.translation:
            parts.append(f"Translation: {rule.translation}")

        if rule.commentary:
            parts.append(f"Commentary: {rule.commentary}")

        if rule.modifiers:
            parts.append(f"Modifiers: {', '.join(rule.modifiers)}")

        return " | ".join(parts)

    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate OpenAI embedding for text

        Args:
            text: Text to embed

        Returns:
            List of floats (1536 dimensions for ada-002)
        """
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding

        except Exception as e:
            print(f"❌ OpenAI embedding error: {str(e)}")
            raise

    # =========================================================================
    # SYMBOLIC KEY EXTRACTION
    # =========================================================================

    async def _extract_and_store_symbolic_keys(
        self,
        rule_id: UUID,
        rule: RuleCreate
    ) -> None:
        """Extract symbolic keys from rule and store them"""
        try:
            keys = await self._extract_symbolic_keys_from_rule(rule)

            # Store all keys
            for key_type, key_value in keys:
                key_data = {
                    "rule_id": str(rule_id),
                    "key_type": key_type,
                    "key_value": key_value
                }

                self.db.client.table("kb_symbolic_keys").insert(key_data).execute()

            print(f"  ✅ {len(keys)} symbolic keys extracted for {rule.rule_id}")

        except Exception as e:
            print(f"  ❌ Error extracting symbolic keys for {rule.rule_id}: {str(e)}")
            raise

    async def _extract_symbolic_keys_from_rule(
        self,
        rule: RuleCreate
    ) -> List[tuple[str, str]]:
        """
        Extract symbolic keys from rule content

        Returns list of (key_type, key_value) tuples

        Key Types:
            - planet_house: "Sun_10"
            - planet_sign: "Mars_Aries"
            - planet_house_sign: "Jupiter_5_Leo"
            - house_lord: "10_lord_in_4"
            - yoga: "Gaja_Kesari"
            - domain: "career_success"
        """
        keys = []

        # Add domain key
        keys.append(("domain", rule.domain))

        # Extract from condition
        condition = rule.condition.lower()

        # Extract planet-house patterns: "sun in 10th house"
        import re

        planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
        for planet in planets:
            # Pattern: "planet in Nth house"
            pattern = rf"{planet}\s+in\s+(\d+)(?:st|nd|rd|th)?\s+house"
            matches = re.findall(pattern, condition)
            for house_num in matches:
                keys.append(("planet_house", f"{planet.capitalize()}_{house_num}"))

        # Extract house lord patterns: "10th lord in 4th house"
        pattern = r"(\d+)(?:st|nd|rd|th)?\s+lord\s+in\s+(\d+)(?:st|nd|rd|th)?\s+house"
        matches = re.findall(pattern, condition)
        for source_house, target_house in matches:
            keys.append(("house_lord", f"{source_house}_lord_in_{target_house}"))

        # Extract sign patterns: "planet in sign"
        signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo",
                 "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]

        for planet in planets:
            for sign in signs:
                if f"{planet} in {sign}" in condition or f"{planet} occupies {sign}" in condition:
                    keys.append(("planet_sign", f"{planet.capitalize()}_{sign.capitalize()}"))

        # Extract yoga patterns
        yogas = ["gaja kesari", "raj yoga", "dhana yoga", "budhaditya", "viparita"]
        for yoga in yogas:
            if yoga in condition.lower() or yoga in rule.effect.lower():
                yoga_key = yoga.replace(" ", "_")
                keys.append(("yoga", yoga_key))

        # Add scope-based keys
        keys.append(("scope", rule.scope))

        return keys

    # =========================================================================
    # RULE QUERIES
    # =========================================================================

    async def get_rule(self, rule_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a single rule by UUID"""
        try:
            response = self.db.client.table("kb_rules")\
                .select("*")\
                .eq("id", str(rule_id))\
                .execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None

        except Exception as e:
            print(f"❌ Error getting rule: {str(e)}")
            return None

    async def get_rules_by_domain(
        self,
        domain: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get rules by domain"""
        try:
            response = self.db.client.table("kb_rules")\
                .select("*")\
                .eq("domain", domain)\
                .eq("status", "active")\
                .order("weight", desc=True)\
                .limit(limit)\
                .execute()

            return response.data if response.data else []

        except Exception as e:
            print(f"❌ Error getting rules by domain: {str(e)}")
            return []

    async def count_rules(self) -> Dict[str, int]:
        """Get statistics about rules in the knowledge base"""
        try:
            # Total rules
            total_response = self.db.client.table("kb_rules").select("id", count="exact").execute()
            total = total_response.count if hasattr(total_response, 'count') else len(total_response.data)

            # Rules with embeddings
            embeddings_response = self.db.client.table("kb_rule_embeddings").select("id", count="exact").execute()
            embeddings = embeddings_response.count if hasattr(embeddings_response, 'count') else len(embeddings_response.data)

            # Symbolic keys
            keys_response = self.db.client.table("kb_symbolic_keys").select("id", count="exact").execute()
            keys = keys_response.count if hasattr(keys_response, 'count') else len(keys_response.data)

            return {
                "total_rules": total,
                "rules_with_embeddings": embeddings,
                "symbolic_keys": keys
            }

        except Exception as e:
            print(f"❌ Error counting rules: {str(e)}")
            return {"total_rules": 0, "rules_with_embeddings": 0, "symbolic_keys": 0}


# Global instance
knowledge_base_service = KnowledgeBaseService()
