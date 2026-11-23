"""Strażnik wolumenu (G1/G2/G3, miejsce) i init_work_volume.py, bez prawdziwego dysku."""
import contextlib
import importlib.util
import io
import json
import os
import plistlib
import subprocess
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from literaki_slownik import canonical, volume
from literaki_slownik.inputs import GeneratorError

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'init_work_volume.py'
FAKE_UUID = '00000000-0000-0000-0000-00000000FAKE'
GB = 10 ** 9


def load_script():
    spec = importlib.util.spec_from_file_location('init_work_volume', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VolumeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        base = Path(os.path.realpath(self.directory.name))
        # Fikcyjny układ: dysk systemowy (z repo i „/Volumes”) i dwa zamontowane wolumeny.
        self.internal, self.volumes = base, base / 'Volumes'
        self.repo, self.data, self.data1 = self.internal / 'repo', self.volumes / 'Data', self.volumes / 'Data 1'
        for path in (self.repo / 'data' / 'work', self.data, self.data1):
            path.mkdir(parents=True)
        self.mounts = {str(self.internal), str(self.data), str(self.data1)}
        real_ismount = os.path.ismount
        self.free = 500 * GB
        patches = [
            mock.patch.object(volume, 'REPO_ROOT', self.repo),
            mock.patch('os.path.ismount', lambda path: os.path.realpath(path) in self.mounts
                       or (os.path.realpath(path) == '/' and real_ismount('/'))),
            mock.patch('os.statvfs', lambda path: types.SimpleNamespace(f_bavail=self.free, f_frsize=1)),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.addCleanup(volume.deactivate)
        self.addCleanup(self.directory.cleanup)

    def mark(self, root, marker_id='m-data'):
        canonical.write_json(root / volume.MARKER, {'schema_version': 1, 'marker_id': marker_id,
                                                    'volume_uuid': FAKE_UUID})

    def assertCode(self, code, function, *args, **kwargs):
        with self.assertRaises(GeneratorError) as caught:
            function(*args, **kwargs)
        self.assertEqual(code, caught.exception.code, str(caught.exception))

    def test_fresh_without_work_root_internal_passes_external_unmarked_76(self):
        self.assertIsNone(volume.check_fresh(self.repo / 'data' / 'work' / 'run-a'))
        self.assertCode(76, volume.check_fresh, self.data / 'run-a')
        self.mark(self.data)
        self.assertEqual({'marker_id': 'm-data'}, volume.check_fresh(self.data / 'run-a'))

    def test_fresh_with_work_root_needs_marker_and_space(self):
        self.assertCode(75, volume.check_fresh, self.data / 'brak' / 'run-a', work_root=self.data / 'brak')
        self.assertCode(76, volume.check_fresh, self.internal / 'run-a', work_root=self.internal)
        self.assertCode(76, volume.check_fresh, self.data / 'run-a', work_root=self.data)
        self.mark(self.data)
        self.assertEqual({'marker_id': 'm-data'}, volume.check_fresh(self.data / 'run-a', work_root=self.data))
        self.free = 50 * GB - 1
        self.assertCode(78, volume.check_fresh, self.data / 'run-a', work_root=self.data)
        self.free = 50 * GB
        self.assertEqual({'marker_id': 'm-data'}, volume.check_fresh(self.data / 'run-a', work_root=self.data))
        self.free = 99 * GB
        self.assertCode(78, volume.check_space, self.data, volume.MIN_FREE_PAIR)

    def test_check_work_root_is_one_contract_75_76_78(self):
        self.assertCode(75, volume.check_work_root, self.data / 'brak')
        self.assertCode(76, volume.check_work_root, self.repo / 'data' / 'work')  # dysk repo
        self.assertCode(76, volume.check_work_root, self.data)  # bez znacznika
        self.assertEqual((self.data, None), volume.check_work_root(self.data, marker=False))
        self.mark(self.data)
        (self.data / 'literaki-slownik' / 'work').mkdir(parents=True)
        mount, marker = volume.check_work_root(self.data / 'literaki-slownik' / 'work')
        self.assertEqual((mount, marker['marker_id']), (self.data, 'm-data'))
        self.free = 99 * GB
        self.assertCode(78, volume.check_work_root, self.data, volume.MIN_FREE_PAIR)
        self.assertEqual(self.data, volume.check_work_root(self.data)[0])  # bez progu nie liczy miejsca

    def test_build_pair_check_uses_the_shared_contract(self):
        script = (Path(__file__).resolve().parents[1] / 'scripts' / 'build_pair.sh').read_text(encoding='utf-8')
        self.assertIn('volume.check_work_root(', script)
        self.assertIn('MIN_FREE_PAIR', script)

    def test_resume_unmounted_volume_or_dangling_symlink_75(self):
        link = self.repo / 'data' / 'work' / 'run-a'
        # Wolumen niezamontowany: w „/Volumes” został pusty katalog na dysku systemowym.
        self.mounts.discard(str(self.data))
        (self.data / 'run-a').mkdir()
        link.symlink_to(self.data / 'run-a')
        self.assertCode(75, volume.check_mounted, link)
        self.assertCode(75, volume.check_resume, link, 'm-data')
        link.unlink()
        link.symlink_to(self.data1 / 'brak')
        self.assertCode(75, volume.check_mounted, link)

    def test_resume_marker_rules(self):
        link = self.repo / 'data' / 'work' / 'run-a'
        (self.data / 'run-a').mkdir()
        link.symlink_to(self.data / 'run-a')
        self.assertCode(76, volume.check_resume, link, 'm-data')  # brak znacznika
        self.mark(self.data, 'm-inny')
        self.assertCode(76, volume.check_resume, link, 'm-data')
        self.assertCode(76, volume.check_resume, link, None)  # manifest null, a przebieg na wolumenie
        self.mark(self.data, 'm-data')
        self.assertEqual({'marker_id': 'm-data'}, volume.check_resume(link, 'm-data'))
        self.free = GB
        self.assertCode(78, volume.check_resume, link, 'm-data')
        internal = self.repo / 'data' / 'work' / 'run-b'
        internal.mkdir()
        self.assertIsNone(volume.check_resume(internal, None))

    def test_g3_st_dev_change_75(self):
        run = self.data / 'run-a'
        run.mkdir()
        volume.activate(run)
        volume.check_active()
        real_stat = os.stat
        changed = lambda path, *a, **k: (types.SimpleNamespace(st_dev=real_stat(path).st_dev + 1)
                                         if os.path.realpath(path) == str(run) else real_stat(path, *a, **k))
        with mock.patch('os.stat', changed):
            self.assertCode(75, volume.check_active)
        volume.deactivate()
        with mock.patch('os.stat', changed):
            volume.check_active()  # bez aktywnego przebiegu nie ma czego pilnować

    def test_replace_guard_keeps_old_file_and_ignores_other_targets(self):
        run = self.data / 'run-a'
        (run / 'reports').mkdir(parents=True)
        volume.activate(run)
        target, outside = run / 'reports' / 'r.json', self.internal / 'poza.json'
        canonical.write_json(target, {'v': 1})
        real_stat = os.stat
        changed = lambda path, *a, **k: (types.SimpleNamespace(st_dev=real_stat(path).st_dev + 1)
                                         if os.path.realpath(path) == str(run) else real_stat(path, *a, **k))
        with mock.patch('os.stat', changed):
            self.assertCode(75, canonical.write_json, target, {'v': 2})
            canonical.write_json(outside, {'v': 3})
        self.assertEqual({'v': 1}, canonical.load_json(target))
        self.assertEqual(['r.json'], os.listdir(run / 'reports'))
        self.assertEqual({'v': 3}, canonical.load_json(outside))
        volume.deactivate()
        self.assertIsNone(canonical.set_replace_guard(None))

    def test_find_by_marker_under_other_path(self):
        self.mark(self.data1, 'm-data')
        (self.volumes / 'pusty').mkdir()
        self.mark(self.volumes / 'pusty', 'm-pusty')  # nie jest punktem montowania
        self.assertEqual(self.data1, volume.find_by_marker('m-data', self.volumes))
        self.assertIsNone(volume.find_by_marker('m-pusty', self.volumes))
        self.assertIsNone(volume.find_by_marker('m-brak', self.volumes))

    def test_init_work_volume_once_and_never_on_repo_disk(self):
        script = load_script()
        plist = plistlib.dumps({'VolumeUUID': FAKE_UUID, 'MountPoint': str(self.data)})
        calls = []

        def run(command, **kwargs):
            calls.append(command)
            return subprocess.CompletedProcess(command, 0, stdout=plist, stderr=b'')

        def invoke(root):
            out, err = io.StringIO(), io.StringIO()
            with mock.patch('subprocess.run', run), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = script.main([str(root)])
            return code, out.getvalue(), err.getvalue()

        code, out, _ = invoke(self.data)
        self.assertEqual(0, code)
        printed = json.loads(out)
        self.assertEqual(['marker_id'], list(printed))
        self.assertNotIn(FAKE_UUID, out)
        marker = canonical.load_json(self.data / volume.MARKER)
        self.assertEqual((printed['marker_id'], FAKE_UUID), (marker['marker_id'], marker['volume_uuid']))
        self.assertEqual(['diskutil', 'info', '-plist', str(self.data)], calls[0])
        before = (self.data / volume.MARKER).read_bytes()
        code, out, err = invoke(self.data)
        self.assertNotEqual(0, code)
        self.assertEqual('', out)
        self.assertTrue(err)
        self.assertEqual(before, (self.data / volume.MARKER).read_bytes())
        code, _, _ = invoke(self.internal)
        self.assertEqual(76, code)
        self.assertFalse((self.internal / volume.MARKER).exists())


if __name__ == '__main__':
    unittest.main()
