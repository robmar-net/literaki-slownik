"""Odbiór budów a/b jednego tematu: czysty kod, identyczne bajty, checker PASS na obu.

Kopia skryptu z #11 (`2026-10-28-11-tematy-morze/analysis/verify_real.py`) z argumentami
--topic, --a, --b. Budowy robi CLI `tematy`; ten skrypt ich nie uruchamia, tylko sprawdza
i zapisuje dowód. Czasy budów podaje się argumentem --times (JSON {a: {start, end, exit}, b: {...}}).
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
    sr = summary.get('srodladowe')
    return {
        'liczby': summary['liczby'],
        'przeciecia': przec,
        'diagnostyka': summary['diagnostyka'],
        'slowa_oczywiste': {k: sl[k] for k in ('razem', 'T1', 'T1_T2', 'spelniony', 'prog')},
        'srodladowe': ({k: {kk: vv for kk, vv in v.items() if kk != 'przyklady'} if isinstance(v, dict) else v
                        for k, v in sr.items()} if isinstance(sr, dict) else sr),
        'odrzucone': bez_przykladow(summary['odrzucone']),
        't3': bez_przykladow(summary.get('t3')),
        'wieloznaczny': summary['wieloznaczny'],
        'wykluczenia': summary.get('wykluczenia'),
        'werdykt': summary['werdykt'],
    }


def git_porcelain(*paths):
    return subprocess.run(['git', 'status', '--porcelain', '--untracked-files=normal', '--', *paths],
                          cwd=REPO, capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--topic', required=True, help='plik tematu, np. config/generator/tematy/morze.json')
    ap.add_argument('--a', required=True, help='katalog pakietu a')
    ap.add_argument('--b', required=True, help='katalog pakietu b')
    ap.add_argument('--times', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    times = json.loads(Path(args.times).read_text())
    pakiety = [(REPO/args.a).resolve(), (REPO/args.b).resolve()]

    porcelain = git_porcelain('config', 'scripts', 'literaki_slownik')
    assert porcelain == '', 'Zmiany w config/, scripts/ lub literaki_slownik/:\n' + porcelain
    print('git status --porcelain config/ scripts/ literaki_slownik/: pusty', flush=True)

    identities = [load_json(p/'release-manifest.json')['code_identity'] for p in pakiety]
    assert identities[0] == identities[1], identities
    assert identities[0]['git_dirty'] is False, identities[0]
    print('code_identity: git_dirty false, commit', identities[0]['git_commit'], flush=True)

    topic_sha = sha256(REPO/args.topic)
    for p in pakiety:
        got = load_json(p/'release-manifest.json')['topic']['sha256']
        assert got == topic_sha, (p.name, got, topic_sha)

    names = files(pakiety[0])
    assert names == files(pakiety[1]), 'Różne zbiory plików'
    hashes = {n: sha256(pakiety[0]/n) for n in names}
    assert all(sha256(pakiety[1]/n) == h for n, h in hashes.items()), 'Różne bajty'
    sums = [sha256(p/'SHA256SUMS') for p in pakiety]
    assert sums[0] == sums[1], sums
    print('Identyczne bajty wszystkich', len(names), 'plików; SHA256SUMS', sums[0], flush=True)

    checks = {}
    for p in pakiety:
        r = subprocess.run([sys.executable, str(REPO/'scripts/check_tematy_package.py'), '--package-dir', str(p),
                            '--manifest', str(MANIFEST), '--config', str(CONFIG)],
                           capture_output=True, text=True, cwd=REPO)
        assert r.returncode == 0, (p.name, r.returncode, r.stdout[-2000:], r.stderr[-2000:])
        out = json.loads(r.stdout)
        assert out.get('status') == 'pass', (p.name, out)
        checks[p.name] = {'exit': r.returncode, 'status': out.get('status'), 'wynik': out}
        print('Checker', p.name, out.get('status'), flush=True)

    summary = load_json(pakiety[0]/'reports/summary.json')
    proof = {
        'topic': args.topic,
        'topic_sha256': topic_sha,
        'code_identity': identities[0],
        'git_status_config_scripts': 'pusty',
        'budowy': times,
        'pakiety': [str(p.relative_to(REPO)) for p in pakiety],
        'sha256sums_sha256': sums[0],
        'files_sha256': hashes,
        'all_files_identical': True,
        'checker': {k: {'exit': v['exit'], 'status': v['status']} for k, v in checks.items()},
        'checker_wynik_a': checks[pakiety[0].name]['wynik'],
        'summary': kluczowe(summary),
    }
    Path(args.output).write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Zapisano', args.output, flush=True)


if __name__ == '__main__':
    main()
