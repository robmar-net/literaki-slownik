"""`.gitignore`: symlinki przebiegów w `data/work` i logi w `logs/` są ignorowane (R1, L2)."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def git(repo,*args):
    env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
    return subprocess.run(['git','-C',str(repo),*args],env=env,capture_output=True,text=True)

class GitignoreTests(unittest.TestCase):
    def repo(self):
        repo=Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.assertEqual(git(repo,'init','-q').returncode,0)
        shutil.copy(ROOT/'.gitignore',repo/'.gitignore')
        return repo

    def test_run_symlink_and_log_are_ignored(self):
        repo=self.repo();target=repo/'poza'/'x';target.mkdir(parents=True)
        (repo/'data'/'work').mkdir(parents=True);(repo/'data'/'work'/'x').symlink_to(target)
        (repo/'logs').mkdir();(repo/'logs'/'x.out.json').write_text('{}')
        for path in ('data/work/x','logs/x.out.json'):
            with self.subTest(path=path):
                self.assertEqual(git(repo,'check-ignore','-q',path).returncode,0)

    def test_code_file_is_not_ignored(self):
        repo=self.repo();(repo/'literaki_slownik').mkdir()
        (repo/'literaki_slownik'/'x.py').write_text('')
        self.assertEqual(git(repo,'check-ignore','-q','literaki_slownik/x.py').returncode,1)

if __name__=='__main__':
    unittest.main()
