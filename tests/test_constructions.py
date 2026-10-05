"""Konstrukcje zachowują źródłową interpretację, bez kwalifikacji do gry."""
import unittest

from literaki_slownik.constructions import impt_particle_candidates, by_aglt_candidates
from literaki_slownik.inputs import GeneratorError


def source(form='daj', tag='impt:sg:sec:perf', qualifiers=''):
    return {'source_id': 'SGJP-fixture', 'first_source_row': 12, 'original': form,
            'lemma_id': 'dać:fixture', 'raw_tag': tag, 'names': '', 'qualifiers': qualifiers}


class ConstructionTests(unittest.TestCase):
    def test_by_aglt_only_four_nonvocalic_personal_endings(self):
        operator = source('by', 'part')
        operator['lemma_id'] = 'by:T'
        for suffix, number, person, expected in [('m', 'sg', 'pri', 'bym'), ('ś', 'sg', 'sec', 'byś'),
                                                  ('śmy', 'pl', 'pri', 'byśmy'), ('ście', 'pl', 'sec', 'byście')]:
            aglt = source(suffix, f'aglt:{number}:{person}:imperf:nwok')
            result, = by_aglt_candidates(operator, aglt)
            self.assertEqual(result['original'], expected)
            self.assertEqual([item['interpretation'] for item in result['components']], [operator, aglt])
            self.assertEqual(result['status'], 'candidate_not_qualified')

    def test_by_aglt_preserves_all_component_labels_without_sense_cross_product(self):
        operator = source('by', 'comp', 'rzad.')
        aglt = source('m', 'aglt:sg:pri:imperf:nwok', 'niezal.|rzad.')
        result, = by_aglt_candidates(operator, aglt)
        self.assertEqual(result['qualifiers'], 'niezal.|rzad.')
        self.assertEqual(result['components'][0]['interpretation']['qualifiers'], 'rzad.')
        self.assertEqual(result['components'][1]['interpretation']['qualifiers'], 'niezal.|rzad.')

    def test_by_aglt_wrong_hosts_and_vocalic_endings_not_generated(self):
        self.assertEqual(by_aglt_candidates(source('niby', 'part'), source('m', 'aglt:sg:pri:imperf:nwok')), [])
        self.assertEqual(by_aglt_candidates(source('by', 'subst:sg:nom:m3'), source('m', 'aglt:sg:pri:imperf:nwok')), [])
        for suffix, tag in [('em', 'aglt:sg:pri:imperf:wok'), ('eśmy', 'aglt:pl:pri:imperf:wok'),
                            ('ś', 'aglt:sg:pri:imperf:nwok'), ('m', 'aglt:sg:pri:perf:nwok')]:
            with self.subTest(suffix=suffix, tag=tag), self.assertRaises(GeneratorError):
                by_aglt_candidates(source('by', 'part'), source(suffix, tag))

    def test_single_particle_correct_sg_and_pl_forms(self):
        for form, tag, result in [('daj', 'impt:sg:sec:perf', 'dajże'),
                                  ('czytaj', 'impt:sg:sec:imperf', 'czytajże'),
                                  ('dajcie', 'impt:pl:sec:perf', 'dajcież'),
                                  ('dajmy', 'impt:pl:pri:perf', 'dajmyż')]:
            candidate, = impt_particle_candidates(source(form, tag))
            self.assertEqual(candidate['original'], result)
            self.assertEqual(candidate['status'], 'candidate_not_qualified')
            self.assertEqual(candidate['components'][0]['interpretation'], source(form, tag))
            self.assertEqual(len(candidate['components']), 2)

    def test_source_qualifiers_case_and_full_homonym_id_preserved(self):
        original = source('Daj', qualifiers='daw.,niezal.')
        result, = impt_particle_candidates(original)
        self.assertEqual(result['original'], 'Dajże')
        self.assertEqual(result['qualifiers'], 'daw.,niezal.')
        self.assertEqual(result['names'], '')
        self.assertEqual(result['lemma_id'], 'dać:fixture')
        self.assertEqual(original, source('Daj', qualifiers='daw.,niezal.'))

    def test_not_suffix_guessing_or_double_particle(self):
        self.assertEqual(impt_particle_candidates(source('czytajże', 'subst:sg:nom:m3')), [])
        result, = impt_particle_candidates(source('żeż', 'impt:sg:sec:perf'))
        self.assertEqual(result['original'], 'żeżże')  # rozkaźnik żec, nie analiza podwojonej partykuły
        self.assertNotEqual(result['original'], 'żeżżeż')

    def test_expanded_tags_keep_raw_source_and_separate_derivations(self):
        raw = source('daj', 'impt:sg:sec:perf.imperf')
        result = impt_particle_candidates(raw)
        self.assertEqual(len(result), 2)
        self.assertEqual({item['expanded_tag'] for item in result}, {'impt:sg:sec:perf', 'impt:sg:sec:imperf'})
        self.assertTrue(all(item['components'][0]['interpretation']['raw_tag'] == raw['raw_tag'] for item in result))

    def test_invalid_source_and_uncovered_impt_class_are_errors(self):
        for record in [source('', 'impt:sg:sec:perf'), source('dajmy', 'impt:sg:sec:perf'),
                       source('daj', 'impt:sg:pri:perf'), source('daj', 'impt:sg:sec:new'),
                       {'original': 'daj', 'raw_tag': 'impt:sg:sec:perf'}]:
            with self.subTest(record=record), self.assertRaises(GeneratorError):
                impt_particle_candidates(record)


