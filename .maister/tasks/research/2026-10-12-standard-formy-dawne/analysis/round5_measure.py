"""Kalibracja POP w pamięci. Kod produkcyjny, baza i wydania bez zmian.

Odtworzenie: python3 PATH/round5_measure.py. Cache wejściowy można odtworzyć
przez round3_pop.py bootstrap; wszystkie duże pośrednie dane zostają w tmp/.
"""
import collections
import gzip
import hashlib
import json
import math
import pickle
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from literaki_slownik import pop
from literaki_slownik.database import connect
from round4_pop import graph, update_forms
from round3_pop import digest_list

OUT = TASK/'analysis/findings/round5'
TMP = ROOT/'tmp/research-issue4/round5'
CAPS = [40000, 50000, 60000, 60025, 65000, 70000, 75000, 80000, 90000, 100000]
SCORES = [0.1, 0.075, 0.05, 0.025, 0.01]
SEED = 'issue4-round5-pop-boundary-v1'


def now():
    return subprocess.check_output(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], text=True).strip()


def save(name, obj):
    (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def score_cut(g, minimum):
    keys = [k for k in g['ranks'] if g['measured'][k]['value'] >= minimum]
    members = frozenset(m for k in keys for m in g['result']['units'][k]['members'])
    return {'units': tuple(keys), 'members': members, 'lexemes': len(members),
            'rank': max((g['ranks'][k] for k in keys), default=0), 'reached': True,
            'next_block': None, 'minimum_score': minimum}


def value_prune(g, cut, minimum):
    """Wariant badawczy: własna miara >= minimum, z tymi samymi wyjątkami głowy/braku podziału."""
    by_unit = collections.defaultdict(list)
    for key, obj in g['members']['units'].items():
        by_unit[obj['unit']].append(key)
    removed, heads = set(), 0
    for unit in cut['units']:
        subs = by_unit[unit]
        if len(subs) <= 1:
            continue
        values = [g['own'][key]['value'] for key in subs if g['own'][key]['value'] is not None]
        if not values:
            continue
        best = max(values)
        heads += best < minimum
        for key in subs:
            value = g['own'][key]['value']
            if value != best and (value is None or value < minimum):
                removed.update(key)
    return {'kept': frozenset(cut['members']-removed), 'pruned': tuple(sorted(removed)), 'heads': heads}


def formset(data, config, members):
    return pop.forms_for(members, config['d2'], {'i': data['forms']}, data['constructions'])['forms']


def metrics(data, g, config, cut, pruned, forms, published, frequent):
    kept = pruned['kept']
    statuses = collections.Counter('/'.join((g['result']['units'][k]['kwjp']['status'],
                                            g['result']['units'][k]['nkjp']['status'])) for k in cut['units'])
    flags = collections.Counter(flag for k in cut['units'] for flag in g['measured'][k]['flags'])
    scores = [g['measured'][k]['value'] for k in cut['units']]
    return {'units': len(cut['units']), 'lexemes_before_pruning': cut['lexemes'],
            'lexemes': len(kept), 'lemmas': len({m[1].split(':')[0] for m in kept}),
            'forms': len(forms), 'sha256_forms': digest_list(forms),
            'last_score': min(scores) if scores else None, 'cut_rank': cut['rank'],
            'next_block': cut.get('next_block'), 'pruned_lexemes': len(pruned['pruned']),
            'head_exceptions_units': pruned['heads'], 'selected_unit_statuses': dict(statuses),
            'selected_unit_flags': dict(flags),
            'coverage': {d: pop.coverage(kept, data['kwjp'], d, data['relevant']) for d in ('kwjp-standard','kwjp-all')},
            'versus_published': {'added': len(forms-published), 'removed': len(published-forms)},
            'frequent_guard_missing': len(set(frequent[:20000])-forms)}


def run_scenario(name, data, nkjp, config, published, fixed):
    g = graph(data, nkjp, config)
    print(name, 'graph ready', len(g['ranks']), flush=True)
    in_kwjp = set(data['kwjp']['lexemes']).union(*data['kwjp']['groups'])
    allowed = set()
    for m in (data['relevant']-data['proper']) & in_kwjp:
        allowed.update(data['forms'].get(m, ()))
        allowed.update(data['constructions']['forms'].get(m, ()))
    frequent = pop.rank_frequent_forms(data['orth'][1], allowed, 50000)
    frequent_words = frequent
    results, selections = {}, {}
    previous = frozenset()
    for cap in CAPS:
        cut = pop.threshold(g['ranks'], g['result'], {'by':'count','value':cap},
                            data['kwjp'], data['relevant'], g['measured'])
        pruned = pop.prune_members(g['members'],g['own'],g['measured'],{'pop':cut})['lists']['pop']
        forms = formset(data,config,pruned['kept'])
        assert previous <= pruned['kept'], (name,cap,'nonmonotonic')
        previous = pruned['kept']
        if cap == 60000:
            assert forms == g['lists']['pop']
            if name == 'baseline':
                assert forms == published['pop'] and g['lists']['pop0'] == published['pop0']
                fixed['baseline60k'] = min(g['measured'][k]['value'] for k in cut['units'])
            else:
                expected = json.loads((TASK/'analysis/findings/round3/pop-impact.json').read_text())['deltas']
                assert sorted(forms-published['pop']) == expected['pop']['added']
                assert sorted(published['pop']-forms) == expected['pop']['removed']
        key = f'count-{cap}'
        results[key] = metrics(data,g,config,cut,pruned,forms,published['pop'],frequent_words)
        results[key]['policy'] = {'kind':'count','cap':cap,'pruning':'current-rank'}
        selections[key] = {'kept':pruned['kept'],'cut':cut}
        print(name,key,results[key]['lexemes'],len(forms),flush=True)
    thresholds = {'baseline60k': fixed['baseline60k'], **{str(x):math.log10(x) for x in SCORES}}
    for label, minimum in thresholds.items():
        cut = score_cut(g,minimum)
        pruned = value_prune(g,cut,minimum)
        forms = formset(data,config,pruned['kept'])
        by_rank = pop.prune_members(g['members'],g['own'],g['measured'],{'pop':cut})['lists']['pop']
        key = f'score-{label}'
        results[key] = metrics(data,g,config,cut,pruned,forms,published['pop'],frequent_words)
        results[key]['policy'] = {'kind':'score','minimum_score':minimum,'label':label,'pruning':'own-score-plus-existing-exceptions'}
        results[key]['rank_pruning_comparison'] = {'own_score_only_extra_members':len(pruned['kept']-by_rank['kept']),
                                                  'rank_only_extra_members':len(by_rank['kept']-pruned['kept'])}
        selections[key] = {'kept':pruned['kept'],'cut':cut}
        print(name,key,results[key]['lexemes'],len(forms),flush=True)
    diagnostic,grid=dispersion(data,g,config,published['pop'],frequent_words,selections)
    results.update(diagnostic)
    save(f'{name}-dispersion-grid.json',{'grid':grid})
    save(f'{name}-measurements.json',{'created_at':now(),'research_only':True,'scenario':name,
             'standard_forms':len(data['standard']),'variants':results,'pop0':{'forms':len(g['lists']['pop0']),
             'sha256_forms':digest_list(g['lists']['pop0'])},'fixed_score_thresholds':thresholds})
    with (TMP/f'{name}-graph.pickle').open('wb') as f:
        pickle.dump((data,g,selections),f,pickle.HIGHEST_PROTOCOL)
    return results


def sample_row(data,g,lemma):
    members = sorted(m for m in data['relevant']-data['proper'] if m[1].split(':')[0] == lemma)
    rows = []
    for m in members:
        u,sub = g['unit_of'].get(m),g['sub_of'].get(m)
        if u is None:
            continue
        obj = g['result']['units'][u]
        own = g['members']['units'][sub] if sub else obj if len(u)==1 else None
        rows.append({'key':list(m),'pos':data['pos'].get(m),'group_members':[x[1] for x in u],
                     'kwjp_group':obj['kwjp'],'nkjp_group_status':obj['nkjp']['status'],
                     'kwjp_own':own['kwjp'] if own else None,
                     'nkjp_own_status':own['nkjp']['status'] if own else None,
                     'score_flags':g['measured'][u]['flags'],
                     'standard_forms_count':len(data['forms'].get(m,())),
                     'forms_examples':sorted(data['forms'].get(m,()))[:5]})
    original=original_rows().get(lemma,[])
    return {'lemma':lemma,'evidence':rows,'original_kwjp_rows':[
        {'row':r['row'],'unit':r['unit'],'pos':r['pos'],'F':r['freq'],'ARF':r['metrics']['ARF'],
         'DP':r['metrics'].get('DP'),'DP_norm':r['metrics'].get('DP_norm'),'status':r['status']} for r in original]}


def samples():
    with (TMP/'baseline-graph.pickle').open('rb') as f:data,g,sel=pickle.load(f)
    stem = lambda ms:{m[1].split(':')[0] for m in ms}
    all_samples, inventory, used = [], {}, set()
    def pick(label,population,n):
        population=sorted(population-used)
        ordered=sorted(population,key=lambda w:hashlib.sha256(json.dumps([SEED,label,w],ensure_ascii=False,separators=(',',':')).encode()).hexdigest())
        chosen=ordered[:n]
        inventory[label]={'population':len(population),'selected':chosen,'method':'lowest SHA256([seed,stratum,lemma]), UTF-8 compact JSON'}
        for lemma in chosen:
            row=sample_row(data,g,lemma)
            row['id']=hashlib.sha256((SEED+'|'+lemma).encode()).hexdigest()[:12]
            all_samples.append(row)
        used.update(chosen)
    for lo,hi in ((40000,50000),(50000,60000),(60000,70000),(70000,80000),(80000,90000),(90000,100000)):
        pick(f'band-{lo}-{hi}',stem(sel[f'count-{hi}']['kept'])-stem(sel[f'count-{lo}']['kept']),40)
    disagree=stem(sel['count-80000']['kept']) ^ stem(sel['score-0.05']['kept'])
    pick('score-disagreement',disagree,20)
    dispersion=stem(sel['count-80000']['kept'])-stem(sel['dispersion-arf3-ratio0.1']['kept'])
    pick('dispersion-disagreement',dispersion,20)
    controls=set('anyżowy szybkościomierz żelatynowy wypełzły dekagram kot pies ryba pensja kardamon rowerzystka koronawirus tomahawk psinka podjarać shaker mikrokomputer ruptura dejman dragować'.split())
    pick('named-controls',controls,20)
    all_samples.sort(key=lambda r:r['id'])
    save('sample-blind.json',{'seed':SEED,'method':'Evidence visible; stratum, rank, score and membership withheld from initial reviewer.','cases':all_samples})
    save('sample-design.json',{'seed':SEED,'created_at':now(),'strata':inventory,'unique_lemmas':len(used)})
    for label,offset in (('a',0),('b',1)):
        rows=all_samples[offset::2]
        save(f'sample-blind-{label}.json',{'seed':SEED,'cases':rows})
    # Thirty shared cases for a later independent check. No duplicate first-pass assignment.
    save('sample-crosscheck.json',{'cases':all_samples[:30]})
    print('sample',len(all_samples),{k:v['population'] for k,v in inventory.items()},flush=True)


def comparisons():
    with (TMP/'baseline-graph.pickle').open('rb') as f:before,gb,sb=pickle.load(f)
    with (TMP/'proposal-graph.pickle').open('rb') as f:after,ga,sa=pickle.load(f)
    config=json.loads((ROOT/'config/generator/pop.json').read_text())
    variants={}
    for key in sb:
        a,b=sb[key]['kept'],sa[key]['kept']
        fa,fb=formset(before,config,a),formset(after,config,b)
        variants[key]={'members_added':len(b-a),'members_removed':len(a-b),'forms_added':len(fb-fa),'forms_removed':len(fa-fb),
                       'added_lemmas':sorted({m[1] for m in b-a}),'removed_lemmas':sorted({m[1] for m in a-b}),
                       'removed_forms':sorted(fa-fb)}
    save('standard-sensitivity.json',{'created_at':now(),'variants':variants})


_ROW_CACHE = None


def original_rows():
    """Jeden oryginalny wiersz KWJP, wszyscy kandydaci mają tę samą podstawę."""
    global _ROW_CACHE
    if _ROW_CACHE is None:
        path=ROOT/'data/work/lists-v30-20261010-165826-a/build.sqlite'
        with connect(path,readonly=True) as db:
            rows=pop.load_kwjp(db,'KWJP100-kwjp100-slowa-lemma-all')
        _ROW_CACHE=collections.defaultdict(list)
        for r in rows:
            bases={m[1].split(':')[0] for m in r['lexemes']}
            if len(bases)==1:_ROW_CACHE[next(iter(bases))].append(r)
    return _ROW_CACHE


def row_passes(row,arf,ratio,freq=0):
    return row['freq']>=freq and float(row['metrics']['ARF'])>=arf and float(row['metrics']['ARF'])/row['freq']>=ratio


def dispersion(data,g,config,published,frequent_words,selections):
    """OR oryginalnych wierszy; ARF i F zawsze z tego samego rekordu."""
    rows=original_rows()
    results={}
    def record(key,selected,policy,unknown=()):
        selected=frozenset(selected)
        forms=formset(data,config,selected)
        results[key]={'policy':policy,'lexemes':len(selected),'forms':len(forms),'sha256_forms':digest_list(forms),
                      'unknown_lexemes':len(unknown),
                      'coverage':{d:pop.coverage(selected,data['kwjp'],d,data['relevant']) for d in ('kwjp-standard','kwjp-all')},
                      'versus_published':{'added':len(forms-published),'removed':len(published-forms)},
                      'frequent_guard_missing':len(set(frequent_words[:20000])-forms)}
        selections[key]={'kept':selected,'unknown':frozenset(unknown)}
    for arf in (3,10):
        for ratio in (0.1,0.3):
            kept,unknown=set(),set()
            for m in selections['count-80000']['kept']:
                own=rows.get(m[1].split(':')[0],[])
                if not own:unknown.add(m)
                elif any(row_passes(r,arf,ratio) for r in own):kept.add(m)
            for fallback in (False,True):
                key=f'dispersion-arf{arf}-ratio{ratio}'+('-keep-unknown' if fallback else '')
                record(key,kept|(unknown if fallback else set()),
                       {'kind':'diagnostic-filter-count80000','min_ARF':arf,'min_ARF_F':ratio,
                        'unknown':'kept' if fallback else 'not_selected_separately_counted',
                        'evidence':'OR original KWJP rows; all candidates share lemma base'},unknown)
    eligible=data['relevant']-data['proper']
    unknown_eligible={m for m in eligible if not rows.get(m[1].split(':')[0])}
    for freq,arf in ((10,3),(20,5),(50,10)):
        selected={m for m in eligible if any(row_passes(r,arf,0.1,freq) for r in rows.get(m[1].split(':')[0],()))}
        record(f'kwjp-F{freq}-ARF{arf}-ratio0.1',selected,
               {'kind':'absolute-own-kwjp','min_F':freq,'min_ARF':arf,'min_ARF_F':0.1,'unknown':'not_selected',
                'evidence':'OR original KWJP rows; all candidates share lemma base'},unknown_eligible)
    grid=[]
    for arf in (1.1,2,3,5,10):
        for ratio in (0,0.01,0.03,0.1,0.3):
            accepted={m for m in selections['count-80000']['kept'] if any(row_passes(r,arf,ratio) for r in rows.get(m[1].split(':')[0],()))}
            unknown={m for m in selections['count-80000']['kept'] if not rows.get(m[1].split(':')[0])}
            grid.append({'ARF':arf,'ARF_F':ratio,'observed_pass_lexemes':len(accepted),'unknown_lexemes':len(unknown),
                         'keep_unknown_lexemes':len(accepted|unknown)})
    return results,grid


def repair_diagnostics():
    """Wznowienie korekty sondy; bazowe pomiary limitów i wartości nie zmieniają się."""
    config=json.loads((ROOT/'config/generator/pop.json').read_text())
    for name in ('baseline','proposal'):
        with (TMP/f'{name}-graph.pickle').open('rb') as f:data,g,sel=pickle.load(f)
        path=OUT/f'{name}-measurements.json'
        prior=json.loads(path.read_text())
        archive=TMP/f'{name}-measurements-before-own-row-fix.json'
        if not archive.exists():archive.write_bytes(path.read_bytes())
        with (ROOT/'tmp/research-issue4/round3-pop-inputs.pickle').open('rb') as f:published=pickle.load(f)[4]
        in_kwjp=set(data['kwjp']['lexemes']).union(*data['kwjp']['groups'])
        allowed=set()
        for m in (data['relevant']-data['proper'])&in_kwjp:
            allowed.update(data['forms'].get(m,()))
            allowed.update(data['constructions']['forms'].get(m,()))
        frequent=pop.rank_frequent_forms(data['orth'][1],allowed,50000)
        results,grid=dispersion(data,g,config,published['pop'],frequent,sel)
        prior['variants'].update(results)
        prior['corrected_at']=now()
        prior['diagnostic_correction']='Original rows for singleton and pooled lemmas; ARF/F from the same row. Earlier diagnostic invalid, archived locally.'
        save(path.name,prior)
        save(f'{name}-dispersion-grid.json',{'grid':grid})
        with (TMP/f'{name}-graph.pickle').open('wb') as f:pickle.dump((data,g,sel),f,pickle.HIGHEST_PROTOCOL)
        print(name,'diagnostics corrected',flush=True)
        del data,g,sel,published
    samples();comparisons()
    inputs=json.loads((OUT/'input-manifest.json').read_text())
    inputs.update(script_sha256=sha(Path(__file__)),diagnostics_corrected_at=now())
    save('input-manifest.json',inputs)


def main():
    OUT.mkdir(exist_ok=True);TMP.mkdir(exist_ok=True)
    cache=ROOT/'tmp/research-issue4/round3-pop-inputs.pickle'
    with cache.open('rb') as f:data,nkjp,config,paths,cached_published=pickle.load(f)
    assert sha(ROOT/'config/generator/pop.json') == config['config_sha256']
    package=ROOT/'data/work/pop-v2-20261011-194738-b'
    published={n:set(gzip.open(package/filename,'rt').read().splitlines()) for n,filename in pop.LIST_FILES.items()}
    assert all(published[n]==cached_published[n] for n in pop.LISTS)
    inputs={'cache_sha256':sha(cache),'database_expected_sha256':paths['database_sha256'],
            'config_sha256':sha(ROOT/'config/generator/pop.json'),'source_manifest_sha256':sha(ROOT/'config/generator/pop-sources.json'),
            'production_code_sha256':sha(ROOT/'literaki_slownik/pop.py'),
            'proposal_sha256':sha(TASK/'analysis/findings/round3/proposal.json'),
            'script_sha256':sha(Path(__file__)),'started_at':now(),'read_only_database':str(paths['database'])}
    save('input-manifest.json',inputs)
    fixed={}
    run_scenario('baseline',data,nkjp,config,published,fixed)
    additions=set(json.loads((TASK/'analysis/findings/round3/proposal.json').read_text())['new_words'])
    changed=update_forms(data,additions,set(),paths)
    print('proposal morphology loaded',flush=True)
    run_scenario('proposal',changed,nkjp,config,published,fixed)
    del changed,data,nkjp
    samples()
    comparisons()
    actual=pop.database_sha256(paths['database'])
    assert actual==paths['database_sha256']
    inputs.update(finished_at=now(),database_verified_sha256=actual,script_sha256=sha(Path(__file__)))
    save('input-manifest.json',inputs)
    print('complete',flush=True)


if __name__=='__main__':
    if sys.argv[1:]==['samples']:samples()
    elif sys.argv[1:]==['comparisons']:comparisons()
    elif sys.argv[1:]==['repair_diagnostics']:repair_diagnostics()
    else:main()
