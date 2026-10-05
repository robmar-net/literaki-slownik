"""Dowód użycia nie może stać się rozstrzygnięciem wszystkich znaczeń."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


class PanReviewTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'scripts/audit_pan_review.py'
        spec = importlib.util.spec_from_file_location('pan_review', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.cases = {'cases': [
            {'case_id': 'f', 'source': {'lemma_id': 'de:F', 'tag': 'frag'},
             'other_source_analyses': [{'lemma_id': 'de:S'}]},
            {'case_id': 'g', 'source': {'lemma_id': 'ibn', 'tag': 'frag'},
             'other_source_analyses': []},
        ]}
        self.review = {'automatic_eligibility_decisions': False,
            'sources': {'doc': {'role': 'documentary_observation_only'}},
            'annotations': [{'case_id': 'f', 'source': self.cases['cases'][0]['source'],
                'scope': 'documented_use_only', 'semantic_class': 'proper_name_component',
                'evidence': [{'source_id': 'doc', 'locator': '7.12'}],
                'normative_status': 'pending', 'eligibility_status': 'unresolved'}]}

    def test_use_evidence_preserves_unknowns_and_independent_homonym(self):
        result = self.module.audit(self.cases, self.review)
        self.assertEqual(result['coverage']['documented_use_cases'], 1)
        self.assertEqual(result['coverage']['without_documented_use_review'], 1)
        self.assertEqual(result['coverage']['eligibility_unresolved'], 2)
        self.assertEqual(result['cases'][0]['other_source_analyses'], [{'lemma_id': 'de:S'}])
        self.assertFalse(result['automatic_eligibility_decisions'])
        self.assertNotIn('review', self.cases['cases'][0])

    def test_mismatched_identity_duplicate_or_missing_evidence_is_refused(self):
        for change in ('identity', 'duplicate', 'evidence'):
            review = copy.deepcopy(self.review)
            if change == 'identity':
                review['annotations'][0]['source']['lemma_id'] = 'de:S'
            elif change == 'duplicate':
                review['annotations'] *= 2
            else:
                review['annotations'][0]['evidence'][0]['source_id'] = 'missing'
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.module.audit(self.cases, review)

    def test_exhaustive_meaning_or_eligibility_claim_is_refused(self):
        for field, value in [('scope', 'all_meanings'), ('eligibility_status', 'accept')]:
            review = copy.deepcopy(self.review)
            review['annotations'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.module.audit(self.cases, review)

    def test_snapshot_hash_mismatch_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'cases.json'
            path.write_text(json.dumps(self.cases))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.module.check_snapshot(path, digest)
            path.write_text('{}')
            with self.assertRaises(ValueError):
                self.module.check_snapshot(path, digest)
