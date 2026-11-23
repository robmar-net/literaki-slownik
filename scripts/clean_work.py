#!/usr/bin/env python3
"""Sprzątanie przebiegów na T7 i starych wydań (#22, R11).

Użycie:
  python3 scripts/clean_work.py [--work-root W] [--apply] [--server-repo ŚCIEŻKA]
                                [--server-current NAZWA]... [--delete-releases PLIK]

Domyślnie tylko lista (JSON na stdout: wpis, klasa, rozmiar, powód); bez `--apply` nic nie znika.
Klasy według pierwszeństwa (wygrywa pierwsza pasująca):
  T7:   1 VERIFIED/FROZEN, 2 promocja w toku, 3 przebieg w toku (blokada nadzorcy albo buildu,
        wszystkie etapy complete i czeka na verify, zmiany < 24 h), 4 nieznana zawartość,
        5 osierocony albo przerwane kasowanie `.<nazwa>.deleting` (kasuje), 6 nieukończony z symlinkiem (kasuje).
  Dysk wewnętrzny: 7 tylko lista, 8 stare wydanie (tylko z `--delete-releases`).
Wydanie skasuje wyłącznie `--apply --delete-releases PLIK` z nazwami zaakceptowanymi przez
właściciela; nazwa spoza kandydatów → odmowa całości. Serwer: `git -C <repo> show origin/main:NOTICE`,
tylko odczyt, bez fetch. Brak NOTICE → wszystkie wydania potrzebne.
Kasowanie jest wznawialne: drzewo najpierw dostaje nazwę `.<nazwa>.deleting`, a `--apply` dokańcza
takie resztki na T7 i w data/work. Kody: 0, 2 argumenty, 4 odmowa albo błąd kasowania, 75 T7 zniknął
w trakcie kasowania.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from literaki_slownik import volume, workfs  # noqa: E402
from literaki_slownik.run import STAGES  # noqa: E402
from literaki_slownik.canonical import load_json, sha256  # noqa: E402
from literaki_slownik.inputs import GeneratorError  # noqa: E402

AGE = 24 * 3600
CLASSES = {1: 'zweryfikowany', 2: 'promocja w toku', 3: 'przebieg w toku', 4: 'nieznana zawartość',
           5: 'osierocony', 6: 'nieukończony', 7: 'tylko lista', 8: 'kandydat'}
T7_DELETABLE = {5, 6}
SYSTEM = {volume.MARKER, '.Spotlight-V100', '.fseventsd', '.Trashes', '.TemporaryItems',
          '.DocumentRevisions-V100', '.DS_Store'}
RELEASE = 'release-manifest.json'
PIN_KEYS = ('run_dir', 'release_dir', 'path')
HASH = re.compile(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])')
LEXICON = re.compile(r'(?:lab/)?lexicons/pl-[A-Za-z0-9-]+\.dawg')
VERSION = re.compile(r'^(?P<family>.+?)-v(?P<version>\d+(?:[a-z]+\d+)*)(?=-|$)')
LIST_SUFFIXES = ('.txt', '.txt.gz')


def parse_version(name):
    """Rodzina do pierwszego `-v<cyfry>` i wersja jako krotka (`v1r2` → (1, 2)); None, gdy nierozpoznane."""
    match = VERSION.match(name)
    if match is None:
        return None
    return match['family'], tuple(int(part) for part in re.findall(r'\d+', match['version']))


def _inside(path, root):
    return workfs.is_within(path, root, strict=True)


def _json(path):
    try:
        data = load_json(path)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _newest(path):
    """Najnowszy mtime katalogu i jego bezpośrednich wpisów (manifest, baza, journal, raporty)."""
    newest = os.lstat(path).st_mtime
    try:
        for child in os.scandir(path):
            newest = max(newest, child.stat(follow_symlinks=False).st_mtime)
    except OSError:
        pass
    return newest


# --- kontekst ---------------------------------------------------------------------------------

def _work_root(given):
    path = given or os.environ.get('LITERAKI_WORK_ROOT')
    if not path:
        return None, {'status': 'not-given', 'reason': 'brak --work-root i LITERAKI_WORK_ROOT; T7 pominięty'}
    try:
        _, marker = volume.check_work_root(path)
    except GeneratorError as error:
        # 75 niezamontowany; 76 korzeń na dysku repo albo wolumen bez znacznika: T7 pominięty, nic nie znika.
        status = 'unavailable' if error.code == 75 else 'wrong-volume'
        return None, {'status': status, 'path': path, 'code': error.code, 'reason': str(error)}
    return Path(os.path.realpath(path)), {'status': 'available', 'path': path, 'marker_id': marker['marker_id']}


def _links(work):
    """realpath celu → symlinki w data/work."""
    links = {}
    for child in sorted(work.iterdir()):
        if child.is_symlink():
            links.setdefault(os.path.realpath(child), []).append(child)
    return links


def _promotions(work):
    """Ścieżki t7_path/peer_path z rekordów promocji bez `completed` (katalogi i staging)."""
    paths = set()
    for record in sorted(work.glob('*/promotion.json')) + sorted(work.glob('.*.promote/promotion.json')):
        data = _json(record)
        if data is None or data.get('completed'):
            continue
        for key in ('t7_path', 'peer_path'):
            if isinstance(data.get(key), str):
                paths.add(os.path.realpath(data[key]))
    return paths


def _context(work_root):
    work = Path(volume.REPO_ROOT) / 'data' / 'work'
    return {'work': work, 'logs': Path(volume.REPO_ROOT) / 'logs', 'root': work_root,
            'links': _links(work), 'promotions': _promotions(work), 'now': time.time()}


# --- T7 ---------------------------------------------------------------------------------------

def classify_t7(entry, ctx):
    """(klasa, powód) wpisu w korzeniu T7 według pierwszeństwa 1–6."""
    if workfs.is_deleting(entry.name):
        return 5, 'przerwane kasowanie (.deleting); dokończy --apply'
    real = os.path.realpath(entry)
    links = ctx['links'].get(real, [])
    names = {entry.name} | {link.name for link in links}
    manifest = _json(entry / 'manifest.json') if entry.is_dir() and not entry.is_symlink() else None
    readiness = (manifest or {}).get('readiness')
    if readiness in ('VERIFIED', 'FROZEN'):
        return 1, f'manifest {readiness}; czeka na promocję' + ('' if links else ' (brak symlinku)')
    if any(workfs.lock_held(workfs.promote_lock(ctx['logs'], name)) for name in names):
        return 2, 'trzymana blokada promocji'
    if any(os.path.lexists(ctx['work'] / f'.{name}.promote') for name in names):
        return 2, 'staging promocji w data/work'
    if real in ctx['promotions']:
        return 2, 'ścieżka z promotion.json bez completed'
    if any(workfs.lock_held(workfs.supervisor_lock(ctx['logs'], name)) for name in names):
        return 3, 'trzymana blokada nadzorcy'
    if any(workfs.lock_held(workfs.build_lock(ctx['work'] / name)) for name in names):
        return 3, 'trzymana blokada buildu'
    stages = (manifest or {}).get('stages') or {}
    if readiness == 'INCOMPLETE' and set(stages) == set(STAGES) \
            and all((item or {}).get('status') == 'complete' for item in stages.values()):
        # Decyzja właściciela: kompletny build przed verify nie znika, choćby czekał dłużej niż 24 h.
        return 3, 'kompletny, czeka na verify'
    if ctx['now'] - _newest(entry) < AGE:
        return 3, 'zmieniany w ostatnich 24 h'
    if manifest is None:
        return 4, 'brak albo nieczytelny manifest'
    if readiness != 'INCOMPLETE':
        return 4, f'nieznany status manifestu: {readiness}'
    leftover = not (entry / 'build.sqlite').exists() and bool(stages) \
        and all((item or {}).get('status') == 'pending' for item in stages.values())
    kind = 'resztka startu' if leftover else 'INCOMPLETE'
    if not links:
        return 5, f'{kind} bez symlinku w data/work, ≥ 24 h'
    return 6, f'{kind} z symlinkiem w data/work, ≥ 24 h'


def scan_t7(ctx):
    root = ctx['root']
    if root is None:
        return []
    items = []
    for entry in sorted(root.iterdir()):
        if entry.name in SYSTEM or workfs.is_build_lock(entry.name):
            continue
        number, reason = classify_t7(entry, ctx)
        items.append({'entry': entry.name, 'where': 't7', 'class': number, 'class_name': CLASSES[number],
                      'size': workfs.tree_size(entry), 'reason': reason, 'path': entry})
    return items


# --- wydania ----------------------------------------------------------------------------------

def server_notice(repo):
    """Hashe z `git show origin/main:NOTICE` (tylko odczyt) albo powód niedostępności."""
    if not Path(repo).is_dir():
        return {'status': 'unavailable', 'reason': 'brak checkoutu serwera'}, set()
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env.update(GIT_TERMINAL_PROMPT='0', GIT_OPTIONAL_LOCKS='0')
    try:
        shown = subprocess.run(['git', '-C', str(repo), 'show', 'origin/main:NOTICE'], capture_output=True,
                               text=True, env=env, stdin=subprocess.DEVNULL, timeout=60)
    except (OSError, subprocess.SubprocessError) as error:
        return {'status': 'unavailable', 'reason': f'git nie działa: {error}'}, set()
    if shown.returncode != 0:
        detail = (shown.stderr.strip().splitlines() or ['bez komunikatu'])[0]
        return {'status': 'unavailable', 'reason': f'brak origin/main albo NOTICE: {detail}'}, set()
    hashes = set(HASH.findall(shown.stdout))
    if not hashes:
        return {'status': 'unavailable', 'reason': 'NOTICE bez żadnego hasha'}, set()
    return {'status': 'available', 'hashes': len(hashes),
            'lexicons': sorted(set(LEXICON.findall(shown.stdout)))}, hashes


def _pins():
    """Ścieżki (realpath) z kluczy run_dir/release_dir/path w config/generator/*-sources.json."""
    pins = []
    for config in sorted((Path(volume.REPO_ROOT) / 'config' / 'generator').glob('*-sources.json')):
        def walk(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key in PIN_KEYS and isinstance(value, str):
                        pins.append((os.path.realpath(config.parent / value), config.name))
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)
        walk(_json(config) or {})
    return pins


def _find_releases(work):
    """Wydania w data/work do głębokości 2 oraz katalogi-kontenery wydań."""
    releases, containers = [], set()
    for child in sorted(work.iterdir()):
        if child.is_symlink() or not child.is_dir():
            continue
        if (child / RELEASE).is_file():
            releases.append((child.name, child))
            continue
        for nested in sorted(child.iterdir()):
            if not nested.is_symlink() and nested.is_dir() and (nested / RELEASE).is_file():
                releases.append((f'{child.name}/{nested.name}', nested))
                containers.add(child.name)
    return releases, containers


def _server_hashes(path, manifest):
    hashes = set()
    try:
        hashes.add(sha256(path / RELEASE))
    except OSError:
        pass
    for name, item in (manifest.get('files') or {}).items():
        if isinstance(item, dict) and isinstance(item.get('sha256'), str):
            hashes.add(item['sha256'])
        target = path / name
        if name.endswith(LIST_SUFFIXES) and target.is_file() and not target.is_symlink():
            try:
                hashes.add(sha256(target))
            except OSError:
                pass
    return hashes


def analyse_releases(ctx, notice_hashes, notice_available, server_current):
    """Rekordy wydań: potrzebne (klasa 7, powody) albo kandydaci (8)."""
    work = ctx['work']
    releases, containers = _find_releases(work)
    pins = _pins()
    records = []
    for name, path in releases:
        manifest = _json(path / RELEASE)
        record = {'entry': name, 'path': path, 'manifest': manifest, 'needed': [],
                  'run': None, 'parsed': parse_version(path.name)}
        if manifest is None:
            record['needed'].append('nieczytelny release-manifest.json')
            records.append(record)
            continue
        run_name = (manifest.get('source_run') or {}).get('run_name')
        if isinstance(run_name, str) and run_name and '/' not in run_name:
            record['run'] = run_name
        if record['parsed'] is None:
            record['needed'].append('nierozpoznana nazwa wydania (rodzina/wersja)')
        roots = [os.path.realpath(path)] + ([os.path.realpath(work / record['run'])] if record['run'] else [])
        for pin, config in pins:
            if any(pin == root or pin.startswith(root + os.sep) for root in roots):
                record['needed'].append(f'przypięte w config/generator/{config}')
                break
        if not notice_available:
            record['needed'].append('NOTICE serwera niedostępny: wszystkie wydania potrzebne')
        elif _server_hashes(path, manifest) & notice_hashes:
            record['needed'].append('bieżące na serwerze (hash w NOTICE)')
        if name in server_current or path.name in server_current or manifest.get('package_id') in server_current:
            record['needed'].append('na liście --server-current')
        records.append(record)
    families = {}
    for record in records:
        if record['manifest'] is not None and record['parsed'] is not None:
            key = (record['parsed'][1], str(record['manifest'].get('frozen_at') or ''))
            families.setdefault(record['parsed'][0], []).append((key, record))
    for members in families.values():
        best = max(key for key, _ in members)
        for key, record in members:
            if key == best:
                record['needed'].append('ostatnie w rodzinie')
    return records, containers


def _run_deletable(work, run_name, referencing, approved):
    run = work / run_name
    if run.is_symlink() or not run.is_dir() or (_json(run / 'manifest.json') or {}).get('readiness') != 'FROZEN':
        return False
    return referencing.get(run_name, set()) <= approved


def scan_internal(ctx, records, containers):
    work, root = ctx['work'], ctx['root']
    by_entry = {record['entry']: record for record in records}
    referencing = {}
    for record in records:
        if record['run']:
            referencing.setdefault(record['run'], set()).add(record['entry'])
    candidates = {record['entry'] for record in records if not record['needed']}
    runs_with = {}
    for record in records:
        if record['entry'] in candidates and record['run'] \
                and _run_deletable(work, record['run'], referencing, candidates):
            runs_with.setdefault(record['run'], []).append(record['entry'])
    items = []
    for child in sorted(work.iterdir()):
        name = child.name
        if workfs.is_build_lock(name):
            continue  # pusty plik blokady buildu, opisany przy przebiegu
        if child.is_symlink():
            target = os.path.realpath(child)
            if root is not None and _inside(target, root) and os.path.lexists(target):
                continue  # opisany przy wpisie T7
            reason = 'symlink, cel niedostępny' if not os.path.exists(target) else 'symlink poza wolumenem roboczym'
            items.append({'entry': name, 'where': 'internal', 'class': 7, 'size': 0, 'reason': reason})
            continue
        if name in by_entry:
            continue
        if name in containers:
            reason = 'katalog z wydaniami'
        elif name in runs_with:
            reason = 'przebieg FROZEN; idzie z wydaniem-kandydatem ' + ', '.join(runs_with[name])
        elif (child / 'promotion.json').is_file():
            reason = 'promowany przebieg'
        elif name.startswith('.') and name.endswith('.promote'):
            reason = 'staging promocji'
        elif workfs.is_deleting(name):
            reason = 'przerwane kasowanie wydania (.deleting); dokończy --apply'
        else:
            reason = 'dysk wewnętrzny: tylko lista'
        items.append({'entry': name, 'where': 'internal', 'class': 7, 'size': workfs.tree_size(child),
                      'reason': reason})
    for record in records:
        number = 7 if record['needed'] else 8
        size = workfs.tree_size(record['path'])
        run = record['run'] if number == 8 and record['run'] in runs_with else None
        if run:
            size += workfs.tree_size(work / run)
        reason = '; '.join(record['needed']) if record['needed'] else 'stare wydanie; tylko z --delete-releases'
        items.append({'entry': record['entry'], 'where': 'internal', 'class': number, 'size': size,
                      'reason': reason, 'run': run})
    for item in items:
        item['class_name'] = CLASSES[item['class']]
    return items, referencing


# --- kasowanie --------------------------------------------------------------------------------

def _approved(path):
    try:
        lines = Path(path).read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise GeneratorError(f'Nieczytelny plik --delete-releases: {error}', 2) from error
    return {line.strip() for line in lines if line.strip() and not line.strip().startswith('#')}


def delete_t7(items, ctx):
    deleted, root = [], ctx['root']
    for item in items:
        if item['class'] not in T7_DELETABLE:
            continue
        entry = item['path']
        number, _ = classify_t7(entry, ctx)  # ponowna klasyfikacja tuż przed kasowaniem
        if number not in T7_DELETABLE or not _inside(entry, root) \
                or volume.mount_point(entry) == volume.repo_mount():
            continue
        real = os.path.realpath(entry)
        for link in ctx['links'].get(real, []):
            if link.is_symlink() and os.path.realpath(link) == real:
                os.unlink(link)
        if workfs.is_deleting(entry.name):
            workfs.finish_deleting(entry.parent)
        else:
            workfs.delete_tree(entry)
        deleted.append({'entry': item['entry'], 'where': 't7', 'class': number, 'size': item['size']})
    return deleted


def finish_internal(ctx, containers):
    """Dokańcza przerwane kasowania wydań (`.<nazwa>.deleting`) w data/work i w katalogach z wydaniami."""
    finished = []
    for directory in [ctx['work'], *(ctx['work'] / name for name in sorted(containers))]:
        for name in workfs.finish_deleting(directory):
            finished.append({'entry': name, 'where': 'internal', 'class': 7, 'size': 0,
                             'reason': 'dokończone przerwane kasowanie'})
    return finished


def delete_releases(names, records, referencing, ctx):
    work, deleted = ctx['work'], []
    by_entry = {record['entry']: record for record in records}
    for name in sorted(names):
        record = by_entry[name]
        path = record['path']
        if path.is_symlink() or not _inside(path, work) or not (path / RELEASE).is_file():
            raise GeneratorError('Wydanie poza data/work albo bez release-manifest.json; przerwano', 4, name)
        size = workfs.tree_size(path)
        workfs.delete_tree(path)
        deleted.append({'entry': name, 'where': 'internal', 'class': 8, 'size': size})
        run = record['run']
        if run and _run_deletable(work, run, referencing, names) and _inside(work / run, work):
            size = workfs.tree_size(work / run)
            workfs.delete_tree(work / run)
            deleted.append({'entry': run, 'where': 'internal', 'class': 8, 'size': size,
                            'reason': f'przebieg wydania {name}'})
    return deleted


def clean(work_root=None, *, apply=False, server_repo=None, server_current=(), delete_file=None):
    if delete_file is not None and not apply:
        raise GeneratorError('--delete-releases wymaga --apply', 2)
    approved = _approved(delete_file) if delete_file is not None else set()
    root, root_status = _work_root(work_root)
    ctx = _context(root)
    repo = server_repo or str(Path(volume.REPO_ROOT).parent / 'server')
    notice, hashes = server_notice(repo)
    records, containers = analyse_releases(ctx, hashes, notice['status'] == 'available', set(server_current))
    t7_items = scan_t7(ctx)
    internal_items, referencing = scan_internal(ctx, records, containers)
    candidates = sorted(record['entry'] for record in records if not record['needed'])
    refused = sorted(approved - set(candidates))
    if refused:
        raise GeneratorError('Odmowa: nazwy spoza kandydatów (nic nie skasowano): ' + ', '.join(refused), 4)
    deleted = []
    if apply:
        try:
            deleted += finish_internal(ctx, containers)
            deleted += delete_t7(t7_items, ctx)
            deleted += delete_releases(approved, records, referencing, ctx)
        except OSError as error:
            gone = root is not None and not os.path.isdir(root)
            raise GeneratorError(f'Kasowanie przerwane błędem dysku: {error}; ponów --apply', 75 if gone else 4,
                                 getattr(error, 'filename', None)) from error
    entries = [{key: value for key, value in item.items() if key != 'path'} for item in t7_items + internal_items]
    counts = {}
    for item in entries:
        counts[str(item['class'])] = counts.get(str(item['class']), 0) + 1
    return {'apply': apply, 'work_root': root_status, 'server_notice': notice, 'counts': counts,
            'candidates': candidates, 'entries': entries, 'deleted': deleted}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Sprzątanie przebiegów na T7 i starych wydań (domyślnie lista)')
    parser.add_argument('--work-root', help='korzeń przebiegów na T7 (domyślnie LITERAKI_WORK_ROOT)')
    parser.add_argument('--apply', action='store_true', help='kasuje klasy 5–6 na T7')
    parser.add_argument('--server-repo', help='checkout Literaki-server (domyślnie ../server), tylko odczyt')
    parser.add_argument('--server-current', action='append', default=[], metavar='NAZWA',
                        help='wydanie albo package_id bieżące na serwerze (dodatek do NOTICE)')
    parser.add_argument('--delete-releases', metavar='PLIK',
                        help='plik z nazwami wydań zaakceptowanymi przez właściciela; wymaga --apply')
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return 0 if error.code == 0 else 2
    try:
        result = clean(args.work_root, apply=args.apply, server_repo=args.server_repo,
                       server_current=args.server_current, delete_file=args.delete_releases)
    except GeneratorError as error:
        print(str(error), file=sys.stderr)
        return error.code
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
