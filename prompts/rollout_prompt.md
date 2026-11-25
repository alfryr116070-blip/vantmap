<!-- 每日任务和建图时派子任务用的提示词模板。<工作目录> 换成本次运行的本地目录，{MAP} 等占位符按需替换。 -->
# 迁移到三层结构：观察名单（第二层）

你在给一张 Vantmap 研究进度地图建观察名单。地图目录：<工作目录>/{MAP}/。
- 目标和现有分支：读 {MAP}/map.json 的 project.goal / project.branches（只读，不要改 map.json）。
- 主图团队：{MAP}/entries_index.json（跳过它们，以及换个名字的同一项目）。
- 写作规则：prompts/watch_spec.md。地图目标用本图的 project.goal；规则全部照做（每团队最多打开 2 页、quote 是 passage 的逐字子串、one_line 只写 passage 里有的、组织名/数字/日期必须在 passage 里、没看到年份就写 null、要求 WebFetch 逐字返回原文）。

任务：
1. 先处理这些已有候选：{CANDS}
2. 再补 8–14 个**和目标相关、但规模较小、偏一点或主图还没收**的团队，优先覆盖现有分支里团队少的地方。
3. 可以新增最多 2 个更宽的分支（id 用英文小写，name/desc 用中文），让地图覆盖面更大；新增分支的团队都放进观察名单。
4. 每个团队写一个观察名单对象（格式见 spec），branch 必须是现有分支 id 或你新增的分支 id。
5. 只有 D 级来源的团队不要写进 watch，放进 `leads_only`：[{"name","url","why"}]。

输出 <工作目录>/{MAP}/watch.json：{"searches":n,"fetches":n,"new_branches":[{"id","name","desc"}],"watch":[...],"leads_only":[...],"dropped":[{"name","why"}]}。
写完后用 Python 自查每条 quote 是 passage 的子串、日期年份出现在 passage 里（不满足就把 date 改 null 或修 quote）。不要使用任何定时、提醒或触发器工具。回复 3 行摘要。
