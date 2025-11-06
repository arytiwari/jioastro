"""
Run Knowledge Base Migration
Creates the knowledge_base table with pgvector support and sample rules
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.supabase_service import supabase_service


async def run_migration():
    """Run the knowledge base migration SQL"""

    print("🚀 Starting knowledge_base table migration...")
    print("=" * 60)

    # Read the migration SQL file
    migration_file = Path(__file__).parent.parent / "docs" / "database-migrations" / "002_create_knowledge_base_table.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False

    print(f"📄 Reading migration file: {migration_file.name}")

    with open(migration_file, 'r') as f:
        sql_content = f.read()

    # Split into individual statements (rough split by semicolon)
    # Note: This is a simple approach. For complex SQL, use a proper SQL parser
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

    print(f"📋 Found {len(statements)} SQL statements to execute")
    print()

    success_count = 0
    error_count = 0

    for i, statement in enumerate(statements, 1):
        # Skip comments and empty statements
        if not statement or statement.startswith('--') or statement.startswith('/*'):
            continue

        # Get first line for logging
        first_line = statement.split('\n')[0][:80]
        print(f"[{i}/{len(statements)}] Executing: {first_line}...")

        try:
            # Execute via Supabase RPC (need to use raw SQL execution)
            # Note: Supabase client doesn't support raw SQL directly
            # You may need to run this manually in Supabase SQL editor

            # For now, just show what would be executed
            print(f"  ⚠️  Please run this SQL manually in Supabase SQL editor")
            print(f"  Statement: {statement[:200]}...")

            success_count += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            error_count += 1

    print()
    print("=" * 60)
    print(f"✅ Migration preparation complete")
    print(f"   Successfully prepared: {success_count} statements")
    print(f"   Errors: {error_count} statements")
    print()
    print("📝 MANUAL STEP REQUIRED:")
    print("   Please copy the SQL from the migration file and run it in:")
    print("   Supabase Dashboard → SQL Editor → New Query")
    print()
    print(f"   File location: {migration_file}")
    print()

    # Verify if table exists after manual run
    try:
        response = supabase_service.client.table('knowledge_base').select('count').limit(1).execute()
        print("✅ knowledge_base table exists and is accessible!")

        # Count rules
        rules_response = supabase_service.client.table('knowledge_base').select('*').execute()
        rule_count = len(rules_response.data) if rules_response.data else 0
        print(f"📚 Found {rule_count} rules in knowledge_base")

        if rule_count > 0:
            print("\n Sample rules:")
            for rule in rules_response.data[:3]:
                print(f"   - {rule.get('rule_id')}: {rule.get('condition')[:60]}...")

        return True

    except Exception as e:
        print(f"⚠️  knowledge_base table not found yet")
        print(f"   Error: {e}")
        print(f"   Please run the SQL migration manually in Supabase Dashboard")
        return False


async def main():
    """Main entry point"""
    try:
        success = await run_migration()

        if success:
            print("\n✅ Migration completed successfully!")
        else:
            print("\n⚠️  Please complete the manual migration step")
            print("   Then run this script again to verify")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
