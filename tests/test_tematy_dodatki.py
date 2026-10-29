"""Ręczne dodatki TEMATY: warstwa D (#11, grupa 16, ADR-010 poprawka 2026-10-29)."""
import gzip
import tempfile
import unittest

from literaki_slownik import tematy
from literaki_slownik.canonical import load_json
from literaki_slownik.inputs import GeneratorError
from tests.tematy_helpers import SOURCE, inputs_fixture, load_script, rewrite

checker = load_script('check_tematy_package')
KOT = {'lemat': 'kot', 'czesc_mowy': 'subst', 'powód': 'test dodatku'}


def label(lemma_id):
    return lemma_id + '@' + SOURCE


def with_addenda(f, items):
    rewrite(f['topic'], lambda v: (v.update(dodatki=items), v.update(wersja='morze-v2')))


class TematyDodatkiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.f = inputs_fixture(cls.tmp.name)
        cls.root = cls.f['root']
        # Budowa bez dodatków (wzorzec próby), potem z dodatkiem `kot` (poza T1–T3, w POP i POP0).
        tematy.build_package(cls.f['manifest'], cls.f['config'], cls.f['topic'], cls.root/'bez')
        with_addenda(cls.f, [KOT])
        cls.result = tematy.build_package(cls.f['manifest'], cls.f['config'], cls.f['topic'], cls.root/'z')
        cls.summary = load_json(cls.root/'z/reports/summary.json')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def entries_error(self, items):
        with_addenda(self.f, items)
        try:
            data = tematy.check_inputs(self.f['manifest'], self.f['config'], self.f['topic'])
            with self.assertRaises(GeneratorError) as caught:
                tematy.build_entries(data, tematy.candidates(data))
            return caught.exception.code
        finally:
            with_addenda(self.f, [KOT])

    def test_topic_accepts_addenda_and_vn_version_but_not_the_same_pair_excluded(self):
        topic = tematy.load_topic(self.f['topic'])
        self.assertEqual((topic['wersja'], topic['dodatki']), ('morze-v2', [KOT]))
        for change in (lambda v: v.update(wersja='morze-v'), lambda v: v.update(wersja='morze-2'),
                       lambda v: v.update(wykluczenia=[KOT]), lambda v: v.update(dodatki=[KOT, KOT])):
            rewrite(self.f['topic'], change)
            with self.assertRaises(GeneratorError) as caught:
                tematy.load_topic(self.f['topic'])
            self.assertEqual(caught.exception.code, 2)
            with_addenda(self.f, [KOT])
            rewrite(self.f['topic'], lambda v: v.update(wykluczenia=[]))

    def test_addendum_is_its_own_layer_d_with_forms_in_standard(self):
        rows = gzip.decompress((self.root/'z/MORZE.tsv.gz').read_bytes()).decode().splitlines()
        row = dict(zip(tematy.TSV_KOLUMNY, next(r for r in rows if r.startswith(label('kot') + '\t')).split('\t')))
        self.assertEqual((row['warstwa'], row['zrodla'], row['znaczenie'], row['formy']),
                         ('D', 'D', 'D: test dodatku', '3'))
        self.assertIn(row['wieloznaczny'], tematy.WIELOZNACZNY)
        n = self.summary['liczby']
        self.assertEqual(n['warstwy'], {'T1': 4, 'T2': 4, 'T3': 1, 'D': 1})
        self.assertEqual(n['wpisy'], 10)
        lex = self.summary['przeciecia']['leksemy']
        self.assertEqual((lex['D']['temat'], lex['D']['pop']['liczba'], lex['D']['pop00']['liczba']), (1, 1, 1))
        self.assertEqual(lex['razem']['temat'], 10)
        self.assertIn('| D | 1 |', (self.root/'z/reports/raport.md').read_text(encoding='utf-8'))

    def test_r2_sample_ignores_layer_d_and_keeps_t1_t3_bytes(self):
        sample = load_json(self.root/'z/reports/sample.json')
        self.assertEqual(set(sample['strata']), {'T1', 'T2', 'T3'})
        self.assertNotIn(label('kot'), {i['key'] for i in sample['items']})
        self.assertEqual((self.root/'z/reports/sample.json').read_bytes(),
                         (self.root/'bez/reports/sample.json').read_bytes())

    def test_obvious_words_count_layer_d(self):
        wpisy = {'a': {'warstwa': 'T1', 'lemat': 'kil'}, 'b': {'warstwa': 'D', 'lemat': 'kot'}}
        words = tematy.slowa_oczywiste(['kil', 'kot'], wpisy, tematy.Fraction(1))
        self.assertEqual((words['razem']['pokryte'], words['T1_T2']['pokryte'], words['spelniony']), (2, 1, True))

    def test_bad_addendum_is_code_4(self):
        cases = {
            'poza STANDARD': [{'lemat': 'szkuta', 'czesc_mowy': 'subst', 'powód': 'x'}],
            'brak leksemu': [{'lemat': 'kotwica', 'czesc_mowy': 'subst', 'powód': 'x'}],
            'zła część mowy': [{'lemat': 'kot', 'czesc_mowy': 'inf', 'powód': 'x'}],
            'już w T2': [{'lemat': 'statek', 'czesc_mowy': 'subst', 'powód': 'x'}],
            'kilka leksemów': [{'lemat': 'kuter', 'czesc_mowy': 'subst', 'powód': 'x'}],
        }
        for name, items in cases.items():
            self.assertEqual(self.entries_error(items), 4, name)

    def test_checker_passes_and_counts_layer_d(self):
        report = checker.check(self.root/'z', self.f['manifest'], self.f['config'])
        self.assertEqual((report['status'], report['wpisy']), ('pass', 10))
        self.assertEqual(report['warstwy'], {'T1': 4, 'T2': 4, 'T3': 1, 'D': 1})


if __name__ == '__main__':
    unittest.main()
