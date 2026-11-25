<!-- 每日任务和建图时派子任务用的提示词模板。<工作目录> 换成本次运行的本地目录，{MAP} 等占位符按需替换。 -->
# 重写 AI 解读（brief）

读地图文件 {MAP}（只读）。只写到输出文件 {OUT}。不要用 WebSearch/WebFetch，不要使用任何定时、提醒或触发器工具。

规则：
- 只能依据 map.json 当前的字段写，不能加入数据里没有的事实；只用第一层（entries），观察名单（watch）和线索（leads）不进解读。
- 格式：{"date":"{T}","headline":"一句话结论，要强调的部分用 *星号* 包住","points":[{"text":"…","refs":["条目id"]}],"you":{"text":"…","refs":[]}}
- points 3–5 条，每条不超过 80 字：
  - 第 1 条：主方向（section 为 main）一共几个团队、最远到哪个阶段、有几支到达目标阶段（project.target_stage），必须和数据一致（数字按 entries 现算）。
  - 其余：最接近目标阶段的团队；体量集中在谁手里（按 funding 里的估值或市值）；最近 30 天 changes 里的重要变化；最值得注意的模式。
  - 提到本图验收情况时，只能用 project.audit.acceptance 里的最新数字和 project.verified 的值。
  - 有 project.human_queue 待办的，可以写一句“某项判定等待人工核对”。
- you：“对你意味着什么”，不超过 110 字，以 project.goal 为准，说清哪段还是空白、最该盯谁。
- refs 只能填 entries 里存在的 id。
- 每个数字、日期、阶段都要能在 map.json 里找到；措辞强度和数据一致（“称”“自报”“预印本”照写）。

写完后用 Python 自查：refs 都存在；第 1 条的团队数、最远阶段、到达数与 entries 现算一致。输出只含 brief 对象。回复一行。
