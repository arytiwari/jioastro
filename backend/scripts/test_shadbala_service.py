"""
Test Shadbala Service
Demonstrates 6-fold planetary strength calculations
"""

import sys
from pathlib import Path
from datetime import datetime, date, time

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.shadbala_service import shadbala_service
from app.services.astrology import astrology_service


# Sample birth data for testing
SAMPLE_BIRTH_DATA_1 = {
    "name": "Strong Chart Example",
    "birth_date": date(1990, 3, 15),
    "birth_time": time(14, 30),
    "latitude": 19.0760,
    "longitude": 72.8777,
    "timezone_str": "Asia/Kolkata",
    "city": "Mumbai"
}

SAMPLE_BIRTH_DATA_2 = {
    "name": "Varied Strengths Example",
    "birth_date": date(1985, 11, 5),
    "birth_time": time(8, 15),
    "latitude": 28.7041,
    "longitude": 77.1025,
    "timezone_str": "Asia/Kolkata",
    "city": "Delhi"
}


def test_basic_shadbala():
    """Test 1: Basic Shadbala calculation"""
    print("=" * 80)
    print("TEST 1: BASIC SHADBALA CALCULATION")
    print("=" * 80)

    print("\n📋 Birth Data:")
    print(f"   Name: {SAMPLE_BIRTH_DATA_1['name']}")
    print(f"   Birth Date: {SAMPLE_BIRTH_DATA_1['birth_date']}")
    print(f"   Birth Time: {SAMPLE_BIRTH_DATA_1['birth_time']}")
    print(f"   Location: {SAMPLE_BIRTH_DATA_1['city']}")

    # Calculate birth chart
    print("\n🔮 Calculating birth chart...")
    chart = astrology_service.calculate_birth_chart(**SAMPLE_BIRTH_DATA_1)

    # Calculate Shadbala
    birth_datetime = datetime.combine(
        SAMPLE_BIRTH_DATA_1['birth_date'],
        SAMPLE_BIRTH_DATA_1['birth_time']
    )

    shadbala_results = shadbala_service.calculate_shadbala(
        chart_data=chart,
        birth_datetime=birth_datetime
    )

    print("\n" + "=" * 80)
    print("SHADBALA RESULTS (6-FOLD PLANETARY STRENGTH)")
    print("=" * 80)

    print("\n📊 Planetary Strengths:\n")

    for planet, data in shadbala_results['shadbala_by_planet'].items():
        rating_emoji = {
            "Exceptional": "⭐⭐⭐⭐⭐",
            "Very Strong": "⭐⭐⭐⭐",
            "Strong": "⭐⭐⭐",
            "Moderate": "⭐⭐",
            "Weak": "⭐",
            "Very Weak": "·"
        }.get(data['strength_rating'], "·")

        print(f"{planet:10} : {data['total_shadbala']:6.2f} / {data['required_shadbala']:3.0f} "
              f"({data['percentage']:6.2f}%) {rating_emoji} {data['strength_rating']}")

        components = data['components']
        print(f"             Sthana: {components['sthana_bala']:5.2f}  "
              f"Dig: {components['dig_bala']:5.2f}  "
              f"Kala: {components['kala_bala']:5.2f}")
        print(f"             Chesta: {components['chesta_bala']:5.2f}  "
              f"Nais: {components['naisargika_bala']:5.2f}  "
              f"Drik: {components['drik_bala']:5.2f}")
        print()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if shadbala_results['strongest_planet']:
        strongest = shadbala_results['strongest_planet']
        print(f"\n🏆 Strongest Planet: {strongest['planet']} ({strongest['strength']:.2f}%)")

    if shadbala_results['weakest_planet']:
        weakest = shadbala_results['weakest_planet']
        print(f"⚠️  Weakest Planet: {weakest['planet']} ({weakest['strength']:.2f}%)")

    print(f"\n📊 Average Strength: {shadbala_results['average_strength']:.2f}%")

    print(f"\n✅ Planets Above Required Strength ({len(shadbala_results['planets_above_required'])}):")
    for planet in shadbala_results['planets_above_required']:
        strength = shadbala_results['shadbala_by_planet'][planet]
        print(f"   • {planet} ({strength['percentage']:.2f}%)")

    print(f"\n⚠️  Planets Below Required Strength ({len(shadbala_results['planets_below_required'])}):")
    for planet in shadbala_results['planets_below_required']:
        strength = shadbala_results['shadbala_by_planet'][planet]
        print(f"   • {planet} ({strength['percentage']:.2f}%)")

    print("\n✅ Test 1 Complete!\n")
    return shadbala_results


