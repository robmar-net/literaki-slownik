"""Metoda pop-v2: warianty lematu przy przycinaniu (G1), straż częstych form (G2), warunki pakietu,
blokada zapisu w przebiegu i pakiecie LL-PL (W1), kody błędów danych (W2), CRLF w NKJP (I8), I4."""
import contextlib
import io
import json
import math
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from literaki_slownik import pop as pop_module
from literaki_slownik.canonical import load_json
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.pop import (build_package, build_pop, frequent_guard, load_config, measure, measure_floors,
                                  member_units, prune_members, rank_frequent_forms, rank_units, read_nkjp,
                                  threshold, units)
from tests.pop_helpers import NKJP_POP_1GRAMS, gz_write, pop_config, pop_fixture, pop_package

S = 'synthetic'
ROOT = Path(__file__).resolve().parent.parent
D3 = {'source': 'kwjp+nkjp', 'field': 'log-ipm', 'weight': 0.5}


def _row(freq, row, status='EXACT_CANDIDATE'):
    return {'F': freq, 'ARF': float(freq), '1-DP': 0.5, 'row': row, 'row_F': freq, 'rows': 1, 'genres': (),
            'status': status}


def _code(call, *args, **kwargs):
    with unittest.TestCase().assertRaises(GeneratorError) as raised:
        call(*args, **kwargs)
    return raised.exception


class VariantPoolTests(unittest.TestCase):
    """G1, wzór `pies:Sm1`/`pies:Sm2`: SGJP dzieli lemat na warianty; masa wspólna leży w wierszu AMBIGUOUS
    i formach NKJP obu wariantów. Każdy wariant sam ma słabe dowody (Sm1: EXACT 1, `psem` 1; Sm2: brak),
    razem są mocne. `psie` łączy wariant z `psi` (inny lemat), więc jednostka ma trzech członków.
    Progi: POP0 = 4 leksemy (jednostka + dom), POP = 5 (+ kot)."""

    def data(self, second):
        k = lambda name: (S, name)
        sm1, sm2, psi = k('pies:Sm1'), k(second), k('psi')
        kwjp = {'lexemes': {sm1: _row(1, 1), psi: _row(400, 2), k('dom'): _row(500, 3), k('kot'): _row(300, 4),
                            k('rzadki'): _row(6, 5)},
                'groups': {tuple(sorted((sm1, sm2))): _row(1500, 6, 'AMBIGUOUS')},
                'mass': {'total': 10000}}
        owners = {'pies': tuple(sorted((sm1, sm2))), 'psem': (sm1,), 'psie': tuple(sorted((sm2, psi))),
                  'psi': (psi,), 'dom': (k('dom'),), 'kot': (k('kot'),), 'rzadki': (k('rzadki'),)}
        forms = {'pies': 3000, 'psem': 1, 'psie': 100, 'psi': 1000, 'dom': 5000, 'kot': 2000, 'rzadki': 10}
        nkjp = {'forms': forms, 'total': 100000, 'matched': sum(forms.values())}
        relevant = frozenset(m for members in owners.values() for m in members)
        result = units(kwjp, 'e', relevant, nkjp, owners, eligible=relevant)
        found = measure(result, D3, 'lower-bound-absent')['units']
        ranks = rank_units(found)
        cuts = {name: threshold(ranks, result, {'by': 'count', 'value': limit}, values=found)
                for name, limit in (('pop0', 4), ('pop', 5))}
        members = member_units(result, kwjp, relevant, nkjp, owners)
        own = measure(members, D3, 'lower-bound-absent', floors=measure_floors(result, D3))['units']
        return {'sm1': sm1, 'sm2': sm2, 'psi': psi, 'result': result, 'ranks': ranks, 'cuts': cuts,
                'members': members, 'pruned': prune_members(members, own, found, cuts)}

    def test_variants_of_one_lemma_are_judged_together_and_kept(self):
        d = self.data('pies:Sm2')
        sm1, sm2, psi = d['sm1'], d['sm2'], d['psi']
        unit = tuple(sorted((psi, sm1, sm2)))
        self.assertEqual(d['ranks'][unit], 1)
        self.assertIn(unit, d['cuts']['pop0']['units'])
        pair = (sm1, sm2)
        self.assertIn(pair, d['members']['units'])
        # Wiersz AMBIGUOUS obu wariantów i ich wspólna forma NKJP należą do podjednostki; `psie` (inny lemat) nie.
        self.assertEqual(d['members']['units'][pair]['kwjp']['F'], 1501)
        self.assertEqual(d['members']['nkjp_f'][pair], 3001)
        self.assertEqual(d['members']['nkjp_f'][(psi,)], 1000)
        # F nie jest dzielone ani kopiowane: suma podjednostek = F jednostki.
        self.assertEqual(sum(u['kwjp']['F'] for u in d['members']['units'].values() if u['unit'] == unit),
                         d['result']['units'][unit]['kwjp']['F'])
        for name in ('pop0', 'pop'):
            kept = d['pruned']['lists'][name]['kept']
            self.assertTrue({sm1, sm2} <= kept, name)
            self.assertNotIn(psi, kept, name)

    def test_different_lemmas_are_never_pooled(self):
        # Te same dane, ale drugi wariant ma inny lemat: każdy jest oceniany sam i oba wypadają.
        d = self.data('psina:Sm2')
        sm1, sm2, psi = d['sm1'], d['sm2'], d['psi']
        self.assertNotIn(tuple(sorted((sm1, sm2))), d['members']['units'])
        kept = d['pruned']['lists']['pop0']['kept']
        self.assertFalse({sm1, sm2} & kept)
        self.assertIn(psi, kept)  # najmocniejszy członek zostaje zawsze


