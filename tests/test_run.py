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
