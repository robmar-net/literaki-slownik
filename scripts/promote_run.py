#!/usr/bin/env python3
"""Promocja zweryfikowanego przebiegu z T7 na dysk wewnętrzny (#22, R10).

Użycie:
  python3 scripts/promote_run.py --run-dir data/work/<A> [--peer data/work/<B>]

Stany na dysku (wznawialne z każdego miejsca):
  S0  data/work/<A> to symlink, brak stagingu: kontrole pieczęci, wolumenu i miejsca.
  S1  symlink + staging data/work/.<A>.promote: staging zawsze od zera, kopia trwała,
      porównanie sha256 i trybu, promotion.json, changes_since_verify(staging) puste.
  S2  po renamex_np(RENAME_SWAP): data/work/<A> to katalog z promotion.json.
  S3  kasowanie B (INCOMPLETE i zgodny canonical-index) i kopii A na T7.
  S4  promotion.json ma `completed`: nic do zrobienia.

Manifest A się nie zmienia, więc pieczęć verify zostaje ważna. stdout: JSON; stderr: błąd.
Kody: 0, 2 argumenty, 4 kopia/zamiana/blokada, 5 pieczęć, 75 T7 zniknął, 76 zły wolumen,
78 brak miejsca wewnątrz.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from literaki_slownik import canonical, volume  # noqa: E402
from literaki_slownik.canonical import load_json, sha256, write_json  # noqa: E402
from literaki_slownik.export import changes_since_verify, rename_swap  # noqa: E402
from literaki_slownik.inputs import GeneratorError  # noqa: E402
from literaki_slownik.run import now  # noqa: E402

RECORD = 'promotion.json'
SPACE_FACTOR = 1.1


def _logs():
    logs = Path(volume.REPO_ROOT) / 'logs'
    logs.mkdir(exist_ok=True)
    return logs


def _log(name, event, **details):
    with (_logs() / f'{name}.promote.log').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps({'time': now(), 'event': event, **details}, ensure_ascii=False) + '\n')


def _guard(path, marker_id):
    """Strażnik T7 po błędzie albo przed S3: brak ścieżki lub montowania → 75, zły znacznik → 76."""
    if not os.path.exists(path):
        raise GeneratorError('Dysk roboczy zniknął (brak ścieżki na T7)', 75, str(path))
    volume.check_marker(path, marker_id)


def _classify(error, path, marker_id):
    """Błąd I/O: strażnik daje 75/76; gdy przechodzi, błąd jest błędem kopii (4)."""
    _guard(path, marker_id)
    return GeneratorError(f'Błąd I/O promocji: {error}', 4, str(path))


def _copy_file(source, target):
    """Trwała kopia pliku: tmp obok celu, F_FULLFSYNC, tryb i mtime źródła, os.replace, sync katalogu."""
    info = os.lstat(source)
    descriptor, temporary = tempfile.mkstemp(prefix='.' + target.name + '-', dir=target.parent)
    replaced = False
    try:
        with open(source, 'rb') as reader, os.fdopen(descriptor, 'wb') as writer:
            shutil.copyfileobj(reader, writer, 1024 * 1024)
            writer.flush()
            canonical._full_sync(writer.fileno())
        os.chmod(temporary, stat.S_IMODE(info.st_mode))
        os.utime(temporary, ns=(info.st_atime_ns, info.st_mtime_ns))
        os.replace(temporary, target)
        replaced = True
        canonical._sync_directory(target.parent)
    finally:
        if not replaced:
            try:
                os.unlink(temporary)
            except OSError:
                pass


def _walk(source):
    """Pliki i katalogi przebiegu (ścieżki względne). Symlink albo plik specjalny → 4."""
    directories, files = [], []
    for current, names, filenames in os.walk(source, followlinks=False):
        for name in sorted(names + filenames):
            path = Path(current) / name
            mode = os.lstat(path).st_mode
            relative = path.relative_to(source)
            if stat.S_ISDIR(mode):
                directories.append(relative)
            elif stat.S_ISREG(mode):
                files.append(relative)
            else:
                raise GeneratorError('Przebieg zawiera symlink albo plik specjalny; promocja odmawia', 4,
                                     str(relative))
        names.sort()
    return directories, files


def _size(source):
    return sum(os.lstat(Path(source) / relative).st_size for relative in _walk(source)[1])


def _remove(path):
    """Kasowanie drzewa z plikami tylko do odczytu (np. build.sqlite po export)."""
    def writable(function, target, _):
        os.chmod(os.path.dirname(target), stat.S_IRWXU)
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR)
        function(target)
    shutil.rmtree(path, onerror=writable)


def _check_s0(link, manifest):
    volume.check_mounted(link)
    if manifest.get('readiness') != 'VERIFIED':
        raise GeneratorError(f'Promocja wymaga przebiegu VERIFIED (jest {manifest.get("readiness")})', 5,
                             str(link))
    changes = changes_since_verify(link, manifest)
    if changes:
        raise GeneratorError('Zmiany po verify unieważniają werdykt: ' + ', '.join(changes), 5, str(link))
    marker_id = (manifest.get('work_volume') or {}).get('marker_id')
    if volume.check_marker(link, marker_id) is None:
        raise GeneratorError('Przebieg nie leży na wolumenie roboczym; nic do promocji', 5, str(link))
    need = int(_size(os.path.realpath(link)) * SPACE_FACTOR)
    free = volume.free_bytes(link.parent)
    if free < need:
        raise GeneratorError(f'Za mało miejsca na dysku wewnętrznym: {free // volume.GB} GB < '
                             f'{-(-need // volume.GB)} GB', 78, str(link.parent))
    return marker_id


def _stage(link, staging, peer, marker_id, hook):
    """S1: staging od zera, kopia, porównanie, promotion.json i pieczęć na stagingu."""
    source = Path(os.path.realpath(link))
    if os.path.lexists(staging):
        if staging.is_symlink() or not staging.is_dir():
            os.unlink(staging)
        else:
            _remove(staging)
    staging.mkdir()
    directories, files = _walk(source)
    for relative in directories:
        (staging / relative).mkdir()
    for relative in files:
        _copy_file(source / relative, staging / relative)
        hook('copy-file')
    for relative in files:
        original, copy = os.lstat(source / relative), os.lstat(staging / relative)
        if stat.S_IMODE(original.st_mode) != stat.S_IMODE(copy.st_mode) \
                or sha256(source / relative) != sha256(staging / relative):
            raise GeneratorError('Kopia różni się od T7 (sha256 albo tryb); nic nie skasowano', 4, str(relative))
    if set(_walk(staging)[1]) != set(files):
        raise GeneratorError('Staging zawiera pliki spoza przebiegu', 4, str(staging))
    peer_link = str(Path(peer).absolute()) if peer is not None else None
    write_json(staging / RECORD, {
        'schema_version': 1, 'kind': 'literaki-promotion', 't7_path': str(source),
        'peer_link': peer_link, 'peer_path': os.path.realpath(peer) if peer is not None else None,
        'marker_id': marker_id, 'started': now(), 'completed': None})
    changes = changes_since_verify(staging, load_json(staging / 'manifest.json'))
    if changes:
        raise GeneratorError('Staging nie przechodzi pieczęci verify: ' + ', '.join(changes), 4, str(staging))
    hook('staged')


def _swap(link, staging, hook):
    """S1 → S2: atomowa zamiana symlinku na katalog (dawny symlink zostaje pod nazwą stagingu)."""
    try:
        rename_swap(staging, link)
    except OSError as error:
        raise GeneratorError(f'Zamiana nazw nie powiodła się; nic nie zmieniono: {error}', 4, str(link)) from error
    hook('swapped')


def _peer_deletable(record, seal, name):
    peer_link, peer_path = record.get('peer_link'), record.get('peer_path')
    if peer_link is None:
        return False
    link = Path(peer_link)
    if not link.is_symlink() or os.path.realpath(link) != peer_path:
        _log(name, 'peer-kept', reason='symlink B nie wskazuje peer_path')
        return False
    if volume.mount_point(peer_path) == volume.repo_mount() or peer_path == record['t7_path']:
        _log(name, 'peer-kept', reason='B leży na dysku wewnętrznym')
        return False
    try:
        manifest = load_json(Path(peer_path) / 'manifest.json')
        index = sha256(Path(peer_path) / 'reports/canonical-index.json')
    except (OSError, ValueError):
        _log(name, 'peer-kept', reason='nieczytelny manifest albo canonical-index B')
        return False
    if manifest.get('readiness') != 'INCOMPLETE':
        _log(name, 'peer-kept', reason=f'B ma status {manifest.get("readiness")}')
        return False
    if index != seal.get('canonical_index_sha256'):
        _log(name, 'peer-kept', reason='canonical-index B różni się od pieczęci A')
        return False
    return True


def _finish(link, staging, name, hook):
    """S2/S3: sprzątanie po zamianie, kasowanie B i kopii A na T7, `completed`."""
    if staging.is_symlink():
        os.unlink(staging)
        canonical._sync_directory(link.parent)
    hook('unlinked')
    record = load_json(link / RECORD)
    if record.get('completed'):
        return {'status': 'already-promoted', 'run': link.name, 'peer_deleted': None, 't7_deleted': None}
    manifest = load_json(link / 'manifest.json')
    if manifest.get('readiness') not in ('VERIFIED', 'FROZEN'):
        raise GeneratorError(f'Promowany przebieg ma status {manifest.get("readiness")}', 5, str(link))
    t7_path, marker_id = Path(record['t7_path']), record['marker_id']
    # Kopia A mogła już zniknąć przy przerwanej próbie; korzeń przebiegów na T7 zostaje.
    _guard(t7_path.parent, marker_id)
    peer_deleted = False
    try:
        peer_link, peer_path = record.get('peer_link'), record.get('peer_path')
        if peer_link and Path(peer_link).is_symlink() and os.path.realpath(peer_link) == peer_path \
                and not os.path.lexists(peer_path) and Path(peer_path).parent.is_dir():
            # Przerwanie między skasowaniem B a jego symlinku.
            os.unlink(peer_link)
            peer_deleted = True
        elif _peer_deletable(record, manifest.get('verification') or {}, name):
            _remove(peer_path)
            os.unlink(peer_link)
            peer_deleted = True
            _log(name, 'peer-deleted')
        hook('peer-deleted')
        t7_deleted = False
        if os.path.lexists(t7_path):
            if os.path.realpath(t7_path) == os.path.realpath(link) \
                    or volume.mount_point(t7_path) == volume.repo_mount():
                raise GeneratorError('t7_path wskazuje katalog wewnętrzny; nic nie skasowano', 4, str(t7_path))
            _remove(t7_path)
            t7_deleted = True
            _log(name, 't7-deleted')
        hook('t7-deleted')
    except OSError as error:
        raise _classify(error, t7_path.parent, marker_id) from error
    record['completed'] = now()
    write_json(link / RECORD, record)
    _log(name, 'completed')
    return {'status': 'promoted', 'run': link.name, 'peer_deleted': peer_deleted, 't7_deleted': t7_deleted}


def _state(link, staging):
    if link.is_symlink():
        return 'S1' if os.path.lexists(staging) else 'S0'
    if not link.is_dir():
        raise GeneratorError('Brak przebiegu', 4, str(link))
    try:
        record = load_json(link / RECORD)
    except FileNotFoundError as error:
        raise GeneratorError('Przebieg wewnętrzny bez promotion.json; nic do promocji', 5, str(link)) from error
    except (OSError, ValueError) as error:
        raise GeneratorError(f'Nieczytelny promotion.json: {error}', 4, str(link)) from error
    return 'S4' if record.get('completed') else 'S2'


def _promote(link, peer, hook):
    name = link.name
    staging = link.parent / f'.{name}.promote'
    state = _state(link, staging)
    _log(name, 'start', state=state)
    if state in ('S0', 'S1'):
        try:
            manifest = load_json(link / 'manifest.json')
        except (OSError, ValueError) as error:
            volume.check_mounted(link)
            raise GeneratorError(f'Nieczytelny manifest przebiegu: {error}', 4, str(link)) from error
        marker_id = _check_s0(link, manifest)
        t7_path = os.path.realpath(link)
        try:
            _stage(link, staging, peer, marker_id, hook)
        except OSError as error:
            raise _classify(error, t7_path, marker_id) from error
        _swap(link, staging, hook)
        _log(name, 'swapped')
    result = _finish(link, staging, name, hook)
    result['state'] = state
    return result


def promote(run_dir, peer_dir=None, *, hook=None):
    """Promocja A (i skasowanie B) pod blokadą logs/<A>.promote.lock. `hook` służy testom przerwań."""
    link = Path(run_dir).absolute()
    peer = Path(peer_dir).absolute() if peer_dir is not None else None
    lock = open(_logs() / f'{link.name}.promote.lock', 'a')
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise GeneratorError('Promocja tego przebiegu już trwa (blokada)', 4, str(link)) from error
        try:
            return _promote(link, peer, hook or (lambda event: None))
        except GeneratorError as error:
            _log(link.name, 'error', code=error.code, message=str(error))
            raise
    finally:
        lock.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description='Promocja przebiegu z T7 na dysk wewnętrzny')
    parser.add_argument('--run-dir', required=True, help='data/work/<A> (symlink na T7)')
    parser.add_argument('--peer', help='data/work/<B>: kasowany, gdy INCOMPLETE i zgodny z pieczęcią A')
    args = parser.parse_args(argv)
    try:
        result = promote(args.run_dir, args.peer)
    except GeneratorError as error:
        print(str(error), file=sys.stderr)
        return error.code
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
