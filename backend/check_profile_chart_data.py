"""
Check if there's a birth chart with coordinates for this profile
"""
import asyncio
from app.core.supabase_client import SupabaseClient

async def check_chart_data():
    client = SupabaseClient(use_service_role=True)

    profile_id = "271aeac2-1f98-407f-adcd-1ce43eef859d"

    # Check if there's a chart with coordinates
    charts = await client.select(
        "charts",
        filters={"profile_id": profile_id}
    )

    if charts:
        print(f"Found {len(charts)} chart(s) for this profile:")
        for chart in charts:
            print(f"\nChart ID: {chart.get('id')}")
            print(f"  Birth Place: {chart.get('birth_place')}")
            print(f"  Latitude: {chart.get('latitude')}")
            print(f"  Longitude: {chart.get('longitude')}")
            print(f"  Timezone: {chart.get('timezone')}")
    else:
        print("No charts found for this profile")

if __name__ == "__main__":
    asyncio.run(check_chart_data())
