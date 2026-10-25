# XAPI Korea Python SDK

[![PyPI](https://img.shields.io/pypi/v/xapikorea)](https://pypi.org/project/xapikorea/)

Python SDK for XAPI Korea. Search used-car listings from **Encar and KB ChaChaCha**,
retrieve prices, specifications and photos, and load available Encar inspection
reports and insurance history. Supported fields can be returned in English.

> XAPI Korea is independent and unofficial. It is not affiliated with or endorsed by Encar or KB ChaChaCha.

- API docs: https://docs.xapikorea.com
- Free API key (no credit card): https://xapikorea.com/signup

## Installation

Python 3.10 or newer is required.

```bash
python -m pip install xapikorea
```

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

For development, install the test and build tools:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m build
```

## Usage

```python
import os

from xapikorea import XAPIKorea


with XAPIKorea(os.environ["XAPIKOREA_API_KEY"]) as client:
    account = client.me()

print(account.email, account.plan)
```

Search either marketplace or both, with price bounds in KRW (default) or EUR:

```python
with XAPIKorea(os.environ["XAPIKOREA_API_KEY"]) as client:
    results = client.search(
        source="all",
        brand="hyundai",
        year_from=2022,
        price_max=20_000,
        currency="eur",
        mileage_max=80_000,
        sale_type="normal",
        limit=5,
    )

for car in results.results:
    print(car.source, car.id, car.model, car.price_eur, car.listing_url)

if results.partial:
    print("Incomplete inventory:", results.source_errors)
```

`source` defaults to `encar`; use `kbchachacha` for KB only. Always store a
listing's `source` and `id` together and pass both when retrieving it:

```python
with XAPIKorea(os.environ["XAPIKOREA_API_KEY"]) as client:
    results = client.search(source="all", sale_type="normal", limit=1)
    if results.results:
        listing = results.results[0]
        car = client.get_car(listing.id, source=listing.source)
        print(car.manufacturer, car.model, car.listing_url)
        print(*car.photos, sep="\n")
        images = client.get_images(listing.id, source=listing.source)
```

`listing_url` links to either marketplace; `encar_url` remains available for
Encar compatibility. Prices and other listing fields may be `None`. Search
results include `sale_type` and `lease_rent`: lease and rent amounts describe a
contract transfer and must not be presented as a purchase price.

Discover supported inputs and vehicle-specific Encar variants:

```python
with XAPIKorea(os.environ["XAPIKOREA_API_KEY"]) as client:
    filters = client.get_filters(source="encar")
    makes = client.get_makes(source="encar")
    models = client.get_models("Kia", source="encar")
    choices = client.get_trims(brand="kia", model="sportage")
    if choices.generations:
        generation = choices.generations[0]
        print(generation.label, generation.count)
        variants = client.get_trims(
            brand="kia", model="sportage", generation=generation.value,
        )
```

Trim discovery progresses through `generation`, `badge_group`, `badge`, then
`trim`. Display each choice's `label` and pass its exact `value` back to
`get_trims()` or `search()`. The filters catalog's `trims` are common aliases,
not a guarantee that a particular model has that trim.

Count matching listings without loading a result page:

```python
with XAPIKorea(os.environ["XAPIKOREA_API_KEY"]) as client:
    count = client.count(source="all", brand="kia", sale_type="normal")
    print(count.count, count.partial, count.source_errors)
```

Retrieve available Encar reports after checking the detail flags:

```python
with XAPIKorea(os.environ["XAPIKOREA_API_KEY"]) as client:
    car = client.get_car(42662587, source="encar")
    if car.inspection_available:
        inspection = client.get_inspection(car.id, source=car.source)
        print(inspection.available, inspection.had_accident)
    if car.insurance_available:
        insurance = client.get_insurance(car.id, source=car.source)
        print(insurance.available, insurance.had_insurance_accident)
    similar = client.get_similar(car.id, source=car.source, limit=5)
```

Missing reports mean unknown condition. `is_accident_free` filters Encar's
seller-declared inspection classification; insurance history is separate.
`sales_status="under_contract"` identifies Encar's contract status.
`listing_status` can be `advertised`, `sold`, `waiting`, or `None`.
`advertised` and a missing status do not confirm availability to buy.
The legacy `is_reserved` flag is separate from contract status.

## Methods

| Method | REST endpoint |
| --- | --- |
| `me()` | `/v1/me` |
| `search(...)` | `/v1/search` |
| `count(...)` | `/v1/search/count` |
| `get_filters(source=...)` | `/v1/filters` |
| `get_makes(source=...)` | `/v1/makes` |
| `get_models(make, source=...)` | `/v1/makes/{make}/models` |
| `get_trims(brand=..., model=..., ...)` | `/v1/trims` |
| `get_car(id, source=..., lang=...)` | `/v1/cars/{id}` |
| `get_images(id, source=...)` | `/v1/cars/{id}/images` |
| `get_inspection(id, source=..., lang=...)` | `/v1/cars/{id}/inspection` |
| `get_insurance(id, source=...)` | `/v1/cars/{id}/insurance` |
| `get_similar(id, source=..., limit=..., lang=...)` | `/v1/cars/{id}/similar` |

Responses use dataclasses; arrays become tuples. `search()` supports brand,
model, year and price bounds, `currency`, mileage bounds, fuel, transmission,
body style, domestic/import `car_type`, `is_accident_free`, `sale_type`, color,
trim, generation, badge group, badge, sort, pagination, language and source.
`count()` accepts the same inventory filters except `body_style`; it has no
sort, pagination or language parameters. Comma-separated supported filters,
such as `brand="BMW,Audi"`, use OR within a field.

## Marketplace behavior and pagination

- `search`, `count`, `get_filters` and `get_makes` accept `source="all"`.
  Vehicle endpoints and model discovery accept one marketplace at a time.
- KB-only and combined searches require a brand when filtering by model.
  They reject `trim`, `generation`, `badge_group`, `badge` and
  `is_accident_free` (including `False`). Use one sale type, `normal` or
  `lease`; `rent` is unsupported. Discover colors for the chosen source.
- Trim discovery supports Encar only. KB inspection, insurance and similar
  listings currently return HTTP `501`.
- Follow `next_page` until it is `None`, keeping filters, source, sort and
  limit unchanged. REST pages support up to 50 listings. Encar has a
  12,450-result depth limit; KB-only and combined searches default to a
  500-result depth limit. Narrow filters to reach more inventory.
- Combined `ModifiedDate` ordering alternates sources in their own newest-first
  order. Numeric sorts merge sorted prefixes. Counts represent marketplace
  listings; a physical car listed on both marketplaces can appear twice.
- Check `partial`, `sources` and `source_errors` on searches and counts. A
  failed source is missing inventory, and the count covers successful sources.

## Configuration and errors

Use `base_url` to point the client at a local API:

```python
client = XAPIKorea("enc_test_key", base_url="http://localhost:8000")
```

Use `timeout` to change the default 30-second timeout. Call `close()` when
finished, or use the client as a context manager. Requests default to English
where supported; pass `lang="ko"` for Korean.

HTTP errors raise `APIError`, exposing `status_code`, `body` and an integer
`retry_after` when supplied. Connection errors, timeouts and malformed responses
raise `XAPIKoreaError`; `APIError` is a subclass of it.

## License

This project is licensed under the [MIT License](https://github.com/xapiauto/xapikorea-python/blob/main/LICENSE).

## Support

For bugs and feature requests, [open a GitHub issue](https://github.com/xapiauto/xapikorea-python/issues).
