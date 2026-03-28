import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

# Support running as `python app/db/smoke_test.py` from project root.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.session import engine


async def main() -> None:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("DB SELECT 1 ->", result.scalar_one())


if __name__ == "__main__":
    asyncio.run(main())

