"""Metoda pop-v3 (ADR-008, #6): POP i POP0 = stałe progi punktacji.

Próg punktacji bierze każdą jednostkę z miarą ≥ wartość (remis wchodzi), bez jednostek bez miary.
Członkowie grup porównują własną punktację z progiem swojej listy; wyjątki jak w pop-v2.
Próg POP0 ≥ próg POP, więc POP0 ⊆ POP wynika z konfiguracji.
"""
import importlib.util
import io
import json
import math
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import tests.test_pop as base_tests
from literaki_slownik.canonical import load_json, sha256
from literaki_slownik.explain import explain_pop, format_pop_explanation
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.pop import (build_pop, load_config, measure, measure_floors, member_units, prune_members,
                                  rank_units, threshold, units)
from tests.pop_helpers import NKJP_POP_1GRAMS, pop_config, pop_config_v3, pop_fixture, pop_package

S = 'synthetic'
ROOT = Path(__file__).resolve().parent.parent
D3 = {'source': 'kwjp+nkjp', 'field': 'log-ipm', 'weight': 0.5}
ISSUE_6 = 'https://github.com/robmar-net/literaki-slownik/issues/6'
SPEC = importlib.util.spec_from_file_location('check_pop_package', ROOT / 'scripts/check_pop_package.py')
check_pop_package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_pop_package)
# Miary jednostek fikstury `pop_fixture` (log-ipm 0,5/0,5), zob. `PopBuildTests`.
FAJNY, ZAMEK, BAC = 4.234511124, 3.933703186, 4.817424209
# `duży`: ostatnia jednostka cięcia POP0 = 6 leksemów (ranga 4); w POP0 jest `lato`/`rok`, bez `lato`.
DUZY = 4.885589928
# Stałe pop-v3: punktacja ostatniej jednostki cięć 60 000 i 20 000 na wydanych wejściach pop-v2.
POP_SCORE, POP0_SCORE = -1.042878629, 0.57370099


def _code(call, *args, **kwargs):
    with unittest.TestCase().assertRaises(GeneratorError) as raised:
        call(*args, **kwargs)
    return raised.exception


class ScoreThresholdTests(unittest.TestCase):
    def setUp(self):
        self.result = {'units': {(k,): {'size': 1, 'members': ((S, k),)} for k in 'abcdef'}}
        self.measured = {('a',): {'value': 5.0}, ('b',): {'value': 3.0}, ('c',): {'value': 3.0},
                         ('d',): {'value': 3.0}, ('e',): {'value': 1.0}, ('f',): {'value': None}}
        self.ranks = rank_units(self.measured)

    def cut(self, value):
        return threshold(self.ranks, self.result, {'by': 'score', 'value': value}, values=self.measured)

    def test_score_takes_every_unit_at_or_above_value_with_ties(self):
        cut = self.cut(3.0)
        self.assertEqual(cut['units'], (('a',), ('b',), ('c',), ('d',)))
        self.assertEqual((cut['lexemes'], cut['rank'], cut['reached'], cut['score']), (4, 4, True, 3.0))
        self.assertEqual(cut['next_block'], {'units': 1, 'lexemes': 1, 'rank': 5})
        above = self.cut(3.000000001)
        self.assertEqual((above['units'], above['rank']), ((('a',),), 1))
        self.assertEqual(above['next_block'], {'units': 3, 'lexemes': 3, 'rank': 2})
        self.assertEqual(self.cut(3)['units'], cut['units'])  # liczba całkowita też

    def test_unit_without_score_is_never_chosen(self):
        cut = self.cut(-100.0)
        self.assertEqual(len(cut['units']), 5)
        self.assertNotIn(('f',), cut['units'])
        self.assertEqual((cut['reached'], cut['next_block']), (False, None))
        empty = self.cut(9.0)
        self.assertEqual((empty['units'], empty['rank'], empty['lexemes']), ((), None, 0))

    def test_score_needs_values_and_a_finite_number(self):
        with self.assertRaises(ValueError):
            threshold(self.ranks, self.result, {'by': 'score', 'value': 3.0})
        for value in (True, '3', math.inf, -math.inf, math.nan, None):
            self.assertEqual(_code(self.cut, value).code, 2, value)


