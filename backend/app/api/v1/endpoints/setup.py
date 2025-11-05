"""Setup endpoints for initial system configuration"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.db.database import get_db, Base, engine
from app.models.admin import AdminUser
from app.core.admin_security import hash_password

router = APIRouter()


@router.post("/initialize-admin", status_code=status.HTTP_201_CREATED)
async def initialize_admin_system(db: AsyncSession = Depends(get_db)):
    """
    Initialize admin system - creates tables and default admin user
    This endpoint can be called without authentication for initial setup

    ⚠️ SECURITY: This endpoint should be disabled in production or protected
    """
    try:
        # Create tables
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            from app.models import AdminUser, KnowledgeDocument

            # Create admin tables
            await conn.run_sync(Base.metadata.create_all)

        # Check if admin user already exists
        result = await db.execute(
            select(AdminUser).where(AdminUser.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            return {
                "message": "Admin system already initialized",
                "admin_exists": True,
                "admin_id": str(existing_admin.id),
                "username": existing_admin.username
            }

        # Create default admin user
        admin = AdminUser(
            username="admin",
            password_hash=hash_password("admin@123"),
            email="admin@jioastro.com",
            is_active=True
        )

        db.add(admin)
        await db.commit()
        await db.refresh(admin)

        return {
            "message": "Admin system initialized successfully",
            "admin_created": True,
            "admin_id": str(admin.id),
            "username": "admin",
            "default_password": "admin@123",
            "warning": "Please change the default password immediately!"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize admin system: {str(e)}"
        )


@router.get("/check-admin")
async def check_admin_exists(db: AsyncSession = Depends(get_db)):
    """Check if admin system is initialized"""
    try:
        result = await db.execute(
            select(AdminUser).where(AdminUser.username == "admin")
        )
        admin = result.scalar_one_or_none()

        return {
            "admin_exists": admin is not None,
            "admin_id": str(admin.id) if admin else None,
            "username": admin.username if admin else None,
            "is_active": admin.is_active if admin else None
        }
    except Exception as e:
        # Table might not exist yet
        return {
            "admin_exists": False,
            "error": "Admin tables not created yet",
            "message": "Call /setup/initialize-admin to create tables and admin user"
        }


@router.post("/create-tables-only")
async def create_admin_tables_only():
    """
    Create admin tables only (without creating admin user)
    Useful if you want to create admin user manually
    """
    try:
        async with engine.begin() as conn:
            # Import all models
            from app.models import AdminUser, KnowledgeDocument

            # Create tables
            await conn.run_sync(Base.metadata.create_all)

        return {
            "message": "Admin tables created successfully",
            "tables_created": ["admin_users", "knowledge_documents"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tables: {str(e)}"
        )
