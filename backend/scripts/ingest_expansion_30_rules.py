"""Ingest 30 expansion rules - House lords, Aspects, D9, D10"""

import asyncio
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.knowledge_base import knowledge_base_service
from app.schemas.knowledge_base import RuleIngestionBatch


async def ingest_expansion_rules():
    """Ingest 30 new rules focusing on house lords, aspects, and varga charts"""

    print("\n" + "="*70)
    print("INGESTING 30 EXPANSION RULES")
    print("="*70)

    # Load rules from JSON
    json_path = Path(__file__).parent.parent / "data" / "bphs_rules_expansion_30.json"

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rules = data['rules']

    print(f"\n📚 Loaded {len(rules)} expansion rules from JSON")
    print(f"   Coverage:")
    for key, value in data['metadata']['coverage'].items():
        print(f"   - {key}: {value}")

    # Fetch BPHS source_id
    print(f"\n🔍 Fetching BPHS source ID...")
    sources_query = knowledge_base_service.db.client.from_("kb_sources")\
        .select("id")\
        .eq("title", "Brihat Parashara Hora Shastra")\
        .execute()

    if not sources_query.data:
        print("❌ BPHS source not found in database.")
        print("   Please ensure BPHS source exists in kb_sources table")
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
            for error in result.errors[:10]:  # Show first 10 errors
                print(f"   - {error}")

    except Exception as e:
        print(f"\n❌ Ingestion failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    # Get updated statistics
    print("\n📊 Fetching updated knowledge base statistics...")
    counts = await knowledge_base_service.count_rules()

    print(f"\n📈 FINAL KNOWLEDGE BASE STATUS:")
    print(f"   Total rules: {counts.get('total_rules', 0)}")
    print(f"   Rules with embeddings: {counts.get('rules_with_embeddings', 0)}")
    print(f"   Symbolic keys: {counts.get('symbolic_keys', 0)}")
    print(f"   Target: 120 rules")
    print(f"   Coverage: {(counts.get('total_rules', 0) / 120 * 100):.1f}%")


if __name__ == "__main__":
    asyncio.run(ingest_expansion_rules())
