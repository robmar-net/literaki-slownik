"""Deterministyczny dobór próbek; bez kwalifikacji słów i automatycznego odbioru."""
import hashlib
import heapq
import re

from .canonical import dumps
from .inputs import GeneratorError

ENCODING = 'canonical JSON array [seed,stratum,key], UTF-8'


def _config(config):
    if (not isinstance(config, dict)
            or set(config) != {'version', 'seed', 'size_per_stratum', 'encoding'}
            or config['version'] != 'quality-v1'
            or config['seed'] != 'literaki-slownik-g1-v1'
            or type(config['size_per_stratum']) is not int
            or config['size_per_stratum'] != 30
            or config['encoding'] != ENCODING):
        raise GeneratorError('Nieobsługiwana konfiguracja quality-v1', 2)


def sampling_digest(seed, stratum, key):
    return hashlib.sha256(dumps([seed, stratum, key]).encode('utf-8')).hexdigest()


class _WorstFirst:
    def __init__(self, digest, key):
        self.rank = (digest, key)

    def __lt__(self, other):
        return self.rank > other.rank


def sample_strata(strata, config):
    """Każda warstwa dostarcza uporządkowane klucze, np. SQL ORDER BY key.

    Powtórzenia klucza są liczone raz. Wejście jest strumieniowane, pamięć
    ograniczona do 30 wybranych jednostek na warstwę; niesortowane odrzucamy.
    Nazwy warstw i klucze nadaje osobny etap raportów, nie ten moduł.
    """
    _config(config)
    if (not isinstance(strata, dict)
            or any(not isinstance(name, str) or not name for name in strata)):
        raise GeneratorError('Warstwy wymagają niepustych identyfikatorów', 2)
    selected_by_key, report = {}, {}
    for name in sorted(strata):
        heap, previous, population = [], None, 0
        for key in strata[name]:
            if not isinstance(key, str) or not key:
                raise GeneratorError('Nieprawidłowy stabilny klucz próbki', 4, name)
            if previous is not None and key < previous:
                raise GeneratorError('Klucze próbki nie są uporządkowane', 4, name)
            if key == previous:
                continue
            previous = key
            population += 1
            entry = _WorstFirst(sampling_digest(config['seed'], name, key), key)
            if len(heap) < config['size_per_stratum']:
                heapq.heappush(heap, entry)
            elif entry.rank < heap[0].rank:
                heapq.heapreplace(heap, entry)
        selected = [{'key': item.rank[1], 'sha256': item.rank[0]}
                    for item in sorted(heap, key=lambda item: item.rank)]
        report[name] = {'population': population, 'sample_size': len(selected),
                        'coverage': 'SAMPLED_NOT_VERIFIED' if population else 'EMPTY_NOT_COVERAGE',
                        'selected': selected}
        for item in selected:
            selected_by_key.setdefault(item['key'], []).append(name)
    return {
        'schema_version': 1, **config, 'status': 'UNREVIEWED',
        'strata': report, 'unique_selected_units': len(selected_by_key),
        'overlaps': [{'key': key, 'strata': names}
                     for key, names in sorted(selected_by_key.items()) if len(names) > 1],
    }


def review_template(sample, *, canonical_index_sha256, evidence_sha256):
    """Szablon nie zatwierdza próbki; hash wiąże go z konkretnym wynikiem."""
    def valid_hash(value):
        return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value)
    if (not valid_hash(canonical_index_sha256)
            or not isinstance(evidence_sha256, dict) or not evidence_sha256
            or any(not isinstance(key, str) or not key or not valid_hash(value)
                   for key, value in evidence_sha256.items())):
        raise GeneratorError('Przegląd wymaga hashy indeksu i dowodów', 2)
    memberships = {}
    for name, stratum in sorted(sample['strata'].items()):
        for item in stratum['selected']:
            memberships.setdefault(item['key'], []).append(name)
    return {
        'schema_version': 1, 'version': sample['version'], 'status': 'UNREVIEWED',
        'canonical_index_sha256': canonical_index_sha256,
        'sample_sha256': hashlib.sha256(dumps(sample).encode('utf-8')).hexdigest(),
        'evidence_sha256': dict(sorted(evidence_sha256.items())),
        'items': [{'key': key, 'strata': names, 'assessment': None,
                   'reviewer': None, 'source_justification': None}
                  for key, names in sorted(memberships.items())],
    }
