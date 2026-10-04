import unittest
import json
from pathlib import Path
from literaki_slownik.policy import assess_profile, spelling_checks


class PolicyTests(unittest.TestCase):
    def test_profile_matches_versioned_canonical_registry(self):
        from literaki_slownik.policy import ALPHABET
        path = Path(__file__).resolve().parents[1] / 'config/generator/profile.json'
        profile = json.loads(path.read_text())
        self.assertEqual(profile['alphabet'], ALPHABET)
        self.assertEqual(len(set(ALPHABET)), 32)
        self.assertEqual((profile['minimum'], profile['maximum'], profile['version']), (2, 15, 'pl-v1'))

    def test_original_uppercase_and_profile_are_independent(self):
        self.assertEqual(spelling_checks('PCR')[0]['status'], 'reject')
        self.assertEqual(assess_profile('PCR')['status'], 'accept')
        pcv = assess_profile('PCV')
        self.assertEqual(pcv['status'], 'reject')
        self.assertEqual(pcv['invalid_characters'], ['v'])
        self.assertEqual(pcv['game_key'], 'pcv')

    def test_nfc_preserves_diacritics_and_does_not_strip_characters(self):
        normalized = assess_profile('z\u0307aba')
        self.assertEqual(normalized['nfc'], 'żaba')
        self.assertEqual(normalized['status'], 'accept')
        for form in ('a', 'a' * 16, 'pol-ski', 'co jest', 'kot.', 'ko*'):
            self.assertEqual(assess_profile(form)['status'], 'reject', form)
        self.assertEqual(assess_profile('a' * 15)['status'], 'accept')
        self.assertEqual(assess_profile('aa')['status'], 'accept')
