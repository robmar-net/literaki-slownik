#!/usr/bin/env python3
"""Pomiar narzutu `PRAGMA fullfsync` (R8, ADR-020) i wybór trybu 4B/4C.

Tylko stdlib, bez importu buildu słownika. Pisze wyłącznie tymczasową bazę w nowym katalogu `--dir`
i kasuje go na końcu. Wynik (JSON na stdout) nie zawiera ścieżek.
"""
import argparse
import datetime
import json
import math
import os
import shutil
import sqlite3
import statistics
import sys
import time
from pathlib import Path

BUILD_SECONDS = 46800       # czas pełnego buildu (13 h), podstawa reguły ze spec
THRESHOLD_PCT = 5           # ≤ 5% → `build` (4B), inaczej `stage_boundaries` (4C)
BATCH = 10000               # partia buildu: commit co 10 000 rekordów
STAGE_COMMITS = 7           # commity granic etapów: tyle, ile etapów w `run.STAGES`
DECISION_KEYS = ('analyses', 'construction_analyses')


def choose(overhead_pct):
    return 'build' if overhead_pct <= THRESHOLD_PCT else 'stage_boundaries'


def build_commits(run_dir):
    """Commity buildu przebiegu: każde źródło i rodzaj analiz to osobne partie, w górę, plus etapy."""
    reports = Path(run_dir) / 'reports'
    counts = json.loads((reports / 'import-counts.json').read_text(encoding='utf-8'))
    decisions = json.loads((reports / 'decisions.json').read_text(encoding='utf-8'))
    imports = [int(value['records']) for _, value in sorted(counts.items())]
    analyses = [int(decisions[key]) for key in DECISION_KEYS]
    batches = sum(math.ceil(n / BATCH) for n in imports + analyses)
    return {'name': Path(run_dir).resolve().name, 'import_records': sum(imports),
            'decision_records': sum(analyses), 'batch_commits': batches,
            'stage_commits': STAGE_COMMITS, 'build_commits': batches + STAGE_COMMITS}


def pragmas(db):
    return {'fullfsync': db.execute('PRAGMA fullfsync').fetchone()[0],
            'journal_mode': db.execute('PRAGMA journal_mode').fetchone()[0],
            'synchronous': db.execute('PRAGMA synchronous').fetchone()[0]}


def trial(db, fullfsync, commits, batch_rows, start):
    db.execute('PRAGMA fullfsync=' + ('ON' if fullfsync else 'OFF'))
    seen, times = pragmas(db), []
    payload = 'x' * 96
    for c in range(commits):
        base = start + c * batch_rows
        db.executemany('insert into t(id, v) values (?, ?)', ((base + i, payload) for i in range(batch_rows)))
        t0 = time.perf_counter()
        db.commit()
        times.append(time.perf_counter() - t0)
    return seen, times


def measure(directory, commits, repeats, batch_rows):
    db = sqlite3.connect(directory / 'measure.sqlite', isolation_level='DEFERRED')
    try:
        if db.execute('PRAGMA journal_mode=DELETE').fetchone()[0] != 'delete':
            raise RuntimeError('journal_mode=DELETE nie zadziałał')
        db.execute('PRAGMA synchronous=FULL')
        db.execute('create table t(id integer primary key, v text not null)')
        db.commit()
        result, start = {}, 0
        for _ in range(repeats):
            for name, on in (('fullfsync_off', False), ('fullfsync_on', True)):
                seen, times = trial(db, on, commits, batch_rows, start)
                start += commits * batch_rows
                slot = result.setdefault(name, {'pragmas': seen, 'times': []})
                if slot['pragmas'] != seen:
                    raise RuntimeError('PRAGMA zmieniły się między próbami')
                slot['times'].extend(times)
    finally:
        db.close()
    return {name: {'median_commit_seconds': statistics.median(slot['times']),
                   'commits': len(slot['times']), 'pragmas': slot['pragmas']}
            for name, slot in result.items()}


def quick_check(path):
    """`PRAGMA quick_check` tylko do odczytu: URI `mode=ro&immutable=1`, plik nietknięty."""
    uri = Path(path).resolve().as_uri() + '?mode=ro&immutable=1'
    t0 = time.perf_counter()
    db = sqlite3.connect(uri, uri=True)
    try:
        rows = [row[0] for row in db.execute('PRAGMA quick_check')]
    finally:
        db.close()
    return {'result': 'ok' if rows == ['ok'] else 'błąd', 'messages': rows[:10] if rows != ['ok'] else [],
            'seconds': time.perf_counter() - t0}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Pomiar narzutu fullfsync (ADR-020).')
    parser.add_argument('--dir', required=True, help='nowy katalog na tymczasową bazę; kasowany na końcu')
    parser.add_argument('--reference-run', help='przebieg referencyjny (reports/import-counts.json, decisions.json)')
    parser.add_argument('--quick-check', help='baza do PRAGMA quick_check, tylko do odczytu')
    parser.add_argument('--commits', type=int, default=200, help='commity na próbę')
    parser.add_argument('--repeats', type=int, default=5, help='powtórzenia par OFF/ON')
    parser.add_argument('--batch-rows', type=int, default=BATCH, help='wiersze na commit')
    args = parser.parse_args(argv)
    if min(args.commits, args.repeats, args.batch_rows) < 1:
        print('--commits, --repeats i --batch-rows muszą być ≥ 1', file=sys.stderr)
        return 2
    directory = Path(args.dir)
    try:
        directory.mkdir(parents=False)
    except FileExistsError:
        print('katalog pomiaru już istnieje; nic nie zmieniono', file=sys.stderr)
        return 2
    except OSError as error:
        print(f'nie da się utworzyć katalogu pomiaru: {error.strerror}', file=sys.stderr)
        return 2
    try:
        result = {'schema_version': 1, 'measured_on': datetime.date.today().isoformat(),
                  'platform': sys.platform, 'sqlite_version': sqlite3.sqlite_version,
                  'settings': {'batch_rows': args.batch_rows, 'commits_per_trial': args.commits,
                               'repeats': args.repeats},
                  **measure(directory, args.commits, args.repeats, args.batch_rows)}
    finally:
        shutil.rmtree(directory)
    if args.reference_run:
        reference = build_commits(args.reference_run)
        delta = result['fullfsync_on']['median_commit_seconds'] - result['fullfsync_off']['median_commit_seconds']
        overhead = delta * reference['build_commits'] / BUILD_SECONDS * 100
        result.update({'reference_run': reference, 'build_commits': reference['build_commits'],
                       'build_seconds_basis': BUILD_SECONDS, 'commit_delta_seconds': delta,
                       'overhead_pct': overhead, 'threshold_pct': THRESHOLD_PCT, 'choice': choose(overhead)})
    if args.quick_check:
        result['quick_check'] = quick_check(args.quick_check)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
