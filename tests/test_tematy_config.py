"""Konfiguracja TEMATY: metoda, temat i manifest wejść (#11, W3–W5; #12, W1 i W5)."""
import tempfile
import unittest

from literaki_slownik import tematy
from literaki_slownik.inputs import GeneratorError
from tests.tematy_helpers import CONFIG, config_fixture, rewrite

KOT = {'lemat': 'kot', 'czesc_mowy': 'subst', 'powód': 'test'}


class TematyConfigTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.f = config_fixture(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def code(self, load, path):
        with self.assertRaises(GeneratorError) as caught:
            load(path)
        return caught.exception.code

    def test_valid_files_load(self):
        method = tematy.load_method(self.f['config'])
        self.assertEqual(method['config']['version'], 'tematy-v2')
        self.assertEqual(str(method['progi']['t2_tak']), '2/3')
        self.assertEqual(set(method['teksty']), {'ATTRIBUTIONS-tematy.md', 'LIMITATIONS.md', 'TERMS.md'})
        topic = tematy.load_topic(self.f['topic'])
        self.assertEqual(topic['t2']['tryb'], 'pelne')
        self.assertEqual(len(topic['diagnostyka']['slowa_oczywiste']), 37)
        self.assertEqual(tematy.load_sources(self.f['manifest'])['version'], 'tematy-sources-v1')

    def test_unknown_field_in_each_file_is_code_2(self):
        rewrite(self.f['config'], lambda v: v.update(extra=1))
        rewrite(self.f['topic'], lambda v: v['t3']['iate'].update(extra=1))
        rewrite(self.f['manifest'], lambda v: v['inputs']['iate'].update(extra=1))
        self.assertEqual(self.code(tematy.load_method, self.f['config']), 2)
        self.assertEqual(self.code(tematy.load_topic, self.f['topic']), 2)
        self.assertEqual(self.code(tematy.load_sources, self.f['manifest']), 2)

    def test_relation_and_mode_are_closed(self):
        rewrite(self.f['topic'], lambda v: v['t2'].update(relacje=[11, 25, 108]))
        self.assertEqual(self.code(tematy.load_topic, self.f['topic']), 2)
        rewrite(self.f['topic'], lambda v: v['t2'].update(relacje=[11, 25, 27], tryb='ograniczone'))
        self.assertEqual(self.code(tematy.load_topic, self.f['topic']), 2)

    def test_sampling_goes_through_quality_config(self):
        rewrite(self.f['config'], lambda v: v['sampling'].update(size_per_stratum=30))
        self.assertEqual(self.code(tematy.load_method, self.f['config']), 2)
        rewrite(self.f['config'], lambda v: (v['sampling'].update(size_per_stratum=50),
                                             v['sampling'].update(extra='x')))
        self.assertEqual(self.code(tematy.load_method, self.f['config']), 2)

    # --- #12, W1 i W5: temat bez T3, dodatki i wykluczenia na górnym poziomie, `operator_warstwy` ---
    def assert_topic_codes(self, changes):
        for change in changes:
            body = self.f['topic'].read_bytes()
            rewrite(self.f['topic'], change)
            try:
                self.assertEqual(self.code(tematy.load_topic, self.f['topic']), 2)
            finally:
                self.f['topic'].write_bytes(body)

    def test_topic_without_t3_loads_and_t3_keeps_only_iate(self):
        with tempfile.TemporaryDirectory() as tmp:
            topic = tematy.load_topic(config_fixture(tmp, t3=False)['topic'])
        self.assertNotIn('t3', topic)
        self.assertNotIn('znaczniki_srodladowe', topic['diagnostyka'])
        self.assert_topic_codes([lambda v: v['t3'].update(dodatki=[]), lambda v: v.update(t3={})])

    def test_top_level_addenda(self):
        rewrite(self.f['topic'], lambda v: v.update(dodatki=[KOT]))
        self.assertEqual(tematy.load_topic(self.f['topic'])['dodatki'], [KOT])
        self.assert_topic_codes([lambda v: v.update(dodatki=[KOT, KOT]),
                                 lambda v: v.update(dodatki=[{**KOT, 'powód': 'a\tb'}]),
                                 lambda v: v.pop('dodatki')])

    def test_lemma_exclusions(self):
        rewrite(self.f['topic'], lambda v: v.update(wykluczenia=[KOT, {**KOT, 'czesc_mowy': 'adj'}]))
        self.assertEqual(len(tematy.load_topic(self.f['topic'])['wykluczenia']), 2)
        self.assert_topic_codes([lambda v: v.update(wykluczenia=[KOT, KOT]),
                                 lambda v: v.update(wykluczenia=[{**KOT, 'powód': 'a\tb'}]),
                                 lambda v: v.update(wykluczenia=[{**KOT, 'powód': 'a\nb'}]),
                                 lambda v: v.update(wykluczenia=[{**KOT, 'czesc_mowy': 'rzeczownik'}])])

    def test_same_pair_in_addenda_and_exclusions_is_code_2(self):
        self.assert_topic_codes([lambda v: v.update(dodatki=[KOT], wykluczenia=[KOT])])
        rewrite(self.f['topic'], lambda v: v.update(dodatki=[KOT], wykluczenia=[{**KOT, 'czesc_mowy': 'adj'}]))
        tematy.load_topic(self.f['topic'])

    def test_inland_markers_need_t3_with_code_4821(self):
        rewrite(self.f['topic'], lambda v: v['diagnostyka'].pop('znaczniki_srodladowe'))
        tematy.load_topic(self.f['topic'])
        with tempfile.TemporaryDirectory() as tmp:
            topic = config_fixture(tmp, t3=False)['topic']
            rewrite(topic, lambda v: v['diagnostyka'].update(znaczniki_srodladowe={'pl': ['rzek'], 'en': ['river']}))
            self.assertEqual(self.code(tematy.load_topic, topic), 2)
        self.f['topic'].write_bytes((CONFIG/'tematy/morze.json').read_bytes())
        rewrite(self.f['topic'], lambda v: v['t3']['iate'].update(kody_dziedzin=['2841']))
        self.assertEqual(self.code(tematy.load_topic, self.f['topic']), 2)

    def test_operator_layers(self):
        for bad in ([], ['T2', 'T2'], ['T2', 'D'], ['t2'], 'T2'):
            rewrite(self.f['config'], lambda v: v.update(operator_warstwy=bad))
            self.assertEqual(self.code(tematy.load_method, self.f['config']), 2, bad)
        rewrite(self.f['config'], lambda v: v.update(operator_warstwy=['T2', 'T3']))
        self.assertEqual(tematy.load_method(self.f['config'])['config']['operator_warstwy'], ['T2', 'T3'])

    def test_real_method_and_sea_topic_load(self):
        # Prawdziwe pliki: teksty i ich hashe z repozytorium (bez fikstury).
        method = tematy.load_method(CONFIG/'tematy.json')
        self.assertEqual((method['config']['version'], method['config']['adr']),
                         ('tematy-v2', 'docs/adr/ADR-012-tematy-fala-1.md'))
        self.assertEqual(method['config']['operator_warstwy'], ['T2', 'T3'])
        topic = tematy.load_topic(CONFIG/'tematy/morze.json')
        self.assertEqual((topic['wersja'], len(topic['dodatki']), topic['wykluczenia']), ('morze-v2', 6, []))
        self.assertEqual(set(topic['t3']), {'iate'})

    def test_part_of_speech_code_outside_the_map(self):
        rewrite(self.f['config'], lambda v: v['czesci_mowy'].update({'5': ['subst']}))
        self.assertEqual(self.code(tematy.load_method, self.f['config']), 2)

    def test_wrong_text_hash_is_code_3(self):
        (self.f['texts']/'TERMS.md').write_text('# Zmieniony\n', encoding='utf-8')
        self.assertEqual(self.code(tematy.load_method, self.f['config']), 3)


if __name__ == '__main__':
    unittest.main()
