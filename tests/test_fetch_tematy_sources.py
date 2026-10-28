"""Pobranie źródeł TEMATY (#11, W1): bez sieci, przez `file://`."""
import importlib.util
import os
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('fetch_tematy_sources', ROOT / 'scripts/fetch_tematy_sources.py')
fetch_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetch_module)


class FetchTematySourcesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / 'zrodlo' / 'IATE_export.zip'
        self.source.parent.mkdir()
        with zipfile.ZipFile(self.source, 'w') as archive:
            archive.writestr('IATE_export_26022019.tbx', '<martif/>')
        self.target_dir = self.root / 'cache' / 'iate'
        self.target_dir.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_record_and_no_overwrite(self):
        target = self.target_dir / 'IATE_download.zip'
        record = fetch_module.fetch(self.source.as_uri(), target, iate=True)
        self.assertEqual({'url', 'retrieved_at', 'sha256', 'bytes', 'path', 'last_modified', 'member'}, set(record))
        self.assertEqual(self.source.read_bytes(), target.read_bytes())
        self.assertEqual(fetch_module.sha256_file(self.source), record['sha256'])
        self.assertEqual(self.source.stat().st_size, record['bytes'])
        self.assertEqual(str(target), record['path'])
        self.assertEqual('IATE_export_26022019.tbx', record['member'])
        self.assertTrue(record['last_modified'])
        self.assertTrue(record['retrieved_at'].endswith('Z'))
        before = target.read_bytes()
        with self.assertRaises(fetch_module.FetchError):
            fetch_module.fetch(self.source.as_uri(), target, iate=True)
        self.assertEqual(before, target.read_bytes())
        self.assertEqual(['IATE_download.zip'], os.listdir(self.target_dir))

    def test_plwordnet_wrong_hash_leaves_nothing(self):
        target = self.target_dir / 'wordnet_work_4_5.zip'
        with self.assertRaises(fetch_module.FetchError) as caught:
            fetch_module.fetch(self.source.as_uri(), target, expected_sha256=fetch_module.PLWORDNET_SHA256)
        self.assertIn('SHA-256', str(caught.exception))
        self.assertFalse(target.exists())
        self.assertEqual([], os.listdir(self.target_dir))


if __name__ == '__main__':
    unittest.main()
