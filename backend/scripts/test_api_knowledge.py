"""Test Knowledge Base API Endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Sample chart data
SAMPLE_CHART = {
    "planets": {
        "Sun": {"sign": "Capricorn", "house": 11, "degree": 15.5},
        "Moon": {"sign": "Leo", "house": 6, "degree": 22.3},
        "Mars": {"sign": "Scorpio", "house": 9, "degree": 8.7},
        "Mercury": {"sign": "Capricorn", "house": 11, "degree": 25.1},
        "Jupiter": {"sign": "Virgo", "house": 7, "degree": 12.4},
        "Venus": {"sign": "Sagittarius", "house": 10, "degree": 18.9},
        "Saturn": {"sign": "Pisces", "house": 1, "degree": 5.2}
    },
    "ascendant": {"sign": "Pisces", "degree": 1.27}
}


def test_stats():
    """Test knowledge base statistics endpoint"""
    print("="*70)
    print("TEST 1: KNOWLEDGE BASE STATISTICS")
    print("="*70)

    response = requests.get(f"{BASE_URL}/knowledge/stats")

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Total Rules: {data['total_rules']}")
        print(f"✅ Rules with Embeddings: {data['rules_with_embeddings']}")
        print(f"✅ Total Symbolic Keys: {data['total_symbolic_keys']}")
        print(f"✅ Coverage: {data['coverage_percentage']}%")
        print(f"\n📊 Rules by Domain:")
        for domain, count in data['rules_by_domain'].items():
            print(f"   {domain.capitalize()}: {count}")
    else:
        print(f"❌ Error: {response.text}")


def test_retrieve_rules():
    """Test rule retrieval endpoint"""
    print("\n" + "="*70)
    print("TEST 2: RULE RETRIEVAL (HYBRID SEARCH)")
    print("="*70)

    payload = {
        "chart_data": SAMPLE_CHART,
        "query": "Tell me about career and professional success",
        "domain": "career",
        "limit": 5,
        "min_weight": 0.5
    }

    response = requests.post(
        f"{BASE_URL}/knowledge/retrieve",
        json=payload
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n🔍 Retrieval Method: {data['retrieval_method']}")
        print(f"⏱️  Query Time: {data['query_time_ms']:.2f}ms")
        print(f"📊 Total Matches: {data['total_matches']}")
        print(f"🔑 Symbolic Keys: {', '.join(data['symbolic_keys_used'][:5])}")

        print(f"\n📚 Retrieved Rules:")
        for i, rule in enumerate(data['rules'], 1):
            print(f"\n{i}. {rule['rule_id']} (weight: {rule['weight']})")
            if rule.get('relevance_score'):
                print(f"   Relevance: {rule['relevance_score']:.3f}")
            if rule.get('semantic_score'):
                print(f"   Semantic: {rule['semantic_score']:.3f}")
            print(f"   Condition: {rule['condition'][:60]}...")
            print(f"   Effect: {rule['effect'][:60]}...")
    else:
        print(f"❌ Error: {response.text}")


def test_get_domains():
    """Test domains endpoint"""
    print("\n" + "="*70)
    print("TEST 3: GET AVAILABLE DOMAINS")
    print("="*70)

    response = requests.get(f"{BASE_URL}/knowledge/domains")

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        domains = response.json()
        print(f"\n📂 Available Domains: {', '.join(domains)}")
    else:
        print(f"❌ Error: {response.text}")


def test_get_domain_rules():
    """Test getting rules for specific domain"""
    print("\n" + "="*70)
    print("TEST 4: GET RULES BY DOMAIN (WEALTH)")
    print("="*70)

    response = requests.get(
        f"{BASE_URL}/knowledge/rules/domain/wealth",
        params={"limit": 5, "min_weight": 0.8}
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        rules = response.json()
        print(f"\n📊 Found {len(rules)} wealth rules (weight >= 0.8)")

        for i, rule in enumerate(rules[:3], 1):
            print(f"\n{i}. {rule['rule_id']} (weight: {rule['weight']})")
            print(f"   {rule['condition'][:60]}...")
    else:
        print(f"❌ Error: {response.text}")


def test_get_specific_rule():
    """Test getting a specific rule by ID"""
    print("\n" + "="*70)
    print("TEST 5: GET SPECIFIC RULE")
    print("="*70)

    rule_id = "BPHS-18-PAN-03"  # Hamsa Yoga

    response = requests.get(f"{BASE_URL}/knowledge/rules/{rule_id}")

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        rule = response.json()
        print(f"\n📚 Rule: {rule['rule_id']}")
        print(f"Domain: {rule['domain']}")
        print(f"Weight: {rule['weight']}")
        print(f"Anchor: {rule['anchor']}")
        print(f"\nCondition: {rule['condition']}")
        print(f"\nEffect: {rule['effect']}")
        if rule.get('commentary'):
            print(f"\nCommentary: {rule['commentary']}")
    else:
        print(f"❌ Error: {response.text}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("KNOWLEDGE BASE API TESTS")
    print("="*70)

    try:
        test_stats()
        test_retrieve_rules()
        test_get_domains()
        test_get_domain_rules()
        test_get_specific_rule()

        print("\n" + "="*70)
        print("✅ ALL API TESTS COMPLETED!")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
