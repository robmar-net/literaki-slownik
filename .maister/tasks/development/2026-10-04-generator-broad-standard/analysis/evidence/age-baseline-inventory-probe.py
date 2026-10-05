import hashlib,json,time
from pathlib import Path
from literaki_slownik.database import connect
from literaki_slownik.canonical import sha256,dumps,write_json
from literaki_slownik.sgjp import tag_size
from literaki_slownik.policy import history_checks
p=Path('data/work/import-20261004-1302/build.sqlite');before=sha256(p);started=time.monotonic()
counts={};total=0
with connect(p,readonly=True) as db:
 for tag,names,qual,n in db.execute('select tag,names,qualifiers,count(*) from interpretation group by tag,names,qualifiers order by tag,names,qualifiers'):
  total+=n;checks=history_checks(qual,'standard');status='explicit_history_reject' if any(c['status']=='reject' for c in checks) else 'no_excluding_history_label'
  key=(status,qual=='',names in ('','nazwa_pospolita'),tag.split(':')[0]);item=counts.setdefault(key,{'compact':0,'expanded':0})
  item['compact']+=n;item['expanded']+=n*tag_size(tag)
 samples=[]
 for word in ('kot','dom','dwójnasób','trójnasób'):
  rows=db.execute('select f.original,l.lemma_id,i.tag,i.names,i.qualifiers,i.first_row from interpretation i join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id where f.game_key=? order by i.source_id,i.first_row',(word,)).fetchall()
  samples.append({'word':word,'records':[list(r) for r in rows]})
 assert db.total_changes==0
assert before==sha256(p)
result={'schema_version':1,'scope':'full_source_age_evidence_inventory_not_acceptance','source_db_sha256':before,'source_unchanged':True,'compact_interpretations':total,'groups':[{'age_status':k[0],'empty_qualifiers':k[1],'empty_or_common_names':k[2],'pos':k[3],**v} for k,v in sorted(counts.items())],'examples':samples,'seconds':time.monotonic()-started}
write_json(Path('tmp/age-baseline-counts.json'),result)
print(json.dumps({'compact':total,'groups':len(counts),'no_excluding_history_label':sum(v['compact'] for k,v in counts.items() if k[0]=='no_excluding_history_label'),'explicit_history_reject':sum(v['compact'] for k,v in counts.items() if k[0]=='explicit_history_reject')}))
