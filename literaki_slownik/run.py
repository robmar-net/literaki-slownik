"""Oddzielne statusy etapów oraz gotowości wydania."""
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import subprocess
from .canonical import load_json, write_json
from .inputs import GeneratorError

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


def create_run(path, inputs):
    path = Path(path)
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError as error:
        raise GeneratorError('Katalog przebiegu już istnieje; wybierz nowy', 4, str(path)) from error
    (path / 'reports').mkdir()
    write_json(path / 'manifest.json', {
        'schema_version': 1, 'readiness': 'INCOMPLETE', 'created': now(), 'inputs': inputs,
        'code': code_identity(),
        'stages': {name: {'status': 'pending'} for name in STAGES},
    })


def set_stage(path, stage, status, details=None):
    if stage not in STAGES or status not in {'running', 'complete', 'failed'}:
        raise GeneratorError('Niepoprawny etap/status', 4)
    target = Path(path) / 'manifest.json'
    manifest = load_json(target)
    if manifest['readiness'] in {'VERIFIED', 'FROZEN'}:
        raise GeneratorError(f'Przebieg ma status {manifest["readiness"]}; zmiany po verify są niedozwolone', 5)
    manifest['readiness'] = 'INCOMPLETE'
    manifest['stages'][stage] = {'status': status, 'updated': now(), **(details or {})}
    write_json(target, manifest)
