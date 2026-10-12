"""Kontrfaktyczny POP w pamięci; bez budowania pakietu i bez zapisu do bazy."""
import gzip
import hashlib
import json
import pickle
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
from literaki_slownik import pop
from literaki_slownik.database import connect

TASK=Path(__file__).resolve().parents[1]
TMP=ROOT/'tmp/research-issue4'
OUT=TASK/'analysis/findings/round3'
PACKAGE=ROOT/'data/work/pop-v2-20261011-194738-b'
CACHE=TMP/'round3-pop-inputs.pickle'

def save(path,obj): path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def digest_list(words): return hashlib.sha256(''.join(w+'\n' for w in sorted(words)).encode()).hexdigest()

def calculate(data,nkjp,config):
    kwjp,relevant,proper=data['kwjp'],data['relevant'],data['proper']
    eligible=relevant-proper
    result=pop.units(kwjp,'e',relevant,nkjp,data['owners'],eligible=eligible)
    result['units']={k:u for k,u in result['units'].items() if not proper.issuperset(u['members'])}
    members=pop.member_units(result,kwjp,eligible,nkjp,data['owners'])
    found=pop.measure(result,config['d3'],config['d8'])
    ranks=pop.rank_units(found['units'])
    cuts={n:pop.threshold(ranks,result,config['d6'][n],kwjp,relevant,found['units']) for n in pop.LISTS}
    own=pop.measure(members,config['d3'],config['d8'],floors=pop.measure_floors(result,config['d3']))['units']
    pruned=pop.prune_members(members,own,found['units'],cuts)
    kept={n:pruned['lists'][n]['kept'] for n in pop.LISTS}
    lists={n:pop.forms_for(kept[n],config['d2'],{'i':data['forms']},data['constructions'])['forms'] for n in pop.LISTS}
    assert lists['pop0']<=lists['pop']<=data['standard']
    in_kwjp=set(kwjp['lexemes']).union(*kwjp['groups'])
    with_lemma=set()
    for m in eligible&in_kwjp:
        with_lemma.update(data['forms'].get(m,()))
        with_lemma.update(data['constructions']['forms'].get(m,()))
    sid,orth=data['orth']
    freq=pop.rank_frequent_forms(orth,with_lemma,max(config['frequent_guard']['pop_top'],pop.FREQUENT_SAMPLE))
    guard=pop.frequent_guard(freq,lists,config['frequent_guard'],sid)
    assert all(w in lists['pop0'] for w in config['must_include_pop0'])
    summary={'method':config['version'],'standard_forms':len(data['standard']),
             'ranked_units':len(ranks),'relevant_lexemes':len(relevant),'frequent_guard':guard,
             'thresholds':{n:{k:v for k,v in cuts[n].items() if k not in ('units','members')} for n in pop.LISTS},
             'lists':{n:{'forms':len(lists[n]),'units':len(cuts[n]['units']),
                         'lexemes':len(relevant.intersection(kept[n])),
                         'sha256_uncompressed':digest_list(lists[n])} for n in pop.LISTS}}
    return lists,summary

def bootstrap():
    config=pop.load_config(ROOT/'config/generator/pop.json')
    sources=pop.load_sources(ROOT/'config/generator/pop-sources.json')
    paths=pop.check_inputs(sources)
    print('input pins checked',flush=True)
    data=pop._lexicon(paths,sources,True)
    print('morphology loaded',flush=True)
    nkjp=pop.read_nkjp(paths['nkjp'],config['d4'],data['owners'])
    lists,summary=calculate(data,nkjp,config)
    for name,filename in pop.LIST_FILES.items():
        expected=set(gzip.open(PACKAGE/filename,'rt').read().splitlines())
        assert lists[name]==expected,(name,len(lists[name]),len(expected))
    summary['baseline_matches_published_lists']=True
    summary['database_sha256']=paths['database_sha256']
    summary['config_sha256']=config['config_sha256']
    summary['published_manifest_sha256']=hashlib.sha256((PACKAGE/'release-manifest.json').read_bytes()).hexdigest()
    save(OUT/'pop-baseline.json',summary)
    with CACHE.open('wb') as stream: pickle.dump((data,nkjp,config,paths,lists),stream,pickle.HIGHEST_PROTOCOL)
    print(json.dumps(summary,ensure_ascii=False),flush=True)

