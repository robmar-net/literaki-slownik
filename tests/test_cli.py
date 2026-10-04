import json
import subprocess
import sys
import tempfile
import unittest
from tests.helpers import fixture_manifest, rewrite


class CliTests(unittest.TestCase):
    def test_inspect_json_and_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path, manifest = fixture_manifest(directory)
            cmd = [sys.executable, '-m', 'literaki_slownik', 'inspect-sources', '--manifest', str(path), '--json']
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], 'ok')
            manifest['artifacts'][0]['status'] = 'BLOCKED'
            rewrite(path, manifest)
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 3)
            self.assertEqual(json.loads(result.stdout)['status'], 'error')
            self.assertTrue(result.stderr)

    def test_help_and_missing_argument(self):
        result = subprocess.run([sys.executable, '-m', 'literaki_slownik', '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('inspect-sources', result.stdout)
        result = subprocess.run([sys.executable, '-m', 'literaki_slownik', 'inspect-sources', '--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'error')
