#!/usr/bin/env python
"""
Clear cached charts from database to force recalculation with updated sign_num indexing.

This script deletes all cached chart data, forcing the system to recalculate charts
using the corrected 1-based sign numbering (1-12 instead of 0-11).
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.supabase_client import supabase_client


async def clear_charts():
    """Delete all cached charts from the database."""
    print("🗑️  Clearing cached charts from database...")

    try:
        # Count charts before deletion
        count_before = await supabase_client.count("charts")
        print(f"📊 Found {count_before} cached charts")

        if count_before == 0:
            print("✅ No charts to clear")
            return

        # Delete all charts (empty filters means delete all)
        # Note: We can't delete all at once with Supabase REST API
        # So we'll select all IDs and delete one by one
        charts = await supabase_client.select("charts", select="id")

        if not charts:
            print("✅ No charts found")
            return

        deleted_count = 0
        for chart in charts:
            try:
                await supabase_client.delete("charts", filters={"id": chart["id"]})
                deleted_count += 1
                if deleted_count % 10 == 0:
                    print(f"   Deleted {deleted_count}/{len(charts)} charts...")
            except Exception as e:
                print(f"   Warning: Failed to delete chart {chart['id']}: {e}")

        print(f"✅ Successfully deleted {deleted_count} cached charts")
        print(f"   Charts will be recalculated with corrected sign_num indexing (1-12)")

    except Exception as e:
        print(f"❌ Error clearing charts: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(clear_charts())
