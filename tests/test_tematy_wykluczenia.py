"""Wykluczenia lematów i poddrzew TEMATY (#12 W1, W3)."""
import gzip
import tempfile
import unittest
from pathlib import Path

from literaki_slownik import tematy
from literaki_slownik.canonical import load_json
from tests.tematy_helpers import SOURCE, inputs_fixture, rewrite


def label(lemma_id):
    return lemma_id + '@' + SOURCE


def exclusion(lemat, czesc_mowy):
    return {'lemat': lemat, 'czesc_mowy': czesc_mowy, 'powód': 'ocena R2'}


class TematyWykluczeniaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.f = inputs_fixture(self.tmp.name)
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, name='pkg'):
        return tematy.build_package(self.f['manifest'], self.f['config'], self.f['topic'], self.root/name)

    def code(self):
        with self.assertRaises(tematy.GeneratorError) as caught:
            self.build()
        self.assertFalse((self.root/'pkg').exists())
        return caught.exception.code

    def test_exclusion_removes_lexemes_of_every_layer(self):
        # `kuter`: leksem T1+T2 i homonim `kuter:S2` (T2); `barka`: T3.
        rewrite(self.f['topic'], lambda v: v.update(wykluczenia=[exclusion('kuter', 'subst'),
                                                                  exclusion('barka', 'subst')]))
        self.build()
        rows = gzip.decompress((self.root/'pkg/MORZE.tsv.gz').read_bytes()).decode().splitlines()[1:]
        keys = [r.split('\t')[0] for r in rows]
        self.assertEqual(len(keys), 6)
        self.assertFalse({label('kuter'), label('kuter:S2'), label('barka')} & set(keys))
        summary = load_json(self.root/'pkg/reports/summary.json')
        self.assertEqual(summary['wykluczenia'], [
            {**exclusion('kuter', 'subst'), 'klucze': [label('kuter:S2'), label('kuter')], 'warstwy': ['T1', 'T2']},
            {**exclusion('barka', 'subst'), 'klucze': [label('barka')], 'warstwy': ['T3']}])
        self.assertEqual(summary['liczby']['warstwy'], {'T1': 3, 'T2': 3, 'T3': 0, 'D': 0})
        report = (self.root/'pkg/reports/raport.md').read_text(encoding='utf-8')
        self.assertIn('## Wykluczenia', report)
        self.assertIn('kuter (subst): ocena R2', report)

    def test_report_has_no_exclusion_section_when_list_is_empty(self):
        self.build()
        self.assertEqual(load_json(self.root/'pkg/reports/summary.json')['wykluczenia'], [])
        self.assertNotIn('Wykluczenia', (self.root/'pkg/reports/raport.md').read_text(encoding='utf-8'))

    def test_exclusion_without_candidate_is_code_4(self):
        # `kot` nie jest kandydatem morza; `żeglować` jest, ale bez klasy `subst`.
        for item in (exclusion('kot', 'subst'), exclusion('żeglować', 'subst')):
            rewrite(self.f['topic'], lambda v: v.update(wykluczenia=[item]))
            self.assertEqual(self.code(), 4, item)

    def test_unreachable_subtree_exclusion_is_code_4(self):
        # Synset 500 (`kot 1`) istnieje, ale nie wychodzi z korzeni morza.
        rewrite(self.f['topic'], lambda v: v['t2'].update(
            wykluczenia_poddrzew=[{'synset': 500, 'nazwa': 'kot 1', 'powód': 'test'}]))
        self.assertEqual(self.code(), 4)
        # Kontrola pozytywna: osiągalne poddrzewo `kuter 1` przechodzi i znika z T2.
        rewrite(self.f['topic'], lambda v: v['t2'].update(
            wykluczenia_poddrzew=[{'synset': 900, 'nazwa': 'kuter 1', 'powód': 'test'}]))
        self.build()
        summary = load_json(self.root/'pkg/reports/summary.json')
        self.assertEqual(summary['liczby']['warstwy']['T2'], 3)


if __name__ == '__main__':
    unittest.main()
