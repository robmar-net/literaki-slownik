#!/usr/bin/env python3
"""Niezależna kontrola pakietu POP i przeglądu (D-3, D-5).

Użycie:
  python3 scripts/check_pop_package.py --pop-dir <pakiet> --standard <v29>/lists/standard.txt
      [--review <pop-v1-review.json>]

Tylko biblioteka standardowa: skrypt nie importuje `literaki_slownik` ani `pop.py`, więc błąd
w kodzie budowy nie ukryje się w kontroli. Sprawdza:
- `SHA256SUMS` i `files` manifestu: zbiór plików dokładnie jak w `SHA256SUMS`, hashe i rozmiary;
  status `BUILT`; pliki 0444; gzip list bez nazwy i z `mtime=0`;
- POP0 ⊆ POP ⊆ STANDARD na plikach; `--standard` musi mieć hash `inputs.standard_sha256`;
  słowa z `must_include_pop0` manifestu w POP0;
- brak surowego NKJP: klucze JSON z `nkjp` tylko z listy dozwolonej, żadnych plików `nkjp`/`1gram`;
  wiersze `reports/units.json` bez `value` (miara log-ipm łączy F NKJP; tylko ranga i percentyl);
- z `--review`: status `REVIEWED`, hashe próbki, indeksu jednostek, dowodów i `SHA256SUMS`
  (`sha256sums_sha256`), każda pozycja szablonu oceniona, bez pozycji zmieniającej listy.
Kody: 0 zgodne, 2 argumenty, 3 `--standard` ≠ pin manifestu, 4 naruszenia (lista na stderr).
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import stat
import sys

REQUIRED = ('ATTRIBUTIONS.md', 'LIMITATIONS.md', 'POP.txt.gz', 'POP0.txt.gz', 'TERMS.md',
            'release-manifest.json', 'reports/review-template.json', 'reports/sample.json',
            'reports/thresholds.json', 'reports/units.json')
LISTS = {'pop': 'POP.txt.gz', 'pop0': 'POP0.txt.gz'}
# Hashe manifestu obejmują wszystko poza nim samym i SHA256SUMS (`hash_scope`).
UNHASHED = ('release-manifest.json', 'SHA256SUMS')
NKJP_REPORT_KEYS = {'nkjp_rank', 'nkjp_percentile', 'nkjp_status'}
NKJP_MANIFEST_KEYS = {'nkjp_sha256', 'nkjp_rule_id'}
RAW_NKJP_NAMES = ('nkjp', '1gram')
ASSESSMENTS = ('correct', 'incorrect', 'unknown')
READ_ONLY = 0o444


class Usage(Exception):
    """Zły argument: kod 2."""


class Pin(Exception):
    """`--standard` nie jest plikiem przypiętym w manifeście: kod 3."""


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def json_keys(value):
    """Wszystkie klucze słowników w drzewie JSON."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from json_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from json_keys(item)


def read_list(path, failures):
    """Słowa listy gz; nagłówek bez nazwy i czasu, wiersze posortowane, bez spacji i cyfr liczników."""
    head = Path(path).read_bytes()[:10]
    if len(head) < 10 or head[:2] != b'\x1f\x8b' or head[3] & 0x08 or head[4:8] != b'\0\0\0\0':
        failures.append(f'{Path(path).name}: gzip musi mieć pustą nazwę i mtime=0')
    with gzip.open(path, 'rt', encoding='utf-8', newline='') as stream:
        text = stream.read()
    words = text.split('\n')
    if words[-1] != '':
        failures.append(f'{Path(path).name}: brak końcowego \\n')
    words = words[:-1]
    if any(not w or w != w.strip() or ' ' in w or '\t' in w for w in words):
        failures.append(f'{Path(path).name}: pusty wiersz albo biały znak w słowie')
    if any(a >= b for a, b in zip(words, words[1:])):
        failures.append(f'{Path(path).name}: słowa nieposortowane albo powtórzone')
    return set(words)


