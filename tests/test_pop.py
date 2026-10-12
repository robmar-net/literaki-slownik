"""POP/POP0: manifest źródeł, piny podstawy LL-PL, wejścia (A1, C2) i dane z bazy (A6, A8, A9)."""
import gzip
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from literaki_slownik.canonical import load_json, sha256, write_json
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.database import connect
from literaki_slownik import pop as pop_module
from literaki_slownik.canonical import dumps
from literaki_slownik.pop import (CLEANING_RULES, build_package, build_pop, check_inputs, coverage, database_sha256,
                                  form_owners, forms_for, kwjp_measures, load_config, load_constructions,
                                  load_form_classes, load_forms, load_forms_accepted, load_kwjp, load_kwjp_lists,
                                  load_lexemes, load_sources,
                                  measure, measure_floors, member_ranks, member_units, prune_members, nkjp_collisions, nkjp_form_status, nkjp_lexeme_ranks,
                                  percentiles, rank_units, read_nkjp, read_standard, spearman, tag_classes,
                                  threshold, top_overlap, units)
from tests.pop_helpers import (NKJP_POP_1GRAMS, gz_write, kwjp_lemma_sources, pop_config, pop_fixture,
                               pop_package, write_pop_sources)


class PopSourcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = pop_fixture(Path(cls.tmp.name) / 'pop')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.directory = Path(self.work.name)

    def tearDown(self):
        self.work.cleanup()

    def sources(self, **overrides):
        f = self.fixture
        return write_pop_sources(self.directory / 'pop-sources.json', f['run'], f['release'], f['nkjp'], **overrides)

    def code(self, call, *args):
        with self.assertRaises(GeneratorError) as raised:
            call(*args)
        return raised.exception.code, str(raised.exception)

    def test_valid_manifest_returns_paths_and_database_hash(self):
        f = self.fixture
        sources = load_sources(self.sources())
        result = check_inputs(sources, f['run'], f['release'])
        self.assertEqual(result['database_sha256'], sha256(f['run'] / 'build.sqlite'))
        self.assertEqual(result['database_sha256'], database_sha256(f['run'] / 'build.sqlite'))
        self.assertEqual(Path(result['database']), (f['run'] / 'build.sqlite').resolve())
        self.assertEqual(Path(result['standard']), (f['run'] / 'lists/standard.txt').resolve())
        self.assertEqual(Path(result['nkjp']), f['nkjp'].resolve())
        self.assertEqual(result['release_manifest_sha256'], sha256(f['release'] / 'release-manifest.json'))
        standard = read_standard(result['standard'])
        self.assertIsInstance(standard, frozenset)
        self.assertTrue({'rok', 'lata', 'polska', 'ul'} <= standard)
        # Bez --run-dir i --release-dir ścieżki pochodzą z manifestu POP.
        self.assertEqual(check_inputs(sources)['database_sha256'], result['database_sha256'])

    def test_wrong_database_pin_is_code_3(self):
        f = self.fixture
        sources = load_sources(self.sources(database_sha256='0' * 64))
        self.assertEqual(self.code(check_inputs, sources, f['run'], f['release'])[0], 3)

    def test_run_export_hash_differs_from_release_manifest_is_code_3(self):
        f = self.fixture
        release = self.directory / 'release'
        shutil.copytree(f['release'], release)
        target = release / 'release-manifest.json'
        target.chmod(0o644)
        data = load_json(target)
        data['package_id'] = 'LL-PL-INNY'
        write_json(target, data)
        sources = load_sources(self.sources(release_manifest_sha256=sha256(target)))
        code, message = self.code(check_inputs, sources, f['run'], release)
        self.assertEqual(code, 3)
        self.assertIn('export', message)
        # Pin zgodny z przebiegiem, ale inny plik w --release-dir: też kod 3.
        sources = load_sources(self.sources())
        self.assertEqual(self.code(check_inputs, sources, f['run'], release)[0], 3)

    def test_wrong_standard_or_nkjp_hash_is_code_3(self):
        f = self.fixture
        for override in ({'standard_sha256': 'f' * 64}, {'nkjp_sha256': 'e' * 64}):
            sources = load_sources(self.sources(**override))
            self.assertEqual(self.code(check_inputs, sources, f['run'], f['release'])[0], 3, override)

    def test_run_not_frozen_is_code_5(self):
        f = self.fixture
        run = self.directory / 'run'
        shutil.copytree(f['run'], run)
        manifest = load_json(run / 'manifest.json')
        manifest['readiness'] = 'VERIFIED'
        write_json(run / 'manifest.json', manifest)
        sources = load_sources(self.sources())
        self.assertEqual(self.code(check_inputs, sources, run, f['release'])[0], 5)

    def test_foreign_input_or_unknown_key_is_code_2(self):
        path = self.sources()
        manifest = json.loads(path.read_text(encoding='utf-8'))
        sjp = dict(manifest['inputs'][1], source_id='sjp', kind='sjp')
        cases = [
            {**manifest, 'inputs': manifest['inputs'] + [sjp]},
            {**manifest, 'extra': True},
            {**manifest, 'base': {**manifest['base'], 'extra': 1}},
            {**manifest, 'inputs': [dict(manifest['inputs'][0], extra='x'), manifest['inputs'][1]]},
            {**manifest, 'inputs': manifest['inputs'][:1]},
            {**manifest, 'version': 'pop-sources-v0'},
        ]
        for case in cases:
            path.write_text(json.dumps(case, ensure_ascii=False), encoding='utf-8')
            self.assertEqual(self.code(load_sources, path)[0], 2, case)


S = 'synthetic'


class PopDatabaseTests(unittest.TestCase):
    """Leksemy, formy i KWJP z bazy tylko do odczytu."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = pop_fixture(Path(cls.tmp.name) / 'pop')
        cls.database = cls.fixture['database']
        cls.standard = read_standard(cls.fixture['run'] / 'lists/standard.txt')
        cls.lemma_sources = {g: s for s, g in kwjp_lemma_sources(cls.fixture['run']).items()}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def measures(self):
        with connect(self.database, readonly=True) as db:
            lexemes = load_lexemes(db)
            rows, genres = load_kwjp_lists(db, self.lemma_sources, lexemes)
        return kwjp_measures(rows, genres)

    def test_lexeme_key_is_source_and_lemma_id(self):
        with connect(self.database, readonly=True) as db:
            lexemes = load_lexemes(db)
            ids = dict(db.execute('select lemma_id,id from lexeme'))
        self.assertEqual(lexemes[ids['rok:S1']]['key'], (S, 'rok:S1'))
        self.assertEqual(lexemes[ids['lato']]['pos'], ('subst',))
        self.assertTrue(lexemes[ids['Polska']]['proper'])
        self.assertFalse(lexemes[ids['polski']]['proper'])
        result = self.measures()
        self.assertIn((S, 'lato'), result['lexemes'])
        self.assertTrue(all(isinstance(k, tuple) and len(k) == 2 and all(isinstance(p, str) for p in k)
                            for k in result['lexemes']))
        self.assertEqual(result['lexemes'][(S, 'lato')]['F'], 20)

    def test_several_rows_of_one_lexeme_sum_f_and_take_rest_from_max_f_row(self):
        bac = self.measures()['lexemes'][(S, 'bać')]
        # 10 + 30 + 30; remis 30/30 rozstrzyga klucz wiersza (fin, wiersz 11).
        self.assertEqual(bac['F'], 70)
        self.assertEqual((bac['ARF'], bac['1-DP'], bac['row']), ('3', '0.8', 11))
        self.assertEqual(bac['rows'], 3)
        # Gatunki z wiersza fin; publicystyka ma tylko praet. F gatunków nie wchodzi do sumy.
        self.assertEqual(bac['genres'], ('fakt', 'fikcja'))
        self.assertEqual(self.measures()['mass'], {'total': 393, 'EXACT_CANDIDATE': 265, 'AMBIGUOUS': 120,
                                                   'UNMATCHED': 8})

    def test_ambiguous_zamek_is_a_group_without_member_f(self):
        result = self.measures()
        group = ((S, 'zamek:a'), (S, 'zamek:b'))
        self.assertEqual(result['groups'][group]['F'], 30)
        self.assertEqual(result['groups'][group]['status'], 'AMBIGUOUS')
        self.assertNotIn((S, 'zamek:a'), result['lexemes'])
        self.assertNotIn((S, 'zamek:b'), result['lexemes'])
        rok = result['groups'][((S, 'rok:S1'), (S, 'rok:S2'))]
        self.assertEqual((rok['F'], rok['genres']), (90, ('fikcja',)))
        self.assertNotIn((S, 'rok:S1'), result['lexemes'])

    def test_lexeme_forms_come_only_from_standard_keys(self):
        with connect(self.database, readonly=True) as db:
            forms = load_forms(db, self.standard)
            accepted = load_forms_accepted(db, self.standard)
        self.assertEqual(forms[(S, 'rok:S1')], frozenset({'rok', 'lata'}))
        self.assertEqual(forms[(S, 'lato')], frozenset({'lato', 'lata'}))
        self.assertEqual(forms[(S, 'Polska')], frozenset({'polska'}))
        self.assertNotIn((S, 'kotek'), forms)
        self.assertTrue(all(f <= self.standard for f in forms.values()))
        # Reguła (ii): analiza przyjęta w STANDARD; zawsze zawarta w regule (i).
        self.assertNotIn((S, 'kotek'), accepted)
        self.assertTrue(all(accepted[k] <= forms[k] for k in accepted))
        self.assertEqual(accepted[(S, 'bać')], frozenset({'boi', 'bał', 'bojąc'}))

    def test_construction_form_goes_to_component_lexeme(self):
        with connect(self.database, readonly=True) as db:
            result = load_constructions(db, self.standard)
        self.assertEqual(result['forms'][(S, 'duży')], frozenset({'nieduży'}))
        self.assertEqual(result['forms'][(S, 'polski')], frozenset({'niepolska', 'niepolski'}))
        self.assertEqual(result['counts'], {'one': 4, 'none': 0, 'several': 0})
        self.assertEqual(result['only_constructions'], 4)

    def test_colloquial_is_pot_in_any_interpretation(self):
        with connect(self.database, readonly=True) as db:
            lexemes = {v['key']: v for v in load_lexemes(db).values()}
        self.assertTrue(lexemes[(S, 'fajny')]['colloquial'])
        self.assertTrue(lexemes[(S, 'kumpel')]['colloquial'])
        self.assertFalse(lexemes[(S, 'duży')]['colloquial'])
        self.assertEqual(lexemes[(S, 'kumpel')]['qualifiers'], ('pot.',))

    def test_database_hash_unchanged_and_queries_bounded(self):
        before = database_sha256(self.database)
        with connect(self.database, readonly=True) as db:
            lexemes = load_lexemes(db)
            load_kwjp(db, self.lemma_sources['all'], lexemes)
            load_forms(db, self.standard)
            load_forms_accepted(db, self.standard)
            load_constructions(db, self.standard)
        self.assertEqual(database_sha256(self.database), before)
        source = (Path(__file__).resolve().parent.parent / 'literaki_slownik/pop.py').read_text(encoding='utf-8')
        self.assertNotIn('left join evidence_candidate', source.lower())
        self.assertNotIn('order by', source.lower())


class PopNkjpTests(unittest.TestCase):
    """NKJP 1grams: czytanie, reguły czyszczenia D4, kolizje i jednoznaczność form (A10, C7, C8, C14)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = pop_fixture(Path(cls.tmp.name) / 'pop')
        with connect(cls.fixture['database'], readonly=True) as db:
            cls.owners = form_owners(db)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, rule, keys=None):
        return read_nkjp(self.fixture['nkjp'], rule, self.owners if keys is None else keys)

    def test_parser_streams_nfc_lowercase_and_sums_by_game_key(self):
        result = self.read('full-nfc')
        # Polska (15) i polska (40) to jeden klucz gry; suma całości liczona ze wszystkich wierszy.
        self.assertEqual(result['forms']['polska'], 55)
        self.assertEqual(result['total'], 199)
        self.assertEqual(result['lines'], 9)
        self.assertEqual(result['matched'], 55 + 10 + 25 + 20 + 8 + 1)
        # W pamięci tylko klucze form SGJP: `ul.` i `ok.` nie są formami.
        self.assertNotIn('ul.', result['forms'])
        self.assertTrue(set(result['forms']) <= set(self.owners))
        path = gz_write(Path(self.tmp.name) / 'nfd.gz', '      3 DUZ\u0307Y\n      2 duży\n')
        self.assertEqual(read_nkjp(path, 'full-nfc', self.owners)['forms'], {'duży': 5})
        broken = gz_write(Path(self.tmp.name) / 'broken.gz', '      3 duży\nduży 3\n')
        with self.assertRaises(GeneratorError) as raised:
            read_nkjp(broken, 'full-nfc', self.owners)
        self.assertEqual((raised.exception.code, raised.exception.row), (4, 2))
        with self.assertRaises(GeneratorError) as raised:
            read_nkjp(self.fixture['nkjp'], 'strip-all', self.owners)
        self.assertEqual(raised.exception.code, 2)

    def test_three_cleaning_rules_with_versioned_ids(self):
        keys = set(self.owners) | {'ok'}
        self.assertEqual(set(CLEANING_RULES), {'full-nfc', 'strip-edges', 'strip-edges-keep-dot'})
        found = {rule: self.read(rule, keys) for rule in CLEANING_RULES}
        for rule, result in found.items():
            self.assertEqual(result['rule'], rule)
            self.assertRegex(result['rule_id'], r'^nkjp-clean-[a-z-]+-v[0-9]+$')
            self.assertEqual(result['total'], 199)
        self.assertEqual(len({r['rule_id'] for r in found.values()}), 3)
        self.assertEqual(found['full-nfc']['forms']['ul'], 10)
        self.assertNotIn('ok', found['full-nfc']['forms'])
        self.assertEqual(found['strip-edges']['forms']['ul'], 60)
        self.assertEqual(found['strip-edges']['forms']['ok'], 30)
        self.assertEqual(found['strip-edges-keep-dot']['forms']['ul'], 10)
        self.assertNotIn('ok', found['strip-edges-keep-dot']['forms'])

    def test_collision_list_gives_mass_of_both_sides(self):
        keys = set(self.owners) | {'ok'}
        collisions = nkjp_collisions(self.read('strip-edges', keys))
        self.assertEqual(collisions, [
            {'key': 'ul', 'kept': 10, 'merged': 50, 'sources': [('ul.', 50)]},
            {'key': 'ok', 'kept': 0, 'merged': 30, 'sources': [('ok.', 30)]},
        ])
        self.assertEqual(nkjp_collisions(self.read('strip-edges', keys), top=1), collisions[:1])
        self.assertEqual(nkjp_collisions(self.read('full-nfc', keys)), [])
        self.assertEqual(nkjp_collisions(self.read('strip-edges-keep-dot', keys)), [])

    def test_polska_shared_with_proper_name_gives_no_f_to_polski(self):
        self.assertEqual(self.owners['polska'], ((S, 'Polska'), (S, 'polski')))
        self.assertEqual(self.owners['polski'], ((S, 'polski'),))
        ranks = nkjp_lexeme_ranks(self.read('full-nfc'), self.owners)
        # 55 wystąpień `polska` nie trafia ani do nazwy własnej, ani do przymiotnika.
        for key in ((S, 'Polska'), (S, 'polski')):
            self.assertNotEqual(ranks['lexemes'][key]['status'], 'OBSERVED', key)
            self.assertIsNone(ranks['lexemes'][key]['rank'])
        self.assertEqual(ranks['mass']['shared'], 55 + 25 + 20)

    def test_lata_of_rok_and_lato_gives_f_to_nobody(self):
        self.assertEqual(self.owners['lata'], ((S, 'lato'), (S, 'rok:S1')))
        ranks = nkjp_lexeme_ranks(self.read('full-nfc'), self.owners)
        for key in ((S, 'lato'), (S, 'rok:S1'), (S, 'rok:S2')):
            self.assertNotEqual(ranks['lexemes'][key]['status'], 'OBSERVED', key)
        # Tylko formy jednoznaczne: ul (10), duży (8), fajny (1). Każdy ma jedną formę i dostaje rangę.
        observed = {k: (v['rank'], v['percentile']) for k, v in ranks['lexemes'].items() if v['status'] == 'OBSERVED'}
        self.assertEqual(observed, {(S, 'ul'): (1, 100.0), (S, 'duży'): (2, 66.6667), (S, 'fajny'): (3, 33.3333)})
        # C14: na wyjściu tylko ranga i percentyl, bez liczby NKJP leksemu.
        for value in ranks['lexemes'].values():
            self.assertEqual(set(value), {'status', 'rank', 'percentile'})

    def test_form_without_nkjp_row_is_not_in_published_list_never_zero(self):
        nkjp = self.read('full-nfc')
        self.assertEqual(nkjp_form_status(nkjp, 'kumpel'), 'NOT_IN_PUBLISHED_LIST')
        self.assertEqual(nkjp_form_status(nkjp, 'duży'), 'OBSERVED')
        ranks = nkjp_lexeme_ranks(nkjp, self.owners)
        self.assertEqual(ranks['lexemes'][(S, 'kumpel')],
                         {'status': 'NOT_IN_PUBLISHED_LIST', 'rank': None, 'percentile': None})
        self.assertNotIn(0, [v['rank'] for v in ranks['lexemes'].values()])
        # Każdy leksem SGJP ma status, także bez żadnej formy w NKJP.
        everyone = {key for keys in self.owners.values() for key in keys}
        self.assertEqual(set(ranks['lexemes']), everyone)


