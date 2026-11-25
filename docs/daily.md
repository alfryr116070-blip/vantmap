Translated from the Chinese original in docs/zh-CN/daily.md.

# Vantmap daily task v17.1 (three tiers + discovery layer + verify only when something happened)

You are the daily maintainer of Vantmap. Work in the root of this repository. The rules are in docs/pipeline.md (section 2, "Daily flow"). The evidence rules are in docs/rubric.md. The zero-error standard is unchanged. Run it in Claude Code (you need the Agent subtask tool, WebSearch and WebFetch). The plugin in plugins/vantmap runs it in one step: `/vantmap:vantmap-daily`.

The goal for a run is what the user gives you: a command argument or a GitHub issue. Report progress in the chat, or as a comment on the issue.

## 0 Preparation
(Additional conventions, v17.1)
- **SINCE**: always take the `last_run` in feed.json minus 2 days. If there is no feed.json, take today minus 7 days (tools/feed.py treats it as an empty state). A second run on the same day works the same way. De-duplication relies on feed.json.
- **No subtask tool (Agent)**: do only the mechanical steps and tier 3 (leads). Write nothing to tier 1. Put every finding that would belong in tier 1 into project.human_queue (why: "cannot run two-way judgment"). In run_stats, record by_model as 0 and tokens as null, and say so in note.
- **Items with no year** (GitHub release pages and similar): if the month and day shown are earlier than the window, treat the item as old and do not make it a lead. If it falls inside the window, first confirm the year on a page that shows the year (PyPI, the original CHANGELOG). If you cannot confirm it, make it a lead and do not write tier 1.
- **human_queue** takes three kinds of item: cases where arbitration is still uncertain; findings from the fallback sweep that have only D-grade sources or for which two-way judgment cannot be run; regulatory or milestone events that may change a stage.
- **Label-library verdict**: besides correct / minor_error / wrong / unsupported / unreachable, triage hits and fallback findings may also use not_material (not substantive progress), old_item (an old item outside the window) and unresolved (moved to human_queue).
- **Dead sources**: if a source returns only content older than 30 days, or cannot be opened, in 3 runs in a row, mark "suspected dead" in that source's note. The Monday missed-report check also looks for a replacement page and updates project.sources.
- **Page run state**: set project.auto_refresh to true only if you run this update on a schedule (for example a cron job or a scheduled Claude Code run); the viewer then says "refreshes every morning". A manual run does not change it.
- **Weekly spot check**: append the result to project.audit.weekly ({date,n,correct,minor,wrong,unsupported,unreachable,note}). The method section of the page shows the latest one and how many days ago it was.
- **Translation**: run i18n_missing with --prune (promises.json and compare.json must be in the same directory). With no subtasks, the main session translates. After translating, check 10 pairs yourself for misalignment and say so in the report.
- **Local files**: the page-text archive (data/archive/), the audit labels (data/labels/) and the page cache (cache/) stay on your machine. Do not commit them (copyright).

