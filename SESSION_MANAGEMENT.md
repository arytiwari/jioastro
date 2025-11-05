# Long-Running Session Management with Idle Timeout

This document describes the implementation of a robust session management system that prevents users from being logged out unnecessarily while maintaining security through idle timeout.

## Features Implemented

### 1. **Automatic Token Refresh** ✅
- Tokens are automatically refreshed 5 minutes before expiration
- Background refresh process runs every 60 seconds
- Seamless user experience with no interruption

### 2. **Idle Timeout Detection** ✅
- User activity is tracked (mouse, keyboard, scroll, touch events)
- **30-minute idle timeout** - users are logged out after 30 minutes of inactivity
- Idle time can be checked and reset programmatically

### 3. **Smart Request Handling** ✅
- API client automatically refreshes tokens before making requests
- Failed requests due to expired tokens trigger automatic retry with fresh token
- Only redirects to login if refresh fails completely

### 4. **Session Persistence** ✅
- Sessions remain active as long as user is active
- Refresh tokens allow extending sessions beyond initial expiry
- Background process maintains valid tokens

## Files Created/Modified

### Created Files:

1. **`frontend/lib/sessionManager.ts`**
   - Core session management logic
   - Activity tracking
   - Idle timeout detection
   - Automatic refresh scheduling

2. **`frontend/components/SessionProvider.tsx`**
   - React component to initialize session manager
   - Handles session expiration callbacks
   - Integrated into app layout

### Modified Files:

1. **`frontend/lib/supabase.ts`**
   - Added `refreshSession()` function
   - Added `isSessionExpired()` function
   - Added `getValidSession()` function for automatic refresh

2. **`frontend/lib/api.ts`**
   - Updated request method to auto-refresh tokens
   - Added retry logic for 401 errors
   - Better error handling

3. **`frontend/app/providers.tsx`**
   - Added SessionProvider wrapper
   - Initialized at app root level

## Configuration

### Session Manager Settings

Located in `frontend/lib/sessionManager.ts`:

```typescript
const CONFIG = {
  // Refresh token 5 minutes before expiry
  REFRESH_BUFFER_SECONDS: 300,

  // Check session validity every 60 seconds
  CHECK_INTERVAL_MS: 60 * 1000,

  // Idle timeout: 30 minutes of inactivity
  IDLE_TIMEOUT_MS: 30 * 60 * 1000,

  // Activity events to track
  ACTIVITY_EVENTS: ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'],
}
```

### Customizing Idle Timeout

To change the idle timeout duration, modify the `IDLE_TIMEOUT_MS` value:

```typescript
// For 1 hour idle timeout:
IDLE_TIMEOUT_MS: 60 * 60 * 1000,

// For 15 minutes idle timeout:
IDLE_TIMEOUT_MS: 15 * 60 * 1000,
```

## Supabase JWT Configuration

### Recommended Settings

Configure longer JWT token expiration in Supabase dashboard:

1. Go to **Supabase Dashboard** → **Authentication** → **Settings**

2. **JWT Expiry**: Set to **8 hours** (28800 seconds)
   ```
   Access Token Lifetime: 28800
   ```

3. **Refresh Token Lifetime**: Set to **30 days** (2592000 seconds)
   ```
   Refresh Token Lifetime: 2592000
   ```

### Current Default Values:
- Access Token: 3600 seconds (1 hour)
- Refresh Token: 2592000 seconds (30 days)

