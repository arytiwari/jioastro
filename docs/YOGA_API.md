# Yoga Detection API - Quick Reference

**Last Updated:** November 8, 2025
**Base URL:** `http://localhost:8000/api/v1/enhancements`
**Authentication:** Required (JWT Bearer token)

---

## Endpoints

### 1. Analyze Yogas

Detect all yogas in a birth chart with strength and category information.

```http
POST /yogas/analyze
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "profile_id": "uuid-string",
  "include_all": true
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| profile_id | string (UUID) | Yes | - | Birth profile ID |
| include_all | boolean | No | true | Include weak yogas (false = only Strong/Very Strong) |

**Response: 200 OK**
```json
{
  "yogas": [
    {
      "name": "Hamsa Yoga",
      "description": "Jupiter in Kendra in own/exaltation sign...",
      "strength": "Very Strong",
      "category": "Pancha Mahapurusha"
    }
  ],
  "total_yogas": 15,
  "categories": {
    "Pancha Mahapurusha": 2,
    "Wealth": 3,
    "Power & Status": 2,
    "Learning & Wisdom": 1
  },
  "strongest_yogas": ["Hamsa Yoga", "Gaja Kesari Yoga"],
  "summary": "Chart has 15 yogas, indicating exceptional potential and multiple fortunate combinations! Notably, the chart features Hamsa Yoga, Gaja Kesari Yoga.",
  "chart_quality": "Exceptional"
}
```

**Chart Quality Ratings:**
- **Exceptional**: Very Strong yogas present
- **Excellent**: 10+ yogas detected
- **Very Good**: 6-10 yogas
- **Good**: 1-5 yogas
- **Average**: No major yogas

**Error Responses:**
```json
// 401 Unauthorized
{
  "detail": "Not authenticated"
}

// 404 Not Found
{
  "detail": "Profile not found"
}

// 404 Not Found
{
  "detail": "Chart not found. Please calculate chart first."
}

// 500 Internal Server Error
{
  "detail": "Failed to analyze yogas: <error message>"
}
```

---

### 2. Get Yoga Timing

Calculate when a specific yoga will activate based on dasha periods.

```http
GET /yoga-timing/{profile_id}?yoga_name=Hamsa+Yoga
Authorization: Bearer <token>
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| profile_id | string (UUID) | Birth profile ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| yoga_name | string | Yes | Exact yoga name (URL-encoded) |

**Response: 200 OK**
```json
{
  "yoga_name": "Hamsa Yoga",
  "activation_status": "Upcoming",
  "current_strength": "Very Strong",
  "dasha_activation_periods": [
    {
      "planet": "Jupiter",
      "start_date": "2028-05-12",
      "end_date": "2044-05-12",
      "period_type": "Mahadasha",
      "intensity": "High"
    },
    {
      "planet": "Jupiter",
      "start_date": "2030-08-15",
      "end_date": "2032-12-20",
      "period_type": "Antardasha",
      "intensity": "High"
    }
  ],
  "peak_periods": [],
  "general_activation_age": "25-35 years",
  "recommendations": [
    "Focus on higher education and spiritual practices during Jupiter dasha",
    "This is an excellent time for teaching, counseling, and advisory roles",
    "Practice meditation and connect with spiritual mentors",
    "Engage in philanthropic activities to maximize yoga benefits"
  ]
}
```

**Activation Status Values:**
- `"Active"`: Yoga is currently manifesting
- `"Upcoming"`: Will activate in future dasha period
- `"Past"`: Already completed activation period

**Intensity Levels:**
- `"High"`: Strong manifestation during this dasha
- `"Medium"`: Moderate effects
- `"Low"`: Subtle influence

**Error Responses:**
```json
// 404 Not Found
{
  "detail": "Yoga 'Invalid Yoga Name' not found in chart"
}
```

---

## Frontend Usage

### Using API Client

