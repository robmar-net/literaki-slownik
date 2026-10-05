#!/usr/bin/env python3
"""Strumieniowy przesiew SGJP; nie jest finalną klasyfikacją skrótowców."""
import argparse
import json
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


def probe(database, profile):
    upper, valid = [], []
    examples = {word: [] for word in ['PCR', 'PCV', 'PESEL', 'AGD', 'RNA', 'DNA', 'AIDS', 'aids']}
    with sqlite3.connect(Path(database).resolve().as_uri() + '?mode=ro', uri=True) as db:
        rows = db.execute("""select f.original,f.game_key,l.lemma_id,i.tag,i.names,i.qualifiers
            from interpretation i join surface_form f on f.id=i.form_id
            join lexeme l on l.id=i.lexeme_id
            where i.names='nazwa_pospolita' and i.tag like 'subst:%'""")
        alphabet = set(profile['alphabet'])
        for row in rows:
            if row[0] in examples:
                examples[row[0]].append(list(row))
            if row[0].isupper():
                upper.append(row)
                if profile['minimum'] <= len(row[1]) <= profile['maximum'] and set(row[1]) <= alphabet:
                    valid.append(row)
    return {
        'scope': 'Jednoznaczna nazwa_pospolita, tag subst; wielkie litery jako przesiew, nie dowód klasy skrótowca. Brak końcowej kwalifikacji i delty słownika.',
        'upper_compact_interpretations': len(upper),
        'upper_game_keys': len({row[1] for row in upper}),
        'profile_valid_compact_interpretations': len(valid),
        'profile_valid_game_keys': len({row[1] for row in valid}),
        'examples_columns': ['original', 'game_key', 'lemma_id', 'tag', 'names', 'qualifiers'],
        'examples': examples,
    }


def label_coverage(database):
    """Pełne wartości pól; przecinek nie jest technicznym separatorem."""
    with sqlite3.connect(Path(database).resolve().as_uri() + '?mode=ro', uri=True) as db:
        inventory = {field: dict(db.execute(f'select {field},count(*) from interpretation group by {field} order by {field}'))
                     for field in ('names', 'qualifiers', 'tag')}
        mixed = list(db.execute('''select f.original,l.lemma_id,i.tag,i.names,i.qualifiers
            from interpretation i join surface_form f on f.id=i.form_id
            join lexeme l on l.id=i.lexeme_id
            where i.names like '%nazwa_pospolita%' and i.names<>'nazwa_pospolita'
            order by f.original,l.lemma_id,i.tag,i.qualifiers'''))
        labels = Counter()
        for raw, count in inventory['qualifiers'].items():
            for label in set(raw.split('|')) - {''}:
                labels[label] += count
        return {'schema_version': 1, 'compact_interpretations': sum(inventory['tag'].values()),
                'inventory': inventory, 'pipe_qualifier_labels': dict(sorted(labels.items())),
                'mixed_common_name_count': len(mixed),
                'mixed_common_name_without_uppercase': sum(not any(c.isupper() for c in row[0]) for row in mixed),
                'mixed_common_name_rows': mixed,
                'notice': 'Pełne pola i literalne etykiety. Brak decyzji językowej, delty list lub podziału przecinka na znaczenia.'}


def kwjp_mapping(database):
    with sqlite3.connect(Path(database).resolve().as_uri() + '?mode=ro', uri=True) as db:
        lexemes = {i: (lid, unicodedata.normalize('NFC', base)) for i, lid, base in db.execute('select id,lemma_id,lemma_base from lexeme')}
        index = defaultdict(set)
        classes = Counter()
        for lid, tag in db.execute('select lexeme_id,tag from interpretation'):
            pos = tag.split(':', 1)[0]
            index[lexemes[lid][1], pos].add(lexemes[lid][0])
            classes[pos] += 1
        counts = defaultdict(Counter)
        examples, non_nfc = {}, []
        for unit, pos, freq in db.execute("select unit_1,pos,freq from corpus_evidence where source_id='KWJP100-kwjp100-slowa-lemma-all' order by row_number"):
            matches = index.get((unicodedata.normalize('NFC', unit), pos), set())
            status = 'UNMATCHED' if not matches else 'AMBIGUOUS' if len(matches) > 1 else 'EXACT_LEMMA_POS_CANDIDATE'
            counts[pos][status] += 1
            examples.setdefault((pos, status), [unit, freq, sorted(matches)])
            if unicodedata.normalize('NFC', unit) != unit:
                non_nfc.append([unit, pos, freq, sorted(matches)])
        return {'method': 'NFC, case-preserving exact lemma_base + POS; suffix retained in full lemma_id; no allocation of frequencies',
                'sgjp_classes': dict(sorted(classes.items())),
                'kwjp_lemma_all_status_by_pos': {pos: dict(sorted(c.items())) for pos, c in sorted(counts.items())},
                'first_examples': [{'pos': p, 'status': s, 'data': data} for (p, s), data in sorted(examples.items())],
                'non_nfc': non_nfc}


def qualifier_conditions(database):
    # Skrypt działa również spoza katalogu repozytorium.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from literaki_slownik.database import connect
    from literaki_slownik.reports import qualifier_coverage
    with connect(database, readonly=True) as db:
        fields = db.execute('select qualifiers,count(*) from interpretation group by qualifiers')
        return qualifier_coverage(fields)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', required=True)
    parser.add_argument('--profile', default='config/generator/profile.json')
    parser.add_argument('--mode', choices=['acronyms', 'labels', 'kwjp', 'qualifier-conditions'], default='acronyms')
    args = parser.parse_args()
    result = (qualifier_conditions(args.database) if args.mode == 'qualifier-conditions' else
              label_coverage(args.database) if args.mode == 'labels' else
              kwjp_mapping(args.database) if args.mode == 'kwjp' else
              probe(args.database, json.loads(Path(args.profile).read_text())))
    print(json.dumps(result, ensure_ascii=False, indent=2))
