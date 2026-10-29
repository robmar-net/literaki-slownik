"""Odbiór budów a/b tematu MORZE: czysty kod, identyczne bajty, checker PASS na obu.

Budowy robi CLI (grupa 13.2); ten skrypt ich nie uruchamia, tylko sprawdza i zapisuje dowód.
Czasy budów podaje się argumentem --times (JSON {a: {start, end, exit}, b: {...}}).
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
sys.path.insert(0, str(REPO))
from literaki_slownik.canonical import load_json, sha256  # noqa: E402

PAKIETY = [REPO/'data/work'/('tematy-v1-20261029-' + s) for s in ('a', 'b')]
MANIFEST = REPO/'config/generator/tematy-sources.json'
CONFIG = REPO/'config/generator/tematy.json'


def files(root):
    return sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file())


def bez_przykladow(value):
    """Kopia bez list przykładów (dowód ma być zwięzły)."""
    if isinstance(value, dict):
        return {k: bez_przykladow(v) for k, v in value.items() if k != 'przyklady'}
    return value


def kluczowe(summary):
    """Zwięzły wyciąg z summary.json (bez przykładów i pełnych list)."""
    przec = {
        rodzaj: {w: {'temat': v['temat'], 'pop': v['pop'], 'pop00': v['pop00']}
                 for w, v in summary['przeciecia'][rodzaj].items()}
        for rodzaj in ('leksemy', 'formy')}
    sl = summary['slowa_oczywiste']
    sr = summary['srodladowe']
    return {
        'liczby': summary['liczby'],
        'przeciecia': przec,
        'diagnostyka': summary['diagnostyka'],
        'slowa_oczywiste': {k: sl[k] for k in ('razem', 'T1', 'T1_T2', 'spelniony', 'prog')},
        'srodladowe': {k: {kk: vv for kk, vv in v.items() if kk != 'przyklady'} if isinstance(v, dict) else v
                       for k, v in sr.items()},
        'odrzucone': bez_przykladow(summary['odrzucone']),
        't3': bez_przykladow(summary['t3']),
        'wieloznaczny': summary['wieloznaczny'],
        'werdykt': summary['werdykt'],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--times', required=True)
    ap.add_argument('--output', default=str(TASK/'verification/real-builds.json'))
    args = ap.parse_args()
    times = json.loads(Path(args.times).read_text())

    identities = [load_json(p/'release-manifest.json')['code_identity'] for p in PAKIETY]
    assert identities[0] == identities[1], identities
    assert identities[0]['git_dirty'] is False, identities[0]
    print('code_identity: git_dirty false, commit', identities[0]['git_commit'], flush=True)

    names = files(PAKIETY[0])
    assert names == files(PAKIETY[1]), 'Różne zbiory plików'
    hashes = {n: sha256(PAKIETY[0]/n) for n in names}
    assert all(sha256(PAKIETY[1]/n) == h for n, h in hashes.items()), 'Różne bajty'
    print('Identyczne bajty wszystkich', len(names), 'plików', flush=True)

    checks = {}
    for p in PAKIETY:
        r = subprocess.run([sys.executable, str(REPO/'scripts/check_tematy_package.py'), '--package-dir', str(p),
                            '--manifest', str(MANIFEST), '--config', str(CONFIG)],
                           capture_output=True, text=True, cwd=REPO)
        assert r.returncode == 0, (p.name, r.returncode, r.stdout[-2000:], r.stderr[-2000:])
        out = json.loads(r.stdout)
        checks[p.name] = {'exit': r.returncode, 'status': out.get('status'), 'wynik': out}
        print('Checker', p.name, out.get('status'), flush=True)

    summary = load_json(PAKIETY[0]/'reports/summary.json')
    proof = {
        'code_identity': identities[0],
        'budowy': times,
        'pakiety': [str(p.relative_to(REPO)) for p in PAKIETY],
        'sha256sums_sha256': sha256(PAKIETY[0]/'SHA256SUMS'),
        'files_sha256': hashes,
        'all_files_identical': True,
        'checker': {k: {'exit': v['exit'], 'status': v['status']} for k, v in checks.items()},
        'checker_wynik_a': checks[PAKIETY[0].name]['wynik'],
        'summary': kluczowe(summary),
    }
    Path(args.output).write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Zapisano', args.output, flush=True)


if __name__ == '__main__':
    main()
