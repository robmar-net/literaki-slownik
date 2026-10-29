"""Pliki 9 tematów pierwszej fali (#12, W10.5 i W11; v2 z #13): konfiguracja i zamrożone listy słów."""
import json
import unittest

from literaki_slownik import tematy
from tests.tematy_helpers import CONFIG, ROOT

FALA = ('zwierzeta', 'rosliny', 'medycyna', 'muzyka', 'kuchnia', 'sport', 'matematyka', 'pogoda', 'grzyby')
SLOWA = ROOT/'.maister/tasks/development/2026-10-29-12-tematy-fala-1/analysis/slowa-oczywiste.json'


def topics():
    return {i: tematy.load_topic(CONFIG/'tematy'/f'{i}.json') for i in FALA}


# v2 z bramki #12 (#13, ADR-013): dodatki D (lemat → klasa) i wykluczenia (lematy, klasa subst).
V2 = {
    'grzyby': ({'blaszka': 'subst', 'drożdże': 'subst', 'grzybiarz': 'subst', 'grzybobranie': 'subst',
                'jadalny': 'adj', 'nóżka': 'subst', 'trujący': 'adj', 'trzon': 'subst', 'zielonka': 'subst'},
               ('flagowiec', 'megaspora', 'monada', 'promiennik', 'zrywka')),
    'pogoda': ({'chłód': 'subst', 'deszczowy': 'adj', 'pochmurny': 'adj', 'słoneczny': 'adj', 'susza': 'subst',
                'temperatura': 'subst', 'wilgoć': 'subst'}, ()),
    'sport': ({'biegać': 'inf', 'boisko': 'subst', 'bramka': 'subst', 'drużyna': 'subst', 'gol': 'subst',
               'kibic': 'subst', 'medal': 'subst', 'mistrz': 'subst', 'narta': 'subst', 'rakieta': 'subst',
               'rower': 'subst', 'stadion': 'subst', 'trener': 'subst', 'zwycięstwo': 'subst'}, ()),
    'matematyka': ({}, ('deniwelacja', 'eksport', 'hasło', 'kolur', 'oszczędności', 'wwóz')),
    'muzyka': ({}, ('pokrywa', 'różaniec', 'zakrętka')),
    'kuchnia': ({}, ('cytoplazma', 'sadzeniak', 'tyrozynaza')),
    'medycyna': ({}, ('gladius', 'indywiduacja', 'macka', 'mizogin', 'numulit', 'pantofelek', 'skrzele')),
}


class TematyFalaTest(unittest.TestCase):
    def test_each_topic_loads_with_id_and_version(self):
        for ident, topic in topics().items():
            with self.subTest(ident):
                self.assertEqual((topic['id'], topic['wersja']), (ident, f'{ident}-v{2 if ident in V2 else 1}'))
                self.assertEqual(topic['t2']['tryb'], 'pelne')

    def test_obvious_words_equal_the_frozen_file(self):
        wynik = json.loads(SLOWA.read_text(encoding='utf-8'))['wynik']
        self.assertEqual(set(wynik), set(FALA))
        for ident, topic in topics().items():
            with self.subTest(ident):
                self.assertEqual(topic['diagnostyka']['slowa_oczywiste'], wynik[ident])

    def test_no_topic_has_t3_or_inland_marks(self):
        # Medycyna v2 bez IATE (bramka #12).
        for ident, topic in topics().items():
            with self.subTest(ident):
                self.assertNotIn('t3', topic)
                self.assertNotIn('znaczniki_srodladowe', topic['diagnostyka'])

    def test_v2_additions_and_exclusions_follow_the_gate(self):
        for ident, topic in topics().items():
            dodatki, wykluczenia = V2.get(ident, ({}, ()))
            with self.subTest(ident):
                self.assertEqual({d['lemat']: d['czesc_mowy'] for d in topic['dodatki']}, dodatki)
                self.assertEqual([(w['lemat'], w['czesc_mowy']) for w in topic['wykluczenia']],
                                 [(w, 'subst') for w in wykluczenia])
                # Dodatek D to brakujące słowo oczywiste tematu.
                self.assertLessEqual(set(dodatki), set(topic['diagnostyka']['slowa_oczywiste']))

if __name__ == '__main__':
    unittest.main()
