# Quantustik

[![MCP Badge](https://lobehub.com/badge/mcp/quantustik-quantustik)](https://lobehub.com/mcp/quantustik-quantustik)

**Quantustik is a market data service for the S&P 500 — prices, fundamentals, SEC filings, insider and Congress trades, macro indicators and market conditions — for investors and AI agents, through a dashboard, a REST API and an MCP server.**

Every value carries its source and as-of date. Quantustik publishes measured data only, with no predictions and no recommendations.

- **Website:** <https://quantustik.com>
- **REST API base:** `https://quantustik.com/api/v1` · [OpenAPI spec](https://quantustik.com/api/v1/openapi.json) · [Swagger UI](https://quantustik.com/api/v1/docs)
- **Hosted MCP server:** `https://quantustik.com/mcp` (streamable-HTTP, no key required)
- **Stdio proxy (npm):** [quantustik/mcp-server](https://github.com/quantustik/mcp-server)
- **Free API key (optional):** <https://quantustik.com/developers>
- **For LLMs:** [llms.txt](https://quantustik.com/llms.txt)

> **Market data only — not investment advice.** Nothing here is a recommendation to buy or sell any security.

This repository is the public developer and agent documentation: manifests and client examples. The live service is canonical; `openapi.json`, `server.json`, `llms.txt` and `.well-known/` are mirrored from it.

## What you can get

| Data | REST endpoint | MCP tool |
|---|---|---|
| CNN Fear & Greed index (0-100) | `GET /api/v1/market/fear-greed` | `get_fear_greed` |
| Next and last earnings dates for a ticker | `GET /api/v1/earnings/{ticker}` | `get_earnings_calendar` |
| SEC Form 4 insider activity, per ticker or a feed | `GET /api/v1/insider/{ticker}`, `GET /api/v1/insider/feed` | `get_insider_pulse` |
| SEC 8-K event digest, per ticker or a recent feed | `GET /api/v1/filings/digest/{ticker}`, `GET /api/v1/filings/digest` | `get_filings_digest` |
| What changed in the prose between a ticker's two most recent 10-K or 10-Q filings | `GET /api/v1/filings/language-diff/{ticker}` | `get_filing_language_diff` |
| 13F institutional ownership changes and SC 13D/G activist filings | `GET /api/v1/institutional/{ticker}` | `get_institutional_activity` |
| Discover all tools and resources | none | `list_capabilities` |
| Onboarding: quotas and how a free key raises them | none | `get_started` |

The full REST surface is in the [OpenAPI spec](https://quantustik.com/api/v1/openapi.json).

## Quickstart: REST API (no key required)

Anonymous callers get a per-IP hourly quota with no signup.

```bash
curl "https://quantustik.com/api/v1/market/fear-greed"
curl "https://quantustik.com/api/v1/earnings/AAPL"
curl "https://quantustik.com/api/v1/insider/AAPL"
curl "https://quantustik.com/api/v1/filings/digest/AAPL"
```

```python
import urllib.request, json

with urllib.request.urlopen("https://quantustik.com/api/v1/market/fear-greed") as r:
    data = json.loads(r.read())

print(data["current"]["score"], data["current"]["rating"], data["timestamp"])
```

An optional free API key raises quotas. Send it as a bearer token:

```bash
curl -H "Authorization: Bearer qk_live_<your_key>" "https://quantustik.com/api/v1/insider/feed?limit=25"
```

Get a key at <https://quantustik.com/developers>.

## Quickstart: MCP server (for AI agents)

The hosted server at `https://quantustik.com/mcp` uses streamable-HTTP. No install, no signup, no key; an optional bearer key raises quotas.

Claude Code:

```bash
claude mcp add --transport http quantustik https://quantustik.com/mcp
```

Cursor (`~/.cursor/mcp.json`):

```jsonc
{
  "mcpServers": {
    "quantustik": { "url": "https://quantustik.com/mcp" }
  }
}
```

Clients that only support local stdio servers (Claude Desktop, Windsurf and others) can use the npm proxy in [quantustik/mcp-server](https://github.com/quantustik/mcp-server). Start with the `get_started` or `list_capabilities` tool.

## Discovery manifests

| File | Live URL | Purpose |
|---|---|---|
| [`openapi.json`](openapi.json) | `/api/v1/openapi.json` | OpenAPI spec for the REST API |
| [`server.json`](server.json) | none | MCP registry manifest |
| [`.well-known/mcp.json`](.well-known/mcp.json) | `/.well-known/mcp.json` | MCP endpoint discovery |
| [`llms.txt`](llms.txt) | `/llms.txt` | LLM-oriented site index ([llmstxt.org](https://llmstxt.org)) |

## Disclaimer

Market data returned by Quantustik is for educational and research purposes only. It is not investment advice and not a recommendation to buy or sell any security. Consult a qualified financial professional before making investment decisions.

## License

Documentation and example code in this repository are released under the [MIT License](LICENSE). The license covers only this repository and grants no rights to the Quantustik service, which remains proprietary.
