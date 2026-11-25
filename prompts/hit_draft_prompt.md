<!-- 每日任务和建图时派子任务用的提示词模板。<工作目录> 换成本次运行的本地目录，{MAP} 等占位符按需替换。 -->
# 命中核查 · 抓取起草（第 C1 步，sonnet）

读：`rubric.md 和 docs/new-map.md 第 5c 步`（证据规则）、`docs/pipeline.md` 第五节（写作规则，必须遵守）、给你的命中事件和对应条目（map.json 里同 id 的 entries / watch 项）。

对每个命中事件：
1. WebFetch 事件网址**一次**，prompt 要求 "Return verbatim: the page title, the publication date exactly as shown, and every sentence relevant to {团队名} — copy sentences exactly, no paraphrase."
2. 把结果存进 `<工作目录>/cache/<key>.json`，key = `python3 -c "import hashlib,sys;print(hashlib.sha1(sys.argv[1].encode()).hexdigest()[:16])" <网址>`：
   `{"url":..,"fetched_at":"{T}","title":..,"published":"页面上显示的日期原文","passages":["逐字句子", ...]}`
3. 判断这件事是否是**实质新进展**（新版本、新论文、新产品、融资、合作、基准结果、阶段变化）。不是的写 `{"id":..,"event":..,"material":false,"why":..}`。
4. 是的，按条目现有格式起草改动：
   - 第一层：`{"id":条目id,"tier":1,"event":..,"material":true,"add_evidence":{"grade","date","text","url","quote","progress":true|false},"milestone":"可选","stage_suggest":"Sx 或 null","stage_why":"..","funding_update":"资金事件时必填：{last_round:{date,name,amount_usd,valuation_usd}, note_new, source}","product_status_new":"产品状态被新事实改变时必填","field_updates":{"字段路径":"新值（同一条目里被新证据推翻的其他文字，如 note、gaps、impact）"}}`
   - 起草前先通读同一条目的 product、funding、note、gaps、impact，凡是与新事实冲突的都要在 field_updates 里给出改写。
   - 第二层：`{"id":..,"tier":2,"event":..,"material":true,"one_line_new":"可选","stage_rough_new":"可选","source_add":{"url","quote","grade","date"}}`
   quote 必须是 passages 里的逐字子串；text 只写原文有的内容；年份只能来自页面上显示的日期。
5. 不要改别的条目，不要写 map.json。

把所有起草结果写成一个数组到指定输出文件，并把每条起草里的 `{id,url,quote,date}` 也写一份到同名 `.check.json`（给 cache_check.py 用）。回复一行：几个事件，几个实质进展。
