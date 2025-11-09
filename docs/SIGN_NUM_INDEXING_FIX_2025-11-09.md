# Sign Number Indexing Fix

**Date**: 2025-11-09
**Issue**: Invalid sign_num for Ketu: 0
**Status**: ✅ FIXED

---

## Problem Description

The backend was using 0-based indexing (0-11) for zodiac signs, while the frontend expected 1-based indexing (1-12) according to Vedic astrology convention:

- **Backend**: Aries=0, Taurus=1, ..., Pisces=11
- **Frontend**: Aries=1, Taurus=2, ..., Pisces=12

This caused validation errors in the chart data transformer, particularly visible with Ketu when it was in Aries (sign 0).

### Error Message
```
Invalid chart data format
Invalid sign_num for Ketu: 0
```

---

## Root Cause

In `backend/app/services/vedic_astrology_accurate.py`, all zodiac sign calculations used Python's 0-indexed array system:

```python
# SIGNS array is 0-indexed
SIGNS = ["Aries", "Taurus", ..., "Pisces"]  # Index 0-11

# Calculation produces 0-11
sign = int(sidereal_long / 30)  # Returns 0-11

# But was stored as-is without converting to 1-based
"sign_num": sign  # PROBLEM: 0-11 instead of 1-12
```

This affected:
- All 9 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
- Ascendant (Lagna)
- All 12 houses
- Navamsa (D9) chart positions

---

## Solution

Added `+ 1` to all `sign_num` assignments to convert from 0-indexed (0-11) to 1-indexed (1-12).

### Files Modified

**1. Backend: `backend/app/services/vedic_astrology_accurate.py`**

#### Planets (Line 262)
```python
# BEFORE
planets_data[planet_name] = {
    "sign_num": sign,  # 0-11
}

# AFTER
planets_data[planet_name] = {
    "sign_num": sign + 1,  # Convert to 1-12
}
```

#### Ketu (Line 279)
```python
# BEFORE
planets_data["Ketu"] = {
    "sign_num": ketu_sign,  # 0-11
}

# AFTER
planets_data["Ketu"] = {
    "sign_num": ketu_sign + 1,  # Convert to 1-12
}
```

#### Ascendant (Line 218)
```python
# BEFORE
"ascendant": {
    "sign_num": asc_sign,  # 0-11
}

# AFTER
"ascendant": {
    "sign_num": asc_sign + 1,  # Convert to 1-12
}
```

#### Houses (Line 301)
```python
# BEFORE
houses.append({
    "sign_num": house_sign,  # 0-11
})

# AFTER
houses.append({
    "sign_num": house_sign + 1,  # Convert to 1-12
})
```

#### Navamsa (Line 555)
```python
# BEFORE
return {
    "sign_num": navamsa_sign,  # 0-11
}

# AFTER
return {
    "sign_num": navamsa_sign + 1,  # Convert to 1-12
}
```

**2. Frontend: `frontend/lib/chartDataTransformer.ts`**

Removed incorrect edge case handling that was trying to normalize 0 → 12:

```typescript
// REMOVED (incorrect logic)
if (planet.sign_num === 0) {
  console.warn(`Planet ${name} has sign_num 0, normalizing to 12 (Pisces)`)
  planet.sign_num = 12  // WRONG: 0 should be 1 (Aries), not 12 (Pisces)
}

// KEPT (clean validation)
if (!planet.sign_num || planet.sign_num < 1 || planet.sign_num > 12) {
  console.error(`Invalid sign_num for ${name}: ${planet.sign_num}`)
  return false
}
```

---

## Testing

### Manual Testing Steps

1. **Start Development Server**
   ```bash
   # Backend (already running)
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload

   # Frontend
   cd frontend
   npm run dev
   ```

2. **Navigate to Chart Page**
   ```
   http://localhost:3000/dashboard/chart/[any-profile-id]
   ```

3. **Verify in Browser Console**
   - ✅ No "Invalid sign_num" errors
   - ✅ No validation failures
   - ✅ Chart renders correctly
   - ✅ All planets positioned properly