1. Run `git pull` to get the latest data. Read data/maps.json, and for every map its map.json / en.json / feed.json. Also read tools/*.py, docs/pipeline.md, docs/rubric.md and prompts/.
2. Set T = today's date. Set SINCE as described above (last_run minus 2 days).

## 1 For each map, in turn (run in parallel where you can; at most 12 background subtasks at once)
A. Discovery layer: for every 10 entries in project.sources, start 1 **haiku** subtask that uses only WebFetch. Use the prompt prompts/discover_prompt.md. The rules are in docs/pipeline.md, step A.
B. `python3 tools/feed.py map.json feed.json items.json T hits/` produces hits.json, newleads.json, sweep.json and overflow.json. A map with no feed.json runs in baseline mode the first time and produces no hits.
C. Fallback sweep: for the items in sweep.json, start 1 **haiku** subtask. Each item gets 1 WebSearch. Merge the results into the hits.
D. Hit verification (prompts: prompts/hit_draft_prompt.md and prompts/hit_judge_prompt.md): for every 3–5 hit events, start 1 **sonnet** subtask to fetch and draft (fetch each URL once; save the original text in cache/). Then run `python3 tools/cache_check.py`. For a tier-1 hit, start 2 **opus** subtasks that judge separately, with no web access. Write the entry only if both say correct. If they disagree, start a third opus to arbitrate. If it is still uncertain, put it in human_queue. For a tier-2 hit, do only one judgment (what can be changed is in docs/pipeline.md, step C4). Spot-check 20% of the new tier-1 conclusions written that day, with web access (step C5). After writing, sync the whole entry (product, funding, notes and other fields) by step C6.
E. Leads: append newleads to leads. Start 1 **sonnet** subtask to pick the 5 most relevant leads and open them to check. A lead with a C-grade or better source moves up to the watch list (and gets one more opus judgment). Delete irrelevant leads. Delete leads that have not moved up within 90 days.
F. Promotion and demotion: follow the promotion and demotion rules in section 1 of docs/pipeline.md. Write each move into changes (type promote / demote / watch).
G. `tools/derive.py` derives milestones and activity. `tools/check.py` must report 0 errors (including the tier-2 key_checked rule).
H. Translation: new Chinese goes to en.json (haiku; after translating, check 10 pairs for misalignment and for company names replaced by other companies). New English goes to data/i18n/<6 languages>.json (haiku).
I. Archive: write data/archive/T.json (the passages and sha256 of every cached page) and the label library data/labels/T.jsonl.txt (one line per judgment). Both stay local.
J. Append to project.run_stats on **every map**. The subtask and token counts may be a combined total for all 5 maps, but every map needs that day's entry, including hits and material. Fields: {date, by_model:{haiku,sonnet,opus}, tokens_by_model (add up the usage in the subtask results), searches, fetches, hits, leads_new}. This step is required. Report cost only from these real numbers.

I2. For any map that had a tier-1 write that day, start 1 sonnet subtask to rewrite the AI summary by prompts/brief_prompt.md. Publish only after check.py reports 0 errors.

## 2 Publish
Run `python3 tools/check.py`. When it reports 0 errors, `git commit` the changed files. Leave out feed.json for now, and leave out data/archive/, data/labels/ and cache/. Push only if the user asked you to. If the repository serves GitHub Pages and you pushed, the page updates by itself.

Do not include feed.json in the first commit. After the first commit succeeds, run tools/feed.py again with the same arguments plus `--commit` for each map, then commit feed.json on its own.

After publishing, leave two lines in the chat (or as an issue comment): for each map, how many hits, how many written, how many promotions and demotions, and the number of subtasks (by model).

## 3 Extra on Mondays
Do these: spot-check 50 tier-1 entries (opus, with web access); the **canary check** (pick 2–3 real, dated items from the past week on fixed sources, without telling the screening agents, and confirm the discovery layer surfaced them; record hits/misses in project.audit.canary); and the **missed-report check** (one agent that did no other work searches independently, by a different route — other languages, patents, trial registries, papers — for teams or news from the past 7 days that the map lacks; record what it found in project.audit.recall and add real finds as leads). For tier 2, spot-check 20 entries per map (opus, with web access, including the rough-judgment stage; prompt prompts/acc_prompt.md). The standard is 0 errors and at most 1 minor error in 20. If it fails, fix the problem entries and demote them.

## Do not
Do not delete data files. Do not change repository settings. If something needs payment or authorization, stop and leave a note.

## 4 Other recurring steps
- 1a Exchange rates: WebFetch https://open.er-api.com/v6/latest/USD and update data/fx.json (if the fetch fails, keep the old file).
- 1b New-direction requests: the repository version has no request queue. A new map is built separately with docs/new-map.md (see "Make a new map" in the README, or `/vantmap:vantmap-new-map`).
- 1d/1e Error reports and appeals: the repository version reads them from GitHub issues with the label `correction`, at most 10 per day. Start subtasks that were not involved, with web access, to re-check each one. Write the verdict to the label library (round = report:T). Reply with the result in the issue.
- 4a–4c Field and accuracy rules: docs/rubric.md, step 5c of docs/new-map.md and the writing rules in section 5 of docs/pipeline.md all apply. New tier-1 conclusions still need two-way blind review. Funding figures and promise verdicts count as key conclusions.
- 4d Promise ledger (data/promises.json: dated public promises by teams and whether they were kept) and 4e engineering activity (`python3 tools/signals.py <map.json> <signals.json> <today>`): update when the inputs changed.
- 5 AI summary: write it only from tier 1 (entries). The watch list and leads do not go into the summary or the statistics.
- 6b There is nothing to write back in the repository version.
- 7 Report in the chat (or as an issue comment): 2–5 sentences per map. Put the human_queue count and the error count at the end. On Mondays, add the previous week's subtask counts by model.
