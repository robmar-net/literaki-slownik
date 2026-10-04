import unittest
import json
from pathlib import Path
from literaki_slownik.policy import assess_profile, spelling_checks, disrecommended_checks, history_checks
from literaki_slownik.decisions import assess_analysis, aggregate, assessment
from literaki_slownik.inputs import GeneratorError


class PolicyTests(unittest.TestCase):
    def test_informal_and_rare_conditions_do_not_reject(self):
        from literaki_slownik.policy import usage_checks
        for field in ('pot.', 'wulg.', 'reg.', 'gwar.', 'rzad.', 'pot.,reg.,rzad.', 'rzad.,wulg.'):
            checks = usage_checks(field)
            self.assertEqual(len(checks), 1, field)
            self.assertEqual(checks[0]['status'], 'accept')
            self.assertEqual(checks[0]['source_label'], field)

    def test_usage_does_not_guess_unreviewed_compounds_or_complete_policy(self):
        from literaki_slownik.policy import usage_checks
        for field in ('niepopr.,pot.', 'pot.,po_liczebniku', 'daw.,reg.', 'reg.,nowe', ''):
            self.assertEqual(usage_checks(field), [], field)
        checks = usage_checks('pot.|rzad.|pot.')
        self.assertEqual(len(checks), 2)
        checks.append({'rule_id': 'remaining', 'status': 'unresolved', 'message': 'Pending', 'evidence': []})
        self.assertEqual(assessment(checks)['status'], 'unresolved')
        checks += history_checks('daw.', 'standard')
        self.assertEqual(assessment(checks)['status'], 'reject')

    def test_usage_registry_matches_closed_literals(self):
        from literaki_slownik.policy import USAGE_LABELS
        rules = json.loads(Path('config/generator/policy.json').read_text())['rules']
        rule = next(r for r in rules if r['rule_id'] == 'linguistic-informal-rare-non-excluding-v1')
        self.assertEqual(set(rule['literal_labels']), USAGE_LABELS)
        self.assertEqual(rule['variants'], {'broad': 'non_excluding', 'standard': 'non_excluding'})

    def test_history_priority_applies_to_same_interpretation_only(self):
        mixed = ('daw.,daw._dziś_gwar.', 'daw.,daw._dziś_gwar.,rzad.',
                 'przest.,przest._dziś_książk.')
        for field in mixed:
            self.assertEqual(assessment(history_checks(field, 'standard'))['status'], 'reject', field)
            self.assertEqual(assessment(history_checks(field, 'broad'))['status'], 'accept', field)
            self.assertTrue(any(c['rule_id'] == 'linguistic-current-usage-non-excluding-v1'
                                for c in history_checks(field, 'standard')))

    def test_current_usage_labels_do_not_reject_standard(self):
        for field in ('daw._dziś_gwar.', 'daw._dziś_rzad.', 'daw._dziś_fraz.',
                      'przest._dziś_książk.,żart.', 'przest._dziś_gwar.'):
            self.assertEqual(assessment(history_checks(field, 'standard'))['status'], 'accept', field)

    def test_archaic_forms_not_restored_by_current_lexeme(self):
        for field in ('przest._dziś_książk.,arch.,char.', 'arch._(tylko_po_"ku")',
                      'daw.,niezal.', 'niezal.,przest.'):
            self.assertEqual(assessment(history_checks(field, 'standard'))['status'], 'reject', field)
            self.assertEqual(assessment(history_checks(field, 'broad'))['status'], 'accept', field)

    def test_age_rule_is_closed_and_does_not_guess_from_substring(self):
        for field in ('archit.', 'archeol.', 'hist.', 'char.,archit.', 'przestawny',
                      'daw.,nowy_kwalifikator'):
            self.assertEqual(history_checks(field, 'standard'), [], field)
        checks = history_checks('daw.|daw._dziś_gwar.', 'standard')
        self.assertEqual(assessment(checks)['status'], 'reject')
        with self.assertRaises(GeneratorError):
            history_checks('daw.', 'unknown')

    def test_positive_other_homonym_survives_historical_rejection(self):
        game_ok = [{'rule_id': 'game-fixture', 'status': 'accept', 'message': 'Test', 'evidence': ['fixture']}]
        old = assess_analysis('forma', language={v: history_checks('daw.', v) for v in ('broad','standard')},
                              game_checks=game_ok)
        current = assess_analysis('forma', language={v: history_checks('daw._dziś_gwar.', v) for v in ('broad','standard')},
                                  game_checks=game_ok)
        self.assertEqual(old['membership']['standard']['status'], 'reject')
        self.assertEqual(aggregate([old,current], 'standard')['status'], 'accept')

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

    def test_age_registry_matches_versioned_literals(self):
        from literaki_slownik.policy import HISTORICAL_LABELS, CURRENT_USAGE_LABELS
        rules = {r['rule_id']: r for r in json.loads(Path('config/generator/policy.json').read_text())['rules']}
        self.assertEqual(set(rules['linguistic-historical-form-v1']['literal_labels']), HISTORICAL_LABELS)
        self.assertEqual(set(rules['linguistic-current-usage-non-excluding-v1']['literal_labels']), CURRENT_USAGE_LABELS)
        self.assertEqual(rules['linguistic-historical-form-v1']['variants'], {'broad': 'non_excluding', 'standard': 'reject'})

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
