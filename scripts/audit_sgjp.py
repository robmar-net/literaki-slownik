#!/usr/bin/env python3
"""Odtwarzalny audyt tekstowego SGJP; nie eksportuje słowników produkcyjnych."""
import argparse
import gzip
import hashlib
import itertools
import json
import math
import os
import subprocess
import tempfile
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def records(path):
    # Eksport nie grupuje wszystkich powtórzeń form obok siebie.
    # Sortowanie bajtowe pozwala dokładnie deduplikować, bez hashy rekordów.
    Path('cache').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='sgjp-sort-', dir='cache') as temp:
        raw, ordered = Path(temp)/'raw.tsv', Path(temp)/'ordered.tsv'
        with gzip.open(path, 'rt', encoding='utf-8', errors='strict') as stream, raw.open('w') as out:
            for line in stream:
                if line.rstrip() == '#</COPYRIGHT>':
                    break
            else:
                raise ValueError('Brak końca nagłówka licencji')
            for number, line in enumerate(stream, 1):
                fields = line.rstrip('\r\n').split('\t')
                if len(fields) != 5:
                    raise ValueError(f'Rekord {number}: {len(fields)} kolumn zamiast 5')
                out.write('\t'.join(fields)+'\n')
        subprocess.run(['sort', '-T', temp, '-o', str(ordered), str(raw)],
                       env=dict(os.environ, LC_ALL='C'), check=True)
        with ordered.open() as stream:
            for line in stream:
                yield tuple(line.rstrip('\n').split('\t'))