class FrequentGuardUnitTests(unittest.TestCase):
    def test_ranking_counts_only_lowercase_spellings_by_f_then_row(self):
        # Lista `kwjp_orth` rozróżnia wielkość liter: `Ala`/`ALA` (imię) nie liczą się do formy `ala`.
        rows = [(1, 'Ala', 900), (2, 'ma', 50), (3, 'kota', 10), (4, 'ALA', 99), (5, 'psa', 50), (6, 'x.', 70),
                (7, 'ala', 5), (8, 'ma', 1)]
        allowed = {'ala', 'ma', 'kota', 'psa'}
        self.assertEqual(rank_frequent_forms(rows, allowed, 10), ['ma', 'psa', 'kota', 'ala'])
        self.assertEqual(rank_frequent_forms(rows, allowed, 2), ['ma', 'psa'])

    def test_guard_passes_or_lists_missing_forms_with_code_4(self):
        ranked = ['a', 'b', 'c', 'd']
        lists = {'pop': {'a', 'b', 'c'}, 'pop0': {'a'}}
        report = frequent_guard(ranked, lists, {'pop_top': 3, 'pop0_top': 1}, 'orth-all')
        self.assertEqual(report['pop'], {'top': 3, 'checked': 3, 'missing': 0})
        self.assertEqual(report['pop0'], {'top': 1, 'checked': 1, 'missing': 0})
        self.assertEqual(report['source_id'], 'orth-all')
        error = _code(frequent_guard, ranked, lists, {'pop_top': 4, 'pop0_top': 2}, 'orth-all')
        self.assertEqual(error.code, 4)
        self.assertIn('d', str(error))
        self.assertIn('b', str(error))
        many = [f'w{n:03}' for n in range(80)]
        error = _code(frequent_guard, many, {'pop': set(), 'pop0': set()}, {'pop_top': 80, 'pop0_top': 1}, 'o')
        self.assertIn('w049', str(error))
        self.assertNotIn('w050', str(error))


