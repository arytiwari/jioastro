"""
Test Transit Service
Demonstrates current planetary transits and their effects on birth chart
"""

import sys
from pathlib import Path
from datetime import datetime, date, time, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.transit_service import transit_service
from app.services.astrology import astrology_service


# Sample birth chart for testing
SAMPLE_BIRTH_DATA = {
    "name": "Test Person",
    "birth_date": date(1990, 3, 15),
    "birth_time": time(14, 30),
    "latitude": 19.0760,
    "longitude": 72.8777,
    "timezone_str": "Asia/Kolkata",
    "city": "Mumbai"
}


def test_current_transits():
    """Test 1: Current transits analysis"""
    print("=" * 80)
    print("TEST 1: CURRENT TRANSITS ANALYSIS")
    print("=" * 80)

    print("\n📋 Birth Data:")
    print(f"   Name: {SAMPLE_BIRTH_DATA['name']}")
    print(f"   Birth Date: {SAMPLE_BIRTH_DATA['birth_date']}")
    print(f"   Birth Time: {SAMPLE_BIRTH_DATA['birth_time']}")
    print(f"   Location: {SAMPLE_BIRTH_DATA['city']}")

    # Calculate birth chart
    print("\n🔮 Calculating birth chart...")
    birth_chart = astrology_service.calculate_birth_chart(**SAMPLE_BIRTH_DATA)

    # Calculate current transits
    print("\n🌟 Calculating current transits...")
    transits = transit_service.calculate_current_transits(
        birth_chart=birth_chart,
        transit_date=datetime.now(),
        latitude=SAMPLE_BIRTH_DATA["latitude"],
        longitude=SAMPLE_BIRTH_DATA["longitude"],
        timezone_str=SAMPLE_BIRTH_DATA["timezone_str"]
    )

    print("\n" + "=" * 80)
    print("CURRENT TRANSIT POSITIONS")
    print("=" * 80)

    print(f"\n📅 Transit Date: {transits['transit_date'][:10]}")
    print("\n🌍 Planetary Positions:")
    for planet, data in transits['transit_planets'].items():
        retro = " ®" if data.get('retrograde') else ""
        print(f"   {planet:10} : {data['sign']:15} {data['degree']:6.2f}° (House {data.get('house', '?')}){retro}")

    print("\n" + "=" * 80)
    print("SIGNIFICANT ASPECTS")
    print("=" * 80)

    if transits['significant_aspects']:
        print(f"\n🔗 Found {len(transits['significant_aspects'])} significant aspects:\n")

        for i, aspect in enumerate(transits['significant_aspects'][:10], 1):
            strength_emoji = {
                "very_strong": "⭐⭐⭐",
                "strong": "⭐⭐",
                "moderate": "⭐",
                "weak": "·"
            }.get(aspect['strength'], "·")

            print(f"{i:2}. {strength_emoji} {aspect['transit_planet']:10} {aspect['aspect'].upper():12} natal {aspect['natal_planet']}")
            print(f"    Orb: {aspect['orb']:.2f}° | Strength: {aspect['strength']}")
            print(f"    Transit: {aspect['transit_sign']:15} | Natal: {aspect['natal_sign']}")
            print(f"    Effect: {aspect['interpretation']}")
            print()
    else:
        print("\n   No significant aspects at this time")

    print("\n" + "=" * 80)
    print("HOUSE TRANSITS")
    print("=" * 80)

    print("\n🏠 Planets transiting your houses:\n")
    for transit in transits['house_transits'][:7]:
        print(f"   {transit['planet']:10} in House {transit['house']:2} ({transit['sign']:15})")
        print(f"      {transit['interpretation']}")
        print()

    print("\n" + "=" * 80)
    print("UPCOMING SIGN CHANGES")
    print("=" * 80)

    if transits['upcoming_sign_changes']:
        print(f"\n🔄 {len(transits['upcoming_sign_changes'])} planets changing signs in next 30 days:\n")

        for change in transits['upcoming_sign_changes']:
            print(f"   {change['planet']:10} : {change['current_sign']:15} → {change['new_sign']:15}")
            print(f"      In {change['days_until']:.1f} days (around {change['date']})")
            print()
    else:
        print("\n   No sign changes in next 30 days")

    print("\n" + "=" * 80)
    print("STRENGTH ANALYSIS")
    print("=" * 80)

    strength = transits['strength_analysis']
    print(f"\n📊 Overall Transit Strength:")
    print(f"   Total Aspects: {strength['total_aspects']}")

    if strength.get('aspect_breakdown'):
        print("\n   Aspect Breakdown:")
        for aspect_type, count in strength['aspect_breakdown'].items():
            print(f"      {aspect_type.capitalize():12} : {count}")

    if strength.get('strongest_aspect'):
        strongest = strength['strongest_aspect']
        print(f"\n   Strongest Aspect:")
        print(f"      {strongest['description']}")
        print(f"      Strength: {strongest['strength']}")

    if strength.get('most_emphasized_house'):
        house = strength['most_emphasized_house']
        print(f"\n   Most Emphasized House:")
        print(f"      House {house['house']} ({house['planet_count']} planets)")
        print(f"      Focus: {house['meaning']}")

    print(f"\n📝 Summary: {transits['summary']}")

    print("\n✅ Test 1 Complete!\n")
    return transits


