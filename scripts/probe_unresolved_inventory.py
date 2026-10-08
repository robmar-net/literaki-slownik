#!/usr/bin/env python3
"""Inwentarz nierozstrzygnięć wpływających na listy BROAD/STANDARD (G3.4, sonda).

Tylko odczyt. Symuluje bieżącą politykę (`literaki_slownik.decisions.assess_diagnostic`,
ta sama ścieżka co `materialize_assessments`) na pełnym imporcie SGJP oraz
kandydatach konstrukcji, bez zapisu ocen i bez aktywowania nowych dowodów.

Rozdziela dwa stałe placeholdery (`linguistic-policy-not-active-v1`,
`game-metadata-not-complete-v1`) od kategorii merytorycznych. Kategorie danych
(frag, adjp, przesiew nazw mieszkańców, by po spójniku, kwalifikatory) są
populacjami do decyzji, NIE klasyfikatorami polityki.

Wynik: kanoniczny JSON na stdout (deterministyczny) oraz pełne listy słów w --lists-dir.
"""
import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from literaki_slownik.canonical import dumps  # noqa: E402
from literaki_slownik.decisions import (assess_diagnostic, checked_use_reviews, remainder_exhausted_check, use_closure_check,  # noqa: E402
                                        VARIANTS)
from literaki_slownik.policy import (VERSION as POLICY_VERSION,  # noqa: E402
                                     MANDATORY_CAPITAL_2026_LEMMAS, RESIDENT_RELATION_SOURCES)
from literaki_slownik.sgjp import expand_tag  # noqa: E402

PLACEHOLDERS = frozenset({'linguistic-policy-not-active-v1', 'game-metadata-not-complete-v1'})

# RJP 2026 (PDF sha 87daaddd…, s. 43, §8.1.2 pkt 3) – przykłady nazw mieszkańców, zapis
# obniżony do małej litery w celu wyszukania małoliterowych lematów SGJP. Lista zamknięta.
RJP_RESIDENT_EXAMPLES = (
    'meksykanin', 'rzymianin', 'sądeczanin', 'ślązak', 'ślązaczka', 'wielkopolanin',
    'małopolanin', 'bawarczyk', 'bawarka', 'korsykanin', 'korsykanka', 'warszawianin',
    'warszawiak', 'krakowianin', 'krakowiak', 'krakus', 'ochocianka', 'mokotowianin',
    'nowohucianin', 'zatorzanin', 'niebuszewianka', 'chochołowianin', 'kresowianin', 'zaolzianin')
# RJP 2026 §4.5 pkt 1c–d (s. 26): formy z łączną cząstką by o statusie odrębnego wyrazu.
RJP_JOINED_BY = frozenset({'aby', 'ażeby', 'byleby', 'chociażby', 'choćby', 'czyżby', 'gdyby',
                           'gdzieżby', 'iżby', 'jakby', 'jakoby', 'jakżeby', 'niby', 'niżby',
                           'żeby', 'oby'})
CODED_BY = frozenset({'jeśliby', 'jeżeliby'})
# Runda 1 decyzji właściciela (2026-10-08, owner-decisions-round1-decision.md):
# kategorie rozstrzygnięte regułą polityki v22 nie są już niewiadomą.
OWNER_RESOLVED = frozenset({'adjp', 'conjunction_by_outside_rjp_list', 'qualifier_registry_semantics',
                            # Runda 2: frag dopuszczone warunkowo; pozostałość użyć ocenia reguła odmowy.
                            'frag', 'documented_use_remainder',
                            # R1: przesiew rozstrzyga reguła game-resident-screen-capital-2026-v1 z wyjątkami.
                            'resident_screen_anin'})
# Bawarka (kulin., napój) nie jest nazwą mieszkanki; decyzja R2.
NOT_RESIDENT = frozenset({'bawarka'})
BY_CLASSES = frozenset({'comp', 'conj', 'part', 'qub', 'adv'})

