// Quantustik REST API — minimal TypeScript client (fetch, no dependencies).
// Educational research only; not investment advice.
// Optional free API key for higher quotas: https://quantustik.com/developers

const BASE = "https://quantustik.com/api/v1";
const API_KEY = process.env.QUANTUSTIK_API_KEY; // optional

async function get(path: string, params: Record<string, string | number> = {}) {
  const qs = new URLSearchParams(
    Object.entries(params).map(([k, v]) => [k, String(v)])
  ).toString();
  const url = `${BASE}${path}${qs ? `?${qs}` : ""}`;
  const headers: Record<string, string> = API_KEY
    ? { Authorization: `Bearer ${API_KEY}` }
    : {};
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

async function main() {
  const data = await get("/signals", {
    direction: "BUY",
    min_conviction: 7,
    limit: 5,
  });
  console.log(`generated_at=${data.generated_at}`);
  for (const item of data.results ?? []) {
    const sig = item.signal ?? {};
    console.log(
      item.ticker,
      sig.verdict,
      `conviction=${sig.conviction}`,
      `entry=${sig.entry_price}`,
      `stop=${sig.stop_loss}`,
      `TP=${JSON.stringify(sig.take_profit)}`
    );
  }
}

main().catch(console.error);