```typescript
import { apiClient } from '@/lib/api'

// Analyze yogas
const analyzeYogas = async (profileId: string, includeAll: boolean = true) => {
  try {
    const response = await apiClient.analyzeYogasForProfile({
      profile_id: profileId,
      include_all: includeAll
    })

    console.log('Total yogas:', response.data.total_yogas)
    console.log('Chart quality:', response.data.chart_quality)

    return response.data
  } catch (error) {
    console.error('Error analyzing yogas:', error)
    throw error
  }
}

// Get yoga timing
const getYogaTiming = async (profileId: string, yogaName: string) => {
  try {
    const response = await apiClient.get(
      `/enhancements/yoga-timing/${profileId}`,
      {
        params: { yoga_name: yogaName }
      }
    )

    console.log('Activation status:', response.data.activation_status)
    console.log('Dasha periods:', response.data.dasha_activation_periods)

    return response.data
  } catch (error) {
    console.error('Error fetching yoga timing:', error)
    throw error
  }
}
```

### Example: Complete Yoga Analysis Flow

```typescript
const performCompleteYogaAnalysis = async (profileId: string) => {
  // Step 1: Analyze yogas
  const yogaAnalysis = await analyzeYogas(profileId, true)

  // Step 2: Filter significant yogas
  const significantYogas = yogaAnalysis.yogas.filter(
    y => y.strength === 'Very Strong' || y.strength === 'Strong'
  )

  console.log(`Found ${significantYogas.length} significant yogas`)

  // Step 3: Get timing for each significant yoga
  const timingPromises = significantYogas.map(async (yoga) => {
    try {
      const timing = await getYogaTiming(profileId, yoga.name)
      return { yoga, timing }
    } catch (error) {
      console.error(`Failed to get timing for ${yoga.name}:`, error)
      return null
    }
  })

  const yogaTimings = await Promise.all(timingPromises)
  const validTimings = yogaTimings.filter(t => t !== null)

  // Step 4: Sort by activation date
  validTimings.sort((a, b) => {
    const aDate = a.timing.dasha_activation_periods[0]?.start_date
    const bDate = b.timing.dasha_activation_periods[0]?.start_date

    if (!aDate || !bDate) return 0
    return new Date(aDate).getTime() - new Date(bDate).getTime()
  })

  return {
    analysis: yogaAnalysis,
    timings: validTimings
  }
}
```

---

## Backend Usage

### Using Extended Yoga Service

```python
from app.services.extended_yoga_service import extended_yoga_service

# Detect yogas
def detect_chart_yogas(chart_data: Dict[str, Any]) -> List[Dict]:
    """Detect all yogas in a chart"""
    planets = chart_data.get('planets', {})
    houses = chart_data.get('houses', {})

    yogas = extended_yoga_service.detect_extended_yogas(planets, houses)

    # Filter by strength
    strong_yogas = [y for y in yogas if y.get('strength') in ['Very Strong', 'Strong']]

    return yogas

# Calculate timing
def get_yoga_timing_info(yoga: Dict, chart_data: Dict) -> Dict:
    """Get timing information for a yoga"""
    timing = extended_yoga_service.calculate_yoga_timing(
        yoga=yoga,
        chart_data=chart_data
    )

    return timing
```

### Example: Integration with AI Orchestrator

```python
from app.services.extended_yoga_service import extended_yoga_service
from app.services.ai_orchestrator import ai_orchestrator

async def generate_reading_with_yogas(
    chart_data: Dict,
    query: str,
    user_id: str
):
    """Generate AI reading with yoga context"""

    # Detect yogas
    planets = chart_data.get('planets', {})
    yogas = extended_yoga_service.detect_extended_yogas(planets)

    # Filter significant yogas
    significant_yogas = [
        y for y in yogas
        if y.get('strength') in ['Very Strong', 'Strong']
    ]

    # Prepare yoga data for AI
    yoga_data = {
        "total_yogas": len(yogas),
        "significant_yogas": len(significant_yogas),
        "yogas": significant_yogas,
        "strongest_yogas": [
            y['name'] for y in yogas
            if y.get('strength') == 'Very Strong'
        ]
    }

    # Generate reading with yoga context
    result = await ai_orchestrator.generate_comprehensive_reading(
        chart_data=chart_data,
        query=query,
        yoga_data=yoga_data  # Yoga context
    )

    return result
```