class ScorePruneTests(unittest.TestCase):
    """Dane `PopPruneTests` (wzór `kią`); POP0 liczy leksemy, POP ma stałą punktację."""

    def setUp(self):
        base_tests.PopPruneTests.setUp(self)

    def run_lists(self, score, nkjp=None, pop0=4, pop0_score=None):
        nkjp = nkjp or self.nkjp
        result = units(self.kwjp, 'e', self.relevant, nkjp, self.owners, eligible=self.eligible)
        result['units'] = {key: u for key, u in result['units'].items() if key != (self.k('Kia'),)}
        found = measure(result, D3, 'lower-bound-absent')['units']
        ranks = rank_units(found)
        members = member_units(result, self.kwjp, self.eligible, nkjp, self.owners)
        own = measure(members, D3, 'lower-bound-absent', floors=measure_floors(result, D3))['units']
        score = score(found, own) if callable(score) else score
        pop0_d6 = ({'by': 'count', 'value': pop0} if pop0_score is None
                   else {'by': 'score', 'value': pop0_score(found, own)})
        cuts = {'pop0': threshold(ranks, result, pop0_d6, values=found),
                'pop': threshold(ranks, result, {'by': 'score', 'value': score}, values=found)}
        self.members = members
        return found, own, cuts, prune_members(members, own, found, cuts)

    def test_own_score_equal_to_threshold_keeps_member_rank_would_not(self):
        k = self.k
        found, own, cuts, pruned = self.run_lists(lambda found, own: own[(k('ki'),)]['value'])
        group = (k('ki'), k('kia'), k('kto'))
        self.assertEqual(set(cuts['pop']['units']), {group, (k('dom'),), (k('zamek:a'), k('zamek:b')), (k('pies'),)})
        self.assertEqual(cuts['pop']['rank'], 4)
        # ki: własna ranga 5 > ranga progu 4, ale własna punktacja = próg (remis wchodzi).
        self.assertEqual(pruned['members'][(k('ki'),)]['rank'], 5)
        kept = pruned['lists']['pop']['kept']
        self.assertTrue({k('ki'), k('kia'), k('kto'), k('zamek:a'), k('zamek:b')} <= kept)
        self.assertEqual(pruned['lists']['pop']['pruned'], ())
        # Ta sama granica jako ranga przycina ki (ścieżka pop-v2).
        plain = {name: {key: value for key, value in cut.items() if key != 'score'} for name, cut in cuts.items()}
        by_rank = prune_members(self.members, own, found, plain)
        self.assertNotIn(k('ki'), by_rank['lists']['pop']['kept'])
        # POP0 (limit liczby) nadal przycina własną rangą; POP0 ⊆ POP.
        self.assertEqual(pruned['lists']['pop0']['kept'], {k('kto'), k('dom')})
        self.assertTrue(pruned['lists']['pop0']['kept'] <= kept)

    def test_pop0_score_prunes_by_own_score_and_stays_inside_pop(self):
        k = self.k
        ki = lambda found, own: own[(k('ki'),)]['value']
        _, _, by_count, counted = self.run_lists(ki)
        last = lambda found, own: min(found[unit]['value'] for unit in by_count['pop0']['units'])
        found, own, cuts, pruned = self.run_lists(ki, pop0_score=last)
        # Punktacja ostatniej jednostki cięcia liczbą daje te same jednostki i tych samych członków.
        self.assertEqual(cuts['pop0']['units'], by_count['pop0']['units'])
        self.assertEqual(pruned['lists']['pop0']['kept'], counted['lists']['pop0']['kept'])
        self.assertEqual(pruned['lists']['pop0']['kept'], {k('kto'), k('dom')})
        # ki: własna punktacja = próg POP (zostaje w POP), < próg POP0 (przycięty w POP0).
        self.assertLess(own[(k('ki'),)]['value'], cuts['pop0']['score'])
        self.assertIn(k('ki'), pruned['lists']['pop']['kept'])
        self.assertTrue(pruned['lists']['pop0']['kept'] <= pruned['lists']['pop']['kept'])
        # Próg POP0 równy własnej punktacji ki: ki zostaje (remis wchodzi), choć jego ranga jest za słaba.
        found, own, cuts, pruned = self.run_lists(ki, pop0_score=ki)
        self.assertIn(k('ki'), pruned['lists']['pop0']['kept'])

    def test_member_under_threshold_is_pruned_group_without_evidence_stays_whole(self):
        k = self.k
        found, own, cuts, pruned = self.run_lists(lambda found, own: own[(k('ki'),)]['value'] + 1e-6)
        kept = pruned['lists']['pop']['kept']
        self.assertEqual(pruned['lists']['pop']['pruned'], (k('ki'),))
        self.assertTrue({k('kia'), k('kto'), k('zamek:a'), k('zamek:b'), k('dom'), k('pies')} <= kept)

    def test_strongest_member_stays_below_threshold(self):
        k = self.k
        self.kwjp['lexemes'][k('kto')] = base_tests._kwjp_row(10, 1)
        nkjp = dict(self.nkjp, forms=dict(self.nkjp['forms'], kto=50))
        group = (k('ki'), k('kia'), k('kto'))
        found, own, cuts, pruned = self.run_lists(lambda found, own: found[group]['value'], nkjp, pop0=1)
        self.assertEqual(cuts['pop']['units'][-1], group)
        self.assertTrue(all(own[(m,)]['value'] < cuts['pop']['score'] for m in group))
        self.assertEqual(pruned['lists']['pop']['kept'] & set(group), {k('kia')})
        self.assertEqual(pruned['lists']['pop']['heads'], 1)

    def test_member_without_own_score_is_out(self):
        k = self.k
        nkjp = dict(self.nkjp, forms=dict(self.nkjp['forms'], kiach=7), matched=self.nkjp['matched'] + 7)
        found, own, cuts, pruned = self.run_lists(-100.0, nkjp)
        self.assertIsNone(own[(k('kia'),)]['value'])
        self.assertNotIn(k('kia'), pruned['lists']['pop']['kept'])
        self.assertIn(k('ki'), pruned['lists']['pop']['kept'])


