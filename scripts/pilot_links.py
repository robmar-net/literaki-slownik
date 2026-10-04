#!/usr/bin/env python3
"""Ilustracyjny pilotaż SGJP/KWJP: brak imputacji i rozdzielania częstości."""
import csv
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/analysis/findings'
FORMS = {'kot', 'kotem', 'zamek', 'mam', 'róża', 'Róża', 'em', 'czytał', 'czytałem', 'czytałbym', 'polsku', 'dwa', 'sto'}
LEMMAS = {'kot', 'zamek', 'mieć', 'mama', 'róża', 'Róża', 'em', 'czytać', 'polski', 'dwa', 'sto', 'być'}


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    source = ROOT / 'cache/sgjp/sgjp-20260823.tab.gz'
    form_rows = defaultdict(list)
    lemma_ids = defaultdict(set)
    with gzip.open(source, 'rt') as f:
        for line in f:
            if line.strip() == '#</COPYRIGHT>':
                break
        for line in f:
            row = line.rstrip('\n').split('\t')
            form, lemma, tag, _, _ = row
            if form in FORMS:
                form_rows[form].append(row)
            base = lemma.split(':')[0]
            if base in LEMMAS:
                lemma_ids[base, tag.split(':')[0]].add(lemma)
    source_hashes = {source.name: sha(source)}
    form_output = {}
    lemma_output = []
    for kind in ['orth', 'orth_lc', 'lemma']:
        path = ROOT / f'cache/kwjp/kwjp100-slowa-{kind}-all.csv.gz'
        source_hashes[path.name] = sha(path)
        found = {}
        with gzip.open(path, 'rt') as f:
            reader = csv.reader(f)
            header = next(reader)
            for number, row in enumerate(reader, 1):
                if kind == 'lemma':
                    if row[0] not in LEMMAS:
                        continue
                    candidates = sorted(lemma_ids[row[0], row[1]])
                    lemma_output.append({'corpus_unit': row[:2], 'published_metrics': dict(zip(header[2:], row[2:])),
                                         'sgjp_lemma_ids': candidates,
                                         'link_status': 'UNMATCHED' if not candidates else ('AMBIGUOUS' if len(candidates)>1 else 'EXACT_LEMMA_POS_CANDIDATE'),
                                         'availability': 'OBSERVED', 'source_row': number,
                                         'note': 'Częstość pozostaje przy jednostce korpusowej; zgodność napisu i POS nie dowodzi tożsamości znaczenia.'})
                elif row[0] in FORMS:
                    found[row[0]] = {'availability': 'OBSERVED', 'published_metrics': dict(zip(header[1:], row[1:])), 'source_row': number}
        if kind != 'lemma':
            form_output[kind] = []
            for form in sorted(FORMS):
                evidence = found.get(form)
                # Pełne formy osobowe nie są porównywalne z segmentacją korpusu.
                unavailable = 'UNMATCHED' if form in {'czytałem', 'czytałbym'} else 'NOT_IN_PUBLISHED_LIST'
                reason = 'niepotwierdzona porównywalność jednostki lub zakres listy'
                if kind == 'orth_lc' and form != form.lower():
                    unavailable = 'UNMATCHED'
                    reason = 'Lista orth_lc scala wielkość liter; brak osobnej jednostki Róża nie jest brakiem poświadczenia. Jednostka róża jest pokazana osobno.'
                form_output[kind].append({'form': form, 'sgjp_rows': form_rows[form],
                                          'kwjp': evidence or {'availability': unavailable, 'published_metrics': None, 'reason': reason},
                                          'nkjp': {'availability': 'UNAVAILABLE', 'reason': 'BLOCKED_LICENSE_UNRESOLVED'}})
    result = {'selection': '13 form i 12 napisów lematów dobranych jawnie dla ilustracji, nie próba losowa jakości',
              'method': 'Dokładny napis, rozróżnianie wielkości; suffix homonimii oddzielony tylko na potrzeby klucza łączenia, nigdy usunięty z ID. POS bez mapowania; niezgodności pozostają UNMATCHED.',
              'source_sha256': source_hashes, 'script_sha256': sha(Path(__file__)),
              'forms': form_output, 'lemmas': lemma_output,
              'checks': {'no_frequency_allocation_to_lexemes': True, 'no_missing_as_zero': True, 'no_nkjp_usage': True}}
    (OUT / 'pilot-links.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    from collections import Counter
    print(json.dumps({'lemma_link_statuses': dict(Counter(r['link_status'] for r in lemma_output)), 'form_units_per_list': len(FORMS)},ensure_ascii=False))


if __name__ == '__main__':
    main()
