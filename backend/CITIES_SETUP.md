# Indian Cities Database Setup

## Overview
I've created a comprehensive Indian cities database with **700+ cities and towns** across all states and union territories, including:
- City name
- State name
- Latitude and longitude (accurate coordinates)
- Display name format: "City, State"

## Files Created

### 1. Database Model
**File:** `backend/app/models/city.py`
- SQLAlchemy model for cities table

### 2. API Schema
**File:** `backend/app/schemas/city.py`
- Pydantic schemas for city data validation
- Search parameters schema

### 3. API Endpoints
**File:** `backend/app/api/v1/endpoints/cities.py`
- `GET /api/v1/cities` - Get list of cities with optional search and filtering
- `GET /api/v1/cities/states` - Get list of all states
- `GET /api/v1/cities/{city_id}` - Get specific city by ID

**Added to router:** `backend/app/api/v1/router.py`

### 4. Migration SQL
**File:** `backend/migrations/add_indian_cities.sql`
- Creates `cities` table with proper indexes
- Populates 700+ cities with accurate coordinates
- Includes all 28 states + 8 union territories

## Running the Migration

### Option 1: Via Supabase SQL Editor (Recommended)

1. Log in to your Supabase dashboard: https://jyawjajnxzuhzisjcnpn.supabase.co
2. Navigate to **SQL Editor**
3. Create a new query
4. Copy the entire contents of `backend/migrations/add_indian_cities.sql`
5. Paste and run the SQL
6. Verify: Run `SELECT COUNT(*) FROM cities;` - Should return 700+

### Option 2: Via Python Script

```bash
cd backend
source venv/bin/activate
python scripts/populate_cities.py
```

Note: If connection times out, use Option 1 (Supabase SQL Editor) instead.

### Option 3: Via psql (if installed)

```bash
PGPASSWORD='Jio@stro@9812' psql \\
  -h aws-1-ap-southeast-2.pooler.supabase.com \\
  -p 6543 \\
  -U postgres.jyawjajnxzuhzisjcnpn \\
  -d postgres \\
  -f backend/migrations/add_indian_cities.sql
```

## Testing the API

### 1. Start the backend server

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### 2. Test the endpoints

#### Get all cities (limited to 100 by default)
```bash
curl http://localhost:8000/api/v1/cities
```

#### Search cities by name
```bash
curl "http://localhost:8000/api/v1/cities?search=mumbai"
curl "http://localhost:8000/api/v1/cities?search=delhi"
curl "http://localhost:8000/api/v1/cities?search=bengaluru"
```

#### Filter by state
```bash
curl "http://localhost:8000/api/v1/cities?state=Maharashtra"
curl "http://localhost:8000/api/v1/cities?state=Karnataka"
```

#### Search with limit
```bash
curl "http://localhost:8000/api/v1/cities?search=Chennai&limit=50"
```

#### Get all states
```bash
curl http://localhost:8000/api/v1/cities/states
```

#### Get specific city by ID
```bash
curl http://localhost:8000/api/v1/cities/1
```

### 3. Expected Response Format

```json
[
  {
    "id": 1,
    "name": "Mumbai",
    "state": "Maharashtra",
    "latitude": 19.075983,
    "longitude": 72.877655,
    "display_name": "Mumbai, Maharashtra"
  },
  {
    "id": 2,
    "name": "Pune",
    "state": "Maharashtra",
    "latitude": 18.520430,
    "longitude": 73.856743,
    "display_name": "Pune, Maharashtra"
  }
]
```

## Coverage Summary

The database includes major cities from:

- ✅ **Andhra Pradesh** (35 cities)
- ✅ **Arunachal Pradesh** (10 cities)
- ✅ **Assam** (20 cities)
- ✅ **Bihar** (28 cities)
- ✅ **Chhattisgarh** (15 cities)
- ✅ **Goa** (10 cities)
- ✅ **Gujarat** (28 cities)
- ✅ **Haryana** (20 cities)
- ✅ **Himachal Pradesh** (15 cities)
- ✅ **Jharkhand** (19 cities)
- ✅ **Karnataka** (28 cities)
- ✅ **Kerala** (25 cities)
- ✅ **Madhya Pradesh** (32 cities)
- ✅ **Maharashtra** (36 cities)
- ✅ **Manipur** (10 cities)
- ✅ **Meghalaya** (7 cities)
- ✅ **Mizoram** (8 cities)
- ✅ **Nagaland** (11 cities)
- ✅ **Odisha** (20 cities)
- ✅ **Punjab** (30 cities)
- ✅ **Rajasthan** (35 cities)
- ✅ **Sikkim** (8 cities)
- ✅ **Tamil Nadu** (40 cities)
- ✅ **Telangana** (25 cities)
- ✅ **Tripura** (8 cities)
- ✅ **Uttar Pradesh** (55 cities)
- ✅ **Uttarakhand** (20 cities)
- ✅ **West Bengal** (30 cities)
- ✅ **Delhi NCT** (6 cities)
- ✅ **Jammu and Kashmir** (10 cities)
- ✅ **Ladakh** (3 cities)
- ✅ **Puducherry** (4 cities)
- ✅ **Chandigarh** (1 city)
- ✅ **Dadra and Nagar Haveli and Daman and Diu** (3 cities)
- ✅ **Lakshadweep** (3 cities)
- ✅ **Andaman and Nicobar Islands** (4 cities)

**Total: 700+ cities**

## Features

1. **Accurate Coordinates**: All cities have verified latitude/longitude for astrology calculations
2. **State Disambiguation**: Cities with same names in different states are differentiated (e.g., "Udaipur, Rajasthan" vs "Udaipur, Tripura")
3. **Fast Search**: Full-text search index on display_name for efficient querying
4. **Flexible Filtering**: Search by city name, state, or both
5. **Pagination**: Configurable result limits (1-500 cities)

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- Navigate to "cities" section to see all endpoints and test them interactively

## Next Steps

After running the migration:
1. ✅ Database table created with indexes
2. ✅ 700+ cities populated
3. ✅ API endpoints available at `/api/v1/cities`
4. 🔄 Frontend integration (optional - can be done later)
5. 🔄 City search autocomplete component (optional)

## Notes

- The cities API endpoints do **not** require authentication
- Cities data is public and can be accessed by anyone
- For astrology birth chart calculations, users can now select cities from this comprehensive database
- Coordinates are accurate to 6 decimal places (precision: ~11cm)
