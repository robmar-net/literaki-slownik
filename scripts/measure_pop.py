#!/usr/bin/env python3
"""Pomiar POP i POP0 (etap A, A1–A10): tylko odczyt, raport dla właściciela.

Użycie:
  python3 scripts/measure_pop.py --output-dir data/work/pop-measure-<stempel>
      [--sources config/generator/pop-sources.json] [--run-dir <przebieg v29>]
      [--release-dir <pakiet LL-PL v29>] [--with-membership-ii]

Wynik w nowym katalogu: `measure.json` (kanoniczny, bez czasów i ścieżek; jedyne miejsce
z liczbami NKJP per forma), `timing.json` (czasy i pamięć), `report.md` (po polsku; NKJP
tylko jako rangi, percentyle i udziały). Baza tylko `mode=ro`; hash bazy przed i po.
Kody: 2 argumenty, 3 piny, 4 katalog istnieje, 5 baza zmieniona lub przebieg nie FROZEN.
Reguła przynależności (ii) trwa ok. 13 min, więc jest mierzona tylko z `--with-membership-ii`.
"""
import argparse
from collections import Counter
import hashlib
import os
from pathlib import Path
import resource
import shutil
import statistics
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from literaki_slownik.canonical import dumps, write_json  # noqa: E402
from literaki_slownik.database import connect  # noqa: E402
from literaki_slownik.export import rename_noreplace  # noqa: E402
from literaki_slownik.inputs import GeneratorError  # noqa: E402
from literaki_slownik.pop import (CLEANING_RULES, D1_OPTIONS, check_inputs, coverage,  # noqa: E402
                                  database_sha256, form_owners, forms_for, kwjp_measures, load_constructions,
                                  load_form_classes, load_forms, load_forms_accepted, load_kwjp_lists,
                                  load_lexemes, load_sources, measure, nkjp_collisions, percentiles, rank_units,
                                  read_nkjp, read_standard, spearman, threshold, top_overlap, units)
from literaki_slownik.quality import ENCODING, sample_strata  # noqa: E402
from literaki_slownik.run import code_identity  # noqa: E402

VERSION = 'pop-measure-v1'
SAMPLING = {'version': 'pop-quality-v1', 'seed': 'literaki-slownik-pop-v1', 'size_per_stratum': 30,
            'encoding': ENCODING}
POP_REF, POP0_REF = 40000, 5000
COUNTS = (5000, 10000, 20000, 40000, 80000)
TARGETS = (0.8, 0.9, 0.95, 0.98)
WINDOW = 500  # jednostek po każdej stronie granicy w próbkach
D2_BASE = {'classes': [], 'constructions': 'yes', 'membership': 'i'}
# Bazowa miara ADR-007 po przeglądzie próbek: log-ipm; średnia percentyli F zostaje wariantem do porównań.
D3_BASE = {'source': 'kwjp+nkjp', 'field': 'log-ipm', 'weight': 0.5}
D3_PERCENTILE = {'source': 'kwjp+nkjp', 'field': 'F', 'weight': 0.5}
BASE = {'d1': 'kwjp-standard', 'd2': D2_BASE, 'd3': D3_BASE, 'd4': 'strip-edges-keep-dot', 'd5': 'e-common',
        'd6': {'by': 'count', 'value': POP_REF}, 'd6_pop0': {'by': 'count', 'value': POP0_REF},
        'd8': 'lower-bound-absent'}
D2_VARIANTS = (
    ('pełna odmiana', D2_BASE),
    ('bez wołacza', dict(D2_BASE, classes=['voc'])),
    ('bez rozkaźnika', dict(D2_BASE, classes=['impt'])),
    ('bez imiesłowów', dict(D2_BASE, classes=['participle'])),
    ('bez os. 1/2', dict(D2_BASE, classes=['person-1-2'])),
    ('bez czterech klas', dict(D2_BASE, classes=['voc', 'impt', 'participle', 'person-1-2'])),
    ('bez konstrukcji', dict(D2_BASE, constructions='no')),
    ('reguła (ii)', dict(D2_BASE, membership='ii')),
)
D3_VARIANTS = (
    ('KWJP+NKJP log-ipm, waga 0,5', D3_BASE),
    ('KWJP+NKJP log-ipm, waga 0,75', dict(D3_BASE, weight=0.75)),
    ('KWJP+NKJP log-ipm, waga 0,25', dict(D3_BASE, weight=0.25)),
    ('KWJP+NKJP percentyle F, waga 0,5', D3_PERCENTILE),
    ('KWJP+NKJP percentyle F, waga 0,75', dict(D3_PERCENTILE, weight=0.75)),
    ('KWJP+NKJP percentyle F, waga 0,25', dict(D3_PERCENTILE, weight=0.25)),
    ('sama KWJP: log-ipm', {'source': 'kwjp', 'field': 'log-ipm'}),
    ('sama KWJP: F', {'source': 'kwjp', 'field': 'F'}),
    ('sama KWJP: ARF', {'source': 'kwjp', 'field': 'ARF'}),
    ('sama KWJP: 1-DP', {'source': 'kwjp', 'field': '1-DP'}),
    ('sama KWJP: gatunki', {'source': 'kwjp', 'field': 'genres'}),
)
D5_VARIANTS = (
    ('a', 'a: brak F przy niejednoznaczności'),
    ('b', 'b: F kopiowane z flagą (tylko porównanie)'),
    ('c', 'c: tylko formy jednoznaczne'),
    ('d', 'd: grupa homonimów (wszyscy właściciele)'),
    ('e-literal', 'e dosłowne: łączy tylko leksemy z formą w STANDARD'),
    ('e-common', 'e bez nazw własnych'),
)
D8_RULES = ('lower-bound-absent', 'available-only', 'lower-bound', 'exclude')
WORDS = ('nie', 'to', 'być', 'rok', 'raz', 'dzień', 'lata', 'lato', 'polska', 'polski', 'zamek')
TOP_GROUPS = 50
TOP_COLLISIONS = 15
POS_CLASSES = (('subst', {'subst', 'depr'}),
               ('verb', {'fin', 'praet', 'inf', 'impt', 'imps', 'pcon', 'pant', 'pact', 'ppas', 'ger', 'bedzie',
                         'winien'}),
               ('adj', {'adj', 'adja', 'adjp', 'adjc'}),
               ('adv', {'adv'}))
