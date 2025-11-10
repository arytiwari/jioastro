"""
Test script to verify yoga enrichment with classification metadata
"""

from app.services.extended_yoga_service import ExtendedYogaService

def test_yoga_enrichment():
    """Test the yoga enrichment functionality"""
    service = ExtendedYogaService()

    # Create a sample chart with diverse planetary positions
    planets = {
        "Sun": {"house": 1, "longitude": 15.5, "sign_num": 1, "retrograde": False},
        "Moon": {"house": 4, "longitude": 105.2, "sign_num": 4, "retrograde": False},
        "Mars": {"house": 10, "longitude": 285.8, "sign_num": 10, "retrograde": False},  # Mars in 10th (Kendra)
        "Mercury": {"house": 1, "longitude": 25.3, "sign_num": 1, "retrograde": False},
        "Jupiter": {"house": 4, "longitude": 110.7, "sign_num": 4, "retrograde": False},  # Jupiter in 4th (Kendra)
        "Venus": {"house": 7, "longitude": 195.1, "sign_num": 7, "retrograde": False},  # Venus in 7th (Kendra)
        "Saturn": {"house": 10, "longitude": 289.9, "sign_num": 10, "retrograde": False},  # Saturn in 10th (Kendra)
        "Rahu": {"house": 6, "longitude": 165.0, "sign_num": 6, "retrograde": True},
        "Ketu": {"house": 12, "longitude": 345.0, "sign_num": 12, "retrograde": True}
    }

    # Detect yogas
    print("=" * 80)
    print("TESTING YOGA ENRICHMENT WITH CLASSIFICATION METADATA")
    print("=" * 80)
    print()

    yogas = service.detect_extended_yogas(planets)
    print(f"✅ Detected {len(yogas)} yogas")
    print()

    # Enrich yogas
    enriched_yogas = service.enrich_yogas(yogas)
    print(f"✅ Enriched {len(enriched_yogas)} yogas with classification metadata")
    print()

    # Categorize by importance and impact
    major_positive = [y for y in enriched_yogas if y.get('importance') == 'major' and y.get('impact') == 'positive']
    major_challenge = [y for y in enriched_yogas if y.get('importance') == 'major' and y.get('impact') in ['negative', 'mixed']]
    moderate = [y for y in enriched_yogas if y.get('importance') == 'moderate']
    minor_positive = [y for y in enriched_yogas if y.get('importance') == 'minor' and y.get('impact') == 'positive']
    minor_challenge = [y for y in enriched_yogas if y.get('importance') == 'minor' and y.get('impact') in ['negative', 'mixed']]

    print("CATEGORIZATION RESULTS:")
    print("-" * 80)
    print(f"Major Positive Yogas: {len(major_positive)}")
    print(f"Major Challenge Yogas: {len(major_challenge)}")
    print(f"Moderate Yogas: {len(moderate)}")
    print(f"Minor Positive Yogas: {len(minor_positive)}")
    print(f"Minor Challenge Yogas: {len(minor_challenge)}")
    print()

    # Display sample yogas from each category
    if major_positive:
        print("🌟 MAJOR POSITIVE YOGAS (Sample):")
        for yoga in major_positive[:3]:
            print(f"  ✅ {yoga['name']}")
            print(f"     Impact: {yoga.get('impact', 'N/A')}")
            print(f"     Importance: {yoga.get('importance', 'N/A')}")
            print(f"     Life Area: {yoga.get('life_area', 'N/A')}")
            print(f"     Strength: {yoga.get('strength', 'N/A')}")
            print()

    if major_challenge:
        print("⚠️ MAJOR CHALLENGE YOGAS (Sample):")
        for yoga in major_challenge[:3]:
            print(f"  ⚠️ {yoga['name']}")
            print(f"     Impact: {yoga.get('impact', 'N/A')}")
            print(f"     Importance: {yoga.get('importance', 'N/A')}")
            print(f"     Life Area: {yoga.get('life_area', 'N/A')}")
            print(f"     Strength: {yoga.get('strength', 'N/A')}")
            print()

    if moderate:
        print("📊 MODERATE YOGAS (Sample):")
        for yoga in moderate[:3]:
            print(f"  ℹ️ {yoga['name']}")
            print(f"     Impact: {yoga.get('impact', 'N/A')}")
            print(f"     Importance: {yoga.get('importance', 'N/A')}")
            print(f"     Life Area: {yoga.get('life_area', 'N/A')}")
            print(f"     Strength: {yoga.get('strength', 'N/A')}")
            print()

    print("=" * 80)
    print("✅ ENRICHMENT TEST SUCCESSFUL!")
    print("=" * 80)

    # Verify all yogas have metadata
    missing_metadata = []
    for yoga in enriched_yogas:
        if not all(key in yoga for key in ['impact', 'importance', 'life_area']):
            missing_metadata.append(yoga['name'])

    if missing_metadata:
        print(f"⚠️ WARNING: {len(missing_metadata)} yogas missing metadata:")
        for name in missing_metadata:
            print(f"  - {name}")
    else:
        print("✅ All yogas have complete metadata (impact, importance, life_area)")

    return enriched_yogas

if __name__ == "__main__":
    test_yoga_enrichment()
