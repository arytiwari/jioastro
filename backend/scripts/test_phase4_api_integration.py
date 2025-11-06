"""
Integration Tests for Phase 4 API Endpoints
Tests remedies, rectification, transits, and shadbala endpoints
"""

import requests
from datetime import datetime, date
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_PROFILE_ID = "your-test-profile-id"  # Replace with actual profile ID
AUTH_TOKEN = "your-jwt-token"  # Replace with actual JWT token

# Test data
BIRTH_DATA = {
    "name": "Test User",
    "birth_date": "1990-01-15",
    "birth_time": "14:30",
    "birth_city": "New York",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
}

# Headers with authentication
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}


def print_test_header(test_name):
    """Print formatted test header"""
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)


def print_response(response):
    """Print formatted response"""
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
    try:
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
        return data
    except:
        print(f"Response Text: {response.text}")
        return None


def test_remedy_generation():
    """Test 1: Remedy Generation API"""
    print_test_header("Remedy Generation")

    payload = {
        "profile_id": TEST_PROFILE_ID,
        "domain": "career",
        "specific_issue": "Job instability and career growth",
        "max_remedies": 5,
        "include_practical": True
    }

    print(f"\nRequest Payload:\n{json.dumps(payload, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/enhancements/remedies/generate",
        json=payload,
        headers=headers
    )

    data = print_response(response)

    if response.status_code == 200 and data:
        print("\n✅ TEST PASSED")
        print(f"   Generated {len(data.get('remedies', []))} remedies")
        print(f"   Priority planets: {', '.join(data.get('priority_planets', []))}")
        print(f"   Current dasha: {data.get('current_dasha', 'Unknown')}")

        # Print first remedy as sample
        if data.get('remedies'):
            remedy = data['remedies'][0]
            print(f"\n   Sample Remedy:")
            print(f"   - Type: {remedy.get('type')}")
            print(f"   - Title: {remedy.get('title')}")
            print(f"   - Planet: {remedy.get('planet')}")
            print(f"   - Difficulty: {remedy.get('difficulty')}")

        return True
    else:
        print("\n❌ TEST FAILED")
        return False


def test_rectification():
    """Test 2: Birth Time Rectification API"""
    print_test_header("Birth Time Rectification")

    payload = {
        "name": BIRTH_DATA["name"],
        "birth_date": BIRTH_DATA["birth_date"],
        "approximate_time": BIRTH_DATA["birth_time"],
        "time_window_minutes": 30,
        "birth_city": BIRTH_DATA["birth_city"],
        "birth_lat": BIRTH_DATA["latitude"],
        "birth_lon": BIRTH_DATA["longitude"],
        "birth_timezone": BIRTH_DATA["timezone"],
        "event_anchors": [
            {
                "event_type": "marriage",
                "event_date": "2015-06-15",
                "description": "Marriage ceremony",
                "significance": 9
            },
            {
                "event_type": "job_start",
                "event_date": "2012-03-01",
                "description": "First job after college",
                "significance": 7
            }
        ]
    }

    print(f"\nRequest Payload:\n{json.dumps(payload, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/enhancements/rectification/calculate",
        json=payload,
        headers=headers
    )

    data = print_response(response)

    if response.status_code == 200 and data:
        print("\n✅ TEST PASSED")
        rectification = data.get('rectification', {})
        print(f"   Top candidates: {len(rectification.get('top_candidates', []))}")
        print(f"   Events analyzed: {rectification.get('events_analyzed', 0)}")
        print(f"   Candidates tested: {rectification.get('candidates_tested', 0)}")

        # Print top candidate
        if rectification.get('top_candidates'):
            top = rectification['top_candidates'][0]
            print(f"\n   Top Candidate:")
            print(f"   - Birth time: {top.get('birth_time')}")
            print(f"   - Confidence: {top.get('confidence_score')}%")
            print(f"   - Ascendant: {top.get('ascendant')}")
            print(f"   - Moon sign: {top.get('moon_sign')}")

        return True
    else:
        print("\n❌ TEST FAILED")
        return False


