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
