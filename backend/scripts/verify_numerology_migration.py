"""
Verification script for numerology database migration

This script checks if the numerology tables were created successfully
and that the schema is correct.

Usage:
    python scripts/verify_numerology_migration.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.supabase_service import supabase_service


def check_table_exists(table_name):
    """Check if a table exists and is accessible"""
    try:
        response = supabase_service.client.table(table_name).select("*").limit(0).execute()
        return True, "Table exists and is accessible"
    except Exception as e:
        error_msg = str(e)
        if "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
            return False, "Table does not exist"
        return False, f"Error accessing table: {error_msg[:100]}"


def check_sample_rules():
    """Check if sample numerology rules were inserted"""
    try:
        response = supabase_service.client.table("kb_rules")\
            .select("rule_id, domain, system")\
            .eq("domain", "numerology")\
            .execute()

        if response.data:
            return True, f"Found {len(response.data)} numerology rules"
        return False, "No numerology rules found in kb_rules table"
    except Exception as e:
        return False, f"Error checking kb_rules: {str(e)[:100]}"


def main():
    """Main verification function"""
    print("\n" + "=" * 70)
    print("     NUMEROLOGY MIGRATION VERIFICATION")
    print("=" * 70)

    # Tables to check
    tables = {
        'numerology_profiles': 'Main numerology profiles table',
        'numerology_name_trials': 'Name trial experiments table',
        'privacy_preferences': 'User privacy preferences table',
        'kb_rules': 'Extended knowledge base rules (should have numerology entries)'
    }

    print("\n🔍 Checking database tables...")
    print("-" * 70)

    all_passed = True
    passed_count = 0

    for table_name, description in tables.items():
        exists, message = check_table_exists(table_name)

        status = "✅" if exists else "❌"
        print(f"{status} {table_name}")
        print(f"   {description}")
        print(f"   Status: {message}")
        print()

        if exists:
            passed_count += 1
        else:
            all_passed = False

    # Check sample rules
    print("-" * 70)
    print("\n🔍 Checking sample numerology rules...")
    rules_exist, rules_message = check_sample_rules()
    status = "✅" if rules_exist else "⚠️ "
    print(f"{status} {rules_message}")

    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ MIGRATION VERIFICATION PASSED!")
        print(f"   All {passed_count}/{len(tables)} tables are accessible")
        if rules_exist:
            print("   Sample numerology rules found in kb_rules")
        print("\n📍 Next steps:")
        print("   1. Test API endpoints at: http://localhost:8000/docs")
        print("   2. Look for 'numerology' tag in Swagger UI")
        print("   3. Try POST /api/v1/numerology/calculate")
        print("=" * 70)
        return 0
    else:
        print("❌ MIGRATION VERIFICATION FAILED")
        print(f"   Only {passed_count}/{len(tables)} tables are accessible")
        print("\n📝 Please run the migration manually:")
        print("   1. Go to Supabase Dashboard > SQL Editor")
        print("   2. Open backend/docs/database-migrations/001_add_numerology_schema.sql")
        print("   3. Copy and paste the entire SQL content")
        print("   4. Click 'Run' button")
        print("   5. Run this verification script again")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
