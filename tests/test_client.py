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
    CountResponse,
    FiltersResponse,
    InspectionReport,
    InsuranceHistory,
    LeaseRentTerms,
    MakeModelsResponse,
    PanelDamage,
    SearchResponse,
    TrimChoice,
    TrimsResponse,
    Warranty,
    XAPIKorea,
    XAPIKoreaError,
    __version__,
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
        assert request.headers["User-Agent"] == f"xapikorea-python/{__version__}"
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
                "source": "encar",
                "currency": "krw",
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
                listing_url="https://fem.encar.com/cars/detail/41750571",
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
        assert request.url.params == httpx.QueryParams({"lang": "ko", "source": "encar"})
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
        assert request.url.params == httpx.QueryParams({"lang": "ko", "source": "encar"})
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


def test_multisource_search_preserves_identity_and_terms(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    filters = {
        "source": "all", "brand": "BMW,Audi", "currency": "eur",
        "price_min": 0, "price_max": 20_000, "mileage_min": 0,
        "mileage_max": 80_000, "sale_type": "lease", "color": "white,black",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params == httpx.QueryParams(
            {**filters, "page": 1, "limit": 20, "lang": "en"}
        )
        return httpx.Response(200, json={
            "total_count": 2, "page": 1, "limit": 20,
            "results": [
                {"id": 123, "manufacturer": "BMW", "model": "5 Series",
                 "source": "kbchachacha", "listing_url": "https://example.test/kb/123",
                 "encar_url": None, "price_krw": None, "badge": None,
                 "sale_type": "lease", "lease_rent": {"monthly_fee_krw": 450_000}},
                {"id": 123, "manufacturer": "BMW", "model": "5 Series",
                 "source": "encar", "encar_url": "https://example.test/encar/123",
                 "sales_status": "under_contract", "listing_status": None},
            ],
            "next_page": 2, "sources": ["encar", "kbchachacha"], "partial": False,
            "source_errors": {},
        })

    result = client_factory(handler).search(**filters)

    assert [(car.source, car.id) for car in result.results] == [
        ("kbchachacha", 123), ("encar", 123)
    ]
    assert result.results[0].price_krw is None
    assert result.results[0].encar_url is None
    assert result.results[0].listing_url == "https://example.test/kb/123"
    assert result.results[0].lease_rent == LeaseRentTerms(monthly_fee_krw=450_000)
    assert result.results[1].listing_url == "https://example.test/encar/123"
    assert result.results[1].sales_status == "under_contract"
    assert result.next_page == 2
    assert result.sources == ("encar", "kbchachacha")
    assert result.partial is False
    assert result.source_errors == {}


def test_count_sends_supported_filters_and_preserves_zero_count(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    filters = {
        "source": "encar", "brand": "kia", "model": "sportage",
        "year_from": 2022, "year_to": 2026, "price_min": 0, "price_max": 20_000,
        "currency": "eur", "mileage_min": 0, "mileage_max": 90_000,
        "fuel_type": "gasoline", "transmission": "auto", "car_type": "Y",
        "is_accident_free": False, "sale_type": "normal", "color": "white",
        "trim": "시그니처", "generation": "스포티지 5세대", "badge_group": "가솔린 2WD",
        "badge": "가솔린 1.6 터보 2WD",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/search/count"
        assert request.url.params == httpx.QueryParams(filters)
        return httpx.Response(200, json={"count": 0})

    response = client_factory(handler).count(**filters)
    assert response == CountResponse(count=0)
    assert CountResponse.from_dict({"count": 5}) == CountResponse(count=5)


@pytest.mark.parametrize("method", ["search", "count"])
@pytest.mark.parametrize("failed_source", ["encar", "kbchachacha"])
def test_partial_results_preserve_failed_source(
    client_factory: Callable[[Handler], XAPIKorea], method: str, failed_source: str,
) -> None:
    sources = [source for source in ("encar", "kbchachacha") if source != failed_source]
    payload = {
        "sources": sources, "partial": True,
        "source_errors": {failed_source: "upstream_provider_unavailable"},
    }
    if method == "search":
        payload.update({"total_count": 0, "page": 1, "limit": 20, "results": []})
    else:
        payload["count"] = 0

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["source"] == "all"
        return httpx.Response(200, json=payload)

    result = getattr(client_factory(handler), method)(source="all")
    assert result.sources == tuple(sources)
    assert result.partial is True
    assert result.source_errors == {failed_source: "upstream_provider_unavailable"}


def test_trim_discovery_values_can_be_passed_to_search(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    generation = "스포티지 5세대"
    badge_group = "가솔린 2WD"
    badge = "가솔린 1.6 터보 2WD"
    trim = "시그니처"

    def handler(request: httpx.Request) -> httpx.Response:
        params = request.url.params
        assert params["generation"] == generation
        assert params["badge_group"] == badge_group
        assert params["badge"] == badge
        if request.url.path == "/v1/trims":
            assert "trim" not in params
            return httpx.Response(200, json={
                "brand": "기아", "model": "스포티지", "generation": generation,
                "badge_group": badge_group, "badge": badge,
                "trims": [{"value": trim, "label": "Signature", "count": 12}],
            })
        assert request.url.path == "/v1/search"
        assert params["trim"] == trim
        return httpx.Response(200, json={
            "total_count": 0, "page": 1, "limit": 20, "results": [],
        })

    client = client_factory(handler)
    choices = client.get_trims(
        brand="kia", model="sportage", generation=generation,
        badge_group=badge_group, badge=badge,
    )
    assert choices == TrimsResponse(
        brand="기아", model="스포티지", generation=generation, badge_group=badge_group,
        badge=badge, trims=(TrimChoice(value=trim, label="Signature", count=12),),
    )
    result = client.search(
        brand="kia", model="sportage", generation=choices.generation,
        badge_group=choices.badge_group, badge=choices.badge, trim=choices.trims[0].value,
    )
    assert result.next_page is None


@pytest.mark.parametrize("status", ["advertised", "sold", "waiting", None])
def test_car_preserves_listing_status_independently_of_reserved_flag(status: str | None) -> None:
    car = Car.from_dict({
        "id": 1, "manufacturer": "Kia", "model": "Sportage",
        "sales_status": "under_contract", "listing_status": status, "is_reserved": False,
    })
    assert car.sales_status == "under_contract"
    assert car.listing_status == status
    assert car.is_reserved is False


@pytest.mark.parametrize("method", ["get_car", "get_images", "get_inspection", "get_insurance", "get_similar"])
def test_vehicle_methods_send_selected_marketplace(
    client_factory: Callable[[Handler], XAPIKorea], method: str,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["source"] == "kbchachacha"
        assert request.url.path.startswith("/v1/cars/123")
        if method in ("get_inspection", "get_insurance", "get_similar"):
            return httpx.Response(501, json={"error": "KB reports are not integrated"})
        if method == "get_images":
            assert "lang" not in request.url.params
            return httpx.Response(200, json=["https://example.test/kb.jpg"])
        return httpx.Response(200, json={
            "id": 123, "source": "kbchachacha", "manufacturer": "Kia", "model": "K5",
            "listing_url": "https://example.test/kb/123", "encar_url": None,
        })

    call = getattr(client_factory(handler), method)
    if method in ("get_inspection", "get_insurance", "get_similar"):
        with pytest.raises(APIError, match="not integrated") as caught:
            call(123, source="kbchachacha")
        assert caught.value.status_code == 501
    elif method == "get_car":
        car = call(123, source="kbchachacha")
        assert car.source == "kbchachacha"
        assert car.listing_url == "https://example.test/kb/123"
        assert car.encar_url is None
    else:
        assert call(123, source="kbchachacha") == ("https://example.test/kb.jpg",)


@pytest.mark.parametrize("available", [True, False])
def test_insurance_preserves_unknown_history_and_real_zero_claims(
    client_factory: Callable[[Handler], XAPIKorea], available: bool,
) -> None:
    payload = {"available": available}
    if available:
        payload.update({
            "accident_report_url": "https://example.test/insurance", "had_insurance_accident": False,
            "accident_count": 0, "accident_cost_krw": 0, "other_accident_count": 1,
            "other_accident_cost_krw": 750_000, "owner_change_count": 2,
            "was_flooded": False, "was_total_loss": False, "was_stolen": False,
            "used_as_rental": True, "used_as_commercial": False, "used_as_government": False,
        })

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/cars/1/insurance"
        assert request.url.params == httpx.QueryParams({"source": "encar"})
        return httpx.Response(200, json=payload)

    report = client_factory(handler).get_insurance(1)
    assert report == InsuranceHistory(**payload)
    assert report.accident_count == (0 if available else None)
    assert report.had_insurance_accident is (False if available else None)


def test_discovery_and_similar_endpoints(
    client_factory: Callable[[Handler], XAPIKorea],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-API-Key"] == "enc_test_key"
        assert request.url.params["source"] == "encar"
        path = request.url.path
        if path == "/v1/filters":
            return httpx.Response(200, json={
                "manufacturers": ["Kia"], "fuel_types": ["Gasoline"],
                "transmissions": ["Automatic"], "body_styles": ["suv"],
                "sort_options": ["ModifiedDate"], "colors": ["white"], "trims": ["signature"],
            })
        if path == "/v1/makes":
            return httpx.Response(200, json=["Kia"])
        if path == "/v1/makes/르노 코리아/models":
            assert b"%EB" in request.url.raw_path
            assert b"%20" in request.url.raw_path
            return httpx.Response(200, json={"make": "르노 코리아", "models": ["QM6"]})
        assert path == "/v1/cars/1/similar"
        assert request.url.params == httpx.QueryParams({"source": "encar", "limit": 3, "lang": "ko"})
        return httpx.Response(200, json=[{"id": 2, "manufacturer": "Kia", "model": "K5"}])

    client = client_factory(handler)
    assert client.get_filters() == FiltersResponse(
        manufacturers=("Kia",), fuel_types=("Gasoline",), transmissions=("Automatic",),
        body_styles=("suv",), sort_options=("ModifiedDate",), colors=("white",), trims=("signature",),
    )
    assert client.get_makes() == ("Kia",)
    assert client.get_models("르노 코리아") == MakeModelsResponse(make="르노 코리아", models=("QM6",))
    assert client.get_similar(1, limit=3, lang="ko") == (CarSummary(id=2, manufacturer="Kia", model="K5"),)


@pytest.mark.parametrize(
    ("method", "args", "kwargs", "payload"),
    [
        ("get_insurance", (1,), {}, []),
        ("get_images", (1,), {}, "not a list"),
        ("get_images", (1,), {}, [123]),
        ("get_similar", (1,), {}, [{}]),
        ("get_similar", (1,), {}, [None]),
        ("get_filters", (), {}, {"manufacturers": "not a list"}),
        ("get_makes", (), {}, {}),
        ("get_models", ("Kia",), {}, {"make": "Kia", "models": [None]}),
        ("get_trims", (), {"brand": "kia", "model": "sportage"},
         {"brand": "kia", "model": "sportage", "trims": [None]}),
        ("count", (), {}, {"count": 3, "source_errors": []}),
        ("search", (), {}, {"total_count": 1, "page": 1, "limit": 20, "results": [None]}),
        ("search", (), {}, {"total_count": 0, "page": 1, "limit": 20, "results": [], "sources": None}),
        ("search", (), {}, {"total_count": 1, "page": 1, "limit": 20, "results": [
            {"id": 1, "manufacturer": "Kia", "model": "K5", "lease_rent": []}]}),
    ],
)
def test_new_endpoints_wrap_malformed_responses(
    client_factory: Callable[[Handler], XAPIKorea], method: str,
    args: tuple, kwargs: dict, payload: object,
) -> None:
    client = client_factory(lambda request: httpx.Response(200, json=payload))
    with pytest.raises(XAPIKoreaError, match="Unexpected response from GET /v1/"):
        getattr(client, method)(*args, **kwargs)
