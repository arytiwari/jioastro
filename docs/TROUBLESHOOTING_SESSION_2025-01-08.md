# Troubleshooting Session - January 8, 2025

## Summary
This session involved migrating from SQLAlchemy to Supabase REST API and fixing multiple authentication and routing issues. This document captures critical learnings to prevent similar issues in future development.

---

## Issue #1: SQLAlchemy Cannot Connect (500 Errors)

### Problem
```
TimeoutError: PostgreSQL connection failed
500 Internal Server Error on all new endpoints (Prashna, Chart Comparison)
```

### Root Cause
- **PostgreSQL ports (5432) are blocked** in deployment environments
- Backend was using SQLAlchemy ORM with direct PostgreSQL connection
- `init_db()` was timing out trying to create tables
- Models weren't being imported properly at startup

### Solution
✅ **Complete migration to Supabase REST API**

**Created enhanced Supabase client** (`app/core/supabase_client.py`):
```python
class SupabaseClient:
    async def select(self, table, filters, order, limit, offset, single)
    async def insert(self, table, data)
    async def update(self, table, filters, data)
    async def delete(self, table, filters)
    async def count(self, table, filters)
    async def rpc(self, function_name, params)
```

**Updated `database.py`**:
```python
# NEW: Primary dependency
def get_supabase_client() -> SupabaseClient:
    return supabase_client

# DEPRECATED: Legacy SQLAlchemy (kept for backward compatibility)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    ...
```

**Migrated endpoints**:
- Prashna: All 5 endpoints (analyze, save, list, get, delete)
- Chart Comparison: compare endpoint

### Key Learnings
1. ✅ **ALWAYS use Supabase REST API for database operations**
2. ❌ **NEVER use SQLAlchemy in this project** (ports are blocked)
3. ✅ **Use `get_supabase_client()` dependency, NOT `get_db()`**
4. ✅ **Work with dictionaries, NOT ORM models**

---

## Issue #2: JWT Token Structure Mismatch (KeyError: 'sub')

### Problem
```python
KeyError: 'sub'
# at: user_id = current_user["sub"]
```

### Root Cause
**Inconsistent token payload structure across codebase**

- `get_current_user()` in `security.py` returns:
  ```python
  {"user_id": user_id, "email": payload.get("email")}
  ```
- But new endpoints were trying to access:
  ```python
  user_id = current_user["sub"]  # ❌ This key doesn't exist!
  ```

### Solution
✅ **Updated all endpoints to use correct key**

**Before** (WRONG):
```python
user_id = current_user["sub"]  # ❌ KeyError!
```

**After** (CORRECT):
```python
user_id = current_user["user_id"]  # ✅ Works!
```

**Files fixed**:
- `app/api/v1/endpoints/prashna.py` (4 places)
- `app/api/v1/endpoints/chart_comparison.py` (1 place)

### Key Learnings
1. ✅ **Check `security.py` to understand JWT payload structure**
2. ✅ **Always use `current_user["user_id"]` NOT `current_user["sub"]`**
3. ✅ **Test endpoints immediately after creation to catch these early**
4. ✅ **Add detailed error logging to see actual payload structure**

---

## Issue #3: Route Matching Bug (Automatic Logout)

### Problem
```
User gets logged out automatically when clicking Prashna
localStorage.getItem('supabase.session') returns null
Session not found in storage
```

### Root Cause
**Faulty public route detection logic in `dashboard/layout.tsx`**

**Before** (WRONG):
```typescript
const isPublicRoute = publicRoutes.some(route => {
  const currentStartsWithPublic = normalizedPath.startsWith(normalizedRoute)
  const publicStartsWithCurrent = normalizedRoute.startsWith(normalizedPath) && normalizedPath !== '/'
  return currentStartsWithPublic || publicStartsWithCurrent  // ❌ BUG!
})
```

**The bug**: When on `/dashboard`, it checked:
- `"/dashboard/instant-onboarding".startsWith("/dashboard")` ✅ true
- So `/dashboard` was marked as **public**
- Session was **NOT loaded** on dashboard
- Then navigating to `/dashboard/prashna` = **no session** = **logout**

### Solution
✅ **Fixed route matching to be strict**

**After** (CORRECT):
```typescript
const isPublicRoute = publicRoutes.some(route => {
  const normalizedRoute = route.toLowerCase()
  // Exact match or proper sub-path only
  const match = normalizedPath === normalizedRoute ||
                normalizedPath.startsWith(normalizedRoute + '/')
  return match  // ✅ Correct!
})
```

**Now**:
- `/dashboard` = protected ✅
- `/dashboard/instant-onboarding` = public ✅
- `/dashboard/instant-onboarding/step1` = public ✅
- `/dashboard/prashna` = protected ✅

