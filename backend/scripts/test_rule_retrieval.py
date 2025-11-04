"""
Test Rule Retrieval Service

Tests symbolic, semantic, and hybrid search
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rule_retrieval import rule_retrieval_service


# Sample birth chart data (from previous test)
SAMPLE_CHART = {
    "planets": {
        "Sun": {"sign": "Capricorn", "house": 11, "degree": 15.5},
        "Moon": {"sign": "Leo", "house": 6, "degree": 22.3},
        "Mars": {"sign": "Scorpio", "house": 9, "degree": 8.7},
        "Mercury": {"sign": "Capricorn", "house": 11, "degree": 25.1},
        "Jupiter": {"sign": "Virgo", "house": 7, "degree": 12.4},
        "Venus": {"sign": "Sagittarius", "house": 10, "degree": 18.9},
        "Saturn": {"sign": "Pisces", "house": 1, "degree": 5.2},
        "Rahu": {"sign": "Gemini", "house": 4, "degree": 14.6},
        "Ketu": {"sign": "Sagittarius", "house": 10, "degree": 14.6}
    },
    "ascendant": {"sign": "Pisces", "degree": 1.27}
}


async def test_symbolic_search():
    """Test symbolic key search"""
    print("\n" + "="*60)
    print("TEST 1: SYMBOLIC SEARCH")
    print("="*60)

    result = await rule_retrieval_service.retrieve_rules(
        chart_data=SAMPLE_CHART,
        query=None,  # No query for pure symbolic
        domain="career",
        limit=5
    )

    print(f"\n🔍 Search Method: {result['retrieval_method']}")
    print(f"⏱️  Query Time: {result['query_time_ms']}ms")
    print(f"📊 Total Matches: {result['total_matches']}")
    print(f"🔑 Symbolic Keys: {result['symbolic_keys_used'][:5]}")

    print(f"\n📚 Retrieved Rules:")
    for i, rule in enumerate(result['rules'][:3], 1):
        print(f"\n{i}. {rule['rule_id']} (weight: {rule['weight']})")
        print(f"   Domain: {rule['domain']}")
        print(f"   Condition: {rule['condition'][:60]}...")
        print(f"   Effect: {rule['effect'][:60]}...")


async def test_semantic_search():
    """Test semantic similarity search"""
    print("\n" + "="*60)
    print("TEST 2: SEMANTIC SEARCH")
    print("="*60)

    result = await rule_retrieval_service.retrieve_rules(
        chart_data={},  # Empty chart for pure semantic
        query="What does Sun in 10th house mean for career success?",
        domain=None,
        limit=5
    )

    print(f"\n🔍 Search Method: {result['retrieval_method']}")
    print(f"⏱️  Query Time: {result['query_time_ms']}ms")
    print(f"📊 Total Matches: {result['total_matches']}")

    print(f"\n📚 Retrieved Rules:")
    for i, rule in enumerate(result['rules'][:3], 1):
        semantic_score = rule.get('semantic_score', 0.0)
        print(f"\n{i}. {rule['rule_id']} (weight: {rule['weight']}, semantic: {semantic_score:.3f})")
        print(f"   Domain: {rule['domain']}")
        print(f"   Condition: {rule['condition'][:60]}...")
        print(f"   Effect: {rule['effect'][:60]}...")


async def test_hybrid_search():
    """Test hybrid search (symbolic + semantic)"""
    print("\n" + "="*60)
    print("TEST 3: HYBRID SEARCH")
    print("="*60)

    result = await rule_retrieval_service.retrieve_rules(
        chart_data=SAMPLE_CHART,
        query="Tell me about career and professional success",
        domain="career",
        limit=5
    )

    print(f"\n🔍 Search Method: {result['retrieval_method']}")
    print(f"⏱️  Query Time: {result['query_time_ms']}ms")
    print(f"📊 Total Matches: {result['total_matches']}")
    print(f"🔑 Symbolic Keys: {result['symbolic_keys_used'][:5]}")

    print(f"\n📚 Retrieved Rules:")
    for i, rule in enumerate(result['rules'][:5], 1):
        relevance = rule.get('relevance_score', 0.0)
        symbolic = "✓" if rule.get('symbolic_match') else "✗"
        semantic = rule.get('semantic_score', 0.0)

        print(f"\n{i}. {rule['rule_id']} (relevance: {relevance:.3f})")
        print(f"   Weight: {rule['weight']} | Symbolic: {symbolic} | Semantic: {semantic:.3f}")
        print(f"   Domain: {rule['domain']}")
        print(f"   Condition: {rule['condition'][:60]}...")
        print(f"   Effect: {rule['effect'][:60]}...")


async def test_domain_specific():
    """Test domain-specific queries"""
    print("\n" + "="*60)
    print("TEST 4: DOMAIN-SPECIFIC QUERIES")
    print("="*60)

    domains = ["wealth", "relationships", "health"]

    for domain in domains:
        result = await rule_retrieval_service.retrieve_rules(
            chart_data=SAMPLE_CHART,
            query=None,
            domain=domain,
            limit=3
        )

        print(f"\n📂 Domain: {domain.upper()}")
        print(f"   Matches: {result['total_matches']}")

        for rule in result['rules'][:2]:
            print(f"   • {rule['rule_id']}: {rule['condition'][:50]}...")


async def main():
    """Run all tests"""
    print("="*60)
    print("RULE RETRIEVAL SERVICE TESTS")
    print("="*60)

    try:
        # Test 1: Symbolic Search
        await test_symbolic_search()

        # Test 2: Semantic Search
        await test_semantic_search()

        # Test 3: Hybrid Search
        await test_hybrid_search()

        # Test 4: Domain Specific
        await test_domain_specific()

        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
