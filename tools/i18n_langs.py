
import sys as _sys
if len(_sys.argv) < 2 or _sys.argv[1] in ("-h", "--help"):
    print(__doc__ or "see docs/"); _sys.exit(0)
# 其他 6 种语言的翻译检查：英文源 = 各地图 en.json 的英文值；字典 = data/i18n/<语言>.json（键是英文原文）
# 用法：python3 i18n_langs.py <输出目录> <i18n 目录> <en.json> [更多 en.json ...]
# 为每种语言写出 <输出目录>/missing_<语言>.json（还没翻译的英文列表），并检查已有译文的占位符 {0} 是否保留。
import json, sys, re, os
LANGS=["ja","ko","es","fr","de","pt"]
out, idir, ens = sys.argv[1], sys.argv[2], sys.argv[3:]
src=set()
for f in ens:
    for v in json.load(open(f)).values():
        if isinstance(v,str) and re.search(r'[A-Za-z]{2}',v) and not re.match(r'^https?://\S+$',v): src.add(v)  # 纯网址不翻译
err=0
for l in LANGS:
    p=os.path.join(idir,l+".json"); d=json.load(open(p)) if os.path.exists(p) else {}
    miss=sorted(s for s in src if not (isinstance(d.get(s),str) and d[s].strip()))
    json.dump(miss,open(os.path.join(out,f"missing_{l}.json"),"w"),ensure_ascii=False,indent=0)
    bad=[k for k,v in d.items() if isinstance(v,str) and set(re.findall(r'\{\d\}',v))-set(re.findall(r'\{\d\}',k))]
    zh=[k for k,v in d.items() if l not in("ja",) and not re.match(r'^https?://',str(v)) and re.search(r'[一-鿿]',str(v)) and not re.search(r'[一-鿿]',k)]
    if bad or zh: err=1
    print(f"{l}: {len(d)} 条已有，缺少 {len(miss)} 条" + (f"，{len(bad)} 条占位符有误" if bad else "") + (f"，{len(zh)} 条译文里混进了中文" if zh else ""))
sys.exit(err)
