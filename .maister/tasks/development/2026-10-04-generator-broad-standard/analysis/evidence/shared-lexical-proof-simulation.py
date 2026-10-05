import copy,json,hashlib
from pathlib import Path
from literaki_slownik.database import connect
from literaki_slownik.decisions import persisted_assessments,assessment
p=Path('.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence')
r=json.loads((p/'age-baseline-runtime.json').read_text());root=Path(r['outputs'][0]['run']);dbfile=root/'build.sqlite';before=hashlib.sha256(dbfile.read_bytes()).hexdigest();out=[]
with connect(dbfile,readonly=True) as db:
 for key in ['wznak','dwójnasób','trójnasób','kroćset','roścież','ziem']:
  for item in persisted_assessments(db,key,'standard'):
   if item.get('semantic_trace',{}).get('kind')!='documented_use':continue
   old=item['assessment'];new=copy.deepcopy(old);checks=new['language']['checks'];proof=[c for c in checks if c['rule_id']=='linguistic-documented-use-lexical-proof-v1'];assert len(proof)==1 and proof[0]['status']=='unresolved';proof[0]['status']='accept';new['language']=assessment(checks)
   member=assessment(checks+new['game']['checks']+new['profile']['checks']+new['release_scope']['checks'])
   out.append({'word_key':key,'source':item['semantic_trace']['source'],'lexical_before':'unresolved','lexical_option_A':'accept','language_before':old['language']['status'],'language_option_A':new['language']['status'],'membership_before':old['membership']['status'],'membership_option_A':member['status'],'remaining_rules':[c['rule_id'] for c in member['checks'] if c['status']!='accept']})
 assert db.total_changes==0
assert len(out)==6 and before==hashlib.sha256(dbfile.read_bytes()).hexdigest()
(p/'shared-lexical-proof-simulation.json').write_text(json.dumps({'scope':'readonly_counterfactual_single_check_not_policy_activation','run':str(root),'db_sha256':before,'source_unchanged':True,'cases':out},ensure_ascii=False,indent=2)+'\n')
print([(x['word_key'],x['membership_before'],x['membership_option_A']) for x in out])
