"""Sonda uzupełniająca po wykryciu dawnych odmian we wstępnej próbce #4.

Nie jest strojona do SJP. Utrzymuje jawne etykiety arch. jako blokadę
nowego wyjątku lematowego. Nie zmienia dotychczasowych przyjęć STANDARD.
"""
import csv
import gzip
import hashlib
import json
from decimal import Decimal
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
TMP = ROOT/'tmp/research-issue4'
data = json.loads((TMP/'candidate-details.json').read_text())
lm = Counter()
for genre in ('fakt', 'publicystyka'):
    with gzip.open(ROOT/f'cache/kwjp/kwjp100-slowa-lemma-{genre}.csv.gz', 'rt') as stream:
        reader = csv.reader(stream)
        next(reader)
        for row in reader:
            frequency = Decimal(row[2])
            assert frequency == int(frequency)
            lm[(row[0], row[1])] += int(frequency)


def archaic(labels):
    return any('arch.' in label.split(',') for label in labels.split('|'))


eligible = defaultdict(set)
all_lemmas = set()
arch_only = set()
full = set((TMP/'lemma-nf-30.txt').read_text().splitlines())
for word in full:
    matching = [v for v in data[word] if lm[(v[1],v[2])] >= 30]
    all_lemmas.update(v[0] for v in matching)
    good = [v for v in matching if not archaic(v[3])]
    if good:
        for v in good:
            eligible[v[0]].add(word)
    else:
        arch_only.add(word)
words = set().union(*eligible.values())
benchmark = json.loads((ROOT/'tmp/benchmark/sjp-missing-v29.json').read_text())
top = {r['word'] for r in benchmark['standard']['top']}
sample = []
for lid in sorted(eligible, key=lambda x:hashlib.sha256(('issue4-noarch-v1:'+x).encode()).hexdigest())[:30]:
    forms = sorted(eligible[lid])
    sample.append({'lemma':lid,'count':len(forms),'forms':forms[:20],
                   'labels':sorted({v[3] for w in forms for v in data[w] if v[0]==lid})})
out={'reason':'Wstępna próbka wykazała przenoszenie dowodu żywego leksemu na archaiczne formy.',
 'scope':'Dodatkowy wyjątek lemma+POS NF≥30, bez etykiety arch.; stare przyjęcia zachowane.',
 'new_forms':len(words),'matched_lemma_ids':len(eligible),'lemma30_matched_lemma_ids':len(all_lemmas),
 'blocked_arch_only_forms':len(arch_only),'top2000_recovered':len(words&top),'sample':sample}
(TASK/'analysis/findings/followup.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(TMP/'lemma-nf-30-noarch.txt').write_text('\n'.join(sorted(words))+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
