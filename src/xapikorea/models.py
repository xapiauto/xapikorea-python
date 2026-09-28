from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AccountInfo:
    email: str
    plan: str
    key_label: str
    key_prefix: str
    requests_this_month: int
    monthly_cap: int | None
    remaining: int | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AccountInfo:
        return cls(
            email=data["email"],
            plan=data["plan"],
            key_label=data["key_label"],
            key_prefix=data["key_prefix"],
            requests_this_month=data["requests_this_month"],
            monthly_cap=data.get("monthly_cap"),
            remaining=data.get("remaining"),
        )


@dataclass(frozen=True)
class CarSummary:
    id: int
    manufacturer: str
    model: str
    badge: str
    badge_detail: str | None
    year: str
    mileage_km: int
    price_krw: int
    price_eur: float
    fuel_type: str
    transmission: str
    location: str
    thumbnail: str
    encar_url: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CarSummary:
        return cls(
            id=data["id"],
            manufacturer=data["manufacturer"],
            model=data["model"],
            badge=data["badge"],
            badge_detail=data.get("badge_detail"),
            year=data["year"],
            mileage_km=data["mileage_km"],
            price_krw=data["price_krw"],
            price_eur=data["price_eur"],
            fuel_type=data["fuel_type"],
            transmission=data["transmission"],
            location=data["location"],
            thumbnail=data["thumbnail"],
            encar_url=data["encar_url"],
        )


@dataclass(frozen=True)
class SearchResponse:
    total_count: int
    page: int
    limit: int
    results: tuple[CarSummary, ...]
    next_page: int | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SearchResponse:
        results = data["results"]
        if not isinstance(results, list):
            raise TypeError("results must be a list")

        return cls(
            total_count=data["total_count"],
            page=data["page"],
            limit=data["limit"],
            results=tuple(CarSummary.from_dict(item) for item in results),
            next_page=data["next_page"],
        )
