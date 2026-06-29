from typing import Any

import httpx

from app.core.config import settings


class ThingsBoardClient:
    def __init__(self) -> None:
        self.base_url = settings.thingsboard_base_url.rstrip("/")
        self.username = settings.thingsboard_username
        self.password = settings.thingsboard_password

    async def _token(self) -> str:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=15) as client:
            response = await client.post(
                "/api/auth/login",
                json={"username": self.username, "password": self.password},
            )
            response.raise_for_status()
            return response.json()["token"]

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        token = await self._token()
        headers = kwargs.pop("headers", {})
        headers["X-Authorization"] = f"Bearer {token}"
        async with httpx.AsyncClient(base_url=self.base_url, timeout=20) as client:
            response = await client.request(method, path, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None

    async def health(self) -> dict[str, str]:
        await self._token()
        return {"status": "connected", "provider": "thingsboard"}

    async def create_device(self, name: str, device_type: str, label: str | None = None) -> dict[str, Any]:
        payload = {"name": name, "type": device_type}
        if label:
            payload["label"] = label
        return await self._request("POST", "/api/device", json=payload)

    async def get_latest_telemetry(self, device_id: str, keys: list[str] | None = None) -> dict[str, Any]:
        query = {"keys": ",".join(keys)} if keys else None
        return await self._request(
            "GET",
            f"/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries",
            params=query,
        )

    async def get_device_credentials(self, device_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/device/{device_id}/credentials")


thingsboard_client = ThingsBoardClient()
