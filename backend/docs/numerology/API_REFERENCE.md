# Numerology API Reference

Complete API documentation for all numerology endpoints in JioAstro.

**Base URL**: `/api/v1/numerology`

**Authentication**: All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

---

## Table of Contents
1. [Calculation Endpoints](#calculation-endpoints)
2. [Profile Management](#profile-management)
3. [Name Trials](#name-trials)
4. [Comparison Tools](#comparison-tools)
5. [Error Codes](#error-codes)
6. [Rate Limiting](#rate-limiting)

---

## Calculation Endpoints

### POST /calculate

Calculate numerology on-demand without saving to database.

**Request Body**:
```json
{
  "full_name": "John Doe",
  "birth_date": "1990-06-15",
  "system": "both",
  "common_name": "John",
  "name_at_birth": "Jonathan Doe",
  "profile_id": "uuid-optional"
}
```

**Parameters**:
- `full_name` (required): Full name as it appears on birth certificate
- `birth_date` (required): Birth date in YYYY-MM-DD format
- `system` (optional): "western", "vedic", "chaldean", or "both" (default: "both")
- `common_name` (optional): Common name or nickname
- `name_at_birth` (optional): Name at birth if different from current
- `profile_id` (optional): Link to existing birth profile UUID

**Response** (200 OK):
```json
{
  "system": "both",
  "western": {
    "system": "western",
    "core_numbers": {
      "life_path": {
        "number": 4,
        "is_master": false,
        "karmic_debt": 13,
        "meaning": "The Builder - practical, stable, hardworking",
        "breakdown": {
          "month": 6,
          "day": 6,
          "year": 4
        }
      },
      "expression": {
        "number": 8,
        "is_master": false,
        "meaning": "Natural authority and material success"
      },
      "soul_urge": {
        "number": 6,
        "is_master": false,
        "meaning": "Desire for harmony and service"
      },
      "personality": {
        "number": 2,
        "is_master": false,
        "meaning": "Appears diplomatic and cooperative"
      },
      "maturity": {
        "number": 3,
        "is_master": false,
        "meaning": "Later life focused on creativity"
      },
      "birth_day": {
        "number": 6,
        "karmic_debt": null,
        "meaning": "Natural counselor and helper"
      }
    },
    "special_numbers": {
      "master_numbers": [],
      "karmic_debt_numbers": [13]
    },
    "current_cycles": {
      "personal_year": {
        "number": 8,
        "meaning": "Year of power and achievement"
      },
      "personal_month": {
        "number": 3,
        "meaning": "Month of creative expression"
      },
      "personal_day": {
        "number": 5,
        "meaning": "Day of change and freedom"
      },
      "universal_year": {
        "number": 9,
        "meaning": "Universal year of completion"
      }
    },
    "life_periods": {
      "pinnacles": [
        {
          "number": 2,
          "age_range": "0-27",
          "meaning": "Early life focused on cooperation"
        },
        {
          "number": 6,
          "age_range": "28-36",
          "meaning": "Middle years centered on family"
        },
        {
          "number": 8,
          "age_range": "37-45",
          "meaning": "Later middle age brings material success"
        },
        {
          "number": 5,
          "age_range": "46+",
          "meaning": "Final years seek freedom and adventure"
        }
      ],
      "challenges": [
        {
          "number": 4,
          "age_range": "0-27",
          "meaning": "Early challenge with discipline"
        },
        {
          "number": 0,
          "age_range": "28-36",
          "meaning": "Life is your classroom"
        },
        {
          "number": 4,
          "age_range": "37-45",
          "meaning": "Continue learning structure"
        },
        {
          "number": 2,
          "age_range": "46+",
          "meaning": "Final challenge with patience"
        }
      ]
    },
    "calculation_hash": "abc123...",
    "calculated_at": "2025-11-05T10:30:00Z"
  },
  "vedic": {
    "system": "vedic",
    "psychic_number": {
      "number": 6,
      "planet": "Venus",
      "meaning": "Artistic, loving, luxurious",
      "favorable_dates": [6, 15, 24],
      "favorable_colors": ["white", "light blue", "pink"],
      "favorable_gems": ["diamond", "white sapphire"],
      "favorable_days": ["Friday"]
    },
    "destiny_number": {
      "number": 4,
      "planet": "Rahu",
      "meaning": "Unconventional, materialistic",
      "favorable_dates": [4, 13, 22, 31],
      "favorable_colors": ["grey", "black"],
      "favorable_gems": ["hessonite"],
      "favorable_days": ["Saturday"]
    },
    "name_number": {
      "number": 7,
      "meaning": "Mysterious, spiritual nature"
    },
    "calculation_hash": "def456...",
    "calculated_at": "2025-11-05T10:30:00Z"
  },
  "calculation_hash": "combined_hash",
  "calculated_at": "2025-11-05T10:30:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication token
- `422 Unprocessable Entity`: Validation error

---

## Profile Management

### POST /profiles

Create and save a numerology profile.

**Request Body**: Same as `/calculate`

**Response** (201 Created):
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "profile_id": "uuid",
  "full_name": "John Doe",
  "common_name": "John",
  "name_at_birth": "Jonathan Doe",
  "birth_date": "1990-06-15",
  "system": "both",
  "western_data": { ... },
  "vedic_data": { ... },
  "cycles": { ... },
  "calculation_hash": "abc123...",
  "calculated_at": "2025-11-05T10:30:00Z",
  "created_at": "2025-11-05T10:30:00Z",
  "updated_at": "2025-11-05T10:30:00Z"
}
```

---

### GET /profiles

List all numerology profiles for the authenticated user.

**Query Parameters**:
- `limit` (optional): Number of profiles to return (default: 20, max: 100)
- `offset` (optional): Number of profiles to skip (default: 0)

**Response** (200 OK):
```json
[
  {
    "id": "uuid",
    "full_name": "John Doe",
    "birth_date": "1990-06-15",
    "system": "both",
    "created_at": "2025-11-05T10:30:00Z"
  },
  ...
]
```

---

### GET /profiles/{id}

Get a specific numerology profile by ID.

**Path Parameters**:
- `id` (required): Profile UUID

**Response** (200 OK): Same as POST /profiles response

**Error Responses**:
- `404 Not Found`: Profile doesn't exist or doesn't belong to user

---

### PATCH /profiles/{id}

Update a numerology profile.

**Path Parameters**:
- `id` (required): Profile UUID

**Request Body**:
```json
{
  "full_name": "John Michael Doe",
  "common_name": "JD"
}
```

**Updatable Fields**:
- `full_name`
- `common_name`
- `name_at_birth`

**Note**: Updating `full_name` will trigger recalculation of all name-based numbers.

**Response** (200 OK): Updated profile object

---

### DELETE /profiles/{id}

Delete a numerology profile.

**Path Parameters**:
- `id` (required): Profile UUID

**Response** (204 No Content)

---

## Name Trials

### POST /profiles/{profile_id}/name-trials

Create a name trial for testing alternative names.

**Path Parameters**:
- `profile_id` (required): Numerology profile UUID

**Request Body**:
```json
{
  "trial_name": "Jon Doe",
  "system": "western",
  "notes": "Testing shorter first name",
  "is_preferred": false
}
```

**Parameters**:
- `trial_name` (required): Alternative name to test
- `system` (required): "western", "vedic", or "chaldean"
- `notes` (optional): Reason for testing this name
- `is_preferred` (optional): Mark as preferred name (default: false)

**Response** (201 Created):
```json
{
  "id": "uuid",
  "numerology_profile_id": "uuid",
  "user_id": "uuid",
  "trial_name": "Jon Doe",
  "system": "western",
  "calculated_values": {
    "expression": { "number": 7, ... },
    "soul_urge": { "number": 6, ... },
    "personality": { "number": 1, ... }
  },
  "notes": "Testing shorter first name",
  "is_preferred": false,
  "created_at": "2025-11-05T10:30:00Z"
}
```

---

### GET /profiles/{profile_id}/name-trials

Get all name trials for a profile.

**Path Parameters**:
- `profile_id` (required): Numerology profile UUID

**Response** (200 OK):
```json
[
  {
    "id": "uuid",
    "trial_name": "Jon Doe",
    "system": "western",
    "calculated_values": { ... },
    "notes": "Testing shorter first name",
    "is_preferred": false,
    "created_at": "2025-11-05T10:30:00Z"
  },
  ...
]
```

---

### PATCH /profiles/{profile_id}/name-trials/{trial_id}

Update a name trial (notes or preferred status).

**Path Parameters**:
- `profile_id` (required): Numerology profile UUID
- `trial_id` (required): Name trial UUID

**Request Body**:
```json
{
  "notes": "Updated notes",
  "is_preferred": true
}
```

**Response** (200 OK): Updated name trial object

---

### DELETE /profiles/{profile_id}/name-trials/{trial_id}

Delete a name trial.

**Path Parameters**:
- `profile_id` (required): Numerology profile UUID
- `trial_id` (required): Name trial UUID

**Response** (204 No Content)

---

## Comparison Tools

### POST /compare

Compare multiple name variations side-by-side.

**Request Body**:
```json
{
  "names": [
    "John Doe",
    "Jon Doe",
    "Jonathan Doe",
    "J. Doe"
  ],
  "birth_date": "1990-06-15",
  "system": "western"
}
```

**Parameters**:
- `names` (required): Array of 2-5 names to compare
- `birth_date` (required): Birth date for Life Path calculation
- `system` (required): "western", "vedic", or "chaldean"

**Response** (200 OK):
```json
{
  "system": "western",
  "birth_date": "1990-06-15",
  "comparisons": [
    {
      "name": "John Doe",
      "western": {
        "core_numbers": {
          "life_path": { "number": 4, ... },
          "expression": { "number": 8, ... },
          "soul_urge": { "number": 6, ... },
          "personality": { "number": 2, ... }
        }
      }
    },
    {
      "name": "Jon Doe",
      "western": {
        "core_numbers": {
          "life_path": { "number": 4, ... },
          "expression": { "number": 7, ... },
          "soul_urge": { "number": 6, ... },
          "personality": { "number": 1, ... }
        }
      }
    },
    ...
  ],
  "recommendation": {
    "best_name": "Jonathan Doe",
    "reason": "Highest number of master numbers and favorable planetary alignments"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Less than 2 or more than 5 names provided

---

## Error Codes

### Standard HTTP Error Responses

**400 Bad Request**
```json
{
  "detail": "Invalid input: birth_date must be in YYYY-MM-DD format"
}
```

**401 Unauthorized**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden**
```json
{
  "detail": "Not enough permissions"
}
```

**404 Not Found**
```json
{
  "detail": "Numerology profile not found"
}
```

**422 Unprocessable Entity**
```json
{
  "detail": [
    {
      "loc": ["body", "full_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

### Limits
- **Anonymous users**: Not allowed (authentication required)
- **Authenticated users**: 100 requests per hour per endpoint
- **Premium users**: 500 requests per hour per endpoint

### Rate Limit Headers
Every response includes:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1699123456
```

### Rate Limit Exceeded Response (429)
```json
{
  "detail": "Rate limit exceeded. Try again in 3600 seconds.",
  "retry_after": 3600
}
```

---

## Authentication

All numerology endpoints require authentication. Include the JWT token in the Authorization header:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

To obtain a token, authenticate via Supabase Auth (see main API documentation).

---

## Example cURL Requests

### Calculate Numerology
```bash
curl -X POST https://api.jioastro.com/api/v1/numerology/calculate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "birth_date": "1990-06-15",
    "system": "both"
  }'
```

### Create Profile
```bash
curl -X POST https://api.jioastro.com/api/v1/numerology/profiles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "birth_date": "1990-06-15",
    "system": "both",
    "common_name": "John"
  }'
```

### List Profiles
```bash
curl -X GET https://api.jioastro.com/api/v1/numerology/profiles?limit=10 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Compare Names
```bash
curl -X POST https://api.jioastro.com/api/v1/numerology/compare \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "names": ["John Doe", "Jon Doe", "Jonathan Doe"],
    "birth_date": "1990-06-15",
    "system": "western"
  }'
```

---

## Webhooks (Future Feature)

Coming soon: Webhook support for numerology profile events.

Planned events:
- `numerology.profile.created`
- `numerology.profile.updated`
- `numerology.profile.deleted`
- `numerology.name_trial.created`

---

## SDK Support

### Python SDK
```python
from jioastro import NumerologyClient

client = NumerologyClient(token="YOUR_TOKEN")

# Calculate numerology
result = client.calculate(
    full_name="John Doe",
    birth_date="1990-06-15",
    system="both"
)

# Create profile
profile = client.create_profile(
    full_name="John Doe",
    birth_date="1990-06-15"
)

# Compare names
comparison = client.compare_names(
    names=["John Doe", "Jon Doe"],
    birth_date="1990-06-15",
    system="western"
)
```

### JavaScript SDK
```javascript
import { NumerologyClient } from '@jioastro/sdk';

const client = new NumerologyClient({ token: 'YOUR_TOKEN' });

// Calculate numerology
const result = await client.calculate({
  fullName: 'John Doe',
  birthDate: '1990-06-15',
  system: 'both'
});

// Create profile
const profile = await client.createProfile({
  fullName: 'John Doe',
  birthDate: '1990-06-15'
});
```

---

## Changelog

### v1.0.0 (2025-11-05)
- Initial release
- 11 endpoints covering calculation, profile management, name trials, and comparison
- Support for Western (Pythagorean) and Vedic (Chaldean) systems
- Calculation hash caching for performance
- Rate limiting implementation

---

For questions or support, contact: support@jioastro.com
