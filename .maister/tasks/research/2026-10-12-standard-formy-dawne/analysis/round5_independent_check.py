"""Niezależna kontrola cięć i list z cache grafu; bez importu pop.py/round5_measure.

Nie odtwarza budowy grafu ani morfologii. Własne cięcia, pruning, składanie form,
pokrycie, wiersze KWJP z SQLite i próbkowanie. Zapisuje wyłącznie swój raport.
"""
import bisect
import collections
import gc
import gzip
import hashlib
import itertools
import json
import math
import pickle
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
OUT = TASK/'analysis/findings/round5'
CACHE = ROOT/'tmp/research-issue4/round5'
CAPS = (40000,50000,60000,60025,65000,70000,75000,80000,90000,100000)
KEYS = ('count-60000','count-70000','count-80000','score-baseline60k','score-0.05')


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()


def digest(words):
    h=hashlib.sha256()
    for w in sorted(words):h.update((w+'\n').encode())
    return h.hexdigest()


def chosen(g,cap=None,score=None):
    order=sorted((k for k,v in g['measured'].items() if v['value'] is not None),
                 key=lambda k:(-g['measured'][k]['value'],k))
    selected=[];size=0;blocked=None
    for value,bucket in itertools.groupby(order,key=lambda k:g['measured'][k]['value']):
        block=list(bucket);block_size=sum(g['result']['units'][k]['size'] for k in block)
        if cap is not None and size+block_size>cap:
            blocked={'units':len(block),'lexemes':block_size,'rank':len(selected)+1};break
        if score is not None and value<score:break
        selected.extend(block);size+=block_size
        if cap is not None and size==cap:break
    return selected,size,blocked


def prune(g,selected,minimum=None):
    all_values=sorted(v['value'] for v in g['measured'].values() if v['value'] is not None)
    subunits=collections.defaultdict(list)
    for s,u in g['members']['units'].items():subunits[u['unit']].append(s)
    kept=set(m for u in selected for m in g['result']['units'][u]['members'])
    removed=set();heads=0
    for u in selected:
        ss=subunits[u]
        if len(ss)<2:continue
        values={s:g['own'][s]['value'] for s in ss}
        measured=[v for v in values.values() if v is not None]
        if not measured:continue
        best=max(measured)
        qualifies=lambda v: v is not None and (v>=minimum if minimum is not None else
                         1+len(all_values)-bisect.bisect_right(all_values,v)<=len(selected))
        heads+=not qualifies(best)
        for s,v in values.items():
            if v!=best and not qualifies(v):removed.update(s)
    return frozenset(kept-removed),removed,heads


def forms(data,members):
    words=set()
    for m in members:
        words.update(data['forms'].get(m,()))
        words.update(data['constructions']['forms'].get(m,()))
    return words


def coverage(data,members,kind):
    k=data['kwjp'];relevant=data['relevant'];numerator=0;denominator=0
    for m,row in k['lexemes'].items():
        if kind=='kwjp-all' or m in relevant:
            denominator+=row['F']
            if m in members:numerator+=row['F']
    for group,row in k['groups'].items():
        if kind=='kwjp-all' or any(m in relevant for m in group):
            denominator+=row['F']
            if all(m in members for m in group):numerator+=row['F']
    if kind=='kwjp-all':denominator=k['mass']['total']
    return {'denominator':kind,'covered':numerator,'total':denominator,
            'coverage':round(numerator/denominator,6) if denominator else None}


def original_rows(database):
    # Niezależne złączenie SQL; nie używa load_kwjp ani cache agregacji.
    db=sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)
    sql='''select c.id,c.row_number,c.unit_1,c.pos,c.freq,c.typed_metrics,l.lemma_id
           from corpus_evidence c join evidence_candidate e on e.evidence_id=c.id
           join lexeme l on l.id=e.lexeme_id
           where c.source_id=? order by c.id'''
    grouped=collections.defaultdict(list)
    rows=db.execute(sql,('KWJP100-kwjp100-slowa-lemma-all',))
    count=0
    for eid,entries in itertools.groupby(rows,key=lambda r:r[0]):
        entries=list(entries);bases={r[6].split(':',1)[0] for r in entries}
        if len(bases)==1:
            r=entries[0];typed=json.loads(r[5]);count+=1
            grouped[next(iter(bases))].append({'row':r[1],'unit':r[2],'pos':r[3],
              'F':r[4],'ARF':float(typed['ARF']),'DP':typed.get('DP'),'DP_norm':typed.get('DP_norm')})
    db.close()
    return grouped,count


def pass_row(row,policy):
    return row['F']>=policy.get('min_F',0) and row['ARF']>=policy['min_ARF'] and row['ARF']/row['F']>=policy['min_ARF_F']


