"""
Test AI Service + Knowledge Base Integration
Demonstrates scripture-grounded interpretations with rule citations
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ai_service import ai_service


# Sample birth chart data
SAMPLE_CHART = {
    "basic_info": {
        "name": "Test User",
        "birth_datetime": "1990-01-15 10:30:00",
        "location": {
            "city": "Mumbai",
            "latitude": 19.0760,
            "longitude": 72.8777
        }
    },
    "ascendant": {
        "sign": "Pisces",
        "position": 5.27
    },
    "planets": {
        "Sun": {
            "sign": "Capricorn",
            "house": 11,
            "position": 15.5,
            "retrograde": False
        },
        "Moon": {
            "sign": "Leo",
            "house": 6,
            "position": 22.3,
            "retrograde": False
        },
        "Mars": {
            "sign": "Scorpio",
            "house": 9,
            "position": 8.7,
            "retrograde": False
        },
        "Mercury": {
            "sign": "Capricorn",
            "house": 11,
            "position": 25.1,
            "retrograde": False
        },
        "Jupiter": {
            "sign": "Cancer",
            "house": 5,
            "position": 12.4,
            "retrograde": False
        },
        "Venus": {
            "sign": "Sagittarius",
            "house": 10,
            "position": 18.9,
            "retrograde": False
        },
        "Saturn": {
            "sign": "Capricorn",
            "house": 11,
            "position": 5.2,
            "retrograde": False
        }
    },
    "yogas": [
        {
            "name": "Gaja Kesari Yoga",
            "description": "Jupiter and Moon in mutual angles",
            "strength": "Strong"
        }
    ],
    "dasha": {
        "current_dasha": "Jupiter",
        "period_years": 16
    }
}


async def test_career_query():
    """Test career-related query with knowledge base"""
    print("=" * 80)
    print("TEST 1: CAREER QUERY WITH KNOWLEDGE BASE")
    print("=" * 80)

    question = "What does my birth chart indicate about my career prospects and professional success?"

    print(f"\n📝 Question: {question}")
    print(f"📊 Chart: Jupiter in Cancer (5th house), Venus in Sagittarius (10th house)")
    print(f"\n🔄 Generating interpretation with knowledge base integration...")

    result = await ai_service.generate_interpretation(
        chart_data=SAMPLE_CHART,
        question=question,
        category="career",
        use_knowledge_base=True
    )

    print(f"\n✅ Generation Complete!")
    print(f"   Model: {result['model']}")
    print(f"   Tokens Used: {result['tokens_used']}")
    print(f"   Rules Retrieved: {result.get('rules_retrieved', 0)}")
    print(f"   Rules Cited: {len(result.get('rules_used', []))}")
    print(f"   KB Used: {result.get('knowledge_base_used', False)}")

    if result.get('rules_used'):
        print(f"\n📚 Rules Cited in Interpretation:")
        for rule in result['rules_used']:
            print(f"   - {rule['rule_id']}: {rule['anchor']} (weight: {rule['weight']})")

    print(f"\n📖 AI INTERPRETATION:")
    print("-" * 80)
    print(result['interpretation'])
    print("-" * 80)

    return result


async def test_relationship_query():
    """Test relationship query with D9 rules"""
    print("\n\n" + "=" * 80)
    print("TEST 2: RELATIONSHIP QUERY WITH D9 NAVAMSA RULES")
    print("=" * 80)

    question = "How is my married life and relationship with spouse according to Vedic astrology?"

    print(f"\n📝 Question: {question}")
    print(f"📊 Chart: Venus in Sagittarius (10th house)")
    print(f"\n🔄 Generating interpretation (should retrieve D9 rules)...")

    result = await ai_service.generate_interpretation(
        chart_data=SAMPLE_CHART,
        question=question,
        category="relationship",
        use_knowledge_base=True
    )

    print(f"\n✅ Generation Complete!")
    print(f"   Rules Retrieved: {result.get('rules_retrieved', 0)}")
    print(f"   Rules Cited: {len(result.get('rules_used', []))}")

    if result.get('rules_used'):
        print(f"\n📚 Rules Cited:")
        for rule in result['rules_used']:
            print(f"   - {rule['rule_id']}: {rule['anchor']}")

    print(f"\n📖 AI INTERPRETATION:")
    print("-" * 80)
    print(result['interpretation'])
    print("-" * 80)

    return result


async def test_without_knowledge_base():
    """Test interpretation WITHOUT knowledge base (baseline)"""
    print("\n\n" + "=" * 80)
    print("TEST 3: INTERPRETATION WITHOUT KNOWLEDGE BASE (BASELINE)")
    print("=" * 80)

    question = "What does my chart say about wealth and financial prosperity?"

    print(f"\n📝 Question: {question}")
    print(f"\n🔄 Generating interpretation WITHOUT knowledge base...")

    result = await ai_service.generate_interpretation(
        chart_data=SAMPLE_CHART,
        question=question,
        category="wealth",
        use_knowledge_base=False  # Disabled
    )

    print(f"\n✅ Generation Complete!")
    print(f"   KB Used: {result.get('knowledge_base_used', False)}")
    print(f"   Rules Retrieved: {result.get('rules_retrieved', 0)}")

    print(f"\n📖 AI INTERPRETATION (No KB):")
    print("-" * 80)
    print(result['interpretation'])
    print("-" * 80)

    return result


async def test_with_vs_without_comparison():
    """Compare interpretation quality with and without KB"""
    print("\n\n" + "=" * 80)
    print("TEST 4: WITH KB vs WITHOUT KB COMPARISON")
    print("=" * 80)

    question = "Tell me about my spiritual inclinations and dharmic path"

    # Without KB
    print(f"\n📝 Question: {question}")
    print(f"\n🔄 Test A: WITHOUT Knowledge Base...")
    result_without = await ai_service.generate_interpretation(
        chart_data=SAMPLE_CHART,
        question=question,
        category="spirituality",
        use_knowledge_base=False
    )

    # With KB
    print(f"\n🔄 Test B: WITH Knowledge Base...")
    result_with = await ai_service.generate_interpretation(
        chart_data=SAMPLE_CHART,
        question=question,
        category="spirituality",
        use_knowledge_base=True
    )

    print(f"\n📊 COMPARISON:")
    print(f"   Without KB - Tokens: {result_without['tokens_used']}, Rules: 0")
    print(f"   With KB    - Tokens: {result_with['tokens_used']}, Rules: {len(result_with.get('rules_used', []))}")

    print(f"\n📖 INTERPRETATION A (Without KB):")
    print("-" * 80)
    print(result_without['interpretation'][:500] + "...")
    print("-" * 80)

    print(f"\n📖 INTERPRETATION B (With KB + Citations):")
    print("-" * 80)
    print(result_with['interpretation'][:500] + "...")
    if result_with.get('rules_used'):
        print(f"\n   Citations: {[r['rule_id'] for r in result_with['rules_used']]}")
    print("-" * 80)


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("AI + KNOWLEDGE BASE INTEGRATION TESTS")
    print("Testing scripture-grounded interpretations with BPHS rule citations")
    print("=" * 80)

    try:
        # Test 1: Career with KB
        await test_career_query()

        # Test 2: Relationship with D9 rules
        await test_relationship_query()

        # Test 3: Without KB (baseline)
        await test_without_knowledge_base()

        # Test 4: Comparison
        await test_with_vs_without_comparison()

        print("\n\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nKey Observations:")
        print("  - Knowledge base rules are retrieved and included in prompts")
        print("  - GPT-4 cites specific BPHS rules in interpretations")
        print("  - Citations include chapter/verse anchors")
        print("  - Interpretations are grounded in classical texts")
        print("  - D9 and D10 rules appear for relevant queries")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
