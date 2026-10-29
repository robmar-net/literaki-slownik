"""Teksty z odcinkami T3 i SRODLADOWE oraz raport zależny od tematu (#12 W4, W8)."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from literaki_slownik import tematy
from literaki_slownik.canonical import load_json
from tests.tematy_helpers import CONFIG, inputs_fixture, rewrite, set_text

TEKSTY = CONFIG/'tematy-teksty'
# Hashe tekstów pakietu morza `tematy-v2-20261029-a` (przed odcinkami); morze ma T3 i znaczniki.
STARE = {'ATTRIBUTIONS-tematy.md': 'd667315606d06a79c3dac617127641fb09fb4483e1919559a1c1e7f236d85f4e',
         'TERMS.md': 'b42502890ca2c830da72652360e3db8b6f131bf4bf9e02379f99a86f234c9651',
         'LIMITATIONS.md': 'faca2603d2005fe183785a70924351f6ce2f70ed1c2b79863f6571b70efe2b4d'}
# Jedyne zmiany treści LIMITATIONS.md (W4): punkt T2 bez przykładów morza, punkt T3 bez „T3 jest mała”.
PUNKTY = (
    ('- T2 to pełne domknięcie od ręcznie wybranych korzeni. Daje szum (np. `angora`, `bungee`). '
     'Korzenie wybrał jeden oceniający.',
     '- T2 to pełne domknięcie od ręcznie wybranych korzeni. Daje szum; przykłady w `reports/raport.md` '
     'i próbie R2. Korzenie wybrał jeden oceniający.'),
    ('- T3 jest mała: IATE ma niewiele polskich terminów jednowyrazowych w dziedzinie tematu. '
     'Dane IATE pochodzą z 2019 r.',
     '- T3 to polskie terminy jednowyrazowe IATE z dziedzin tematu; liczba w `reports/raport.md`. '
     'Dane IATE pochodzą z 2019 r.'),
)
OBA = {'T3', 'SRODLADOWE'}


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def real(name):
    return (TEKSTY/name).read_text(encoding='utf-8')


def build(f, out):
    tematy.build_package(f['manifest'], f['config'], f['topic'], out)
    return out


class TematyTekstyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_kept_segments_give_old_attributions_and_terms_bytes(self):
        for name in ('ATTRIBUTIONS-tematy.md', 'TERMS.md'):
            self.assertIn('<!--T3-->', real(name), name)  # kontrola pozytywna: plik ma odcinek
            self.assertEqual(sha(tematy.odcinki(real(name), OBA)), STARE[name], name)

    def test_limitations_differ_from_old_only_in_t2_and_t3_points(self):
        text = tematy.odcinki(real('LIMITATIONS.md'), OBA)
        for old, new in PUNKTY:
            self.assertEqual(text.count(new), 1, new)
            text = text.replace(new, old)
        self.assertEqual(sha(text), STARE['LIMITATIONS.md'])

    def test_topic_without_t3_has_no_iate_and_no_inland_text(self):
        f = inputs_fixture(self.root, t3=False, temat='zwierzeta')
        out = build(f, self.root/'pkg')
        for name in ('ATTRIBUTIONS.md', 'LIMITATIONS.md', 'TERMS.md'):
            text = (out/name).read_text(encoding='utf-8')
            self.assertNotIn('IATE', text, name)
            for bad in ('śródląd', '<!--', '@@'):
                self.assertNotIn(bad, text.lower(), name)
        # Kontrola pozytywna: zostały teksty spoza odcinków.
        self.assertIn('Słowosieć', (out/'ATTRIBUTIONS.md').read_text(encoding='utf-8'))
        self.assertIn(PUNKTY[0][1], (out/'LIMITATIONS.md').read_text(encoding='utf-8'))

    def test_broken_segments_and_marker_are_code_2(self):
        for text in ('a<!--T3-->b', 'a<!--/T3-->', '<!--T3-->a<!--SRODLADOWE-->b<!--/SRODLADOWE--><!--/T3-->',
                     '<!--T3-->a<!--/SRODLADOWE-->', '<!--INNY-->a<!--/INNY-->', 'a<!-- T3 -->'):
            for keep in (set(), OBA):
                with self.assertRaises(tematy.GeneratorError, msg=text) as caught:
                    tematy.odcinki(text, keep)
                self.assertEqual(caught.exception.code, 2, text)
        good = {name: real(name) for name in tematy.TEKSTY}
        limits = good['LIMITATIONS.md']
        topic = {'t3': {}, 'diagnostyka': {'znaczniki_srodladowe': {}}}
        for name, text in (('LIMITATIONS.md', limits.replace(tematy.ZNACZNIK, '')),
                           ('LIMITATIONS.md', limits.replace(tematy.ZNACZNIK, tematy.ZNACZNIK * 2)),
                           ('LIMITATIONS.md', limits.replace(tematy.ZNACZNIK, '') + tematy.ZNACZNIK + '\n'),
                           ('TERMS.md', good['TERMS.md'] + tematy.ZNACZNIK)):
            with self.assertRaises(tematy.GeneratorError) as caught:
                tematy.teksty_pakietu({**good, name: text}, topic)
            self.assertEqual(caught.exception.code, 2, text[-80:])
        # Ta sama kontrola w budowie: niezamknięty odcinek daje kod 2 i nie zostawia pakietu.
        f = inputs_fixture(self.root)
        set_text(f, 'TERMS.md', real('TERMS.md').replace('<!--/T3-->', ''))
        with self.assertRaises(tematy.GeneratorError) as caught:
            build(f, self.root/'pkg')
        self.assertEqual(caught.exception.code, 2)
        self.assertFalse((self.root/'pkg').exists())
        self.assertFalse(list(self.root.glob('.pkg.staging-*')))

    def test_t3_without_markers_has_no_inland_report(self):
        f = inputs_fixture(self.root)
        rewrite(f['topic'], lambda v: v['diagnostyka'].pop('znaczniki_srodladowe'))
        out = build(f, self.root/'pkg')
        summary = load_json(out/'reports/summary.json')
        self.assertIsNone(summary['srodladowe'])
        self.assertGreater(summary['t3']['hasla_kandydaci'], 0)
        raport = (out/'reports/raport.md').read_text(encoding='utf-8')
        self.assertNotIn('Śródlądowe', raport)
        self.assertNotIn('Żegluga śródlądowa', raport)
        self.assertIn('- T3: hasła z kodem dziedziny', raport)
        limits = (out/'LIMITATIONS.md').read_text(encoding='utf-8')
        self.assertNotIn('śródląd', limits.lower())
        self.assertIn(PUNKTY[1][1], limits)
        self.assertIn('## IATE', (out/'ATTRIBUTIONS.md').read_text(encoding='utf-8'))

    def test_other_topic_report_and_messages_use_its_id(self):
        f = inputs_fixture(self.root, t3=False, temat='zwierzeta')
        out = build(f, self.root/'pkg')
        summary = load_json(out/'reports/summary.json')
        self.assertIsNone(summary['t3'])
        raport = (out/'reports/raport.md').read_text(encoding='utf-8')
        self.assertNotIn('MORZE', raport)
        self.assertIn('formy w ZWIERZETA', raport)
        self.assertNotIn('T1 < T2 < T3', raport)
        self.assertIn('najniższa z T1 < T2;', raport)
        for line in ('- T3: hasła', '- T3 termType', 'Wpisy T3:', 'Śródlądowe', 'T1 ∪ T2 ∪ T3'):
            self.assertNotIn(line, raport)
        entry = {'lemat': 'a', 'czesci_mowy': ['subst'], 'warstwa': 'T2', 'zrodla': ['T2'], 'znaczenie': {},
                 'wieloznaczny': 'nie', 'formy': ['a']}
        with self.assertRaisesRegex(ValueError, 'ZWIERZETA.tsv'):
            tematy._tsv_rows({'a\tb': entry}, 'ZWIERZETA')
        # Literał MORZE w kodzie tylko w komentarzach (kryterium grupy 5).
        source = Path(tematy.__file__).read_text(encoding='utf-8').splitlines()
        self.assertEqual([s for s in source if 'MORZE' in s and not s.lstrip().startswith('#')], [])


if __name__ == '__main__':
    unittest.main()
