#!/usr/bin/env python3
"""G0: jednorazowe przeniesienie zatwierdzonego zakresu #4 do config/generator.

Czyta badawcze `proposal-proof.json` i `family-decisions.json`, wiąże każdą trójkę
(forma, lemat, rozwinięty tag) z dokładnie jedną zapisaną analizą zamrożonej bazy v30
(tylko `mode=ro`), której jedyną odmową jest dawność. Zapisuje produkcyjny JSON bez
znaczników badawczych. Później plik jest zwykłym, ręcznie edytowalnym wejściem.

v2 (#5): `nie-prefix-degree-v1` zastąpiła `nie-prefix-degree-v2` (constructions.py). Nowy build
nie wytworzy kandydatów v1, więc ich wpisy dostają klucz kandydata v2 wyliczony bieżącym kodem
z tego samego składnika źródłowego. Odpowiednik musi być jedyny i różnić się od v1 tylko ID
reguły; w bazie v30 tych kluczy nie ma (opis w `source_snapshot.recomputed_constructions`).

Użycie (z katalogu repo):
  python3 .maister/tasks/development/2026-10-12-stabilizacja-progu-pop/analysis/derive_standard_age_exceptions.py \
      [--output config/generator/standard-age-exceptions.json]
"""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))

from literaki_slownik.canonical import dumps, sha256  # noqa: E402
from literaki_slownik.constructions import NIE_DEGREE_RULE, nie_degree_candidates  # noqa: E402
from literaki_slownik.standard_age_exceptions import (  # noqa: E402
    OVERRIDDEN_RULE, analysis_key, order, render, validate)

RUN = 'lists-v30-20261010-165826-a'
DATABASE = ROOT / 'data/work' / RUN / 'build.sqlite'
DATABASE_MTIME = 1791660525
RESEARCH = '.maister/tasks/research/2026-10-12-standard-formy-dawne'
FINDINGS = f'{RESEARCH}/analysis/findings'
INPUTS = [f'{FINDINGS}/round3/{name}' for name in
          ('proposal-proof.json', 'family-decisions.json', 'proposal.json', 'validation.json')] + [
          f'{FINDINGS}/round4/{name}' for name in ('family-review.json', 'validation.json')]
OLD_NIE_DEGREE_RULE = 'nie-prefix-degree-v1'
APPROVAL = ('.maister/tasks/development/2026-10-12-stabilizacja-progu-pop/analysis/requirements.md'
            ' — zakres zatwierdzony przez właściciela 2026-10-12 (#4)')


def safe(payload):
    """Jedyną odmową jest dawność; wszystkie pozostałe warunki accept."""
    checks = [c for layer in ('language', 'game', 'profile', 'release_scope') for c in payload[layer]['checks']]
    return (any(c['rule_id'] == OVERRIDDEN_RULE and c['status'] == 'reject' for c in checks)
            and all(c['status'] == 'accept' or (c['rule_id'] == OVERRIDDEN_RULE and c['status'] == 'reject')
                    for c in checks))


def evidence_item(item):
    if 'path' in item:
        item = {**item, 'path': str(Path(FINDINGS, 'round3', item['path']).resolve().relative_to(ROOT))}
        if 'word' in item:  # przegląd KWJP: odnośnik zapytania wystarcza; ścieżka lokalna to materiał badania
            item.pop('path')
    return {k: item[k] for k in ('kind', 'word', 'url', 'path') if k in item}


def nie_degree_v2(db, payload, indeclinable):
    """Jedyny kandydat v2 z tego samego składnika; poza ID reguły identyczny z v1."""
    source = next(p['interpretation'] for p in payload['components'] if p['kind'] == 'source_interpretation')
    base = source['lemma_id'].split(':', 1)[0]
    if base not in indeclinable:
        # Ten sam warunek co nie_indeclinable_lemmas(), zawężony do jednego lematu (bez pełnego skanu).
        indeclinable[base] = any(forms == 1 and tags > 1 for forms, tags in db.execute(
            '''select count(distinct i.form_id),count(distinct i.tag) from lexeme l join interpretation i on i.lexeme_id=l.id
               where (l.lemma_id=? or l.lemma_id like ?) and i.tag like 'adj:%' group by l.id''', (base, base + ':%')))
    exists = lambda original: db.execute('select 1 from surface_form where original=?', (original,)).fetchone() is not None
    found = [c for c in nie_degree_candidates(dict(source), exists, {b for b, v in indeclinable.items() if v})
             if c['expanded_tag'] == payload['expanded_tag']]
    expected = json.loads(dumps(payload).replace(OLD_NIE_DEGREE_RULE, NIE_DEGREE_RULE))
    if len(found) != 1 or found[0] != expected:
        sys.exit(f"{payload['original']}: brak jedynego odpowiednika {NIE_DEGREE_RULE}")
    return found[0]


