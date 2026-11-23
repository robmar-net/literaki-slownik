"""R9: nadzorca buildu wznawia tylko po 75; build_pair.sh sprawdza środowisko przed startem."""
from contextlib import redirect_stderr
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import tempfile
import unittest
from unittest import mock

from literaki_slownik import volume
from literaki_slownik.canonical import write_json
from literaki_slownik.inputs import GeneratorError
from tests.layout_helpers import LayoutCase

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('build_supervised', ROOT / 'scripts/build_supervised.py')
build_supervised = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_supervised)


class FakeClock:
    """Zegar przesuwany tylko przez podstawiony sleep: testy nie czekają."""

    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class SupervisorCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = self.tmp / 'work' / 'lists-x-a'
        self.run_dir.parent.mkdir()
        self.logs = self.tmp / 'logs'
        self.time = FakeClock()
        self.calls = []

    def fake_build(self, codes, create_run=True):
        """Podstawiony build: zwraca kolejne kody; przy pierwszym wywołaniu tworzy przebieg."""
        codes = list(codes)

        def run(argv, out, err):
            self.calls.append(list(argv))
            if create_run and not self.run_dir.exists():
                self.run_dir.mkdir()
                write_json(self.run_dir / 'manifest.json', {'work_volume': {'marker_id': 'm-1'}})
            out.write(json.dumps({'attempt': len(self.calls)}) + '\n')
            return codes.pop(0)
        return run

    def supervise(self, run, probe=None, find=None, **options):
        return build_supervised.supervise(
            'config/generator/sources.json', str(self.run_dir), work_root=options.pop('work_root', None),
            run_build=run, sleep=self.time.sleep, clock=self.time.clock,
            probe=probe or (lambda *args: None), find=find or (lambda marker_id: None),
            logs_dir=self.logs, **options)

    def events(self):
        path = self.logs / 'lists-x-a.supervisor.log'
        return [json.loads(line)['event'] for line in path.read_text(encoding='utf-8').splitlines()]

    def test_75_75_0_resumes_twice_and_ends_0(self):
        code = self.supervise(self.fake_build([75, 75, 0]))
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls), 3)
        self.assertNotIn('--resume', self.calls[0])
        self.assertTrue(all('--resume' in argv for argv in self.calls[1:]))
        self.assertEqual(len((self.logs / 'lists-x-a.out.json').read_text().splitlines()), 3)
        self.assertEqual(self.events()[-1], 'end')

    def test_four_times_75_stops_with_75_after_three_resumes(self):
        code = self.supervise(self.fake_build([75, 75, 75, 75, 0]))
        self.assertEqual(code, 75)
        self.assertEqual(len(self.calls), 4)

    def test_75_before_the_run_exists_starts_fresh_again(self):
        code = self.supervise(self.fake_build([75, 0], create_run=False), work_root=str(self.tmp / 'T7'))
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls), 2)
        for argv in self.calls:
            self.assertNotIn('--resume', argv)
            self.assertIn('--work-root', argv)

    def test_other_codes_stop_without_retry(self):
        for code in (4, 77, 76, 78, 5, 2, 3):
            self.calls.clear()
            shutil.rmtree(self.run_dir, ignore_errors=True)
            self.assertEqual(self.supervise(self.fake_build([code, 0])), code)
            self.assertEqual(len(self.calls), 1, code)
            self.assertEqual(self.time.sleeps, [])

    def test_volume_elsewhere_or_wrong_marker_stops_76_at_once(self):
        def missing(*args):
            raise GeneratorError('brak dysku', 75)
        found = self.tmp / 'T7 1'
        code = self.supervise(self.fake_build([75, 0]), probe=missing, find=lambda marker_id: found)
        self.assertEqual((code, len(self.calls), self.time.sleeps), (76, 1, []))
        self.assertIn('elsewhere', self.events())

        def wrong(*args):
            raise GeneratorError('inny znacznik', 76)
        self.calls.clear()
        self.assertEqual(self.supervise(self.fake_build([75, 0]), probe=wrong), 76)
        self.assertEqual(len(self.calls), 1)

    def test_waiting_longer_than_the_limit_ends_75(self):
        def missing(*args):
            raise GeneratorError('brak dysku', 75)
        code = self.supervise(self.fake_build([75, 0]), probe=missing, wait_seconds=60, poll_seconds=5)
        self.assertEqual(code, 75)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(sum(self.time.sleeps), 60)
        self.assertTrue(all(seconds == 5 for seconds in self.time.sleeps))

    def test_disk_returning_during_wait_resumes(self):
        answers = [75, 75, None]

        def flaky(*args):
            code = answers.pop(0)
            if code:
                raise GeneratorError('brak dysku', code)
        self.assertEqual(self.supervise(self.fake_build([75, 0]), probe=flaky), 0)
        self.assertEqual(self.time.sleeps, [5, 5])
        self.assertIn('--resume', self.calls[1])

    def test_sigint_ends_130_and_other_signals_pass_the_child_code(self):
        state = {'signal': None}
        run = self.fake_build([75, 0])

        def interrupted(argv, out, err):
            state['signal'] = signal.SIGINT
            return run(argv, out, err)
        self.assertEqual(self.supervise(interrupted, state=state), 130)
        self.assertEqual(len(self.calls), 1)

        state['signal'] = None
        self.calls.clear()
        run = self.fake_build([75, 0])

        def terminated(argv, out, err):
            state['signal'] = signal.SIGTERM
            return run(argv, out, err)
        self.assertEqual(self.supervise(terminated, state=state), 75)
        self.assertEqual(len(self.calls), 1)

    def test_lock_is_held_while_supervising_and_a_second_supervisor_refuses(self):
        seen = []

        def run(argv, out, err):
            seen.append(build_supervised.lock_held(self.logs / 'lists-x-a.lock'))
            with redirect_stderr(io.StringIO()):
                self.assertEqual(self.supervise(self.fake_build([0])), 4)
            return 0
        self.assertEqual(self.supervise(run), 0)
        self.assertEqual(seen, [True])
        self.assertFalse(build_supervised.lock_held(self.logs / 'lists-x-a.lock'))

    def test_marker_known_before_the_disk_vanished_finds_the_volume_elsewhere_at_once(self):
        # Po 75 manifest na T7 jest nieczytelny; marker_id zapamiętany przed pierwszym procesem wystarcza.
        self.run_dir.mkdir()
        write_json(self.run_dir / 'manifest.json', {'work_volume': {'marker_id': 'm-1'}})

        def vanish(argv, out, err):
            self.calls.append(list(argv))
            (self.run_dir / 'manifest.json').unlink()
            return 75

        def missing(*args):
            raise GeneratorError('brak dysku', 75)
        found = self.tmp / 'T7 1'
        code = self.supervise(vanish, probe=missing, find=lambda marker_id: found if marker_id == 'm-1' else None)
        self.assertEqual((code, len(self.calls), self.time.sleeps), (76, 1, []))
        self.assertIn('elsewhere', self.events())

    def test_stalled_child_resumes_when_the_guard_fails_and_stops_4_when_healthy(self):
        self.run_dir.mkdir()
        write_json(self.run_dir / 'manifest.json', {'work_volume': {'marker_id': 'm-1'}})
        codes = [build_supervised.STALLED, 0]

        def stalled(argv, out, err):
            self.calls.append(list(argv))
            return codes.pop(0)
        answers = [75, None, None]

        def guard(*args):
            code = answers.pop(0)
            if code:
                raise GeneratorError('brak dysku', code)
        self.assertEqual(self.supervise(stalled, probe=guard), 0)
        self.assertEqual(len(self.calls), 2)
        self.assertIn('--resume', self.calls[1])
        self.assertIn('stalled', self.events())

        self.calls.clear()
        shutil.rmtree(self.logs)
        codes[:] = [build_supervised.STALLED, 0]
        self.assertEqual(self.supervise(stalled), 4)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.events()[-2:], ['stalled', 'end'])