SHORT, LONG = 3, 12


# --- Pomocnicze ---

def _options_sha256():
    options = {'base': BASE, 'counts': COUNTS, 'targets': TARGETS, 'window': WINDOW, 'pop_ref': POP_REF,
               'pop0_ref': POP0_REF, 'd2': D2_VARIANTS, 'd3': D3_VARIANTS, 'd5': D5_VARIANTS, 'd8': D8_RULES,
               'cleaning': sorted(CLEANING_RULES.values()), 'sampling': SAMPLING, 'words': WORDS}
    return hashlib.sha256(dumps(options).encode('utf-8')).hexdigest()


def _key(key):
    """Klucz leksemu jako napis do próbek i JSON: `lemma_id@source_id`."""
    return f'{key[1]}@{key[0]}'


def _unit_label(members, limit=4):
    names = [m[1] for m in members[:limit]]
    rest = len(members) - limit
    return '+'.join(names) + (f' (+{rest})' if rest > 0 else '')


def _share(part, total):
    return round(part / total, 6) if total else None


class Clock:
    def __init__(self):
        self.seconds = {}

    def run(self, name, call, *args, **kwargs):
        start = time.perf_counter()
        try:
            return call(*args, **kwargs)
        finally:
            self.seconds[name] = round(time.perf_counter() - start, 1)


def _peak_rss_mb():
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(peak / (1024 * 1024 if sys.platform == 'darwin' else 1024), 1)


# --- Wybór i podsumowanie ---

def _select(ctx, result, d3=D3_BASE, d8=BASE['d8'], d6=None):
    found = measure(result, d3, d8)
    ranks = rank_units(found['units'])
    cut = threshold(ranks, result, d6 or BASE['d6'], ctx['kwjp'], ctx['relevant'], found['units'])
    return found, ranks, cut


def _forms(ctx, members, d2=D2_BASE):
    return forms_for(members, d2, ctx['forms'], ctx['constructions'], ctx['classes'])


def _row(ctx, cut, d2=D2_BASE):
    members = cut['members']
    return {'lexemes': cut['lexemes'], 'units': len(cut['units']), 'rank': cut['rank'],
            'reached': cut['reached'], 'forms': len(_forms(ctx, members, d2)['forms']),
            'coverage': {d1: coverage(members, ctx['kwjp'], d1, ctx['relevant'])['coverage'] for d1 in D1_OPTIONS}}


def _jaccard(a, b):
    union = len(a | b)
    return round(len(a & b) / union, 6) if union else None


def _fates(result, ranks, cut, wanted):
    """Los wskazanych leksemów: jednostka, jej ranga, rozmiar i czy w POP (wg progu `cut`)."""
    chosen = set(cut['units'])
    found = {}
    for unit, item in result['units'].items():
        hit = wanted.intersection(item['members'])
        for key in hit:
            found[key] = {'unit': [m[1] for m in item['members'][:10]], 'size': len(item['members']),
                          'rank': ranks.get(unit), 'in_pop': unit in chosen}
    return found


def _d5_option(ctx, option):
    if option == 'e-common':
        return units(ctx['kwjp'], 'e', ctx['relevant'], ctx['nkjp'], ctx['owners'],
                     eligible=ctx['relevant'] - ctx['proper'])
    return units(ctx['kwjp'], 'e' if option == 'e-literal' else option, ctx['relevant'], ctx['nkjp'],
                 ctx['owners'])


# --- Etapy pomiaru ---

def _load(paths, clock, with_ii):
    standard = clock.run('standard', read_standard, paths['standard'])
    sources = paths['sources']
    lemma = next(i for i in sources['inputs'] if i['kind'] == 'kwjp')['lemma_sources']
    ctx = {'standard_size': len(standard)}
    with connect(paths['database'], readonly=True) as db:
        lexemes = clock.run('lexemes', load_lexemes, db)
        rows, genres = clock.run('kwjp', load_kwjp_lists, db, lemma, lexemes)
        ctx['owners'] = clock.run('form_owners', form_owners, db, lexemes)
        forms = {'i': clock.run('membership_i', load_forms, db, standard, lexemes)}
        if with_ii:
            forms['ii'] = clock.run('membership_ii', load_forms_accepted, db, standard, lexemes)
        ctx['constructions'] = clock.run('constructions', load_constructions, db, standard, lexemes)
        ctx['classes'] = clock.run('form_classes', load_form_classes, db, standard, lexemes)
    ctx['kwjp'] = clock.run('kwjp_measures', kwjp_measures, rows, genres)
    ctx['group_text'] = {r['row']: r['unit'] for r in rows if r['status'] == 'AMBIGUOUS'}
    del rows, genres
    info = {item['key']: item for item in lexemes.values()}
    del lexemes
    ctx.update(info=info, forms=forms, relevant=frozenset(forms['i']),
               proper=frozenset(k for k, v in info.items() if v['proper']),
               colloquial=frozenset(k for k, v in info.items() if v['colloquial']))
    return ctx


