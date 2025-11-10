# Calendar Year Predictions Feature

**Status:** 🚧 In Progress
**Type:** Separate feature from Varshaphal (Solar Return)
**Purpose:** Transit-based predictions for calendar years (Jan 1 - Dec 31)

---

## Overview

This is a **new feature** separate from Varshaphal, providing transit-based annual predictions for calendar years. Unlike Varshaphal which runs birthday to birthday, this runs from January 1 to December 31 of the selected year.

### Key Differences

| Aspect | Varshaphal (Solar Return) | Calendar Year Predictions |
|--------|--------------------------|---------------------------|
| **Period** | Birthday to birthday | Jan 1 - Dec 31 |
| **Chart Type** | Solar return chart | Natal chart + transits |
| **Method** | Varshaphal yogas, Patyayini Dasha | Transit analysis (Gochar) |
| **Start Date** | Unique per person | Same for everyone (Jan 1) |
| **Best For** | Annual predictions, timing | Year planning, monthly overview |

---

## Implementation Status

### ✅ Completed

#### 1. Backend Service (`app/services/calendar_year_service.py`)

**Features Implemented:**
- ✅ **Monthly Transit Predictions** - 12 month analysis with quality ratings
- ✅ **Major Transits** - Saturn, Jupiter, Rahu/Ketu movement tracking
- ✅ **Eclipse Predictions** - Solar and lunar eclipses with dates and effects
- ✅ **Best/Worst Months** - Identifies favorable and challenging periods
- ✅ **Opportunities & Challenges** - Key themes for the year
- ✅ **Remedies** - Recommendations for difficult periods
- ✅ **Month Quality Rating** - Excellent, Very Good, Moderate, Challenging, Difficult

**Technical Details:**
- Uses Swiss Ephemeris for accurate transit calculations
- Analyzes Jupiter and Saturn positions for monthly quality
- Eclipse detection using built-in Swiss Ephemeris functions
- House-based transit analysis from Moon sign
- Comprehensive effects for each planetary transit

### ⏳ In Progress

#### 2. API Schemas (`app/schemas/calendar_year.py`)

Need to create Pydantic schemas for:
- Request: `CalendarYearRequest` (profile_id, target_year)
- Response: `CalendarYearResponse` (monthly predictions, transits, eclipses)
- Supporting schemas for nested data

#### 3. API Endpoints (`app/api/v1/endpoints/calendar_year.py`)

Need to create endpoints:
- `POST /api/v1/calendar-year/generate` - Generate predictions
- `GET /api/v1/calendar-year/{id}` - Get specific prediction
- `GET /api/v1/calendar-year/list` - List all predictions
- `DELETE /api/v1/calendar-year/{id}` - Delete prediction

### 📋 Pending

#### 4. Frontend Page (`app/dashboard/calendar-year/page.tsx`)

Features to implement:
- Year and profile selection
- Monthly predictions display (calendar view or list)
- Major transits timeline
- Eclipse warnings and dates
- Best/worst months highlighting
- Opportunity and challenge lists
- Remedies section

#### 5. Database Schema (Optional)

If we want to cache predictions:
- Create `calendar_year_predictions` table
- Similar structure to `varshaphal_data`
- Store generated predictions for reuse

#### 6. Navigation

Add links to:
- Main dashboard
- Advanced features menu
- Sidebar navigation

---

## Feature Capabilities

### What This Feature Provides

**1. Monthly Predictions (January - December)**
Each month includes:
- Quality rating (Excellent → Difficult)
- Sun sign position
- Jupiter and Saturn house positions
- Key themes and focus areas
- Specific advice
- Important dates (Full Moon, New Moon)

**Example Output:**
```json
{
  "month": "March",
  "quality": "Excellent",
  "sun_sign": "Pisces",
  "jupiter_house": 5,
  "saturn_house": 11,
  "key_themes": ["Growth and expansion", "Positive opportunities", "Creativity"],
  "focus_areas": ["Major initiatives", "Investments", "New beginnings"],
  "advice": "Excellent time for important decisions and new projects"
}
```

**2. Major Planetary Transits**
Tracks slow-moving planets:
- **Jupiter** - Expands areas it transits (1 year per sign)
- **Saturn** - Tests and strengthens (2.5 years per sign)
- **Rahu/Ketu** - Bring unconventional changes (1.5 years per sign)

Detects:
- Sign changes during the year
- Exact dates of transit shifts
- Effects on natal chart houses
- Significance levels

**3. Eclipse Predictions**
Finds all eclipses in the year:
- Solar eclipses (external changes)
- Lunar eclipses (emotional/internal)
- Dates and times
- Type (total, partial, annular)
- Effects and recommendations

**4. Best & Worst Months**
Identifies:
- Top 3 most favorable months
- 2 most challenging months
- Reasons (based on transits)
- How to utilize/navigate them

