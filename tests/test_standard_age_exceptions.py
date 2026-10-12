"""Walidator zatwierdzonych wyjątków dawności STANDARD (#4, G0)."""
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
from literaki_slownik import standard_age_exceptions as sae
from tests.helpers import fixture_manifest, rewrite

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = 'a' * 64
SOURCE = {'source_id': 'synthetic', 'first_source_row': 7, 'original': 'admiratora',
          'lemma_id': 'admirator', 'raw_tag': 'subst:sg:gen.acc:m1',
          'names': 'nazwa_pospolita', 'qualifiers': 'przest.'}
COMPONENT = {'source_id': 'synthetic', 'first_source_row': 9, 'original': 'dwoicie',
             'lemma_id': 'dwoić', 'raw_tag': 'impt:pl:sec:imperf', 'names': '', 'qualifiers': 'przest.'}
CANDIDATE = {'components': [{'interpretation': COMPONENT, 'kind': 'source_interpretation'},
                            {'kind': 'grammatical_particle', 'original': 'ż', 'rule_id': 'impt-single-particle-v1'}],
             'evidence': ['docs/generator/konstrukcje.md'], 'expanded_tag': 'impt:pl:sec:imperf',
             'lemma_id': 'dwoić', 'names': '', 'original': 'dwoicież', 'qualifiers': 'przest.',
             'rule_id': 'impt-single-particle-v1', 'status': 'candidate_not_qualified'}
CANDIDATE_KEY = hashlib.sha256(dumps(CANDIDATE).encode()).hexdigest()


def family(lemma, **extra):
    return {'family': lemma, 'lemma_id': lemma, 'status': 'propose', 'scope': 'współczesna odmiana',
            'meaning_note': 'opis', 'confidence': 'medium', 'reader_article_ids': [1],
            'kwjp_documents': ['136007', '136095'],
            'evidence': [{'kind': 'kwjp_review', 'word': lemma, 'url': 'https://kwjp.pl/x'}], **extra}


def source_entry(tag):
    return {'kind': 'source', 'family': 'admirator', 'proof': 'reader_exact', 'reader_word': 'admiratora',
            **SOURCE, 'tag': tag}


def construction_entry():
    return {'kind': 'construction', 'family': 'dwoić', 'proof': 'existing_qualified_construction',
            'candidate_key': CANDIDATE_KEY, 'rule_id': 'impt-single-particle-v1', 'original': 'dwoicież',
            'lemma_id': 'dwoić', 'tag': 'impt:pl:sec:imperf', 'names': '', 'qualifiers': 'przest.',
            'components': [{'source_id': 'synthetic', 'first_source_row': 9, 'original': 'dwoicie',
                            'raw_tag': 'impt:pl:sec:imperf'}]}


def config():
    return {
        'schema_version': 1, 'decision_version': 'standard-age-exceptions-test',
        'description': 'fikstura', 'overrides_rule': 'linguistic-historical-form-v1',
        'source_snapshot': {'run': 'fixture', 'database_sha256': 'b' * 64, 'policy_version': 'test',
                            'matches_per_analysis': {'1': 3}},
        'sources': {'synthetic': SOURCE_SHA},
        'provenance': {'research_task': 'fixture', 'approval': 'fixture',
                       'inputs': {'proposal-proof.json': 'c' * 64}},
        'expected_counts': {'words': 2, 'analyses': 3, 'source_analyses': 2,
                            'construction_analyses': 1, 'families': 2},
        'families': [family('admirator'), family('dwoić')],
        'cases': [{'word': 'admiratora', 'analyses': [source_entry('subst:sg:acc:m1'), source_entry('subst:sg:gen:m1')]},
                  {'word': 'dwoicież', 'analyses': [construction_entry()]}],
    }


def source_key(tag):
    return hashlib.sha256(dumps(['source', SOURCE, tag]).encode()).hexdigest()


