本文件是 docs/daily.md 的中文原文（已按仓库版整理）。

# Vantmap 每日任务 v17.1（三层分级 + 发现层 + 有事才核查）

你是 Vantmap 的每日维护员。在本仓库的根目录工作。规则以 docs/pipeline.md 为准（第二节“每日流程”），证据规则见 docs/rubric.md，零错误标准不变。推荐在 Claude Code 里运行（需要 Agent 子任务工具、WebSearch、WebFetch）；也可以用 plugins/vantmap 里的插件一键运行：`/vantmap:vantmap-daily`。

本次运行的目标就是用户给出的目标（命令参数或 GitHub issue）。进度在会话里汇报，或写成 issue 评论。

## 0 准备
（补充约定，v17.1）
- **SINCE**：一律取 feed.json 的 last_run 往前 2 天（没有 feed.json 时取今天往前 7 天，tools/feed.py 以空状态处理）。同一天第二次运行也这样取，去重靠 feed.json。
- **没有子任务工具（Agent）时**：只做机械步骤和第三层（线索），第一层一条都不写；需要写第一层的发现一律进 project.human_queue（why 写“无法派两路判断”）；run_stats 的 by_model 记 0、tokens 记 null，并在 note 里写明。
- **没有年份的发布条目**（GitHub 发布页等）：显示的月日早于窗口的，直接判为旧条目，不进线索；落在窗口内的必须先在带年份的页面（PyPI、CHANGELOG 原文）确认年份，确认不了就进线索、不写第一层。
- **human_queue** 收三类：仲裁仍不确定的；兜底轮查发现、但只有 D 级来源或派不出两路判断的；可能改变阶段的监管或里程碑事件。
- **标注库 verdict** 除 correct / minor_error / wrong / unsupported / unreachable 外，命中分诊和兜底发现还可以用 not_material（不是实质进展）、old_item（窗口外旧条目）、unresolved（进了 human_queue）。
- **失效信源**：连续 3 次运行都只返回 30 天前的旧内容、或打不开的信源，在该信源的 note 里标“疑似失效”，每周一的漏报检查顺带找替代页并更新 project.sources。
- **页面的运行状态**：project.auto_refresh 只有在你按计划定时运行本更新（例如 cron 或定时的 Claude Code 任务）时才设为 true，页面会显示“每天早上自动刷新”；手动运行不改它。
- **每周抽查**：结果追加进 project.audit.weekly（{date,n,correct,minor,wrong,unsupported,unreachable,note}），页面方法区会显示最近一次和距今天数。
- **翻译**：i18n_missing 要加 --prune（promises.json、compare.json 必须放在同一目录）；没有子任务时由主会话翻译，翻完自己抽 10 对检查错位并在汇报里说明。
- **本地文件**：网页全文存档（data/archive/）、标注库（data/labels/）和页面缓存（cache/）只留在本机，不提交（版权原因）。

