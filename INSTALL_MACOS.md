# 🚀 MacBook Installation Guide - Vedic AI Astrology MVP

**For: MacBook M2 Pro 16GB**
**Time Required: 30-45 minutes**

---

## ✅ Step 1: Check Prerequisites (5 minutes)

### 1.1 Check if Homebrew is installed

Open **Terminal** and run:

```bash
brew --version
```

**If you see a version number** → Skip to 1.2
**If you see "command not found"** → Install Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, run these commands (the installer will tell you to):
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 1.2 Check Python version

```bash
python3 --version
```

**Expected**: Python 3.11 or higher
**If lower than 3.11**, install Python 3.11:

```bash
brew install python@3.11
echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
python3 --version
```

### 1.3 Check Node.js version

```bash
node --version
```

**Expected**: v18.0.0 or higher
**If not installed or version too low**:

```bash
brew install node@18
echo 'export PATH="/opt/homebrew/opt/node@18/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
node --version
npm --version
```

### 1.4 Verify Git

```bash
git --version
```

**Expected**: Any version (should be pre-installed on Mac)
**If not**: `brew install git`

---

## ✅ Step 2: Set Up Supabase (10 minutes)

### 2.1 Create Supabase Account

1. Go to: https://supabase.com
2. Click **"Start your project"**
3. Sign in with GitHub (recommended) or email
4. Click **"New Project"**

### 2.2 Create Project

Fill in these details:
- **Name**: `vedic-astrology` (or any name you like)
- **Database Password**: Create a strong password (save it somewhere safe!)
- **Region**: Choose closest to you (e.g., `US West`)
- **Pricing Plan**: Free tier is perfect for now

Click **"Create new project"**