def family_entry(record):
    entry = {'family': record['lemma_id'], 'lemma_id': record['lemma_id'], 'status': record['status']}
    if record['status'] == 'limited':
        entry['scope'] = 'Tylko wymienione formy.'
        forms = record['scope']
    else:
        entry['scope'], forms = record['scope'], None
    entry.update(meaning_note=record['meaning_note'], confidence=record['confidence'],
                 reader_article_ids=sorted(set(record['article_ids'])),
                 kwjp_documents=sorted(set(record['documents'])),
                 evidence=[evidence_item(e) for e in record['evidence']])
    if forms is not None:
        entry['forms'] = sorted(forms)
    if 'exclude_pos' in record:
        entry['exclude_pos'] = sorted(record['exclude_pos'])
    return entry


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(ROOT / 'config/generator/standard-age-exceptions.json'))
    args = parser.parse_args(argv)
    if DATABASE.stat().st_mtime_ns // 10**9 != DATABASE_MTIME:
        sys.exit('zmieniony mtime zamrożonej bazy')
    proof = json.loads((ROOT / INPUTS[0]).read_text())
    families = {r['lemma_id']: r for r in json.loads((ROOT / INPUTS[1]).read_text())}
    proposal = json.loads((ROOT / INPUTS[2]).read_text())
    manifest = json.loads((ROOT / 'config/generator/sources.json').read_text())
    source_hashes = {a['source_id']: a['sha256'] for a in manifest['artifacts']}

    db = sqlite3.connect(f'file:{DATABASE}?mode=ro', uri=True)
    db.execute('pragma query_only=on')
    query = '''select a.analysis_key,a.interpretation_id,a.candidate_key,a.expanded_tag,a.original,a.policy_version,
          i.source_id,i.first_row,coalesce(l.lemma_id,c.lemma_id),i.tag,coalesce(i.names,c.names),
          coalesce(i.qualifiers,c.qualifiers),f.original,c.rule_id,c.payload,p.assessment
        from analysis a indexed by analysis_game_key join variant_decision d on d.analysis_key=a.analysis_key
        join decision_payload p on p.assessment_key=d.assessment_key
        left join interpretation i on i.id=a.interpretation_id left join lexeme l on l.id=i.lexeme_id
        left join surface_form f on f.id=i.form_id
        left join derivation_candidate c on c.candidate_key=a.candidate_key
        where a.game_key=? and +d.variant='standard' '''
    all_matches, safe_matches, versions = collections.Counter(), collections.Counter(), set()
    cases, used_families = [], set()
    recomputed, indeclinable = 0, {}
    for case in proof['cases']:
        word = case['word']
        rows = db.execute(query, (word,)).fetchall()
        if any(json.loads(r[15])['membership']['status'] == 'accept' for r in rows):
            sys.exit(f'{word}: już w STANDARD')
        entries = []
        for analysis in case['analyses']:
            triple = (analysis['lemma_id'], analysis['tag'], analysis['derived'])
            hits = [r for r in rows if (r[8], r[3], r[2] is not None) == triple]
            good = [r for r in hits if safe(json.loads(r[15]))]
            all_matches[len(hits)] += 1
            safe_matches[len(good)] += 1
            if len(good) != 1:
                sys.exit(f'{word}: {len(good)} dopasowań {triple}')
            row = good[0]
            versions.add(row[5])
            family = families[analysis['lemma_id']]
            if family['status'] == 'hold':
                sys.exit(f'{word}: wstrzymana rodzina')
            used_families.add(family['lemma_id'])
            method = analysis['proof']['method']
            if row[2] is None:
                entry = {'kind': 'source', 'family': family['lemma_id'], 'proof': method,
                         'reader_word': analysis['proof']['word'], 'source_id': row[6], 'first_source_row': row[7],
                         'original': row[12], 'lemma_id': row[8], 'raw_tag': row[9], 'names': row[10],
                         'qualifiers': row[11], 'tag': row[3]}
            else:
                payload = json.loads(row[14])
                entry = {'kind': 'construction', 'family': family['lemma_id'], 'proof': method,
                         'candidate_key': row[2], 'rule_id': row[13], 'original': row[4], 'lemma_id': row[8],
                         'tag': row[3], 'names': row[10], 'qualifiers': row[11],
                         'components': [{k: p['interpretation'][k] for k in
                                         ('source_id', 'first_source_row', 'original', 'raw_tag')}
                                        for p in payload['components'] if p['kind'] == 'source_interpretation']}
                if hashlib.sha256(row[14].encode()).hexdigest() != row[2]:
                    sys.exit(f'{word}: klucz kandydata nie jest hashem treści')
            if analysis_key(entry) != row[0]:
                sys.exit(f'{word}: klucz analizy niezgodny ze schematem')
            if entry.get('rule_id') == OLD_NIE_DEGREE_RULE:
                candidate = nie_degree_v2(db, payload, indeclinable)
                entry.update(rule_id=NIE_DEGREE_RULE,
                             candidate_key=hashlib.sha256(dumps(candidate).encode()).hexdigest())
                recomputed += 1
            entries.append(entry)
        cases.append({'word': word, 'analyses': sorted(entries, key=order)})
    db.close()
    if len(versions) != 1:
        sys.exit(f'wiele wersji polityki: {versions}')
    database_sha = sha256(DATABASE)
    if DATABASE.stat().st_mtime_ns // 10**9 != DATABASE_MTIME:
        sys.exit('zmieniony mtime zamrożonej bazy')
    used_sources = sorted({e['source_id'] for c in cases for e in c['analyses'] if e['kind'] == 'source'}
                          | {p['source_id'] for c in cases for e in c['analyses'] if e['kind'] == 'construction'
                             for p in e['components']})
    analyses = sum(len(c['analyses']) for c in cases)
    config = {
        'schema_version': 1,
        'decision_version': 'standard-age-exceptions-v2',
        'description': ('Zatwierdzone (#4) analizy odrzucane w STANDARD wyłącznie za dawność, z potwierdzonym '
                        'współczesnym użyciem. Wyjątek uchyla tylko tę odmowę dla dokładnie wskazanej analizy; '
                        'inne warunki zostają. Zmiana pliku wymaga nowego hasha w sources.json i nowego przebiegu.'),
        'overrides_rule': OVERRIDDEN_RULE,
        'source_snapshot': {'run': RUN, 'database_sha256': database_sha, 'policy_version': versions.pop(),
                            'matches_per_analysis': {str(k): v for k, v in sorted(safe_matches.items())},
                            'recomputed_constructions': {NIE_DEGREE_RULE: {
                                'replaces': OLD_NIE_DEGREE_RULE, 'analyses': recomputed,
                                'note': (f'Klucze kandydatów {NIE_DEGREE_RULE} wyliczone bieżącym kodem constructions.py '
                                         f'z tych samych składników co {OLD_NIE_DEGREE_RULE} w migawce; w bazie migawki '
                                         'ich nie ma. Dopasowania 1:1 dotyczą analiz v1 w migawce.')}}},
        'sources': {sid: source_hashes[sid] for sid in used_sources},
        'provenance': {'research_task': RESEARCH, 'approval': APPROVAL,
                       'inputs': {path: sha256(ROOT / path) for path in INPUTS}},
        'expected_counts': {'words': len(cases), 'analyses': analyses,
                            'source_analyses': sum(e['kind'] == 'source' for c in cases for e in c['analyses']),
                            'construction_analyses': sum(e['kind'] == 'construction' for c in cases for e in c['analyses']),
                            'families': len(used_families)},
        'families': [family_entry(families[name]) for name in sorted(used_families)],
        'cases': sorted(cases, key=lambda c: c['word']),
    }
    loaded = validate(config, source_hashes=source_hashes)
    if set(proposal['new_words']) != {c['word'] for c in cases} or loaded['counts']['families'] != proposal['counts']['families_with_additions']:
        sys.exit('niezgodność z proposal.json')
    Path(args.output).write_text(render(config), encoding='utf-8')
    print(json.dumps({'output': os.path.relpath(args.output, ROOT), 'sha256': sha256(args.output),
                      'counts': loaded['counts'], 'database_sha256': database_sha,
                      'all_matches_per_triple': {str(k): v for k, v in sorted(all_matches.items())},
                      'safe_matches_per_triple': {str(k): v for k, v in sorted(safe_matches.items())},
                      'recomputed_nie_degree_v2': recomputed,
                      'inputs': config['provenance']['inputs'], 'sources': config['sources']},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
