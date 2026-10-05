"""Powiązanie korpusu nie jest decyzją słownikową ani przypisaniem sensu."""
import json
import tempfile
import unittest
from pathlib import Path

from literaki_slownik.database import connect
from literaki_slownik.links import candidates, availability, create_links, link_report
from literaki_slownik.inputs import GeneratorError


class LinksTests(unittest.TestCase):
    def test_derived_forms_match_whole_orth_only_without_inheriting_root_frequency(self):
        from literaki_slownik.constructions import materialize_confirmed_candidates
        # Dwa źródłowe rozkaźniki dają dwa ślady tej samej pełnej formy.
        for number, lemma in [(101,'czytać:a'),(102,'czytać:b')]:
            self.db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)', ('SGJP',number,'czytaj',lemma,'impt:sg:sec:imperf','',''))
            self.db.execute('insert into lexeme(source_id,lemma_id,lemma_base) values (?,?,?)', ('SGJP',lemma,'czytać'))
            lid = self.db.execute('select id from lexeme where lemma_id=?',(lemma,)).fetchone()[0]
            self.db.execute('insert or ignore into surface_form(original,nfc,game_key,length) values (?,?,?,?)', ('czytaj','czytaj','czytaj',6))
            fid = self.db.execute("select id from surface_form where original='czytaj'").fetchone()[0]
            self.db.execute('insert into interpretation(source_id,first_row,form_id,lexeme_id,tag,names,qualifiers) values (?,?,?,?,?,?,?)', ('SGJP',number,fid,lid,'impt:sg:sec:imperf','',''))
        materialize_confirmed_candidates(self.db)
        whole = candidates(self.db,'kwjp_orth','czytajże')
        self.assertEqual(whole['status'],'AMBIGUOUS')
        self.assertEqual(len(whole['candidates']),2)
        self.assertTrue(all(c['candidate_key'] for c in whole['candidates']))
        self.assertEqual(candidates(self.db,'kwjp_lemma','czytajże',pos='impt')['candidates'],[])
        self.db.execute('insert into source_artifact values (?,?,?)', ('ORTH','kwjp_orth','{}'))
        self.db.execute('insert into corpus_evidence values (?,?,?,?,?,?,?,?,?)', (1,'ORTH',1,'czytajże',None,None,'{"freq":"5"}','{"freq":5}',5))
        summary = create_links(self.db)
        self.assertEqual(summary['ORTH'],{'AMBIGUOUS':1})
        self.assertEqual(self.db.execute('select count(*) from evidence_candidate where candidate_key is not null').fetchone()[0],2)
        self.assertEqual(self.db.execute('select sum(freq) from corpus_evidence').fetchone()[0],5)
        self.assertEqual(self.db.execute('pragma foreign_key_check').fetchall(),[])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.connection = connect(Path(self.temp.name) / 'test.sqlite', create=True)
        self.db = self.connection.__enter__()
        self.addCleanup(self.connection.__exit__, None, None, None)
        self.db.execute('insert into source_artifact values (?,?,?)', ('SGJP', 'sgjp_tab', '{}'))
        for index, (lemma, base, form, pos) in enumerate([
            ('zamek:a', 'zamek', 'zamek', 'subst'),
            ('zamek:b', 'zamek', 'zamek', 'subst'),
            ('Róża', 'Róża', 'Róża', 'subst'),
            ('róża', 'róża', 'róża', 'subst'),
            ('polski:A', 'polski', 'polski', 'adj'),
            ('polski:S', 'polski', 'polski', 'subst'),
            ('é', 'e\u0301', 'e\u0301', 'subst'),
        ], 1):
            self.db.execute('insert into lexeme values (?,?,?,?)', (index, 'SGJP', lemma, base))
            self.db.execute('insert or ignore into surface_form(original,nfc,game_key,length) values (?,nfc(?),game_key(?),length(nfc(?)))', (form, form, form, form))
            fid = self.db.execute('select id from surface_form where original=?', (form,)).fetchone()[0]
            self.db.execute('insert into interpretation values (?,?,?,?,?,?,?,?)', (index, 'SGJP', index, fid, index, pos + ':test', '', ''))

    def test_lemma_pos_preserves_homonyms_and_case(self):
        result = candidates(self.db, 'kwjp_lemma', 'zamek', pos='subst')
        self.assertEqual(result['status'], 'AMBIGUOUS')
        self.assertEqual([c['lemma_id'] for c in result['candidates']], ['zamek:a', 'zamek:b'])
        self.assertFalse(result['sense_identity_confirmed'])
        self.assertEqual([c['lemma_id'] for c in candidates(self.db, 'kwjp_lemma', 'Róża', pos='subst')['candidates']], ['Róża'])
        self.assertEqual([c['lemma_id'] for c in candidates(self.db, 'kwjp_lemma', 'polski', pos='subst')['candidates']], ['polski:S'])
        self.assertEqual(candidates(self.db, 'kwjp_lemma', 'polski', pos='cond')['status'], 'UNMATCHED')
        self.assertEqual(candidates(self.db, 'kwjp_lemma', 'é', pos='subst')['candidates'][0]['lemma_id'], 'é')

    def test_forms_lowercase_and_bigram_remain_different_methods(self):
        exact = candidates(self.db, 'kwjp_orth', 'Róża')
        self.assertEqual([c['original'] for c in exact['candidates']], ['Róża'])
        lower = candidates(self.db, 'kwjp_orth_lc', 'róża')
        self.assertEqual([c['original'] for c in lower['candidates']], ['Róża', 'róża'])
        self.assertEqual(lower['status'], 'AMBIGUOUS')
        bigram = candidates(self.db, 'kwjp_bigram', 'czytał', unit_2='bym')
        self.assertEqual(bigram['status'], 'NOT_APPLICABLE')
        self.assertEqual(bigram['candidates'], [])
        with self.assertRaises(ValueError):
            candidates(self.db, 'unknown', 'kot')

    def test_availability_never_infers_zero_from_absence(self):
        self.assertEqual(availability(observed={'freq': 1, 'DP': '0'}, genre='fikcja')['metrics']['DP'], '0')
        # Niedopasowanie leksemu nie usuwa zaobserwowanej jednostki korpusu.
        self.assertEqual(availability(observed={'freq': 7}, mapped=False)['status'], 'OBSERVED')
        self.assertEqual(availability(threshold=5, comparable=True)['status'], 'ABSENT_OR_BELOW_PUBLICATION_THRESHOLD')
        self.assertEqual(availability(threshold=5, comparable=True, genre='fikcja')['status'], 'NOT_IN_PUBLISHED_LIST')
        self.assertEqual(availability(threshold=5, comparable=False)['status'], 'NOT_IN_PUBLISHED_LIST')
        self.assertIsNone(availability(threshold=5, comparable=True)['metrics'])
        self.assertEqual(availability(unavailable_reason='NKJP BLOCKED')['status'], 'UNAVAILABLE')

    def test_persist_links_reference_one_evidence_without_copying_f(self):
        self.db.execute('insert into source_artifact values (?,?,?)', ('KWJP', 'kwjp_lemma', json.dumps({'genre': 'all'})))
        self.db.execute('insert into corpus_evidence values (?,?,?,?,?,?,?,?,?)', (1, 'KWJP', 1, 'zamek', None, 'subst', '{"freq":"7"}', '{"freq":7}', 7))
        self.db.execute('insert into corpus_evidence values (?,?,?,?,?,?,?,?,?)', (2, 'KWJP', 2, 'brak', None, 'subst', '{"freq":"5"}', '{"freq":5}', 5))
        summary = create_links(self.db)
        self.assertEqual(summary['KWJP'], {'AMBIGUOUS': 1, 'UNMATCHED': 1})
        self.assertEqual(self.db.execute('select count(*) from evidence_candidate where evidence_id=1').fetchone()[0], 2)
        self.assertEqual(self.db.execute('select sum(freq) from corpus_evidence').fetchone()[0], 12)
        self.assertNotIn('freq', [r[1] for r in self.db.execute('pragma table_info(evidence_candidate)')])
        self.assertEqual(self.db.execute('pragma foreign_key_check').fetchall(), [])
        report = link_report(self.db, unavailable=[{'source_id': 'NKJP', 'reason': 'BLOCKED'}])
        row = report['lists']['KWJP']
        self.assertEqual(row['evidence_units'], 2)
        self.assertEqual(row['sum_freq'], 12)  # F homonimu liczone raz, nie za każdą krawędź.
        self.assertEqual(row['candidate_edges'], 2)
        self.assertEqual(row['genre'], 'all')
        self.assertEqual(row['observed_units'], 2)  # UNMATCHED nadal ma obserwację korpusową.
        self.assertEqual(row['link_statuses'], {'AMBIGUOUS': 1, 'UNMATCHED': 1})
        self.assertEqual(report['unavailable'][0]['status'], 'UNAVAILABLE')
        self.db.execute('delete from evidence_link where evidence_id=2')
        with self.assertRaises(GeneratorError):
            link_report(self.db)
