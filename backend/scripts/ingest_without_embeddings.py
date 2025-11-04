"""
BPHS Rule Ingestion (Without Embeddings)

Test ingestion with symbolic keys only, skipping embeddings due to API quota
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.knowledge_base import knowledge_base_service
from app.schemas.knowledge_base import RuleCreate, RuleIngestionBatch
from app.services.supabase_service import supabase_service


async def get_bphs_source_id() -> str:
    """Get the UUID of BPHS source from kb_sources table"""
    response = supabase_service.client.table("kb_sources")\
        .select("id")\
        .eq("title", "Brihat Parashara Hora Shastra")\
        .execute()

    source_id = response.data[0]["id"]
    print(f"✅ Found BPHS source: {source_id}")
    return source_id


async def load_rules_from_json(file_path: str, source_id: str) -> list[RuleCreate]:
    """Load rules from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rules = []
    for rule_data in data.get("rules", []):
        rule_data["source_id"] = source_id
        rule_data.setdefault("modifiers", [])
        rule_data.setdefault("weight", 0.5)
        rule_data.setdefault("applicable_vargas", ["D1"])
        rule_data.setdefault("cancelers", [])
        rule_data.setdefault("version", 1)
        rule_data.setdefault("status", "active")
        rules.append(RuleCreate(**rule_data))

    print(f"✅ Loaded {len(rules)} rules from {file_path}")
    return rules


async def main():
    print("="*60)
    print("BPHS RULE INGESTION (Without Embeddings)")
    print("="*60)
    print()

    # Get BPHS source
    source_id = await get_bphs_source_id()

    # Load rules
    json_path = Path(__file__).parent.parent / "data" / "bphs_rules_sample.json"
    rules = await load_rules_from_json(str(json_path), source_id)

    # Create batch WITHOUT embeddings
    print("\nIngesting rules with symbolic keys only...")
    batch = RuleIngestionBatch(
        rules=rules,
        generate_embeddings=False,  # Skip embeddings
        extract_symbolic_keys=True   # Generate symbolic keys
    )

    # Ingest
    response = await knowledge_base_service.ingest_batch(batch)

    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"✅ Rules ingested: {response.ingested_count}")
    print(f"✅ Symbolic keys: {response.symbolic_keys_generated}")
    print(f"⏱️  Duration: {response.duration_seconds:.2f}s")

    if response.errors:
        print(f"\n⚠️  Errors: {len(response.errors)}")
        for error in response.errors[:3]:  # Show first 3
            print(f"   • {error}")

    # Verify
    stats = await knowledge_base_service.count_rules()
    print("\n📊 Knowledge Base:")
    print(f"   Total Rules: {stats['total_rules']}")
    print(f"   Symbolic Keys: {stats['symbolic_keys']}")

    # Show sample symbolic keys
    print("\n🔑 Sample Symbolic Keys:")
    keys_response = supabase_service.client.table("kb_symbolic_keys")\
        .select("*")\
        .limit(10)\
        .execute()

    for key in keys_response.data[:10]:
        print(f"   • {key['key_type']:15} {key['key_value']}")

    print("\n✅ Done!")


if __name__ == "__main__":
    asyncio.run(main())
