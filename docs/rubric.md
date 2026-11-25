Translated from the Chinese original in docs/zh-CN/rubric.md.

# Rating Rubric v0.7-prod (Product / Startup Edition)

This file is adapted from the AI edition v0.2-ai. The structure and rule numbers are kept. Only the domain-specific evidence requirements are replaced.

## Three dimensions

Each object gets three judgments: stage, activity, and special flags. They are judged separately and not combined into one score. First write down the "target claim" clearly. The same company or product can be at different stages for different features, markets, metrics and points in time.

In this domain the target claim is usually one testable statement. Examples: "a product has been delivered to consumers and can do X", "a company's annual revenue reached N", "a technology has reached commercial mass production", "a platform's daily active users reached N".

### Stage

| Stage | Definition | Minimum evidence for a product / startup |
| --- | --- | --- |
| S0 Proposed | An idea or plan has been made public | The company announces a plan, a concept release, a roadmap, or a vision made public at a funding round |
| S1 Partial progress | There is a prototype, pilot or partial result | A prototype or demo unit, a closed beta or waitlist, a small pilot, running in only one place or with one customer, some features live |
| S2 Claimed done / effective | The claimant publicly says the claim holds. There is no independent test yet | A company launch event or press release, a founder statement, company-reported users or revenue, a claim of "in mass production" or "delivered" |
| S3 Under verification | Independent testing is under way. There is no consensus yet | Measurements by a named independent evaluator or institution, an investigation or inquiry by a regulator, a specific check by a named analyst or investigative journalist based on documents or data, specific allegations in a lawsuit, an independent estimate from a third-party data firm |
| S4 Accepted | Confirmed by independent sources | At least two mutually independent confirmations (for example, audited financial statements or a regulatory filing plus an independent measurement; or results from two independent evaluators), or one formal regulatory finding (such as an approval, certification or ruling) plus one independent confirmation. And there is no unresolved specific objection |
| S5 Consolidated | Has become an industry standard or infrastructure | Has become an industry standard or common specification, a widely adopted mainstream solution, or has been audited and disclosed continuously over many years and used by peers as a benchmark |

### Activity

Activity looks at the time of the latest "substantive progress" before the cutoff date. Substantive progress means: a new product or new version release, start of mass production, delivery, funding, a regulatory decision, audited financial statements, an independent evaluation result, a substantive court ruling, a product being taken off the market, or the company closing. The first public showing of a new generation of product counts as a "new version release". Showing or demoing the same generation again does not. Media coverage, interviews and repeated promotion of old results do not count.

| Activity | Window |
| --- | --- |
| Active | Substantive progress within 6 months |
| Slowing | 6 to 18 months |
| Stalled | More than 18 months, and there is a recognized obstacle (such as regulatory rejection, funding cut-off, or inability to mass-produce) |
| Abandoned | The company clearly ends the product or project, the product is taken off the market, the company goes bankrupt or closes; or the company later withdraws or replaces that specific claim in its own statements |

Objects that have reached S4 or S5 are not rated for activity (write "—").

Activity looks only at the progress of the target claim's own object. Progress on the same company's other products, other markets, other product lines or other sites cannot be used to judge this object "active". If the latest substantive progress is more than 18 months ago and there is a recognized obstacle, judge "Stalled". If it is more than 18 months ago but there is no recognized obstacle, judge "Slowing" and state the length of the gap in the notes.

### Special flags (several allowed, or none)

- Disputed: a named expert, analyst, investigative journalist (based on documents or data), regulator or litigant has publicly raised a specific objection, and it is unresolved.
- Withdrawn / overturned: the claim has been formally rejected. For example, a regulator finds it false, a court rules fraud, the company restates its financials and removes the number, the product is recalled or taken off the market, or an independent test decisively shows it cannot be done.
- Known gap: the source text itself names a specific unresolved problem (for example "this figure is unaudited", "regulatory approval is still required before launch", "bulk delivery has not started", "operates only on test roads"), and the statement comes from the claimant, a regulator or an evaluator. A general "the outlook remains uncertain" does not count. A specific doubt raised only by an outside commentator gets the flag "Disputed". Conditions still missing for the next level (for example a regulation published but not yet in force, a standard with fewer than three adopters, only one year of data) are already reflected by the stage itself and do not get this flag.
  - Examples where the flag applies: the claimant says "this figure is unaudited"; a regulator names "a missing safety analysis"; an evaluator says "tested in only one scenario"; the company admits "part of the demo was remotely operated by a human".
  - Examples where the flag does not apply: "not yet approved", "not yet delivered", "construction permit not yet issued", "mass production planned for 2028", "final investment decision not yet made". These are steps still missing before the target is met. The stage and the "latest milestone of its own" already express them.
