"""Badawczy ślad POP. Nie zmienia konfiguracji, bazy ani pakietów wydania.

Cache zawiera dane korpusu i pozostaje ignorowany; JSON publikuje własne
wyniki, statusy i rangi, nigdy surowe częstości NKJP.
"""
import collections
import hashlib
import json
import pickle
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from literaki_slownik import pop
from literaki_slownik.database import connect

TASK = Path(__file__).resolve().parents[1]
TMP = ROOT/'tmp/research-issue4'
OUT = TASK/'analysis/findings/round4'
R3 = TASK/'analysis/findings/round3'
OUT.mkdir(exist_ok=True)

def save(name, obj):
    (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

def graph(data, nkjp, config):
    kwjp, relevant = data['kwjp'], data['relevant']
    eligible = relevant-data['proper']
    result = pop.units(kwjp, 'e', relevant, nkjp, data['owners'], eligible=eligible)
    result['units'] = {k:u for k,u in result['units'].items() if not data['proper'].issuperset(u['members'])}
    measured = pop.measure(result, config['d3'], config['d8'])['units']
    ranks = pop.rank_units(measured)
    cuts = {n:pop.threshold(ranks, result, config['d6'][n], kwjp, relevant, measured) for n in pop.LISTS}
    members = pop.member_units(result, kwjp, eligible, nkjp, data['owners'])
    own = pop.measure(members, config['d3'], config['d8'], floors=pop.measure_floors(result, config['d3']))['units']
    prune = pop.prune_members(members, own, measured, cuts)
    kept = {n:prune['lists'][n]['kept'] for n in pop.LISTS}
    lists = {n:pop.forms_for(kept[n],config['d2'],{'i':data['forms']},data['constructions'])['forms'] for n in pop.LISTS}
    return dict(result=result, measured=measured, ranks=ranks, cuts=cuts, members=members, own=own, prune=prune, kept=kept, lists=lists,
                unit_of={m:k for k,u in result['units'].items() for m in u['members']},
                sub_of={m:k for k,u in members['units'].items() for m in u['members']})

def key_label(k): return k[1]
def unit_label(k): return [key_label(m) for m in k]

def trace(g, m):
    u=g['unit_of'].get(m)
    if u is None:return {'lemma':m[1], 'eligible':False}
    obj=g['result']['units'][u]
    sub=g['sub_of'].get(m)
    ans={'lemma':m[1], 'unit':unit_label(u), 'unit_size':obj['size'],
         'kwjp':obj['kwjp'], 'nkjp':obj['nkjp'], 'measure':g['measured'][u], 'rank':g['ranks'].get(u),
         'selected_unit':{n:u in g['cuts'][n]['units'] for n in pop.LISTS},
         'kept_member':{n:m in g['kept'][n] for n in pop.LISTS}}
    if sub is not None:
        sm=g['members']['units'][sub]
        ans['subunit']={'members':unit_label(sub),'kwjp':sm['kwjp'],'nkjp':sm['nkjp'],'measure':g['own'][sub],'rank':g['prune']['members'][sub]['rank']}
    return ans

def summary(g):
    return {'ranked_units':len(g['ranks']),
            'cuts':{n:{k:v for k,v in c.items() if k not in ('units','members')} for n,c in g['cuts'].items()},
            'forms':{n:len(g['lists'][n]) for n in pop.LISTS},
            'kept_lexemes':{n:len(g['kept'][n]) for n in pop.LISTS}}

def delta(g, base):
    return {n:{'added':sorted(g['lists'][n]-base['lists'][n]),'removed':sorted(base['lists'][n]-g['lists'][n])} for n in pop.LISTS}

def update_forms(data, additions, removals, paths):
    changed=dict(data,standard=(data['standard']|additions)-removals)
    with connect(paths['database'],readonly=True) as db:
        changed['forms']=pop.load_forms(db,changed['standard'])
        changed['constructions']=pop.load_constructions(db,changed['standard'])
    changed['relevant']=frozenset(changed['forms'])
    return changed

def run():
    now=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
    with (TMP/'round3-pop-inputs.pickle').open('rb') as f:data,nkjp,config,paths,published=pickle.load(f)
    print('cache loaded',flush=True)
    base=graph(data,nkjp,config)
    assert all(base['lists'][n]==published[n] for n in pop.LISTS)
    print('baseline matches',summary(base),flush=True)
    additions=set(json.loads((R3/'proposal.json').read_text())['new_words'])
    changed=update_forms(data,additions,set(),paths)
    main=graph(changed,nkjp,config)
    d=delta(main,base)
    expected=json.loads((R3/'pop-impact.json').read_text())['deltas']
    assert all(d[n][k]==expected[n][k] for n in pop.LISTS for k in ('added','removed'))
    print('proposal matches',summary(main),flush=True)
    # Każdy utracony członek i każda forma, nie tylko przykłady.
    lost_members=base['kept']['pop']-main['kept']['pop']
    rows=[]
    for m in sorted(lost_members):
        before,after=trace(base,m),trace(main,m)
        u=main['unit_of'].get(m)
        if u is None:reason='not_eligible'
        elif u not in main['cuts']['pop']['units']:
            unchanged=(base['unit_of'][m]==u and base['measured'][u]==main['measured'][u])
            reason='threshold_only' if unchanged else 'unit_or_score_then_threshold'
        else:reason='member_pruning'
        removed=(data['forms'].get(m,frozenset())|data['constructions']['forms'].get(m,frozenset()))&set(d['pop']['removed'])
        rows.append({'key':list(m),'reason':reason,'before':before,'after':after,'removed_words':sorted(removed)})
    classified=set().union(*(set(r['removed_words']) for r in rows))
    assert classified==set(d['pop']['removed'])
    by_reason={r:sorted(set().union(*(set(x['removed_words']) for x in rows if x['reason']==r))) for r in sorted({x['reason'] for x in rows})}
    new_members=main['kept']['pop']-base['kept']['pop']
    removed_unit_keys=set(base['cuts']['pop']['units'])-set(main['cuts']['pop']['units'])
    added_unit_keys=set(main['cuts']['pop']['units'])-set(base['cuts']['pop']['units'])
    save('pop-losses.json',{'accessed_at':now,'baseline':summary(base),'proposal':summary(main),
         'exact_round3_delta_reproduced':True,'removed_forms':len(classified),'lost_members':len(lost_members),
         'new_members':len(new_members),'lost_unit_keys':len(removed_unit_keys),'new_unit_keys':len(added_unit_keys),
         'reason_counts':{k:len(v) for k,v in by_reason.items()},'words_by_reason':by_reason,'members':rows,
         'new_relevant':[{**trace(main,m),'proper':m in data['proper']} for m in sorted(changed['relevant']-data['relevant'])]})
    print('loss causes', {k:len(v) for k,v in by_reason.items()},flush=True)
    # Dag w izolacji, zgodnie z wcześniejszą kontrolą.
    strip=lambda fs:{k:v-{'dag'} for k,v in fs.items() if v-{'dag'}}
    no_dag=dict(data,standard=data['standard']-{'dag'},forms=strip(data['forms']),
                constructions=dict(data['constructions'],forms=strip(data['constructions']['forms'])))
    no_dag['relevant']=frozenset(no_dag['forms'])
    dg=graph(no_dag,nkjp,config)
    expected_dag=json.loads((R3/'dag-control.json').read_text())['deltas']
    assert delta(dg,base)==expected_dag
    affected={m for m in data['relevant'] if m[1].split(':')[0] in ('dag','daga','dekagram')}
    # Kontrola przyczynowa: zachowaj populację rankingu, usuń tylko formę dag z listy.
    freeze=dict(no_dag,relevant=data['relevant'])
    fg=graph(freeze,nkjp,config)
    # Kontrola źródła: samo KWJP, stałe pozostałe ustawienia, oba składy STANDARD.
    kwconfig=dict(config,d3={'source':'kwjp','field':'log-ipm'})
    kbase=graph(data,nkjp,kwconfig)
    kdag=graph(no_dag,nkjp,kwconfig)
    # Każda obserwowana forma, która łączy dekagram z niekwalifikującym członkiem.
    collision=[]
    eligible=no_dag['relevant']-data['proper']
    for word in sorted(nkjp['forms']):
        owners=data['owners'][word]
        if any(m[1].split(':')[0]=='dekagram' for m in owners) and len(owners)>1:
            collision.append({'word':word,'owners':[list(x) for x in owners],
                              'all_eligible_before':(data['relevant']-data['proper']).issuperset(owners),
                              'all_eligible_after':eligible.issuperset(owners)})
    save('dag-mechanism.json',{'accessed_at':now,'baseline':summary(base),'without_dag':summary(dg),
         'delta':delta(dg,base),'lost_relevant':[list(x) for x in sorted(data['relevant']-no_dag['relevant'])],
         'traces':[{'key':list(m),'before':trace(base,m),'after':trace(dg,m)} for m in sorted(affected)],
         'collisions':collision,
         'frozen_population_control':{'description':'Kontrola przyczynowa: ranking zachowuje bazowe relevant, formy list usuwają dag. To eksperyment, nie propozycja metody.','delta':delta(fg,base)},
         'kwjp_scoring_control':{'description':'Sama punktacja KWJP, topologia grup nadal z KWJP i NKJP. Izoluje wpływ mieszania miar; nie jest pełnym wycofaniem NKJP.','delta':delta(kdag,kbase),
                              'traces':[{'key':list(m),'before':trace(kbase,m),'after':trace(kdag,m)} for m in sorted(affected)]}})
    print('dag mechanisms saved',flush=True)
    hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ('literaki_slownik/pop.py','config/generator/pop.json','config/generator/pop-sources.json')}
    save('pop-validation.json',{'baseline_matches_published':True,'round3_proposal_matches':True,'round3_dag_matches':True,
         'all_2430_losses_attributed':True,'readonly_database':str(paths['database']), 'pins':hashes,
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'limitations':['Kontrole zamrożonej populacji i samej KWJP służą identyfikacji przyczyny. Nie wdrożono ani nie zatwierdzono żadnej z nich.']})

