"""Konstrukcje zachowują źródłową interpretację, bez kwalifikacji do gry."""
import unittest

from literaki_slownik.constructions import impt_particle_candidates, by_aglt_candidates
from literaki_slownik.inputs import GeneratorError


def source(form='daj', tag='impt:sg:sec:perf', qualifiers=''):
    return {'source_id': 'SGJP-fixture', 'first_source_row': 12, 'original': form,
            'lemma_id': 'dać:fixture', 'raw_tag': tag, 'names': '', 'qualifiers': qualifiers}


class ConstructionTests(unittest.TestCase):
    def test_by_aglt_only_four_nonvocalic_personal_endings(self):
        operator = source('by', 'part')
        operator['lemma_id'] = 'by:T'
        for suffix, number, person, expected in [('m', 'sg', 'pri', 'bym'), ('ś', 'sg', 'sec', 'byś'),
                                                  ('śmy', 'pl', 'pri', 'byśmy'), ('ście', 'pl', 'sec', 'byście')]:
            aglt = source(suffix, f'aglt:{number}:{person}:imperf:nwok')
            result, = by_aglt_candidates(operator, aglt)
            self.assertEqual(result['original'], expected)
            self.assertEqual([item['interpretation'] for item in result['components']], [operator, aglt])
            self.assertEqual(result['status'], 'candidate_not_qualified')

    def test_by_aglt_preserves_all_component_labels_without_sense_cross_product(self):
        operator = source('by', 'comp', 'rzad.')
        aglt = source('m', 'aglt:sg:pri:imperf:nwok', 'niezal.|rzad.')
        result, = by_aglt_candidates(operator, aglt)
        self.assertEqual(result['qualifiers'], 'niezal.|rzad.')
        self.assertEqual(result['components'][0]['interpretation']['qualifiers'], 'rzad.')
        self.assertEqual(result['components'][1]['interpretation']['qualifiers'], 'niezal.|rzad.')

    def test_by_aglt_wrong_hosts_and_vocalic_endings_not_generated(self):
        self.assertEqual(by_aglt_candidates(source('niby', 'part'), source('m', 'aglt:sg:pri:imperf:nwok')), [])
        self.assertEqual(by_aglt_candidates(source('by', 'subst:sg:nom:m3'), source('m', 'aglt:sg:pri:imperf:nwok')), [])
        for suffix, tag in [('em', 'aglt:sg:pri:imperf:wok'), ('eśmy', 'aglt:pl:pri:imperf:wok'),
                            ('ś', 'aglt:sg:pri:imperf:nwok'), ('m', 'aglt:sg:pri:perf:nwok')]:
            with self.subTest(suffix=suffix, tag=tag), self.assertRaises(GeneratorError):
                by_aglt_candidates(source('by', 'part'), source(suffix, tag))

    def test_single_particle_correct_sg_and_pl_forms(self):
        for form, tag, result in [('daj', 'impt:sg:sec:perf', 'dajże'),
                                  ('czytaj', 'impt:sg:sec:imperf', 'czytajże'),
                                  ('dajcie', 'impt:pl:sec:perf', 'dajcież'),
                                  ('dajmy', 'impt:pl:pri:perf', 'dajmyż')]:
            candidate, = impt_particle_candidates(source(form, tag))
            self.assertEqual(candidate['original'], result)
            self.assertEqual(candidate['status'], 'candidate_not_qualified')
            self.assertEqual(candidate['components'][0]['interpretation'], source(form, tag))
            self.assertEqual(len(candidate['components']), 2)

    def test_source_qualifiers_case_and_full_homonym_id_preserved(self):
        original = source('Daj', qualifiers='daw.,niezal.')
        result, = impt_particle_candidates(original)
        self.assertEqual(result['original'], 'Dajże')
        self.assertEqual(result['qualifiers'], 'daw.,niezal.')
        self.assertEqual(result['names'], '')
        self.assertEqual(result['lemma_id'], 'dać:fixture')
        self.assertEqual(original, source('Daj', qualifiers='daw.,niezal.'))

    def test_not_suffix_guessing_or_double_particle(self):
        self.assertEqual(impt_particle_candidates(source('czytajże', 'subst:sg:nom:m3')), [])
        result, = impt_particle_candidates(source('żeż', 'impt:sg:sec:perf'))
        self.assertEqual(result['original'], 'żeżże')  # rozkaźnik żec, nie analiza podwojonej partykuły
        self.assertNotEqual(result['original'], 'żeżżeż')

    def test_expanded_tags_keep_raw_source_and_separate_derivations(self):
        raw = source('daj', 'impt:sg:sec:perf.imperf')
        result = impt_particle_candidates(raw)
        self.assertEqual(len(result), 2)
        self.assertEqual({item['expanded_tag'] for item in result}, {'impt:sg:sec:perf', 'impt:sg:sec:imperf'})
        self.assertTrue(all(item['components'][0]['interpretation']['raw_tag'] == raw['raw_tag'] for item in result))

    def test_invalid_source_and_uncovered_impt_class_are_errors(self):
        for record in [source('', 'impt:sg:sec:perf'), source('dajmy', 'impt:sg:sec:perf'),
                       source('daj', 'impt:sg:pri:perf'), source('daj', 'impt:sg:sec:new'),
                       {'original': 'daj', 'raw_tag': 'impt:sg:sec:perf'}]:
            with self.subTest(record=record), self.assertRaises(GeneratorError):
                impt_particle_candidates(record)
