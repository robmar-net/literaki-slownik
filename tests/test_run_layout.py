"""R1: przebieg na wolumenie roboczym (katalog + symlink w data/work) i nowe pola manifestu."""
import os
import shutil
from unittest import mock

from literaki_slownik import run as run_module
from literaki_slownik.build import build
from literaki_slownik.canonical import load_json, write_json
from literaki_slownik.explain import explain
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.run import STAGES
from tests.layout_helpers import LayoutCase


class RunLayoutTests(LayoutCase):
    def test_work_root_build_creates_directory_then_symlink_and_new_fields(self):
        link, target = self.work / 'r1', self.data / 'r1'
        real_symlink = os.symlink

        def symlink(source, destination, *args, **kwargs):
            # Symlink powstaje na końcu: po manifeście i reports/.
            self.assertTrue((target / 'manifest.json').is_file())
            self.assertTrue((target / 'reports').is_dir())
            return real_symlink(source, destination, *args, **kwargs)

        with mock.patch.object(run_module.os, 'symlink', side_effect=symlink) as spy:
            build(self.manifest, link, work_root=self.data)
        spy.assert_called_once()
        self.assertTrue(link.is_symlink())
        self.assertEqual(os.path.realpath(link), str(target))
        self.assertTrue((target / 'build.sqlite').is_file())
        manifest = load_json(target / 'manifest.json')
        self.assertEqual(manifest['work_volume'], {'marker_id': 'm-data'})
        self.assertEqual(manifest['resume'], {'resumed': False, 'count': 0})
        self.assertEqual(len(manifest['build_attempts']), 1)
        attempt = manifest['build_attempts'][0]
        self.assertEqual(set(attempt), {'attempt', 'started', 'ended', 'first_stage', 'last_stage',
                                        'outcome', 'exit_code'})
        self.assertEqual((attempt['attempt'], attempt['first_stage'], attempt['exit_code']), (1, 'preflight', 0))
        self.assertIn(attempt['outcome'], {'complete', 'incomplete'})
        self.assertIsNotNone(attempt['ended'])
        self.assertNotIn('m-data', str(manifest['stages']))

    def test_missing_or_unmarked_work_root_leaves_data_work_empty(self):
        unmarked = self.internal / 'Volumes' / 'Other'
        unmarked.mkdir()
        self.mounts.add(str(unmarked))
        for name, root, code in (('brak', self.data / 'missing', 75), ('bez-znacznika', unmarked, 76),
                                 ('dysk-repo', self.internal / 'inputs', 76)):
            with self.subTest(name):
                with self.assertRaises(GeneratorError) as caught:
                    build(self.manifest, self.work / name, work_root=root)
                self.assertEqual(caught.exception.code, code)
                self.assertEqual(list(self.work.iterdir()), [])
                self.assertFalse((root / name).exists())

    def test_leftover_of_failed_start_is_replaced_other_content_refused(self):
        leftover = self.data / 'r2'
        leftover.mkdir()
        (leftover / 'reports').mkdir()
        write_json(leftover / 'manifest.json', {'schema_version': 1, 'readiness': 'INCOMPLETE',
                                                'stages': {name: {'status': 'pending'} for name in STAGES}})
        build(self.manifest, self.work / 'r2', work_root=self.data)
        self.assertTrue((self.work / 'r2').is_symlink())
        self.assertEqual(load_json(leftover / 'manifest.json')['stages']['preflight']['status'], 'complete')
        for name, prepare in (
            ('baza', lambda path: (path / 'build.sqlite').write_bytes(b'')),
            ('etap', lambda path: write_json(path / 'manifest.json', {
                'stages': {**{n: {'status': 'pending'} for n in STAGES}, 'preflight': {'status': 'complete'}}})),
            ('obcy', lambda path: (path / 'notatka.txt').write_text('cudze')),
        ):
            with self.subTest(name):
                path = self.data / name
                path.mkdir()
                write_json(path / 'manifest.json', {'stages': {n: {'status': 'pending'} for n in STAGES}})
                prepare(path)
                before = sorted(p.name for p in path.iterdir())
                with self.assertRaises(GeneratorError) as caught:
                    build(self.manifest, self.work / name, work_root=self.data)
                self.assertEqual(caught.exception.code, 4)
                self.assertEqual(sorted(p.name for p in path.iterdir()), before)
                self.assertFalse(os.path.lexists(self.work / name))
        # Istniejący symlink przebiegu też nie jest nadpisywany.
        shutil.rmtree(self.data / 'baza')
        with self.assertRaises(GeneratorError) as caught:
            build(self.manifest, self.work / 'r2', work_root=self.data)
        self.assertEqual(caught.exception.code, 4)

    def test_internal_build_has_null_work_volume_and_explain_returns_statuses(self):
        run = self.work / 'r3'
        build(self.manifest, run)
        self.assertFalse(run.is_symlink())
        manifest = load_json(run / 'manifest.json')
        self.assertIsNone(manifest['work_volume'])
        self.assertEqual(manifest['resume'], {'resumed': False, 'count': 0})
        found = explain(run, 'kot', 'broad')
        self.assertEqual(found['stages'], {name: manifest['stages'][name]['status'] for name in STAGES})
        self.assertTrue(all(isinstance(status, str) for status in found['stages'].values()))
