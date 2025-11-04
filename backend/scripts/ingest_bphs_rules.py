"""
BPHS Rule Ingestion Script

This script ingests foundational rules from Brihat Parashara Hora Shastra
into the knowledge base with embeddings and symbolic keys.

Usage:
    python scripts/ingest_bphs_rules.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.knowledge_base import knowledge_base_service
from app.schemas.knowledge_base import RuleCreate, RuleIngestionBatch
from app.services.supabase_service import supabase_service


async def get_bphs_source_id() -> str:
    """Get the UUID of BPHS source from kb_sources table"""
    try:
        response = supabase_service.client.table("kb_sources")\
            .select("id")\
            .eq("title", "Brihat Parashara Hora Shastra")\
            .execute()

        if not response.data or len(response.data) == 0:
            raise Exception("BPHS source not found in kb_sources table. Run migration first.")

        source_id = response.data[0]["id"]
        print(f"✅ Found BPHS source: {source_id}")
        return source_id

    except Exception as e:
        print(f"❌ Error getting BPHS source: {str(e)}")
        raise


async def load_rules_from_json(file_path: str, source_id: str) -> list[RuleCreate]:
    """Load rules from JSON file and convert to RuleCreate objects"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        rules = []
        for rule_data in data.get("rules", []):
            # Add source_id to each rule
            rule_data["source_id"] = source_id

            # Handle optional fields with defaults
            rule_data.setdefault("modifiers", [])
            rule_data.setdefault("weight", 0.5)
            rule_data.setdefault("applicable_vargas", ["D1"])
            rule_data.setdefault("cancelers", [])
            rule_data.setdefault("version", 1)
            rule_data.setdefault("status", "active")

            # Create RuleCreate object
            rule = RuleCreate(**rule_data)
            rules.append(rule)

        print(f"✅ Loaded {len(rules)} rules from {file_path}")
        return rules

    except Exception as e:
        print(f"❌ Error loading rules from JSON: {str(e)}")
        raise


async def verify_ingestion():
    """Verify rules were ingested correctly"""
    try:
        print("\n" + "="*60)
        print("VERIFICATION")
        print("="*60)

        # Get statistics
        stats = await knowledge_base_service.count_rules()

        print(f"\n📊 Knowledge Base Statistics:")
        print(f"   Total Rules: {stats['total_rules']}")
        print(f"   Rules with Embeddings: {stats['rules_with_embeddings']}")
        print(f"   Symbolic Keys: {stats['symbolic_keys']}")

        # Get sample rules by domain
        print(f"\n📚 Sample Rules by Domain:")

        domains = ["career", "wealth", "relationships", "health", "education", "spirituality"]
        for domain in domains:
            rules = await knowledge_base_service.get_rules_by_domain(domain, limit=3)
            if rules:
                print(f"\n   {domain.upper()}: {len(rules)} rules")
                for rule in rules[:2]:  # Show first 2
                    print(f"      • {rule['rule_id']}: {rule['condition'][:50]}...")

        print("\n✅ Verification complete!")

    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        raise


async def main():
    """Main ingestion process"""
    print("="*60)
    print("BPHS RULE INGESTION")
    print("="*60)
    print()

    try:
        # Step 1: Get BPHS source ID
        print("Step 1: Getting BPHS source ID...")
        source_id = await get_bphs_source_id()
        print()

        # Step 2: Load rules from JSON
        print("Step 2: Loading rules from JSON...")
        json_path = Path(__file__).parent.parent / "data" / "bphs_rules_sample.json"
        rules = await load_rules_from_json(str(json_path), source_id)
        print()

        # Step 3: Create ingestion batch
        print("Step 3: Creating ingestion batch...")
        batch = RuleIngestionBatch(
            rules=rules,
            generate_embeddings=True,
            extract_symbolic_keys=True
        )
        print(f"✅ Batch created with {len(batch.rules)} rules")
        print()

        # Step 4: Ingest batch
        print("Step 4: Ingesting rules (this may take a minute)...")
        print("-" * 60)
        response = await knowledge_base_service.ingest_batch(batch)
        print("-" * 60)
        print()

        # Step 5: Display results
        print("="*60)
        print("INGESTION RESULTS")
        print("="*60)
        print(f"\n✅ Successfully ingested: {response.ingested_count} rules")
        print(f"✅ Embeddings generated: {response.embeddings_generated}")
        print(f"✅ Symbolic keys created: {response.symbolic_keys_generated}")
        print(f"⏱️  Duration: {response.duration_seconds:.2f} seconds")

        if response.errors:
            print(f"\n⚠️  Errors encountered: {len(response.errors)}")
            for error in response.errors:
                print(f"   • {error}")
        else:
            print(f"\n✅ No errors!")

        # Step 6: Verify ingestion
        await verify_ingestion()

        print("\n" + "="*60)
        print("✅ INGESTION COMPLETE!")
        print("="*60)
        print()

    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
