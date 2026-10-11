"""Strona wiki z wyniku sjp_missing_top.py: najczęstsze słowa SJP.pl, których brak u nas.

Użycie:
  python3 scripts/render_sjp_missing.py IN_JSON > Brakujace-slowa-SJP.pl.md
"""
import json
import sys
from collections import Counter

# Krótki opis reguły odrzucenia dla gracza; nieznana reguła zostaje jako identyfikator.
# None pomija regułę pomocniczą, która nie jest samodzielnym powodem.
LABELS = {
    'game-proper-name-class-v1': 'nazwa własna',
    'game-required-uppercase-v1': 'wielka litera',
    'linguistic-historical-form-v1': 'forma dawna',
    'game-brand-name-v1': 'marka',
    'game-abbreviation-v1': 'skrót',
    'game-abbreviation-noun-v1': 'skrót',
    'game-dependent-segment-v1': 'cząstka niesamodzielna',
    'game-documented-resident-capital-v1': 'mieszkaniec (wielka litera od 2026)',
    'game-resident-screen-capital-2026-v1': 'mieszkaniec (wielka litera od 2026)',
    'game-mandatory-capital-2026-v1': 'mieszkaniec (wielka litera od 2026)',
    'orthography-documented-resident-capital-2026-v1': 'mieszkaniec (wielka litera od 2026)',
    'orthography-2026-resident-capital-v1': 'mieszkaniec (wielka litera od 2026)',
    'game-documented-surname-component-v1': 'część nazwiska',
    'game-mobile-host-composition-v1': 'pisownia z „by” (2026)',
    'orthography-2026-host-by-sequence-v1': 'pisownia z „by” (2026)',
    'game-personal-host-aglt-v1': 'konstrukcja z końcówką osobową',
    'game-zds-named-exclusion-v1': 'wyłączenie z zasad SJP.pl (ZDS)',
    'semantic-remainder-exhausted-v1': None,
}
VARIANTS = (('standard', 'STANDARD'), ('broad', 'BROAD'))


def reason(row):
    rules = row['reject_rules']
    if rules is None:
        return 'brak w SGJP'
    labels = []
    for rule in rules:
        label = LABELS.get(rule, f'`{rule}`')
        if label and label not in labels:
            labels.append(label)
    if 'nazwa własna' in labels and 'wielka litera' in labels:
        labels.remove('wielka litera')
    return ', '.join(labels) or '—'


def lemmas(row):
    """Hasła SGJP bez znaczników odmiany (`Janusz:Sm1` → `Janusz`), najwyżej trzy."""
    out = []
    for lemma in row['sgjp_lemmas']:
        lemma = lemma.split(':', 1)[0].replace('_', ' ').replace('|', '/')
        if lemma not in out:
            out.append(lemma)
    return ', '.join(out[:3])


def num(x):
    return f'{x:,}'.replace(',', ' ')


def main(path):
    d = json.load(open(path, encoding='utf-8'))
    n = d['n']
    out = ['# Brakujące słowa SJP.pl', '',
           f'Słowa z listy SJP.pl, których nie ma w naszych listach, od najczęstszych w tekstach (korpus KWJP). '
           f'Po {n} na listę. SJP.pl jest tu tylko miarą: tych słów nie dopisujemy, '
           'a każdą zmianę reguł uzasadniamy niezależnie ([Porównanie z SJP.pl](Porownanie-z-SJP.pl)).', '',
           '| | STANDARD | BROAD |', '|---|---:|---:|',
           '| słowa SJP.pl, których brak | ' + ' | '.join(num(d[v]['missing_words']) for v, _ in VARIANTS) + ' |',
           '| w tym występujące w KWJP | ' + ' | '.join(num(d[v]['with_kwjp']) for v, _ in VARIANTS) + ' |', '',
           '**Kolumny:** „wyst.” — liczba wystąpień formy w KWJP (73 mln słów); „lemat” — hasło SGJP; '
           '„powód” — reguła, która odrzuciła słowo, albo „brak w SGJP”. '
           'Wystąpienia liczymy po zamianie na małe litery, więc `ewa` liczy też „Ewa”.', '']
    for v, name in VARIANTS:
        x = d[v]
        counts = Counter(reason(r) for r in x['top'])
        out += [f'## Brak w {name}', '',
                f'Powody wśród {len(x["top"])} słów: ' + '; '.join(f'{k} {c}' for k, c in counts.most_common(6))
                + f'; inne {sum(c for _, c in counts.most_common()[6:])}.', '']
        head = '| # | słowo | wyst. | lemat | powód |' + (' w BROAD |' if v == 'standard' else '')
        out += [head, '|---:|---|---:|---|---|' + ('---|' if v == 'standard' else '')]
        for i, r in enumerate(x['top'], 1):
            cells = [str(i), r['word'], num(r['kwjp']), lemmas(r), reason(r)]
            if v == 'standard':
                cells.append('tak' if r['in_broad'] else '')
            out.append('| ' + ' | '.join(cells) + ' |')
        out.append('')
    i = d['inputs']
    out += [f"Dane: przebieg `{i['run'].split('/')[-1]}` (LL-PL v29), lista SJP.pl `20260820` (sha256 `{i['sjp_sha256'][:8]}…`). "
            'Skrypt: [`scripts/sjp_missing_top.py`](https://github.com/robmar-net/literaki-slownik/blob/main/scripts/sjp_missing_top.py).', '',
            'Atrybucja: lista słów „Słownik języka polskiego”, © sjp.pl, CC BY 4.0. Frekwencje: KWJP, CC BY 4.0.', '']
    sys.stdout.write('\n'.join(out))


if __name__ == '__main__':
    main(sys.argv[1])
