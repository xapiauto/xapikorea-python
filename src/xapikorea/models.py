from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _listing_url(data: dict[str, Any]) -> str | None:
    url = data.get("listing_url")
    if url is None and data.get("source", "encar") == "encar":
        return data.get("encar_url")
    return url


def _strings(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError("expected a list of strings")
    return tuple(value)


def _source_metadata(data: dict[str, Any]) -> dict[str, Any]:
    errors = data.get("source_errors", {})
    if not isinstance(errors, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in errors.items()
    ):
        raise TypeError("source_errors must be an object of strings")
    return {
        "sources": _strings(data.get("sources", ["encar"])),
        "partial": data.get("partial", False),
        "source_errors": dict(errors),
    }


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
    badge: str | None = None
    badge_detail: str | None = None
    year: str | None = None
    mileage_km: int | None = None
    price_krw: int | None = None
    price_eur: float | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    location: str | None = None
    thumbnail: str | None = None
    encar_url: str | None = None
    source: str = "encar"
    listing_url: str | None = None
    sales_status: str | None = None
    listing_status: str | None = None
    sale_type: str | None = None
    lease_rent: LeaseRentTerms | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CarSummary:
        lease_rent = data.get("lease_rent")
        if lease_rent is not None and not isinstance(lease_rent, dict):
            raise TypeError("lease_rent must be an object")

        return cls(
            id=data["id"],
            manufacturer=data["manufacturer"],
            model=data["model"],
            badge=data.get("badge"),
            badge_detail=data.get("badge_detail"),
            year=data.get("year"),
            mileage_km=data.get("mileage_km"),
            price_krw=data.get("price_krw"),
            price_eur=data.get("price_eur"),
            fuel_type=data.get("fuel_type"),
            transmission=data.get("transmission"),
            location=data.get("location"),
            thumbnail=data.get("thumbnail"),
            encar_url=data.get("encar_url"),
            source=data.get("source", "encar"),
            listing_url=_listing_url(data),
            sales_status=data.get("sales_status"),
            listing_status=data.get("listing_status"),
            sale_type=data.get("sale_type"),
            lease_rent=LeaseRentTerms.from_dict(lease_rent) if lease_rent is not None else None,
        )


@dataclass(frozen=True)
class SearchResponse:
    total_count: int
    page: int
    limit: int
    results: tuple[CarSummary, ...]
    next_page: int | None
    sources: tuple[str, ...] = ("encar",)
    partial: bool = False
    source_errors: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SearchResponse:
        results = data["results"]
        if not isinstance(results, list) or not all(isinstance(item, dict) for item in results):
            raise TypeError("results must be a list of objects")

        return cls(
            total_count=data["total_count"],
            page=data["page"],
            limit=data["limit"],
            results=tuple(CarSummary.from_dict(item) for item in results),
            next_page=data.get("next_page"),
            **_source_metadata(data),
        )


@dataclass(frozen=True)
class LeaseRentTerms:
    monthly_fee_krw: int | None = None
    remaining_months: int | None = None
    deposit_krw: int | None = None
    advance_krw: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LeaseRentTerms:
        return cls(
            monthly_fee_krw=data.get("monthly_fee_krw"),
            remaining_months=data.get("remaining_months"),
            deposit_krw=data.get("deposit_krw"),
            advance_krw=data.get("advance_krw"),
        )


@dataclass(frozen=True)
class Warranty:
    company_name: str | None = None
    body_months: int | None = None
    body_mileage_km: int | None = None
    transmission_months: int | None = None
    transmission_mileage_km: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Warranty:
        return cls(
            company_name=data.get("company_name"),
            body_months=data.get("body_months"),
            body_mileage_km=data.get("body_mileage_km"),
            transmission_months=data.get("transmission_months"),
            transmission_mileage_km=data.get("transmission_mileage_km"),
        )


@dataclass(frozen=True)
class Car:
    id: int
    manufacturer: str
    model: str
    badge: str | None = None
    badge_detail: str | None = None
    year: str | None = None
    mileage_km: int | None = None
    price_krw: int | None = None
    price_eur: float | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    location: str | None = None
    thumbnail: str | None = None
    encar_url: str | None = None
    form_year: int | None = None
    original_price_krw: int | None = None
    drive_type: str | None = None
    engine_cc: str | None = None
    seat_count: int | None = None
    doors: int | None = None
    origin_country: str | None = None
    body_style: str | None = None
    color: str | None = None
    vin: str | None = None
    vehicle_no: str | None = None
    vehicle_id: int | None = None
    vehicle_type: str | None = None
    inspection_available: bool = False
    insurance_available: bool = False
    is_rental: bool | None = None
    sale_type: str | None = None
    lease_rent: LeaseRentTerms | None = None
    photos: tuple[str, ...] = ()
    diagnosis_image_url: str | None = None
    options: tuple[str, ...] = ()
    is_reserved: bool | None = None
    seizing_count: int | None = None
    pledge_count: int | None = None
    warranty: Warranty | None = None
    source: str = "encar"
    listing_url: str | None = None
    sales_status: str | None = None
    listing_status: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Car:
        lease_rent_data = data.get("lease_rent")
        if lease_rent_data is not None and not isinstance(lease_rent_data, dict):
            raise TypeError("lease_rent must be an object")

        warranty_data = data.get("warranty")
        if warranty_data is not None and not isinstance(warranty_data, dict):
            raise TypeError("warranty must be an object")

        photos = data.get("photos", [])
        if not isinstance(photos, list):
            raise TypeError("photos must be a list")

        options = data.get("options", [])
        if not isinstance(options, list):
            raise TypeError("options must be a list")

        return cls(
            id=data["id"],
            manufacturer=data["manufacturer"],
            model=data["model"],
            badge=data.get("badge"),
            badge_detail=data.get("badge_detail"),
            year=data.get("year"),
            mileage_km=data.get("mileage_km"),
            price_krw=data.get("price_krw"),
            price_eur=data.get("price_eur"),
            fuel_type=data.get("fuel_type"),
            transmission=data.get("transmission"),
            location=data.get("location"),
            thumbnail=data.get("thumbnail"),
            encar_url=data.get("encar_url"),
            form_year=data.get("form_year"),
            original_price_krw=data.get("original_price_krw"),
            drive_type=data.get("drive_type"),
            engine_cc=data.get("engine_cc"),
            seat_count=data.get("seat_count"),
            doors=data.get("doors"),
            origin_country=data.get("origin_country"),
            body_style=data.get("body_style"),
            color=data.get("color"),
            vin=data.get("vin"),
            vehicle_no=data.get("vehicle_no"),
            vehicle_id=data.get("vehicle_id"),
            vehicle_type=data.get("vehicle_type"),
            inspection_available=data.get("inspection_available", False),
            insurance_available=data.get("insurance_available", False),
            is_rental=data.get("is_rental"),
            sale_type=data.get("sale_type"),
            lease_rent=(
                LeaseRentTerms.from_dict(lease_rent_data)
                if lease_rent_data is not None
                else None
            ),
            photos=tuple(photos),
            diagnosis_image_url=data.get("diagnosis_image_url"),
            options=tuple(options),
            is_reserved=data.get("is_reserved"),
            seizing_count=data.get("seizing_count"),
            pledge_count=data.get("pledge_count"),
            warranty=(
                Warranty.from_dict(warranty_data)
                if warranty_data is not None
                else None
            ),
            source=data.get("source", "encar"),
            listing_url=_listing_url(data),
            sales_status=data.get("sales_status"),
            listing_status=data.get("listing_status"),
        )


@dataclass(frozen=True)
class PanelDamage:
    panel: str
    damage: tuple[str, ...] = ()
    rank: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PanelDamage:
        damage = data.get("damage", [])
        if not isinstance(damage, list):
            raise TypeError("damage must be a list")

        return cls(
            panel=data["panel"],
            damage=tuple(damage),
            rank=data.get("rank"),
        )


@dataclass(frozen=True)
class InspectionReport:
    available: bool = True
    is_rental: bool | None = None
    usage_history: tuple[str, ...] = ()
    had_accident: bool | None = None
    had_simple_repair: bool | None = None
    damage_severity: str | None = None
    panel_damage: tuple[PanelDamage, ...] = ()
    has_tuning: bool | None = None
    tuning_types: tuple[str, ...] = ()
    first_registration_date: str | None = None
    inspection_date: str | None = None
    inspection_grade: str | None = None
    inspection_report_url: str | None = None
    inspection_report_print_url: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InspectionReport:
        usage_history = data.get("usage_history", [])
        if not isinstance(usage_history, list):
            raise TypeError("usage_history must be a list")

        panel_damage = data.get("panel_damage", [])
        if not isinstance(panel_damage, list) or not all(
            isinstance(item, dict) for item in panel_damage
        ):
            raise TypeError("panel_damage must be a list of objects")

        tuning_types = data.get("tuning_types", [])
        if not isinstance(tuning_types, list):
            raise TypeError("tuning_types must be a list")

        return cls(
            available=data.get("available", True),
            is_rental=data.get("is_rental"),
            usage_history=tuple(usage_history),
            had_accident=data.get("had_accident"),
            had_simple_repair=data.get("had_simple_repair"),
            damage_severity=data.get("damage_severity"),
            panel_damage=tuple(PanelDamage.from_dict(item) for item in panel_damage),
            has_tuning=data.get("has_tuning"),
            tuning_types=tuple(tuning_types),
            first_registration_date=data.get("first_registration_date"),
            inspection_date=data.get("inspection_date"),
            inspection_grade=data.get("inspection_grade"),
            inspection_report_url=data.get("inspection_report_url"),
            inspection_report_print_url=data.get("inspection_report_print_url"),
        )


@dataclass(frozen=True)
class InsuranceHistory:
    available: bool = True
    accident_report_url: str | None = None
    had_insurance_accident: bool | None = None
    accident_count: int | None = None
    accident_cost_krw: int | None = None
    other_accident_count: int | None = None
    other_accident_cost_krw: int | None = None
    owner_change_count: int | None = None
    was_flooded: bool | None = None
    was_total_loss: bool | None = None
    was_stolen: bool | None = None
    used_as_rental: bool | None = None
    used_as_commercial: bool | None = None
    used_as_government: bool | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InsuranceHistory:
        return cls(
            available=data.get("available", True),
            accident_report_url=data.get("accident_report_url"),
            had_insurance_accident=data.get("had_insurance_accident"),
            accident_count=data.get("accident_count"),
            accident_cost_krw=data.get("accident_cost_krw"),
            other_accident_count=data.get("other_accident_count"),
            other_accident_cost_krw=data.get("other_accident_cost_krw"),
            owner_change_count=data.get("owner_change_count"),
            was_flooded=data.get("was_flooded"),
            was_total_loss=data.get("was_total_loss"),
            was_stolen=data.get("was_stolen"),
            used_as_rental=data.get("used_as_rental"),
            used_as_commercial=data.get("used_as_commercial"),
            used_as_government=data.get("used_as_government"),
        )


@dataclass(frozen=True)
class FiltersResponse:
    manufacturers: tuple[str, ...]
    fuel_types: tuple[str, ...]
    transmissions: tuple[str, ...]
    body_styles: tuple[str, ...]
    sort_options: tuple[str, ...]
    colors: tuple[str, ...] = ()
    trims: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FiltersResponse:
        return cls(
            manufacturers=_strings(data["manufacturers"]),
            fuel_types=_strings(data["fuel_types"]),
            transmissions=_strings(data["transmissions"]),
            body_styles=_strings(data["body_styles"]),
            sort_options=_strings(data["sort_options"]),
            colors=_strings(data.get("colors", [])),
            trims=_strings(data.get("trims", [])),
        )


@dataclass(frozen=True)
class MakeModelsResponse:
    make: str
    models: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MakeModelsResponse:
        return cls(make=data["make"], models=_strings(data["models"]))


@dataclass(frozen=True)
class TrimChoice:
    value: str
    label: str
    count: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrimChoice:
        return cls(value=data["value"], label=data["label"], count=data["count"])


@dataclass(frozen=True)
class TrimsResponse:
    brand: str
    model: str
    generation: str | None = None
    badge_group: str | None = None
    badge: str | None = None
    generations: tuple[TrimChoice, ...] = ()
    badge_groups: tuple[TrimChoice, ...] = ()
    badges: tuple[TrimChoice, ...] = ()
    trims: tuple[TrimChoice, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrimsResponse:
        choices = {}
        for key in ("generations", "badge_groups", "badges", "trims"):
            items = data.get(key, [])
            if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
                raise TypeError(f"{key} must be a list of objects")
            choices[key] = tuple(TrimChoice.from_dict(item) for item in items)
        return cls(
            brand=data["brand"],
            model=data["model"],
            generation=data.get("generation"),
            badge_group=data.get("badge_group"),
            badge=data.get("badge"),
            **choices,
        )


@dataclass(frozen=True)
class CountResponse:
    count: int
    sources: tuple[str, ...] = ("encar",)
    partial: bool = False
    source_errors: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CountResponse:
        return cls(count=data["count"], **_source_metadata(data))
