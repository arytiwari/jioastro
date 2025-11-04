"""
Ingest Comprehensive BPHS Rules
Ingests 120 comprehensive rules with embeddings
"""

import asyncio
import sys
import json
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.knowledge_base import knowledge_base_service
from app.schemas.knowledge_base import RuleIngestionBatch


async def main():
    print("="*70)
    print("COMPREHENSIVE BPHS RULES INGESTION")
    print("="*70)

    # Load comprehensive rules
    rules_file = Path(__file__).parent.parent / "data" / "bphs_rules_comprehensive.json"

    print(f"\n📂 Loading rules from: {rules_file}")

    with open(rules_file, 'r') as f:
        data = json.load(f)

    rules = data['rules']
    metadata = data['metadata']

    print(f"\n📊 Dataset Information:")
    print(f"   Version: {metadata['version']}")
    print(f"   Total Rules: {metadata['rule_count']}")
    print(f"   Coverage:")
    for category, count in metadata['coverage'].items():
        print(f"      - {category.replace('_', ' ').title()}: {count}")

    # Fetch BPHS source_id
    print(f"\n🔍 Fetching BPHS source ID...")
    sources_query = knowledge_base_service.db.client.from_("kb_sources")\
        .select("id")\
        .eq("title", "Brihat Parashara Hora Shastra")\
        .execute()

    if not sources_query.data:
        print("❌ BPHS source not found in database. Please run source initialization first.")
        return

    bphs_source_id = sources_query.data[0]['id']
    print(f"✅ Found BPHS source: {bphs_source_id}")

    # Add source_id to all rules
    for rule in rules:
        rule['source_id'] = bphs_source_id

    # Prepare batch
    batch = RuleIngestionBatch(
        rules=rules,
        generate_embeddings=True,  # Azure OpenAI embeddings
        batch_size=10
    )

    print(f"\n🚀 Starting ingestion...")
    print(f"   Generate Embeddings: Yes (Azure OpenAI)")
    print(f"   Batch Size: 10 rules at a time")

    start_time = time.time()

    # Ingest batch
    try:
        result = await knowledge_base_service.ingest_batch(batch)

        duration = time.time() - start_time

        print(f"\n" + "="*70)
        print("INGESTION RESULTS")
        print("="*70)

        print(f"\n✅ Successfully Ingested: {result.ingested_count} rules")
        print(f"🔑 Symbolic Keys Extracted: {result.symbolic_keys_generated}")
        print(f"📊 Embeddings Generated: {result.embeddings_generated}")
        print(f"⏱️  Duration: {result.duration_seconds:.2f} seconds")
        print(f"📈 Rate: {result.ingested_count / result.duration_seconds:.2f} rules/second")

        if result.errors:
            print(f"\n⚠️  Errors encountered:")
            for error in result.errors[:5]:  # Show first 5 errors
                print(f"   - {error}")

        # Verification queries
        print(f"\n" + "="*70)
        print("VERIFICATION")
        print("="*70)

        # Count rules by domain
        print(f"\n📂 Rules by Domain:")
        domains = ["career", "wealth", "relationships", "health", "education", "spirituality", "general"]
        for domain in domains:
            rules = await knowledge_base_service.get_rules_by_domain(domain, limit=1000)
            print(f"   {domain.capitalize()}: {len(rules)} rules")

        # Total rule count
        total_rules = await knowledge_base_service.count_rules()
        print(f"\n📊 Total Rules in Database: {total_rules}")

        # Sample symbolic keys
        print(f"\n🔑 Sample Symbolic Keys:")
        sample_keys_query = knowledge_base_service.db.client.from_("kb_symbolic_keys")\
            .select("key_type, key_value")\
            .limit(15)\
            .execute()

        if sample_keys_query.data:
            key_types = {}
            for key_data in sample_keys_query.data:
                key_type = key_data['key_type']
                key_value = key_data['key_value']
                if key_type not in key_types:
                    key_types[key_type] = []
                key_types[key_type].append(key_value)

            for key_type, values in key_types.items():
                print(f"   {key_type}: {', '.join(values[:3])}")

        # Sample rules
        print(f"\n📚 Sample Ingested Rules:")
        sample_rules = await knowledge_base_service.get_rules_by_domain("career", limit=3)
        for i, rule in enumerate(sample_rules[:3], 1):
            print(f"\n   {i}. {rule['rule_id']} (weight: {rule['weight']})")
            print(f"      Domain: {rule['domain']}")
            print(f"      Condition: {rule['condition'][:60]}...")
            print(f"      Effect: {rule['effect'][:60]}...")

        print(f"\n" + "="*70)
        print("✅ INGESTION COMPLETE!")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Ingestion failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
