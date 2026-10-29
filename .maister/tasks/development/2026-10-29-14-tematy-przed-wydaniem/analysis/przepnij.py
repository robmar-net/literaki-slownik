"""Przepięcie przeglądów R2 na pakiety serii przed wydaniem (#14; wzór `przepnij_morze.py` z #12).

Dotyczy 8 tematów bez zmiany składu. Stary przegląd (z #13 albo #12) przechodzi, gdy próba
(`sample_sha256`) i indeks (`canonical_index_sha256`) nowego pakietu są takie same. Oceny agenta
i operatora (morze) bez zmian; nowe są tylko wiązania z pakietem. Potem checker `--review`, wynik
w `verification/review-check-<id>.json`. Inna próba albo odmowa checkera: kod 1.

Użycie: python3 przepnij.py
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
SERIA = REPO/'data/work/tematy-wydanie-20261029'
V13 = REPO/'.maister/tasks/development/2026-10-29-13-tematy-v2/verification'
V12 = REPO/'.maister/tasks/development/2026-10-29-12-tematy-fala-1/verification'
STARE = {**{t: V13 for t in ('grzyby', 'pogoda', 'muzyka', 'sport', 'kuchnia')},
         **{t: V12 for t in ('rosliny', 'zwierzeta', 'morze')}}
POLA = ('sample_sha256', 'canonical_index_sha256', 'evidence_sha256', 'version')

_spec = importlib.util.spec_from_file_location('tematy_review', REPO/'scripts/tematy_review.py')
tr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tr)
checker = tr.checker


def pakiet(temat):
    wersja = json.loads((REPO/f'config/generator/tematy/{temat}.json').read_text(encoding='utf-8'))['wersja']
    return SERIA/f'tematy-{wersja}-20261029-a'


def przepnij(temat):
    root = pakiet(temat)
    old = checker.read(STARE[temat]/f'tematy-{temat}-review.json')
    template = checker.read(root/'reports/review-template.json')
    for pole in ('sample_sha256', 'canonical_index_sha256'):
        checker.require(old[pole] == template[pole], f'{temat}: inna próba albo indeks ({pole})')
    review = dict(old)
    review.update({f: template[f] for f in POLA})
    review['sha256sums_sha256'] = checker.digest(root/'SHA256SUMS')
    review['method'] = checker.read(root/'release-manifest.json')['method']
    checker.binding(review, root)
    out = TASK/f'verification/tematy-{temat}-review.json'
    tr.write_review(out, review)
    r = subprocess.run([sys.executable, str(REPO/'scripts/check_tematy_package.py'), '--package-dir', str(root),
                        '--manifest', str(REPO/'config/generator/tematy-sources.json'),
                        '--config', str(REPO/'config/generator/tematy.json'), '--review', str(out)],
                       capture_output=True, text=True, cwd=REPO)
    print(temat, 'checker --review: exit', r.returncode, flush=True)
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        return 1
    (TASK/f'verification/review-check-{temat}.json').write_text(r.stdout, encoding='utf-8')
    return 0


def main():
    kod = 0
    for temat in STARE:
        try:
            kod = przepnij(temat) or kod
        except (checker.Refused, OSError, KeyError) as e:
            print(temat, 'ODMOWA:', e, file=sys.stderr, flush=True)
            kod = 1
    return kod


if __name__ == '__main__':
    sys.exit(main())
