"""
Clear Life Threads dasha timeline cache to force recalculation with accurate logic
"""
import asyncio
from app.core.supabase_client import SupabaseClient

async def clear_cache():
    client = SupabaseClient(use_service_role=True)
    
    try:
        # Update expires_at to force expiry
        from datetime import datetime, timezone
        expired_time = datetime(2020, 1, 1, tzinfo=timezone.utc).isoformat()
        
        # Get all cache entries
        caches = await client.select("dasha_timeline_cache")
        
        if caches:
            print(f"Found {len(caches)} cached timelines")
            for cache in caches:
                await client.update(
                    "dasha_timeline_cache",
                    filters={"profile_id": cache["profile_id"]},
                    data={"expires_at": expired_time}
                )
            print(f"✅ Expired {len(caches)} cached timelines - they will recalculate on next load")
        else:
            print("No cached timelines found")
            
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(clear_cache())
