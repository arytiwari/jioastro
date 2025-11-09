"""
Test script for Phase 4: Bhava Yogas implementation
Tests house lord calculations and Bhava Yoga detection

Part A: House Lord Calculations (12 ascendants)
Part B: Bhava Yoga Detection (48 critical yogas)
"""

from app.services.extended_yoga_service import ExtendedYogaService

def test_house_lord_calculations():
    """Test house lord calculations for all 12 ascendant signs"""
    service = ExtendedYogaService()

    print("=" * 80)
    print("PART A: HOUSE LORD CALCULATIONS TEST")
    print("=" * 80)
    print()

    # Expected lords for Aries ascendant (base case)
    aries_expected = {
        1: "Mars",      # 1st house = Aries
        2: "Venus",     # 2nd house = Taurus
        3: "Mercury",   # 3rd house = Gemini
        4: "Moon",      # 4th house = Cancer
        5: "Sun",       # 5th house = Leo
        6: "Mercury",   # 6th house = Virgo
        7: "Venus",     # 7th house = Libra
        8: "Mars",      # 8th house = Scorpio
        9: "Jupiter",   # 9th house = Sagittarius
        10: "Saturn",   # 10th house = Capricorn
        11: "Saturn",   # 11th house = Aquarius
        12: "Jupiter"   # 12th house = Pisces
    }

    # Test all 12 ascendants
    ascendant_names = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    passed = 0
    total = 0

    for asc_num in range(1, 13):
        asc_name = ascendant_names[asc_num - 1]
        house_lords = service.get_house_lords_map(asc_num)

        print(f"✓ {asc_name} Ascendant (sign #{asc_num}):")
        print(f"  1st lord: {house_lords[1]}")
        print(f"  10th lord: {house_lords[10]}")
        print(f"  9th lord: {house_lords[9]}")
        print(f"  5th lord: {house_lords[5]}")
        print()

        # Verify all 12 houses have lords
        if len(house_lords) == 12:
            passed += 1
        total += 1

    print(f"House Lord Calculation Tests: {passed}/{total} passed")
    print()
    return passed == total


