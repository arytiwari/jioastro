"""
Database connection and session management
Using Supabase REST API (Primary) with SQLAlchemy fallback (Deprecated)

IMPORTANT: All new code should use Supabase REST API via get_supabase_client()
SQLAlchemy support is deprecated and will be removed in future versions.
"""

from typing import AsyncGenerator
from app.core.supabase_client import SupabaseClient, supabase_client
from app.core.config import settings

# DEPRECATED: SQLAlchemy is being phased out - use Supabase REST API instead
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Convert postgres:// to postgresql+asyncpg:// for async support
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    future=True,
    pool_pre_ping=True,
    connect_args={
        "timeout": 5,
        "command_timeout": 5
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def init_db():
    """
    Initialize database (SQLAlchemy - DEPRECATED)

    This function attempts direct PostgreSQL connection via SQLAlchemy.
    It's normal for this to fail if PostgreSQL ports are blocked.
    The application will use Supabase REST API as the primary database interface.
    """
    try:
        async with engine.begin() as conn:
            # Import all models here to ensure they are registered
            from app.models import profile, chart, query, response, feedback, prashna, varshaphal
            # Create tables
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        # Expected to fail if PostgreSQL ports are blocked
        pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session (DEPRECATED)

    WARNING: This is deprecated. Use get_supabase_client() instead.
    This function is only kept for backward compatibility with legacy code.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_supabase_client() -> SupabaseClient:
    """
    Dependency for getting Supabase REST API client.

    This is the RECOMMENDED way to interact with the database.

    Example usage in FastAPI endpoint:
    ```python
    @router.get("/items")
    async def list_items(
        supabase: SupabaseClient = Depends(get_supabase_client),
        current_user: dict = Depends(get_current_user)
    ):
        items = await supabase.select(
            "items",
            filters={"user_id": current_user["sub"]},
            order="created_at.desc",
            limit=10
        )
        return items
    ```

    Returns:
        SupabaseClient: Configured Supabase REST API client
    """
    return supabase_client
