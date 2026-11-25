# Changelog

## 0.1.0 — 2026-11-25 (first public release)

- Viewer: map, compare, list, timeline, changes, method/audit panels; 8 languages; three tiers (main map, watch list, leads).
- One fictional demo map (made-up teams, numbers and links) to show the viewer.
- Pipeline: fixed sources → cheap screening → `feed.py` dedupe/match → drafts → `cache_check.py` → two offline judges → ≥20% online re-check → `derive.py` → `check.py`.
- Tools: `check.py` (schema, tiers, stages vs evidence, brief numbers, acceptance consistency), `derive.py`, `feed.py`, `cache_check.py`, `fetch_archive.py` (full-page archive with quote check), `cost.py`, i18n helpers.
- Claude Code plugin (`/vantmap:vantmap-daily`, `/vantmap:vantmap-new-map`, `/vantmap:vantmap-check`) and a ChatGPT prompt + standalone viewer.
- Acceptance and weekly spot-check numbers are shown on every map, including "not passed" banners.
