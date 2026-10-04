import hashlib
import json
from pathlib import Path


def fixture_manifest(directory):
    directory = Path(directory)
    source = directory / 'source.gz'
    source.write_bytes(b'fixture')
    notice = directory / 'notice.txt'
    notice.write_text('Własne dane testowe', encoding='utf-8')
    manifest = {
        'schema_version': 1, 'project': 'literaki-slownik', 'mode': 'test',
        'artifacts': [{
            'source_id': 'synthetic', 'kind': 'sgjp_tab', 'role': 'lexical',
            'origin': 'synthetic', 'status': 'ALLOWED', 'path': source.name,
            'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'version': 'fixture-v1', 'url': 'synthetic:own', 'retrieved_at': 'fixture',
            'authors': 'Projekt', 'license': 'własna fikstura',
            'license_scope': 'test', 'used_for': 'generator',
            'attribution': 'Własne dane', 'dependencies': 'brak',
            'evidence': [{'path': notice.name,
                          'sha256': hashlib.sha256(notice.read_bytes()).hexdigest()}],
        }], 'configurations': {}, 'unavailable': [{'source_id': 'NKJP', 'reason': 'BLOCKED'}],
    }
    path = directory / 'sources.json'
    path.write_text(json.dumps(manifest), encoding='utf-8')
    return path, manifest


def rewrite(path, manifest):
    path.write_text(json.dumps(manifest), encoding='utf-8')
