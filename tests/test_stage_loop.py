"""R6: pętla etapów i cztery poprawki „wznowiony = świeży”."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from literaki_slownik import build as build_module
from literaki_slownik.build import build, import_counts
from literaki_slownik.canonical import load_json
from literaki_slownik.constructions import materialize_confirmed_candidates
from literaki_slownik.database import connect
from literaki_slownik.links import create_links, link_report
from literaki_slownik.run import set_stage as real_set_stage
from tests.release_helpers import fixture_inputs

# Metryki import-counts.json fikstury sprzed podziału buildu na etapy.
FIXTURE_COUNTS = {'corpus': {'records': 1, 'sum_freq': 7},
                  'synthetic': {'duplicates': 0, 'expanded_alternatives': 5, 'interpretations': 4,
                                'lexemes': 4, 'original_forms': 3, 'records': 4}}


class StageLoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)
        (self.directory / 'inputs').mkdir()
        self.manifest = fixture_inputs(self.directory / 'inputs')
        self.run = self.directory / 'run'

    def tearDown(self):
        self.tmp.cleanup()

    def build_recording(self, check=None):
        """Build z zapisem kolejnych (etap, status); check(stage, status) wołany przed zapisem."""
        calls = []

        def recording(path, stage, status, details=None):
            if check:
                check(stage, status)
            calls.append((stage, status, details))
            return real_set_stage(path, stage, status, details)

        with patch.object(build_module, 'set_stage', recording):
            build(self.manifest, self.run)
        return calls

    def test_canonical_reports_have_no_inserted_counters_but_functions_return_them(self):
        build(self.manifest, self.run)
        constructions = load_json(self.run / 'reports/construction-candidates.json')
        decisions = load_json(self.run / 'reports/decisions.json')
        self.assertNotIn('new_candidates', constructions)
        self.assertIn('candidates', constructions)
        self.assertFalse({'new_analyses', 'new_decisions'} & set(decisions))
        self.assertIn('analyses', decisions)
        with connect(self.run / 'build.sqlite') as db:
            self.assertEqual(materialize_confirmed_candidates(db, 10000)['new_candidates'], 0)

    def test_import_counts_are_computed_from_database(self):
        build(self.manifest, self.run)
        self.assertEqual(load_json(self.run / 'reports/import-counts.json'), FIXTURE_COUNTS)
        artifacts = load_json(self.run / 'manifest.json')['inputs']['artifacts']
        with connect(self.run / 'build.sqlite', readonly=True) as db:
            self.assertEqual(import_counts(db, artifacts), FIXTURE_COUNTS)

    def test_import_reports_exist_before_import_kwjp_complete(self):
        seen = {}

        def check(stage, status):
            if (stage, status) == ('import_kwjp', 'complete'):
                seen['files'] = {name: (self.run / 'reports' / name).is_file() for name in
                                 ('import-counts.json', 'inventory.json', 'qualifier-conditions.json')}

        calls = self.build_recording(check)
        self.assertEqual(seen['files'], dict.fromkeys(seen['files'], True))
        order = [call[:2] for call in calls]
        self.assertLess(order.index(('import_kwjp', 'complete')), order.index(('constructions', 'running')))

    def test_links_runs_again_and_ends_pending_with_reason_when_incomplete(self):
        calls = self.build_recording()
        links = [call[1] for call in calls if call[0] == 'links']
        self.assertEqual(links, ['running', 'complete'])
        before = load_json(self.run / 'reports/links.json')
        with connect(self.run / 'build.sqlite') as db:
            create_links(db)
            db.commit()
            again = link_report(db, details=True)
        self.assertEqual(again['lists'], before['lists'])
        other = self.directory / 'niepelny'
        blocked = {'complete': False, 'blocking': ['missing_edges=1'], 'verification': {}}
        with patch.object(build_module, 'link_stage_gate', return_value=blocked):
            build(self.manifest, other)
        stage = load_json(other / 'manifest.json')['stages']['links']
        self.assertEqual(stage['status'], 'pending')
        self.assertIn('missing_edges=1', stage['reason'])

    def test_preflight_complete_only_after_source_artifact_commit(self):
        seen = {}

        def check(stage, status):
            if (stage, status) == ('preflight', 'complete'):
                with connect(self.run / 'build.sqlite', readonly=True) as db:
                    seen['rows'] = db.execute('select count(*) from source_artifact').fetchone()[0]

        calls = self.build_recording(check)
        self.assertEqual(seen['rows'], len(load_json(self.run / 'manifest.json')['inputs']['artifacts']))
        self.assertEqual([call[:2] for call in calls][:2], [('preflight', 'running'), ('preflight', 'complete')])


if __name__ == '__main__':
    unittest.main()
