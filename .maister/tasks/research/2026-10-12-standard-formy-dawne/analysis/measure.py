"""Sondy researchu #4. Wyłącznie odczyt zamrożonej bazy; bez zmiany polityki.

Uruchom z katalogu repo: python3 .maister/tasks/research/2026-10-12-standard-formy-dawne/analysis/measure.py
Sondy lemma/POS są celowo prostym eksperymentem, nie algorytmem produkcyjnym.
"""
import hashlib
import json
import sqlite3
import subprocess
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
RUN = ROOT / 'data/work/lists-v30-20261010-165826-a'
TMP = ROOT / 'tmp/research-issue4'
TMP.mkdir(parents=True, exist_ok=True)
db = sqlite3.connect(f'file:{RUN}/build.sqlite?mode=ro', uri=True)
db.execute('PRAGMA query_only=ON')
HIST = 'linguistic-historical-form-v1'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 << 20), b''):
            h.update(block)
    return h.hexdigest()


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


database_sha = digest(RUN/'build.sqlite')
expected = json.loads((ROOT/'config/generator/pop-sources.json').read_text())['base']['database_sha256']
assert database_sha == expected, 'Baza nie odpowiada przypiętemu wydaniu.'
safe, any_history = set(), set()
for key, text in db.execute('select assessment_key,assessment from decision_payload'):
    value = json.loads(text)
    checks = [c for layer in ('language', 'game', 'profile', 'release_scope')
              for c in value[layer]['checks']]
    if any(c['rule_id'] == HIST and c['status'] == 'reject' for c in checks):
        any_history.add(key)
        if all(c['status'] == 'accept' or (c['rule_id'] == HIST and c['status'] == 'reject') for c in checks):
            safe.add(key)
print('payloads', len(any_history), len(safe), flush=True)

cache = TMP / 'candidates.json'
if cache.exists():
    rows = json.loads(cache.read_text())
else:
    # Bez tymczasowych tabel w bazie. Jedyny warunek znoszony: dawność.
    query = '''select distinct a.game_key,coalesce(l.lemma_id,c.lemma_id),
               coalesce(l.lemma_base,substr(c.lemma_id,1,instr(c.lemma_id||':',':')-1)),
               a.expanded_tag,coalesce(i.qualifiers,c.qualifiers),a.candidate_key is not null
               from variant_decision d join analysis a on a.analysis_key=d.analysis_key
               left join interpretation i on i.id=a.interpretation_id
               left join lexeme l on l.id=i.lexeme_id
               left join derivation_candidate c on c.candidate_key=a.candidate_key
               where d.variant='standard' and d.membership_status='reject'
               and d.assessment_key in (''' + ','.join('?' for _ in safe) + ')'
    rows = list(db.execute(query, sorted(safe)))
    save(cache, rows)
print('rows', len(rows), flush=True)
candidates = defaultdict(set)
for word, lemma_id, base, tag, labels, derived in rows:
    candidates[word].add((lemma_id, base, tag.split(':')[0], labels, derived))
standard = set((RUN / 'lists/standard.txt').read_text().splitlines())
already = set(candidates) & standard
candidates = {w: values for w, values in candidates.items() if w not in standard}
print('new possible',len(candidates),'already',len(already),flush=True)

forms = defaultdict(dict)
lemmas = defaultdict(dict)
for sid, kind, meta in db.execute('select source_id,kind,metadata from source_artifact'):
    if kind not in {'kwjp_orth', 'kwjp_orth_lc', 'kwjp_lemma'}:
        continue
    genre = json.loads(meta)['genre']
    for unit, pos, freq, typed in db.execute('select unit_1,pos,freq,typed_metrics from corpus_evidence where source_id=?', (sid,)):
        if kind == 'kwjp_lemma':
            lemmas[(unit, pos)][genre] = dict(json.loads(typed), freq=freq)
        elif unit == unit.lower():
            forms[unit][kind + '/' + genre] = freq


def f(word, genre, kind='kwjp_orth'):
    return forms.get(word, {}).get(kind + '/' + genre, 0)


def nf(word):
    return f(word, 'fakt') + f(word, 'publicystyka')


def lm(base, pos):
    data = lemmas.get((base, pos), {})
    return sum(data.get(g, {}).get('freq', 0) for g in ('fakt', 'publicystyka'))


def disperse(base, pos):
    data = lemmas.get((base, pos), {})
    # Jeden gatunek z >=30 i DP_norm<=0.9 jest sondą kontrolną.
    return any(data.get(g, {}).get('freq', 0) >= 30 and
               float(data.get(g, {}).get('DP_norm', 1)) <= .9 for g in ('fakt', 'publicystyka'))


