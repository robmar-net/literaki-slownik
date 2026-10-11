"""Niezależna kontrola pakietu POP i przeglądu (D-3, D-5): `scripts/check_pop_package.py`."""
import ast
import gzip
import hashlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tests.pop_helpers import pop_package

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'scripts/check_pop_package.py'
SPEC = importlib.util.spec_from_file_location('check_pop_package', SCRIPT)
check_pop_package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_pop_package)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _rewrite(path, data):
    """Zapis do pliku 0444 i powrót do 0444, żeby test mierzył treść, nie tryb."""
    path = Path(path)
    if path.exists():
        path.chmod(0o644)
    path.write_bytes(data)
    path.chmod(0o444)


def _gz(words):
    raw = io.BytesIO()
    with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as stream:
        stream.write(''.join(f'{w}\n' for w in words).encode('utf-8'))
    return raw.getvalue()


def _reseal(package):
    """Przelicz `files` manifestu i `SHA256SUMS`: zmiana treści przechodzi kontrolę hashy."""
    manifest_path = package / 'release-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['files'] = {rel: {'sha256': _sha(package / rel), 'bytes': (package / rel).stat().st_size}
                         for rel in manifest['files']}
    _rewrite(manifest_path, json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode('utf-8'))
    sums = sorted(str(p.relative_to(package)) for p in package.rglob('*')
                  if p.is_file() and p.name != 'SHA256SUMS')
    _rewrite(package / 'SHA256SUMS', ''.join(f'{_sha(package / r)}  {r}\n' for r in sums).encode('utf-8'))


