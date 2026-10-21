"""Odtwarzalna sonda form POP0; nie jest generatorem ani wyborem progu."""
from pathlib import Path
import csv, gzip, hashlib, json
from collections import Counter

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
POP = REPO / 'tmp/release-pop-v3/POP0.txt.gz'
ALL = REPO / 'cache/kwjp/kwjp100-slowa-orth-all.csv.gz'
FIC = REPO / 'cache/kwjp/kwjp100-slowa-orth-fikcja.csv.gz'
LOW = REPO / 'cache/kwjp/kwjp100-slowa-orth_lc-all.csv.gz'

def read(path):
    with gzip.open(path, 'rt') as stream:
        return {r['']: {k: float(v) for k,v in r.items() if k} for r in csv.DictReader(stream)}

with gzip.open(POP, 'rt') as stream:
    pop = set(stream.read().splitlines())
all_rows, fic, lower = read(ALL), read(FIC), read(LOW)
observed = pop & all_rows.keys()
mass = sum(all_rows[w]['freq'] for w in observed)
published_mass = sum(r['freq'] for w,r in all_rows.items() if w == w.lower())

def stats(kept):
    retained_mass=sum(all_rows.get(w,{}).get('freq',0) for w in kept)
    return {'forms':len(kept), 'share_pop0_pct':100*len(kept)/len(pop),
            'mass_within_observed_pop0_pct':100*retained_mass/mass,
            'mass_published_lowercase_orth_pct':100*retained_mass/published_mass,
            'lengths':dict(sorted(Counter(map(len,kept)).items()))}

variants={'POP0':stats(pop), 'observed':stats(observed)}
for t in (0.1,0.5,1,2,5):
    variants[f'ipm_{t}']=stats({w for w in observed if all_rows[w]['ipm']>=t})
variants['all_or_fiction_ipm_1']=stats({w for w in pop if max(all_rows.get(w,{}).get('ipm',0),fic.get(w,{}).get('ipm',0))>=1})
examples='kot kota kotem kotu kotami kotach kocie pies psa psie psami dom domu domem domami kobieta kobieto kobiecie książka książką książkami czytam czytasz czyta czytaj czytajcie czytając czytawszy zrobił zrobiłem zrobiłam zrobiliśmy zrobiłbym zrobiłabym zrobiłbyś jestem jesteś byliśmy byłam byłem jesteśmy remontowałoś przeczytałobym nieczytanie umywszy zrobiwszy dziękuję proszę cześć pa papa hej siedmioletni sześcioletni nieładny nieładna nieładnie miły mili miłymi miłemu pięknie ładnie'.split()
sample={w:{'pop0':w in pop,'all':all_rows.get(w),'fiction':fic.get(w),'casefold_ipm':lower.get(w,{}).get('ipm')} for w in examples}
result={'method':'Bez normalizacji poza wejściowym zapisem POP0; dokładny małoliterowy zapis orth. Brak wiersza nie jest zerową częstością językową. Progi odnoszą się do opublikowanego IPM z 2 miejscami.',
        'inputs':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (POP,ALL,FIC,LOW)},
        'counts':{'pop0':len(pop),'observed_exact':len(observed),'missing_exact':len(pop-observed),'observed_casefold':len(pop&lower.keys())},
        'variants':variants,'examples':sample}
out=TASK/'analysis/evidence/form-measurement.json'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'counts':result['counts'],'variants':{k:{a:b for a,b in v.items() if a!='lengths'} for k,v in variants.items()},'examples':{w:{'pop0':r['pop0'],'ipm':r['all']['ipm'] if r['all'] else None} for w,r in sample.items()}},ensure_ascii=False,indent=2))
