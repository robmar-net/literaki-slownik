"""Kontrola efektu bieżącego wyjątku na poziomie napisu, nie pojedynczej analizy."""
import hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];TASK=Path(__file__).resolve().parents[1];TMP=ROOT/'tmp/research-issue4'
c=sqlite3.connect(f'file:{ROOT}/data/work/lists-v30-20261010-165826-a/build.sqlite?mode=ro',uri=True);c.execute('pragma query_only=on')
ks=[];ordinary=set()
for k,t in c.execute('select assessment_key,assessment from decision_payload'):
 d=json.loads(t)
 if d['membership']['status']=='accept':
  if 'linguistic-contemporary-use-kwjp-v2' in t:ks.append(k)
  else:ordinary.add(k)
path=TMP/'current-override-words.json'
if path.exists():ws=json.loads(path.read_text())
else:
 q='select distinct a.game_key from variant_decision d not indexed join analysis a on a.analysis_key=d.analysis_key where d.variant="standard" and d.assessment_key in ('+','.join('?' for _ in ks)+')'
 ws=sorted(r[0] for r in c.execute(q,ks));path.write_text(json.dumps(ws,ensure_ascii=False))
necessary=[];incidental=[]
q='select d.assessment_key from analysis a indexed by analysis_game_key join variant_decision d on d.analysis_key=a.analysis_key where a.game_key=? and +d.variant="standard" and d.membership_status="accept"'
for w in ws:
 keys={r[0] for r in c.execute(q,(w,))}
 (incidental if keys&ordinary else necessary).append(w)
sample=sorted(necessary,key=lambda w:hashlib.sha256(('issue4-current-required-v1:'+w).encode()).hexdigest())[:40]
out={'words_with_any_override_analysis':len(ws),'words_dependent_on_override':len(necessary),'words_with_independent_accepted_analysis':len(incidental),'necessary_words':necessary,'sample_seed':'issue4-current-required-v1:','sample':sample}
(TASK/'analysis/findings/round2/current-override.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print({k:v for k,v in out.items() if k!='necessary_words'})
