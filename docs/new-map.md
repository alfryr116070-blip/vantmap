Translated from the Chinese original in docs/zh-CN/new-map.md.

# Build a new map (on-demand research)

This task handles a new-direction request. The request is the goal the user gives you: a command argument or a GitHub issue. It may also carry these fields: `text` (the direction), `type` ("goal" or "target"), `target_stage`, `map` (which map it refers to), `tier` ("quick" or "full") and `draft`. Report progress in the chat, or as comments on the issue. Do not stop to ask questions.

0. Take the request.
   - Work on one request at a time.
   - After each big step, report progress in the chat (or as an issue comment), for example "starting research".

1. Read the current state.
   - Read data/maps.json (the map list), docs/rubric.md, tools/check.py, tools/i18n_missing.py, and the data file and English translation file of the map the request's `map` field points to.
   - Read docs/rubric.md in full. Judge stages S0–S5 and evidence grades A–D by it.
   - Take file paths from the `map` and `en` fields in maps.json.
   - If the request has no `map` field, it means the first map in maps.json.

2. Type "target" (only move the finish line).
   - Change that map's project.target_stage to the requested target_stage.
   - Run tools/check.py and write the map's data file.
   - Also change target_stage for this map in data/maps.json.
   - Commit both files. Report "target stage changed to S?" in the chat. Then go to step 6.

3. Type "goal": first decide whether it is a rewording or a change of field.
   - If the new direction `text` and the original map's project.goal are in the same field and have mostly the same main rivals (for example, only a different phrasing, or a slightly narrower or wider scope), it is a rewording. Do step 4.
   - If the field is different (for example, from balcony plant-care devices to urban vertical farms), it is a change of field. Do step 5 and generate a new map. Keep the original map.
   - Report the decision in the chat, for example "this is a new field, generating a new map".

4. Rewording: update the original map.
   - Change project.goal to the new direction. Write the old goal into merge_notes.
   - If the request has a target_stage, also update project.target_stage.
   - Re-judge section for the existing entries. An entry that no longer belongs to the main direction becomes adjacent. Do not delete it.
   - Search for new teams under the new direction: at most 15 searches, mostly in English. For Chinese teams, add one search in Chinese.
   - Fill new entries by the field requirements in step 5c. Append records to changes.
   - Then do steps 5e and 5f, but publish the original map's files.

