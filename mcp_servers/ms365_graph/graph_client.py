"""Microsoft Graph API HTTP client with BYOT (Bring Your Own Token) auth."""

import os
from typing import Any

import httpx

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class GraphClient:
    """Thin async HTTP client for Microsoft Graph API."""

    def __init__(self, access_token: str | None = None):
        self.access_token = access_token or os.environ.get("MS365_ACCESS_TOKEN", "")
        if not self.access_token:
            raise ValueError(
                "No access token provided. Set MS365_ACCESS_TOKEN env var "
                "or pass access_token to GraphClient."
            )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        hdrs = self._headers()
        if headers:
            hdrs.update(headers)
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{GRAPH_BASE_URL}{path}", params=params, headers=hdrs
            )
            resp.raise_for_status()
            if resp.headers.get("content-type", "").startswith("application/json"):
                return resp.json()
            return {"content": resp.text}

    async def post(
        self,
        path: str,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        hdrs = self._headers()
        if headers:
            hdrs.update(headers)
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{GRAPH_BASE_URL}{path}", json=json_body, headers=hdrs
            )
            resp.raise_for_status()
            if resp.status_code in (202, 204):
                return {"status": "success"}
            if resp.headers.get("content-type", "").startswith("application/json"):
                return resp.json()
            return {"status": "success"}

    async def patch(
        self,
        path: str,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        hdrs = self._headers()
        if headers:
            hdrs.update(headers)
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.patch(
                f"{GRAPH_BASE_URL}{path}", json=json_body, headers=hdrs
            )
            resp.raise_for_status()
            if resp.status_code == 204:
                return {"status": "success"}
            if resp.headers.get("content-type", "").startswith("application/json"):
                return resp.json()
            return {"status": "success"}

    async def delete(
        self,
        path: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        hdrs = self._headers()
        if headers:
            hdrs.update(headers)
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.delete(f"{GRAPH_BASE_URL}{path}", headers=hdrs)
            resp.raise_for_status()
            return {"status": "deleted"}

    async def get_all_pages(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        max_pages: int = 10,
    ) -> list[dict[str, Any]]:
        """Follow @odata.nextLink to fetch all pages (up to max_pages)."""
        all_items: list[dict[str, Any]] = []
        url = f"{GRAPH_BASE_URL}{path}"
        page = 0
        async with httpx.AsyncClient(timeout=30) as client:
            while url and page < max_pages:
                resp = await client.get(
                    url,
                    params=params if page == 0 else None,
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                all_items.extend(data.get("value", []))
                url = data.get("@odata.nextLink")
                page += 1
        return all_items
