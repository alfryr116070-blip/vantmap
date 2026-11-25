---
name: vantmap-new-map
description: Build a new Vantmap progress map for a research or product goal — who is working on it, what stage each has reached, every claim sourced and independently checked, with a watch list, leads and a fixed source list. Use when the user asks to map a new direction.
---

# New Vantmap map

Work in the root of a Vantmap repository.

1. Ask for (or take from the request) the goal in one sentence and the target stage. Everything else you decide.
2. Read `docs/new-map.md`, `docs/pipeline.md` section 3, `docs/rubric.md` and `prompts/`.
3. Build the map in three tiers exactly as `docs/pipeline.md` section 3 says: survey → fixed source list (`prompts/sources_prompt.md`) → tier-1 entries with verbatim cached quotes → `tools/cache_check.py` → two offline judges → watch list (`prompts/watch_spec.md`) with one judge → acceptance sample checked online by an agent that wrote nothing (`prompts/acc_prompt.md`), at most 3 rounds.
4. Publish honestly: if acceptance does not pass, set `project.verified=false` and keep the real numbers in `project.audit.acceptance` — the viewer shows a banner.
5. Add the map to `data/maps.json`, write `en.json` (and the 6 other languages via `tools/i18n_langs.py`), run `tools/check.py` to 0 errors, and commit.
