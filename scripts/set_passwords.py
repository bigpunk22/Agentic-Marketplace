"""Set passwords for customer test accounts."""
import asyncio
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DB = "postgresql+asyncpg://agentic:agentic_dev_password@localhost:5432/agentic_marketplace"

async def main():
    engine = create_async_engine(DB)
    async with engine.begin() as conn:
        pw = pwd_context.hash("Customer123!")
        await conn.execute(text("UPDATE users SET password_hash=:pw WHERE email='dadyjoe@example.com'"), {"pw": pw})
        print("✅ dadyjoe@example.com -> Customer123!")

        pw2 = pwd_context.hash("Customer123!")
        await conn.execute(text("UPDATE users SET password_hash=:pw WHERE email='tenanttest@example.com'"), {"pw": pw2})
        print("✅ tenanttest@example.com -> Customer123!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
