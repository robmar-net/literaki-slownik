"""Sonda proponowanych reguł POP00; bez zmian generatora i wejść."""
from collections import Counter, defaultdict
from pathlib import Path
import csv
import gzip
import hashlib
from itertools import product
import json
import sqlite3

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
BASE = REPO / 'data/work/pop-v3-20261014-022011-a'
DATABASE = REPO / 'data/work/lists-v31-20261012-162111-a/build.sqlite'
ORTH = REPO / 'cache/kwjp/kwjp100-slowa-orth-all.csv.gz'

def classify(tag, rule=None):
    fields = tag.split(':')
    if 'n' in fields and ('pri' in fields or 'sec' in fields):
        return 'neuter-person-1-2'
    if rule == 'by-aglt-nwok-v1':
        return 'ordinary'
    if rule and rule != 'nie-prefix-degree-v2':
        return 'construction'
    if fields[0] in ('pact', 'ppas', 'pant', 'pacta'):
        return fields[0]
    if fields[0] == 'ger' and any('neg' in f.split('.') for f in fields[1:]):
        return 'negative-gerund'
    if fields[0] in ('adja', 'adjp'):
        return fields[0]
    if fields[0] in ('adj', 'adv') and any(set(f.split('.')) & {'com', 'comp', 'sup'} for f in fields[1:]):
        return 'degree-com-sup'
    return 'ordinary'

def classes(tag, rule=None):
    return {classify(':'.join(fields), rule)
            for fields in product(*(field.split('.') for field in tag.split(':')))}

with gzip.open(BASE / 'POP0.txt.gz', 'rt') as f:
    pop = set(f.read().splitlines())
chosen = {m for row in json.loads((BASE/'reports/units.json').read_text())['units']
          for m in row['members_in'].get('POP0', [])}
with gzip.open(ORTH, 'rt') as f:
    metrics = {r['']: float(r['ipm']) for r in csv.DictReader(f) if r[''] in pop}
analyses = defaultdict(set)
owners = defaultdict(set)
pos_words = defaultdict(set)
with sqlite3.connect(DATABASE.as_uri()+'?mode=ro', uri=True) as db:
    ids = {i: lemma+'@'+source for i,source,lemma in db.execute('select id,source_id,lemma_id from lexeme')
           if lemma+'@'+source in chosen}
    assert set(ids.values()) == chosen
    for start in range(0,len(ids),400):
        chunk=sorted(ids)[start:start+400]
        sql='select i.lexeme_id,s.game_key,i.tag from interpretation i join surface_form s on s.id=i.form_id where i.lexeme_id in ('+','.join('?'*len(chunk))+')'
        for ident,word,tag in db.execute(sql,chunk):
            if word in pop:
                analyses[word].update(classes(tag))
                owners[ids[ident]].add(word)
                pos_words[tag.split(':')[0]].add(word)
    sql="select c.game_key,c.lemma_id,c.expanded_tag,p.source_id,c.rule_id from derivation_candidate c join derivation_component p on p.candidate_key=c.candidate_key where p.kind='source_interpretation'"
    for word,lemma,tag,source,rule in db.execute(sql):
        member=lemma+'@'+source
        if member in chosen and word in pop:
            analyses[word].update(classes(tag,rule))
            owners[member].add(word)
assert set(analyses)==pop
assert set(owners)==chosen
ordinary={w for w,reasons in analyses.items() if 'ordinary' in reasons}
narrow={w for w,reasons in analyses.items() if reasons-{'neuter-person-1-2'}}
selected={'POP0':pop,'narrow':narrow}
for t in (0.1,0.5,1):
    selected['hybrid_'+str(t)]={w for w,reasons in analyses.items()
        if 'ordinary' in reasons or (reasons-{'neuter-person-1-2'} and metrics.get(w,-1)>=t)}
    selected['strict_'+str(t)]={w for w,v in metrics.items() if v>=t}
mass=sum(metrics.values())  # IPM, nikomu nie przypisujemy masy leksemowej
results={}
for name,words in selected.items():
    lost=sorted(m for m,forms in owners.items() if not forms & words)
    results[name]={'forms':len(words),'removed':len(pop-words),'lost_lexemes':len(lost),
        'lost_examples':lost[:20],'lengths':dict(sorted(Counter(map(len,words)).items())),
        'retained_published_pop0_ipm_pct':100*sum(metrics.get(w,0) for w in words)/mass}
examples='kot kotach kotem czytam czytasz czytaj czytajcie czytając czytany czytanymi czytanie zrobiłem zrobiłam byłem byłam zrobiliśmy zrobiłbym remontowałoś przeczytałobym zrobiwszy najmilszy najmilszemu miłemu mili miłymi lepszy lepszemu nieczytanie nieczytaniami czytajże bym byś byśmy byście'.split()
out={'description':'Sonda reguł do planu, nie zatwierdzona polityka ani lista wydania.',
    'database_sha256_pinned_not_recomputed':'4b0d17c6e75139042cf18d6ea9a24650d4e7906b999d3a0ce9331de2ecb27a45',
    'inputs':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (BASE/'POP0.txt.gz',BASE/'reports/units.json',ORTH)},
    'classes':{c:sum(c in reasons for reasons in analyses.values()) for c in sorted({c for r in analyses.values() for c in r})},
    'pos_form_counts':{p:len(w) for p,w in sorted(pos_words.items())},
    'variants':results,'examples':{w:{'in_pop0':w in pop,'classes':sorted(analyses.get(w,[])),
        'ipm':metrics.get(w),'variants':{name:w in words for name,words in selected.items()}}
        for w in examples}}
(TASK/'analysis/policy-probe.json').write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
print(json.dumps({'variants':{k:{a:b for a,b in v.items() if a in ('forms','removed','lost_lexemes')}
                            for k,v in results.items()}},ensure_ascii=False,indent=2))