class FakeChild:
    """Proces potomny na podstawionym zegarze: wait(timeout) przesuwa czas i rzuca TimeoutExpired."""

    def __init__(self, clock, finish_at=None, ignores_term=False):
        self.clock, self.finish_at, self.ignores_term = clock, finish_at, ignores_term
        self.code, self.signals, self.pid = None, [], 4242

    def poll(self):
        if self.code is None and self.finish_at is not None and self.clock.now >= self.finish_at:
            self.code = 0
        return self.code

    def wait(self, timeout=None):
        if self.poll() is not None:
            return self.code
        self.clock.sleep(timeout)
        if self.poll() is not None:
            return self.code
        raise subprocess.TimeoutExpired('build', timeout)

    def terminate(self):
        self.signals.append('TERM')
        if not self.ignores_term:
            self.code = -signal.SIGTERM

    def kill(self):
        self.signals.append('KILL')
        self.code = -signal.SIGKILL


class WatchdogTests(unittest.TestCase):
    def watch(self, child, progress, clock):
        return build_supervised.watch(child, progress, clock=clock.clock, stall_seconds=7200, poll_seconds=60,
                                      grace_seconds=30)

    def test_progress_keeps_the_child_alive_until_it_ends(self):
        clock = FakeClock()
        child = FakeChild(clock, finish_at=5 * 3600)
        self.assertEqual(self.watch(child, lambda: clock.now, clock), 0)
        self.assertEqual(child.signals, [])

    def test_no_progress_for_the_limit_terminates_then_kills(self):
        for ignores, expected in ((False, ['TERM']), (True, ['TERM', 'KILL'])):
            with self.subTest(ignores_term=ignores):
                clock = FakeClock()
                child = FakeChild(clock, ignores_term=ignores)
                self.assertEqual(self.watch(child, lambda: 'stoi', clock), build_supervised.STALLED)
                self.assertEqual(child.signals, expected)
                self.assertGreaterEqual(clock.now, 7200)
                self.assertLess(clock.now, 7200 + 60 + 2 * 30 + 1)

    def test_zero_limit_disables_the_watchdog(self):
        clock = FakeClock()
        child = FakeChild(clock, finish_at=30 * 3600)
        self.assertEqual(build_supervised.watch(child, lambda: 'stoi', clock=clock.clock, stall_seconds=0,
                                                poll_seconds=60), 0)

    def test_progress_sees_database_journal_and_reports(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / 'reports').mkdir()
        before = build_supervised.progress(tmp, None)
        (tmp / 'build.sqlite-journal').write_bytes(b'j')
        self.assertNotEqual(build_supervised.progress(tmp, None), before)
        self.assertEqual(build_supervised.progress(tmp / 'brak', None), build_supervised.progress(tmp / 'brak', None))


