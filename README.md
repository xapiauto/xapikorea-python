# XAPI Korea Python

Python client for the XAPI Korea API. The current version supports account
information, vehicle search, vehicle details and inspection history.

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

Search the current inventory:

```python
with XAPIKorea(os.environ["XAPIKOREA_API_KEY"]) as client:
    results = client.search(
        brand="hyundai",
        year_from=2022,
        price_max=30_000_000,
        limit=5,
    )

for car in results.results:
    print(car.manufacturer, car.model, car.price_krw)
```

Retrieve full vehicle details and photos:

```python
with XAPIKorea(os.environ["XAPIKOREA_API_KEY"]) as client:
    car = client.get_car(42662587)

print(car.manufacturer, car.model, car.price_krw)
print(*car.photos, sep="\n")
```

Retrieve the vehicle's inspection report:

```python
with XAPIKorea(os.environ["XAPIKOREA_API_KEY"]) as client:
    inspection = client.get_inspection(42662587)

if not inspection.available:
    print("No inspection sheet is available")
elif inspection.had_accident:
    print("The inspection sheet reports accident history")
else:
    print("No accident history reported on the inspection sheet")
```

Use `base_url` to point the client at a local API:

```python
client = XAPIKorea("enc_test_key", base_url="http://localhost:8000")
```

## License

This project is licensed under the [MIT License](https://github.com/xapiauto/xapikorea-python/blob/main/LICENSE).

## Support

For bugs and feature requests, [open a GitHub issue](https://github.com/xapiauto/xapikorea-python/issues).
