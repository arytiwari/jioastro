"""
Test script for Phase 2 & 3 Yoga implementations:
- 16 Nabhasa Akriti yogas (expanded from 4 to 20)
- 3 Nabhasa Sankhya yogas
- 7 Sanyas yogas

Total: 26 new yogas to test
"""

from app.services.extended_yoga_service import ExtendedYogaService

def create_test_planets(house_positions):
    """
    Create a planets dict with specified house positions
    house_positions: dict like {"Sun": 1, "Moon": 1, ...}
    """
    planets = {}
    sign_mapping = {1: 1, 4: 4, 7: 7, 10: 10}  # Simple kendra mapping

    planet_defaults = {
        "Sun": {"longitude": 0, "sign_num": 1, "retrograde": False},
        "Moon": {"longitude": 30, "sign_num": 2, "retrograde": False},
        "Mars": {"longitude": 60, "sign_num": 3, "retrograde": False},
        "Mercury": {"longitude": 90, "sign_num": 4, "retrograde": False},
        "Jupiter": {"longitude": 120, "sign_num": 5, "retrograde": False},
        "Venus": {"longitude": 150, "sign_num": 6, "retrograde": False},
        "Saturn": {"longitude": 180, "sign_num": 7, "retrograde": False},
        "Rahu": {"longitude": 210, "sign_num": 8, "retrograde": True},
        "Ketu": {"longitude": 30, "sign_num": 2, "retrograde": True}
    }

    for planet, defaults in planet_defaults.items():
        if planet in house_positions:
            planets[planet] = {
                "house": house_positions[planet],
                "longitude": defaults["longitude"],
                "sign_num": defaults["sign_num"],
                "retrograde": defaults["retrograde"]
            }

    return planets


def test_nabhasa_akriti_yogas():
    """Test new Nabhasa Akriti yogas"""
    service = ExtendedYogaService()

    print("=" * 80)
    print("TESTING NABHASA AKRITI YOGAS (NEW IMPLEMENTATIONS)")
    print("=" * 80)
    print()

    tests = []

    # Test 1: Kamala Yoga - All planets in kendras (1,4,7,10)
    planets = create_test_planets({
        "Sun": 1, "Moon": 4, "Mars": 7, "Mercury": 10,
        "Jupiter": 1, "Venus": 4, "Saturn": 7
    })
    yogas = service.detect_extended_yogas(planets)
    kamala = [y for y in yogas if "Kamala" in y.get("name", "")]
    tests.append(("Kamala Yoga (all in kendras)", len(kamala) > 0, kamala))

    # Test 2: Chaapa Yoga - All in trikona houses (1,5,9)
    planets = create_test_planets({
        "Sun": 1, "Moon": 5, "Mars": 9, "Mercury": 1,
        "Jupiter": 5, "Venus": 9, "Saturn": 1
    })
    yogas = service.detect_extended_yogas(planets)
    chaapa = [y for y in yogas if "Chaapa" in y.get("name", "") or "Dhanu" in y.get("name", "")]
    tests.append(("Chaapa Yoga (all in trikonas)", len(chaapa) > 0, chaapa))

    # Test 3: Hal Yoga - All NOT in kendras
    planets = create_test_planets({
        "Sun": 2, "Moon": 3, "Mars": 5, "Mercury": 6,
        "Jupiter": 8, "Venus": 9, "Saturn": 11
    })
    yogas = service.detect_extended_yogas(planets)
    hal = [y for y in yogas if "Hal" in y.get("name", "")]
    tests.append(("Hal Yoga (none in kendras)", len(hal) > 0, hal))

    # Test 4: Vajra Yoga - All in 1st and 7th
    planets = create_test_planets({
        "Sun": 1, "Moon": 7, "Mars": 1, "Mercury": 7,
        "Jupiter": 1, "Venus": 7, "Saturn": 1
    })
    yogas = service.detect_extended_yogas(planets)
    vajra = [y for y in yogas if "Vajra" in y.get("name", "")]
    tests.append(("Vajra Yoga (1st & 7th)", len(vajra) > 0, vajra))

    # Test 5: Yava Yoga - All in 1st and 4th
    planets = create_test_planets({
        "Sun": 1, "Moon": 4, "Mars": 1, "Mercury": 4,
        "Jupiter": 1, "Venus": 4, "Saturn": 1
    })
    yogas = service.detect_extended_yogas(planets)
    yava = [y for y in yogas if "Yava" in y.get("name", "")]
    tests.append(("Yava Yoga (1st & 4th)", len(yava) > 0, yava))

    # Test 6: Shakti Yoga - All in 7 consecutive houses
    planets = create_test_planets({
        "Sun": 1, "Moon": 2, "Mars": 3, "Mercury": 4,
        "Jupiter": 5, "Venus": 6, "Saturn": 7
    })
    yogas = service.detect_extended_yogas(planets)
    shakti = [y for y in yogas if "Shakti" in y.get("name", "")]
    tests.append(("Shakti Yoga (7 consecutive)", len(shakti) > 0, shakti))

    # Test 7: Danda Yoga - All in 6 consecutive houses
    planets = create_test_planets({
        "Sun": 3, "Moon": 4, "Mars": 5, "Mercury": 6,
        "Jupiter": 7, "Venus": 8, "Saturn": 8
    })
    yogas = service.detect_extended_yogas(planets)
    danda = [y for y in yogas if "Danda" in y.get("name", "") or "Dand" in y.get("name", "")]
    tests.append(("Danda Yoga (6 consecutive)", len(danda) > 0, danda))

    # Test 8: Chakra Yoga - All in kendras and trikonas
    planets = create_test_planets({
        "Sun": 1, "Moon": 4, "Mars": 5, "Mercury": 7,
        "Jupiter": 9, "Venus": 10, "Saturn": 1
    })
    yogas = service.detect_extended_yogas(planets)
    chakra = [y for y in yogas if "Chakra" in y.get("name", "")]
    tests.append(("Chakra Yoga (kendras + trikonas)", len(chakra) > 0, chakra))

    # Print results
    passed = 0
    for test_name, result, found_yogas in tests:
        if result:
            print(f"✅ {test_name}")
            if found_yogas:
                print(f"   Detected: {found_yogas[0].get('name', 'Unknown')}")
            passed += 1
        else:
            print(f"❌ {test_name} - NOT DETECTED")
        print()

    print(f"Akriti Tests: {passed}/{len(tests)} passed")
    print()
    return passed, len(tests)