def _words(path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        return stream.read().splitlines()


class CheckPopPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.fixture = pop_package(cls.root)
        cls.package = cls.fixture['package']
        cls.standard = cls.fixture['run'] / 'lists/standard.txt'
        cls.copies = 0

    @classmethod
    def tearDownClass(cls):
        for path in cls.root.rglob('*'):
            if path.is_file():
                path.chmod(0o644)
        cls.tmp.cleanup()

    def copy(self):
        type(self).copies += 1
        target = self.root / f'copy-{self.copies}'
        shutil.copytree(self.package, target)
        return target

    def run_check(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = check_pop_package.main([str(a) for a in args])
        return code, out.getvalue() + err.getvalue()

    def check(self, package, *extra):
        return self.run_check('--pop-dir', package, '--standard', self.standard, *extra)

    def review(self, directory, mutate=None, package=None):
        """Wypełniony szablon przeglądu pakietu; `mutate` psuje go przed zapisem."""
        package = package or self.package
        review = json.loads((package / 'reports/review-template.json').read_text(encoding='utf-8'))
        review['status'] = 'REVIEWED'
        review['sha256sums_sha256'] = _sha(package / 'SHA256SUMS')
        for item in review['items']:
            item.update(assessment='correct', reviewer='agent', source_justification='KWJP fikstury, ranga',
                        affects_lists_or_links=False)
        if mutate:
            mutate(review)
        path = Path(directory) / f'review-{self.copies}-{id(mutate)}.json'
        path.write_text(json.dumps(review, ensure_ascii=False), encoding='utf-8')
        return path

    def test_valid_package_passes(self):
        code, output = self.check(self.package)
        self.assertEqual(code, 0, output)
        self.assertIn('OK', output)

    def test_changed_missing_or_extra_file_fails(self):
        def changed(p):
            _rewrite(p / 'TERMS.md', (p / 'TERMS.md').read_bytes() + b'dopisek\n')

        def missing(p):
            (p / 'LIMITATIONS.md').unlink()

        def extra(p):
            _rewrite(p / 'reports/extra.json', b'{}')

        def writable(p):
            (p / 'POP.txt.gz').chmod(0o644)

        for name, mutate in (('changed', changed), ('missing', missing), ('extra', extra), ('mode', writable)):
            with self.subTest(name):
                package = self.copy()
                mutate(package)
                code, output = self.check(package)
                self.assertEqual(code, 4, output)

    def test_subsets_and_must_include(self):
        def pop0_outside_pop(p):
            # `fajny` jest w STANDARD fikstury, ale poza POP.
            self.assertNotIn('fajny', _words(p / 'POP.txt.gz'))
            _rewrite(p / 'POP0.txt.gz', _gz(sorted({*_words(p / 'POP0.txt.gz'), 'fajny'})))

        def pop_outside_standard(p):
            words = _words(p / 'POP.txt.gz')
            _rewrite(p / 'POP.txt.gz', _gz(sorted({*words, 'zzzspozastandard'})))

        def no_kot(p):
            _rewrite(p / 'POP0.txt.gz', _gz([w for w in _words(p / 'POP0.txt.gz') if w != 'kot']))

        for name, mutate, reason in (('pop0-pop', pop0_outside_pop, 'POP0'),
                                     ('pop-standard', pop_outside_standard, 'STANDARD'),
                                     ('kot', no_kot, 'kot')):
            with self.subTest(name):
                package = self.copy()
                mutate(package)
                _reseal(package)
                code, output = self.check(package)
                self.assertEqual(code, 4, output)
                self.assertIn(reason, output)

    def test_nkjp_keys_and_raw_files_fail(self):
        def bad_key(p):
            path = p / 'reports/units.json'
            units = json.loads(path.read_text(encoding='utf-8'))
            units['units'][0]['nkjp_freq'] = 7340919
            _rewrite(path, json.dumps(units, ensure_ascii=False).encode('utf-8'))

        def raw_file(p):
            _rewrite(p / 'reports/1grams.gz', _gz(['7340919 kot']))

        for name, mutate, reason in (('key', bad_key, 'nkjp_freq'), ('file', raw_file, '1grams')):
            with self.subTest(name):
                package = self.copy()
                mutate(package)
                _reseal(package)
                code, output = self.check(package)
                self.assertEqual(code, 4, output)
                self.assertIn(reason, output)

    def test_review(self):
        directory = self.root / 'reviews'
        directory.mkdir(exist_ok=True)
        code, output = self.check(self.package, '--review', self.review(directory))
        self.assertEqual(code, 0, output)

        def unreviewed(review):
            review['status'] = 'UNREVIEWED'

        def unassessed(review):
            review['items'][0]['assessment'] = None

        def no_justification(review):
            review['items'][-1]['source_justification'] = ' '

        def affects(review):
            review['items'][0]['affects_lists_or_links'] = True

        def dropped(review):
            review['items'] = review['items'][1:]

        def other_sample(review):
            review['sample_sha256'] = '0' * 64

        def other_index(review):
            review['canonical_index_sha256'] = '1' * 64

        def other_sums(review):
            review['sha256sums_sha256'] = '2' * 64

        for mutate in (unreviewed, unassessed, no_justification, affects, dropped, other_sample, other_index,
                       other_sums):
            with self.subTest(mutate.__name__):
                code, output = self.check(self.package, '--review', self.review(directory, mutate))
                self.assertEqual(code, 4, output)

    def test_bad_arguments_and_standard_pin(self):
        for args in ([], ['--pop-dir', self.package], ['--pop-dir', self.root / 'brak', '--standard', self.standard],
                     ['--pop-dir', self.package, '--standard', self.root / 'brak.txt'],
                     ['--pop-dir', self.package, '--standard', self.standard, '--nieznana']):
            with self.subTest(args=args):
                code, output = self.run_check(*args)
                self.assertEqual(code, 2, output)
        other = self.root / 'standard-inny.txt'
        other.write_bytes(self.standard.read_bytes() + b'zzz\n')
        code, output = self.run_check('--pop-dir', self.package, '--standard', other)
        self.assertEqual(code, 3, output)

    def test_script_is_independent_of_package_code(self):
        tree = ast.parse(SCRIPT.read_text(encoding='utf-8'))
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0, 'import względny')
                modules.add(node.module)
            elif isinstance(node, ast.Call) and getattr(node.func, 'id', None) == '__import__':
                self.fail('dynamiczny import')
        self.assertTrue(modules)
        for module in modules:
            top = module.split('.')[0]
            self.assertNotIn(top, ('pop', 'literaki_slownik', 'tests'), module)
            self.assertIn(top, sys.stdlib_module_names, module)
        self.assertNotIn('importlib', modules)


if __name__ == '__main__':
    unittest.main()