def _d4(ctx, path, clock):
    """Reguły czyszczenia NKJP po jednej naraz; bazowa wczytana na końcu i zostaje w pamięci."""
    found = {}
    for rule in sorted(CLEANING_RULES, key=lambda r: (r == BASE['d4'], r)):
        ctx['nkjp'] = None
        nkjp = clock.run(f'nkjp_{rule}', read_nkjp, path, rule, ctx['owners'])
        collisions = nkjp_collisions(nkjp)
        strict = units(ctx['kwjp'], 'c', ctx['relevant'], nkjp, ctx['owners'])['mass']['nkjp']
        found[rule] = {'rule_id': nkjp['rule_id'], 'lines': nkjp['lines'], 'total': nkjp['total'],
                       'matched': nkjp['matched'], 'matched_share': _share(nkjp['matched'], nkjp['total']),
                       'collisions': len(collisions), 'merged': sum(c['merged'] for c in collisions),
                       'merged_share': _share(sum(c['merged'] for c in collisions), nkjp['total']),
                       'strict_attributed_share': _share(strict['attributed'], strict['matched']),
                       # Liczby NKJP per forma: tylko tutaj, w measure.json (A10, C14).
                       'top_collisions': [{'key': c['key'], 'kept': c['kept'], 'merged': c['merged'],
                                           'sources': [list(s) for s in c['sources'][:5]]}
                                          for c in collisions[:TOP_COLLISIONS]]}
        ctx['nkjp'] = nkjp
    return found


def _d5(ctx, clock):
    wanted = {key for word in WORDS for key in ctx['owners'].get(word, ())}
    top = sorted(ctx['kwjp']['groups'].items(), key=lambda item: (-item[1]['F'], item[0]))[:TOP_GROUPS]
    for group, _ in top:
        wanted.update(group)
    rows, base = {}, None
    for option, _ in D5_VARIANTS:
        result = clock.run(f'units_{option}', _d5_option, ctx, option)
        found, ranks, cut = _select(ctx, result)
        fates = _fates(result, ranks, cut, wanted)
        rows[option] = {**_row(ctx, cut), 'mass': result['mass'], 'groups': result['groups'],
                        'units_total': len(result['units']), 'fates': fates}
        if option == BASE['d5']:
            base = {'result': result, 'found': found, 'ranks': ranks, 'cut': cut}
        del result, found, ranks
    words = {word: sorted(_key(k) for k in ctx['owners'].get(word, ())) for word in WORDS}
    groups = [{'members': [_key(k) for k in group], 'unit': ctx['group_text'].get(entry['row']),
               'F': entry['F']} for group, entry in top]
    for option in rows:
        rows[option]['fates'] = {_key(k): v for k, v in sorted(rows[option]['fates'].items())}
    return {'options': rows, 'words': words, 'top_groups': groups}, base


def _d1(ctx, base):
    everyone = {m for item in base['result']['units'].values() for m in item['members']}
    return {'pop': _row(ctx, base['cut']),
            'ceiling': {d1: coverage(everyone, ctx['kwjp'], d1, ctx['relevant']) for d1 in D1_OPTIONS},
            'kwjp_mass': ctx['kwjp']['mass']}


def _d2(ctx, base):
    members = base['cut']['members']
    full = _forms(ctx, members)['forms']
    nkjp = ctx['nkjp']
    rows = {}
    for label, d2 in D2_VARIANTS:
        if d2['membership'] not in ctx['forms']:
            rows[label] = None
            continue
        found = _forms(ctx, members, d2)
        removed = full - found['forms']
        added = found['forms'] - full
        rows[label] = {'d2': d2, 'forms': len(found['forms']), 'removed': len(removed), 'added': len(added),
                       'removed_by_class': found['removed'], 'constructions': found['constructions'],
                       'removed_nkjp_share': _share(sum(nkjp['forms'].get(f, 0) for f in removed), nkjp['matched'])}
    all_forms = set()
    for forms in ctx['forms']['i'].values():
        all_forms |= forms
    return {'variants': rows, 'standard': ctx['standard_size'], 'standard_with_lexeme': len(all_forms)}


def _d3(ctx, base):
    result, base_ranks = base['result'], base['ranks']
    base_members = base['cut']['members']
    rows = {}
    for label, d3 in D3_VARIANTS:
        found, ranks, cut = _select(ctx, result, d3)
        rows[label] = {'d3': d3, **_row(ctx, cut), 'spearman': spearman(base_ranks, ranks),
                       'top_pop0': top_overlap(base_ranks, ranks, POP0_REF),
                       'top_pop': top_overlap(base_ranks, ranks, POP_REF),
                       'pop_jaccard': _jaccard(base_members, cut['members'])}
    chosen = set(base['cut']['units'])
    confidence = {'all': Counter(), 'pop': Counter()}
    for unit, item in result['units'].items():
        name = item['confidence'] or 'NONE'
        confidence['all'][name] += 1
        if unit in chosen:
            confidence['pop'][name] += 1
    return {'variants': rows, 'confidence': {k: dict(sorted(v.items())) for k, v in confidence.items()}}


