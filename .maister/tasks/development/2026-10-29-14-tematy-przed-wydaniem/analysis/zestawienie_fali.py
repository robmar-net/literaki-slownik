"""Zestawienie przed wydaniem (#14; kopia skryptu #13).

Czyta 10 pakietów z jednej serii (`data/work/tematy-wydanie-20261029/`) i pliki
`verification/review-check-<id>.json` tego zadania.
Liczby bierzemy z `reports/summary.json`, `release-manifest.json` i `review-check-<id>.json`;
lematy do macierzy nakładania z `<ID>.tsv.gz`. Wynik: `verification/zestawienie-wydanie.json`.

Dwa werdykty na temat:
- `werdykt_checkera`: werdykt checkera bez zmian (bez ocen operatora T2/T3 i zgodność „czeka”);
- `bramka`: werdykt według zmiany metody R2 (operator, 2026-10-29, `scope-clarifications.md`):
  T2 i T3 z ocen agenta, te same progi z `config/generator/tematy.json`; zgodność nie dotyczy.
  Liczy go funkcja `verdict` z checkera, więc granice i kierunki są te same.

Użycie: python3 zestawienie_fali.py
"""
import gzip
import importlib.util
from itertools import combinations
import json
from fractions import Fraction
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
VER = TASK/'verification'
TEMATY = ('grzyby', 'pogoda', 'matematyka', 'muzyka', 'sport', 'kuchnia', 'rosliny', 'zwierzeta', 'medycyna')
WERSJE = {t: json.loads((REPO/f'config/generator/tematy/{t}.json').read_text(encoding='utf-8'))['wersja']
          for t in (*TEMATY, 'morze')}
PAKIETY = {t: REPO/f'data/work/tematy-wydanie-20261029/tematy-{w}-20261029-a' for t, w in WERSJE.items()}
NIE_DOTYCZY = 'nie dotyczy'
BRAK_OCEN = 'brak ocen'
PRZYKLADY = 10

_spec = importlib.util.spec_from_file_location('check_tematy_package', REPO/'scripts/check_tematy_package.py')
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)
PROGI = json.loads((REPO/'config/generator/tematy.json').read_text(encoding='utf-8'))['progi']


