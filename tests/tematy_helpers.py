"""Mała fikstura TEMATY: własne kopie konfiguracji i hashe fikstury, bez prawdziwych pinów."""
import json
import os
from pathlib import Path
from literaki_slownik.canonical import sha256, write_json

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT/'config/generator'
TEXTS = ('ATTRIBUTIONS-tematy.md', 'LIMITATIONS.md', 'TERMS.md')
PATH_INPUTS = ('base_run', 'database', 'release_manifest', 'standard', 'broad',
               'base_pop', 'base_pop00', 'plwordnet_db', 'iate')


def config_fixture(root):
    """Konfiguracja metody, temat i manifest wejść w `root`; pliki wejść to zaślepki."""
    root = Path(root)
    texts, inputs = root/'tematy-teksty', root/'inputs'
    for p in (texts, inputs, root/'tematy'):
        p.mkdir(parents=True)
    for name in TEXTS:
        (texts/name).write_text('# Fikstura ' + name + '\n', encoding='utf-8')
    method = json.loads((CONFIG/'tematy.json').read_text(encoding='utf-8'))
    method['teksty'] = {name: {'path': 'tematy-teksty/' + name, 'sha256': sha256(texts/name)}
                        for name in TEXTS}
    config = root/'tematy.json'
    write_json(config, method)
    topic = root/'tematy/morze.json'
    topic.write_bytes((CONFIG/'tematy/morze.json').read_bytes())
    refs = {}
    for key in PATH_INPUTS:
        path = inputs/(key + '.bin')
        path.write_bytes(key.encode() + b'\n')
        refs[key] = {'path': os.path.relpath(path, root), 'sha256': sha256(path)}
    refs['plwordnet_zip'] = {'url': 'https://example.invalid/plwn.zip', 'retrieved_at': '2026-10-28T00:00:00Z',
                             'bytes': 1, 'sha256': '0' * 64}
    refs['iate'].update({'url': 'https://example.invalid/iate.zip', 'retrieved_at': '2026-10-28T00:00:00Z',
                         'last_modified': 'Mon, 30 Sep 2019 07:41:10 GMT', 'member': 'iate.tbx', 'bytes': 5})
    manifest = root/'tematy-sources.json'
    write_json(manifest, {'schema_version': 1, 'version': 'tematy-sources-v1', 'inputs': refs})
    return {'root': root, 'config': config, 'topic': topic, 'manifest': manifest, 'texts': texts}


def rewrite(path, change):
    """Wczytaj JSON, zmień go funkcją `change` i zapisz kanonicznie."""
    path = Path(path)
    value = json.loads(path.read_text(encoding='utf-8'))
    change(value)
    write_json(path, value)
