"""One-time migration: add user_type column and backfill existing users."""
import asyncio
import os

os.environ.setdefault("DATABASE_URL", "postgresql://agentic:agentic_dev_password@localhost:5432/agentic_marketplace")

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DB_URL = "postgresql+asyncpg://agentic:agentic_dev_password@localhost:5432/agentic_marketplace"

async def main():
    engine = create_async_engine(DB_URL, echo=True)
    
    async with engine.begin() as conn:
        # Create the enum type first
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'usertype') THEN
                    CREATE TYPE usertype AS ENUM ('creator', 'customer');
                END IF;
            END$$;
        """))
        
        # Add column if not exists
        await conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS user_type usertype;
        """))
        
        # Backfill: set creator account as creator, admin as NULL (super admin)
        await conn.execute(text("""
            UPDATE users SET user_type = 'creator' WHERE email = 'creator@agentic.com';
        """))
        await conn.execute(text("""
            UPDATE users SET user_type = 'customer' WHERE user_type IS NULL AND is_super_admin = false;
        """))
        
        print("✅ Migration complete!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
