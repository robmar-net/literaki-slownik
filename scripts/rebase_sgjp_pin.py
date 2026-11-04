#!/usr/bin/env python3
"""Przepięcie konfiguracji na nowy eksport SGJP (#16).

Użycie:
  python3 -I scripts/rebase_sgjp_pin.py --old cache/sgjp/sgjp-20260823.tab.gz \
      --new cache/sgjp/sgjp-20261018.tab.gz --new-id sgjp-20261018 \
      --run-db data/work/<przebieg>/build.sqlite [--write]

Działa tylko wtedy, gdy nowy eksport różni się od starego jednym ciągłym blokiem dopisanych
wierszy (bez usunięć i zmian). Wtedy stary wiersz r przechodzi na r albo r+len(blok).
Przepisuje `source_id`, `source_sha256` i numery wierszy w konfiguracjach generatora, sprawdza
każdy wskazany rekord w nowym eksporcie i przelicza `candidate_key` konstrukcji z payloadu
w bazie przebiegu (tylko odczyt). Bez `--write` tylko raportuje. Kody: 0 zgodne, 2 argumenty,
3 eksporty niezgodne z założeniem, 4 rekord bez pary lub brak kandydata.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from literaki_slownik import sgjp  # noqa: E402
from literaki_slownik.canonical import dumps, load_json, sha256  # noqa: E402
from literaki_slownik.standard_age_exceptions import render  # noqa: E402

CONFIG = ROOT / 'config/generator'
PLAIN = ('policy.json', 'orthography.json', 'semantic-uses.json')
AGE = 'standard-age-exceptions.json'
ROW_KEYS = ('first_source_row', 'first_row')
RECORD_KEYS = ('original', 'lemma_id', 'raw_tag', 'names', 'qualifiers')


def fail(message, code):
    print(json.dumps({'error': message}, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(code)


def insertion(old, new):
    """Zwraca (pierwszy wiersz bloku, długość) albo kończy kodem 3; strumieniowo."""
    a, b = sgjp.rows(old), sgjp.rows(new)
    start, block = None, []
    for (number, left) in a:
        right = next(b, (None, None))[1]
        if start is None and left != right:
            start, block = number, [right]
            while True:
                nxt = next(b, (None, None))[1]
                if nxt is None:
                    fail('eksporty różnią się czymś więcej niż jednym blokiem dopisanych wierszy', 3)
                if nxt == left:
                    break
                block.append(nxt)
        elif start is not None and left != right:
            fail('eksporty różnią się czymś więcej niż jednym blokiem dopisanych wierszy', 3)
    if start is None or next(b, None) is not None:
        fail('eksporty różnią się czymś więcej niż jednym blokiem dopisanych wierszy', 3)
    return start, len(block)


def fetch(path, wanted):
    found = {}
    for number, fields in sgjp.rows(path):
        if number in wanted:
            found[number] = fields
    return found


def walk(value, visit):
    if isinstance(value, dict):
        visit(value)
        for child in value.values():
            walk(child, visit)
    elif isinstance(value, list):
        for child in value:
            walk(child, visit)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--old', required=True)
    parser.add_argument('--new', required=True)
    parser.add_argument('--new-id', required=True)
    parser.add_argument('--run-db', required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)

    manifest = load_json(CONFIG / 'sources.json')
    sgjp_entry = [a for a in manifest['artifacts'] if a['kind'] == 'sgjp_tab']
    if len(sgjp_entry) != 1:
        fail('manifest wymaga jednego SGJP', 2)
    old_id, old_sha = sgjp_entry[0]['source_id'], sgjp_entry[0]['sha256']
    if sha256(args.old) != old_sha:
        fail('stary eksport ma inny SHA256 niż manifest', 2)
    new_sha = sha256(args.new)
    start, extra = insertion(args.old, args.new)

    def shift(row):
        return row if row < start else row + extra

    report = {'old': old_id, 'new': args.new_id, 'new_sha256': new_sha,
              'insertion': {'first_row': start, 'rows': extra}, 'files': {}}
    expected = []

    def rebase(node):
        if node.get('source_id') != old_id:
            return
        node['source_id'] = args.new_id
        if 'source_sha256' in node:
            node['source_sha256'] = new_sha
        for key in ROW_KEYS:
            if key in node:
                node[key] = shift(node[key])
                if all(k in node for k in RECORD_KEYS):
                    expected.append((node[key], {0: node['original'], 1: node['lemma_id'], 2: node['raw_tag'],
                                                 3: node['names'], 4: node['qualifiers']}))
                elif 'original' in node and 'raw_tag' in node:
                    expected.append((node[key], {0: node['original'], 2: node['raw_tag']}))

    outputs = {}
    for name in PLAIN:
        data = load_json(CONFIG / name)
        before = dumps(data)

        def visit(node):
            source = node.get('source') if isinstance(node.get('source'), dict) else None
            old_row = source.get('first_source_row') if source else None
            if source:
                rebase(source)
            rebase(node)
            use_id = node.get('use_id')
            if old_row is not None and isinstance(use_id, str) and f'-{old_row}-v' in use_id:
                node['use_id'] = use_id.replace(f'-{old_row}-v', f"-{node['source']['first_source_row']}-v")
        walk(data, visit)
        outputs[name] = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
        report['files'][name] = 'changed' if dumps(data) != before else 'unchanged'

    age = load_json(CONFIG / AGE)
    if age['sources'] != {old_id: old_sha}:
        fail('plik wyjątków cytuje inne źródła niż manifest', 2)
    age['sources'] = {args.new_id: new_sha}
    db = sqlite3.connect(f'file:{args.run_db}?mode=ro', uri=True)
    missing, rekeyed = [], 0
    for case in age['cases']:
        for entry in case['analyses']:
            if entry['kind'] == 'construction':
                row = db.execute('select payload from derivation_candidate where candidate_key=?',
                                 (entry['candidate_key'],)).fetchone()
                if row is None:
                    missing.append(entry['candidate_key'])
                    walk(entry, rebase)
                    continue
                candidate = json.loads(row[0])
                walk(candidate, rebase)
                entry['candidate_key'] = hashlib.sha256(dumps(candidate).encode('utf-8')).hexdigest()
                rekeyed += 1
            walk(entry, rebase)
    outputs[AGE] = render(age)
    report['files'][AGE] = 'changed'
    rows = fetch(args.new, {row for row, _ in expected})
    mismatched = [(row, want) for row, want in expected
                  if row not in rows or any(rows[row][i] != v for i, v in want.items())]
    report.update(checked_records=len(expected), mismatched=mismatched[:20], mismatched_count=len(mismatched),
                  rekeyed_constructions=rekeyed, constructions_without_payload=len(missing))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if mismatched or missing:
        raise SystemExit(4)
    if args.write:
        for name, text in outputs.items():
            (CONFIG / name).write_text(text, encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
