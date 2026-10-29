"""Zapis ocen agenta (grupa 13.6, D12) do verification/tematy-morze-review.json.

Oceny leżą w analysis/agent-ratings.json; zapis idzie przez scripts/tematy_review.py
(agent_review + write_review), więc plik przeglądu ma hash ocen i powiązanie z pakietem a.
Na koniec checker z --review sprawdza wynik.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
PKG = REPO/'data/work/tematy-v1-20261029-a'
OUT = TASK/'verification/tematy-morze-review.json'

spec = importlib.util.spec_from_file_location('tematy_review', REPO/'scripts/tematy_review.py')
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)


def main():
    data = json.loads((TASK/'analysis/agent-ratings.json').read_text(encoding='utf-8'))
    review = tr.agent_review(PKG, data['oceny'], data['reviewer'], data['reviewed_at'])
    tr.write_review(OUT, review)
    print('Zapisano', OUT.relative_to(REPO), 'agent_sha256', review['agent_sha256'], flush=True)
    r = subprocess.run([sys.executable, str(REPO/'scripts/check_tematy_package.py'), '--package-dir', str(PKG),
                        '--manifest', str(REPO/'config/generator/tematy-sources.json'),
                        '--config', str(REPO/'config/generator/tematy.json'), '--review', str(OUT)],
                       capture_output=True, text=True, cwd=REPO)
    print('checker --review: exit', r.returncode, flush=True)
    print(r.stdout or r.stderr)


if __name__ == '__main__':
    main()
