"""
Run Phase 3 migration to add columns to reading_sessions table
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.supabase_service import supabase_service

def run_migration():
    """Run SQL migration via Supabase"""

    # Read migration SQL
    migration_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs",
        "add-phase3-columns.sql"
    )

    print(f"📖 Reading migration from: {migration_path}")

    with open(migration_path, 'r') as f:
        sql = f.read()

    print(f"📝 Migration SQL loaded ({len(sql)} characters)")
    print("\n" + "="*60)
    print("RUNNING MIGRATION")
    print("="*60 + "\n")

    try:
        # Execute via Supabase RPC or direct SQL
        # Note: This requires the SQL to be executed via Supabase dashboard or psql
        print("⚠️  This migration must be run via Supabase SQL Editor or psql")
        print("\nSteps:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the SQL from:")
        print(f"   {migration_path}")
        print("4. Click 'Run' to execute the migration")
        print("\nOR run via psql:")
        print(f"   psql YOUR_DATABASE_URL < {migration_path}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("PHASE 3 MIGRATION - Add Phase 3 Columns")
    print("="*60)
    print()

    success = run_migration()

    if success:
        print("\n" + "="*60)
        print("✅ Migration instructions provided!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Migration failed!")
        print("="*60)
        sys.exit(1)
