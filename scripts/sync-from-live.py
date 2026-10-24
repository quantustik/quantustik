#!/usr/bin/env python3
"""Refresh this repo's machine-readable artifacts from the live Quantustik service.

Everything under `.well-known/`, `openapi.json`, `llms.txt` and the tool /
prompt / resource inventory in `server.json` is a *copy* of something the
running service already serves. Copies drift: between 2026-07-14 and
2026-08-02 the vendored openapi.json fell six endpoints behind and the tool
catalog four tools behind, with nothing failing to say so.

    python3 scripts/sync-from-live.py            # rewrite the copies in place
    python3 scripts/sync-from-live.py --check    # exit 1 if anything is stale

`--check` is what CI runs, so drift shows up as a red build rather than as a
developer reading a stale tool list.

The prose in `docs/` and `README.md` is NOT synced — it is written by hand and
this script only tells you when its tool count no longer matches the server.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.request

BASE = "https://quantustik.com"
ROOT = pathlib.Path(__file__).resolve().parent.parent
TIMEOUT = 30

#: Copied verbatim from the live service: (repo path, URL path).
MIRRORED = (
    ("openapi.json", "/openapi.json"),
    ("llms.txt", "/llms.txt"),
    (".well-known/mcp.json", "/.well-known/mcp.json"),
    (".well-known/ai-plugin.json", "/.well-known/ai-plugin.json"),
)

#: Files whose tool table must stay in step with the live server.
TOOL_TABLE_DOCS = ("docs/mcp.md",)


def _fetch(path: str) -> bytes:
    req = urllib.request.Request(
        BASE + path, headers={"User-Agent": "quantustik-docs-sync"}
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read()


def _rpc(method: str, params: dict | None = None) -> dict:
    """One stateless JSON-RPC call against the hosted MCP endpoint."""
    body = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    ).encode()
    req = urllib.request.Request(
        BASE + "/mcp",
        data=body,
        headers={
            "Content-Type": "application/json",
            # The endpoint is streamable-HTTP: without text/event-stream in
            # Accept it refuses the request outright.
            "Accept": "application/json, text/event-stream",
            "User-Agent": "quantustik-docs-sync",
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read().decode()
    # A streamable-HTTP reply may arrive as an SSE frame ("data: {...}").
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        raise SystemExit(f"unparseable {method} response: {raw[:200]}")
    payload = json.loads(match.group(0))
    if "error" in payload:
        raise SystemExit(f"{method} failed: {payload['error']}")
    return payload["result"]


def _canonical(text: str) -> str:
    """Pretty-print JSON so a one-field change is a one-line diff."""
    return json.dumps(json.loads(text), indent=2, ensure_ascii=False) + "\n"


def _live_server_json() -> str:
    """server.json with its inventory rebuilt from what the server answers now."""
    current = json.loads((ROOT / "server.json").read_text())
    current["tools"] = [
        {
            "name": t["name"],
            "description": t.get("description", ""),
            "inputSchema": t.get("inputSchema", {}),
        }
        for t in sorted(_rpc("tools/list")["tools"], key=lambda t: t["name"])
    ]
    current["prompts"] = [
        {"name": p["name"], "description": p.get("description", "").strip()}
        for p in _rpc("prompts/list")["prompts"]
    ]
    current["resources"] = [
        {
            "uri": r["uri"],
            "name": r["name"],
            "description": r.get("description", "").strip(),
        }
        for r in _rpc("resources/list")["resources"]
    ]
    return json.dumps(current, indent=2, ensure_ascii=False) + "\n"


def _documented_tools() -> set[str]:
    """Tool names in the `## Tools` table — that section only.

    Scoped to the section because the Prompts table below it uses the same
    row shape, and counting those as tools reports every prompt as a tool the
    server no longer serves.
    """
    names: set[str] = set()
    for rel in TOOL_TABLE_DOCS:
        text = (ROOT / rel).read_text()
        section = re.search(r"^## Tools\b.*?(?=^## |\Z)", text, re.M | re.S)
        if not section:
            raise SystemExit(f"{rel}: no '## Tools' section to check")
        names |= set(re.findall(r"^\| `([a-z_]+)` \|", section.group(0), re.M))
    return names


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift and exit 1 instead of rewriting files",
    )
    args = parser.parse_args()

    stale: list[str] = []

    for rel, url_path in MIRRORED:
        raw = _fetch(url_path).decode()
        wanted = _canonical(raw) if rel.endswith(".json") else raw
        target = ROOT / rel
        if target.read_text() == wanted:
            continue
        stale.append(rel)
        if not args.check:
            target.write_text(wanted)

    wanted_manifest = _live_server_json()
    if (ROOT / "server.json").read_text() != wanted_manifest:
        stale.append("server.json")
        if not args.check:
            (ROOT / "server.json").write_text(wanted_manifest)

    live_tools = {t["name"] for t in _rpc("tools/list")["tools"]}
    missing = sorted(live_tools - _documented_tools())
    removed = sorted(_documented_tools() - live_tools)

    for rel in stale:
        print(f"{'stale' if args.check else 'updated'}: {rel}")
    if missing:
        print(f"undocumented tools (add to {TOOL_TABLE_DOCS[0]}): {', '.join(missing)}")
    if removed:
        print(f"documented but not live: {', '.join(removed)}")

    if args.check and (stale or missing or removed):
        return 1
    if missing or removed:
        # Prose is hand-written; syncing the manifests cannot fix it.
        return 1
    if not stale:
        print("up to date with the live service")
    return 0


if __name__ == "__main__":
    sys.exit(main())