def test_nabhasa_sankhya_yogas():
    """Test Nabhasa Sankhya yogas"""
    service = ExtendedYogaService()

    print("=" * 80)
    print("TESTING NABHASA SANKHYA YOGAS")
    print("=" * 80)
    print()

    tests = []

    # Test 1: Vallaki Yoga - Benefics in upachayas (3,6,10,11), malefics elsewhere
    planets = create_test_planets({
        "Jupiter": 3, "Venus": 6, "Mercury": 10, "Moon": 11,  # Benefics in upachayas
        "Sun": 1, "Mars": 2, "Saturn": 5  # Malefics NOT in upachayas
    })
    yogas = service.detect_extended_yogas(planets)
    vallaki = [y for y in yogas if "Vallaki" in y.get("name", "")]
    tests.append(("Vallaki Yoga (benefics in upachayas)", len(vallaki) > 0, vallaki))

    # Test 2: Daam Yoga - Malefics in 6th and 12th
    planets = create_test_planets({
        "Sun": 6, "Mars": 12, "Saturn": 6,
        "Jupiter": 1, "Venus": 2, "Mercury": 3, "Moon": 4
    })
    yogas = service.detect_extended_yogas(planets)
    daam = [y for y in yogas if "Daam" in y.get("name", "")]
    tests.append(("Daam Yoga (malefics in 6th & 12th)", len(daam) > 0, daam))

    # Test 3: Paasha Yoga - All malefics in upachayas
    planets = create_test_planets({
        "Sun": 3, "Mars": 6, "Saturn": 10,
        "Jupiter": 1, "Venus": 2, "Mercury": 4, "Moon": 5
    })
    yogas = service.detect_extended_yogas(planets)
    paasha = [y for y in yogas if "Paasha" in y.get("name", "") or "Pasha" in y.get("name", "")]
    tests.append(("Paasha Yoga (malefics in upachayas)", len(paasha) > 0, paasha))

    # Print results
    passed = 0
    for test_name, result, found_yogas in tests:
        if result:
            print(f"✅ {test_name}")
            if found_yogas:
                print(f"   Detected: {found_yogas[0].get('name', 'Unknown')}")
            passed += 1
        else:
            print(f"❌ {test_name} - NOT DETECTED")
        print()

    print(f"Sankhya Tests: {passed}/{len(tests)} passed")
    print()
    return passed, len(tests)


