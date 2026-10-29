"""Raporty, próba, pakiet i CLI TEMATY (#11, W6, W8–W11, W15)."""
import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from literaki_slownik import tematy
from literaki_slownik.canonical import load_json, sha256
from tests.tematy_helpers import ROOT, SOURCE, inputs_fixture, rewrite

FILES = {'MORZE.txt.gz', 'MORZE.tsv.gz', 'tematy/morze.json', 'method.json', 'reports/summary.json',
         'reports/raport.md', 'reports/sample.json', 'reports/review-template.json', 'ATTRIBUTIONS.md',
         'LIMITATIONS.md', 'TERMS.md', 'release-manifest.json', 'SHA256SUMS'}


def label(lemma_id):
    return lemma_id + '@' + SOURCE


def build(f, out):
    return tematy.build_package(f['manifest'], f['config'], f['topic'], out)


class TematyPackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.f = inputs_fixture(cls.tmp.name)
        cls.root = cls.f['root']
        cls.a, cls.b = build(cls.f, cls.root/'a'), build(cls.f, cls.root/'b')
        cls.summary = load_json(cls.root/'a/reports/summary.json')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_two_builds_have_identical_sha256sums(self):
        sums = (self.root/'a/SHA256SUMS').read_bytes()
        self.assertEqual(sums, (self.root/'b/SHA256SUMS').read_bytes())
        self.assertEqual(self.a['release_manifest_sha256'], self.b['release_manifest_sha256'])
        self.assertEqual(sorted(line.split('  ', 1)[1] for line in sums.decode().splitlines()), sorted(FILES - {'SHA256SUMS'}))

    def test_package_files_modes_and_morze_list(self):
        out = self.root/'a'
        files = {p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()}
        self.assertEqual(files, FILES)
        self.assertTrue(all((out/p).stat().st_mode & 0o777 == 0o444 for p in files))
        words = gzip.decompress((out/'MORZE.txt.gz').read_bytes()).decode().splitlines()
        self.assertEqual(words, sorted(words))
        self.assertLessEqual(set(words), set((self.f['paths']['standard']).read_text().split()))
        self.assertIn('okrętże', words)
        rows = gzip.decompress((out/'MORZE.tsv.gz').read_bytes()).decode().splitlines()
        self.assertEqual(rows[0].split('\t'), list(tematy.TSV_KOLUMNY))
        self.assertEqual([r.split('\t')[0] for r in rows[1:]], sorted(r.split('\t')[0] for r in rows[1:]))
        self.assertEqual(len(rows) - 1, 9)
        manifest = load_json(out/'release-manifest.json')
        self.assertEqual((manifest['kind'], manifest['status'], manifest['counts']['morze']['wpisy']),
                         ('literaki-tematy-manifest', 'BUILT', 9))
        self.assertEqual(set(manifest['files']), FILES - {'release-manifest.json', 'SHA256SUMS'})
        limits = (out/'LIMITATIONS.md').read_text(encoding='utf-8')
        self.assertNotIn('@@', limits)
        self.assertIn('3 z 3', limits)
        self.assertIn('SGJP', (out/'ATTRIBUTIONS.md').read_text(encoding='utf-8'))
        self.assertEqual((out/'tematy/morze.json').read_bytes(), self.f['topic'].read_bytes())

    def test_summary_overlap_with_pop_and_pop00_matches_hand_counts(self):
        overlap = self.summary['przeciecia']
        # Wpisy: T1 bosman, kuter, reja, żeglować; T2 kuter:S2, okręt, statek, łódź; T3 barka.
        # POP: członkowie {kot, statek}; POP00 na poziomie leksemów = POP0 {kot}.
        lex = overlap['leksemy']
        self.assertEqual({w: lex[w]['temat'] for w in ('T1', 'T2', 'T3', 'razem')},
                         {'T1': 4, 'T2': 4, 'T3': 1, 'razem': 9})
        self.assertEqual(lex['razem']['pop'], {'liczba': 1, 'procent': '11.1'})
        self.assertEqual(lex['T2']['pop'], {'liczba': 1, 'procent': '25.0'})
        self.assertEqual(lex['T1']['pop'], {'liczba': 0, 'procent': '0.0'})
        self.assertTrue(all(lex[w]['pop00'] == {'liczba': 0, 'procent': '0.0'} for w in ('T1', 'T2', 'T3', 'razem')))
        self.assertEqual(lex['D'], {'temat': 0, 'pop': {'liczba': 0, 'procent': None},
                                    'pop00': {'liczba': 0, 'procent': None}})
        # Formy: T1 5, T2 7 (kutrem, okręt, okrętże, statek, statkiem, łódź, łodzią), T3 1, razem 13.
        forms = overlap['formy']
        self.assertEqual({w: forms[w]['temat'] for w in ('T1', 'T2', 'T3', 'razem')},
                         {'T1': 5, 'T2': 7, 'T3': 1, 'razem': 13})
        self.assertEqual(forms['razem']['pop'], {'liczba': 1, 'procent': '7.7'})
        self.assertEqual(forms['T2']['pop'], {'liczba': 1, 'procent': '14.3'})
        self.assertEqual(forms['razem']['pop00'], {'liczba': 0, 'procent': '0.0'})
        diag = self.summary['diagnostyka']['razem']['leksemy']
        self.assertEqual((diag['kandydaci'], diag['broad'], diag['standard']), (11, 10, 9))
        rejected = self.summary['odrzucone']['T2']
        self.assertEqual(rejected['BRAK_LEKSEMU']['ger'], {'liczba': 1, 'przyklady': ['żeglowanie']})
        self.assertEqual(rejected['POZA_STANDARD']['przyklady'], [label('szkuta')])

    def test_37_words_and_inland_share(self):
        words = self.summary['slowa_oczywiste']
        self.assertEqual(words['lista'], 37)
        self.assertEqual({k: words[k]['pokryte'] for k in ('razem', 'T1', 'T1_T2')}, {'razem': 5, 'T1': 3, 'T1_T2': 5})
        self.assertIn('kambuz', words['razem']['brakujace'])  # poza BROAD, więc nie jest wpisem
        self.assertNotIn('kuter', words['razem']['brakujace'])
        self.assertEqual(len(words['razem']['brakujace']), 32)
        self.assertEqual((words['prog'], words['spelniony']), ('0.70', False))
        verdict = self.summary['werdykt']
        self.assertEqual((verdict['automatyczny'], verdict['niespelnione']), ('popraw', ['slowa_oczywiste']))
        self.assertEqual(verdict['czeka_na_ocene'], ['t1_tak', 't2_tak', 't2_nie', 't3_tak', 'zgodnosc'])
        inland = self.summary['srodladowe']
        # IATE-1 (EN „inland”), IATE-4 (PL „statek rzeczny”), IATE-5 (PL „barka”, EN „barge”).
        self.assertEqual((inland['kandydaci_t3']['hasla'], inland['kandydaci_t3']['srodladowe']), (3, 3))
        self.assertEqual(inland['wpisy_t3']['srodladowe'], 1)
        self.assertEqual(tematy.srodladowe_hasla({'X': {'pl': ('molo',), 'en': ('blocking',)}},
                                                 {'pl': ['rzek'], 'en': ['lock']}), [])

    def test_sample_takes_min_50_and_operator_first_min_30_by_rank(self):
        method = load_json(self.f['config'])
        layers = {'T1': [f'a{i:03d}@s' for i in range(70)], 'T2': [f'b{i:03d}@s' for i in range(40)],
                  'T3': [f'c{i:03d}@s' for i in range(10)]}
        payloads = {k: {'key': k} for keys in layers.values() for k in keys}
        sample = tematy.sample(layers, payloads, method)
        sizes = {w: (s['population'], s['sample_size']) for w, s in sample['strata'].items()}
        self.assertEqual(sizes, {'T1': (70, 50), 'T2': (40, 40), 'T3': (10, 10)})
        for name, stratum in sample['strata'].items():
            ranked = [item['key'] for item in stratum['selected']]
            self.assertEqual(sample['operator']['strata'][name], ranked[:min(30, len(ranked))])
        self.assertEqual(sample['operator']['per_stratum'], 30)
        built = load_json(self.root/'a/reports/sample.json')
        self.assertEqual(built['operator']['strata']['T3'], [label('barka')])
        template = load_json(self.root/'a/reports/review-template.json')
        item = next(i for i in template['items'] if i['key'] == label('kuter'))
        self.assertEqual(item['selected_unit']['zrodla'], ['T1', 'T2'])
        self.assertEqual(item['selected_unit']['lemat'], 'kuter')

    def test_refusals_and_config_change_during_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = inputs_fixture(tmp)
            root = f['root']
            build(f, root/'out')
            for target, code in ((root/'out', 4), (f['run']/'bad', 2), (f['paths']['iate'].parent/'x', 2)):
                with self.assertRaises(tematy.GeneratorError) as caught:
                    build(f, target)
                self.assertEqual(caught.exception.code, code, target)
            original = tematy._write_package

            def change_config(*args, **kwargs):
                result = original(*args, **kwargs)
                rewrite(f['config'], lambda v: v.update(operator_per_stratum=29))
                return result
            with patch.object(tematy, '_write_package', side_effect=change_config):
                with self.assertRaises(tematy.GeneratorError) as caught:
                    build(f, root/'late')
            self.assertEqual(caught.exception.code, 5)
            self.assertFalse((root/'late').exists())
            self.assertFalse(list(root.glob('.late.staging-*')))

    def test_sqlite_data_error_is_code_4_and_leaves_no_package(self):
        import sqlite3
        from contextlib import closing
        with tempfile.TemporaryDirectory() as tmp:
            f = inputs_fixture(tmp)
            root, plwn = f['root'], f['paths']['plwordnet_db']
            original = plwn.read_bytes()

            def repin():
                rewrite(f['manifest'], lambda v: v['inputs']['plwordnet_db'].update(sha256=sha256(plwn)))
            # Przypięty plik, który nie jest bazą SQLite: odczyt `meta` w sprawdzaniu wejść.
            plwn.write_bytes(b'to nie jest SQLite\n' * 64)
            repin()
            # Poprawne `meta`, ale brak tabeli relacji: błąd SQLite w trakcie budowy (mapowanie na kod 4).
            broken = root/'broken.sqlite'
            broken.write_bytes(original)
            with closing(sqlite3.connect(broken)) as db:
                db.execute('DROP TABLE synsetrelation')
                db.commit()
            for content in (None, broken.read_bytes()):
                if content is not None:
                    plwn.write_bytes(content)
                    repin()
                with self.assertRaises(tematy.GeneratorError) as caught:
                    build(f, root/'out')
                self.assertEqual(caught.exception.code, 4, content is None)
                self.assertFalse((root/'out').exists())
                self.assertFalse(list(root.glob('.out.staging-*')))

    def test_cli_json_envelope_and_exit_codes(self):
        out = self.root/'cli'
        cmd = [sys.executable, '-m', 'literaki_slownik', 'tematy', '--manifest', str(self.f['manifest']),
               '--config', str(self.f['config']), '--topic', str(self.f['topic']), '--output-dir', str(out), '--json']
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        envelope = json.loads(result.stdout)
        self.assertEqual(set(envelope), {'schema_version', 'command', 'status', 'diagnostics', 'result'})
        self.assertEqual((envelope['command'], envelope['status']), ('tematy', 'ok'))
        self.assertEqual(envelope['result']['release_manifest_sha256'], sha256(out/'release-manifest.json'))
        self.assertEqual((out/'SHA256SUMS').read_bytes(), (self.root/'a/SHA256SUMS').read_bytes())
        again = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(again.returncode, 4)
        self.assertEqual(json.loads(again.stdout)['status'], 'error')
        human = subprocess.run(cmd[:-1], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((human.returncode, human.stdout), (4, ''))
        self.assertIn('już istnieje', human.stderr)
        missing = subprocess.run(cmd[:4] + ['--json'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(json.loads(missing.stdout)['status'], 'error')
        fresh = subprocess.run(cmd[:-2] + [str(self.root/'cli-human')], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(fresh.returncode, 0, fresh.stderr)
        self.assertIn('Pakiet TEMATY', fresh.stdout)


if __name__ == '__main__':
    unittest.main()
