import ast
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from literaki_slownik.canonical import sha256,load_json
from literaki_slownik.pop00 import build_package
from tests.pop00_helpers import ROOT,fixture,cleanup,rewrite

SCRIPT=ROOT/'scripts/check_pop00_package.py'
spec=importlib.util.spec_from_file_location('check_pop00_package',SCRIPT)
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)


def reseal(root):
    m=load_json(root/'release-manifest.json')
    m['files']={name:{'sha256':sha256(root/name),'bytes':(root/name).stat().st_size} for name in m['files']}
    rewrite(root/'release-manifest.json',m)
    (root/'release-manifest.json').chmod(0o444)
    sums=root/'SHA256SUMS';sums.chmod(0o644)
    sums.write_text(''.join(f'{sha256(p)}  {p.relative_to(root).as_posix()}\n' for p in sorted(root.rglob('*'))
                           if p.is_file() and p.name!='SHA256SUMS'))
    sums.chmod(0o444)


class IndependentPop00Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.f=fixture(self.root)
        self.package=self.root/'out';build_package(self.f['manifest'],self.f['config'],self.package)

    def tearDown(self):cleanup(self.root);self.tmp.cleanup()

    def check(self,review=None):
        return checker.check(self.package,self.f['manifest'],self.f['config'],review)

    def test_checker_is_independent_and_accepts_complete_source_result(self):
        self.assertEqual(self.check()['forms'],9)
        for node in ast.walk(ast.parse(SCRIPT.read_text())):
            if isinstance(node,ast.ImportFrom):self.assertFalse((node.module or '').startswith('literaki_slownik'))
            if isinstance(node,ast.Import):self.assertFalse(any(n.name.startswith('literaki_slownik') for n in node.names))

    def test_forged_reason_is_rejected_even_with_recomputed_checksums(self):
        p=self.package/'reports/decisions.json';rows=load_json(p)
        rows['zrobiłem']['analyses'][0]['groups']=['construction']
        rewrite(p,rows);p.chmod(0o444);reseal(self.package)
        with self.assertRaises(checker.Refused):self.check()

    def test_sample_tampering_is_rejected_after_resealing(self):
        p=self.package/'reports/sample.json';s=load_json(p)
        s['unique_selected_units']+=1
        rewrite(p,s);p.chmod(0o444);reseal(self.package)
        with self.assertRaises(checker.Refused):self.check()

    def test_review_is_bound_complete_and_has_no_unresolved_entries(self):
        review=load_json(self.package/'reports/review-template.json')
        review['status']='REVIEWED';review['sha256sums_sha256']=sha256(self.package/'SHA256SUMS')
        for item in review['items']:
            item.update(assessment='correct',reviewer='test',source_justification='Źródłowa fikstura i jawny tag.',
                        affects_lists_or_links=False)
        path=self.root/'review.json';rewrite(path,review)
        self.assertTrue(self.check(path)['review_checked'])
        if review['items']:
            review['items'][0]['assessment']='unknown';rewrite(path,review)
            with self.assertRaises(checker.Refused):self.check(path)

    def test_extra_file_or_symlink_is_refused(self):
        (self.package/'extra').write_text('extra')
        with self.assertRaises(checker.Refused):self.check()
