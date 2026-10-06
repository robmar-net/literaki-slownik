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


class LinkCompletionTests(unittest.TestCase):
    """G5: jawne mapowanie POS, statusy dostępności i bramka pełnego etapu."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.connection = connect(Path(self.temp.name) / 'test.sqlite', create=True)
        self.db = self.connection.__enter__()
        self.addCleanup(self.connection.__exit__, None, None, None)
        self.db.execute('insert into source_artifact values (?,?,?)', ('SGJP', 'sgjp_tab', '{}'))
        rows = [(1, 'zamek', 'zamek:a', 'subst:sg:nom:m3'), (2, 'zamek', 'zamek:b', 'subst:sg:nom:m3'),
                (3, 'róża', 'róża', 'subst:sg:nom:f'), (4, 'czytaj', 'czytać', 'impt:sg:sec:imperf'),
                (5, 'jeśliby', 'jeśliby', 'cond'), (6, 'czytajże', 'czytajża', 'subst:sg:nom:f')]
        for number, form, lemma, tag in rows:
            self.db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)', ('SGJP', number, form, lemma, tag, '', ''))
            self.db.execute('insert or ignore into lexeme(source_id,lemma_id,lemma_base) values (?,?,?)',
                            ('SGJP', lemma, lemma.split(':')[0]))
            lid = self.db.execute('select id from lexeme where lemma_id=?', (lemma,)).fetchone()[0]
            self.db.execute('insert or ignore into surface_form(original,nfc,game_key,length) values (?,nfc(?),game_key(?),length(?))',
                            (form, form, form, form))
            fid = self.db.execute('select id from surface_form where original=?', (form,)).fetchone()[0]
            self.db.execute('insert into interpretation(source_id,first_row,form_id,lexeme_id,tag,names,qualifiers) values (?,?,?,?,?,?,?)',
                            ('SGJP', number, fid, lid, tag, '', ''))

    def corpus(self):
        from literaki_slownik.constructions import materialize_confirmed_candidates
        materialize_confirmed_candidates(self.db)
        lists = [('ORTH-ALL', 'kwjp_orth', 'all'), ('ORTH-FIK', 'kwjp_orth', 'fikcja'),
                 ('LC-ALL', 'kwjp_orth_lc', 'all'), ('LEMMA-ALL', 'kwjp_lemma', 'all'),
                 ('LEMMA-FIK', 'kwjp_lemma', 'fikcja'), ('BI', 'kwjp_bigram', 'all')]
        for sid, kind, genre in lists:
            self.db.execute('insert into source_artifact values (?,?,?)',
                            (sid, kind, json.dumps({'genre': genre, 'publication_threshold': 5})))
        evidence = [('ORTH-ALL', 'zamek', None, None, 7, '0'), ('ORTH-FIK', 'zamek', None, None, 2, '0.5'),
                    ('LC-ALL', 'czytajże', None, None, 9, '0.1'), ('LEMMA-ALL', 'zamek', None, 'subst', 11, '0'),
                    ('LEMMA-ALL', 'jeśliby', None, 'comp', 6, '0.2'), ('LEMMA-ALL', 'kropka', None, 'interp', 8, '0'),
                    ('BI', 'czytał', 'bym', None, 5, '0.3')]
        for number, (sid, first, second, pos, freq, dp) in enumerate(evidence, 1):
            typed = {'freq': freq, 'DP': dp, 'total_freq': max(freq, 5)}
            self.db.execute('insert into corpus_evidence values (?,?,?,?,?,?,?,?,?)',
                            (number, sid, number, first, second, pos, json.dumps(typed), json.dumps(typed), freq))
        create_links(self.db)

    def test_pos_map_config_is_explicit_and_rejects_sense_or_frequency_claims(self):
        from literaki_slownik.links import load_pos_map, SHARED_POS
        config = Path(__file__).resolve().parents[1] / 'config/generator/pos-map.json'
        mapping = load_pos_map(config)
        self.assertEqual(mapping['version'], 'pos-map-v1')
        self.assertEqual(set(mapping['pairs']), set(SHARED_POS))
        self.assertTrue(all(k == v for k, v in mapping['pairs'].items()))
        data = json.loads(config.read_text(encoding='utf-8'))
        for change in [{'sense_identity_confirmed': True}, {'allocate_frequency_to_candidates': True},
                       {'kwjp_only': data['kwjp_only'] + ['subst']},
                       {'confirmed_pairs': {**data['confirmed_pairs'], 'interp': 'nieistniejący'}}]:
            broken = Path(self.temp.name) / 'pos-map.json'
            broken.write_text(json.dumps({**data, **change}), encoding='utf-8')
            with self.assertRaises(GeneratorError):
                load_pos_map(broken)

    def test_unmatched_reason_separates_missing_pos_unmapped_pos_and_missing_lemma(self):
        missing = candidates(self.db, 'kwjp_lemma', 'zamek', pos=None)
        unmapped = candidates(self.db, 'kwjp_lemma', 'kropka', pos='interp')
        absent = candidates(self.db, 'kwjp_lemma', 'brak', pos='subst')
        self.assertEqual({missing['status'], unmapped['status'], absent['status']}, {'UNMATCHED'})
        self.assertEqual(missing['unmatched_reason'], 'NO_POS')
        self.assertEqual(unmapped['unmatched_reason'], 'POS_OUTSIDE_EXPLICIT_MAP')
        self.assertEqual(absent['unmatched_reason'], 'NO_STRUCTURAL_CANDIDATE')
        self.assertEqual(len({missing['reason'], unmapped['reason'], absent['reason']}), 3)
        ambiguous = candidates(self.db, 'kwjp_lemma', 'zamek', pos='subst')
        self.assertIn('nie wybieramy', ambiguous['reason'])
        # Mapowanie z konfiguracji może być inne niż nazwa KWJP; tu jawnie comp→cond nie istnieje.
        self.assertEqual(candidates(self.db, 'kwjp_lemma', 'jeśliby', pos='comp')['status'], 'UNMATCHED')
        mapped = candidates(self.db, 'kwjp_lemma', 'jeśliby', pos='comp', allowed_pos={'comp': 'cond'})
        self.assertEqual([c['lemma_id'] for c in mapped['candidates']], ['jeśliby'])

    def test_word_availability_reports_every_list_without_imputing_zero(self):
        from literaki_slownik.links import word_availability
        self.corpus()
        zamek = word_availability(self.db, 'zamek', unavailable=[{'source_id': 'NKJP', 'reason': 'BLOCKED'}])
        by_list = {item['source_id']: item for item in zamek['lists']}
        self.assertEqual(set(by_list), {'ORTH-ALL', 'ORTH-FIK', 'LC-ALL', 'LEMMA-ALL', 'LEMMA-FIK', 'BI'})
        orth = by_list['ORTH-ALL']['targets']
        self.assertEqual(len(orth), 1)  # jedna forma, mimo dwóch homonimów
        self.assertEqual(orth[0]['status'], 'OBSERVED')
        self.assertEqual([o['typed_metrics']['DP'] for o in orth[0]['metrics']], ['0'])  # zero miary jest obserwacją
        self.assertEqual(by_list['ORTH-FIK']['targets'][0]['metrics'][0]['freq'], 2)  # gatunkowe F 1–4
        self.assertEqual(by_list['LC-ALL']['targets'][0]['status'], 'ABSENT_OR_BELOW_PUBLICATION_THRESHOLD')
        self.assertIsNone(by_list['LC-ALL']['targets'][0]['metrics'])
        lemma = by_list['LEMMA-ALL']['targets']
        self.assertEqual([t['target']['lemma_id'] for t in lemma], ['zamek:a', 'zamek:b'])
        self.assertEqual({t['status'] for t in lemma}, {'OBSERVED'})
        # F jednej jednostki korpusu pokazane przy obu kandydatach jako ten sam rekord, nie suma.
        self.assertEqual({t['metrics'][0]['row_number'] for t in lemma}, {4})
        self.assertEqual({t['status'] for t in by_list['LEMMA-FIK']['targets']}, {'NOT_IN_PUBLISHED_LIST'})
        self.assertEqual(by_list['BI']['targets'][0]['status'], 'NOT_APPLICABLE')
        self.assertEqual(zamek['unavailable'][0]['status'], 'UNAVAILABLE')
        self.assertTrue(zamek['absence_is_not_zero'])

        roza = {i['source_id']: i for i in word_availability(self.db, 'róża')['lists']}
        self.assertEqual(roza['ORTH-ALL']['targets'][0]['status'], 'ABSENT_OR_BELOW_PUBLICATION_THRESHOLD')
        self.assertEqual(roza['ORTH-FIK']['targets'][0]['status'], 'NOT_IN_PUBLISHED_LIST')  # brak gatunkowy ≠ F<5

        cond = {i['source_id']: i for i in word_availability(self.db, 'jeśliby')['lists']}
        self.assertEqual(cond['LEMMA-ALL']['targets'][0]['status'], 'UNMATCHED')  # SGJP cond bez aliasu

        # Konstrukcja segmentowana: brak w orth to niepewna tokenizacja, nie F 0–4.
        derived = {i['source_id']: i for i in word_availability(self.db, 'czytajże')['lists']}
        orth_targets = {t['target']['type']: t for t in derived['ORTH-ALL']['targets']}
        self.assertEqual(orth_targets['derivation_candidate']['status'], 'NOT_IN_PUBLISHED_LIST')
        self.assertIn('segment', orth_targets['derivation_candidate']['reason'])
        # Bezpośredni homograf konstrukcji również nie dostaje progu.
        self.assertEqual(orth_targets['form']['status'], 'NOT_IN_PUBLISHED_LIST')
        lc = {t['target']['type'] for t in derived['LC-ALL']['targets'] if t['status'] == 'OBSERVED'}
        self.assertEqual(lc, {'form', 'derivation_candidate'})
        self.assertNotIn('derivation_candidate', {t['target']['type'] for t in derived['LEMMA-ALL']['targets']})

    def test_detailed_report_counts_methods_targets_ambiguity_and_unmatched_pos(self):
        self.corpus()
        report = link_report(self.db, details=True, pos_map_version='pos-map-v1')
        lemma = report['lists']['LEMMA-ALL']
        self.assertEqual(lemma['methods'], {'NFC_LEMMA_POS': 3})
        self.assertEqual(lemma['unmatched_by_pos'], {'comp': 1, 'interp': 1})
        self.assertEqual(lemma['candidates_per_unit'], {'0': 2, '2': 1})
        self.assertEqual(lemma['sum_freq_by_status'], {'AMBIGUOUS': 11, 'UNMATCHED': 14})
        lc = report['lists']['LC-ALL']
        self.assertEqual(lc['candidate_edges_by_target'], {'derivation_candidate': 1, 'form': 1, 'lexeme': 0})
        self.assertEqual(report['lists']['BI']['link_statuses'], {'NOT_APPLICABLE': 1})
        self.assertEqual(report['pos_map_version'], 'pos-map-v1')
        derived = report['derivation_candidates']
        self.assertEqual(derived['total'], self.db.execute('select count(*) from derivation_candidate').fetchone()[0])
        self.assertEqual(derived['with_corpus_edge'], 1)

    def test_completion_gate_requires_verified_edges_and_complete_constructions(self):
        from literaki_slownik.links import verify_link_completeness, link_stage_gate
        self.corpus()
        verified = verify_link_completeness(self.db)
        self.assertEqual(verified['missing_edges'], 0)
        self.assertEqual(verified['unexpected_edges'], 0)
        self.assertEqual(verified['inconsistent_statuses'], 0)
        self.assertEqual(verified['units_without_link'], 0)
        self.assertFalse(link_stage_gate(verified, constructions_status='pending')['complete'])
        self.assertIn('constructions', link_stage_gate(verified, constructions_status='pending')['blocking'][0])
        self.assertTrue(link_stage_gate(verified, constructions_status='complete')['complete'])
        # Kandydat dopisany po powiązaniach nie może przejść jako powiązany.
        self.db.execute('''insert into derivation_candidate values ('k-late','test','zamek','zamek','zamek:a','t','','','{}')''')
        late = verify_link_completeness(self.db)
        self.assertEqual(late['missing_edges'], 2)  # orth-all i orth-fikcja zawierają „zamek”
        gate = link_stage_gate(late, constructions_status='complete')
        self.assertFalse(gate['complete'])
        self.db.execute("delete from derivation_candidate where candidate_key='k-late'")
        self.db.execute('delete from evidence_candidate where id=(select min(id) from evidence_candidate)')
        broken = verify_link_completeness(self.db)
        self.assertEqual(broken['missing_edges'], 1)
        self.assertEqual(broken['inconsistent_statuses'], 1)
