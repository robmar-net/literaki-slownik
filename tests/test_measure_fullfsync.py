"""Skrypt pomiaru `fullfsync` (R8, ADR-020): JSON, reguła 4B/4C, quick_check tylko do odczytu."""
import hashlib
import io
import importlib.util
import json
import math
import shutil
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('measure_fullfsync', ROOT / 'scripts/measure_fullfsync.py')
measure = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(measure)

FAST = ['--commits', '3', '--repeats', '1', '--batch-rows', '10']
IMPORT_COUNTS = {'sgjp-x': {'records': 25001, 'lexemes': 9}, 'kwjp-x': {'records': 10000, 'sum_freq': 7}}
DECISIONS = {'analyses': 30000, 'construction_analyses': 1, 'new_analyses': 30000, 'variant_decisions': 60000}


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _strings(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, str):
        yield value


class MeasureFullfsyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.dir = self.root / 'measure'

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = measure.main(['--dir', str(self.dir), *FAST, *args])
        return code, out.getvalue(), err.getvalue()

    def reference_run(self):
        run = self.root / 'lists-ref'
        (run / 'reports').mkdir(parents=True)
        (run / 'reports/import-counts.json').write_text(json.dumps(IMPORT_COUNTS), encoding='utf-8')
        (run / 'reports/decisions.json').write_text(json.dumps(DECISIONS), encoding='utf-8')
        return run

    def test_both_variants_reported(self):
        code, out, _ = self.run_script()
        self.assertEqual(code, 0)
        result = json.loads(out)
        for variant in ('fullfsync_off', 'fullfsync_on'):
            self.assertEqual(result[variant]['commits'], 3)
            self.assertGreater(result[variant]['median_commit_seconds'], 0)
        self.assertEqual(result['fullfsync_off']['pragmas'], {'fullfsync': 0, 'journal_mode': 'delete', 'synchronous': 2})
        self.assertEqual(result['fullfsync_on']['pragmas']['fullfsync'], 1)

    def test_reference_run_gives_commits_overhead_and_choice(self):
        code, out, _ = self.run_script('--reference-run', str(self.reference_run()))
        self.assertEqual(code, 0)
        result = json.loads(out)
        # Każde źródło i każdy rodzaj analiz to osobne partie po 10 000, w górę; plus commity etapów.
        expected = 3 + 1 + 3 + 1 + measure.STAGE_COMMITS
        self.assertEqual(result['build_commits'], expected)
        delta = result['fullfsync_on']['median_commit_seconds'] - result['fullfsync_off']['median_commit_seconds']
        self.assertAlmostEqual(result['overhead_pct'], delta * expected / 46800 * 100, places=9)
        self.assertEqual(result['choice'], 'build' if result['overhead_pct'] <= 5 else 'stage_boundaries')
        self.assertEqual(measure.choose(5.0), 'build')
        self.assertEqual(measure.choose(5.0001), 'stage_boundaries')

    def test_quick_check_reads_copy_without_changing_it(self):
        source = self.root / 'src.sqlite'
        db = sqlite3.connect(source)
        db.execute('create table t(x integer primary key, y text)')
        db.executemany('insert into t(y) values (?)', [(str(i),) for i in range(100)])
        db.commit()
        db.close()
        copy = self.root / 'copy.sqlite'
        shutil.copy2(source, copy)
        copy.chmod(0o444)
        before = (_digest(copy), copy.stat().st_mtime_ns)
        code, out, _ = self.run_script('--quick-check', str(copy))
        self.assertEqual(code, 0)
        check = json.loads(out)['quick_check']
        self.assertEqual(check['result'], 'ok')
        self.assertGreaterEqual(check['seconds'], 0)
        self.assertEqual((_digest(copy), copy.stat().st_mtime_ns), before)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['copy.sqlite', 'src.sqlite'])

    def test_no_absolute_paths_and_dir_removed(self):
        code, out, _ = self.run_script('--reference-run', str(self.reference_run()))
        self.assertEqual(code, 0)
        self.assertFalse(self.dir.exists())
        self.assertNotIn(self.tmp.name, out)
        self.assertNotIn(str(Path.home()), out)
        for text in _strings(json.loads(out)):
            self.assertFalse(text.startswith('/'), text)
        self.assertEqual(json.loads(out)['reference_run']['name'], 'lists-ref')

    def test_existing_dir_refused_and_left_alone(self):
        self.dir.mkdir()
        keep = self.dir / 'keep.txt'
        keep.write_text('x', encoding='utf-8')
        code, out, err = self.run_script()
        self.assertNotEqual(code, 0)
        self.assertEqual(out, '')
        self.assertIn('istnieje', err)
        self.assertEqual(keep.read_text(encoding='utf-8'), 'x')
        self.assertEqual([p.name for p in self.dir.iterdir()], ['keep.txt'])


if __name__ == '__main__':
    unittest.main()
