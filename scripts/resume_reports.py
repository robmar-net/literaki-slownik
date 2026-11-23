#!/usr/bin/env python3
"""Dokończenie etapu `reports` przerwanego przebiegu build (#16); od #22 nakładka na `build --resume`.

Użycie:
  python3 scripts/resume_reports.py --manifest config/generator/sources.json --run-dir data/work/<przebieg>

Najpierw te same kontrole co przed #22: etapy do `links` mają status complete, `reports` running
albo failed, a kod generatora jest ten sam co przy build i bez niezatwierdzonych zmian. Potem
`build --resume`, które sprawdza dysk, wolumen, miejsce, manifest wejść i bazę, a potem liczy
raporty od pierwszego bez znacznika `reports/.done`. Nieczytelny manifest przebiegu przechodzi
od razu do `build --resume` (75, gdy dysk zniknął, inaczej 4).

stdout: JSON z `build --resume`; stderr: błąd. Kody: 2 przebieg nie czeka na wznowienie samych
raportów; 4 inny kod generatora, manifest bez `stages`/`code` albo trzymana blokada buildu
(`.<nazwa>.build.lock`, żywy build); pozostałe przekazane z `build --resume` (0, 3, 4, 5, 75, 76,
77, 78, 130; opis w docs/generator/cli.md).
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from literaki_slownik import workfs  # noqa: E402
from literaki_slownik.canonical import load_json  # noqa: E402
from literaki_slownik.cli import main as cli_main  # noqa: E402
from literaki_slownik.run import code_identity  # noqa: E402

DONE = ('preflight', 'import_sgjp', 'import_kwjp', 'constructions', 'decisions', 'links')


def refuse(message, code):
    print(json.dumps({'error': message}, ensure_ascii=False), file=sys.stderr)
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--run-dir', required=True)
    args = parser.parse_args(argv)
    if workfs.lock_held(workfs.build_lock(args.run_dir)):
        # `reports: running` bywa stanem żywego buildu; nakładka nie rusza przebiegu, którego blokadę ktoś trzyma.
        return refuse('build albo --resume tego przebiegu trwa (blokada .<nazwa>.build.lock)', 4)
    try:
        manifest = load_json(Path(args.run_dir) / 'manifest.json')
    except (OSError, ValueError):
        manifest = None
    if manifest is not None:
        try:
            stages = manifest['stages']
            if any(stages.get(name, {}).get('status') != 'complete' for name in DONE):
                return refuse('etapy do links nie są ukończone', 2)
            if stages.get('reports', {}).get('status') not in {'running', 'failed'}:
                return refuse('etap reports nie czeka na wznowienie', 2)
            tree = manifest['code']['tree_sha256']
        except (KeyError, TypeError, AttributeError):
            return refuse('manifest przebiegu bez pól stages albo code', 4)
        current = code_identity()
        if tree != current['tree_sha256'] or current['git_dirty'] is not False:
            return refuse('kod generatora różni się od kodu build', 4)
    return cli_main(['build', '--resume', '--manifest', args.manifest, '--run-dir', args.run_dir, '--json'])


if __name__ == '__main__':
    raise SystemExit(main())