class SignalTests(unittest.TestCase):
    def test_signal_before_popen_starts_no_build(self):
        state = {'signal': signal.SIGTERM, 'child': None}
        run = build_supervised.subprocess_runner(state, '/brak/run', stall_seconds=0)
        with mock.patch.object(build_supervised.subprocess, 'Popen', side_effect=AssertionError('Popen')):
            self.assertEqual(run(['build'], None, None), 128 + signal.SIGTERM)

    def test_nohup_keeps_sighup_ignored(self):
        previous = {signum: signal.getsignal(signum) for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
        self.addCleanup(lambda: [signal.signal(signum, handler) for signum, handler in previous.items()])
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        build_supervised.install_signals({'signal': None, 'child': None})
        self.assertIs(signal.getsignal(signal.SIGHUP), signal.SIG_IGN)
        self.assertIsNot(signal.getsignal(signal.SIGTERM), signal.SIG_IGN)


class ProbeCase(unittest.TestCase):
    """Domyślna sonda: G1 i G2 strażnika na podstawionym montowaniu (bez /Volumes)."""

    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp()))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / 'repo'
        self.t7 = self.tmp / 'T7'
        (self.repo / 'data/work').mkdir(parents=True)
        self.t7.mkdir()
        self.mounts = {str(self.t7)}
        for patch in (mock.patch.object(volume, 'REPO_ROOT', self.repo),
                      mock.patch('os.path.ismount', lambda path: os.path.realpath(path) in self.mounts
                                 or os.path.realpath(path) == '/')):
            patch.start()
            self.addCleanup(patch.stop)
        write_json(self.t7 / volume.MARKER, {'marker_id': 'm-1'})
        (self.t7 / 'lists-x-a').mkdir()
        self.run_dir = self.repo / 'data/work/lists-x-a'
        self.run_dir.symlink_to(self.t7 / 'lists-x-a')

    def code(self, *args):
        try:
            build_supervised.probe(*args)
        except GeneratorError as error:
            return error.code
        return 0

    def test_g1_without_g2_is_76_and_missing_mount_is_75(self):
        self.assertEqual(self.code(str(self.run_dir), None, 'm-1'), 0)
        self.assertEqual(self.code(str(self.run_dir), None, 'm-2'), 76)
        self.mounts.clear()
        self.assertEqual(self.code(str(self.run_dir), None, 'm-1'), 75)
        # Korzeń istnieje, ale leży na dysku repo: zły wolumen (76) jak w check_fresh i build_pair.sh.
        self.assertEqual(self.code(str(self.repo / 'data/work/nowy'), str(self.t7), 'm-1'), 76)
        self.assertEqual(self.code(str(self.repo / 'data/work/nowy'), str(self.t7 / 'brak'), 'm-1'), 75)
        self.mounts.add(str(self.t7))
        self.assertEqual(self.code(str(self.repo / 'data/work/nowy'), str(self.t7), 'm-1'), 0)
        self.assertEqual(self.code(str(self.repo / 'data/work/nowy'), str(self.t7), 'm-2'), 76)


