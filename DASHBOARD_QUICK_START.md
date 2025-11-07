# JioAstro Dashboard - Quick Start Guide

**Problem:** Empty dashboard showing "0 Active profiles"
**Solution:** Create your first birth profile!

---

## 🎯 3 Ways to Populate Your Dashboard

### Method 1: Frontend UI (Easiest - Recommended)

#### Step-by-Step:

1. **Navigate to Profiles**
   - URL: http://localhost:3000/dashboard/profiles
   - Or click "Birth Profiles" in sidebar

2. **Click "Create New Profile" button**

3. **Fill in Your Birth Details:**
   ```
   Name:           Your Name
   Date of Birth:  15/01/1990 (DD/MM/YYYY)
   Time of Birth:  14:30 (24-hour format) or 2:30 PM
   Place of Birth: New Delhi, India
   ```

4. **Submit Form**
   - Backend will geocode your location
   - Chart will be calculated
   - You'll be redirected to view your chart

5. **Return to Dashboard**
   - Now you'll see:
     - ✅ Birth Profiles: 1
     - ✅ Your recent profile card
     - ✅ Ability to ask questions about your chart

---

### Method 2: Use Swagger API UI

#### Navigate to API Documentation:
```
http://localhost:8000/docs
```

#### Create Profile via API:

1. **Authenticate First** (if required):
   - Expand `/api/v1/auth/login` endpoint
   - Click "Try it out"
   - Enter credentials
   - Copy the `access_token` from response

2. **Create Profile**:
   - Expand `/api/v1/profiles` POST endpoint
   - Click "Try it out"
   - Click "Authorize" button (paste token)
   - Fill in JSON:
     ```json
     {
       "name": "Test User",
       "birth_date": "1990-01-15",
       "birth_time": "14:30:00",
       "birth_place": "New Delhi, India",
       "latitude": 28.6139,
       "longitude": 77.2090,
       "timezone": "Asia/Kolkata"
     }
     ```
   - Click "Execute"

3. **Refresh Dashboard**
   - Go back to http://localhost:3000/dashboard
   - You should see your profile!

---

### Method 3: Instant Onboarding (Feature #13 - If Enabled)

**Note:** This requires the Instant Onboarding feature to be enabled and migrated.

#### Quick Test Script:

```bash
# Navigate to project root
cd /Users/arvind.tiwari/Desktop/jioastro

# Run test script
./test_instant_onboarding.sh
```

#### Or Test Manually via API:

```bash
# Generate chart directly (no auth required!)
curl -X POST "http://localhost:8000/api/v2/instant-onboarding/quick-chart" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "birth_date": "1990-01-15",
    "birth_time": "14:30:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": "Asia/Kolkata",
    "language": "en"
  }'
```

**Expected Response:**
```json
{
  "session_id": "uuid",
  "profile_id": "uuid",
  "sun_sign": "Capricorn",
  "moon_sign": "Taurus",
  "ascendant": "Leo",
  "top_insights": [
    "Your Sun sign is Capricorn",
    "Your Moon sign is Taurus",
    "Your Ascendant is Leo"
  ],
  "shareable_link": "http://localhost:3000/chart/uuid?ref=instant"
}
```

---

## 🔍 Verify Backend Connection

Before creating profiles, ensure backend is responding:

### Quick Health Check:
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "supabase_rest_api",
  "api": "operational"
}
```

### Check Available Endpoints:
```bash
# Visit API docs
open http://localhost:8000/docs
```

---

## 📊 What You'll See After Creating Profiles

### Dashboard Will Show:

1. **Birth Profiles Card**
   ```
   Birth Profiles
   1 Active profiles

   [Your Profile Card]
   Name: Test User
   Born: Jan 15, 1990
   Location: New Delhi
   ```

2. **Questions Asked Card**
   ```
   Questions Asked
   0 AI-powered insights
   ```
   - You can now ask questions!
   - Click "Ask a Question" button

3. **Average Rating Card**
   ```
   Average Rating
   N/A Your feedback
   ```
   - Will show ratings after you rate responses

### Navigation Options:

- **View Chart**: See full birth chart visualization
- **Numerology**: Calculate numerology profile
- **Ask Questions**: Get AI-powered insights
- **History**: View all past queries

---

## 🎨 Sample Birth Data for Testing

Use these for quick testing:

### Profile 1: New Delhi
```json
{
  "name": "Raj Kumar",
  "birth_date": "1990-01-15",
  "birth_time": "14:30:00",
  "birth_place": "New Delhi, India",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timezone": "Asia/Kolkata"
}
```

### Profile 2: Mumbai
```json
{
  "name": "Priya Sharma",
  "birth_date": "1985-06-20",
  "birth_time": "09:15:00",
  "birth_place": "Mumbai, India",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "timezone": "Asia/Kolkata"
}
```

### Profile 3: New York
```json
{
  "name": "John Doe",
  "birth_date": "1992-12-05",
  "birth_time": "18:45:00",
  "birth_place": "New York, USA",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "timezone": "America/New_York"
}
```

---

## 🐛 Troubleshooting

### Issue 1: "401 Unauthorized" Error

**Cause:** Not logged in or token expired

**Solution:**
1. Check if you're logged in: http://localhost:3000/auth/login
2. If logged in, try logging out and back in
3. Clear browser cache/cookies
4. Check browser console for errors (F12)

### Issue 2: "Network Error" or "Cannot connect"

**Cause:** Backend not running or wrong URL

**Solution:**
```bash
# Check if backend is running
ps aux | grep uvicorn

