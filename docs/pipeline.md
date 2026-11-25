Translated from the Chinese original in docs/zh-CN/pipeline.md.

# Vantmap Pipeline v2: Three Tiers + Discovery Layer + Verify Only When Something Happens

Version 2.1 (2026-11-24, revised after independent review). Prompt templates for sub-tasks are in prompts/. docs/daily.md and docs/new-map.md follow this file; where they differ, this file wins. Rules not mentioned here stay as before (rubric.md, the zero-error standard, archives, the label store, translation).

## 1. Three tiers

| Tier | Where the data lives | What goes in | What we guarantee | How it is checked |
|---|---|---|---|---|
| Tier 1: main map | map.json `entries` | Teams that are actively working on this problem and have evidence of grade C or better | Stage, evidence, funding, product and public results are all error-free | Draft, then two independent judgments, then a sampled acceptance check |
| Tier 2: watch list | map.json `watch` | Teams that are related but smaller, slightly off-target, or not yet fully checked | Only this: the team exists, and the one-line description matches the source page | Draft, then one judgment, then a sampled acceptance check (20 entries per map build) |
| Tier 3: leads | map.json `leads` | Links caught by the feed that nobody has opened and checked yet | No judgment at all. Only title, source and date are listed | Not checked |

- Page statistics (number of teams, furthest stage, number that reached the end, number active), the AI brief, competitive pressure and scale concentration use Tier 1 only.
- A Tier 2 `stage_rough` is written only as "rough Sx". It does not enter any statistic. **The rough stage must follow this map's own stage definitions (project.domain_rules)**, and it must reflect the entry's relation to the map's goal (for example, a product that only does part of the goal does not count as S2 for the goal itself). If unsure, write null and the page shows no stage. Acceptance must check the rough stage.
- If a Tier 2 one-liner contains an **amount, a valuation, a regulatory conclusion (approval, accelerated approval, a date) or a self-reported performance number**, the sentence is treated as a key conclusion. A separate opus sub-task that did not write it must check it online. After it passes, write `key_checked: date`. check.py blocks entries that lack `key_checked`. `why` states only the factual basis for "why this is not on the main map" (stage, indication, off-target direction, scope of the check). It must not contain unsourced judgments such as "small scale".
- Tier 3 carries no conclusions. The title is the original title. `title_zh` may only be a literal translation of the title.

### Data structure

```
watch: [{id, name, short, branch, stage_rough: "S0".."S3"|null, one_line, why, key_checked?,
         sources: [{url, quote, grade, date, verified, archive}], checked, added}]
leads: [{id: "l-…", title: original title (for a demoted entry use the team name and set title_is_name:true, with no description), title_zh?, url, source: source name or domain, date, found, matched: entry id|null, branch_guess, note?: status note, title_is_name?}]
project.sources: [{id, name, url, kind: "blog|news|releases|arxiv|journal|registry|other",
                   covers: [entry id...], lang, note}]
```
`data/maps/<id>/feed.json`: `{last_run, seen: {url_hash: date}, titles: {norm_title: date}}` (the dedup state of the discovery layer; entries are only added, never removed; kept for 180 days).

### Promotion and demotion rules (fixed)
- Tier 3 to Tier 2: after opening, a source of grade C or better is found, and the item is relevant to the goal.
- Tier 2 to Tier 1: passes the full check (draft plus two judgments), and has evidence of grade C or better that supports the stage.
- Tier 1 to Tier 2: the evidence is overturned; or there has been no substantive progress for more than 18 months and the team no longer fits the goal; or the check shows it is outside the scope of this map.
- Tier 3 deletion: a lead that has not been promoted within 90 days is deleted (feed.json still records it, so it will not come back).
- Every promotion or demotion appends one record to `changes`, with type `promote`, `demote` or `watch`.

## 2. Daily flow (for each map)

