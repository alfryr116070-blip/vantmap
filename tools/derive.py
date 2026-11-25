"""从证据推导里程碑、最近进展日期和活跃度，保证三者和证据一致。

用法：python3 derive.py map.json 今天(YYYY-MM-DD)
- 每条证据可带 progress: true（可选 event_date：事件本身的日期，与报道日期不同时填写），表示它记录的是这个团队自身的一次“实质进展”
  （新产品或新版本发布、交付、融资、监管决定、经审计的财报）；展会展出、重复演示、采访不算。
- 对每个团队：取 progress 为 true、日期最新的那条证据，
  milestone = 它的 text，last_progress = 它的 date，milestone_ref = 它的 url；
  活跃度按日期重算（6 个月内“活跃”，6～18 个月“放缓”，更早且无公认障碍写“放缓（已超过 18 个月没有实质进展）”）；
  原来是“停滞”“已放弃”的保持不变。
- progress 证据都没有日期时，用最后一条，last_progress 留空，活跃度写“无法判定”。
- 没有任何 progress 证据的团队不改，打印出来，需要人工补。
"""
import sys as _sys
if len(_sys.argv) < 2 or _sys.argv[1] in ("-h", "--help"):
    print(__doc__ or "see docs/"); _sys.exit(0)

import json, sys, datetime as dt
mp, today = sys.argv[1], dt.date.fromisoformat(sys.argv[2])
def d(s):
    s = str(s or "")
    try:
        if len(s) >= 10: return dt.date.fromisoformat(s[:10])
        if len(s) == 7: return dt.date.fromisoformat(s + "-01")
        if len(s) == 4: return dt.date.fromisoformat(s + "-01-01")
    except ValueError: return None
def months(a, b): return (b.year - a.year) * 12 + (b.month - a.month) + (b.day - a.day) / 31
m = json.load(open(mp)); missing = []
for e in m["entries"]:
    ev = [x for x in e.get("evidence", []) if x.get("progress") and d(x.get("event_date") or x.get("date"))]
    if not ev:
        und = [x for x in e.get("evidence", []) if x.get("progress")]
        if not und:
            missing.append(e["id"]); continue
        x = und[-1]   # progress evidence whose page shows no date: keep it, but the date stays unknown
        e["milestone"], e["last_progress"], e["milestone_ref"], e["milestone_grade"] = x["text"], None, x["url"], x.get("grade")
        if not str(e.get("activity", "")).startswith(("停滞", "已放弃")): e["activity"] = "无法判定"
        continue
    x = max(ev, key=lambda x: (d(x.get("event_date") or x["date"]), len(str(x.get("event_date") or x["date"]))))
    e["milestone"], e["last_progress"], e["milestone_ref"] = x["text"], x.get("event_date") or x["date"], x["url"]
    e["milestone_grade"] = x.get("grade")
    a = str(e.get("activity", ""))
    if a.startswith("停滞") or a.startswith("已放弃"): continue
    mo = months(d(x.get("event_date") or x["date"]), today)
    e["activity"] = "活跃" if mo <= 6 else ("放缓" if mo <= 18 else "放缓（已超过 18 个月没有实质进展）")
json.dump(m, open(mp, "w"), ensure_ascii=False, indent=1)
print("没有实质进展证据的团队：", missing or "无")