### With Our Implementation:
- **Access tokens** are refreshed automatically 5 minutes before expiry
- **Refresh tokens** allow session extension for up to 30 days
- **Idle timeout** logs users out after 30 minutes of inactivity
- **Active users** can stay logged in indefinitely (as long as they're using the app)

## How It Works

### 1. Login Flow
```
User logs in
  ↓
Supabase returns access_token + refresh_token + expires_at
  ↓
Session stored in localStorage
  ↓
SessionManager initialized
  ↓
Background checking starts
```

### 2. Active Session Flow
```
Every 60 seconds:
  ↓
Check if user is idle (> 30 min inactivity)
  ├─ YES → Logout and redirect
  └─ NO → Continue
       ↓
   Check if token expires soon (< 5 min remaining)
     ├─ YES → Refresh token automatically
     └─ NO → Continue
```

### 3. API Request Flow
```
API request made
  ↓
Get valid session (auto-refresh if needed)
  ↓
Make request with fresh token
  ↓
If 401 error:
  ├─ Try refreshing token
  ├─ Retry request with new token
  └─ If refresh fails → Logout and redirect
```

### 4. User Activity Flow
```
User interacts with app (click, type, scroll, etc.)
  ↓
Activity timestamp updated
  ↓
Idle timeout reset
```

## API Reference

### SessionManager Methods

```typescript
import { sessionManager } from '@/lib/sessionManager'

// Initialize (done automatically by SessionProvider)
sessionManager.init(() => {
  // Optional: custom callback on session expired
  console.log('Session expired!')
})

// Manually refresh token
const success = await sessionManager.refreshNow()

// Check idle status
const isIdle = sessionManager.checkIsIdle()

// Get idle time remaining
const msRemaining = sessionManager.getIdleTimeRemaining()

// Reset idle timeout
sessionManager.resetIdleTimeout()

// Get full status
const status = sessionManager.getStatus()
console.log(status)
// {
//   initialized: true,
//   isIdle: false,
//   idleTimeMs: 120000,
//   idleTimeRemainingMs: 1680000,
//   sessionExpired: false
// }

// Cleanup (done automatically on unmount)
sessionManager.destroy()
```

### Supabase Auth Methods

```typescript
import { refreshSession, isSessionExpired, getValidSession } from '@/lib/supabase'

// Check if session is expired
const expired = isSessionExpired(300) // Buffer in seconds

// Get valid session (auto-refresh if needed)
const session = await getValidSession()

// Manually refresh session
const result = await refreshSession()
if (result.data.session) {
  console.log('Refreshed!')
}
```

## Testing

### Test Scenarios:

1. **Active User - No Logout**
   - Login to the app
   - Keep using the app (clicking, typing, navigating)
   - **Expected**: User stays logged in indefinitely

2. **Idle User - Automatic Logout**
   - Login to the app
   - Leave the app idle for 30+ minutes
   - **Expected**: User is logged out and redirected to login page

3. **Token Expiry - Auto Refresh**
   - Login to the app
   - Wait for token to near expiry (check console logs)
   - **Expected**: Token refreshes automatically in background

4. **Expired Token on Request**
   - Force token expiration (modify localStorage)
   - Make an API request
   - **Expected**: Token refreshes, request retries automatically

### Console Logs to Monitor:

```
🚀 Initializing SessionManager...
✅ SessionManager initialized
👂 Activity tracking enabled
⏰ Session checks started
🔄 Token expiring soon, refreshing...
✅ Token refreshed successfully
😴 User is idle, logging out...
🚪 Session expired: User inactivity timeout
```

## Security Considerations

### ✅ Implemented:
- **Idle timeout** prevents unauthorized access on abandoned devices
- **Automatic token refresh** maintains security without UX disruption
- **Activity tracking** ensures only active users stay logged in
- **Secure storage** in localStorage (HTTPS required in production)
- **Token expiration** enforced on both client and server

### ⚠️ Recommendations:
- Always use **HTTPS** in production
- Consider implementing **device fingerprinting** for added security
- Implement **concurrent session limits** if needed
- Add **suspicious activity detection** (e.g., IP address changes)

## Troubleshooting

### Issue: User still gets logged out while active

**Solution:**
- Check browser console for session manager logs
- Verify activity events are being tracked
- Ensure no browser extensions blocking localStorage
- Check if idle timeout is too short

### Issue: Token refresh fails

**Solution:**
- Verify Supabase credentials in `.env.local`
- Check refresh token is being stored
- Verify network connectivity to Supabase
- Check Supabase dashboard for auth errors

### Issue: Session manager not initialized

**Solution:**
- Verify `SessionProvider` is in app layout
- Check browser console for initialization logs
- Ensure component is client-side (`'use client'`)

## Migration from Old Auth

If updating from previous authentication:

1. **No breaking changes** - Old sessions will work
2. Session manager auto-initializes on app load
3. Existing localStorage sessions will be refreshed
4. Users may need to re-login once if refresh token expired

## Benefits Summary

### Before Implementation:
- ❌ Users logged out after 1 hour (fixed token expiry)
- ❌ No auto-refresh - manual re-login required
- ❌ Lost work if session expired during use
- ❌ Poor UX with frequent logouts

### After Implementation:
- ✅ Users can stay logged in for days if active
- ✅ Automatic token refresh (seamless)
- ✅ 30-minute idle timeout (security + UX balance)
- ✅ No interruption during active use
- ✅ Activity-based session management
- ✅ Background token maintenance

## Next Steps (Optional Enhancements)

1. **Remember Me** option to extend session beyond 30 days
2. **Session analytics** to track user activity patterns
3. **Multi-device session management** with device list
4. **Notification before logout** - warn user at 25 minutes of inactivity
5. **Persist session across browser tabs** using BroadcastChannel
6. **Biometric authentication** for sensitive operations

## Support

For issues or questions:
- Check browser console for session manager logs
- Review Supabase auth logs in dashboard
- Test with different idle timeout values
- Monitor network tab for token refresh requests