class VariantScoreTests(unittest.TestCase):
    """Warianty jednego lematu (`pies:Sm1`/`Sm2`) razem także przy progu punktacji."""

    def test_variants_are_kept_together(self):
        k = lambda name: (S, name)
        row = base_tests._kwjp_row
        sm1, sm2, psi = k('pies:Sm1'), k('pies:Sm2'), k('psi')
        kwjp = {'lexemes': {sm1: row(1, 1), psi: row(400, 2), k('dom'): row(500, 3)},
                'groups': {(sm1, sm2): dict(row(1500, 6), status='AMBIGUOUS')}, 'mass': {'total': 10000}}
        owners = {'pies': (sm1, sm2), 'psem': (sm1,), 'psie': (sm2, psi), 'psi': (psi,), 'dom': (k('dom'),)}
        forms = {'pies': 3000, 'psem': 1, 'psie': 100, 'psi': 1000, 'dom': 5000}
        nkjp = {'forms': forms, 'total': 100000, 'matched': sum(forms.values())}
        relevant = frozenset(m for found in owners.values() for m in found)
        result = units(kwjp, 'e', relevant, nkjp, owners, eligible=relevant)
        found = measure(result, D3, 'lower-bound-absent')['units']
        members = member_units(result, kwjp, relevant, nkjp, owners)
        own = measure(members, D3, 'lower-bound-absent', floors=measure_floors(result, D3))['units']
        # Próg = własna punktacja pary: każdy wariant sam byłby pod progiem.
        cut = threshold(rank_units(found), result, {'by': 'score', 'value': own[(sm1, sm2)]['value']}, values=found)
        kept = prune_members(members, own, found, {'pop': cut})['lists']['pop']['kept']
        self.assertTrue({sm1, sm2} <= kept)
        self.assertNotIn(psi, kept)


