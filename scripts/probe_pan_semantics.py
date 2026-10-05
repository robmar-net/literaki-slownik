#!/usr/bin/env python3
"""Pełny rejestr frag i kandydatów dowodowych PAN; bez werdyktów gry."""
import argparse
import csv
import gzip
import hashlib
import json
import re
import sqlite3
import tarfile
import unicodedata
from collections import Counter
from pathlib import Path


def key(text):
    return unicodedata.normalize('NFC', text).lower()


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def probe(database, samples, lists):
    cases = {}
    with sqlite3.connect(Path(database).resolve().as_uri() + '?mode=ro', uri=True) as db:
        query = 'SELECT source_id,row_number,form,lemma,tag,names,qualifiers FROM sgjp_record'
        for sid, row, original, lemma, tag, names, qualifiers in db.execute(query + " WHERE tag='frag' ORDER BY source_id,row_number"):
            identity = (sid, original, lemma, tag, names, qualifiers)
            if identity not in cases:
                case_id = hashlib.sha256(json.dumps(identity, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
                cases[identity] = {
                    'case_id': case_id,
                    'source': dict(source_id=sid, original=original, lemma_id=lemma,
                                   tag=tag, names=names, qualifiers=qualifiers, row_numbers=[]),
                    'lookup_key': key(original), 'other_source_analyses': [],
                    'corpus_candidates': [], 'sample_matches': [],
                    'semantic_status': 'unresolved',
                    'mapping_status': 'spelling_candidates_only_not_meaning_alignment',
                }
            cases[identity]['source']['row_numbers'].append(row)
        by_key = {}
        for case in cases.values():
            by_key.setdefault(case['lookup_key'], []).append(case)
        alternatives = {}
        # Czytamy wszystkie surowe rekordy, aby nie utracić odmiennej pisowni/homonimu.
        for sid, row, original, lemma, tag, names, qualifiers in db.execute(query + ' ORDER BY source_id,row_number'):
            if key(original) not in by_key:
                continue
            identity = (sid, original, lemma, tag, names, qualifiers)
            if identity not in alternatives:
                alternatives[identity] = dict(source_id=sid, original=original, lemma_id=lemma,
                                              tag=tag, names=names, qualifiers=qualifiers, row_numbers=[])
            alternatives[identity]['row_numbers'].append(row)
        for identity, analysis in alternatives.items():
            for case in by_key[key(analysis['original'])]:
                if case['source'] != analysis:
                    case['other_source_analyses'].append(analysis)
        assert db.total_changes == 0

    sources = []
    corpus_records = {}
    for source in lists:
        path = Path(source['path'])
        source_hash = digest(path)
        if source.get('sha256') and source['sha256'] != source_hash:
            raise ValueError('Niezgodny hash listy: ' + str(path))
        sources.append({k: v for k, v in source.items() if k != 'path'} | {'sha256': source_hash})
        with gzip.open(path, 'rt', encoding='utf-8', newline='') as stream:
            rows = csv.reader(stream)
            header = next(rows)
            for rank, row in enumerate(rows, 1):
                units = row[:2] if source['kind'] == 'kwjp_bigram' else row[:1]
                targets = {key(unit) for unit in units} & by_key.keys()
                if not targets:
                    continue
                record_id = source['source_id'] + ':' + str(rank)
                metric_start = 2 if source['kind'] in ('kwjp_lemma', 'kwjp_bigram') else 1
                corpus_records[record_id] = {
                    'source_id': source['source_id'], 'row_number': rank,
                    'units': units, 'pos': row[1] if source['kind'] == 'kwjp_lemma' else None,
                    'frequency_original': row[metric_start],
                    'method': 'NFC_lower_spelling_candidate_not_sense_proof',
                }
                for target in sorted(targets):
                    for case in by_key[target]:
                        case['corpus_candidates'].append(record_id)

    sample_files = sample_units = 0
    bibliography = {}
    with tarfile.open(samples) as archive:
        for member in sorted(archive.getmembers(), key=lambda m: m.name):
            if not member.isfile():
                continue
            obj = json.load(archive.extractfile(member))
            sample_files += 1
            for position, sample in enumerate(obj['samples']):
                sample_units += 1
                tokens = re.findall(r'(?<![\w-])\w+(?![\w-])', unicodedata.normalize('NFC', sample['text']))
                matches = {}
                for token in tokens:
                    if key(token) in by_key:
                        matches.setdefault(key(token), []).append(token)
                for target, matched in sorted(matches.items()):
                    bibliography[member.name] = obj['meta']
                    proof = {'file': member.name, 'sample_index': position,
                             'matched_forms': matched,
                             'method': 'whole_token_NFC_lower_candidate_not_sense_proof'}
                    for case in by_key[target]:
                        case['sample_matches'].append(proof)

    ordered = sorted(cases.values(), key=lambda c: (c['source']['source_id'], c['source']['row_numbers'][0]))
    coverage = Counter()
    for case in ordered:
        coverage['cases'] += 1
        coverage['with_other_source_analyses'] += bool(case['other_source_analyses'])
        coverage['with_corpus_candidates'] += bool(case['corpus_candidates'])
        coverage['with_sample_matches'] += bool(case['sample_matches'])
        coverage['without_corpus_or_sample_match'] += not (case['corpus_candidates'] or case['sample_matches'])
        coverage['semantic_unresolved'] += case['semantic_status'] == 'unresolved'
    return {'schema_version': 1, 'scope': 'all_source_frag_compact_analyses_only_not_all_semantic_exceptions',
            'automatic_eligibility_decisions': False, 'source_lists': sources,
            'corpus_records': corpus_records, 'sample_bibliography': bibliography,
            'samples': {'sha256': digest(samples), 'files_inspected': sample_files,
                        'sample_units_inspected': sample_units},
            'coverage': dict(coverage), 'cases': ordered}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--samples', type=Path, required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.sources.read_text())
    lexical = [entry for entry in manifest['artifacts'] if entry['kind'] == 'sgjp_tab']
    if len(lexical) != 1 or lexical[0]['status'] != 'ALLOWED' or lexical[0]['role'] != 'lexical':
        raise ValueError('Wymagane jedno dopuszczone wejście SGJP')
    with sqlite3.connect(args.database.resolve().as_uri() + '?mode=ro', uri=True) as db:
        stored = list(db.execute("SELECT source_id,metadata FROM source_artifact WHERE kind='sgjp_tab'"))
        if len(stored) != 1 or stored[0][0] != lexical[0]['source_id'] or json.loads(stored[0][1])['sha256'] != lexical[0]['sha256']:
            raise ValueError('Baza nie odpowiada przypiętemu SGJP')
    lists = []
    for entry in manifest['artifacts']:
        if entry['origin'] == 'KWJP':
            if entry['status'] != 'ALLOWED' or entry['role'] != 'corpus_evidence':
                raise ValueError('Lista poza dopuszczoną rolą')
            lists.append(entry | {'path': args.sources.parent / entry['path']})
    result = probe(args.database, args.samples, lists)
    result['lexical_source'] = {k: lexical[0][k] for k in ('source_id', 'version', 'sha256', 'url', 'license')}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Nowy plik wynikowy; nie nadpisujemy wcześniejszych dowodów.
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(result['coverage'], ensure_ascii=False))


if __name__ == '__main__':
    main()
