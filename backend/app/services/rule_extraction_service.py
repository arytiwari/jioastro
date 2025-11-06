"""
Rule Extraction Service
Automatically extracts astrological and numerological rules from knowledge documents
Uses GPT-4 to identify, structure, and store rules with embeddings
"""

import asyncio
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import AsyncOpenAI, AsyncAzureOpenAI

from app.core.config import settings
from app.services.supabase_service import supabase_service


class RuleExtractionService:
    """Extract structured rules from unstructured knowledge documents"""

    def __init__(self):
        """Initialize with OpenAI or Azure OpenAI client"""
        if settings.USE_AZURE_OPENAI:
            # Use Azure OpenAI
            self.client = AsyncAzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.model = settings.AZURE_OPENAI_DEPLOYMENT  # Azure uses deployment name
            self.embedding_model = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
            print(f"✅ Rule Extraction: Using Azure OpenAI (deployment: {self.model})")
        else:
            # Use standard OpenAI
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4o"  # Updated to gpt-4o (available model)
            self.embedding_model = "text-embedding-ada-002"
            print("✅ Rule Extraction: Using OpenAI")

    async def extract_rules_from_document(
        self,
        document_id: str,
        text: str,
        document_title: str,
        document_type: str
    ) -> Dict[str, Any]:
        """
        Extract all rules from a document's text.

        Args:
            document_id: UUID of the document
            text: Full text content of the document
            document_title: Title for source attribution
            document_type: Type (astrology, numerology, palmistry, etc.)

        Returns:
            Dictionary with extraction stats and results
        """
        print(f"\n🔍 Starting rule extraction for: {document_title}")
        print(f"   Document ID: {document_id}")
        print(f"   Text length: {len(text)} characters")

        start_time = datetime.utcnow()

        # Chunk the text for processing (GPT-4 has token limits)
        chunks = self._chunk_text_for_extraction(text, chunk_size=4000, overlap=500)
        print(f"   Created {len(chunks)} chunks for processing")

        all_rules = []
        tokens_used = 0

        # Process each chunk
        for i, chunk in enumerate(chunks, 1):
            print(f"\n   📄 Processing chunk {i}/{len(chunks)}...")

            try:
                extracted_rules = await self._extract_rules_from_chunk(
                    chunk=chunk,
                    document_title=document_title,
                    document_type=document_type,
                    chunk_index=i
                )

                if extracted_rules:
                    all_rules.extend(extracted_rules['rules'])
                    tokens_used += extracted_rules['tokens_used']
                    print(f"      ✅ Extracted {len(extracted_rules['rules'])} rules")
                else:
                    print(f"      ℹ️  No rules found in this chunk")

                # Rate limiting - small delay between chunks
                if i < len(chunks):
                    await asyncio.sleep(1)

            except Exception as e:
                print(f"      ❌ Error processing chunk {i}: {e}")
                continue

        print(f"\n   📊 Total rules extracted: {len(all_rules)}")

        # Deduplicate rules (same rule might appear in overlapping chunks)
        unique_rules = self._deduplicate_rules(all_rules)
        print(f"   🔄 After deduplication: {len(unique_rules)} unique rules")

        # Generate embeddings and store rules
        stored_count = 0
        failed_count = 0

        print(f"\n   💾 Storing rules in database...")

        for i, rule in enumerate(unique_rules, 1):
            if i % 5 == 0:
                print(f"      Processing rule {i}/{len(unique_rules)}...")

            try:
                # Generate embedding for the rule
                embedding = await self._generate_rule_embedding(rule)

                # Store in database
                await self._store_rule(
                    document_id=document_id,
                    rule=rule,
                    embedding=embedding,
                    document_title=document_title
                )

                stored_count += 1

                # Rate limiting for embeddings API
                if i % 10 == 0:
                    await asyncio.sleep(0.5)

            except Exception as e:
                print(f"      ❌ Error storing rule {i}: {e}")
                failed_count += 1

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        print(f"\n   ✅ Rule extraction complete!")
        print(f"      Stored: {stored_count} rules")
        print(f"      Failed: {failed_count} rules")
        print(f"      Time: {processing_time:.1f}s")
        print(f"      Tokens used: {tokens_used}")

        return {
            "success": True,
            "document_id": document_id,
            "rules_extracted": len(all_rules),
            "unique_rules": len(unique_rules),
            "rules_stored": stored_count,
            "rules_failed": failed_count,
            "tokens_used": tokens_used,
            "processing_time_seconds": processing_time
        }

    async def _extract_rules_from_chunk(
        self,
        chunk: str,
        document_title: str,
        document_type: str,
        chunk_index: int
    ) -> Optional[Dict[str, Any]]:
        """
        Use GPT-4 to extract structured rules from a text chunk.

        Returns:
            Dictionary with extracted rules and metadata
        """

        # Determine extraction prompt based on document type
        system_prompt = self._get_extraction_system_prompt(document_type)
        user_prompt = self._get_extraction_user_prompt(chunk, document_title)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=2000,
                response_format={"type": "json_object"}  # Force JSON output
            )

            result_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Parse JSON response
            result = json.loads(result_text)

            return {
                "rules": result.get("rules", []),
                "tokens_used": tokens_used
            }

        except json.JSONDecodeError as e:
            print(f"         ⚠️  Failed to parse JSON response: {e}")
            return None
        except Exception as e:
            print(f"         ⚠️  GPT-4 extraction error: {e}")
            return None

    def _get_extraction_system_prompt(self, document_type: str) -> str:
        """Get system prompt for rule extraction based on document type"""

        base_prompt = """You are an expert in extracting structured knowledge rules from {doc_type} texts.

Your task is to identify ALL rules, principles, and correlations in the text and extract them in a structured format.

For each rule you find, extract:
1. **condition**: The specific configuration, placement, or situation (e.g., "Mars in 10th house", "Life Path Number 5")
2. **effect**: The result, prediction, or interpretation
3. **domain**: Category (career, wealth, relationships, health, education, spirituality, personality, general)
4. **confidence**: Your confidence in this being a complete rule (high, medium, low)

IMPORTANT GUIDELINES:
- Extract EVERY rule you find, no matter how small
- Be comprehensive - don't skip rules
- Keep condition and effect separate
- Use clear, specific language
- For planetary rules: include house number and planet name
- For numerological rules: include the number and its meaning
- Domain should be one of: career, wealth, relationships, health, education, spirituality, personality, general

Return your response as a JSON object with this structure:
{{
  "rules": [
    {{
      "condition": "specific condition or configuration",
      "effect": "the result or prediction",
      "domain": "career|wealth|relationships|health|education|spirituality|personality|general",
      "confidence": "high|medium|low"
    }}
  ]
}}"""

        doc_type_map = {
            "astrology": "Vedic astrology",
            "numerology": "numerology and number science",
            "palmistry": "palmistry and hand reading",
            "text": "spiritual and occult science",
            "pdf": "esoteric knowledge",
            "article": "metaphysical wisdom"
        }

        doc_type_text = doc_type_map.get(document_type, "spiritual knowledge")
        return base_prompt.format(doc_type=doc_type_text)

    def _get_extraction_user_prompt(self, chunk: str, document_title: str) -> str:
        """Get user prompt with the text chunk to analyze"""

        return f"""Extract all rules from the following text from "{document_title}".

Remember to:
- Extract EVERY rule, principle, and correlation you find
- Be thorough and comprehensive
- Separate condition from effect
- Assign appropriate domain
- Rate your confidence

Text to analyze:

{chunk}

Return a JSON object with all extracted rules."""

    def _chunk_text_for_extraction(
        self,
        text: str,
        chunk_size: int = 4000,
        overlap: int = 500
    ) -> List[str]:
        """
        Split text into overlapping chunks for comprehensive extraction.
        Overlap ensures rules spanning chunk boundaries aren't missed.
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence ending in the last 200 chars
                last_period = text[end-200:end].rfind('.')
                if last_period != -1:
                    end = end - 200 + last_period + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap  # Overlap to catch rules spanning boundaries

        return chunks

    def _deduplicate_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate rules that may appear in overlapping chunks.
        Uses condition + effect hash for deduplication.
        """
        seen_hashes = set()
        unique_rules = []

        for rule in rules:
            # Create hash from condition and effect
            rule_text = f"{rule.get('condition', '')}|{rule.get('effect', '')}"
            rule_hash = hashlib.md5(rule_text.lower().encode()).hexdigest()

            if rule_hash not in seen_hashes:
                seen_hashes.add(rule_hash)
                unique_rules.append(rule)

        return unique_rules

    async def _generate_rule_embedding(self, rule: Dict[str, Any]) -> List[float]:
        """Generate OpenAI embedding for a rule"""

        # Combine condition and effect for embedding
        text_to_embed = f"{rule.get('condition', '')}. {rule.get('effect', '')}"

        try:
            # For text-embedding-3-large, specify dimensions=1536 to match database
            # Note: Azure OpenAI doesn't support dimensions parameter yet
            if settings.USE_AZURE_OPENAI:
                response = await self.client.embeddings.create(
                    model=self.embedding_model,
                    input=text_to_embed
                    # Azure: dimensions configured at deployment level
                )
            else:
                response = await self.client.embeddings.create(
                    model=self.embedding_model,
                    input=text_to_embed,
                    dimensions=1536  # OpenAI: force 1536 dimensions
                )

            return response.data[0].embedding

        except Exception as e:
            print(f"         ⚠️  Embedding generation error: {e}")
            return None

    async def _store_rule(
        self,
        document_id: str,
        rule: Dict[str, Any],
        embedding: Optional[List[float]],
        document_title: str
    ) -> bool:
        """Store extracted rule in knowledge_base table"""

        try:
            # Generate unique rule_id
            rule_text = f"{rule.get('condition')}|{rule.get('effect')}"
            rule_hash = hashlib.md5(rule_text.encode()).hexdigest()[:8]
            rule_id = f"{document_id[:8]}-{rule_hash}"

            # Prepare rule data
            rule_data = {
                "rule_id": rule_id,
                "document_id": document_id,
                "domain": rule.get("domain", "general"),
                "condition": rule.get("condition", ""),
                "effect": rule.get("effect", ""),
                "anchor": f"{document_title}",
                "commentary": f"Confidence: {rule.get('confidence', 'medium')}",
                "weight": self._confidence_to_weight(rule.get("confidence", "medium")),
                "embedding": embedding
            }

            # Insert into database
            response = supabase_service.client.table("knowledge_base")\
                .upsert(rule_data, on_conflict="rule_id")\
                .execute()

            return True

        except Exception as e:
            print(f"         ⚠️  Database insert error: {e}")
            return False

    def _confidence_to_weight(self, confidence: str) -> float:
        """Convert confidence level to numeric weight"""
        confidence_map = {
            "high": 0.95,
            "medium": 0.80,
            "low": 0.60
        }
        return confidence_map.get(confidence.lower(), 0.80)


# Singleton instance
rule_extraction_service = RuleExtractionService()