1. `git pull` 拿到最新数据；读 data/maps.json、每张图的 map.json / en.json / feed.json、tools/*.py、docs/pipeline.md、docs/rubric.md、prompts/。
2. 设 T = 今天日期，SINCE 按上面的约定取（last_run 往前 2 天）。

## 1 每张图依次做（能并行就并行，后台子任务同时不超过 12 个）
A. 发现层：按 project.sources 每 10 个信源派 1 个 **haiku** 子任务，只用 WebFetch，提示词用 prompts/discover_prompt.md，规则见 docs/pipeline.md 步骤 A。
B. `python3 tools/feed.py map.json feed.json items.json T hits/` → hits.json、newleads.json、sweep.json、overflow.json。没有 feed.json 的图第一次是基线模式，不产生命中。
C. 兜底轮查：sweep.json 里的条目派 1 个 **haiku** 子任务，每个 1 次 WebSearch，结果并入命中。
D. 命中核查（提示词 prompts/hit_draft_prompt.md、prompts/hit_judge_prompt.md）：每 3–5 个命中事件派 1 个 **sonnet** 子任务抓取起草（每个网址只抓一次，原文存 cache/）→ `python3 tools/cache_check.py` → 第一层命中派 2 个 **opus** 子任务不联网分别判断（两路都判正确才写入；不一致派第三个 opus 仲裁；仍不确定进 human_queue）；第二层命中只做一路判断（可改内容见 docs/pipeline.md 步骤 C4）。当天写入第一层的新结论按 20% 联网抽查（步骤 C5），写入后按步骤 C6 同步整个条目（产品、资金、说明等字段）。
E. 线索：newleads 追加进 leads；派 1 个 **sonnet** 子任务挑 5 条最相关的打开核对，有 C 级以上来源的升入观察名单（再做一路 opus 判断），无关的删除；90 天未升层的线索删除。
F. 升降：按 docs/pipeline.md 第一节的升降规则；每次升降写进 changes（type promote / demote / watch）。
G. tools/derive.py 派生里程碑和活跃度；tools/check.py 必须 0 错误（含第二层的 key_checked 规则）。
H. 翻译：新中文 → en.json（haiku，翻完抽 10 对检查错位、公司名有没有被换成别家）；新英文 → data/i18n/<6 语言>.json（haiku）。
I. 存档 data/archive/T.json（每个缓存页的 passages 和 sha256），标注库 data/labels/T.jsonl.txt（每条判断一行）。两者只留在本机。
J. **每张图**的 project.run_stats 都追加（子任务和 token 可以写 5 张图合计，但每张图都要有当天这一条，含 hits 和 material） {date, by_model:{haiku,sonnet,opus}, tokens_by_model（按子任务结果里的 usage 累加）, searches, fetches, hits, leads_new}。这是必做项，成本只按这些真实数字报告。

I2. 第一层当天有写入的图，按 prompts/brief_prompt.md 派 1 个 sonnet 子任务重写 AI 解读，check.py 0 错误后才发布。

## 2 发布
运行 `python3 tools/check.py`，全部 0 错误后，`git commit` 改过的文件。先不带 feed.json，也不带 data/archive/、data/labels/、cache/。用户要求时才 push；仓库开了 GitHub Pages 且已 push 的，页面会自动更新。

第一次 commit 不要带 feed.json；成功后，对每张图用同样参数加 `--commit` 再跑一次 tools/feed.py，再单独 commit feed.json。

发布后在会话里（或 issue 评论里）留两行：每张图命中几件、写入几件、升降几次、子任务数（按模型）。

## 3 每周一额外
第一层抽查 50 条（opus 联网）；**金丝雀检查**（从固定信源挑 2–3 条过去一周真实、带日期的条目，不告诉筛选代理，确认发现层把它们找出来了，结果记入 project.audit.canary）；**漏报检查**（派 1 个没做其他工作的代理，换一条搜索路线——换语言、专利、试验登记、论文——独立找过去 7 天地图上没有的团队或新闻，结果记入 project.audit.recall，真实发现作为线索加入）；第二层每张图抽 20 条（opus 联网，含粗判阶段，提示词 prompts/acc_prompt.md），标准 0 错误、小误差 ≤ 1/20，不过就修正并降级有问题的条目。

## 不要做
不删除数据文件；不改仓库设置；遇到需要付费或授权的情况，停下来留言。

## 4 其余例行步骤
- 1a 汇率：WebFetch https://open.er-api.com/v6/latest/USD 更新 data/fx.json（取不到保留旧文件）。
- 1b 新方向请求：仓库版没有请求队列；新地图用 docs/new-map.md 单独运行（见 README“新建一张地图”）。
- 1d/1e 报错和申诉：仓库版从 GitHub issue（标签 correction）读取，每天最多 10 条，派没参与的子任务联网复核，判定写进标注库（round 用 report:T），结果回复在 issue 里。
- 4a–4c 字段与准确性规则：docs/rubric.md、docs/new-map.md 的 5c 和 docs/pipeline.md 第五节写作规则同时适用；第一层新结论仍要双路盲审，资金数字、承诺判定属于关键结论。
- 4d 承诺账本（data/promises.json）、4e 工程活跃度（`python3 tools/signals.py <map.json> <signals.json> <今天>`）：输入有变化时更新。
- 5 AI 解读：只依据第一层（entries）写，观察名单和线索不进解读和统计。
- 6b 仓库版没有需要回写的内容。
- 7 在会话里（或 issue 评论里）汇报：每张图 2–5 句；human_queue 和报错数量写在最后；每周一附上一周按模型分的子任务数。
