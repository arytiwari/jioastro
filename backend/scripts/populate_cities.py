#!/usr/bin/env python3
"""Script to populate Indian cities in the database"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create engine with longer timeout
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and not DATABASE_URL.startswith('postgresql+asyncpg://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "timeout": 30,  # 30 second timeout
        "command_timeout": 30
    }
)


async def populate_cities():
    """Run the cities migration SQL"""

    migration_file = Path(__file__).parent.parent / "migrations" / "add_indian_cities.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return

    # Read SQL file
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    print("🚀 Running cities migration...")
    print(f"📄 Migration file: {migration_file}")

    # Execute SQL
    async with engine.begin() as conn:
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

        total_statements = len(statements)
        print(f"📊 Executing {total_statements} SQL statements...\n")

        for i, statement in enumerate(statements, 1):
            try:
                # Skip comment-only statements
                if statement.strip().startswith('--') or not statement.strip():
                    continue

                await conn.execute(text(statement))

                # Print progress for key operations
                if 'CREATE TABLE' in statement:
                    print(f"✅ [{i}/{total_statements}] Created cities table")
                elif 'CREATE INDEX' in statement:
                    print(f"✅ [{i}/{total_statements}] Created index")
                elif 'TRUNCATE' in statement:
                    print(f"✅ [{i}/{total_statements}] Cleared existing data")
                elif 'INSERT INTO cities' in statement:
                    # Count how many cities in this insert
                    lines = statement.count('\n')
                    if lines > 5:
                        print(f"✅ [{i}/{total_statements}] Inserted cities batch ({lines} rows)")
                elif 'COMMENT' in statement:
                    print(f"✅ [{i}/{total_statements}] Added table comments")

            except Exception as e:
                print(f"❌ Error executing statement {i}: {e}")
                print(f"Statement: {statement[:100]}...")
                raise

        await conn.commit()

    # Count total cities
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM cities"))
        count = result.scalar()
        print(f"\n✅ Migration completed successfully!")
        print(f"📊 Total cities in database: {count}")

        # Show sample cities
        result = await conn.execute(text("SELECT name, state, display_name FROM cities ORDER BY RANDOM() LIMIT 10"))
        cities = result.fetchall()
        print(f"\n📋 Sample cities:")
        for city in cities:
            print(f"  • {city[2]}")


if __name__ == "__main__":
    asyncio.run(populate_cities())
