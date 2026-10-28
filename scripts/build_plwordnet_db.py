#!/usr/bin/env python3
"""Pochodna Słowosieci 4.5 dla TEMATY (#11, W2): zip ze zrzutem MySQL → nowy plik SQLite.

Użycie:
  python3 -I scripts/build_plwordnet_db.py --zip cache/plwordnet/wordnet_work_4_5.zip \
      --output cache/plwordnet/plwn45-tematy.sqlite

Zrzut czytamy strumieniowo z zipa, bez rozpakowania na dysk. Kopiujemy tylko tabele i kolumny
z listy `ALLOWED` (bez danych redaktorów: `owner`, `comment`, `error_comment`, `iplog`,
`iplimit`, `tracker_*`), z `synsetrelation` tylko wiersze `valid=1`. Wiersze wstawiamy po
kluczu, więc dwa uruchomienia na tym samym zipie dają ten sam plik (przy tej samej wersji
SQLite). Tabela `meta` wiąże pochodną z zipem. Nazwy relacji 11, 25, 27 są sprawdzane.
Wynik powstaje w pliku tymczasowym obok celu i jest przenoszony bez nadpisania.
Na stdout: JSON z licznościami i hashami. Kody: 1 błąd (cel istnieje, zrzut, relacje).
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import time
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from literaki_slownik.export import rename_noreplace  # noqa: E402

SCRIPT_VERSION = 'plwn-tematy-v1'
# Tabela → (kolumny w kolejności wyjścia, klucz sortowania jako indeksy tych kolumn, DDL).
ALLOWED = {
    'lexicalunit': (('ID', 'lemma', 'pos', 'variant'), (0,),
                    'ID INTEGER PRIMARY KEY, lemma TEXT NOT NULL, pos INTEGER NOT NULL, variant INTEGER NOT NULL'),
    'synset': (('ID', 'isabstract'), (0,), 'ID INTEGER PRIMARY KEY, isabstract INTEGER NOT NULL'),
    'unitandsynset': (('LEX_ID', 'SYN_ID', 'unitindex'), (1, 2),
                      'LEX_ID INTEGER NOT NULL, SYN_ID INTEGER NOT NULL, unitindex INTEGER NOT NULL, '
                      'PRIMARY KEY (SYN_ID, unitindex)'),
    'synsetrelation': (('PARENT_ID', 'CHILD_ID', 'REL_ID'), (0, 1, 2),
                       'PARENT_ID INTEGER NOT NULL, CHILD_ID INTEGER NOT NULL, REL_ID INTEGER NOT NULL, '
                       'PRIMARY KEY (PARENT_ID, CHILD_ID, REL_ID)'),
    'relationtype': (('ID', 'name'), (0,), 'ID INTEGER PRIMARY KEY, name TEXT NOT NULL'),
}
INDEXES = (
    'CREATE INDEX lexicalunit_lemma ON lexicalunit(lemma)',
    'CREATE INDEX unitandsynset_lex ON unitandsynset(LEX_ID)',
    'CREATE INDEX synsetrelation_child ON synsetrelation(CHILD_ID)',
)
EXPECTED_RELATIONS = {11: 'hiperonimia', 25: 'część', 27: 'miejsce'}

CREATE_RE = re.compile(r'CREATE TABLE `([^`]+)`')
INSERT_RE = re.compile(r'INSERT INTO `([^`]+)` VALUES\s*')
COLUMN_RE = re.compile(r'^\s*`([^`]+)`\s', re.M)
TOKEN_RE = re.compile(r"""\s*(?:(?P<open>\()|(?P<close>\))|(?P<comma>,)|(?P<end>;)|'(?P<str>(?:[^'\\]+|\\.|'')*)'"""
                      r"""|(?P<null>NULL)|(?P<num>-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?))""", re.S)
ESCAPE_RE = re.compile(r"\\(.)|''", re.S)
ESCAPES = {'0': '\0', 'b': '\b', 'n': '\n', 'r': '\r', 't': '\t', 'Z': '\x1a', '%': '\\%', '_': '\\_'}
BACKSLASH_PAIR_RE = re.compile(r'\\.', re.S)


