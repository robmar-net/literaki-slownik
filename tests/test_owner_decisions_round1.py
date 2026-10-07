"""Decyzje właściciela, runda 1 (2026-10-08): R2, adjp, -by, etykiety złożone."""
import unittest
from literaki_slownik.decisions import assessment
from literaki_slownik.canonical import load_json
from literaki_slownik.policy import (ADJP_GAME_STATUS, mandatory_capital_checks, orthography_checks,
                                     source_game_checks)

R2 = [('krakowianin', 'krakowianin', 'subst:sg:nom:m1'), ('krakus', 'krakusów', 'subst:pl:gen.acc:m1'),
      ('kresowianin', 'kresowianie', 'depr:pl:nom.acc.voc:m2'), ('rzymianin', 'rzymianin', 'subst:sg:nom:m1'),
      ('sądeczanin', 'sądeczanina', 'subst:sg:gen.acc:m1'), ('zatorzanin', 'zatorzanin', 'subst:sg:nom:m1')]


def source(tag, **fields):
    return dict({'original': 'x', 'lemma_id': 'x', 'raw_tag': tag, 'names': 'nazwa_pospolita', 'qualifiers': ''},
                **fields)


class OwnerDecisionsRound1Tests(unittest.TestCase):
    def test_rjp_literal_resident_examples_need_capital(self):
        for lemma, word, tag in R2:
            s = source(tag, original=word, lemma_id=lemma)
            self.assertEqual(assessment(source_game_checks(s))['status'], 'reject', lemma)
            self.assertEqual(assessment(orthography_checks(s, 'standard'))['status'], 'reject', lemma)
            self.assertEqual(assessment(orthography_checks(s, 'broad'))['status'], 'accept', lemma)
        # Bawarka (kulin., napój), formy żeńskie i nazwisko Krakus nie są objęte decyzją.
        for lemma, word, tag in [('bawarka', 'bawarka', 'subst:sg:nom:f'), ('krakowianka', 'krakowianka', 'subst:sg:nom:f'),
                                 ('Krakus:Sm1', 'Krakus', 'subst:sg:nom:m1')]:
            self.assertEqual(mandatory_capital_checks(source(tag, original=word, lemma_id=lemma)), [], lemma)

    def test_adjp_accepted_provisionally_and_marked(self):
        self.assertEqual(ADJP_GAME_STATUS, 'accept')
        checks = source_game_checks(source('adjp', original='polsku', lemma_id='polski:A', names=''))
        marked = [c for c in checks if c['rule_id'] == 'game-adjp-graphic-word-v1']
        self.assertEqual(len(marked), 1)
        self.assertEqual(marked[0]['status'], 'accept')
        self.assertTrue(marked[0]['provisional'])
        self.assertEqual(assessment(checks)['status'], 'accept')
        # Inne klasy nie dostają znacznika.
        for tag in ('adj:sg:nom:m1:pos', 'frag', 'adja'):
            self.assertFalse(any(c['rule_id'] == 'game-adjp-graphic-word-v1'
                                 for c in source_game_checks(source(tag))), tag)

    def test_adjp_switch_rejects_when_withdrawn(self):
        from unittest.mock import patch
        with patch('literaki_slownik.policy.ADJP_GAME_STATUS', 'reject'):
            checks = source_game_checks(source('adjp', original='polsku', lemma_id='polski:A', names=''))
        self.assertEqual(assessment(checks)['status'], 'reject')

    def test_by_single_words_accepted_as_in_sgjp(self):
        for lemma, tag in [('bodajby', 'part'), ('niechby', 'part'), ('kieby', 'comp'), ('jeźliby', 'comp')]:
            s = source(tag, original=lemma, lemma_id=lemma, names='')
            for variant in ('broad', 'standard'):
                checks = orthography_checks(s, variant)
                self.assertEqual([c['rule_id'] for c in checks], ['orthography-sgjp-single-word-by-v1'], lemma)
                self.assertEqual(assessment(checks)['status'], 'accept', lemma)
        # Norma 2026 dla jeśliby/jeżeliby pozostaje bez zmian.
        s = source('comp', original='jeśliby', lemma_id='jeśliby', names='')
        self.assertEqual(assessment(orthography_checks(s, 'standard'))['status'], 'reject')
        # Inny napis lub klasa nie dostaje reguły.
        self.assertEqual(orthography_checks(source('part', original='niechbym', lemma_id='niechby', names=''), 'broad'), [])

    def test_coverage_records_round1_and_closes_compound_qualifiers(self):
        coverage = load_json('config/generator/coverage.json')
        self.assertNotIn('all_compound_qualifier_semantics_and_variant_policy', coverage['pending'])
        for key in ('compound_qualifier_conjunction_user_approved', 'rjp_literal_resident_examples_capital_user_approved',
                    'adjp_graphic_word_provisional_user_approved', 'by_single_word_sgjp_user_approved'):
            self.assertIn(key, coverage['confirmed'])
        self.assertTrue(coverage['release_blocked'])


if __name__ == '__main__':
    unittest.main()
