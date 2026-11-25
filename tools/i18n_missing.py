"""列出 map.json 里还没有英文翻译的中文字符串。

用法：python3 i18n_missing.py map.json en.json [out.json]
- 打印缺少翻译的条数；
- 把缺少的字符串写成 JSON 数组到 out.json（默认 missing.json）；
- 翻译好后，把 {中文原文: 英文} 合并进 en.json；原文必须逐字一致，作为键。
- 同一目录下如果有 promises.json（承诺账本），以及 compare.json（和直接问 AI 的对比），也一起扫描；
- 同时删掉 en.json 里已经不在 map.json 中出现的旧键，避免越积越多（加 --prune）。
"""
import sys as _sys
if len(_sys.argv) < 2 or _sys.argv[1] in ("-h", "--help"):
    print(__doc__ or "see docs/"); _sys.exit(0)

import json, re, sys

CJK = re.compile(r"[一-鿿]")


def strings(x, acc):
    if isinstance(x, str):
        if CJK.search(x):
            acc.add(x)
    elif isinstance(x, list):
        for v in x:
            strings(v, acc)
    elif isinstance(x, dict):
        for k, v in x.items():
            if k == "quote":  # 证据里的原文摘句，保持原文，不翻译
                continue
            strings(v, acc)
    return acc


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    prune = "--prune" in sys.argv
    m = json.load(open(args[0], encoding="utf-8"))
    en = json.load(open(args[1], encoding="utf-8"))
    out = args[2] if len(args) > 2 else "missing.json"
    need = strings(m, set())
    # 同目录下的承诺账本也要翻译（否则 --prune 会删掉它的译文）
    import os
    for extra in ("promises.json", "compare.json"):
        pp = os.path.join(os.path.dirname(os.path.abspath(args[0])), extra)
        if os.path.exists(pp):
            strings(json.load(open(pp, encoding="utf-8")), need)
    miss = sorted(s for s in need if s not in en)
    json.dump(miss, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"需要翻译 {len(need)} 条，缺少 {len(miss)} 条，已写入 {out}")
    if prune:
        old = [k for k in en if k not in need]
        for k in old:
            del en[k]
        json.dump(en, open(args[1], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print(f"已删除 {len(old)} 条不再使用的旧翻译")
    bad = [k for k, v in en.items() if CJK.search(v)]
    if bad:
        print(f"错误：有 {len(bad)} 条英文里还含有中文")
        sys.exit(1)


if __name__ == "__main__":
    main()