def _d6(ctx, base):
    result, ranks, values = base['result'], base['ranks'], base['found']['units']
    counts = {str(n): _row(ctx, threshold(ranks, result, {'by': 'count', 'value': n}, values=values))
              for n in COUNTS}
    targets = {}
    for target in TARGETS:
        d6 = {'by': 'coverage', 'value': target, 'denominator': BASE['d1']}
        targets[str(target)] = _row(ctx, threshold(ranks, result, d6, ctx['kwjp'], ctx['relevant']))
    return {'counts': counts, 'targets': targets}


def _d7(ctx, base):
    """Luka potoczna (A6): ile leksemów `pot.` wypada przy progach; różnica percentyli NKJP − KWJP."""
    result, ranks = base['result'], base['ranks']
    colloquial = ctx['colloquial'] & ctx['relevant']
    kwjp_ranks = rank_units(measure(result, {'source': 'kwjp', 'field': 'F'})['units'])
    kwjp_pct = percentiles(kwjp_ranks)
    gaps = {'colloquial': [], 'other': []}
    candidates = []
    for unit, item in result['units'].items():
        nkjp_pct = item['nkjp']['percentile']
        is_colloquial = bool(colloquial.intersection(item['members']))
        if nkjp_pct is not None and unit in kwjp_pct:
            gaps['colloquial' if is_colloquial else 'other'].append(nkjp_pct - kwjp_pct[unit])
        if is_colloquial and item['nkjp']['rank'] is not None:
            candidates.append((item['nkjp']['rank'], unit))
    by_count = {}
    for n in COUNTS:
        members = threshold(ranks, result, {'by': 'count', 'value': n}, values=base['found']['units'])['members']
        inside = len(colloquial & members)
        by_count[str(n)] = {'inside': inside, 'outside': len(colloquial) - inside}
    pop = base['cut']['members']
    examples = [{'unit': [m[1] for m in unit[:4]], 'nkjp_rank': rank, 'kwjp_rank': kwjp_ranks.get(unit),
                 'rank': ranks.get(unit)}
                for rank, unit in sorted(candidates) if not pop.intersection(unit)][:15]
    median = lambda values: round(statistics.median(values), 4) if values else None
    return {'colloquial': len(colloquial), 'by_count': by_count, 'examples': examples,
            'gap_median': {k: median(v) for k, v in gaps.items()}, 'gap_n': {k: len(v) for k, v in gaps.items()}}


def _d8(ctx, base):
    result = base['result']
    rows, members = {}, {}
    for rule in D8_RULES:
        found, ranks, cut = _select(ctx, result, D3_BASE, rule)
        members[rule] = cut['members']
        rows[rule] = {**_row(ctx, cut), 'missing': found['missing']}
    for rule in D8_RULES:
        rows[rule]['jaccard_available_only'] = _jaccard(members['available-only'], members[rule])
    full = base['found']['missing']
    return {'rules': rows, 'full': full['full'], 'statuses': full['statuses']}


def _a9(ctx, timing):
    c = ctx['constructions']
    found = {'only_constructions': c['only_constructions'], 'counts': c['counts'], 'examples': c['examples'],
             'membership_ii': None}
    if 'ii' in ctx['forms']:
        first, second = ctx['forms']['i'], ctx['forms']['ii']
        pairs = lambda forms: sum(len(v) for v in forms.values())
        only_i = sum(len(v - second.get(k, frozenset())) for k, v in first.items())
        only_ii = sum(len(v - first.get(k, frozenset())) for k, v in second.items())
        found['membership_ii'] = {'pairs_i': pairs(first), 'pairs_ii': pairs(second), 'only_i': only_i,
                                  'only_ii': only_ii, 'lexemes_i': len(first), 'lexemes_ii': len(second)}
    return found


def _pos(info):
    tags = set(info['pos'])
    return next((name for name, group in POS_CLASSES if tags & group), 'other')


def _samples(ctx, base):
    """Warstwy `pop-quality-v1` (A7, C17): granice POP/POP0, braki, rozbieżność, grupy, POS, długość."""
    result, ranks, found = base['result'], base['ranks'], base['found']
    relevant = ctx['relevant']
    order = sorted(ranks, key=ranks.get)

    def keys(selected):
        return sorted({_key(m) for unit in selected for m in result['units'][unit]['members'] if m in relevant})

    strata = {}
    for name, d6 in (('pop', BASE['d6']), ('pop0', BASE['d6_pop0'])):
        position = len(threshold(ranks, result, d6, values=found['units'])['units'])
        strata[f'{name}-granica-wewnatrz'] = keys(order[max(0, position - WINDOW):position])
        strata[f'{name}-granica-zewnatrz'] = keys(order[position:position + WINDOW])
    strata['braki-danych'] = keys(u for u, item in found['units'].items()
                                  if item['status'] != 'MEASURED' or item['flags'])
    kwjp_pct = percentiles(rank_units(measure(result, {'source': 'kwjp', 'field': 'F'})['units']))
    strata['rozbieznosc-kwjp-nkjp'] = keys(
        u for u, item in result['units'].items()
        if u in kwjp_pct and item['nkjp']['percentile'] is not None
        and abs(kwjp_pct[u] - item['nkjp']['percentile']) >= 50)
    strata['grupy-homonimow'] = keys(u for u, item in result['units'].items() if len(item['members']) > 1)
    pop_members = sorted(m for m in base['cut']['members'] if m in relevant)
    by_pos = {}
    for member in pop_members:
        by_pos.setdefault(f"pos-{_pos(ctx['info'][member])}", []).append(_key(member))
    strata.update({name: sorted(values) for name, values in by_pos.items()})
    pop_forms = sorted(_forms(ctx, base['cut']['members'])['forms'])
    strata['formy-krotkie'] = [f for f in pop_forms if len(f) <= SHORT]
    strata['formy-dlugie'] = [f for f in pop_forms if len(f) >= LONG]
    # Pusta warstwa zostaje jawnie: `EMPTY_NOT_COVERAGE`.
    return sample_strata(strata, SAMPLING)