def test_current_transits():
    """Test 3: Current Transits API"""
    print_test_header("Current Transits")

    payload = {
        "profile_id": TEST_PROFILE_ID,
        "transit_date": None,  # Current date/time
        "include_timeline": True,
        "focus_planets": ["Jupiter", "Saturn"]
    }

    print(f"\nRequest Payload:\n{json.dumps(payload, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/enhancements/transits/current",
        json=payload,
        headers=headers
    )

    data = print_response(response)

    if response.status_code == 200 and data:
        print("\n✅ TEST PASSED")
        print(f"   Transit date: {data.get('transit_date')}")
        print(f"   Current positions: {len(data.get('current_positions', []))}")
        print(f"   Significant aspects: {len(data.get('significant_aspects', []))}")
        print(f"   Upcoming sign changes: {len(data.get('upcoming_sign_changes', []))}")

        # Print summary
        print(f"\n   Summary: {data.get('summary', 'N/A')}")
        print(f"   Focus areas: {', '.join(data.get('focus_areas', []))}")

        # Print first aspect as sample
        if data.get('significant_aspects'):
            aspect = data['significant_aspects'][0]
            print(f"\n   Sample Aspect:")
            print(f"   - {aspect.get('transiting_planet')} {aspect.get('aspect_type')} {aspect.get('natal_planet')}")
            print(f"   - Strength: {aspect.get('strength')}")
            print(f"   - Orb: {aspect.get('orb')}°")

        return True
    else:
        print("\n❌ TEST FAILED")
        return False


def test_shadbala():
    """Test 4: Shadbala Calculation API"""
    print_test_header("Shadbala Calculation")

    payload = {
        "profile_id": TEST_PROFILE_ID,
        "include_breakdown": True,
        "comparison": True
    }

    print(f"\nRequest Payload:\n{json.dumps(payload, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/enhancements/shadbala/calculate",
        json=payload,
        headers=headers
    )

    data = print_response(response)

    if response.status_code == 200 and data:
        print("\n✅ TEST PASSED")
        print(f"   Strongest planet: {data.get('strongest_planet')}")
        print(f"   Weakest planet: {data.get('weakest_planet')}")
        print(f"   Average strength: {data.get('average_strength'):.2f}%")
        print(f"   Planets above minimum: {data.get('planets_above_minimum')}/7")
        print(f"   Overall chart strength: {data.get('overall_chart_strength')}")

        # Print strength breakdown for one planet
        if data.get('planetary_strengths'):
            planet_strength = data['planetary_strengths'][0]
            print(f"\n   Sample ({planet_strength.get('planet')}):")
            print(f"   - Total strength: {planet_strength.get('total_strength'):.2f}")
            print(f"   - Required: {planet_strength.get('required_minimum'):.2f}")
            print(f"   - Percentage: {planet_strength.get('percentage_of_required'):.2f}%")
            print(f"   - Rating: {planet_strength.get('rating')}")

        return True
    else:
        print("\n❌ TEST FAILED")
        return False


def test_all_endpoints():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("PHASE 4 API INTEGRATION TESTS")
    print("Testing: Remedies, Rectification, Transits, Shadbala")
    print("=" * 80)

    results = {
        "Remedy Generation": test_remedy_generation(),
        "Birth Time Rectification": test_rectification(),
        "Current Transits": test_current_transits(),
        "Shadbala Calculation": test_shadbala()
    }

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")

    print("\n" + "-" * 80)
    print(f"Total: {passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
    print("=" * 80)

    return passed == total


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║   Phase 4 API Integration Tests                            ║
    ║   JioAstro - Enhancement APIs                              ║
    ╚══════════════════════════════════════════════════════════════╝

    PREREQUISITES:
    1. Backend server running on http://localhost:8000
    2. Valid JWT authentication token
    3. Test profile created with chart data
    4. Update TEST_PROFILE_ID and AUTH_TOKEN in this file

    ENDPOINTS TESTED:
    - POST /api/v1/enhancements/remedies/generate
    - POST /api/v1/enhancements/rectification/calculate
    - POST /api/v1/enhancements/transits/current
    - POST /api/v1/enhancements/shadbala/calculate
    """)

    # Run tests
    all_passed = test_all_endpoints()

    # Exit code
    import sys
    sys.exit(0 if all_passed else 1)