def _unit(*names):
    return tuple((S, name) for name in names)


KWJP_ONLY = {'source': 'kwjp', 'field': 'F'}


class PopRankingTests(unittest.TestCase):
    """Jednostki D5, miary D3/D8, rangi, pokrycie D1, progi D6, formy D2, Spearman (C5–C9, C14)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = pop_fixture(Path(cls.tmp.name) / 'pop')
        standard = read_standard(cls.fixture['run'] / 'lists/standard.txt')
        lemma_sources = {g: s for s, g in kwjp_lemma_sources(cls.fixture['run']).items()}
        with connect(cls.fixture['database'], readonly=True) as db:
            lexemes = load_lexemes(db)
            rows, genres = load_kwjp_lists(db, lemma_sources, lexemes)
            cls.owners = form_owners(db, lexemes)
            cls.forms = load_forms(db, standard, lexemes)
            cls.accepted = load_forms_accepted(db, standard, lexemes)
            cls.constructions = load_constructions(db, standard, lexemes)
            cls.classes = load_form_classes(db, standard, lexemes)
        cls.kwjp = kwjp_measures(rows, genres)
        cls.relevant = frozenset(cls.forms)
        cls.nkjp = read_nkjp(cls.fixture['nkjp'], 'full-nfc', cls.owners)
        # `kotek`: tylko NKJP (brak w KWJP), żeby był brak częściowy w obie strony.
        cls.nkjp_plus = dict(cls.nkjp, forms=dict(cls.nkjp['forms'], kotek=3), matched=cls.nkjp['matched'] + 3)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def units(self, d5, nkjp=None, relevant=None):
        return units(self.kwjp, d5, relevant or self.relevant, nkjp if nkjp is not None else self.nkjp,
                     self.owners)

    def test_rank_is_deterministic_minus_measure_then_unit_key(self):
        measured = {('b',): {'value': 5}, ('c',): {'value': 9}, ('a',): {'value': 5}, ('d',): {'value': None}}
        ranks = rank_units(measured)
        self.assertEqual(list(ranks.items()), [(('c',), 1), (('a',), 2), (('b',), 3)])
        self.assertEqual(rank_units(dict(reversed(list(measured.items())))), ranks)
        # D5d: dwie jednostki z F = 110; remis rozstrzyga klucz jednostki (krotka kluczy członków).
        result = self.units('d')
        found = measure(result, KWJP_ONLY)
        polska, rok = _unit('Polska', 'polski'), _unit('lato', 'rok:S1', 'rok:S2')
        self.assertEqual((found['units'][polska]['value'], found['units'][rok]['value']), (110, 110))
        self.assertEqual((rank_units(found['units'])[polska], rank_units(found['units'])[rok]), (1, 2))
        self.assertNotIn(0, rank_units(found['units']).values())

    def test_percentiles_on_small_example(self):
        self.assertEqual(percentiles({('a',): 1, ('b',): 2, ('c',): 3, ('d',): 4}),
                         {('a',): 100.0, ('b',): 75.0, ('c',): 50.0, ('d',): 25.0})
        self.assertEqual(percentiles({}), {})
        # NKJP leksemu tylko jako ranga i percentyl (C14), także w jednostkach.
        result = self.units('c')
        observed = {k: (v['nkjp']['rank'], v['nkjp']['percentile'])
                    for k, v in result['units'].items() if v['nkjp']['status'] == 'OBSERVED'}
        self.assertEqual(observed, {_unit('ul'): (1, 100.0), _unit('duży'): (2, 66.6667),
                                    _unit('fajny'): (3, 33.3333)})
        for value in result['units'].values():
            self.assertEqual(set(value['nkjp']), {'status', 'rank', 'percentile', 'ambiguous'})

    def test_missing_data_separate_statuses_never_zero_and_three_partial_rules(self):
        # `kotek` nie ma formy w STANDARD fikstury; dołączony jawnie jako leksem z formą.
        result = self.units('c', self.nkjp_plus, self.relevant | {(S, 'kotek')})
        kumpel, bac, kotek = result['units'][_unit('kumpel')], result['units'][_unit('bać')], \
            result['units'][_unit('kotek')]
        self.assertEqual((kumpel['kwjp']['status'], kumpel['nkjp']['status']),
                         ('ABSENT_OR_BELOW_PUBLICATION_THRESHOLD', 'NOT_IN_PUBLISHED_LIST'))
        self.assertIsNone(kumpel['kwjp']['F'])
        self.assertEqual((bac['kwjp']['status'], bac['nkjp']['status']), ('OBSERVED', 'NOT_IN_PUBLISHED_LIST'))
        self.assertEqual((kotek['kwjp']['status'], kotek['nkjp']['status'], kotek['confidence']),
                         ('ABSENT_OR_BELOW_PUBLICATION_THRESHOLD', 'OBSERVED', 'NKJP_ONLY'))
        # Grupa `rok` pod D5c: KWJP zna wiersz, ale nie daje F członkom.
        self.assertEqual(result['units'][_unit('rok:S2')]['kwjp']['status'], 'UNMATCHED')
        only = measure(result, KWJP_ONLY)
        self.assertEqual(only['units'][_unit('kotek')], {'value': None, 'status': 'NO_DATA', 'flags': ()})
        self.assertIsNone(only['missing']['partial'])
        both = {'source': 'kwjp+nkjp', 'field': 'F', 'weight': 0.5}
        rules = {rule: measure(result, both, rule) for rule in ('available-only', 'lower-bound', 'exclude')}
        kwjp_pct = percentiles(rank_units({k: {'value': v['kwjp']['F']} for k, v in result['units'].items()}))
        floor = round(100 / (3 + 1 + 1), 4)  # 4 leksemy z rangą NKJP; dolna granica = poniżej ostatniego
        self.assertEqual(rules['available-only']['units'][_unit('bać')],
                         {'value': kwjp_pct[_unit('bać')], 'status': 'MEASURED', 'flags': ('single_source:kwjp',)})
        self.assertEqual(rules['lower-bound']['units'][_unit('bać')],
                         {'value': round(0.5 * kwjp_pct[_unit('bać')] + 0.5 * floor, 6), 'status': 'MEASURED',
                          'flags': ('lower_bound:nkjp',)})
        self.assertEqual(rules['exclude']['units'][_unit('bać')],
                         {'value': None, 'status': 'EXCLUDED_PARTIAL', 'flags': ()})
        self.assertEqual(rules['exclude']['units'][_unit('kumpel')]['status'], 'NO_DATA')
        for rule, found in rules.items():
            self.assertNotIn(0, [v['value'] for v in found['units'].values()], rule)
            self.assertEqual(found['missing']['full'], rules['exclude']['missing']['full'])
            self.assertGreater(found['missing']['partial'], 0)
        statuses = rules['exclude']['missing']['statuses']
        self.assertEqual(statuses['ABSENT_OR_BELOW_PUBLICATION_THRESHOLD/NOT_IN_PUBLISHED_LIST'], 1)  # kumpel
        self.assertEqual(sum(statuses.values()), len(result['units']))
        with self.assertRaises(GeneratorError) as raised:
            measure(result, both, 'zero')
        self.assertEqual(raised.exception.code, 2)

    def test_d5_options_attribute_mass_and_homonym_group_is_one_unit(self):
        found = {d5: self.units(d5) for d5 in 'abcd'}
        mass = {d5: (r['mass']['kwjp']['attributed'], r['mass']['nkjp']['attributed'], r['mass']['nkjp']['copied'])
                for d5, r in found.items()}
        # NKJP dopasowane 119: wspólne polska 55, lata 25, rok 20; jednoznaczne ul 10, duży 8, fajny 1.
        self.assertEqual(mass, {'a': (265, 19, 0), 'b': (385, 119, 100), 'c': (265, 19, 0), 'd': (385, 119, 0)})
        self.assertEqual(found['d']['mass']['nkjp']['unattributed'], 0)
        self.assertEqual(found['c']['mass']['nkjp']['unattributed'], 100)
        self.assertEqual(found['d']['mass']['kwjp']['unattributed'], 8)  # kwiat: UNMATCHED w KWJP
        # a: leksem z dowolną formą wspólną nie dostaje F; c: zostaje F form jednoznacznych.
        self.assertEqual(found['a']['units'][_unit('polski')]['nkjp']['status'], 'UNMATCHED')
        # `polski` (jednoznaczna) po `polska` (wspólna) w kolejności kluczy: c ją liczy, a nie.
        extra = dict(self.nkjp, forms=dict(self.nkjp['forms'], polski=7), matched=self.nkjp['matched'] + 7)
        self.assertEqual(self.units('c', extra)['units'][_unit('polski')]['nkjp']['status'], 'OBSERVED')
        self.assertEqual(self.units('a', extra)['units'][_unit('polski')]['nkjp']['status'], 'UNMATCHED')
        self.assertEqual(found['b']['units'][_unit('rok:S1')]['kwjp'],
                         {**found['b']['units'][_unit('rok:S1')]['kwjp'], 'F': 90, 'ambiguous': True})
        d = found['d']['units']
        rok, zamek = _unit('lato', 'rok:S1', 'rok:S2'), _unit('zamek:a', 'zamek:b')
        self.assertEqual((d[rok]['kwjp']['F'], d[rok]['kwjp']['status'], d[rok]['confidence']),
                         (110, 'OBSERVED', 'AMBIGUOUS'))
        self.assertEqual(d[zamek]['kwjp']['F'], 30)
        self.assertEqual(d[rok]['size'], 3)
        members = [m for key in d for m in d[key]['members']]
        self.assertEqual(len(members), len(set(members)))  # każdy leksem w jednej jednostce
        self.assertTrue(self.relevant <= set(members))
        ranks = rank_units(measure(found['d'], KWJP_ONLY)['units'])
        by_member = member_ranks(ranks, found['d'])
        self.assertEqual({by_member[k] for k in rok}, {ranks[rok]})
        # Próg 4 leksemów: Polska+polski (2) wchodzi, grupa rok (3) nie mieści się — w całości albo wcale.
        cut = threshold(ranks, found['d'], {'by': 'count', 'value': 4})
        self.assertEqual((cut['units'], cut['lexemes'], cut['rank']), ((_unit('Polska', 'polski'),), 2, 1))
        self.assertTrue(set(rok).isdisjoint(cut['members']))
        cut = threshold(ranks, found['d'], {'by': 'count', 'value': 5})
        self.assertTrue(set(rok) <= cut['members'])

    def test_d5e_groups_only_owner_sets_of_eligible_lexemes(self):
        polska, rok = _unit('Polska', 'polski'), _unit('lato', 'rok:S1', 'rok:S2')
        # Dosłownie (eligible = relevant): `Polska` ma formę `polska` w STANDARD, więc łączy się z `polski`.
        literal = self.units('e')['units']
        self.assertIn(polska, literal)
        self.assertEqual(literal[rok]['kwjp']['F'], 110)
        # Bez nazw własnych: `polska` nieprzypisana, `polski` bez NKJP (PROPER_SHARED); rok/lato jedną grupą.
        common = self.relevant - {(S, 'Polska')}
        found = units(self.kwjp, 'e', self.relevant, self.nkjp, self.owners, eligible=common)
        self.assertNotIn(polska, found['units'])
        self.assertEqual(found['units'][_unit('polski')]['nkjp']['status'], 'PROPER_SHARED')
        self.assertEqual(found['units'][_unit('Polska')]['nkjp']['status'], 'UNMATCHED')
        self.assertEqual(found['units'][_unit('Polska')]['kwjp']['F'], 60)
        self.assertEqual(found['units'][rok]['kwjp']['F'], 110)
        self.assertEqual(found['units'][rok]['nkjp']['status'], 'OBSERVED')
        self.assertEqual((found['mass']['nkjp']['attributed'], found['mass']['nkjp']['unattributed']), (64, 55))
        self.assertEqual(found['groups'], {'count': 2, 'largest': 3})  # rok/lato i zamek
        # Łańcuch przez nazwę własną: forma wspólna `Polska`+`duży` łączy w D5d, w D5e nie.
        owners = dict(self.owners, xy=((S, 'Polska'), (S, 'duży')))
        nkjp = dict(self.nkjp, forms=dict(self.nkjp['forms'], xy=5), matched=self.nkjp['matched'] + 5)
        chained = units(self.kwjp, 'd', self.relevant, nkjp, owners)['units']
        self.assertIn(_unit('Polska', 'duży', 'polski'), chained)
        split = units(self.kwjp, 'e', self.relevant, nkjp, owners, eligible=common)['units']
        self.assertTrue({_unit('Polska'), _unit('polski'), _unit('duży')} <= set(split))
        with self.assertRaises(ValueError):
            units(self.kwjp, 'd', self.relevant, self.nkjp, self.owners, eligible=common)

    def test_coverage_in_three_denominators(self):
        everyone = {m for u in self.units('d')['units'].values() for m in u['members']}
        full = {d1: coverage(everyone, self.kwjp, d1, self.relevant) for d1 in ('kwjp-all', 'kwjp-exact',
                                                                                  'kwjp-standard')}
        self.assertEqual({k: (v['covered'], v['total']) for k, v in full.items()},
                         {'kwjp-all': (385, 393), 'kwjp-exact': (265, 265), 'kwjp-standard': (385, 385)})
        self.assertEqual(full['kwjp-standard']['coverage'], 1.0)
        part = {d1: coverage({(S, 'bać'), (S, 'duży'), (S, 'rok:S1')}, self.kwjp, d1, self.relevant)
                for d1 in ('kwjp-all', 'kwjp-exact', 'kwjp-standard')}
        # Grupa rok bez rok:S2 nie jest pokryta.
        self.assertEqual({k: v['covered'] for k, v in part.items()},
                         {'kwjp-all': 110, 'kwjp-exact': 110, 'kwjp-standard': 110})
        self.assertEqual(part['kwjp-all']['coverage'], round(110 / 393, 6))
        with self.assertRaises(GeneratorError):
            coverage(everyone, self.kwjp, 'nkjp-all', self.relevant)

    def test_threshold_by_unit_count_and_by_coverage_target(self):
        result = self.units('c')
        ranks = rank_units(measure(result, KWJP_ONLY)['units'])
        self.assertEqual(list(ranks)[:4], [_unit('bać'), _unit('Polska'), _unit('polski'), _unit('duży')])
        cut = threshold(ranks, result, {'by': 'count', 'value': 3})
        self.assertEqual((cut['units'], cut['lexemes'], cut['rank'], cut['reached']),
                         ((_unit('bać'), _unit('Polska'), _unit('polski')), 3, 3, True))
        target = {'by': 'coverage', 'value': 0.5, 'denominator': 'kwjp-exact'}
        cut = threshold(ranks, result, target, self.kwjp, self.relevant)
        # 70/265 < 0,5; 130/265 < 0,5; 180/265 ≥ 0,5.
        self.assertEqual((cut['rank'], cut['coverage']['covered'], cut['reached']), (3, 180, True))
        cut = threshold(ranks, result, {'by': 'coverage', 'value': 1.0, 'denominator': 'kwjp-all'},
                        self.kwjp, self.relevant)
        self.assertFalse(cut['reached'])
        self.assertEqual(len(cut['units']), len(ranks))
        for bad in ({'by': 'count', 'value': 0}, {'by': 'count', 'value': True},
                    {'by': 'coverage', 'value': 1.5, 'denominator': 'kwjp-all'}, {'by': 'rank', 'value': 3}):
            with self.assertRaises(GeneratorError) as raised:
                threshold(ranks, result, bad, self.kwjp, self.relevant)
            self.assertEqual(raised.exception.code, 2, bad)

    def test_forms_by_tag_classes_constructions_and_membership_rule(self):
        self.assertEqual(tag_classes('subst:sg:voc:m1'), frozenset({'voc'}))
        self.assertEqual(tag_classes('subst:sg:nom.voc:m1'), frozenset())
        self.assertEqual(tag_classes('impt:sg:sec:imperf'), frozenset({'impt', 'person-1-2'}))
        self.assertEqual(tag_classes('pact:sg:nom:m1:imperf:aff'), frozenset({'participle'}))
        self.assertEqual(tag_classes('fin:sg:pri:imperf'), frozenset({'person-1-2'}))
        self.assertEqual(tag_classes('fin:sg:ter:imperf'), frozenset())
        self.assertEqual(self.classes[(S, 'bać')], {'bojąc': frozenset({frozenset({'participle'})})})
        rules = {'i': self.forms, 'ii': self.accepted}
        full = {'classes': (), 'constructions': 'no', 'membership': 'i'}
        bac = _unit('bać')
        self.assertEqual(forms_for(bac, full, rules, self.constructions, self.classes)['forms'],
                         frozenset({'boi', 'bał', 'bojąc'}))
        cut = forms_for(bac, dict(full, classes=('participle', 'voc')), rules, self.constructions, self.classes)
        self.assertEqual((cut['forms'], cut['removed']), (frozenset({'boi', 'bał'}), {'participle': 1}))
        polski = _unit('Polska', 'polski')
        self.assertEqual(forms_for(polski, full, rules)['forms'], frozenset({'polska', 'polski'}))
        built = forms_for(polski, dict(full, constructions='yes'), rules, self.constructions, self.classes)
        self.assertEqual(built['forms'], frozenset({'polska', 'polski', 'niepolska', 'niepolski'}))
        self.assertEqual(built['constructions'], 2)
        # Forma z jedną analizą spoza klas zostaje (wołacz = mianownik).
        mixed = {(S, 'x'): {'kocie': frozenset({frozenset({'voc'})})}}
        both = {'i': {(S, 'x'): frozenset({'kocie', 'kot'})}}
        self.assertEqual(forms_for(_unit('x'), dict(full, classes=('voc',)), both, None, mixed)['forms'],
                         frozenset({'kot'}))
        for bad in (dict(full, classes=('dual',)), dict(full, constructions='maybe'),
                    dict(full, membership='iii')):
            with self.assertRaises(GeneratorError) as raised:
                forms_for(bac, bad, rules, self.constructions, self.classes)
            self.assertEqual(raised.exception.code, 2, bad)

    def test_spearman_top_overlap_and_weighted_combination_from_ranks_only(self):
        a = {('a',): 1, ('b',): 2, ('c',): 3, ('d',): 4}
        self.assertEqual(spearman(a, a), {'n': 4, 'rho': 1.0})
        self.assertEqual(spearman(a, {k: 5 - r for k, r in a.items()}), {'n': 4, 'rho': -1.0})
        self.assertEqual(spearman(a, {('a',): 1, ('z',): 2}), {'n': 1, 'rho': None})
        self.assertEqual(top_overlap(a, {('b',): 1, ('a',): 2, ('z',): 3, ('c',): 4}, 2),
                         {'n': 2, 'overlap': 2, 'share': 1.0})
        self.assertEqual(top_overlap(a, {('z',): 1, ('a',): 2}, 2)['overlap'], 1)
        result = self.units('d')
        kwjp_pct = percentiles(rank_units(measure(result, KWJP_ONLY)['units']))
        nkjp_pct = {k: v['nkjp']['percentile'] for k, v in result['units'].items() if v['nkjp']['rank']}
        both = sorted(set(kwjp_pct) & set(nkjp_pct))
        self.assertTrue(both)
        for weight in (1.0, 0.25, 0.0):
            found = measure(result, {'source': 'kwjp+nkjp', 'field': 'F', 'weight': weight}, 'exclude')
            for key in both:
                self.assertEqual(found['units'][key]['value'],
                                 round(weight * kwjp_pct[key] + (1 - weight) * nkjp_pct[key], 6))
                self.assertTrue(0 < found['units'][key]['value'] <= 100)
        # Pole miary KWJP: ARF i liczba gatunków z obecnością.
        arf = measure(result, {'source': 'kwjp', 'field': 'ARF'})['units']
        self.assertEqual(arf[_unit('bać')]['value'], 3.0)
        genres = measure(result, {'source': 'kwjp', 'field': 'genres'})['units']
        self.assertEqual(genres[_unit('bać')]['value'], 2)
        for bad in ({'source': 'kwjp+nkjp', 'field': 'F', 'weight': 1.5}, {'source': 'kwjp', 'field': 'ipm'},
                    {'source': 'nkjp', 'field': 'F'}, {'source': 'kwjp+nkjp', 'field': 'F'}):
            with self.assertRaises(GeneratorError) as raised:
                measure(result, bad)
            self.assertEqual(raised.exception.code, 2, bad)

    # --- Poprawki metody po przeglądzie próbek (grupa 16, poprawki ADR-007) ---

    def test_nkjp_form_shared_with_proper_name_makes_unit_kwjp_only(self):
        # `polska` ma właścicieli Polska (nazwa własna) i polski; `polski` ma też własną formę `polski`.
        # Masa `polska` zostaje nieprzypisana, więc ranga NKJP z samego `polski` zaniżałaby słowo.
        common = self.relevant - {(S, 'Polska')}
        extra = dict(self.nkjp, forms=dict(self.nkjp['forms'], polski=7), matched=self.nkjp['matched'] + 7)
        found = units(self.kwjp, 'e', self.relevant, extra, self.owners, eligible=common)
        polski = found['units'][_unit('polski')]
        self.assertEqual(polski['nkjp'], {'status': 'PROPER_SHARED', 'rank': None, 'percentile': None,
                                          'ambiguous': False})
        self.assertEqual(polski['confidence'], 'EXACT')
        # Inne jednostki zostają w NKJP; `polski` nie zajmuje rangi NKJP.
        ranked = {k: v['nkjp']['rank'] for k, v in found['units'].items() if v['nkjp']['status'] == 'OBSERVED'}
        self.assertIn(_unit('duży'), ranked)
        self.assertEqual(sorted(ranked.values()), list(range(1, len(ranked) + 1)))
        # Masa: własne formy jednostki PROPER_SHARED nie są przypisane; osobny licznik.
        self.assertEqual(found['mass']['nkjp']['attributed'], 64)
        self.assertEqual(found['mass']['nkjp']['proper_shared'], {'units': 1, 'mass': 7})
        self.assertEqual(found['mass']['nkjp']['unattributed'], extra['matched'] - 64)
        for d3 in ({'source': 'kwjp+nkjp', 'field': 'F', 'weight': 0.5},
                   {'source': 'kwjp+nkjp', 'field': 'log-ipm', 'weight': 0.5}):
            item = measure(found, d3)['units'][_unit('polski')]
            self.assertEqual((item['status'], item['flags']), ('MEASURED', ('single_source:kwjp',)), d3)
        # Bez `eligible` (D5e dosłownie) i w D5c reguła nie działa: tylko e-common ma nieprzypisaną masę.
        self.assertEqual(units(self.kwjp, 'c', self.relevant, extra, self.owners)['units'][_unit('polski')]
                         ['nkjp']['status'], 'OBSERVED')
        self.assertNotIn('proper_shared', units(self.kwjp, 'c', self.relevant, extra, self.owners)['mass']['nkjp'])

    def test_log_ipm_combines_sources_by_their_own_totals(self):
        import math
        common = self.relevant - {(S, 'Polska')}
        result = units(self.kwjp, 'e', self.relevant, self.nkjp, self.owners, eligible=common)
        kwjp_total, nkjp_total = self.kwjp['mass']['total'], self.nkjp['total']
        self.assertEqual((kwjp_total, nkjp_total), (393, 199))
        ipm = lambda f, total: math.log10(f / total * 1e6)
        found = measure(result, {'source': 'kwjp+nkjp', 'field': 'log-ipm', 'weight': 0.5})['units']
        # duży: KWJP 40 z 393, NKJP 8 z 199 — średnia log-ipm, nie percentyli.
        self.assertAlmostEqual(found[_unit('duży')]['value'],
                               0.5 * ipm(40, kwjp_total) + 0.5 * ipm(8, nkjp_total), places=9)
        self.assertEqual(found[_unit('duży')]['flags'], ())
        # rok+lato: KWJP 110, NKJP lata 25 + rok 20.
        rok = _unit('lato', 'rok:S1', 'rok:S2')
        self.assertAlmostEqual(found[rok]['value'], 0.5 * ipm(110, kwjp_total) + 0.5 * ipm(45, nkjp_total), places=9)
        # Jedno źródło (D8 available-only): sama wartość tego źródła z flagą.
        self.assertAlmostEqual(found[_unit('bać')]['value'], ipm(70, kwjp_total), places=9)
        self.assertEqual(found[_unit('bać')]['flags'], ('single_source:kwjp',))
        self.assertEqual(found[_unit('kumpel')], {'value': None, 'status': 'NO_DATA', 'flags': ()})
        # Inna suma NKJP zmienia wartość: suma źródła wchodzi do miary.
        bigger = dict(self.nkjp, total=self.nkjp['total'] * 10)
        again = units(self.kwjp, 'e', self.relevant, bigger, self.owners, eligible=common)
        moved = measure(again, {'source': 'kwjp+nkjp', 'field': 'log-ipm', 'weight': 0.5})['units']
        self.assertAlmostEqual(found[_unit('duży')]['value'] - moved[_unit('duży')]['value'], 0.5, places=9)
        # Słowo z rozbieżnymi korpusami: średnia percentyli ciągnie w dół, log-ipm nie (przekopiować, dopóty).
        pct = measure(result, {'source': 'kwjp+nkjp', 'field': 'F', 'weight': 0.5})['units']
        self.assertNotEqual(rank_units(found), rank_units(pct))
        # Pozostałe reguły D8 i sama KWJP.
        lower = measure(result, {'source': 'kwjp+nkjp', 'field': 'log-ipm', 'weight': 0.5}, 'lower-bound')['units']
        self.assertEqual(lower[_unit('bać')]['flags'], ('lower_bound:nkjp',))
        self.assertLess(lower[_unit('bać')]['value'], ipm(70, kwjp_total))
        excluded = measure(result, {'source': 'kwjp+nkjp', 'field': 'log-ipm', 'weight': 0.5}, 'exclude')['units']
        self.assertEqual(excluded[_unit('bać')]['status'], 'EXCLUDED_PARTIAL')
        only = measure(result, {'source': 'kwjp', 'field': 'log-ipm'})['units']
        self.assertAlmostEqual(only[_unit('bać')]['value'], ipm(70, kwjp_total), places=9)
        self.assertEqual(rank_units(only), rank_units(measure(result, KWJP_ONLY)['units']))
        # NKJP jednostki tylko jako status, ranga, percentyl (C14), także przy log-ipm.
        for value in result['units'].values():
            self.assertEqual(set(value['nkjp']), {'status', 'rank', 'percentile', 'ambiguous'})

    def test_lower_bound_absent_puts_nkjp_only_word_under_word_from_both_sources(self):
        import math
        # `kotek`: tylko NKJP, F 40 (jak F KWJP `duży`); brak w KWJP = poniżej progu publikacji.
        nkjp = dict(self.nkjp, forms=dict(self.nkjp['forms'], kotek=40), matched=self.nkjp['matched'] + 40)
        relevant = self.relevant | {(S, 'kotek')}
        result = units(self.kwjp, 'e', relevant, nkjp, self.owners, eligible=relevant - {(S, 'Polska')})
        d3 = {'source': 'kwjp+nkjp', 'field': 'log-ipm', 'weight': 0.5}
        only = measure(result, d3, 'available-only')['units']
        bound = measure(result, d3, 'lower-bound-absent')['units']
        kotek, duzy = _unit('kotek'), _unit('duży')
        self.assertGreater(only[kotek]['value'], only[duzy]['value'])
        self.assertLess(bound[kotek]['value'], bound[duzy]['value'])
        self.assertEqual(bound[kotek]['flags'], ('bound:kwjp',))
        self.assertEqual(bound[duzy], only[duzy])
        # Brakujące źródło dostaje najmniejszy zaobserwowany log-ipm tego źródła (KWJP: ul, F 6).
        ipm = lambda f, total: math.log10(f / total * 1e6)
        self.assertAlmostEqual(bound[kotek]['value'], 0.5 * ipm(6, 393) + 0.5 * ipm(40, 199), places=9)
        self.assertEqual(bound[_unit('kumpel')], {'value': None, 'status': 'NO_DATA', 'flags': ()})

    def test_lower_bound_absent_keeps_unreliable_source_out(self):
        # PROPER_SHARED (jak kot przez Kot) nie jest brakiem: miara z samej KWJP, bez kary.
        extra = dict(self.nkjp, forms=dict(self.nkjp['forms'], polski=7), matched=self.nkjp['matched'] + 7)
        result = units(self.kwjp, 'e', self.relevant, extra, self.owners, eligible=self.relevant - {(S, 'Polska')})
        d3 = {'source': 'kwjp+nkjp', 'field': 'log-ipm', 'weight': 0.5}
        bound = measure(result, d3, 'lower-bound-absent')['units']
        only = measure(result, d3, 'available-only')['units']
        self.assertEqual(result['units'][_unit('polski')]['nkjp']['status'], 'PROPER_SHARED')
        self.assertEqual(bound[_unit('polski')], only[_unit('polski')])
        self.assertEqual(bound[_unit('polski')]['flags'], ('single_source:kwjp',))
        # Prawdziwy brak w NKJP (bać: NOT_IN_PUBLISHED_LIST) obniża miarę i ma flagę `bound:nkjp`.
        self.assertEqual(result['units'][_unit('bać')]['nkjp']['status'], 'NOT_IN_PUBLISHED_LIST')
        self.assertEqual(bound[_unit('bać')]['flags'], ('bound:nkjp',))
        self.assertLess(bound[_unit('bać')]['value'], only[_unit('bać')]['value'])

    def test_threshold_never_splits_a_block_of_equal_measure(self):
        result = {'units': {(k,): {'size': 1, 'members': ((S, k),)} for k in 'abcde'}}
        measured = {('a',): {'value': 5.0}, ('b',): {'value': 3.0}, ('c',): {'value': 3.0},
                    ('d',): {'value': 3.0}, ('e',): {'value': 1.0}}
        ranks = rank_units(measured)
        # Próg 2 i 3: blok b, c, d (3 leksemy) nie mieści się, więc lista kończy się przed nim.
        for limit in (2, 3):
            cut = threshold(ranks, result, {'by': 'count', 'value': limit}, values=measured)
            self.assertEqual((cut['units'], cut['lexemes'], cut['rank'], cut['reached']),
                             ((('a',),), 1, 1, True), limit)
        cut = threshold(ranks, result, {'by': 'count', 'value': 4}, values=measured)
        self.assertEqual((cut['units'], cut['lexemes'], cut['reached']), ((('a',), ('b',), ('c',), ('d',)), 4, True))
        cut = threshold(ranks, result, {'by': 'count', 'value': 10}, values=measured)
        self.assertEqual((len(cut['units']), cut['reached']), (5, False))
        # Bez wartości: stare zachowanie (jednostka po jednostce, remis wg klucza).
        cut = threshold(ranks, result, {'by': 'count', 'value': 2})
        self.assertEqual(cut['units'], (('a',), ('b',)))


def _kwjp_row(freq, row):
    return {'F': freq, 'ARF': float(freq), '1-DP': 0.5, 'row': row, 'row_F': freq, 'rows': 1, 'genres': (),
            'status': 'EXACT_CANDIDATE'}


class PopPruneTests(unittest.TestCase):
    """D5 `prune-weak-members` (iteracja 3): członek grupy zostaje na liście tylko z własną rangą w progu.

    Dane syntetyczne, wzór `kią`: grupa {ki, kia, kto} przez formy wspólne `kim` i `kie`. Rangi jednostek
    (log-ipm 0,5/0,5): grupa 1, dom 2, zamek 3, pies 4, rzadki 5. Progi: POP0 = 4 leksemy (grupa + dom),
    POP = 7 (do psa). Własne miary: kto nad domem; kia (tylko NKJP `kią`, KWJP dolna granica) pod domem,
    nad psem (ranga 4 = próg POP); ki (KWJP 50, NKJP `ki` 300) pod psem. Zamek: żaden członek nie ma własnego dowodu.
    """
    D3 = {'source': 'kwjp+nkjp', 'field': 'log-ipm', 'weight': 0.5}

    def setUp(self):
        k = lambda name: (S, name)
        self.k = k
        self.kwjp = {'lexemes': {k('kto'): _kwjp_row(1000, 1), k('ki'): _kwjp_row(50, 2), k('dom'): _kwjp_row(500, 3),
                                 k('pies'): _kwjp_row(100, 4), k('rzadki'): _kwjp_row(6, 5)},
                     'groups': {(k('zamek:a'), k('zamek:b')): dict(_kwjp_row(300, 6), status='AMBIGUOUS')},
                     'mass': {'total': 2000}}
        self.owners = {'kto': (k('kto'),), 'kim': (k('kia'), k('kto')), 'kie': (k('ki'), k('kia')),
                       'kią': (k('kia'),), 'ki': (k('ki'),), 'zamek': (k('zamek:a'), k('zamek:b')),
                       'dom': (k('dom'),), 'pies': (k('pies'),), 'rzadki': (k('rzadki'),),
                       'kiach': (k('Kia'), k('kia'))}
        forms = {'kto': 9000, 'kim': 3000, 'kie': 5, 'kią': 20000, 'ki': 300, 'zamek': 2000, 'dom': 5000,
                 'pies': 800, 'rzadki': 10}
        self.nkjp = {'forms': forms, 'total': 100000, 'matched': sum(forms.values())}
        self.relevant = frozenset(k(n) for n in ('kto', 'kia', 'ki', 'dom', 'pies', 'rzadki', 'zamek:a',
                                                 'zamek:b', 'Kia'))
        self.eligible = self.relevant - {k('Kia')}

    def run_lists(self, nkjp=None):
        nkjp = nkjp or self.nkjp
        result = units(self.kwjp, 'e', self.relevant, nkjp, self.owners, eligible=self.eligible)
        result['units'] = {key: u for key, u in result['units'].items() if key != (self.k('Kia'),)}
        found = measure(result, self.D3, 'lower-bound-absent')['units']
        ranks = rank_units(found)
        cuts = {name: threshold(ranks, result, {'by': 'count', 'value': limit}, values=found)
                for name, limit in (('pop0', 4), ('pop', 7))}
        members = member_units(result, self.kwjp, self.eligible, nkjp, self.owners)
        measured = measure(members, self.D3, 'lower-bound-absent', floors=measure_floors(result, self.D3))['units']
        return result, found, ranks, cuts, members, measured, prune_members(members, measured, found, cuts)

    def test_rare_member_pulled_in_by_shared_form_leaves_pop0_but_stays_in_pop_by_own_rank(self):
        k = self.k
        result, found, ranks, cuts, members, measured, pruned = self.run_lists()
        group = (k('ki'), k('kia'), k('kto'))
        self.assertEqual(ranks[group], 1)
        self.assertEqual(set(cuts['pop0']['units']), {group, (k('dom'),)})
        self.assertEqual(cuts['pop']['rank'], 4)
        kept = {name: pruned['lists'][name]['kept'] for name in ('pop0', 'pop')}
        self.assertEqual(kept['pop0'], {k('kto'), k('dom')})
        self.assertEqual(kept['pop'], {k('kto'), k('kia'), k('dom'), k('pies'), k('zamek:a'), k('zamek:b')})
        self.assertEqual(pruned['lists']['pop0']['pruned'], (k('ki'), k('kia')))
        self.assertEqual(pruned['lists']['pop']['pruned'], (k('ki'),))
        own = pruned['members']
        self.assertEqual((own[(k('kto'),)]['rank'], own[(k('kia'),)]['rank'], own[(k('ki'),)]['rank']), (2, 4, 5))
        # kia: KWJP nieobecne = dolna granica (D8), NKJP z własnej formy `kią`; formy wspólne poza miarą.
        self.assertEqual(measured[(k('kia'),)]['flags'], ('bound:kwjp',))
        self.assertEqual(members['units'][(k('kia'),)]['nkjp']['status'], 'OBSERVED')
        self.assertEqual(members['nkjp_f'][(k('kia'),)], 20000)
        # POP0 ⊆ POP także po przycięciu.
        self.assertTrue(kept['pop0'] <= kept['pop'])

    def test_group_without_own_evidence_stays_whole_and_f_is_never_copied(self):
        k = self.k
        result, found, ranks, cuts, members, measured, pruned = self.run_lists()
        zamek = (k('zamek:a'), k('zamek:b'))
        # Żaden członek nie ma własnego dowodu: podjednostka = cała grupa, ta sama miara co jednostka.
        self.assertIn(zamek, members['units'])
        self.assertEqual(measured[zamek]['value'], found[zamek]['value'])
        self.assertTrue(set(zamek) <= pruned['lists']['pop']['kept'])
        # F grupy KWJP raz; członkowie z własnym wierszem dostają tylko swój wiersz (kto 1000, ki 50).
        self.assertEqual(members['units'][zamek]['kwjp']['F'], 300)
        self.assertEqual(members['units'][(k('kto'),)]['kwjp']['F'], 1000)
        self.assertEqual(members['units'][(k('ki'),)]['kwjp']['F'], 50)
        self.assertEqual(members['units'][(k('kia'),)]['kwjp']['status'], 'ABSENT_OR_BELOW_PUBLICATION_THRESHOLD')
        group = (k('ki'), k('kia'), k('kto'))
        sub_f = sum(u['kwjp']['F'] or 0 for key, u in members['units'].items() if u['unit'] == group)
        self.assertEqual(sub_f, result['units'][group]['kwjp']['F'])
        # NKJP: tylko formy jednego właściciela; `kim` i `kie` (wspólne) nie trafiają do nikogo.
        self.assertEqual(sum(v for key, v in members['nkjp_f'].items() if members['units'][key]['unit'] == group),
                         9000 + 20000 + 300)
        # Jednostki jednoczłonowe nie mają podjednostek; rangi jednostek bez zmian.
        self.assertNotIn((k('dom'),), members['units'])
        self.assertEqual(ranks, rank_units(measure(result, self.D3, 'lower-bound-absent')['units']))

    def test_strongest_member_stays_when_no_member_reaches_the_threshold_alone(self):
        # Wzór `jedyny:A`/`jedyny:S`: masa grupy jest w formach wspólnych, więc żaden członek sam nie
        # dochodzi do progu POP0. Jednostka nie może wejść na listę pusta: zostaje najmocniejszy członek.
        k = self.k
        self.kwjp['lexemes'][k('kto')] = _kwjp_row(10, 1)
        nkjp = dict(self.nkjp, forms=dict(self.nkjp['forms'], kto=50))
        result, found, ranks, cuts, members, measured, pruned = self.run_lists(nkjp)
        group = (k('ki'), k('kia'), k('kto'))
        self.assertEqual(set(cuts['pop0']['units']), {group, (k('dom'),)})
        self.assertEqual(cuts['pop0']['rank'], 2)
        own = {m: pruned['members'][(m,)]['rank'] for m in group}
        self.assertTrue(all(rank > 2 for rank in own.values()), own)
        self.assertEqual(min(own, key=own.get), k('kia'))
        self.assertEqual(pruned['lists']['pop0']['kept'], {k('kia'), k('dom')})
        self.assertEqual(pruned['lists']['pop0']['pruned'], (k('ki'), k('kto')))
        self.assertEqual(pruned['lists']['pop0']['heads'], 1)

    def test_nkjp_form_shared_with_proper_name_gives_member_no_nkjp(self):
        k = self.k
        nkjp = dict(self.nkjp, forms=dict(self.nkjp['forms'], kiach=7), matched=self.nkjp['matched'] + 7)
        result, found, ranks, cuts, members, measured, pruned = self.run_lists(nkjp)
        kia = members['units'][(k('kia'),)]
        self.assertEqual(kia['nkjp']['status'], 'PROPER_SHARED')
        self.assertNotIn((k('kia'),), members['nkjp_f'])
        # Bez KWJP i bez wiarygodnego NKJP: brak własnej miary, więc poza obiema listami.
        self.assertEqual(measured[(k('kia'),)]['status'], 'NO_DATA')
        self.assertIsNone(pruned['members'][(k('kia'),)]['rank'])
        self.assertNotIn(k('kia'), pruned['lists']['pop']['kept'])


class PopConfigTests(unittest.TestCase):
    """`pop.json` i `load_config` (B3, C3, ADR-007): zamknięte klucze, opcje, typy i zakresy."""
    ROOT = Path(__file__).resolve().parent.parent

    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.directory = Path(self.work.name)
        self.base = load_json(self.ROOT / 'config/generator/pop-v2.json')

    def tearDown(self):
        self.work.cleanup()

    def write(self, config):
        path = self.directory / 'pop.json'
        path.write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
        return path

    def variant(self, change):
        config = json.loads(json.dumps(self.base))
        change(config)
        return config

    def assert_code_2(self, config, label):
        with self.assertRaises(GeneratorError, msg=label) as raised:
            load_config(self.write(config))
        self.assertEqual(raised.exception.code, 2, label)

    def test_historical_config_is_valid_and_encodes_adr_007(self):
        config = load_config(self.ROOT / 'config/generator/pop-v2.json')
        self.assertEqual(config['version'], 'pop-v2')
        self.assertEqual(config['adr'], 'docs/adr/ADR-007-metoda-pop-v1.md')
        self.assertTrue((self.ROOT / config['adr']).is_file())
        self.assertEqual(config['d1'], 'kwjp-standard')
        self.assertEqual(config['d2'], {'classes': [], 'constructions': 'yes', 'membership': 'i'})
        self.assertEqual(config['d3'], {'source': 'kwjp+nkjp', 'field': 'log-ipm', 'weight': 0.5})
        self.assertEqual(config['d4'], 'strip-edges-keep-dot')
        self.assertEqual(config['d5'], {'groups': 'e-common', 'members': 'prune-weak-members-v2'})
        self.assertEqual(config['d6'], {'pop': {'by': 'count', 'value': 60000},
                                        'pop0': {'by': 'count', 'value': 20000}})
        self.assertEqual((config['d7'], config['d8']), ('accepted', 'lower-bound-kwjp-absent'))
        self.assertIs(config['proper_names_in_ranking'], False)
        self.assertEqual(config['must_include_pop0'], ['kot'])
        self.assertEqual(config['sampling']['version'], 'pop-quality-v1')
        self.assertEqual(config['config_sha256'], sha256(self.ROOT / 'config/generator/pop-v2.json'))
        # ADR-007 wskazuje pop.json.
        adr = (self.ROOT / config['adr']).read_text(encoding='utf-8')
        self.assertIn('config/generator/pop-v2.json', adr)
        # Zapis kanoniczny: indent=2, ensure_ascii=False, newline.
        text = (self.ROOT / 'config/generator/pop-v2.json').read_text(encoding='utf-8')
        self.assertEqual(text, json.dumps(self.base, indent=2, ensure_ascii=False) + '\n')

    def test_unknown_or_missing_key_is_code_2(self):
        cases = {
            'nowy klucz': lambda c: c.update(extra=1),
            'brak d7': lambda c: c.pop('d7'),
            'klucz w d2': lambda c: c['d2'].update(extra=1),
            'klucz w d3': lambda c: c['d3'].update(extra=1),
            'klucz w d5': lambda c: c['d5'].update(extra=1),
            'brak d5 members': lambda c: c['d5'].pop('members'),
            'waga przy samej KWJP': lambda c: c['d3'].update(source='kwjp'),
            'klucz w d6': lambda c: c['d6'].update(pop1={'by': 'count', 'value': 1}),
            'klucz w d6.pop': lambda c: c['d6']['pop'].update(denominator='kwjp-all'),
            'klucz w sampling': lambda c: c['sampling'].update(extra=1),
        }
        for label, change in cases.items():
            self.assert_code_2(self.variant(change), label)
        path = self.directory / 'dup.json'
        path.write_text('{"version": "pop-v1", "version": "pop-v1"}', encoding='utf-8')
        with self.assertRaises(GeneratorError) as raised:
            load_config(path)
        self.assertEqual(raised.exception.code, 2)

    def test_option_outside_closed_list_is_code_2(self):
        cases = {
            'version': lambda c: c.update(version='pop-v3'),
            'adr': lambda c: c.update(adr='docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md'),
            'd1': lambda c: c.update(d1='kwjp-everything'),
            'd2 klasa': lambda c: c['d2'].update(classes=['noun']),
            'd2 powtórzona klasa': lambda c: c['d2'].update(classes=['voc', 'voc']),
            'd2 konstrukcje': lambda c: c['d2'].update(constructions=True),
            'd2 reguła': lambda c: c['d2'].update(membership='iii'),
            'd3 źródło': lambda c: c['d3'].update(source='nkjp'),
            'd3 pole': lambda c: c['d3'].update(field='f'),
            'd4': lambda c: c.update(d4='strip-all'),
            'd4 brak przy NKJP': lambda c: c.update(d4=None),
            'd5': lambda c: c.update(d5='f'),
            'd5 groups': lambda c: c['d5'].update(groups='f'),
            'd5 members': lambda c: c['d5'].update(members='prune'),
            'd5 jako tekst': lambda c: c.update(d5='e-common'),
            'd6 by': lambda c: c['d6']['pop'].update(by='lexemes'),
            'd7': lambda c: c.update(d7='corrected'),
            'd8': lambda c: c.update(d8='zero'),
            'd9 nie bool': lambda c: c.update(proper_names_in_ranking=0),
        }
        for label, change in cases.items():
            self.assert_code_2(self.variant(change), label)

    def test_number_of_wrong_type_or_out_of_range_is_code_2(self):
        cases = {
            'POP bool': lambda c: c['d6']['pop'].update(value=True),
            'POP float': lambda c: c['d6']['pop'].update(value=60000.0),
            'POP tekst': lambda c: c['d6']['pop'].update(value='60000'),
            'POP zero': lambda c: c['d6']['pop'].update(value=0),
            'POP0 ujemne': lambda c: c['d6']['pop0'].update(value=-1),
            'POP0 = POP': lambda c: c['d6']['pop0'].update(value=60000),
            'POP0 > POP': lambda c: c['d6']['pop0'].update(value=70000),
            'waga bool': lambda c: c['d3'].update(weight=True),
            'waga zero': lambda c: c['d3'].update(weight=0),
            'waga > 1': lambda c: c['d3'].update(weight=1.5),
            'waga tekst': lambda c: c['d3'].update(weight='0.5'),
            'sampling float': lambda c: c['sampling'].update(size_per_stratum=30.0),
        }
        for label, change in cases.items():
            self.assert_code_2(self.variant(change), label)
        # Waga 1 jest w zakresie (0, 1], ale ADR-007 przyjmuje tylko 0,5 (C3).
        self.assert_code_2(self.variant(lambda c: c['d3'].update(weight=1)), 'waga 1')

    def test_kwjp_only_rollback_is_always_accepted(self):
        def rollback(config):
            config['d3'] = {'source': 'kwjp', 'field': 'F'}
        # Wycofanie NKJP zostawiające regułę D4 to błąd: bez NKJP nie ma czego czyścić (C3).
        self.assert_code_2(self.variant(rollback), 'wycofanie z d4')

        def without_d4(config):
            rollback(config)
            config['d4'] = None
        self.assertIsNone(load_config(self.write(self.variant(without_d4)))['d4'])

    def test_only_adr_007_values_pass_and_kwjp_only_needs_d4_null(self):
        cases = {
            'd1 kwjp-all': lambda c: c.update(d1='kwjp-all'),
            'd2 klasy': lambda c: c['d2'].update(classes=['voc']),
            'd2 bez konstrukcji': lambda c: c['d2'].update(constructions='no'),
            'd2 reguła (ii)': lambda c: c['d2'].update(membership='ii'),
            'd3 pole ARF': lambda c: c['d3'].update(field='ARF'),
            'd3 średnia percentyli F': lambda c: c['d3'].update(field='F'),
            'd3 sama KWJP log-ipm z d4': lambda c: c.update(d3={'source': 'kwjp', 'field': 'log-ipm'}),
            'd3 waga 0,75': lambda c: c['d3'].update(weight=0.75),
            'd3 sama KWJP ARF': lambda c: c.update(d3={'source': 'kwjp', 'field': 'ARF'}, d4=None),
            'd4 inna reguła': lambda c: c.update(d4='strip-edges'),
            'd5 d': lambda c: c['d5'].update(groups='d'),
            'd5 e dosłowne': lambda c: c['d5'].update(groups='e'),
            'd5 bez przycinania': lambda c: c['d5'].update(members='all'),
            'd6 przez pokrycie': lambda c: c.update(d6={
                'pop': {'by': 'coverage', 'value': 0.98, 'denominator': 'kwjp-standard'},
                'pop0': {'by': 'coverage', 'value': 0.9, 'denominator': 'kwjp-standard'}}),
            'd8 exclude': lambda c: c.update(d8='exclude'),
            'd8 available-only': lambda c: c.update(d8='available-only'),
            'd8 przy wycofaniu NKJP': lambda c: c.update(d3={'source': 'kwjp', 'field': 'F'}, d4=None,
                                                          d8='available-only'),
            'd9 true': lambda c: c.update(proper_names_in_ranking=True),
            'wycofanie z d4': lambda c: c.update(d3={'source': 'kwjp', 'field': 'F'}),
        }
        for label, change in cases.items():
            self.assert_code_2(self.variant(change), label)
        load_config(self.ROOT / 'config/generator/pop-v2.json')
        config = load_config(self.write(self.variant(lambda c: c.update(d3={'source': 'kwjp', 'field': 'F'},
                                                                          d4=None))))
        self.assertEqual((config['d3'], config['d4']), ({'source': 'kwjp', 'field': 'F'}, None))
        # Wycofanie NKJP przy log-ipm: sama KWJP log-ipm bez D4 (ta sama kolejność co F).
        config = load_config(self.write(self.variant(lambda c: c.update(d3={'source': 'kwjp', 'field': 'log-ipm'},
                                                                          d4=None))))
        self.assertEqual((config['d3'], config['d4']), ({'source': 'kwjp', 'field': 'log-ipm'}, None))

    def test_sampling_other_than_pop_quality_v1_is_code_2(self):
        cases = {
            'quality-v1': lambda c: c.update(sampling={'version': 'quality-v1', 'seed': 'literaki-slownik-g1-v1',
                                                       'size_per_stratum': 30,
                                                       'encoding': c['sampling']['encoding']}),
            'zły seed': lambda c: c['sampling'].update(seed='inny'),
            'inny rozmiar': lambda c: c['sampling'].update(size_per_stratum=31),
            'inne kodowanie': lambda c: c['sampling'].update(encoding='json'),
            'nie obiekt': lambda c: c.update(sampling='pop-quality-v1'),
        }
        for label, change in cases.items():
            self.assert_code_2(self.variant(change), label)

    def test_must_include_pop0_is_non_empty_list_of_words(self):
        cases = {
            'pusta lista': lambda c: c.update(must_include_pop0=[]),
            'tekst': lambda c: c.update(must_include_pop0='kot'),
            'pusty wyraz': lambda c: c.update(must_include_pop0=['kot', '']),
            'liczba': lambda c: c.update(must_include_pop0=[1]),
            'powtórzenie': lambda c: c.update(must_include_pop0=['kot', 'kot']),
        }
        for label, change in cases.items():
            self.assert_code_2(self.variant(change), label)


def _lexeme(*names):
    return tuple(sorted((S, name) for name in names))


class PopBuildTests(unittest.TestCase):
    """Polecenie `pop`: listy POP i POP0 w pamięci (C1–C10, C14, C19).

    Rangi fikstury (D3 log-ipm 0,5/0,5, D8 lower-bound-kwjp-absent): polski 1 (sama KWJP, PROPER_SHARED), kot 2,
    lato+rok 3, duży 4, bać 5 (granica NKJP), fajny 6, zamek 7 (granica NKJP), ul 8; kumpel bez danych.
    Leksemy narastająco: 1, 2, 5, 6, 7, 8, 10, 11.
    """
    ROOT = Path(__file__).resolve().parent.parent

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = pop_fixture(Path(cls.tmp.name) / 'pop', NKJP_POP_1GRAMS)
        cls.standard = read_standard(cls.fixture['run'] / 'lists/standard.txt')
        cls.result = build_pop(cls.fixture['sources'], pop_config(cls.tmp.name, 9, 6))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.directory = Path(self.work.name)

    def tearDown(self):
        self.work.cleanup()

    def build(self, pop=9, pop0=6, **changes):
        return build_pop(self.fixture['sources'], pop_config(self.directory, pop, pop0, **changes))

    def code(self, call, *args, **kwargs):
        with self.assertRaises(GeneratorError) as raised:
            call(*args, **kwargs)
        return raised.exception.code

    def row(self, result, *names):
        unit = _lexeme(*names)
        found = [r for r in result['units'] if r['unit'] == unit]
        return found[0] if found else None

    def test_pop0_in_pop_in_standard_and_homonym_group_whole_or_not_at_all(self):
        result = self.result
        self.assertEqual(result['pop'], sorted(result['pop']))
        self.assertEqual(result['pop0'], sorted(result['pop0']))
        self.assertTrue(set(result['pop0']) < set(result['pop']) <= self.standard)
        self.assertEqual([r['unit'] for r in result['units'] if r['list'] == 'POP0'],
                         [_lexeme('polski'), _lexeme('kot'), _lexeme('lato', 'rok:S1', 'rok:S2'), _lexeme('duży')])
        # 6 leksemów w jednostkach POP0; `lato` przycięte (prune-weak-members), więc na liście 5.
        self.assertEqual(result['thresholds']['pop0']['pruning']['before']['lexemes'], 6)
        self.assertEqual(result['thresholds']['pop0']['lexemes'], 5)
        # Próg 9: grupa zamek (2 leksemy, ranga 7) się nie mieści, więc nie wchodzi żaden członek;
        # lista kończy się przed nią (8 leksemów), `ul` (ranga 8) też poza.
        self.assertEqual((result['thresholds']['pop']['lexemes'], result['thresholds']['pop']['rank']), (8, 6))
        self.assertEqual(result['thresholds']['pop']['next_block'], {'units': 1, 'lexemes': 2, 'rank': 7})
        zamek = self.row(result, 'zamek:a', 'zamek:b')
        self.assertEqual((zamek['rank'], zamek['list'], zamek['size']), (7, None, 2))
        self.assertNotIn('zamek', result['pop'])
        self.assertIsNone(self.row(result, 'ul')['list'])
        # Grupa ma jeden wiersz; członek nie ma własnego wiersza ani F.
        self.assertIsNone(self.row(result, 'zamek:a'))
        self.assertNotIn('F', zamek['kwjp'])
        # Próg 10: grupa wchodzi w całości.
        bigger = self.build(10, 6)
        self.assertEqual(bigger['thresholds']['pop']['lexemes'], 10)
        self.assertEqual(self.row(bigger, 'zamek:a', 'zamek:b')['list'], 'POP')
        self.assertIn('zamek', bigger['pop'])
        for name in ('pop', 'pop0'):
            report = result['thresholds'][name]
            self.assertEqual(set(report['coverage']), {'kwjp-standard', 'kwjp-all'})
            self.assertEqual(report['forms'], len(result[name]))

    def test_weak_member_of_listed_group_is_pruned_and_takes_only_its_own_forms(self):
        result = self.result
        lato, rok1, rok2 = (S, 'lato'), (S, 'rok:S1'), (S, 'rok:S2')
        row = self.row(result, 'lato', 'rok:S1', 'rok:S2')
        # Ranga i lista jednostki bez zmian (grupa nie jest dzielona ani przeliczana).
        self.assertEqual((row['rank'], row['list']), (3, 'POP0'))
        # `lato`: własne KWJP 20 (EXACT), wspólne `lata` poza miarą → ranga 6 (pod `bać`), pod progiem POP0 (4), w POP (6).
        # rok:S1+rok:S2: bez własnych dowodów, wspólny wiersz KWJP `rok` → jedna podjednostka, ranga 1.
        self.assertEqual(row['members_in'], {'POP': [lato, rok1, rok2], 'POP0': [rok1, rok2]})
        self.assertEqual(row['member_ranks'], {f'lato@{S}': 6, f'rok:S1@{S}': 1, f'rok:S2@{S}': 1})
        self.assertNotIn('lato', result['pop0'])
        self.assertIn('lato', result['pop'])
        self.assertIn('lata', result['pop0'])  # forma wspólna z rok:S1 zostaje
        self.assertIn('rok', result['pop0'])
        pop0, pop = result['thresholds']['pop0'], result['thresholds']['pop']
        self.assertEqual(pop0['pruning']['rule'], 'prune-weak-members-v2')
        self.assertEqual((pop0['pruning']['pruned_members'], pop['pruning']['pruned_members']), (1, 0))
        self.assertEqual(pop0['pruning']['examples'], [{'member': f'lato@{S}', 'unit_rank': 3, 'own_rank': 6,
                                                        'unit_size': 3}])
        self.assertEqual(pop0['forms'], len(result['pop0']))
        self.assertGreater(pop0['pruning']['before']['forms'], pop0['forms'])
        self.assertLessEqual(pop0['coverage']['kwjp-standard']['covered'],
                             pop0['pruning']['before']['coverage']['kwjp-standard']['covered'])
        # Jednostka jednoczłonowa: lista = członek, bez rang członków.
        duzy = self.row(result, 'duży')
        self.assertEqual(duzy['members_in'], {'POP': [(S, 'duży')], 'POP0': [(S, 'duży')]})
        self.assertNotIn('member_ranks', duzy)
        self.assertEqual(self.row(result, 'kumpel')['members_in'], {})

    def test_proper_name_has_no_rank_and_its_form_enters_through_common_lexeme(self):
        result = self.result
        self.assertIsNone(self.row(result, 'Polska'))
        self.assertFalse(any((S, 'Polska') in r['unit'] for r in result['units']))
        self.assertEqual(result['proper_units'], 1)
        self.assertEqual(self.row(result, 'polski')['list'], 'POP0')
        self.assertIn('polska', result['pop0'])
        # Lata: grupa lato+rok (wspólna forma NKJP), Polska nie łączy się z polski (D5 e-common).
        self.assertTrue(self.row(result, 'lato', 'rok:S1', 'rok:S2')['nkjp']['ambiguous'])

    def test_missing_data_full_is_out_partial_is_flagged_never_rank_zero(self):
        result = self.result
        kumpel = self.row(result, 'kumpel')
        self.assertEqual((kumpel['status'], kumpel['rank'], kumpel['list'], kumpel['value']),
                         ('NO_DATA', None, None, None))
        self.assertEqual((kumpel['kwjp']['status'], kumpel['nkjp']['status']),
                         ('ABSENT_OR_BELOW_PUBLICATION_THRESHOLD', 'NOT_IN_PUBLISHED_LIST'))
        self.assertNotIn('kumpel', result['pop'])
        bac = self.row(result, 'bać')
        # `boi` jest w NKJP (rew. 4: fikstura bez braków NKJP), ranga 5 jak w rew. 3 (D8 rew. 4:
        # brak w NKJP = sama KWJP, test w test_pop_v2.AsymmetricBoundTests).
        self.assertEqual((bac['status'], bac['flags'], bac['rank']), ('MEASURED', [], 5))
        polski = self.row(result, 'polski')
        self.assertEqual((polski['flags'], polski['rank']), (['single_source:kwjp'], 1))
        self.assertEqual(bac['nkjp']['status'], 'OBSERVED')
        self.assertEqual(result['missing']['full'], 1)
        for row in result['units']:
            self.assertNotEqual(row['rank'], 0)
            self.assertNotIn(0, (row['kwjp']['percentile'], row['nkjp']['percentile'], row['nkjp']['rank']))

    def test_construction_form_enters_with_component_and_ul_dot_stays_apart(self):
        result = self.result
        self.assertEqual(self.row(result, 'fajny')['list'], 'POP')
        self.assertIn('niefajny', result['pop'])
        self.assertNotIn('niefajny', result['pop0'])
        self.assertTrue({'niepolska', 'niepolski'} <= set(result['pop0']))
        # `ul.` (9 182 736) nie skleja się z `ul` (41 207): ul ma ostatnią rangę NKJP.
        ul = self.row(result, 'ul')
        # NKJP: kot, duży, lata, fajny, ul (polski PROPER_SHARED nie ma rangi NKJP).
        self.assertEqual((ul['nkjp']['status'], ul['nkjp']['rank'], ul['rank']), ('OBSERVED', 7, 8))
        self.assertEqual(result['nkjp_rule_id'], 'nkjp-clean-strip-edges-keep-dot-v1')
        self.assertNotIn('ul.', result['pop'])

    def test_word_missing_from_pop0_is_code_4(self):
        for words in (['kumpel'], ['fajny'], ['kot', 'pies']):
            self.assertEqual(self.code(self.build, must_include_pop0=words), 4, words)
        self.assertEqual(self.build(must_include_pop0=['kot', 'polska'])['must_include_pop0'],
                         {'kot': 2, 'polska': 1})

    def test_kwjp_only_does_not_open_nkjp_and_has_no_nkjp_fields(self):
        refuse = mock.Mock(side_effect=AssertionError('NKJP otwarty'))
        with mock.patch.object(pop_module, 'read_nkjp', refuse), mock.patch.object(pop_module.gzip, 'open', refuse):
            result = self.build(11, 6, d3={'source': 'kwjp', 'field': 'F'}, d4=None, must_include_pop0=['rok'])
        refuse.assert_not_called()
        self.assertNotIn('nkjp', dumps(result).lower())
        self.assertTrue(all('nkjp' not in row for row in result['units']))
        # Sama KWJP F: bez NKJP `lata` nie łączy lato z rok. rok 90, bać 70, polski 50, duży 40;
        # kot (F 7) poza POP0.
        self.assertEqual([r['unit'] for r in result['units'] if r['list'] == 'POP0'],
                         [_lexeme('rok:S1', 'rok:S2'), _lexeme('bać'), _lexeme('polski'), _lexeme('duży')])
        self.assertEqual(self.code(self.build, 11, 6, d3={'source': 'kwjp', 'field': 'F'}, d4=None), 4)
        self.assertTrue(set(result['pop0']) < set(result['pop']) <= self.standard)

    def test_database_hash_unchanged_and_cli_codes(self):
        f = self.fixture
        before = sha256(f['database'])
        result = self.build()
        self.assertEqual((result['database_sha256'], sha256(f['database'])), (before, before))
        changed = mock.Mock(side_effect=[before, 'f' * 64])
        with mock.patch.object(pop_module, 'database_sha256', changed):
            self.assertEqual(self.code(self.build), 5)
        self.assertEqual(changed.call_count, 2)

        def cli(sources, config, *extra, output='out', text=False):
            output = self.directory / output
            existed = output.exists()
            done = subprocess.run([sys.executable, '-m', 'literaki_slownik', 'pop', '--manifest', str(sources),
                                   '--config', str(config), '--output-dir', str(output),
                                   *(() if text else ('--json',)), *extra],
                                  cwd=self.ROOT, capture_output=True, text=True)
            if done.returncode and not existed:
                self.assertFalse(output.exists())
            return done.returncode, done.stdout if text else json.loads(done.stdout)

        good = pop_config(self.directory, 9, 6)
        code, answer = cli(f['sources'], good, output='package')
        self.assertEqual((code, answer['status'], answer['command']), (0, 'ok', 'pop'), answer)
        self.assertEqual(answer['result']['thresholds']['pop0']['lexemes'], 5)
        self.assertEqual(answer['result']['must_include_pop0'], {'kot': 2})
        self.assertEqual(answer['result']['output_dir'], str((self.directory / 'package').resolve()))
        self.assertTrue((self.directory / 'package/SHA256SUMS').is_file())
        code, text = cli(f['sources'], good, output='package-text', text=True)
        self.assertEqual(code, 0)
        self.assertIn(str((self.directory / 'package-text').resolve()), text)
        self.assertIn(f"POP0: {answer['result']['forms']['pop0']} form", text)
        self.assertEqual(cli(f['sources'], good, output='package')[0], 4)
        for path in self.directory.rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        (self.directory / 'bad').mkdir()
        bad = pop_config(self.directory / 'bad', 9, 6, d5='d')
        self.assertEqual(cli(f['sources'], bad)[0], 2)
        pin = write_pop_sources(self.directory / 'pin.json', f['run'], f['release'], f['nkjp'],
                                database_sha256='0' * 64)
        self.assertEqual(cli(pin, good)[0], 3)
        run = self.directory / 'run'
        shutil.copytree(f['run'], run)
        manifest = load_json(run / 'manifest.json')
        manifest['readiness'] = 'VERIFIED'
        write_json(run / 'manifest.json', manifest)
        self.assertEqual(cli(f['sources'], good, '--run-dir', str(run))[0], 5)


# Rzadkie ciągi cyfr NKJP z `NKJP_POP_1GRAMS` (11.2) i ich suma: żaden nie może trafić do pakietu (C14).
NKJP_NUMBERS = ('97340919', '6182537', '5093746', '4718293', '9182736', '7837465', '3271946', '1302857', '130419', '135102442')
PACKAGE_FILES = {'POP.txt.gz', 'POP0.txt.gz', 'reports/thresholds.json', 'reports/units.json', 'reports/sample.json',
                 'reports/review-template.json', 'release-manifest.json', 'ATTRIBUTIONS.md', 'LIMITATIONS.md',
                 'TERMS.md', 'SHA256SUMS'}
NKJP_KEYS = {'nkjp_rank', 'nkjp_percentile', 'nkjp_status'}


def _files(directory):
    return {str(p.relative_to(directory)): p for p in sorted(Path(directory).rglob('*')) if p.is_file()}


def _json_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _json_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _json_keys(item)


class PopPackageTests(unittest.TestCase):
    """Pakiet POP `BUILT` (C11–C13, C17, C18, C19); fikstura `pop_package` (progi 9/6)."""

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

    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.directory = Path(self.work.name)

    def tearDown(self):
        for path in self.directory.rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        self.work.cleanup()

    def read(self, relative):
        return (self.package / relative).read_text(encoding='utf-8')

    def test_two_runs_are_byte_identical_and_gzip_is_canonical(self):
        other = self.directory / 'b'
        build_package(self.made['sources'], self.made['config'], other)
        first, second = _files(self.package), _files(other)
        self.assertEqual(set(first), set(second))
        for relative in first:
            self.assertEqual(first[relative].read_bytes(), second[relative].read_bytes(), relative)
        result = build_pop(self.made['sources'], self.made['config'])
        for name in ('POP', 'POP0'):
            raw = (self.package / f'{name}.txt.gz').read_bytes()
            # Nagłówek gzip: bez FNAME (FLG = 0), MTIME = 0, XFL = 2 (poziom 9).
            self.assertEqual((raw[3], raw[4:8], raw[8]), (0, b'\0\0\0\0', 2), name)
            text = gzip.decompress(raw).decode('utf-8')
            keys = result[name.lower()]
            self.assertEqual(text, ''.join(k + '\n' for k in keys))
            self.assertEqual(keys, sorted(keys))
        self.assertIn('kot', gzip.decompress((self.package / 'POP0.txt.gz').read_bytes()).decode().split('\n'))

    def test_layout_and_sha256sums_cover_everything_but_itself(self):
        self.assertEqual(set(_files(self.package)), PACKAGE_FILES)
        lines = self.read('SHA256SUMS').splitlines()
        listed = [line.split('  ', 1)[1] for line in lines]
        self.assertEqual(listed, sorted(listed))
        self.assertEqual(set(listed), PACKAGE_FILES - {'SHA256SUMS'})
        for line in lines:
            digest, relative = line.split('  ', 1)
            self.assertEqual(digest, sha256(self.package / relative), relative)

    def test_manifest_is_built_pinned_and_free_of_time_and_paths(self):
        from literaki_slownik.run import code_identity
        made, text = self.made, self.read('release-manifest.json')
        manifest = json.loads(text)
        self.assertEqual((manifest['status'], manifest['method'], manifest['adr']),
                         ('BUILT', 'pop-v2', 'docs/adr/ADR-007-metoda-pop-v1.md'))
        inputs = manifest['inputs']
        self.assertEqual(inputs['database_sha256'], sha256(made['database']))
        self.assertEqual(inputs['release_manifest_sha256'], sha256(made['release'] / 'release-manifest.json'))
        self.assertEqual(inputs['standard_sha256'], sha256(made['run'] / 'lists/standard.txt'))
        self.assertEqual(inputs['nkjp_sha256'], sha256(made['nkjp']))
        self.assertEqual(inputs['sources_sha256'], sha256(made['sources']))
        self.assertEqual(manifest['config_sha256'], sha256(made['config']))
        self.assertEqual(manifest['code_identity'], code_identity())
        self.assertEqual(manifest['must_include_pop0'], ['kot'])
        self.assertEqual(manifest['nkjp_rule_id'], 'nkjp-clean-strip-edges-keep-dot-v1')
        self.assertEqual(set(manifest['files']), PACKAGE_FILES - {'SHA256SUMS', 'release-manifest.json'})
        for relative, meta in manifest['files'].items():
            path = self.package / relative
            self.assertEqual((meta['sha256'], meta['bytes']), (sha256(path), path.stat().st_size), relative)
        self.assertNotRegex(text, r'\d{4}-\d{2}-\d{2}T\d{2}:')
        for path in (self.tmp.name, str(Path(self.tmp.name).resolve()), str(Path.home())):
            self.assertNotIn(path, text)
        self.assertNotIn('"/', text)

    def test_read_only_existing_target_is_4_and_failure_leaves_nothing(self):
        for relative, path in _files(self.package).items():
            self.assertEqual(path.stat().st_mode & 0o777, 0o444, relative)
        made = self.made
        existing = self.directory / 'existing'
        existing.mkdir()
        (existing / 'keep.txt').write_text('x', encoding='utf-8')
        with self.assertRaises(GeneratorError) as raised:
            build_package(made['sources'], made['config'], existing)
        self.assertEqual(raised.exception.code, 4)
        self.assertEqual(set(_files(existing)), {'keep.txt'})
        broken = mock.Mock(side_effect=[None, OSError('dysk pełny')])
        target = self.directory / 'broken'
        with mock.patch.object(pop_module, '_write_gzip', broken), self.assertRaises(OSError):
            build_package(made['sources'], made['config'], target)
        self.assertEqual(broken.call_count, 2)
        self.assertFalse(target.exists())
        self.assertEqual(sorted(p.name for p in self.directory.iterdir()), ['existing'])

    def test_package_has_no_nkjp_numbers_raw_file_or_foreign_nkjp_keys(self):
        raw_lines = [line.strip() for line in NKJP_POP_1GRAMS.splitlines()]
        found_keys = set()
        for relative, path in _files(self.package).items():
            data = path.read_bytes()
            text = (gzip.decompress(data) if relative.endswith('.gz') else data).decode('utf-8')
            for number in NKJP_NUMBERS:
                self.assertNotIn(number, text, relative)
            for line in raw_lines:
                self.assertNotIn(line, text, relative)
            self.assertNotIn('1grams', relative.lower())
            if relative.startswith('reports/'):
                found_keys |= {k for k in _json_keys(json.loads(text)) if 'nkjp' in k.lower()}
        self.assertEqual(found_keys, NKJP_KEYS)

    def test_package_has_combined_rank_and_percentile_but_no_raw_log_ipm(self):
        # C14: miara log-ipm łączy F NKJP z sumą korpusu; pakiet podaje tylko rangę i percentyl łączny.
        result = build_pop(self.made['sources'], self.made['config'])
        rows = json.loads(self.read('reports/units.json'))['units']
        ranked = [row for row in rows if row['rank'] is not None]
        self.assertTrue(ranked)
        for row in rows:
            self.assertNotIn('value', row)
            self.assertIn('percentile', row)
        self.assertEqual(ranked[0]['percentile'], 100.0)
        self.assertEqual(min(row['percentile'] for row in ranked), round(100 / len(ranked), 4))
        self.assertTrue(all(row['percentile'] is None for row in rows if row['rank'] is None))
        values = [row['value'] for row in result['units'] if row['value'] is not None
                  and not any(f == 'single_source:kwjp' for f in row['flags'])]
        self.assertTrue(values)
        texts = {relative: (gzip.decompress(p.read_bytes()) if relative.endswith('.gz') else p.read_bytes())
                 .decode('utf-8') for relative, p in _files(self.package).items()}
        for value in values:
            for shape in {repr(value)[:8], f'{value:.4f}', f'{value:.6f}'}:
                for relative, text in texts.items():
                    self.assertNotIn(shape, text, (relative, value))

    def test_samples_use_pop_quality_v1_strata_and_review_template_is_bound(self):
        sample = json.loads(self.read('reports/sample.json'))
        self.assertEqual((sample['version'], sample['seed'], sample['size_per_stratum'], sample['status']),
                         ('pop-quality-v1', 'literaki-slownik-pop-v1', 30, 'UNREVIEWED'))
        fixed = {'pop-granica-wewnatrz', 'pop-granica-zewnatrz', 'pop0-granica-wewnatrz', 'pop0-granica-zewnatrz',
                 'braki-danych', 'rozbieznosc-korpusow', 'grupy-homonimow', 'formy-krotkie', 'formy-dlugie',
                 'czeste-poza-lista'}
        strata = sample['strata']
        self.assertTrue(fixed <= set(strata), set(strata))
        self.assertTrue(any(name.startswith('pos-') for name in strata))
        self.assertTrue(set(strata) - fixed <= {f'pos-{p}' for p in ('subst', 'verb', 'adj', 'adv', 'other')})
        selected = lambda name: {item['key'] for item in strata[name]['selected']}
        self.assertIn(f'kumpel@{S}', selected('braki-danych'))
        self.assertIn(f'zamek:a@{S}', selected('grupy-homonimow'))
        self.assertIn(f'kot@{S}', selected('pop0-granica-wewnatrz'))
        self.assertIn(f'zamek:b@{S}', selected('pop0-granica-zewnatrz'))
        # Członek przycięty z POP0 nie jest próbką z wnętrza POP0; w POP zostaje.
        self.assertNotIn(f'lato@{S}', selected('pop0-granica-wewnatrz'))
        self.assertIn(f'lato@{S}', selected('pop-granica-wewnatrz'))
        template = json.loads(self.read('reports/review-template.json'))
        self.assertEqual(template['status'], 'UNREVIEWED')
        self.assertEqual(template['canonical_index_sha256'], sha256(self.package / 'reports/units.json'))
        self.assertEqual(template['sample_sha256'], sha256(self.package / 'reports/sample.json'))
        self.assertEqual(template['evidence_sha256'],
                         {name: sha256(self.package / name)
                          for name in ('POP.txt.gz', 'POP0.txt.gz', 'reports/thresholds.json')})
        self.assertTrue(template['items'] and all(i['assessment'] is None for i in template['items']))

    def test_package_rows_carry_member_lists_and_thresholds_report_pruning(self):
        rows = json.loads(self.read('reports/units.json'))['units']
        rok, = [row for row in rows if f'lato@{S}' in row['members']]
        self.assertEqual(rok['members_in'], {'POP': [f'lato@{S}', f'rok:S1@{S}', f'rok:S2@{S}'],
                                             'POP0': [f'rok:S1@{S}', f'rok:S2@{S}']})
        self.assertEqual(rok['member_ranks'], {f'lato@{S}': 6, f'rok:S1@{S}': 1, f'rok:S2@{S}': 1})
        for row in rows:
            listed = row['members_in']
            self.assertTrue(set(listed.get('POP0', ())) <= set(listed.get('POP', ())) <= set(row['members']))
            self.assertEqual(bool(listed), row['list'] is not None)
        thresholds = json.loads(self.read('reports/thresholds.json'))['thresholds']
        self.assertEqual(thresholds['pop0']['pruning']['pruned_members'], 1)
        self.assertEqual(thresholds['pop0']['pruning']['examples'][0]['member'], f'lato@{S}')
        words = gzip.decompress((self.package / 'POP0.txt.gz').read_bytes()).decode('utf-8').split()
        self.assertNotIn('lato', words)
        self.assertEqual(thresholds['pop0']['forms'], len(words))

    def test_ul_dot_mass_stays_out_of_ul_in_package(self):
        # D4 w pakiecie: `ul` ma rangę NKJP z własnych 41 207, nie z 9 182 736 `ul.`; `ul.` nie ma wiersza.
        rows = json.loads(self.read('reports/units.json'))['units']
        ul, = [row for row in rows if 'ul@synthetic' in row['members']]
        self.assertEqual((ul['members'], ul['nkjp_status'], ul['nkjp_rank'], ul['rank']),
                         (['ul@synthetic'], 'OBSERVED', 7, 8))
        self.assertEqual(min(row['nkjp_rank'] for row in rows if row['nkjp_rank'] is not None), 1)
        self.assertNotEqual(ul['nkjp_rank'], 1)
        for name in ('POP.txt.gz', 'POP0.txt.gz'):
            words = gzip.decompress((self.package / name).read_bytes()).decode('utf-8').split()
            self.assertNotIn('ul.', words)
            self.assertFalse([w for w in words if '.' in w], name)

    def test_attributions_follow_adr_006_terms_and_kwjp_only_drops_nkjp(self):
        made = self.made
        nkjp = [i for i in load_sources(made['sources'])['inputs'] if i['kind'] == 'nkjp_1gram'][0]
        attributions = self.read('ATTRIBUTIONS.md')
        for text in (nkjp['creator'], nkjp['url'], nkjp['license'], nkjp['sha256'], nkjp['title'],
                     'nkjp-clean-strip-edges-keep-dot-v1', 'ADR-006', '1.0–4.0', 'nie popierają', 'SGJP'):
            self.assertIn(text, attributions)
        terms = self.read('TERMS.md')
        for text in ('CC BY 4.0', 'BSD-2-Clause', 'SGJP', 'KWJP', 'NKJP', 'ADR-006'):
            self.assertIn(text, terms)
        limitations = self.read('LIMITATIONS.md')
        for text in ('STANDARD', 'D7', 'D9', 'e-common', 'zrobił', 'próbk', 'pop-sources.json',
                     'nkjp-clean-strip-edges-keep-dot-v1'):
            self.assertIn(text, limitations)
        # C19: sama KWJP (wycofanie NKJP) nie czyta NKJP i nie wymienia go w atrybucjach ani manifeście.
        refuse = mock.Mock(side_effect=AssertionError('NKJP otwarty'))
        config = pop_config(self.directory, 11, 6, d3={'source': 'kwjp', 'field': 'F'}, d4=None,
                            must_include_pop0=['rok'])
        target = self.directory / 'kwjp'
        with mock.patch.object(pop_module, 'read_nkjp', refuse), mock.patch.object(pop_module.gzip, 'open', refuse):
            build_package(made['sources'], config, target)
        refuse.assert_not_called()
        for name in ('ATTRIBUTIONS.md', 'release-manifest.json', 'TERMS.md'):
            self.assertNotIn('nkjp', (target / name).read_text(encoding='utf-8').lower(), name)
        self.assertIn('SGJP', (target / 'ATTRIBUTIONS.md').read_text(encoding='utf-8'))
        # Wzór licencji ADR-006 w repozytorium: „CC BY, wersja nieokreślona”.
        repo = load_sources(Path(__file__).resolve().parent.parent / 'config/generator/pop-sources.json')
        license = [i for i in repo['inputs'] if i['kind'] == 'nkjp_1gram'][0]['license']
        self.assertIn('CC BY, wersja nieokreślona', license)


class RepositoryPopSourcesTests(unittest.TestCase):
    def test_repository_manifest_is_valid_and_pinned(self):
        root = Path(__file__).resolve().parent.parent
        sources = load_sources(root / 'config/generator/pop-sources.json')
        self.assertEqual(sources['version'], 'pop-sources-v1')
        self.assertEqual(sources['base']['database_sha256'][:8], '85b23ca5')
        self.assertEqual(sources['base']['release_manifest_sha256'][:8], '54705743')
        self.assertEqual(sources['base']['standard_sha256'][:8], 'a432c7c5')
        nkjp = [i for i in sources['inputs'] if i['kind'] == 'nkjp_1gram'][0]
        self.assertEqual(nkjp['sha256'], '73af49094621b2f86b594beba783c14aee8c8212f1aff3d61f281ab5d99e3dc9')
        self.assertEqual(sorted(i['kind'] for i in sources['inputs']), ['kwjp', 'nkjp_1gram'])


if __name__ == '__main__':
    unittest.main()
