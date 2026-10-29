"""Konfiguracja TEMATY: metoda, temat i manifest wejść (#11, W3–W5)."""
import tempfile
import unittest

from literaki_slownik import tematy
from literaki_slownik.inputs import GeneratorError
from tests.tematy_helpers import config_fixture, rewrite


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
        self.assertEqual(method['config']['version'], 'tematy-v1')
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

    def test_lemma_exclusions_must_be_empty_and_addenda_are_allowed(self):
        # ADR-010 (poprawka 2026-10-29): dodatki tworzą warstwę D; wykluczeń budowa nie czyta (kod 2).
        rewrite(self.f['topic'], lambda v: v['t3'].update(
            dodatki=[{'lemat': 'kot', 'czesc_mowy': 'subst', 'powód': 'test'}]))
        tematy.load_topic(self.f['topic'])
        rewrite(self.f['topic'], lambda v: v.update(
            wykluczenia=[{'lemat': 'kot', 'czesc_mowy': 'subst', 'powód': 'test'}]))
        self.assertEqual(self.code(tematy.load_topic, self.f['topic']), 2)
        rewrite(self.f['topic'], lambda v: v.update(wykluczenia=[]))
        tematy.load_topic(self.f['topic'])

    def test_part_of_speech_code_outside_the_map(self):
        rewrite(self.f['config'], lambda v: v['czesci_mowy'].update({'5': ['subst']}))
        self.assertEqual(self.code(tematy.load_method, self.f['config']), 2)

    def test_wrong_text_hash_is_code_3(self):
        (self.f['texts']/'TERMS.md').write_text('# Zmieniony\n', encoding='utf-8')
        self.assertEqual(self.code(tematy.load_method, self.f['config']), 3)


if __name__ == '__main__':
    unittest.main()
