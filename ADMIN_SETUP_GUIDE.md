# Admin Portal Setup Guide

## Database Connection Issue

If you're experiencing database connection timeouts, you have **three alternative methods** to initialize the admin system:

---

## Method 1: Direct SQL Execution (RECOMMENDED)

This is the **easiest and most reliable method** if you have access to your Supabase dashboard.

### Steps:

1. **Login to Supabase Dashboard**
   - Go to https://supabase.com
   - Navigate to your JioAstro project
   - Click on "SQL Editor" in the left sidebar

2. **Run the Initialization Script**
   - Open the file: `backend/scripts/init_admin_tables.sql`
   - Copy the entire SQL script
   - Paste it into the Supabase SQL Editor
   - Click "Run" or press Cmd/Ctrl + Enter

3. **Verify Success**
   - You should see confirmation messages in the results
   - Check the `admin_users` table - it should contain one row with username "admin"

### Default Admin Credentials:
- **Username**: `admin`
- **Email**: `admin@jioastro.com`
- **Password**: `admin@123`

You can log in with either username or email.

⚠️ **IMPORTANT**: The SQL script includes a bcrypt hash of the password "admin@123". If you want a different password, you'll need to generate a new bcrypt hash.

---

## Method 2: Generate Custom Password Hash

If you want to use a different password than "admin@123", generate a bcrypt hash:

### Using Python:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -c "from app.core.admin_security import hash_password; print(hash_password('YOUR_PASSWORD_HERE'))"
```

Then update the SQL script with your hash before running it in Supabase.

---

## Method 3: API Endpoint Initialization (When Database is Accessible)

If your backend can connect to the database successfully:

```bash
curl -X POST http://localhost:8000/api/v1/setup/initialize-admin
```

Response should be:
```json
{
  "message": "Admin system initialized successfully",
  "admin_created": true,
  "username": "admin",
  "default_password": "admin@123",
  "warning": "Please change the default password immediately!"
}
```

### Check If Admin Exists:

```bash
curl http://localhost:8000/api/v1/setup/check-admin
```

---

## Method 4: Python Script (When Database Connection Works)

If you can resolve the database connection timeout issue:

```bash
cd backend
source venv/bin/activate
python scripts/create_admin_user.py
```

### Fixing Database Connection Timeout:

If you're getting timeout errors, try these fixes:

1. **Check DATABASE_URL in .env file**
   ```bash
   # Make sure it's using asyncpg driver
   DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
   ```

2. **Increase Connection Timeout**

   Edit `backend/app/db/database.py` line 20-23:
   ```python
   connect_args={
       "timeout": 30,  # Increase from 5 to 30 seconds
       "command_timeout": 30
   }
   ```

3. **Check if PostgreSQL port is accessible**
   ```bash
   # Test connection
   telnet your-supabase-host.supabase.co 5432
   ```

4. **Check firewall/network settings**
   - Ensure port 5432 is not blocked
   - Check if you're behind a corporate firewall
   - Try using a different network

---

## Verification Steps

After initialization, verify the admin system is working:

### 1. Check Tables Exist (in Supabase Dashboard):

Navigate to "Table Editor" and confirm these tables exist:
- `admin_users` - Should have 1 row (username: admin)
- `knowledge_documents` - Should be empty initially

### 2. Test Admin Login:

```bash
# Test login via API
curl -X POST http://localhost:8000/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin@123"}'
```

Expected response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "admin_id": "...",
  "username": "admin"
}
```

### 3. Test Frontend Login:

1. Start frontend: `cd frontend && npm run dev`
2. Navigate to: `http://localhost:3000/admin/login`
3. Login with credentials: `admin` / `admin@123`
4. You should be redirected to the admin dashboard

---

## Troubleshooting

### "Incorrect username or password"

- Double-check you're using exact credentials: `admin` / `admin@123`
- Verify the admin_users table has the record
- Check if password_hash was inserted correctly

### "Failed to initialize admin system"

- Database connection issue - see Method 1 (SQL script)
- Check backend logs for specific error
- Verify DATABASE_URL is correct in .env

### "Admin tables already exist"

- If you get this message, tables are already created
- Just verify the admin user exists in the admin_users table
- If admin user is missing, manually insert using SQL

### Frontend - "Could not validate admin credentials"

- Backend might not be running - check `http://localhost:8000/health`
- Token might have expired - try logging in again
- Check browser console for detailed error messages

---

## Security Best Practices

### 1. Change Default Password Immediately

After first login, create a new admin user with a strong password:

```bash
curl -X POST http://localhost:8000/api/v1/admin/create \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "yourusername",
    "password": "your_strong_password",
    "email": "your@email.com"
  }'
```

### 2. Disable Setup Endpoint in Production

After initialization, comment out or remove the setup router in `backend/app/api/v1/router.py`:

```python
# api_router.include_router(setup.router, prefix="/setup", tags=["setup"])
```

### 3. Use Environment Variables for Admin Credentials

Never commit credentials to version control. Consider using environment variables:

```bash
# .env
ADMIN_DEFAULT_USERNAME=admin
ADMIN_DEFAULT_PASSWORD=your_secure_password_here
```

### 4. Implement Rate Limiting

Add rate limiting to admin endpoints to prevent brute force attacks:

```python
# Install slowapi
pip install slowapi

# Add to admin endpoints
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login", response_model=AdminLoginResponse)
@limiter.limit("5/minute")  # 5 attempts per minute
async def admin_login(...):
    ...
```

### 5. Use HTTPS in Production

Always use HTTPS in production to encrypt:
- Login credentials
- Admin tokens
- Uploaded documents

---

## Next Steps

Once admin system is initialized:

1. **Access Admin Portal**: `http://localhost:3000/admin/login`
2. **Change Default Password**: Create a new admin user with strong credentials
3. **Upload Knowledge Documents**: Start enriching the knowledge base
4. **Manage Users**: View and manage user profiles
5. **Integrate Ingestion Pipeline**: Connect uploaded documents to training pipeline

Refer to `ADMIN_PORTAL_README.md` for detailed usage instructions.

---

## Support

If you continue to have issues:

1. **Check Backend Logs**: Look for specific error messages
2. **Verify Database Connection**: Test Supabase connectivity
3. **Review Environment Variables**: Ensure all required vars are set
4. **Check Network/Firewall**: Ensure database ports are accessible

For persistent issues, consider:
- Using Supabase SQL Editor (Method 1) - most reliable
- Checking Supabase dashboard for connection status
- Reviewing Supabase project logs
