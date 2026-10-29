"""Testy zestawienia fali (#12, W14, grupa 16.1) na małych pakietach syntetycznych.

Uruchomienie: python3 -m unittest discover -s <T>/analysis -p 'test_zestawienie_fali.py'
"""
import gzip
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import zestawienie_fali as zf  # noqa: E402

KOLUMNY = 'klucz\tlemat\tczesci_mowy\twarstwa\tzrodla\tznaczenie\twieloznaczny\tformy\n'


def pakiet(base, temat, lematy, *, t3=False, wpisy=7, formy=55):
    """Pakiet z samymi plikami, które czyta zestawienie; liczby celowo różne od TSV,
    żeby test złapał liczenie „z pamięci” albo z TSV zamiast z raportów."""
    root = Path(base)/f'tematy-{temat}-v1-x-a'
    (root/'reports').mkdir(parents=True)
    wiersze = ''.join(f'{lem}@s\t{lem}\tsubst\tT2\tT2\tT2: 1 {lem} 1\tnie\t1\n' for lem in sorted(lematy))
    with gzip.open(root/f'{temat.upper()}.tsv.gz', 'wt', encoding='utf-8') as f:
        f.write(KOLUMNY + wiersze)
    warstwy = {'D': 1, 'T1': 2, 'T2': 4, 'T3': 0}
    liczby = {'formy': formy, 'kandydaci': 9, 'warstwy': warstwy, 'wpisy': wpisy}
    przec = {'leksemy': {'razem': {'pop': {'liczba': 3, 'procent': '42.9'}, 'pop00': {'liczba': 1, 'procent': '14.3'},
                                   'temat': wpisy}},
             'formy': {'razem': {'pop': {'liczba': 20, 'procent': '36.4'}, 'pop00': {'liczba': 5, 'procent': '9.1'},
                                 'temat': formy}}}
    diag = {'razem': {'leksemy': {'kandydaci': 9, 'broad': 8, 'standard': wpisy},
                      'formy': {'kandydaci': 70, 'broad': 60, 'standard': formy}}}
    summary = {'liczby': liczby, 'przeciecia': przec, 'diagnostyka': diag, 't3': {'status': 'ok'} if t3 else None,
               'slowa_oczywiste': {'lista': 10, 'razem': {'pokryte': 6, 'procent': '60.0', 'brakujace': ['b', 'a']}}}
    (root/'reports/summary.json').write_text(json.dumps(summary), encoding='utf-8')
    manifest = {'counts': {temat: liczby}, 'overlap': przec, 'topic': {'id': temat, 'wersja': temat + '-v1'}}
    (root/'release-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    return root


def warstwa(n, tak, nie):
    return {'N': n, 'tak': tak, 'nie': nie, 'niepewne': n - tak - nie,
            'tak_udzial': f'{tak}/{n}' if n else None, 'nie_udzial': f'{nie}/{n}' if n else None}


def kontrola(base, temat, *, t3=False):
    agent = {'T1': warstwa(10, 10, 0), 'T2': warstwa(12, 9, 1), 'T3': warstwa(4, 3, 0) if t3 else warstwa(0, 0, 0)}
    progi = [{'prog': p, 'status': 'czeka'} for p in ('t2_tak', 't2_nie', 'zgodnosc')]
    check = {'status': 'pass', 'temat': temat, 'przeglad': {
        'agent': agent, 'operator': None, 'zgodnosc': None,
        'slowa_oczywiste': {'udzial': '3/5'},
        'werdykt': {'wynik': 'popraw', 'niespelnione': ['slowa_oczywiste'], 'czeka_na_ocene': ['t2_tak', 't2_nie',
                    'zgodnosc'], 'nie_dotyczy': [] if t3 else ['t3_tak'], 'progi': progi}}}
    path = Path(base)/f'review-check-{temat}.json'
    path.write_text(json.dumps(check), encoding='utf-8')
    return path


class TestZestawienie(unittest.TestCase):
    def test_macierz_naklada_lematy_pary_deterministycznie(self):
        lematy = {'aa': {f'w{i:02d}' for i in range(15)} | {'tylko_a'},
                  'bb': {f'w{i:02d}' for i in range(15)} | {'tylko_b'},
                  'cc': {'w03', 'zeta', 'alfa'}}
        pary = zf.macierz(lematy, ['aa', 'bb', 'cc'])
        self.assertEqual([(p['a'], p['b']) for p in pary], [('aa', 'bb'), ('aa', 'cc'), ('bb', 'cc')])
        ab = pary[0]
        self.assertEqual(ab['wspolne'], 15)
        self.assertEqual(ab['przyklady'], [f'w{i:02d}' for i in range(10)])
        self.assertEqual(pary[1], {'a': 'aa', 'b': 'cc', 'wspolne': 1, 'przyklady': ['w03']})
        # ta sama macierz z inną kolejnością wstawiania zbiorów
        self.assertEqual(zf.macierz(dict(reversed(list(lematy.items()))), ['aa', 'bb', 'cc']), pary)

    def test_wiersz_bierze_liczby_z_plikow(self):
        with tempfile.TemporaryDirectory() as d:
            root = pakiet(d, 'zupa', {'x', 'y'}, wpisy=7, formy=55)
            w = zf.wiersz(root, kontrola(d, 'zupa'))
        self.assertEqual((w['wpisy'], w['formy']), (7, 55))  # z summary.json, nie z 2 wierszy TSV
        self.assertEqual(w['warstwy'], {'D': 1, 'T1': 2, 'T2': 4, 'T3': zf.NIE_DOTYCZY})
        self.assertEqual(w['przeciecia']['leksemy'], {'pop': 3, 'pop_procent': '42.9', 'pop00': 1,
                                                      'pop00_procent': '14.3'})
        self.assertEqual(w['diagnostyka']['leksemy'], {'kandydaci': 9, 'broad': 8, 'standard': 7})
        self.assertEqual(w['slowa_oczywiste'], {'lista': 10, 'pokryte': 6, 'procent': '60.0',
                                                'brakujace': ['a', 'b']})
        self.assertEqual(w['agent']['T2'], {'N': 12, 'tak': 9, 'nie': 1, 'niepewne': 2, 'tak_udzial': '9/12',
                                            'nie_udzial': '1/12'})
        self.assertEqual(w['werdykt_checkera']['wynik'], 'popraw')  # werdykt checkera bez zmian
        with tempfile.TemporaryDirectory() as d:
            root = pakiet(d, 'zupa', {'x'})
            m = json.loads((root/'release-manifest.json').read_text())
            m['counts']['zupa']['wpisy'] = 8
            (root/'release-manifest.json').write_text(json.dumps(m))
            with self.assertRaises(ValueError):
                zf.wiersz(root, kontrola(d, 'zupa'))

    def test_temat_bez_t3_ma_nie_dotyczy(self):
        with tempfile.TemporaryDirectory() as d:
            bez = zf.wiersz(pakiet(d + '/1', 'zupa', {'x'}), kontrola(d, 'zupa'))
            z = zf.wiersz(pakiet(d + '/2', 'lek', {'x'}, t3=True), kontrola(d, 'lek', t3=True))
        self.assertEqual(bez['warstwy']['T3'], zf.NIE_DOTYCZY)
        self.assertEqual(bez['agent']['T3'], zf.NIE_DOTYCZY)
        self.assertEqual(bez['operator']['T3'], zf.NIE_DOTYCZY)
        self.assertNotEqual(bez['warstwy']['T3'], 0)
        self.assertEqual(z['warstwy']['T3'], 0)
        self.assertEqual(z['agent']['T3']['tak_udzial'], '3/4')
        # bramka (zmieniona metoda): T3 bez t3 nie dotyczy, zgodność nie dotyczy, T2 z ocen agenta
        self.assertIn('t3_tak', bez['bramka']['nie_dotyczy'])
        self.assertIn('zgodnosc', bez['bramka']['nie_dotyczy'])
        self.assertEqual(bez['bramka']['czeka_na_ocene'], [])
        self.assertNotIn('t3_tak', z['bramka']['nie_dotyczy'])


if __name__ == '__main__':
    unittest.main()