def czytaj(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def lematy(root, temat):
    """Zbiór lematów z kolumny `lemat` pliku `<ID>.tsv.gz`."""
    with gzip.open(Path(root)/f'{temat.upper()}.tsv.gz', 'rt', encoding='utf-8') as f:
        lines = f.read().splitlines()
    head = lines[0].split('\t')
    i = head.index('lemat')
    return {line.split('\t')[i] for line in lines[1:]}


def macierz(zbiory, kolejnosc):
    """Pary tematów w podanej kolejności: liczba wspólnych lematów i do 10 przykładów (sortowanie po tekście)."""
    out = []
    for a, b in combinations(kolejnosc, 2):
        wspolne = sorted(zbiory[a] & zbiory[b])
        out.append({'a': a, 'b': b, 'wspolne': len(wspolne), 'przyklady': wspolne[:PRZYKLADY]})
    return out


def _warstwa(dane):
    return {k: dane[k] for k in ('N', 'tak', 'nie', 'niepewne', 'tak_udzial', 'nie_udzial')}


def bramka(przeglad, t3):
    """Werdykt bramki po zmianie metody: T1, T2, T3 z ocen agenta; zgodność nie dotyczy."""
    agent = przeglad['agent']
    miary = {'slowa_oczywiste': Fraction(przeglad['slowa_oczywiste']['udzial'])}
    pole = {'t1_tak': ('T1', 'tak_udzial'), 't2_tak': ('T2', 'tak_udzial'), 't2_nie': ('T2', 'nie_udzial'),
            't3_tak': ('T3', 'tak_udzial')}
    for prog, (name, field) in pole.items():
        if prog == 't3_tak' and not t3:
            miary[prog] = checker.NIE_DOTYCZY
        else:
            value = agent[name][field]
            miary[prog] = None if value is None else Fraction(value)  # pusta warstwa: niespełniony
    miary['zgodnosc'] = checker.NIE_DOTYCZY
    wynik = checker.verdict(PROGI, miary)
    wynik['metoda'] = 'R2 z ocen agenta (operator 2026-10-29); zgodność operator–agent nie dotyczy'
    return wynik


def wiersz(root, check_path, review_path=None):
    """Wiersz tematu z plików pakietu i pliku kontroli; niespójność plików to ValueError."""
    root = Path(root)
    summary, manifest, check = czytaj(root/'reports/summary.json'), czytaj(root/'release-manifest.json'), czytaj(check_path)
    temat = manifest['topic']['id']
    liczby = summary['liczby']
    if manifest['counts'] != {temat: liczby} or manifest['overlap'] != summary['przeciecia']:
        raise ValueError(f'{temat}: release-manifest.json różny od summary.json')
    if check.get('status') != 'pass' or check.get('temat') != temat or 'przeglad' not in check:
        raise ValueError(f'{temat}: zły plik kontroli {check_path}')
    t3 = summary['t3'] is not None
    przeglad = check['przeglad']

    def przec(rodzaj):
        r = summary['przeciecia'][rodzaj]['razem']
        return {'pop': r['pop']['liczba'], 'pop_procent': r['pop']['procent'],
                'pop00': r['pop00']['liczba'], 'pop00_procent': r['pop00']['procent']}

    diag = summary['diagnostyka']['razem']
    so = summary['slowa_oczywiste']
    agent = {w: _warstwa(przeglad['agent'][w]) for w in ('T1', 'T2', 'T3')}
    operator = {w: (_warstwa(przeglad['operator'][w]) if przeglad['operator'] else BRAK_OCEN) for w in ('T2', 'T3')}
    if not t3:
        agent['T3'] = operator['T3'] = NIE_DOTYCZY
    zg = przeglad['zgodnosc']
    werdykt = dict(przeglad['werdykt'])
    werdykt['wynik'] = werdykt['wynik'] or 'czeka'
    out = {
        'temat': temat, 'pakiet': root.name, 'wersja_tematu': manifest['topic']['wersja'], 't3': t3,
        'wpisy': liczby['wpisy'], 'formy': liczby['formy'],
        'warstwy': {**liczby['warstwy'], **({} if t3 else {'T3': NIE_DOTYCZY})},
        'przeciecia': {'leksemy': przec('leksemy'), 'formy': przec('formy')},
        'diagnostyka': {r: {k: diag[r][k] for k in ('kandydaci', 'broad', 'standard')} for r in ('leksemy', 'formy')},
        'slowa_oczywiste': {'lista': so['lista'], 'pokryte': so['razem']['pokryte'], 'procent': so['razem']['procent'],
                            'brakujace': sorted(so['razem']['brakujace'])},
        'agent': agent, 'operator': operator,
        'zgodnosc': NIE_DOTYCZY if zg is None else {k: zg[k] for k in ('N', 'zgodnosc', 'kappa')},
        'werdykt_checkera': {k: werdykt[k] for k in ('wynik', 'niespelnione', 'czeka_na_ocene', 'nie_dotyczy')},
        'bramka': {k: v for k, v in bramka(przeglad, t3).items() if k != 'uwaga'},
        'decyzja_operatora': None,
    }
    if review_path is not None:
        items = czytaj(review_path)['agent']['items']
        out['agent_nie'] = sorted(i['key'].split('@')[0] for i in items if i['ocena'] == 'nie')
    return out


def main():
    kolejnosc = list(TEMATY) + ['morze']
    wiersze = [wiersz(PAKIETY[t], VER/f'review-check-{t}.json', VER/f'tematy-{t}-review.json') for t in kolejnosc]
    zbiory = {t: lematy(PAKIETY[t], t) for t in kolejnosc}
    wynik = {
        'zadanie': '#14, przed wydaniem',
        'metoda_r2': 'Trafność T2 i T3 z ocen agenta (decyzja operatora 2026-10-29, scope-clarifications.md, '
                     '„Zmiana metody R2”); progi z config/generator/tematy.json; zgodność i kappa: nie dotyczy. '
                     'Werdykt checkera podany bez zmian obok.',
        'progi': PROGI,
        'kolejnosc': kolejnosc,
        'tematy': wiersze,
        'nakladanie': macierz(zbiory, kolejnosc),
    }
    out = VER/'zestawienie-wydanie.json'
    out.write_text(json.dumps(wynik, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    for w in wiersze:
        print(w['temat'], 'checker:', w['werdykt_checkera']['wynik'], 'bramka:', w['bramka']['wynik'],
              'niespełnione:', ','.join(w['bramka']['niespelnione']) or '-')
    print('zapisano', out)


if __name__ == '__main__':
    main()
