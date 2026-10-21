import io
from contextlib import redirect_stdout,redirect_stderr
from pathlib import Path
import tempfile
import unittest
from literaki_slownik.cli import main
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.pop00 import build_package,explain_pop00,format_pop00_explanation
from tests.pop00_helpers import fixture,cleanup


class ExplainPop00Tests(unittest.TestCase):
    def test_explains_kept_removed_and_outside_base(self):
        with tempfile.TemporaryDirectory() as t:
            f=fixture(t);out=Path(t)/'out';build_package(f['manifest'],f['config'],out)
            for word,reason in [('ZROBIŁEM','IN_POP00'),('czytanymi','FORM_FILTERED'),('absent','NOT_IN_POP0')]:
                answer=explain_pop00(out,f['run'],word)
                self.assertEqual(answer['reason'],reason)
                self.assertIn(reason,format_pop00_explanation(answer))
            with redirect_stderr(io.StringIO()),redirect_stdout(io.StringIO()) as captured:
                code=main(['explain','--run-dir',str(f['run']),'--variant','pop00','--pop00-dir',str(out),'--word','bym'])
            self.assertEqual(code,0);self.assertIn('IN_POP00',captured.getvalue())
            p=out/'reports/decisions.json';p.chmod(0o644);p.write_text('{}')
            with self.assertRaises(GeneratorError):explain_pop00(out,f['run'],'bym')
            cleanup(t)

    def test_cli_requires_package_and_builds_json(self):
        with tempfile.TemporaryDirectory() as t:
            f=fixture(t)
            with redirect_stderr(io.StringIO()),redirect_stdout(io.StringIO()):
                self.assertEqual(main(['explain','--run-dir',str(f['run']),'--variant','pop00','--word','kot']),2)
                self.assertEqual(main(['pop00','--manifest',str(f['manifest']),'--config',str(f['config']),
                                      '--output-dir',str(Path(t)/'out'),'--json']),0)
            cleanup(t)
