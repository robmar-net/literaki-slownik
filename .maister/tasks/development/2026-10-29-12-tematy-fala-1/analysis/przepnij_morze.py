"""Przepięcie ocen morza z #11 na nowy pakiet a (#12 W9, audyt W1 i D4).

Wejście: `tematy-morze-v2-review.json` z #11 i pakiet `data/work/tematy-morze-v2-20261029-a`.
Oceny agenta i `agent_sha256` bez zmian. Od operatora zostają tylko klucze z `sample.operator.strata`
nowego pakietu (T2 i T3); oceny T1 odpadają. Wiązanie: 4 pola z `reports/review-template.json`
i hash `SHA256SUMS`. Wyjście: `verification/tematy-morze-review.json`, potem checker `--review`
zapisuje wynik do `verification/review-check-morze.json`. Wynik inny niż w W9 daje kod 1.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
PKG = REPO/'data/work/tematy-morze-v2-20261029-a'
OLD = REPO/'.maister/tasks/development/2026-10-28-11-tematy-morze/verification/tematy-morze-v2-review.json'
OUT = TASK/'verification/tematy-morze-review.json'
CHECK_OUT = TASK/'verification/review-check-morze.json'
POLA = ('sample_sha256', 'canonical_index_sha256', 'evidence_sha256', 'version')

_spec = importlib.util.spec_from_file_location('tematy_review', REPO/'scripts/tematy_review.py')
tr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tr)
checker = tr.checker

# W9 (D4): wartości progów i zgodność, policzone w audycie z ocen #11.
OCZEKIWANE = {'progi': {'t1_tak': ('23/25', 'spelniony'), 't2_tak': ('1', 'spelniony'),
                        't2_nie': ('0', 'spelniony'), 't3_tak': ('1', 'spelniony')},
              'zgodnosc': '20/57', 'kappa': '0', 'wynik': 'popraw'}


def przepnij(old, root):
    """Nowy przegląd: oceny agenta bez zmian, operator tylko z próby operatora, wiązanie z pakietem."""
    root = Path(root)
    manifest = checker.read(root/'release-manifest.json')
    sample = checker.read(root/'reports/sample.json')
    template = checker.read(root/'reports/review-template.json')
    strata = sample['operator']['strata']
    expected = {k: w for w, keys in strata.items() for k in keys}
    old_op = {i['key']: i for i in old['operator']['items']}
    missing = sorted(set(expected) - set(old_op))
    checker.require(not missing, 'Brak starej oceny operatora: ' + ', '.join(missing[:10]))
    checker.require(all(old_op[k]['warstwa'] == w for k, w in expected.items()), 'Inna warstwa klucza operatora')
    review = dict(old)
    review.update({f: template[f] for f in POLA})
    review['sha256sums_sha256'] = checker.digest(root/'SHA256SUMS')
    review['method'] = manifest['method']
    review['operator'] = {'reviewer': old['operator']['reviewer'], 'reviewed_at': old['operator']['reviewed_at'],
                          'agent_sha256': old['agent_sha256'],
                          'items': [{'key': k, 'warstwa': expected[k], 'ocena': old_op[k]['ocena']}
                                    for k in sorted(expected)]}
    checker.binding(review, root)
    checker.agent_items(review, tr._membership(sample))
    checker.operator_items(review, strata)
    return review


def porownaj(przeglad):
    """Lista rozbieżności z W9 (pusta: zgodnie)."""
    bledy = []
    progi = {r['prog']: (r['wartosc'], r['status']) for r in przeglad['werdykt']['progi']}
    for prog, chcemy in OCZEKIWANE['progi'].items():
        if progi.get(prog) != chcemy:
            bledy.append(f'{prog}: {progi.get(prog)} zamiast {chcemy}')
    zg = przeglad['zgodnosc'] or {}
    if zg.get('zgodnosc') != OCZEKIWANE['zgodnosc'] or progi.get('zgodnosc', (None, ''))[1] != 'niespelniony':
        bledy.append(f"zgodność: {zg.get('zgodnosc')} {progi.get('zgodnosc')} zamiast 20/57 niespełniona")
    if zg.get('kappa') != OCZEKIWANE['kappa']:
        bledy.append(f"kappa: {zg.get('kappa')} zamiast 0")
    if przeglad['werdykt']['wynik'] != OCZEKIWANE['wynik']:
        bledy.append(f"werdykt: {przeglad['werdykt']['wynik']} zamiast popraw")
    return bledy


def main():
    review = przepnij(checker.read(OLD), PKG)
    tr.write_review(OUT, review)
    print('Zapisano', OUT.relative_to(REPO), 'agent_sha256', review['agent_sha256'],
          'operator', len(review['operator']['items']), flush=True)
    r = subprocess.run([sys.executable, str(REPO/'scripts/check_tematy_package.py'), '--package-dir', str(PKG),
                        '--manifest', str(REPO/'config/generator/tematy-sources.json'),
                        '--config', str(REPO/'config/generator/tematy.json'), '--review', str(OUT)],
                       capture_output=True, text=True, cwd=REPO)
    print('checker --review: exit', r.returncode, flush=True)
    if r.returncode != 0:
        print(r.stderr)
        return 1
    CHECK_OUT.write_text(r.stdout, encoding='utf-8')
    bledy = porownaj(json.loads(r.stdout)['przeglad'])
    for b in bledy:
        print('ROZBIEŻNOŚĆ:', b)
    print('Wynik zgodny z W9' if not bledy else 'Wynik różny od W9', flush=True)
    return 1 if bledy else 0


if __name__ == '__main__':
    sys.exit(main())