class BuildError(Exception):
    pass


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def _quotes_balanced(text):
    if '\\' in text:
        text = BACKSLASH_PAIR_RE.sub('', text)
    return text.count("'") % 2 == 0


def iter_statements(lines):
    """Instrukcje SQL zrzutu; instrukcja może zajmować wiele wierszy, także wewnątrz napisu."""
    parts = []
    for line in lines:
        if not parts and (not line.strip() or line.startswith('--')):
            continue
        parts.append(line)
        if line.rstrip().endswith(';'):
            statement = ''.join(parts) if len(parts) > 1 else line
            if _quotes_balanced(statement):
                parts = []
                yield statement.strip()
    if parts:
        raise BuildError('zrzut kończy się niedomkniętą instrukcją')


def _unescape(text):
    return ESCAPE_RE.sub(lambda m: "'" if m.group(1) is None else ESCAPES.get(m.group(1), m.group(1)), text)


def parse_insert(statement):
    """`INSERT INTO `t` VALUES (...),(...);` → (t, lista krotek); błąd przy czymkolwiek innym."""
    head = INSERT_RE.match(statement)
    if not head:
        raise BuildError(f'nieznana postać INSERT: {statement[:60]!r}')
    rows, row, pos, depth = [], None, head.end(), 0
    expect_value = False
    while pos < len(statement):
        match = TOKEN_RE.match(statement, pos)
        if not match:
            raise BuildError(f'{head.group(1)}: nieczytelny zrzut przy znaku {pos}')
        pos = match.end()
        kind = match.lastgroup
        if kind == 'open' and depth == 0:
            row, depth, expect_value = [], 1, True
        elif kind == 'close' and depth == 1 and not expect_value:
            rows.append(tuple(row))
            depth = 0
        elif kind == 'comma' and depth == 1 and not expect_value:
            expect_value = True
        elif kind == 'comma' and depth == 0 and rows:
            continue
        elif kind == 'end' and depth == 0:
            if statement[pos:].strip():
                raise BuildError(f'{head.group(1)}: tekst po średniku')
            return head.group(1), rows
        elif depth == 1 and expect_value and kind in ('str', 'null', 'num'):
            if kind == 'str':
                row.append(_unescape(match.group('str')))
            elif kind == 'null':
                row.append(None)
            else:
                text = match.group('num')
                row.append(int(text) if re.fullmatch(r'-?\d+', text) else float(text))
            expect_value = False
        else:
            raise BuildError(f'{head.group(1)}: nieoczekiwany element przy znaku {pos}')
    raise BuildError(f'{head.group(1)}: INSERT bez średnika')


def read_dump(zip_path):
    """Czyta zrzut strumieniowo; zwraca wybrane wiersze, liczności źródłowe i pominięte relacje."""
    with zipfile.ZipFile(zip_path) as archive:
        members = [n for n in archive.namelist() if n.lower().endswith('.sql')]
        if len(members) != 1:
            raise BuildError(f'zip: oczekiwany jeden plik .sql, jest {len(members)}')
        member = members[0]
        columns, rows = {}, {table: [] for table in ALLOWED}
        source_rows, skipped_valid = {}, {}
        with archive.open(member) as raw:
            text = io.TextIOWrapper(raw, encoding='utf-8', newline='')
            for statement in iter_statements(text):
                if statement.startswith('CREATE TABLE'):
                    name = CREATE_RE.match(statement).group(1)
                    if name in ALLOWED:
                        body = statement[statement.index('(') + 1:]
                        columns[name] = [c for c in COLUMN_RE.findall(body)]
                    continue
                if not statement.startswith('INSERT INTO'):
                    continue
                name = INSERT_RE.match(statement)
                if not name or name.group(1) not in ALLOWED:
                    continue  # tabela spoza listy: nie parsujemy wartości
                table, values = parse_insert(statement)
                if table not in columns:
                    raise BuildError(f'{table}: INSERT przed CREATE TABLE')
                names = columns[table]
                wanted = ALLOWED[table][0]
                missing = [c for c in wanted if c not in names]
                if missing or (table == 'synsetrelation' and 'valid' not in names):
                    raise BuildError(f'{table}: brak kolumn {missing or ["valid"]}')
                picks = [names.index(c) for c in wanted]
                valid_at = names.index('valid') if table == 'synsetrelation' else None
                bucket = rows[table]
                for value in values:
                    if len(value) != len(names):
                        raise BuildError(f'{table}: wiersz ma {len(value)} pól, oczekiwano {len(names)}')
                    source_rows[table] = source_rows.get(table, 0) + 1
                    if valid_at is not None and value[valid_at] != 1:
                        key = str(value[valid_at])
                        skipped_valid[key] = skipped_valid.get(key, 0) + 1
                        continue
                    bucket.append(tuple(value[i] for i in picks))
    missing_tables = sorted(set(ALLOWED) - set(columns))
    if missing_tables:
        raise BuildError(f'zrzut bez tabel: {missing_tables}')
    return member, rows, source_rows, skipped_valid


