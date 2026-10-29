"""Pliki 9 tematów pierwszej fali (#12, W10.5 i W11): tylko konfiguracja i zamrożone listy słów."""
import json
import unittest

from literaki_slownik import tematy
from tests.tematy_helpers import CONFIG, ROOT

FALA = ('zwierzeta', 'rosliny', 'medycyna', 'muzyka', 'kuchnia', 'sport', 'matematyka', 'pogoda', 'grzyby')
SLOWA = ROOT/'.maister/tasks/development/2026-10-29-12-tematy-fala-1/analysis/slowa-oczywiste.json'


def topics():
    return {i: tematy.load_topic(CONFIG/'tematy'/f'{i}.json') for i in FALA}


class TematyFalaTest(unittest.TestCase):
    def test_each_topic_loads_with_id_and_first_version(self):
        for ident, topic in topics().items():
            with self.subTest(ident):
                self.assertEqual((topic['id'], topic['wersja']), (ident, f'{ident}-v1'))
                self.assertEqual(topic['t2']['tryb'], 'pelne')

    def test_obvious_words_equal_the_frozen_file(self):
        wynik = json.loads(SLOWA.read_text(encoding='utf-8'))['wynik']
        self.assertEqual(set(wynik), set(FALA))
        for ident, topic in topics().items():
            with self.subTest(ident):
                self.assertEqual(topic['diagnostyka']['slowa_oczywiste'], wynik[ident])

    def test_only_medicine_has_t3_and_nobody_has_inland_marks_or_d_layer(self):
        loaded = topics()
        self.assertEqual({i for i, t in loaded.items() if 't3' in t}, {'medycyna'})
        self.assertEqual(loaded['medycyna']['t3']['iate']['kody_dziedzin'], ['2841'])
        for ident, topic in loaded.items():
            with self.subTest(ident):
                self.assertNotIn('znaczniki_srodladowe', topic['diagnostyka'])
                self.assertEqual((topic['dodatki'], topic['wykluczenia']), ([], []))


if __name__ == '__main__':
    unittest.main()
