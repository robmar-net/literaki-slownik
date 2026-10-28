#!/usr/bin/env python3
"""Kontrola nowej pochodnej Słowosieci (#11, grupa 3, krok 3.7). Tylko odczyt (`mode=ro`).

Użycie (z katalogu repo):
  python3 -I .maister/tasks/development/2026-10-28-11-tematy-morze/analysis/verify_plwordnet.py \
      --db cache/plwordnet/plwn45-tematy.sqlite [--old-db data/work/plwordnet/plwn45.sqlite] \
      --output .maister/tasks/development/2026-10-28-11-tematy-morze/verification/plwordnet-derivative.json

Sprawdza: kierunek relacji 11 (`statek 1` → `łódź 2`, `okręt 1` jako PARENT_ID → CHILD_ID),
nazwy 6 korzeni (`lemma + ' ' + variant` jednostki o najniższym `unitindex`), kody `pos` 1–4
na przykładach, brak kolumn redaktorów, oraz liczbę lematów pełnego domknięcia T2.
Ta sama miara domknięcia na starej pochodnej (tylko `valid=1`) kalibruje ją wobec audytu (874).
Kod 1, gdy któraś kontrola nie przechodzi.
"""
import argparse
from collections import Counter
import hashlib
import json
import re
import sqlite3
import sys
import unicodedata

ROOTS = {7354: 'statek 1', 2149: 'okręt 1', 4511: 'łódź 2', 6214: 'marynarz 1',
         14136: 'żegluga 1', 14515: 'żeglarstwo 1'}
RELATIONS = (11, 25, 27)
EXPECTED_RELATION_NAMES = {11: 'hiperonimia', 25: 'część', 27: 'miejsce'}
POS_MAP = {1: ['inf'], 2: ['subst', 'depr'], 3: ['adv'], 4: ['adj']}
# Przykłady do potwierdzenia mapy kodów: (lemat, oczekiwany kod).
POS_EXAMPLES = (('statek', 2), ('morze', 2), ('pływać', 1), ('żeglować', 1),
                ('morski', 4), ('szybki', 4), ('szybko', 3), ('daleko', 3))
ONE_WORD = re.compile(r'[a-ząćęłńóśźż]+')
FORBIDDEN = ('owner', 'comment', 'error_comment', 'iplog', 'iplimit', 'tracker')


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def connect(path):
    return sqlite3.connect(f'file:{path}?mode=ro', uri=True)


def synset_name(db, synset_id):
    row = db.execute('SELECT u.lemma, u.variant FROM unitandsynset s JOIN lexicalunit u ON u.ID = s.LEX_ID '
                     'WHERE s.SYN_ID = ? ORDER BY s.unitindex LIMIT 1', (synset_id,)).fetchone()
    return None if row is None else f'{row[0]} {row[1]}'


def closure(db, valid_filter=''):
    """Pełne domknięcie od korzeni po 11/25/27, kierunek PARENT_ID → CHILD_ID."""
    marks = ','.join('?' * len(RELATIONS))
    seen, frontier = set(ROOTS), list(ROOTS)
    while frontier:
        nxt = []
        for synset in frontier:
            for (child,) in db.execute(f'SELECT CHILD_ID FROM synsetrelation WHERE PARENT_ID = ? '
                                       f'AND REL_ID IN ({marks}){valid_filter}', (synset, *RELATIONS)):
                if child not in seen:
                    seen.add(child)
                    nxt.append(child)
        frontier = nxt
    return seen


