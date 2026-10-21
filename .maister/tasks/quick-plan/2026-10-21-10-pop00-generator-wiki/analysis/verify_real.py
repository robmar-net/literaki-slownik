"""Odbiór na przypiętych danych; zachowuje istniejące przebiegi i dowody."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys

TASK=Path(__file__).resolve().parents[1]
REPO=TASK.parents[3]
sys.path.insert(0,str(REPO))
from literaki_slownik.canonical import sha256,load_json
from literaki_slownik.pop00 import build_package,read_words
from literaki_slownik.run import code_identity

def main():
    identity=code_identity()
    assert identity['git_dirty'] is False
    source=REPO/'config/generator/pop00-sources.json'
    config=REPO/'config/generator/pop00.json'
    paths=[REPO/'data/work'/('pop00-v1-20261021-r2-'+suffix) for suffix in ('a','b')]
    for path in paths:
        if not path.exists():
            report=build_package(source,config,path)
            print('BUILT',path.name,report['forms'],report['selected_lexemes'],flush=True)
        assert load_json(path/'release-manifest.json')['code_identity']==identity
    names={p.relative_to(paths[0]).as_posix() for p in paths[0].rglob('*') if p.is_file()}
    assert names=={p.relative_to(paths[1]).as_posix() for p in paths[1].rglob('*') if p.is_file()}
    hashes={name:sha256(paths[0]/name) for name in sorted(names)}
    assert all(sha256(paths[1]/name)==value for name,value in hashes.items())
    print('Dwa pakiety: identyczne bajty wszystkich',len(names),'plików',flush=True)
    with redirect_stdout(io.StringIO()):
        probe=runpy.run_path(str(TASK/'analysis/probe_policy.py'))
    expected=probe['selected']['hybrid_0.1']
    actual=read_words(paths[0]/'POP00.txt.gz')
    assert actual==expected,{'only_actual':sorted(actual-expected)[:30],'only_probe':sorted(expected-actual)[:30]}
    print('Dokładny diff względem sondy: 0/0',flush=True)
    checks=[]
    for path in paths:
        result=subprocess.run([sys.executable,str(REPO/'scripts/check_pop00_package.py'),
            '--pop00-dir',str(path),'--manifest',str(source),'--config',str(config)],
            capture_output=True,text=True,cwd=REPO)
        assert result.returncode==0,(result.returncode,result.stderr)
        checks.append(json.loads(result.stdout))
        print('Niezależny kontroler:',path.name,'PASS',flush=True)
    now=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
    proof={'verified_at':now,'code_identity':identity,'packages':[str(p.relative_to(REPO)) for p in paths],
           'files_sha256':hashes,'all_files_identical':True,'full_word_diff_against_probe':{'added':0,'removed':0},
           'checks':checks,'summary':load_json(paths[0]/'reports/summary.json')}
    (TASK/'verification').mkdir(exist_ok=True)
    (TASK/'verification/real-builds-r2.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
