#!/usr/bin/env python3
"""Strumieniowy przesiew SGJP; nie jest finalną klasyfikacją skrótowców."""
import argparse
import json
import sqlite3
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', required=True)
    parser.add_argument('--profile', default='config/generator/profile.json')
    args = parser.parse_args()
    print(json.dumps(probe(args.database, json.loads(Path(args.profile).read_text())), ensure_ascii=False, indent=2))
