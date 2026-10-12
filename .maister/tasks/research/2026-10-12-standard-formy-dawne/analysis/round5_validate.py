"""Kontrola kompletności artefaktów badania; bez zmiany list produkcyjnych."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

TASK = Path(__file__).resolve().parents[1]
ROOT = TASK.parents[3]
OUT = TASK / 'analysis/findings/round5'


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []
    all_json = list(OUT.glob('*.json'))
    for path in all_json:
        load(path)
    checks.append(f'Parsowanie {len(all_json)} JSON')
    manifest = load(OUT / 'input-manifest.json')
    hashes = {
        'config_sha256': ROOT / 'config/generator/pop.json',
        'source_manifest_sha256': ROOT / 'config/generator/pop-sources.json',
        'production_code_sha256': ROOT / 'literaki_slownik/pop.py',
        'proposal_sha256': TASK / 'analysis/findings/round3/proposal.json',
        'script_sha256': TASK / 'analysis/round5_measure.py',
    }
    for key, path in hashes.items():
        assert sha(path) == manifest[key], (key, path)
    checks.append('Niezmienione wejścia, konfiguracja i kod pomiaru zgodne z manifestem')
    summary = load(OUT / 'quality-summary.json')
    assert summary['all_cases']['n'] == 300
    assert sum(summary['all_cases']['classes'].values()) == 300
    for name, digest in summary['source_hashes'].items():
        assert sha(OUT / name) == digest, name
    assert summary['contexts']['read_case_contexts'] == 632
    assert summary['crosscheck']['n'] == 30
    assert summary['crosscheck']['agreement'] == 22
    a = load(OUT / 'quality-a-source-access.json')
    b = load(OUT / 'quality-b-post-freeze.json')
    assert a['frozen_matrix']['unchanged']
    assert a['frozen_matrix']['current_sha256'] == sha(OUT / 'quality-a.json')
    assert b['frozen_matrix_sha256'] == sha(OUT / 'quality-b.json')
    assert not b['frozen_classes_modified']
    assert sum(len(c['sources']) for c in a['cases']) == 36
    assert all(s.get('open_attempt') for c in a['cases'] for s in c['sources'])
    assert b['summary']['original_urls_attempted'] == 19
    checks.append('300 zamrożonych ocen, 30 kontroli i próby dostępu do 55 źródeł')
    for name in ('baseline', 'proposal'):
        assert len(load(OUT / f'{name}-measurements.json')['variants']) == 27
        assert len(load(OUT / f'{name}-dispersion-grid.json')['grid']) == 25
    checks.append('27 pełnych wariantów i 25 pól siatki na każdy STANDARD')

    def no_raw_contexts(value):
        if isinstance(value, dict):
            assert not {'left', 'right'}.intersection(value)
            for v in value.values():
                no_raw_contexts(v)
        elif isinstance(value, list):
            for v in value:
                no_raw_contexts(v)

    for name in ('quality-a.json', 'quality-b.json', 'context-manifest.json'):
        no_raw_contexts(load(OUT / name))
    checks.append('Publiczne macierze bez surowych kontekstów left/right')
    markdowns = list(OUT.glob('*.md')) + [TASK / 'outputs/pop-calibration.md', TASK / 'analysis/synthesis-round5.md', TASK / 'planning/round5-plan.md']
    count = 0
    for path in markdowns:
        text = path.read_text()
        assert text.startswith('# '), path
        for heading in ('## TL;DR', '## Key Decisions', '## Open Questions / Risks'):
            assert heading in text, (path, heading)
        assert '<!-- QUALITY_TABLE -->' not in text and '<!-- RECOMMENDATION -->' not in text
        for target in re.findall(r'\]\(([^)]+)\)', text):
            target = target.strip('<>').split('#')[0]
            if not target or re.match(r'^[a-z]+:', target):
                continue
            assert (path.parent / unquote(target)).exists(), (path, target)
            count += 1
    checks.append(f'Nagłówki wymagane i {count} odsyłaczy lokalnych Markdown')
    changed = subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).splitlines()
    assert all(p.startswith(str(TASK.relative_to(ROOT)) + '/') for p in changed), changed
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    checks.append('Zmiany śledzone tylko w zadaniu; git diff --check poprawny')
    result = {'status': 'passed', 'checked_at': subprocess.check_output(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], text=True).strip(),
              'checks': checks, 'source_coverage': {'required_categories': 5, 'covered': 5, 'external_quality_source_attempts': 55,
                                                 'relevant_fragments_read': 40, 'observed_access_limits': 15},
              'tests': '25 istniejących testów POP przeszło w niezależnym przeglądzie; nie powtarzano po samych zmianach raportowych.',
              'limits': ['Nie odtworzono niezależnie całego grafu i morfologii.', 'Zamrożone klasy zachowują historię sprzed korekt źródłowych.', 'Nie zbadano rozpoznawalności słów przez graczy.'],
              'implementation_changed': False}
    path = OUT / 'validation.json'
    if path.exists() and 'visual_preview' in load(path):
        result['visual_preview'] = load(path)['visual_preview']
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
