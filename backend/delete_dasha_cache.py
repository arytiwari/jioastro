"""
Delete Life Threads dasha timeline cache entries completely (not just expire)
"""
import asyncio
from app.core.supabase_client import SupabaseClient

async def delete_cache():
    client = SupabaseClient(use_service_role=True)

    try:
        # Get all cache entries first
        caches = await client.select("dasha_timeline_cache")

        if caches:
            print(f"Found {len(caches)} cached timelines")
            for cache in caches:
                print(f"  Profile ID: {cache['profile_id']}")
                # DELETE instead of UPDATE to force fresh calculation
                await client.delete(
                    "dasha_timeline_cache",
                    filters={"profile_id": cache["profile_id"]}
                )
            print(f"✅ Deleted {len(caches)} cached timelines - fresh calculation will occur on next load")
        else:
            print("No cached timelines found")

    except Exception as e:
        print(f"❌ Error deleting cache: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(delete_cache())
