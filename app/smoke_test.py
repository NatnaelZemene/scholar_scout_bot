import asyncio
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import text

# Support running as `python app/smoke_test.py` from project root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api.main import app
from app.db.session import engine


def check_api() -> None:
    client = TestClient(app)
    health = client.get("/health")
    ping = client.get("/ping")
    assert health.status_code == 200
    assert ping.status_code == 200


async def check_db() -> None:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar_one() == 1


if __name__ == "__main__":
    check_api()
    asyncio.run(check_db())
    print("Smoke test passed")
