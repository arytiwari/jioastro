# Clear Old Charts from Database

## Issue
Old chart data in Supabase has incomplete structure (missing `houses`, `ascendant`, etc.) causing frontend errors.

## Solution
Delete all old charts from the database. They will be automatically recalculated with the correct structure on next access.

## Option 1: SQL Query (Recommended - Fast)

Run this SQL query in your Supabase SQL Editor:

```sql
-- Delete all existing charts
DELETE FROM charts;

-- Verify deletion
SELECT COUNT(*) FROM charts;
-- Should return 0
```

### Steps:
1. Go to https://supabase.com/dashboard
2. Select your project
3. Click "SQL Editor" in the left sidebar
4. Click "New Query"
5. Paste the DELETE statement above
6. Click "Run" or press Ctrl+Enter
7. Verify with the SELECT statement

## Option 2: Via Backend API (Slower)

If you have the backend running, you can delete charts via API:

```bash
# Get your JWT token from the browser console
# Go to Application > Local Storage > your Supabase URL
# Find and copy the 'sb-<project>-auth-token' value

# Set your token
TOKEN="your-jwt-token-here"

# Get your profile ID (check the URL when viewing a profile)
PROFILE_ID="your-profile-id-here"

# Delete D1 chart
curl -X DELETE "http://localhost:8000/api/v1/charts/${PROFILE_ID}/D1" \
  -H "Authorization: Bearer ${TOKEN}"

# Delete D9 chart
curl -X DELETE "http://localhost:8000/api/v1/charts/${PROFILE_ID}/D9" \
  -H "Authorization: Bearer ${TOKEN}"
```

## After Clearing

1. Pull the latest code changes:
   ```bash
   cd /Users/arvind.tiwari/Desktop/jioastro
   git pull origin claude/vedic-astrology-mvp-011CUW2MK4vfrjHsuSGNoNen
   ```

2. Restart your frontend (if running):
   ```bash
   # Stop with Ctrl+C, then restart
   cd frontend
   npm run dev
   ```

3. Restart your backend (if running):
   ```bash
   # Stop with Ctrl+C, then restart
   cd backend
   source venv/bin/activate
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Visit your profile page - charts will be automatically recalculated with the correct structure

## Verification

After clearing and restarting:
1. Go to any profile view
2. Open browser console (F12)
3. Look for `BirthChart received data:` logs
4. Verify the data includes:
   - `houses` array with 12 entries
   - `planets` object
   - `ascendant` object
   - `yogas` array
   - `dasha` object

The charts should now display properly without errors!
