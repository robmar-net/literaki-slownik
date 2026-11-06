#!/usr/bin/env python3
"""Kontrola przypiętych wykluczeń STANDARD (#15).

Użycie:
  python3 scripts/check_standard_exclusions.py [--manifest config/generator/sources.json]
      [--database <przebieg>/build.sqlite [--records-only]]

Sprawdza hash pliku w `configurations` manifestu, schemat, kolejność, tagi, hashe źródeł
i liczby. Z `--database` (tylko `mode=ro`) dodatkowo: każdy rekord importu istnieje dokładnie
raz, a bez `--records-only` także zapisana analiza o tym kluczu.
Kody: 0 zgodne, 2 argumenty, inne — kod odmowy generatora (opis JSON na stderr).
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from literaki_slownik.database import connect  # noqa: E402
from literaki_slownik.inputs import GeneratorError  # noqa: E402
from literaki_slownik.standard_exclusions import check_database, from_manifest  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--manifest', default=str(ROOT / 'config/generator/sources.json'))
    parser.add_argument('--database')
    parser.add_argument('--records-only', action='store_true')
    args = parser.parse_args(argv)
    if args.records_only and not args.database:
        parser.error('--records-only wymaga --database')
    try:
        loaded = from_manifest(args.manifest)
        result = {'status': 'passed', 'decision_version': loaded['decision_version'], 'counts': loaded['counts']}
        if args.database:
            path = Path(args.database)
            if not path.is_file():
                raise GeneratorError('Brak bazy przebiegu', 3, str(path))
            with connect(path, readonly=True) as db:
                result['database'] = check_database(db, loaded, analyses=not args.records_only)
    except GeneratorError as error:
        print(json.dumps(error.diagnostic(), ensure_ascii=False), file=sys.stderr)
        return error.code
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