def fixture_db(path, *, with_analyses=True):
    with connect(path, create=True) as db:
        db.execute("insert into source_artifact values ('synthetic','sgjp_tab',?)", (json.dumps({'sha256': SOURCE_SHA}),))
        for row, item in ((7, SOURCE), (9, COMPONENT)):
            db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)',
                       ('synthetic', row, item['original'], item['lemma_id'], item['raw_tag'], item['names'], item['qualifiers']))
        for iid, item in ((1, SOURCE), (2, COMPONENT)):
            db.execute('insert into lexeme values (?,?,?,?)', (iid, 'synthetic', item['lemma_id'], item['lemma_id']))
            db.execute('insert into surface_form values (?,?,?,?,?)',
                       (iid, item['original'], item['original'], item['original'], len(item['original'])))
            db.execute('insert into interpretation values (?,?,?,?,?,?,?,?)',
                       (iid, 'synthetic', item['first_source_row'], iid, iid, item['raw_tag'], item['names'], item['qualifiers']))
        db.execute('insert into derivation_candidate values (?,?,?,?,?,?,?,?,?)',
                   (CANDIDATE_KEY, CANDIDATE['rule_id'], 'dwoicież', 'dwoicież', 'dwoić', CANDIDATE['expanded_tag'],
                    '', 'przest.', dumps(CANDIDATE)))
        db.execute("insert into derivation_component values (?,0,'source_interpretation','synthetic',9)", (CANDIDATE_KEY,))
        db.execute("insert into derivation_component values (?,1,'grammatical_particle',null,null)", (CANDIDATE_KEY,))
        if with_analyses:
            for tag in ('subst:sg:gen:m1', 'subst:sg:acc:m1'):
                db.execute('insert into analysis values (?,?,?,?,?,?,?,?,?)',
                           (source_key(tag), 1, None, tag, 'admiratora', 'admiratora', 'admiratora', 10, 'test'))
            db.execute('insert into analysis values (?,?,?,?,?,?,?,?,?)',
                       (hashlib.sha256(dumps(['construction', CANDIDATE_KEY]).encode()).hexdigest(), None, CANDIDATE_KEY,
                        'impt:pl:sec:imperf', 'dwoicież', 'dwoicież', 'dwoicież', 8, 'test'))


