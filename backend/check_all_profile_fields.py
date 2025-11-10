"""
Check ALL fields in the profile to see what data exists
"""
import asyncio
import json
from app.core.supabase_client import SupabaseClient

async def check_all_fields():
    client = SupabaseClient(use_service_role=True)

    profile_id = "271aeac2-1f98-407f-adcd-1ce43eef859d"

    profile_result = await client.select(
        "profiles",
        filters={"id": profile_id}
    )

    if not profile_result:
        print("Profile not found")
        return

    profile = profile_result[0]
    print("ALL Profile Fields:")
    print(json.dumps(profile, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(check_all_fields())
