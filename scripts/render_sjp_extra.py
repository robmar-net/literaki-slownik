"""Strona wiki z wyniku sjp_extra_top.py: najczęstsze nasze słowa, których nie ma w SJP.pl.

Użycie:
  python3 scripts/render_sjp_extra.py IN_JSON > Slowa-spoza-SJP.pl.md
"""
import hashlib
import json
import sys
from collections import Counter

from render_sjp_missing import VARIANTS, lemmas, num

# Krótki opis źródła; nieznana reguła konstrukcji zostaje jako identyfikator.
SOURCES = {
    'sgjp': 'SGJP',
    'nie-prefix-degree-v1': 'nie- + słowo z SGJP',
    'impt-single-particle-v1': 'rozkaźnik z -że/-ż',
    'impt-double-particle-v1': 'rozkaźnik z dwiema partykułami',
    'mobile-host-by-sequence-v1': 'pisownia z „by” (2026)',
    'mobile-by-host-aglt-v1': 'pisownia z „by” (2026)',
    'mobile-source-host-aglt-v1': 'konstrukcja z końcówką osobową',
    'personal-host-aglt-v1': 'konstrukcja z końcówką osobową',
    'by-aglt-nwok-v1': 'konstrukcja z końcówką osobową',
    'preposition-n-source-v1': 'przyimek z -ń',
}

# Projekt nie wymienia nazw innych gier słownych (wiki też), więc takie słowo
# z listy jest ukryte; skrót sha256 zamiast zapisu, żeby nie było go w repo.
HIDDEN = {'376805920e557651'}


def shown(word):
    return '*(nazwa innej gry, ukryta)*' if hashlib.sha256(word.encode()).hexdigest()[:16] in HIDDEN else word


def source(row):
    labels = []
    for s in row['sources']:
        label = SOURCES.get(s, f'`{s}`')
        if label not in labels:
            labels.append(label)
    return ', '.join(labels) or '—'


def table_row(i, row, variant):
    cells = [str(i), shown(row['word']), num(row['kwjp']), shown(lemmas(row)), source(row)]
    if variant == 'broad':
        cells.append('tak' if row['in_standard'] else '')
    return '| ' + ' | '.join(cells) + ' |'


def main(path):
    d = json.load(open(path, encoding='utf-8'))
    n = d['n']
    out = ['# Słowa spoza SJP.pl', '',
           f'Słowa z naszych list, których nie ma na liście SJP.pl, od najczęstszych w tekstach (korpus KWJP). '
           f'Po {n} na listę. SJP.pl jest tu tylko miarą: nie usuwamy tych słów dlatego, że SJP.pl ich nie ma. '
           'Odwrotny kierunek: [Brakujące słowa SJP.pl](Brakujace-slowa-SJP.pl).', '',
           '| | STANDARD | BROAD |', '|---|---:|---:|',
           '| nasze słowa, których brak w SJP.pl | ' + ' | '.join(num(d[v]['extra_words']) for v, _ in VARIANTS) + ' |',
           '| w tym występujące w KWJP | ' + ' | '.join(num(d[v]['with_kwjp']) for v, _ in VARIANTS) + ' |', '',
           '**Kolumny:** „wyst.” — liczba wystąpień formy w KWJP (73 mln słów); „lemat” — hasło SGJP; '
           '„źródło” — skąd słowo jest na liście: wprost z SGJP albo z naszej konstrukcji. '
           'Wystąpienia liczymy po zamianie na małe litery, więc `paweł` liczy też imię „Paweł”. '
           'Słowa bez wystąpień są na końcu, alfabetycznie.', '']
    for v, name in VARIANTS:
        x = d[v]
        counts = Counter(source(r) for r in x['top'])
        out += [f'## Brak w SJP.pl, jest w {name}', '',
                f'Źródła wśród {len(x["top"])} słów: ' + '; '.join(f'{k} {c}' for k, c in counts.most_common()) + '.', '']
        out += ['| # | słowo | wyst. | lemat | źródło |' + (' w STANDARD |' if v == 'broad' else ''),
                '|---:|---|---:|---|---|' + ('---|' if v == 'broad' else '')]
        out += [table_row(i, r, v) for i, r in enumerate(x['top'], 1)]
        out.append('')
    i = d['inputs']
    out += [f"Dane: przebieg `{i['run'].split('/')[-1]}` (LL-PL v29), lista SJP.pl `20260820` (sha256 `{i['sjp_sha256'][:8]}…`). "
            'Skrypt: [`scripts/sjp_extra_top.py`](https://github.com/robmar-net/literaki-slownik/blob/main/scripts/sjp_extra_top.py).', '',
            'Atrybucja: lista słów „Słownik języka polskiego”, © sjp.pl, CC BY 4.0. Frekwencje: KWJP, CC BY 4.0.', '']
    sys.stdout.write('\n'.join(out))


if __name__ == '__main__':
    main(sys.argv[1])
