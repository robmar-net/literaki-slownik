"""Oddzielne statusy etapów oraz gotowości wydania."""
from datetime import datetime, timezone
from pathlib import Path
from .canonical import load_json, write_json
from .inputs import GeneratorError

STAGES = ('preflight', 'import_sgjp', 'import_kwjp', 'constructions', 'decisions', 'links', 'reports')


def now():
    return datetime.now(timezone.utc).isoformat()


def create_run(path, inputs):
    path = Path(path)
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError as error:
        raise GeneratorError('Katalog przebiegu już istnieje; wybierz nowy', 4, str(path)) from error
    (path / 'reports').mkdir()
    write_json(path / 'manifest.json', {
        'schema_version': 1, 'readiness': 'INCOMPLETE', 'created': now(), 'inputs': inputs,
        'stages': {name: {'status': 'pending'} for name in STAGES},
    })


def set_stage(path, stage, status, details=None):
    if stage not in STAGES or status not in {'running', 'complete', 'failed'}:
        raise GeneratorError('Niepoprawny etap/status', 4)
    target = Path(path) / 'manifest.json'
    manifest = load_json(target)
    if manifest['readiness'] == 'FROZEN':
        raise GeneratorError('Przebieg jest zamrożony', 5)
    manifest['readiness'] = 'INCOMPLETE'
    manifest['stages'][stage] = {'status': status, 'updated': now(), **(details or {})}
    write_json(target, manifest)