def check_relations(relation_rows):
    names = dict(relation_rows)
    for rel_id, expected in sorted(EXPECTED_RELATIONS.items()):
        if names.get(rel_id) != expected:
            raise BuildError(f'relacja {rel_id}: nazwa {names.get(rel_id)!r}, oczekiwano {expected!r}')


def write_db(path, rows, meta):
    db = sqlite3.connect(path, isolation_level=None)
    try:
        db.execute('PRAGMA page_size = 4096')
        db.execute('PRAGMA journal_mode = DELETE')
        db.execute('BEGIN')
        for table, (cols, key, ddl) in ALLOWED.items():
            db.execute(f'CREATE TABLE {table} ({ddl})')
            data = sorted(rows[table], key=lambda r, k=key: tuple(r[i] for i in k))
            marks = ', '.join('?' * len(cols))
            db.executemany(f'INSERT INTO {table} ({", ".join(cols)}) VALUES ({marks})', data)
        db.execute('CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        db.executemany('INSERT INTO meta (key, value) VALUES (?, ?)', sorted(meta.items()))
        for statement in INDEXES:
            db.execute(statement)
        db.execute('COMMIT')
    finally:
        db.close()


def build(zip_path, output_path):
    zip_path, output_path = Path(zip_path), Path(output_path)
    if output_path.exists():
        raise BuildError(f'wynik istnieje, nie nadpisuję: {output_path}')
    started = time.monotonic()
    zip_sha256 = sha256_file(zip_path)
    member, rows, source_rows, skipped_valid = read_dump(zip_path)
    check_relations(rows['relationtype'])
    meta = dict(script_version=SCRIPT_VERSION, zip_member=member, zip_sha256=zip_sha256)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=output_path.parent, prefix='.plwn-', suffix='.sqlite.part')
    os.close(fd)
    os.unlink(tmp_name)  # SQLite tworzy plik sam; nazwa zostaje zarezerwowana w tym katalogu
    try:
        write_db(tmp_name, rows, meta)
        os.chmod(tmp_name, 0o444)
        try:
            rename_noreplace(tmp_name, output_path)
        except FileExistsError:
            raise BuildError(f'wynik powstał w trakcie, nie nadpisuję: {output_path}') from None
    finally:
        for leftover in (tmp_name, tmp_name + '-journal'):
            try:
                os.unlink(leftover)
            except FileNotFoundError:
                pass
    return dict(
        output=str(output_path), output_sha256=sha256_file(output_path), output_bytes=output_path.stat().st_size,
        meta=meta, counts={t: len(r) for t, r in sorted(rows.items())}, source_rows=dict(sorted(source_rows.items())),
        skipped_relations_by_valid=dict(sorted(skipped_valid.items())), sqlite_version=sqlite3.sqlite_version,
        seconds=round(time.monotonic() - started, 1))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--zip', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    try:
        report = build(args.zip, args.output)
    except (BuildError, OSError, UnicodeDecodeError, zipfile.BadZipFile, sqlite3.Error) as error:
        print(f'błąd: {error}', file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
