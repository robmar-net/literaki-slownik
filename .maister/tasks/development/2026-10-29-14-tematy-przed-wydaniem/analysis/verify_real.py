"""Kopia z #13 (#14: seria 10 tematów; morze bez --fala).

Odbiór budów a/b jednego tematu: czysty kod, identyczne bajty, checker PASS na obu.

Kopia skryptu z #11 (`2026-10-28-11-tematy-morze/analysis/verify_real.py`) z argumentami
--topic, --a, --b. Budowy robi CLI `tematy`; ten skrypt ich nie uruchamia, tylko sprawdza
i zapisuje dowód. Czasy budów podaje się argumentem --times (JSON {a: {start, end, exit}, b: {...}}).

#12 W12 (grupa 12): `--fala` dokłada kontrolę fali 1. T3 niepuste tylko w medycynie; IATE tylko
w medycynie (`inputs`, blok `iate`, ATTRIBUTIONS.md, TERMS.md, LIMITATIONS.md), a w innych
tematach nigdzie w pakiecie (także w rozpakowanych .gz); `srodladowe` = null we wszystkich 9.
"""
import argparse
import gzip
import re
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


# #13: medycyna v2 bez T3, więc żaden temat nie ma T3 ani IATE.
Z_T3 = set()
IATE_PLIKI = ('ATTRIBUTIONS.md', 'TERMS.md', 'LIMITATIONS.md')
# Całe słowo: „kwiatek”, „świateł” zawierają „iate” i nie są IATE.
IATE_RE = re.compile(r'(?<![^\W\d_])iate(?![^\W\d_])', re.IGNORECASE)


def tekst(path):
    data = path.read_bytes()
    return (gzip.decompress(data) if path.suffix == '.gz' else data).decode('utf-8')


def kontrola_fali(topic_id, pakiet, summary):
    """Kontrola W12 (#12): T3 i IATE tylko w medycynie, `srodladowe` = null wszędzie."""
    manifest = load_json(pakiet/'release-manifest.json')
    t3_liczba = summary['liczby']['warstwy'].get('T3', 0)
    # #13: kopia pliku tematu pomija skan; `uwagi` medycyny v2 opisują usunięcie IATE (nie atrybucja).
    iate_w_plikach = {n: len(IATE_RE.findall(tekst(pakiet/n))) for n in files(pakiet) if n != f'tematy/{topic_id}.json'}
    iate_w_plikach = {n: c for n, c in iate_w_plikach.items() if c}
    wynik = {
        'temat': topic_id,
        't3_wpisy': t3_liczba,
        'summary_t3_null': summary.get('t3') is None,
        'srodladowe_null': summary.get('srodladowe') is None,
        'iate_w_inputs': 'iate' in manifest['inputs'],
        'iate_blok_manifestu': 'iate' in manifest,
        'iate_w_plikach': iate_w_plikach,
    }
    bledy = []
    if not wynik['srodladowe_null']:
        bledy.append('srodladowe nie jest null')
    if topic_id in Z_T3:
        if not t3_liczba or wynik['summary_t3_null']:
            bledy.append('medycyna bez T3')
        if not (wynik['iate_w_inputs'] and wynik['iate_blok_manifestu']):
            bledy.append('medycyna bez IATE w inputs albo bez bloku iate')
        bledy += [f'brak IATE w {n}' for n in IATE_PLIKI if n not in iate_w_plikach]
    else:
        if t3_liczba or not wynik['summary_t3_null']:
            bledy.append(f'T3 poza medycyną: {t3_liczba}')
        if wynik['iate_w_inputs'] or wynik['iate_blok_manifestu'] or iate_w_plikach:
            bledy.append(f'IATE poza medycyną: {sorted(iate_w_plikach)}')
    wynik['bledy'] = bledy
    wynik['zgodna'] = not bledy
    return wynik


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
    ap.add_argument('--fala', action='store_true', help='kontrola fali 1 (#12 W12): T3/IATE tylko w medycynie')
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
    fala = None
    if args.fala:
        topic_id = load_json(REPO/args.topic)['id']
        fala = kontrola_fali(topic_id, pakiety[0], summary)
        print('Kontrola fali', topic_id, 'zgodna' if fala['zgodna'] else 'NIEZGODNA: ' + '; '.join(fala['bledy']),
              flush=True)
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
    if fala is not None:
        proof['fala'] = fala
    Path(args.output).write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Zapisano', args.output, flush=True)
    if fala is not None and not fala['zgodna']:
        sys.exit(1)


if __name__ == '__main__':
    main()
