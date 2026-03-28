from __future__ import annotations

import httpx


class BackendApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def health(self) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def latest_scholarships(self, limit: int = 5) -> list[dict]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/scholarships", params={"limit": limit, "skip": 0})
            response.raise_for_status()
            return response.json()