scenarios = {f'form-nf-{threshold}': {w for w in candidates if nf(w) >= threshold} for threshold in (5, 10, 20, 30)}
scenarios['form-all-30'] = {w for w in candidates if f(w, 'all') >= 30}
for threshold in (30, 100):
    scenarios[f'lemma-nf-{threshold}'] = {w for w, vals in candidates.items()
        if any(lm(base, pos) >= threshold for _, base, pos, _, _ in vals)}
scenarios['lemma-nf-30-dispersion'] = {w for w, vals in candidates.items()
    if any(disperse(base, pos) for _, base, pos, _, _ in vals)}
scenarios['remove-age'] = set(candidates)
assert not scenarios['form-nf-30'], 'Obecny próg nie odtwarza zera zmian!'

benchmark = json.loads((ROOT/'tmp/benchmark/sjp-missing-v29.json').read_text())
top = benchmark['standard']['top']
top_hist = {r['word'] for r in top if HIST in (r.get('reject_rules') or [])}
summary = {}
for name, words in scenarios.items():
    summary[name] = {'new_forms': len(words), 'top2000_recovered': len(words & {r['word'] for r in top}),
       'top2000_history_recovered': len(words & top_hist),
       'source_lemma_ids_in_new_forms': len({v[0] for w in words for v in candidates[w]}),
       'no_published_lowercase_form': sum(f(w,'all') == 0 for w in words),
       'top_forms': [[w, nf(w), f(w, 'all')] for w in sorted(words, key=lambda w: (-f(w,'all'), w))[:50]]}
    (TMP/f'{name}.txt').write_text('\n'.join(sorted(words))+'\n')

examples = []
for word in 'desperacja desperacji desperacyj ekscytacją ekscytacja niezbędnik familia odzienie surdut aliści jakoż iże nazad trzykroć'.split():
    sources = list(db.execute('''select distinct l.lemma_id,l.lemma_base,i.tag,i.qualifiers
      from surface_form f join interpretation i on i.form_id=f.id join lexeme l on l.id=i.lexeme_id
      where f.original=?''', (word,)))
    examples.append({'word':word, 'standard':word in standard,'nf':nf(word),'orth_all':f(word,'all'),
       'orth_lc_all':f(word,'all','kwjp_orth_lc'), 'fakt':f(word,'fakt'), 'publicystyka':f(word,'publicystyka'),
       'analyses':[{'lemma':lid,'tag':tag,'labels':labels,'lemma_nf':lm(base,tag.split(':')[0]),
                   'lemma_metrics':lemmas.get((base,tag.split(':')[0]),{})} for lid,base,tag,labels in sources],
       'added_by':[name for name, words in scenarios.items() if word in words]})

# Próbka deterministyczna lematów: hash, nie SJP ani wybór znanych słów.
sample_lemmas = sorted({v[0] for w in scenarios['lemma-nf-30'] for v in candidates[w] if lm(v[1],v[2]) >= 30},
                      key=lambda x: hashlib.sha256(('issue4-v1:'+x).encode()).hexdigest())[:40]
sample = []
for lid in sample_lemmas:
    words = sorted(w for w in scenarios['lemma-nf-30'] if any(v[0]==lid and lm(v[1],v[2]) >= 30 for v in candidates[w]))
    values = sorted({v for w in words for v in candidates[w] if v[0]==lid and lm(v[1],v[2]) >= 30})
    sample.append({'lemma':lid,'new_forms':len(words),'forms':words[:15],
        'evidence':[{'pos':v[2], 'nf':lm(v[1],v[2]), 'metrics':lemmas.get((v[1],v[2]),{})} for v in values],
        'labels':sorted({v[3] for v in values})})

out={'created':subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip(),
     'run':str(RUN.relative_to(ROOT)), 'method':'replace only historical rejections within one otherwise accepted persisted analysis; unique new game_key; monotone scenarios',
     'standard':len(standard),'possible_new_forms':len(candidates),'historical_forms_already_standard':len(already),
     'benchmark_history_top2000':len(top_hist),'benchmark_run':benchmark['inputs']['run'],
     'scenarios':summary,'examples':examples,'sample':sample,
     'database_sha256':database_sha,'standard_sha256':digest(RUN/'lists/standard.txt'),
     'script_sha256':digest(Path(__file__))}
save(TASK/'analysis/findings/measurements.json',out)
save(TMP/'candidate-details.json',{w:sorted(v) for w,v in candidates.items()})
print(json.dumps({k:{kk:vv for kk,vv in v.items() if kk!='top_forms'} for k,v in summary.items()},ensure_ascii=False,indent=2),flush=True)
print('output',TASK/'analysis/findings/measurements.json',flush=True)
