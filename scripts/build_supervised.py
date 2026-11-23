#!/usr/bin/env python3
"""Nadzorca buildu: po kodzie 75 czeka na dysk roboczy i wznawia przebieg (#22, R9).

Użycie (odpięte od terminala, bez uśpienia maszyny):
  nohup caffeinate -dimsu python3 scripts/build_supervised.py --manifest M --run-dir data/work/<nazwa>
      [--work-root W] [--max-resumes 3] [--wait-minutes 30] [--poll-seconds 5] [--stall-minutes 120]
      > logs/<nazwa>.supervisor.out 2>> logs/<nazwa>.err & disown

Przed każdym procesem: przebieg istnieje (lexists) i manifest jest czytelny → `build --resume`;
przebiegu nie ma → świeży `build --work-root W` (także po 75 sprzed powstania przebiegu);
symlink jest, a dysku brak → czekanie. Po 75 co `poll` sekund G1+G2 strażnika. Wolumen o tym
marker_id pod inną ścieżką albo inny znacznik → 76 od razu (marker_id zapamiętany przed pierwszym
procesem i po każdym, bo po 75 manifest na T7 bywa nieczytelny). Po `wait` minutach albo po
`max-resumes` wznowieniach → 75. Dwa 75 z rzędu w tym samym etapie, za każdym razem przy sondzie
zdrowej od razu (dysk nie zniknął), → zdarzenie `repeated-75-healthy` i kod 4: to błąd w kodzie albo błąd
I/O spoza odłączenia, a nie utrata dysku. Jedno takie 75 dalej wznawia (T7 wrócił przed sondą).
Inne kody kończą pracę z tym kodem. SIGINT trafia do buildu
i kończy kodem 130; SIGTERM i SIGHUP trafiają do buildu i kończą jego kodem, bez wznowienia.
Uruchomiony przez `nohup` (SIGHUP ignorowany) zostawia SIGHUP ignorowany.

Watchdog: gdy przez `--stall-minutes` (domyślnie 120, 0 wyłącza) nie zmienia się mtime manifestu,
bazy, journala ani raportów i nie rośnie czas CPU dziecka, nadzorca zapisuje `stalled`, wysyła SIGTERM,
po 60 s SIGKILL. Strażnik G1/G2 zawodzi → 75 (czekanie i wznowienie), zły wolumen → 76, inaczej 4.
Gdy `ps` nie podaje czasu CPU, postęp liczy się tylko z mtime; nadzorca zapisuje wtedy raz na proces
zdarzenie `cputime-unknown`.

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

from literaki_slownik import volume, workfs  # noqa: E402
from literaki_slownik.canonical import load_json  # noqa: E402
from literaki_slownik.inputs import GeneratorError  # noqa: E402
from literaki_slownik.run import STAGES  # noqa: E402

RETRY = 75
LOGS = ROOT / 'logs'
STALLED = 'stalled'  # wynik run_build po zatrzymaniu zawieszonego buildu przez watchdog
STALL_SECONDS = 2 * 3600


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


def _stage(run_dir):
    """Etap, w którym przerwała się próba (pierwszy `failed` albo `running`); None, gdy nieznany."""
    stages = (_manifest(run_dir) or {}).get('stages')
    if not isinstance(stages, dict):
        return None
    return next((name for name in STAGES if (stages.get(name) or {}).get('status') in ('failed', 'running')), None)


def probe(run_dir, work_root, marker_id):
    """G1+G2 przed ponowieniem: brak dysku → GeneratorError 75, zły wolumen (także dysk repo) → 76."""
    if os.path.lexists(run_dir):
        volume.check_mounted(run_dir)
        if marker_id is not None:
            volume.check_marker(run_dir, marker_id)
        return
    if work_root is None:
        return
    _, marker = volume.check_work_root(work_root)
    if marker_id is not None and marker['marker_id'] != marker_id:
        raise GeneratorError('Wolumen pod --work-root ma inny znacznik', 76)


def command(manifest, run_dir, work_root):
    """Polecenie następnego procesu albo None, gdy symlink jest, a manifestu nie da się czytać."""
    if os.path.lexists(run_dir):
        if _manifest(run_dir) is None and os.path.islink(run_dir):
            return None
        return ['build', '--resume', '--manifest', manifest, '--run-dir', run_dir, '--json']
    fresh = ['build', '--manifest', manifest, '--run-dir', run_dir, '--json']
    return fresh + (['--work-root', work_root] if work_root is not None else [])


lock_held = workfs.lock_held


def progress(run_dir, pid):
    """Ślad postępu buildu: mtime manifestu, bazy, journala, raportów i ich znaczników oraz czas CPU dziecka.

    Etap `reports` potrafi godzinami tylko czytać bazę (tabele temp w RAM); wtedy rośnie sam czas CPU.
    Proces zawieszony na I/O zanikającego USB nie zmienia ani plików, ani CPU."""
    run = Path(run_dir)
    times = []
    for name in ('manifest.json', 'build.sqlite', 'build.sqlite-journal', 'reports', 'reports/.done'):
        try:
            times.append(os.stat(run / name).st_mtime_ns)
        except OSError:
            times.append(None)
    cpu = None
    if pid is not None:
        try:
            cpu = subprocess.run(['ps', '-o', 'cputime=', '-p', str(pid)], capture_output=True, text=True,
                                 timeout=30).stdout.strip() or None
        except (OSError, subprocess.SubprocessError):
            cpu = None
    return tuple(times), cpu


def stop_child(child, grace_seconds):
    """SIGTERM, po `grace_seconds` SIGKILL; proces w nieprzerywalnym I/O może nie zniknąć i wtedy go zostawia."""
    child.terminate()
    try:
        child.wait(timeout=grace_seconds)
        return
    except subprocess.TimeoutExpired:
        pass
    child.kill()
    try:
        child.wait(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        pass


def watch(child, progress, *, clock, stall_seconds, poll_seconds=60, grace_seconds=60):
    """Czeka na koniec dziecka. Bez zmiany `progress()` przez `stall_seconds` (0 wyłącza): stop_child → STALLED."""
    last, since = progress(), clock()
    while True:
        try:
            code = child.wait(timeout=poll_seconds)
            return 128 - code if code < 0 else code
        except subprocess.TimeoutExpired:
            pass
        current = progress()
        if current != last:
            last, since = current, clock()
        elif stall_seconds and clock() - since >= stall_seconds:
            stop_child(child, grace_seconds)
            return STALLED


def _wait(run_dir, work_root, marker_id, *, probe, find, sleep, clock, wait_seconds, poll_seconds, state, log):
    """Czeka na dysk. Zwraca (kod, od_razu): 0 (wracamy do pracy), 75 (limit czasu), 76 (zły wolumen) albo
    sygnał; `od_razu` jest prawdą, gdy dysk był zdrowy już przy pierwszej sondzie."""
    deadline = clock() + wait_seconds
    expected = os.path.realpath(work_root if work_root is not None and not os.path.lexists(run_dir) else run_dir)
    first = True
    while True:
        try:
            probe(run_dir, work_root, marker_id)
            return 0, first
        except GeneratorError as error:
            if error.code != RETRY:
                log('wrong_volume', code=error.code, message=str(error))
                return error.code, False
        first = False
        found = find(marker_id) if marker_id is not None else None
        if found is not None and not workfs.is_within(expected, found):
            log('elsewhere', path=str(found))
            return 76, False
        if clock() >= deadline:
            log('timeout', seconds=wait_seconds)
            return RETRY, False
        sleep(poll_seconds)
        if state.get('signal') is not None:
            return (130 if state['signal'] == signal.SIGINT else RETRY), False


def _stalled(run_dir, work_root, marker_id, probe, log):
    """Kod po zatrzymaniu zawieszonego buildu: strażnik zawodzi → 75 (wznowienie), zły wolumen → 76, inaczej 4."""
    try:
        probe(run_dir, work_root, marker_id)
    except GeneratorError as error:
        log('stalled', guard=error.code)
        return error.code
    log('stalled', guard=0)
    return 4


def supervise(manifest, run_dir, work_root=None, *, run_build, sleep=time.sleep, clock=time.monotonic,
              probe=probe, find=volume.find_by_marker, logs_dir=LOGS, max_resumes=3, wait_seconds=1800,
              poll_seconds=5, state=None):
    """Pętla nadzorcy. `run_build(argv, out, err)` zwraca kod procesu buildu; `state['signal']`
    ustawia obsługa sygnałów, a `state['log']` dostaje funkcję logu zdarzeń. Zwraca kod wyjścia nadzorcy."""
    state = {'signal': None} if state is None else state
    run_dir = str(run_dir)
    name = Path(run_dir).name
    logs = Path(logs_dir)
    logs.mkdir(parents=True, exist_ok=True)
    lock = open(workfs.supervisor_lock(logs, name), 'a+b')
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
            state['log'] = log

            resumes = 0
            healthy_stage = None  # etap poprzedniego 75 przy od razu zdrowej sondzie (N1)
            # marker_id znany przed zniknięciem dysku: po 75 manifest na T7 bywa nieczytelny (R9, 76 od razu).
            marker_id = _marker_id(run_dir, work_root)
            while True:
                marker_id = _marker_id(run_dir, work_root) or marker_id
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
                    marker_id = _marker_id(run_dir, work_root) or marker_id
                if code == STALLED:
                    code = _stalled(run_dir, work_root, marker_id, probe, log)
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
                log('wait', marker_id_known=marker_id is not None)
                waited, at_once = _wait(run_dir, work_root, marker_id, probe=probe, find=find, sleep=sleep,
                                        clock=clock, wait_seconds=wait_seconds, poll_seconds=poll_seconds,
                                        state=state, log=log)
                if waited != 0:
                    log('end', code=waited)
                    return waited
                stage = _stage(run_dir) if at_once else None
                if stage is not None and stage == healthy_stage:
                    # Dysk nie zniknął dwa razy z rzędu, a etap pada tak samo: wznowienie powtórzy błąd.
                    log('repeated-75-healthy', stage=stage)
                    log('end', code=4, reason='repeated-75-healthy')
                    return 4
                healthy_stage = stage
                resumes += 1
    finally:
        state.pop('log', None)
        lock.close()


def subprocess_runner(state, run_dir, *, stall_seconds=STALL_SECONDS, poll_seconds=60, clock=time.monotonic):
    """Prawdziwy build w procesie potomnym pod watchdogiem; sygnały przekazuje obsługa z `install_signals`."""
    def run(argv, out, err):
        if state.get('signal') is not None:
            return 128 + int(state['signal'])  # Sygnał przed startem: nowego buildu nie zaczyna.
        child = subprocess.Popen([sys.executable, '-m', 'literaki_slownik', *argv], cwd=ROOT,
                                 stdout=out, stderr=err, start_new_session=True)
        state['child'] = child
        warned = []

        def tracked():
            current = progress(run_dir, child.pid)
            if current[1] is None and not warned and state.get('log') is not None:
                warned.append(True)  # Raz na proces: watchdog liczy postęp tylko z mtime (N2).
                state['log']('cputime-unknown', pid=child.pid)
            return current
        try:
            if state.get('signal') is not None and child.poll() is None:
                child.send_signal(state['signal'])  # Sygnał między Popen a przypisaniem dziecka.
            return watch(child, tracked, clock=clock, stall_seconds=stall_seconds, poll_seconds=poll_seconds)
        finally:
            state['child'] = None
    return run


def install_signals(state):
    def handler(signum, frame):
        state['signal'] = signum
        child = state.get('child')
        if child is not None and child.poll() is None:
            child.send_signal(signum)
    for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        if signum == signal.SIGHUP and signal.getsignal(signum) == signal.SIG_IGN:
            continue  # Uruchomiony przez nohup: SIGHUP zostaje ignorowany.
        signal.signal(signum, handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Nadzorca buildu: wznawia przebieg tylko po kodzie 75')
    parser.add_argument('--manifest', required=True, help='Manifest lokalnych wejść')
    parser.add_argument('--run-dir', required=True, help='data/work/<nazwa>')
    parser.add_argument('--work-root', help='Korzeń wolumenu roboczego dla świeżego przebiegu')
    parser.add_argument('--max-resumes', type=int, default=3, help='Limit wznowień po 75')
    parser.add_argument('--wait-minutes', type=float, default=30, help='Jak długo czekać na dysk po 75')
    parser.add_argument('--poll-seconds', type=float, default=5, help='Co ile sekund sprawdzać dysk')
    parser.add_argument('--stall-minutes', type=float, default=STALL_SECONDS / 60,
                        help='Watchdog: tyle minut bez postępu buildu → zatrzymanie (0 wyłącza)')
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return 0 if error.code == 0 else 2
    if args.max_resumes < 0 or args.wait_minutes < 0 or args.poll_seconds <= 0 or args.stall_minutes < 0:
        print(json.dumps({'error': 'limity muszą być nieujemne, a poll dodatni'}, ensure_ascii=False),
              file=sys.stderr)
        return 2
    state = {'signal': None, 'child': None}
    install_signals(state)
    runner = subprocess_runner(state, args.run_dir, stall_seconds=args.stall_minutes * 60)
    code = supervise(args.manifest, args.run_dir, args.work_root, run_build=runner,
                     max_resumes=args.max_resumes, wait_seconds=args.wait_minutes * 60,
                     poll_seconds=args.poll_seconds, state=state)
    print(json.dumps({'run_dir': args.run_dir, 'exit_code': code}, ensure_ascii=False))
    return code


if __name__ == '__main__':
    sys.exit(main())
