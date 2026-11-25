
import sys as _sys
if len(_sys.argv) < 2 or _sys.argv[1] in ("-h", "--help"):
    print(__doc__ or "see docs/"); _sys.exit(0)
# 发现层：去重、聚类、匹配、兜底轮查
# 用法：python3 feed.py <map.json> <feed.json> <items.json> <今天 YYYY-MM-DD> <输出目录> [--since YYYY-MM-DD] [--commit] [--max-hits N]
#   --commit：确认本次结果已处理并发布后才带上，才会把见过的网址写回 feed.json、更新 last_run（失败的运行不会吞掉时间窗口）
#   feed.json 不存在时是“基线模式”：只记录现有条目，不产生命中（避免第一次运行把信源里的旧条目全部当成新消息）
# items.json：发现子任务的输出 {"items":[{url,title,date,source_id,relevant,why}]}（可以是多个文件合并后的列表）
# 输出：<输出目录>/hits.json（命中已追踪团队的事件）、newleads.json（相关但没命中）、sweep.json（今天兜底轮查名单）
# feed.json 会被更新（记住见过的网址和标题）。
import json, sys, re, hashlib, os, datetime as dt
args = sys.argv[1:]
COMMIT = "--commit" in args
def opt(k, dflt=None):
    return args[args.index(k) + 1] if k in args else dflt
mp, fp, ip, T, out = args[:5]
MAXH = int(opt("--max-hits", "25"))
d = json.load(open(mp)); today = dt.date.fromisoformat(T)
BASELINE = not os.path.exists(fp)
feed = json.load(open(fp)) if not BASELINE else {"last_run": None, "seen": {}, "titles": {}}
SINCE = opt("--since", feed.get("last_run") or (today - dt.timedelta(days=2)).isoformat())
raw = json.load(open(ip)); items = raw["items"] if isinstance(raw, dict) else raw

def h(u): return hashlib.sha1(re.sub(r"[#?].*$", "", u.strip().rstrip("/")).lower().encode()).hexdigest()[:16]
STOP = set("a an the of for and in on to with via by from at is are new using towards toward we our".split())
def toks(t): return [w for w in re.findall(r"[a-z0-9]+|[一-鿿]", (t or "").lower()) if w not in STOP]
def nt(t): return " ".join(toks(t))[:120]
def jac(a, b):
    A, B = set(toks(a)), set(toks(b))
    return len(A & B) / max(1, len(A | B))

# 1 去重：按网址；再按（信源, 标题）——不同仓库发同名版本号（如 v1.4.6）不会互相吞掉；太短的标题只按网址去重
fresh, run_urls, old = [], set(), 0
def tkey(it):
    t = nt(it["title"])
    return None if len(set(toks(it["title"]))) < 4 else f'{it.get("source_id")}|{t}'
for it in items:
    if not it.get("url") or not it.get("title"): continue
    k, t = h(it["url"]), tkey(it)
    if k in run_urls or k in feed["seen"] or (t and t in feed["titles"]): continue
    dte = str(it.get("date") or "")
    # 有完整日期且早于窗口起点的丢弃；没有年份的照收，但标为 undated，起草时必须先确认年份
    if not BASELINE and re.match(r"^\d{4}-\d{2}-\d{2}$", dte) and dte < SINCE: old += 1; continue
    if not re.match(r"^\d{4}", dte): it["undated"] = True
    run_urls.add(k); fresh.append(it)
# 2 聚类（标题相似度 ≥ 0.5 视为同一事件；同一事件同一信源只算一次）
clusters = []
for it in fresh:
    for c in clusters:
        if len(set(toks(it["title"]))) >= 4 and jac(c["title"], it["title"]) >= 0.5:  # 太短的标题（如版本号）不聚类
            if it.get("source_id") not in {m.get("source_id") for m in c["members"]}: c["members"].append(it)
            break
    else:
        clusters.append({"title": it["title"], "members": [it]})

# 3 匹配已追踪团队（第一层 entries + 第二层 watch）
# Common words that must not count as a team-name hit on their own. Add map-specific ones in project.generic_names.
GENERIC = set("atlas apollo nova orbit phoenix neo labs ai health systems technologies robotics tech one".split()) | {w.lower() for w in d.get("project", {}).get("generic_names", [])}
def names(e):
    out = [e.get("short") or "", e.get("name") or ""] + list(e.get("aliases") or [])
    res = set()
    for n in out:
        for part in re.split(r"[（()）/,，、]| \+ ", n):
            p = part.strip()
            pl = p.lower()
            if pl in GENERIC: continue  # 常见词单独出现不算命中，必须是多词全名或靠信源归属
            if len(pl) >= 4 or re.search(r"[一-鿿]{2}", pl): res.add(pl)
    return res