class ConfigV2Tests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.directory = Path(self.work.name)
        self.base = load_json(ROOT / 'config/generator/pop.json')

    def tearDown(self):
        self.work.cleanup()

    def load(self, change):
        config = json.loads(json.dumps(self.base))
        change(config)
        path = self.directory / 'pop.json'
        path.write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
        return load_config(path)

    def test_repository_config_is_pop_v2(self):
        config = load_config(ROOT / 'config/generator/pop.json')
        self.assertEqual(config['version'], 'pop-v2')
        self.assertEqual(config['d5'], {'groups': 'e-common', 'members': 'prune-weak-members-v2'})
        self.assertEqual(config['frequent_guard'], {'pop_top': 20000, 'pop0_top': 5000})
        self.assertEqual(config['d8'], 'lower-bound-kwjp-absent')

    def test_bad_values_are_code_2(self):
        cases = {
            'stare przycinanie': lambda c: c['d5'].update(members='prune-weak-members'),
            'stare D8': lambda c: c.update(d8='lower-bound-absent'),
            'stara wersja': lambda c: c.update(version='pop-v1'),
            'brak straży': lambda c: c.pop('frequent_guard'),
            'straż tekst': lambda c: c['frequent_guard'].update(pop_top='20000'),
            'straż bool': lambda c: c['frequent_guard'].update(pop0_top=True),
            'straż float': lambda c: c['frequent_guard'].update(pop_top=20000.0),
            'straż zero': lambda c: c['frequent_guard'].update(pop0_top=0),
            'straż POP0 > POP': lambda c: c['frequent_guard'].update(pop0_top=30000),
            'straż klucz': lambda c: c['frequent_guard'].update(extra=1),
            'słowo wielką literą': lambda c: c.update(must_include_pop0=['Kot']),
            'słowo bez NFC': lambda c: c.update(must_include_pop0=['kót']),
        }
        for label, change in cases.items():
            with self.assertRaises(GeneratorError, msg=label) as raised:
                self.load(change)
            self.assertEqual(raised.exception.code, 2, label)


class BuildV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.fixture = pop_fixture(cls.root / 'pop', NKJP_POP_1GRAMS)

    @classmethod
    def tearDownClass(cls):
        for path in cls.root.rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        cls.tmp.cleanup()

    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.directory = Path(self.work.name)

    def tearDown(self):
        self.work.cleanup()

    def test_frequent_guard_reported_and_miss_is_code_4(self):
        result = build_pop(self.fixture['sources'], pop_config(self.directory, 9, 6))
        guard = result['thresholds']['frequent_guard']
        # rok, polska, lata: formy STANDARD z leksemem w rankingu; `ul.` spoza STANDARD; `Zamek` i `Polska`
        # wielką literą się nie liczą (inaczej `zamek`, poza POP przy progu 9, zatrzymałby `pop`).
        self.assertEqual((guard['source_id'], guard['ranked_forms']), ('corpus-orth-all', 3))
        self.assertEqual(guard['pop0'], {'top': 5000, 'checked': 3, 'missing': 0})
        # `kumple` (kumpel bez danych w liście lematów KWJP) nie liczy się do straży; raport osobno.
        self.assertEqual(result['thresholds']['guard_skipped_no_kwjp_lemma'], {'count': 1, 'examples': ['kumple']})
        # POP0 = 2 leksemy (polski, kot): grupa rok/lato się nie mieści, więc częste `rok` i `lata` wypadają.
        error = _code(build_pop, self.fixture['sources'], pop_config(self.directory, 9, 2))
        self.assertEqual(error.code, 4)
        self.assertIn('rok', str(error))
        self.assertIn('lata', str(error))
        # Liczby z konfiguracji: straż POP0 tylko dla najczęstszej formy (`rok`).
        ok = build_pop(self.fixture['sources'], pop_config(self.directory, 9, 6,
                                                             frequent_guard={'pop_top': 3, 'pop0_top': 1}))
        self.assertEqual(ok['thresholds']['frequent_guard']['pop0'], {'top': 1, 'checked': 1, 'missing': 0})

    def test_output_dir_inside_run_or_release_is_code_2_before_any_work(self):
        config = pop_config(self.directory, 9, 6)
        refuse = mock.Mock(side_effect=AssertionError('praca przed blokadą'))
        for parent in (self.fixture['run'], self.fixture['release'], self.fixture['run'] / 'lists'):
            target = parent / 'pop-inside'
            with mock.patch.object(pop_module, 'build_pop', refuse):
                error = _code(build_package, self.fixture['sources'], config, target)
            self.assertEqual(error.code, 2, parent)
            self.assertFalse(target.exists())
        error = _code(build_package, self.fixture['sources'], config, self.fixture['run'])
        self.assertEqual(error.code, 2)
        refuse.assert_not_called()

    def test_data_errors_map_to_code_4_without_traceback(self):
        config = pop_config(self.directory, 9, 6)
        for raised in (sqlite3.DatabaseError('file is not a database'), KeyError('ARF'), ValueError('zły kształt')):
            with mock.patch.object(pop_module, '_lexicon', side_effect=raised):
                error = _code(build_pop, self.fixture['sources'], config)
            self.assertEqual(error.code, 4, raised)
        from literaki_slownik.cli import main
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(pop_module, '_lexicon', side_effect=KeyError('ARF')), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(['pop', '--manifest', str(self.fixture['sources']), '--config', str(config),
                         '--output-dir', str(self.directory / 'out'), '--json'])
        self.assertEqual(code, 4)
        self.assertNotIn('Traceback', err.getvalue())
        self.assertEqual(json.loads(out.getvalue())['diagnostics'][0]['code'], 4)

    def test_crlf_nkjp_line_is_code_4(self):
        path = gz_write(self.directory / 'crlf.gz', '      5 duży\r\n')
        error = _code(read_nkjp, path, 'full-nfc', {'duży': ((S, 'duży'),)})
        self.assertEqual(error.code, 4)


