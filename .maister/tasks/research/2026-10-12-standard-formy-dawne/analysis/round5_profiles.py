"""Profile kolejnych pasm i jawne członkostwo ocenionej osobno próby."""
import collections
import json
import pickle
import statistics
from pathlib import Path
from round5_measure import OUT,TMP,TASK,original_rows,save,now


def main():
    rows=original_rows()
    with (TMP/'baseline-graph.pickle').open('rb') as f:data,g,sel=pickle.load(f)
    base_of=lambda ms:{m[1].split(':')[0] for m in ms}
    by_base=collections.defaultdict(list)
    for m in data['relevant']-data['proper']:by_base[m[1].split(':')[0]].append(m)
    profiles={}
    for lo,hi in ((40000,50000),(50000,60000),(60000,70000),(70000,80000),(80000,90000),(90000,100000)):
        labels=base_of(sel[f'count-{hi}']['kept'])-base_of(sel[f'count-{lo}']['kept'])
        f_values=[];ratios=[];arfs=[];genres=collections.Counter();flags=collections.Counter();statuses=collections.Counter()
        own,none=0,0
        for lemma in labels:
            rr=rows.get(lemma,[])
            if rr:
                own+=1;f_values.append(sum(r['freq'] for r in rr))
                best=min(rr,key=lambda r:(-r['freq'],r['row']))
                arfs.append(float(best['metrics']['ARF']));ratios.append(float(best['metrics']['ARF'])/best['freq'])
            else:none+=1
            seen=set()
            for m in by_base[lemma]:
                if m not in sel[f'count-{hi}']['kept']:continue
                key=g['unit_of'][m]
                if key in seen:continue
                seen.add(key)
                unit=g['result']['units'][key]
                flags.update(g['measured'][key]['flags'])
                statuses.update([unit['kwjp']['status']+'/'+unit['nkjp']['status']])
                if unit['kwjp']['genres'] is not None:genres.update([len(unit['kwjp']['genres'])])
        profiles[f'{lo}-{hi}']={'lemmas':len(labels),'own_original_kwjp_lemmas':own,'without_own_original_kwjp_lemmas':none,
            'own_F_sum_median_if_available':statistics.median(f_values) if f_values else None,
            'best_original_row_ARF_median_if_available':statistics.median(arfs) if arfs else None,
            'best_original_row_ARF_F_median_if_available':statistics.median(ratios) if ratios else None,
            'selected_group_flags_per_lemma':dict(flags),'selected_group_statuses_per_lemma':dict(statuses),
            'selected_group_genres_per_lemma':dict(genres)}
    save('band-profiles.json',{'created_at':now(),'bands':profiles,'notes':['Band unit is unique lemma base first appearing in the kept set.','Group counters may count more than once per lemma when separate selected groups share its base.','F sums distinct original rows of the same base; ARF/F always from one best original row.']})
    cases=json.loads((OUT/'sample-blind.json').read_text())['cases']
    design=json.loads((OUT/'sample-design.json').read_text())
    stratum={w:k for k,v in design['strata'].items() for w in v['selected']}
    selections={k:base_of(v['kept']) for k,v in sel.items()}
    annotated=[{'id':c['id'],'lemma':c['lemma'],'stratum':stratum[c['lemma']],
                'membership':{k:c['lemma'] in vv for k,vv in selections.items()}} for c in cases]
    save('sample-membership.json',{'method':'At least one selected lexeme of the base; first-pass reviewers must not read before committing their labels.','cases':annotated})
    # Guard omissions and example controls, not a random sample.
    in_kwjp=set(data['kwjp']['lexemes']).union(*data['kwjp']['groups'])
    allowed=set()
    for m in (data['relevant']-data['proper'])&in_kwjp:
        allowed.update(data['forms'].get(m,()));allowed.update(data['constructions']['forms'].get(m,()))
    from round5_measure import pop,formset,ROOT
    config=json.loads((ROOT/'config/generator/pop.json').read_text())
    frequent=pop.rank_frequent_forms(data['orth'][1],allowed,20000)
    misses={}
    for k,v in sel.items():
        if not k.startswith(('dispersion','kwjp')):continue
        forms=formset(data,config,v['kept'])
        misses[k]=[w for w in frequent if w not in forms]
    save('diagnostic-guard-misses.json',{'method':'First 20000 eligible lower-case orth forms by frozen KWJP frequency.','variants':misses})
    print(profiles)


if __name__=='__main__':main()
