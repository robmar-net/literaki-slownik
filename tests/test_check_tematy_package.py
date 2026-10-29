"""Niezależny checker TEMATY i `--review` (#11, W12, ADR-010 „Bramka”)."""
import ast
import gzip
import json
import shutil
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from literaki_slownik.canonical import load_json, sha256
from tests.tematy_helpers import ROOT, SOURCE, load_script, package_fixture, reseal, rewrite

SCRIPT = ROOT/'scripts/check_tematy_package.py'
review_tool = load_script('tematy_review')
checker = review_tool.checker  # ta sama klasa `Refused` co w skrypcie przeglądu


def k(lemma):
    return lemma + '@' + SOURCE


# Wpisy fikstury: T1 bosman, kuter, reja, żeglować; T2 kuter:S2, okręt, statek, łódź; T3 barka.
AGENT = {k('bosman'): 'tak', k('kuter'): 'tak', k('reja'): 'tak', k('żeglować'): 'niepewne',
         k('kuter:S2'): 'tak', k('okręt'): 'nie', k('statek'): 'tak', k('łódź'): 'niepewne', k('barka'): 'tak'}
# Operator ocenia tylko warstwy `operator_warstwy` (T2, T3; #12 W5): `operator_keys` przycina słownik.
OPERATOR = {k('kuter:S2'): 'tak', k('okręt'): 'nie', k('statek'): 'niepewne', k('łódź'): 'tak', k('barka'): 'tak'}


def operator_keys(package):
    """Klucze próby operatora z `sample.operator.strata`."""
    return {key for keys in load_json(Path(package)/'reports/sample.json')['operator']['strata'].values()
            for key in keys}


def write_review(f, path, agent, operator=None):
    """Przegląd z ocenami agenta (pełna próba); oceny operatora przycięte do jego próby."""
    agent = {key: v for key, v in agent.items()
             if key in {i['key'] for i in load_json(Path(f['package'])/'reports/sample.json')['items']}}
    if operator is not None:
        operator = {key: v for key, v in operator.items() if key in operator_keys(f['package'])}
    ratings = {key: {'ocena': v, 'powod': 'powód testowy ' + key} for key, v in agent.items()}
    review = review_tool.agent_review(f['package'], ratings, 'agent', '2026-10-29T00:00:00Z')
    review_tool.write_review(path, review)
    if operator is not None:
        given = {'kind': review_tool.OPERATOR_KIND, 'schema_version': 1, 'temat': 'morze',
                 'sample_sha256': review['sample_sha256'], 'sha256sums_sha256': review['sha256sums_sha256'],
                 'agent_sha256': review['agent_sha256'], 'oceny': operator}
        review_tool.write_review(path, review_tool.record(f['package'], path, given, reviewed_at='2026-10-29T01:00:00Z'))
    return path


