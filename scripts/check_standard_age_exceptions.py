#!/usr/bin/env python3
"""Kontrola przypiętych wyjątków dawności STANDARD (#4).

Użycie:
  python3 scripts/check_standard_age_exceptions.py [--manifest config/generator/sources.json]
      [--database <przebieg>/build.sqlite [--records-only] [--allow-missing-recomputed]]

Sprawdza hash pliku w `configurations` manifestu, schemat, kolejność, rodziny, tagi,
hashe źródeł i liczby. Z `--database` (tylko `mode=ro`) dodatkowo: każdy rekord importu
lub kandydat konstrukcji istnieje dokładnie, a bez `--records-only` także zapisana analiza.
`--allow-missing-recomputed` tylko dla starej migawki (np. v30): kandydaci reguł z
`source_snapshot.recomputed_constructions` (np. 58 × `nie-prefix-degree-v2`) mogą nie istnieć,
jeśli baza nie ma żadnego kandydata tej reguły; wynik podaje ich liczbę w `expected_missing_recomputed`.
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
from literaki_slownik.standard_age_exceptions import check_database, from_manifest  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--manifest', default=str(ROOT / 'config/generator/sources.json'))
    parser.add_argument('--database')
    parser.add_argument('--records-only', action='store_true')
    parser.add_argument('--allow-missing-recomputed', action='store_true')
    args = parser.parse_args(argv)
    if (args.records_only or args.allow_missing_recomputed) and not args.database:
        parser.error('--records-only i --allow-missing-recomputed wymagają --database')
    try:
        loaded = from_manifest(args.manifest)
        result = {'status': 'passed', 'decision_version': loaded['decision_version'], 'counts': loaded['counts']}
        if args.database:
            path = Path(args.database)
            if not path.is_file():
                raise GeneratorError('Brak bazy przebiegu', 3, str(path))
            with connect(path, readonly=True) as db:
                result['database'] = check_database(db, loaded, analyses=not args.records_only,
                                                    allow_missing_recomputed=args.allow_missing_recomputed)
    except GeneratorError as error:
        print(json.dumps(error.diagnostic(), ensure_ascii=False), file=sys.stderr)
        return error.code
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
