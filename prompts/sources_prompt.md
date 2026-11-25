<!-- 每日任务和建图时派子任务用的提示词模板。<工作目录> 换成本次运行的本地目录，{MAP} 等占位符按需替换。 -->
为 Vantmap 地图 <工作目录>/{MAP}/ 建发现层的固定信源清单。目标和分支见 {MAP}/map.json 的 project（只读）；主图团队见 {MAP}/entries_index.json。
要 25–45 个**便宜模型每天只用 WebFetch 打开就能看到新动态**的网页：各重要团队的官方新闻/博客页或 GitHub releases 页（尽量覆盖主图团队）、2–4 个领域媒体栏目或期刊/预印本列表页、监管或注册库的列表页（如适用）。
每个候选 WebFetch 一次，确认能打开且列出带日期的条目（打不开或没有日期的放进 failed）。
输出 <工作目录>/{MAP}/sources.json：{"fetches":n,"sources":[{"id","name","url","kind":"blog|news|releases|arxiv|journal|registry|other","covers":[entries_index 里的 id],"lang","note"}],"failed":[{"url","why"}],"uncovered":[没被覆盖的主图 id]}。不要使用任何定时、提醒或触发器工具。回复 3 行摘要，写明覆盖了多少主图团队。