def tamper(package, name, change):
    """Zmiana pliku pakietu `name` (tekst: str → str, JSON: dict w miejscu) i nowe hashe (`reseal`)."""
    target = Path(package)/name
    target.chmod(0o644)
    if name.endswith('.json'):
        rewrite(target, change)
    else:
        target.write_text(change(target.read_text(encoding='utf-8')), encoding='utf-8')
    target.chmod(0o444)
    reseal(package)
    return package


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
        self.assertEqual(report['warstwy'], {'T1': 4, 'T2': 4, 'T3': 1, 'D': 0})
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
        # T2: tak, nie, niepewne, tak → „tak” 2 z N = 4; „niepewne” nie jest „tak”. T1 operator nie ocenia.
        self.assertEqual(operator['T2'], {'N': 4, 'tak': 2, 'nie': 1, 'niepewne': 1,
                                          'tak_udzial': '1/2', 'nie_udzial': '1/4'})
        self.assertEqual((operator['T1']['N'], operator['T1']['tak_udzial']), (0, None))
        self.assertEqual((operator['T3']['N'], operator['T3']['tak_udzial']), (1, '1'))
        self.assertEqual((agent['T1']['tak_udzial'], agent['T1']['niepewne']), ('3/4', 1))
        # Zgodność na 5 pozycjach ocenionych przez obu: 3/5. Brzegowe: agent tak 3, nie 1, niepewne 1;
        # operator tak 3, nie 1, niepewne 1. p_e = (9 + 1 + 1) / 25 = 11/25; kappa = (3/5 − 11/25) / (14/25) = 2/7.
        self.assertEqual(result['zgodnosc'], {'N': 5, 'zgodnosc': '3/5', 'kappa': '2/7', 'oczekiwana': '11/25'})
        self.assertEqual(checker.agreement({'a': 'tak', 'b': 'nie'}, {'a': 'tak', 'b': 'niepewne'})['zgodnosc'], '1/2')

    def test_review_verdict_lists_thresholds_and_small_layers_use_shares(self):
        path = write_review(self.f, self.root/'review-b.json', AGENT, OPERATOR)
        verdict = self.check(review=path)['przeglad']['werdykt']
        self.assertEqual(verdict['wynik'], 'popraw')
        self.assertEqual([r['prog'] for r in verdict['progi']],
                         ['slowa_oczywiste', 't1_tak', 't2_tak', 't2_nie', 't3_tak', 'zgodnosc'])
        self.assertEqual(verdict['niespelnione'], ['slowa_oczywiste', 't1_tak', 't2_tak', 't2_nie', 'zgodnosc'])
        self.assertEqual((verdict['czeka_na_ocene'], verdict['nie_dotyczy']), ([], []))
        t3 = next(r for r in verdict['progi'] if r['prog'] == 't3_tak')
        self.assertEqual((t3['wartosc'], t3['granica'], t3['status']), ('1', '2/3', 'spelniony'))  # N = 1, udział 1
        # Agent wszystko „tak” poza jednym w T1: 3/4 < 0,90 mimo małej warstwy; reszta spełniona.
        almost = {key: 'tak' for key in AGENT}
        almost[k('reja')] = 'nie'
        path = write_review(self.f, self.root/'review-c.json', almost, {key: 'tak' for key in OPERATOR})
        verdict = self.check(review=path)['przeglad']['werdykt']
        self.assertEqual((verdict['wynik'], verdict['niespelnione']), ('popraw', ['slowa_oczywiste', 't1_tak']))
        t1 = next(r for r in verdict['progi'] if r['prog'] == 't1_tak')
        self.assertEqual((t1['wartosc'], t1['status']), ('3/4', 'niespelniony'))
        progi = load_json(self.f['config'])['progi']
        passing = {'slowa_oczywiste': Fraction(26, 37), 't1_tak': Fraction(27, 30), 't2_tak': Fraction(2, 3),
                   't2_nie': Fraction(3, 30), 't3_tak': Fraction(2, 3), 'zgodnosc': Fraction(4, 5)}
        self.assertEqual(checker.verdict(progi, passing)['wynik'], 'dalej')
        self.assertEqual(checker.verdict(progi, {**passing, 't2_nie': Fraction(4, 30)})['niespelnione'], ['t2_nie'])
        self.assertEqual(checker.verdict(progi, {**passing, 't3_tak': None})['niespelnione'], ['t3_tak'])

    # --- #12 W6, W7 ---

    def test_review_without_operator_counts_t1_from_agent_and_waits_for_operator_layers(self):
        path = write_review(self.f, self.root/'review-d.json', AGENT)
        verdict = self.check(review=path)['przeglad']['werdykt']
        self.assertEqual((verdict['wynik'], verdict['czeka_na_ocene'], verdict['nie_dotyczy']),
                         ('popraw', ['t2_tak', 't2_nie', 't3_tak', 'zgodnosc'], []))
        t1 = next(r for r in verdict['progi'] if r['prog'] == 't1_tak')
        self.assertEqual((t1['wartosc'], t1['status']), ('3/4', 'niespelniony'))
        path = write_review(self.f, self.root/'review-e.json', {key: 'tak' for key in AGENT})
        t1 = next(r for r in self.check(review=path)['przeglad']['werdykt']['progi'] if r['prog'] == 't1_tak')
        self.assertEqual((t1['wartosc'], t1['status']), ('1', 'spelniony'))

    def test_operator_strata_other_than_operator_layers_are_refused(self):
        config = load_json(self.f['config'])
        rows = checker.tsv(Path(self.f['package']), 'morze')
        self.assertEqual(set(checker.check_sample(Path(self.f['package']), rows, config, 'MORZE')['operator']),
                         {'T2', 'T3'})
        for layers in (['T1', 'T2', 'T3'], ['T2']):
            with self.assertRaises(checker.Refused) as caught:
                checker.check_sample(Path(self.f['package']), rows, {**config, 'operator_warstwy': layers}, 'MORZE')
            self.assertIn('próba operatora', str(caught.exception))

    def test_tsv_row_with_excluded_lemma_and_class_is_refused(self):
        package = self.copy('excluded')
        topic = package/'tematy/morze.json'
        manifest = package/'release-manifest.json'
        for p in (topic, manifest):
            p.chmod(0o644)
        rewrite(topic, lambda v: v.update(wykluczenia=[{'lemat': 'okręt', 'czesc_mowy': 'subst', 'powód': 'test'}]))
        rewrite(manifest, lambda m: m['topic'].update(sha256=sha256(topic)))
        for p in (topic, manifest):
            p.chmod(0o444)
        reseal(package)
        with self.assertRaises(checker.Refused) as caught:
            self.check(package)
        self.assertIn('wykluczon', str(caught.exception))
        self.assertIn('okręt', str(caught.exception))

    def test_summary_exclusions_differing_from_topic_are_refused(self):
        package = self.copy('summary-excluded')
        summary = package/'reports/summary.json'
        summary.chmod(0o644)
        rewrite(summary, lambda v: v.update(wykluczenia=[
            {'lemat': 'kot', 'czesc_mowy': 'subst', 'powód': 'test', 'klucze': [k('kot')], 'warstwy': ['T1']}]))
        summary.chmod(0o444)
        reseal(package)
        with self.assertRaises(checker.Refused) as caught:
            self.check(package)
        self.assertIn('Wykluczenia raportu', str(caught.exception))

    def test_package_texts_with_segment_leftovers_are_refused(self):
        # #13 (ADR-012 „Otwarte na v2” b): teksty pakietu sprawdzamy niezależnie od generatora.
        for n, (name, change) in enumerate((('TERMS.md', lambda t: t + '<!--T3-->'),
                                            ('LIMITATIONS.md', lambda t: t + '@@SRODLADOWE@@\n'),
                                            ('ATTRIBUTIONS.md', lambda t: t + '<!--/T3-->'))):
            package = tamper(self.copy(f'texts-{n}'), name, change)
            with self.assertRaises(checker.Refused, msg=name) as caught:
                self.check(package)
            self.assertIn(name, str(caught.exception))

    def test_summary_t3_inland_and_not_applicable_must_match_topic(self):
        # Morze fikstury ma `t3` i znaczniki śródlądowe: `t3` i `srodladowe` niepuste, `nie_dotyczy` puste.
        for n, change in enumerate((lambda v: v.update(t3=None), lambda v: v.update(srodladowe=None),
                                    lambda v: v['werdykt'].update(nie_dotyczy=['t3_tak']))):
            package = tamper(self.copy(f'summary-{n}'), 'reports/summary.json', change)
            with self.assertRaises(checker.Refused, msg=n) as caught:
                self.check(package)
            self.assertIn('summary', str(caught.exception))

    def test_topic_with_t3_and_empty_t3_layer_fails_t3_tak(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Wykluczenie `barka` opróżnia T3 przy temacie z `t3`.
            f = package_fixture(tmp, change=lambda v: v.update(
                wykluczenia=[{'lemat': 'barka', 'czesc_mowy': 'subst', 'powód': 'test pustej T3'}]))
            report = checker.check(f['package'], f['manifest'], f['config'])
            self.assertEqual(report['warstwy']['T3'], 0)
            path = write_review(f, Path(tmp)/'review.json', AGENT)
            verdict = checker.check(f['package'], f['manifest'], f['config'], path)['przeglad']['werdykt']
            t3 = next(r for r in verdict['progi'] if r['prog'] == 't3_tak')
            self.assertEqual((t3['wartosc'], t3['status']), (None, 'niespelniony'))
            self.assertIn('t3_tak', verdict['niespelnione'])
            self.assertNotIn('t3_tak', verdict['czeka_na_ocene'])


class CheckTematyBezT3Test(unittest.TestCase):
    """Temat bez `t3` (#12 W2, W6, W7, D6)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.f = package_fixture(cls.tmp.name, t3=False)
        cls.root = Path(cls.f['root'])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_pass_without_t3_pins_only_used_inputs_but_manifest_still_needs_iate(self):
        report = checker.check(self.f['package'], self.f['manifest'], self.f['config'])
        self.assertEqual((report['status'], report['warstwy']['T3']), ('pass', 0))
        self.assertNotIn('iate', load_json(self.f['package']/'release-manifest.json')['inputs'])
        # IATE nieużyte: zmiana pliku IATE nie zmienia odbioru.
        iate = self.f['paths']['iate']
        original = iate.read_bytes()
        try:
            iate.write_bytes(b'inny zip')
            self.assertEqual(checker.check(self.f['package'], self.f['manifest'], self.f['config'])['status'], 'pass')
        finally:
            iate.write_bytes(original)
        # Manifest wejść bez `iate` to nadal zły manifest (D6). Pin manifestu wejść sprawdzamy wcześniej,
        # więc podmieniamy manifest i jego pin w kopii pakietu.
        source = self.root/'bez-iate.json'
        value = load_json(self.f['manifest'])
        del value['inputs']['iate']
        source.write_text(json.dumps(value), encoding='utf-8')
        package = self.root/'pkg-bez-iate'
        shutil.copytree(self.f['package'], package)
        manifest = package/'release-manifest.json'
        manifest.chmod(0o644)
        rewrite(manifest, lambda m: m.update(source_manifest_sha256=sha256(source)))
        manifest.chmod(0o444)
        reseal(package)
        with self.assertRaises(checker.Refused) as caught:
            checker.check(package, source, self.f['config'])
        self.assertIn('Zły manifest wejść', str(caught.exception))

    def test_iate_attribution_without_t3_and_summary_fields_are_refused(self):
        cases = (('ATTRIBUTIONS.md', lambda t: t + '\n## IATE\n'), ('TERMS.md', lambda t: t + ' IATE'),
                 ('reports/summary.json', lambda v: v.update(t3={'hasla': 1})),
                 ('reports/summary.json', lambda v: v.update(srodladowe={'kandydaci_t3': {}})),
                 ('reports/summary.json', lambda v: v['werdykt'].update(nie_dotyczy=[])))
        for n, (name, change) in enumerate(cases):
            package = self.root/f'bez-t3-{n}'
            shutil.copytree(self.f['package'], package)
            tamper(package, name, change)
            with self.assertRaises(checker.Refused, msg=(name, n)) as caught:
                checker.check(package, self.f['manifest'], self.f['config'])
            self.assertIn(name.rsplit('/', 1)[-1].split('.')[0], str(caught.exception))

    def test_t3_layer_must_be_empty_without_t3(self):
        # Pakiet z T3 (barka) i podmieniony temat bez `t3`: checker odmawia.
        with tempfile.TemporaryDirectory() as tmp:
            f = package_fixture(tmp)
            package = Path(f['package'])
            topic, manifest = package/'tematy/morze.json', package/'release-manifest.json'
            for p in (topic, manifest):
                p.chmod(0o644)
            rewrite(topic, lambda v: (v.pop('t3'), v['diagnostyka'].pop('znaczniki_srodladowe')))
            rewrite(manifest, lambda m: (m['topic'].update(sha256=sha256(topic)), m['inputs'].pop('iate'),
                                         m.pop('iate')))
            for p in (topic, manifest):
                p.chmod(0o444)
            reseal(package)
            with self.assertRaises(checker.Refused) as caught:
                checker.check(package, f['manifest'], f['config'])
            self.assertIn('T3', str(caught.exception))

    def test_review_without_t3_marks_t3_tak_not_applicable_and_it_does_not_block(self):
        sample = load_json(self.f['package']/'reports/sample.json')
        self.assertEqual(sample['operator']['strata']['T3'], [])
        agent = {i['key']: 'tak' for i in sample['items']}
        path = write_review(self.f, self.root/'review.json', agent)
        verdict = checker.check(self.f['package'], self.f['manifest'], self.f['config'], path)['przeglad']['werdykt']
        self.assertEqual((verdict['nie_dotyczy'], verdict['czeka_na_ocene']),
                         (['t3_tak'], ['t2_tak', 't2_nie', 'zgodnosc']))
        t3 = next(r for r in verdict['progi'] if r['prog'] == 't3_tak')
        self.assertEqual((t3['wartosc'], t3['status']), ('nie_dotyczy', 'nie_dotyczy'))
        progi = load_json(self.f['config'])['progi']
        passing = {'slowa_oczywiste': Fraction(26, 37), 't1_tak': Fraction(27, 30), 't2_tak': Fraction(2, 3),
                   't2_nie': Fraction(3, 30), 't3_tak': 'nie_dotyczy', 'zgodnosc': Fraction(4, 5)}
        result = checker.verdict(progi, passing)
        self.assertEqual((result['wynik'], result['nie_dotyczy'], result['niespelnione']), ('dalej', ['t3_tak'], []))

if __name__ == '__main__':
    unittest.main()
