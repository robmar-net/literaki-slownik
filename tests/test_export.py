import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from literaki_slownik.canonical import load_json, sha256
from literaki_slownik.database import connect
from literaki_slownik.export import export, rename_noreplace
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.reports import logical_content_report
from literaki_slownik.verify import verify
from literaki_slownik import export as export_module
from tests.release_helpers import complete_pair, tree_hashes


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def verified(self):
        manifest, run, peer, review = complete_pair(self.directory)
        report = verify(run, peer, review, allow_test_fixture=True)
        self.assertEqual(report['verdict'], 'VERIFIED')
        return manifest, run, report

    def refused(self, run, target, **kwargs):
        with self.assertRaises(GeneratorError) as raised:
            export(run, target, **kwargs)
        self.assertEqual(raised.exception.code, 5, str(raised.exception))
        return str(raised.exception)

    def test_export_refused_without_positive_verify(self):
        manifest, run, peer, review = complete_pair(self.directory)
        self.assertIn('VERIFIED', self.refused(run, self.directory / 'out', allow_test_fixture=True))
        self.assertFalse((self.directory / 'out').exists())

    def test_frozen_package_has_exact_verified_bytes_and_non_recursive_manifest(self):
        _, run, report = self.verified()
        with connect(run / 'build.sqlite', readonly=True) as db:
            logical_before = logical_content_report(db)['sha256']
        target = self.directory / 'release'
        result = export(run, target, allow_test_fixture=True)
        self.assertEqual(result['status'], 'FROZEN')
        release = load_json(target / 'release-manifest.json')
        self.assertEqual(release['status'], 'FROZEN')
        self.assertNotIn('release-manifest.json', release['files'])
        plan = load_json(run / report['attempt'] / 'package-plan.json')
        candidate = run / report['attempt'] / 'candidate'
        for relative, meta in plan['files'].items():
            self.assertEqual(sha256(target / relative), meta['sha256'], relative)
            self.assertEqual((target / relative).read_bytes(), (candidate / relative).read_bytes())
            self.assertEqual(release['files'][relative]['sha256'], meta['sha256'])
        on_disk = {str(p.relative_to(target)) for p in target.rglob('*') if p.is_file()}
        self.assertEqual(on_disk - {'release-manifest.json'}, set(release['files']))
        self.assertEqual(result['release_manifest_sha256'], sha256(target / 'release-manifest.json'))
        self.assertEqual(release['source_run']['logical_content_sha256'], logical_before)
        self.assertFalse(release['source_run']['database']['distributed'])
        attributions = (target / 'ATTRIBUTIONS.md').read_text(encoding='utf-8')
        self.assertIn('synthetic', attributions)
        self.assertIn('NKJP', (target / 'LIMITATIONS.md').read_text(encoding='utf-8'))
        self.assertTrue((target / 'reports/verification.json').is_file())
        self.assertEqual(load_json(run / 'manifest.json')['readiness'], 'FROZEN')
        # Odczyt zamrożonego przebiegu nie zmienia danych językowych.
        from literaki_slownik.explain import explain
        explain(run, 'kot', 'broad')
        with connect(run / 'build.sqlite', readonly=True) as db:
            self.assertEqual(logical_content_report(db)['sha256'], logical_before)
        self.assertFalse(os.access(target / 'LL-PL-BROAD.txt', os.W_OK))

    def test_existing_target_never_overwritten_even_empty(self):
        _, run, _ = self.verified()
        for target in (self.directory / 'empty', self.directory / 'full'):
            target.mkdir()
        (self.directory / 'full/sentinel').write_text('poprzedni pakiet', encoding='utf-8')
        self.refused(run, self.directory / 'empty', allow_test_fixture=True)
        self.refused(run, self.directory / 'full', allow_test_fixture=True)
        self.assertEqual(list((self.directory / 'empty').iterdir()), [])
        self.assertEqual((self.directory / 'full/sentinel').read_text(encoding='utf-8'), 'poprzedni pakiet')
        self.assertEqual(load_json(run / 'manifest.json')['readiness'], 'VERIFIED')

    def test_race_on_target_refused_and_staging_kept_marked(self):
        _, run, _ = self.verified()
        target = self.directory / 'race'
        original = export_module.write_release_manifest

        def racing(staging, data):
            original(staging, data)
            target.mkdir()
            (target / 'sentinel').write_text('inny proces', encoding='utf-8')

        with patch.object(export_module, 'write_release_manifest', racing):
            self.refused(run, target, allow_test_fixture=True)
        self.assertEqual([p.name for p in target.iterdir()], ['sentinel'])
        staging = [p for p in self.directory.iterdir() if p.name.startswith('.race.staging-')]
        self.assertEqual(len(staging), 1)
        self.assertEqual(load_json(run / 'manifest.json')['readiness'], 'VERIFIED')
        # Ponowienie do nowego celu nadal działa.
        self.assertEqual(export(run, self.directory / 'race-2', allow_test_fixture=True)['status'], 'FROZEN')

    def test_changes_after_verify_refused(self):
        changes = {
            'lista': lambda run, manifest: (run / 'lists/broad.txt').write_bytes(b'kot\n'),
            'kandydat': lambda run, manifest: next((run / 'verification').glob('attempt-*/candidate/LL-PL-BROAD.txt')).write_bytes(b'x\n'),
            'baza': lambda run, manifest: self.touch_database(run),
            'wejście': lambda run, manifest: (manifest.parent / 'lemma.csv.gz').write_bytes(b'x'),
            'manifest': lambda run, manifest: self.edit_run_manifest(run),
        }
        for index, (name, change) in enumerate(changes.items()):
            with self.subTest(name=name):
                directory = self.directory / str(index)
                directory.mkdir()
                manifest, run, peer, review = complete_pair(directory)
                self.assertEqual(verify(run, peer, review, allow_test_fixture=True)['verdict'], 'VERIFIED')
                change(run, manifest)
                self.assertIn('po verify', self.refused(run, directory / 'out', allow_test_fixture=True))
                self.assertFalse((directory / 'out').exists())

    def test_public_cli_refuses_fixture_export(self):
        _, run, _ = self.verified()
        cmd = [sys.executable, '-m', 'literaki_slownik', 'export', '--run-dir', str(run),
               '--output-dir', str(self.directory / 'cli-out'), '--json']
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 5, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'error')
        self.assertFalse((self.directory / 'cli-out').exists())

    def test_frozen_run_not_exported_again_and_previous_package_intact(self):
        _, run, _ = self.verified()
        first = self.directory / 'first'
        export(run, first, allow_test_fixture=True)
        before = tree_hashes(first)
        self.assertIn('FROZEN', self.refused(run, self.directory / 'second', allow_test_fixture=True))
        self.assertEqual(before, tree_hashes(first))

    def test_rename_noreplace_refuses_existing_directory(self):
        source, target = self.directory / 'source', self.directory / 'target'
        source.mkdir()
        target.mkdir()
        with self.assertRaises(FileExistsError):
            rename_noreplace(source, target)
        self.assertTrue(source.is_dir())
        rename_noreplace(source, self.directory / 'new')
        self.assertTrue((self.directory / 'new').is_dir())

    def touch_database(self, run):
        import sqlite3
        db = sqlite3.connect(run / 'build.sqlite')
        db.execute("update surface_form set nfc=nfc||'' ")
        db.execute('create table extra(x)')
        db.commit()
        db.close()

    def edit_run_manifest(self, run):
        from literaki_slownik.canonical import write_json
        manifest = load_json(run / 'manifest.json')
        manifest['inputs']['mode'] = 'production'
        write_json(run / 'manifest.json', manifest)


if __name__ == '__main__':
    unittest.main()
