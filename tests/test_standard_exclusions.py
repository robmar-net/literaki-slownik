"""Wykluczenia dokładnych analiz ze STANDARD (#15): walidator, faza decisions, explain."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from literaki_slownik.canonical import dumps
from literaki_slownik.database import connect
from literaki_slownik.inputs import GeneratorError
from literaki_slownik import standard_exclusions as sex
from tests.helpers import fixture_manifest, rewrite

ROOT = Path(__file__).resolve().parents[1]
RULE = 'linguistic-standard-no-polish-meaning-v1'
SOURCE_SHA = 'a' * 64
UP = {'source_id': 'synthetic', 'first_source_row': 3, 'original': 'up', 'lemma_id': 'up',
      'raw_tag': 'interj', 'names': '', 'qualifiers': ''}
OU = {'source_id': 'synthetic', 'first_source_row': 5, 'original': 'ou', 'lemma_id': 'ou',
      'raw_tag': 'interj', 'names': '', 'qualifiers': 'rzad.'}


def entry(record, tag='interj'):
    return {'kind': 'source', 'reason': 'brak polskiego znaczenia', **record, 'tag': tag}


def config():
    return {
        'schema_version': 1, 'decision_version': 'standard-exclusions-test', 'description': 'fikstura',
        'rule_id': RULE,
        'source_snapshot': {'run': 'fixture', 'policy_version': 'test'},
        'sources': {'synthetic': SOURCE_SHA},
        'provenance': {'issue': 'https://github.com/robmar-net/literaki-slownik/issues/15',
                       'research_task': 'fixture', 'approval': 'fixture',
                       'inputs': {'decision.md': 'c' * 64, 'report.md': 'd' * 64}},
        'expected_counts': {'words': 2, 'analyses': 2},
        'cases': [{'word': 'ou', 'analyses': [entry(OU)]}, {'word': 'up', 'analyses': [entry(UP)]}],
    }


def key(record, tag='interj'):
    return hashlib.sha256(dumps(['source', record, tag]).encode()).hexdigest()


def fixture_db(path, *, with_analyses=True):
    with connect(path, create=True) as db:
        db.execute("insert into source_artifact values ('synthetic','sgjp_tab',?)", (json.dumps({'sha256': SOURCE_SHA}),))
        for iid, item in ((1, UP), (2, OU)):
            db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)',
                       ('synthetic', item['first_source_row'], item['original'], item['lemma_id'], item['raw_tag'],
                        item['names'], item['qualifiers']))
            db.execute('insert into lexeme values (?,?,?,?)', (iid, 'synthetic', item['lemma_id'], item['lemma_id']))
            db.execute('insert into surface_form values (?,?,?,?,?)',
                       (iid, item['original'], item['original'], item['original'], len(item['original'])))
            db.execute('insert into interpretation values (?,?,?,?,?,?,?,?)',
                       (iid, 'synthetic', item['first_source_row'], iid, iid, item['raw_tag'], item['names'], item['qualifiers']))
            if with_analyses:
                db.execute('insert into analysis values (?,?,?,?,?,?,?,?,?)',
                           (key(item), iid, None, 'interj', item['original'], item['original'], item['original'], 2, 'test'))


class StandardExclusionsTests(unittest.TestCase):
    def load(self, value, hashes=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'exclusions.json'
            path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
            return sex.load(path, source_hashes=hashes or {'synthetic': SOURCE_SHA})

    def refused(self, value, hashes=None):
        with self.assertRaises(GeneratorError):
            self.load(value, hashes)

    def test_valid_config_maps_exact_analysis_keys(self):
        loaded = self.load(config())
        self.assertEqual(set(loaded['analyses']), {key(UP), key(OU)})
        self.assertEqual(loaded['analyses'][key(UP)]['word'], 'up')
        self.assertEqual(loaded['counts'], {'words': 2, 'analyses': 2})
        self.assertEqual(loaded['rule_id'], RULE)
        with tempfile.TemporaryDirectory() as directory:
            fixture_db(Path(directory) / 'build.sqlite')
            with connect(Path(directory) / 'build.sqlite', readonly=True) as db:
                self.assertEqual(sex.check_database(db, loaded)['matched_analyses'], 2)

    def test_wrong_source_hash_is_refused(self):
        self.refused(config(), {'synthetic': 'e' * 64})
        value = config()
        value['sources']['synthetic'] = 'e' * 64
        self.refused(value)
        value = config()
        value['sources']['other'] = SOURCE_SHA
        self.refused(value, {'synthetic': SOURCE_SHA, 'other': SOURCE_SHA})  # nieużywany hash
        loaded = self.load(config())
        with tempfile.TemporaryDirectory() as directory:
            fixture_db(Path(directory) / 'build.sqlite')
            with connect(Path(directory) / 'build.sqlite') as db:
                db.execute("update source_artifact set metadata=? where source_id='synthetic'", (json.dumps({'sha256': 'e' * 64}),))
            with connect(Path(directory) / 'build.sqlite', readonly=True) as db, self.assertRaises(GeneratorError):
                sex.check_database(db, loaded)

    def test_schema_order_duplicates_and_counts_are_refused(self):
        mutations = {
            'inna reguła': lambda v: v.update(rule_id='linguistic-historical-form-v1'),
            'nieznane pole': lambda v: v.update(extra=True),
            'brak pola': lambda v: v.pop('provenance'),
            'wersja schematu': lambda v: v.update(schema_version=2),
            'liczby': lambda v: v['expected_counts'].update(analyses=3),
            'kolejność przypadków': lambda v: v['cases'].reverse(),
            'powtórzony przypadek': lambda v: v['cases'].append(deepcopy(v['cases'][1])),
            'powtórzona analiza': lambda v: v['cases'][1]['analyses'].append(deepcopy(v['cases'][1]['analyses'][0])),
            'pusty przypadek': lambda v: v['cases'][1].update(analyses=[]),
            'brak powodu': lambda v: v['cases'][1]['analyses'][0].update(reason=''),
            'konstrukcja': lambda v: v['cases'][1]['analyses'][0].update(kind='construction'),
            'zły hash wejścia': lambda v: v['provenance']['inputs'].update({'report.md': 'x'}),
            'brak zgłoszenia': lambda v: v['provenance'].pop('issue'),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                value = config()
                mutate(value)
                self.refused(value)

    def test_wrong_tag_form_and_record_fields_are_refused(self):
        mutations = {
            'tag spoza rozwinięcia': lambda v: v['cases'][1]['analyses'][0].update(tag='qub'),
            'inna forma gry': lambda v: v['cases'][1]['analyses'][0].update(original='hup'),
            'nieznormalizowany napis': lambda v: v['cases'][1].update(word='Up'),
            'zły wiersz': lambda v: v['cases'][1]['analyses'][0].update(first_source_row=0),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                value = config()
                mutate(value)
                self.refused(value)

    def test_record_must_exist_exactly_in_database(self):
        changes = {'wiersz': lambda e: e.update(first_source_row=4),
                   'lemat': lambda e: e.update(lemma_id='up:S2'),
                   'kwalifikatory': lambda e: e.update(qualifiers='rzad.')}
        for name, change in changes.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                value = config()
                change(value['cases'][1]['analyses'][0])
                loaded = self.load(value)
                fixture_db(Path(directory) / 'build.sqlite')
                with connect(Path(directory) / 'build.sqlite', readonly=True) as db, self.assertRaises(GeneratorError):
                    sex.check_database(db, loaded)
        loaded = self.load(config())
        with tempfile.TemporaryDirectory() as directory:
            # Przed oceną (pusta tabela analysis) sprawdzamy same rekordy importu.
            fixture_db(Path(directory) / 'build.sqlite', with_analyses=False)
            with connect(Path(directory) / 'build.sqlite', readonly=True) as db:
                self.assertEqual(sex.check_database(db, loaded, analyses=False)['matched_analyses'], 2)
                with self.assertRaises(GeneratorError):
                    sex.check_database(db, loaded)

    def test_manifest_pin_detects_unhashed_change(self):
        with tempfile.TemporaryDirectory() as directory:
            path, manifest = fixture_manifest(directory)
            value = config()
            value['sources'] = {'synthetic': manifest['artifacts'][0]['sha256']}
            target = Path(directory) / 'standard-exclusions.json'
            target.write_text(sex.render(value), encoding='utf-8')
            manifest['configurations'][sex.CONFIG_KEY] = {
                'path': target.name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
            rewrite(path, manifest)
            self.assertEqual(len(sex.from_manifest(path)['analyses']), 2)
            script = [sys.executable, str(ROOT / 'scripts/check_standard_exclusions.py'), '--manifest', str(path)]
            self.assertEqual(subprocess.run(script, capture_output=True, cwd=ROOT).returncode, 0)
            target.write_text(sex.render(value).replace('"fikstura"', '"fikstura zmieniona"'), encoding='utf-8')
            with self.assertRaises(GeneratorError):
                sex.from_manifest(path)
            self.assertNotEqual(subprocess.run(script, capture_output=True, cwd=ROOT).returncode, 0)

    def test_render_is_deterministic_and_round_trips(self):
        text = sex.render(config())
        self.assertEqual(json.loads(text), config())
        self.assertEqual(sex.render(json.loads(text)), text)

    def test_repository_config_is_pinned_and_exact(self):
        loaded = sex.from_manifest(ROOT / 'config/generator/sources.json')
        self.assertEqual(loaded['counts'], {'words': 2, 'analyses': 2})
        self.assertEqual(sorted((e['word'], e['lemma_id'], e['tag']) for e in loaded['analyses'].values()),
                         [('ou', 'ou', 'interj'), ('up', 'up', 'interj')])
        self.assertEqual({e['source_id'] for e in loaded['analyses'].values()}, {'sgjp-20261018'})
        path = ROOT / 'config/generator/standard-exclusions.json'
        text = path.read_text(encoding='utf-8')
        self.assertEqual(sex.render(json.loads(text)), text)
        provenance = json.loads(text)['provenance']
        self.assertEqual(provenance['issue'], 'https://github.com/robmar-net/literaki-slownik/issues/15')
        task = '.maister/tasks/research/2026-10-31-przeglad-wykrzyknikow'
        self.assertEqual(provenance['research_task'], task)
        self.assertEqual(set(provenance['inputs']), {f'{task}/outputs/decision.md', f'{task}/outputs/report.md'})
        for name, value in provenance['inputs'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), value, name)

    def test_rule_is_documented_in_policy(self):
        rules = {r['rule_id']: r for r in json.loads((ROOT / 'config/generator/policy.json').read_text())['rules']}
        rule = rules[RULE]
        self.assertEqual(rule['variants'], {'broad': 'unchanged', 'standard': 'reject'})
        self.assertEqual(rule['config'], 'config/generator/standard-exclusions.json')
        self.assertIn('issues/15', rule['issue'])


# Faza decisions. Fikstura: dwie wykluczane analizy, homonim nazwy (wielka litera),
# inny wykrzyknik, który zostaje, i dawna forma odrzucona z innego powodu.
BUILD_SGJP = ('#</COPYRIGHT>\n'
              'UP\tUP\tsubst:sg:nom:f\tnazwa_organizacji\t\n'
              'up\tup\tinterj\t\t\n'
              'ou\tou\tinterj\t\trzad.\n'
              'au\tau\tinterj\t\t\n'
              'kot\tkot\tsubst:sg:nom:m2\t\t\n'
              'zamku\tzamek\tsubst:sg:gen:m3\tnazwa_pospolita\tdaw.\n')


def build_entry(db, original, lemma):
    row = db.execute('''select i.source_id,i.first_row,f.original,l.lemma_id,i.tag,i.names,i.qualifiers
        from interpretation i join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id
        where f.original=? and l.lemma_id=?''', (original, lemma)).fetchone()
    record = dict(zip(sex.RECORD, row))
    return {'kind': 'source', 'reason': 'brak polskiego znaczenia', **record, 'tag': record['raw_tag'].split('.')[0]}


def build_config(source_sha, entries):
    cases = {}
    for item in entries:
        cases.setdefault(item['original'].lower(), []).append(item)
    value = config()
    value.update(sources={'synthetic': source_sha},
                 cases=[{'word': w, 'analyses': es} for w, es in sorted(cases.items())],
                 expected_counts={'words': len(cases), 'analyses': len(entries)})
    return value


class StandardExclusionBuildTests(unittest.TestCase):
    """Przypięty JSON odrzuca w STANDARD tylko wskazane analizy; BROAD bez zmian."""

    def setUp(self):
        from tests.test_build import BuildTests
        from literaki_slownik.build import build
        self.build = build
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest = BuildTests().manifest(self.root, BUILD_SGJP)
        self.old = self.root / 'old'
        build(self.manifest, self.old)
        with connect(self.old / 'build.sqlite', readonly=True) as db:
            self.entries = {'up': build_entry(db, 'up', 'up'), 'ou': build_entry(db, 'ou', 'ou'),
                            'UP': build_entry(db, 'UP', 'UP'), 'zamku': build_entry(db, 'zamku', 'zamek')}

    def tearDown(self):
        self.temp.cleanup()

    def pinned_run(self, names, name='new', sgjp=None):
        manifest = json.loads(self.manifest.read_text(encoding='utf-8'))
        if sgjp is not None:
            import gzip
            source = self.root / 'source.gz'
            with gzip.open(source, 'wt', encoding='utf-8') as stream:
                stream.write(sgjp)
            manifest['artifacts'][0]['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        target = self.root / f'{name}-exclusions.json'
        target.write_text(sex.render(build_config(manifest['artifacts'][0]['sha256'],
                                                  [self.entries[n] for n in names])), encoding='utf-8')
        manifest['configurations'][sex.CONFIG_KEY] = {'path': target.name,
                                                      'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
        rewrite(self.manifest, manifest)
        run = self.root / name
        self.build(self.manifest, run)
        return run

    def failed(self, run):
        stage = json.loads((run / 'manifest.json').read_text())['stages']['decisions']
        self.assertEqual(stage['status'], 'failed')
        self.assertFalse((run / 'lists/standard.txt').exists())

    def test_exact_analyses_leave_standard_only(self):
        self.assertEqual((self.old / 'lists/standard.txt').read_text(), 'au\nkot\nou\nup\n')
        run = self.pinned_run(['ou', 'up'])
        self.assertEqual((run / 'lists/standard.txt').read_text(), 'au\nkot\n')
        report = json.loads((run / 'reports/decisions.json').read_text())['standard_exclusions']
        manifest = json.loads(self.manifest.read_text())
        self.assertEqual(report, {'rule_id': RULE, 'decision_version': 'standard-exclusions-test',
                                  'entries': 2, 'matched': 2, 'unused': 0, 'words': 2,
                                  'sha256': manifest['configurations'][sex.CONFIG_KEY]['sha256']})
        self.assertNotIn('standard_exclusions', json.loads((self.old / 'reports/decisions.json').read_text()))

    def test_broad_is_unchanged(self):
        run = self.pinned_run(['ou', 'up'])
        self.assertEqual((run / 'lists/broad.txt').read_bytes(), (self.old / 'lists/broad.txt').read_bytes())
        self.assertIn('up\n', (run / 'lists/broad.txt').read_text())
        query = '''select a.analysis_key,d.assessment_key from analysis a join variant_decision d using(analysis_key)
            where d.variant='broad' order by 1'''
        with connect(run / 'build.sqlite', readonly=True) as new, connect(self.old / 'build.sqlite', readonly=True) as old:
            self.assertEqual(new.execute(query).fetchall(), old.execute(query).fetchall())

    def test_persisted_payload_names_rule_and_provenance(self):
        from literaki_slownik.decisions import persisted_assessments
        from literaki_slownik.policy import VERSION
        run = self.pinned_run(['ou', 'up'])
        with connect(run / 'build.sqlite', readonly=True) as db:
            rows = persisted_assessments(db, 'up', 'standard')
        interj, = [r for r in rows if r['expanded_tag'] == 'interj']
        self.assertEqual(interj['policy_version'], VERSION)
        self.assertNotEqual(VERSION, 'approved-conditions-v30')
        self.assertEqual(interj['assessment']['membership']['status'], 'reject')
        check, = [c for c in interj['assessment']['language']['checks'] if c['rule_id'] == RULE]
        self.assertEqual(check['status'], 'reject')
        self.assertEqual(check['decision_version'], 'standard-exclusions-test')
        self.assertEqual(check['reason'], 'brak polskiego znaczenia')
        self.assertIn('config/generator/standard-exclusions.json', check['evidence'])
        self.assertIn('https://github.com/robmar-net/literaki-slownik/issues/15', check['evidence'])
        rejected = [c for c in interj['assessment']['language']['checks'] if c['status'] != 'accept']
        self.assertEqual([c['rule_id'] for c in rejected], [RULE])

    def test_refuses_entry_matching_nothing(self):
        # Inny import: wpis wskazuje wiersz, którego nie ma, więc build przerywa przed oceną.
        sgjp = BUILD_SGJP.replace('UP\tUP\tsubst:sg:nom:f\tnazwa_organizacji\t\n', '')
        with self.assertRaises(GeneratorError):
            self.pinned_run(['up'], name='missing', sgjp=sgjp)
        self.failed(self.root / 'missing')

    def test_refuses_entry_on_analysis_rejected_otherwise(self):
        for name in ('UP', 'zamku'):  # wielka litera; dawność
            with self.subTest(name=name), self.assertRaises(GeneratorError):
                self.pinned_run([name], name=f'drift-{name}')
            self.failed(self.root / f'drift-{name}')

    def test_refuses_when_form_stays_in_standard(self):
        # Drugi rekord tej samej formy dopuściłby ją dalej; wykluczenie nie może być ciche.
        sgjp = BUILD_SGJP + 'up\tup:S2\tinterj\t\t\n'
        with self.assertRaises(GeneratorError):
            self.pinned_run(['up'], name='stays', sgjp=sgjp)
        self.failed(self.root / 'stays')

    def test_every_entry_must_be_used_exactly_once(self):
        from literaki_slownik.decisions import materialize_assessments
        run = self.pinned_run(['up'])
        manifest = json.loads(self.manifest.read_text())
        path = self.root / manifest['configurations'][sex.CONFIG_KEY]['path']
        loaded = sex.load(path, source_hashes={'synthetic': manifest['artifacts'][0]['sha256']})
        with connect(run / 'build.sqlite') as db:
            self.assertEqual(materialize_assessments(db, standard_exclusions=loaded)['standard_exclusions']['matched'], 1)
            extra = dict(loaded, analyses={**loaded['analyses'], 'f' * 64: next(iter(loaded['analyses'].values()))})
            with self.assertRaises(GeneratorError):
                materialize_assessments(db, standard_exclusions=extra)

    def test_explain_shows_rule_and_run_pin(self):
        from literaki_slownik.explain import explain, format_explanation
        run = self.pinned_run(['ou', 'up'])
        value = explain(run, 'up', 'standard')
        basis = value['assessment_basis']['standard_exclusions']
        self.assertEqual(basis['status'], 'pinned')
        self.assertEqual(basis['sha256'], json.loads(self.manifest.read_text())['configurations'][sex.CONFIG_KEY]['sha256'])
        interj, = [a for a in value['analyses'] if a['raw_tag'] == 'interj']
        expanded, = interj['expanded_assessments']
        self.assertTrue(expanded['standard_exclusion'])
        self.assertEqual(expanded['assessment']['membership']['standard']['status'], 'reject')
        self.assertEqual(value['source_aggregation']['status'], 'reject')
        text = format_explanation(value)
        self.assertIn(RULE, text)
        self.assertIn('#15', text)
        broad = explain(run, 'up', 'broad')
        self.assertEqual(broad['source_aggregation']['status'], 'accept')
        self.assertEqual(explain(run, 'au', 'standard')['source_aggregation']['status'], 'accept')
        old = explain(self.old, 'up', 'standard')
        self.assertEqual(old['assessment_basis']['standard_exclusions']['status'], 'not_pinned_in_run')
        self.assertIn('bez przypiętych wykluczeń STANDARD', format_explanation(old))


if __name__ == '__main__':
    unittest.main()
