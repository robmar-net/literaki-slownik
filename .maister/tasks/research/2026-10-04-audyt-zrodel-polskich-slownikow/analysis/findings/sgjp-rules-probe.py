"""Audyt form SGJP; nie jest generatorem słownika gry. Uruchom z katalogu repo."""
from pathlib import Path
import collections
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SOURCE = Path('cache/sgjp/sgjp-20260823.tab.gz')
forms = {'czytałem', 'czytałbym', 'gniótłem', 'gniotłem', 'gniótłbym', 'gniotł',
         'em', 'eśmy', 'ś', 'by', 'bym', 'byśmy', 'doń', 'przezeń', 'biało',
         'czytajże', 'czytaj', 'nieczytanie', 'niegrzeczniejszy', 'będę', 'ń', 'że', 'ż', 'polsku'}
counts = collections.Counter()
examples = []
base = []
direct = set()
aglt = []
dependent = []
with gzip.open(SOURCE, 'rt', encoding='utf-8') as f:
    for line in f:
        row = line.rstrip('\n').split('\t')
        if len(row) != 5:
            continue
        form, lemma, tag, name, labels = row
        parts = tag.split(':')
        pos = parts[0]
        person = any(p in {'pri','sec','ter'} for p in parts)
        if pos in {'praet','cond','winien','aglt','bedzie'}:
            counts[f'{pos}:{"person" if person else "no_person"}'] += 1
        if form in forms:
            examples.append(row)
        if pos == 'aglt':
            aglt.append(row)
        if pos == 'praet' and not person:
            base.append(row)
        if pos in {'praet','cond'} and person:
            direct.add((form, lemma, tag))
        if ((lemma.split(':')[0] == 'on' and tag in {'ppron3:sg:gen.acc:m1.m2.m3:ter:nakc:praep', 'ppron3:sg:gen:m1.m2.m3:ter:nakc:praep', 'ppron3:sg:acc:m1.m2.m3:ter:nakc:praep'})
            or (lemma == 'ż' and tag in {'part:wok', 'part:nwok'})):
            dependent.append(row)
# Próba kontrolna: porównanie domknięcia czasu przeszłego/warunkowego
# z pełnymi rekordami, BEZ importowania wyników do słownika gry.
expected = set()
for form, lemma, tag, _, _ in base:
    p = tag.split(':')
    _, number, gender, aspect, *tail = p
    if tail != ['agl']:
        expected.add((form, lemma, f'praet:{number}:{gender}:ter:{aspect}'))
        expected.add((form+'by', lemma, f'cond:{number}:{gender}:ter:{aspect}'))
    for agform, _, agtag, _, _ in aglt:
        ap = agtag.split(':')
        if ap[1] != number:
            continue
        person = ap[2]
        if tail != ['agl'] and ap[-1] == 'nwok':
            expected.add((form+'by'+agform, lemma, f'cond:{number}:{gender}:{person}:{aspect}'))
        if tail == ['nagl']:
            continue
        wok_needed = number == 'sg' and (gender == 'm1.m2.m3' or tail == ['agl'])
        if ap[-1] == ('wok' if wok_needed else 'nwok'):
            expected.add((form+agform, lemma, f'praet:{number}:{gender}:{person}:{aspect}'))
missing = sorted(expected-direct)
unexplained = sorted(direct-expected)
result = {
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'unit': 'wiersz źródłowy dla counts; unikalna trójka forma/lemat/tag dla closure_probe',
    'counts': dict(sorted(counts.items())),
    'examples': examples,
    'dependent_lexeme_rows': dependent,
    'closure_probe': {
        'scope': 'praet/cond: porównanie osobowych rekordów z kombinacjami prostych form praet + aglt/by według zgodności liczby i wokaliczności; kwalifikatory nie są agregowane',
        'expected_unique': len(expected), 'direct_unique': len(direct),
        'expected_missing_in_direct': len(missing),
        'direct_not_explained_by_probe': len(unexplained),
        'missing_first_30': missing[:30], 'unexplained_first_30': unexplained[:30],
        'production_completeness_claim': False,
    },
}
(ROOT/'sgjp-rules-probe.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'counts':result['counts'],'closure_probe':result['closure_probe']}, ensure_ascii=False,indent=2))
