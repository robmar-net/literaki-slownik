"""Leksemy, warstwy i formy TEMATY (#11, W7, W8): kandydaci → wpisy z formami w STANDARD."""
import tempfile
import unittest

from literaki_slownik import tematy
from tests.tematy_helpers import SOURCE, TBX, inputs_fixture, repin_iate, write_iate


def label(lemma_id):
    return lemma_id + '@' + SOURCE


class TematyLayersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.f = inputs_fixture(cls.tmp.name)
        cls.data = tematy.check_inputs(cls.f['manifest'], cls.f['config'], cls.f['topic'])
        cls.cands = tematy.candidates(cls.data)
        cls.result = tematy.build_entries(cls.data, cls.cands)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def map(self, wanted):
        with tematy._readonly(self.data['paths']['database']) as db:
            return tematy.map_lemmas(db, wanted, self.cands['sgjp']['klasy'])

    def test_lemma_maps_to_lexemes_with_equal_base_and_class_of_the_code(self):
        verb, noun = tematy.CZESCI_MOWY['1'], tematy.CZESCI_MOWY['2']
        found = self.map({'żeglować': verb, 'statek': noun})
        self.assertEqual({k: [found['wiersze'][i][1] for i in v] for k, v in found['leksemy'].items()},
                         {'żeglować': ['żeglować'], 'statek': ['statek']})
        # Ten sam lemat z kodem rzeczownika albo jako termin T3: leksem `żeglować` ma tylko ger i inf.
        self.assertEqual(self.map({'żeglować': noun})['brak'], ['żeglować'])
        self.assertEqual(self.map({'żeglować': tuple(tematy.T3_KLASY)})['brak'], ['żeglować'])
        # Lemat T2 `kuter` wskazuje dwa leksemy o równym `lemma_base`; oba są wpisami T2 albo niżej.
        entries = self.result['kandydaci']
        self.assertEqual(entries[label('kuter:S2')]['zrodla'], ('T2',))
        self.assertEqual(entries[label('kuter:S2')]['znaczenie'], {'T2': ('900 kuter 1',)})
        self.assertEqual(entries[label('barka')]['znaczenie'], {'T3': ('IATE-5 4821',)})
        self.assertEqual(entries[label('barka')]['iate'], ('IATE-5',))

    def test_gerund_lemma_is_brak_leksemu_with_its_own_count(self):
        rejected, ger = self.result['odrzucone'], self.result['ger']
        self.assertEqual(rejected['T2']['BRAK_LEKSEMU'], ['marynarz', 'żeglarstwo', 'żeglowanie', 'żegluga'])
        self.assertEqual(ger['T2'], ['żeglowanie'])
        self.assertEqual(rejected['T3']['BRAK_LEKSEMU'], ['kil'])
        self.assertEqual(ger['T3'], [])
        self.assertEqual(ger['razem'], ['żeglowanie'])
        self.assertEqual(rejected['T2']['NIE_JEDNO_SLOWO'], ['statek rzeczny'])
        self.assertEqual(rejected['T3']['NIE_JEDNO_SLOWO'], ['statek rzeczny'])
        self.assertEqual(rejected['T1']['BRAK_LEKSEMU'], [])
        # Forma bez pasującego leksemu, ale nie `ger` (`żeglować` to `inf`), nie wchodzi do podliczby.
        noun = tematy.CZESCI_MOWY['2']
        found = self.map({'żeglować': noun, 'żeglowanie': noun})
        self.assertEqual((found['brak'], found['ger']), (['żeglowanie', 'żeglować'], ['żeglowanie']))

    def test_lexeme_in_t1_and_t2_takes_t1_and_keeps_both_sources(self):
        kuter = self.result['wpisy'][label('kuter')]
        self.assertEqual((kuter['warstwa'], kuter['zrodla']), ('T1', ('T1', 'T2')))
        self.assertEqual(kuter['znaczenie'], {'T1': ('ryb.',), 'T2': ('900 kuter 1',)})
        szkuta = self.result['kandydaci'][label('szkuta')]
        self.assertEqual((szkuta['warstwa'], szkuta['zrodla']), ('T2', ('T2', 'T3')))
        self.assertEqual(szkuta['iate'], ('IATE-1', 'IATE-4'))

    def test_wieloznaczny_rule_counts_only_codes_1_to_4(self):
        flags = {e['klucz']: e['wieloznaczny'] for e in self.result['kandydaci'].values()}
        self.assertEqual(flags[label('łódź')], 'tak')  # `łódź 1` poza domknięciem
        self.assertEqual(flags[label('kuter')], 'tak')  # dwa leksemy `kuter` klasy subst
        self.assertEqual(flags[label('kuter:S2')], 'tak')
        self.assertEqual(flags[label('statek')], 'nie')
        self.assertEqual(flags[label('okręt')], 'nie')  # angielska `okręt` (kod 6) poza domknięciem nie liczy się
        self.assertEqual(flags[label('bosman')], 'brak_danych')
        self.assertEqual(flags[label('barka')], 'brak_danych')

    def test_forms_include_constructions_of_candidate_lexemes_only(self):
        forms = {k: e['formy'] for k, e in self.result['wpisy'].items()}
        self.assertEqual(forms[label('okręt')], ('okręt', 'okrętże'))
        self.assertEqual(forms[label('żeglować')], ('żeglowanie', 'żeglować'))  # kolejność punktów kodowych
        self.assertNotIn('kotże', self.result['formy'])  # konstrukcja leksemu spoza tematu
        self.assertIn('okrętże', self.result['formy'])

    def test_diagnostics_split_poza_broad_and_poza_standard(self):
        rejected, diag = self.result['odrzucone'], self.result['diagnostyka']
        self.assertEqual(rejected['T2']['POZA_STANDARD'], [label('szkuta')])
        self.assertEqual(rejected['T2']['POZA_BROAD'], [label('kambuz')])
        self.assertEqual(rejected['razem']['POZA_BROAD'], [label('kambuz')])
        self.assertEqual(diag['T2']['leksemy'], {'kandydaci': 6, 'broad': 5, 'standard': 4})
        self.assertEqual(diag['T2']['formy'], {'kandydaci': 9, 'broad': 8, 'standard': 7})
        self.assertEqual(diag['razem']['leksemy'], {'kandydaci': 11, 'broad': 10, 'standard': 9})
        layers = ('T1', 'T2', 'T3')
        self.assertEqual(sum(diag[w]['leksemy']['kandydaci'] for w in layers), diag['razem']['leksemy']['kandydaci'])

    def test_result_is_subset_of_standard_and_layers_are_disjoint(self):
        result, standard = self.result, self.data['standard']
        self.assertLessEqual(set(result['formy']), standard)
        self.assertEqual(list(result['formy']), sorted(result['formy']))
        layers = [set(result['warstwy'][w]) for w in ('T1', 'T2', 'T3')]
        self.assertEqual(sum(map(len, layers)), len(set().union(*layers)))
        self.assertEqual(set().union(*layers), set(result['wpisy']))
        self.assertEqual(result['warstwy'], {'T1': tuple(label(x) for x in ('bosman', 'kuter', 'reja', 'żeglować')),
                                             'T2': tuple(label(x) for x in ('kuter:S2', 'okręt', 'statek', 'łódź')),
                                             'T3': (label('barka'),), 'D': ()})
        self.assertTrue(all(e['formy'] and set(e['formy']) <= standard for e in result['wpisy'].values()))


