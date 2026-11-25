"""进度地图数据的机械检查。用法：python3 check.py map.json [今天日期 YYYY-MM-DD]
有错误时退出码为 1，并逐条打印；只有提醒时退出码为 0。"""
import sys as _sys
if len(_sys.argv) < 2 or _sys.argv[1] in ("-h", "--help"):
    print(__doc__ or "see docs/"); _sys.exit(0)

import json, sys, re, datetime as dt

STAGES = {f"S{i}" for i in range(6)}
ACT = ("活跃", "放缓", "停滞", "已放弃", "无法判定")
GRADES = set("ABCD")
DATE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")


def d(s):
    if not s or not DATE.match(s):
        return None
    return dt.date.fromisoformat(s if len(s) == 10 else s + "-01")


def main(path, today):
    T = dt.date.fromisoformat(today) if today else dt.date.today()
    six = T - dt.timedelta(days=183)
    m = json.load(open(path, encoding="utf-8"))
    err, warn = [], []
    p = m.get("project", {})
    bids = {b["id"] for b in p.get("branches", [])}
    ids = set()
    for e in m.get("entries", []):
        i = e.get("id", "?")
        if i in ids:
            err.append(f"{i}: id 重复")
        ids.add(i)
        for k in ("name", "branch", "section", "stage", "milestone", "activity", "confidence", "evidence"):
            if k not in e:
                err.append(f"{i}: 缺少字段 {k}")
        if e.get("branch") not in bids:
            err.append(f"{i}: branch={e.get('branch')} 不在 project.branches 里")
        adjb = {b["id"] for b in p.get("branches", []) if b["id"] == "adjacent" or b.get("adjacent")}
        if (e.get("branch") in adjb) != (e.get("section") == "adjacent"):
            err.append(f"{i}: section 与 branch 不一致")
        LAY = set(m.get("project", {}).get("layers") or [])
        r = e.get("role")
        if not LAY:
            pass  # no project.layers: role is optional
        elif not r:
            warn.append(f"{i}: 缺少 role（负责哪一块）")
        elif r.get("main") not in LAY or any(x not in LAY for x in r.get("layers", [])):
            err.append(f"{i}: role 里有不在 project.layers 内的值")
        for o in e.get("openness", []) or []:
            if not str(o.get("url", "")).startswith("http"):
                err.append(f"{i}: 公开成果 {o.get('name')} 没有链接")
            if o.get("kind") not in ("code", "weights", "dataset", "paper", "sdk", "hardware", "registry"):
                err.append(f"{i}: 公开成果 {o.get('name')} 的 kind 无效")
            if "use" not in o:
                warn.append(f"{i}: 公开成果 {o.get('name')} 缺少 use（能否商用），页面会显示“许可证未写明”")
        g = e.get("gaps")
        if g is not None:
            if not isinstance(g, dict) or not all(isinstance(g.get(k, []), list) for k in ("field", "ours")):
                err.append(f"{i}: gaps 应为 {{field:[...], ours:[...]}}")
            else:
                for k in ("field", "ours"):
                    for x in g.get(k, []):
                        if not (isinstance(x, dict) and str(x.get("text", "")).strip()):
                            err.append(f"{i}: gaps.{k} 里有空条目")
                        u = (x or {}).get("url") or (x or {}).get("basis_url")
                        if u and not str(u).startswith("http"):
                            err.append(f"{i}: gaps.{k} 的链接无效")
        if p.get("tier") == "quick" and not e.get("pick_reason"):
            warn.append(f"{i}: 速览条目缺少 pick_reason（入选理由）")
        if e.get("stage") not in STAGES:
            err.append(f"{i}: 阶段 {e.get('stage')} 无效")
        if not str(e.get("activity", "")).startswith(ACT):
            err.append(f"{i}: 活跃度 {e.get('activity')} 无效")
        ev = e.get("evidence") or []
        for x in ev:
            if x.get("grade") not in GRADES:
                err.append(f"{i}: 证据等级 {x.get('grade')} 无效")
            xd = d(x.get("date"))
            if xd and xd > T:
                err.append(f"{i}: 证据日期 {x.get('date')} 晚于今天")
            if not x.get("url"):
                warn.append(f"{i}: 有一条证据没有链接")
        # 里程碑必须来自一条标了 progress 的证据（由 derive.py 生成）
        refs = [x for x in ev if x.get("progress")]
        if not refs and not e.get("milestone") and e.get("activity") == "无法判定":
            pass  # 没找到符合规则的实质进展：里程碑留空、活跃度写“无法判定”
        elif not refs:
            err.append(f"{i}: 没有任何标了 progress（实质进展）的证据，里程碑没有出处")
        elif e.get("milestone_ref") not in [x.get("url") for x in refs]:
            err.append(f"{i}: milestone_ref 没有指向一条实质进展证据，请运行 derive.py")
        # 产品介绍必须有出处
        pr = e.get("product") or {}
        if pr.get("intro") and not [s_ for s_ in (pr.get("sources") or []) if s_.get("url") and str(s_.get("quote") or "").strip()]:
            err.append(f"{i}: 产品介绍没有带原文摘句的来源（product.sources）")
        # 资金数字必须指明出自哪条来源
        fu = e.get("funding") or {}
        for k in ("total_usd", "valuation_usd", "parent_market_cap_usd", "project_investment_usd"):
            if fu.get(k) and not ((fu.get("cites") or {}).get(k)):
                err.append(f"{i}: 资金数字 {k} 没有写明出处（funding.cites.{k}）")
        # 零错误机制：每一条来源都必须有原文摘句和核对日期，否则不能发布
        for kind, xs in (("证据", ev), ("资金来源", (e.get("funding") or {}).get("sources") or []), ("其他来源", e.get("open_sources") or [])):
            for x in xs:
                if not str(x.get("quote") or "").strip() or not x.get("verified"):
                    err.append(f"{i}: 有一条{kind}缺少原文摘句（quote）或核对日期（verified）：{str(x.get('url'))[:60]}")
                else:
                    vd = d(x.get("verified"))
                    if vd and (T - vd).days > 120:
                        warn.append(f"{i}: 有一条{kind}超过 120 天没有重新核对：{str(x.get('url'))[:60]}")
        # 规则 7：D 级证据不能单独支撑任何升档
        if e.get("stage") != "S0" and ev and all(x.get("grade") == "D" for x in ev):
            err.append(f"{i}: 只有 D 级证据却在 {e['stage']}（规则 7）")
        if e.get("stage") != "S0" and not ev:
            err.append(f"{i}: 没有证据却在 {e['stage']}")
        lp = d(e.get("last_progress"))
        a = str(e.get("activity", ""))
        if a.startswith("活跃") and lp and lp < six:
            err.append(f"{i}: 最近进展 {e['last_progress']} 已超过 6 个月，却标“活跃”")
        if a.startswith("放缓") and lp and lp >= six:
            warn.append(f"{i}: 最近进展 {e['last_progress']} 在 6 个月内，却标“放缓”，请确认")
        if lp and lp > T:
            err.append(f"{i}: 最近进展日期晚于今天")
    for c in m.get("changes", []):
        if c.get("entry") and c["entry"] not in ids and c["entry"] not in {w.get("id") for w in m.get("watch") or []} | {x.get("id") for x in m.get("leads") or []} and c.get("type") != "bad":
            warn.append(f"changes 里引用了不存在的条目 {c['entry']}")
    b = m.get("brief")
    if b:
        for pt in b.get("points", []) + ([b["you"]] if b.get("you") else []):
            for r in pt.get("refs", []):
                if r not in ids:
                    err.append(f"brief 引用了不存在的条目 {r}")
        if b.get("date") and p.get("updated") and b["date"] < p["updated"]:
            warn.append("brief 早于 project.updated，解读可能过时")
        main_ = [e for e in m["entries"] if e.get("section") != "adjacent"]
        top = max([int(e["stage"][1]) for e in main_] or [0])
        hl = b.get("headline", "") + " ".join(x.get("text", "") for x in b.get("points", []))
        for s_ in re.findall(r"最远(?:只)?(?:走)?到 ?(S\d)", hl):
            if s_ != f"S{top}":
                err.append(f"brief 说最远到 {s_}，数据里是 S{top}")
        for n_ in re.findall(r"(\d+) 个主方向团队", hl):
            if int(n_) != len(main_):
                err.append(f"brief 说 {n_} 个主方向团队，数据里是 {len(main_)}")
    if p.get("tier") not in (None, "quick", "full"):
        err.append(f"project.tier={p.get('tier')} 无效（quick 或 full）")
    for r in p.get("roster") or []:
        if not r.get("name") or not str(r.get("url", "")).startswith("http"):
            err.append(f"roster 里的 {r.get('name')} 缺少名称或打开过的链接")
    # 写入后同步：last_round 必须是对象；过时词提醒
    STALE = ("待定", "pending", "尚待", "未完成", "未确认", "尚未获批", "决定待")
    for e in m.get("entries", []):
        f = e.get("funding") or {}
        lr = f.get("last_round")
        if lr is not None and not isinstance(lr, dict):
            err.append(f"{e['id']}: funding.last_round 必须是对象 {{date, name, amount_usd, valuation_usd}}，现在是 {type(lr).__name__}")
        texts = [("product.status", (e.get("product") or {}).get("status")), ("funding.note", f.get("note")), ("note", e.get("note"))]
        texts += [("gaps.field", g.get("text")) for g in ((e.get("gaps") or {}).get("field") or []) if isinstance(g, dict)]
        newest = max([str(x.get("date") or "") for x in e.get("evidence", [])] or [""])
        for k, t in texts:
            touched = any(str(x.get("verified")) == str(e.get("checked")) or str(x.get("archive")) == str(e.get("checked")) for x in e.get("evidence", []))
            if isinstance(t, str) and any(w in t for w in STALE) and touched:
                warn.append(f"{e['id']}: {k} 含“待定/未完成”等词，而条目在最近一次核对日有新核对的证据，请确认这句是否已被推翻")
    acc = (p.get("audit") or {}).get("acceptance") or {}
    if p.get("verified") is True and acc:
        n_ = (acc.get("n") or 0) - (acc.get("unreachable") or 0)
        bad = (acc.get("wrong") or 0) + (acc.get("unsupported") or 0)
        if bad > 0 or (n_ and (acc.get("minor") or 0) / n_ > 0.04):
            err.append(f"project.verified=true，但最近一轮验收（{acc.get('date')}）有 {bad} 条错误/没有依据、小误差 {acc.get('minor')}/{n_}，未达标准")
    # v2 三层分级
    bids = {b["id"] for b in p.get("branches", [])}
    eids = {e["id"] for e in m.get("entries", [])}
    wids = set()
    for w in m.get("watch") or []:
        t = w.get("id", "?")
        if t in eids: err.append(f"观察名单 {t} 和主图重复")
        if t in wids: err.append(f"观察名单 {t} 重复")
        wids.add(t)
        if w.get("branch") not in bids: err.append(f"观察名单 {t} 的分支 {w.get('branch')} 不存在")
        if w.get("stage_rough") not in (None, "S0", "S1", "S2", "S3"):  # 第二层粗判最高 S3
            err.append(f"观察名单 {t} 粗判阶段 {w.get('stage_rough')} 无效")
        if not w.get("one_line"): err.append(f"观察名单 {t} 缺一句话描述")
        src = w.get("sources") or []
        if not src or not all(str(s.get("url", "")).startswith("http") and s.get("quote") for s in src):
            err.append(f"观察名单 {t} 缺少带原文的来源")
        if not any(s.get("grade") in ("A", "B", "C") for s in src): err.append(f"观察名单 {t} 没有 C 级以上来源")
        if not w.get("checked"): err.append(f"观察名单 {t} 缺核对日期")
        txt = (w.get("one_line") or "") + (w.get("why") or "")
        if re.search(r"(\$|美元|亿元|万元|日元|欧元|融资|估值)\s*[\d.]|[\d.]+\s*(亿|万)?\s*(美元|元|日元|欧元)", txt) and not w.get("key_checked"):
            err.append(f"观察名单 {t} 写了金额但没有第二路联网核对（key_checked）")
        if re.search(r"(FDA|EMA|NMPA|批准|获批)", txt) and not w.get("key_checked"):
            err.append(f"观察名单 {t} 写了监管结论但没有第二路联网核对（key_checked）")
        for k in ("stage", "milestone", "funding", "evidence"):
            if k in w: err.append(f"观察名单 {t} 不能有 {k} 字段（第二层不写正式结论）")
    lids = set()
    for x in m.get("leads") or []:
        if not str(x.get("url", "")).startswith("http") or not x.get("title"): err.append(f"线索缺标题或网址：{x.get('id')}")
        if x.get("url") in lids: err.append(f"线索重复：{x.get('url')}")
        lids.add(x.get("url"))
        extra = set(x) - {"id", "title", "title_zh", "url", "source", "date", "found", "matched", "branch_guess", "title_is_name", "note"}
        if not re.match(r"^l-[a-z0-9][a-z0-9-]*$", str(x.get("id", ""))): err.append(f"线索 id 无效：{x.get('id')!r}")
        if x.get("title_is_name") and re.search(r"[（(].*[期期试验批准NCT]", x.get("title", "")): err.append(f"线索 {x.get('id')} 的名称里带了结论性说明")
        if re.search(r"降级|未核实|D 级", str(x.get("source", ""))): err.append(f"线索 {x.get('id')} 的 source 应是信源名，不是状态说明（状态写进 note）")
        if extra: err.append(f"线索 {x.get('id')} 有不允许的字段 {sorted(extra)}（第三层只列标题和来源）")
        if x.get("matched") and x["matched"] not in eids | wids: err.append(f"线索 {x.get('id')} 匹配的 {x['matched']} 不存在")
    for s in p.get("sources") or []:
        if not str(s.get("url", "")).startswith("http"): err.append(f"信源 {s.get('id')} 缺网址")
        for c in s.get("covers") or []:
            if c not in eids | wids: warn.append(f"信源 {s.get('id')} 覆盖的 {c} 不在名单里")
    if (m.get("watch") or m.get("leads")) and not p.get("sources"): warn.append("有第二、三层但没有信源清单")
    for x in err:
        print("错误", x)
    for x in warn:
        print("提醒", x)
    print(f"检查完：{len(err)} 个错误，{len(warn)} 个提醒")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