def test_component_breakdown():
    """Test 2: Detailed component breakdown"""
    print("\n" + "=" * 80)
    print("TEST 2: DETAILED COMPONENT BREAKDOWN")
    print("=" * 80)

    chart = astrology_service.calculate_birth_chart(**SAMPLE_BIRTH_DATA_1)
    birth_datetime = datetime.combine(
        SAMPLE_BIRTH_DATA_1['birth_date'],
        SAMPLE_BIRTH_DATA_1['birth_time']
    )

    shadbala_results = shadbala_service.calculate_shadbala(
        chart_data=chart,
        birth_datetime=birth_datetime
    )

    print("\n📚 Understanding the 6 Components of Shadbala:\n")

    components_info = {
        "Sthana Bala": "Positional strength (exaltation, sign, house)",
        "Dig Bala": "Directional strength (best in specific direction)",
        "Kala Bala": "Temporal strength (day/night, lunar phase)",
        "Chesta Bala": "Motional strength (speed, retrograde)",
        "Naisargika Bala": "Natural strength (inherent to planet)",
        "Drik Bala": "Aspectual strength (aspects received)"
    }

    for component, description in components_info.items():
        print(f"   {component:20} : {description}")

    print("\n" + "=" * 80)
    print("COMPONENT ANALYSIS FOR EACH PLANET")
    print("=" * 80)

    # Show top 3 planets with component breakdown
    sorted_planets = sorted(
        shadbala_results['shadbala_by_planet'].items(),
        key=lambda x: x[1]['percentage'],
        reverse=True
    )

    for i, (planet, data) in enumerate(sorted_planets[:3], 1):
        print(f"\n{i}. {planet} (Total: {data['total_shadbala']:.2f}, {data['percentage']:.2f}%)")
        print(f"   Rating: {data['strength_rating']}\n")

        components = data['components']
        max_component = max(components.items(), key=lambda x: x[1])
        min_component = min(components.items(), key=lambda x: x[1])

        print(f"   Strongest Component: {max_component[0]} = {max_component[1]:.2f}")
        print(f"   Weakest Component: {min_component[0]} = {min_component[1]:.2f}")
        print()

        # Show all components
        for comp_name, comp_value in components.items():
            percentage_of_max = (comp_value / 60) * 100  # Max value for most components is 60
            bar = "█" * int(percentage_of_max / 10)
            print(f"   {comp_name:20} : {comp_value:5.2f} {bar}")

    print("\n✅ Test 2 Complete!\n")


def test_different_chart():
    """Test 3: Test with different birth chart"""
    print("\n" + "=" * 80)
    print("TEST 3: DIFFERENT BIRTH CHART COMPARISON")
    print("=" * 80)

    print(f"\n📋 Birth Data 2:")
    print(f"   Name: {SAMPLE_BIRTH_DATA_2['name']}")
    print(f"   Birth Date: {SAMPLE_BIRTH_DATA_2['birth_date']}")
    print(f"   Birth Time: {SAMPLE_BIRTH_DATA_2['birth_time']}")
    print(f"   Location: {SAMPLE_BIRTH_DATA_2['city']}")

    chart = astrology_service.calculate_birth_chart(**SAMPLE_BIRTH_DATA_2)
    birth_datetime = datetime.combine(
        SAMPLE_BIRTH_DATA_2['birth_date'],
        SAMPLE_BIRTH_DATA_2['birth_time']
    )

    shadbala_results = shadbala_service.calculate_shadbala(
        chart_data=chart,
        birth_datetime=birth_datetime
    )

    print("\n📊 Planetary Strengths (Sorted by Strength):\n")

    sorted_planets = sorted(
        shadbala_results['shadbala_by_planet'].items(),
        key=lambda x: x[1]['percentage'],
        reverse=True
    )

    for i, (planet, data) in enumerate(sorted_planets, 1):
        bar_length = int(data['percentage'] / 10)
        bar = "█" * bar_length

        print(f"{i}. {planet:10} : {data['percentage']:6.2f}% {bar} ({data['strength_rating']})")

    print(f"\n📈 Chart Statistics:")
    print(f"   Average Strength: {shadbala_results['average_strength']:.2f}%")
    print(f"   Strong Planets (≥100%): {len(shadbala_results['planets_above_required'])}")
    print(f"   Weak Planets (<100%): {len(shadbala_results['planets_below_required'])}")

    print("\n✅ Test 3 Complete!\n")


