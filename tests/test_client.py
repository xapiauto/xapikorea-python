from __future__ import annotations

from collections.abc import Callable, Iterator
from functools import partial

import httpx
import pytest

import xapikorea.client as client_module
from xapikorea import (
    APIError,
    AccountInfo,
    Car,
    CarSummary,
    InspectionReport,
    LeaseRentTerms,
    PanelDamage,
    SearchResponse,
    Warranty,
    XAPIKorea,
    XAPIKoreaError,
)


Handler = Callable[[httpx.Request], httpx.Response]


@pytest.fixture
def client_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Callable[[Handler], XAPIKorea]]:
    clients: list[XAPIKorea] = []
    real_client = httpx.Client

    def create(handler: Handler) -> XAPIKorea:
        monkeypatch.setattr(
            client_module.httpx,
            "Client",
            partial(real_client, transport=httpx.MockTransport(handler)),
        )
        client = XAPIKorea("enc_test_key", base_url="https://api.example.test")
        clients.append(client)
        return client

    yield create

    for client in clients:
        client.close()


def test_api_key_is_required() -> None:
    with pytest.raises(ValueError, match="api_key is required"):
        XAPIKorea("   ")


def test_me_sends_authenticated_request_and_returns_account(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url == "https://api.example.test/v1/me"
        assert request.headers["X-API-Key"] == "enc_test_key"
        assert request.headers["Accept"] == "application/json"
        assert request.headers["User-Agent"] == "xapikorea-python/0.1.0"
        return httpx.Response(
            200,
            json={
                "email": "developer@example.com",
                "plan": "starter",
                "key_label": "test",
                "key_prefix": "enc_test",
                "requests_this_month": 12,
                "monthly_cap": 1_000,
                "remaining": 988,
            },
        )

    account = client_factory(handler).me()

    assert account == AccountInfo(
        email="developer@example.com",
        plan="starter",
        key_label="test",
        key_prefix="enc_test",
        requests_this_month=12,
        monthly_cap=1_000,
        remaining=988,
    )


@pytest.mark.parametrize(
    "payload",
    [
        ["not", "an", "object"],
        {"email": "missing-required-fields@example.com"},
    ],
)
def test_me_rejects_unexpected_responses(
    client_factory: Callable[[Handler], XAPIKorea], payload: object
) -> None:
    client = client_factory(lambda request: httpx.Response(200, json=payload))

    with pytest.raises(XAPIKoreaError, match="Unexpected response from GET /v1/me"):
        client.me()


def test_search_sends_filters_and_returns_results(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/v1/search"
        assert request.url.params == httpx.QueryParams(
            {
                "brand": "hyundai",
                "model": "avante",
                "year_from": 2022,
                "year_to": 2024,
                "price_min": 10_000_000,
                "price_max": 30_000_000,
                "fuel_type": "gasoline",
                "transmission": "auto",
                "body_style": "suv",
                "car_type": "Y",
                "is_accident_free": True,
                "sort": "Price",
                "page": 2,
                "limit": 5,
                "lang": "en",
            }
        )
        return httpx.Response(
            200,
            json={
                "total_count": 1,
                "page": 2,
                "limit": 5,
                "results": [
                    {
                        "id": 41750571,
                        "manufacturer": "Hyundai",
                        "model": "Avante (Elantra)",
                        "badge": "2.0 N",
                        "badge_detail": None,
                        "year": "202209",
                        "mileage_km": 64806,
                        "price_krw": 20500000,
                        "price_eur": 13325.0,
                        "fuel_type": "Gasoline",
                        "transmission": "Automatic",
                        "location": "Incheon",
                        "thumbnail": "https://example.test/car.jpg",
                        "encar_url": "https://fem.encar.com/cars/detail/41750571",
                    }
                ],
                "next_page": None,
            },
        )

    response = client_factory(handler).search(
        brand="hyundai",
        model="avante",
        year_from=2022,
        year_to=2024,
        price_min=10_000_000,
        price_max=30_000_000,
        fuel_type="gasoline",
        transmission="auto",
        body_style="suv",
        car_type="Y",
        is_accident_free=True,
        sort="Price",
        page=2,
        limit=5,
    )

    assert response == SearchResponse(
        total_count=1,
        page=2,
        limit=5,
        results=(
            CarSummary(
                id=41750571,
                manufacturer="Hyundai",
                model="Avante (Elantra)",
                badge="2.0 N",
                badge_detail=None,
                year="202209",
                mileage_km=64806,
                price_krw=20500000,
                price_eur=13325.0,
                fuel_type="Gasoline",
                transmission="Automatic",
                location="Incheon",
                thumbnail="https://example.test/car.jpg",
                encar_url="https://fem.encar.com/cars/detail/41750571",
            ),
        ),
        next_page=None,
    )


def test_search_rejects_unexpected_responses(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    client = client_factory(
        lambda request: httpx.Response(
            200,
            json={
                "total_count": 1,
                "page": 1,
                "limit": 20,
                "results": "not a list",
                "next_page": None,
            },
        )
    )

    with pytest.raises(XAPIKoreaError, match="Unexpected response from GET /v1/search"):
        client.search()


def test_get_car_returns_vehicle_details(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/v1/cars/42662587"
        assert request.url.params == httpx.QueryParams({"lang": "ko"})
        return httpx.Response(
            200,
            json={
                "id": 42662587,
                "manufacturer": "ChevroletGMDaewoo",
                "model": "트랙스 Crossover",
                "badge": "1.2 RS",
                "badge_detail": None,
                "year": "202606",
                "mileage_km": 21,
                "price_krw": 25800000,
                "price_eur": 16770.0,
                "fuel_type": "Gasoline",
                "transmission": "Automatic",
                "location": "Daegu",
                "thumbnail": "https://example.test/thumbnail.jpg",
                "encar_url": "https://fem.encar.com/cars/detail/42662587",
                "form_year": 2026,
                "original_price_krw": 28510000,
                "drive_type": None,
                "engine_cc": "1199cc",
                "seat_count": 5,
                "doors": 5,
                "origin_country": "South Korea",
                "body_style": "SUV",
                "color": "Black",
                "vin": "KLALA582DTC112253",
                "vehicle_no": "332우7403",
                "vehicle_id": 42662055,
                "vehicle_type": "CAR",
                "inspection_available": True,
                "insurance_available": True,
                "is_rental": False,
                "sale_type": "lease",
                "lease_rent": {
                    "monthly_fee_krw": 500000,
                    "remaining_months": 12,
                    "deposit_krw": 3000000,
                    "advance_krw": None,
                },
                "photos": [
                    "https://example.test/1.jpg",
                    "https://example.test/2.jpg",
                ],
                "diagnosis_image_url": "https://example.test/diagnosis.jpg",
                "options": ["Sunroof", "Navigation"],
                "is_reserved": True,
                "seizing_count": 0,
                "pledge_count": 0,
                "warranty": {
                    "company_name": None,
                    "body_months": 36,
                    "body_mileage_km": 60000,
                    "transmission_months": 60,
                    "transmission_mileage_km": 100000,
                },
            },
        )

    car = client_factory(handler).get_car(42662587, lang="ko")

    assert isinstance(car, Car)
    assert car.id == 42662587
    assert car.model == "트랙스 Crossover"
    assert car.drive_type is None
    assert car.photos == (
        "https://example.test/1.jpg",
        "https://example.test/2.jpg",
    )
    assert car.options == ("Sunroof", "Navigation")
    assert car.lease_rent == LeaseRentTerms(
        monthly_fee_krw=500000,
        remaining_months=12,
        deposit_krw=3000000,
    )
    assert car.warranty == Warranty(
        company_name=None,
        body_months=36,
        body_mileage_km=60000,
        transmission_months=60,
        transmission_mileage_km=100000,
    )


def test_get_car_accepts_minimal_response(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    client = client_factory(
        lambda request: httpx.Response(
            200,
            json={"id": 1, "manufacturer": "Hyundai", "model": "Sonata"},
        )
    )

    car = client.get_car(1)

    assert car == Car(id=1, manufacturer="Hyundai", model="Sonata")


def test_get_car_rejects_unexpected_response(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    client = client_factory(
        lambda request: httpx.Response(
            200,
            json={
                "id": 1,
                "manufacturer": "Hyundai",
                "model": "Sonata",
                "photos": "not a list",
            },
        )
    )

    with pytest.raises(
        XAPIKoreaError, match="Unexpected response from GET /v1/cars/1"
    ):
        client.get_car(1)


def test_get_car_exposes_not_found_error(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    client = client_factory(
        lambda request: httpx.Response(404, json={"error": "Car not found"})
    )

    with pytest.raises(APIError, match="Car not found") as caught:
        client.get_car(999)

    assert caught.value.status_code == 404


def test_get_inspection_returns_report(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/v1/cars/42662587/inspection"
        assert request.url.params == httpx.QueryParams({"lang": "ko"})
        return httpx.Response(
            200,
            json={
                "available": True,
                "is_rental": False,
                "usage_history": ["Commercial Use"],
                "had_accident": True,
                "had_simple_repair": False,
                "damage_severity": "minor",
                "panel_damage": [
                    {
                        "panel": "Front Fender",
                        "damage": ["Replacement"],
                        "rank": "A",
                    }
                ],
                "has_tuning": True,
                "tuning_types": ["Suspension"],
                "first_registration_date": "20260604",
                "inspection_date": "20260901",
                "inspection_grade": "Good",
                "inspection_report_url": "https://example.test/inspection",
                "inspection_report_print_url": "https://example.test/print",
            },
        )

    report = client_factory(handler).get_inspection(42662587, lang="ko")

    assert report == InspectionReport(
        available=True,
        is_rental=False,
        usage_history=("Commercial Use",),
        had_accident=True,
        had_simple_repair=False,
        damage_severity="minor",
        panel_damage=(
            PanelDamage(
                panel="Front Fender",
                damage=("Replacement",),
                rank="A",
            ),
        ),
        has_tuning=True,
        tuning_types=("Suspension",),
        first_registration_date="20260604",
        inspection_date="20260901",
        inspection_grade="Good",
        inspection_report_url="https://example.test/inspection",
        inspection_report_print_url="https://example.test/print",
    )


def test_get_inspection_preserves_unavailable_state(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    client = client_factory(
        lambda request: httpx.Response(200, json={"available": False})
    )

    report = client.get_inspection(1)

    assert report == InspectionReport(available=False)
    assert report.had_accident is None


def test_get_inspection_rejects_unexpected_response(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    client = client_factory(
        lambda request: httpx.Response(
            200,
            json={"available": True, "panel_damage": "not a list"},
        )
    )

    with pytest.raises(
        XAPIKoreaError,
        match="Unexpected response from GET /v1/cars/1/inspection",
    ):
        client.get_inspection(1)


def test_api_error_exposes_response_details(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    client = client_factory(
        lambda request: httpx.Response(
            429,
            headers={"Retry-After": "30"},
            json={"error": "Rate limit exceeded"},
        )
    )

    with pytest.raises(APIError, match="Rate limit exceeded") as caught:
        client.me()

    assert caught.value.status_code == 429
    assert caught.value.body == {"error": "Rate limit exceeded"}
    assert caught.value.retry_after == 30


def test_non_json_api_error_preserves_response_body(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    client = client_factory(
        lambda request: httpx.Response(502, text="upstream unavailable")
    )

    with pytest.raises(APIError, match="API request failed with status 502") as caught:
        client.me()

    assert caught.value.status_code == 502
    assert caught.value.body == "upstream unavailable"
    assert caught.value.retry_after is None


@pytest.mark.parametrize(
    ("exception_type", "message"),
    [
        (httpx.ReadTimeout, "Request timed out"),
        (httpx.ConnectError, "Could not connect to XAPI Korea"),
    ],
)
def test_transport_errors_are_wrapped(
    client_factory: Callable[[Handler], XAPIKorea],
    exception_type: type[httpx.RequestError],
    message: str,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise exception_type("transport failed", request=request)

    with pytest.raises(XAPIKoreaError, match=message):
        client_factory(handler).me()


def test_context_manager_closes_http_client(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    client = client_factory(lambda request: httpx.Response(200, json={}))

    with client:
        assert not client._client.is_closed

    assert client._client.is_closed