class StandardAgeExceptionsTests(unittest.TestCase):
    def load(self, value, hashes=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'exceptions.json'
            path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
            return sae.load(path, source_hashes=hashes or {'synthetic': SOURCE_SHA})

    def refused(self, value, hashes=None):
        with self.assertRaises(GeneratorError):
            self.load(value, hashes)

    def test_valid_config_maps_exact_analysis_keys(self):
        loaded = self.load(config())
        construction = hashlib.sha256(dumps(['construction', CANDIDATE_KEY]).encode()).hexdigest()
        self.assertEqual(set(loaded['analyses']),
                         {source_key('subst:sg:gen:m1'), source_key('subst:sg:acc:m1'), construction})
        self.assertEqual(loaded['analyses'][construction]['word'], 'dwoicież')
        self.assertEqual(loaded['counts'], config()['expected_counts'])
        with tempfile.TemporaryDirectory() as directory:
            fixture_db(Path(directory) / 'build.sqlite')
            with connect(Path(directory) / 'build.sqlite', readonly=True) as db:
                self.assertEqual(sae.check_database(db, loaded)['matched_analyses'], 3)

    def test_wrong_source_hash_is_refused(self):
        self.refused(config(), {'synthetic': 'd' * 64})
        value = config()
        value['sources']['synthetic'] = 'd' * 64
        self.refused(value)
        with tempfile.TemporaryDirectory() as directory:
            loaded = self.load(config())
            fixture_db(Path(directory) / 'build.sqlite')
            with connect(Path(directory) / 'build.sqlite') as db:
                db.execute("update source_artifact set metadata=? where source_id='synthetic'", (json.dumps({'sha256': 'e' * 64}),))
            with connect(Path(directory) / 'build.sqlite', readonly=True) as db, self.assertRaises(GeneratorError):
                sae.check_database(db, loaded)

    def test_duplicates_and_unknown_keys_are_refused(self):
        value = config()
        value['cases'][0]['analyses'].append(deepcopy(value['cases'][0]['analyses'][1]))
        self.refused(value)
        value = config()
        value['cases'].append(deepcopy(value['cases'][1]))
        self.refused(value)
        value = config()
        value['families'].append(deepcopy(value['families'][0]))
        self.refused(value)
        for key in ('research_only', 'implementation_approved'):
            value = config()
            value[key] = False
            self.refused(value)
        value = config()
        value['expected_counts']['analyses'] = 4
        self.refused(value)
        value = config()
        value['cases'].reverse()
        self.refused(value)

    def test_missing_record_is_refused(self):
        loaded = self.load(config())
        for drop in ('interpretation', 'analysis'):
            with self.subTest(drop=drop), tempfile.TemporaryDirectory() as directory:
                fixture_db(Path(directory) / 'build.sqlite')
                with connect(Path(directory) / 'build.sqlite') as db:
                    if drop == 'interpretation':
                        db.execute('pragma foreign_keys=off')
                        db.execute('update interpretation set first_row=8 where id=1')
                    else:
                        db.execute('delete from analysis where analysis_key=?', (source_key('subst:sg:gen:m1'),))
                with connect(Path(directory) / 'build.sqlite', readonly=True) as db, self.assertRaises(GeneratorError):
                    sae.check_database(db, loaded)
        with tempfile.TemporaryDirectory() as directory:
            # Przed oceną (pusta tabela analysis) sprawdzamy same rekordy importu.
            fixture_db(Path(directory) / 'build.sqlite', with_analyses=False)
            with connect(Path(directory) / 'build.sqlite', readonly=True) as db:
                self.assertEqual(sae.check_database(db, loaded, analyses=False)['matched_analyses'], 3)
                with self.assertRaises(GeneratorError):
                    sae.check_database(db, loaded)

    def test_wrong_tag_foreign_lemma_and_out_of_scope_form(self):
        mutations = {
            'tag spoza rozwinięcia': lambda v: v['cases'][0]['analyses'][0].update(tag='subst:sg:dat:m1'),
            'obcy lemat': lambda v: v['cases'][0]['analyses'][0].update(family='dwoić'),
            'nieznana rodzina': lambda v: v['cases'][0]['analyses'][0].update(family='hold'),
            'inna forma gry': lambda v: v['cases'][0]['analyses'][0].update(original='admiratorowi'),
            'zakres rodziny': lambda v: v['families'][0].update(status='limited', forms=['admirator']),
            'wykluczona część mowy': lambda v: v['families'][0].update(exclude_pos=['subst']),
            'nieznormalizowany napis': lambda v: v['cases'][0].update(word='Admiratora'),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                value = config()
                mutate(value)
                self.refused(value)

    def test_construction_requires_its_exact_key(self):
        for mutate in (lambda e: e.pop('candidate_key'), lambda e: e.update(candidate_key='x'),
                       lambda e: e.update(components=[])):
            value = config()
            mutate(value['cases'][1]['analyses'][0])
            self.refused(value)
        value = config()
        value['cases'][1]['analyses'][0]['candidate_key'] = 'f' * 64
        loaded = self.load(value)
        with tempfile.TemporaryDirectory() as directory:
            fixture_db(Path(directory) / 'build.sqlite')
            with connect(Path(directory) / 'build.sqlite', readonly=True) as db, self.assertRaises(GeneratorError):
                sae.check_database(db, loaded)

    def test_recomputed_keys_are_missing_only_in_an_older_snapshot(self):
        def recomputed(analyses=1, rule='impt-single-particle-v2'):
            value = config()
            value['source_snapshot']['recomputed_constructions'] = {'impt-single-particle-v2': {
                'replaces': 'impt-single-particle-v1', 'analyses': analyses, 'note': 'klucz z kodu nowej reguły'}}
            value['cases'][1]['analyses'][0].update(rule_id=rule, candidate_key='f' * 64)
            return value
        self.refused(recomputed(analyses=2))
        self.refused(recomputed(rule='impt-single-particle-v1'))
        loaded = self.load(recomputed())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'build.sqlite'
            fixture_db(path)
            with connect(path, readonly=True) as db:
                with self.assertRaises(GeneratorError):
                    sae.check_database(db, loaded)
                result = sae.check_database(db, loaded, allow_missing_recomputed=True)
                self.assertEqual((result['matched_analyses'], result['expected_missing_recomputed']),
                                 (2, {'impt-single-particle-v2': 1}))
            # Baza, która ma już kandydatów nowej reguły, nie może zgubić klucza.
            with connect(path) as db:
                db.execute("insert into derivation_candidate values (?,'impt-single-particle-v2','x','x','x','impt','','','{}')",
                           ('e' * 64,))
            with connect(path, readonly=True) as db, self.assertRaises(GeneratorError):
                sae.check_database(db, loaded, allow_missing_recomputed=True)

    def test_manifest_pin_detects_unhashed_change(self):
        with tempfile.TemporaryDirectory() as directory:
            path, manifest = fixture_manifest(directory)
            value = config()
            value['sources'] = {'synthetic': manifest['artifacts'][0]['sha256']}
            target = Path(directory) / 'standard-age-exceptions.json'
            target.write_text(sae.render(value), encoding='utf-8')
            manifest['configurations'][sae.CONFIG_KEY] = {
                'path': target.name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
            rewrite(path, manifest)
            self.assertEqual(len(sae.from_manifest(path)['analyses']), 3)
            script = [sys.executable, str(ROOT / 'scripts/check_standard_age_exceptions.py'), '--manifest', str(path)]
            self.assertEqual(subprocess.run(script, capture_output=True, cwd=ROOT).returncode, 0)
            target.write_text(sae.render(value).replace('"opis"', '"opis zmieniony"'), encoding='utf-8')
            with self.assertRaises(GeneratorError):
                sae.from_manifest(path)
            self.assertNotEqual(subprocess.run(script, capture_output=True, cwd=ROOT).returncode, 0)

    def test_render_is_deterministic_and_round_trips(self):
        text = sae.render(config())
        self.assertEqual(json.loads(text), config())
        self.assertEqual(sae.render(json.loads(text)), text)

    def test_repository_config_is_pinned_and_complete(self):
        loaded = sae.from_manifest(ROOT / 'config/generator/sources.json')
        self.assertEqual(loaded['counts'], {'words': 2382, 'analyses': 7192, 'source_analyses': 7060,
                                            'construction_analyses': 132, 'families': 110})
        text = (ROOT / 'config/generator/standard-age-exceptions.json').read_text(encoding='utf-8')
        self.assertNotIn('research_only', text)
        self.assertNotIn('implementation_approved', text)
        self.assertEqual(sae.render(json.loads(text)), text)


# G1: wyjątki w fazie decisions. Fikstura: jeden dopuszczony zapis, homonim, dawny wariant,
# konstrukcja z istniejącego składnika i analiza z inną odmową (wielka litera).
BUILD_SGJP = ('#</COPYRIGHT>\n'
              'admiratora\tadmirator\tsubst:sg:gen.acc:m1\tnazwa_pospolita\tprzest.\n'
              'admiratorowie\tadmirator\tsubst:pl:nom:m1\tnazwa_pospolita\tdaw.\n'
              'zamku\tzamek:S1\tsubst:sg:gen:m3\tnazwa_pospolita\tdaw.\n'
              'zamku\tzamek:S2\tsubst:sg:loc:m3\tnazwa_pospolita\tdaw.\n'
              'dwoicie\tdwoić\timpt:pl:sec:imperf\t\tprzest.\n'
              'kot\tkot\tsubst:sg:nom:m2\t\t\n'
              'Kmieciu\tKmieć\tsubst:sg:voc:m1\tnazwa_pospolita\tdaw.\n')
EXCEPTION_RULE = 'linguistic-standard-age-exception-v1'


def build_source(db, original, lemma, tag, kind='source'):
    """Pozycja JSON-a z dokładnego rekordu przebiegu (jak generator danych badania)."""
    row = db.execute('''select i.source_id,i.first_row,f.original,l.lemma_id,i.tag,i.names,i.qualifiers
        from interpretation i join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id
        where f.original=? and l.lemma_id=?''', (original, lemma)).fetchone()
    record = dict(zip(sae.RECORD, row))
    return {'kind': 'source', 'family': lemma, 'proof': 'reader_exact', 'reader_word': original, **record, 'tag': tag}


def build_construction(db, original):
    ckey, rule, lemma, tag, names, qualifiers, payload = db.execute('''select candidate_key,rule_id,lemma_id,
        expanded_tag,names,qualifiers,payload from derivation_candidate where original=?''', (original,)).fetchone()
    parts = [p['interpretation'] for p in json.loads(payload)['components'] if p['kind'] == 'source_interpretation']
    return {'kind': 'construction', 'family': lemma, 'proof': 'existing_qualified_construction',
            'candidate_key': ckey, 'rule_id': rule, 'original': original, 'lemma_id': lemma, 'tag': tag,
            'names': names, 'qualifiers': qualifiers, 'components': [{k: p[k] for k in sae.COMPONENT} for p in parts]}


def build_config(source_sha, entries):
    cases = {}
    for entry in entries:
        cases.setdefault(sae.game_key(entry['original']), []).append(entry)
    families = sorted({e['family'] for e in entries})
    value = config()
    value.update(sources={'synthetic': source_sha}, families=[family(f) for f in families],
                 cases=[{'word': w, 'analyses': sorted(es, key=sae.order)} for w, es in sorted(cases.items())],
                 expected_counts={'words': len(cases), 'analyses': len(entries),
                                  'source_analyses': sum(e['kind'] == 'source' for e in entries),
                                  'construction_analyses': sum(e['kind'] == 'construction' for e in entries),
                                  'families': len(families)})
    return value


class StandardAgeExceptionBuildTests(unittest.TestCase):
    """Przypięty JSON uchyla tylko odmowę dawności wskazanej analizy STANDARD."""

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
            self.entries = {'admiratora': build_source(db, 'admiratora', 'admirator', 'subst:sg:gen:m1'),
                            'zamku': build_source(db, 'zamku', 'zamek:S1', 'subst:sg:gen:m3'),
                            'dwoicież': build_construction(db, 'dwoicież'),
                            'kot': build_source(db, 'kot', 'kot', 'subst:sg:nom:m2'),
                            'kmieciu': build_source(db, 'Kmieciu', 'Kmieć', 'subst:sg:voc:m1')}

    def tearDown(self):
        self.temp.cleanup()

    def pinned_run(self, words, name='new'):
        manifest = json.loads(self.manifest.read_text(encoding='utf-8'))
        target = self.root / f'{name}-exceptions.json'
        target.write_text(sae.render(build_config(manifest['artifacts'][0]['sha256'],
                                                  [self.entries[w] for w in words])), encoding='utf-8')
        manifest['configurations'][sae.CONFIG_KEY] = {'path': target.name,
                                                      'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
        rewrite(self.manifest, manifest)
        run = self.root / name
        self.build(self.manifest, run)
        return run

    def statuses(self, run, variant):
        with connect(run / 'build.sqlite', readonly=True) as db:
            return {(o, t): s for o, t, s in db.execute('''select a.original,a.expanded_tag,d.membership_status
                from analysis a join variant_decision d using(analysis_key) where d.variant=?''', (variant,))}

    def test_exact_analyses_enter_standard_and_others_keep_age_reject(self):
        run = self.pinned_run(['admiratora', 'zamku', 'dwoicież'])
        self.assertEqual((run / 'lists/standard.txt').read_text(), 'admiratora\ndwoicież\nkot\nzamku\n')
        self.assertEqual((self.old / 'lists/standard.txt').read_text(), 'kot\n')
        standard = self.statuses(run, 'standard')
        self.assertEqual(standard[('admiratora', 'subst:sg:gen:m1')], 'accept')
        self.assertEqual(standard[('admiratora', 'subst:sg:acc:m1')], 'reject')  # inna analiza tego zapisu
        self.assertEqual(standard[('zamku', 'subst:sg:gen:m3')], 'accept')
        self.assertEqual(standard[('zamku', 'subst:sg:loc:m3')], 'reject')  # inny homonim
        self.assertEqual(standard[('admiratorowie', 'subst:pl:nom:m1')], 'reject')  # dawny wariant formy
        self.assertEqual(standard[('dwoicie', 'impt:pl:sec:imperf')], 'reject')  # składnik bez wyjątku
        self.assertEqual(standard[('dwoicież', 'impt:pl:sec:imperf')], 'accept')
        report = json.loads((run / 'reports/decisions.json').read_text())['standard_age_exceptions']
        self.assertEqual({k: report[k] for k in ('entries', 'matched', 'unused', 'words', 'source_analyses',
                                                 'construction_analyses')},
                         {'entries': 3, 'matched': 3, 'unused': 0, 'words': 3, 'source_analyses': 2,
                          'construction_analyses': 1})
        manifest = json.loads(self.manifest.read_text())
        self.assertEqual(report['sha256'], manifest['configurations'][sae.CONFIG_KEY]['sha256'])
        self.assertEqual(report['rule_id'], EXCEPTION_RULE)
        self.assertNotIn('standard_age_exceptions', json.loads((self.old / 'reports/decisions.json').read_text()))

    def test_persisted_payload_names_rule_decision_and_family_proof(self):
        from literaki_slownik.decisions import persisted_assessments
        from literaki_slownik.policy import VERSION
        run = self.pinned_run(['admiratora'])
        with connect(run / 'build.sqlite', readonly=True) as db:
            rows = {r['expanded_tag']: r for r in persisted_assessments(db, 'admiratora', 'standard')}
        accepted = rows['subst:sg:gen:m1']
        self.assertEqual(accepted['policy_version'], VERSION)
        self.assertNotEqual(VERSION, 'approved-conditions-v29')
        check, = [c for c in accepted['assessment']['language']['checks'] if c['rule_id'] == EXCEPTION_RULE]
        self.assertEqual(check['status'], 'accept')
        self.assertEqual(check['replaces'], 'linguistic-historical-form-v1')
        self.assertEqual(check['source_label'], 'przest.')
        self.assertEqual(check['decision_version'], 'standard-age-exceptions-test')
        self.assertEqual(check['family'], 'admirator')
        self.assertEqual(check['proof'], 'reader_exact')
        self.assertEqual(check['family_evidence'], family('admirator')['evidence'])
        self.assertIn('config/generator/standard-age-exceptions.json', check['evidence'])
        self.assertNotIn('linguistic-historical-form-v1',
                         [c['rule_id'] for c in accepted['assessment']['language']['checks']])
        rejected = rows['subst:sg:acc:m1']['assessment']['language']['checks']
        self.assertIn('linguistic-historical-form-v1', [c['rule_id'] for c in rejected])
        self.assertNotIn(EXCEPTION_RULE, [c['rule_id'] for c in rejected])

    def test_broad_is_unchanged(self):
        run = self.pinned_run(['admiratora', 'zamku', 'dwoicież'])
        self.assertEqual((run / 'lists/broad.txt').read_bytes(), (self.old / 'lists/broad.txt').read_bytes())
        query = '''select a.analysis_key,d.assessment_key from analysis a join variant_decision d using(analysis_key)
            where d.variant='broad' order by 1'''
        with connect(run / 'build.sqlite', readonly=True) as new, connect(self.old / 'build.sqlite', readonly=True) as old:
            self.assertEqual(new.execute(query).fetchall(), old.execute(query).fetchall())

    def test_other_rejection_stays_and_build_refuses_drift(self):
        from literaki_slownik.decisions import assess_diagnostic
        from literaki_slownik.standard_age_exceptions import decision_for
        entry = {**self.entries['kmieciu'], 'word': 'kmieciu'}
        loaded = {'decision_version': 'test', 'families': {'Kmieć': family('Kmieć')}}
        source = {k: entry[k] for k in sae.RECORD}
        assessed = assess_diagnostic('Kmieciu', 'daw.', source_analyses=[dict(source, raw_tag=entry['tag'])],
                                     age_exception=decision_for(loaded, entry))
        self.assertIn(EXCEPTION_RULE, [c['rule_id'] for c in assessed['language']['standard']['checks']])
        self.assertEqual(assessed['membership']['standard']['status'], 'reject')  # wielka litera zostaje
        for word in ('kmieciu', 'kot'):  # inna odmowa; brak odmowy dawności
            with self.subTest(word=word), self.assertRaises(GeneratorError):
                self.pinned_run([word], name=f'drift-{word}')
            stage = json.loads((self.root / f'drift-{word}' / 'manifest.json').read_text())['stages']['decisions']
            self.assertEqual(stage['status'], 'failed')
            self.assertFalse((self.root / f'drift-{word}' / 'lists/standard.txt').exists())

    def test_every_entry_must_be_used_exactly_once(self):
        from literaki_slownik.decisions import materialize_assessments
        run = self.pinned_run(['admiratora'])
        manifest = json.loads(self.manifest.read_text())
        path = self.root / manifest['configurations'][sae.CONFIG_KEY]['path']
        loaded = sae.load(path, source_hashes={'synthetic': manifest['artifacts'][0]['sha256']})
        with connect(run / 'build.sqlite') as db:
            self.assertEqual(materialize_assessments(db, age_exceptions=loaded)['standard_age_exceptions']['matched'], 1)
            extra = dict(loaded, analyses={**loaded['analyses'], 'f' * 64: next(iter(loaded['analyses'].values()))})
            with self.assertRaises(GeneratorError):
                materialize_assessments(db, age_exceptions=extra)

    def test_explain_reads_run_pin_and_marks_old_run_basis(self):
        from literaki_slownik.explain import explain, format_explanation
        run = self.pinned_run(['admiratora', 'dwoicież'])
        value = explain(run, 'admiratora')
        basis = value['assessment_basis']
        self.assertEqual(basis['standard_age_exceptions']['status'], 'pinned')
        self.assertEqual(basis['standard_age_exceptions']['sha256'],
                         json.loads(self.manifest.read_text())['configurations'][sae.CONFIG_KEY]['sha256'])
        self.assertTrue(basis['diagnostic_matches_persisted_policy'])
        analysis, = value['analyses']
        live = {e['expanded_tag']: e['assessment']['membership']['standard']['status'] for e in analysis['expanded_assessments']}
        stored = {r['expanded_tag']: r['assessment']['membership']['status'] for r in value['persisted_analyses']}
        self.assertEqual(live, stored)
        self.assertEqual(live, {'subst:sg:gen:m1': 'accept', 'subst:sg:acc:m1': 'reject'})
        self.assertEqual(value['source_aggregation']['status'], 'accept')
        candidate, = explain(run, 'dwoicież')['derivations']
        self.assertEqual(candidate['assessment']['membership']['standard']['status'], 'accept')
        self.assertIn('wyjątek dawności', format_explanation(value).lower())
        old = explain(self.old, 'admiratora')
        self.assertEqual(old['assessment_basis']['standard_age_exceptions']['status'], 'not_pinned_in_run')
        self.assertEqual({r['assessment']['membership']['status'] for r in old['persisted_analyses']}, {'reject'})
        self.assertNotIn('expanded_assessments', old['analyses'][0])
        self.assertIn('bez przypiętych wyjątków dawności', format_explanation(old))
        # Ocena zapisana starszą polityką: explain nie podaje przeliczenia jako historycznej podstawy.
        with connect(self.old / 'build.sqlite') as db:
            db.execute("update analysis set policy_version='approved-conditions-v29'")
        old = explain(self.old, 'admiratora')
        self.assertEqual(old['assessment_basis']['persisted_policy_versions'], ['approved-conditions-v29'])
        self.assertFalse(old['assessment_basis']['diagnostic_matches_persisted_policy'])
        self.assertIn('przeliczenie bieżącym kodem', format_explanation(old))


if __name__ == '__main__':
    unittest.main()
