本文件是 docs/new-map.md 的中文原文（已按仓库版整理）。

# 建一张新地图（按需调研）

处理一条新方向请求。请求就是用户给出的目标：命令参数或 GitHub issue。请求可以带这些字段：text（新方向）、type（"goal" 或 "target"）、target_stage、map（指哪张地图）、tier（"quick" 或 "full"）、draft。进度在会话里汇报，或写成 issue 评论。不要停下来提问。

0. 接收请求。
   - 一次只处理 1 条请求。
   - 每完成一个大步骤，在会话里（或 issue 评论里）汇报一次进度，例如“开始调研”。

1. 读取现状。
   - 读 data/maps.json（地图列表）、docs/rubric.md、tools/check.py、tools/i18n_missing.py，以及请求里 map 字段指向的那张地图的数据文件和英文翻译文件。
   - 完整读一遍 docs/rubric.md，阶段 S0–S5 和证据等级 A–D 都按它判断。
   - 地图的文件路径以 maps.json 里的 map / en 字段为准。
   - 请求没有 map 字段时，指的是 maps.json 里的第一张地图。

2. type 为 "target"（只改终点线）。
   - 把那张地图的 project.target_stage 改成请求里的 target_stage。
   - 运行 tools/check.py，写入这张地图的数据文件。
   - data/maps.json 里这张地图的 target_stage 也同步改掉。
   - 两个文件一起 commit，在会话里汇报“目标阶段已改为 S?”。然后跳到第 6 步。

3. type 为 "goal"：先判断是"改措辞"还是"换领域"。
   - 新方向 text 和原地图 project.goal 在同一个领域、主要对手基本相同（例如只是换个说法、收窄或放宽一点）：算改措辞，做第 4 步。
   - 领域不同（例如从阳台植物养护设备换成城市垂直农场）：算换领域，做第 5 步，生成一张新地图，原地图保留。
   - 判断结果在会话里汇报，例如“这是一个新领域，正在生成新地图”。

4. 改措辞：更新原地图。
   - 把 project.goal 改成新方向，旧目标写进 merge_notes。
   - 请求带了 target_stage 的，同时更新 project.target_stage。
   - 对已有条目重新判断 section：不再属于主方向的改为 adjacent，不删除。
   - 补查新方向下的新团队：最多 15 次搜索，英文为主，中国团队加一次中文搜索。
   - 新条目按第 5c 步的字段要求填写，changes 追加记录。
   - 之后做第 5e、5f 步，但写入的是原地图的文件。

