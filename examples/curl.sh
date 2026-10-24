#!/usr/bin/env bash
# Quantustik REST API — curl examples. No API key required.
# Educational research only; not investment advice.
set -euo pipefail
BASE="https://quantustik.com/api/v1"

# 1. Health check
curl -s "$BASE/health"

# 2. High-conviction BUY signals across the S&P 500
curl -s "$BASE/signals?direction=BUY&min_conviction=7&limit=5"

# 3. One ticker's signal (entry / stop / take-profit)
curl -s "$BASE/signals/NVDA"

# 4. Multi-horizon quantum forecast
curl -s "$BASE/forecast/AAPL"

# 5. Market regime + fear/greed
curl -s "$BASE/market/regime"
curl -s "$BASE/market/fear-greed"

# 6. With an optional API key for higher quotas (get one at /developers)
# curl -s -H "Authorization: Bearer qk_live_<your_key>" \
#   "$BASE/signals?direction=BUY&limit=25"
