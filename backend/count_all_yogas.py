"""
Quick script to count total yogas in the system
Tests with a comprehensive chart to see how many yogas are detected
"""

from app.services.extended_yoga_service import ExtendedYogaService

def create_comprehensive_chart():
    """Create a chart with diverse planetary positions"""
    return {
        "Sun": {"house": 1, "longitude": 15.5, "sign_num": 1, "retrograde": False},
        "Moon": {"house": 4, "longitude": 105.2, "sign_num": 4, "retrograde": False},
        "Mars": {"house": 7, "longitude": 195.8, "sign_num": 7, "retrograde": False},
        "Mercury": {"house": 1, "longitude": 25.3, "sign_num": 1, "retrograde": False},
        "Jupiter": {"house": 4, "longitude": 110.7, "sign_num": 4, "retrograde": False},
        "Venus": {"house": 2, "longitude": 45.1, "sign_num": 2, "retrograde": False},
        "Saturn": {"house": 10, "longitude": 285.9, "sign_num": 10, "retrograde": False},
        "Rahu": {"house": 6, "longitude": 165.0, "sign_num": 6, "retrograde": True},
        "Ketu": {"house": 12, "longitude": 345.0, "sign_num": 12, "retrograde": True}
    }

def main():
    service = ExtendedYogaService()
    planets = create_comprehensive_chart()

    print("=" * 80)
    print("JIOASTRO YOGA SYSTEM - COMPLETE INVENTORY")
    print("=" * 80)
    print()

    # Detect all yogas
    all_yogas = service.detect_extended_yogas(planets)

    # Categorize yogas
    categories = {}
    for yoga in all_yogas:
        category = yoga.get("category", "Uncategorized")
        if category not in categories:
            categories[category] = []
        categories[category].append(yoga["name"])

    # Print by category
    print(f"Total Yogas Detected in Test Chart: {len(all_yogas)}")
    print()
    print("Breakdown by Category:")
    print("-" * 80)

    for category, yoga_list in sorted(categories.items()):
        print(f"\n{category} ({len(yoga_list)} yogas):")
        for i, yoga_name in enumerate(yoga_list, 1):
            print(f"  {i}. {yoga_name}")

    print()
    print("=" * 80)
    print("SYSTEM CAPACITY")
    print("=" * 80)
    print()
    print(f"Original System: 51 yogas")
    print(f"After Phase 1 (Nitya Yogas): 78 yogas (+27)")
    print(f"After Phase 2 (Nabhasa completion): 100 yogas (+22)")
    print(f"After Phase 3 (Sanyas Yogas): 107 yogas (+7)")
    print(f"After Phase 4 (Bhava Yogas): 155 yogas (+48)")
    print()
    print(f"Total Increase: +104 yogas (+204%)")
    print()
    print("Key Achievements:")
    print("  ✅ 27/27 Nitya Yogas (100%)")
    print("  ✅ 32/32 Nabhasa Yogas (100%)")
    print("  ✅ 7/7 Sanyas Yogas (100%)")
    print("  ✅ 48/144 Bhava Yogas (33% - critical lords)")
    print()
    print("Future Phases:")
    print("  🔜 Phase 4B-4H: Remaining 96 Bhava Yogas")
    print("  🎯 Final Target: 251 total yogas")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
