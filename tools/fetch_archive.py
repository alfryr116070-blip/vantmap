"""Save full-page snapshots of every source URL in a map (the "evidence archive").

Why: the hosted pipeline only stores the excerpts a fetch tool returned. Run this on any
machine with normal internet access to keep the full page text, so anyone can later
check a quote against what the page really said on that day.

usage: python3 tools/fetch_archive.py <map.json> <out_dir> [--only-today YYYY-MM-DD] [--delay 1.0]

For every URL in entries[].evidence / product.sources / funding.sources / openness and
watch[].sources it writes <out_dir>/<sha1(url)[:16]>.json:
  {url, fetched_at, status, final_url, content_type, title, text, sha256, quotes_found:{quote: bool}}
and an index <out_dir>/index.json. Only the standard library is used. Pages are fetched
politely (one at a time, a delay between requests, honest User-Agent, robots.txt respected).
Full-page text can be copyrighted: keep the archive for verification; do not republish it.
"""
import sys as _sys
if len(_sys.argv) < 2 or _sys.argv[1] in ("-h", "--help"):
    print(__doc__ or "see docs/"); _sys.exit(0)

import hashlib, html, json, os, re, sys, time, datetime as dt, urllib.request, urllib.robotparser
from urllib.parse import urlparse

UA = "VantmapArchiver/1.0 (+https://github.com/; evidence verification)"


def collect(m):
    out = {}
    def add(u, q=None, where=""):
        if not isinstance(u, str) or not u.startswith("http"): return
        r = out.setdefault(u, {"quotes": set(), "where": set()})
        if q: r["quotes"].add(q)
        r["where"].add(where)
    for e in m.get("entries", []):
        for x in e.get("evidence", []): add(x.get("url"), x.get("quote"), e["id"])
        for k in ("product", "funding"):
            for x in (e.get(k) or {}).get("sources", []) or []: add(x.get("url"), x.get("quote"), e["id"])
        for x in e.get("openness", []) or []: add(x.get("url"), None, e["id"])
    for w in m.get("watch", []) or []:
        for x in w.get("sources", []): add(x.get("url"), x.get("quote"), w["id"])
    return out


def text_of(raw, ctype):
    if "html" not in ctype: return raw
    raw = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
    title = re.search(r"(?is)<title[^>]*>(.*?)</title>", raw)
    t = re.sub(r"(?s)<[^>]+>", " ", raw)
    t = html.unescape(re.sub(r"\s+", " ", t)).strip()
    return t, (html.unescape(title.group(1)).strip() if title else None)


def norm(s):
    return re.sub(r"\s+", " ", (s or "").replace("’", "'").replace("“", '"').replace("”", '"')).strip().lower()


def main():
    a = sys.argv[1:]
    if len(a) < 2: print(__doc__); sys.exit(2)
    mp, outd = a[0], a[1]
    delay = float(a[a.index("--delay") + 1]) if "--delay" in a else 1.0
    only = a[a.index("--only-today") + 1] if "--only-today" in a else None
    m = json.load(open(mp))
    urls = collect(m)
    if only:  # only URLs whose evidence was verified that day
        keep = set()
        for e in m.get("entries", []):
            for x in e.get("evidence", []):
                if str(x.get("verified")) == only: keep.add(x.get("url"))
        urls = {u: v for u, v in urls.items() if u in keep}
    os.makedirs(outd, exist_ok=True)
    robots = {}
    index = []
    for i, (u, meta) in enumerate(sorted(urls.items())):
        key = hashlib.sha1(u.encode()).hexdigest()[:16]
        rec = {"url": u, "fetched_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z", "used_by": sorted(meta["where"])}
        host = "{0.scheme}://{0.netloc}".format(urlparse(u))
        try:
            if host not in robots:
                rp = urllib.robotparser.RobotFileParser(host + "/robots.txt")
                try: rp.read()
                except Exception: rp = None
                robots[host] = rp
            rp = robots[host]
            if rp is not None and not rp.can_fetch(UA, u):
                rec["status"] = "robots_disallowed"
            else:
                req = urllib.request.Request(u, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=30) as r:
                    ctype = r.headers.get("Content-Type", "")
                    body = r.read(8_000_000)
                    rec.update(status=r.status, final_url=r.geturl(), content_type=ctype)
                if "pdf" in ctype:
                    rec["text"] = None; rec["note"] = "PDF saved as bytes hash only; extract text with a PDF tool if needed"
                    rec["sha256"] = hashlib.sha256(body).hexdigest()
                else:
                    raw = body.decode(r.headers.get_content_charset() or "utf-8", "replace")
                    t, title = text_of(raw, ctype) if "html" in ctype else (raw, None)
                    rec.update(title=title, text=t, sha256=hashlib.sha256(t.encode()).hexdigest())
                    nt = norm(t)
                    rec["quotes_found"] = {q: norm(q) in nt for q in sorted(meta["quotes"])}
        except Exception as ex:
            rec["status"] = "error"; rec["error"] = str(ex)[:300]
        json.dump(rec, open(os.path.join(outd, key + ".json"), "w"), ensure_ascii=False)
        index.append({k: rec.get(k) for k in ("url", "status", "sha256", "fetched_at")} | {"file": key + ".json",
                      "quotes_missing": [q for q, ok in (rec.get("quotes_found") or {}).items() if not ok]})
        print(f"[{i+1}/{len(urls)}] {rec.get('status')} {u[:90]}")
        time.sleep(delay)
    json.dump(index, open(os.path.join(outd, "index.json"), "w"), ensure_ascii=False, indent=1)
    miss = sum(1 for x in index if x["quotes_missing"])
    print(f"done: {len(index)} pages, {miss} with at least one quote not found verbatim (see index.json)")


if __name__ == "__main__":
    main()
