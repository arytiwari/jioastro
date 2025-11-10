"""
Check current status of dasha timeline cache
"""
import asyncio
from app.core.supabase_client import SupabaseClient

async def check_cache():
    client = SupabaseClient(use_service_role=True)

    try:
        # Get all cache entries
        caches = await client.select("dasha_timeline_cache")

        if caches:
            print(f"Found {len(caches)} cached timelines:")
            for cache in caches:
                print(f"\n  Profile ID: {cache['profile_id']}")
                print(f"  Expires at: {cache.get('expires_at', 'N/A')}")
                print(f"  Created at: {cache.get('created_at', 'N/A')}")

                # Show first mahadasha from timeline_data
                if 'timeline_data' in cache and isinstance(cache['timeline_data'], dict):
                    periods = cache['timeline_data'].get('mahadasha_periods', [])
                    if periods:
                        print(f"  First Mahadasha: {periods[0].get('planet', 'Unknown')}")
                        print(f"  Total Periods: {len(periods)}")
        else:
            print("✅ No cached timelines found - fresh calculation will occur")

    except Exception as e:
        print(f"❌ Error checking cache: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_cache())
