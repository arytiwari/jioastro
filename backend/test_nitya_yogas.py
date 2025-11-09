"""
Test script for 27 Nitya Yogas implementation
Tests all 27 yogas with sample Sun-Moon distances
"""

from app.services.extended_yoga_service import ExtendedYogaService

def test_nitya_yogas():
    """Test all 27 Nitya Yogas"""
    service = ExtendedYogaService()

    print("=" * 80)
    print("NITYA YOGAS VERIFICATION TEST")
    print("=" * 80)
    print()

    # Test data: Sun-Moon distances for all 27 yogas
    test_cases = [
        (0, 5.0, "Vishkambha"),  # 0° - 13°20'
        (1, 20.0, "Priti"),       # 13°20' - 26°40'
        (2, 35.0, "Ayushman"),    # 26°40' - 40°
        (3, 45.0, "Saubhagya"),   # 40° - 53°20'
        (4, 60.0, "Shobhana"),    # 53°20' - 66°40'
        (5, 75.0, "Atiganda"),    # 66°40' - 80°
        (6, 88.0, "Sukarma"),     # 80° - 93°20'
        (7, 100.0, "Dhriti"),     # 93°20' - 106°40'
        (8, 115.0, "Shoola"),     # 106°40' - 120°
        (9, 128.0, "Ganda"),      # 120° - 133°20'
        (10, 140.0, "Vriddhi"),   # 133°20' - 146°40'
        (11, 155.0, "Dhruva"),    # 146°40' - 160°
        (12, 168.0, "Vyaghata"),  # 160° - 173°20'
        (13, 180.0, "Harshana"),  # 173°20' - 186°40'
        (14, 195.0, "Vajra"),     # 186°40' - 200°
        (15, 208.0, "Siddhi"),    # 200° - 213°20'
        (16, 220.0, "Vyatipata"), # 213°20' - 226°40'
        (17, 235.0, "Variyan"),   # 226°40' - 240°
        (18, 248.0, "Parigha"),   # 240° - 253°20'
        (19, 260.0, "Shiva"),     # 253°20' - 266°40'
        (20, 275.0, "Siddha"),    # 266°40' - 280°
        (21, 288.0, "Sadhya"),    # 280° - 293°20'
        (22, 300.0, "Shubha"),    # 293°20' - 306°40'
        (23, 312.0, "Shukla"),    # 306°40' - 320°
        (24, 328.0, "Brahma"),    # 320° - 333°20'
        (25, 340.0, "Indra"),     # 333°20' - 346°40'
        (26, 355.0, "Vaidhriti"), # 346°40' - 360°
    ]

    success_count = 0

    for expected_index, sun_moon_distance, expected_name in test_cases:
        # Calculate Sun and Moon longitudes that give the desired distance
        # Moon longitude = Sun longitude + distance
        sun_long = 0.0
        moon_long = sun_moon_distance

        planets = {
            "Sun": {
                "longitude": sun_long,
                "house": 1,
                "sign_num": 1,
                "retrograde": False
            },
            "Moon": {
                "longitude": moon_long,
                "house": 1,
                "sign_num": 1,
                "retrograde": False
            }
        }

        yogas = service.detect_extended_yogas(planets)

        # Debug: Print first few yogas to see what's being detected
        if expected_index == 0:
            print(f"DEBUG: Total yogas detected: {len(yogas)}")
            print(f"DEBUG: First few yoga names:")
            for i, y in enumerate(yogas[:5]):
                print(f"  {i+1}. {y.get('name', 'Unknown')} - Category: {y.get('category', 'N/A')}")
            print()

        # Find Nitya Yoga in results
        nitya_yoga = None
        for yoga in yogas:
            if "Nitya Yoga" in yoga.get("category", ""):
                nitya_yoga = yoga
                break

        # Verify
        if nitya_yoga:
            detected_name = nitya_yoga["name"]
            if expected_name in detected_name:
                print(f"✅ Test {expected_index + 1}: {expected_name} Yoga")
                print(f"   Distance: {sun_moon_distance:.2f}°")
                print(f"   Detected: {detected_name}")
                print(f"   Nature: {nitya_yoga.get('nature', 'N/A')}")
                print(f"   Deity: {nitya_yoga.get('deity', 'N/A')}")
                print()
                success_count += 1
            else:
                print(f"❌ Test {expected_index + 1}: Expected {expected_name}, got {detected_name}")
                print()
        else:
            print(f"❌ Test {expected_index + 1}: No Nitya Yoga detected for {expected_name}")
            print()

    print("=" * 80)
    print(f"RESULTS: {success_count}/27 tests passed")
    print("=" * 80)

    if success_count == 27:
        print("✅ ALL NITYA YOGAS WORKING CORRECTLY!")
    else:
        print(f"⚠️  {27 - success_count} tests failed")

    return success_count == 27

if __name__ == "__main__":
    success = test_nitya_yogas()
    exit(0 if success else 1)
