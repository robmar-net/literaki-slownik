"""Zapis ocen agenta R2 (#14; kopia z #13) do verification/tematy-<id>-review.json.

Kopia skryptu z #11 z pętlą po tematach. Oceny leżą w analysis/agent-ratings-<id>.json
(format: analysis/instrukcja-oceny-agenta.md). Zapis idzie przez scripts/tematy_review.py
(agent_review + write_review), więc plik przeglądu ma hash ocen i powiązanie z pakietem a.
Potem checker z --review sprawdza wynik. Zły plik ocen: odmowa, nic nie jest zapisane.

Użycie: python3 record_agent_review.py [id ...]   (bez argumentów: matematyka i medycyna v3)
`--ratings` i `--out-dir` są tylko do kontroli 13.1 (plik syntetyczny, wynik poza zadaniem).
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
TEMATY = ('matematyka', 'medycyna')
WERSJA = 'v3-20261029-a'

spec = importlib.util.spec_from_file_location('tematy_review', REPO/'scripts/tematy_review.py')
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)


def pakiet(temat):
    return REPO/f'data/work/tematy-wydanie-20261029/tematy-{temat}-{WERSJA}'


def wczytaj(path):
    """Plik ocen w kształcie z instrukcji; kształt sprawdzamy tu, klucze i oceny sprawdza agent_review."""
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    tr.require(isinstance(data, dict) and set(data) == {'reviewer', 'reviewed_at', 'oceny'},
               'Plik ocen: klucze najwyższego poziomu to reviewer, reviewed_at, oceny')
    tr.require(isinstance(data['reviewer'], str) and data['reviewer'].strip(), 'Plik ocen: pusty reviewer')
    tr.require(isinstance(data['reviewed_at'], str) and data['reviewed_at'].endswith('Z'),
               'Plik ocen: reviewed_at w UTC (…Z)')
    tr.require(isinstance(data['oceny'], dict), 'Plik ocen: oceny to obiekt key → ocena')
    for key, value in data['oceny'].items():
        tr.require(isinstance(value, dict) and set(value) == {'ocena', 'powod'},
                   'Plik ocen: pozycja ma dokładnie pola ocena i powod: ' + key)
    return data


def zapisz(temat, ratings_path, out_dir):
    root = pakiet(temat)
    data = wczytaj(ratings_path)
    review = tr.agent_review(root, data['oceny'], data['reviewer'], data['reviewed_at'])
    out = Path(out_dir)/f'tematy-{temat}-review.json'
    tr.write_review(out, review)
    print(temat, 'zapisano', out, 'agent_sha256', review['agent_sha256'], flush=True)
    r = subprocess.run([sys.executable, str(REPO/'scripts/check_tematy_package.py'), '--package-dir', str(root),
                        '--manifest', str(REPO/'config/generator/tematy-sources.json'),
                        '--config', str(REPO/'config/generator/tematy.json'), '--review', str(out)],
                       capture_output=True, text=True, cwd=REPO)
    print(temat, 'checker --review: exit', r.returncode, flush=True)
    if r.returncode != 0:
        print(r.stderr or r.stdout)
    else:
        # #13: wynik checkera z `--review` zapisujemy obok (wejście zestawienia v2).
        (Path(out_dir)/f'review-check-{temat}.json').write_text(r.stdout, encoding='utf-8')
    return r.returncode, review['agent_sha256']


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('tematy', nargs='*', help='id tematów; domyślnie wszystkie')
    ap.add_argument('--ratings', help='plik ocen (tylko z jednym tematem; domyślnie analysis/agent-ratings-<id>.json)')
    ap.add_argument('--out-dir', default=str(TASK/'verification'), help='folder wyniku (domyślnie verification/)')
    args = ap.parse_args(argv)
    tematy = args.tematy or list(TEMATY)
    obce = [t for t in tematy if t not in TEMATY]
    if obce:
        ap.error('nieznane tematy: ' + ', '.join(obce))
    if args.ratings and len(tematy) != 1:
        ap.error('--ratings tylko z jednym tematem')
    kod, hashe = 0, {}
    for temat in tematy:
        path = args.ratings or TASK/f'analysis/agent-ratings-{temat}.json'
        try:
            rc, sha = zapisz(temat, path, args.out_dir)
        except (tr.Refused, OSError, ValueError, KeyError, TypeError) as e:
            print(temat, 'ODMOWA:', e, file=sys.stderr, flush=True)
            kod = 1
            continue
        hashe[temat] = sha
        kod = kod or rc
    for temat, sha in hashe.items():
        print(f'{temat} agent_sha256 {sha}')
    return kod


if __name__ == '__main__':
    sys.exit(main())
