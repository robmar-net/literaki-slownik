import csv
import gzip
import tempfile
import unittest
from pathlib import Path
from literaki_slownik.kwjp import rows, COLUMNS
from literaki_slownik.inputs import GeneratorError


class KwjpTests(unittest.TestCase):
    def source(self, directory, kind, data):
        p = Path(directory) / 'renamed.gz'
        columns = COLUMNS[kind]
        with gzip.open(p, 'wt', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow([''] * (len(columns) - 7 - ('Dice' in columns)) + [c for c in columns if c not in {'lemma', 'pos', 'form', 'unit_1', 'unit_2'}])
            writer.writerow(data)
        return p

    def test_declared_type_not_filename_and_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.source(directory, 'kwjp_lemma', ['kot', 'subst', '1.0', '0.1', '1', '1', '1.00013', '0', '5.0'])
            number, raw, typed = next(rows(p, 'kwjp_lemma'))
            self.assertEqual(typed['freq'], 1)
            self.assertEqual(raw['DP_norm'], '1.00013')
            self.assertEqual(typed['1-DP'], '0')
            self.assertEqual(number, 1)

    def test_bigram_two_empty_headers(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.source(directory, 'kwjp_bigram', ['kot', 'w', '5', '1', '2', '0.5', '0.5', '0.5', '0', '5'])
            _, raw, typed = next(rows(p, 'kwjp_bigram'))
            self.assertEqual(raw['unit_1'], 'kot')
            self.assertEqual(raw['unit_2'], 'w')
            self.assertIn('Dice', typed)

    def test_nan_fractional_count_and_bad_width_rejected(self):
        for value in ['NaN', 'Infinity', '1.5', '-1']:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                p = self.source(directory, 'kwjp_orth', ['kot', value, '1', '2', '0.5', '0.5', '0.5', '5'])
                with self.assertRaises(GeneratorError):
                    list(rows(p, 'kwjp_orth'))