CATEGORIES = (
    # (identyfikator, warstwa: real/formal)
    ('frag', 'real'),
    ('adjp', 'real'),
    ('resident_rjp_examples', 'real'),
    ('resident_screen_anin', 'real'),
    ('conjunction_by_outside_rjp_list', 'real'),
    ('documented_use_remainder', 'real'),
    ('code:semantic-use-qualification-pending-v1', 'real'),
    ('code:first-release-contraction-scope-v1', 'real'),
    ('code:game-construction-whole-unit-v1', 'real'),
    ('code:game-source-name-labels-v1', 'real'),
    ('code:game-proper-name-class-v1', 'real'),
    ('code:other', 'real'),
    ('qualifier_registry_semantics', 'formal'),
)
CAT_INDEX = {name: i for i, (name, _) in enumerate(CATEGORIES)}
REAL_MASK = sum(1 << i for i, (_, layer) in enumerate(CATEGORIES) if layer == 'real')
QUAL_BIT = 1 << CAT_INDEX['qualifier_registry_semantics']
# Bity słowa poza kategoriami.
B_NONR = 1 << 20        # jest analiza bez niezależnego reject
B_CLEAN = 1 << 21       # jest analiza bez żadnej kategorii (tylko placeholdery)
B_CLEAN_REAL = 1 << 22  # jest analiza bez kategorii realnych (dopuszczalne kwalifikatory)
B_ANY = 1 << 23
EXAMPLE_POOL = 400


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(8 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def gender_ok(tag, feminine):
    parts = tag.split(':')
    if parts[0] == 'depr':
        return not feminine
    return parts[0] == 'subst' and ((parts[-1] == 'f') if feminine else (parts[-1] == 'm1' or
                                                                          (len(parts) > 3 and parts[3] == 'm1')))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True, help='pełny import SGJP (readonly)')
    parser.add_argument('--candidates-database', required=True, help='baza z derivation_candidate (readonly)')
    parser.add_argument('--semantic-uses', default=str(ROOT / 'config/generator/semantic-uses.json'))
    parser.add_argument('--lists-dir', default=None, help='pełne listy słów (np. tmp/...)')
    parser.add_argument('--limit-id', type=int, default=None, help='tylko do testów: i.id<=N')
    parser.add_argument('--min-id', type=int, default=1, help='tylko do testów: i.id>=N')
    parser.add_argument('--skip-hash', action='store_true', help='tylko do testów; wynik nieodtwarzalny')
    args = parser.parse_args()

    hashes_before = {} if args.skip_hash else {
        'database': sha256_file(args.database), 'candidates_database': sha256_file(args.candidates_database)}
    db = sqlite3.connect(f'file:{args.database}?mode=ro', uri=True)
    cdb = sqlite3.connect(f'file:{args.candidates_database}?mode=ro', uri=True)
    uses = json.loads(Path(args.semantic_uses).read_text(encoding='utf-8'))['reviews']
    reviewed = checked_use_reviews(db, uses)
    source_hashes = {sid: json.loads(meta).get('sha256')
                     for sid, meta in db.execute('select source_id,metadata from source_artifact')}

    anin_m1 = {row[0] for row in db.execute(
        "select distinct lemma_base from lexeme where lemma_base like '%anin'") if row[0].islower()}
    anka_from_anin = {base[:-2] + 'ka' for base in anin_m1}  # krakowianin → krakowianka
    documented_res = set(MANDATORY_CAPITAL_2026_LEMMAS) | {'warszawianka'}
    rjp_res = {b for b in RJP_RESIDENT_EXAMPLES}
    rjp_res_documented = {b for b in rjp_res if b in {l.split(':')[0] for l in documented_res}}

    words = {}
    examples = {name: [] for name, _ in CATEGORIES}
    stats = {v: {'analyses': 0, 'independent_reject': 0, 'non_rejected': 0, 'clean_placeholder_only': 0,
                 'clean_real': 0, 'by_category': {name: 0 for name, _ in CATEGORIES},
                 'by_category_compact': {name: 0 for name, _ in CATEGORIES},
                 'code_unresolved_rules': {}, 'clean_by_class': {}} for v in VARIANTS}
    population = {name: {'compact': set(), 'analyses': 0} for name, _ in CATEGORIES}
    residents_rjp_in_sgjp = {}
    totals = {'compact_interpretations': 0, 'source_analyses': 0, 'construction_analyses': 0,
              'documented_use_analyses': 0, 'remainder_analyses': 0, 'reviewed_interpretations': len(reviewed)}
    seen_compact = {v: {} for v in VARIANTS}

    def data_categories(src, tag, cls, remainder):
        cats = 0
        if src is None:
            return cats
        lemma_base = src['lemma_id'].split(':', 1)[0]
        original = src['original']
        if cls == 'frag':
            cats |= 1 << CAT_INDEX['frag']
        elif cls == 'adjp':
            cats |= 1 << CAT_INDEX['adjp']
        if original.islower() and cls in ('subst', 'depr') and src['lemma_id'] not in documented_res:
            if (lemma_base in rjp_res and lemma_base not in rjp_res_documented
                    and gender_ok(tag, lemma_base.endswith('ka'))):
                cats |= 1 << CAT_INDEX['resident_rjp_examples']
            elif ((lemma_base in anin_m1 and gender_ok(tag, False))
                  or (lemma_base in anka_from_anin and gender_ok(tag, True))):
                cats |= 1 << CAT_INDEX['resident_screen_anin']
        if (cls in BY_CLASSES and lemma_base.endswith('by') and lemma_base not in RJP_JOINED_BY
                and lemma_base not in CODED_BY and len(lemma_base) > 2):
            cats |= 1 << CAT_INDEX['conjunction_by_outside_rjp_list']
        if remainder:
            cats |= 1 << CAT_INDEX['documented_use_remainder']
        if src['qualifiers']:
            cats |= QUAL_BIT
        if lemma_base in NOT_RESIDENT:
            cats &= ~(1 << CAT_INDEX['resident_rjp_examples'])
        for name in OWNER_RESOLVED:
            cats &= ~(1 << CAT_INDEX[name])
        return cats

    def record(assessed, src, tag, cls, remainder, compact_id, identity):
        key = assessed['game_key']
        base_cats = data_categories(src, tag, cls, remainder)
        if src is not None and src['lemma_id'].split(':')[0] in rjp_res:
            residents_rjp_in_sgjp.setdefault(src['lemma_id'], set()).add(src['original'])
        masks = words.get(key)
        if masks is None:
            masks = words[key] = [0, 0]
        for vi, variant in enumerate(VARIANTS):
            st = stats[variant]
            st['analyses'] += 1
            checks = assessed['membership'][variant]['checks']
            rejected = any(c['status'] == 'reject' for c in checks)
            masks[vi] |= B_ANY
            if rejected:
                st['independent_reject'] += 1
                continue
            cats = base_cats
            for c in checks:
                if c['status'] == 'unresolved' and c['rule_id'] not in PLACEHOLDERS:
                    name = 'code:' + c['rule_id']
                    cats |= 1 << CAT_INDEX.get(name, CAT_INDEX['code:other'])
                    st['code_unresolved_rules'][c['rule_id']] = st['code_unresolved_rules'].get(c['rule_id'], 0) + 1
            st['non_rejected'] += 1
            masks[vi] |= B_NONR | cats
            if not cats:
                masks[vi] |= B_CLEAN | B_CLEAN_REAL
                st['clean_placeholder_only'] += 1
                bucket = cls if src is not None else 'construction:' + identity['rule_id']
                st['clean_by_class'][bucket] = st['clean_by_class'].get(bucket, 0) + 1
            elif not cats & REAL_MASK:
                masks[vi] |= B_CLEAN_REAL
                st['clean_real'] += 1
            for name, _ in CATEGORIES:
                bit = 1 << CAT_INDEX[name]
                if cats & bit:
                    st['by_category'][name] += 1
                    if compact_id is not None and not seen_compact[variant].get((name, compact_id)):
                        seen_compact[variant][(name, compact_id)] = True
                        st['by_category_compact'][name] += 1
                    if variant == 'broad' and len(examples[name]) < EXAMPLE_POOL:
                        examples[name].append((key, identity))
                    if variant == 'standard' and len(examples[name]) < EXAMPLE_POOL and not any(
                            e[1] == identity for e in examples[name]):
                        examples[name].append((key, identity))

    query = '''select i.id,i.source_id,i.first_row,f.original,l.lemma_id,i.tag,i.names,i.qualifiers
        from interpretation i join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id
        where (? is null or i.id<=?) and i.id>=? order by i.id'''
    fields = ('source_id', 'first_source_row', 'original', 'lemma_id', 'raw_tag', 'names', 'qualifiers')
    for row in db.execute(query, (args.limit_id, args.limit_id, args.min_id)):
        totals['compact_interpretations'] += 1
        source = dict(zip(fields, row[1:]))
        for tag in expand_tag(source['raw_tag']):
            cls = tag.split(':', 1)[0]
            analysis_source = dict(source, raw_tag=tag, source_sha256=source_hashes[source['source_id']])
            identity = {'kind': 'source', 'source_id': source['source_id'], 'first_source_row': source['first_source_row'],
                        'original': source['original'], 'lemma_id': source['lemma_id'], 'raw_tag': source['raw_tag'],
                        'expanded_tag': tag, 'names': source['names'], 'qualifiers': source['qualifiers']}
            if row[0] in reviewed:
                assessed = assess_diagnostic(source['original'], source['qualifiers'],
                                             additional_checks=[remainder_exhausted_check(reviewed[row[0]])],
                                             source_analyses=[analysis_source], documented_condition_ids=[])
                record(assessed, source, tag, cls, True, row[0], dict(identity, kind='remainder'))
                totals['remainder_analyses'] += 1
                for review in reviewed[row[0]]:
                    use = assess_diagnostic(source['original'], source['qualifiers'],
                        additional_checks=[use_closure_check(review)],
                        source_analyses=[analysis_source],
                        documented_condition_ids=review.get('documented_conditions', []), lexical_use_review=review)
                    record(use, source, tag, cls, False, row[0], dict(identity, kind='documented_use', use_id=review['use_id']))
                    totals['documented_use_analyses'] += 1
                    totals['source_analyses'] += 1
            else:
                assessed = assess_diagnostic(source['original'], source['qualifiers'], source_analyses=[analysis_source])
                record(assessed, source, tag, cls, False, row[0], identity)
            totals['source_analyses'] += 1

    by_rule = {}
    for ckey, payload in cdb.execute('select candidate_key,payload from derivation_candidate order by candidate_key'):
        candidate = json.loads(payload)
        proof = candidate.get('linguistic_evidence')
        components = [c['interpretation'] for c in candidate['components'] if c['kind'] == 'source_interpretation']
        assessed = assess_diagnostic(candidate['original'], candidate['qualifiers'], [proof] if proof else [],
                                     components, candidate)
        identity = {'kind': 'construction', 'candidate_key': ckey, 'rule_id': candidate['rule_id'],
                    'original': candidate['original'], 'lemma_id': candidate['lemma_id'],
                    'expanded_tag': candidate['expanded_tag'], 'names': candidate['names'],
                    'qualifiers': candidate['qualifiers']}
        by_rule[candidate['rule_id']] = by_rule.get(candidate['rule_id'], 0) + 1
        record(assessed, None, candidate['expanded_tag'], candidate['expanded_tag'].split(':')[0], False, None, identity)
        totals['construction_analyses'] += 1

    # Agregacja słów.
    word_stats = {}
    lists = {}
    for vi, variant in enumerate(VARIANTS):
        ws = {'game_keys_with_analysis': 0, 'definite_reject': 0, 'with_non_rejected_analysis': 0,
              'clean_placeholder_only_words': 0, 'clean_real_words': 0,
              'dependent_any_category_formal': 0, 'dependent_any_real_category': 0,
              'by_category': {name: {'dependent': 0, 'sole_category': 0} for name, _ in CATEGORIES}}
        dep_lists = {name: [] for name, _ in CATEGORIES}
        dep_real = []
        for key, masks in words.items():
            mask = masks[vi]
            if not mask & B_ANY:
                continue
            ws['game_keys_with_analysis'] += 1
            if not mask & B_NONR:
                ws['definite_reject'] += 1
                continue
            ws['with_non_rejected_analysis'] += 1
            if mask & B_CLEAN:
                ws['clean_placeholder_only_words'] += 1
            else:
                ws['dependent_any_category_formal'] += 1
            if mask & B_CLEAN_REAL:
                ws['clean_real_words'] += 1
                if not mask & B_CLEAN:
                    name = 'qualifier_registry_semantics'
                    ws['by_category'][name]['dependent'] += 1
                    ws['by_category'][name]['sole_category'] += 1
                    dep_lists[name].append(key)
                continue
            ws['dependent_any_real_category'] += 1
            dep_real.append(key)
            real = mask & REAL_MASK
            for name, layer in CATEGORIES:
                bit = 1 << CAT_INDEX[name]
                if layer == 'real' and real & bit:
                    ws['by_category'][name]['dependent'] += 1
                    dep_lists[name].append(key)
                    if real == bit:
                        ws['by_category'][name]['sole_category'] += 1
        word_stats[variant] = ws
        lists[variant] = (dep_lists, dep_real)
    union = {'dependent_any_real_category_either_variant': 0, 'dependent_any_real_category_both_variants': 0}
    for masks in words.values():
        flags = [bool(m & B_NONR) and not m & B_CLEAN_REAL for m in masks]
        union['dependent_any_real_category_either_variant'] += any(flags)
        union['dependent_any_real_category_both_variants'] += all(flags)

    dependent_sets = {v: {name: set(lists[v][0][name]) for name, _ in CATEGORIES} for v in VARIANTS}
    chosen = {}
    for name, _ in CATEGORIES:
        pool = examples[name]
        pick = [e for e in pool if e[0] in dependent_sets['broad'][name] or e[0] in dependent_sets['standard'][name]]
        picked, keys = [], set()
        for key, ident in pick + pool:
            if key in keys:
                continue
            keys.add(key)
            picked.append(dict(ident, game_key=key,
                               word_dependent_broad=key in dependent_sets['broad'][name],
                               word_dependent_standard=key in dependent_sets['standard'][name]))
            if len(picked) == 5:
                break
        chosen[name] = picked

    lists_meta = {}
    if args.lists_dir:
        out = Path(args.lists_dir)
        out.mkdir(parents=True, exist_ok=True)
        for variant in VARIANTS:
            dep_lists, dep_real = lists[variant]
            for name, values in list(dep_lists.items()) + [('ANY_REAL', dep_real)]:
                text = ''.join(k + '\n' for k in sorted(values))
                fname = f"words-{variant}-{name.replace(':', '_')}.txt"
                (out / fname).write_text(text, encoding='utf-8')
                lists_meta[fname] = {'words': len(values), 'sha256': hashlib.sha256(text.encode()).hexdigest()}

    hashes_after = {} if args.skip_hash else {
        'database': sha256_file(args.database), 'candidates_database': sha256_file(args.candidates_database)}
    for st in stats.values():
        st['code_unresolved_rules'] = dict(sorted(st['code_unresolved_rules'].items()))
        st['clean_by_class'] = dict(sorted(st['clean_by_class'].items()))
    result = {
        'schema_version': 1,
        'scope': 'unresolved_inventory_simulation_not_release_or_policy_change',
        'policy_version': POLICY_VERSION,
        'placeholders': sorted(PLACEHOLDERS),
        'categories': [{'id': n, 'layer': l} for n, l in CATEGORIES],
        'totals': totals,
        'construction_candidates_by_rule': dict(sorted(by_rule.items())),
        'analysis_stats': stats,
        'word_stats': word_stats,
        'word_union': union,
        'examples': chosen,
        'rjp_resident_examples_found_in_sgjp': {k: sorted(v) for k, v in sorted(residents_rjp_in_sgjp.items())},
        'anin_lowercase_lemmas': len(anin_m1),
        'lists': lists_meta,
        'readonly_hashes_before': hashes_before,
        'readonly_hashes_after': hashes_after,
        'readonly_unchanged': hashes_before == hashes_after,
        'script_sha256': sha256_file(__file__),
    }
    sys.stdout.write(dumps(result) + '\n')


if __name__ == '__main__':
    main()