def collect(paths, with_ii):
    """Cały pomiar w pamięci; zwraca (measure.json, timing.json). Bez zapisu na dysk."""
    clock = Clock()
    ctx = _load(paths, clock, with_ii)
    data = {'schema_version': 1, 'version': VERSION, 'code_identity': code_identity(),
            'options_sha256': _options_sha256(), 'base': BASE,
            'inputs': {'pop_sources_sha256': paths['sources']['manifest_sha256'],
                       'release_manifest_sha256': paths['release_manifest_sha256'],
                       'standard_sha256': paths['standard_sha256'], 'nkjp_sha256': paths['nkjp_sha256']},
            'population': {'standard': ctx['standard_size'], 'relevant_lexemes': len(ctx['relevant']),
                           'proper_relevant': len(ctx['proper'] & ctx['relevant']),
                           'colloquial_relevant': len(ctx['colloquial'] & ctx['relevant']),
                           'kwjp_lexemes': len(ctx['kwjp']['lexemes']), 'kwjp_groups': len(ctx['kwjp']['groups'])}}
    data['d4'] = _d4(ctx, paths['nkjp'], clock)
    data['d5'], base = _d5(ctx, clock)
    data['d1'] = clock.run('d1', _d1, ctx, base)
    data['d2'] = clock.run('d2', _d2, ctx, base)
    data['d3'] = clock.run('d3', _d3, ctx, base)
    data['d6'] = clock.run('d6', _d6, ctx, base)
    data['d7'] = clock.run('d7', _d7, ctx, base)
    data['d8'] = clock.run('d8', _d8, ctx, base)
    data['a9'] = _a9(ctx, clock.seconds)
    data['samples'] = clock.run('samples', _samples, ctx, base)
    timing = {'seconds': clock.seconds, 'membership_ii_measured': with_ii}
    return data, timing


# --- Raport ---

def _n(value):
    return '—' if value is None else f'{value:,}'.replace(',', ' ')


def _pct(value, digits=1):
    return '—' if value is None else f'{100 * value:.{digits}f}%'.replace('.', ',')


def _num(value, digits=4):
    return '—' if value is None else f'{value:.{digits}f}'.replace('.', ',')


def _table(headers, rows):
    lines = ['| ' + ' | '.join(headers) + ' |', '|' + '---|' * len(headers)]
    lines += ['| ' + ' | '.join(str(cell) for cell in row) + ' |' for row in rows]
    return lines


def _cov(row):
    return [_pct(row['coverage'][d1]) for d1 in D1_OPTIONS]


COV_HEAD = ['pokrycie kwjp-all', 'kwjp-exact', 'kwjp-standard']


def _fate(fate):
    if fate is None:
        return '—'
    rank = '—' if fate['rank'] is None else _n(fate['rank'])
    return f"r {rank}, {fate['size']} leks.{', POP' if fate['in_pop'] else ''}"


