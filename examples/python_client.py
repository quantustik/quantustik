"""Quantustik REST API — minimal Python client (stdlib only, no dependencies).

Educational research only; not investment advice.
Get an optional free API key for higher quotas at https://quantustik.com/developers
"""

import json
import os
import urllib.request

BASE = "https://quantustik.com/api/v1"
API_KEY = os.environ.get("QUANTUSTIK_API_KEY")  # optional


def get(path: str, **params) -> dict:
    qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
    url = f"{BASE}{path}" + (f"?{qs}" if qs else "")
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


if __name__ == "__main__":
    # High-conviction BUY signals
    data = get("/signals", direction="BUY", min_conviction=7, limit=5)
    print(f"generated_at={data.get('generated_at')}")
    for item in data.get("results", []):
        sig = item.get("signal") or {}
        print(
            f"{item['ticker']:6} {sig.get('verdict'):5} "
            f"conviction={sig.get('conviction')} "
            f"entry={sig.get('entry_price')} stop={sig.get('stop_loss')} "
            f"TP={sig.get('take_profit')}"
        )

    # One ticker's full forecast
    fc = get("/forecast/NVDA")
    print("\nNVDA forecast horizons:", list((fc.get("horizons") or {}).keys()))
