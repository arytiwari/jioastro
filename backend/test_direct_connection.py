"""Test direct database connection (bypassing pooler)"""
import asyncio
import os

import pytest

if os.getenv("RUN_SUPABASE_TESTS") != "1":
    pytest.skip("Supabase integration tests are disabled", allow_module_level=True)

asyncpg = pytest.importorskip(
    "asyncpg", reason="asyncpg is required for Supabase connection smoke tests"
)

async def test_direct():
    # Try direct connection to Supabase database (not pooler)
    direct_url = "postgresql://postgres.jyawjajnxzuhzisjcnpn:Jio%40stro%409812@db.jyawjajnxzuhzisjcnpn.supabase.co:5432/postgres"

    print("=" * 60)
    print("TESTING DIRECT DATABASE CONNECTION (Port 5432)")
    print("=" * 60)
    print(f"\nDirect connection URL: {direct_url}\n")

    try:
        print("Attempting to connect...")
        conn = await asyncpg.connect(direct_url, timeout=10)
        print("✅ Direct connection successful!")

        version = await conn.fetchval('SELECT version()')
        print(f"\nPostgreSQL version:\n{version}\n")

        await conn.close()
        print("Connection closed successfully.")

        print("\n" + "=" * 60)
        print("RECOMMENDATION: Use direct connection in .env file")
        print("=" * 60)
        print("\nUpdate your DATABASE_URL in .env to:")
        print("DATABASE_URL=postgresql+asyncpg://postgres.jyawjajnxzuhzisjcnpn:Jio%40stro%409812@db.jyawjajnxzuhzisjcnpn.supabase.co:5432/postgres")
        return True

    except asyncio.TimeoutError:
        print("❌ Direct connection also timed out!")
        print("\nThis suggests a network/firewall issue.")
        print("Please check:")
        print("1. Your internet connection")
        print("2. Supabase project status (dashboard)")
        print("3. Try accessing Supabase from a different network")
        return False

    except asyncpg.InvalidPasswordError:
        print("❌ Invalid password!")
        print("\nThe database is reachable but password is wrong.")
        print("Please verify your database password in Supabase Settings → Database")
        return False

    except Exception as e:
        print(f"❌ Connection failed:")
        print(f"Error: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_direct())
