---
name: vantmap-check
description: Run Vantmap's mechanical checks on every map in the repository (schema, stages vs evidence, tiers, brief numbers, translations) and explain any errors. Use before committing map data or when the user asks whether the maps are consistent.
---

# Vantmap checks

From the repository root, for each map listed in `data/maps.json`:

```bash
python3 tools/derive.py <map.json> <today>
python3 tools/check.py <map.json> <today>
python3 tools/i18n_missing.py <map.json> <en.json> /tmp/missing.json
```

Then `python3 tools/i18n_langs.py /tmp data/i18n data/en.json data/maps/*/en.json`.
Report errors first (they block publishing), then warnings, with the entry id and the fix. Do not change data unless the user asks.