---

## Testing

### cURL Examples

```bash
# 1. Analyze yogas
curl -X POST http://localhost:8000/api/v1/enhancements/yogas/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{
    "profile_id": "123e4567-e89b-12d3-a456-426614174000",
    "include_all": true
  }'

# 2. Get yoga timing
curl -X GET "http://localhost:8000/api/v1/enhancements/yoga-timing/123e4567-e89b-12d3-a456-426614174000?yoga_name=Hamsa%20Yoga" \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

### Python Test Script

```python
import httpx
import asyncio

async def test_yoga_api():
    """Test yoga API endpoints"""

    base_url = "http://localhost:8000/api/v1/enhancements"
    token = "YOUR_JWT_TOKEN"
    headers = {"Authorization": f"Bearer {token}"}
    profile_id = "123e4567-e89b-12d3-a456-426614174000"

    async with httpx.AsyncClient() as client:
        # Test 1: Analyze yogas
        print("Testing yoga analysis...")
        response = await client.post(
            f"{base_url}/yogas/analyze",
            json={
                "profile_id": profile_id,
                "include_all": True
            },
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        print(f"✓ Found {data['total_yogas']} yogas")
        print(f"✓ Chart quality: {data['chart_quality']}")

        # Test 2: Get timing for first yoga
        if data['yogas']:
            yoga_name = data['yogas'][0]['name']
            print(f"\nTesting timing for '{yoga_name}'...")

            response = await client.get(
                f"{base_url}/yoga-timing/{profile_id}",
                params={"yoga_name": yoga_name},
                headers=headers
            )

            assert response.status_code == 200
            timing = response.json()
            print(f"✓ Activation status: {timing['activation_status']}")
            print(f"✓ Dasha periods: {len(timing['dasha_activation_periods'])}")

        print("\n✓ All tests passed!")

# Run tests
asyncio.run(test_yoga_api())
```

---

## Rate Limits

- **No specific rate limits** for yoga endpoints (inherits general API limits)
- **Recommended**: Cache yoga analysis results on frontend for 24 hours
- **Performance**: ~100ms per yoga analysis, ~30ms per timing calculation

---

## Best Practices

1. **Cache Results**: Store yoga analysis in component state to avoid re-fetching
2. **Batch Timing Requests**: Use `Promise.all()` for parallel timing fetches
3. **Filter Wisely**: Use `include_all: false` to reduce payload size
4. **Error Handling**: Always wrap API calls in try-catch blocks
5. **URL Encoding**: Encode yoga names in query params (`encodeURIComponent()`)

---

## Troubleshooting

### Issue: "Yoga not found in chart"

**Cause:** Yoga name doesn't match exactly

**Solution:** Use exact name from analysis response:
```typescript
// ✗ Wrong
yoga_name: "hamsa yoga"  // lowercase

// ✓ Correct
yoga_name: "Hamsa Yoga"  // exact match
```

### Issue: "Chart not found"

**Cause:** Chart hasn't been generated for the profile

**Solution:** Generate chart first:
```typescript
await apiClient.generateChart(profileId, 'D1')
await apiClient.analyzeYogasForProfile({ profile_id: profileId })
```

### Issue: "No dasha activation periods returned"

**Cause:** Chart doesn't have dasha data

**Solution:** Ensure Vimshottari dasha is calculated during chart generation. This should happen automatically for D1 charts.

---

## Reference

- **Main Documentation**: [YOGA_ENHANCEMENT.md](YOGA_ENHANCEMENT.md)
- **Service Code**: `backend/app/services/extended_yoga_service.py`
- **API Code**: `backend/app/api/v1/endpoints/enhancements.py`
- **Frontend Components**: `frontend/components/yoga/`

---

**End of API Reference**
