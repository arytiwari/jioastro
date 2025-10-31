"""Simple database connection test"""
import asyncio
import os
import urllib.parse

import pytest

pytest.importorskip(
    "dotenv", reason="python-dotenv is required for Supabase connection smoke tests"
)
from dotenv import load_dotenv

asyncpg = pytest.importorskip(
    "asyncpg", reason="asyncpg is required for Supabase connection smoke tests"
)
load_dotenv()

async def test_connection():
    database_url = os.getenv("DATABASE_URL")

    print("=" * 60)
    print("TESTING DATABASE CONNECTION")
    print("=" * 60)
    print(f"\nOriginal DATABASE_URL: {database_url}\n")

    # Parse the URL
    if database_url.startswith("postgresql+asyncpg://"):
        # Remove the sqlalchemy dialect
        db_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        print(f"Cleaned URL for asyncpg: {db_url}\n")
    else:
        db_url = database_url

    # Try to connect
    try:
        print("Attempting to connect...")
        conn = await asyncpg.connect(db_url, timeout=10)
        print("✅ Connection successful!")

        # Try a simple query
        version = await conn.fetchval('SELECT version()')
        print(f"\nPostgreSQL version:\n{version}\n")

        await conn.close()
        print("Connection closed successfully.")
        return True

    except asyncio.TimeoutError:
        print("❌ Connection timed out!")
        print("\nPossible issues:")
        print("1. Wrong host/port (check if you're using pooler.supabase.com:6543)")
        print("2. Connection pooling not enabled in Supabase")
        print("3. Firewall blocking the connection")
        return False

    except asyncpg.InvalidPasswordError:
        print("❌ Invalid password!")
        print("\nPlease check:")
        print("1. Your database password in Supabase Settings → Database")
        print("2. Special characters are URL-encoded (@ becomes %40)")
        return False

    except Exception as e:
        print(f"❌ Connection failed with error:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if success:
        print("\n" + "=" * 60)
        print("DATABASE CONNECTION IS WORKING!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("DATABASE CONNECTION FAILED - CHECK CONFIGURATION")
        print("=" * 60)