tracked = [(e["id"], 1, names(e)) for e in d.get("entries", [])] + [(w["id"], 2, names(w)) for w in d.get("watch", [])]
hits, newleads = [], []
srcmap = {s["id"]: s for s in d["project"].get("sources", [])}
tierof = {i: t for i, t, _ in tracked}
def path(u): return re.sub(r"^https?://[^/]+", "", u or "").lower()
for c in clusters:
    if not any(x.get("relevant", True) for x in c["members"]): continue  # 发现子任务判为无关的直接丢弃
    # 只在标题和网址路径里找团队名（不看域名，避免“synopsys.com 上的任何文章都算 Synopsys”）
    blob = " ".join((m.get("title") or "") + " " + path(m.get("url")) for m in c["members"]).lower()
    m = [(i, tier) for i, tier, ns in tracked if any(re.search(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])", blob) for n in ns)]
    # 只覆盖一个团队的信源（某团队自己的发布页、博客），条目直接算这个团队
    for x in c["members"]:
        cv = srcmap.get(x.get("source_id"), {}).get("covers") or []
        if len(cv) == 1 and cv[0] in tierof and cv[0] not in [y[0] for y in m]: m.append((cv[0], tierof[cv[0]]))
    ev = {"title": c["title"], "sources": len(c["members"]), "members": c["members"]}
    if any(x.get("undated") for x in c["members"]): ev["undated"] = True
    if m: ev["matched"] = [x[0] for x in m]; ev["tier"] = min(x[1] for x in m); hits.append(ev)
    else: newleads.append(ev)

# 4 兜底轮查：第一层每 7 天一轮；第二层每 30 天一轮；没被任何信源覆盖的第一层条目每 3 天
covered = {c for s in d["project"].get("sources", []) for c in s.get("covers", [])}
dn = today.toordinal()
def slot(i, n): return int(hashlib.sha1(i.encode()).hexdigest(), 16) % n == dn % n
sweep = [{"id": e["id"], "tier": 1, "why": "weekly"} for e in d.get("entries", []) if slot(e["id"], 7)]
sweep += [{"id": e["id"], "tier": 1, "why": "uncovered"} for e in d.get("entries", []) if e["id"] not in covered and slot(e["id"], 3) and not slot(e["id"], 7)]
sweep += [{"id": w["id"], "tier": 2, "why": "monthly"} for w in d.get("watch", []) if slot(w["id"], 30)]

# 5 命中上限：第一层优先、有日期的优先，超出的留到明天（不写进 feed，明天还会出现）
hits.sort(key=lambda x: (x["tier"], bool(x.get("undated"))))
overflow = hits[MAXH:]; hits = hits[:MAXH]
held = {h(m["url"]) for ev in overflow for m in ev["members"]}
if BASELINE: hits, newleads, overflow = [], [], []
# 6 更新 feed 状态（保留 180 天）；只有 --commit 或基线模式才写回
for it in fresh:
    if h(it["url"]) in held: continue
    feed["seen"][h(it["url"])] = T
    k = tkey(it)
    if k: feed["titles"][k] = T
cut = (today - dt.timedelta(days=180)).isoformat()
feed["seen"] = {k: v for k, v in feed["seen"].items() if v >= cut}
feed["titles"] = {k: v for k, v in feed["titles"].items() if v >= cut}
feed["last_run"] = T
if COMMIT or BASELINE: json.dump(feed, open(fp, "w"), ensure_ascii=False)
os.makedirs(out, exist_ok=True)
for n, v in (("hits", hits), ("newleads", newleads), ("sweep", sweep), ("overflow", overflow)):
    json.dump(v, open(os.path.join(out, n + ".json"), "w"), ensure_ascii=False, indent=1)
mode = "基线模式（只记录，不产生命中）" if BASELINE else ("已写回 feed.json" if COMMIT else "未写回 feed.json（处理完并发布后用 --commit 再跑一次）")
print(f"items {len(items)} → 窗口外 {old} → new {len(fresh)} → events {len(clusters)}: hits {len(hits)} (tier1 {sum(1 for x in hits if x['tier']==1)}, 无年份 {sum(1 for x in hits if x.get('undated'))}), 超出上限 {len(overflow)}, new leads {len(newleads)}; sweep today {len(sweep)}; {mode}")
