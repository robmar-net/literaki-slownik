"""Spójność pomiarów researchu oraz niezależny kontrolny odczyt decyzji bazy."""
import collections
import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
TASK=Path(__file__).resolve().parents[1]
OUT=TASK/'analysis/findings/round2'
def read(name):return json.loads((OUT/name).read_text())
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8<<20),b''):h.update(block)
    return h.hexdigest()
metrics=read('metrics.json');census=read('census-1580.json');sample=read('sample-forms.json')
full={w for g in census for w in g['new_forms']};clean={w for g in census for w in g['new_noarch']}
assert len(census)==1580 and len(full)==4559 and len(clean)==3364
assert sum(not x['new_noarch'] for x in census)==1176
assert sum(bool(x['new_noarch']) for x in census)==404
assert sum(metrics['strata'].values())==3364
assert len(sample['cases'])==155 and len({x['word'] for x in sample['cases']})==155
for x in sample['cases']:assert x['word'] in clean
assert len(metrics['grid'])==30 and len(metrics['extra'])==10
assert next(x['new_forms'] for x in metrics['grid'] if x['lemma_nf']==30 and x['form_nf']==0)==3364
base=json.loads((TASK/'analysis/findings/measurements.json').read_text())
assert base['scenarios']['lemma-nf-30']['new_forms']==4559
controls=read('current-override.json');outside=read('controls.json')['rejected_outside_lemma30_with_nf_evidence']
assert len(controls['necessary_words'])==290
assert controls['words_with_any_override_analysis']==290+2011
assert len(controls['sample'])==len(outside)==40
assert not {x['word'] for x in outside}&full
live=read('live-review.json');inventory=read('kwjp-live-inventory.json')
assert len(live['cases'])==len(inventory['cases'])==257
assert sum(x['inspected'] for x in live['cases'])==643
assert all(x['total_live'] is not None and x['note'] and x['eligibility_decision'] is None for x in live['cases'])
assert {x['word'] for x in live['cases']}=={x['word'] for x in inventory['cases']}
contexts=read('context-review.json');ci=read('context-inventory.json')
assert len(contexts['records'])==ci['selected_hits']==ci['lemma30_hits']==107
assert ci['focus_hits']==106 and ci['files']==5500 and ci['units']==11108
assert {x['id'] for x in contexts['records']}=={x['id'] for x in ci['records']}
assert sum(contexts['counts'].values())==107
assert all(x['note'] and x['eligibility_decision'] is None for x in contexts['records'])
sgjp=read('sgjp-review.json');assert len(sgjp['cases'])==40
assert sum(len(x['articles']) for x in sgjp['cases'])==47
for relative,expected in metrics['source_hashes'].items():assert digest(ROOT/relative)==expected,relative
db=ROOT/base['run']/'build.sqlite'
assert digest(db)==base['database_sha256']
assert digest(ROOT/base['run']/'lists/standard.txt')==base['standard_sha256']
print('Źródła i sumy zgodne.',flush=True)
conn=sqlite3.connect(f'file:{db}?mode=ro',uri=True);conn.execute('pragma query_only=on')
query='''select a.expanded_tag,d.membership_status,p.assessment from analysis a indexed by analysis_game_key
join variant_decision d on d.analysis_key=a.analysis_key join decision_payload p on p.assessment_key=d.assessment_key
where a.game_key=? and +d.variant="standard"'''
checked=0
for w in controls['necessary_words']:
    accepted=[json.loads(t) for tag,status,t in conn.execute(query,(w,)) if status=='accept']
    assert accepted and all(any(q['rule_id']=='linguistic-contemporary-use-kwjp-v2' for q in d['language']['checks']) for d in accepted),w
    checked+=1
examples={}
for w in ['sek','cześci','desperacja','desperacji','ekscytacja','ekscytacją','niezbędnik','wywre','ośm','aktuariusz','moderowana','upakowanych']:
    rows=[]
    for tag,status,t in conn.execute(query,(w,)):
        d=json.loads(t)
        relevant=[q for area in ('language','game') for q in d[area]['checks'] if q['rule_id'] in ('linguistic-contemporary-use-kwjp-v2','linguistic-historical-form-v1','game-abbreviation-v1')]
        rows.append({'tag':tag,'status':status,'checks':relevant})
    assert rows
    examples[w]=rows
assert any(r['status']=='accept' and r['tag'].startswith('subst:') and any(q.get('nonfiction_frequency')==301 for q in r['checks']) for r in examples['sek'])
assert all(r['status']=='reject' for r in examples['sek'] if r['tag'].startswith('brev:'))
result={'checked_at':subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip(),
        'status':'passed','structural_census':1580,'form_sample':155,'live_queries':257,'inspected_live_contexts':643,
        'public_sample_contexts':107,'dependent_accepted_words_independently_rechecked':checked,
        'database_sha256':base['database_sha256'],'standard_sha256':base['standard_sha256'],
        'source_hashes_verified':len(metrics['source_hashes'])+2,'examples':examples,
        'limits':['Walidacja obliczeń i zapisanych decyzji nie jest niezależnym drugim przeglądem językoznawczym.','Nie ocenia prawidłowości wszystkich 303 trafień sek.'],
        'research_script_sha256':{p.name:digest(p) for p in sorted((TASK/'analysis').glob('*.py')) if p.name!='render.py'}}
(OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS: spis, warstwy, 257 notatek, 107 fragmentów, 47 artykułów, 290 przyjęć i 12 przykładów bazy.')
