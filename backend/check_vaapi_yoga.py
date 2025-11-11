#!/usr/bin/env python3
"""
Check Vaapi Yoga for Arvind Kumar Tiwari
DOB: 1976-02-29 at 3:45 AM IST (GMT+5:30)
Location: Lat 28.613939, Lon 77.209021 (Delhi, India)
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from datetime import datetime, date, time
from app.services.vedic_astrology_accurate import AccurateVedicAstrology

# Birth details
birth_date_obj = date(1976, 2, 29)  # Leap year!
birth_time_obj = time(3, 45, 0)  # 3:45 AM
latitude = 28.613939
longitude = 77.209021
timezone_str = "Asia/Kolkata"  # IST

print("=" * 80)
print("VAAPI YOGA CHECK - Arvind Kumar Tiwari")
print("=" * 80)
print(f"\nBirth Details:")
print(f"  Date: 1976-02-29 (Leap Year Birthday!)")
print(f"  Time: 03:45 AM IST")
print(f"  Location: Lat {latitude}, Lon {longitude} (Delhi, India)")
print(f"  Timezone: {timezone_str}")

# Calculate chart
astro = AccurateVedicAstrology()
chart = astro.calculate_birth_chart(
    name="Arvind Kumar Tiwari",
    birth_date=birth_date_obj,
    birth_time=birth_time_obj,
    latitude=latitude,
    longitude=longitude,
    timezone_str=timezone_str,
    city="Delhi"
)

print("\n" + "=" * 80)
print("PLANETARY POSITIONS")
print("=" * 80)

planets = chart['planets']
ascendant = chart['ascendant']

# Define house types
kendra_houses = [1, 4, 7, 10]  # Angular
panaphar_houses = [2, 5, 8, 11]  # Succedent
apoklima_houses = [3, 6, 9, 12]  # Cadent

def get_house_type(house):
    if house in kendra_houses:
        return "Kendra (Angular)"
    elif house in panaphar_houses:
        return "Panaphar (Succedent)"
    elif house in apoklima_houses:
        return "Apoklima (Cadent)"
    return "Unknown"

# Print ascendant
print(f"\nAscendant:")
print(f"  Sign: {ascendant['sign']}")
print(f"  Degree: {ascendant['degree']:.2f}°")
print(f"  House: 1 (Kendra)")

# Print all planets
print(f"\nPlanets:")
main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
planet_positions = {}

for planet_name in main_planets:
    planet = planets.get(planet_name, {})
    house = planet.get('house', 0)
    sign = planet.get('sign', 'Unknown')
    degree = planet.get('degree', 0)
    house_type = get_house_type(house)
    planet_positions[planet_name] = {
        'house': house,
        'house_type': house_type,
        'sign': sign,
        'degree': degree
    }

    retro = " (R)" if planet.get('retrograde', False) else ""
    print(f"  {planet_name:8} -> House {house:2} ({house_type:20}) | {sign:12} {degree:6.2f}°{retro}")

# Check Vaapi Yoga
print("\n" + "=" * 80)
print("VAAPI YOGA ANALYSIS")
print("=" * 80)

print("\nVaapi Yoga Requirements:")
print("1. ALL 7 planets must be in Panaphar (2,5,8,11) OR Apoklima (3,6,9,12)")
print("2. NO planets in Kendra houses (1,4,7,10)")

# Count planets by house type
planets_in_kendra = []
planets_in_panaphar = []
planets_in_apoklima = []

for planet_name, data in planet_positions.items():
    house = data['house']
    if house in kendra_houses:
        planets_in_kendra.append(planet_name)
    elif house in panaphar_houses:
        planets_in_panaphar.append(planet_name)
    elif house in apoklima_houses:
        planets_in_apoklima.append(planet_name)

print(f"\nDistribution:")
print(f"  Kendra (1,4,7,10):    {len(planets_in_kendra)} planets - {', '.join(planets_in_kendra) if planets_in_kendra else 'None'}")
print(f"  Panaphar (2,5,8,11):  {len(planets_in_panaphar)} planets - {', '.join(planets_in_panaphar) if planets_in_panaphar else 'None'}")
print(f"  Apoklima (3,6,9,12):  {len(planets_in_apoklima)} planets - {', '.join(planets_in_apoklima) if planets_in_apoklima else 'None'}")

# Check Vaapi Yoga conditions
print(f"\n" + "-" * 80)
print("Vaapi Yoga Verification:")
print("-" * 80)

# Check 1: NO planets in Kendras
if len(planets_in_kendra) > 0:
    print(f"\n✗ CONDITION 1 FAILED: {len(planets_in_kendra)} planet(s) in Kendra houses")
    print(f"  Planets in Kendras: {', '.join(planets_in_kendra)}")
    print(f"  → Vaapi Yoga requirement violated: NO planets should be in Kendras")
    vaapi_yoga_formed = False
else:
    print(f"\n✓ CONDITION 1 PASSED: No planets in Kendra houses")

    # Check 2: All in Panaphar OR all in Apoklima
    if len(planets_in_panaphar) == 7 and len(planets_in_apoklima) == 0:
        print(f"✓ CONDITION 2 PASSED: All 7 planets in Panaphar houses (2,5,8,11)")
        vaapi_yoga_formed = True
    elif len(planets_in_apoklima) == 7 and len(planets_in_panaphar) == 0:
        print(f"✓ CONDITION 2 PASSED: All 7 planets in Apoklima houses (3,6,9,12)")
        vaapi_yoga_formed = True
    else:
        print(f"✗ CONDITION 2 FAILED: Planets distributed across both Panaphar and Apoklima")
        print(f"  Panaphar: {len(planets_in_panaphar)}, Apoklima: {len(planets_in_apoklima)}")
        print(f"  → All planets must be in SAME group (either all Panaphar OR all Apoklima)")
        vaapi_yoga_formed = False

# Final result
print("\n" + "=" * 80)
if vaapi_yoga_formed:
    print("✓✓✓ VAAPI YOGA IS FORMED ✓✓✓")
    print("=" * 80)
    print("\nEffects of Vaapi Yoga:")
    print("  • Wealth Accumulation - Like water in a well, steady growth")
    print("  • Secretive Nature - Private about finances and strategies")
    print("  • Supportive Relationships - Strong friend network")
    print("  • High Position Through Hard Work - Gradual rise to prominence")
    print("  • Resilience - Overcome obstacles through persistence")
    print("\nClassification: Major Positive Yoga (Nabhasa - Akriti)")
    print("Strength: Strong")
else:
    print("✗✗✗ VAAPI YOGA IS NOT FORMED ✗✗✗")
    print("=" * 80)
    print("\nThis is normal! Only 2-3% of charts have Vaapi Yoga.")
    print("Your chart likely has other powerful wealth yogas.")

print("\n" + "=" * 80)
print("END OF ANALYSIS")
print("=" * 80)
