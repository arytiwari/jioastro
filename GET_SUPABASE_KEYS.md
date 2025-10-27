# How to Get Your Supabase Keys

## Required Keys for Backend

The backend needs the **Service Role Key** to bypass Row Level Security (RLS) when making database operations on behalf of authenticated users.

## Step-by-Step Instructions

### 1. Go to Supabase Dashboard
- Open your browser and go to: https://supabase.com/dashboard
- Log in to your account
- Select your project: **jyawjajnxzuhzisjcnpn**

### 2. Navigate to API Settings
- Click on **Settings** (gear icon) in the left sidebar
- Click on **API** under Project Settings

### 3. Find Your Keys

You'll see several keys on this page:

#### Project URL
```
https://jyawjajnxzuhzisjcnpn.supabase.co
```
This is your `SUPABASE_URL` (already configured)

#### anon public key
- This is a long string starting with `eyJhbGci...`
- Used for client-side (frontend) operations
- This is your `SUPABASE_ANON_KEY`

#### service_role key (⚠️ SECRET - NEVER EXPOSE TO CLIENT)
- This is also a long JWT string starting with `eyJhbGci...`
- Click the eye icon to reveal it
- **Keep this secret!** Only use in backend/server code
- This is your `SUPABASE_SERVICE_ROLE_KEY`

#### JWT Secret
- A random string of characters
- Used for verifying JWT tokens
- This is your `SUPABASE_JWT_SECRET` (already configured)

## 4. Update Your Backend .env File

Edit `/home/user/jioastro/backend/.env` and update:

```bash
# Supabase Configuration
SUPABASE_URL=https://jyawjajnxzuhzisjcnpn.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci... (paste your service_role key here)
SUPABASE_JWT_SECRET=(your JWT secret - already configured)
```

**Important Notes:**
- The service_role key is a long JWT token (500+ characters)
- It starts with `eyJhbGci`
- Never commit this key to git or expose it publicly
- The backend .env file is already in .gitignore

## 5. Restart Your Backend Server

After updating the .env file:
```bash
# Stop the server: Ctrl+C

# Start again:
cd /home/user/jioastro/backend
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
✅ Supabase REST API client initialized (using service_role key)
```

## Why Do We Need the Service Role Key?

- **Anon Key**: Used by frontend, subject to Row Level Security (RLS) policies
- **Service Role Key**: Used by backend, bypasses RLS to perform operations on behalf of authenticated users
- Your backend authenticates users with JWT tokens, then uses the service role key to perform database operations

This is the standard pattern for Supabase backend services.
