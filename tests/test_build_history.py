"""R12: skrót historii prób w verify (JSON i tekst) i w release-manifest.json, pod pieczęcią."""
import tempfile
import unittest
from pathlib import Path

from literaki_slownik.build import build, resume
from literaki_slownik.canonical import load_json, write_json
from literaki_slownik.export import export
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.verify import format_verification, verify
from tests.release_helpers import complete_run, fixture_inputs, make_review
from tests.test_resume import clean_identity
from tests.test_resume_equivalence import after

KEYS = {'resumed', 'resume_count', 'attempts', 'stages', 'outcomes', 'exit_codes', 'resumed_from'}


class BuildHistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        (self.directory / 'inputs').mkdir()
        manifest = fixture_inputs(self.directory / 'inputs')
        self.enterContext(clean_identity())
        self.fresh, self.run = self.directory / 'swiezy', self.directory / 'wznowiony'
        build(manifest, self.fresh)
        with after('link_report'), self.assertRaises(GeneratorError):
            build(manifest, self.run)
        resume(manifest, self.run)
        complete_run(self.run)
        complete_run(self.fresh)
        review = make_review(self.run, self.directory / 'review.json')
        self.report = verify(self.run, self.fresh, review, allow_test_fixture=True)
        self.assertEqual(self.report['verdict'], 'VERIFIED', self.report['checks'])

    def test_verify_reports_history_in_json_and_text(self):
        history = self.report['build_history']
        attempts = load_json(self.run / 'manifest.json')['build_attempts']
        self.assertEqual(set(history), KEYS)
        self.assertEqual(history['resumed'], True)
        self.assertEqual(history['resume_count'], 1)
        self.assertEqual(history['attempts'], 2)
        self.assertEqual(history['outcomes'], ['failed', 'complete'])
        self.assertEqual(history['exit_codes'], [a['exit_code'] for a in attempts])
        self.assertEqual(history['resumed_from'], [attempts[1]['first_stage']])
        self.assertEqual(history['stages'], [[a['first_stage'], a['last_stage']] for a in attempts])
        self.assertEqual(load_json(self.run / self.report['attempt'] / 'verification.json')['build_history'],
                         history)
        text = format_verification(self.report)
        self.assertIn('Historia buildu: wznowiony 1×, prób 2', text)
        self.assertIn(f'wznowiono od: {attempts[1]["first_stage"]}', text)

    def test_export_copies_history_without_messages_or_paths(self):
        target = self.directory / 'release'
        export(self.run, target, allow_test_fixture=True)
        source = load_json(target / 'release-manifest.json')['source_run']
        self.assertEqual(source['build_history'], self.report['build_history'])
        self.assertIn('code', source)
        flat = str(source['build_history'])
        self.assertNotIn('/', flat)
        self.assertNotIn('error', flat)

    def test_editing_attempts_after_verify_blocks_export(self):
        path = self.run / 'manifest.json'
        manifest = load_json(path)
        manifest['build_attempts'] = manifest['build_attempts'][-1:]
        manifest['resume'] = {'resumed': False, 'count': 0}
        write_json(path, manifest)
        with self.assertRaises(GeneratorError) as raised:
            export(self.run, self.directory / 'release', allow_test_fixture=True)
        self.assertEqual(raised.exception.code, 5)
        self.assertIn('manifest przebiegu', str(raised.exception))
        self.assertFalse((self.directory / 'release').exists())


if __name__ == '__main__':
    unittest.main()
