# XAPI Korea Python

Python client for the XAPI Korea API. The current version includes the base
client and the `/v1/me` endpoint.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Usage

```python
import os

from xapikorea import XAPIKorea


with XAPIKorea(os.environ["XAPIKOREA_API_KEY"]) as client:
    account = client.me()

print(account.email, account.plan)
```

Use `base_url` to point the client at a local API:

```python
client = XAPIKorea("enc_test_key", base_url="http://localhost:8000")
```
