"""
Script to run numerology database migration on Supabase

This script executes the 001_add_numerology_schema.sql migration file
directly on the Supabase database.

Usage:
    python scripts/run_numerology_migration.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.supabase_service import supabase_service


def read_migration_file():
    """Read the SQL migration file"""
    migration_path = Path(__file__).parent.parent / "docs" / "database-migrations" / "001_add_numerology_schema.sql"

    if not migration_path.exists():
        print(f"❌ Migration file not found at: {migration_path}")
        sys.exit(1)

    with open(migration_path, 'r') as f:
        sql_content = f.read()

    print(f"✅ Loaded migration file: {migration_path.name}")
    print(f"   File size: {len(sql_content)} characters")
    return sql_content


def execute_migration():
    """Execute the migration SQL on Supabase"""
    print("\n🚀 Starting numerology database migration...")
    print("=" * 70)

    # Read migration file
    sql_content = read_migration_file()

    # Split into individual statements (rough split by semicolon + newline)
    statements = []
    current_statement = []
    in_function = False

    for line in sql_content.split('\n'):
        # Skip comments and empty lines
        if line.strip().startswith('--') or not line.strip():
            continue

        # Track function definitions (they contain multiple semicolons)
        if 'CREATE OR REPLACE FUNCTION' in line or 'CREATE FUNCTION' in line:
            in_function = True

        current_statement.append(line)

        # End of statement detection
        if line.strip().endswith(';') and not in_function:
            statement = '\n'.join(current_statement).strip()
            if statement:
                statements.append(statement)
            current_statement = []
        elif '$$;' in line or 'END;' in line:
            in_function = False

    # Add any remaining statement
    if current_statement:
        statement = '\n'.join(current_statement).strip()
        if statement:
            statements.append(statement)

    print(f"\n📋 Found {len(statements)} SQL statements to execute")
    print("=" * 70)

    # Execute each statement
    success_count = 0
    error_count = 0

    for i, statement in enumerate(statements, 1):
        # Show progress for long migrations
        if i % 10 == 0 or i == len(statements):
            print(f"\n⏳ Progress: {i}/{len(statements)} statements...")

        try:
            # Preview first 80 chars of statement
            preview = statement[:80].replace('\n', ' ')
            if len(statement) > 80:
                preview += "..."

            # Execute via Supabase REST API's RPC endpoint
            # Note: Supabase REST API has limited DDL support
            # For full DDL execution, we need to use SQL Editor or direct psql

            # Try to execute via SQL query
            response = supabase_service.client.rpc('sql', {'query': statement}).execute()

            success_count += 1
            print(f"   ✅ [{i}] {preview}")

        except Exception as e:
            error_count += 1
            error_msg = str(e)[:100]
            print(f"   ⚠️  [{i}] Error: {error_msg}")
            print(f"       Statement: {preview}")

            # Some errors are expected (e.g., table already exists)
            if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                print(f"       (This is okay - object already exists)")
                success_count += 1
                error_count -= 1

    print("\n" + "=" * 70)
    print(f"✅ Migration execution completed!")
    print(f"   Success: {success_count} statements")
    print(f"   Errors: {error_count} statements")

    if error_count > 0:
        print(f"\n⚠️  Note: Supabase REST API has limited DDL support.")
        print(f"   For full migration, please use one of these methods:")
        print(f"   1. Supabase SQL Editor (recommended)")
        print(f"   2. Direct psql connection")
        print(f"   3. Supabase CLI: supabase db push")

    return success_count, error_count


def verify_migration():
    """Verify that tables were created successfully"""
    print("\n🔍 Verifying migration...")
    print("=" * 70)

    tables_to_check = [
        'numerology_profiles',
        'numerology_name_trials',
        'privacy_preferences'
    ]

    verified_count = 0

    for table in tables_to_check:
        try:
            # Try to query the table (will fail if it doesn't exist)
            response = supabase_service.client.table(table).select("id").limit(1).execute()
            print(f"   ✅ Table '{table}' exists and is accessible")
            verified_count += 1
        except Exception as e:
            print(f"   ❌ Table '{table}' not found or not accessible")
            print(f"      Error: {str(e)[:100]}")

    print(f"\n{'✅' if verified_count == len(tables_to_check) else '⚠️ '} Verified {verified_count}/{len(tables_to_check)} tables")

    return verified_count == len(tables_to_check)


def show_manual_instructions():
    """Show manual migration instructions"""
    print("\n" + "=" * 70)
    print("📝 MANUAL MIGRATION INSTRUCTIONS")
    print("=" * 70)
    print("\nIf automatic execution fails, please run migration manually:")
    print("\n1. Go to Supabase Dashboard: https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Click 'SQL Editor' in the left sidebar")
    print("4. Click 'New Query'")
    print("5. Copy the contents of:")
    print(f"   backend/docs/database-migrations/001_add_numerology_schema.sql")
    print("6. Paste into the SQL Editor")
    print("7. Click 'Run' button")
    print("\nAlternatively, use Supabase CLI:")
    print("   cd backend")
    print("   supabase db push")
    print("=" * 70)


def main():
    """Main execution function"""
    print("\n" + "=" * 70)
    print("     NUMEROLOGY DATABASE MIGRATION")
    print("     Phase 1: Schema Setup")
    print("=" * 70)

    try:
        # Execute migration
        success, errors = execute_migration()

        # Verify tables exist
        if errors == 0:
            verified = verify_migration()

            if verified:
                print("\n" + "=" * 70)
                print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
                print("=" * 70)
                print("\nNext steps:")
                print("1. Test API endpoints at: http://localhost:8000/docs")
                print("2. Look for the 'numerology' tag in Swagger UI")
                print("3. Try POST /api/v1/numerology/calculate endpoint")
                return 0
            else:
                print("\n⚠️  Migration executed but verification failed")
                show_manual_instructions()
                return 1
        else:
            print(f"\n⚠️  Migration completed with {errors} errors")
            show_manual_instructions()
            return 1

    except Exception as e:
        print(f"\n❌ Migration failed with error: {str(e)}")
        show_manual_instructions()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
