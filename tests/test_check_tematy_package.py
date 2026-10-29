"""Niezależny checker TEMATY i `--review` (#11, W12, ADR-010 „Bramka”)."""
import ast
import gzip
import shutil
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from literaki_slownik.canonical import load_json
from tests.tematy_helpers import ROOT, SOURCE, load_script, package_fixture, reseal

SCRIPT = ROOT/'scripts/check_tematy_package.py'
review_tool = load_script('tematy_review')
checker = review_tool.checker  # ta sama klasa `Refused` co w skrypcie przeglądu


def k(lemma):
    return lemma + '@' + SOURCE


# Wpisy fikstury: T1 bosman, kuter, reja, żeglować; T2 kuter:S2, okręt, statek, łódź; T3 barka.
AGENT = {k('bosman'): 'tak', k('kuter'): 'tak', k('reja'): 'tak', k('żeglować'): 'niepewne',
         k('kuter:S2'): 'tak', k('okręt'): 'nie', k('statek'): 'tak', k('łódź'): 'niepewne', k('barka'): 'tak'}
OPERATOR = {k('bosman'): 'tak', k('kuter'): 'tak', k('reja'): 'nie', k('żeglować'): 'niepewne',
            k('kuter:S2'): 'tak', k('okręt'): 'nie', k('statek'): 'niepewne', k('łódź'): 'tak', k('barka'): 'tak'}


def write_review(f, path, agent, operator=None):
    ratings = {key: {'ocena': v, 'powod': 'powód testowy ' + key} for key, v in agent.items()}
    review = review_tool.agent_review(f['package'], ratings, 'agent', '2026-10-29T00:00:00Z')
    review_tool.write_review(path, review)
    if operator is not None:
        given = {'kind': review_tool.OPERATOR_KIND, 'schema_version': 1, 'temat': 'morze',
                 'sample_sha256': review['sample_sha256'], 'sha256sums_sha256': review['sha256sums_sha256'],
                 'agent_sha256': review['agent_sha256'], 'oceny': operator}
        review_tool.write_review(path, review_tool.record(f['package'], path, given, reviewed_at='2026-10-29T01:00:00Z'))
    return path


class CheckTematyPackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.f = package_fixture(cls.tmp.name)
        cls.root = Path(cls.f['root'])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def check(self, package=None, review=None):
        return checker.check(package or self.f['package'], self.f['manifest'], self.f['config'], review)

    def copy(self, name):
        target = self.root/name
        shutil.copytree(self.f['package'], target)
        return target

    def test_pass_on_fixture_and_changed_byte_is_refused(self):
        report = self.check()
        self.assertEqual((report['status'], report['wpisy'], report['formy']), ('pass', 9, 13))
        self.assertEqual(report['warstwy'], {'T1': 4, 'T2': 4, 'T3': 1})
        for node in ast.walk(ast.parse(SCRIPT.read_text(encoding='utf-8'))):
            if isinstance(node, ast.ImportFrom):
                self.assertFalse((node.module or '').startswith('literaki_slownik'))
            if isinstance(node, ast.Import):
                self.assertFalse(any(n.name.startswith('literaki_slownik') for n in node.names))
        package = self.copy('byte')
        target = package/'MORZE.txt.gz'
        target.chmod(0o644)
        data = bytearray(target.read_bytes())
        data[-1] ^= 1
        target.write_bytes(bytes(data))
        target.chmod(0o444)
        with self.assertRaises(checker.Refused) as caught:
            self.check(package)
        self.assertIn('manifest', str(caught.exception))

    def test_form_outside_standard_or_lexeme_in_two_layers_is_refused(self):
        package = self.copy('outside')
        target = package/'MORZE.txt.gz'
        words = gzip.decompress(target.read_bytes()).decode().splitlines()
        target.chmod(0o644)
        target.write_bytes(gzip.compress(''.join(w + '\n' for w in sorted(words + ['szkuta'])).encode(), mtime=0))
        target.chmod(0o444)
        reseal(package)
        with self.assertRaises(checker.Refused) as caught:
            self.check(package)
        self.assertIn('⊆ STANDARD', str(caught.exception))

        package = self.copy('twice')
        target = package/'MORZE.tsv.gz'
        rows = gzip.decompress(target.read_bytes()).decode().splitlines()
        row = next(r for r in rows if r.startswith(k('okręt') + '\t')).split('\t')
        row[3], row[4] = 'T3', 'T3'
        rows = [rows[0]] + sorted(rows[1:] + ['\t'.join(row)])
        target.chmod(0o644)
        target.write_bytes(gzip.compress(''.join(r + '\n' for r in rows).encode(), mtime=0))
        target.chmod(0o444)
        reseal(package)
        with self.assertRaises(checker.Refused) as caught:
            self.check(package)
        self.assertIn('dwóch warstwach', str(caught.exception))

    def test_review_accuracy_with_real_n_agreement_and_kappa(self):
        path = write_review(self.f, self.root/'review-a.json', AGENT, OPERATOR)
        result = self.check(review=path)['przeglad']
        operator, agent = result['operator'], result['agent']
        # T1: tak, tak, nie, niepewne → „tak” 2 z N = 4; „niepewne” nie jest „tak” (inaczej 3/4).
        self.assertEqual(operator['T1'], {'N': 4, 'tak': 2, 'nie': 1, 'niepewne': 1,
                                          'tak_udzial': '1/2', 'nie_udzial': '1/4'})
        self.assertEqual((operator['T2']['N'], operator['T2']['tak_udzial'], operator['T2']['nie_udzial']),
                         (4, '1/2', '1/4'))
        self.assertEqual((operator['T3']['N'], operator['T3']['tak_udzial']), (1, '1'))
        self.assertEqual((agent['T1']['tak_udzial'], agent['T1']['niepewne']), ('3/4', 1))
        # Zgodność 6/9. Brzegowe: agent tak 6, nie 1, niepewne 2; operator 5, 2, 2.
        # p_e = (6·5 + 1·2 + 2·2) / 81 = 4/9; kappa = (2/3 − 4/9) / (1 − 4/9) = 2/5.
        self.assertEqual(result['zgodnosc'], {'N': 9, 'zgodnosc': '2/3', 'kappa': '2/5', 'oczekiwana': '4/9'})
        self.assertEqual(checker.agreement({'a': 'tak', 'b': 'nie'}, {'a': 'tak', 'b': 'niepewne'})['zgodnosc'], '1/2')

    def test_review_verdict_lists_thresholds_and_small_layers_use_shares(self):
        path = write_review(self.f, self.root/'review-b.json', AGENT, OPERATOR)
        verdict = self.check(review=path)['przeglad']['werdykt']
        self.assertEqual(verdict['wynik'], 'popraw')
        self.assertEqual([r['prog'] for r in verdict['progi']],
                         ['slowa_oczywiste', 't1_tak', 't2_tak', 't2_nie', 't3_tak', 'zgodnosc'])
        self.assertEqual(verdict['niespelnione'], ['slowa_oczywiste', 't1_tak', 't2_tak', 't2_nie', 'zgodnosc'])
        t3 = next(r for r in verdict['progi'] if r['prog'] == 't3_tak')
        self.assertEqual((t3['wartosc'], t3['granica'], t3['status']), ('1', '2/3', 'spelniony'))  # N = 1, udział 1
        # Operator wszystko „tak” poza jednym w T1: 3/4 < 0,90 mimo małej warstwy; reszta spełniona.
        almost = {key: 'tak' for key in OPERATOR}
        almost[k('reja')] = 'nie'
        path = write_review(self.f, self.root/'review-c.json', {key: 'tak' for key in AGENT}, almost)
        verdict = self.check(review=path)['przeglad']['werdykt']
        self.assertEqual((verdict['wynik'], verdict['niespelnione']), ('popraw', ['slowa_oczywiste', 't1_tak']))
        t1 = next(r for r in verdict['progi'] if r['prog'] == 't1_tak')
        self.assertEqual((t1['wartosc'], t1['status']), ('3/4', 'niespelniony'))
        # Bez ocen operatora: progi z ocen czekają, 37 słów już rozstrzyga „popraw”.
        path = write_review(self.f, self.root/'review-d.json', AGENT)
        verdict = self.check(review=path)['przeglad']['werdykt']
        self.assertEqual((verdict['wynik'], verdict['czeka_na_ocene']),
                         ('popraw', ['t1_tak', 't2_tak', 't2_nie', 't3_tak', 'zgodnosc']))
        progi = load_json(self.f['config'])['progi']
        passing = {'slowa_oczywiste': Fraction(26, 37), 't1_tak': Fraction(27, 30), 't2_tak': Fraction(2, 3),
                   't2_nie': Fraction(3, 30), 't3_tak': Fraction(2, 3), 'zgodnosc': Fraction(4, 5)}
        self.assertEqual(checker.verdict(progi, passing)['wynik'], 'dalej')
        self.assertEqual(checker.verdict(progi, {**passing, 't2_nie': Fraction(4, 30)})['niespelnione'], ['t2_nie'])
        self.assertEqual(checker.verdict(progi, {**passing, 't3_tak': None})['niespelnione'], ['t3_tak'])


if __name__ == '__main__':
    unittest.main()
