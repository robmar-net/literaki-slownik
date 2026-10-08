"""Decyzje właściciela, runda 2 (2026-10-08): frag warunkowo, użycia wyczerpują ID."""
import unittest
from unittest.mock import patch
from literaki_slownik.canonical import load_json
from literaki_slownik.decisions import assessment, remainder_exhausted_check, use_closure_check
from literaki_slownik.policy import FRAG_GAME_STATUS, source_game_checks


def frag(original='bezcen', names='', qualifiers=''):
    return {'original': original, 'lemma_id': original, 'raw_tag': 'frag', 'names': names,
            'qualifiers': qualifiers, 'source_id': 'x', 'first_source_row': 1}


class OwnerDecisionsRound2Tests(unittest.TestCase):
    def test_frag_accepted_provisionally_and_marked(self):
        self.assertEqual(FRAG_GAME_STATUS, 'accept')
        checks = source_game_checks(frag())
        marked = [c for c in checks if c['rule_id'] == 'game-frag-graphic-word-v1']
        self.assertEqual(len(marked), 1)
        self.assertTrue(marked[0]['provisional'])
        self.assertEqual(assessment(checks)['status'], 'accept')
        self.assertFalse(any(c['rule_id'] == 'game-frag-graphic-word-v1'
                             for c in source_game_checks(frag() | {'raw_tag': 'adjp'})))

    def test_frag_switch_rejects_when_withdrawn(self):
        with patch('literaki_slownik.policy.FRAG_GAME_STATUS', 'reject'):
            self.assertEqual(assessment(source_game_checks(frag()))['status'], 'reject')

    def test_documented_surname_component_still_rejected(self):
        checks = source_game_checks({'original': 'ibn', 'lemma_id': 'ibn', 'raw_tag': 'frag', 'names': '',
                                     'qualifiers': '', 'source_id': 'sgjp-20260823', 'first_source_row': 1960055,
                                     'source_sha256': '3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810'})
        self.assertEqual(assessment(checks)['status'], 'reject')

    def test_use_closed_and_remainder_exhausted(self):
        review = {'use_id': 'u1', 'evidence': [{'artifact_id': 'a'}]}
        self.assertEqual(use_closure_check(review)['status'], 'accept')
        self.assertEqual(use_closure_check(review)['rule_id'], 'semantic-use-qualification-closed-v1')
        check = remainder_exhausted_check([review])
        self.assertEqual((check['status'], check['documented_use_ids']), ('reject', ['u1']))

    def test_resident_screen_rejected_in_game_except_non_residents(self):
        from literaki_slownik.policy import orthography_checks
        def src(original, lemma, tag):
            return {'original': original, 'lemma_id': lemma, 'raw_tag': tag, 'names': 'nazwa_pospolita', 'qualifiers': ''}
        for s in (src('abramowianin', 'abramowianin', 'subst:sg:nom:m1'),
                  src('kisieliczan', 'kisieliczanin', 'subst:pl:gen.acc:m1'),
                  src('krakowianki', 'krakowianka', 'subst:pl:nom.acc.voc:f'),
                  src('abramowianie', 'abramowianin', 'depr:pl:nom.acc.voc:m2')):
            game = source_game_checks(s)
            self.assertTrue(any(c['rule_id'] == 'game-resident-screen-capital-2026-v1' for c in game), s)
            self.assertEqual(assessment(game)['status'], 'reject', s)
            self.assertEqual(assessment(orthography_checks(s, 'standard'))['status'], 'reject', s)
            self.assertEqual(assessment(orthography_checks(s, 'broad'))['status'], 'accept', s)
        for s in (src('chrześcijanin', 'chrześcijanin', 'subst:sg:nom:m1'),
                  src('chrześcijanka', 'chrześcijanka', 'subst:sg:nom:f'),
                  src('mieszczanie', 'mieszczanin', 'depr:pl:nom.acc.voc:m2'),
                  src('wegetarianin', 'wegetarianin', 'subst:sg:nom:m1'),
                  # Nie m1/f, wielka litera i lemat spoza przesiewu nie podlegają regule.
                  src('mezanin', 'mezanin', 'subst:sg:nom:m3'),
                  src('Abramowianin', 'abramowianin', 'subst:sg:nom:m1'),
                  src('kot', 'kot:Sm2', 'subst:sg:nom:m2')):
            self.assertFalse(any(c['rule_id'] == 'game-resident-screen-capital-2026-v1'
                                 for c in source_game_checks(s)), s)
            self.assertEqual(orthography_checks(s, 'standard'), [], s)

    def test_resident_screen_lists_are_closed_and_consistent(self):
        from literaki_slownik.resident_screen import (RESIDENT_SCREEN_MASCULINE, RESIDENT_SCREEN_FEMININE,
                                                      NON_RESIDENT_EXCEPTIONS)
        self.assertEqual((len(RESIDENT_SCREEN_MASCULINE), len(RESIDENT_SCREEN_FEMININE), len(NON_RESIDENT_EXCEPTIONS)),
                         (2103, 2051, 76))
        self.assertLessEqual(NON_RESIDENT_EXCEPTIONS, RESIDENT_SCREEN_MASCULINE)
        self.assertTrue(all(w[:-2] + 'in' in RESIDENT_SCREEN_MASCULINE for w in RESIDENT_SCREEN_FEMININE))

    def test_coverage_records_round2(self):
        confirmed = load_json('config/generator/coverage.json')['confirmed']
        for key in ('frag_graphic_word_provisional_user_approved', 'documented_uses_exhaust_reviewed_ids_user_approved',
                    'resident_screen_class_capital_with_76_exceptions_user_approved'):
            self.assertIn(key, confirmed)


if __name__ == '__main__':
    unittest.main()