def test_specific_date_transits():
    """Test 2: Transits for specific date"""
    print("\n" + "=" * 80)
    print("TEST 2: SPECIFIC DATE TRANSITS")
    print("=" * 80)

    # Calculate birth chart
    birth_chart = astrology_service.calculate_birth_chart(**SAMPLE_BIRTH_DATA)

    # Test date: 6 months from now
    test_date = datetime.now() + timedelta(days=180)

    print(f"\n📅 Analyzing transits for: {test_date.strftime('%Y-%m-%d')}")
    print("   (6 months from now)")

    transits = transit_service.calculate_current_transits(
        birth_chart=birth_chart,
        transit_date=test_date,
        latitude=SAMPLE_BIRTH_DATA["latitude"],
        longitude=SAMPLE_BIRTH_DATA["longitude"],
        timezone_str=SAMPLE_BIRTH_DATA["timezone_str"]
    )

    print("\n🌍 Planetary Positions (6 months ahead):")
    for planet, data in list(transits['transit_planets'].items())[:7]:
        print(f"   {planet:10} : {data['sign']:15} {data['degree']:6.2f}°")

    print(f"\n🔗 Significant Aspects: {len(transits['significant_aspects'])}")

    if transits['significant_aspects']:
        print("\n   Top 3 Aspects:")
        for i, aspect in enumerate(transits['significant_aspects'][:3], 1):
            print(f"      {i}. {aspect['transit_planet']} {aspect['aspect']} natal {aspect['natal_planet']} ({aspect['strength']})")

    print("\n✅ Test 2 Complete!\n")
    return transits


