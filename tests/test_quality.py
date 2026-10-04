"""Próbka jakości jest odtwarzalna i nie stanowi werdyktu językowego."""
import unittest
from unittest.mock import patch

from literaki_slownik.canonical import load_json
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.quality import sample_strata, sampling_digest, review_template


class QualityTests(unittest.TestCase):
    def setUp(self):
        self.config = load_json('config/generator/quality.json')

    def test_utf8_canonical_encoding_known_digest(self):
        self.assertEqual(sampling_digest(self.config['seed'], 'krótkie', 'ąę'),
                         '1df9886d041a162a42789bde80cd56c662d3948408f6429c5d4f4217d20f2be3')

    def test_stable_mapping_order_duplicates_and_limit(self):
        keys = [f'word:{n:04}' for n in range(1000)]
        first = sample_strata({'b': iter(keys), 'a': iter(['a', 'a', 'b'])}, self.config)
        second = sample_strata({'a': iter(['a', 'b']), 'b': iter(keys)}, self.config)
        self.assertEqual(first, second)
        self.assertEqual(first['strata']['a']['population'], 2)
        self.assertEqual(first['strata']['b']['population'], 1000)
        self.assertEqual(first['strata']['b']['sample_size'], 30)
        selected = first['strata']['b']['selected']
        self.assertEqual(selected, sorted(selected, key=lambda item: (item['sha256'], item['key'])))
        remaining = set(keys) - {item['key'] for item in selected}
        self.assertTrue(all(sampling_digest(self.config['seed'], 'b', key) >= selected[-1]['sha256']
                            for key in remaining))

    def test_empty_and_small_strata_and_overlap(self):
        result = sample_strata({'empty': [], 'one': ['a'], 'two': ['a', 'b']}, self.config)
        self.assertEqual(result['strata']['empty']['coverage'], 'EMPTY_NOT_COVERAGE')
        self.assertEqual(result['strata']['empty']['sample_size'], 0)
        self.assertEqual(result['strata']['two']['sample_size'], 2)
        self.assertEqual(result['unique_selected_units'], 2)
        self.assertEqual(result['overlaps'], [{'key': 'a', 'strata': ['one', 'two']}])
        self.assertEqual(result['status'], 'UNREVIEWED')

    def test_unsorted_or_invalid_keys_refused(self):
        for keys in [['b', 'a'], ['a', None], ['']]:
            with self.subTest(keys=keys), self.assertRaises(GeneratorError):
                sample_strata({'x': keys}, self.config)

    def test_hash_tie_uses_stable_key(self):
        with patch('literaki_slownik.quality.sampling_digest', return_value='0' * 64):
            result = sample_strata({'x': [f'{n:03}' for n in range(40)]}, self.config)
        self.assertEqual([item['key'] for item in result['strata']['x']['selected']],
                         [f'{n:03}' for n in range(30)])

    def test_unapproved_config_changes_refused(self):
        for field, value in [('version', 'v2'), ('size_per_stratum', 31),
                             ('size_per_stratum', True), ('seed', ''),
                             ('encoding', 'concatenation'), ('extra', 1)]:
            config = {**self.config, field: value}
            with self.subTest(field=field, value=value), self.assertRaises(GeneratorError):
                sample_strata({'x': ['a']}, config)

    def test_review_template_bound_to_inputs_without_default_approval(self):
        sample = sample_strata({'one': ['a'], 'two': ['a', 'b']}, self.config)
        review = review_template(sample, canonical_index_sha256='a' * 64,
                                 evidence_sha256={'rules': 'b' * 64})
        self.assertEqual(review['canonical_index_sha256'], 'a' * 64)
        self.assertEqual(review['evidence_sha256'], {'rules': 'b' * 64})
        self.assertEqual(review['status'], 'UNREVIEWED')
        self.assertEqual(len(review['items']), 2)
        self.assertEqual(review['items'][0]['strata'], ['one', 'two'])
        for item in review['items']:
            self.assertIsNone(item['assessment'])
            self.assertIsNone(item['reviewer'])
            self.assertIsNone(item['source_justification'])
        for index, evidence in [('x', {'rules': 'b' * 64}), ('a' * 64, {}),
                                ('a' * 64, {'rules': 'x'})]:
            with self.assertRaises(GeneratorError):
                review_template(sample, canonical_index_sha256=index, evidence_sha256=evidence)
