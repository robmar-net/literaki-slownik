"""Kontrola kompletności, powiązań i pomiarów rundy 4; baza tylko do odczytu."""
import collections
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
from literaki_slownik.database import connect
TASK=Path(__file__).resolve().parents[1]
OUT=TASK/'analysis/findings/round4'
R3=TASK/'analysis/findings/round3'
CACHE=ROOT/'tmp/research-issue4/round4-twelve'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

proposal=read(R3/'proposal.json'); family=read(OUT/'family-review.json')
assert len(family['families'])==110
assert len({r['lemma_id'] for r in family['families']})==110
assert set().union(*(set(r['proposed_words']) for r in family['families']))==set(proposal['new_words'])
assert sum(r['affected_count'] for r in family['families'])==0
assert sum(len(r['reviewed_contexts']) for r in family['families'])==324
for filename,digest in family['input_sha256'].items():assert sha(ROOT/filename)==digest,filename
web={r['id']:r for r in family['web_sources']}
for r in family['extra_source_downloads']:
    if 'error' in r:assert web[r['id']]['read'],r['id']

twelve=read(OUT/'current-twelve.json')
assert len(twelve['cases'])==12
assert {c['word'] for c in twelve['cases']}==set(read(R3/'current-review.json')['unsupported_evidence_words'])
assert sum(len(c['accepted_analyses']) for c in twelve['cases'])==30
counts=collections.Counter(c['decision'] for c in twelve['cases'])
assert counts=={'kwalifikuje do cofnięcia po decyzji':8,'wstrzymać':4}
for rawname,field,expected in [('kwjp-raw.json','pages',771),('kwjp-supplement-raw.json','supplement_pages',25)]:
    raw=read(CACHE/rawname); index={(r['word'],r['page']):r for r in raw}
    assert len(index)==len(twelve[field])
    total=0
    for p in twelve[field]:
        source=index[p['word'],p['page']]
        assert p['sha256']==source['sha256']
        assert p['downloaded']==p['read_and_assessed']==len(p['annotations'])==len(source['rows'])
        for n,(annotation,row) in enumerate(zip(p['annotations'],source['rows']),start=(p['page']-1)*50):
            assert annotation['hit_index_zero_based']==n
            assert annotation['document_id']==row['document_id']
            assert annotation['sentence']==row['sentence']
            assert annotation['manual_class'] in twelve['class_legend']
        total+=len(p['annotations'])
    assert total==expected,(field,total)

with connect(ROOT/twelve['baseline'],readonly=True) as db:
    for c in twelve['cases']:
        # Najpierw kilka analiz zapisu, następnie decyzje po kluczu; unikamy
        # skanowania wszystkich przyjęć STANDARD dla każdego z 12 zapisów.
        found={r[0] for r in db.execute("select a.analysis_key from analysis a where a.game_key=? and exists (select 1 from variant_decision d where d.analysis_key=a.analysis_key and d.variant='standard' and d.membership_status='accept')",(c['word'],))}
        assert found=={a['analysis_key'] for a in c['accepted_analyses']},c['word']

loss=read(OUT/'pop-losses.json'); dag=read(OUT/'dag-mechanism.json'); validation=read(OUT/'pop-validation.json')
sets={k:set(v) for k,v in loss['words_by_reason'].items()}
assert sum(map(len,sets.values()))==len(set().union(*sets.values()))==2430
assert set().union(*sets.values())==set(read(R3/'pop-impact.json')['deltas']['pop']['removed'])
assert all(r['before']['measure']==r['after']['measure'] for r in loss['members'])
assert dag['frozen_population_control']['delta']=={n:{'added':[],'removed':['dag']} for n in ('pop','pop0')}
assert dag['kwjp_full_control']['delta']['pop0']=={'added':[],'removed':[]}
for r in dag['kwjp_full_control']['traces']:
    assert r['before']['nkjp']['status']=='NOT_APPLICABLE'
for filename,digest in validation['pins'].items():assert sha(ROOT/filename)==digest,filename

eight=read(OUT/'eight-sensitivity.json')
assert eight['review_sha256']==sha(OUT/'current-twelve.json')
assert eight['proposal_sha256']==sha(R3/'proposal.json')
assert set(eight['removed_analysis_keys'])=={a['analysis_key'] for c in twelve['cases'] if c['decision']=='kwalifikuje do cofnięcia po decyzji' for a in c['accepted_analyses']}
assert len(eight['removed_analysis_keys'])==24
assert eight['standard_forms']==3090194+2382-8
for n,baseline in [('pop',1227250),('pop0',388509)]:
    d=eight['deltas'][n]
    assert baseline+len(d['added'])-len(d['removed'])==eight['lists'][n]['forms']
    assert len(d['added'])-len(d['removed'])==d['net']
    assert eight['frequent_guard'][n]['missing']==0

for filename in OUT.glob('*.json'):
    def check(obj):
        if isinstance(obj,dict):
            assert not {'left','right','raw_html','nkjp_f'}&obj.keys(),filename
            for v in obj.values():check(v)
        elif isinstance(obj,list):
            for v in obj:check(v)
    check(read(filename))

now=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
result={'checked_at':now,'status':'passed','families':110,'proposal_words':2382,'family_context_ids':324,
        'current_words':12,'current_accepted_analyses_verified_in_readonly_db':30,
        'annotated_exact_rows':771,'annotated_supplement_rows':25,'losses_attributed':2430,
        'sensitivity_removed_analyses':24,'source_coverage':'Wszystkie wymagane kategorie pokryte; błędy pobrania rodzin mają udany odczyt web. Ograniczenia pomocniczych tropów ujawnione.',
        'raw_corpus_fields_published':False,'script_sha256':sha(Path(__file__)),
        'pop_script_sha256':sha(Path(__file__).with_name('round4_pop.py')),
        'inputs':{p.name:sha(p) for p in OUT.glob('*.json') if p.name!='validation.json'}}
(OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='inputs'},ensure_ascii=False,indent=2))
