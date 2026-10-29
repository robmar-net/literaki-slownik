"""Regresja morza (#12 W8): nowy pakiet a wobec `data/work/tematy-v2-20261029-a` (metoda tematy-v1).

Stary pakiet porównujemy tylko hashami i diffem (nowy checker go nie sprawdza).
Poprawka orkiestratora do W8 (2026-10-29): z `summary.json` usuwamy też `werdykt.czeka_na_ocene`,
bo `t1_tak` już nie czeka; oczekiwana nowa wartość: [t2_tak, t2_nie, t3_tak, zgodnosc].
Kod 0: wszystkie punkty zgodne; kod 1: jakakolwiek różnica poza listą „mogą się różnić”.
"""
import argparse
import copy
import difflib
import json
from pathlib import Path
import sys

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
sys.path.insert(0, str(REPO))
from literaki_slownik.canonical import load_json, sha256  # noqa: E402

STARY = 'data/work/tematy-v2-20261029-a'
BAJTOWO = {
    'MORZE.txt.gz': '6e78d1ef',
    'MORZE.tsv.gz': '83037db1',
    'ATTRIBUTIONS.md': 'a3a221e9',
    'TERMS.md': 'b4250289',
}
MOGA_SIE_ROZNIC = {'tematy/morze.json', 'method.json', 'reports/raport.md', 'reports/review-template.json',
                   'release-manifest.json', 'SHA256SUMS'}
SPRAWDZANE_OSOBNO = {'LIMITATIONS.md', 'reports/summary.json', 'reports/sample.json'}
USUWANE_Z_SUMMARY = ['method', 'wykluczenia', 'werdykt.nie_dotyczy', 'werdykt.czeka_na_ocene']
CZEKA_NOWE = ['t2_tak', 't2_nie', 't3_tak', 'zgodnosc']
SAMPLE_ROWNE = ['strata', 'items', 'unique_selected_units', 'overlaps']


def files(root):
    return sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file())


def bez(summary):
    s = copy.deepcopy(summary)
    for path in USUWANE_Z_SUMMARY:
        *head, last = path.split('.')
        node = s
        for k in head:
            node = node.get(k, {})
        node.pop(last, None)
    return s


