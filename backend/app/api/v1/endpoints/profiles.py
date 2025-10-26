"""Profile API Endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID

from app.db.database import get_db
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new birth profile"""

    # If this is set as primary, unset other primary profiles
    if profile_data.is_primary:
        await db.execute(
            update(Profile)
            .where(Profile.user_id == UUID(current_user["user_id"]))
            .values(is_primary=False)
        )

    # Create new profile
    new_profile = Profile(
        user_id=UUID(current_user["user_id"]),
        **profile_data.model_dump()
    )

    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)

    return new_profile


@router.get("/", response_model=List[ProfileResponse])
async def list_profiles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all profiles for the current user"""

    result = await db.execute(
        select(Profile)
        .where(Profile.user_id == UUID(current_user["user_id"]))
        .order_by(Profile.is_primary.desc(), Profile.created_at.desc())
    )

    profiles = result.scalars().all()
    return profiles


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific profile"""

    result = await db.execute(
        select(Profile).where(
            Profile.id == profile_id,
            Profile.user_id == UUID(current_user["user_id"])
        )
    )

    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return profile


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: UUID,
    profile_update: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a profile"""

    # Get existing profile
    result = await db.execute(
        select(Profile).where(
            Profile.id == profile_id,
            Profile.user_id == UUID(current_user["user_id"])
        )
    )

    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # If setting as primary, unset others
    if profile_update.is_primary:
        await db.execute(
            update(Profile)
            .where(Profile.user_id == UUID(current_user["user_id"]))
            .values(is_primary=False)
        )

    # Update profile
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)

    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a profile"""

    result = await db.execute(
        select(Profile).where(
            Profile.id == profile_id,
            Profile.user_id == UUID(current_user["user_id"])
        )
    )

    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    await db.delete(profile)
    await db.commit()

    return None