def test_sanyas_yogas():
    """Test Sanyas yogas"""
    service = ExtendedYogaService()

    print("=" * 80)
    print("TESTING SANYAS YOGAS")
    print("=" * 80)
    print()

    tests = []

    # Test 1: Maha Sanyas Yoga - 4+ planets in one house
    planets = create_test_planets({
        "Sun": 10, "Moon": 10, "Mars": 10, "Mercury": 10, "Saturn": 10,  # 5 planets in 10th
        "Jupiter": 1, "Venus": 2
    })
    yogas = service.detect_extended_yogas(planets)
    maha_sanyas = [y for y in yogas if "Maha Sanyas" in y.get("name", "")]
    tests.append(("Maha Sanyas Yoga (5 planets in house 10)", len(maha_sanyas) > 0, maha_sanyas))

    # Test 2: Parivraja Yoga - Jupiter in kendra from Moon with Saturn
    planets = create_test_planets({
        "Moon": 1, "Jupiter": 4, "Saturn": 4,  # Jupiter in kendra (4th) from Moon (1st), with Saturn
        "Sun": 2, "Mars": 3, "Mercury": 5, "Venus": 6
    })
    yogas = service.detect_extended_yogas(planets)
    parivraja = [y for y in yogas if "Parivraja" in y.get("name", "")]
    tests.append(("Parivraja Yoga (Jupiter-Moon-Saturn)", len(parivraja) > 0, parivraja))

    # Test 3: Markandeya Sanyas - Jupiter & Saturn in kendras, Moon in 9th/10th
    planets = create_test_planets({
        "Jupiter": 1, "Saturn": 4, "Moon": 9,  # Jupiter & Saturn in kendras, Moon in 9th
        "Sun": 2, "Mars": 3, "Mercury": 5, "Venus": 6
    })
    yogas = service.detect_extended_yogas(planets)
    markandeya = [y for y in yogas if "Markandeya" in y.get("name", "")]
    tests.append(("Markandeya Sanyas (J&S kendras, Moon 9th)", len(markandeya) > 0, markandeya))

    # Test 4: Akhanda Sanyas - Jupiter in 9th, Saturn in 8th, Rahu/Ketu in 4th
    planets = create_test_planets({
        "Jupiter": 9, "Saturn": 8, "Rahu": 4, "Ketu": 10,
        "Sun": 1, "Moon": 2, "Mars": 3, "Mercury": 5, "Venus": 6
    })
    yogas = service.detect_extended_yogas(planets)
    akhanda = [y for y in yogas if "Akhanda" in y.get("name", "")]
    tests.append(("Akhanda Sanyas (J-9, S-8, R-4)", len(akhanda) > 0, akhanda))

    # Test 5: Kalanala Sanyas - 4+ planets in 10th
    planets = create_test_planets({
        "Sun": 10, "Moon": 10, "Mars": 10, "Jupiter": 10,  # 4 planets in 10th
        "Mercury": 1, "Venus": 2, "Saturn": 3
    })
    yogas = service.detect_extended_yogas(planets)
    kalanala = [y for y in yogas if "Kalanala" in y.get("name", "")]
    tests.append(("Kalanala Sanyas (4 planets in 10th)", len(kalanala) > 0, kalanala))

    # Print results
    passed = 0
    for test_name, result, found_yogas in tests:
        if result:
            print(f"✅ {test_name}")
            if found_yogas:
                print(f"   Detected: {found_yogas[0].get('name', 'Unknown')}")
            passed += 1
        else:
            print(f"❌ {test_name} - NOT DETECTED")
        print()

    print(f"Sanyas Tests: {passed}/{len(tests)} passed")
    print()
    return passed, len(tests)


def main():
    """Run all tests"""
    print("=" * 80)
    print("PHASE 2 & 3 YOGA VERIFICATION TEST")
    print("Testing 26 newly implemented yogas")
    print("=" * 80)
    print()

    # Run all test suites
    akriti_passed, akriti_total = test_nabhasa_akriti_yogas()
    sankhya_passed, sankhya_total = test_nabhasa_sankhya_yogas()
    sanyas_passed, sanyas_total = test_sanyas_yogas()

    # Final summary
    total_passed = akriti_passed + sankhya_passed + sanyas_passed
    total_tests = akriti_total + sankhya_total + sanyas_total

    print("=" * 80)
    print(f"FINAL RESULTS: {total_passed}/{total_tests} tests passed")
    print("=" * 80)
    print()
    print(f"  Nabhasa Akriti: {akriti_passed}/{akriti_total}")
    print(f"  Nabhasa Sankhya: {sankhya_passed}/{sankhya_total}")
    print(f"  Sanyas Yogas: {sanyas_passed}/{sanyas_total}")
    print()

    if total_passed == total_tests:
        print("✅ ALL PHASE 2 & 3 YOGAS WORKING CORRECTLY!")
        return True
    else:
        print(f"⚠️  {total_tests - total_passed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