def render(data, timing):
    d1, d2, d3, d4, d5, d6, d7, d8, a9 = (data[k] for k in ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'a9'))
    pop = d1['pop']
    base5 = d5['options'][BASE['d5']]
    worst = d5['options']['d']
    rule = d4[BASE['d4']]
    seconds = timing['seconds']
    out = ['# Pomiar POP i POP0 — etap A', '',
           'Raport tylko do odczytu. NKJP wyłącznie jako rangi, percentyle i udziały (C14). '
           'Przykłady w tabelach to **ilustracja**, nie próba losowa. Próba losowa jest w sekcji „Próbki”.', '',
           '## TL;DR',
           f"- Baza bez zmian: hash przed = po (`{data['database']['sha256_before'][:12]}…`).",
           f"- Wariant bazowy: D5 `{BASE['d5']}`, D3 KWJP+NKJP (log-ipm, waga 0,5), D4 `{BASE['d4']}`, "
           f"POP = {_n(POP_REF)} leksemów, POP0 = {_n(POP0_REF)}.",
           f"- POP bazowy: {_n(pop['lexemes'])} leksemów, {_n(pop['forms'])} form STANDARD, pokrycie "
           f"kwjp-all {_pct(pop['coverage']['kwjp-all'])}, kwjp-standard {_pct(pop['coverage']['kwjp-standard'])}.",
           f"- Sufit pokrycia (wszystkie leksemy): kwjp-all {_pct(d1['ceiling']['kwjp-all']['coverage'])}.",
           f"- D5d łączy łańcuchowo: największa grupa {_n(worst['groups']['largest'])} leksemów; "
           f"`{BASE['d5']}`: {_n(base5['groups']['largest'])}.",
           f"- NKJP ściśle jednoznaczne (D5c) przypisuje {_pct(_attr(d5['options']['c']))} "
           f"masy dopasowanej; d {_pct(_attr(worst))}; `{BASE['d5']}` {_pct(_attr(base5))}.",
           f"- Reguła D4 `{BASE['d4']}`: dopasowane {_pct(rule['matched_share'])} tokenów NKJP.", '']
    out += ['## Podstawa', '']
    out += _table(['pole', 'wartość'], [
        ['leksemy z formą w STANDARD', _n(data['population']['relevant_lexemes'])],
        ['w tym nazwy własne', _n(data['population']['proper_relevant'])],
        ['w tym potoczne (`pot.`)', _n(data['population']['colloquial_relevant'])],
        ['formy STANDARD', _n(data['population']['standard'])],
        ['leksemy KWJP (EXACT) / grupy AMBIGUOUS', f"{_n(data['population']['kwjp_lexemes'])} / "
                                                  f"{_n(data['population']['kwjp_groups'])}"],
        ['options_sha256', f"`{data['options_sha256'][:16]}…`"],
        ['code_identity', f"`{data['code_identity']['tree_sha256'][:16]}…`"]])
    out.append('')

    # D1
    mass = d1['kwjp_mass']
    ceiling = d1['ceiling']['kwjp-all']['coverage']
    out += ['## D1 — mianownik pokrycia', '']
    out += _table(['mianownik', 'masa KWJP', 'POP bazowy', 'sufit (wszystkie leksemy)'], [
        [d1_name, _n(d1['ceiling'][d1_name]['total']), _pct(pop['coverage'][d1_name]),
         _pct(d1['ceiling'][d1_name]['coverage'])] for d1_name in D1_OPTIONS])
    out += ['', f"Masa KWJP: EXACT {_n(mass['EXACT_CANDIDATE'])}, AMBIGUOUS {_n(mass['AMBIGUOUS'])}, "
                f"UNMATCHED {_n(mass['UNMATCHED'])}.", '',
            f"**Zalecenie D1:** progi liczyć w `kwjp-standard`; w raporcie zawsze też `kwjp-all`. "
            f"Cel „98–99% tekstu” w `kwjp-all` jest "
            f"{'nieosiągalny' if (ceiling or 0) < 0.98 else 'osiągalny'} (sufit {_pct(ceiling)}).",
            '']

    # D2
    out += ['## D2 — formy listy', '',
            f"POP bazowy ({_n(pop['lexemes'])} leksemów). STANDARD: {_n(d2['standard'])} form, "
            f"z leksemem (reguła i): {_n(d2['standard_with_lexeme'])}.", '']
    rows = []
    for label, item in d2['variants'].items():
        if item is None:
            rows.append([label, 'nie mierzono w tym przebiegu', '—', '—', '—'])
            continue
        classes = ', '.join(f'{k} {_n(v)}' for k, v in item['removed_by_class'].items()) or '—'
        rows.append([label, _n(item['forms']), f"−{_n(item['removed'])} / +{_n(item['added'])}", classes,
                     _pct(item['removed_nkjp_share'], 2)])
    out += _table(['wariant', 'formy', 'zmiana vs pełna', 'usunięte wg klasy', 'udział masy NKJP usuniętych'], rows)
    out += ['', '**Zalecenie D2:** pełna odmiana, konstrukcje: tak, reguła (i). Wykluczenia klas tną formy, '
                'które gracz zna z tekstu; reguła (ii) kosztuje kilkanaście minut na każdy `pop` '
                f"(czas tutaj: {_time(seconds, 'membership_ii')}).", '']

    # D3
    out += ['## D3 — miara i wagi', '']
    rows = [[label, _n(item['lexemes']), _n(item['forms']), *_cov(item), _num(item['spearman']['rho']),
             _pct(item['top_pop0']['share']), _pct(item['top_pop']['share']), _pct(item['pop_jaccard'])]
            for label, item in d3['variants'].items()]
    out += _table(['miara', 'leksemy', 'formy', *COV_HEAD, 'Spearman vs bazowa',
                   f'top {_n(POP0_REF)} wspólne', f'top {_n(POP_REF)} wspólne', 'POP Jaccard'], rows)
    conf = d3['confidence']
    out += ['', 'Pewność dopasowania (jednostki wszystkie / w POP): ' + ', '.join(
        f"{name} {_n(conf['all'].get(name, 0))} / {_n(conf['pop'].get(name, 0))}"
        for name in sorted(set(conf['all']) | set(conf['pop']))) + '.', '',
        '**Zalecenie D3:** KWJP+NKJP log-ipm (log10 częstości na milion tokenów źródła), waga 0,5. '
        'Średnia percentyli z dwóch populacji zaniżała słowa o rozbieżnych korpusach. Sama KWJP zostaje '
        'ścieżką wycofania NKJP (ADR-006); różnicę pokazują kolumny Spearman i Jaccard.', '']

    # D4
    out += ['## D4 — czyszczenie NKJP', '']
    out += _table(['reguła', 'id', 'dopasowane tokeny', 'kolizje', 'masa scalona', 'D5c przypisane'], [
        [name, f"`{item['rule_id']}`", _pct(item['matched_share']), _n(item['collisions']),
         _pct(item['merged_share'], 2), _pct(item['strict_attributed_share'])] for name, item in sorted(d4.items())])
    out += ['', 'Największe kolizje (ilustracja; bez liczb, liczby tylko w `measure.json`):', '']
    for name, item in sorted(d4.items()):
        if item['top_collisions']:
            shown = ', '.join(f"`{c['key']}` ← {'/'.join(f'`{s[0]}`' for s in c['sources'][:2])}"
                              for c in item['top_collisions'][:10])
            out.append(f'- `{name}`: {shown}')
    out += ['', f"**Zalecenie D4:** `{BASE['d4']}` — zdejmuje cudzysłowy i nawiasy, ale nie skleja skrótów z kropką "
                f"(`ul.`, `r.`, `art.`), które dominują kolizje `strip-edges`.", '']

    # D5
    out += ['## D5 — homonimy', '']
    rows = []
    for option, label in D5_VARIANTS:
        item = d5['options'][option]
        rows.append([label, _n(item['lexemes']), _n(item['forms']), *_cov(item),
                     _pct(_attr_kwjp(item)), _pct(_attr(item)), _n(item['groups']['count']),
                     _n(item['groups']['largest'])])
    out += _table(['opcja', 'leksemy', 'formy', *COV_HEAD, 'KWJP przypisane', 'NKJP przypisane', 'grupy',
                   'największa'], rows)
    out += ['', 'Los słów (ilustracja): ranga jednostki, liczba leksemów w jednostce, czy w POP.', '']
    rows = []
    for word in WORDS:
        owners = d5['words'][word]
        if not owners:
            rows.append([f'`{word}`', '—', *['brak w danych'] * len(D5_VARIANTS)])
            continue
        cells = []
        for option, _ in D5_VARIANTS:
            fates = d5['options'][option]['fates']
            cells.append('; '.join(f"{k.split('@')[0]}: {_fate(fates.get(k))}" for k in owners[:3])
                         + (f' (+{len(owners) - 3})' if len(owners) > 3 else ''))
        rows.append([f'`{word}`', _n(len(owners)), *cells])
    out += _table(['forma', 'leksemy', *(option for option, _ in D5_VARIANTS)], rows)
    out += ['', f'Top {TOP_GROUPS} wierszy AMBIGUOUS KWJP wg F i ich los (ranga jednostki pierwszego członka):', '']
    rows = []
    for group in d5['top_groups']:
        first = group['members'][0]
        rows.append([f"`{group['unit']}`", _n(group['F']), _n(len(group['members'])),
                     *[_fate(d5['options'][option]['fates'].get(first)) for option, _ in D5_VARIANTS]])
    out += _table(['lemat KWJP', 'F', 'kandydaci', *(option for option, _ in D5_VARIANTS)], rows)
    out += ['', f"**Zalecenie D5:** `{BASE['d5']}` — grupa homonimów bez nazw własnych. Nie kopiuje F, "
                f"przypisuje {_pct(_attr(base5))} masy NKJP (c: {_pct(_attr(d5['options']['c']))}), a największa "
                f"grupa ma {_n(base5['groups']['largest'])} leksemów (d: {_n(worst['groups']['largest'])}).", '']

    # D6
    out += ['## D6 — progi POP i POP0', '']
    rows = [[f'{_n(int(n))} leksemów', _n(item['lexemes']), _n(item['units']), _n(item['rank']), _n(item['forms']),
             *_cov(item)] for n, item in d6['counts'].items()]
    rows += [[f"pokrycie {_pct(float(t), 0)} ({BASE['d1']})", _n(item['lexemes']), _n(item['units']),
              _n(item['rank']), _n(item['forms']), *_cov(item)] for t, item in d6['targets'].items()]
    out += _table(['próg', 'leksemy', 'jednostki', 'ranga graniczna', 'formy', *COV_HEAD], rows)
    pop0 = d6['counts'].get(str(POP0_REF))
    out += ['', f"**Zalecenie D6:** wstępnie POP = {_n(POP_REF)} leksemów "
                f"({_pct(pop['coverage']['kwjp-standard'])} kwjp-standard), POP0 = {_n(POP0_REF)} "
                f"({_pct(pop0['coverage']['kwjp-standard']) if pop0 else '—'}). Ostatecznie po ocenie próbek granicznych.",
            '']

    # D7
    out += ['## D7 — luka potoczna (A6)', '',
            f"Leksemy potoczne z formą w STANDARD: {_n(d7['colloquial'])}. Mediana różnicy percentyli "
            f"NKJP − KWJP: potoczne {_num(d7['gap_median']['colloquial'], 2)} (n = {_n(d7['gap_n']['colloquial'])}), "
            f"pozostałe {_num(d7['gap_median']['other'], 2)} (n = {_n(d7['gap_n']['other'])}).", '']
    out += _table(['próg', 'potoczne w POP', 'potoczne poza'], [
        [f'{_n(int(n))} leksemów', _n(v['inside']), _n(v['outside'])] for n, v in d7['by_count'].items()])
    out += ['', 'Potoczne poza POP bazowym, wg rangi NKJP (ilustracja):', '']
    out += _table(['jednostka', 'ranga NKJP', 'ranga KWJP', 'ranga bazowa'], [
        [_unit_label([('', u) for u in e['unit']]), _n(e['nkjp_rank']), _n(e['kwjp_rank']), _n(e['rank'])]
        for e in d7['examples']] or [['—', '—', '—', '—']])
    out += ['', '**Zalecenie D7:** przyjąć lukę w `pop-v1` i opisać ją w LIMITATIONS; dodatki potoczne '
                'to osobne zadanie.', '']

    # D8
    out += ['## D8 — braki danych', '',
            f"Brak pełny (bez KWJP i NKJP): {_n(d8['full'])} jednostek. Statusy KWJP/NKJP (§8.2):", '']
    out += _table(['KWJP / NKJP', 'jednostki'], [[k, _n(v)] for k, v in d8['statuses'].items()])
    out += ['']
    out += _table(['brak częściowy', 'leksemy', 'formy', *COV_HEAD, 'braki częściowe', 'POP Jaccard vs available-only'],
                  [[rule_name, _n(item['lexemes']), _n(item['forms']), *_cov(item), _n(item['missing']['partial']),
                    _pct(item['jaccard_available_only'])] for rule_name, item in d8['rules'].items()])
    out += ['', '**Zalecenie D8:** brak pełny poza listą; brak częściowy `lower-bound-absent`: źródło '
                'nieobecne dostaje najmniejszą zaobserwowaną miarę (flaga `bound`), źródło niewiarygodne '
                '(`PROPER_SHARED`, `UNMATCHED`) jest pomijane (flaga `single_source`). Wrażliwość pokazuje '
                'kolumna Jaccard.', '']

    # A9
    counts = a9['counts']
    out += ['## A9 — formy konstrukcji i czas reguł', '',
            f"Formy STANDARD tylko z konstrukcji: {_n(a9['only_constructions'])}. Jeden leksem składnika: "
            f"{_n(counts['one'])}, żaden: {_n(counts['none'])}, kilka: {_n(counts['several'])}.", '']
    for name, label in (('none', 'żaden'), ('several', 'kilka')):
        if a9['examples'].get(name):
            out.append(f"- {label} (ilustracja): " + ', '.join(f'`{k}`' for k in a9['examples'][name]))
    out += ['', f"Czas reguły (i): {_time(seconds, 'membership_i')}. Czas reguły (ii): "
                f"{_time(seconds, 'membership_ii')}.", '']
    second = a9['membership_ii']
    if second:
        out += _table(['reguła', 'leksemy', 'pary leksem–forma', 'tylko w tej regule'], [
            ['(i)', _n(second['lexemes_i']), _n(second['pairs_i']), _n(second['only_i'])],
            ['(ii)', _n(second['lexemes_ii']), _n(second['pairs_ii']), _n(second['only_ii'])]])
        out.append('')
    out += ['Pozostałe etapy: ' + ', '.join(f'{k} {_num(v, 1)} s' for k, v in sorted(seconds.items())) + '.', '']

    # Próbki
    samples = data['samples']
    out += ['## Próbki (A7)', '',
            f"`{samples['version']}`, seed `{samples['seed']}`, {samples['size_per_stratum']} na warstwę, status "
            f"`{samples['status']}`. Ocena wstępna agenta: grupa 7.", '']
    out += _table(['warstwa', 'populacja', 'próbka'], [
        [name, _n(item['population']), _n(item['sample_size'])] for name, item in samples['strata'].items()])
    out.append('')
    for name, item in samples['strata'].items():
        out.append(f"- `{name}`: " + ', '.join(f"`{s['key'].split('@')[0]}`" for s in item['selected']))
    out.append('')
    return '\n'.join(out)


