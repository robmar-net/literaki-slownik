"""Kontrola jawnych artefaktów, ról i metadanych przed importem."""
from pathlib import Path
import re
from .canonical import load_json, sha256


class GeneratorError(Exception):
    def __init__(self, message, code=3, source=None, row=None):
        super().__init__(message)
        self.code, self.source, self.row = code, source, row

    def diagnostic(self):
        return {'code': self.code, 'message': str(self), 'source': self.source, 'row': self.row}


KINDS = {'sgjp_tab': ('lexical', 'SGJP'),
         'kwjp_lemma': ('corpus_evidence', 'KWJP'),
         'kwjp_orth': ('corpus_evidence', 'KWJP'),
         'kwjp_orth_lc': ('corpus_evidence', 'KWJP'),
         'kwjp_bigram': ('corpus_evidence', 'KWJP')}
REQUIRED = ('source_id', 'version', 'url', 'retrieved_at', 'authors', 'license',
            'license_scope', 'used_for', 'attribution', 'dependencies')


def checked_file(base, reference):
    if not isinstance(reference, dict) or not isinstance(reference.get('path'), str):
        raise GeneratorError('Nieprawidłowe odwołanie do pliku', 2)
    expected = reference.get('sha256')
    if not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
        raise GeneratorError('Nieprawidłowy SHA256', 2, reference['path'])
    path = (base / reference['path']).resolve()
    if not path.is_file():
        raise GeneratorError('Brak zwykłego pliku', 3, str(path))
    if sha256(path) != expected:
        raise GeneratorError('Niezgodny SHA256', 3, str(path))
    return path


def inspect_sources(manifest_path):
    path = Path(manifest_path).resolve()
    try:
        manifest = load_json(path)
        if (not isinstance(manifest, dict) or type(manifest.get('schema_version')) is not int
                or manifest['schema_version'] != 1 or manifest.get('project') != 'literaki-slownik'):
            raise GeneratorError('Nieobsługiwany schemat manifestu', 2, str(path))
        mode = manifest.get('mode')
        if mode not in {'production', 'test'}:
            raise GeneratorError('Manifest wymaga jawnego trybu production/test', 2)
        artifacts = manifest.get('artifacts')
        if not isinstance(artifacts, list) or not artifacts:
            raise GeneratorError('Brak aktywnych artefaktów', 2)
        seen, results = set(), []
        for artifact in artifacts:
            if not isinstance(artifact, dict) or any(not isinstance(artifact.get(k), str) or not artifact[k] for k in REQUIRED):
                raise GeneratorError('Brak wymaganych metadanych źródła', 2)
            sid = artifact['source_id']
            if sid in seen:
                raise GeneratorError('Powtórzony source_id', 2, sid)
            seen.add(sid)
            expected = KINDS.get(artifact.get('kind'))
            if not expected or artifact.get('role') != expected[0]:
                raise GeneratorError('Niedopuszczony typ lub rola źródła', 3, sid)
            origin = artifact.get('origin')
            if origin != expected[1] and not (mode == 'test' and origin == 'synthetic'):
                raise GeneratorError('Wyłączone lub nieustalone pochodzenie', 3, sid)
            if artifact.get('status') != 'ALLOWED':
                raise GeneratorError('Artefakt nie jest ALLOWED', 3, sid)
            counts = artifact.get('expected_counts', {})
            metrics = ({'records', 'interpretations', 'duplicates', 'expanded_alternatives',
                        'lexemes', 'original_forms'} if artifact['kind'] == 'sgjp_tab'
                       else {'records', 'sum_freq'})
            if (not isinstance(counts, dict) or set(counts) - metrics
                    or any(type(value) is not int or value < 0 for value in counts.values())):
                raise GeneratorError('Nieprawidłowe jednostki expected_counts', 2, sid)
            evidence = artifact.get('evidence')
            if not isinstance(evidence, list) or not evidence:
                raise GeneratorError('Brak dowodów warunków użycia', 3, sid)
            checked = checked_file(path.parent, artifact)
            for item in evidence:
                checked_file(path.parent, item)
            results.append({**artifact, 'resolved_path': str(checked)})
        configurations = manifest.get('configurations')
        if not isinstance(configurations, dict):
            raise GeneratorError('Brak configurations', 2)
        for item in configurations.values():
            checked_file(path.parent, item)
        if mode == 'production':
            if sum(a['kind'] == 'sgjp_tab' for a in artifacts) != 1 or len(artifacts) != 14:
                raise GeneratorError('Pełny manifest wymaga jednego SGJP i 13 list KWJP', 3)
            slots = {(kind, genre) for kind in ('kwjp_lemma', 'kwjp_orth', 'kwjp_orth_lc')
                     for genre in ('all', 'fakt', 'fikcja', 'publicystyka')}
            slots.add(('kwjp_bigram', 'all'))
            actual = {(a['kind'], a.get('genre')) for a in artifacts if a['kind'] != 'sgjp_tab'}
            if actual != slots:
                raise GeneratorError('Brak odrębnej wymaganej listy KWJP lub powtórzony gatunek', 3)
            if any(not a.get('expected_counts') for a in artifacts):
                raise GeneratorError('Brak oczekiwanych metryk pełnego importu', 2)
        return {'mode': mode, 'manifest_sha256': sha256(path), 'manifest_path': str(path),
                'artifacts': results, 'manifest': manifest}
    except GeneratorError:
        raise
    except (OSError, ValueError, TypeError) as error:
        raise GeneratorError(f'Nie można sprawdzić manifestu: {error}', 2, str(path)) from error
