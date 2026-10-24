# Quantustik MCP Server

Quantustik ships a **hosted [Model Context Protocol](https://modelcontextprotocol.io)
server** so LLM agents can pull S&P 500 signals, forecasts, trade plans, market conditions and
SEC filing intelligence as native tools.

- **Endpoint:** `https://quantustik.com/mcp`
- **Transport:** `streamable-http`
- **Auth:** none required (anonymous, 1,000 requests/hour/IP). Optional bearer API key for
  higher quotas — free at <https://quantustik.com/developers>.
- **Discovery:** [`/.well-known/mcp.json`](https://quantustik.com/.well-known/mcp.json) ·
  registry manifest [`server.json`](../server.json)

> **Disclaimer:** all outputs are educational research only, not investment advice.

---

## Connect

Every client below talks to the same endpoint — `https://quantustik.com/mcp`,
streamable-HTTP, no auth required. Only the config file/UI differs by client. MCP
client config formats change often; each section cites the official doc it was
verified against (2026-07).

### Claude Code

CLI (recommended):

```bash
claude mcp add --transport http quantustik https://quantustik.com/mcp
```

Or add to a project's `.mcp.json` (checked into version control) or your user-scoped
`~/.claude.json`:

```jsonc
{
  "mcpServers": {
    "quantustik": {
      "type": "http",
      "url": "https://quantustik.com/mcp"
    }
  }
}
```

Source: [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)

### Claude Desktop / claude.ai (Custom Connectors)

Claude Desktop's local `claude_desktop_config.json` only accepts **local/stdio**
servers — it does not parse a `type`/`url` remote-server entry. To connect a remote
server like Quantustik, add it as a **Custom Connector** instead:

1. In claude.ai: **Settings → Connectors** (or **Customize → Connectors**).
2. **Add custom connector** → enter `https://quantustik.com/mcp`.
3. **Add**. No OAuth/advanced settings needed — the server is anonymous.
4. Enable it per-conversation via the **+** button → **Connectors**.

Desktop shares the same account-level connectors, so a connector added on claude.ai
is available in Desktop too.

Source: [support.claude.com — Getting started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp)

### ChatGPT (custom connector, Developer Mode)

Custom MCP connectors in ChatGPT live behind **Developer Mode** (Plus/Pro/Team/
Enterprise/Edu plans):

1. **Settings → Connectors → Advanced → Developer mode** — turn it on.
2. **Settings → Connectors → Create** (or the **+** in a chat's Connectors menu) →
   point the new app at `https://quantustik.com/mcp`.
3. No authentication field is required.

Source: [developers.openai.com/api/docs/mcp](https://developers.openai.com/api/docs/mcp) ·
[help.openai.com — Developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt)

### Cursor

Add to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project):

```jsonc
{
  "mcpServers": {
    "quantustik": {
      "url": "https://quantustik.com/mcp"
    }
  }
}
```

Source: [cursor.com/docs/context/mcp](https://cursor.com/docs/context/mcp)

### VS Code (GitHub Copilot Chat)

Add to `.vscode/mcp.json`:

```jsonc
{
  "servers": {
    "quantustik": {
      "type": "http",
      "url": "https://quantustik.com/mcp"
    }
  }
}
```

Note the top-level key is `servers`, not `mcpServers`, in VS Code's schema.

Source: [code.visualstudio.com/docs/copilot/chat/mcp-servers](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)

### Cline

Add to `cline_mcp_settings.json`:

```jsonc
{
  "mcpServers": {
    "quantustik": {
      "type": "streamableHttp",
      "url": "https://quantustik.com/mcp",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Source: [docs.cline.bot/mcp/configuring-mcp-servers](https://docs.cline.bot/mcp/configuring-mcp-servers)

### LobeHub

```jsonc
{
  "mcpServers": {
    "quantustik": {
      "url": "https://quantustik.com/mcp",
      "type": "http"
    }
  }
}
```

Or install straight from the
[LobeHub MCP marketplace listing](https://lobehub.com/mcp/quantustik-quantustik).

Source: [lobehub.com/docs/usage/community/mcp-market](https://lobehub.com/docs/usage/community/mcp-market)

### With an API key (higher quotas)

Any client above that uses an `mcpServers`/`servers` JSON entry accepts a headers
field, e.g.:

```jsonc
{
  "mcpServers": {
    "quantustik": {
      "type": "http",
      "url": "https://quantustik.com/mcp",
      "headers": { "Authorization": "Bearer qk_live_<your_key>" }
    }
  }
}
```

Get a free key at <https://quantustik.com/developers>.

Once connected, tell the agent what you want, e.g.:

> *"Check market conditions, then use quantustik's top_opportunities to list only the
> asymmetric swing setups right now, with entry, stop and take-profit for each."*

A good first call is **`get_started`** (onboarding + live quotas) or **`list_capabilities`**
(enumerate everything).

---

## Tools (24)

| Tool | Purpose |
|---|---|
| `get_started` | Onboarding — quotas, optional free key, auth header. |
| `get_signal` | BUY/WAIT/AVOID/EXIT verdict + entry / stop / TP ladder + conviction for one ticker. |
| `get_trade_plan` | Execution-ready plan; `actionable=false` unless it's a ≥2:1 BUY/EXIT. |
| `explain_signal` | Factor attribution: `dominant_factor` + `dissenting_factors`. Two-sided. |
| `get_ticker_indicators` | Everything computed about one stock in plain English, grouped by what it does to the verdict — including every risk check that can veto a BUY. |
| `get_signals_batch` | Signals (or plans) for a whole watchlist in one call, max 25. |
| `get_forecast` | 1mo/3mo/6mo/1y forecasts + calibration. Optional `horizon`. |
| `get_market_overview` | The whole dashboard market picture in one call. Reach for this before stitching the three tools below. |
| `get_market_regime` | Buying conditions 0–100 (Strong Buy / Buy / Neutral / Caution / Strong Avoid) **plus** a separate froth check reported as two legs. Gates signal generation. |
| `get_market_indicators` | Every market indicator in plain English, grouped by whether it pushes the verdict up, down or not at all. |
| `get_fear_greed` | CNN Fear & Greed 0–100. |
| `get_signal_history` | new_buy / tp_hit / stop_hit / position_closed events. |
| `get_track_record` | Realised win-rate + R-multiple distribution (losses included). |
| `get_earnings_calendar` | Next/last earnings + `earnings_risk_note`. |
| `top_opportunities` | Tiny risk-vetted shortlist (market permits longs, conviction ≥ 7.5, R:R ≥ 2:1). Empty is valid. |
| `scan_universe` | Filtered + paginated S&P 500 scan (conviction / direction / sector). |
| `get_correlation_map` | Cross-ticker entanglement matrix (diversification / pairs). |
| `get_insider_pulse` | SEC Form 4 activity — role, size vs history, cluster-buy detection. |
| `get_filings_digest` | SEC 8-K event digest, Item-grounded + one-line AI summary. |
| `get_filing_language_diff` | "Lazy Prices" 10-K/10-Q language diff (TF-IDF). |
| `get_institutional_activity` | 13F whale + 13D/G activist activity, each linked to its filing. |
| `search` | Search for S&P 500 tickers by symbol or company name. Paired with `fetch`. |
| `fetch` | Full signal + forecast writeup for one ticker, by `search` id or a bare ticker. Paired with `search`. |
| `list_capabilities` | Discover all tools, prompts and resources. |

`get_signal`, `get_trade_plan` and `top_opportunities` also emit typed `structuredContent`
cards. SEC tools (`get_insider_pulse`, `get_filings_digest`, `get_filing_language_diff`,
`get_institutional_activity`) are **information-surfacing only** and do not feed the
model's conviction logic; every result links to the source filing. `search` + `fetch`
implement the two-tool convention ChatGPT connectors and deep-research clients expect
from an MCP server, in addition to the richer per-domain tools above.

## Prompts (3)

| Prompt | Args | Purpose |
|---|---|---|
| `find_swing_trade` | `min_conviction?`, `sector?` | Guided market → scan → trade-plan workflow. |
| `risk_check` | `ticker`, `position_size?` | Explicit max-loss, exit ladder, invalidation. |
| `market_briefing` | — | Market-conditions + fear/greed briefing with suppressed-risk note. |

## Resources (4)

| URI | Contents |
|---|---|
| `quantustik://methodology` | How the Schrödinger + Feynman path-integral model works. |
| `quantustik://calibration` | CI90 coverage by horizon from the committed backtest. |
| `quantustik://track-record` | Realised outcomes, including losses. |
| `quantustik://disclaimer` | Full disclaimer and model limitations. |

---

## stdio (for clients that can't do remote MCP)

Some clients still only speak stdio. For those,
[`@quantustik/mcp-server`](https://www.npmjs.com/package/@quantustik/mcp-server)
([source](https://github.com/quantustik/mcp-server)) is a thin proxy that forwards
stdio to the hosted endpoint:

```jsonc
{
  "mcpServers": {
    "quantustik": {
      "command": "npx",
      "args": ["-y", "@quantustik/mcp-server"],
      "env": { "QUANTUSTIK_API_KEY": "qk_live_<your_key>" }
    }
  }
}
```

`QUANTUSTIK_API_KEY` is optional and does the same thing as the `Authorization`
header above — raises quota, nothing else.

It is a **proxy, not a local build**: it still calls `https://quantustik.com/mcp`,
so it needs network access and gives no offline path. The model and server source are
proprietary and not published here, so there is no self-hosted Quantustik. Prefer the
remote endpoint wherever your client supports it — one less hop to break.

---

## Disclaimer

All signals, forecasts and market data are for **educational research purposes only** and
do not constitute personalized financial advice. Past model performance does not guarantee
future results. Always consult a qualified financial professional before making investment
decisions.
