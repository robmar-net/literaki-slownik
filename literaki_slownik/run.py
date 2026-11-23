"""Oddzielne statusy etapów oraz gotowości wydania."""
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
from .canonical import load_json, write_json
from .inputs import GeneratorError, inspect_sources

STAGES = ('preflight', 'import_sgjp', 'import_kwjp', 'constructions', 'decisions', 'links', 'reports')


def now():
    return datetime.now(timezone.utc).isoformat()


def code_identity():
    """Tożsamość kodu generatora: hash plików pakietu oraz stan git (K8).

    Hash obejmuje posortowane *.py i schema.sql; git_dirty=None oznacza brak
    dostępu do repozytorium i jest traktowany przez verify jako odmowa.
    Nieśledzony plik w pakiecie też oznacza dirty: nie da się go odtworzyć z commitu.
    """
    package = Path(__file__).resolve().parent
    digest = hashlib.sha256()
    for path in sorted([*package.glob('*.py'), package / 'schema.sql']):
        digest.update(path.name.encode('utf-8') + b'\0' + hashlib.sha256(path.read_bytes()).digest())
    commit = dirty = None
    try:
        root = package.parent
        commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, capture_output=True,
                                text=True, check=True, timeout=30).stdout.strip() or None
        status = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=normal', '--', 'literaki_slownik'],
                                cwd=root, capture_output=True, text=True, check=True, timeout=30).stdout
        dirty = bool(status.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return {'tree_sha256': digest.hexdigest(), 'git_commit': commit, 'git_dirty': dirty}


def _leftover_start(path):
    """Resztka nieudanego startu: bez build.sqlite, pusty reports/, etapy pending (albo brak manifestu)."""
    names = {entry.name for entry in path.iterdir()}
    temporary = {name for name in names if name.startswith('.manifest.json-')}
    if not names - temporary <= {'manifest.json', 'reports'}:
        return False
    if (path / 'reports').exists() and (not (path / 'reports').is_dir() or any((path / 'reports').iterdir())):
        return False
    if 'manifest.json' not in names:
        return True
    try:
        stages = load_json(path / 'manifest.json')['stages']
        return set(stages) == set(STAGES) and all(stages[name] == {'status': 'pending'} for name in STAGES)
    except (OSError, ValueError, KeyError, TypeError):
        return False


def create_run(path, inputs, work_root=None, work_volume=None):
    """Nowy przebieg. Z work_root: katalog W/<nazwa> i na końcu symlink path → W/<nazwa> (R1)."""
    link = Path(path)
    if os.path.lexists(link):
        raise GeneratorError('Katalog przebiegu już istnieje; wybierz nowy', 4, str(link))
    target = link
    if work_root is not None:
        target = Path(work_root) / link.name
        if not link.parent.is_dir():
            raise GeneratorError('Brak katalogu nadrzędnego przebiegu', 4, str(link.parent))
        if target.is_dir() and not target.is_symlink() and _leftover_start(target):
            shutil.rmtree(target)
    try:
        target.mkdir(parents=False, exist_ok=False)
    except FileExistsError as error:
        raise GeneratorError('Katalog przebiegu już istnieje; wybierz nowy', 4, str(target)) from error
    except FileNotFoundError as error:
        raise GeneratorError('Brak katalogu nadrzędnego przebiegu', 4, str(target.parent)) from error
    (target / 'reports').mkdir()
    started = now()
    write_json(target / 'manifest.json', {
        'schema_version': 1, 'readiness': 'INCOMPLETE', 'created': started, 'inputs': inputs,
        'code': code_identity(),
        'stages': {name: {'status': 'pending'} for name in STAGES},
        'work_volume': work_volume,
        'build_attempts': [{'attempt': 1, 'started': started, 'ended': None, 'first_stage': STAGES[0],
                            'last_stage': None, 'outcome': None, 'exit_code': None}],
        'resume': {'resumed': False, 'count': 0},
    })
    if target != link:
        os.symlink(os.path.abspath(target), link)
    return target


def close_attempt(path, last_stage, outcome, exit_code):
    """Zamyka ostatnią próbę w build_attempts. Bez komunikatów błędów i ścieżek."""
    if outcome not in {'complete', 'incomplete', 'interrupted', 'failed'}:
        raise GeneratorError('Niepoprawny wynik próby', 4)
    target = Path(path) / 'manifest.json'
    manifest = load_json(target)
    manifest['build_attempts'][-1].update(ended=now(), last_stage=last_stage, outcome=outcome,
                                          exit_code=exit_code)
    write_json(target, manifest)


def set_stage(path, stage, status, details=None):
    if stage not in STAGES or status not in {'pending', 'running', 'complete', 'failed'}:
        raise GeneratorError('Niepoprawny etap/status', 4)
    target = Path(path) / 'manifest.json'
    manifest = load_json(target)
    if manifest['readiness'] in {'VERIFIED', 'FROZEN'}:
        raise GeneratorError(f'Przebieg ma status {manifest["readiness"]}; zmiany po verify są niedozwolone', 5)
    manifest['readiness'] = 'INCOMPLETE'
    manifest['stages'][stage] = {'status': status, 'updated': now(), **(details or {})}
    write_json(target, manifest)


def first_incomplete(stages):
    """Pierwszy etap, który nie jest complete; przy komplecie reports (raporty końcowe od nowa, znaczniki .done)."""
    return next((name for name in STAGES if stages[name]['status'] != 'complete'), STAGES[-1])


def check_identity(manifest, manifest_path):
    """Kontrole 8–9 wznowienia: ten sam kod bez zmian (4) i ten sam manifest wejść (3). Zwraca wejścia."""
    current = code_identity()
    if manifest['code']['tree_sha256'] != current['tree_sha256'] or current['git_dirty'] is not False:
        raise GeneratorError('Kod generatora różni się od kodu build albo ma niezatwierdzone zmiany', 4)
    inputs = inspect_sources(manifest_path)
    if inputs['manifest_sha256'] != manifest['inputs']['manifest_sha256']:
        raise GeneratorError('Manifest wejść różni się od manifestu build', 3)
    return inputs


def begin_resume(path, first=None):
    """Krok 12: running → failed, otwarta próba → interrupted, nowa próba, resume + 1. Zwraca pierwszy etap."""
    target = Path(path) / 'manifest.json'
    manifest = load_json(target)
    started = now()
    running = [name for name in STAGES if manifest['stages'][name]['status'] == 'running']
    for name in running:
        manifest['stages'][name] = {'status': 'failed', 'updated': started,
                                    'reason': 'proces przerwany bez zamknięcia etapu'}
    attempts = manifest.setdefault('build_attempts', [])
    if attempts and attempts[-1]['ended'] is None:
        attempts[-1].update(ended=started, outcome='interrupted',
                            last_stage=running[-1] if running else attempts[-1]['last_stage'])
    first = first or first_incomplete(manifest['stages'])
    attempts.append({'attempt': len(attempts) + 1, 'started': started, 'ended': None, 'first_stage': first,
                     'last_stage': None, 'outcome': None, 'exit_code': None})
    count = (manifest.get('resume') or {}).get('count', 0)
    manifest['resume'] = {'resumed': True, 'count': count + 1}
    manifest['readiness'] = 'INCOMPLETE'
    write_json(target, manifest)
    return first
