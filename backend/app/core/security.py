"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SUPABASE_JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        # Decode Supabase JWT token without audience verification
        # Supabase tokens have audience claim set to "authenticated"
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False}  # Skip audience verification for Supabase tokens
        )
        print(f"✅ Token verified successfully for user: {payload.get('sub')}")
        return payload
    except JWTError as e:
        print(f"❌ JWT verification failed: {type(e).__name__}: {str(e)}")
        print(f"Token (first 50 chars): {token[:50]}...")
        print(f"JWT Secret (first 20 chars): {settings.SUPABASE_JWT_SECRET[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return {"user_id": user_id, "email": payload.get("email")}