class ConfigV3Tests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.directory = Path(self.work.name)
        self.base = load_json(ROOT / 'config/generator/pop.json')

    def tearDown(self):
        self.work.cleanup()

    def load(self, change, base=None):
        config = json.loads(json.dumps(base or self.base))
        change(config)
        path = self.directory / 'pop.json'
        path.write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
        return load_config(path)

    def test_repository_config_is_pop_v3(self):
        config = load_config(ROOT / 'config/generator/pop.json')
        self.assertEqual(config['version'], 'pop-v3')
        self.assertEqual(config['adr'], 'docs/adr/ADR-008-pop-v3-staly-prog.md')
        adr = (ROOT / config['adr']).read_text(encoding='utf-8')
        for text in ('config/generator/pop.json', 'config/generator/pop-v2.json', ISSUE_6, 'ADR-007'):
            self.assertIn(text, adr)
        self.assertEqual(config['d6'], {'pop': {'by': 'score', 'value': POP_SCORE},
                                        'pop0': {'by': 'score', 'value': POP0_SCORE}})
        # Poza wersją, ADR i D6 metoda jest ta sama co pop-v2 (D1–D5, D7–D9, straż, próbki).
        v2 = load_json(ROOT / 'config/generator/pop-v2.json')
        drop = lambda c: {k: v for k, v in c.items() if k not in ('version', 'adr', 'd6')}
        self.assertEqual(drop(self.base), drop(v2))
        text = (ROOT / 'config/generator/pop.json').read_text(encoding='utf-8')
        self.assertEqual(text, json.dumps(self.base, indent=2, ensure_ascii=False) + '\n')

    def test_v3_needs_score_for_pop_and_pop0(self):
        cases = {
            'POP liczba': lambda c: c['d6'].update(pop={'by': 'count', 'value': 60000}),
            'POP0 liczba': lambda c: c['d6'].update(pop0={'by': 'count', 'value': 20000}),
            'POP0 pokrycie': lambda c: c['d6'].update(pop0={'by': 'coverage', 'value': 0.9,
                                                           'denominator': 'kwjp-standard'}),
            'POP0 poniżej POP': lambda c: c['d6']['pop0'].update(value=POP_SCORE - 0.001),
            'POP0 bool': lambda c: c['d6']['pop0'].update(value=False),
            'POP0 tekst': lambda c: c['d6']['pop0'].update(value='0.57'),
            'POP pokrycie': lambda c: c['d6'].update(pop={'by': 'coverage', 'value': 0.98,
                                                         'denominator': 'kwjp-standard'}),
            'POP bool': lambda c: c['d6']['pop'].update(value=True),
            'POP tekst': lambda c: c['d6']['pop'].update(value='-1.04'),
            'POP null': lambda c: c['d6']['pop'].update(value=None),
            'POP klucz': lambda c: c['d6']['pop'].update(denominator='kwjp-all'),
            'ADR-007': lambda c: c.update(adr='docs/adr/ADR-007-metoda-pop-v1.md'),
            'd5 bez przycinania': lambda c: c['d5'].update(members='all'),
            'wycofanie NKJP': lambda c: c.update(d3={'source': 'kwjp', 'field': 'log-ipm'}, d4=None),
        }
        for label, change in cases.items():
            with self.subTest(label):
                self.assertEqual(_code(self.load, change).code, 2)
        # Nieskończoność i NaN nie są JSON-em kanonicznym: odmowa przy wczytaniu.
        path = self.directory / 'inf.json'
        path.write_text(json.dumps(self.base).replace('-1.042878629', '-Infinity'), encoding='utf-8')
        self.assertEqual(_code(load_config, path).code, 2)
        self.assertEqual(self.load(lambda c: c['d6']['pop'].update(value=-1))['d6']['pop']['value'], -1)
        # Próg POP0 równy progowi POP: POP0 = POP jest dozwolone (POP0 ⊆ POP nadal prawdziwe).
        same = self.load(lambda c: c['d6']['pop0'].update(value=POP_SCORE))
        self.assertEqual(same['d6']['pop0']['value'], POP_SCORE)

    def test_v2_still_refuses_score(self):
        v2 = load_json(ROOT / 'config/generator/pop-v2.json')
        error = _code(self.load, lambda c: c['d6'].update(pop={'by': 'score', 'value': -1.0}), v2)
        self.assertEqual(error.code, 2)


