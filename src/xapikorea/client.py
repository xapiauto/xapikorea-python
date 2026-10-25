from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar
from urllib.parse import quote

import httpx

from ._version import __version__
from .errors import APIError, XAPIKoreaError
from .models import (
    AccountInfo,
    Car,
    CarSummary,
    CountResponse,
    FiltersResponse,
    InspectionReport,
    InsuranceHistory,
    MakeModelsResponse,
    SearchResponse,
    TrimsResponse,
    _strings,
)

T = TypeVar("T")


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
                "User-Agent": f"xapikorea-python/{__version__}",
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
        source: str = "encar",
        currency: str = "krw",
        mileage_min: int | None = None,
        mileage_max: int | None = None,
        sale_type: str | None = None,
        color: str | None = None,
        trim: str | None = None,
        generation: str | None = None,
        badge_group: str | None = None,
        badge: str | None = None,
    ) -> SearchResponse:
        """Search one marketplace or both; follow next_page with identical filters."""
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
            "source": source,
            "currency": currency,
            "mileage_min": mileage_min,
            "mileage_max": mileage_max,
            "sale_type": sale_type,
            "color": color,
            "trim": trim,
            "generation": generation,
            "badge_group": badge_group,
            "badge": badge,
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

    def get_car(self, car_id: int, *, lang: str = "en", source: str = "encar") -> Car:
        data = self._request(
            "GET",
            f"v1/cars/{car_id}",
            params={"lang": lang, "source": source},
        )
        if not isinstance(data, dict):
            raise XAPIKoreaError(f"Unexpected response from GET /v1/cars/{car_id}")

        try:
            return Car.from_dict(data)
        except (KeyError, TypeError) as exc:
            raise XAPIKoreaError(
                f"Unexpected response from GET /v1/cars/{car_id}"
            ) from exc

    def get_inspection(
        self, car_id: int, *, lang: str = "en", source: str = "encar"
    ) -> InspectionReport:
        path = f"v1/cars/{car_id}/inspection"
        data = self._request("GET", path, params={"lang": lang, "source": source})
        if not isinstance(data, dict):
            raise XAPIKoreaError(f"Unexpected response from GET /{path}")

        try:
            return InspectionReport.from_dict(data)
        except (KeyError, TypeError) as exc:
            raise XAPIKoreaError(f"Unexpected response from GET /{path}") from exc

    def get_insurance(self, car_id: int, *, source: str = "encar") -> InsuranceHistory:
        """Get Encar insurance history; unavailable records mean unknown history."""
        return self._get_object(
            f"v1/cars/{car_id}/insurance", InsuranceHistory.from_dict, {"source": source}
        )

    def get_images(self, car_id: int, *, source: str = "encar") -> tuple[str, ...]:
        return self._get_parsed(f"v1/cars/{car_id}/images", _strings, {"source": source})

    def get_similar(
        self, car_id: int, *, source: str = "encar", limit: int = 10, lang: str = "en"
    ) -> tuple[CarSummary, ...]:
        """Get similar Encar listings. KB ChaChaCha currently returns HTTP 501."""
        def parse(data: Any) -> tuple[CarSummary, ...]:
            if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
                raise TypeError("expected a list of objects")
            return tuple(CarSummary.from_dict(item) for item in data)

        return self._get_parsed(
            f"v1/cars/{car_id}/similar", parse,
            {"source": source, "limit": limit, "lang": lang},
        )

    def get_filters(self, *, source: str = "encar") -> FiltersResponse:
        return self._get_object("v1/filters", FiltersResponse.from_dict, {"source": source})

    def get_makes(self, *, source: str = "encar") -> tuple[str, ...]:
        return self._get_parsed("v1/makes", _strings, {"source": source})

    def get_models(self, make: str, *, source: str = "encar") -> MakeModelsResponse:
        return self._get_object(
            f"v1/makes/{quote(make, safe='')}/models", MakeModelsResponse.from_dict,
            {"source": source},
        )

    def get_trims(
        self,
        *,
        brand: str,
        model: str,
        source: str = "encar",
        generation: str | None = None,
        badge_group: str | None = None,
        badge: str | None = None,
    ) -> TrimsResponse:
        """Discover Encar variants; pass choice.value back as the exact filter."""
        return self._get_object(
            "v1/trims", TrimsResponse.from_dict,
            {
                "brand": brand, "model": model, "source": source,
                "generation": generation, "badge_group": badge_group, "badge": badge,
            },
        )

    def count(
        self,
        *,
        source: str = "encar",
        brand: str | None = None,
        model: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        price_min: int | None = None,
        price_max: int | None = None,
        currency: str = "krw",
        mileage_min: int | None = None,
        mileage_max: int | None = None,
        fuel_type: str | None = None,
        transmission: str | None = None,
        car_type: str | None = None,
        is_accident_free: bool | None = None,
        sale_type: str | None = None,
        color: str | None = None,
        trim: str | None = None,
        generation: str | None = None,
        badge_group: str | None = None,
        badge: str | None = None,
    ) -> CountResponse:
        """Count matching listings without fetching a page of results."""
        return self._get_object(
            "v1/search/count", CountResponse.from_dict,
            {
                "source": source, "brand": brand, "model": model,
                "year_from": year_from, "year_to": year_to,
                "price_min": price_min, "price_max": price_max, "currency": currency,
                "mileage_min": mileage_min, "mileage_max": mileage_max,
                "fuel_type": fuel_type, "transmission": transmission, "car_type": car_type,
                "is_accident_free": is_accident_free, "sale_type": sale_type, "color": color,
                "trim": trim, "generation": generation, "badge_group": badge_group, "badge": badge,
            },
        )

    def _get_object(
        self,
        path: str,
        parser: Callable[[dict[str, Any]], T],
        params: dict[str, str | int | bool | None],
    ) -> T:
        def parse(data: Any) -> T:
            if not isinstance(data, dict):
                raise TypeError("expected an object")
            return parser(data)

        return self._get_parsed(path, parse, params)

    def _get_parsed(
        self,
        path: str,
        parser: Callable[[Any], T],
        params: dict[str, str | int | bool | None],
    ) -> T:
        data = self._request(
            "GET", path, params={key: value for key, value in params.items() if value is not None}
        )
        try:
            return parser(data)
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
