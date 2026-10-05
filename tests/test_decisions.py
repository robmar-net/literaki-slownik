import unittest
from literaki_slownik.decisions import assessment, assess_analysis, aggregate
from literaki_slownik.inputs import GeneratorError


def checks(status):
    return [{'rule_id': 'synthetic-v1', 'status': status,
             'message': 'Własna fikstura', 'evidence': ['synthetic:own']}]


def analysis(language, game, form='kot'):
    return assess_analysis(form, language={'broad': checks(language), 'standard': checks(language)},
                           game_checks=checks(game))


class DecisionsTests(unittest.TestCase):
    def test_release_scope_excludes_candidate_without_lexical_rejection_or_homonym_loss(self):
        outside = assess_analysis('kołoń', language={v:checks('unresolved') for v in ('broad','standard')},
                                  game_checks=checks('accept'), scope_checks=checks('reject'))
        self.assertEqual(outside['language']['standard']['status'],'unresolved')
        self.assertEqual(outside['game']['status'],'accept')
        self.assertEqual(outside['release_scope']['status'],'reject')
        self.assertEqual(outside['membership']['standard']['status'],'reject')
        direct = analysis('accept','accept','kołoń')
        self.assertEqual(direct['release_scope']['status'],'accept')
        self.assertEqual(aggregate([outside,direct],'standard')['status'],'accept')

    def test_known_reject_retains_unknown_and_empty_is_not_accept(self):
        value = assessment(checks('unresolved') + checks('reject'))
        self.assertEqual(value['status'], 'reject')
        self.assertEqual(len(value['checks']), 2)
        self.assertEqual(assessment([])['status'], 'unresolved')
        with self.assertRaises(GeneratorError):
            assessment(checks('maybe'))

    def test_all_conditions_must_hold_in_same_analysis(self):
        values = [analysis('accept', 'reject'), analysis('reject', 'accept')]
        self.assertEqual(aggregate(values, 'standard')['status'], 'reject')
        values.append(analysis('accept', 'accept'))
        self.assertEqual(aggregate(values, 'standard')['status'], 'accept')
        self.assertEqual(len(values), 3)
        self.assertEqual(aggregate([analysis('unresolved', 'accept')], 'broad')['status'], 'unresolved')
        self.assertEqual(aggregate([], 'broad')['status'], 'absent')

    def test_uppercase_reject_does_not_remove_lexical_assessment(self):
        value = analysis('accept', 'accept', 'PCV')
        self.assertEqual(value['language']['standard']['status'], 'accept')
        self.assertEqual(value['game']['status'], 'reject')
        self.assertEqual(value['profile']['status'], 'reject')
        self.assertEqual(value['membership']['standard']['status'], 'reject')
        self.assertEqual(value['original'], 'PCV')

    def test_standard_cannot_accept_an_analysis_rejected_by_broad(self):
        with self.assertRaises(GeneratorError):
            assess_analysis('kot', language={'broad': checks('reject'), 'standard': checks('accept')},
                            game_checks=checks('accept'))

    def test_empty_game_assessment_and_cross_word_aggregation_are_not_acceptance(self):
        value = assess_analysis('kot', language={'broad': checks('accept'), 'standard': checks('accept')},
                                game_checks=[])
        self.assertEqual(value['game']['status'], 'unresolved')
        self.assertEqual(value['membership']['standard']['status'], 'unresolved')
        with self.assertRaises(GeneratorError):
            aggregate([analysis('accept', 'accept', 'kot'), analysis('accept', 'accept', 'pies')], 'standard')