class BuildV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = pop_fixture(Path(cls.tmp.name) / 'pop', NKJP_POP_1GRAMS)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.directory = Path(self.work.name)

    def tearDown(self):
        self.work.cleanup()

    def build(self, score, pop0=DUZY):
        return build_pop(self.fixture['sources'], pop_config_v3(self.directory, score, pop0))

    def test_score_of_last_counted_unit_reproduces_count_lists(self):
        v2 = build_pop(self.fixture['sources'], pop_config(self.directory, 9, 6))
        v3 = self.build(FAJNY)
        self.assertEqual((v3['pop'], v3['pop0']), (v2['pop'], v2['pop0']))
        self.assertEqual((v3['method'], v3['adr']), ('pop-v3', 'docs/adr/ADR-008-pop-v3-staly-prog.md'))
        pop, pop0 = v3['thresholds']['pop'], v3['thresholds']['pop0']
        self.assertEqual((pop['by'], pop['score'], pop['rank'], pop['units'], pop['lexemes']), ('score', FAJNY, 6, 6, 8))
        self.assertEqual(pop['provisional'], ISSUE_6)
        self.assertNotIn('limit', pop)
        self.assertEqual(set(pop['coverage']), {'kwjp-standard', 'kwjp-all'})
        self.assertEqual((pop0['by'], pop0['score'], pop0['rank'], pop0['units'], pop0['lexemes']),
                         ('score', DUZY, 4, 4, 5))  # leksemy po przycięciu (lato poza)
        self.assertEqual(pop0['provisional'], ISSUE_6)
        self.assertNotIn('limit', pop0)
        # pop-v2 bez zmian w raporcie: bez `by`, z `limit`.
        self.assertNotIn('by', v2['thresholds']['pop'])
        self.assertEqual(v2['thresholds']['pop']['limit'], 9)

    def test_tie_at_threshold_enters_and_unmeasured_stays_out(self):
        result = self.build(ZAMEK)
        rows = {tuple(m[1] for m in row['unit']): row for row in result['units']}
        self.assertEqual(rows[('zamek:a', 'zamek:b')]['list'], 'POP')
        self.assertIn('zamek', result['pop'])
        self.assertIsNone(rows[('ul',)]['list'])
        self.assertIsNone(rows[('kumpel',)]['rank'])
        self.assertEqual(result['thresholds']['pop']['next_block'], {'units': 1, 'lexemes': 1, 'rank': 8})

    def test_cli_text_names_method_and_provisional_score(self):
        from literaki_slownik.cli import main
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(['pop', '--manifest', str(self.fixture['sources']), '--config',
                         str(pop_config_v3(self.directory, FAJNY, DUZY)), '--output-dir', str(self.directory / 'out')])
        self.assertEqual(code, 0, err.getvalue())
        for part in ('pop-v3', f'Próg POP: punktacja ≥ {FAJNY}', f'Próg POP0: punktacja ≥ {DUZY}', ISSUE_6):
            self.assertIn(part, out.getvalue())

    def test_pop0_threshold_below_pop_is_refused(self):
        # Próg POP0 < próg POP dałby POP0 poza POP: odmowa już przy konfiguracji (kod 2).
        error = _code(self.build, 5.05)
        self.assertEqual(error.code, 2)
        self.assertIn('POP0', str(error))