class PersistedConstructionTests(unittest.TestCase):
    def database(self, directory):
        from pathlib import Path
        from literaki_slownik.database import connect
        return connect(Path(directory) / 'db.sqlite', create=True)

    def insert_sources(self, db):
        from literaki_slownik.canonical import dumps
        db.execute('insert into source_artifact values (?,?,?)', ('fixture', 'sgjp_tab', dumps({'origin':'synthetic'})))
        rows = [('daj', 'dać:S1', 'impt:sg:sec:perf', '', 'niepopr.'),
                ('daj', 'dać:S2', 'impt:sg:sec:perf', '', ''),
                ('dajże', 'dajże:S3', 'subst:sg:nom:m3', '', ''),
                ('by', 'by:T', 'part', '', ''),
                ('m', 'być:A', 'aglt:sg:pri:imperf:nwok', '', ''),
                ('em', 'być:A', 'aglt:sg:pri:imperf:wok', '', '')]
        for number, (form, lemma, tag, names, qualifiers) in enumerate(rows, 1):
            db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)', ('fixture', number, form, lemma, tag, names, qualifiers))
            db.execute('insert or ignore into lexeme(source_id,lemma_id,lemma_base) values (?,?,?)', ('fixture', lemma, lemma.split(':')[0]))
            db.execute('insert or ignore into surface_form(original,nfc,game_key,length) values (?,?,?,?)', (form, form, form.lower(), len(form)))
            fid = db.execute('select id from surface_form where original=?', (form,)).fetchone()[0]
            lid = db.execute('select id from lexeme where lemma_id=?', (lemma,)).fetchone()[0]
            db.execute('insert into interpretation(source_id,first_row,form_id,lexeme_id,tag,names,qualifiers) values (?,?,?,?,?,?,?)',
                       ('fixture', number, fid, lid, tag, names, qualifiers))
        db.commit()

    def test_persistence_keeps_alternative_sources_components_and_direct_form(self):
        import json
        import tempfile
        from literaki_slownik.constructions import materialize_confirmed_candidates
        with tempfile.TemporaryDirectory() as directory, self.database(directory) as db:
            self.insert_sources(db)
            report = materialize_confirmed_candidates(db, batch_size=1)
            self.assertEqual(report['candidates'], 3)  # dwa homonimy daj i by+m; wpis dajże zachowany
            self.assertEqual(report['scope'], 'confirmed_subset_candidates_not_full_constructions')
            self.assertTrue(report['full_constructions_pending'])
            candidates = [json.loads(row[0]) for row in db.execute('select payload from derivation_candidate where original=?', ('dajże',))]
            self.assertEqual({c['lemma_id'] for c in candidates}, {'dać:S1','dać:S2'})
            self.assertEqual({c['qualifiers'] for c in candidates}, {'','niepopr.'})
            self.assertTrue(all(c['status']=='candidate_not_qualified' for c in candidates))
            self.assertEqual(db.execute('select count(*) from derivation_component').fetchone()[0], 6)
            self.assertEqual(db.execute('select count(*) from interpretation').fetchone()[0], 6)
            self.assertEqual(db.execute('pragma foreign_key_check').fetchall(), [])
            self.assertEqual(db.execute('select count(*) from derivation_candidate where original=?', ('byem',)).fetchone()[0], 0)

    def test_repeat_materialization_preserves_stable_ids_and_no_duplicates(self):
        import tempfile
        from literaki_slownik.constructions import materialize_confirmed_candidates
        with tempfile.TemporaryDirectory() as directory, self.database(directory) as db:
            self.insert_sources(db)
            materialize_confirmed_candidates(db)
            first = db.execute('select candidate_key,payload from derivation_candidate order by candidate_key').fetchall()
            second_report = materialize_confirmed_candidates(db)
            self.assertEqual(second_report['new_candidates'], 0)
            self.assertEqual(first, db.execute('select candidate_key,payload from derivation_candidate order by candidate_key').fetchall())

    def test_failure_in_uncovered_class_keeps_partial_output_not_full_completion(self):
        import tempfile
        from literaki_slownik.constructions import materialize_confirmed_candidates
        with tempfile.TemporaryDirectory() as directory, self.database(directory) as db:
            self.insert_sources(db)
            db.execute("update interpretation set tag='impt:sg:sec:new' where first_row=2")
            with self.assertRaises(GeneratorError):
                materialize_confirmed_candidates(db, batch_size=1)
            self.assertEqual(db.execute('select count(*) from derivation_candidate').fetchone()[0], 1)
