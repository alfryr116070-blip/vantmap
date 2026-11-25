"""Append one audit/verification round to data/labels/<date>.jsonl.txt (one shard per day).
usage: python3 tools/append_labels.py <map_id> <round_name> <claims.json> <verdicts.json> [date]
claims:   [{cid,type,team,team_name,path,claim,urls,grade_given?}]
verdicts: [{cid,verdict(correct|minor_error|wrong|unsupported|unreachable),checked_url,quote,correction,grade_ok,grade_suggested,note}]
Rows already present (same id) are skipped, so re-running is safe."""
import json,sys,os,datetime
m,rnd,cf,vf=sys.argv[1:5]; d=sys.argv[5] if len(sys.argv)>5 else datetime.date.today().isoformat()
P=f'data/labels/{d}.jsonl.txt'; ids=set()  # one shard per day; never rewrite older shards
import glob
os.makedirs('data/labels',exist_ok=True)
for p in glob.glob('data/labels/*.jsonl.txt'):
    for l in open(p):
        if l.strip(): ids.add(json.loads(l)['id'])
C={c['cid']:c for c in json.load(open(cf))}; n=0
VER={'correct','minor_error','wrong','unsupported','unreachable'}
with open(P,'a') as f:
    for v in json.load(open(vf)):
        c=C.get(v.get('cid')); i=f"{m}:{rnd}:{v.get('cid')}"
        if not c or i in ids or v.get('verdict') not in VER: continue
        f.write(json.dumps({"id":i,"date":d,"round":rnd,"map":m,"team":c.get('team'),"team_name":c.get('team_name'),
          "claim_type":c.get('type'),"path":c.get('path'),"claim":c.get('claim'),"urls":c.get('urls') or [],
          "grade_given":c.get('grade_given'),"verdict":v['verdict'],"checked_url":v.get('checked_url'),
          "evidence_quote":v.get('quote'),"correction":v.get('correction') or "","grade_ok":v.get('grade_ok'),
          "grade_suggested":v.get('grade_suggested'),"note":v.get('note') or "","rubric":"v0.7"},ensure_ascii=False)+'\n'); n+=1; ids.add(i)
print("appended",n)