# If not running, start it
cd /Users/arvind.tiwari/Desktop/jioastro/backend
source venv/bin/activate
uvicorn main:app --reload

# Verify it's accessible
curl http://localhost:8000/health
```

### Issue 3: Profile Created but Not Showing on Dashboard

**Cause:** Frontend not refreshing or cache issue

**Solution:**
1. Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
2. Clear browser cache
3. Check Network tab (F12) for API calls
4. Verify profile exists via API:
   ```bash
   curl http://localhost:8000/api/v1/profiles \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

### Issue 4: "Invalid coordinates" or "Location not found"

**Cause:** Geocoding failed or coordinates incorrect

**Solution:**
1. Use coordinates directly (latitude/longitude)
2. Get coordinates from: https://www.latlong.net/
3. Or use one of the sample profiles above

### Issue 5: Chart Generation Fails

**Cause:** Missing dependencies or calculation error

**Solution:**
1. Check backend logs:
   ```bash
   tail -f /Users/arvind.tiwari/Desktop/jioastro/backend/backend.log
   ```
2. Verify all required packages installed:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Check for errors in Supabase dashboard

---

## 📱 Next Steps After Creating Profiles

### 1. View Your Chart
- Click on profile card
- See detailed birth chart
- Explore D1 (Rashi) and D9 (Navamsa) charts
- View planetary positions and houses

### 2. Calculate Numerology
- Navigate to: http://localhost:3000/dashboard/numerology
- Enter name and birth date
- Get Western and Vedic numerology analysis
- View life path, expression, soul urge numbers

### 3. Ask AI Questions
- Click "Ask a Question"
- Select your profile
- Enter question like:
  - "What does my chart say about my career?"
  - "When is a good time for marriage?"
  - "What are my strengths and weaknesses?"
- Get AI-powered interpretation using GPT-4

### 4. Compare Profiles (if you created multiple)
- Go to Compatibility (if available)
- Compare two birth charts
- See relationship insights

### 5. Explore Knowledge Base
- Navigate to: http://localhost:3000/dashboard/knowledge
- Learn about Vedic astrology concepts
- Understand your chart better

---

## 🎯 Quick Commands Cheatsheet

```bash
# Check backend status
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Check if backend is running
ps aux | grep uvicorn

# Start backend (if not running)
cd backend && source venv/bin/activate && uvicorn main:app --reload

# Start frontend (if not running)
cd frontend && npm run dev

# View backend logs
tail -f backend/backend.log

# Create test profile (Instant Onboarding)
./test_instant_onboarding.sh

# Check Supabase connection
cd backend && python test_db_connection.py
```

---

## 💡 Pro Tips

1. **Create Multiple Profiles**: Test with family/friends' birth data
2. **Try Different Locations**: See how location affects charts
3. **Ask Diverse Questions**: Test AI's knowledge range
4. **Rate Responses**: Help improve AI quality
5. **Export Charts**: Share with others (if feature available)
6. **Save Favorite Questions**: Create templates for common queries

---

## 📞 Need More Help?

**Frontend Issues:**
- Check: `frontend/` directory
- Logs: Browser console (F12 → Console tab)
- Network: F12 → Network tab

**Backend Issues:**
- Check: `backend/backend.log`
- API Docs: http://localhost:8000/docs
- Database: Supabase dashboard

**Feature Issues:**
- Instant Onboarding: See `backend/app/features/instant_onboarding/README.md`
- Numerology: See `backend/docs/numerology/`

---

## ✅ Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Logged in to dashboard
- [ ] Created at least 1 profile
- [ ] Dashboard shows profile count
- [ ] Can view chart
- [ ] Can ask questions
- [ ] AI responds to questions

Once all checked, you're all set! 🎉

---

**Last Updated:** 2025-11-07
**Version:** 1.0.0