5. Change of field: generate a new map.
   - Use at most 150 searches in total. Run at most 15 subtasks at the same time. Use only pages you opened. Do not rely on memory.

   5a. Define the map.
   - id: lowercase English with hyphens, for example balcony-plant-care. It must not repeat an id already in maps.json.
   - File paths: data/maps/<id>/map.json and data/maps/<id>/en.json.
   - project fields:
     - title: a short Chinese title.
     - goal: the user's direction as one clear Chinese sentence that can be judged.
     - idea: the user's own words.
     - created and updated: today.
     - rubric: the same version as docs/rubric.md.
     - target_stage: the requested target_stage. If there is none, choose the most reasonable level for this field and explain the reason in merge_notes.
     - finish_def: one Chinese sentence that says exactly what "reaching the finish line" means in this field, for example "a product is sold to households and both waters and feeds plants automatically".
   - branches: 3 to 5 routes, in the format {"id","name","desc"}. The last one is always {"id":"adjacent","name":"相邻方向","desc":"…"}.
   - layers: the links of the industry chain for this field, 5 to 6 short Chinese terms, for example "传感器", "执行机构", "控制软件", "量产", "渠道", "售后". An entry's role may use only these terms.
   - domain_rules: 3 to 8 Chinese rules specific to this field. Write them into project.domain_rules. Every subtask and every checker judges by them. They must say at least:
     - What counts as "substantive progress" in this field (for example, for a consumer device: a working prototype in real homes, a certification passed, first paid deliveries, a new production line; not counted: concept videos, trade-show demos, plans).
     - What S1–S5 mean in this field (for example, S2 = the company announces reaching the target endpoint; S4 = regulatory approval plus independent confirmation).
     - The statements that are easy to confuse and must be told apart (for example, "approved to run a trial" is not "approved for market", "enrollment complete" is not "endpoint reached", "indication A approved" is not "indication B approved").
     - What the A-grade sources are in this field (for example, regulator databases, standards bodies' certification lists, peer-reviewed papers).

   5b. Survey.
   - First start 1 Opus subtask to write a "deep-research first draft". Give it only the question for this direction (no existing data). It may use at most 30 searches. It writes a list of teams with source links and a conclusion for each ({team, claim, urls}). A comparison on 2026-11-06 showed that such a draft is fully correct about 95% of the time, which cuts the later searching a lot. The draft is not evidence. Every conclusion in it must still be checked against the original page by 5c, 5c2 and 5c3, and any conclusion without support is deleted.
   - Then start at most 4 subtasks to add to the survey, with at most 20 searches in total, mostly English with Chinese added. They look specifically for what the draft missed (especially teams from China and from non-English sources).
   - Find 12 to 25 teams that are working toward this goal. Include companies, labs, big-company projects, government- or fund-backed programs, and those that have announced but not yet published results.
   - If the request has a `draft` field (an analysis frame the user supplies: routes, stages, finish, evidence, questions, with no teams), you may use it as a reference for branches, finish_def and domain_rules. Re-judge all of it for this field. The frame is not evidence. If an old-format draft carries entries, treat them only as survey leads. Do not put into the map anything you cannot verify.
   - Cast a wide net. Even for a quick view, first list every team you can find (name, one sentence and one link only), then choose which to verify.
   - First make the list. Remove duplicates and the obviously irrelevant.
   - Report progress in the chat, for example "found 18 teams, verifying one by one".

   5b1. Missed-report check: after the list is made, start 1 more subtask that did not take part in 5b. It takes a different search route (change language, search patents, search job postings or tenders, search industry directories) with at most 10 searches, and lists the teams again. Write the difference between the two lists into project.audit.recall = [{"date","found_new","names"}]. Merge the newly found teams into the list.

   5b2. Quick view or full version (the request's `tier` field; the default is "quick").
   - tier "quick" (the default): from the list, pick the 5 to 8 "most important" teams by a fixed standard, and verify only those:
     - at least 1 representative for every route (branch);
     - fill the rest in this order: the furthest stage evidence; has deliveries or approvals; the largest funding or market value; the most active in the last 6 months;
     - write the reason for the pick into every entry's pick_reason (one Chinese sentence, for example "furthest stage on this route").
     - Write the rest of the teams in the list into project.roster: [{"name","one_line","url"}] (only a name, one sentence and one link you opened; no stage judgment, no numbers). The viewer shows "found N teams, listing the main M here".
     - Set project.tier to "quick". Steps 5c, 5c2 and 5c3 apply only to the picked entries. If there are fewer than 50 items for the acceptance sample, check them all.
   - tier "full" (when the user asks for the full version): verify every team on the list. Set project.tier to "full" and clear roster. Quick-view entries that are already verified are reused without re-checking.

   5c. Verify one by one.
   - The accuracy rules in the daily task (docs/daily.md) apply here too: B/C-grade sources go into evidence; open LICENSE to check licenses; reposts and aggregator sites count as D; every piece of evidence carries a quote (one sentence copied word for word from the original) and a verified date; "recent progress" counts only substantive progress.
   - Start 1 subtask per team, with at most 4 searches. Fill in the field structure of the entries in data/map.json:
     - Basic information: id, name, short (at most 14 characters), section (main or adjacent), branch.
     - Progress: stage, milestone, milestone_grade, activity, last_progress, flags, confidence, evidence ([{grade,date,text,url}], at least 1), note, checked (today).
     - Funding: funding, on the same basis as data/map.json. kind is startup, listed or project, or academic (academic or charity funding). If it cannot be found, use null.
     - Role and product: role ({layers,main}, using only the layers from 5a), product ({name,intro,status}).
     - Public output: openness (code, data, models, papers, trial registrations; kind is code, weights, dataset, paper, sdk, hardware or registry; list only links you opened and verified, each with a use field), closed_note.
     - Relation to the user: relation, one or two sentences.
     - Two kinds of gaps, `gaps` (the page shows them separately; do not mix them):
       - gaps.field: what this team still lacks, by this map's stage definitions, to reach the next level and the target stage (1–3 items, for example "to reach S4: no independent long-term disease-free survival data seen in public material"). Before writing it, search and confirm that public material really has none. If it does exist and the map has just not opened and checked it, it is not a field gap. It is an ours gap.
       - gaps.ours: homework the map itself has not finished (0–3 items, for example "the FDA approval page has not been opened and checked; only the company press release so far", "stage rests only on D-grade sources"). Put the primary-source link in url when you have one.
       - Format: {"field":[{"text","basis_url"}],"ours":[{"text","url"}]}. The daily task fills the ours items first.
   - Rule 7, in the original words: "D-grade evidence cannot alone support any move up a stage". A team with only D-grade evidence is at stage S0.

   5c2. Independent check (zero-error standard).
   - After all teams are written, start subtasks that took part in neither 5b nor 5c (do not use haiku). Each checks at most 20 conclusions. For each one it opens the original page and judges "correct / minor error / wrong / no support".
   - Keep only those judged "correct". Change "minor error" ones to match the original. Delete "wrong" and "no support" ones. After the evidence is deleted, judge the stage again by the rules (only D-grade left means S0).
   - Key conclusions get two-way blind review (credibility standard v1.0, layer 4). This covers evidence that supports a stage, funding and market-value figures, and conclusions that rest only on D-grade sources. Start a second subtask that knows nothing of the first (different prompt and search path, and it cannot see the original stage or the first judgment) and have it judge again on its own. Keep the conclusion only if both say "correct". If the two disagree, a third subtask arbitrates by rule number. If it is still uncertain, do not write it. Record it in project.human_queue. Write every disagreement into the label library (round = dual:<today>).
   - Every source must have a quote (one sentence copied word for word) and a verified date. Without them tools/check.py reports an error and you cannot publish.

   5c3. Acceptance gate (a map that does not pass is not "verified").
   - Start 2 to 3 subtasks that took part in none of 5b, 5c and 5c2 (do not use haiku). From all conclusions of this map (evidence, funding sources, funding figures, public output, milestones, product descriptions), draw 50 with a fixed random seed (if there are fewer than 50, check them all). For each one, open the original page and judge "correct / minor error / wrong / no support / unreachable". They must follow project.domain_rules when judging.
   - Pass standard: 0 wrong and 0 no support. Minor errors at most 4% (at most 2 of 50).
   - If it fails: fix or delete according to the findings (after deleting evidence, re-judge the stage by the rules). Then start new subtasks that took no part before, change the random seed and draw 50 again. At most 3 rounds.
   - Write the result into project.audit = {"date","pool","n","correct","minor","wrong","unsupported","accuracy","lower95","stage_agree","stage_n","target":"96%","acceptance":{"date","n","correct","minor","wrong","unsupported","unreachable","lower95","rounds"}}. Write all changes into corrections. lower95 is the two-sided 95% Clopper-Pearson bound (for the proportion with no errors).
   - If it still fails after 3 rounds: publish as usual, but set project.verified to false. The page then shows "acceptance not passed" with the real numbers at the top. If it passes, set project.verified to true.
   - Report progress in the chat, for example "acceptance round 2: 0 wrong out of 50, 1 minor error".
   - Evidence archive and check label library: in 5c2 and 5c3, every checking subtask brings back a page snapshot {url, fetched_at, status, final_url, title, published, passages (original paragraphs word for word), quotes, found} and its verdicts. Merge the snapshots into data/archive/<today>.json (merge if it already exists; do not overwrite old entries) and write the archive date on the source. Write the verdicts into data/labels/<today>.jsonl.txt with `python3 tools/append_labels.py <new map id> independent:<today>` (or `accept<round>:<today>`) `claims.json verdicts.json`. The archive (full-page text) and the label library stay local. Do not commit them (copyright).

   5c4. Record cost (used for pricing). Write into project.build_stats {"date","tier","teams_listed","teams_verified","searches","fetches","subagents","minutes"}. Add up searches, fetches and subtasks by the real number of calls. minutes is the real number of minutes from start to publishing. Do not estimate. Write null for what you cannot count.

   5d. Closing data.
   - changes: one entry per team, type "new", date today, summary one Chinese sentence.
   - candidates: teams not fully verified, at most 8.
   - merge_notes: say which request generated this map, and on what date.
   - brief: write it in the format of the daily task, with headline, 3 to 5 points, and you. The headline uses the "goal reached" wording, and point 1 must agree with the data.

   5e. Check and translate.
   - Run `python3 tools/check.py <map.json> <today>` and fix until there are 0 errors.
   - Run `python3 tools/i18n_missing.py <map.json> <en.json> missing.json --prune`. Translate all the missing Chinese into English and merge it into en.json. Run it again, until 0 are missing.
   - Translate into natural, concise American English. Keep numbers, dates, links, S0–S5 and A/B/C/D as they are.
   - Then translate into the other 6 languages (the page supports English, Chinese, Japanese, Korean, Spanish, French, German and Portuguese):
     - Read data/i18n/ja.json, ko.json, es.json, fr.json, de.json, pt.json and tools/i18n_langs.py.
     - Run `python3 tools/i18n_langs.py <output dir> <i18n dir> <en.json of all maps>`. You get a missing_<language>.json for each language.
     - Translate the English each language lacks into that language and merge it into data/i18n/<language>.json. The keys must be word-for-word the English original. You can start one subtask per language to do this in parallel.
     - Run it again, until every language shows "0 missing" and no errors.
     - Do not translate company names, product names, links, numbers, S0–S5 or A/B/C/D. Keep the placeholders {0}, {1} as they are.

   5f. Publish.
   - Append one item to the end of the maps array in data/maps.json: {"id","map":"data/maps/<id>/map.json","en":"data/maps/<id>/en.json","title","title_en","goal","target_stage","created","updated"}. For a rewording, only update goal, target_stage and updated of the existing item.
   - Write the new map's map.json and en.json under data/maps/<id>/ (for a rewording, the original map's files). Write the changed data/i18n/<language>.json files.
   - Run `python3 tools/check.py` and get 0 errors.
   - `git commit` the new map's map.json and en.json, data/maps.json and the changed data/i18n/<language>.json files. Do not commit data/labels/ or data/archive/ (copyright). Push only if the user asked.
   - If git reports a conflict, pull the latest data/maps.json, redo your change on top of it and commit again.

6. Close the request. Do this only after publishing succeeds.
   - Say in the chat (or in the issue) one Chinese or English sentence of result, for example "new map generated: 18 teams, furthest S2; acceptance 50 items, 0 wrong". If acceptance did not pass, say "acceptance not passed: ..." and give the numbers.
   - If you fail partway and cannot finish, say exactly which step you are stuck on, in one sentence. Do not pretend it is done.

7. Tell the user the result in two or three sentences, with the path of the map file:
   - which direction you handled;
   - whether you generated a new map or updated the original;
   - how many teams, and the furthest stage;
   - what is still uncertain.
