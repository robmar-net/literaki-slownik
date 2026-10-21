import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from literaki_slownik.canonical import sha256, load_json
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.pop00 import build_package, check_inputs, load_config, read_orth
from tests.pop00_helpers import fixture, cleanup, rewrite


class Pop00PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.f=fixture(self.root)

    def tearDown(self):
        cleanup(self.root);self.tmp.cleanup()

    def build(self,name='out'):
        return build_package(self.f['manifest'],self.f['config'],self.root/name)

    def test_two_runs_have_identical_files_and_complete_decisions(self):
        a,b=self.build('a'),self.build('b')
        self.assertEqual((a['forms'],a['lost_lexemes']),(9,0))
        paths={p.relative_to(self.root/'a') for p in (self.root/'a').rglob('*') if p.is_file()}
        self.assertTrue(all((self.root/'a'/p).read_bytes()==(self.root/'b'/p).read_bytes() for p in paths))
        rows=load_json(self.root/'a/reports/decisions.json')
        self.assertEqual(set(rows),self.f['words'])
        self.assertEqual((self.root/'a/POP00.txt.gz').read_bytes()[4:8],b'\0'*4)
        self.assertTrue(all(p.stat().st_mode&0o777==0o444 for p in (self.root/'a').rglob('*') if p.is_file()))

    def test_existing_and_protected_outputs_and_race_are_refused(self):
        self.build()
        before=sha256(self.root/'out/POP00.txt.gz')
        with self.assertRaises(GeneratorError):self.build()
        self.assertEqual(before,sha256(self.root/'out/POP00.txt.gz'))
        with self.assertRaises(GeneratorError):
            build_package(self.f['manifest'],self.f['config'],self.f['run']/'bad')
        with patch('literaki_slownik.pop00.rename_noreplace',side_effect=FileExistsError()):
            with self.assertRaises(GeneratorError):self.build('race')
        self.assertFalse(list(self.root.glob('.race.staging-*')))

    def test_wrong_pin_and_unfrozen_run_are_refused(self):
        data=load_json(self.f['manifest']);data['inputs']['orth']['sha256']='0'*64;rewrite(self.f['manifest'],data)
        with self.assertRaises(GeneratorError) as err:check_inputs(self.f['manifest'])
        self.assertEqual(err.exception.code,3)
        data['inputs']['orth']['sha256']=sha256(self.f['refs']['orth'])
        run=load_json(self.f['run']/'manifest.json');run['readiness']='INCOMPLETE';rewrite(self.f['run']/'manifest.json',run)
        data['inputs']['base_run']['sha256']=sha256(self.f['run']/'manifest.json');rewrite(self.f['manifest'],data)
        with self.assertRaises(GeneratorError) as err:check_inputs(self.f['manifest'])
        self.assertEqual(err.exception.code,5)

    def test_changed_inputs_abort_package_and_bad_config_is_refused(self):
        with patch('literaki_slownik.pop00.confirm_unchanged',side_effect=GeneratorError('changed',5)):
            with self.assertRaises(GeneratorError):self.build()
        self.assertFalse((self.root/'out').exists())
        self.assertFalse(list(self.root.glob('.out.staging-*')))
        c=load_json(self.f['config']);c['ipm_min']='0.5';rewrite(self.f['config'],c)
        with self.assertRaises(GeneratorError):load_config(self.f['config'])

    def test_nonfinite_frequency_is_data_error_not_missing(self):
        for value in ['NaN','Infinity','-1']:
            p=self.root/'bad.gz'
            with gzip.open(p,'wt') as f:f.write(',freq,ipm\nkot,5,'+value+'\n')
            with self.assertRaises(GeneratorError):read_orth(p)
