"""
Debug dasha calculation for specific profile
"""
import asyncio
from datetime import date, time as datetime_time
from app.services.vedic_astrology_accurate import AccurateVedicAstrology
from app.core.supabase_client import SupabaseClient

async def test_profile_dasha():
    client = SupabaseClient(use_service_role=True)

    # Get the profile data
    profile_id = "271aeac2-1f98-407f-adcd-1ce43eef859d"
    profile_result = await client.select(
        "profiles",
        filters={"id": profile_id}
    )

    if not profile_result:
        print("Profile not found")
        return

    profile = profile_result[0]
    print("Profile data:")
    print(f"  Name: {profile.get('name')}")
    print(f"  Birth Date: {profile.get('birth_date')}")
    print(f"  Birth Time: {profile.get('birth_time')}")
    print(f"  Latitude: {profile.get('birth_lat')}")  # Fixed field name
    print(f"  Longitude: {profile.get('birth_lon')}")  # Fixed field name
    print(f"  Birth Place: {profile.get('birth_city')}")  # Fixed field name

    # Try to calculate
    try:
        birth_date = date.fromisoformat(profile["birth_date"])
        birth_time_str = profile.get("birth_time")
        latitude = profile.get("birth_lat")  # Fixed field name
        longitude = profile.get("birth_lon")  # Fixed field name

        if not birth_time_str or latitude is None or longitude is None:
            print("\n❌ Missing required data for calculation")
            print(f"  Birth time: {birth_time_str}")
            print(f"  Latitude: {latitude}")
            print(f"  Longitude: {longitude}")
            return

        # Parse birth time
        time_parts = birth_time_str.split(':')
        birth_time = datetime_time(int(time_parts[0]), int(time_parts[1]), 0)

        print(f"\n✅ All data present, calculating...")

        # Calculate
        astro_service = AccurateVedicAstrology()
        chart_data = astro_service.calculate_birth_chart(
            name=profile.get('name', 'Test'),
            birth_date=birth_date,
            birth_time=birth_time,
            latitude=latitude,
            longitude=longitude,
            timezone_str="Asia/Kolkata"
        )

        print(f"\n✅ Calculation successful!")
        print(f"Chart data keys: {list(chart_data.keys())}")

        # Check dasha data
        dasha_data = chart_data.get("dasha", {})
        print(f"\nDasha data keys: {list(dasha_data.keys())}")

        mahadashas = dasha_data.get("mahadashas", [])
        print(f"Number of mahadashas: {len(mahadashas)}")

        if mahadashas:
            print(f"\nFirst 5 Mahadashas:")
            for i, maha in enumerate(mahadashas[:5]):
                print(f"{i+1}. {maha['planet']}: {maha['start_date']} to {maha['end_date']} ({maha['years']} years)")

    except Exception as e:
        print(f"\n❌ Error during calculation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_profile_dasha())