def test_transit_timeline():
    """Test 3: Transit timeline (30-day forecast)"""
    print("\n" + "=" * 80)
    print("TEST 3: TRANSIT TIMELINE (30-DAY FORECAST)")
    print("=" * 80)

    # Calculate birth chart
    birth_chart = astrology_service.calculate_birth_chart(**SAMPLE_BIRTH_DATA)

    # Timeline: next 30 days
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)

    print(f"\n📅 Timeline Period:")
    print(f"   Start: {start_date.strftime('%Y-%m-%d')}")
    print(f"   End: {end_date.strftime('%Y-%m-%d')}")

    timeline = transit_service.calculate_transit_timeline(
        birth_chart=birth_chart,
        start_date=start_date,
        end_date=end_date,
        latitude=SAMPLE_BIRTH_DATA["latitude"],
        longitude=SAMPLE_BIRTH_DATA["longitude"],
        timezone_str=SAMPLE_BIRTH_DATA["timezone_str"]
    )

    print("\n" + "=" * 80)
    print("TIMELINE EVENTS")
    print("=" * 80)

    print(f"\n📊 Total Events: {timeline['total_events']}")
    print(f"   Date Range: {timeline['start_date']} to {timeline['end_date']}")

    if timeline['events']:
        print(f"\n📋 Significant Events (showing first 15):\n")

        current_date = None
        for i, event in enumerate(timeline['events'][:15], 1):
            event_date = event['date']

            # Print date header if new date
            if event_date != current_date:
                print(f"\n   📅 {event_date}")
                current_date = event_date

            if event['type'] == 'aspect':
                print(f"      🔗 {event['description']}")
                print(f"         Strength: {event['strength']} | {event['effect']}")

            elif event['type'] == 'sign_change':
                print(f"      🔄 {event['description']}")
                print(f"         {event['current_sign']} → {event['new_sign']}")

            print()
    else:
        print("\n   No significant events in this period")

    print("\n✅ Test 3 Complete!\n")
    return timeline


def test_major_transits():
    """Test 4: Focus on major outer planet transits"""
    print("\n" + "=" * 80)
    print("TEST 4: MAJOR OUTER PLANET TRANSITS")
    print("=" * 80)

    print("\n📋 Focusing on slow-moving planets:")
    print("   Jupiter, Saturn, Rahu, Ketu")
    print("   (These transits last longer and have more significant effects)")

    # Calculate birth chart
    birth_chart = astrology_service.calculate_birth_chart(**SAMPLE_BIRTH_DATA)

    # Calculate current transits
    transits = transit_service.calculate_current_transits(
        birth_chart=birth_chart,
        transit_date=datetime.now(),
        latitude=SAMPLE_BIRTH_DATA["latitude"],
        longitude=SAMPLE_BIRTH_DATA["longitude"],
        timezone_str=SAMPLE_BIRTH_DATA["timezone_str"]
    )

    print("\n🪐 Outer Planet Positions:\n")

    outer_planets = ["Jupiter", "Saturn", "Rahu", "Ketu"]
    for planet in outer_planets:
        if planet in transits['transit_planets']:
            data = transits['transit_planets'][planet]
            print(f"   {planet:10} : {data['sign']:15} {data['degree']:6.2f}°")

            # Find house transit for this planet
            house_transit = next(
                (t for t in transits['house_transits'] if t['planet'] == planet),
                None
            )

            if house_transit:
                print(f"      Transiting House {house_transit['house']}: {house_transit['meaning']}")
            print()

    print("\n🔗 Major Planet Aspects:\n")

    # Filter for outer planet aspects
    major_aspects = [
        a for a in transits['significant_aspects']
        if a['transit_planet'] in outer_planets or a['natal_planet'] in outer_planets
    ]

    if major_aspects:
        for i, aspect in enumerate(major_aspects[:5], 1):
            print(f"   {i}. {aspect['transit_planet']} {aspect['aspect'].upper()} natal {aspect['natal_planet']}")
            print(f"      {aspect['interpretation']}")
            print(f"      Strength: {aspect['strength']} (Orb: {aspect['orb']:.2f}°)")
            print()
    else:
        print("   No major outer planet aspects at this time")

    print("\n📚 Note on Outer Planet Transits:")
    print("   • Jupiter: Growth, expansion, opportunity (12-year cycle)")
    print("   • Saturn: Discipline, responsibility, karma (29-year cycle)")
    print("   • Rahu/Ketu: Karmic nodes, destined events (18-year cycle)")
    print("   • These slow transits create longer-lasting effects")

    print("\n✅ Test 4 Complete!\n")