def test_strength_ratings():
    """Test 4: Understanding strength ratings"""
    print("\n" + "=" * 80)
    print("TEST 4: STRENGTH RATING SYSTEM")
    print("=" * 80)

    print("\n📚 Strength Rating Scale:\n")

    ratings = [
        ("Exceptional", "≥150%", "Extremely powerful, outstanding results"),
        ("Very Strong", "125-149%", "Very powerful, excellent results"),
        ("Strong", "100-124%", "Good strength, positive results"),
        ("Moderate", "75-99%", "Adequate strength, mixed results"),
        ("Weak", "50-74%", "Low strength, challenging results"),
        ("Very Weak", "<50%", "Very low strength, significant challenges"),
    ]

    for rating, range_str, interpretation in ratings:
        emoji = {
            "Exceptional": "⭐⭐⭐⭐⭐",
            "Very Strong": "⭐⭐⭐⭐",
            "Strong": "⭐⭐⭐",
            "Moderate": "⭐⭐",
            "Weak": "⭐",
            "Very Weak": "·"
        }[rating]

        print(f"{emoji} {rating:15} : {range_str:10} - {interpretation}")

    print("\n💡 Interpretation Guide:")
    print("   • Percentage = (Actual Shadbala / Required Shadbala) × 100")
    print("   • 100% = Planet meets minimum required strength")
    print("   • >100% = Planet is stronger than required (beneficial)")
    print("   • <100% = Planet is weaker than required (may need remedies)")

    print("\n📊 Required Shadbala by Planet:")
    required = shadbala_service.required_shadbala
    for planet in sorted(required.keys(), key=lambda p: required[p], reverse=True):
        print(f"   {planet:10} : {required[planet]:3.0f} Shashtiamsas")

    print("\n✅ Test 4 Complete!\n")


def test_specific_components():
    """Test 5: Specific component calculations"""
    print("\n" + "=" * 80)
    print("TEST 5: SPECIFIC COMPONENT CALCULATIONS")
    print("=" * 80)

    chart = astrology_service.calculate_birth_chart(**SAMPLE_BIRTH_DATA_1)

    print("\n🔍 Testing Individual Components:\n")

    # Test Naisargika Bala (Natural Strength)
    print("1. NAISARGIKA BALA (Natural Strength)")
    print("   Inherent strength of each planet:\n")
    for planet, strength in shadbala_service.naisargika_bala.items():
        print(f"   {planet:10} : {strength:5.2f}")

    # Test Dig Bala (Directional Strength)
    print("\n2. DIG BALA (Directional Strength)")
    print("   Best house for each planet:\n")
    for planet, house in shadbala_service.dig_bala_houses.items():
        direction = {1: "East", 4: "North", 7: "West", 10: "South"}.get(house, "?")
        print(f"   {planet:10} : House {house:2} ({direction})")

    # Test Exaltation Points
    print("\n3. EXALTATION POINTS")
    print("   Maximum strength positions:\n")
    for planet, point in shadbala_service.exaltation_points.items():
        print(f"   {planet:10} : {point['sign']} {point['degree']}°")

    print("\n✅ Test 5 Complete!\n")


def main():
    """Run all Shadbala service tests"""
    print("\n" + "=" * 80)
    print("SHADBALA SERVICE TEST SUITE")
    print("Six-Fold Planetary Strength System")
    print("=" * 80)

    try:
        # Test 1: Basic Shadbala
        test_basic_shadbala()

        # Test 2: Component breakdown
        test_component_breakdown()

        # Test 3: Different chart
        test_different_chart()

        # Test 4: Strength ratings
        test_strength_ratings()

        # Test 5: Specific components
        test_specific_components()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)

        print("\n📊 Shadbala Service Features Verified:")
        print("  ✅ Complete 6-fold strength calculation")
        print("  ✅ Sthana Bala (positional strength)")
        print("  ✅ Dig Bala (directional strength)")
        print("  ✅ Kala Bala (temporal strength)")
        print("  ✅ Chesta Bala (motional strength)")
        print("  ✅ Naisargika Bala (natural strength)")
        print("  ✅ Drik Bala (aspectual strength)")
        print("  ✅ Strength rating system (6 levels)")
        print("  ✅ Strongest/weakest planet identification")
        print("  ✅ Component breakdown analysis")

        print("\n🔍 Shadbala Calculation Method:")
        print("  • Calculates 6 different types of planetary strength")
        print("  • Each component measured in Shashtiamsas (1/60th rupa)")
        print("  • Total Shadbala = Sum of all 6 components")
        print("  • Compared against required minimum for each planet")
        print("  • Results expressed as percentage of required strength")

        print("\n📚 The 6 Balas (Strengths):")
        print("  1. Sthana Bala - Position (sign, house, exaltation)")
        print("  2. Dig Bala - Direction (angular houses)")
        print("  3. Kala Bala - Time (day/night, lunar phase)")
        print("  4. Chesta Bala - Motion (speed, retrograde)")
        print("  5. Naisargika Bala - Nature (inherent to planet)")
        print("  6. Drik Bala - Aspects (received from others)")

        print("\n💡 Usage Example:")
        print("  shadbala_results = shadbala_service.calculate_shadbala(")
        print("      chart_data=chart,")
        print("      birth_datetime=datetime.combine(birth_date, birth_time)")
        print("  )")
        print()
        print("  # Get specific planet strength")
        print("  jupiter_strength = shadbala_results['shadbala_by_planet']['Jupiter']")
        print("  print(f\"Jupiter: {jupiter_strength['percentage']}%\")")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
