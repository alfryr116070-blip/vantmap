<!-- 每日任务和建图时派子任务用的提示词模板。<工作目录> 换成本次运行的本地目录，{MAP} 等占位符按需替换。 -->
# 命中核查 · 判断（第 C3 步，opus，不联网）

**不要用 WebSearch 或 WebFetch。** 只读给你的起草文件和 `<工作目录>/cache/` 里对应的缓存原文（key 计算方式见起草文件旁的 .check.json，或 `sha1(url)[:16]`）。

按 `rubric.md 和 docs/new-map.md 第 5c 步` 的证据等级和阶段规则，对每条 `material:true` 的起草逐项判断：
- text / one_line_new 和原文是否一致；quote 是否支持 text；日期是否和页面显示一致；等级是否正确；progress 是否成立；阶段建议是否符合阶段规则。
- 缓存原文只是抓取工具返回的摘录：**不要下“页面未提 X / 页面没有 X”这类否定结论**，只能写“缓存中未见 X”，并把该条标 `needs_online: true`，交给联网核对；涉及否定性结论（未提及、不存在、未批准、待定）的一律如此。
- 每项输出：正确 / 小误差（措辞略强、少了限定词等，不改变结论）/ 错误 / 没有依据。

{路径说明}

输出 JSON 数组到指定文件：`[{"id","event","verdict":"correct|minor|wrong|unsupported","items":{"text":..,"quote":..,"date":..,"grade":..,"progress":..,"stage":..},"fix":"建议的改法，可为空","note":".."}]`
回复一行：几条，各类判定几条。
