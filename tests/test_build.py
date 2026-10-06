import gzip
import hashlib
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from tests.helpers import fixture_manifest, rewrite
from literaki_slownik.build import build
from literaki_slownik.database import connect
from literaki_slownik.canonical import load_json
from literaki_slownik.inputs import GeneratorError


class BuildTests(unittest.TestCase):
    def test_diagnostic_decisions_written_with_full_reasons_without_activating_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            p=self.manifest(directory,'#</COPYRIGHT>\nkot\tkot\tsubst:sg:nom.acc:m2\t\t\n')
            run=Path(directory)/'run';build(p,run)
            with connect(run/'build.sqlite',readonly=True) as db:
                self.assertEqual(db.execute('select count(*) from analysis').fetchone()[0],2)
                self.assertEqual(db.execute('select count(*) from variant_decision').fetchone()[0],4)
                self.assertEqual(db.execute('select distinct membership_status from variant_decision').fetchall(),[('unresolved',)])
            self.assertTrue(load_json(run/'reports/decisions.json')['full_qualification_pending'])
            self.assertEqual(load_json(run/'manifest.json')['stages']['decisions']['status'],'pending')

    def test_preposition_candidates_store_proof_and_unresolved_without_losing_homonym(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.manifest(directory, '#</COPYRIGHT>\ndo\tdo:P\tprep:gen\t\t\nkoło\tkoło:P\tprep:gen\t\t\nń\ton:S\tppron3:sg:gen:m1.m2.m3:ter:nakc:praep\t\tpisane_łącznie_z_przyimkiem\ndoń\tdonia\tsubst:pl:gen:f\t\t\n')
            run = Path(directory) / 'run'
            build(p, run)
            import json
            with connect(run / 'build.sqlite', readonly=True) as db:
                candidates = [json.loads(r[0]) for r in db.execute('select payload from derivation_candidate')]
                self.assertEqual(len(candidates), 6)
                self.assertEqual({c['linguistic_evidence']['status'] for c in candidates if c['original']=='doń'}, {'accept'})
                self.assertEqual({c['linguistic_evidence']['status'] for c in candidates if c['original']=='kołoń'}, {'unresolved'})
                self.assertEqual(db.execute('select count(*) from derivation_component').fetchone()[0], 12)
                self.assertEqual(db.execute('select count(*) from interpretation').fetchone()[0], 4)
                self.assertEqual(db.execute('pragma foreign_key_check').fetchall(), [])

    def corpus_manifest(self, directory):
        p = self.manifest(directory, '#</COPYRIGHT>\nzamek\tzamek:a\tsubst:sg:nom:m3\t\t\nzamek\tzamek:b\tsubst:sg:nom:m3\t\t\n')
        manifest = load_json(p)
        corpus = Path(directory) / 'lemma.csv.gz'
        with gzip.open(corpus, 'wt', encoding='utf-8') as stream:
            stream.write(',,freq,ipm,ARF,DP,DP_norm,1-DP,total_freq\nzamek,subst,7,1,1,0,0,1,7\nbrak,subst,5,1,1,0,0,1,5\n')
        artifact = dict(manifest['artifacts'][0])
        artifact.update(source_id='corpus', kind='kwjp_lemma', role='corpus_evidence',
                        path=corpus.name, sha256=hashlib.sha256(corpus.read_bytes()).hexdigest(),
                        genre='all', publication_threshold=5)
        manifest['artifacts'].append(artifact)
        rewrite(p, manifest)
        return p

    def test_build_links_all_corpus_units_without_assigning_frequency_to_homonyms(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.corpus_manifest(directory)
            run = Path(directory) / 'run'
            result = build(p, run)
            with connect(run / 'build.sqlite', readonly=True) as db:
                self.assertEqual(db.execute('select count(*) from evidence_link').fetchone()[0], 2)
                self.assertEqual(db.execute('select count(*) from evidence_candidate').fetchone()[0], 2)
                self.assertEqual(db.execute('select sum(freq) from corpus_evidence').fetchone()[0], 12)
                self.assertEqual(db.execute('pragma foreign_key_check').fetchall(), [])
            report = load_json(run / 'reports/links.json')
            self.assertEqual(report['lists']['corpus']['link_statuses'], {'AMBIGUOUS': 1, 'UNMATCHED': 1})
            self.assertEqual(report['unavailable'][0]['source_id'], 'NKJP')
            manifest = load_json(run / 'manifest.json')
            # Dopóki konstrukcje nie są powiązane, pełny etap pozostaje pending.
            self.assertEqual(manifest['stages']['links']['status'], 'pending')
            self.assertIn('links', result['pending'])
            self.assertEqual(manifest['readiness'], 'INCOMPLETE')
            self.assertIn('diagnostic_links', load_json(run / 'reports/performance.json'))

    def test_links_gate_records_verification_and_keeps_stage_pending_without_constructions(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.corpus_manifest(directory)
            run = Path(directory) / 'run'
            result = build(p, run)
            report = load_json(run / 'reports/links.json')
            gate = report['stage_completion']
            self.assertFalse(gate['complete'])
            self.assertTrue(gate['blocking'][0].startswith('constructions=pending'))
            self.assertEqual(gate['verification']['missing_edges'], 0)
            self.assertEqual(gate['verification']['unexpected_edges'], 0)
            self.assertEqual(report['lists']['corpus']['unmatched_by_pos'], {'subst': 1})
            self.assertEqual(report['pos_map_version'], 'builtin-identity-shared-pos')
            self.assertEqual(load_json(run / 'manifest.json')['stages']['links']['status'], 'pending')
            self.assertEqual(result['readiness'], 'INCOMPLETE')

    def test_build_uses_declared_pos_map(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            p = self.corpus_manifest(directory)
            manifest = load_json(p)
            data = json.loads((Path(__file__).resolve().parents[1] / 'config/generator/pos-map.json').read_text(encoding='utf-8'))
            data['confirmed_pairs'].pop('subst')
            data['version'] = 'pos-map-test'
            config = Path(directory) / 'pos-map.json'
            config.write_text(json.dumps(data), encoding='utf-8')
            manifest['configurations']['pos-map'] = {'path': config.name,
                                                     'sha256': hashlib.sha256(config.read_bytes()).hexdigest()}
            rewrite(p, manifest)
            run = Path(directory) / 'run'
            build(p, run)
            report = load_json(run / 'reports/links.json')
            self.assertEqual(report['pos_map_version'], 'pos-map-test')
            self.assertEqual(report['lists']['corpus']['link_statuses'], {'UNMATCHED': 2})
            self.assertEqual(report['stage_completion']['verification']['missing_edges'], 0)

    def test_links_failure_preserves_imports_and_candidate_traces(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.corpus_manifest(directory)
            run = Path(directory) / 'run'
            with patch('literaki_slownik.build.create_links', side_effect=ValueError('uszkodzone powiązanie')):
                with self.assertRaises(GeneratorError):
                    build(p, run)
            manifest = load_json(run / 'manifest.json')
            self.assertEqual(manifest['stages']['links']['status'], 'failed')
            self.assertEqual(manifest['stages']['import_kwjp']['status'], 'complete')
            self.assertEqual(manifest['readiness'], 'INCOMPLETE')

    def manifest(self, directory, contents):
        p, manifest = fixture_manifest(directory)
        source = Path(directory) / 'source.gz'
        with gzip.open(source, 'wt', encoding='utf-8') as stream:
            stream.write(contents)
        manifest['artifacts'][0]['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        rewrite(p, manifest)
        return p

    def test_duplicates_homonyms_and_outside_profile_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.manifest(directory, '#</COPYRIGHT>\nkot\tkot:S1\tsubst:sg:nom.acc:m2\t\t\nkot\tkot:S1\tsubst:sg:nom.acc:m2\t\t\nRóża\tRóża:S2\tsubst:sg:nom:f\timię\t\npol-ski\tpolski\tadj:sg:nom:m1:pos\t\t\n')
            run = Path(directory) / 'run'
            result = build(p, run, batch_size=1)
            counts = result['counts']['synthetic']
            self.assertEqual(counts['records'], 4)
            self.assertEqual(counts['interpretations'], 3)
            self.assertEqual(counts['expanded_alternatives'], 4)
            with connect(run / 'build.sqlite') as db:
                self.assertEqual(db.execute('select count(*) from sgjp_record').fetchone()[0], 4)
                self.assertEqual(db.execute('select lemma_id from lexeme where lemma_id like ?', ('kot%',)).fetchone()[0], 'kot:S1')
                self.assertEqual(db.execute('select original from surface_form where original=?', ('pol-ski',)).fetchone()[0], 'pol-ski')
            self.assertEqual(load_json(run / 'manifest.json')['readiness'], 'INCOMPLETE')

    def test_failure_after_committed_batch_not_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.manifest(directory, '#</COPYRIGHT>\nkot\tkot\tsubst\t\t\nbad\trow\n')
            run = Path(directory) / 'run'
            with self.assertRaises(GeneratorError):
                build(p, run, batch_size=1)
            stage = load_json(run / 'manifest.json')['stages']['import_sgjp']
            self.assertEqual(stage['status'], 'failed')
            with connect(run / 'build.sqlite') as db:
                self.assertEqual(db.execute('select count(*) from sgjp_record').fetchone()[0], 1)

    def test_count_mismatch_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.manifest(directory, '#</COPYRIGHT>\nkot\tkot\tsubst\t\t\n')
            manifest = load_json(p)
            manifest['artifacts'][0]['expected_counts'] = {'records': 2}
            rewrite(p, manifest)
            with self.assertRaises(GeneratorError):
                build(p, Path(directory) / 'run')

    def test_qualifier_report_uses_deduplicated_interpretations_without_completing_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            line = 'kot\tkot\tsubst:sg:nom:m2\t\trzad.|nieznane\n'
            p = self.manifest(directory, '#</COPYRIGHT>\n' + line + line)
            run = Path(directory) / 'run'
            build(p, run)
            report = load_json(run / 'reports/qualifier-conditions.json')
            self.assertEqual(report['totals']['compact_interpretations'], 1)
            self.assertEqual(report['unmapped_labels'], ['nieznane'])
            self.assertTrue(report['full_qualification_pending'])
            manifest = load_json(run / 'manifest.json')
            self.assertEqual(manifest['readiness'], 'INCOMPLETE')
            self.assertEqual(manifest['stages']['reports']['status'], 'pending')

    def test_confirmed_candidates_materialized_without_completing_constructions(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.manifest(directory, '#</COPYRIGHT>\ndaj\tdać\timpt:sg:sec:perf\t\trzad.\nby\tby:T\tpart\t\t\nm\tbyć\taglt:sg:pri:imperf:nwok\t\t\n')
            run = Path(directory) / 'run'
            build(p, run)
            with connect(run / 'build.sqlite', readonly=True) as db:
                forms = {row[0] for row in db.execute('select original from derivation_candidate')}
                self.assertEqual(forms, {'dajże','dajżeż','bym'})
                self.assertEqual(db.execute('pragma foreign_key_check').fetchall(), [])
            report = load_json(run / 'reports/construction-candidates.json')
            self.assertEqual(report['candidates'], 3)
            self.assertTrue(report['full_constructions_pending'])
            manifest = load_json(run / 'manifest.json')
            self.assertEqual(manifest['stages']['constructions']['status'], 'pending')
            self.assertEqual(manifest['readiness'], 'INCOMPLETE')

    def test_construction_failure_marks_failed_and_preserves_import(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.manifest(directory, '#</COPYRIGHT>\ndajmy\tdać\timpt:sg:sec:perf\t\t\n')
            run = Path(directory) / 'run'
            with self.assertRaises(GeneratorError):
                build(p, run)
            manifest = load_json(run / 'manifest.json')
            self.assertEqual(manifest['stages']['constructions']['status'], 'failed')
            self.assertEqual(manifest['stages']['import_sgjp']['status'], 'complete')
            self.assertEqual(manifest['readiness'], 'INCOMPLETE')
