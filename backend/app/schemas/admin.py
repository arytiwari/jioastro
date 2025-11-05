"""Admin schemas for request/response validation"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class AdminLogin(BaseModel):
    """Admin login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class AdminLoginResponse(BaseModel):
    """Admin login response with token"""
    access_token: str
    token_type: str = "bearer"
    admin_id: str
    username: str


class AdminCreate(BaseModel):
    """Create new admin user"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[str] = None


class AdminResponse(BaseModel):
    """Admin user response"""
    id: UUID
    username: str
    email: Optional[str]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class AdminPasswordReset(BaseModel):
    """Reset user password (admin only)"""
    user_id: str = Field(..., description="User ID to reset password for")
    new_password: str = Field(..., min_length=6, description="New password")