def check_files(pop_dir, manifest, failures):
    """`SHA256SUMS`, `files` manifestu, tryby 0444."""
    sums = {}
    for number, line in enumerate((pop_dir / 'SHA256SUMS').read_text(encoding='utf-8').splitlines(), 1):
        digest, sep, rel = line.partition('  ')
        if not sep or len(digest) != 64 or rel in sums:
            failures.append(f'SHA256SUMS: zły wiersz {number}')
            continue
        sums[rel] = digest
    if list(sums) != sorted(sums):
        failures.append('SHA256SUMS: wiersze nieposortowane')
    actual = set()
    for path in pop_dir.rglob('*'):
        rel = path.relative_to(pop_dir).as_posix()
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            failures.append(f'Niedozwolony wpis w pakiecie: {rel}')
        elif path.is_file():
            actual.add(rel)
            if stat.S_IMODE(path.stat().st_mode) != READ_ONLY:
                failures.append(f'{rel}: tryb {oct(stat.S_IMODE(path.stat().st_mode))}, oczekiwany 0o444')
        if any(name in path.name.lower() for name in RAW_NKJP_NAMES):
            failures.append(f'Plik o nazwie surowego NKJP w pakiecie: {rel}')
    expected = set(sums) | {'SHA256SUMS'}
    for rel in sorted(expected - actual):
        failures.append(f'Brak pliku z SHA256SUMS: {rel}')
    for rel in sorted(actual - expected):
        failures.append(f'Plik spoza SHA256SUMS: {rel}')
    for rel in REQUIRED:
        if rel not in sums:
            failures.append(f'SHA256SUMS bez wymaganego pliku: {rel}')
    for rel, digest in sorted(sums.items()):
        if rel in actual and sha256(pop_dir / rel) != digest:
            failures.append(f'Hash niezgodny z SHA256SUMS: {rel}')
    files = manifest.get('files')
    if not isinstance(files, dict):
        failures.append('Manifest bez `files`')
        return
    scope = set(sums) - set(UNHASHED)
    if set(files) != scope:
        failures.append(f'`files` manifestu ≠ SHA256SUMS bez {", ".join(UNHASHED)}: '
                        f'{sorted(set(files) ^ scope)}')
    for rel, entry in sorted(files.items()):
        if rel not in actual:
            continue
        if not isinstance(entry, dict) or entry.get('sha256') != sha256(pop_dir / rel) \
                or entry.get('bytes') != (pop_dir / rel).stat().st_size:
            failures.append(f'Hash lub rozmiar niezgodny z manifestem: {rel}')


def check_manifest(manifest, failures):
    for key, value in (('schema_version', 1), ('kind', 'literaki-pop-manifest'), ('status', 'BUILT')):
        if manifest.get(key) != value:
            failures.append(f'Manifest: {key} = {manifest.get(key)!r}, oczekiwane {value!r}')
    words = manifest.get('must_include_pop0')
    if not isinstance(words, list) or not words or not all(isinstance(w, str) and w for w in words):
        failures.append('Manifest: `must_include_pop0` musi być niepustą listą słów')
        return []
    return words


def check_nkjp(pop_dir, manifest, failures):
    """C14: NKJP tylko jako ranga, percentyl i status w raportach; w manifeście hash i reguła."""
    sources = [('release-manifest.json', manifest, NKJP_REPORT_KEYS | NKJP_MANIFEST_KEYS)]
    for path in sorted((pop_dir / 'reports').rglob('*.json')):
        try:
            sources.append((path.relative_to(pop_dir).as_posix(), load_json(path), NKJP_REPORT_KEYS))
        except (OSError, ValueError) as error:
            failures.append(f'{path.relative_to(pop_dir).as_posix()}: nieczytelny JSON ({error})')
    for rel, data, allowed in sources:
        bad = sorted({k for k in json_keys(data) if 'nkjp' in str(k).lower() and k not in allowed})
        if bad:
            failures.append(f'{rel}: niedozwolone klucze NKJP {bad}')
        if rel == 'reports/units.json' and isinstance(data, dict):
            raw = [row for row in data.get('units') or [] if isinstance(row, dict) and 'value' in row]
            if raw:
                failures.append(f'{rel}: {len(raw)} jednostek z kluczem `value` (miara łączy F NKJP; '
                                'tylko ranga i percentyl)')


