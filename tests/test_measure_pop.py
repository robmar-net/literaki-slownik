"""Skrypt pomiaru POP (etap A, A1–A10): dym na fiksturze POP."""
import importlib.util
import io
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch
from literaki_slownik.canonical import load_json, sha256
from tests.pop_helpers import gz_write, pop_fixture, write_pop_sources

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('measure_pop', ROOT / 'scripts/measure_pop.py')
measure_pop = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(measure_pop)

# Liczby NKJP per forma dobrane tak, żeby nie wystąpiły w raporcie przypadkiem (C14, A10).
NKJP_COUNTS = {'ul.': 50013, 'ul': 10007, 'ok.': 30011, 'polska': 40009, 'Polska': 15013, 'lata': 25013,
               'rok': 20011, 'duży': 8017, 'fajny': 1009}
# Formy po scaleniu: `ul` + `ul.` (strip-edges) i `polska` + `Polska` (małe litery).
PER_FORM = sorted({*NKJP_COUNTS.values(), 10007 + 50013, 40009 + 15013})


def _grouped(number):
    return f'{number:,}'.replace(',', ' ')


class MeasurePopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        cls.fixture = f = pop_fixture(root / 'pop')
        lines = ''.join(f'{count:>8} {text}\n' for text, count in NKJP_COUNTS.items())
        nkjp = gz_write(root / '1grams-distinct.gz', lines)
        cls.sources = write_pop_sources(root / 'pop-sources.json', f['run'], f['release'], nkjp)
        cls.before = sha256(f['database'])
        cls.out = root / 'out'
        cls.out.mkdir()
        cls.codes = [cls.measure(cls.out / name) for name in ('a', 'b')]
        cls.after = sha256(f['database'])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def measure(cls, output, sources=None):
        f = cls.fixture
        stderr = io.StringIO()
        with redirect_stderr(stderr), redirect_stdout(io.StringIO()):
            code = measure_pop.main(['--sources', str(sources or cls.sources), '--run-dir', str(f['run']),
                                     '--release-dir', str(f['release']), '--output-dir', str(output)])
        cls.stderr = stderr.getvalue()
        return code

    def test_two_runs_give_byte_equal_measure_json(self):
        self.assertEqual(self.codes, [0, 0])
        a, b = (self.out / name / 'measure.json' for name in ('a', 'b'))
        self.assertEqual(a.read_bytes(), b.read_bytes())
        data = load_json(a)
        self.assertEqual(data['version'], 'pop-measure-v1')
        self.assertEqual(set(data['code_identity']), {'tree_sha256', 'git_commit', 'git_dirty'})
        self.assertEqual(data['inputs']['pop_sources_sha256'], sha256(self.sources))
        self.assertRegex(data['options_sha256'], '^[0-9a-f]{64}$')
        text = a.read_text(encoding='utf-8')
        # Bez ścieżek i czasów: czasy są w osobnym timing.json.
        self.assertNotIn(self.tmp.name, text)
        self.assertNotIn('seconds', text)
        self.assertIn('seconds', (self.out / 'a' / 'timing.json').read_text(encoding='utf-8'))
        self.assertEqual(sorted(p.name for p in (self.out / 'a').iterdir()),
                         ['measure.json', 'report.md', 'timing.json'])

    def test_existing_output_directory_is_code_4(self):
        target = self.out / 'a'
        before = sorted(p.name for p in self.out.iterdir())
        self.assertEqual(self.measure(target), 4)
        self.assertEqual(sorted(p.name for p in self.out.iterdir()), before)
        self.assertEqual(load_json(target / 'measure.json'), load_json(self.out / 'b' / 'measure.json'))

    def test_wrong_pin_is_code_3_and_nothing_written(self):
        f = self.fixture
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            bad = write_pop_sources(folder / 'pop-sources.json', f['run'], f['release'], f['nkjp'],
                                    standard_sha256='0' * 64)
            self.assertEqual(self.measure(folder / 'out', bad), 3)
            self.assertEqual(sorted(p.name for p in folder.iterdir()), ['pop-sources.json'])
            self.assertIn('kod 3', self.stderr)

    def test_database_hash_before_equals_after_else_code_5(self):
        self.assertEqual(self.before, self.after)
        data = load_json(self.out / 'a' / 'measure.json')
        self.assertEqual(data['database']['sha256_before'], self.before)
        self.assertEqual(data['database']['sha256_after'], self.before)
        # Zmiana bazy w trakcie pomiaru: kod 5 i nic nie trafia na dysk.
        # Hash „przed” liczy check_inputs; skrypt liczy „po” raz, na końcu.
        calls = []

        def drifting(path):
            calls.append(path)
            return 'f' * 64
        with tempfile.TemporaryDirectory() as folder, patch.object(measure_pop, 'database_sha256', drifting):
            folder = Path(folder)
            self.assertEqual(self.measure(folder / 'out'), 5)
            self.assertEqual(list(folder.iterdir()), [])
        self.assertEqual(len(calls), 1)

    def test_report_has_sections_d1_to_d8_a9_and_samples(self):
        report = (self.out / 'a' / 'report.md').read_text(encoding='utf-8')
        for heading in ('## TL;DR', *(f'## D{n}' for n in range(1, 9)), '## A9', '## Próbki'):
            self.assertRegex(report, rf'(?m)^{re.escape(heading)}\b', heading)
        self.assertEqual(report.count('**Zalecenie'), 8)
        self.assertIn('ilustracja', report)
        for word in ('rok', 'lata', 'lato', 'polska', 'polski', 'zamek'):
            self.assertIn(f'`{word}`', report)
        # Reguła (ii) bez flagi nie jest mierzona.
        self.assertIn('nie mierzono w tym przebiegu', report)
        data = load_json(self.out / 'a' / 'measure.json')
        self.assertEqual(data['samples']['version'], 'pop-quality-v1')
        self.assertEqual(data['samples']['status'], 'UNREVIEWED')
        self.assertTrue(data['samples']['strata'])

    def test_report_has_no_nkjp_counts_per_form(self):
        report = (self.out / 'a' / 'report.md').read_text(encoding='utf-8')
        measured = (self.out / 'a' / 'measure.json').read_text(encoding='utf-8')
        for number in PER_FORM:
            for shape in {str(number), _grouped(number)}:
                self.assertNotIn(shape, report, number)
        # Liczby per forma są tylko w measure.json (kolizje czyszczenia D4).
        self.assertIn('50013', measured)
        self.assertIn('"ul."', measured)


if __name__ == '__main__':
    unittest.main()