class BuildPairCase(unittest.TestCase):
    """build_pair.sh w kopii repo z podstawionym PATH: bez caffeinate i bez buildu."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / 'repo'
        (self.repo / 'scripts').mkdir(parents=True)
        shutil.copy(ROOT / 'scripts/build_pair.sh', self.repo / 'scripts/build_pair.sh')
        self.bin = self.tmp / 'bin'
        self.bin.mkdir()
        self.record = self.tmp / 'record.txt'
        self.tool('git', 'exit 0')
        self.tool('python3', '[ "$1" = "-c" ] && exit "${FAKE_SPACE_RC:-0}"\necho "python3 $*" >> "$FAKE_RECORD"')
        self.tool('caffeinate', 'echo "caffeinate $*" >> "$FAKE_RECORD"\nshift\nexec "$@"')
        self.work = self.tmp / 'T7'
        self.work.mkdir()

    def tool(self, name, body):
        path = self.bin / name
        path.write_text('#!/bin/sh\n' + body + '\n', encoding='utf-8')
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def run_pair(self, env=None, *args):
        base = {'PATH': f'{self.bin}:/usr/bin:/bin', 'FAKE_RECORD': str(self.record)}
        return subprocess.run(['/bin/sh', str(self.repo / 'scripts/build_pair.sh'), *args],
                              env={**base, **(env or {})}, capture_output=True, text=True)

    def test_requires_work_root_name_and_space(self):
        self.assertEqual(self.run_pair({}, 'lists-x').returncode, 2)
        self.assertEqual(self.run_pair({'LITERAKI_WORK_ROOT': str(self.work)}).returncode, 2)
        low = self.run_pair({'LITERAKI_WORK_ROOT': str(self.work), 'FAKE_SPACE_RC': '78'}, 'lists-x')
        self.assertEqual(low.returncode, 78)
        self.assertFalse(self.record.exists())

    def test_starts_two_supervisors_under_caffeinate(self):
        done = self.run_pair({'LITERAKI_WORK_ROOT': str(self.work)}, 'lists-x')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue((self.repo / 'logs').is_dir())
        lines = self.record.read_text(encoding='utf-8').splitlines()
        sleepers = [line for line in lines if line.startswith('caffeinate -dimsu ')]
        supervisors = [line for line in lines if 'scripts/build_supervised.py' in line]
        self.assertEqual((len(sleepers), len(supervisors)), (2, 4))
        logs = sorted(path.name.rsplit('-', 1)[1] for path in (self.repo / 'logs').iterdir())
        # Końcowy JSON nadzorcy idzie do .supervisor.out, a nie do jego logu zdarzeń.
        self.assertEqual(logs, ['a.err', 'a.supervisor.out', 'b.err', 'b.supervisor.out'])
        for side in 'ab':
            self.assertTrue(any('--run-dir data/work/lists-x-' in line and line.endswith(
                f'-{side} --work-root {self.work}') for line in supervisors if line.startswith('python3')),
                lines)


class SupervisorWithRealBuildTests(LayoutCase):
    """Styk: nadzorca czyta kody prawdziwego `cli.main build` i jego polecenie przyjmuje parser CLI."""

    def test_disk_lost_in_a_stage_is_75_then_supervisor_resumes_to_a_complete_run(self):
        import contextlib
        import sqlite3
        from literaki_slownik import build as build_module, cli
        from literaki_slownik.canonical import load_json
        from literaki_slownik.run import STAGES
        run_dir = self.work / 'lists-e2e-a'
        real_decisions = build_module.STAGE_RUNNERS['decisions']
        lost = []

        def decisions(db, ctx):
            if not lost:
                lost.append(True)
                self.mounts.discard(str(self.data))  # T7 znika w trakcie etapu.
                raise sqlite3.OperationalError('disk I/O error')
            return real_decisions(db, ctx)

        codes = []

        def run_build(argv, out, err):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                codes.append(cli.main(list(argv)))
            return codes[-1]

        clock = FakeClock()

        def sleep(seconds):
            clock.sleep(seconds)
            self.mounts.add(str(self.data))  # Dysk wraca przy pierwszym czekaniu.

        from tests.test_resume import clean_identity  # drzewo robocze implementera bywa dirty
        with mock.patch.dict(build_module.STAGE_RUNNERS, {'decisions': decisions}), clean_identity():
            code = build_supervised.supervise(
                str(self.manifest), str(run_dir), work_root=str(self.data), run_build=run_build,
                sleep=sleep, clock=clock.clock, find=lambda marker_id: None, logs_dir=self.repo / 'logs')
        self.assertEqual(code, 0)
        self.assertEqual(codes, [75, 0])
        self.assertTrue(run_dir.is_symlink())
        manifest = load_json(run_dir / 'manifest.json')
        self.assertEqual([manifest['stages'][name]['status'] for name in STAGES], ['complete'] * len(STAGES))
        self.assertEqual(manifest['resume']['count'], 1)
        # Strata ≤ bieżący etap: wznowienie zaczyna od etapu, w którym zniknął dysk.
        self.assertEqual([(attempt['exit_code'], attempt['first_stage']) for attempt in manifest['build_attempts']],
                         [(75, 'preflight'), (0, 'decisions')])
        log = (self.repo / 'logs/lists-e2e-a.supervisor.log').read_text(encoding='utf-8').splitlines()
        argvs = [json.loads(line)['argv'] for line in log if json.loads(line)['event'] == 'start']
        self.assertIn('--work-root', argvs[0])
        self.assertEqual(argvs[1][:2], ['build', '--resume'])


if __name__ == '__main__':
    unittest.main()
