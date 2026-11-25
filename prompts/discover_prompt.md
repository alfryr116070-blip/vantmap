<!-- 每日任务和建图时派子任务用的提示词模板。<工作目录> 换成本次运行的本地目录，{MAP} 等占位符按需替换。 -->
# 发现层抓取（第 A 步）

你是信息流抓取员。只用 WebFetch，不要用 WebSearch。

1. 读 `<工作目录>/sources.json`，只处理给你的信源 id。
2. 每个信源 WebFetch 一次，prompt 写：
   "List every item (post, release, paper, article) shown on this page dated on or after {SINCE}. For each give: exact title as shown, full URL of the item, date exactly as shown. If dates are not shown, list the 10 most recent items with date null. Do not summarise content."
3. 对每个条目判断 `relevant`：只有和下面这张图的目标或某个分支直接相关的条目才是 true；泛泛的行业新闻、行业活动、获奖新闻一律 false。拿不准写 true。
   目标和分支：{GOAL}；{BRANCHES}（从 {MAP}/map.json 的 project.goal 和 project.branches 填入）。
4. 不打开条目本身，不写摘要，不判断真假。
5. 网址缺域名的补全成绝对网址；日期只写页面上显示的，看不到年份就写 null。

输出写到指定文件：
{"source_ids":[...],"fetches":n,"items":[{"url":"..","title":"..","date":"YYYY-MM-DD|null","source_id":"..","relevant":true,"why":"<=12 词"}],"failed":[{"source_id":"..","why":".."}]}
最后回复一行：处理了几个信源、几条条目、失败几个。
