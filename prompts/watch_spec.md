<!-- 每日任务和建图时派子任务用的提示词模板。<工作目录> 换成本次运行的本地目录，{MAP} 等占位符按需替换。 -->
# 观察名单条目写作规则（Vantmap v2 第二层）

地图目标：见 {MAP}/map.json 的 project.goal 和 project.finish_def。

第二层只保证两件事：**团队/项目确实存在**；**一句话描述和来源网页一致**。阶段只是粗判。

## 每个团队
1. 用 WebSearch 找到它，最多 WebFetch 打开 2 个网页（优先官方页、论文页、GitHub、官方新闻稿）。
2. 让 WebFetch 返回**原文逐字句子**（prompt 里写明 "Quote the exact sentences verbatim, do not paraphrase"）。
3. 写一个对象：

```json
{"id":"kebab-case","name":"中文名或通用名（机构）","short":"短名","branch":"分支 id",
 "stage_rough":"S0|S1|S2|null",
 "one_line":"一句中文描述，只写来源原文里有的内容，不写推断",
 "why":"为什么不在主图（偏离目标 / 只是工具或数据集 / 阶段或适应症的事实 / 还没做完整核对；不要写“规模小”这类没有来源的判断）",
 "sources":[{"url":"...","quote":"原文逐字，<=25 个英文词或 <=40 个汉字","grade":"A|B|C|D","date":"YYYY-MM-DD 或 YYYY-MM 或 null","passage":"WebFetch 返回的包含 quote 的原文段落（逐字，100-600 字符）"}],
 "checked":"2026-11-23","added":"2026-11-23"}
```

## 规则
- `one_line` 的每个事实都要能在 `passage` 里找到。不写“领先”“首个”等原文没有的评价；原文这么说就写“自称”。
- `quote` 必须是 `passage` 的逐字子串。
- 日期只写网页上看到的；只看到月日没有年份时写 null。
- 等级以 rubric.md 和本图 project.domain_rules 为准：A 同行评审论文、监管文件和决定、官方产品文档和发布说明（含代码仓库的发布页和 README）；B 公司新闻稿、博客、营销页、预印本、机构库记录；C 专业媒体原创报道；D 转载、聚合站、自媒体、招聘帖。
- 粗判阶段：S0 只有计划或概念；S1 有原型/论文/开源代码/试点；S2 自己宣称已做到地图目标（很少）。拿不准写 S0 或 S1 中较低的。
- 找不到可打开的页面、或打开后发现和目标无关的，不写条目，放进 `dropped` 并写原因。
- 已在主图的团队（见 entries_index.json）不要重复写。

## 输出
写到指定的 JSON 文件：`{"searches":n,"fetches":n,"watch":[...],"dropped":[{"name":..,"why":..}]}`
