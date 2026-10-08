"""G7/7.4: dwa małe przepływy cyklu przebiegu i awarie na granicach etapów."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from literaki_slownik import build as build_module
from literaki_slownik import export as export_module
from literaki_slownik.build import build
from literaki_slownik.canonical import load_json, write_json
from literaki_slownik.explain import explain
from literaki_slownik.export import export
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.run import set_stage
from literaki_slownik.verify import verify, KS
from tests.release_helpers import complete_pair, fixture_inputs, tree_hashes


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_build_verify_export_then_every_change_refused(self):
        _, run, peer, review = complete_pair(self.directory)
        self.assertEqual(verify(run, peer, review, allow_test_fixture=True)['verdict'], 'VERIFIED')
        with self.assertRaises(GeneratorError) as raised:
            set_stage(run, 'reports', 'running')
        self.assertEqual(raised.exception.code, 5)
        package = self.directory / 'pakiet'
        self.assertEqual(export(run, package, allow_test_fixture=True)['status'], 'FROZEN')
        frozen = tree_hashes(package)
        run_before = tree_hashes(run)
        for action in (lambda: set_stage(run, 'reports', 'complete'),
                       lambda: verify(run, peer, review, allow_test_fixture=True),
                       lambda: export(run, self.directory / 'drugi', allow_test_fixture=True)):
            with self.assertRaises(GeneratorError) as raised:
                action()
            self.assertEqual(raised.exception.code, 5)
        read = explain(run, 'kot', 'broad')
        self.assertEqual((read['readiness'], read['source_presence']), ('FROZEN', 'present'))
        self.assertEqual(frozen, tree_hashes(package))
        self.assertEqual(run_before, tree_hashes(run))
        self.assertFalse((self.directory / 'drugi').exists())

    def test_interrupted_build_is_failed_refused_and_keeps_previous_run(self):
        manifest = fixture_inputs(self.directory)
        previous = self.directory / 'poprzedni'
        build(manifest, previous)
        kept = tree_hashes(previous)
        broken = self.directory / 'przerwany'

        def interrupted(*args, **kwargs):
            raise KeyboardInterrupt

        with patch.object(build_module, 'import_kwjp', interrupted):
            with self.assertRaises(KeyboardInterrupt):
                build(manifest, broken)
        stages = load_json(broken / 'manifest.json')['stages']
        self.assertEqual(stages['import_sgjp']['status'], 'complete')
        self.assertEqual(stages['import_kwjp']['status'], 'failed')
        report = verify(broken, previous, self.directory / 'review.json', allow_test_fixture=True)
        self.assertEqual(report['verdict'], 'REFUSED')
        for k in KS:
            self.assertIn('import_kwjp ma status failed', ' '.join(r['message'] for r in report['checks'][k]['reasons']))
        self.assertEqual(load_json(broken / 'manifest.json')['readiness'], 'INCOMPLETE')
        with self.assertRaises(GeneratorError):
            build(manifest, previous)
        self.assertEqual(kept, tree_hashes(previous))

    def test_hard_crash_left_running_is_not_complete(self):
        _, run, peer, review = complete_pair(self.directory)
        manifest = load_json(run / 'manifest.json')
        manifest['stages']['decisions'] = {'status': 'running', 'updated': 'awaria'}
        write_json(run / 'manifest.json', manifest)
        report = verify(run, peer, review, allow_test_fixture=True)
        self.assertEqual(report['verdict'], 'REFUSED')
        self.assertIn('decisions ma status running', report['checks']['K3']['reasons'][0]['message'])

    def test_export_failure_inside_staging_leaves_no_package_and_retry_works(self):
        _, run, peer, review = complete_pair(self.directory)
        verify(run, peer, review, allow_test_fixture=True)
        target = self.directory / 'pakiet'

        def full_disk(staging, data):
            raise OSError(28, 'No space left on device')

        with patch.object(export_module, 'write_release_manifest', full_disk):
            with self.assertRaises(OSError):
                export(run, target, allow_test_fixture=True)
        self.assertFalse(target.exists())
        self.assertEqual(len(list(self.directory.glob('.pakiet.staging-*'))), 1)
        self.assertEqual(load_json(run / 'manifest.json')['readiness'], 'VERIFIED')
        self.assertEqual(export(run, self.directory / 'pakiet-2', allow_test_fixture=True)['status'], 'FROZEN')

    def test_cli_text_verify_lists_blocking_k(self):
        manifest = fixture_inputs(self.directory)
        run, peer = self.directory / 'a', self.directory / 'b'
        build(manifest, run)
        build(manifest, peer)
        result = subprocess.run([sys.executable, '-m', 'literaki_slownik', 'verify', '--run-dir', str(run),
                                 '--peer-run', str(peer), '--review', str(self.directory / 'r.json')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertIn('Werdykt: REFUSED', result.stdout)
        # Kompletny build fikstury: blokują tryb test (K1) i brak przeglądu (K7, K9).
        self.assertIn('K1: BLOKADA', result.stdout)
        self.assertIn('K9: BLOKADA', result.stdout)
        self.assertIn('K3: OK', result.stdout)
        self.assertIn('blokady: K1', result.stderr)


if __name__ == '__main__':
    unittest.main()
