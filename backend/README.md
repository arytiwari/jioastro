# Vedic AI Astrology - Backend API

FastAPI-based backend for AI-powered Vedic astrology service.

## Features

- Birth chart generation (D1 Rashi and D9 Navamsa charts)
- Vedic astrology calculations using Swiss Ephemeris
- AI-powered interpretations using OpenAI GPT-4
- User authentication (via Supabase)
- Rate limiting
- Feedback system

## Setup

### Requirements

- Python 3.11+
- PostgreSQL (or Supabase account)
- Redis (or Upstash account)
- OpenAI API key

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

4. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Docker

Build and run with Docker:

```bash
docker build -t vedic-astrology-api .
docker run -p 8000:8000 --env-file .env vedic-astrology-api
```

## API Endpoints

### Profiles
- `POST /api/v1/profiles` - Create birth profile
- `GET /api/v1/profiles` - List profiles
- `GET /api/v1/profiles/{id}` - Get specific profile
- `PATCH /api/v1/profiles/{id}` - Update profile
- `DELETE /api/v1/profiles/{id}` - Delete profile

### Charts
- `POST /api/v1/charts/calculate` - Calculate chart (D1 or D9)
- `GET /api/v1/charts/{profile_id}/{chart_type}` - Get cached chart
- `DELETE /api/v1/charts/{profile_id}/{chart_type}` - Delete cached chart

### Queries
- `POST /api/v1/queries` - Submit question and get AI interpretation
- `GET /api/v1/queries` - List query history
- `GET /api/v1/queries/{id}` - Get specific query and response

### Feedback
- `POST /api/v1/feedback` - Submit feedback for interpretation
- `GET /api/v1/feedback/response/{response_id}` - Get feedback
- `GET /api/v1/feedback/stats` - Get feedback statistics

## Astrological Calculations

- **Zodiac System**: Sidereal (Vedic)
- **Ayanamsa**: Lahiri
- **Dasha System**: Vimshottari
- **Chart Types**: D1 (Rashi), D9 (Navamsa)
- **Yogas**: Raj Yoga, Dhana Yoga, Gaja Kesari, and more

## Rate Limiting

- Default: 10 queries per day per user
- Configurable via `RATE_LIMIT_QUERIES_PER_DAY` environment variable

## License

MIT License
