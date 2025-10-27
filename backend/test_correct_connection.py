"""Test connection with the correct Supabase format"""
import asyncio
import asyncpg

async def test_correct_format():
    # Using the DIRECT_URL format from Supabase (port 5432, no pgbouncer)
    correct_url = "postgresql://postgres.jyawjajnxzuhzisjcnpn:Jio%40stro%409812@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres"

    print("=" * 70)
    print("TESTING WITH CORRECT SUPABASE FORMAT")
    print("=" * 70)
    print(f"\nConnection URL: {correct_url}\n")
    print("Using DIRECT_URL format (port 5432, no pgbouncer parameter)\n")

    try:
        print("Attempting to connect...")
        conn = await asyncpg.connect(correct_url, timeout=15)
        print("✅ CONNECTION SUCCESSFUL!\n")

        # Test query
        version = await conn.fetchval('SELECT version()')
        print(f"PostgreSQL version:\n{version}\n")

        # Test a simple table query
        result = await conn.fetchval('SELECT current_database()')
        print(f"Current database: {result}\n")

        await conn.close()
        print("Connection closed successfully.")

        print("\n" + "=" * 70)
        print("SUCCESS! Update your .env file with this DATABASE_URL:")
        print("=" * 70)
        print("\nDATABASE_URL=postgresql+asyncpg://postgres.jyawjajnxzuhzisjcnpn:Jio%40stro%409812@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres")
        print("\nKey points:")
        print("- Use port 5432 (not 6543)")
        print("- No pgbouncer=true parameter")
        print("- postgresql+asyncpg:// prefix for SQLAlchemy")
        return True

    except asyncio.TimeoutError:
        print("❌ Connection timed out")
        print("\nThe port 5432 on the pooler host is not responding.")
        print("Please check if IPv6/IPv4 settings or try the direct database host.")
        return False

    except asyncpg.InvalidPasswordError:
        print("❌ Invalid password!")
        print("\nThe password is incorrect. Please verify it in Supabase.")
        return False

    except Exception as e:
        print(f"❌ Connection failed:")
        print(f"Error: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_correct_format())

    if not success:
        print("\n" + "=" * 70)
        print("If this still fails, we'll need to use Supabase via REST API")
        print("=" * 70)
