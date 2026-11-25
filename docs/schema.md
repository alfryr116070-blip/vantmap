# Data format

A repository holds any number of maps. `data/maps.json` lists them; the viewer (`index.html`) and every script read the same files.

```
data/maps.json                      {"maps":[{id, map, en, title, title_en, goal, target_stage, created, updated}]}
data/map.json  + data/en.json       the first map (kept at the top level for backwards compatibility)
data/maps/<id>/map.json             one map
data/maps/<id>/en.json              {Chinese source string: English}  — map content is authored in Chinese
data/maps/<id>/feed.json            discovery-layer state (seen URLs/titles, last_run)
data/i18n/<lang>.json               {English string: translation} for ja ko es fr de pt (shared by all maps)
data/fx.json                        exchange rates; funding is stored in USD and shown in local currency
```

Content strings are Chinese; English comes from `en.json`; other languages translate the English. Add a language by adding `data/i18n/<code>.json` and its name in `index.html`.

## map.json

```jsonc
{
  "project": {
    "title": "…", "goal": "one sentence", "target_stage": "S2",
    "finish_def": "what counts as reaching the goal",   // optional
    "branches": [{"id": "agent", "name": "…", "desc": "…", "adjacent": false}],
    "domain_rules": ["map-specific rules for stages and grades"],   // optional; without it the general rubric applies
    "verified": true,                 // false → the viewer shows a "not passed" banner
    "auto_refresh": false,            // true only while a scheduled daily update is running
    "sources": [{"id","name","url","kind","covers":[entry ids],"lang","note"}],
    "audit": {"acceptance": {...}, "weekly": [...], "canary": [...], "recall": [...]},
    "human_queue": [{"date","entry","claim","url","why"}],
    "run_stats": [{"date","by_model","usage_by_model","hits","material"}],
    "updated": "YYYY-MM-DD"
  },
  "entries": [ /* tier 1 — main map */ ],
  "watch":   [ /* tier 2 — watch list */ ],
  "leads":   [ /* tier 3 — leads */ ],
  "changes": [{"date","entry","type","summary","url"}],   // type: new|stage|milestone|bad|activity|promote|demote|watch
  "corrections": [{"date","entry","what","url"}],
  "brief": {"date","headline","points":[{"text","refs"}],"you":{"text","refs"}}
}
```

### Tier 1 entry (`entries[]`)

| field | meaning |
|---|---|
| `id`, `name`, `short` | stable id, full name, ≤14-char label for the map |
| `section`, `branch` | `main` or `adjacent`; one of `project.branches[].id` |
| `stage` | S0–S5 (see `docs/rubric.md`) |
| `evidence[]` | `{grade A–D, date, text, url, quote (verbatim), verified, archive, progress (bool), event_date?}` |
| `milestone`, `last_progress`, `milestone_ref`, `milestone_grade`, `activity` | **derived** by `tools/derive.py` from the newest `progress:true` evidence — don't hand-edit |
| `product` | `{name, intro, status, sources:[{url, quote}]}` |
| `funding` | `{kind, total_usd, valuation_usd, last_round:{date,name,amount_usd,valuation_usd}, investors, sources, cites:{field:{url,quote}}, note}` |
| `openness[]` | `{kind code|weights|dataset|paper|sdk|hardware|registry, name, url, license, use, date}` |
| `gaps` | `{field:[{text,basis_url}], ours:[…]}` — what the team still lacks / what we haven't verified |
| `relation`, `impact`, `note` | plain-language context for the reader |

### Tier 2 entry (`watch[]`)

`{id, name, short, branch, stage_rough: S0–S3|null, one_line, why, sources:[{url, quote, grade, date}], checked, added, key_checked?}`
Only existence and the one-line description are guaranteed. `key_checked` is required when `one_line`/`why` contain money, regulatory decisions or self-reported metrics. Tier 2 must not have `stage`, `evidence`, `funding` or `milestone`.

### Tier 3 lead (`leads[]`)

`{id: "l-…", title, title_zh?, url, source, date, found, matched, branch_guess, note?, title_is_name?}` — no claims.

Older maps may also carry legacy keys (`candidates`, `merge_notes`, `candidates_migrated`, `idea`, evidence `date_orig`/`date_note`, gap items with `url` instead of `basis_url`); the viewer and checks tolerate them.

All of this is enforced by `tools/check.py` (exit code 1 on any error).
