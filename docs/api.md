# Quantustik REST API Reference

**Base URL:** `https://quantustik.com/api/v1`
**Machine-readable spec:** [`/api/v1/openapi.json`](https://quantustik.com/api/v1/openapi.json) (OpenAPI 3.1) · [Swagger UI](https://quantustik.com/api/v1/docs) · [ReDoc](https://quantustik.com/api/v1/redoc)

All endpoints are **read-only GET** (except one webhook), return JSON, and require **no
authentication**. Every response carries a `generated_at` timestamp, a `stale` flag, a
`source` citation block, and an `"Educational research; not investment advice."`
disclaimer.

> **Disclaimer:** outputs are for educational research only and are not personalized
> financial advice. See the bottom of this file.

---

## Authentication (optional)

Anonymous access works out of the box: **1,000 requests/hour per IP**. To raise quotas,
create a free API key at <https://quantustik.com/developers> and send it as a bearer token:

```
Authorization: Bearer qk_live_<your_key>
```

Quota headroom is reported on every response via `X-Quota-Limit` and `X-Quota-Remaining`.
Over-quota requests return HTTP `429` with an `upgrade_url` in the body.

## Errors

Uniform envelope:

```json
{ "error": "not_found", "message": "Ticker XYZ is not in the current scan." }
```

| Status | Meaning |
|---|---|
| `400` | Bad request / invalid parameter |
| `402` | Feature requires a paid tier (entitlement) |
| `404` | Ticker or resource not found |
| `429` | Rate limit exceeded — see `upgrade_url` |
| `503` | Data not ready yet (market conditions / fear-greed still computing) |

---

## Endpoints

### Signals

#### `GET /signals`
List all scanned S&P 500 tickers with their current signals.

Signals carry **two facets**, and they answer different questions:

- **verdict** — what the model thinks of the stock: `BUY` \| `WAIT` \| `AVOID` \| `EXIT`.
- **timing** — whether to enter *right now*: `BUY` \| `WATCH` \| `WAIT` \| `AVOID`.

There is no `SELL`. `EXIT` is an opinion on the security, never a short-sell view.

| Query param | Type | Notes |
|---|---|---|
| `min_conviction` | float | 0–10 |
| `verdict` | enum | `BUY` \| `WAIT` \| `AVOID` \| `EXIT` (case-insensitive) |
| `timing` | enum | `BUY` \| `WATCH` \| `WAIT` \| `AVOID` (case-insensitive) |
| `direction` | enum | **Deprecated** alias for `timing`. Use `timing`. |
| `sector` | string | partial name match |
| `limit` | int | 1–100 |
| `cursor` | string | pagination cursor from `next_cursor` |

Returns `{ count, generated_at, results[], next_cursor, source }`. Each result is a
`TickerSignal` (see [schema](#schema-tickersignal)).

#### `GET /signals/{ticker}`
Current signal + quantum snapshot for one ticker. Add `?format=markdown` (or an
`Accept: text/markdown` header) to get a rendered card instead of JSON.

#### `GET /signals/{ticker}/history`
Past signal events for a ticker. `?limit=` 1–100 (default 10). Events include
`new_buy`, `tp_hit`, `stop_hit`, `position_closed`.

#### `GET /signals/track-record`
Backtested / realised win-rate and R-multiple distribution. `?ticker=` optional. Small
samples are flagged `illustrative`.

### Forecast

#### `GET /forecast/{ticker}`
Full multi-horizon quantum forecast. Returns `horizons` keyed `1mo` / `3mo` / `6mo` /
`1y`, each a `QuantumHorizon` with `prob_up`, `growth_pct`, `downside_pct`, `ci_low`,
`ci_high`, `backtest_ci90`, and a `calibration` block. `?format=markdown` supported.

### Market

#### `GET /market`
The whole market picture in one call — `verdict`, 0–100 score, the signal breakdown and
the `action_plan`. Reach for this before stitching `/market/regime`, `/market/indicators`
and `/market/fear-greed` together.

#### `GET /market/indicators`
Every market indicator we compute, in plain English, with its live contribution — grouped
by whether it pushes the verdict up, down or not at all.

#### `GET /market/regime`
Current S&P 500 market conditions (`verdict`, `score`, `computed_at`, `action_plan`). `503`
until computed.

#### `GET /market/fear-greed`
CNN Fear & Greed index (`value` 0–100, `label`, `timestamp`). `503` if unavailable.

#### `GET /market/correlations`
Cross-ticker correlation / entanglement map.

| Query param | Default | Notes |
|---|---|---|
| `horizon` | `3mo` | `1mo` \| `3mo` \| `6mo` \| `1y` |
| `mode` | `forecast` | `forecast` \| `realized` |
| `basis` | `mean` | `mean` \| `ensemble` |
| `top_n` | — | 2–100 |
| `ticker` | — | single-ticker view (most entangled / most divergent) |

### Earnings & filings

| Endpoint | Returns |
|---|---|
| `GET /earnings/{ticker}` | next/last earnings, `days_until_next`, `earnings_risk_note` |
| `GET /insider/{ticker}` | SEC Form 4 pulse: transactions, `cluster_buy_active`, `accession_url` |
| `GET /insider/screener` | S&P 500 top-100 notable insider activity |
| `GET /insider/feed` | paginated insider feed (`page`, `per_page`, `window`, `type`) |
| `GET /filings/digest` | site-wide recent 8-K feed (AI-summarised, Item-grounded) |
| `GET /filings/digest/{ticker}` | per-ticker 8-K digest |
| `GET /filings/digest/10-k` | recent 10-K feed |
| `GET /filings/8-k/feed` | paginated durable 8-K store |
| `GET /filings/language-diff/{ticker}` | "Lazy Prices" TF-IDF diff (`?form=10-K\|10-Q`) |
| `GET /filings/feed` | every stored SEC form in one dated feed (`page`, `per_page`, `form`, `ticker`, `event_type`) |
| `GET /institutional/{ticker}` | 13F whale summary + 13D/G activist alerts |
| `GET /institutional/feed` | dated 13F holdings feed (`page`, `per_page`, `window`, `ticker`) |

### Per-ticker explainers

| Endpoint | Returns |
|---|---|
| `GET /ticker/{ticker}/indicators` | everything computed about one stock in plain English, each with its contribution |
| `GET /ticker/{ticker}/too-late` | "am I too late to buy this?" — answered with a price in it |

### Utility

| Endpoint | Returns |
|---|---|
| `GET /health` | `{ status }` — always 200, no auth |
| `POST /webhook/tradingview` | body `{ ticker, message }` → queues a background rescan |

---

## Schema: `TickerSignal`

```jsonc
{
  "ticker": "NVDA",
  "company_name": "NVIDIA Corporation",
  "sector": "Information Technology",
  "generated_at": "2026-07-09T09:14:33+00:00",
  "stale": false,
  "calibration_score": 90.9,
  "regime_conditioned": true,
  "signal": {
    "verdict": "BUY",                       // BUY | WAIT | AVOID | EXIT
    "conviction": 8.2,                      // 0-10
    "entry_price": 118.40,
    "stop_loss": 111.20,
    "take_profit": [129.00, 141.50, 155.00],// TP1 / TP2 / TP3 ladder
    "position_size_pct": 4.0,
    "rr_ratio": 2.8,
    "invalidation_note": "Close below $111 invalidates the setup"
  },
  "quantum": {
    "prob_up": 0.72,
    "growth_pct": 12.8,
    "downside_pct": -5.9,
    "ci_low": 109.50,
    "ci_high": 133.80,
    "backtest_ci90": 90.9,
    "calibration": {
      "ci90_empirical_coverage": 90.9,
      "calibration_status": "well_calibrated",
      "note": "…"
    }
  }
}
```

The authoritative, always-current schema for every endpoint is the OpenAPI document at
<https://quantustik.com/api/v1/openapi.json> (mirrored in this repo as
[`../openapi.json`](../openapi.json)).

---

## Disclaimer

All data, signals, and forecasts are for **educational research purposes only**. They are
not personalized financial advice, not a solicitation to buy or sell any security, and not
a guarantee of future performance. Past model calibration does not guarantee future
accuracy. Always do your own research and consult a qualified financial professional
before investing.