def measure():
    with CACHE.open('rb') as stream: original,nkjp,config,paths,base=pickle.load(stream)
    input_name=sys.argv[2] if len(sys.argv)>2 else 'proposal.json'
    output_name=sys.argv[3] if len(sys.argv)>3 else 'pop-impact.json'
    scenario_bytes=(OUT/input_name).read_bytes()
    scenario=json.loads(scenario_bytes)
    additions=set(scenario['new_words']); removals=set(scenario.get('removed_words',[]))
    assert additions.isdisjoint(original['standard'])
    assert removals<=original['standard']
    changed=dict(original,standard=(original['standard']|additions)-removals)
    with connect(paths['database'],readonly=True) as db:
        changed['forms']=pop.load_forms(db,changed['standard'])
        changed['constructions']=pop.load_constructions(db,changed['standard'])
    changed['relevant']=frozenset(changed['forms'])
    print('changed morphology loaded',flush=True)
    lists,summary=calculate(changed,nkjp,config)
    summary['standard_delta']={'added':len(additions),'removed':len(removals)}
    summary['new_relevant_lexemes']=[list(x) for x in sorted(changed['relevant']-original['relevant'])]
    summary['lost_relevant_lexemes']=[list(x) for x in sorted(original['relevant']-changed['relevant'])]
    summary['deltas']={n:{'added':sorted(lists[n]-base[n]),'removed':sorted(base[n]-lists[n]),
                          'net':len(lists[n])-len(base[n]),
                          'previously_standard_entering':sorted((lists[n]-base[n])&original['standard'])} for n in pop.LISTS}
    # Pełny ponowny hash po kontrfaktycznym odczycie. Baza musi pozostać identyczna.
    after=pop.database_sha256(paths['database']);assert after==paths['database_sha256']
    summary['database_unchanged_sha256']=after
    assert scenario_bytes==(OUT/input_name).read_bytes(),'Propozycja zmieniła się w czasie pomiaru'
    summary['proposal_sha256']=hashlib.sha256(scenario_bytes).hexdigest()
    save(OUT/output_name,summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='deltas'},ensure_ascii=False),flush=True)
    print('DELTAS',{n:{k:len(v) if isinstance(v,list) else v for k,v in d.items()} for n,d in summary['deltas'].items()},flush=True)

def baseline_diagnostics():
    with CACHE.open('rb') as stream: data,nkjp,config,paths,base=pickle.load(stream)
    lists,summary=calculate(data,nkjp,config)
    assert all(lists[n]==base[n] for n in pop.LISTS)
    old=json.loads((OUT/'pop-baseline.json').read_text())
    old['thresholds']=summary['thresholds']
    save(OUT/'pop-baseline.json',old)
    print('baseline thresholds',summary['thresholds'],flush=True)

def impact_thresholds():
    with CACHE.open('rb') as stream: data,nkjp,config,paths,base=pickle.load(stream)
    impact=json.loads((OUT/'pop-impact.json').read_text())
    relevant=(data['relevant']|{tuple(x) for x in impact['new_relevant_lexemes']})-{tuple(x) for x in impact['lost_relevant_lexemes']}
    eligible=relevant-data['proper']
    result=pop.units(data['kwjp'],'e',relevant,nkjp,data['owners'],eligible=eligible)
    result['units']={k:u for k,u in result['units'].items() if not data['proper'].issuperset(u['members'])}
    measured=pop.measure(result,config['d3'],config['d8'])['units']
    ranks=pop.rank_units(measured)
    assert len(ranks)==impact['ranked_units']
    cuts={n:pop.threshold(ranks,result,config['d6'][n],data['kwjp'],relevant,measured) for n in pop.LISTS}
    assert all(len(cuts[n]['units'])==impact['lists'][n]['units'] for n in pop.LISTS)
    impact['thresholds']={n:{k:v for k,v in cuts[n].items() if k not in ('units','members')} for n in pop.LISTS}
    save(OUT/'pop-impact.json',impact)
    print('impact thresholds',impact['thresholds'],flush=True)

def dag_control():
    """Izolacja przyczyny: tylko cofnięcie dag z bazowego STANDARD."""
    with CACHE.open('rb') as stream: data,nkjp,config,paths,base=pickle.load(stream)
    def without_dag(forms):return {k:v-{'dag'} for k,v in forms.items() if v-{'dag'}}
    changed=dict(data,standard=data['standard']-{'dag'},forms=without_dag(data['forms']),
                 constructions=dict(data['constructions'],forms=without_dag(data['constructions']['forms'])))
    changed['relevant']=frozenset(changed['forms'])
    lists,summary=calculate(changed,nkjp,config)
    summary['intervention']='Usunięto wyłącznie dag z bazowego STANDARD; bez proponowanych dodatków i innych cofnięć.'
    summary['deltas']={n:{'added':sorted(lists[n]-base[n]),'removed':sorted(base[n]-lists[n])} for n in pop.LISTS}
    save(OUT/'dag-control.json',summary)
    print('dag-only delta',{n:{k:len(v) for k,v in d.items()} for n,d in summary['deltas'].items()},flush=True)
    print('POP0 removed',summary['deltas']['pop0']['removed'],flush=True)

if __name__=='__main__':
    {'bootstrap':bootstrap,'measure':measure,'baseline_diagnostics':baseline_diagnostics,'impact_thresholds':impact_thresholds,'dag_control':dag_control}[sys.argv[1]]()
