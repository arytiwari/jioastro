"""
Run Life Snapshot database migration.
Creates the life_snapshot_data table with proper indexes and RLS policies.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def run_migration():
    """Run the Life Snapshot migration."""

    # Get DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    # Convert postgresql+asyncpg:// to postgresql:// for asyncpg
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    # Read migration SQL
    migration_file = "app/features/life_snapshot/migration.sql"
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    # Connect and run migration
    print(f"🔌 Connecting to database...")
    conn = await asyncpg.connect(database_url)

    try:
        print(f"📋 Running Life Snapshot migration...")
        await conn.execute(migration_sql)
        print(f"✅ Migration completed successfully!")

        # Verify table was created
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'life_snapshot_data'
            )
        """)

        if result:
            print(f"✅ Verified: life_snapshot_data table exists")
        else:
            print(f"⚠️  Warning: life_snapshot_data table not found after migration")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await conn.close()
        print(f"🔌 Database connection closed")

if __name__ == "__main__":
    asyncio.run(run_migration())
