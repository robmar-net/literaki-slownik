"""Explain dla POP/POP0 (C16): powód obecności lub braku słowa, bez liczb NKJP i bez zapisu."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from literaki_slownik import decisions
from literaki_slownik.canonical import load_json, sha256
from literaki_slownik.explain import explain_pop, format_pop_explanation
from literaki_slownik.inputs import GeneratorError
from tests import pop_helpers
from tests.pop_helpers import NKJP_POP_1GRAMS, pop_package

# Leksem `odra` ma analizę nazwy własnej, a `odry` bez oznaczenia trafia do STANDARD (D9: poza rankingiem).
PROPER_SGJP = 'Odra\todra\tsubst:sg:nom:f\tnazwa_geograficzna\t\nodry\todra\tsubst:pl:nom:f\t\t\n'
# Krótkie liczby (12, 41, 317) trafiają przypadkiem w hashe; rzadkie siedmiocyfrowe wykrywają wyciek F.
NKJP_COUNTS = [c for c in (line.split()[0] for line in NKJP_POP_1GRAMS.splitlines()) if len(c) >= 6]


class ExplainPopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.fixture = pop_package(Path(cls.temp.name) / 'base')
        cls.run_dir, cls.package = cls.fixture['run'], cls.fixture['package']
        cls.frozen = {p: sha256(p) for p in (cls.run_dir / 'build.sqlite', cls.run_dir / 'manifest.json',
                                             cls.fixture['release'] / 'release-manifest.json')}

    @classmethod
    def tearDownClass(cls):
        for root, dirs, files in os.walk(cls.temp.name):
            for name in dirs + files:
                os.chmod(os.path.join(root, name), 0o755)
        cls.temp.cleanup()

    def explain(self, word, variant='pop0', package=None):
        return explain_pop(package or self.package, self.run_dir, word, variant)

    def test_reasons_for_each_case(self):
        cases = [('kot', 'pop0', 'IN_POP0'), ('fajny', 'pop', 'IN_POP'), ('fajny', 'pop0', 'BELOW_THRESHOLD'),
                 ('zamek', 'pop', 'BELOW_THRESHOLD'), ('kumpel', 'pop', 'NO_DATA'),
                 ('xyzzy', 'pop', 'NOT_IN_STANDARD'), ('Polska', 'pop0', 'IN_POP0'),
                 ('lato', 'pop0', 'PRUNED_WEAK_MEMBER'), ('lato', 'pop', 'IN_POP')]
        for word, variant, reason in cases:
            with self.subTest(word=word, variant=variant):
                value = self.explain(word, variant)
                self.assertEqual(value['reason'], reason)
                self.assertEqual(value['in_list'], reason.startswith('IN_'))
        self.assertFalse(self.explain('xyzzy', 'pop')['in_standard'])
        self.assertEqual(self.explain('fajny', 'pop0')['lists'], {'pop': True, 'pop0': False})
        # D9: leksem z nazwą własną nie ma jednostki ani rangi; forma jest w STANDARD.
        directory = Path(self.temp.name) / 'proper'
        with mock.patch.object(pop_helpers, 'POP_SGJP', pop_helpers.POP_SGJP + PROPER_SGJP):
            proper = pop_package(directory)
        value = explain_pop(proper['package'], proper['run'], 'odry', 'pop')
        self.assertTrue(value['in_standard'])
        self.assertEqual(value['reason'], 'PROPER_NAME_ONLY')
        self.assertEqual(value['lexemes'], [{'lexeme': 'odra@synthetic', 'proper_name': True, 'unit': None}])

    def test_pruned_member_explains_own_rank_and_unit_in_list(self):
        # `lato`: jednostka lato+rok jest w POP0, ale własna ranga `lato` (6) jest pod progiem POP0 (4).
        value = self.explain('lato', 'pop0')
        self.assertEqual(value['reason'], 'PRUNED_WEAK_MEMBER')
        unit, = value['units']
        self.assertEqual(unit['list'], 'POP0')
        self.assertNotIn('lato@synthetic', unit['members_in']['POP0'])
        self.assertEqual(unit['member_ranks']['lato@synthetic'], 6)
        text = format_pop_explanation(value)
        self.assertIn('PRUNED_WEAK_MEMBER', text)
        self.assertIn('członkowie w POP0: rok:S1@synthetic, rok:S2@synthetic', text)
        self.assertIn('lato@synthetic 6', text)

    def test_construction_form_reports_component_lexeme(self):
        # Forma konstrukcji nie ma własnej interpretacji: leksem przychodzi przez składnik (jak `pop`).
        below = self.explain('niefajny', 'pop0')
        self.assertEqual(below['reason'], 'BELOW_THRESHOLD')
        self.assertTrue(below['in_standard'])
        self.assertEqual(below['lists'], {'pop': True, 'pop0': False})
        self.assertEqual(below['lexemes'], [{'lexeme': 'fajny@synthetic', 'proper_name': False, 'unit': 0}])
        self.assertEqual(below['units'][0]['members'], ['fajny@synthetic'])
        inside = self.explain('niepolski', 'pop0')
        self.assertEqual(inside['reason'], 'IN_POP0')
        self.assertEqual([item['lexeme'] for item in inside['lexemes']], ['polski@synthetic'])

    def test_ul_rank_ignores_ul_dot_mass(self):
        # D4 strip-edges-keep-dot: `ul.` (9 182 736) nie wlicza się do `ul` (41 207).
        value = self.explain('ul', 'pop')
        self.assertEqual(value['reason'], 'BELOW_THRESHOLD')
        unit, = value['units']
        self.assertEqual((unit['members'], unit['nkjp_status'], unit['nkjp_rank'], unit['rank']),
                         (['ul@synthetic'], 'OBSERVED', 7, 8))
        self.assertEqual(self.explain('ul.', 'pop')['reason'], 'NOT_IN_STANDARD')

    def test_result_shows_lexemes_units_threshold_and_no_nkjp_counts(self):
        value = self.explain('lata', 'pop0')
        self.assertEqual(value['reason'], 'IN_POP0')
        self.assertTrue(value['in_standard'])
        self.assertEqual({item['lexeme'] for item in value['lexemes']},
                         {'rok:S1@synthetic', 'lato@synthetic'})
        unit, = value['units']
        self.assertEqual(unit['members'], ['lato@synthetic', 'rok:S1@synthetic', 'rok:S2@synthetic'])
        self.assertEqual((unit['rank'], unit['status'], unit['list'], unit['nkjp_rank']), (3, 'MEASURED', 'POP0', 3))
        for key in ('percentile', 'flags', 'confidence', 'kwjp_status', 'kwjp_percentile', 'nkjp_percentile',
                    'nkjp_status'):
            self.assertIn(key, unit)
        # C14: miara łączy F NKJP (log-ipm), więc explain podaje rangę i percentyl łączny, nie wartość.
        self.assertNotIn('value', unit)
        self.assertIn(f"percentyl {unit['percentile']}", format_pop_explanation(value))
        self.assertNotIn('miara:', format_pop_explanation(value))
        self.assertEqual(value['threshold']['rank'], 4)
        self.assertEqual(value['threshold']['limit'], 6)
        zamek = self.explain('zamek', 'pop')
        self.assertEqual(zamek['units'][0]['flags'], ['ambiguous:nkjp'])  # `zamek` 12 w NKJP: bez flag braków
        text = json.dumps(value, ensure_ascii=False) + format_pop_explanation(value) + format_pop_explanation(zamek)
        for count in NKJP_COUNTS:
            self.assertNotIn(count, text)
        self.assertIn('IN_POP0', format_pop_explanation(value))

    def test_kwjp_only_package_explains_without_nkjp(self):
        # C19: pakiet bez NKJP; explain działa, a jednostki i tekst nie mają pól NKJP.
        made = pop_package(Path(self.temp.name) / 'kwjp-only', pop=11, pop0=6,
                           d3={'source': 'kwjp', 'field': 'F'}, d4=None, must_include_pop0=['rok'])
        value = explain_pop(made['package'], made['run'], 'lata', 'pop0')
        self.assertEqual(value['reason'], 'IN_POP0')
        self.assertTrue(value['units'])
        for row in value['units']:
            self.assertFalse([key for key in row if 'nkjp' in key])
        self.assertNotIn('NKJP', format_pop_explanation(value))

    def test_package_pins_must_match_run(self):
        for field in ('database_sha256', 'release_manifest_sha256', 'standard_sha256'):
            with self.subTest(field=field):
                copy = Path(self.temp.name) / f'pins-{field}'
                shutil.copytree(self.package, copy)
                path = copy / 'release-manifest.json'
                path.chmod(0o644)
                manifest = load_json(path)
                manifest['inputs'][field] = '0' * 64
                path.write_text(json.dumps(manifest), encoding='utf-8')
                with self.assertRaises(GeneratorError) as caught:
                    self.explain('kot', 'pop0', copy)
                self.assertEqual(caught.exception.code, 3)
        with self.assertRaises(GeneratorError) as caught:
            self.explain('kot', 'broad')
        self.assertEqual(caught.exception.code, 2)

    def test_read_only_and_variants_unchanged(self):
        package_before = {p: sha256(p) for p in self.package.rglob('*') if p.is_file()}
        for word in ('kot', 'duży', 'xyzzy'):
            self.explain(word, 'pop')
        self.assertEqual({p: sha256(p) for p in self.frozen}, self.frozen)
        self.assertEqual({p: sha256(p) for p in self.package.rglob('*') if p.is_file()}, package_before)
        self.assertEqual(decisions.VARIANTS, ('broad', 'standard'))

    def test_cli_text_json_and_missing_pop_dir(self):
        cmd = [sys.executable, '-m', 'literaki_slownik', 'explain', '--variant', 'pop0', '--pop-dir',
               str(self.package), '--run-dir', str(self.run_dir), '--word', 'kot']
        result = subprocess.run(cmd + ['--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['result']['reason'], 'IN_POP0')
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('IN_POP0', result.stdout)
        self.assertIn('kot@synthetic', result.stdout)
        result = subprocess.run([sys.executable, '-m', 'literaki_slownik', 'explain', '--variant', 'pop',
                                 '--run-dir', str(self.run_dir), '--word', 'kot', '--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'error')
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