### Key Learnings
1. ✅ **Route matching must be exact or proper sub-path with `/`**
2. ❌ **NEVER use `startsWith()` alone for route matching**
3. ✅ **Test route logic with various paths**:
   - Parent path (`/dashboard`)
   - Public route (`/dashboard/instant-onboarding`)
   - Protected route (`/dashboard/prashna`)
   - Nested paths (`/dashboard/instant-onboarding/step1`)
4. ✅ **Add debug logging to route detection during development**

---

## Issue #4: HTTP Request Timeouts

### Problem
```python
httpx.ConnectTimeout
# at: supabase.count("prashnas", filters=filters)
```

### Root Cause
**Missing timeout configuration for httpx AsyncClient**
- Default httpx timeout is too short for Supabase queries
- Complex queries or slow network can cause timeouts

### Solution
✅ **Added 30-second timeout to all HTTP requests**

**Before** (WRONG):
```python
async with httpx.AsyncClient() as client:  # ❌ Uses default timeout (5s)
    response = await client.get(url, headers=headers, params=params)
```

**After** (CORRECT):
```python
async with httpx.AsyncClient(timeout=30.0) as client:  # ✅ 30 second timeout
    response = await client.get(url, headers=headers, params=params)
```

**Updated in**:
- `count()` method
- `select()` method
- `insert()` method
- `update()` method
- `delete()` method
- `rpc()` method

### Key Learnings
1. ✅ **ALWAYS set explicit timeout for httpx clients**
2. ✅ **Use 30s timeout for Supabase REST API calls**
3. ✅ **Apply timeout to ALL async HTTP methods consistently**
4. ✅ **Consider longer timeouts for complex queries or large datasets**

---

## Issue #5: Database Schema Assumptions

### Problem
```
Supabase SELECT error: 400 - column charts.created_at does not exist
```

### Root Cause
**Assumed `created_at` column exists in `charts` table**
```python
charts_1 = await supabase.select(
    "charts",
    filters={"profile_id": request.profile_id_1, "chart_type": "D1"},
    order="created_at.desc",  # ❌ Column doesn't exist!
    limit=1
)
```

### Solution
✅ **Removed non-existent column reference**

**After** (CORRECT):
```python
charts_1 = await supabase.select(
    "charts",
    filters={"profile_id": request.profile_id_1, "chart_type": "D1"},
    limit=1  # ✅ No ordering
)
```

### Key Learnings
1. ✅ **Check actual database schema before writing queries**
2. ✅ **Use Supabase dashboard to verify column names**
3. ❌ **NEVER assume standard column names exist (created_at, updated_at)**
4. ✅ **Run database migrations to add missing standard columns if needed**
5. ✅ **Test queries in Supabase SQL editor first**

---

## Issue #6: Session Refresh Logic

### Problem
```
Session was being cleared on refresh failures
Even valid sessions were lost on transient errors
```

### Root Cause
**Too aggressive session clearing in `getValidSession()`**
- Refresh failure → `null` session → automatic logout
- No distinction between expired tokens and network errors

### Solution
✅ **Made session refresh more robust**

```typescript
export async function getValidSession(): Promise<SupabaseSession | null> {
  const session = getSession()
  if (!session) return null

  if (isSessionExpired(300)) {
    const result = await refreshSession()

    // If refresh fails but session not completely expired, keep it
    if (!result.data.session && session) {
      const now = Math.floor(Date.now() / 1000)
      const isCompletelyExpired = session.expires_at && now >= session.expires_at

      if (isCompletelyExpired) {
        return null  // Truly expired
      }

      // Session expires soon but still valid, allow it
      return session
    }

    return result.data.session
  }

  return session
}
```

### Key Learnings
1. ✅ **Distinguish between expired sessions and network errors**
2. ✅ **Don't clear valid sessions on transient failures**
3. ✅ **Check actual expiry time before rejecting session**
4. ✅ **Add detailed logging to session management**

---

## Architecture Guidelines (UPDATED)

### Database Access Pattern

**✅ REQUIRED Pattern for ALL new code:**

```python
from fastapi import APIRouter, Depends
from app.core.supabase_client import SupabaseClient
from app.db.database import get_supabase_client
from app.core.security import get_current_user

@router.get("/items")
async def list_items(
    current_user: dict = Depends(get_current_user),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    user_id = current_user["user_id"]  # ✅ Use "user_id" NOT "sub"

    # Count
    total = await supabase.count("items", filters={"user_id": user_id})

    # Select with pagination
    items = await supabase.select(
        "items",
        filters={"user_id": user_id},
        order="id.desc",  # ✅ Verify column exists first!
        limit=10,
        offset=0
    )

    return {"items": items, "total": total}
```

