# Profile Deletion Fix - Complete ✅

## Summary

Fixed the profile deletion functionality for both regular users and admin. Users can now delete their own profiles, and admins can delete any profile through the admin panel.

## Issues Fixed

### 1. **Backend API Issue**
**Problem:** The admin delete endpoint was calling `delete_profile()` with missing parameters.

**Root Cause:**
- `supabase_service.delete_profile()` required both `profile_id` and `user_id` parameters
- Admin endpoint was only passing `profile_id`
- The method would fail because `user_id` was required but not provided

**Fix Applied:**
```python
# backend/app/services/supabase_service.py (line 68)
async def delete_profile(self, profile_id: str, user_id: str = None) -> bool:
    """Delete a profile - user_id is optional for admin deletion"""
    query = self.client.table("profiles").delete().eq("id", profile_id)
    if user_id:
        query = query.eq("user_id", user_id)
    response = query.execute()
    return len(response.data) > 0 if response.data else False
```

**Benefits:**
- ✅ Regular users can still delete only their own profiles (with user_id check)
- ✅ Admins can delete any profile (without user_id check)
- ✅ Security maintained through separate authentication layers

### 2. **Admin Endpoint Improvement**
**File:** `backend/app/api/v1/endpoints/admin.py` (lines 98-130)

**Changes:**
- Added profile existence check before deletion
- Updated parameter name from `user_id` to `profile_id` for clarity
- Added proper error handling with HTTPException
- Returns success message with `profile_id`

**Updated Endpoint:**
```python
@router.delete("/users/{profile_id}")
async def delete_user_profile(
    profile_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a user profile (admin only)"""
    try:
        # Check if profile exists
        profile = await supabase_service.get_profile(profile_id=profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Delete from Supabase (admin can delete without user_id check)
        success = await supabase_service.delete_profile(profile_id=profile_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete profile"
            )

        return {"message": "User profile deleted successfully", "profile_id": profile_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )
```

### 3. **Get Profile Method Update**
**File:** `backend/app/services/supabase_service.py` (line 54)

**Problem:** Admin couldn't fetch profile details without user_id

**Fix:**
```python
async def get_profile(self, profile_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
    """Get a specific profile - user_id is optional for admin access"""
    query = self.client.table("profiles").select("*").eq("id", profile_id)
    if user_id:
        query = query.eq("user_id", user_id)
    response = query.execute()
    return response.data[0] if response.data else None
```

### 4. **Frontend Delete Button Added**
**File:** `frontend/app/dashboard/profiles/[id]/page.tsx`

**Added Features:**
- Delete button with trash icon
- Confirmation dialog before deletion
- Loading state while deleting
- Automatic redirect to profiles list after successful deletion
- Cache invalidation to refresh profile list

**Implementation:**
```typescript
const handleDelete = async () => {
  if (!confirm('Are you sure you want to delete this profile? This action cannot be undone.')) {
    return
  }

  setDeleteLoading(true)
  try {
    await apiClient.deleteProfile(profileId)
    queryClient.invalidateQueries({ queryKey: ['profiles'] })
    router.push('/dashboard/profiles')
  } catch (error: any) {
    alert(error?.message || 'Failed to delete profile')
    setDeleteLoading(false)
  }
}
```

**UI Changes:**
- Added Trash2 icon to icons export
- Delete button appears next to "Ask Question" button
- Red destructive styling
- Disabled state during deletion

### 5. **Icon Export**
**File:** `frontend/components/icons.tsx`

**Added:** `Trash2` icon export from lucide-react

## Files Modified

### Backend:
1. **`backend/app/services/supabase_service.py`**
   - Line 54: Updated `get_profile()` to make `user_id` optional
   - Line 68: Updated `delete_profile()` to make `user_id` optional

2. **`backend/app/api/v1/endpoints/admin.py`**
   - Lines 98-130: Completely rewrote admin delete endpoint with proper validation and error handling

### Frontend:
1. **`frontend/components/icons.tsx`**
   - Line 31: Added `Trash2` icon export

2. **`frontend/app/dashboard/profiles/[id]/page.tsx`**
   - Lines 5, 14, 21-23: Added imports and state for delete functionality
   - Lines 92-106: Added `handleDelete` function
   - Lines 142-157: Added delete button to UI

## Security Considerations

### ✅ Implemented:
- **User-level deletion:** Regular users can only delete their own profiles (user_id check enforced)
- **Admin-level deletion:** Admins can delete any profile (authenticated via admin JWT)
- **Confirmation dialog:** Prevents accidental deletions
- **Existence check:** Validates profile exists before attempting deletion
- **Proper error handling:** Returns appropriate HTTP status codes

### 🔒 Security Flow:
1. **Regular User:**
   - Authenticated via Supabase JWT
   - `user_id` extracted from token
   - Can only delete profiles where `user_id` matches

2. **Admin:**
   - Authenticated via separate admin JWT
   - Special admin endpoints at `/api/v1/admin/*`
   - Can delete any profile without `user_id` restriction

## Testing

### Manual Testing Steps:

#### 1. Test Regular User Delete:
```bash
# Login as regular user
# Navigate to http://localhost:3000/dashboard/profiles/{profile_id}
# Click the red "Delete" button
# Confirm deletion in dialog
# Verify redirect to profiles list
# Verify profile is removed from database
```

#### 2. Test Admin Delete:
```bash
# Login as admin
# Navigate to admin users list
# Click delete on any profile
# Verify deletion success
```

#### 3. Test API Endpoint:
```bash
# Test user delete (requires valid user JWT)
curl -X DELETE \
  http://localhost:8000/api/v1/profiles/{profile_id} \
  -H "Authorization: Bearer {user_jwt_token}"

# Test admin delete (requires valid admin JWT)
curl -X DELETE \
  http://localhost:8000/api/v1/admin/users/{profile_id} \
  -H "Authorization: Bearer {admin_jwt_token}"
```

## Current Status

### ✅ Completed:
- Backend delete methods fixed
- Admin endpoint updated
- Frontend delete button added
- Confirmation dialog implemented
- Error handling added
- Icon exports updated
- Both servers running

### 🧪 Tested:
- Backend API health check ✅
- Admin authentication ✅
- Profile deletion flow (needs manual UI testing)

## How to Use

### As a Regular User:
1. Navigate to any of your profiles
2. Click the red "Delete" button in the top-right
3. Confirm the deletion
4. You'll be redirected to the profiles list

### As an Admin:
1. Login to admin panel
2. Navigate to Users section
3. Click delete button next to any user profile
4. Profile will be deleted from database

## Future Enhancements (Optional)

1. **Cascade deletion:** Also delete related charts, queries, and responses when profile is deleted
2. **Soft delete:** Mark profiles as deleted instead of hard delete (for data recovery)
3. **Audit logging:** Log all profile deletions for compliance
4. **Batch deletion:** Allow admin to delete multiple profiles at once
5. **Delete confirmation with typing:** Require user to type "DELETE" for extra safety

## Notes

- The API client already had the `deleteProfile()` method implemented
- Session management with auto-refresh ensures deletion requests don't fail due to expired tokens
- Frontend uses React Query to automatically invalidate cache after deletion

## Support

If deletion is not working:
1. Check browser console for errors
2. Verify authentication token is valid
3. Check backend logs: `curl http://localhost:8000/health`
4. Ensure profile exists in database
5. Test API endpoint directly with curl

---

**Status:** ✅ Complete and Ready for Testing

**Servers Running:**
- Backend: http://localhost:8000 ✅
- Frontend: http://localhost:3000 ✅