- Gap fixed: a problem was found in the target claim itself and was later resolved by new data, a correction, a supplementary audit or supplementary regulatory material. A quality problem in individual units that was fixed by a recall is not a gap in the claim itself and is not flagged.
- Denied claim exists: someone claims it holds, and experts or the media widely reject it, but there is no formal finding, ruling or decisive counter-evidence. If there is already a formal finding or decisive counter-evidence, use "Withdrawn / overturned" instead. The two flags are not applied together.
- Conditional: the claim itself is explicitly conditional on something that has not yet happened (for example "will launch in a given year if regulatory approval is granted", "provided funding is in place"). Data not being public does not make it conditional. If the author points it out, use "Known gap".
- Scope mismatch: the claimant's own wording clearly states a conclusion beyond the evidence. Typical cases: calling a demo or staged shot a mass-production capability; calling a pilot or single-city result a full launch; calling reservations, letters of intent or sign-ups sales or active users; calling gross transaction value revenue; calling one-off revenue recurring revenue. If only the media exaggerate and the claimant's own wording is accurate, do not flag.
- Prior work exists: the claimed "first" was in fact achieved by others earlier.
- To be verified: there are signs that the conclusion may have been overturned, but the evidence cannot confirm that it concerns this specific claim.

## Scoring rules

The core rule is "take the lower level": judge the level that the evidence can support, and no higher.

### Evidence grades

| Grade | Content |
| --- | --- |
| A Primary, formal | Regulatory filings (such as SEC 10-K, S-1, 8-K), audited financial statements, regulator decisions or certifications, court documents, official product documentation or release notes, formal reports from independent evaluation bodies |
| B Primary, informal | Company blog or press release, founder talks or social media posts, the company's own marketing material |
| C Secondary, authoritative | Comments by named industry analysts or experts, professional media (citing named sources or documents), investigative reporting (based on documents or data), hands-on tests by professional review media |
| D Secondary, general | General news, social media reposts, aggregator sites |

### Decision rules

