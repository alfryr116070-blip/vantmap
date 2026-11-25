---
name: vantmap-daily
description: Run the Vantmap daily update in a Vantmap repository — screen fixed sources, verify only the hits, update the three tiers, check and commit. Use when the user asks to update, refresh or run the daily job for their Vantmap maps.
---

# Vantmap daily update

Work in the root of a Vantmap repository (it has `data/maps.json`, `docs/daily.md`, `tools/check.py`).
If you are not in one, say so and stop.

1. Read `docs/daily.md` completely, then `docs/pipeline.md` (section 2), `docs/rubric.md` and the prompt templates in `prompts/`.
2. Follow `docs/daily.md` step by step. Delegate with the plugin's agents:
   - `vantmap-scout` (small model) — fetch fixed sources, list new items, fallback searches.
   - `vantmap-drafter` (medium model) — open each hit once, cache verbatim passages, draft the change.
   - `vantmap-judge` (large model) — two independent offline judgements per tier-1 draft.
   - `vantmap-verifier` (large model) — online re-check of ≥20% of tier-1 writes, and any `needs_online` item.
   If you cannot start sub-agents, do not write anything to tier 1; put findings in `project.human_queue` (see the v17.1 notes in `docs/daily.md`).
3. Zero-error rule: write to tier 1 only when both judges say correct (re-judge after fixing a minor). After every write, update the whole entry (product, funding, note, gaps, impact) — `docs/pipeline.md` step C6.
4. Run `python3 tools/derive.py <map> <today>` and `python3 tools/check.py <map> <today>` for every map until there are 0 errors; review every warning.
5. Append `project.run_stats` to every map with `by_model` and `usage_by_model` (input/output tokens from the sub-agent results) so `tools/cost.py` can price it exactly.
6. Commit the changed data (not uncommitted feed state), then run `feed.py … --commit` and commit `feed.json`. Push only if the user asked you to.
7. Report per map in 2–5 sentences, the human_queue items, and anything in the docs you had to guess.
