
import sys as _sys
if len(_sys.argv) < 2 or _sys.argv[1] in ("-h", "--help"):
    print(__doc__ or "see docs/"); _sys.exit(0)
# 写稿后的机器检查：quote 必须是缓存原文的逐字子串；日期的年份（和日）必须在原文同一段里出现
# 注意：缓存原文来自抓取工具的返回，可能是摘录或转述，这个检查只能证明“写的和抓到的一致”，证明不了“和网页一致”；真正的外部检查是联网验收和每日抽查
# 用法：python3 cache_check.py <drafts.json> <cache 目录>
#   drafts.json：[{id, url, quote, date, ...}]（证据、观察名单来源都可以；观察名单可直接带 passage 字段）
#   cache/<sha1(url)[:16]>.json：{url, fetched_at, title, published, passages:[...]}
# 退出码 0 = 全部通过；1 = 有不通过的（逐条列出）
import json, sys, os, re, hashlib, unicodedata
dp, cd = sys.argv[1], sys.argv[2]
def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip().lower()
def key(u): return hashlib.sha1(re.sub(r"#.*$", "", u.strip()).encode()).hexdigest()[:16]
items = json.load(open(dp)); bad = 0; n = 0
for it in items:
    u, q = it.get("url"), it.get("quote")
    if not u: continue
    n += 1
    texts = []
    if it.get("passage"): texts.append(it["passage"])
    p = os.path.join(cd, key(u) + ".json")
    if os.path.exists(p):
        c = json.load(open(p)); texts += c.get("passages", []); texts.append(c.get("published") or "")
    blob = norm(" \n ".join(texts))
    errs = []
    if not texts: errs.append("没有缓存原文")
    if q and norm(q) not in blob: errs.append("quote 不是原文逐字子串")
    dte = str(it.get("date") or "")
    if dte and texts:
        # 日期精度：年份必须出现在某段原文里（不算版权行），写到日的还要在同一段里看到这一天
        y = dte[:4]
        paras = [norm(t) for t in texts if t and not re.search(r"(©|copyright|all rights reserved)", t, re.I)]
        withy = [p for p in paras if y in p] or ([norm(u)] if y in u else [])
        if not withy: errs.append(f"原文里没有年份 {y}（版权行不算）")
        elif re.match(r"^\d{4}-\d{2}-\d{2}$", dte):
            d = str(int(dte[8:10]))
            if not any(re.search(r"(?<!\d)0?" + d + r"(?!\d)", p.replace(y, "")) for p in withy):
                errs.append(f"原文里有年份 {y}，但同一段里没看到日 {d}（日期精度可能写高了）")
    if errs: bad += 1; print(f"✗ {it.get('id','?')} {u}: " + "；".join(errs))
print(f"检查 {n} 条，不通过 {bad} 条")
sys.exit(1 if bad else 0)