def roznice(a, b, prefix=''):
    """Lista ścieżek, pod którymi a i b się różnią."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            p = f'{prefix}.{k}' if prefix else k
            if k not in a or k not in b:
                out.append(p)
            else:
                out += roznice(a[k], b[k], p)
        return out
    return [] if a == b else [prefix or '<root>']


def punkt_limitations(line):
    return line.startswith('- T2 ') or line.startswith('- T3 ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--a', required=True, help='nowy pakiet a')
    ap.add_argument('--stary', default=STARY)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    nowy, stary = REPO/args.a, REPO/args.stary
    wynik, bledy = {'nowy': args.a, 'stary': args.stary, 'poprawka_orkiestratora': (
        'summary.json porównany także bez werdykt.czeka_na_ocene (t1_tak już nie czeka); '
        'raport.md może się różnić (W8)')}, []

    # Spójność starego pakietu z jego SHA256SUMS (nowy checker go nie sprawdza).
    stare_sumy = dict(reversed(l.split('  ', 1)) for l in (stary/'SHA256SUMS').read_text().splitlines())
    zgodne = all(sha256(stary/n) == h for n, h in stare_sumy.items())
    wynik['stary_sha256sums_zgodne'] = zgodne
    if not zgodne:
        bledy.append('stary pakiet niezgodny z własnym SHA256SUMS')

    # 1. Bajtowo równe pliki.
    bajt = {}
    for n, pref in BAJTOWO.items():
        hn, hs = sha256(nowy/n), sha256(stary/n)
        ok = hn == hs and hn.startswith(pref)
        bajt[n] = {'nowy': hn, 'stary': hs, 'oczekiwany_prefiks': pref, 'zgodny': ok}
        if not ok:
            bledy.append(f'{n}: inny hash')
    wynik['bajtowo_rowne'] = bajt

    # Zbiór plików i różnice poza listą.
    fn, fs = files(nowy), files(stary)
    if fn != fs:
        bledy.append(f'różne zbiory plików: {sorted(set(fn) ^ set(fs))}')
    rozne = sorted(n for n in set(fn) & set(fs) if sha256(nowy/n) != sha256(stary/n))
    poza = [n for n in rozne if n not in MOGA_SIE_ROZNIC | SPRAWDZANE_OSOBNO]
    wynik['pliki_rozne'] = rozne
    wynik['pliki_rozne_poza_lista'] = poza
    if poza:
        bledy.append(f'różnice poza listą: {poza}')

    # 2. LIMITATIONS.md różni się tylko punktami T2 i T3.
    ln = (nowy/'LIMITATIONS.md').read_text(encoding='utf-8').splitlines()
    ls = (stary/'LIMITATIONS.md').read_text(encoding='utf-8').splitlines()
    diff = list(difflib.unified_diff(ls, ln, 'stary/LIMITATIONS.md', 'nowy/LIMITATIONS.md', lineterm='', n=0))
    zmienione = [l[1:] for l in diff if l[:1] in '+-' and not l.startswith(('+++', '---'))]
    ok = bool(zmienione) and all(punkt_limitations(l) for l in zmienione)
    ok = ok and [l for l in ln if not punkt_limitations(l)] == [l for l in ls if not punkt_limitations(l)]
    wynik['limitations'] = {'diff': diff, 'tylko_T2_T3': ok}
    if not ok:
        bledy.append('LIMITATIONS.md różni się poza punktami T2 i T3')

    # 3. summary.json po usunięciu pól.
    sn, ss = load_json(nowy/'reports/summary.json'), load_json(stary/'reports/summary.json')
    r = roznice(bez(ss), bez(sn))
    czeka = sn.get('werdykt', {}).get('czeka_na_ocene')
    wynik['summary'] = {
        'usuniete': USUWANE_Z_SUMMARY,
        'roznice_po_usunieciu': r,
        'method': {'stary': ss.get('method'), 'nowy': sn.get('method')},
        'wykluczenia_nowy': sn.get('wykluczenia'),
        'nie_dotyczy_nowy': sn.get('werdykt', {}).get('nie_dotyczy'),
        'czeka_na_ocene': {'stary': ss.get('werdykt', {}).get('czeka_na_ocene'), 'nowy': czeka,
                           'oczekiwany': CZEKA_NOWE},
        't3_obecne': sn.get('t3') is not None,
        'srodladowe_obecne': sn.get('srodladowe') is not None,
    }
    if r:
        bledy.append(f'summary.json różni się: {r}')
    if czeka != CZEKA_NOWE:
        bledy.append(f'werdykt.czeka_na_ocene = {czeka}')
    if sn.get('t3') is None or sn.get('srodladowe') is None:
        bledy.append('brak summary.t3 lub srodladowe')

    # 4. sample.json.
    pn, ps = load_json(nowy/'reports/sample.json'), load_json(stary/'reports/sample.json')
    sample = {k: pn.get(k) == ps.get(k) for k in SAMPLE_ROWNE}
    op = sorted(pn.get('operator', {}).get('strata', {}))
    op_ok = op == ['T2', 'T3']
    op_klucze = all(pn['operator']['strata'][s] == ps['operator']['strata'].get(s) for s in op) if op_ok else False
    wynik['sample'] = {'rowne': sample, 'operator_strata': op, 'operator_strata_ok': op_ok,
                       'operator_klucze_T2_T3_jak_w_starym': op_klucze,
                       'inne_roznice': [p for p in roznice(ps, pn) if p.split('.')[0] not in SAMPLE_ROWNE]}
    if not all(sample.values()):
        bledy.append(f'sample.json różni się: {sample}')
    if not op_ok:
        bledy.append(f'operator.strata = {op}')

    # 5. Liczby.
    sl = sn['slowa_oczywiste']
    liczby = {'wpisy': sn['liczby']['wpisy'], 'formy': sn['liczby']['formy'],
              'test': f"{sl['razem']['pokryte']}/{sl['lista']}"}
    wynik['liczby'] = liczby
    if liczby != {'wpisy': 970, 'formy': 11035, 'test': '37/37'}:
        bledy.append(f'liczby: {liczby}')

    wynik['bledy'] = bledy
    wynik['werdykt'] = 'ZGODNE' if not bledy else 'STOP'
    Path(args.output).write_text(json.dumps(wynik, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'werdykt': wynik['werdykt'], 'bledy': bledy}, ensure_ascii=False))
    return 0 if not bledy else 1


if __name__ == '__main__':
    sys.exit(main())
