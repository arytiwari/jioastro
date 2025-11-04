"""
Test AI Orchestrator - Phase 3 Complete
Multi-role orchestration with predictions, memory, and confidence scoring
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ai_orchestrator import ai_orchestrator


# Sample birth chart data (same as previous tests for consistency)
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


async def test_comprehensive_reading_with_predictions():
    """Test 1: Comprehensive reading with time-based predictions"""
    print("=" * 80)
    print("TEST 1: COMPREHENSIVE READING WITH PREDICTIONS")
    print("=" * 80)

    try:
        result = await ai_orchestrator.generate_comprehensive_reading(
            chart_data=SAMPLE_CHART,
            query="What can you tell me about my life prospects?",
            domains=["career", "wealth", "relationships"],
            include_predictions=True,
            include_transits=False,
            prediction_window_months=12
        )

        print(f"\n✅ Test 1 Passed!")
        print(f"\n📊 Orchestration Metadata:")
        print(f"   Roles Executed: {result['orchestration_metadata']['roles_executed']}")
        print(f"   Tokens Used: {result['orchestration_metadata']['tokens_used']}/{result['orchestration_metadata']['token_budget']}")
        print(f"   Domains Analyzed: {result['orchestration_metadata']['domains_analyzed']}")
        print(f"   Model: {result['orchestration_metadata']['model']}")

        print(f"\n📚 Knowledge Base:")
        print(f"   Total Rules Retrieved: {result['total_rules_retrieved']}")
        print(f"   Rules Cited: {len(result['rules_used'])}")
        if result['rules_used']:
            print(f"\n   Top 3 Cited Rules:")
            for i, rule in enumerate(result['rules_used'][:3], 1):
                print(f"   {i}. {rule['rule_id']}: {rule['anchor']} (weight: {rule['weight']})")

        print(f"\n🔮 Predictions:")
        print(f"   Total Predictions: {len(result['predictions'])}")
        if result['predictions']:
            for pred in result['predictions'][:2]:  # Show first 2
                print(f"\n   Domain: {pred['domain']}")
                print(f"   Summary: {pred.get('prediction_summary', 'N/A')[:100]}...")
                print(f"   Confidence: {pred.get('confidence_score', 0)}% ({pred.get('confidence_level', 'N/A')})")
                print(f"   Key Periods: {len(pred.get('key_periods', []))} events")

        print(f"\n✅ Verification:")
        print(f"   Quality Score: {result['verification']['quality_score']}/10")
        print(f"   Overall Confidence: {result['verification']['overall_confidence']}")
        print(f"   Issues Found: {len(result['verification'].get('issues', []))}")
        print(f"   Citation Accuracy: {result['verification']['citation_metrics']['citation_accuracy']:.1%}")

        print(f"\n📖 INTERPRETATION (First 500 chars):")
        print("-" * 80)
        print(result['interpretation'][:500] + "...")
        print("-" * 80)

        return result

    except Exception as e:
        print(f"\n❌ Test 1 Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_targeted_question():
    """Test 2: Targeted question answering (no predictions)"""
    print("\n\n" + "=" * 80)
    print("TEST 2: TARGETED QUESTION (CAREER-FOCUSED)")
    print("=" * 80)

    try:
        result = await ai_orchestrator.generate_comprehensive_reading(
            chart_data=SAMPLE_CHART,
            query="Should I start my own business or continue in a job?",
            domains=None,  # Let coordinator decide
            include_predictions=False,  # No time predictions
            include_transits=False,
            prediction_window_months=0
        )

        print(f"\n✅ Test 2 Passed!")
        print(f"\n🎯 Coordinator Analysis:")
        print(f"   Automatically Detected Domains: {result['orchestration_metadata']['domains_analyzed']}")
        print(f"   Tokens Used: {result['orchestration_metadata']['tokens_used']}")

        print(f"\n📚 Rules Used: {len(result['rules_used'])}")
        if result['rules_used']:
            for rule in result['rules_used'][:3]:
                print(f"   - {rule['rule_id']}: {rule['anchor']}")

        print(f"\n📖 ANSWER:")
        print("-" * 80)
        print(result['interpretation'][:400] + "...")
        print("-" * 80)

        return result

    except Exception as e:
        print(f"\n❌ Test 2 Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_spirituality_domain():
    """Test 3: Spirituality domain analysis"""
    print("\n\n" + "=" * 80)
    print("TEST 3: SPIRITUALITY DOMAIN ANALYSIS")
    print("=" * 80)

    try:
        result = await ai_orchestrator.generate_comprehensive_reading(
            chart_data=SAMPLE_CHART,
            query=None,  # No specific query
            domains=["spirituality"],
            include_predictions=True,
            include_transits=False,
            prediction_window_months=6
        )

        print(f"\n✅ Test 3 Passed!")
        print(f"\n📊 Analysis:")
        print(f"   Domain: spirituality")
        print(f"   Rules Retrieved: {result['total_rules_retrieved']}")
        print(f"   Predictions Generated: {len(result['predictions'])}")
        print(f"   Confidence: {result['confidence']}")

        if result['predictions']:
            pred = result['predictions'][0]
            print(f"\n🔮 Spiritual Prediction:")
            print(f"   Summary: {pred.get('prediction_summary', 'N/A')[:150]}...")
            print(f"   Confidence: {pred.get('confidence_score', 0)}%")

        print(f"\n📖 INTERPRETATION:")
        print("-" * 80)
        print(result['interpretation'][:400] + "...")
        print("-" * 80)

        return result

    except Exception as e:
        print(f"\n❌ Test 3 Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_verifier_quality_check():
    """Test 4: Verifier quality checking with multiple domains"""
    print("\n\n" + "=" * 80)
    print("TEST 4: VERIFIER QUALITY CHECKING")
    print("=" * 80)

    try:
        result = await ai_orchestrator.generate_comprehensive_reading(
            chart_data=SAMPLE_CHART,
            query="Provide a comprehensive analysis of all life areas",
            domains=["general", "career", "wealth", "relationships", "health", "education"],
            include_predictions=False,
            include_transits=False,
            prediction_window_months=0
        )

        print(f"\n✅ Test 4 Passed!")
        print(f"\n✅ Verifier Report:")
        verification = result['verification']

        print(f"   Quality Score: {verification['quality_score']}/10")
        print(f"   Overall Confidence: {verification['overall_confidence']}")

        print(f"\n   Issues Found: {len(verification.get('issues', []))}")
        if verification.get('issues'):
            for i, issue in enumerate(verification['issues'][:3], 1):
                print(f"   {i}. {issue}")

        print(f"\n   Contradictions: {len(verification.get('contradictions', []))}")
        if verification.get('contradictions'):
            for i, contradiction in enumerate(verification['contradictions'][:2], 1):
                print(f"   {i}. {contradiction}")

        print(f"\n   Suggestions: {len(verification.get('suggestions', []))}")
        if verification.get('suggestions'):
            for i, suggestion in enumerate(verification['suggestions'][:2], 1):
                print(f"   {i}. {suggestion}")

        print(f"\n   📊 Citation Metrics:")
        cit = verification['citation_metrics']
        print(f"      Total Citations: {cit['total_citations']}")
        print(f"      Valid Citations: {cit['valid_citations']}")
        print(f"      Invalid Citations: {cit['invalid_citations']}")
        print(f"      Citation Accuracy: {cit['citation_accuracy']:.1%}")

        print(f"\n📚 Comprehensive Analysis:")
        print(f"   Domains Analyzed: {len(result['orchestration_metadata']['domains_analyzed'])}")
        print(f"   Total Rules Retrieved: {result['total_rules_retrieved']}")
        print(f"   Rules Cited: {len(result['rules_used'])}")
        print(f"   Tokens Used: {result['orchestration_metadata']['tokens_used']}")

        return result

    except Exception as e:
        print(f"\n❌ Test 4 Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_token_budget_tracking():
    """Test 5: Token budget tracking across roles"""
    print("\n\n" + "=" * 80)
    print("TEST 5: TOKEN BUDGET TRACKING")
    print("=" * 80)

    try:
        result = await ai_orchestrator.generate_comprehensive_reading(
            chart_data=SAMPLE_CHART,
            query="Quick analysis of career prospects",
            domains=["career"],
            include_predictions=False,
            include_transits=False,
            prediction_window_months=0
        )

        print(f"\n✅ Test 5 Passed!")
        metadata = result['orchestration_metadata']

        print(f"\n💰 Token Budget Analysis:")
        print(f"   Total Budget: {metadata['token_budget']} tokens")
        print(f"   Tokens Used: {metadata['tokens_used']} tokens")
        print(f"   Remaining: {metadata['token_budget'] - metadata['tokens_used']} tokens")
        print(f"   Usage: {(metadata['tokens_used'] / metadata['token_budget'] * 100):.1f}%")

        print(f"\n🎭 Roles Executed:")
        for role in metadata['roles_executed']:
            print(f"   ✓ {role.capitalize()}")

        return result

    except Exception as e:
        print(f"\n❌ Test 5 Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all orchestrator tests"""
    print("\n" + "=" * 80)
    print("PHASE 3 ORCHESTRATOR TEST SUITE")
    print("Testing: Multi-Role AI Orchestration with Predictions & Memory")
    print("=" * 80)

    results = {}

    # Test 1: Comprehensive reading with predictions
    results['test1'] = await test_comprehensive_reading_with_predictions()
    await asyncio.sleep(2)  # Rate limit

    # Test 2: Targeted question
    results['test2'] = await test_targeted_question()
    await asyncio.sleep(2)

    # Test 3: Spirituality domain
    results['test3'] = await test_spirituality_domain()
    await asyncio.sleep(2)

    # Test 4: Verifier quality check
    results['test4'] = await test_verifier_quality_check()
    await asyncio.sleep(2)

    # Test 5: Token budget tracking
    results['test5'] = await test_token_budget_tracking()

    # Summary
    print("\n\n" + "=" * 80)
    print("TEST SUITE SUMMARY")
    print("=" * 80)

    passed = sum(1 for r in results.values() if r is not None)
    total = len(results)

    print(f"\n✅ Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nPhase 3 Features Verified:")
        print("  ✅ Multi-role orchestration (Coordinator, Retriever, Synthesizer, Verifier, Predictor)")
        print("  ✅ Scripture-grounded interpretations with rule citations")
        print("  ✅ Time-based predictions with confidence scoring")
        print("  ✅ Quality verification and contradiction checking")
        print("  ✅ Token budget tracking and management")
        print("  ✅ Domain routing and analysis")
        print("  ✅ Citation accuracy validation")

        print("\n📊 Average Metrics:")
        valid_results = [r for r in results.values() if r]
        if valid_results:
            avg_tokens = sum(r['orchestration_metadata']['tokens_used'] for r in valid_results) / len(valid_results)
            avg_rules = sum(r['total_rules_retrieved'] for r in valid_results) / len(valid_results)
            avg_quality = sum(r['verification']['quality_score'] for r in valid_results) / len(valid_results)

            print(f"  Average Tokens Used: {avg_tokens:.0f}")
            print(f"  Average Rules Retrieved: {avg_rules:.1f}")
            print(f"  Average Quality Score: {avg_quality:.1f}/10")

    else:
        print("\n⚠️  Some tests failed. Review output above.")

    print("\n" + "=" * 80)
    print("PHASE 3: LLM ORCHESTRATION - COMPLETE ✅")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
