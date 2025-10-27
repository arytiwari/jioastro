"""Profile API Endpoints - Using Supabase REST API"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.core.security import get_current_user
from app.services.supabase_service import supabase_service

router = APIRouter()


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new birth profile"""
    try:
        profile = await supabase_service.create_profile(
            user_id=current_user["user_id"],
            profile_data=profile_data.model_dump()
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create profile"
            )

        return profile
    except Exception as e:
        print(f"Error creating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}"
        )


@router.get("/", response_model=List[ProfileResponse])
async def list_profiles(
    current_user: dict = Depends(get_current_user)
):
    """List all profiles for the current user"""
    try:
        profiles = await supabase_service.get_profiles(user_id=current_user["user_id"])
        return profiles
    except Exception as e:
        print(f"Error listing profiles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list profiles: {str(e)}"
        )


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific profile"""
    try:
        profile = await supabase_service.get_profile(
            profile_id=profile_id,
            user_id=current_user["user_id"]
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        return profile
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    profile_update: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a profile"""
    try:
        # Check if profile exists
        existing_profile = await supabase_service.get_profile(
            profile_id=profile_id,
            user_id=current_user["user_id"]
        )

        if not existing_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Update profile
        update_data = profile_update.model_dump(exclude_unset=True)
        updated_profile = await supabase_service.update_profile(
            profile_id=profile_id,
            user_id=current_user["user_id"],
            update_data=update_data
        )

        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )

        return updated_profile
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a profile"""
    try:
        # Check if profile exists
        existing_profile = await supabase_service.get_profile(
            profile_id=profile_id,
            user_id=current_user["user_id"]
        )

        if not existing_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Delete profile
        success = await supabase_service.delete_profile(
            profile_id=profile_id,
            user_id=current_user["user_id"]
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete profile"
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete profile: {str(e)}"
        )
