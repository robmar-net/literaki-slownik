import tempfile
import unittest
from pathlib import Path
from literaki_slownik.run import create_run, set_stage
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.canonical import load_json


class RunTests(unittest.TestCase):
    def test_new_run_and_failed_stage_remain_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / 'run'
            create_run(run, {'mode': 'test'})
            set_stage(run, 'import_sgjp', 'running')
            set_stage(run, 'import_sgjp', 'failed', {'reason': 'przerwanie'})
            manifest = load_json(run / 'manifest.json')
            self.assertEqual(manifest['readiness'], 'INCOMPLETE')
            self.assertEqual(manifest['stages']['import_sgjp']['status'], 'failed')

    def test_existing_target_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            sentinel = target / 'sentinel'
            sentinel.write_text('istniejące')
            with self.assertRaises(GeneratorError):
                create_run(target, {})
            self.assertEqual(sentinel.read_text(), 'istniejące')

    def test_missing_parent_is_not_created_and_new_fields_start_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(GeneratorError) as caught:
                create_run(Path(directory) / 'brak' / 'run', {})
            self.assertEqual(caught.exception.code, 4)
            self.assertFalse((Path(directory) / 'brak').exists())
            run = Path(directory) / 'run'
            create_run(run, {})
            manifest = load_json(run / 'manifest.json')
            self.assertIsNone(manifest['work_volume'])
            self.assertEqual(manifest['resume'], {'resumed': False, 'count': 0})
            self.assertEqual([(a['attempt'], a['ended'], a['outcome']) for a in manifest['build_attempts']],
                             [(1, None, None)])
