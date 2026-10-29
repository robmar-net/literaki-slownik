"""Wykluczenia lematów i poddrzew TEMATY (#12 W1, W3)."""
import gzip
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from literaki_slownik import tematy
from literaki_slownik.canonical import load_json
from tests import tematy_helpers
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

    def test_addendum_on_an_excluded_lexeme_is_code_4(self):
        # Para różna od wykluczenia (load_topic przechodzi), ale ten sam leksem `żeglować` (inf i ger).
        rewrite(self.f['topic'], lambda v: v.update(
            wykluczenia=[exclusion('żeglować', 'inf')],
            dodatki=[{'lemat': 'żeglować', 'czesc_mowy': 'ger', 'powód': 'test'}]))
        tematy.load_topic(self.f['topic'])
        with self.assertRaises(tematy.GeneratorError) as caught:
            self.build()
        self.assertEqual(caught.exception.code, 4)
        self.assertIn('wykluczony', str(caught.exception))
        self.assertFalse((self.root/'pkg').exists())

    def test_addendum_on_a_homonym_of_an_excluded_lemma_is_code_4(self):
        # Wykluczenie jest bezwzględne (#13, ADR-013). `bosman` (T1, subst) wykluczony; homonim `bosman:A`
        # (adj i subst, poza T1–T3) jako dodatek adj ma klasę subst wykluczenia, więc checker by go odrzucił.
        homonym = [('bosmański', 'bosman:A', 'adj:sg:nom:m1:pos', ''), ('bosmana', 'bosman:A', 'subst:sg:gen:m1', '')]
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(tematy_helpers, 'SGJP', tematy_helpers.SGJP + homonym):
            self.f, self.root = inputs_fixture(tmp), Path(tmp)
            rewrite(self.f['topic'], lambda v: v.update(
                wykluczenia=[exclusion('bosman', 'subst')],
                dodatki=[{'lemat': 'bosman', 'czesc_mowy': 'adj', 'powód': 'test'}]))
            tematy.load_topic(self.f['topic'])
            with self.assertRaises(tematy.GeneratorError) as caught:
                self.build()
            self.assertEqual(caught.exception.code, 4)
            self.assertIn('wykluczony', str(caught.exception))
            self.assertFalse((self.root/'pkg').exists())
            # Kontrola pozytywna: bez wykluczenia ten sam dodatek przechodzi jako D.
            rewrite(self.f['topic'], lambda v: v.update(wykluczenia=[]))
            self.build()
            summary = load_json(self.root/'pkg/reports/summary.json')
            self.assertEqual(summary['liczby']['warstwy']['D'], 1)

    def test_topic_with_t3_and_empty_t3_keeps_t3_tak_applicable_in_summary(self):
        # Pusta T3 przy temacie z `t3` to błąd konfiguracji: `t3_tak` nie może zniknąć jako `nie_dotyczy` (W6).
        rewrite(self.f['topic'], lambda v: v.update(wykluczenia=[exclusion('barka', 'subst')]))
        self.build()
        summary = load_json(self.root/'pkg/reports/summary.json')
        self.assertEqual(summary['liczby']['warstwy']['T3'], 0)
        self.assertIsNotNone(summary['t3'])
        self.assertEqual(summary['werdykt']['nie_dotyczy'], [])
        self.assertIn('t3_tak', summary['werdykt']['czeka_na_ocene'] + summary['werdykt']['niespelnione'])
        sample = load_json(self.root/'pkg/reports/sample.json')
        self.assertEqual(sample['strata']['T3']['coverage'], 'EMPTY_NOT_COVERAGE')
        self.assertEqual(sample['operator']['strata']['T3'], [])


if __name__ == '__main__':
    unittest.main()