def check_lists(pop_dir, standard, words, failures):
    lists = {name: read_list(pop_dir / file, failures) for name, file in LISTS.items()}
    standard_words = set(Path(standard).read_text(encoding='utf-8').splitlines())
    for word, outside in (('POP0 ⊄ POP', lists['pop0'] - lists['pop']),
                          ('POP ⊄ STANDARD', lists['pop'] - standard_words)):
        if outside:
            failures.append(f'{word}: {len(outside)} słów, np. {sorted(outside)[:10]}')
    absent = [w for w in words if w not in lists['pop0']]
    if absent:
        failures.append(f'Słowa z must_include_pop0 poza POP0: {absent}')
    return lists


def check_package_review(pop_dir, failures):
    """Szablon w pakiecie musi wskazywać próbkę i indeks jednostek tego pakietu."""
    template = load_json(pop_dir / 'reports/review-template.json')
    if template.get('sample_sha256') != sha256(pop_dir / 'reports/sample.json'):
        failures.append('review-template.json: sample_sha256 ≠ hash reports/sample.json')
    if template.get('canonical_index_sha256') != sha256(pop_dir / 'reports/units.json'):
        failures.append('review-template.json: canonical_index_sha256 ≠ hash reports/units.json')
    evidence = template.get('evidence_sha256')
    if not isinstance(evidence, dict) or not evidence:
        failures.append('review-template.json: brak evidence_sha256')
    else:
        for rel, digest in sorted(evidence.items()):
            path = pop_dir / rel
            if not path.is_file() or sha256(path) != digest:
                failures.append(f'review-template.json: hash dowodu {rel} niezgodny z pakietem')
    return template


def check_review(pop_dir, template, review_path, failures):
    """D-5: przegląd `REVIEWED` związany hashami z tym pakietem, każda pozycja oceniona."""
    try:
        review = load_json(review_path)
    except (OSError, ValueError) as error:
        failures.append(f'Przegląd nieczytelny: {error}')
        return
    if not isinstance(review, dict):
        failures.append('Przegląd: oczekiwany obiekt JSON')
        return
    if review.get('status') != 'REVIEWED':
        failures.append(f'Przegląd: status {review.get("status")!r}, oczekiwany REVIEWED')
    expected = {'schema_version': template.get('schema_version'), 'version': template.get('version'),
                'sample_sha256': sha256(pop_dir / 'reports/sample.json'),
                'canonical_index_sha256': sha256(pop_dir / 'reports/units.json'),
                'evidence_sha256': template.get('evidence_sha256'),
                'sha256sums_sha256': sha256(pop_dir / 'SHA256SUMS')}
    for field, value in expected.items():
        if review.get(field) != value:
            failures.append(f'Przegląd: {field} niezgodne z pakietem')
    wanted = {item['key']: item['strata'] for item in template.get('items', [])}
    items = review.get('items')
    if not isinstance(items, list):
        failures.append('Przegląd: brak listy items')
        return
    found = {}
    for item in items:
        key = item.get('key') if isinstance(item, dict) else None
        if not isinstance(key, str) or key in found:
            failures.append(f'Przegląd: zła albo powtórzona pozycja {key!r}')
            continue
        found[key] = item
    missing, extra = sorted(set(wanted) - set(found)), sorted(set(found) - set(wanted))
    if missing:
        failures.append(f'Przegląd: brak {len(missing)} pozycji próbki, np. {missing[:10]}')
    if extra:
        failures.append(f'Przegląd: pozycje spoza próbki {extra[:10]}')
    for key, item in sorted(found.items()):
        if key not in wanted:
            continue
        if item.get('strata') != wanted[key]:
            failures.append(f'Przegląd: {key} ma inne warstwy niż szablon')
        if item.get('assessment') not in ASSESSMENTS:
            failures.append(f'Przegląd: {key} bez oceny ({", ".join(ASSESSMENTS)})')
        for field in ('reviewer', 'source_justification'):
            if not isinstance(item.get(field), str) or not item[field].strip():
                failures.append(f'Przegląd: {key} bez pola {field}')
        if type(item.get('affects_lists_or_links')) is not bool:
            failures.append(f'Przegląd: {key} bez oceny wpływu na listy (affects_lists_or_links)')
        elif item['affects_lists_or_links']:
            failures.append(f'Przegląd: {key} to błąd zmieniający listy')


