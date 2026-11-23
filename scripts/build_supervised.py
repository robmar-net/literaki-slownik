#!/usr/bin/env python3
"""Nadzorca buildu: po kodzie 75 czeka na dysk roboczy i wznawia przebieg (#22, R9).

Użycie:
  python3 scripts/build_supervised.py --manifest M --run-dir data/work/<nazwa> [--work-root W]
      [--max-resumes 3] [--wait-minutes 30] [--poll-seconds 5]

Przed każdym procesem: przebieg istnieje (lexists) i manifest jest czytelny → `build --resume`;
przebiegu nie ma → świeży `build --work-root W` (także po 75 sprzed powstania przebiegu);
symlink jest, a dysku brak → czekanie. Po 75 co `poll` sekund G1+G2 strażnika. Wolumen o tym
marker_id pod inną ścieżką albo inny znacznik → 76 od razu. Po `wait` minutach albo po
`max-resumes` wznowieniach → 75. Inne kody kończą pracę z tym kodem. SIGINT trafia do buildu
i kończy kodem 130; SIGTERM i SIGHUP trafiają do buildu i kończą jego kodem, bez wznowienia.

Plików przebiegu nie dotyka. Logi na dysku wewnętrznym: logs/<nazwa>.out.json (stdout prób,
dopisywany), logs/<nazwa>.err, logs/<nazwa>.supervisor.log (linia JSON na zdarzenie).
Przez cały czas pracy trzyma flock na logs/<nazwa>.lock (clean_work.py rozpoznaje po nim
żywy przebieg). stdout: JSON z wynikiem. Kody jak `build` (0, 2, 3, 4, 5, 75, 76, 77, 78, 130);
4 także wtedy, gdy blokadę trzyma inny nadzorca.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from literaki_slownik import volume  # noqa: E402
from literaki_slownik.canonical import load_json  # noqa: E402
from literaki_slownik.inputs import GeneratorError  # noqa: E402

RETRY = 75
LOGS = ROOT / 'logs'


def _manifest(run_dir):
    """Manifest przebiegu albo None, gdy nieczytelny (np. dysk zniknął)."""
    try:
        manifest = load_json(Path(run_dir) / 'manifest.json')
    except (OSError, ValueError):
        return None
    return manifest if isinstance(manifest, dict) else None


def _marker_id(run_dir, work_root):
    """marker_id z manifestu, a przy świeżym starcie ze znacznika W; None, gdy nieznany."""
    manifest = _manifest(run_dir)
    if manifest is not None:
        return (manifest.get('work_volume') or {}).get('marker_id')
    if work_root is not None and os.path.isdir(work_root):
        try:
            return (volume.read_marker(volume.mount_point(work_root)) or {}).get('marker_id')
        except GeneratorError:
            return None
    return None


def probe(run_dir, work_root, marker_id):
    """G1+G2 przed ponowieniem: brak dysku → GeneratorError 75, zły wolumen → 76."""
    if os.path.lexists(run_dir):
        volume.check_mounted(run_dir)
        if marker_id is not None:
            volume.check_marker(run_dir, marker_id)
        return
    if work_root is None:
        return
    if not os.path.isdir(work_root):
        raise GeneratorError('Katalog --work-root nie istnieje; dysk roboczy niezamontowany', 75)
    mount = volume.mount_point(work_root)
    if mount == volume.repo_mount():
        raise GeneratorError('--work-root leży na dysku repo; wolumen roboczy niezamontowany', 75)
    marker = volume.read_marker(mount)
    if marker is None or (marker_id is not None and marker['marker_id'] != marker_id):
        raise GeneratorError('Wolumen pod --work-root ma inny znacznik albo żadnego', 76)


def command(manifest, run_dir, work_root):
    """Polecenie następnego procesu albo None, gdy symlink jest, a manifestu nie da się czytać."""
    if os.path.lexists(run_dir):
        if _manifest(run_dir) is None and os.path.islink(run_dir):
            return None
        return ['build', '--resume', '--manifest', manifest, '--run-dir', run_dir, '--json']
    fresh = ['build', '--manifest', manifest, '--run-dir', run_dir, '--json']
    return fresh + (['--work-root', work_root] if work_root is not None else [])


def lock_held(path):
    """Czy ktoś trzyma flock na pliku blokady."""
    try:
        stream = open(path, 'rb')
    except FileNotFoundError:
        return False
    with stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(stream, fcntl.LOCK_UN)
        return False


def _within(path, root):
    path, root = str(path), str(root)
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def _wait(run_dir, work_root, marker_id, *, probe, find, sleep, clock, wait_seconds, poll_seconds, state, log):
    """Czeka na dysk. Zwraca 0 (wracamy do pracy), 75 (limit czasu), 76 (zły wolumen) albo sygnał."""
    deadline = clock() + wait_seconds
    expected = os.path.realpath(work_root if work_root is not None and not os.path.lexists(run_dir) else run_dir)
    while True:
        try:
            probe(run_dir, work_root, marker_id)
            return 0
        except GeneratorError as error:
            if error.code != RETRY:
                log('wrong_volume', code=error.code, message=str(error))
                return error.code
        found = find(marker_id) if marker_id is not None else None
        if found is not None and not _within(expected, found):
            log('elsewhere', path=str(found))
            return 76
        if clock() >= deadline:
            log('timeout', seconds=wait_seconds)
            return RETRY
        sleep(poll_seconds)
        if state.get('signal') is not None:
            return 130 if state['signal'] == signal.SIGINT else RETRY


def supervise(manifest, run_dir, work_root=None, *, run_build, sleep=time.sleep, clock=time.monotonic,
              probe=probe, find=volume.find_by_marker, logs_dir=LOGS, max_resumes=3, wait_seconds=1800,
              poll_seconds=5, state=None):
    """Pętla nadzorcy. `run_build(argv, out, err)` zwraca kod procesu buildu; `state['signal']`
    ustawia obsługa sygnałów. Zwraca kod wyjścia nadzorcy."""
    state = {'signal': None} if state is None else state
    run_dir = str(run_dir)
    name = Path(run_dir).name
    logs = Path(logs_dir)
    logs.mkdir(parents=True, exist_ok=True)
    lock = open(logs / f'{name}.lock', 'a+b')
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({'error': f'inny nadzorca trzyma blokadę logs/{name}.lock'}, ensure_ascii=False),
                  file=sys.stderr)
            return 4
        with open(logs / f'{name}.supervisor.log', 'a', encoding='utf-8') as events, \
                open(logs / f'{name}.out.json', 'a', encoding='utf-8') as out, \
                open(logs / f'{name}.err', 'a', encoding='utf-8') as err:
            def log(event, **fields):
                record = {'at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'event': event, 'run': name, **fields}
                events.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + '\n')
                events.flush()

            resumes = 0
            while True:
                argv = command(manifest, run_dir, work_root)
                if argv is None:
                    code = RETRY
                    log('disk_missing')
                else:
                    log('start', argv=argv, resumes=resumes)
                    code = run_build(argv, out, err)
                    out.flush()
                    err.flush()
                    log('exit', code=code)
                if state.get('signal') is not None:
                    code = 130 if state['signal'] == signal.SIGINT else code
                    log('end', code=code, signal=int(state['signal']))
                    return code
                if code != RETRY:
                    log('end', code=code)
                    return code
                if resumes >= max_resumes:
                    log('end', code=code, reason='max_resumes')
                    return code
                marker_id = _marker_id(run_dir, work_root)
                log('wait', marker_id_known=marker_id is not None)
                waited = _wait(run_dir, work_root, marker_id, probe=probe, find=find, sleep=sleep, clock=clock,
                               wait_seconds=wait_seconds, poll_seconds=poll_seconds, state=state, log=log)
                if waited != 0:
                    log('end', code=waited)
                    return waited
                resumes += 1
    finally:
        lock.close()


def subprocess_runner(state):
    """Prawdziwy build w procesie potomnym; sygnały przekazuje obsługa z `install_signals`."""
    def run(argv, out, err):
        child = subprocess.Popen([sys.executable, '-m', 'literaki_slownik', *argv], cwd=ROOT,
                                 stdout=out, stderr=err, start_new_session=True)
        state['child'] = child
        try:
            code = child.wait()
        finally:
            state['child'] = None
        return 128 - code if code < 0 else code
    return run


def install_signals(state):
    def handler(signum, frame):
        state['signal'] = signum
        child = state.get('child')
        if child is not None and child.poll() is None:
            child.send_signal(signum)
    for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(signum, handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Nadzorca buildu: wznawia przebieg tylko po kodzie 75')
    parser.add_argument('--manifest', required=True, help='Manifest lokalnych wejść')
    parser.add_argument('--run-dir', required=True, help='data/work/<nazwa>')
    parser.add_argument('--work-root', help='Korzeń wolumenu roboczego dla świeżego przebiegu')
    parser.add_argument('--max-resumes', type=int, default=3, help='Limit wznowień po 75')
    parser.add_argument('--wait-minutes', type=float, default=30, help='Jak długo czekać na dysk po 75')
    parser.add_argument('--poll-seconds', type=float, default=5, help='Co ile sekund sprawdzać dysk')
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return 0 if error.code == 0 else 2
    if args.max_resumes < 0 or args.wait_minutes < 0 or args.poll_seconds <= 0:
        print(json.dumps({'error': 'limity muszą być nieujemne, a poll dodatni'}, ensure_ascii=False),
              file=sys.stderr)
        return 2
    state = {'signal': None, 'child': None}
    install_signals(state)
    code = supervise(args.manifest, args.run_dir, args.work_root, run_build=subprocess_runner(state),
                     max_resumes=args.max_resumes, wait_seconds=args.wait_minutes * 60,
                     poll_seconds=args.poll_seconds, state=state)
    print(json.dumps({'run_dir': args.run_dir, 'exit_code': code}, ensure_ascii=False))
    return code


if __name__ == '__main__':
    sys.exit(main())
