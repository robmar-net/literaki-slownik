"""R9: resume_reports.py jako nakładka na `build --resume`; kod wyjścia przechodzi dalej."""
from contextlib import redirect_stderr
import importlib.util
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from literaki_slownik.canonical import write_json
from literaki_slownik.run import STAGES

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('resume_reports', ROOT / 'scripts/resume_reports.py')
resume_reports = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(resume_reports)

IDENTITY = {'tree_sha256': 'a' * 64, 'git_dirty': False}


class ResumeReportsCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = self.tmp / 'run'
        self.run_dir.mkdir()
        patch = mock.patch.object(resume_reports, 'code_identity', lambda: dict(IDENTITY))
        patch.start()
        self.addCleanup(patch.stop)

    def manifest(self, reports='failed', tree='a' * 64):
        stages = {name: {'status': 'complete'} for name in STAGES}
        stages['reports'] = {'status': reports}
        write_json(self.run_dir / 'manifest.json', {'stages': stages, 'code': {'tree_sha256': tree}})

    def main(self, cli_code=0):
        calls = []

        def cli_main(argv):
            calls.append(argv)
            return cli_code
        with mock.patch.object(resume_reports, 'cli_main', cli_main), redirect_stderr(io.StringIO()):
            code = resume_reports.main(['--manifest', 'm.json', '--run-dir', str(self.run_dir)])
        return code, calls

    def test_passes_the_exit_code_of_build_resume(self):
        self.manifest()
        for expected in (0, 75, 77):
            code, calls = self.main(expected)
            self.assertEqual(code, expected)
            self.assertEqual(calls, [['build', '--resume', '--manifest', 'm.json', '--run-dir',
                                      str(self.run_dir), '--json']])

    def test_todays_checks_refuse_before_build(self):
        self.manifest(reports='complete')
        self.assertEqual(self.main(), (2, []))
        self.manifest(tree='b' * 64)
        self.assertEqual(self.main(), (4, []))

    def test_unreadable_manifest_goes_to_build_resume_for_75_or_4(self):
        code, calls = self.main(75)
        self.assertEqual(code, 75)
        self.assertEqual(len(calls), 1)


if __name__ == '__main__':
    unittest.main()