4. **Check Chart Data**
   Open browser console and verify chart data structure:
   ```javascript
   // All sign_num values should be 1-12
   chartData.ascendant.sign_num  // Should be 1-12
   chartData.planets.Sun.sign_num  // Should be 1-12
   chartData.planets.Ketu.sign_num  // Should be 1-12 (not 0!)
   ```

### Test Cases

Test different ascendants and planet positions:

| Test Case | Ascendant | Ketu Expected Sign | Expected sign_num |
|-----------|-----------|-------------------|-------------------|
| 1 | Aries (1) | Depends on Rahu | 1-12 (never 0) |
| 2 | Leo (5) | Depends on Rahu | 1-12 (never 0) |
| 3 | Pisces (12) | Depends on Rahu | 1-12 (never 0) |

### Automated Testing

Run integration test suite:
```bash
cd frontend
npm test lib/__tests__/northIndianChartIntegration.test.ts
```

Expected results:
- ✅ All 9 tests pass
- ✅ No validation errors
- ✅ Planet mappings correct
- ✅ Sign numbers in valid range (1-12)

---

## Verification Checklist

- [x] Backend changes applied to `vedic_astrology_accurate.py`
- [x] Frontend changes applied to `chartDataTransformer.ts`
- [x] Backend server restarted (running on port 8000)
- [ ] Manual browser testing completed
- [ ] No console errors observed
- [ ] Charts rendering correctly
- [ ] All planets positioned in correct signs
- [ ] Integration tests pass

---

## Impact Assessment

### Breaking Changes
❌ **None** - This is a bug fix that aligns backend with expected frontend format

### Affected Components
- ✅ Birth chart (D1) calculations
- ✅ Navamsa chart (D9) calculations
- ✅ Moon chart calculations
- ✅ Divisional charts (D2-D60)
- ✅ House calculations
- ✅ Yoga detections (uses planet sign positions)
- ✅ Dosha detections (uses planet sign positions)

### Data Migration
✅ **Not Required** - Charts are calculated on-demand, no stored data affected

---

## Related Documentation

- **Integration Guide**: `docs/NORTH_INDIAN_CHART_INTEGRATION_SUMMARY.md`
- **Version Control**: `docs/NORTH_INDIAN_CHART_VERSIONS.md`
- **Backend Service**: `backend/app/services/vedic_astrology_accurate.py`
- **Data Transformer**: `frontend/lib/chartDataTransformer.ts`
- **Test Suite**: `frontend/lib/__tests__/northIndianChartIntegration.test.ts`

---

## Technical Notes

### Why 1-Based Indexing?

Vedic astrology traditionally numbers zodiac signs from 1-12:
- 1 = Aries (Mesha)
- 2 = Taurus (Vrishabha)
- ...
- 12 = Pisces (Meena)

The backend's internal SIGNS array uses Python's 0-based indexing (0-11) for array access, but the API should return 1-based values (1-12) to match:
- Vedic astrology conventions
- Frontend expectations
- User-facing displays

### Why Not Change Frontend?

We could have changed the frontend to accept 0-11, but:
1. ❌ More confusing for users (Aries=0 is counterintuitive)
2. ❌ Breaks convention in astrology literature (always 1-12)
3. ❌ Would require changes in multiple components
4. ✅ Backend API should provide semantic values (1-12)

### Internal vs External Representation

**Best Practice**: Use 0-based internally (for array indexing), but convert to 1-based for API responses:

```python
# Internal: 0-based for array access
sign_index = int(longitude / 30)  # 0-11
sign_name = SIGNS[sign_index]     # Array access

# External: 1-based for API
"sign_num": sign_index + 1        # Convert to 1-12 for API response
```

---

## Future Improvements

1. **Add Backend Tests**: Test that all sign_num values are 1-12
2. **Add API Contract Tests**: Verify API always returns 1-12 range
3. **Add JSDoc Comments**: Document expected range in type definitions
4. **Type Safety**: Add TypeScript types that enforce 1-12 range

---

**Fix Applied**: 2025-11-09
**Tested By**: Pending manual verification
**Status**: ✅ READY FOR TESTING
