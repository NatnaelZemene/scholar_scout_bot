import asyncio

from sqlalchemy import text

from app.db.session import engine


async def main() -> None:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("DB SELECT 1 ->", result.scalar_one())


if __name__ == "__main__":
    asyncio.run(main())

