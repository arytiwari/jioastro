"""
Test script to verify planetary special states implementation
"""
from app.services.vedic_astrology_accurate import accurate_vedic_astrology
from datetime import date, time

# Test birth chart calculation
result = accurate_vedic_astrology.calculate_birth_chart(
    name='Test User',
    birth_date=date(1990, 1, 1),
    birth_time=time(12, 0),
    latitude=28.6139,
    longitude=77.2090,
    timezone_str='Asia/Kolkata',
    city='Delhi'
)

print('\n' + '='*80)
print('🎯 PLANETARY SPECIAL STATES TEST')
print('='*80)

print(f"\nBirth Details:")
print(f"  Date: 1990-01-01 12:00")
print(f"  Location: Delhi (28.6139, 77.2090)")
print(f"  Timezone: Asia/Kolkata")

print(f"\nAscendant: {result['ascendant']['sign']} {result['ascendant']['degree']:.2f}°")

print('\n' + '-'*80)
print('PLANETARY POSITIONS AND SPECIAL STATES')
print('-'*80)

for planet, data in result['planets'].items():
    print(f"\n{planet}:")
    print(f"  Sign: {data['sign']} ({data['degree']:.2f}°)")
    print(f"  House: {data['house']}")
    print(f"  Retrograde: {'✅ YES' if data.get('retrograde', False) else '❌ NO'}")
    print(f"  Exalted: {'✅ YES' if data.get('exalted', False) else '❌ NO'}")
    print(f"  Debilitated: {'✅ YES' if data.get('debilitated', False) else '❌ NO'}")
    print(f"  Own Sign: {'✅ YES' if data.get('own_sign', False) else '❌ NO'}")
    print(f"  Combust: {'✅ YES' if data.get('combust', False) else '❌ NO'}")
    print(f"  Vargottama: {'✅ YES' if data.get('vargottama', False) else '❌ NO'}")

    if data.get('combustion_distance'):
        print(f"  Combustion Distance from Sun: {data['combustion_distance']}°")

print('\n' + '='*80)
print('✅ TEST COMPLETE')
print('='*80 + '\n')
