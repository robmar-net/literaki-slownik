import tempfile
from copy import deepcopy
import unittest
from pathlib import Path
from tests.helpers import fixture_manifest, rewrite
from literaki_slownik.inputs import inspect_sources, GeneratorError


class InputTests(unittest.TestCase):
    def test_relative_paths_and_no_side_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = fixture_manifest(directory)
            before = sorted(Path(directory).iterdir())
            report = inspect_sources(path)
            self.assertEqual(report['mode'], 'test')
            self.assertEqual(report['artifacts'][0]['source_id'], 'synthetic')
            self.assertEqual(before, sorted(Path(directory).iterdir()))

    def test_blocked_role_origin_and_hash(self):
        for field, value in [('status', 'BLOCKED'), ('role', 'benchmark'),
                             ('origin', 'SJP.pl'), ('origin', 'PoliMorf'),
                             ('role', 'unknown'), ('kind', 'kwjp_orth'),
                             ('sha256', '0' * 64), ('version', '')]:
            with self.subTest(field=field, value=value), tempfile.TemporaryDirectory() as directory:
                path, manifest = fixture_manifest(directory)
                manifest['artifacts'][0][field] = value
                rewrite(path, manifest)
                with self.assertRaises(GeneratorError):
                    inspect_sources(path)

    def test_missing_evidence_and_duplicate_source(self):
        for mutation in ['evidence', 'duplicate']:
            with tempfile.TemporaryDirectory() as directory:
                path, manifest = fixture_manifest(directory)
                if mutation == 'evidence':
                    manifest['artifacts'][0]['evidence'] = []
                else:
                    manifest['artifacts'] *= 2
                rewrite(path, manifest)
                with self.assertRaises(GeneratorError):
                    inspect_sources(path)

    def test_fixture_cannot_claim_production(self):
        with tempfile.TemporaryDirectory() as directory:
            path, manifest = fixture_manifest(directory)
            manifest['mode'] = 'production'
            rewrite(path, manifest)
            with self.assertRaises(GeneratorError):
                inspect_sources(path)

    def test_evidence_and_configuration_hash_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            path, manifest = fixture_manifest(directory)
            manifest['configurations']['profile'] = {'path': 'notice.txt', 'sha256': '0' * 64}
            rewrite(path, manifest)
            with self.assertRaises(GeneratorError):
                inspect_sources(path)

    def test_invalid_json_schema_is_not_assertion(self):
        with tempfile.TemporaryDirectory() as directory:
            path, manifest = fixture_manifest(directory)
            for value in [[], {'schema_version': True}, {'schema_version': 999}]:
                rewrite(path, value)
                with self.assertRaises(GeneratorError):
                    inspect_sources(path)

    def test_expected_counts_have_integer_units(self):
        for value in [True, -1, '1', 1.5]:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                path, manifest = fixture_manifest(directory)
                manifest['artifacts'][0]['expected_counts'] = {'records': value}
                rewrite(path, manifest)
                with self.assertRaises(GeneratorError):
                    inspect_sources(path)

    def test_production_requires_distinct_kwjp_slots(self):
        with tempfile.TemporaryDirectory() as directory:
            path, manifest = fixture_manifest(directory)
            lexical = manifest['artifacts'][0]
            lexical.update(origin='SGJP', expected_counts={'records': 1})
            manifest['mode'] = 'production'
            for kind in ['kwjp_lemma', 'kwjp_orth', 'kwjp_orth_lc']:
                for genre in ['all', 'fakt', 'fikcja', 'publicystyka']:
                    item = deepcopy(lexical)
                    item.update(source_id=kind + genre, origin='KWJP', kind=kind,
                                role='corpus_evidence', genre=genre)
                    manifest['artifacts'].append(item)
            item = deepcopy(manifest['artifacts'][1])
            item.update(source_id='bigram', kind='kwjp_bigram', genre='all')
            manifest['artifacts'].append(item)
            rewrite(path, manifest)
            self.assertEqual(len(inspect_sources(path)['artifacts']), 14)
            manifest['artifacts'][2]['genre'] = 'all'
            rewrite(path, manifest)
            with self.assertRaises(GeneratorError):
                inspect_sources(path)
