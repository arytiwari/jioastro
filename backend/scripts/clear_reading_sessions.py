"""
Clear all reading sessions from the database
Run this to clean up cached readings
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.supabase_service import supabase_service

def clear_all_reading_sessions():
    """Delete all reading sessions"""
    try:
        print("🗑️  Clearing all reading sessions...")

        # Delete all records from reading_sessions table
        result = supabase_service.client.table("reading_sessions")\
            .delete()\
            .neq("id", "00000000-0000-0000-0000-000000000000")\
            .execute()

        count = len(result.data) if result.data else 0
        print(f"✅ Deleted {count} reading sessions")

        return count

    except Exception as e:
        print(f"❌ Error clearing reading sessions: {e}")
        return 0

if __name__ == "__main__":
    print("=" * 60)
    print("CLEAR ALL READING SESSIONS")
    print("=" * 60)
    print("\n⚠️  WARNING: This will delete ALL reading sessions!")
    print("This action cannot be undone.\n")

    confirm = input("Type 'yes' to confirm: ")

    if confirm.lower() == 'yes':
        count = clear_all_reading_sessions()
        print(f"\n✅ Cleanup complete! Removed {count} sessions.")
    else:
        print("\n❌ Cancelled.")