def check(pop_dir, standard, review=None):
    """Lista naruszeń; `Pin`, gdy `--standard` nie jest plikiem z manifestu."""
    failures = []
    manifest = load_json(pop_dir / 'release-manifest.json')
    if not isinstance(manifest, dict):
        return ['release-manifest.json: oczekiwany obiekt JSON']
    pinned = (manifest.get('inputs') or {}).get('standard_sha256')
    if not isinstance(pinned, str) or sha256(standard) != pinned:
        raise Pin(f'Hash --standard ≠ inputs.standard_sha256 manifestu ({pinned})')
    words = check_manifest(manifest, failures)
    check_files(pop_dir, manifest, failures)
    check_nkjp(pop_dir, manifest, failures)
    if all((pop_dir / LISTS[name]).is_file() for name in LISTS):
        lists = check_lists(pop_dir, standard, words, failures)
    else:
        lists = None
    template = None
    if all((pop_dir / rel).is_file() for rel in ('reports/review-template.json', 'reports/sample.json',
                                                  'reports/units.json')):
        template = check_package_review(pop_dir, failures)
    if lists is not None:
        counts = manifest.get('counts') or {}
        for name, words_in in lists.items():
            if (counts.get(name) or {}).get('forms') != len(words_in):
                failures.append(f'Manifest: counts.{name}.forms ≠ liczba słów {LISTS[name]}')
    if review is not None:
        if template is None:
            failures.append('Przegląd: pakiet bez szablonu, próbki albo indeksu jednostek')
        else:
            check_review(pop_dir, template, review, failures)
    return failures


def parse(argv):
    parser = argparse.ArgumentParser(description='Kontrola pakietu POP (D-3) i przeglądu (D-5).')
    parser.add_argument('--pop-dir', required=True, type=Path)
    parser.add_argument('--standard', required=True, type=Path,
                        help='lists/standard.txt przebiegu, przypięty w manifeście pakietu')
    parser.add_argument('--review', type=Path)
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        raise Usage('Zły argument') from error
    if not args.pop_dir.is_dir() or not (args.pop_dir / 'release-manifest.json').is_file():
        raise Usage(f'Brak pakietu POP: {args.pop_dir}')
    if not args.standard.is_file():
        raise Usage(f'Brak pliku --standard: {args.standard}')
    if args.review is not None and not args.review.is_file():
        raise Usage(f'Brak pliku --review: {args.review}')
    return args


def main(argv=None):
    try:
        args = parse(sys.argv[1:] if argv is None else argv)
    except Usage as error:
        print(f'BŁĄD: {error}', file=sys.stderr)
        return 2
    try:
        failures = check(args.pop_dir, args.standard, args.review)
    except Pin as error:
        print(f'BŁĄD: {error}', file=sys.stderr)
        return 3
    except (OSError, ValueError, KeyError, TypeError, AttributeError, EOFError) as error:
        failures = [f'Pakiet nieczytelny: {type(error).__name__}: {error}']
    if failures:
        for failure in failures:
            print(f'NARUSZENIE: {failure}', file=sys.stderr)
        return 4
    print('OK: pakiet POP zgodny' + (' i przegląd REVIEWED' if args.review else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
