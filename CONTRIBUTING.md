# Contributing to Vantmap

Thanks for helping! Vantmap is only as good as its evidence, so every contribution follows one rule:
**every claim needs a link, a verbatim quote from that page, and an evidence grade.**

## Easy ways to help

- **Report a wrong claim** — open a *Correction* issue: the map, the entry, what is wrong, and a link that shows it. An agent that did not write the claim re-checks it online; you will get a reply in the issue.
- **Suggest a team** — open a *New team* issue with one source link. It enters the map as a lead (tier 3) and moves up only after it is checked.
- **Add a fixed source** — a page that lists dated news, releases or papers for a team or field (`project.sources` in a map). Cheap sources make daily updates cheaper.
- **Translate** — fix or add strings in `data/i18n/<lang>.json` (keys are the English text).
- **Request or build a new map** — open a *New map* issue with the goal in one sentence, or build it yourself with the `vantmap-new-map` skill and send a PR.

## Pull requests

1. `pip install pytest` and run `pytest -q` — all tests must pass.
2. Run `python3 tools/check.py <map.json> <today>` for every map you touched — 0 errors.
3. New or changed tier-1 claims must come with the check that supports them (the judge/verifier output, or a short note in the PR with the page and quote). PRs that add claims without sources are closed.
4. Keep quotes short (≤ 40 words) and verbatim. Don't paste full articles.
5. Code: Python 3.10+, standard library only for `tools/` (so it runs anywhere).

## Data rules in one screen

- Stages S0–S5 follow `docs/rubric.md` and each map's `project.domain_rules`.
- Grades: A primary official records (regulatory filings/decisions, audited reports, official product docs and release notes, peer-reviewed papers); B the company's own announcements, preprints, repository records; C specialist media; D reposts, aggregators, general news. D alone can't support any stage above S0.
- Dates only at the precision the page shows. No year on the page → find a page that shows it, or leave it null.
- Write only what the page says: keep "plans", "says", "about", "preprint".

## Code of conduct

Be kind and assume good faith. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