class TematyThreeLayersTest(unittest.TestCase):
    def test_lexeme_in_three_layers_takes_t1_and_keeps_all_sources(self):
        # `kuter` (T1 `ryb.`, T2 `900 kuter 1`) dostaje też termin IATE-5: jeden wpis, warstwa T1.
        term = '<term>barka</term>'
        tig = ('<term>kuter</term>\n            <termNote type="termType">fullForm</termNote>\n'
               '            <descrip type="reliabilityCode">3</descrip>\n          </tig>\n          <tig>\n'
               '            ' + term)
        self.assertEqual(TBX.count(term), 1)
        with tempfile.TemporaryDirectory() as tmp:
            f = inputs_fixture(tmp)
            write_iate(f['paths']['iate'], TBX.replace(term, tig))
            repin_iate(f)
            data = tematy.check_inputs(f['manifest'], f['config'], f['topic'])
            result = tematy.build_entries(data, tematy.candidates(data))
        kuter = result['wpisy'][label('kuter')]
        self.assertEqual((kuter['warstwa'], kuter['zrodla']), ('T1', ('T1', 'T2', 'T3')))
        self.assertEqual(kuter['znaczenie'], {'T1': ('ryb.',), 'T2': ('900 kuter 1',), 'T3': ('IATE-5 4821',)})
        self.assertEqual(kuter['iate'], ('IATE-5',))
        layers = [set(result['warstwy'][w]) for w in ('T1', 'T2', 'T3')]
        self.assertEqual(sum(map(len, layers)), len(set().union(*layers)))
        self.assertIn(label('kuter'), layers[0])


if __name__ == '__main__':
    unittest.main()
