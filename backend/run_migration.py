"""
Run database migration to add profile_id to palmistry tables
"""
import asyncio
import sys
from pathlib import Path

from app.services.supabase_client import SupabaseClient


async def run_migration():
    """Execute the migration SQL file"""
    migration_file = Path(__file__).parent / "migrations" / "add_profile_to_palmistry.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)

    print(f"📖 Reading migration from: {migration_file}")
    with open(migration_file) as f:
        sql = f.read()

    print("🔧 Running migration...")
    client = SupabaseClient()

    try:
        # For Supabase REST API, we need to run each statement separately
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]

        for stmt in statements:
            if 'ALTER TABLE' in stmt or 'CREATE INDEX' in stmt or 'COMMENT ON' in stmt:
                print(f"   Executing: {stmt[:50]}...")
                # Supabase REST API doesn't support raw SQL execution
                # We'll need to run this via psql or Supabase dashboard
                print(f"   Statement: {stmt}")

        print("⚠️  Please run this migration via Supabase SQL Editor or psql")
        print(f"   Migration file: {migration_file}")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_migration())
    sys.exit(0 if success else 1)
