from __future__ import annotations

from typing import Any

import httpx

from .errors import APIError, XAPIKoreaError
from .models import AccountInfo


class XAPIKorea:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.xapikorea.com",
        timeout: float = 30.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key is required")

        self._client = httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "Accept": "application/json",
                "User-Agent": "xapikorea-python/0.1.0",
            },
        )

    def __enter__(self) -> XAPIKorea:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def me(self) -> AccountInfo:
        data = self._request("GET", "v1/me")
        if not isinstance(data, dict):
            raise XAPIKoreaError("Unexpected response from GET /v1/me")

        try:
            return AccountInfo.from_dict(data)
        except (KeyError, TypeError) as exc:
            raise XAPIKoreaError("Unexpected response from GET /v1/me") from exc

    def _request(self, method: str, path: str) -> Any:
        try:
            response = self._client.request(method, path)
        except httpx.TimeoutException as exc:
            raise XAPIKoreaError("Request timed out") from exc
        except httpx.RequestError as exc:
            raise XAPIKoreaError("Could not connect to XAPI Korea") from exc

        try:
            body = response.json()
        except ValueError:
            body = response.text or None

        if response.is_error:
            message = f"API request failed with status {response.status_code}"
            if isinstance(body, dict) and isinstance(body.get("error"), str):
                message = body["error"]

            retry_after = response.headers.get("Retry-After")
            raise APIError(
                message,
                status_code=response.status_code,
                body=body,
                retry_after=int(retry_after) if retry_after and retry_after.isdigit() else None,
            )

        return body