def kwjp_rebuild():
    """Osobna kontrola rzeczywistego wycofania NKJP także z budowania grup."""
    with (TMP/'round3-pop-inputs.pickle').open('rb') as f:data,nkjp,config,paths,published=pickle.load(f)
    strip=lambda fs:{k:v-{'dag'} for k,v in fs.items() if v-{'dag'}}
    no_dag=dict(data,standard=data['standard']-{'dag'},forms=strip(data['forms']),
                constructions=dict(data['constructions'],forms=strip(data['constructions']['forms'])))
    no_dag['relevant']=frozenset(no_dag['forms'])
    config=dict(config,d3={'source':'kwjp','field':'log-ipm'})
    before=graph(data,None,config)
    after=graph(no_dag,None,config)
    d=json.loads((OUT/'dag-mechanism.json').read_text())
    if 'kwjp_only_control' in d:
        d['kwjp_scoring_control']=d.pop('kwjp_only_control')
    d['kwjp_scoring_control']['description']='Sama punktacja KWJP, topologia grup nadal z KWJP i NKJP. Izoluje wpływ mieszania miar; nie jest pełnym wycofaniem NKJP.'
    affected={m for m in data['relevant'] if m[1].split(':')[0] in ('dag','daga','dekagram')}
    d['kwjp_full_control']={'description':'Pełne wycofanie NKJP: nkjp=None zarówno w budowie grup, jak i ocenie członków; miara tylko KWJP. Badanie przyczyny, bez wdrożenia.',
                           'before':summary(before),'after':summary(after),'delta':delta(after,before),
                           'traces':[{'key':list(m),'before':trace(before,m),'after':trace(after,m)} for m in sorted(affected)]}
    save('dag-mechanism.json',d)
    v=json.loads((OUT/'pop-validation.json').read_text())
    v['kwjp_control_corrected']='Rozdzielono samą punktację KWJP przy grupach NKJP od pełnego wycofania NKJP. Obie kontrole policzone.'
    v['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    save('pop-validation.json',v)
    print('KWJP full control',delta(after,before),flush=True)

def sensitivity_eight():
    """Osobny wariant nowej rekomendacji cofnięć; nie zmienia głównej paczki."""
    import importlib.util
    spec=importlib.util.spec_from_file_location('round3_pop',Path(__file__).with_name('round3_pop.py'))
    prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
    with (TMP/'round3-pop-inputs.pickle').open('rb') as f:data,nkjp,config,paths,published=pickle.load(f)
    review_bytes=(OUT/'current-twelve.json').read_bytes()
    cases=json.loads(review_bytes)['cases']
    selected=[c for c in cases if c['decision']=='kwalifikuje do cofnięcia po decyzji']
    removals={c['word'] for c in selected}
    assert removals=={'bad','dag','dyr','reż','sie','sui','wiosenno','świąteczno'}
    proposal=json.loads((R3/'proposal.json').read_text())
    changed=update_forms(data,set(proposal['new_words']),removals,paths)
    lists,summary=prior.calculate(changed,nkjp,config)
    assert all(summary['frequent_guard'][n]['missing']==0 for n in pop.LISTS)
    summary.update(research_only=True,implementation_approved=False,
                   description='Osobna analiza wrażliwości: 2382 dodatki oraz cofnięcie 24 obecnych analiz, jedynych ścieżek dla 8 napisów. Nie jest decyzją o cofnięciu.',
                   removed_standard_words=sorted(removals),removed_analysis_keys=[a['analysis_key'] for c in selected for a in c['accepted_analyses']],
                   standard_delta={'added':len(proposal['new_words']),'removed':len(removals)},
                   deltas={n:{'added':sorted(lists[n]-published[n]),'removed':sorted(published[n]-lists[n]),'net':len(lists[n])-len(published[n])} for n in pop.LISTS},
                   review_sha256=hashlib.sha256(review_bytes).hexdigest(),
                   proposal_sha256=hashlib.sha256((R3/'proposal.json').read_bytes()).hexdigest())
    assert review_bytes==(OUT/'current-twelve.json').read_bytes(),'Przegląd zmienił się podczas pomiaru; należy zweryfikować hash.'
    save('eight-sensitivity.json',summary)
    print({n:{k:len(v) if isinstance(v,list) else v for k,v in d.items()} for n,d in summary['deltas'].items()},flush=True)

if __name__=='__main__':
    if sys.argv[1:] == ['kwjp_rebuild']:kwjp_rebuild()
    elif sys.argv[1:] == ['sensitivity_eight']:sensitivity_eight()
    else:
        run()
        kwjp_rebuild()
