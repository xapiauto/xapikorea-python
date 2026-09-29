from __future__ import annotations

from typing import Any

import httpx

from .errors import APIError, XAPIKoreaError
from .models import AccountInfo, Car, InspectionReport, SearchResponse


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

    def search(
        self,
        *,
        brand: str | None = None,
        model: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        price_min: int | None = None,
        price_max: int | None = None,
        fuel_type: str | None = None,
        transmission: str | None = None,
        body_style: str | None = None,
        car_type: str | None = None,
        is_accident_free: bool | None = None,
        sort: str | None = None,
        page: int = 1,
        limit: int = 20,
        lang: str = "en",
    ) -> SearchResponse:
        params = {
            "brand": brand,
            "model": model,
            "year_from": year_from,
            "year_to": year_to,
            "price_min": price_min,
            "price_max": price_max,
            "fuel_type": fuel_type,
            "transmission": transmission,
            "body_style": body_style,
            "car_type": car_type,
            "is_accident_free": is_accident_free,
            "sort": sort,
            "page": page,
            "limit": limit,
            "lang": lang,
        }
        data = self._request(
            "GET",
            "v1/search",
            params={key: value for key, value in params.items() if value is not None},
        )
        if not isinstance(data, dict):
            raise XAPIKoreaError("Unexpected response from GET /v1/search")

        try:
            return SearchResponse.from_dict(data)
        except (KeyError, TypeError) as exc:
            raise XAPIKoreaError("Unexpected response from GET /v1/search") from exc

    def get_car(self, car_id: int, *, lang: str = "en") -> Car:
        data = self._request(
            "GET",
            f"v1/cars/{car_id}",
            params={"lang": lang},
        )
        if not isinstance(data, dict):
            raise XAPIKoreaError(f"Unexpected response from GET /v1/cars/{car_id}")

        try:
            return Car.from_dict(data)
        except (KeyError, TypeError) as exc:
            raise XAPIKoreaError(
                f"Unexpected response from GET /v1/cars/{car_id}"
            ) from exc

    def get_inspection(self, car_id: int, *, lang: str = "en") -> InspectionReport:
        path = f"v1/cars/{car_id}/inspection"
        data = self._request("GET", path, params={"lang": lang})
        if not isinstance(data, dict):
            raise XAPIKoreaError(f"Unexpected response from GET /{path}")

        try:
            return InspectionReport.from_dict(data)
        except (KeyError, TypeError) as exc:
            raise XAPIKoreaError(f"Unexpected response from GET /{path}") from exc

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, str | int | bool] | None = None,
    ) -> Any:
        try:
            response = self._client.request(method, path, params=params)
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
