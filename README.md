# XAPI Korea Python

Python client for the XAPI Korea API. The current version includes the base
client and the `/v1/me` endpoint.

## Setup

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

Use `base_url` to point the client at a local API:

```python
client = XAPIKorea("enc_test_key", base_url="http://localhost:8000")
```
