"""
Update Embedding Dimensions Migration
Updates knowledge_base table from vector(1536) to vector(3072)
For Azure OpenAI text-embedding-3-large compatibility
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.supabase_service import supabase_service


async def run_migration():
    """Run the embedding dimension update migration"""

    print("🚀 Starting Embedding Dimension Migration (1536 → 3072)...")
    print("=" * 70)

    # Read the migration SQL file
    migration_file = Path(__file__).parent.parent / "docs" / "database-migrations" / "003_update_embedding_dimensions_to_3072.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False

    print(f"📄 Reading migration file: {migration_file.name}")
    print()

    with open(migration_file, 'r') as f:
        sql_content = f.read()

    # Show migration summary
    print("📋 Migration Summary:")
    print("-" * 70)
    print("1. Drop existing vector index")
    print("2. Update embedding column: vector(1536) → vector(3072)")
    print("3. Recreate vector index with new dimensions")
    print("4. Update match_knowledge() function for 3072 dimensions")
    print("5. Clear existing 1536-dim embeddings (incompatible)")
    print("-" * 70)
    print()

    # Warning about data loss
    print("⚠️  WARNING: This migration will:")
    print("   - Clear all existing embeddings (1536-dim incompatible with 3072-dim)")
    print("   - Keep all rules intact")
    print("   - Require re-processing documents to regenerate embeddings")
    print()

    # Manual execution required
    print("=" * 70)
    print("📝 MANUAL STEP REQUIRED:")
    print("=" * 70)
    print()
    print("   Please copy the SQL migration and run it in:")
    print("   Supabase Dashboard → SQL Editor → New Query")
    print()
    print(f"   File location: {migration_file}")
    print()
    print("   After running the migration:")
    print("   1. Verify indexes were recreated")
    print("   2. Run this script again to verify")
    print("   3. Re-process documents to generate new embeddings")
    print()

    # Verify current state
    try:
        print("🔍 Checking current knowledge_base state...")
        print("-" * 70)

        # Count total rules
        rules_response = supabase_service.client.table("knowledge_base")\
            .select("*", count="exact")\
            .execute()

        total_rules = rules_response.count if hasattr(rules_response, 'count') else len(rules_response.data or [])

        # Count rules with embeddings
        rules_with_embeddings = 0
        if rules_response.data:
            for rule in rules_response.data:
                if rule.get('embedding'):
                    rules_with_embeddings += 1

        print(f"📚 Total Rules: {total_rules}")
        print(f"🔢 Rules with embeddings: {rules_with_embeddings}")
        print()

        if rules_with_embeddings > 0:
            print(f"⚠️  After migration, {rules_with_embeddings} embeddings will be cleared")
            print("   (1536-dim embeddings are incompatible with 3072-dim)")
        else:
            print("✅ No embeddings to clear")

        print()
        print("-" * 70)

        return True

    except Exception as e:
        print(f"⚠️  Could not check knowledge_base state")
        print(f"   Error: {e}")
        print()
        return False


async def verify_migration():
    """Verify the migration was successful"""

    print()
    print("=" * 70)
    print("🔍 VERIFYING MIGRATION")
    print("=" * 70)
    print()

    try:
        # Try to query the knowledge_base table
        response = supabase_service.client.table("knowledge_base")\
            .select("*")\
            .limit(1)\
            .execute()

        if response.data:
            print("✅ knowledge_base table accessible")

            # Check if embeddings column exists
            sample_rule = response.data[0]
            if 'embedding' in sample_rule:
                embedding = sample_rule['embedding']
                if embedding:
                    # In Supabase, vectors are returned as arrays
                    if isinstance(embedding, list):
                        dimensions = len(embedding)
                        print(f"✅ Embedding column exists")
                        print(f"📊 Detected dimensions: {dimensions}")

                        if dimensions == 3072:
                            print("✅ MIGRATION SUCCESSFUL - Dimensions = 3072")
                        elif dimensions == 1536:
                            print("⚠️  Migration not yet run - Dimensions still = 1536")
                        else:
                            print(f"⚠️  Unexpected dimensions: {dimensions}")
                    else:
                        print("⚠️  Embedding format unexpected")
                else:
                    print("ℹ️  Sample rule has no embedding (cleared after migration)")
            else:
                print("⚠️  Embedding column not found")
        else:
            print("ℹ️  No rules in knowledge_base table")

        # Count rules
        count_response = supabase_service.client.table("knowledge_base")\
            .select("*", count="exact")\
            .execute()

        total_rules = count_response.count if hasattr(count_response, 'count') else len(count_response.data or [])
        print(f"📚 Total rules: {total_rules}")

        print()

    except Exception as e:
        print(f"❌ Verification error: {e}")
        print()


async def main():
    """Main entry point"""

    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║  Embedding Dimension Migration Tool                               ║")
    print("║  Updates knowledge_base: vector(1536) → vector(3072)              ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()

    # Check if user wants to verify only
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        await verify_migration()
        return

    success = await run_migration()

    if success:
        print()
        print("=" * 70)
        print("✅ NEXT STEPS:")
        print("=" * 70)
        print("1. Run the SQL migration in Supabase Dashboard")
        print("2. Verify: python scripts/run_embedding_dimension_migration.py verify")
        print("3. Re-process documents: python scripts/reprocess_knowledge_documents.py")
        print()


if __name__ == "__main__":
    asyncio.run(main())
