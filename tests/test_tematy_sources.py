"""Kandydaci TEMATY z trzech źródeł: etykiety SGJP (T1), Słowosieć (T2), IATE (T3) (#11, W7)."""
import tempfile
import unittest

from literaki_slownik import tematy
from tests.tematy_helpers import TBX, inputs_fixture, repin_iate, write_iate


class TematySourcesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.f = inputs_fixture(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def data(self):
        return tematy.check_inputs(self.f['manifest'], self.f['config'], self.f['topic'])

    def lexemes(self, data, ids):
        with tematy._readonly(data['paths']['database']) as db:
            names = dict(db.execute('select id, lemma_base from lexeme'))
        return {names[i] for i in ids}

    def code(self, call):
        with self.assertRaises(tematy.GeneratorError) as caught:
            call()
        return caught.exception.code

    # --- T1 ---
    def test_t1_splits_pipe_then_comma_and_matches_whole_atoms(self):
        self.assertEqual(tematy.qualifier_atoms('daw.|mors.,wojsk.'), frozenset({'daw.', 'mors.', 'wojsk.'}))
        data = self.data()
        sgjp = tematy.scan_sgjp(data)
        self.assertEqual(self.lexemes(data, sgjp['t1']), {'bosman', 'kuter', 'reja', 'żeglować'})
        names = {self.lexemes(data, [i]).pop(): atoms for i, atoms in sgjp['t1'].items()}
        self.assertEqual(names['reja'], ('mors.',))
        self.assertEqual(names['żeglować'], ('żegl.',))
        # Klasy tagów każdego leksemu, nie tylko T1 (`fok` ma `mors` bez kropki).
        classes = {self.lexemes(data, [i]).pop(): c for i, c in sgjp['klasy'].items()}
        self.assertEqual(classes['żeglować'], ('ger', 'inf'))
        self.assertEqual(classes['fok'], ('subst',))
        self.assertEqual(len(classes), len(self.lexemes(data, sgjp['klasy'])))

    # --- T2 ---
    def test_t2_closure_runs_parent_to_child_only(self):
        data = self.data()
        full = tematy.t2_candidates(data)
        self.assertLessEqual({'statek', 'łódź', 'okręt', 'kuter'}, set(full['lematy']))
        self.assertEqual(full['lematy']['łódź']['znaczenia'], ('łódź 2',))
        self.assertEqual(full['lematy']['statek']['klasy'], ('depr', 'subst'))
        self.assertNotIn('kot', full['lematy'])
        # Od samego `okręt 1` nie wracamy do `statek` (brak krawędzi odwrotnej).
        data['topic']['t2']['korzenie'] = [{'synset': 2149, 'nazwa': 'okręt 1'}]
        self.assertEqual(tematy.t2_candidates(data)['synsety'], [2149])
        self.assertEqual(set(tematy.t2_candidates(data)['lematy']), {'okręt'})

    def test_t2_abstract_synset_is_transited_without_its_lemmas(self):
        t2 = tematy.t2_candidates(self.data())
        self.assertIn('szkuta', t2['lematy'])  # 7354 → 901 (sztuczny) → 902
        self.assertNotIn('jednostka', t2['lematy'])
        self.assertEqual(t2['sztuczne'], [901])
        self.assertEqual(t2['odrzucone']['NIE_JEDNO_SLOWO'], ['statek rzeczny 1'])

    def test_t2_skips_units_with_codes_outside_the_map(self):
        t2 = tematy.t2_candidates(self.data())
        self.assertNotIn('ship', t2['lematy'])
        self.assertEqual(t2['odrzucone']['KOD_POZA_MAPA'], ['ship 1'])
        self.assertTrue(all(u['kod'] in tematy.CZESCI_MOWY for u in t2['jednostki']))

    def test_t2_root_name_mismatch_is_error(self):
        data = self.data()
        data['topic']['t2']['korzenie'][0]['nazwa'] = 'statek 2'
        self.assertEqual(self.code(lambda: tematy.t2_candidates(data)), 2)
        data['topic']['t2']['korzenie'][0].update(synset=999999, nazwa='statek 1')
        self.assertEqual(self.code(lambda: tematy.t2_candidates(data)), 2)

    # --- T3 ---
    def test_t3_subject_field_compares_whole_codes(self):
        t3 = tematy.t3_candidates(self.data())
        # IATE-2 `48` i IATE-3 `20, 48` nie pasują; IATE-4 `1011, 4821` pasuje.
        self.assertEqual(sorted(t3['hasla']), ['IATE-1', 'IATE-4', 'IATE-5'])
        self.assertEqual(t3['liczniki']['hasla'], 3)
        self.assertNotIn('kot', t3['terminy'])
        self.assertNotIn('kotwica', t3['terminy'])
        self.assertEqual(t3['hasla']['IATE-5']['en'], ('barge',))

    def test_t3_doctype_passes_entity_is_code_4(self):
        self.assertIn('kil', tematy.t3_candidates(self.data())['terminy'])  # DOCTYPE SYSTEM bez DTD obok
        for header in ('<!DOCTYPE martif [<!ENTITY e "kil">]>',
                       '<!DOCTYPE martif SYSTEM "x.dtd" [ ]>'):
            write_iate(self.f['paths']['iate'], TBX.replace('<!DOCTYPE martif SYSTEM "TBXcoreStructV02.dtd">',
                                                            header))
            repin_iate(self.f)
            data = self.data()
            self.assertEqual(self.code(lambda: tematy.t3_candidates(data)), 4, header)

    def test_t3_term_filters_and_type_counts(self):
        t3 = tematy.t3_candidates(self.data())
        self.assertEqual(t3['terminy'], {'barka': ('IATE-5',), 'kil': ('IATE-4',),
                                         'szkuta': ('IATE-1', 'IATE-4')})
        self.assertEqual(t3['odrzucone'], {'TYP': ['kl'], 'STATUS': ['bosman', 'maszt'],
                                           'NIEZAWODNOSC': ['ster'], 'WIELKA_LITERA': ['Bałtyk'],
                                           'NIE_JEDNO_SLOWO': ['statek rzeczny']})
        counts = t3['liczniki']
        self.assertEqual(counts['termType'], {'abbreviation': 1, 'fullForm': 9})
        self.assertEqual(counts['status'], {'BRAK': 8, 'deprecatedTerm-admn-sts': 1,
                                            'supersededTerm-admn-sts': 1})
        self.assertEqual((counts['przyjete'], counts['przyjete_rozne']), (4, 3))
        self.assertEqual(t3['hasla']['IATE-4']['przyjete'], ('kil', 'szkuta'))
        self.assertEqual(t3['hasla']['IATE-1']['pl'], ('bosman', 'szkuta'))


if __name__ == '__main__':
    unittest.main()