**5. Year Overview**
Comprehensive summary:
- Overall year quality
- Key opportunities
- Main challenges
- Recommended remedies
- Important themes

---

## User Experience

### How Users Will Use This

1. **Select Profile & Year**
   - Choose a birth profile
   - Select calendar year (2024, 2025, 2026, etc.)
   - Click "Generate Predictions"

2. **View Monthly Breakdown**
   - See all 12 months at a glance
   - Color-coded by quality (green = good, yellow = moderate, red = challenging)
   - Click month for detailed view

3. **Check Major Events**
   - See when Jupiter/Saturn change signs
   - Eclipse dates and preparation needed
   - Important planetary movements

4. **Plan Year Activities**
   - Use best months for major decisions, investments, launches
   - Avoid worst months for risky ventures
   - Time important events with favorable transits

5. **Apply Remedies**
   - Get specific remedies for challenging periods
   - Follow monthly advice
   - Strengthen weak areas

---

## Next Steps

### Immediate Tasks

1. **Create Schemas** (`app/schemas/calendar_year.py`)
   ```python
   - CalendarYearRequest
   - CalendarYearResponse
   - MonthlyPrediction
   - MajorTransit
   - Eclipse
   ```

2. **Create API Endpoints** (`app/api/v1/endpoints/calendar_year.py`)
   ```python
   - generate_calendar_year()
   - get_calendar_year()
   - list_calendar_years()
   - delete_calendar_year()
   ```

3. **Register Router** (in `app/api/v1/router.py`)
   ```python
   from app.api.v1.endpoints import calendar_year
   router.include_router(calendar_year.router, prefix="/calendar-year", tags=["Calendar Year"])
   ```

4. **Add to API Client** (`frontend/lib/api.ts`)
   ```typescript
   async generateCalendarYear(data: any)
   async getCalendarYear(id: string)
   async listCalendarYears()
   ```

5. **Create Frontend Page** (`app/dashboard/calendar-year/page.tsx`)
   - Selection UI
   - Monthly calendar/list view
   - Transit timeline
   - Eclipse alerts

6. **Add Navigation Link**
   - Dashboard sidebar
   - Advanced features section
   - Main menu

---

## Testing Plan

### Unit Tests
- ✅ Transit calculation accuracy
- ✅ Eclipse detection
- ✅ Month quality determination
- ✅ House calculations

### Integration Tests
- API endpoint responses
- Data persistence
- Cache functionality

### User Acceptance Tests
- Generate predictions for test profile
- Verify all 12 months appear
- Check eclipse dates are accurate
- Confirm major transits are correct

---

## Benefits for Users

### Why This Is Valuable

1. **Clear Calendar Planning**
   - Know which months are favorable
   - Plan important events accordingly
   - Avoid mistakes during difficult periods

2. **Complementary to Varshaphal**
   - Varshaphal: Personal annual chart (birthday-based)
   - Calendar Year: Universal timing (calendar-based)
   - Together: Complete annual guidance

3. **Easy to Understand**
   - Calendar months are familiar
   - Color-coded quality ratings
   - Simple monthly themes

4. **Practical Application**
   - Business planning
   - Life events timing
   - Travel planning
   - Investment decisions

---

## Technical Architecture

### Data Flow

```
User Request
    ↓
Frontend: Select profile + year
    ↓
API: POST /calendar-year/generate
    ↓
Service: Calculate transits for Jan 1 - Dec 31
    ↓
  - Get natal chart
  - Calculate planetary positions each month
  - Find major transit events
  - Detect eclipses
  - Determine monthly quality
  - Generate advice
    ↓
Database: Store predictions (optional caching)
    ↓
Response: Return complete year analysis
    ↓
Frontend: Display monthly calendar + events
```

### Performance

- **Calculation Time:** ~1-2 seconds per year
- **Caching:** 30 days (predictions don't change)
- **Data Size:** ~50-100 KB per year

---

## Future Enhancements

### Possible Additions

1. **Interactive Calendar View**
   - Visual calendar with quality colors
   - Click day for detailed transits
   - Mark important dates

2. **PDF Export**
   - Printable year planner
   - Month-by-month guide
   - Important dates highlighted

3. **Notifications**
   - Eclipse reminders
   - Major transit alerts
   - Best period notifications

4. **Multi-Year View**
   - Compare multiple years
   - Identify long-term patterns
   - Saturn/Jupiter cycles

5. **Custom Event Timing**
   - Input planned event
   - System suggests best dates
   - Avoid unfavorable periods

---

## Status Summary

**Completed:** Backend service with full calculation logic
**In Progress:** API schemas and endpoints
**Pending:** Frontend UI, navigation, testing

**Estimated Time to Complete:** 2-3 hours

**Next Action:** Create API schemas and endpoints

---

**Created:** 2025-11-10
**Last Updated:** 2025-11-10