### Step A: Discovery layer (cheap)
0. The first time a map runs (no feed.json yet), feed.py enters **baseline mode**. It only records the items already on the sources and produces no hits. This stops all old items from being treated as news.
1. Read `project.sources`. For every 10 sources, start 1 haiku sub-task. It **only opens the given URLs with WebFetch and does not use WebSearch**.
2. For each source, the sub-task lists new items inside the window (SINCE = feed.json `last_run` minus 2 days) as `{url, title, date, source_id, relevant: true|false, why}`. `relevant` is true only for items about **progress of the methods or products in this map's direction**. Pure academic research, general LLM news, compute, industry events and award news are always false. If unsure, write true (template: prompts/discover_prompt.md).
3. Run `python3 feed.py map.json feed.json items.json T hits/ [--since D] [--max-hits 25]`:
   - Dedup by URL, then by (source, title). Short titles (such as version numbers) are deduped by URL only.
   - Items with a full date earlier than the window are dropped. Items with no year are marked undated. When drafting, the date must first be confirmed on a page that shows the year. If it is confirmed to be outside the window, mark the item "already recorded / old item".
   - Common-word names (such as Atlas, Nova, Orbit) do not count as a hit on their own. Only the full name or a source attribution counts.
   - At most 25 hits per day (Tier 1 and dated items first). The excess waits until the next day.
   - Similar titles are clustered into one event (several sources for the same event count once).
   - Match Tier 1 and Tier 2 by the entry's name / short / aliases.
   - Output `hits.json`, `newleads.json`, `sweep.json`, `overflow.json`.
   - **Only after the day's results are fully processed and committed to the repository**, run the same command again with `--commit`. This writes the seen URLs back to feed.json. If the run fails midway, nothing is written, and the next day sees this window again.

### Step B: Sweep (catch missed news)
- Tier 1: each day, sweep 1/7 of the entries (`feed.py` computes who is due today from the id hash and the date). This makes sure every entry is searched directly at least once a week. Use haiku, 1 WebSearch per entry.
- Tier 2: sweep all entries once every 30 days (about 1/30 per day).
- Entries in `project.sources` whose `covers` is empty: check every 3 days.
- New developments found by the sweep go into step C, the same as hits.

