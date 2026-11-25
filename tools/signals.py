"""Engineering-activity signals from public git history (reproducible, no API).
usage: python3 signals.py <map.json> <out signals.json> <today YYYY-MM-DD> [workdir]
For every github.com repo in entries[].open_sources/openness: bare clone (blobless),
then count commits per ISO week for 52 weeks, active authors in 90 days, last commit.
Merges into existing signals.json history (one snapshot per date; never deletes)."""
import json,re,subprocess,os,sys,datetime,collections
mp,out,T=sys.argv[1:4]; W=sys.argv[4] if len(sys.argv)>4 else 'work/signals'
os.makedirs(W,exist_ok=True); m=json.load(open(mp)); today=datetime.date.fromisoformat(T)
R={}
for e in m['entries']:
    for x in (e.get('open_sources') or [])+(e.get('openness') or []):
        g=re.match(r'https?://github\.com/([^/#?]+)/([^/#?]+)',x.get('url') or '')
        if g: R.setdefault(f"{g[1]}/{g[2].removesuffix('.git')}",set()).add(e['id'])
S=json.load(open(out)) if os.path.exists(out) else {"method":"git log of public default+all refs, committer dates; counts are commits, not lines","repos":{},"history":{}}
monday=today-datetime.timedelta(days=today.weekday())
weeks=[(monday-datetime.timedelta(weeks=51-i)).isoformat() for i in range(52)]
snap={}
for k,teams in sorted(R.items()):
    d=os.path.join(W,k.replace('/','__')+'.git')
    if os.path.exists(d): r=subprocess.run(['git','-C',d,'fetch','-q','--all'],capture_output=True)
    else: r=subprocess.run(['timeout','120','git','clone','-q','--bare','--filter=blob:none',f'https://github.com/{k}.git',d],capture_output=True,text=True)
    if not os.path.exists(d): S['repos'][k]={"teams":sorted(teams),"status":"unreachable"}; continue
    log=subprocess.run(['git','-C',d,'log','--all','--format=%H|%cs|%ae'],capture_output=True,text=True).stdout.split('\n')
    seen=set(); rows=[]
    for l in log:
        if not l: continue
        h,dt,a=l.split('|',2)
        if h in seen: continue
        seen.add(h); rows.append((dt,a))
    wk=collections.Counter()
    for dt,a in rows:
        dd=datetime.date.fromisoformat(dt); mon=(dd-datetime.timedelta(days=dd.weekday())).isoformat(); wk[mon]+=1
    a90={a for dt,a in rows if (today-datetime.date.fromisoformat(dt)).days<=90}
    c90=sum(1 for dt,a in rows if (today-datetime.date.fromisoformat(dt)).days<=90)
    dates=sorted(dt for dt,a in rows)
    S['repos'][k]={"teams":sorted(teams),"url":f"https://github.com/{k}","status":"ok","first_commit":dates[0] if dates else None,
      "last_commit":dates[-1] if dates else None,"total_commits":len(rows),"commits_90d":c90,"authors_90d":len(a90),
      "weekly":[wk.get(w,0) for w in weeks],"weeks_start":weeks[0]}
    snap[k]={"total_commits":len(rows),"commits_90d":c90,"authors_90d":len(a90),"last_commit":S['repos'][k]['last_commit']}
S['history'][T]=snap; S['updated']=T
# per-team rollup
TM=collections.defaultdict(lambda:{"repos":0,"commits_90d":0,"authors_90d":0,"last_commit":None,"weekly":[0]*52})
for k,v in S['repos'].items():
    if v.get('status')!='ok': continue
    for t in v['teams']:
        x=TM[t]; x['repos']+=1; x['commits_90d']+=v['commits_90d']; x['authors_90d']+=v['authors_90d']
        x['last_commit']=max(filter(None,[x['last_commit'],v['last_commit']]))
        x['weekly']=[a+b for a,b in zip(x['weekly'],v['weekly'])]
S['teams']=dict(TM)
json.dump(S,open(out,'w'),ensure_ascii=False,indent=1)
print(len(R),'repos;',sum(1 for v in S['repos'].values() if v.get('status')=='ok'),'ok')
for t,x in sorted(S['teams'].items(),key=lambda z:-z[1]['commits_90d']): print(t,x['repos'],x['commits_90d'],x['authors_90d'],x['last_commit'])
