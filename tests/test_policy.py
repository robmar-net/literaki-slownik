import unittest
import json
from pathlib import Path
from literaki_slownik.policy import assess_profile, spelling_checks, disrecommended_checks
from literaki_slownik.decisions import assess_analysis


class PolicyTests(unittest.TestCase):
    def test_disrecommended_condition_does_not_reject_known_literal_labels(self):
        for field in ('niezal.', 'niezal.,pot.', 'niezal.,rzad.',
                      'daw.,niezal.', 'niezal.,przest.'):
            checks = disrecommended_checks(field)
            self.assertEqual(len(checks), 1, field)
            self.assertEqual(checks[0]['status'], 'accept')
            self.assertEqual(checks[0]['source_label'], field)
            self.assertTrue(checks[0]['evidence'])

    def test_disrecommended_is_one_condition_not_whole_qualification(self):
        pending = {'rule_id': 'other-conditions', 'status': 'unresolved',
                   'message': 'Pozostałe warunki nieocenione.', 'evidence': []}
        history = {'rule_id': 'historical', 'status': 'reject',
                   'message': 'Odrębny warunek historyczności.', 'evidence': ['fixture']}
        result = assess_analysis('kakaa',
            language={variant: disrecommended_checks('niezal.') + [pending]
                      for variant in ('broad', 'standard')}, game_checks=[])
        self.assertEqual(result['language']['standard']['status'], 'unresolved')
        self.assertEqual(result['membership']['broad']['status'], 'unresolved')
        result = assess_analysis('forma',
            language={'broad': disrecommended_checks('daw.,niezal.'),
                      'standard': disrecommended_checks('daw.,niezal.') + [history]}, game_checks=[])
        self.assertEqual(result['language']['standard']['status'], 'reject')

    def test_literal_labels_not_substrings_or_comma_alternatives(self):
        for field in ('', 'niepopr.', 'niezalecane', 'xniezal.', 'niezal.,nowa_etykieta'):
            self.assertEqual(disrecommended_checks(field), [], field)
        checks = disrecommended_checks('niezal.|niepopr.')
        self.assertEqual([c['source_label'] for c in checks], ['niezal.'])

    def test_disrecommended_registry_matches_documented_partial_policy(self):
        from literaki_slownik.policy import DISRECOMMENDED_LABELS
        policy = json.loads(Path('config/generator/policy.json').read_text())
        self.assertEqual(set(policy['rules'][0]['literal_labels']), DISRECOMMENDED_LABELS)
        self.assertEqual(policy['rules'][0]['variants'], {'broad': 'non_excluding', 'standard': 'non_excluding'})
        self.assertEqual(policy['status'], 'partial_not_release_policy')

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