### Step C: Check hits (spend money only when something happens)
For each hit event:
1. **Fetch and draft** (sonnet; 1 sub-task can handle 3 events). Open the URL once. Save the original passages that contain the key content, word for word, into `cache/<url_sha>.json` (`{url, fetched_at, title, published, passages:[...]}`). Then draft the changes according to the rubric: new evidence `{grade, date, text, url, quote, progress}`, milestones, stage suggestion. **Each quote must be a verbatim substring of the passages.**
2. **Machine check**: `python3 cache_check.py drafts.json cache/` checks that every quote appears word for word in the cached passages, and that every date appears in the passages at the same precision. Drafts that fail go back to step 1 and do not reach judgment.
3. **Two judgments** (opus, **offline, reading only the cached passages**). Two sub-tasks use different questions to judge whether "conclusion + original passage" agree. Each outputs correct / minor error / wrong / no basis. A conclusion is written only if both judge it correct. If one judges a minor error, fix it as suggested and **judge it again** (another opus sub-task, or an online spot check that checks the corrected text item by item). It is written only after that passes. If the two disagree, a third opus sub-task arbitrates by rubric rule number. If arbitration is still uncertain, the item goes into `human_queue`. Any item the judgment marks `needs_online` is always checked online.
4. When a Tier 2 entry is hit, do only one judgment. The only allowed changes are: add a source (source_add), change one_line (one_line_new; if it involves amounts, regulation or self-reported numbers, treat it as a key conclusion and check it online), and change the rough stage (stage_rough_new, per this map's stage definitions). If the promotion conditions are met, follow the promotion and demotion rules in section 1.
5. **Online spot check**: of the new Tier 1 conclusions written that day, randomly pick 20% (at least 1). A separate opus sub-task that took no part opens the original web page online and checks it. If any one is incorrect, all of that day's written conclusions are re-checked online item by item. Reason: the cached text comes from the fetch tool's output, which may be an excerpt or a paraphrase. An offline judgment can only show that "what we wrote matches what we fetched". It cannot show that it "matches the web page".
6. **Sync the whole entry after writing**: after writing a new Tier 1 conclusion, scan every text and number field of the same entry one by one: product (intro, status, sources), funding (last_round, total_usd, valuation_usd, note, sources, cites), milestone, note, gaps, impact, relation. Anything that the new evidence overturns or makes stale (such as "pending", "not completed", "unconfirmed", "not yet") must be rewritten on the spot with a new source. A funding event must also update funding (write last_round as an object `{date, name, amount_usd, valuation_usd}`). The drafting sub-task gives funding_update / product_status_new / field_updates according to hit_draft_prompt, and the judgment covers them too. For entries that have new checked evidence on the latest check date, check.py warns when these words appear. Every warning must be read one by one. The machine warning is only a backstop. The main safeguard is this manual scan. For a map that had Tier 1 writes that day, rewrite the AI brief that day (prompt: prompts/brief_prompt.md).
7. Write every verdict into the label store (use round `hit:T`).

### Step D: Leads
- Append `newleads.json` to `leads` (store only title, source, date, URL and branch_guess). Do not open or check them.
- Each day, start 1 more sonnet sub-task. It picks the 5 newest leads that look most relevant, opens them and checks them. Those with a source of grade C or better move up to Tier 2 (write the watch-list entry as in section 3, and do one judgment). Irrelevant ones are deleted. Note: a company's own official pages (including product feature pages) are grade B, not D. Grade D is only for aggregator sites, reposts, job postings and third-party marketing copy.

### Step E: Everything else as before
Derive milestones, run check.py, translate (haiku; after translating, sample 10 pairs to check for misalignment, and check that no company name has been swapped for another), archive, label store, and commit the files to the repository, then run `feed.py … --commit`. The weekly Monday spot checks, canaries and missed-report checks stay as before. On Mondays, for each map, 20 Tier 2 entries are checked online (including the rough stage). Archives and the label store stay local and are not published.

## 3. Building a new map (the detailed steps are in docs/new-map.md)

1. **Scoping**: same as 5b (first draft by deep research + gap filling + missed-report check). At the end, sort the list into three groups: main-map candidates (actively working on it, with scale or progress large enough to compare), watch-list candidates, and leads.
2. **Source list**: start 1 sonnet sub-task to list 20–60 fixed sources for this map (each team's official news page / blog, GitHub releases pages, relevant arXiv category listing pages, industry media sections). Each one must state its `covers`. List only URLs that can be opened directly.
3. **Main-map entries**: 1 sonnet sub-task per team writes the entry, using the rules in section 5. Every web page cited is also saved in `cache/`.
4. **Machine check** with `cache_check.py`. Failures go back.
5. **Two judgments**: opus, offline, reading only the cached passages. Each sub-task judges 30–40 entries.
6. **Watch list**: 1 sonnet sub-task per 10 teams. For each team it opens 1–2 pages and writes `one_line`, `why`, `stage_rough` and one source with a verbatim quote. 1 opus sub-task does one judgment.
7. **Acceptance**: randomly sample 50 Tier 1 entries. For Tier 2, check all entries if there are 25 or fewer, and sample 20 if there are more. A separate opus sub-task that took no part **opens the original web pages online** and checks them (including the rough stage). Standard: 0 errors and at most 2/50 minor errors (Tier 2: at most 1/20). When re-checking after corrections, the new round must sample entries **that were not sampled before**. At most 3 rounds.
   - Note on statistics: if all 20 are correct, the "rule of three" gives a 95% upper bound on the error rate of about 15%. For 50 all correct it is about 6%. Neither proves "at most 4%". Acceptance is only a gate. What really supports the zero-error standard is the second online check, the daily online spot check and the weekly spot check, accumulated over time. The page reports the cumulative numbers.
8. Translate with haiku. The rest follows docs/new-map.md steps 5e–7.

## 4. Model assignment

| Work | Model | Reason |
|---|---|---|
| Discovery fetching, sweep, translation | haiku | Mechanical work. Later checks catch mistakes |
| First-draft scoping, writing entries, fetch-and-draft, watch list | sonnet | Needs understanding and summarizing, but others judge the final correctness |
| Two judgments, arbitration, acceptance, stage decisions | opus | These steps decide credibility, so do not cut corners |

## 5. Writing rules (from points lost at acceptance on the 11-19 and 11-20 maps)

1. **Year**: write a year only if you saw a date with the year on an opened page. If the release page shows only "21 Apr", open another page that shows the year (such as the PyPI release history) and list it as a source too.
2. **Date format**: if DD/MM versus MM/DD is unclear, judge from other dates on the same site, and state the basis in note.
3. **quote**: must be a verbatim substring of a cached passage, checked by `cache_check.py`. Do not write stitched sentences or summary sentences.
4. **No inference**: the evidence `text` contains only what the original says. Judgments such as "does not mention X" or "is not X" go into `note` or `gaps`, not into evidence. If it must be written, write "the opened page does not mention X".
5. **Affiliations and authors**: write only author affiliations that can be seen on the page. If not visible, do not write them.
6. **Strength of wording**: write plans, "claims", "about", preprints and workshop papers as the original does. A number worked out from a table must be written as "derived from the numbers in the table".
7. **License**: you must open the LICENSE file, the model card or the paper page and read the license shown there. The paper's license and the code's license are written separately.
8. **One piece of evidence says one thing**, so it is easy to judge and to edit later.

## 6. Cost records
Report cost only from real billing numbers (the usage in a sub-task result, or the bill). Do not quote estimated values outside the team. When comparing the old and new pipelines, compare cost per verified conclusion, and include the main session's own reads and writes, the two judgments, the weekly spot checks and the share of map building.
Each run appends `{date, by_model:{haiku:n, sonnet:n, opus:n}, searches, fetches, hits, leads_new, minutes}` to `project.run_stats`. The Monday message summarizes the week's sub-task counts (by model).