def scan_nkjp_raw(obj,path=''):
    findings=[]
    if isinstance(obj,dict):
        for k,v in obj.items():
            p=path+'/'+k
            if k=='nkjp_f':findings.append(p)
            if 'nkjp' in path.lower() and k in ('F','freq','frequency','count'):
                findings.append(p)
            findings.extend(scan_nkjp_raw(v,p))
    elif isinstance(obj,list):
        for i,v in enumerate(obj):findings.extend(scan_nkjp_raw(v,path+f'/{i}'))
    return findings


def main():
    manifest=json.loads((OUT/'input-manifest.json').read_text())
    assert manifest.get('diagnostics_corrected_at'),'Czeka na ukończenie korekty diagnostyki.'
    script=TASK/'analysis/round5_measure.py'
    assert sha(script)==manifest['script_sha256']
    database=Path(manifest['read_only_database']);db_stat=database.stat()
    raw,nrows=original_rows(database)
    result={'status':'in_progress','independent_script_sha256':sha(Path(__file__)),
      'measurement_script_sha256':sha(script),'diagnostics_corrected_at':manifest['diagnostics_corrected_at'],
      'scope':'Własne algorytmy na cache grafu; oryginalne wiersze przez niezależne SQL. Bez przebudowy grafu/morfologii.',
      'original_rows_same_base':nrows,'scenarios':{},'sample_checks':{},'raw_nkjp_scan':{}}
    proposal=set(json.loads((TASK/'analysis/findings/round3/proposal.json').read_text())['new_words'])
    expected_standard=None;all_forms={};all_members={}
    for scenario in ('baseline','proposal'):
        with (CACHE/f'{scenario}-graph.pickle').open('rb') as f:data,g,selections=pickle.load(f)
        expected=json.loads((OUT/f'{scenario}-measurements.json').read_text())
        assert expected.get('corrected_at')
        assert data['relevant']==frozenset(data['forms'])
        if scenario=='baseline':expected_standard=digest(data['standard']|proposal)
        else:assert digest(data['standard'])==expected_standard
        checks={};recomputed={}
        for cap in CAPS:
            key=f'count-{cap}';us,size,blocked=chosen(g,cap=cap);members,removed,heads=prune(g,us)
            assert members==selections[key]['kept'],(scenario,key,'members')
            e=expected['variants'][key]
            assert (len(us),size,len(members),len(removed),heads)==(e['units'],e['lexemes_before_pruning'],e['lexemes'],e['pruned_lexemes'],e['head_exceptions_units']),(scenario,key,'metrics')
            assert blocked==e['next_block'];recomputed[key]=members
        for label,tau in expected['fixed_score_thresholds'].items():
            key='score-'+label;us,size,blocked=chosen(g,score=tau);members,removed,heads=prune(g,us,minimum=tau)
            assert members==selections[key]['kept'],(scenario,key,'members')
            assert len(members)==expected['variants'][key]['lexemes']
            recomputed[key]=members
        all_forms[scenario]={};all_members[scenario]={}
        for key in KEYS:
            members=recomputed[key];words=forms(data,members);e=expected['variants'][key]
            assert len(words)==e['forms'] and digest(words)==e['sha256_forms'],(scenario,key,'forms')
            cov={k:coverage(data,members,k) for k in ('kwjp-standard','kwjp-all')}
            assert cov==e['coverage'],(scenario,key,'coverage')
            assert words<=data['standard']
            if key=='count-60000':
                published=set(gzip.open(ROOT/'data/work/pop-v2-20261011-194738-b/POP.txt.gz','rt').read().splitlines())
                if scenario=='baseline':assert words==published
                else:
                    delta=json.loads((TASK/'analysis/findings/round3/pop-impact.json').read_text())['deltas']['pop']
                    assert words-published==set(delta['added']) and published-words==set(delta['removed'])
                pop0=set(gzip.open(ROOT/'data/work/pop-v2-20261011-194738-b/POP0.txt.gz','rt').read().splitlines())
                if scenario=='baseline':assert g['lists']['pop0']==pop0
                del published,pop0
            checks[key]={'lexemes':len(members),'forms':len(words),'sha256_forms':digest(words),'coverage':cov}
            all_forms[scenario][key]=words;all_members[scenario][key]=members
        diagnostic={}
        for key,e in expected['variants'].items():
            p=e['policy']
            if p['kind'] not in ('diagnostic-filter-count80000','absolute-own-kwjp'):continue
            population=recomputed['count-80000'] if p['kind']=='diagnostic-filter-count80000' else data['relevant']-data['proper']
            unknown={m for m in population if not raw.get(m[1].split(':',1)[0])}
            keep={m for m in population if any(pass_row(r,p) for r in raw.get(m[1].split(':',1)[0],()))}
            if p['unknown']=='kept':keep|=unknown
            assert keep==selections[key]['kept'],(scenario,key,'diagnostic members')
            words=forms(data,keep)
            assert len(words)==e['forms'] and digest(words)==e['sha256_forms'],(scenario,key,'diagnostic forms')
            assert {k:coverage(data,keep,k) for k in ('kwjp-standard','kwjp-all')}==e['coverage']
            if p['kind']=='diagnostic-filter-count80000':assert len(unknown)==e['unknown_lexemes']
            diagnostic[key]={'lexemes':len(keep),'forms':len(words),'unknown_lexemes_actual':len(unknown),'exact':True}
        grid=json.loads((OUT/f'{scenario}-dispersion-grid.json').read_text())['grid']
        for cell in grid:
            p={'min_ARF':cell['ARF'],'min_ARF_F':cell['ARF_F']};population=recomputed['count-80000']
            unknown={m for m in population if not raw.get(m[1].split(':',1)[0])}
            passing={m for m in population if any(pass_row(r,p) for r in raw.get(m[1].split(':',1)[0],()))}
            assert (len(passing),len(unknown),len(passing|unknown))==(cell['observed_pass_lexemes'],cell['unknown_lexemes'],cell['keep_unknown_lexemes'])
        if scenario=='baseline':
            sample=json.loads((OUT/'sample-blind.json').read_text());design=json.loads((OUT/'sample-design.json').read_text())
            cases={r['lemma']:r for r in sample['cases']};used=set();seed=sample['seed'];singletons=0
            stem=lambda members:{m[1].split(':',1)[0] for m in members}
            for label,item in design['strata'].items():
                if label.startswith('band-'):
                    lo,hi=label.split('-')[1:];population=stem(recomputed['count-'+hi])-stem(recomputed['count-'+lo]);n=40
                elif label=='score-disagreement':population=stem(recomputed['count-80000'])^stem(recomputed['score-0.05']);n=20
                elif label=='dispersion-disagreement':population=stem(recomputed['count-80000'])-stem(selections['dispersion-arf3-ratio0.1']['kept']);n=20
                else:
                    population=set('anyżowy szybkościomierz żelatynowy wypełzły dekagram kot pies ryba pensja kardamon rowerzystka koronawirus tomahawk psinka podjarać shaker mikrokomputer ruptura dejman dragować'.split());n=20
                population-=used
                chosen_sample=sorted(population,key=lambda w:hashlib.sha256(json.dumps([seed,label,w],ensure_ascii=False,separators=(',',':')).encode()).hexdigest())[:n]
                assert chosen_sample==item['selected'] and len(population)==item['population'],label
                used.update(chosen_sample)
            assert used==set(cases)
            for lemma,case in cases.items():
                assert set(r['row'] for r in raw.get(lemma,()))==set(r['row'] for r in case['original_kwjp_rows'])
                for row in case['evidence']:
                    m=tuple(row['key']);u=g['unit_of'][m]
                    if len(u)==1:
                        singletons+=1;assert row['kwjp_own']==json.loads(json.dumps(g['result']['units'][u]['kwjp']))
            result['sample_checks']={'cases':len(cases),'singletons_with_correct_own_evidence':singletons,'strata_exact':True,'dispersion_population_after_correction':True}
        result['scenarios'][scenario]={'count_variants_member_exact':len(CAPS),'score_variants_member_exact':len(expected['fixed_score_thresholds']),
            'full_form_and_coverage_checks':checks,'diagnostic_variants':diagnostic,'grid_cells_exact':len(grid),
            'standard_forms':len(data['standard']),'standard_expansion_exact':True}
        print(scenario,'passed',flush=True)
        del data,g,selections,recomputed,words;gc.collect()
    sensitivity=json.loads((OUT/'standard-sensitivity.json').read_text())['variants']
    for key in KEYS:
        a,b=all_forms['baseline'][key],all_forms['proposal'][key]
        ma,mb=all_members['baseline'][key],all_members['proposal'][key];e=sensitivity[key]
        assert (len(b-a),len(a-b),len(mb-ma),len(ma-mb))==(e['forms_added'],e['forms_removed'],e['members_added'],e['members_removed'])
        assert sorted(a-b)==e['removed_forms']
    for path in OUT.glob('*.json'):
        if path.name=='measurement-review.json':continue
        hits=scan_nkjp_raw(json.loads(path.read_text()))
        if hits:result['raw_nkjp_scan'][path.name]=hits
    assert not result['raw_nkjp_scan'],result['raw_nkjp_scan']
    assert (database.stat().st_size,database.stat().st_mtime_ns)==(db_stat.st_size,db_stat.st_mtime_ns)
    result.update(status='passed',standard_sensitivity_checked=list(KEYS),database_stat_unchanged=True,
       limitations=['Nie przebudowano grafu, miar ani morfologii z surowego NKJP.','Hash bazy potwierdzony w manifeście koordynatora; ta kontrola sprawdza tylko odczyt ro oraz niezmienny rozmiar/mtime.'],
       artifact_hashes={p.name:sha(p) for p in OUT.glob('*.json') if p.name!='measurement-review.json'})
    (OUT/'measurement-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('all passed',flush=True)


if __name__=='__main__':main()