class PackageV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.made = pop_package(cls.tmp.name)
        cls.package = cls.made['package']

    @classmethod
    def tearDownClass(cls):
        for path in Path(cls.tmp.name).rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        cls.tmp.cleanup()

    def read(self, relative):
        return (self.package / relative).read_text(encoding='utf-8')

    def test_terms_follow_ll_pl_lists_section(self):
        terms = self.read('TERMS.md')
        self.assertNotIn('Wybór i układ', terms)
        for text in ('BSD-2-Clause', 'pełną atrybucją', 'nie deklaruje wyłącznych praw', 'KWJP', 'NKJP',
                     'ATTRIBUTIONS.md'):
            self.assertIn(text, terms)

    def test_limitations_state_status_and_game_integration_neutrally(self):
        text = self.read('LIMITATIONS.md')
        self.assertNotIn('nie jest wydaniem', text)
        self.assertNotIn('gra dziś', text)
        self.assertIn('Podłączenie POP do gry to osobna praca; POP ⊆ LL-PL STANDARD.', text)
        self.assertIn('BUILT', text)

    def test_thresholds_report_guard_and_sample_has_frequent_outside_stratum(self):
        thresholds = json.loads(self.read('reports/thresholds.json'))
        self.assertEqual(thresholds['method'], 'pop-v2')
        self.assertEqual(thresholds['thresholds']['frequent_guard']['pop']['missing'], 0)
        sample = json.loads(self.read('reports/sample.json'))
        # Wszystkie częste formy fikstury są w POP, więc warstwa jest pusta, ale jawna.
        self.assertIn('czeste-poza-lista', sample['strata'])
        self.assertEqual(sample['strata']['czeste-poza-lista']['population'], 0)


class AsymmetricBoundTests(unittest.TestCase):
    """D8 `lower-bound-kwjp-absent`: brak w KWJP = dolna granica KWJP; brak w NKJP = sama KWJP."""

    def test_kwjp_absent_is_bounded_nkjp_absent_is_kwjp_only(self):
        k = lambda name: (S, name)
        kwjp = {'lexemes': {k('a'): _row(100, 1), k('c'): _row(10, 2)}, 'groups': {}, 'mass': {'total': 1000}}
        owners = {'a': (k('a'),), 'b': (k('b'),), 'c': (k('c'),)}
        forms = {'b': 50, 'c': 10}
        nkjp = {'forms': forms, 'total': 10000, 'matched': 60}
        relevant = frozenset(owners[f][0] for f in owners)
        result = units(kwjp, 'e', relevant, nkjp, owners, eligible=relevant)
        found = measure(result, D3, 'lower-bound-kwjp-absent')['units']
        kwjp_only = round(math.log10(100 / 1000 * 1e6), 9)
        self.assertEqual((found[(k('a'),)]['value'], found[(k('a'),)]['flags']), (kwjp_only, ('single_source:kwjp',)))
        self.assertEqual(found[(k('b'),)]['flags'], ('bound:kwjp',))
        # Stara wartość dawała `a` dolną granicę NKJP (niżej).
        old = measure(result, D3, 'lower-bound-absent')['units']
        self.assertLess(old[(k('a'),)]['value'], found[(k('a'),)]['value'])


