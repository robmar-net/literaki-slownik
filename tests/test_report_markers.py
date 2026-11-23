"""R7: znaczniki reports/.done/<raport>.json i unresolved z pliku."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from literaki_slownik import build as build_module
from literaki_slownik.build import build, run_build, stage_context, MARKED_REPORTS
from literaki_slownik.canonical import load_json, sha256, write_json
from literaki_slownik.inputs import inspect_sources
from literaki_slownik.run import code_identity
from tests.release_helpers import fixture_inputs


class ReportMarkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)
        (self.directory / 'inputs').mkdir()
        self.manifest = fixture_inputs(self.directory / 'inputs')
        self.run = self.directory / 'run'
        build(self.manifest, self.run)
        self.reports = self.run / 'reports'
        self.before = {name: (self.reports / name).read_bytes() for name in MARKED_REPORTS}
        self.index = (self.reports / 'canonical-index.json').read_bytes()

    def tearDown(self):
        self.tmp.cleanup()

    def reports_again(self):
        """Etap reports w istniejącym przebiegu (ta sama pętla co build)."""
        return run_build(stage_context(self.manifest, self.run, inspect_sources(self.manifest)), 'reports')

    def test_fresh_build_writes_markers_and_bad_hash_recomputes_only_that_report(self):
        inputs = inspect_sources(self.manifest)
        tree = code_identity()['tree_sha256']
        for name in MARKED_REPORTS:
            marker = load_json(self.reports / '.done' / name)
            self.assertEqual(marker, {'sha256': sha256(self.reports / name),
                                      'bytes': (self.reports / name).stat().st_size,
                                      'tree_sha256': tree, 'manifest_sha256': inputs['manifest_sha256']})
        marker = load_json(self.reports / '.done/filter-impact.json')
        write_json(self.reports / '.done/filter-impact.json', {**marker, 'sha256': '0' * 64})
        real = build_module.persisted_filter_impact
        with patch.object(build_module, 'persisted_filter_impact', side_effect=real) as impact, \
                patch.object(build_module, 'logical_content_report') as logical, \
                patch.object(build_module, 'unresolved_report') as unresolved:
            self.reports_again()
        self.assertEqual(impact.call_count, 1)
        logical.assert_not_called()
        unresolved.assert_not_called()
        self.assertEqual(load_json(self.reports / '.done/filter-impact.json'), marker)
        self.assertEqual({name: (self.reports / name).read_bytes() for name in MARKED_REPORTS}, self.before)

    def test_unresolved_from_file_gives_same_dependent_bytes_and_done_stays_outside_index(self):
        for name in MARKED_REPORTS:
            if name != 'unresolved.json':
                (self.reports / '.done' / name).unlink()
                (self.reports / name).unlink()
        with patch.object(build_module, 'unresolved_report', side_effect=AssertionError('liczony od nowa')):
            self.reports_again()
        self.assertEqual({name: (self.reports / name).read_bytes() for name in MARKED_REPORTS}, self.before)
        self.assertEqual((self.reports / 'canonical-index.json').read_bytes(), self.index)
        self.assertNotIn('.done', self.index.decode('utf-8'))
        self.assertEqual(load_json(self.run / 'manifest.json')['stages']['reports']['status'], 'complete')


if __name__ == '__main__':
    unittest.main()