1. Use only evidence from before the cutoff date. This includes your own memory: anything not in the evidence package cannot be used.
2. A claim alone reaches at most S2. A company press release saying "in mass production" or "100 million users" is still only a claim.
3. S3 needs action by a third party: at least one piece of grade C or better evidence showing that a non-claimant is testing or evaluating this specific claim (independent measurement, regulatory investigation, document-based investigative reporting, a specific check by a named analyst). A journalist repeating the company's statement does not count.
4. S4 needs two things at the same time: first, the independent confirmation required for S4 in the stage table; second, no unresolved specific objection.
5. Approval or launch does not override a dispute: as long as there is an unresolved specific objection, add "Disputed", and the stage is at most S3.
6. One object is rated on one target claim only. Results from other products, other markets, other metrics or other points in time can support the target claim to S1 at most, and cannot raise it further.
7. Grade D evidence alone cannot support any upgrade.
8. If you cannot tell between two levels, judge the lower one, write confidence "Low", and state what evidence is missing. Confidence reflects only how strongly the evidence supports the conclusion. "The evidence may be incomplete" is not in itself a reason to lower confidence.
9. The stage records the highest level the claim ever reached. The outcome is shown by a flag. Being rejected does not by itself raise or lower the stage. If a third-party test already existed before the cutoff, judge S3 plus "Withdrawn / overturned". If the claim was withdrawn before any third-party test, judge S2 plus "Withdrawn / overturned". A rejected claim cannot be upgraded to S4 or S5 again.
9a. Ongoing work: releasing a new version, a new delivery or a new financial report counts as substantive progress. Merely "about to launch" or "still working on it" does not.
9b. A claim that was never claimed to hold, and was abandoned or rejected with only a prototype, is judged by the last valid evidence before it was rejected (usually S1), plus "Withdrawn / overturned".
9c. The rejection itself can be the third-party test. For example, a regulatory investigation, a failed independent test, or a short-seller report that points to fraud based on documents all count as third-party tests. A claim overturned this way is therefore judged S3.
9d. If the claimant itself clarifies that a demo or a number does not represent the target capability (for example, admits the demo was remote-controlled or staged, or explains that the number is reservations and not sales), this is neither an overturn nor a claim. Judge the stage by the remaining evidence and add "Known gap".
10. Check the scope of standards and certifications: certification, approval or adoption is evidence for S4 or S5 only if what was certified, approved or adopted matches the target claim.
11. A repeated claim can prove that the claim exists: if a third party's grade A or B document mentions that someone claimed the target conclusion, it can support S2. It cannot prove the scope or correctness of the claim.
12. Do not downgrade when an overturn is unconfirmed: if there are only signs and it cannot be confirmed that they concern this specific claim, judge the stage as usual, add "To be verified", and write confidence "Low".
13. Unable to open is not the same as not existing: if there are signs that a primary source exists but it cannot be opened, write it under "Unverified primary sources". If at least two mutually independent reports clearly point to the same document, you may accept that "the claim exists". This supports S2, with confidence "Low".
14. Market-position claims (this applies only to claims of the type "who is first or dominant". It does not apply to the standard-type claims in rule 15) (such as "a company is number one / dominant in a market", "a technology holds the vast majority of share"). To judge S5, you need at least two mutually independent non-claimant sources (such as an independent data firm or a regulator's finding), covering several years. Metrics a company reports itself in filings such as 10-K or S-1, its self-described "leader" status, and third-party rankings repeated by the company all count only as claims (rules 2 and 11). With only one independent source, or only one year covered, the maximum is S4. When the operator of a product or system is also the publisher of its data (for example, a central bank that both runs a payment system and publishes its usage statistics), that data counts as a claimant source and not as an independent source.
15. S5 has four paths. Choose one by claim type. Do not apply the requirements of one path to another type of claim:
   (a) Market-position claims: follow rule 14.
   (b) Voluntary industry standards (published by a standards body, adopted voluntarily by vendors): formally published, and natively adopted in shipping products by at least three mutually independent major vendors: judge S5. Products that are only "compatible / Ready" and not natively adopting do not count. With fewer than three adopters, judge S4. Multi-year data is not required.
   (c) Mandatory standards or regulatory frameworks (set by law, regulation or formal regulator guidance, already in force): in force and with an enforcement or compliance record (such as a regulator enforcing it, or vendors changing products because of it): judge S5. The number of vendors is not required. Published but not yet in force: judge S4.
   (d) Protocols, technologies or practices published by a body that is not a standards organization: adopted by default (not as an optional feature) in at least three mutually independent major products: judge S5.

### Output format (one paragraph per case)

```
案例：P01
目标命题：（照抄）
阶段：S0～S5
活跃度：活跃 / 放缓 / 停滞 / 已放弃 / 无法判定 / —（S4、S5）
特殊标记：无，或列出
置信度：高 / 中 / 低
依据：引用证据编号，每条一句话说明满足哪条规则
缺口：要再升一档还缺什么证据
未核实的一手来源：无，或列出
```

(English glossary for the field labels above. 案例 = Case. 目标命题 = Target claim, copied as is. 阶段 = Stage. 活跃度 = Activity: 活跃 Active / 放缓 Slowing / 停滞 Stalled / 已放弃 Abandoned / 无法判定 Cannot determine / — for S4 and S5. 特殊标记 = Special flags: none, or list them. 置信度 = Confidence: 高 High / 中 Medium / 低 Low. 依据 = Basis: cite evidence numbers, one sentence each saying which rule is met. 缺口 = Gap: what evidence is missing for one more level. 未核实的一手来源 = Unverified primary sources: none, or list them.)


## New in v0.7 (added after the 2026-11-05 review)

This version comes from an item-by-item review of a map. The problems fell into the following groups.

16. Conflicting sources: when two sources say opposite things about the same fact (for example one says "shipped to customers" and the other, an order page, still says "deliveries start next year"), go with the higher-grade source. If the grades are equal, go with the newer date. Write the other one into the evidence and mark "To be verified". A more optimistic statement from a grade D source alone cannot move a level up (rule 7).
17. Entity check: before judging, confirm that the evidence is about the same company and the same product. Keep brands, subsidiaries, partners and products with the same name separate. An entry with the wrong subject is removed directly, and one record of type `bad` is added to changes.
18. Direction check: if the object does not match the map's goal (project.goal, finish_def, domain_rules) — a different form, or a different main use — put it under "adjacent directions". Judge the stage as usual, but do not count it in the main-direction statistics.
19. Estimated dates: if only the month or a time span is verified, write the date down to the month (YYYY-MM). If it is estimated from a known day (such as the opening day of a trade show), write "estimated from X" in the judgment note.
20. Company-level events (listing, financial reports, funding) can update last_progress and activity, but cannot on their own support a stage upgrade. The stage looks only at progress related to the target claim.
21. Machine check: run tools/check.py before publishing, and fix every "error" before publishing. It checks fields, stage against evidence grade (rule 7), whether activity agrees with the date of the latest progress, whether the entries cited by the AI brief exist, and whether the numbers in the brief match the data.
