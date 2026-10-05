#!/usr/bin/env python3
"""Sprawdza mapowanie ręcznego przeglądu PAN; nie aktywuje polityki generatora."""
import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path


def check_snapshot(path, expected):
    with Path(path).open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual != expected:
        raise ValueError('Przegląd nie odpowiada snapshotowi przypadków')


def audit(cases, review):
    if review.get('automatic_eligibility_decisions') is not False:
        raise ValueError('Ten przegląd nie może aktywować kwalifikacji')
    result = copy.deepcopy(cases['cases'])
    by_id = {case['case_id']: case for case in result}
    if len(by_id) != len(result):
        raise ValueError('Powtórzony identyfikator przypadku')
    seen = set()
    for note in review['annotations']:
        cid = note['case_id']
        if cid in seen or cid not in by_id or note['source'] != by_id[cid]['source']:
            raise ValueError('Powtórzone lub niezgodne mapowanie źródłowe')
        if note['scope'] != 'documented_use_only' or note['eligibility_status'] != 'unresolved':
            raise ValueError('Dowód jednego użycia nie rozstrzyga wszystkich znaczeń ani gry')
        evidence = note['evidence']
        if not evidence or any(ref['source_id'] not in review['sources'] or not ref.get('locator') for ref in evidence):
            raise ValueError('Brak śladu dokumentacji')
        if any(review['sources'][ref['source_id']].get('role') != 'documentary_observation_only' for ref in evidence):
            raise ValueError('Niezgodna rola źródła')
        by_id[cid]['review'] = copy.deepcopy(note)
        seen.add(cid)
    coverage = Counter(cases=len(result), documented_use_cases=len(seen),
                       without_documented_use_review=len(result) - len(seen),
                       eligibility_unresolved=len(result))
    classes = Counter(note['semantic_class'] for note in review['annotations'])
    norm = Counter(note['normative_status'] for note in review['annotations'])
    return {'schema_version': 1, 'automatic_eligibility_decisions': False,
            'full_semantic_mapping_complete': False, 'coverage': dict(coverage),
            'documented_use_classes': dict(sorted(classes.items())),
            'normative_review_statuses': dict(sorted(norm.items())),
            'cases': result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    review = json.loads(args.review.read_text())
    check_snapshot(args.cases, review['cases_sha256'])
    result = audit(json.loads(args.cases.read_text()), review)
    result['cases_sha256'] = review['cases_sha256']
    with args.review.open('rb') as stream:
        result['review_sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(result['coverage'], ensure_ascii=False))


if __name__ == '__main__':
    main()