def audit(source, policy, output):
    cfg = json.loads(Path(policy).read_text())
    alphabet = set(cfg['alphabet'].replace(' ', ''))
    filters = ['znaki', 'dlugosc', 'nazwa_wlasna', 'skrot', 'segment_do_oceny',
               'wielka_litera_do_oceny', 'mieszane_oznaczenia_do_oceny', 'niepoprawnosc', 'historycznosc']
    # Każdy bit: rekord przechodzi dany filtr. Osobne bity: przechodzi prefiks filtrów.
    k = len(filters)
    raw_forms = set()
    lexemes = set()
    game_masks = {}
    counts = Counter()
    distributions = {n: Counter() for n in ['pos', 'name_raw', 'labels_raw', 'length_original', 'characters']}
    labels = defaultdict(lambda: {'records': 0, 'forms': set(), 'lexemes': set()})
    examples = defaultdict(list)
    rejected = Counter()
    sequential = Counter()
    overlaps = Counter()
    expanded_cache = {}
    pilot_words = {'róża', 'zamek', 'mam', 'dwa', 'sto', 'kot', 'czytałem', 'czytałbym', 'bym', 'żem', 'polsku', 'biało', 'ABS', 'abs', 'by', 'nie', 'jestem', 'poszedłem'}
    pilot = []
    label_examples = defaultdict(list)
    for form, grouped in itertools.groupby(records(source), key=lambda row: row[0]):
        if form in raw_forms:
            raise ValueError('Forma powraca w nieciągłej grupie; zmień agregację zamiast podawać błędną deduplikację')
        raw_forms.add(form)
        seen = set()
        normalized = unicodedata.normalize('NFC', form)
        key = normalized.lower()
        distributions['length_original'][len(form)] += 1
        distributions['characters'].update(form)
        counts['non_nfc_forms'] += normalized != form
        for row in grouped:
            counts['records'] += 1
            if row in seen:
                counts['duplicate_records'] += 1
                continue
            seen.add(row)
            _, lemma, tag, name, qualifier = row
            counts['unique_compact_interpretations'] += 1
            lexemes.add(lemma)
            pos = tag.split(':')[0]
            if tag not in expanded_cache:
                expanded_cache[tag] = math.prod(len(value.split('.')) for value in tag.split(':'))
            counts['expanded_grammar_alternatives'] += expanded_cache[tag]
            for group, value in [('pos', pos), ('name_raw', name), ('labels_raw', qualifier)]:
                distributions[group][value] += 1
                if len(examples[group + ':' + value]) < 3:
                    examples[group + ':' + value].append(row)
            label_tokens = set(qualifier.replace('|', ',').split(',')) - {''}
            for label in label_tokens:
                labels[label]['records'] += 1
                labels[label]['forms'].add(key)
                labels[label]['lexemes'].add(lemma)
                if len(label_examples[label]) < 3:
                    label_examples[label].append(row)
            mixed = '|' in name or '|' in qualifier
            lemma_base = lemma.split(':')[0]
            lexical_segment = ((lemma_base == 'ż' and tag in {'part:wok', 'part:nwok'})
                               or (lemma_base == 'on' and tag in {
                                   'ppron3:sg:gen.acc:m1.m2.m3:ter:nakc:praep',
                                   'ppron3:sg:gen:m1.m2.m3:ter:nakc:praep',
                                   'ppron3:sg:acc:m1.m2.m3:ter:nakc:praep'})
                               or (lemma_base in {'latek', 'latka', 'lecie', 'ścian'} and pos == 'subst')
                               or (lemma_base == 'kroć' and pos == 'adv')
                               or (lemma_base in {'+znawca', '+dawca', '+biorca', '+żerca', '+maniak', '+logia', '+log'} and pos == 'subst')
                               or (lemma_base in {'ty', 'y'} and pos == 'adj'))
            fails = [not set(key) <= alphabet,
                     not cfg['min_length'] <= len(key) <= cfg['max_length'],
                     bool(name) and 'nazwa_pospolita' not in name.split('|'),
                     pos in cfg['excluded_pos'],
                     pos in cfg['unresolved_segment_pos'] or (pos == 'praet' and tag.endswith(':agl')) or lexical_segment,
                     normalized != normalized.lower(),
                     mixed,
                     bool(label_tokens & set(cfg['incorrect_labels'])),
                     bool(label_tokens & set(cfg['historical_labels']))]
            mask = 0
            alive = True
            for i, fail in enumerate(fails):
                if fail:
                    rejected[filters[i]] += 1
                else:
                    mask |= 1 << i
                alive = alive and not fail
                if alive:
                    sequential[filters[i]] += 1
                    mask |= 1 << (k + i)
            game_masks[key] = game_masks.get(key, 0) | mask
            overlaps[' + '.join(filters[i] for i, fail in enumerate(fails) if fail) or 'brak'] += 1
            if form in pilot_words or key in pilot_words:
                pilot.append({'source_row': row, 'failed_filters': [filters[i] for i, fail in enumerate(fails) if fail]})
    total_forms = len(game_masks)
    filter_stats = []
    previous_rows = counts['unique_compact_interpretations']
    previous_forms = total_forms
    for i, name in enumerate(filters):
        individual_forms = sum(bool(mask & (1 << i)) for mask in game_masks.values())
        combined_forms = sum(bool(mask & (1 << (k+i))) for mask in game_masks.values())
        filter_stats.append({'filter': name, 'rejected_interpretations_alone': rejected[name],
                             'lost_keys_alone': total_forms-individual_forms,
                             'remaining_interpretations_cumulative': sequential[name],
                             'lost_interpretations_at_step': previous_rows-sequential[name],
                             'remaining_keys_cumulative': combined_forms,
                             'lost_keys_at_step': previous_forms-combined_forms})
        previous_rows, previous_forms = sequential[name], combined_forms
    broad_bit, standard_bit = 1 << (k+k-2), 1 << (k+k-1)
    rescued_examples = []
    for row in pilot:
        key = unicodedata.normalize('NFC', row['source_row'][0]).lower()
        row['key_in_broad_screen'] = bool(game_masks[key] & broad_bit)
        row['key_in_standard_screen'] = bool(game_masks[key] & standard_bit)
        if row['failed_filters'] and row['key_in_standard_screen']:
            rescued_examples.append(row)
    result = {'source_sha256': digest(source), 'policy_sha256': digest(policy),
              'script_sha256': digest(__file__), 'counts': dict(counts),
              'unique_original_forms': len(raw_forms), 'unique_nfc_lower_keys': total_forms,
              'unique_source_lemma_identifiers': len(lexemes),
              'definitions': {'interpretation': 'unikalny 5-elementowy rekord z tagiem skompresowanym',
                              'expanded': 'suma iloczynów liczby alternatyw rozdzielonych kropką w polach tagu; nie liczba znaczeń',
                              'lexeme_proxy': 'dokładny identyfikator lematu wraz z sufiksem homonimii; nie zweryfikowany wewnętrzny ID bazy SGJP'},
              'distributions': {name: dict(value) for name, value in distributions.items()},
              'label_stats': {name: {'records': d['records'], 'keys': len(d['forms']), 'lemma_ids': len(d['lexemes']), 'examples': label_examples[name]} for name, d in sorted(labels.items())},
              'filters': filter_stats, 'filter_overlaps': dict(overlaps),
              'examples': dict(examples), 'pilot_sgjp': pilot, 'rescued_examples': rescued_examples,
              'checks': {'standard_subset_broad': all(not mask & standard_bit or mask & broad_bit for mask in game_masks.values()),
                         'one_interpretation_satisfies_entire_prefix': True,
                         'sorted_form_groups_contiguous': True}}
    Path(output).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({name: result[name] for name in ['counts','unique_original_forms','unique_nfc_lower_keys','unique_source_lemma_identifiers','filters','checks']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('output')
    parser.add_argument('--policy', default='config/audit-policy.json')
    args = parser.parse_args()
    audit(args.source, args.policy, args.output)
