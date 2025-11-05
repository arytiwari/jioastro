"""
Create initial admin user
Run this script to create the default admin user with username "admin" and password "admin@123"
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.db.database import AsyncSessionLocal, engine, Base
from app.models.admin import AdminUser
from app.core.admin_security import hash_password


async def create_admin_tables():
    """Create admin tables in database"""
    print("Creating admin tables...")
    async with engine.begin() as conn:
        # Import all models to ensure they're registered
        from app.models import AdminUser, KnowledgeDocument

        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Admin tables created successfully")


async def create_default_admin():
    """Create default admin user"""
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        result = await session.execute(
            select(AdminUser).where(AdminUser.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("⚠️  Admin user already exists")
            print(f"   Username: {existing_admin.username}")
            print(f"   ID: {existing_admin.id}")
            print(f"   Created: {existing_admin.created_at}")
            return existing_admin

        # Create new admin user
        admin = AdminUser(
            username="admin",
            password_hash=hash_password("admin@123"),
            email="admin@jioastro.com",
            is_active=True
        )

        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        print("✅ Admin user created successfully")
        print(f"   Username: admin")
        print(f"   Password: admin@123")
        print(f"   ID: {admin.id}")
        print(f"   Email: {admin.email}")

        return admin


async def main():
    """Main function"""
    print("=" * 50)
    print("Admin User Initialization")
    print("=" * 50)

    try:
        # Create tables
        await create_admin_tables()

        # Create admin user
        await create_default_admin()

        print("\n" + "=" * 50)
        print("✅ Setup completed successfully!")
        print("=" * 50)
        print("\nYou can now log in to the admin portal with:")
        print("  Username: admin")
        print("  Password: admin@123")
        print("\n⚠️  IMPORTANT: Change the default password after first login!")

    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
