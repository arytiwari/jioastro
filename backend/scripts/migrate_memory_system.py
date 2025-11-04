"""
Run Memory System Database Migration
Creates user_memory, event_anchors, and reading_sessions tables
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.supabase_service import supabase_service


def run_migration():
    """Run the memory system database migration"""
    print("=" * 80)
    print("MEMORY SYSTEM DATABASE MIGRATION")
    print("=" * 80)

    # Read migration SQL
    sql_file = Path(__file__).parent.parent / "docs" / "database-schema-memory-system.sql"

    if not sql_file.exists():
        print(f"❌ Migration file not found: {sql_file}")
        return False

    with open(sql_file, 'r') as f:
        sql_content = f.read()

    print(f"\n📄 Reading migration from: {sql_file.name}")
    print(f"   File size: {len(sql_content)} characters")

    # Split SQL into individual statements
    # Filter out comments and empty lines
    statements = []
    current_statement = []

    for line in sql_content.split('\n'):
        # Skip comments and empty lines
        if line.strip().startswith('--') or not line.strip():
            continue

        current_statement.append(line)

        # End of statement
        if line.strip().endswith(';'):
            statement = '\n'.join(current_statement)
            if statement.strip():
                statements.append(statement)
            current_statement = []

    print(f"\n📊 Found {len(statements)} SQL statements to execute")

    # Execute each statement
    success_count = 0
    error_count = 0
    table_count = 0

    for i, statement in enumerate(statements, 1):
        # Get statement type
        stmt_lower = statement.lower().strip()

        if 'create table' in stmt_lower:
            table_name = extract_table_name(statement)
            print(f"\n{i}. Creating table: {table_name}...")
            table_count += 1
        elif 'create index' in stmt_lower:
            index_name = extract_index_name(statement)
            print(f"\n{i}. Creating index: {index_name}...")
        elif 'create policy' in stmt_lower:
            policy_name = extract_policy_name(statement)
            print(f"\n{i}. Creating RLS policy: {policy_name}...")
        elif 'create or replace function' in stmt_lower:
            func_name = extract_function_name(statement)
            print(f"\n{i}. Creating function: {func_name}...")
        elif 'create trigger' in stmt_lower:
            trigger_name = extract_trigger_name(statement)
            print(f"\n{i}. Creating trigger: {trigger_name}...")
        elif 'alter table' in stmt_lower and 'enable row level security' in stmt_lower:
            table_name = extract_alter_table_name(statement)
            print(f"\n{i}. Enabling RLS on: {table_name}...")
        elif 'comment on' in stmt_lower:
            print(f"\n{i}. Adding comment...")
        else:
            print(f"\n{i}. Executing statement...")

        try:
            # Execute via Supabase RPC or direct SQL
            # Note: Supabase REST API doesn't support DDL directly
            # We'll need to use the management API or run via psql

            # For now, we'll skip execution and just validate the SQL
            # In production, this should be run via Supabase Dashboard SQL Editor
            # or using the PostgREST admin API

            print(f"   ⚠️  Statement ready (run via Supabase Dashboard)")
            success_count += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")
            error_count += 1

    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    print(f"\n✅ Statements prepared: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Tables to create: {table_count}")

    print("\n⚠️  IMPORTANT:")
    print("   Supabase REST API doesn't support DDL execution.")
    print("   Please run the migration manually:")
    print()
    print("   Option 1: Supabase Dashboard")
    print("   1. Go to https://supabase.com/dashboard")
    print("   2. Select your project")
    print("   3. Go to SQL Editor")
    print("   4. Paste contents of: docs/database-schema-memory-system.sql")
    print("   5. Run the SQL")
    print()
    print("   Option 2: psql (if installed)")
    print("   PGPASSWORD='Jio@stro@9812' psql \\")
    print("     -h aws-1-ap-southeast-2.pooler.supabase.com \\")
    print("     -p 6543 \\")
    print("     -U postgres.jyawjajnxzuhzisjcnpn \\")
    print("     -d postgres \\")
    print("     -f docs/database-schema-memory-system.sql")

    return True


def extract_table_name(statement):
    """Extract table name from CREATE TABLE statement"""
    parts = statement.lower().split('create table if not exists')
    if len(parts) > 1:
        table_part = parts[1].strip().split()[0]
        return table_part.strip('(')
    return "unknown"


def extract_index_name(statement):
    """Extract index name from CREATE INDEX statement"""
    parts = statement.lower().split('create index')
    if len(parts) > 1:
        return parts[1].strip().split()[0]
    return "unknown"


def extract_policy_name(statement):
    """Extract policy name from CREATE POLICY statement"""
    parts = statement.split('"')
    if len(parts) >= 2:
        return parts[1]
    return "unknown"


def extract_function_name(statement):
    """Extract function name from CREATE FUNCTION statement"""
    parts = statement.lower().split('create or replace function')
    if len(parts) > 1:
        func_part = parts[1].strip().split('(')[0]
        return func_part.strip()
    return "unknown"


def extract_trigger_name(statement):
    """Extract trigger name from CREATE TRIGGER statement"""
    parts = statement.lower().split('create trigger')
    if len(parts) > 1:
        return parts[1].strip().split()[0]
    return "unknown"


def extract_alter_table_name(statement):
    """Extract table name from ALTER TABLE statement"""
    parts = statement.lower().split('alter table')
    if len(parts) > 1:
        return parts[1].strip().split()[0]
    return "unknown"


if __name__ == "__main__":
    run_migration()