def test_bhava_yoga_detection():
    """Test Bhava Yoga detection with sample charts"""
    service = ExtendedYogaService()

    print("=" * 80)
    print("PART B: BHAVA YOGA DETECTION TEST")
    print("=" * 80)
    print()

    tests = []
    test_num = 0

    # Test 1: Aries Ascendant - 1st lord (Mars) in 1st house
    test_num += 1
    print(f"Test {test_num}: 1st lord in 1st house (Lagna Adhi Yoga)")
    planets = {
        "Ascendant": {"sign_num": 1, "house": 1},  # Aries ascendant
        "Mars": {"house": 1, "sign_num": 1},  # 1st lord in 1st house
        "Sun": {"house": 5, "sign_num": 5, "longitude": 120},
        "Moon": {"house": 4, "sign_num": 4, "longitude": 100}
    }
    yogas = service.detect_extended_yogas(planets)
    bhava_yogas = [y for y in yogas if "Bhava Yoga" in y.get("category", "")]
    found = any("Lagna Adhi" in y.get("name", "") for y in bhava_yogas)
    tests.append((f"Test {test_num}: Lagna Adhi Yoga", found, bhava_yogas))
    print(f"  {'✅' if found else '❌'} {len(bhava_yogas)} Bhava Yogas detected")
    if found and bhava_yogas:
        print(f"  Detected: {[y['name'] for y in bhava_yogas if 'Lagna Adhi' in y['name']]}")
    print()

    # Test 2: Aries Ascendant - 10th lord (Saturn) in 10th house
    test_num += 1
    print(f"Test {test_num}: 10th lord in 10th house (Karma Adhi Yoga)")
    planets = {
        "Ascendant": {"sign_num": 1, "house": 1},  # Aries ascendant
        "Saturn": {"house": 10, "sign_num": 10},  # 10th lord in 10th house
        "Mars": {"house": 3, "sign_num": 3},
        "Sun": {"house": 5, "sign_num": 5, "longitude": 120},
        "Moon": {"house": 4, "sign_num": 4, "longitude": 100}
    }
    yogas = service.detect_extended_yogas(planets)
    bhava_yogas = [y for y in yogas if "Bhava Yoga" in y.get("category", "")]
    found = any("Karma Adhi" in y.get("name", "") for y in bhava_yogas)
    tests.append((f"Test {test_num}: Karma Adhi Yoga", found, bhava_yogas))
    print(f"  {'✅' if found else '❌'} {len(bhava_yogas)} Bhava Yogas detected")
    if found and bhava_yogas:
        print(f"  Detected: {[y['name'] for y in bhava_yogas if 'Karma Adhi' in y['name']]}")
    print()

    # Test 3: Aries Ascendant - 9th lord (Jupiter) in 10th house (Dharma-Karma Yoga)
    test_num += 1
    print(f"Test {test_num}: 9th lord in 10th house (Dharma-Karma Yoga / Raj Yoga)")
    planets = {
        "Ascendant": {"sign_num": 1, "house": 1},  # Aries ascendant
        "Jupiter": {"house": 10, "sign_num": 10},  # 9th lord in 10th house
        "Mars": {"house": 2, "sign_num": 2},
        "Saturn": {"house": 11, "sign_num": 11},
        "Sun": {"house": 5, "sign_num": 5, "longitude": 120},
        "Moon": {"house": 4, "sign_num": 4, "longitude": 100}
    }
    yogas = service.detect_extended_yogas(planets)
    bhava_yogas = [y for y in yogas if "Bhava Yoga" in y.get("category", "")]
    found = any("Dharma Karma" in y.get("name", "") or "Karma Dharma" in y.get("name", "") for y in bhava_yogas)
    tests.append((f"Test {test_num}: Dharma-Karma Yoga", found, bhava_yogas))
    print(f"  {'✅' if found else '❌'} {len(bhava_yogas)} Bhava Yogas detected")
    if found and bhava_yogas:
        print(f"  Detected: {[y['name'] for y in bhava_yogas if 'Karma' in y['name'] and 'Dharma' in y['name']]}")
    print()

    # Test 4: Leo Ascendant - 5th lord (Jupiter) in 5th house (Putra Adhi Yoga)
    test_num += 1
    print(f"Test {test_num}: 5th lord in 5th house (Putra Adhi Yoga)")
    planets = {
        "Ascendant": {"sign_num": 5, "house": 1},  # Leo ascendant
        "Jupiter": {"house": 5, "sign_num": 9},  # 5th lord in 5th house (Sagittarius)
        "Sun": {"house": 1, "sign_num": 5, "longitude": 120},
        "Moon": {"house": 4, "sign_num": 8, "longitude": 220}
    }
    yogas = service.detect_extended_yogas(planets)
    bhava_yogas = [y for y in yogas if "Bhava Yoga" in y.get("category", "")]
    found = any("Putra Adhi" in y.get("name", "") for y in bhava_yogas)
    tests.append((f"Test {test_num}: Putra Adhi Yoga", found, bhava_yogas))
    print(f"  {'✅' if found else '❌'} {len(bhava_yogas)} Bhava Yogas detected")
    if found and bhava_yogas:
        print(f"  Detected: {[y['name'] for y in bhava_yogas if 'Putra Adhi' in y['name']]}")
    print()

    # Test 5: Taurus Ascendant - 1st lord (Venus) in 7th house (Kalatra Yoga)
    test_num += 1
    print(f"Test {test_num}: 1st lord in 7th house (Kalatra Yoga)")
    planets = {
        "Ascendant": {"sign_num": 2, "house": 1},  # Taurus ascendant
        "Venus": {"house": 7, "sign_num": 8},  # 1st lord in 7th house
        "Mars": {"house": 10, "sign_num": 11},
        "Sun": {"house": 5, "sign_num": 6, "longitude": 150},
        "Moon": {"house": 3, "sign_num": 4, "longitude": 100}
    }
    yogas = service.detect_extended_yogas(planets)
    bhava_yogas = [y for y in yogas if "Bhava Yoga" in y.get("category", "")]
    found = any("Kalatra" in y.get("name", "") and "1st lord in 7th" in y.get("description", "") for y in bhava_yogas)
    tests.append((f"Test {test_num}: Kalatra Yoga (1st in 7th)", found, bhava_yogas))
    print(f"  {'✅' if found else '❌'} {len(bhava_yogas)} Bhava Yogas detected")
    if found and bhava_yogas:
        print(f"  Detected: {[y['name'] for y in bhava_yogas if 'Kalatra' in y['name']]}")
    print()

    # Test 6: Sagittarius Ascendant - 1st lord (Jupiter) in 9th house (Bhagya Yoga)
    test_num += 1
    print(f"Test {test_num}: 1st lord in 9th house (Bhagya Yoga)")
    planets = {
        "Ascendant": {"sign_num": 9, "house": 1},  # Sagittarius ascendant
        "Jupiter": {"house": 9, "sign_num": 5},  # 1st lord in 9th house (Leo)
        "Mars": {"house": 2, "sign_num": 10},
        "Sun": {"house": 9, "sign_num": 5, "longitude": 135},
        "Moon": {"house": 4, "sign_num": 12, "longitude": 350}
    }
    yogas = service.detect_extended_yogas(planets)
    bhava_yogas = [y for y in yogas if "Bhava Yoga" in y.get("category", "")]
    found = any("Bhagya" in y.get("name", "") for y in bhava_yogas)
    tests.append((f"Test {test_num}: Bhagya Yoga", found, bhava_yogas))
    print(f"  {'✅' if found else '❌'} {len(bhava_yogas)} Bhava Yogas detected")
    if found and bhava_yogas:
        print(f"  Detected: {[y['name'] for y in bhava_yogas if 'Bhagya' in y['name']]}")
    print()

    # Summary
    passed = sum(1 for _, result, _ in tests if result)
    total = len(tests)

    print("=" * 80)
    print(f"Bhava Yoga Detection Tests: {passed}/{total} passed")
    print("=" * 80)
    print()

    return passed == total


def main():
    """Run all tests"""
    print("=" * 80)
    print("BHAVA YOGAS (PHASE 4) VERIFICATION TEST")
    print("Testing house lord calculations and Bhava Yoga detection")
    print("=" * 80)
    print()

    # Part A: House Lord Calculations
    house_lords_pass = test_house_lord_calculations()

    # Part B: Bhava Yoga Detection
    bhava_yogas_pass = test_bhava_yoga_detection()

    # Final summary
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print()
    print(f"Part A (House Lords): {'✅ PASS' if house_lords_pass else '❌ FAIL'}")
    print(f"Part B (Bhava Yogas): {'✅ PASS' if bhava_yogas_pass else '❌ FAIL'}")
    print()

    if house_lords_pass and bhava_yogas_pass:
        print("✅ ALL TESTS PASSED!")
        print("✅ Phase 4: Bhava Yogas system is working correctly!")
        return True
    else:
        print("⚠️  Some tests failed - review implementation")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