class SharedDominantTests(unittest.TestCase):
    """NKJP podjednostki niewiarygodne, gdy masa jej form wspólnych z innym lematem (nieprzypisana) przewyższa
    jej własną masę NKJP (wzór `głównie`: forma `głównie` wspólna z `głównia`)."""

    def data(self, own, kwjp_f=1000):
        k = lambda name: (S, name)
        t, g = k('głównie:T'), k('głównia')
        lexemes = {t: _row(kwjp_f, 1), k('dom'): _row(500, 2)} if kwjp_f else {k('dom'): _row(500, 2)}
        kwjp = {'lexemes': lexemes, 'groups': {}, 'mass': {'total': 10000}}
        owners = {'głównie': (g, t), 'głównież': (t,), 'główni': (g,), 'dom': (k('dom'),)}
        forms = {'głównie': 5000, 'głównież': own, 'główni': 2, 'dom': 3000}
        nkjp = {'forms': forms, 'total': 100000, 'matched': sum(forms.values())}
        relevant = frozenset((t, g, k('dom')))
        result = units(kwjp, 'e', relevant, nkjp, owners, eligible=relevant)
        members = member_units(result, kwjp, relevant, nkjp, owners)
        own_measure = measure(members, D3, 'lower-bound-kwjp-absent', floors=measure_floors(result, D3))['units']
        return t, members, own_measure

    def test_small_own_nkjp_under_dominant_shared_form_is_ignored(self):
        t, members, measured = self.data(3)
        self.assertEqual(members['units'][(t,)]['nkjp']['status'], 'SHARED_DOMINANT')
        self.assertNotIn((t,), members['nkjp_f'])
        self.assertEqual(measured[(t,)]['flags'], ('single_source:kwjp',))

    def test_without_own_kwjp_nkjp_is_the_only_evidence_and_stays(self):
        # Wzór `siebie`: wiersz KWJP niedopasowany, więc NKJP jest jedynym dowodem i zostaje mimo form wspólnych.
        t, members, measured = self.data(3, kwjp_f=0)
        self.assertEqual(members['units'][(t,)]['nkjp']['status'], 'OBSERVED')
        self.assertEqual(members['nkjp_f'][(t,)], 3)
        self.assertIsNotNone(measured[(t,)]['value'])

    def test_own_nkjp_larger_than_shared_stays(self):
        t, members, measured = self.data(6000)
        self.assertEqual(members['units'][(t,)]['nkjp']['status'], 'OBSERVED')
        self.assertEqual(members['nkjp_f'][(t,)], 6000)
        self.assertEqual(measured[(t,)]['flags'], ())


class NkjpOutdatedTests(unittest.TestCase):
    """Rew. 4: KWJP ≥ 100 razy częstsze niż NKJP (różnica log-ipm ≥ 2) → miara z samej KWJP (`koronawirus`)."""

    def test_kwjp_hundred_times_more_frequent_drops_nkjp_reverse_unchanged(self):
        k = lambda name: (S, name)
        kwjp = {'lexemes': {k('nowe'): _row(1000, 1), k('stare'): _row(1, 2), k('equal'): _row(10, 3)},
                'groups': {}, 'mass': {'total': 100000}}
        owners = {'nowe': (k('nowe'),), 'stare': (k('stare'),), 'equal': (k('equal'),)}
        nkjp = {'forms': {'nowe': 1, 'stare': 1000, 'equal': 10}, 'total': 100000, 'matched': 1011}
        relevant = frozenset(o[0] for o in owners.values())
        result = units(kwjp, 'e', relevant, nkjp, owners, eligible=relevant)
        found = measure(result, D3, 'lower-bound-kwjp-absent')['units']
        self.assertEqual(found[(k('nowe'),)], {'value': 4.0, 'status': 'MEASURED', 'flags': ('nkjp_outdated',)})
        self.assertEqual(found[(k('stare'),)]['flags'], ())
        self.assertEqual(found[(k('stare'),)]['value'], 2.5)
        self.assertEqual(found[(k('equal'),)], {'value': 2.0, 'status': 'MEASURED', 'flags': ()})
        # Granica: różnica dokładnie 2 też liczy się jako przestarzałe.
        nkjp['forms']['nowe'] = 10
        result = units(kwjp, 'e', relevant, nkjp, owners, eligible=relevant)
        self.assertEqual(measure(result, D3, 'lower-bound-kwjp-absent')['units'][(k('nowe'),)]['flags'],
                         ('nkjp_outdated',))


if __name__ == '__main__':
    unittest.main()