5. 换领域：生成新地图。
   - 全部搜索加起来不超过 150 次。同时运行的子任务不超过 15 个。只用打开过的网页，不凭记忆。

   5a. 定义地图。
   - id：英文小写短横线，例如 balcony-plant-care，不能和 maps.json 里已有的重复。
   - 文件路径：data/maps/<id>/map.json 和 data/maps/<id>/en.json。
   - project 字段：
     - title：中文短标题；
     - goal：把用户的方向写成一句清楚、可判断的中文目标；
     - idea：用户原话；
     - created 和 updated：今天；
     - rubric：同 rubric.md 版本；
     - target_stage：用请求里的 target_stage；没有就按这个领域选最合理的一档，并写进 merge_notes 说明理由；
     - finish_def：一句中文，说清在这个领域里"到达终点线"具体指什么，例如"有产品卖给家庭，并能同时自动浇水和补肥"。
   - branches：3 到 5 条路线，格式 {"id","name","desc"}，最后一条固定是 {"id":"adjacent","name":"相邻方向","desc":"…"}。
   - layers：这个领域的产业链环节，5 到 6 个中文短词，例如"传感器""执行机构""控制软件""量产""渠道""售后"。条目的 role 只能用这里的词。
   - domain_rules：这个领域特有的判定规则，3 到 8 条中文，写进 project.domain_rules，所有子任务和核查员都按它判定。至少说清：
     - 什么算这个领域的“实质进展”（例如消费类设备：可用原型进入真实家庭、通过认证、首批付费交付、新产线投产；不算：概念视频、展会演示、计划）；
     - S1–S5 在这个领域各对应什么（例如 S2＝公司宣布达到目标终点；S4＝监管批准加独立确认）；
     - 容易混淆、必须分清的说法（例如“获批开展试验”≠“获批上市”，“完成入组”≠“达到终点”，“适应症 A 获批”≠“适应症 B 获批”）；
     - 这个领域的 A 级来源是什么（例如监管机构数据库、标准机构的认证名单、同行评审论文）。

   5b. 摸底。
   - 先派 1 个 Opus 子任务做“深度研究初稿”：只给它这个方向的问题（不给已有数据），最多 30 次搜索，写出带来源链接的团队名单和逐条结论（{team, claim, urls}）。2026-11-06 的对比显示，这样的初稿完全正确率约 95%，可以大幅减少后面的搜索。初稿不是证据：它的每条结论照样要按 5c、5c2、5c3 打开原网页核验，没依据的删掉。
   - 再派最多 4 个子任务补摸底，合计不超过 20 次搜索，英文为主、中文补充，专门找初稿漏掉的（尤其是中国和非英语来源的团队）。
   - 找出 12 到 25 个正在推进这个目标的团队，包括公司、实验室、大公司项目、政府或基金资助的计划，也包括已宣布但还没发表成果的。
   - 请求里如果有 draft 字段（用户提供的分析框架：routes、stages、finish、evidence、questions，不含团队），可以参考它定 branches、finish_def 和 domain_rules，但都要按这个领域重新判断；框架不是证据。旧格式的 draft 若带 entries，只能当摸底线索，核实不到的不放进图。
   - 名单要广撒网：即使是速览，也要先把能找到的团队都列出来（只要名称、一句话、一个链接），再挑要核实的。
   - 先列名单，去掉重复的和明显不相关的。
   - 在会话里汇报进度，例如“找到 18 支团队，正在逐个核实”。

   5b1. 漏报检查：名单列完后，另派 1 个没参与 5b 的子任务，换一条不同的搜索路线（换语言、搜专利、搜招聘或招投标、搜行业名录），最多 10 次搜索，再列一遍名单。两份名单的差异写进 project.audit.recall = [{"date","found_new","names"}]，新找到的并入名单。

   5b2. 速览还是完整版（请求的 tier 字段；没有就按 "quick"）。
   - tier 为 "quick"（速览，默认）：从名单里按固定标准挑 5 到 8 个“最主要”的团队，只核实这几个：
     - 每条路线（branch）至少 1 个代表；
     - 其余按这个顺序补满：阶段证据最靠前的 → 有交付或获批的 → 融资或市值最大的 → 最近 6 个月最活跃的；
     - 挑选理由写进每个条目的 pick_reason（中文一句，例如“该路线阶段最靠前”）。
     - 名单里其余团队写进 project.roster：[{"name","one_line","url"}]（只放名称、一句话和一个打开过的链接，不判阶段、不写数字）。页面会显示“找到 N 个团队，这里列出最主要的 M 个”。
     - project.tier 写 "quick"。5c、5c2、5c3 只对挑出来的条目做；验收抽样不足 50 条就全部核对。
   - tier 为 "full"（完整版，用户要求时）：名单里的团队全部核实，project.tier 写 "full"，roster 清空；已经核实过的速览条目直接沿用，不重查。

   5c. 逐个核实。
   - 每日任务（docs/daily.md）里的“准确性规则”同样适用：B/C 级来源放进 evidence；许可证打开 LICENSE 核对；转载和聚合站算 D；每条证据带 quote（原文逐字一句）和 verified 日期；最近进展只算实质进展。
   - 每个团队派 1 个子任务，最多 4 次搜索，按 data/map.json 里条目的字段结构填写：
     - 基本信息：id、name、short（最多 14 字）、section（main 或 adjacent）、branch；
     - 进度：stage、milestone、milestone_grade、activity、last_progress、flags、confidence、evidence（[{grade,date,text,url}]，至少 1 条）、note、checked（今天）；
     - 资金：funding，口径与 data/map.json 相同；kind 取 startup、listed、project，也可以是 academic（学术或公益资助），查不到填 null；
     - 分工与产品：role（{layers,main}，只能用 5a 的 layers）、product（{name,intro,status}）；
     - 公开成果：openness（代码、数据、模型、论文、试验登记，kind 取 code、weights、dataset、paper、sdk、hardware、registry，只列打开核实过的链接，每项带 use 字段）、closed_note；
     - 与用户的关系：relation，一两句。
     - 两种缺口 gaps（页面分开显示，不能混）：
       - gaps.field：这个团队要到下一档和目标阶段，按本图阶段定义还缺什么（1–3 条，例如“要到 S4：公开资料中未见独立的长期无病生存数据”）。写之前要搜过、确认公开资料里确实没有；如果其实有、只是地图还没打开核对，就不是 field，而是 ours。
       - gaps.ours：地图自己还没做完的功课（0–3 条，例如“FDA 批准页还没打开核对，目前只有公司新闻稿”“阶段只靠 D 级来源”），找到一手链接的写进 url。
       - 格式：{"field":[{"text","basis_url"}],"ours":[{"text","url"}]}；每日任务会优先补 ours。
   - 规则 7 原文：“D 级证据不能单独支撑任何升档”。只有 D 级证据的团队，阶段为 S0。

   5c2. 独立核对（零错误标准）。
   - 所有团队写完后，另派没有参与 5b、5c 的子任务（不要用 haiku），每个最多核对 20 条结论，逐条打开原网页判定“正确 / 小误差 / 错误 / 没有依据”。
   - 只保留判“正确”的；“小误差”改到和原文一致；“错误”和“没有依据”的删除。删完证据后，阶段按规则重新判定（只剩 D 级的判 S0）。
   - 关键结论双路盲审（可信度标准 v1.0 第四层）：支撑阶段的证据、资金和市值数字、只靠 D 级来源的结论，要再派第二个互不知情的子任务（提示词和搜索路径不同、看不到原阶段和第一路判定）独立判一次。两路都判“正确”才保留；两路不一致的由第三个子任务按规则编号仲裁，仍不确定的不写入，记进 project.human_queue。分歧都写进标注库（round 用 dual:<今天>）。
   - 每条来源都必须有 quote（原文逐字一句）和 verified 日期，否则 tools/check.py 会报错，不能发布。

   5c3. 验收关（不合格不算“已核实”）。
   - 派 2 到 3 个没有参与 5b、5c、5c2 的子任务（不要用 haiku），从这张图的全部结论（证据、资金来源、资金数字、公开成果、里程碑、产品介绍）里用固定随机种子抽 50 条（不足 50 条就全部核对），按“正确 / 小误差 / 错误 / 没有依据 / 打不开”逐条打开原网页判定，判定时遵守 project.domain_rules。
   - 合格标准：错误和没有依据都是 0，小误差不超过 4%（50 条里最多 2 条）。
   - 不合格：按核查结果改正或删除（删证据后按规则重判阶段），再换一批没参与过的子任务、换随机种子重新抽 50 条验收；最多 3 轮。
   - 结果写进 project.audit = {"date","pool","n","correct","minor","wrong","unsupported","accuracy","lower95","stage_agree","stage_n","target":"96%","acceptance":{"date","n","correct","minor","wrong","unsupported","unreachable","lower95","rounds"}}，所有改动写进 corrections。lower95 用 Clopper-Pearson 双侧 95%（没有错误的比例）。
   - 3 轮后仍不合格：照常发布，但把 project.verified 设为 false，页面会在顶部显示“验收未通过”和实际数字；合格时 project.verified 设为 true。
   - 在会话里汇报进度，例如“验收第 2 轮：50 条里 0 错误、1 条小误差”。
   - 证据存档和核查标注库：5c2、5c3 每个核对子任务都带回网页快照 {url, fetched_at, status, final_url, title, published, passages（逐字原文段落）, quotes, found} 和判定。快照合并成 data/archive/<今天>.json（已有就合并，不覆盖旧条目），来源上写 archive 日期；判定用 python3 tools/append_labels.py <新地图id> independent:<今天> / accept<轮次>:<今天> claims.json verdicts.json 写入 data/labels/<今天>.jsonl.txt。存档（网页全文）和标注库只留在本机，不提交（版权原因）。

   5c4. 记录成本（用于定价）。在 project.build_stats 写 {"date","tier","teams_listed","teams_verified","searches","fetches","subagents","minutes"}：搜索、抓取、子任务按实际调用次数累加，minutes 从开工到发布的实际分钟数。不要估算，数不清的写 null。

   5d. 收尾数据。
   - changes：每个团队各一条，type 为 "new"，date 为今天，summary 一句中文。
   - candidates：没核实完的最多 8 个。
   - merge_notes：写明这张图是由哪条请求在哪天生成的。
   - brief：按每日任务的格式写，有 headline、3 到 5 个 points、you。headline 用“达成目标”的说法，第 1 条要和数据一致。

   5e. 检查和翻译。
   - 运行 python3 tools/check.py <map.json> 今天，改到 0 个错误。
   - 运行 python3 tools/i18n_missing.py <map.json> <en.json> missing.json --prune，把缺的中文全部翻成英文，合并进 en.json，再运行一次，直到缺少 0 条。
   - 翻译用自然简洁的美式英语，数字、日期、链接、S0–S5、A/B/C/D 原样保留。
   - 再翻成其他 6 种语言（页面支持英、中、日、韩、西、法、德、葡）：
     - 读 data/i18n/ja.json、ko.json、es.json、fr.json、de.json、pt.json 和 tools/i18n_langs.py。
     - 运行 python3 tools/i18n_langs.py <输出目录> <i18n 目录> <所有地图的 en.json>，得到每种语言的 missing_<语言>.json。
     - 把每种语言缺的英文翻成该语言，合并进 data/i18n/<语言>.json；键必须是逐字一致的英文原文。可以每种语言派一个子任务并行做。
     - 再运行一次，直到每种语言都“缺少 0 条”且没有错误。
     - 公司名、产品名、链接、数字、S0–S5、A/B/C/D 不翻译；占位符 {0}、{1} 原样保留。

   5f. 发布。
   - 在 data/maps.json 的 maps 数组末尾追加一项：{"id","map":"data/maps/<id>/map.json","en":"data/maps/<id>/en.json","title","title_en","goal","target_stage","created","updated"}。改措辞的情况下，只更新原有那一项的 goal、target_stage、updated。
   - 把新地图的 map.json、en.json 写到 data/maps/<id>/ 下（改措辞则写原地图的文件），并写入有改动的 data/i18n/<语言>.json。
   - 运行 `python3 tools/check.py`，必须 0 错误。
   - `git commit`：新地图的 map.json、en.json、data/maps.json，以及有改动的 data/i18n/<语言>.json。不要提交 data/labels/ 和 data/archive/（版权原因）。用户要求时才 push。
   - 有冲突时，拉取最新的 data/maps.json，在最新内容上重做修改再 commit。

6. 结束请求。只在发布成功后做。
   - 在会话里（或 issue 里）用一句话写结果，例如“新地图已生成：18 支团队，最远到 S2；验收 50 条 0 错误”；验收未通过的要写明“验收未通过：……”并给出数字。
   - 中途失败、无法完成：用一句话写清卡在哪一步，不要假装完成。

7. 告诉用户结果，两三句话，附地图文件路径：
   - 处理了哪条方向；
   - 生成了新地图还是更新了原地图；
   - 有多少团队、最远到哪个阶段；
   - 还有哪些不确定的地方。