def closure_lemmas(db, synsets, skip_abstract):
    lemmas, abstract = set(), 0
    for synset in sorted(synsets):
        flag = db.execute('SELECT isabstract FROM synset WHERE ID = ?', (synset,)).fetchone()
        if flag and flag[0] == 1:
            abstract += 1
            if skip_abstract:
                continue
        for lemma, pos in db.execute('SELECT u.lemma, u.pos FROM unitandsynset s JOIN lexicalunit u '
                                     'ON u.ID = s.LEX_ID WHERE s.SYN_ID = ?', (synset,)):
            if pos in POS_MAP:
                text = unicodedata.normalize('NFC', lemma).lower()
                if ONE_WORD.fullmatch(text):
                    lemmas.add(text)
    return lemmas, abstract


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--db', required=True)
    parser.add_argument('--old-db')
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    failures = []
    db = connect(args.db)
    result = dict(db=args.db, db_sha256=sha256_file(args.db), meta=dict(db.execute('SELECT key, value FROM meta')))

    schema = {name: [c[1] for c in db.execute(f'PRAGMA table_info({name})')]
              for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")}
    result['schema'] = schema
    leaked = sorted(f'{t}.{c}' for t, cols in schema.items() for c in [t, *cols]
                    if any(f in c.lower() for f in FORBIDDEN))
    result['forbidden_columns_or_tables'] = leaked
    if leaked:
        failures.append(f'kolumny/tabele redaktorów: {leaked}')
    result['counts'] = {t: db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in schema}

    names = dict(db.execute('SELECT ID, name FROM relationtype WHERE ID IN (11, 25, 27)'))
    result['relation_names'] = {str(k): v for k, v in sorted(names.items())}
    if names != EXPECTED_RELATION_NAMES:
        failures.append(f'nazwy relacji {names}')

    children = sorted({synset_name(db, c) for (c,) in db.execute(
        'SELECT CHILD_ID FROM synsetrelation WHERE PARENT_ID = 7354 AND REL_ID = 11')})
    parents = sorted({synset_name(db, p) for (p,) in db.execute(
        'SELECT PARENT_ID FROM synsetrelation WHERE CHILD_ID = 7354 AND REL_ID = 11')})
    direction_ok = {'łódź 2', 'okręt 1'} <= set(children) and not ({'łódź 2', 'okręt 1'} & set(parents))
    result['direction'] = dict(rule='PARENT_ID → CHILD_ID (rodzic = hiperonim)', root='statek 1 (7354)',
                               children_rel11=children, parents_rel11=parents, ok=direction_ok)
    if not direction_ok:
        failures.append('kierunek relacji 11')
    for rel in (25, 27):
        result['direction'][f'children_rel{rel}_of_7354'] = sorted({synset_name(db, c) for (c,) in db.execute(
            'SELECT CHILD_ID FROM synsetrelation WHERE PARENT_ID = 7354 AND REL_ID = ?', (rel,))})

    roots = {}
    for synset, expected in sorted(ROOTS.items()):
        actual = synset_name(db, synset)
        roots[str(synset)] = dict(expected=expected, actual=actual, ok=actual == expected)
        if actual != expected:
            failures.append(f'korzeń {synset}: {actual!r} ≠ {expected!r}')
    result['roots'] = roots

    pos_counts = dict(db.execute('SELECT pos, COUNT(*) FROM lexicalunit GROUP BY pos ORDER BY pos'))
    examples = []
    for lemma, code in POS_EXAMPLES:
        codes = sorted({p for (p,) in db.execute('SELECT pos FROM lexicalunit WHERE lemma = ?', (lemma,))})
        ok = code in codes and all(c not in POS_MAP or c == code for c in codes)
        examples.append(dict(lemma=lemma, expected=code, codes=codes, ok=ok))
        if not ok:
            failures.append(f'pos {lemma}: {codes}, oczekiwano {code}')
    english = {}
    for code in (5, 6, 7, 8):
        english[str(code)] = [r[0] for r in db.execute(
            'SELECT lemma FROM lexicalunit WHERE pos = ? ORDER BY ID LIMIT 5', (code,))]
    result['pos'] = dict(map={str(k): v for k, v in POS_MAP.items()}, units_by_code={str(k): v for k, v in pos_counts.items()},
                         examples=examples, english_examples_5_8=english)

    synsets = closure(db)
    full, abstract = closure_lemmas(db, synsets, skip_abstract=False)
    nonabstract, _ = closure_lemmas(db, synsets, skip_abstract=True)
    t2 = dict(method='pełne domknięcie od 6 korzeni po 11/25/27, PARENT_ID → CHILD_ID, pos 1–4, jedno słowo '
                     '(NFC, małe litery, tylko litery polskie)',
              synsets=len(synsets), abstract_synsets=abstract,
              lemmas_all_synsets=len(full), lemmas_without_abstract_synsets=len(nonabstract),
              control_words_present={w: w in nonabstract for w in
                                     ('łódź', 'okręt', 'burta', 'cuma', 'bukszpryt', 'angora', 'bungee')})
    if args.old_db:
        old = connect(args.old_db)
        old_synsets = closure(old, ' AND valid = 1')
        old_full, _ = closure_lemmas(old, old_synsets, skip_abstract=False)
        old_nonabstract, _ = closure_lemmas(old, old_synsets, skip_abstract=True)
        t2['old_derivative'] = dict(db=args.old_db, synsets=len(old_synsets), lemmas_all_synsets=len(old_full),
                                    lemmas_without_abstract_synsets=len(old_nonabstract), audit_reported=874)
        t2['same_as_old'] = old_synsets == synsets and old_full == full
        result['old_counts'] = dict(
            lexicalunit=old.execute('SELECT COUNT(*) FROM lexicalunit').fetchone()[0],
            synsetrelation=old.execute('SELECT COUNT(*) FROM synsetrelation').fetchone()[0],
            synsetrelation_valid_1=old.execute('SELECT COUNT(*) FROM synsetrelation WHERE valid = 1').fetchone()[0],
            synset=old.execute('SELECT COUNT(*) FROM synset').fetchone()[0],
            unitandsynset=old.execute('SELECT COUNT(*) FROM unitandsynset').fetchone()[0],
            relationtype=old.execute('SELECT COUNT(*) FROM relationtype').fetchone()[0])
        old.close()
    result['t2_closure'] = t2
    db.close()
    result['failures'] = failures
    result['ok'] = not failures
    with open(args.output, 'w', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write('\n')
    print(json.dumps(dict(ok=result['ok'], failures=failures, t2=t2), ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