def _attr(item):
    nkjp = item['mass'].get('nkjp')
    return _share(nkjp['attributed'], nkjp['matched']) if nkjp else None


def _attr_kwjp(item):
    kwjp = item['mass']['kwjp']
    return _share(kwjp['attributed'], kwjp['total'])


def _time(seconds, name):
    if name not in seconds:
        return 'nie mierzono w tym przebiegu'
    return f'{_num(seconds[name], 1)} s'


# --- Przepływ i zapis ---

def run(args):
    output = Path(args.output_dir).resolve()
    if output.exists():
        raise GeneratorError('Katalog wyjściowy istnieje', 4, str(output))
    if not output.parent.is_dir():
        raise GeneratorError('Brak katalogu nadrzędnego wyjścia', 2, str(output.parent))
    sources = load_sources(args.sources)
    paths = check_inputs(sources, args.run_dir, args.release_dir)
    for protected in (paths['run_dir'], paths['release_dir']):
        if output == Path(protected) or Path(protected) in output.parents:
            raise GeneratorError('Wyjście nie może leżeć w przebiegu ani w pakiecie', 2, str(output))
    paths['sources'] = sources
    data, timing = collect(paths, args.with_membership_ii)
    after = database_sha256(paths['database'])
    if after != paths['database_sha256']:
        raise GeneratorError('Hash bazy zmienił się w trakcie pomiaru', 5, paths['database'])
    data['database'] = {'sha256_before': paths['database_sha256'], 'sha256_after': after}
    timing['peak_rss_mb'] = _peak_rss_mb()
    staging = Path(tempfile.mkdtemp(prefix=f'.{output.name}-staging-', dir=output.parent))
    try:
        write_json(staging / 'measure.json', data)
        write_json(staging / 'timing.json', timing)
        (staging / 'report.md').write_text(render(data, timing), encoding='utf-8', newline='\n')
        try:
            rename_noreplace(staging, output)
        except FileExistsError as error:
            raise GeneratorError('Katalog wyjściowy istnieje', 4, str(output)) from error
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return output


def parse(argv):
    parser = argparse.ArgumentParser(description='Pomiar POP i POP0 (etap A), tylko odczyt.')
    parser.add_argument('--sources', default=str(Path(__file__).resolve().parents[1]
                                                 / 'config/generator/pop-sources.json'))
    parser.add_argument('--run-dir')
    parser.add_argument('--release-dir')
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--with-membership-ii', action='store_true',
                        help='zmierz też regułę (ii) z variant_decision (ok. 13 min)')
    return parser.parse_args(argv)


def main(argv=None):
    args = parse(argv)
    try:
        output = run(args)
    except GeneratorError as error:
        print(f'Błąd (kod {error.code}): {error}' + (f' [{error.source}]' if error.source else ''),
              file=sys.stderr)
        return error.code
    print(os.fspath(output))
    return 0


if __name__ == '__main__':
    sys.exit(main())
