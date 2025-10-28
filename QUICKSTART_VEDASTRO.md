# 🚀 Quick Start - See VedAstro Features

## You need to RUN the application to see the features!

The code is ready on your current branch. Follow these steps to see it in action:

---

## Option 1: Automatic Start (Recommended)

```bash
# Run the start script
./start.sh
```

Then open your browser to: **http://localhost:3000**

---

## Option 2: Manual Start

### Terminal 1 - Backend

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install VedAstro (if not already installed)
pip install vedastro

# Start server
uvicorn main:app --reload
```

Backend will run at: http://localhost:8000

### Terminal 2 - Frontend

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

Frontend will run at: http://localhost:3000

---

## 🎯 How to See the VedAstro Features

### Step 1: Open Application
Visit: **http://localhost:3000**

### Step 2: Login/Signup
- Click "Sign Up" if you don't have an account
- Or "Login" if you do

### Step 3: Create a Birth Profile
1. Click "My Profiles" in the navigation
2. Click "New Profile" button
3. Fill in:
   - Name: (e.g., "John Doe")
   - Birth Date: (e.g., "1990-08-15")
   - Birth Time: (e.g., "14:30")
   - Birth City: (e.g., "Mumbai")
   - Latitude: 19.0760
   - Longitude: 72.8777
   - Timezone: Asia/Kolkata
4. Click "Create Profile"

### Step 4: View Enhanced Chart ⭐
On the profile card, click the **"View Enhanced Chart"** button (purple/primary button)

### Step 5: Explore Features

You should now see:

#### **Overview Tab** (Default)
- ✅ Chart Selector buttons at top (North Indian / South Indian / Western Style)
- ✅ Yogas section with color-coded strengths
- ✅ Dasha Timeline with current period highlighted
- ✅ Quick Info Cards (Ascendant, Moon, Sun)

#### **D1 Chart Tab**
- ✅ Birth chart with chart selector
- ✅ Planetary positions table

#### **D9 Chart Tab**
- ✅ Navamsa chart
- ✅ Educational information

#### **Dasha Tab**
- ✅ Complete Mahadasha timeline
- ✅ Current period highlighted
- ✅ Antardasha sub-periods

### Step 6: View Knowledge Base
1. Click **"Knowledge"** in the navigation menu
2. Explore topics:
   - 🪐 Planets
   - 🏠 Houses
   - ✨ Yogas
   - ⭐ Nakshatras
   - ⏰ Dashas

---

## 🔍 What You Should See

### Enhanced Chart Page
```
┌─────────────────────────────────────────────────┐
│ ← [Back]     John Doe         [Ask Question]   │
│   📅 Aug 15, 1990 at 2:30 PM                    │
│   📍 Mumbai                                      │
├─────────────────────────────────────────────────┤
│ [Overview] [D1 Chart] [D9 Chart] [Dasha]       │
├─────────────────────────────────────────────────┤
│                                                  │
│ Birth Chart (Multiple Styles)                   │
│ [North Indian] [South Indian] [Western Style]   │
│ ┌───────────────────────────────────────┐      │
│ │    ⬥ Chart appears here ⬥             │      │
│ │  (Diamond, Square, or Circle shape)   │      │
│ └───────────────────────────────────────┘      │
│                                                  │
│ Planetary Yogas                                  │
│ 👑 Raj Yoga - [Strong]                          │
│    Combination indicating power and success     │
│                                                  │
│ Dasha Timeline                                   │
│ Current: ☿ Mercury [CURRENT]                    │
│ ┌─────┬─────┬─────┬─────┬─────┐                │
│ │ ☿   │ ♃   │ ♄   │ ☊   │ ♀   │                │
│ └─────┴─────┴─────┴─────┴─────┘                │
│                                                  │
│ [Ascendant]  [Moon Sign]  [Sun Sign]           │
│   Aries        Cancer        Leo                │
└─────────────────────────────────────────────────┘
```

### Knowledge Base Page
```
┌─────────────────────────────────────────────────┐
│ 📖 Vedic Astrology Knowledge Base               │
│                                                  │
│ [🪐 Planets] [🏠 Houses] [✨ Yogas]             │
│ [⭐ Nakshatras] [⏰ Dashas]                      │
├─────────────────────────────────────────────────┤
│                                                  │
│ Vedic Planets (Grahas)                          │
│                                                  │
│ ┌───────────────────────────────────────┐      │
│ │ Sun (Surya)                            │      │
│ │ Nature: Soul, authority, father...     │      │
│ │ Strength: Exalted in Aries...          │      │
│ └───────────────────────────────────────┘      │
│                                                  │
│ ┌───────────────────────────────────────┐      │
│ │ Moon (Chandra)                         │      │
│ │ Nature: Mind, mother, emotions...      │      │
│ └───────────────────────────────────────┘      │
│ ...                                              │
└─────────────────────────────────────────────────┘
```

---

## ❌ Troubleshooting

### "Can't connect to backend"
**Solution:** Make sure backend is running on port 8000
```bash
curl http://localhost:8000/api/v1/vedastro/status
```
Should return: `{"available":true,...}`

### "VedAstro library not available"
**Solution:** Install VedAstro
```bash
cd backend
source venv/bin/activate
pip install vedastro
```

### "Page not found" for /dashboard/chart/[id]
**Solution:** Make sure you're on the correct branch
```bash
git branch
# Should show: * claude/vedic-astrology-mvp-011CUW2MK4vfrjHsuSGNoNen
```

### Charts not rendering
**Solution:** Check browser console for errors (F12), ensure profile has valid birth data

### Frontend won't start
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 📸 Expected Screenshots

### Dashboard Navigation
You should see these menu items:
- ✅ Dashboard
- ✅ My Profiles
- ✅ Ask Question
- ✅ **Knowledge** ← NEW!
- ✅ History

### Profile Card
Each profile card should have TWO buttons:
- ✅ **"View Enhanced Chart"** (Primary purple button) ← Click this!
- ✅ "View Standard Chart" (Outline button)

### Enhanced Chart Tabs
Four tabs at the top:
- ✅ Overview
- ✅ D1 Chart
- ✅ D9 Chart
- ✅ Dasha

---

## ✅ Success Checklist

Once running, verify you can:

- [ ] See "Knowledge" in the navigation menu
- [ ] Create a new birth profile
- [ ] See "View Enhanced Chart" button on profile cards
- [ ] Click it and land on `/dashboard/chart/[id]` page
- [ ] See 4 tabs: Overview, D1, D9, Dasha
- [ ] Click chart selector buttons to switch styles
- [ ] See yogas with color-coded strengths
- [ ] See dasha timeline with current period
- [ ] Click Knowledge menu item
- [ ] See 5 topic buttons: Planets, Houses, Yogas, Nakshatras, Dashas
- [ ] Click each topic and see information

---

## 🎯 Quick Test (2 minutes)

```bash
# 1. Start application
./start.sh

