"""Cost report from run_stats.

usage: python3 tools/cost.py [--prices prices.json] [--since YYYY-MM-DD] data/map.json data/maps/*/map.json

Each daily run appends to project.run_stats an entry like
  {"date": "...", "by_model": {"haiku": 17, "sonnet": 4, "opus": 3},
   "tokens_by_model": {"haiku": 1069890, ...},          # summed sub-agent tokens (rough)
   "usage_by_model": {"haiku": {"input": .., "output": .., "cache_read": .., "cache_write": ..}, ...}}  # exact, preferred
If usage_by_model is present it is priced exactly. Otherwise tokens_by_model is priced with a
stated assumption (90% input / 10% output, no caching) and the report says it is an estimate.
Prices default to the table below (USD per million tokens); pass --prices to override.
"""
import sys as _sys
if len(_sys.argv) < 2 or _sys.argv[1] in ("-h", "--help"):
    print(__doc__ or "see docs/"); _sys.exit(0)

import json, sys

PRICES = {  # USD per 1M tokens: input, output, cache_read, cache_write
    "haiku": {"input": 0.10, "output": 0.50, "cache_read": 0.01, "cache_write": 0.125},
    "sonnet": {"input": 2.0, "output": 10.0, "cache_read": 0.20, "cache_write": 2.5},
    "opus": {"input": 4.0, "output": 20.0, "cache_read": 0.40, "cache_write": 5.0},
}


def main():
    a = sys.argv[1:]
    prices = PRICES
    since = None
    if "--prices" in a:
        i = a.index("--prices"); prices = json.load(open(a[i + 1])); del a[i:i + 2]
    if "--since" in a:
        i = a.index("--since"); since = a[i + 1]; del a[i:i + 2]
    if not a: print(__doc__); sys.exit(2)
    seen = set(); total = 0.0; est = False; rows = []
    for p in a:
        m = json.load(open(p))
        for r in m.get("project", {}).get("run_stats", []) or []:
            if since and str(r.get("date")) < since: continue
            key = (r.get("date"), r.get("kind"), json.dumps(r.get("tokens_by_model"), sort_keys=True), json.dumps(r.get("usage_by_model"), sort_keys=True))
            if key in seen or not (r.get("usage_by_model") or r.get("tokens_by_model")): continue  # shared totals are recorded once
            seen.add(key)
            c = 0.0
            if r.get("usage_by_model"):
                for mod, u in r["usage_by_model"].items():
                    pr = prices.get(mod, {})
                    c += sum(u.get(k, 0) * pr.get(k, 0) for k in ("input", "output", "cache_read", "cache_write")) / 1e6
            else:
                est = True
                for mod, t in (r.get("tokens_by_model") or {}).items():
                    if not t: continue
                    pr = prices.get(mod, {})
                    c += (0.9 * t * pr.get("input", 0) + 0.1 * t * pr.get("output", 0)) / 1e6
            rows.append((r.get("date"), r.get("kind"), round(c, 2))); total += c
    for row in rows: print(*row, sep="\t")
    print(f"total\t\t{total:.2f} USD" + ("  (ESTIMATE: no exact usage recorded for some runs)" if est else ""))


if __name__ == "__main__":
    main()