⏳ **Wait 2-3 minutes** for project to be created (you'll see a progress indicator)

### 2.3 Set Up Database Schema

Once your project is ready:

1. In Supabase dashboard, go to **SQL Editor** (left sidebar)
2. Click **"New query"**
3. Open this file on your Mac:
   ```bash
   # In Terminal, navigate to the project
   cd ~/Desktop  # or wherever you want to clone the project

   # Clone the repository (if not already done)
   git clone <repository-url> jioastro
   cd jioastro

   # Open the SQL file
   cat docs/database-schema.sql
   ```

4. **Copy the entire SQL output** from Terminal
5. **Paste it** into the Supabase SQL Editor
6. Click **"Run"** (bottom right)
7. You should see: ✅ **Success. No rows returned**

### 2.4 Enable Email Authentication

1. In Supabase, go to **Authentication** → **Providers** (left sidebar)
2. Make sure **Email** is enabled (it should be by default)
3. Scroll down and **disable** "Confirm email" for testing:
   - Go to **Authentication** → **Settings**
   - Find "Enable email confirmations"
   - **Toggle it OFF** (for easier testing)

### 2.5 Get Your Credentials

1. Go to **Settings** → **API** (left sidebar)
2. Copy these three values (keep this window open, you'll need them):

   - **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
   - **anon public key**: `eyJhbGc...` (long string)
   - **service_role key**: `eyJhbGc...` (different long string)

3. Go to **Settings** → **Database**
4. Scroll to **Connection string** → **URI**
5. Copy the connection string (should look like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```

---

## ✅ Step 3: Set Up Backend (5 minutes)

### 3.1 Navigate to project

```bash
cd ~/Desktop/jioastro  # or wherever you cloned it
cd backend
```

### 3.2 Create Python virtual environment

```bash
python3 -m venv venv
```

### 3.3 Activate virtual environment

```bash
source venv/bin/activate
```

**You should see** `(venv)` at the start of your Terminal prompt

### 3.4 Install Python dependencies

```bash
pip install -r requirements.txt
```

⏳ **This will take 2-3 minutes**. You'll see many packages being installed.

**If you see any errors about missing tools**, run:
```bash
brew install gcc
```

### 3.5 Create environment file

```bash
cp .env.example .env
```

### 3.6 Edit environment file

```bash
nano .env
```

**Replace** the placeholder values with your Supabase credentials:

```bash
# Database - Use the connection string from Supabase
# IMPORTANT: Change postgresql:// to postgresql+asyncpg://
DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres

# Supabase
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=your-anon-public-key-here
SUPABASE_JWT_SECRET=your-service-role-key-here

# OpenAI - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-key-here

# Redis (optional for now, will work without it)
REDIS_URL=redis://localhost:6379

# Configuration
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
RATE_LIMIT_QUERIES_PER_DAY=10
```

**Save and exit**: Press `Control + X`, then `Y`, then `Enter`

### 3.7 Get OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign in or create account
3. Click **"Create new secret key"**
4. Copy the key (starts with `sk-`)
5. Add it to your `.env` file:
   ```bash
   nano .env
   # Find OPENAI_API_KEY line and paste your key
   # Save: Control + X, Y, Enter
   ```

---

## ✅ Step 4: Set Up Frontend (5 minutes)

### 4.1 Open a NEW Terminal window

**Important**: Keep the first Terminal open for backend. Open a new one:
- Press `Command + N` in Terminal
- Or right-click Terminal icon → New Window

### 4.2 Navigate to frontend

```bash
cd ~/Desktop/jioastro/frontend  # adjust path if needed
```

### 4.3 Install Node.js dependencies

```bash
npm install
```

⏳ **This will take 2-3 minutes**

### 4.4 Create environment file

```bash
cp .env.example .env.local
```

### 4.5 Edit environment file

```bash
nano .env.local
```

**Replace** with your Supabase credentials:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-public-key-here
```

**Save and exit**: `Control + X`, `Y`, `Enter`

---

## ✅ Step 5: Start the Application (2 minutes)

### 5.1 Start Backend (Terminal 1)

In your **first Terminal window** (where you set up backend):

```bash
# Make sure you're in backend directory
cd ~/Desktop/jioastro/backend

# Activate virtual environment if not already active
source venv/bin/activate

# Start the server
uvicorn main:app --reload
```

**You should see**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🚀 Starting Vedic AI Astrology API...
✅ Database initialized
INFO:     Application startup complete.
```

✅ **Backend is running!**

### 5.2 Start Frontend (Terminal 2)

In your **second Terminal window**:

```bash
# Make sure you're in frontend directory
cd ~/Desktop/jioastro/frontend

# Start the development server
npm run dev
```

**You should see**:
```
▲ Next.js 14.0.3
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000

✓ Ready in 2.1s
```

✅ **Frontend is running!**

---

## ✅ Step 6: Verify Everything Works (5 minutes)

### 6.1 Open the Application

1. Open **Safari** or **Chrome**
2. Go to: **http://localhost:3000**
3. You should see the **Vedic AI Astrology** landing page

### 6.2 Test Backend API

Open a **third Terminal window** and run:

```bash
curl http://localhost:8000/health
```

**Expected output**:
```json
{"status":"healthy","database":"connected","api":"operational"}
```

### 6.3 Test API Documentation

In your browser, go to: **http://localhost:8000/docs**

You should see the **Swagger UI** with all API endpoints listed.

---

## ✅ Step 7: Test the Application (10 minutes)

### 7.1 Create an Account

1. On the homepage (http://localhost:3000), click **"Get Started Free"**
2. Click **"Sign up"** link
3. Enter:
   - Email: `test@example.com` (or your real email)
   - Password: `password123` (min 6 characters)
   - Confirm password: `password123`
4. Click **"Create Account"**
5. You should see "Success!" message

### 7.2 Log In

1. You'll be redirected to login page
2. Enter the same credentials
3. Click **"Sign In"**
4. You should see the **Dashboard**

### 7.3 Create a Birth Profile

1. Click **"Create Your First Profile"** button
2. Fill in the form:
   - **Name**: `John Doe` (or your name)
   - **Birth Date**: Pick any date (e.g., `1990-01-01`)
   - **Birth Time**: Enter time (e.g., `14:30`)
   - **City**: Select `Mumbai` from dropdown
   - (Lat/Lon will auto-fill)
   - **Timezone**: Keep `Asia/Kolkata`
3. Check **"Set as primary profile"**
4. Click **"Create Profile & Generate Chart"**

⏳ **Wait 2-3 seconds** for chart calculation...

### 7.4 View Birth Chart

You should see:
- ✅ **North Indian style chart** (diamond shape) with planets
- ✅ **Planetary Positions** table
- ✅ **Yogas** detected (if any)
- ✅ **Current Dasha** information

### 7.5 Test AI Query

1. Click **"Ask Question"** button (top right)
2. Select a category: **"Career & Work"**
3. Select your profile from dropdown
4. Enter question: `What career path is best for me?`
5. Click **"Get AI Insights"**

⏳ **Wait 5-10 seconds** for AI response...

You should see a detailed interpretation based on your chart!

### 7.6 Submit Feedback

1. Go to **"History"** in navigation
2. You should see your question
3. Click to expand it
4. Click **"Rate this interpretation"**
5. Select 5 stars
6. Add comment: `Great insights!`
7. Click **"Submit Feedback"**

✅ **Success!**

---

## ✅ Troubleshooting

### Issue: Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Fix**:
```bash
cd ~/Desktop/jioastro/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Frontend won't start

**Error**: `Cannot find module 'next'`

**Fix**:
```bash
cd ~/Desktop/jioastro/frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Database connection error

**Error**: `could not connect to server`

**Fix**:
1. Check your `backend/.env` file
2. Make sure `DATABASE_URL` starts with `postgresql+asyncpg://`
3. Make sure password is correct (no special characters need escaping in connection string)
4. Test connection:
   ```bash
   cd ~/Desktop/jioastro/backend
   source venv/bin/activate
   python3 -c "from app.db.database import engine; import asyncio; asyncio.run(engine.connect())"
   ```

### Issue: OpenAI API error

**Error**: `Invalid API key`

**Fix**:
1. Go to https://platform.openai.com/api-keys
2. Create a new key
3. Update `backend/.env`:
   ```bash
   nano backend/.env
   # Update OPENAI_API_KEY
   ```
4. Restart backend server

### Issue: Port already in use

**Error**: `Address already in use`

**Fix**:
```bash
# Find process using port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or for port 3000
kill -9 $(lsof -ti:3000)
```

---

## 🎉 Success! You're Running Locally

**You now have**:
- ✅ Backend API running on http://localhost:8000
- ✅ Frontend app running on http://localhost:3000
- ✅ Database connected to Supabase
- ✅ AI integration with OpenAI working
- ✅ Full birth chart generation
- ✅ Complete user authentication

**URLs to bookmark**:
- **App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📝 Daily Development Workflow

### Starting the app each day:

**Terminal 1 (Backend)**:
```bash
cd ~/Desktop/jioastro/backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 (Frontend)**:
```bash
cd ~/Desktop/jioastro/frontend
npm run dev
```

### Stopping the app:

- In each Terminal window: Press `Control + C`

---

## 🚀 Next Steps

1. **Test all features** thoroughly
2. **Customize** the app (add more cities, modify prompts, etc.)
3. **Deploy** to production when ready (see DEPLOYMENT.md)
4. **Share** with beta testers

---

## 💡 Useful Commands

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check if frontend is building correctly
cd frontend && npm run build

# View backend logs (while it's running)
# Just look at Terminal 1

# Update dependencies
cd backend && pip install -r requirements.txt --upgrade
cd frontend && npm update

# Clear cache and restart
cd frontend && rm -rf .next && npm run dev
```

---

## 📞 Need Help?

If you encounter any issues:
1. Check the Troubleshooting section above
2. Review the error messages in Terminal
3. Check backend/.env and frontend/.env.local are configured correctly
4. Make sure all prerequisites are installed

---

**Installation complete! Enjoy building with Vedic AI Astrology! 🌟**