# 2. Open browser
# http://localhost:3000

# 3. Sign up / Login

# 4. Create profile:
#    Name: Test User
#    Date: 1990-08-15
#    Time: 14:30
#    City: Mumbai
#    Lat: 19.0760, Lon: 72.8777
#    Timezone: Asia/Kolkata

# 5. Click "View Enhanced Chart"

# 6. You should see:
#    ✓ Chart selector buttons
#    ✓ Birth chart rendering
#    ✓ Yogas section
#    ✓ Dasha timeline
#    ✓ Tabs working

# 7. Click "Knowledge" in menu

# 8. You should see:
#    ✓ 5 topic buttons
#    ✓ Educational content
```

---

## 💡 Tips

1. **Use Chrome/Firefox** - Best compatibility
2. **Open DevTools** (F12) - See console logs
3. **Check Network tab** - See API calls
4. **Refresh page** (Ctrl+R) - If something doesn't load
5. **Clear cache** (Ctrl+Shift+R) - If styles look wrong

---

## 📞 Still Can't See It?

If you still can't see the features after following these steps:

1. **Check current branch:**
   ```bash
   git status
   # Should show: claude/vedic-astrology-mvp-011CUW2MK4vfrjHsuSGNoNen
   ```

2. **Verify files exist:**
   ```bash
   ls -la frontend/app/dashboard/chart/
   ls -la frontend/app/dashboard/knowledge/
   ls -la frontend/components/chart/ChartSelector.tsx
   ls -la frontend/components/vedic/KnowledgeBase.tsx
   ```

3. **Check backend logs:**
   - Look for "VedAstro library is available" message
   - Check for any errors

4. **Check frontend logs:**
   - Open browser console (F12)
   - Look for any red errors
   - Check Network tab for failed requests

---

## 🎉 That's It!

Once the servers are running and you've created a profile, you'll be able to see all the VedAstro features integrated into the application!

**Remember:** The features exist in the CODE but you need to RUN the application to SEE them in the browser.
