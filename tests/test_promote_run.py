"""R10: promocja przebiegu z T7 na dysk wewnętrzny (S0–S4) i odmowa `export` na T7."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
import stat
from pathlib import Path
from unittest import mock

from literaki_slownik import export as export_module
from literaki_slownik.canonical import load_json, sha256, write_json
from literaki_slownik.export import changes_since_verify, export
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.reports import canonical_index
from literaki_slownik.verify import verify
from tests.layout_helpers import LayoutCase
from tests.release_helpers import complete_pair, tree_hashes

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('promote_run', ROOT / 'scripts/promote_run.py')
promote_run = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(promote_run)


class Crash(BaseException):
    """Symulowane przerwanie procesu; omija obsługę błędów skryptu."""


def crash_at(event, nth=1):
    seen = []

    def hook(name):
        if name == event:
            seen.append(name)
            if len(seen) == nth:
                raise Crash(name)
    return hook


class PromoteRunTests(LayoutCase):
    def pair(self, verified=True):
        """Para A+B na T7 (`Data/pair`) z symlinkami w data/work; A po verify."""
        root = self.data / 'pair'
        root.mkdir()
        _, run, peer, review = complete_pair(root)
        self.t7_a, self.t7_b = run, peer
        self.link, self.peer = self.work / 'run-a', self.work / 'run-b'
        os.symlink(run, self.link)
        os.symlink(peer, self.peer)
        if verified:
            report = verify(self.link, self.peer, review, allow_test_fixture=True)
            self.assertEqual(report['verdict'], 'VERIFIED')
        self.manifest_bytes = (run / 'manifest.json').read_bytes()
        self.tree = tree_hashes(run)
        return self.link

    def promote(self, **kwargs):
        return promote_run.promote(self.link, self.peer, **kwargs)

    def refused(self, code, **kwargs):
        with self.assertRaises(GeneratorError) as raised:
            self.promote(**kwargs)
        self.assertEqual(raised.exception.code, code, str(raised.exception))
        return raised.exception

    def staging(self):
        return self.work / '.run-a.promote'

    def assert_promoted(self):
        self.assertFalse(self.link.is_symlink())
        self.assertTrue(self.link.is_dir())
        self.assertFalse(os.path.lexists(self.staging()))
        record = load_json(self.link / 'promotion.json')
        self.assertIsNotNone(record['completed'])
        self.assertEqual(record['t7_path'], str(self.t7_a))
        self.assertEqual(record['marker_id'], 'm-data')
        self.assertEqual((self.link / 'manifest.json').read_bytes(), self.manifest_bytes)
        self.assertEqual(tree_hashes(self.link, skip=('promotion.json',)), self.tree)
        self.assertFalse(self.t7_a.exists())
        self.assertFalse(os.path.lexists(self.peer))
        self.assertFalse(self.t7_b.exists())

    def test_refuses_run_not_verified(self):
        self.pair(verified=False)
        self.assertIn('VERIFIED', str(self.refused(5)))
        self.assertTrue(self.link.is_symlink())
        self.assertFalse(os.path.lexists(self.staging()))

    def test_file_changed_on_t7_after_verify_refused(self):
        self.pair()
        broad = self.t7_a / 'lists/broad.txt'
        broad.write_bytes(broad.read_bytes() + b'pies\n')
        self.refused(5)
        self.assertTrue(self.link.is_symlink())
        self.assertTrue(self.t7_a.is_dir() and self.t7_b.is_dir())

    def test_copy_with_other_sha_or_mode_is_4_and_nothing_deleted(self):
        real_copy = promote_run._copy_file

        def corrupt_bytes(source, target):
            real_copy(source, target)
            if target.name == 'broad.txt':
                os.chmod(target, 0o644)
                target.write_bytes(b'zepsute\n')

        def corrupt_mode(source, target):
            real_copy(source, target)
            if target.name == 'standard.txt':
                os.chmod(target, stat.S_IMODE(os.stat(target).st_mode) ^ stat.S_IRGRP)

        for name, fake in (('sha256', corrupt_bytes), ('tryb', corrupt_mode)):
            with self.subTest(name):
                self.setUp()
                self.pair()
                with mock.patch.object(promote_run, '_copy_file', fake):
                    self.refused(4)
                self.assertTrue(self.link.is_symlink())
                self.assertEqual(tree_hashes(self.t7_a), self.tree)
                self.assertTrue(self.t7_b.is_dir() and self.peer.is_symlink())
                self.assertTrue(self.staging().is_dir())

    def test_t7_vanishing_mid_copy_is_75_and_staging_stays(self):
        self.pair()
        real_copy, calls = promote_run._copy_file, []

        def vanish(source, target):
            calls.append(target)
            if len(calls) == 3:
                self.mounts.discard(str(self.data))
                raise OSError(5, 'Input/output error')
            real_copy(source, target)

        with mock.patch.object(promote_run, '_copy_file', vanish):
            self.refused(75)
        self.assertTrue(self.staging().is_dir())
        self.assertTrue(self.link.is_symlink())
        self.mounts.add(str(self.data))
        result = self.promote()
        self.assertEqual(result['status'], 'promoted')
        self.assert_promoted()

    def test_interrupt_in_every_state_then_rerun_completes(self):
        for event, nth in (('copy-file', 1), ('copy-file', 5), ('staged', 1), ('swapped', 1),
                           ('unlinked', 1), ('peer-deleted', 1), ('t7-deleted', 1)):
            with self.subTest(event=event, nth=nth):
                self.setUp()
                self.pair()
                with self.assertRaises(Crash):
                    self.promote(hook=crash_at(event, nth))
                self.assertEqual(self.promote()['status'], 'promoted')
                self.assert_promoted()
                again = self.promote()
                self.assertEqual(again['status'], 'already-promoted')

    def test_rerun_after_export_deletes_t7_copy(self):
        self.pair()
        with self.assertRaises(Crash):
            self.promote(hook=crash_at('unlinked'))
        self.assertTrue(self.t7_a.is_dir())
        release = self.internal / 'release'
        export(self.link, release, allow_test_fixture=True)
        self.assertEqual(load_json(self.link / 'manifest.json')['readiness'], 'FROZEN')
        result = self.promote()
        self.assertEqual(result['status'], 'promoted')
        self.assertFalse(self.t7_a.exists())
        self.assertFalse(self.t7_b.exists())
        self.assertIsNotNone(load_json(self.link / 'promotion.json')['completed'])

    def test_peer_deleted_only_when_incomplete_with_matching_index(self):
        def other_index(_):
            index = self.t7_b / 'reports/canonical-index.json'
            index.write_bytes(index.read_bytes() + b'\n')

        def verified_peer(_):
            manifest = load_json(self.t7_b / 'manifest.json')
            manifest['readiness'] = 'VERIFIED'
            write_json(self.t7_b / 'manifest.json', manifest)

        def moved_link(_):
            other = self.data / 'pair' / 'run-c'
            other.mkdir()
            os.unlink(self.peer)
            os.symlink(other, self.peer)

        for name, change in (('inny canonical-index', other_index), ('B VERIFIED', verified_peer),
                             ('symlink B gdzie indziej', moved_link)):
            with self.subTest(name):
                self.setUp()
                self.pair()
                change(None)
                result = self.promote()
                self.assertEqual(result['status'], 'promoted')
                self.assertFalse(result['peer_deleted'])
                self.assertTrue(self.t7_b.is_dir())
                self.assertTrue(os.path.lexists(self.peer))
                self.assertFalse(self.t7_a.exists())
                log = (self.repo / 'logs/run-a.promote.log').read_text(encoding='utf-8')
                self.assertIn('peer-kept', log)

    def test_export_refuses_symlink_and_run_on_work_volume(self):
        self.pair()
        for path in (self.link, self.t7_a):
            with self.subTest(path=path.name):
                with self.assertRaises(GeneratorError) as raised:
                    export(path, self.internal / ('out-' + path.parent.name), allow_test_fixture=True)
                self.assertEqual(raised.exception.code, 5)
                self.assertIn('promote_run.py', str(raised.exception))
        self.assertEqual(load_json(self.t7_a / 'manifest.json')['readiness'], 'VERIFIED')

    def test_export_after_promotion_passes_seal_despite_promotion_json(self):
        self.pair()
        self.promote()
        manifest = load_json(self.link / 'manifest.json')
        self.assertEqual(changes_since_verify(self.link, manifest), [])
        self.assertNotIn('promotion.json', canonical_index(self.link)['files'])
        self.assertNotIn('promotion', manifest)
        release = self.internal / 'release'
        result = export(self.link, release, allow_test_fixture=True)
        self.assertEqual(result['status'], 'FROZEN')
        self.assertNotIn('promotion.json', load_json(release / 'release-manifest.json')['files'])
        self.assertEqual(self.promote()['status'], 'already-promoted')

    def pair_promoted_cli(self):
        self.setUp()
        self.pair()
        with redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(promote_run.main(['--run-dir', str(self.link), '--peer', str(self.peer)]), 0)
        result = json.loads(stdout.getvalue())
        self.assertEqual((result['status'], result['state'], result['peer_deleted']), ('promoted', 'S0', True))
        self.assert_promoted()

    def test_cli_json_and_exit_codes(self):
        self.pair(verified=False)
        with redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(promote_run.main(['--run-dir', str(self.link), '--peer', str(self.peer)]), 5)
        self.assertIn('VERIFIED', stderr.getvalue())
        self.pair_promoted_cli()
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            promote_run.main([])
        self.assertEqual(raised.exception.code, 2)


class RenameSwapTests(LayoutCase):
    def test_swap_exchanges_symlink_and_directory(self):
        target = self.data / 'a'
        target.mkdir()
        link, staging = self.work / 'a', self.work / '.a.promote'
        os.symlink(target, link)
        staging.mkdir()
        (staging / 'f').write_text('x', encoding='utf-8')
        export_module.rename_swap(staging, link)
        self.assertTrue(link.is_dir() and not link.is_symlink())
        self.assertTrue(staging.is_symlink())
        self.assertEqual(stat.S_IFMT(os.lstat(link / 'f').st_mode), stat.S_IFREG)
        self.assertEqual(os.path.realpath(staging), str(target))