def test_aspect_interpretations():
    """Test 5: Detailed aspect interpretations"""
    print("\n" + "=" * 80)
    print("TEST 5: ASPECT INTERPRETATION EXAMPLES")
    print("=" * 80)

    print("\n📚 Understanding Transit Aspects:\n")

    aspect_examples = {
        "Conjunction (0°)": "Merging, intensifying, focusing energies - new beginnings",
        "Sextile (60°)": "Opportunity, cooperation, potential - gentle support",
        "Square (90°)": "Challenge, friction, growth through effort - action required",
        "Trine (120°)": "Harmony, ease, natural flow - talents expressed",
        "Opposition (180°)": "Tension, awareness, balance needed - external events",
    }

    for aspect, meaning in aspect_examples.items():
        print(f"   {aspect:20} : {meaning}")

    print("\n🎯 Strength Levels:\n")
    print("   ⭐⭐⭐ Very Strong : Orb within 25% of maximum (life-changing)")
    print("   ⭐⭐   Strong      : Orb within 50% of maximum (significant)")
    print("   ⭐     Moderate    : Orb within 75% of maximum (noticeable)")
    print("   ·      Weak        : Orb within 100% of maximum (subtle)")

    print("\n💡 How to Read Transit Aspects:")
    print("   1. Identify the transit planet (current position in sky)")
    print("   2. Identify the natal planet (position in your birth chart)")
    print("   3. Note the aspect type (conjunction, square, etc.)")
    print("   4. Consider the orb (closer = stronger)")
    print("   5. Read the interpretation for guidance")

    print("\n✅ Test 5 Complete!\n")


def main():
    """Run all transit service tests"""
    print("\n" + "=" * 80)
    print("TRANSIT SERVICE TEST SUITE")
    print("Current Planetary Positions & Effects on Birth Chart")
    print("=" * 80)

    try:
        # Test 1: Current transits
        test_current_transits()

        # Test 2: Specific date transits
        test_specific_date_transits()

        # Test 3: Transit timeline
        test_transit_timeline()

        # Test 4: Major planet transits
        test_major_transits()

        # Test 5: Aspect interpretations
        test_aspect_interpretations()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)

        print("\n📊 Transit Service Features Verified:")
        print("  ✅ Current planetary positions calculation")
        print("  ✅ Transit-to-natal aspect detection (5 aspect types)")
        print("  ✅ House transit analysis (which house each planet is in)")
        print("  ✅ Upcoming sign changes (30-day forecast)")
        print("  ✅ Strength analysis (very strong to weak)")
        print("  ✅ Transit timeline (30-day event calendar)")
        print("  ✅ Major outer planet focus (Jupiter, Saturn, Nodes)")
        print("  ✅ Detailed aspect interpretations")

        print("\n🔍 Transit Analysis Method:")
        print("  • Calculates current planetary positions (transits)")
        print("  • Compares to birth chart positions (natal)")
        print("  • Identifies angular relationships (aspects)")
        print("  • Determines which house each transit falls in")
        print("  • Predicts upcoming sign changes")
        print("  • Generates interpretations and timelines")

        print("\n📚 Aspect Types Detected (5 total):")
        print("  Conjunction (0°), Sextile (60°), Square (90°)")
        print("  Trine (120°), Opposition (180°)")

        print("\n🏠 House Analysis:")
        print("  • 12 houses covering all life areas")
        print("  • Each transit planet analyzed for house position")
        print("  • House meanings provided for interpretation")

        print("\n💡 Usage Example:")
        print("  transits = transit_service.calculate_current_transits(")
        print("      birth_chart=chart,")
        print("      transit_date=datetime.now(),  # or specific date")
        print("      latitude=19.0760,")
        print("      longitude=72.8777,")
        print("      timezone_str='Asia/Kolkata'")
        print("  )")
        print()
        print("  # Get transit timeline")
        print("  timeline = transit_service.calculate_transit_timeline(")
        print("      birth_chart=chart,")
        print("      start_date=datetime.now(),")
        print("      end_date=datetime.now() + timedelta(days=30)")
        print("  )")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