class PackageV3Tests(unittest.TestCase):
    """Pakiet pop-v3: POP do miary `bać` (rangi 1–5), POP0 do `duży` (1–4); `lato` wypada z obu własną punktacją."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.made = pop_package(cls.tmp.name, score=BAC, pop0=DUZY)
        cls.package = cls.made['package']

    @classmethod
    def tearDownClass(cls):
        for path in Path(cls.tmp.name).rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        cls.tmp.cleanup()

    def read(self, relative):
        return (self.package / relative).read_text(encoding='utf-8')

    def test_manifest_and_reports_name_the_method_and_threshold_kind(self):
        manifest = json.loads(self.read('release-manifest.json'))
        self.assertEqual((manifest['method'], manifest['adr']), ('pop-v3', 'docs/adr/ADR-008-pop-v3-staly-prog.md'))
        self.assertEqual(manifest['config_sha256'], sha256(self.made['config']))
        thresholds = json.loads(self.read('reports/thresholds.json'))
        self.assertEqual(thresholds['method'], 'pop-v3')
        self.assertEqual({k: thresholds['thresholds']['pop'][k] for k in ('by', 'score', 'rank', 'provisional')},
                         {'by': 'score', 'score': BAC, 'rank': 5, 'provisional': ISSUE_6})
        self.assertEqual({k: thresholds['thresholds']['pop0'][k] for k in ('by', 'score', 'rank', 'provisional')},
                         {'by': 'score', 'score': DUZY, 'rank': 4, 'provisional': ISSUE_6})
        rows = json.loads(self.read('reports/units.json'))['units']
        self.assertFalse([row for row in rows if 'value' in row])
        group, = [row for row in rows if 'lato@synthetic' in row['members']]
        meets = {'lato@synthetic': False, 'rok:S1@synthetic': True, 'rok:S2@synthetic': True}
        self.assertEqual(group['member_meets_score'], {'POP': meets, 'POP0': meets})
        self.assertEqual(group['members_in'], {'POP': ['rok:S1@synthetic', 'rok:S2@synthetic'],
                                               'POP0': ['rok:S1@synthetic', 'rok:S2@synthetic']})

    def test_limitations_state_both_score_thresholds_are_provisional(self):
        text = self.read('LIMITATIONS.md')
        for part in ('pop-v3', 'punktacja', 'tymczasow', ISSUE_6):
            self.assertIn(part, text)
        for name, value in (('POP', BAC), ('POP0', DUZY)):
            line, = [line for line in text.splitlines() if str(value) in line]
            self.assertTrue(line.startswith(f'- Próg {name} '), line)
            self.assertNotIn('limit', line)
        self.assertNotIn('limit', text)

    def test_independent_checker_passes(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = check_pop_package.main(['--pop-dir', str(self.package),
                                           '--standard', str(self.made['run'] / 'lists/standard.txt')])
        self.assertEqual(code, 0, out.getvalue() + err.getvalue())

    def test_explain_shows_score_thresholds_for_pop_and_pop0(self):
        run = self.made['run']
        lato = explain_pop(self.package, run, 'lato', 'pop')
        self.assertEqual(lato['reason'], 'PRUNED_WEAK_MEMBER')
        self.assertEqual({k: lato['threshold'][k] for k in ('by', 'score', 'rank', 'provisional')},
                         {'by': 'score', 'score': BAC, 'rank': 5, 'provisional': ISSUE_6})
        text = format_pop_explanation(lato)
        self.assertIn(f'punktacja ≥ {BAC}', text)
        self.assertIn(ISSUE_6, text)
        self.assertIn('własna punktacja', text)
        self.assertIn('lato@synthetic nie', text)
        self.assertEqual(explain_pop(self.package, run, 'fajny', 'pop')['reason'], 'BELOW_THRESHOLD')
        self.assertIn('własna punktacja ≥ próg POP: lato@synthetic nie', text)
        kot = explain_pop(self.package, run, 'kot', 'pop0')
        self.assertEqual((kot['reason'], kot['threshold']['by'], kot['threshold']['score'], kot['threshold']['limit']),
                         ('IN_POP0', 'score', DUZY, None))
        self.assertIn(f'Próg POP0: punktacja ≥ {DUZY}', format_pop_explanation(kot))
        lato0 = explain_pop(self.package, run, 'lato', 'pop0')
        self.assertEqual(lato0['reason'], 'PRUNED_WEAK_MEMBER')
        self.assertIn('własna punktacja ≥ próg POP0: lato@synthetic nie', format_pop_explanation(lato0))
        self.assertEqual(explain_pop(self.package, run, 'fajny', 'pop0')['reason'], 'BELOW_THRESHOLD')


if __name__ == '__main__':
    unittest.main()