**❌ NEVER DO THIS:**
```python
# ❌ Don't use SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.item import Item

async def list_items(db: AsyncSession = Depends(get_db)):
    query = select(Item).where(Item.user_id == user_id)
    # This will FAIL - PostgreSQL ports are blocked!
```

### Frontend Route Protection

**✅ REQUIRED Pattern:**

```typescript
// Exact match or proper sub-path only
const isPublicRoute = publicRoutes.some(route => {
  const normalizedRoute = route.toLowerCase()
  return normalizedPath === normalizedRoute ||
         normalizedPath.startsWith(normalizedRoute + '/')
})
```

**❌ NEVER DO THIS:**
```typescript
// ❌ Don't use startsWith alone
const isPublicRoute = publicRoutes.some(route =>
  normalizedPath.startsWith(route.toLowerCase())
)
```

---

## Testing Checklist for New Features

Before marking a feature as complete, verify:

### Backend
- [ ] Uses `get_supabase_client()` NOT `get_db()`
- [ ] Uses `current_user["user_id"]` NOT `current_user["sub"]`
- [ ] All HTTP clients have explicit 30s timeout
- [ ] Database columns referenced actually exist (check Supabase dashboard)
- [ ] Error logging includes detailed exception tracebacks
- [ ] Test endpoint via `/docs` Swagger UI
- [ ] Check backend logs for any errors

### Frontend
- [ ] Hard refresh browser after code changes
- [ ] Test with and without authentication
- [ ] Test route protection (public vs protected)
- [ ] Check `localStorage.getItem('supabase.session')` is not null
- [ ] Verify no automatic logout when navigating
- [ ] Check browser console for errors
- [ ] Test error handling (network failures, invalid data)

### Integration
- [ ] Test full user flow end-to-end
- [ ] Verify session persists across page navigation
- [ ] Check for 500 errors in browser Network tab
- [ ] Test with slow network (throttling)
- [ ] Verify Row-Level Security policies work correctly

---

## Quick Reference: Common Error Solutions

| Error | Root Cause | Solution |
|-------|-----------|----------|
| `KeyError: 'sub'` | Wrong JWT payload key | Use `current_user["user_id"]` |
| `TimeoutError` / `ConnectTimeout` | No HTTP timeout set | Add `timeout=30.0` to httpx.AsyncClient |
| `column X does not exist` | Schema assumption | Verify columns in Supabase dashboard |
| `500 Internal Server Error` | Multiple possible | Check backend logs with full traceback |
| Automatic logout | Route matching bug | Fix route protection logic |
| `No session found in storage` | Session not loaded on parent route | Check route matching logic |
| `Could not validate credentials` | Missing/expired JWT token | Check token refresh logic |

---

## Files Modified in This Session

### Backend
1. `app/core/supabase_client.py` - Enhanced with count(), timeouts
2. `app/db/database.py` - Added get_supabase_client(), deprecated get_db()
3. `app/api/v1/endpoints/prashna.py` - Migrated to Supabase REST API
4. `app/api/v1/endpoints/chart_comparison.py` - Migrated to Supabase REST API
5. `CLAUDE.md` - Added Database Access Pattern guidelines

### Frontend
6. `lib/supabase.ts` - Enhanced getValidSession() with better error handling
7. `app/dashboard/layout.tsx` - Fixed route matching logic

---

## For Future Development

### When Adding New Endpoints

1. **Start with Supabase REST API pattern** (see Architecture Guidelines above)
2. **Use `get_supabase_client()` dependency**
3. **Add timeout to ALL HTTP clients**
4. **Verify database schema first**
5. **Use `current_user["user_id"]`**
6. **Add detailed error logging**
7. **Test immediately via Swagger UI**

### When Adding New Protected Routes

1. **DON'T add to publicRoutes** unless truly public
2. **Test route matching logic** with various paths
3. **Verify session loads** on parent routes
4. **Check localStorage** has session data
5. **Test navigation** from other pages

### When Debugging

1. **Check backend logs** first (full traceback)
2. **Check browser console** for frontend errors
3. **Verify localStorage** has session
4. **Test API directly** via Swagger UI
5. **Check Supabase dashboard** for schema/data
6. **Add temporary debug logging** to isolate issue

---

## Conclusion

This session revealed critical architectural issues that were systematically resolved:

1. ✅ Migrated from SQLAlchemy to Supabase REST API
2. ✅ Fixed JWT token structure inconsistencies
3. ✅ Resolved route matching and session management bugs
4. ✅ Added proper HTTP timeouts
5. ✅ Fixed database schema assumptions

**Most Important Takeaway**:
> **ALWAYS use Supabase REST API (`get_supabase_client()`) for database operations. NEVER use SQLAlchemy (`get_db()`) - PostgreSQL ports are blocked.**

Following the patterns and checklists in this document will prevent similar issues in future development.
