"""Debug script to check .env configuration"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Print loaded values (masking sensitive parts)
database_url = os.getenv("DATABASE_URL", "NOT FOUND")
supabase_url = os.getenv("SUPABASE_URL", "NOT FOUND")
supabase_key = os.getenv("SUPABASE_KEY", "NOT FOUND")

print("=" * 60)
print("ENVIRONMENT VARIABLES CHECK")
print("=" * 60)
print(f"\n.env file location: {env_path}")
print(f".env file exists: {env_path.exists()}")
print("\n" + "=" * 60)
print("DATABASE_URL:")
print("=" * 60)
print(database_url)

print("\n" + "=" * 60)
print("SUPABASE_URL:")
print("=" * 60)
print(supabase_url)

print("\n" + "=" * 60)
print("SUPABASE_KEY (first 50 chars):")
print("=" * 60)
print(supabase_key[:50] + "..." if len(supabase_key) > 50 else supabase_key)

print("\n" + "=" * 60)
print("VALIDATION:")
print("=" * 60)

# Check for common issues
issues = []

if "DATABASE_URL" not in os.environ:
    issues.append("❌ DATABASE_URL not found in environment")
elif "[password]" in database_url or "YOUR_PASSWORD" in database_url:
    issues.append("❌ DATABASE_URL contains placeholder '[password]' or 'YOUR_PASSWORD'")
elif "xxx" in database_url:
    issues.append("❌ DATABASE_URL contains placeholder 'xxx'")
elif not database_url.startswith("postgresql+asyncpg://"):
    issues.append("❌ DATABASE_URL should start with 'postgresql+asyncpg://'")
else:
    issues.append("✅ DATABASE_URL format looks correct")

if "xxx" in supabase_url:
    issues.append("❌ SUPABASE_URL contains placeholder 'xxx'")
elif supabase_url == "NOT FOUND":
    issues.append("❌ SUPABASE_URL not found")
else:
    issues.append("✅ SUPABASE_URL looks correct")

if "your-supabase-key" in supabase_key or supabase_key == "NOT FOUND":
    issues.append("❌ SUPABASE_KEY contains placeholder or not found")
elif not supabase_key.startswith("eyJ"):
    issues.append("❌ SUPABASE_KEY should start with 'eyJ'")
else:
    issues.append("✅ SUPABASE_KEY looks correct")

for issue in issues:
    print(issue)

print("\n" + "=" * 60)
