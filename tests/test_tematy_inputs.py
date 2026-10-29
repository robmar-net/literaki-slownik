"""Wejścia TEMATY i rejestr czytanych plików (#11, W3, W6; #12 W2)."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote

from literaki_slownik import tematy
from literaki_slownik.canonical import load_json, sha256
from literaki_slownik.pop import write_gzip
from tests.tematy_helpers import inputs_fixture, rewrite

OPENED = None  # zbiór ścieżek otwartych w trakcie pomiaru; None = hak nieaktywny


def _audit(event, args):
    if OPENED is None:
        return
    if event == 'open' and isinstance(args[0], (str, bytes, Path)):
        OPENED.add(Path(args[0] if not isinstance(args[0], bytes) else args[0].decode()))
    elif event == 'sqlite3.connect':
        name = str(args[0])
        OPENED.add(Path(unquote(name.removeprefix('file:').split('?')[0])))


sys.addaudithook(_audit)


class TematyInputsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.f = inputs_fixture(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def check(self):
        return tematy.check_inputs(self.f['manifest'], self.f['config'], self.f['topic'])

    def code(self):
        with self.assertRaises(tematy.GeneratorError) as caught:
            self.check()
        return caught.exception.code

    def repin(self, key):
        path = self.f['paths'][key]
        rewrite(self.f['manifest'], lambda v: v['inputs'][key].update(sha256=sha256(path)))

    def test_valid_fixture_passes(self):
        data = self.check()
        self.assertEqual(data['standard'], data['broad'] - {'szkuta'})
        self.assertEqual(data['pop'], {'kot', 'kotem', 'statek'})
        self.assertEqual(data['pop00'], {'kot'})
        self.assertEqual(data['members'], {'POP': {'kot@sgjp', 'statek@sgjp'}, 'POP0': {'kot@sgjp'}})
        self.assertIn('SGJP', data['attribution'])
        self.assertEqual(data['topic']['id'], 'morze')
        tematy.confirm_unchanged(data)

    def test_run_not_frozen_is_code_5(self):
        rewrite(self.f['paths']['base_run'], lambda v: v.update(readiness='BUILT'))
        self.repin('base_run')
        self.assertEqual(self.code(), 5)

    def test_release_manifest_binding_is_code_3(self):
        # Manifest wydania przypięty w źródłach, ale nie ten, który eksportował przebieg.
        rewrite(self.f['paths']['release_manifest'], lambda v: v.update(note='inny'))
        self.repin('release_manifest')
        self.assertEqual(self.code(), 3)
        # Przebieg wskazuje manifest, ale BROAD w manifeście ma inny hash niż przypięty.
        rewrite(self.f['paths']['release_manifest'],
                lambda v: v['files']['LL-PL-BROAD.txt'].update(sha256='b' * 64))
        self.repin('release_manifest')
        rewrite(self.f['paths']['base_run'], lambda v: v['export'].update(
            release_manifest_sha256=sha256(self.f['paths']['release_manifest'])))
        self.repin('base_run')
        self.assertEqual(self.code(), 3)

    def test_derivative_meta_must_match_zip_pin(self):
        rewrite(self.f['manifest'], lambda v: v['inputs']['plwordnet_zip'].update(sha256='f' * 64))
        self.assertEqual(self.code(), 3)

    def test_file_inside_pop_package_changed_after_check_is_code_5(self):
        data = self.check()
        write_gzip(self.f['pop']/'POP.txt.gz', ['kot', 'statek'])
        with self.assertRaises(tematy.GeneratorError) as caught:
            tematy.confirm_unchanged(data)
        self.assertEqual(caught.exception.code, 5)

    def test_every_opened_file_is_registered(self):
        global OPENED
        OPENED = set()
        try:
            data = self.check()
        finally:
            opened, OPENED = OPENED, None
        root = Path(self.tmp.name).resolve()
        opened = {p.resolve() for p in opened if root in p.resolve().parents}
        registry = set(data['registry'])
        f = self.f
        expected = {f['manifest'], f['config'], f['topic'], *(f['texts']/n for n in tematy.TEKSTY),
                    *f['paths'].values(), *(f['pop']/n for n in ('POP.txt.gz', 'reports/units.json',
                                                                  'ATTRIBUTIONS.md')),
                    f['pop00']/'POP00.txt.gz'}
        self.assertEqual(registry, {Path(p).resolve() for p in expected})
        # Kontrola pozytywna: hak widzi zwykłe pliki, gzip i SQLite.
        self.assertLessEqual({Path(p).resolve() for p in (f['paths']['plwordnet_db'], f['pop']/'POP.txt.gz',
                                                           f['manifest'])}, opened)
        self.assertLessEqual(opened, registry)
        self.assertTrue(all(sha256(p) == h for p, h in data['registry'].items()))



class TematyTopicInputsTest(unittest.TestCase):
    """#12 W2: IATE tylko przy `t3`; manifest pakietu z użytymi wejściami."""

    def build(self, tmp, **kwargs):
        f = inputs_fixture(tmp, **kwargs)
        global OPENED
        OPENED = set()
        try:
            data = tematy.check_inputs(f['manifest'], f['config'], f['topic'])
            tematy.build_package(f['manifest'], f['config'], f['topic'], Path(tmp)/'pkg')
        finally:
            opened, OPENED = OPENED, None
        return f, data, opened, load_json(Path(tmp)/'pkg/release-manifest.json')

    def test_topic_without_t3_skips_iate(self):
        with tempfile.TemporaryDirectory() as tmp:
            f, data, opened, manifest = self.build(tmp, t3=False, temat='zwierzeta')
            iate = f['paths']['iate'].resolve()
            self.assertNotIn(iate, set(data['registry']))
            self.assertNotIn('iate', data['paths'])
            # Kontrola pozytywna: hak widział bazę; zip IATE nie był otwierany.
            self.assertIn(f['paths']['database'].resolve(), {p.resolve() for p in opened})
            self.assertNotIn(iate, {p.resolve() for p in opened})
            self.assertEqual(set(manifest['inputs']), set(tematy.INPUTS) - {'iate'})
            self.assertNotIn('iate', manifest)
            summary = load_json(Path(tmp)/'pkg/reports/summary.json')
            self.assertEqual(summary['liczby']['warstwy'], {'T1': 0, 'T2': 1, 'T3': 0, 'D': 0})
            self.assertIsNone(summary['srodladowe'])
            self.assertTrue((Path(tmp)/'pkg/ZWIERZETA.txt.gz').is_file())
            with patch.object(tematy, 't3_candidates', side_effect=AssertionError('IATE')) as t3:
                cands = tematy.candidates(data)
            t3.assert_not_called()
            self.assertEqual((cands['t3']['terminy'], cands['t3']['hasla']), ({}, {}))

    def test_topic_with_t3_keeps_iate_block_and_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            f, data, opened, manifest = self.build(tmp)
            refs = load_json(f['manifest'])['inputs']
            self.assertEqual(manifest['iate'], {k: refs['iate'][k] for k in ('member', 'last_modified', 'bytes')})
            self.assertEqual(manifest['inputs'], {k: refs[k]['sha256'] for k in tematy.INPUTS})
            self.assertIn(f['paths']['iate'].resolve(), set(data['registry']))


if __name__ == '__main__':
    unittest.main()
